"""OLMO_PREMISE_PREREG.md (sealed with this file): premise-and-endpoint check of the stage-1-end OLMo-2 1B Q multimodality.
T1 raw vs gain-folded per-head singular spectra (dip test, the Stage 1b rule: MULTIMODAL iff dip p < 0.01), both trims;
T2 row-norm confusable class (+ dead-rows-removed, lognormal row norms, gain-folded Gaussian) -> FPR at both trims;
T3 two 2x2 tables per type (sigma-multimodal x row-norm-bimodal; sigma-multimodal x dead-row-present) + Fisher p;
T4 endpoint on stage2-ingredient3 (ingredients 1-2 descriptive); T5 dead rows: norm, gain, WD bound (config UNVERIFIED).
Streams q_proj/k_proj/q_norm/k_norm per layer (remote_st). CPU. numpy SVD (128 x 2048 per head, fp64).

Folded map: q = g * RMSNorm(W_Q x) -> up to a per-token scalar the linear map is diag(g) W_Q; per head h the rows
h*128 .. h*128+127 of diag(g) W_Q (OLMo-2 q_norm is over the full 2048-dim query, per-channel gain g).
Usage: olmo_premise.py known-answer   (synthetic only; checkrun before the seal is used)
       olmo_premise.py run            (T1-T5 + verdict -> results/olmo_premise.json)
"""
import json, sys, time
from pathlib import Path
import numpy as np
import diptest
from scipy.stats import binom, fisher_exact
ROOT = Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT))
import remote_st as R

REPO = "allenai/OLMo-2-0425-1B"
REVS = {"step0": "stage1-step0-tokens0B", "stage1_end": "stage1-step1907359-tokens4001B",
        "ing3": "stage2-ingredient3-step23852-tokens51B", "ing1": "stage2-ingredient1-step23852-tokens51B",
        "ing2": "stage2-ingredient2-step23852-tokens51B"}
NL, NH, DH, D = 16, 16, 128, 2048
ALPHA, TRIM = 0.01, 0.1
SEAL = json.loads((ROOT / "seals" / "stage1b_dip_calibration.json").read_text())


def dip_p(x):
    return float(diptest.diptest(np.asarray(x, np.float64))[1])


def head_stats(W, g):
    """W (2048 x 2048) fp64, g (2048,). Per head: sigma raw/folded (128), row norms raw/folded, gains."""
    out = []
    for h in range(NH):
        B = W[h * DH:(h + 1) * DH]; gh = g[h * DH:(h + 1) * DH]; F = gh[:, None] * B
        out.append(dict(sig_raw=np.linalg.svd(B, compute_uv=False), sig_fold=np.linalg.svd(F, compute_uv=False),
                        rn_raw=np.linalg.norm(B, axis=1), rn_fold=np.linalg.norm(F, axis=1), gain=gh))
    return out


def multimodal(sig, trim):
    x = sig / np.median(sig) if np.median(sig) > 0 else sig
    if trim: x = x[x >= TRIM]
    return (dip_p(x) < ALPHA) if len(x) >= 8 else False, len(x)


def rate_table(heads, key, f0):
    out = {}
    for trim in (False, True):
        flags = [multimodal(hd[key], trim)[0] for hd in heads]; k = int(sum(flags)); n = len(flags)
        bp = float(binom.sf(k - 1, n, f0)) if k else 1.0
        out["trim_nearzero" if trim else "all_levels"] = dict(k=k, n=n, frac=k / n, binom_p=bp,
                                                             shows_peaks=bool(k / n >= 0.10 and bp < 1e-3), flags=flags)
    return out


