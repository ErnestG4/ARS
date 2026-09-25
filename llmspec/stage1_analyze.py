"""Stage 1 existence check: apply the SEALED peak criterion (seals/stage1_peak_criterion.json)
to banked spectra. Written and committed before any real spectrum was examined.

Decision checkpoints (declared): OLMo = `main` (final, post stage-2); Pythia-1.4B = step143000.
Also reported: OLMo stage1-step1907359 (end of stage 1); step-0 of both = G0 empirical null.
Outputs: results/stage1_long.parquet (G5 columns), results/stage1_verdict.json, plots/stage1_*.png

AMENDMENT A1 (POST-HOC, declared 2026-09-25 after the first run crashed on OLMo stage1-end and the raw
spectra had been inspected; the sealed primary rule and decision thresholds are UNCHANGED):
  * Spectra estimator v2 = direct fp64 SVD (v1 Gram eigvalsh could not resolve sigma < ~1e-8 sigma_max).
  * Precision floor per head: floor = u * rms(W_head) * (sqrt(d_head) + sqrt(d_model)), u = unit roundoff
    of the grid the stored values actually sit on (G4 audit: fp16 grid -> 2^-11, bf16 -> 2^-8, else 2^-24).
  * RANK_COLLAPSED head: median sigma <= floor (sigma/median undefined). Excluded from mode counts; counted
    and reported. Verdict fractions are reported over n_total (collapsed = not multimodal; the sealed
    decision uses this, conservative) and over n_evaluable.
  * Dead rows per head: rows with norm < t * max row norm, t in {1e-3, 1e-6, 1e-12} (robustness shown).
  * Mode location split: NEAR_ZERO mode = KDE mode at x < 0.1; BULK modes = x >= 0.1. BULK_PEAKS verdict
    applies the sealed thresholds to the bulk-mode count. Aim 1 (narrow peaks in the bulk) is about
    BULK_PEAKS; a primary PEAKS carried only by near-zero modes is labelled NEAR_ZERO_MODES_ONLY.
  * KDE grid: exact-subset sparse grid (verify_kde_sparse.py: 2040/2040 agree with dense; red-paths).
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binom
from scipy.integrate import quad
import peaks as P
import specs as S

ROOT = Path(__file__).resolve().parent
SEAL = json.loads((ROOT / "seals" / "stage1_peak_criterion.json").read_text())
RUNS = [("olmo2-1b", "main", "final"), ("olmo2-1b", "stage1-step1907359-tokens4001B", "stage1_end"),
        ("olmo2-1b", "stage1-step0-tokens0B", "step0"),
        ("pythia-1.4b", "step143000", "final"), ("pythia-1.4b", "step0", "step0")]
MATS = "QKVO"
EST = "stage1-analyze-v2-A1"


def load(model, rev):
    d = ROOT / "cache" / "spectra" / model / rev
    assert (d / "DONE").exists(), f"spectra not banked: {d}"
    L = S.MODELS[model]["n_layer"]
    return [np.load(d / f"L{l:02d}.npz") for l in range(L)]


def mp_sigma_pdf(c):
    """MP singular-value density for aspect c = p/n <= 1 (entries var 1/n): lambda = s^2 has
    density sqrt((b-l)(l-a)) / (2 pi c l) on [a,b], a,b = (1 -/+ sqrt c)^2. Returns (pdf(s), median)."""
    a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    fl = lambda l: np.sqrt(max((b - l) * (l - a), 0)) / (2 * np.pi * c * l)
    fs = lambda s: 2 * s * fl(s * s)
    lo, hi = np.sqrt(a), np.sqrt(b)
    tot = quad(fs, lo, hi, limit=200)[0]
    assert abs(tot - 1) < 1e-3, f"MP pdf does not integrate to 1 (c={c}): {tot}"
    grid = np.linspace(lo, hi, 20001)
    cdf = np.cumsum([fs(s) for s in grid]); cdf /= cdf[-1]
    med = float(grid[np.searchsorted(cdf, 0.5)])
    return fs, lo, hi, med


def unit_roundoff(grid):
    if grid.get("frac_on_fp16_grid", 0) == 1.0:
        return 2.0 ** -11
    if grid.get("frac_on_bf16_grid", 0) == 1.0:
        return 2.0 ** -8
    return 2.0 ** -24


def rule_verdict(k, n, frac_min):
    p = float(binom.sf(k - 1, n, 0.01)) if k > 0 else 1.0
    return {"k": int(k), "n": int(n), "frac": k / n, "binom_p_null01": p,
            "shows_peaks": bool(k / n >= frac_min and p < 1e-3)}


def main():
    assert SEAL["all_checks_pass"], "seal checks did not pass; Stage 1 not licensed"
    uh, uf = SEAL["units"]["per_head"], SEAL["units"]["full_matrix"]
    rows, verdict, keep = [], {}, {}
    for model, rev, tag in RUNS:
        Ls = load(model, rev)
        step = rev
        v = {}
        for M in MATS:
            grid = [json.loads(str(z[f"grid_{M}"])) for z in Ls]
            u = unit_roundoff(grid[0])
            assert all(unit_roundoff(g) == u for g in grid), "mixed storage grids across layers"
            sig = np.concatenate([z[f"sig_head_{M}"] for z in Ls])          # (L*H, d_head) ascending
            rms = np.concatenate([z[f"rms_head_{M}"] for z in Ls])
            rn = np.concatenate([z[f"rownorm_{M}"] for z in Ls])
            H = Ls[0][f"sig_head_{M}"].shape[0]
            dh = sig.shape[1]
            floor = u * rms * (np.sqrt(dh) + np.sqrt(S.MODELS[model]["d_model"]))
            med = np.median(sig, 1)
            collapsed = med <= floor
            ev = ~collapsed
            dead = {t: (rn < t * rn.max(1, keepdims=True)).sum(1) for t in (1e-3, 1e-6, 1e-12)}
            n_below_floor = (sig < floor[:, None]).sum(1)
            xs = np.zeros_like(sig); xs[ev] = sig[ev] / med[ev, None]
            a = np.full(len(sig), -1); m = np.full(len(sig), -1); b = np.full(len(sig), -1)
            nz = np.zeros(len(sig), int); info_a = [None] * len(sig)
            if ev.any():
                ae, _, ia = P.count_batch(xs[ev], uh["h_shape"], uh["p_star_all"], uh["m_min"], keep_info=True)
                _, me = P.count_batch(xs[ev], uh["h_shape"], uh["p_star_massive"], uh["m_min"])
                a[ev], m[ev] = ae, me
                for j, i in enumerate(np.where(ev)[0]):
                    info_a[i] = ia[j]
                    b[i] = sum(1 for loc, _, _ in ia[j] if loc >= 0.1)
                    nz[i] = sum(1 for loc, _, _ in ia[j] if loc < 0.1)
            sf = np.stack([z[f"sig_full_{M}"] for z in Ls])
            xf = P.normalise(sf)
            af, _ = P.count_batch(xf, uf["h_shape"], uf["p_star_all"], uf["m_min"])
            _, mf = P.count_batch(xf, uf["h_shape"], uf["p_star_massive"], uf["m_min"])
            keep[(model, tag, M)] = (xs, a, info_a, xf, af, ev)
            for i in range(len(sig)):
                for met, val in (("n_modes_all", a[i]), ("n_modes_massive", m[i]), ("n_modes_bulk", b[i]),
                                 ("n_modes_nearzero", nz[i]), ("rank_collapsed", collapsed[i]),
                                 ("n_sigma_below_floor", n_below_floor[i]), ("precision_floor", floor[i]),
                                 ("median_sigma", med[i]), ("dead_rows_1e-3", dead[1e-3][i]),
                                 ("dead_rows_1e-6", dead[1e-6][i]), ("dead_rows_1e-12", dead[1e-12][i])):
                    rows.append((model, "base", step, i // H, M, i % H, "all", met, float(val), EST))
            for l in range(len(xf)):
                for met, val in (("n_modes_all", af[l]), ("n_modes_massive", mf[l])):
                    rows.append((model, "base", step, l, M, -1, "all", met, float(val), EST))
            n_ev = int(ev.sum())
            v[M] = {
                "n_heads": len(sig), "n_rank_collapsed": int(collapsed.sum()),
                "heads_with_dead_rows": {str(t): int((dead[t] > 0).sum()) for t in dead},
                "dead_rows_total": {str(t): int(dead[t].sum()) for t in dead},
                "per_head_primary": rule_verdict(int((a >= 2).sum()), len(a), 0.10),
                "per_head_primary_over_evaluable": rule_verdict(int((a >= 2).sum()), max(n_ev, 1), 0.10),
                "per_head_secondary_massive": rule_verdict(int((m >= 2).sum()), len(m), 0.10),
                "per_head_bulk_A1": rule_verdict(int((b >= 2).sum()), len(b), 0.10),
                "heads_with_nearzero_mode_A1": int((nz > 0).sum()),
                "full_primary": rule_verdict(int((af >= 2).sum()), len(af), 0.25),
                "full_secondary_massive": rule_verdict(int((mf >= 2).sum()), len(mf), 0.25),
                "unimodal_frac_all": float((a == 1).mean()), "unimodal_frac_massive": float((m == 1).mean()),
                "G4_grid": {"stored": grid[0]["stored"], "unit_roundoff": u,
                            "min_frac_on_bf16": min(g.get("frac_on_bf16_grid", np.nan) for g in grid),
                            "min_frac_on_fp16": min(g.get("frac_on_fp16_grid", np.nan) for g in grid),
                            "heads_with_sigma_below_floor": int((n_below_floor > 0).sum())},
            }
        bulk = any(v[M]["per_head_bulk_A1"]["shows_peaks"] for M in "QKV")
        prim = any(v[M]["per_head_primary"]["shows_peaks"] for M in "QKV")
        sec = any(v[M]["per_head_secondary_massive"]["shows_peaks"] for M in "QKV")
        full = any(v[M]["full_primary"]["shows_peaks"] for M in "QKV")
        if prim and not sec:
            label = "OUTLIER_MODES_ONLY"
        elif prim:
            label = "PEAKS"
        elif full:
            label = "PEAKS_AT_LAYER_UNIT_ONLY"
        else:
            label = "NO_PEAKS"
        v["model_label"] = label
        v["model_label_bulk_A1"] = ("BULK_PEAKS" if bulk else
                                    ("NEAR_ZERO_MODES_ONLY" if prim else "NO_BULK_PEAKS"))
        if tag == "step0":
            v["G0_pass"] = all(v[M]["unimodal_frac_all"] >= 0.985 and v[M]["unimodal_frac_massive"] >= 0.985
                               for M in MATS)
        v["flags"] = S.MODELS[model]["flags"]
        verdict[f"{model}:{tag}:{rev}"] = v
        print(model, tag, label, v["model_label_bulk_A1"],
              {M: dict(prim=v[M]["per_head_primary"]["k"], mass=v[M]["per_head_secondary_massive"]["k"],
                       bulk=v[M]["per_head_bulk_A1"]["k"], nz=v[M]["heads_with_nearzero_mode_A1"],
                       coll=v[M]["n_rank_collapsed"], full=v[M]["full_primary"]["k"]) for M in MATS}, flush=True)

    o = verdict["olmo2-1b:final:main"]["model_label"]
    p = verdict["pythia-1.4b:final:step143000"]["model_label"]
    peaks = lambda lab: lab in ("PEAKS", "PEAKS_AT_LAYER_UNIT_ONLY")
    if not peaks(o):
        dec = "OLMO_NO_PEAKS: aim 1 dropped/deferred; record null replication of Diffract under the sealed criterion"
    elif not peaks(p):
        dec = "OLMO_ONLY: aim 1 proceeds on OLMo; architectural difference is a stated hypothesis"
    else:
        dec = "BOTH: aim 1 trajectory work moves to Pythia"
    g0 = {k: v.get("G0_pass") for k, v in verdict.items() if "step0" in k}
    ob = verdict["olmo2-1b:final:main"]["model_label_bulk_A1"]
    pb = verdict["pythia-1.4b:final:step143000"]["model_label_bulk_A1"]
    if ob != "BULK_PEAKS":
        dec_b = "OLMO_NO_BULK_PEAKS"
    elif pb != "BULK_PEAKS":
        dec_b = "OLMO_ONLY (bulk)"
    else:
        dec_b = "BOTH (bulk): aim 1 trajectory work moves to Pythia"
    verdict["_decision"] = {"olmo_final": o, "pythia_final": p, "stage1_decision": dec, "G0": g0,
                            "olmo_final_bulk_A1": ob, "pythia_final_bulk_A1": pb,
                            "stage1_decision_bulk_A1_posthoc": dec_b,
                            "resolution_note": "per-head criterion resolves narrow peaks separated by >= ~0.12 "
                            "(sigma/median units); full-matrix unit is far coarser (h=%.3f)" % uf["h_shape"]}
    (ROOT / "results").mkdir(exist_ok=True)
    df = pd.DataFrame(rows, columns=["model", "variant", "step", "layer", "matrix", "head", "band", "metric",
                                     "value", "estimator_version"])
    df.to_parquet(ROOT / "results" / "stage1_long.parquet")
    (ROOT / "results" / "stage1_verdict.json").write_text(json.dumps(verdict, indent=1))
    print(json.dumps(verdict["_decision"], indent=1))
    plots(keep, uh, uf)


def plots(keep, uh, uf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = ROOT / "plots"; out.mkdir(exist_ok=True)
    fs_h, lo_h, hi_h, med_h = mp_sigma_pdf(128 / 2048)
    fs_f, lo_f, hi_f, med_f = mp_sigma_pdf(1.0 - 1e-9)
    bins = np.linspace(0, 3, 61)   # FIXED binning in x = sigma/median, all heads
    for (model, tag, M), (xs, a, info, xf, af, ev) in keep.items():
        L = S.MODELS[model]["n_layer"]; H = S.MODELS[model]["n_head"]
        fig, axs = plt.subplots(L, H, figsize=(H * 1.1, L * 0.8), sharex=True)
        sg = np.linspace(lo_h, hi_h, 300)
        for i, x in enumerate(xs):
            ax = axs[i // H, i % H]
            if not ev[i]:
                ax.set_title(f"L{i//H}h{i%H} COLLAPSED", fontsize=4, color="C1", pad=1); ax.set_yticks([])
                continue
            ax.hist(np.clip(x, 0, 3), bins=bins, density=True, color="0.7")
            g, d = P.kde(x, uh["h_shape"])
            ax.plot(g, d, lw=0.6, color="C0" if a[i] < 2 else "C3")
            ax.plot(sg / med_h, [fs_h(s) * med_h for s in sg], lw=0.5, color="k", ls="--")
            ax.set_xlim(0, 3); ax.set_yticks([]); ax.tick_params(labelsize=4)
            if a[i] >= 2:
                ax.set_title(f"L{i//H}h{i%H} m={a[i]}", fontsize=4, color="C3", pad=1)
        fig.suptitle(f"{model} {tag} W_{M} per-head sigma/median (grey: fixed bins; line: sealed KDE, red = >=2 modes; "
                     f"dashed: MP c=1/16 median-matched)", fontsize=7)
        fig.savefig(out / f"stage1_{model}_{tag}_{M}_heads.png", dpi=110); plt.close(fig)
        fig, axs = plt.subplots(1, L, figsize=(L * 1.2, 1.4), sharey=True)
        sg = np.linspace(lo_f + 1e-6, hi_f - 1e-6, 300)
        for l, x in enumerate(xf):
            ax = axs[l]
            ax.hist(np.clip(x, 0, 4), bins=np.linspace(0, 4, 81), density=True, color="0.7")
            g, d = P.kde(x, uf["h_shape"])
            ax.plot(g, d, lw=0.6, color="C0" if af[l] < 2 else "C3")
            ax.plot(sg / med_f, [fs_f(s) * med_f for s in sg], lw=0.5, color="k", ls="--")
            ax.set_xlim(0, 4); ax.set_title(f"L{l}", fontsize=5); ax.tick_params(labelsize=4)
        fig.suptitle(f"{model} {tag} W_{M} full layer matrix", fontsize=7)
        fig.savefig(out / f"stage1_{model}_{tag}_{M}_full.png", dpi=110, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    main()