def confusables(heads_s1, rng, draws, f0_check=True):
    """FPR of the dip rule on row-norm-structured Gaussian blocks (T2 + A1 cells)."""
    res = {}
    for cls in ("own_rownorm_raw", "own_rownorm_fold", "own_rownorm_raw_deadrows_removed", "lognormal_rownorm", "gain_folded_gaussian"):
        flags = {False: 0, True: 0}
        for _ in range(draws):
            hd = heads_s1[rng.integers(len(heads_s1))]; G = rng.normal(size=(DH, D)) / np.sqrt(D)
            if cls == "own_rownorm_raw": W = hd["rn_raw"][:, None] * G
            elif cls == "own_rownorm_fold": W = hd["rn_fold"][:, None] * G
            elif cls == "own_rownorm_raw_deadrows_removed":
                rn = hd["rn_raw"].copy(); med = np.median(rn); rn[rn < TRIM * med] = med; W = rn[:, None] * G
            elif cls == "lognormal_rownorm": W = np.exp(rng.normal(0, 0.5, size=DH))[:, None] * G
            else: W = hd["gain"][:, None] * G
            s = np.linalg.svd(W, compute_uv=False)
            for trim in (False, True): flags[trim] += multimodal(s, trim)[0]
        res[cls] = {"all_levels": flags[False] / draws, "trim_nearzero": flags[True] / draws, "draws": draws}
    return res


def known_answer(rng, draws=300):
    """RAW known answers (the sealed Stage 1b unit): (a) a Gaussian 128 x 2048 block reads UNIMODAL (FPR <= 0.02);
       (b) a planted two-component head (d=0.3, sd=0.03, w=0.5; the sealed power cell, power 1.0) reads MULTIMODAL >= 0.8.
       FOLDED licensing cell (prereg §4 / A2): the gain-folded Gaussian with REAL stage-1-end gains (layer 0, Q) -- its
       dip rate is the FPR of the folded reading; > 0.02 means the gain alone manufactures peaks and the folded branch is
       NOT LICENSED (reported, not a pass criterion after A2). Also the planted head folded with the same gains."""
    idx = R.index(REPO, REVS["stage1_end"]); g, _ = R.fetch(idx, "model.layers.0.self_attn.q_norm.weight"); g = np.asarray(g, np.float64)
    fa = fb = fc = fd = 0
    for _ in range(draws):
        h = rng.integers(NH); gh = g[h * DH:(h + 1) * DH]
        G = rng.normal(size=(DH, D)) / np.sqrt(D)
        fa += multimodal(np.linalg.svd(G, compute_uv=False), False)[0]
        fc += multimodal(np.linalg.svd(gh[:, None] * G, compute_uv=False), False)[0]
        s = np.where(rng.random(DH) < 0.5, rng.normal(1.0, 0.03, DH), rng.normal(1.3, 0.03, DH))
        U, _ = np.linalg.qr(rng.normal(size=(DH, DH))); V, _ = np.linalg.qr(rng.normal(size=(D, DH)))
        W = (U * s) @ V.T
        fb += multimodal(np.linalg.svd(W, compute_uv=False), False)[0]
        fd += multimodal(np.linalg.svd(gh[:, None] * W, compute_uv=False), False)[0]
    fa, fb, fc, fd = fa / draws, fb / draws, fc / draws, fd / draws
    gm = [dip_p(g[h * DH:(h + 1) * DH]) < ALPHA for h in range(NH)]
    print(f"known-answer RAW: Gaussian FPR {fa:.3f} (<= 0.02); planted two-component detected {fb:.3f} (>= 0.8)")
    print(f"FOLDED licensing cell: gain-folded Gaussian dip rate {fc:.3f} (> 0.02 => folded branch NOT LICENSED); planted+folded {fd:.3f}; "
          f"layer-0 Q gain histograms multimodal in {sum(gm)}/{NH} heads; gain range [{g.min():.2f}, {g.max():.2f}]")
    ok = fa <= 0.02 and fb >= 0.8
    print("FOLDED_LICENSED", fc <= 0.02); print("KNOWN_ANSWER", "PASS" if ok else "FAIL"); return ok


def run():
    rng = np.random.default_rng(20261003); t0 = time.time()
    f0_seal = float(SEAL["f0"]); out = {"repo": REPO, "revisions": REVS, "f0_sealed": f0_seal, "runs": {}, "subs": []}
    heads = {}
    for tag, rev in REVS.items():
        idx = R.index(REPO, rev); heads[tag] = {"Q": [], "K": []}
        for l in range(NL):
            for M, pn, gn in (("Q", "q_proj", "q_norm"), ("K", "k_proj", "k_norm")):
                W, _ = R.fetch(idx, f"model.layers.{l}.self_attn.{pn}.weight"); g, _ = R.fetch(idx, f"model.layers.{l}.self_attn.{gn}.weight")
                for hd in head_stats(np.asarray(W, np.float64), np.asarray(g, np.float64)): hd["layer"] = l; heads[tag][M].append(hd)
        print(f"{tag}: streamed {NL} layers Q,K  {time.time()-t0:.0f}s", flush=True)
    # T2 confusables on stage-1-end heads (Q and K pooled), BEFORE reading T1's folded numbers
    conf = confusables(heads["stage1_end"]["Q"] + heads["stage1_end"]["K"], rng, 2000)
    worst = {trim: max(v[trim] for v in conf.values()) for trim in ("all_levels", "trim_nearzero")}
    f0 = {trim: max(f0_seal, worst[trim]) for trim in worst}
    licensed = {trim: worst[trim] <= 0.02 for trim in worst}
    out["T2_confusables"] = conf; out["f0"] = f0; out["licensed_rownorm"] = licensed
    print("T2 confusable FPR:", {k: {t: round(v[t], 3) for t in ("all_levels", "trim_nearzero")} for k, v in conf.items()}, "licensed:", licensed, flush=True)
    # T1 / T4 rates
    for tag in REVS:
        out["runs"][tag] = {}
        for M in ("Q", "K"):
            r = {}
            for key in ("sig_raw", "sig_fold"):
                rt = {}                                         # f0 per trim (declared): each trim uses its own f0
                for trim, f in (("all_levels", f0["all_levels"]), ("trim_nearzero", f0["trim_nearzero"])):
                    d = rate_table(heads[tag][M], key, f)[trim]; rt[trim] = {k: v for k, v in d.items() if k != "flags"}
                r[key] = rt
            # A2 descriptive gain column: per head, is the gain histogram itself multimodal, and does a Gaussian block folded
            # with the head's OWN gains read multimodal (the folded reading's own confusable, per head)
            gm = [dip_p(hd["gain"]) < ALPHA for hd in heads[tag][M]]
            gf = [multimodal(np.linalg.svd(hd["gain"][:, None] * rng.normal(size=(DH, D)) / np.sqrt(D), compute_uv=False), False)[0] for hd in heads[tag][M]]
            sf = [multimodal(hd["sig_fold"], False)[0] for hd in heads[tag][M]]
            r["A2_gain_descriptive"] = {"frac_gain_hist_multimodal": float(np.mean(gm)), "frac_own_gain_folded_gaussian_multimodal": float(np.mean(gf)),
                                        "frac_folded_multimodal_AND_own_gain_gaussian_multimodal": float(np.mean(np.array(sf) & np.array(gf))),
                                        "frac_folded_multimodal": float(np.mean(sf))}
            # T3 (stage-1 end only, raw and folded) and T5 (stage-1 end)
            if tag == "stage1_end":
                for key, rnk in (("sig_raw", "rn_raw"), ("sig_fold", "rn_fold")):
                    sm = np.array([multimodal(hd[key], False)[0] for hd in heads[tag][M]])
                    rb = np.array([dip_p(hd[rnk]) < ALPHA for hd in heads[tag][M]])
                    dr = np.array([np.any(hd["rn_raw"] < TRIM * np.median(hd["rn_raw"])) for hd in heads[tag][M]])
                    t1 = [[int(np.sum(sm & rb)), int(np.sum(sm & ~rb))], [int(np.sum(~sm & rb)), int(np.sum(~sm & ~rb))]]
                    t2 = [[int(np.sum(sm & dr)), int(np.sum(sm & ~dr))], [int(np.sum(~sm & dr)), int(np.sum(~sm & ~dr))]]
                    r[f"T3_{key}"] = {"sigma_x_rownorm_bimodal": t1, "fisher_p_rownorm": float(fisher_exact(t1)[1]),
                                      "sigma_x_deadrow": t2, "fisher_p_deadrow": float(fisher_exact(t2)[1])}
                dead = []
                for hd in heads[tag][M]:
                    med = np.median(hd["rn_raw"]); medg = np.median(np.abs(hd["gain"]))
                    for i in np.where(hd["rn_raw"] < TRIM * med)[0]:
                        dead.append({"layer": hd["layer"], "norm": float(hd["rn_raw"][i]), "norm_over_median": float(hd["rn_raw"][i] / med),
                                     "gain": float(hd["gain"][i]), "gain_over_median_abs": float(abs(hd["gain"][i]) / medg)})
                bound = float(np.exp(-0.1 * 4e-4 * 0.5 * 1907359))   # UNVERIFIED-config: WD 0.1, peak 4e-4, cosine mean ~0.5
                r["T5_dead_rows"] = {"n": len(dead), "wd_bound_norm_ratio_UNVERIFIED_config": bound,
                                     "frac_gain_below_0.1_median": float(np.mean([d["gain_over_median_abs"] < 0.1 for d in dead])) if dead else None,
                                     "median_norm_over_median": float(np.median([d["norm_over_median"] for d in dead])) if dead else None,
                                     "rows": dead[:400]}
            out["runs"][tag][M] = r
            print(tag, M, {key: {t: (v["k"], round(v["frac"], 3), v["shows_peaks"]) for t, v in r[key].items()} for key in ("sig_raw", "sig_fold")}, flush=True)
    # verdict (prereg §3 + A1 + A2): the RAW branch is primary (the folded branch is NOT LICENSED when the gain-folded
    # Gaussian cell reads > 0.02; its rates are reported as descriptive beside the gain column)
    s1 = out["runs"]["stage1_end"]["Q"]; e3 = out["runs"]["ing3"]["Q"]
    folded_lic = conf["gain_folded_gaussian"]["trim_nearzero"] <= 0.02 and conf["gain_folded_gaussian"]["all_levels"] <= 0.02
    out["folded_branch_licensed"] = folded_lic
    key = "sig_fold" if folded_lic else "sig_raw"
    raw_lic = all(conf[c][t] <= 0.02 for c in ("own_rownorm_raw", "own_rownorm_raw_deadrows_removed", "lognormal_rownorm") for t in ("all_levels", "trim_nearzero"))
    if not raw_lic:
        word = "NOT LICENSED (row-norm confusable on the raw reading)"
    elif s1[key]["trim_nearzero"]["shows_peaks"]:
        fades = all(not e3[key][t]["shows_peaks"] and e3[key][t]["frac"] < 0.10 for t in ("all_levels", "trim_nearzero"))
        word = f"STANDS ({'folded' if folded_lic else 'raw; folded NOT LICENSED, gain-shaped'}); endpoint ingredient 3: " + (
            "FADES (dip-conservative: a weaker multimodality could remain)" if fades else
            ("SURVIVES" if e3[key]["trim_nearzero"]["frac"] >= 0.10 else "INCONCLUSIVE"))
    else:
        word = f"STAGE-1-END RATE SUB-FLOOR on {key} (not STANDS)"
    out["verdict_Q"] = word; out["G0_step0_Q_frac"] = out["runs"]["step0"]["Q"]["sig_fold"]["all_levels"]["frac"]
    print("VERDICT_Q:", word, "| step0 folded frac", out["G0_step0_Q_frac"])
    (ROOT / "results" / "olmo_premise.json").write_text(json.dumps(out, indent=1, default=float))
    print("WROTE results/olmo_premise.json OLMO_PREMISE_DONE", f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "known-answer": sys.exit(0 if known_answer(np.random.default_rng(1)) else 1)
    run()
