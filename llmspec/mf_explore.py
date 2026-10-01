"""mf_explore.py -- EXPLORATORY look at the arm-B multifractality bank (cache/mf, produced by stage3_extract_mf.py).

Impressions only, NO verdicts: every number is paired with (1) the same number on the file's own norm-preserving Gaussian
null draw and (2) the exact Haar expectation for that vector length. A departure the null shares is the norm profile,
not structure. Nothing here is sealed; nothing here promotes or demotes a claim.

Readable models (hard allow-list; everything else is HELD OUT for a later sealed test and is REFUSED):
  pythia-1.4b, pythia-410m-seed1 .. pythia-410m-seed5
Input: <root>/<model>/<rev>/L<layer>.npz, keys per stage3_extract_mf.py's docstring. All shapes (n per side, d_head,
H, bands) are read from the files themselves; mcfg is not consulted.

Per (model, checkpoint, matrix M, side s, index band b):
  mom   mean over the band's vectors of M_q = sum |psi_i|^{2q}, q in q_grid, divided by the exact Haar expectation
        E_Haar[M_q](n) = n * B(q+1/2, (n-1)/2) / B(1/2, (n-1)/2)  (verify_mf_extract.py (a)); trained, null, and
        log(trained/null) with its sd over layers; also the band mean of the per-vector log(M_q / E_Haar).
  box   head-nested side only (u of Q/K/V, v of O): band mean of the per-vector log(box_q(ell) / E_Haar[box_q(ell)]) with
        E_Haar[box_q(ell)](n) = (n/ell) * B(ell/2+q, (n-ell)/2) / B(ell/2, (n-ell)/2); a flat zero line = Haar; a trend
        in ell = scale-dependent concentration; ell = d_head is the head scale. Trained, null, difference, sd over layers.
  head  head-nested side only, from the 16 fp16 subsampled vectors per band: per-head mass mu_h = sum_{i in head h}
        psi_i^2, its max over heads and its Shannon entropy (nats); trained, null, and a seeded Monte-Carlo Haar
        reference (4096 sphere-uniform vectors of the same n, H) -- there is no simple closed form for E[max_h mu_h].
  hist  pooled histogram (over layers) of n*psi_i^2 per band vs the Porter-Thomas chi^2_1 CDF, vs the exact finite-n
        Haar CDF (n*psi^2 ~ n*Beta(1/2,(n-1)/2)) and vs the null's pooled histogram: max |CDF difference| over the 61 log
        bin edges (KS-like), and the tail mass above 10 and 100 (CDF interpolated linearly in log x inside the bin that
        contains the threshold; thresholds are not bin edges).
  normcv coefficient of variation of the row and column norms of W (and of the null draw) -- the norm profile.
Size scaling: log(M_q / E_Haar) vs n for each (M, s, band, q), n = 1024/4096 (410M, mean +- sd over seeds 1-5) and
2048/8192 (1.4B). Seed spread: every quantity for pythia-410m as mean +- sd over the seeds present (>= 2).

Outputs in <out>: mf_explore_<model>.json (+ _seedmean), mom_/box_/head_/hist_/normcv_<model>.csv, scaling.csv,
fig_a_momratio_q{2,4}_<group>.png, fig_b_box_q2_<group>.png, fig_c_tail_<group>.png, SUMMARY.md (top-10 |log
trained/null| per model, numbers only).

Usage: mf_explore.py --root cache/mf --models pythia-1.4b pythia-410m-seed1 ... --out DIR [--revs step0 ...]
       [--layers 0,1,...] [--workers N] [--no-figs]
"""
import os, sys, json, time, argparse, csv
from pathlib import Path
import numpy as np
from scipy.special import betaln, betainc, gammainc, gammaincc

ROOT = Path(__file__).resolve().parent
ALLOW = ("pythia-1.4b",) + tuple(f"pythia-410m-seed{k}" for k in range(1, 6))
SEEDS = tuple(f"pythia-410m-seed{k}" for k in range(1, 6))
MATS = ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")
SIDES = ("u", "v")
NESTED_SIDE = {"Q": "u", "K": "u", "V": "u", "O": "v"}
SIDE_CLASS = {("Q", "u"): "head", ("K", "u"): "head", ("V", "u"): "head", ("O", "v"): "head",
              ("Q", "v"): "residual", ("K", "v"): "residual", ("V", "v"): "residual", ("O", "u"): "residual",
              ("MLP_IN", "v"): "residual", ("MLP_OUT", "u"): "residual",
              ("MLP_IN", "u"): "hidden", ("MLP_OUT", "v"): "hidden"}
TAILS = (10.0, 100.0)
HEAD_MC_N = 4096
HEAD_MC_SEED = 20261001
HAAR_REF = {"mom": "E_Haar[M_q](n) = n * B(q+1/2,(n-1)/2) / B(1/2,(n-1)/2)",
            "box": "E_Haar[box_q(ell)](n) = (n/ell) * B(ell/2+q,(n-ell)/2) / B(ell/2,(n-ell)/2)",
            "hist": "n*psi^2 ~ n*Beta(1/2,(n-1)/2) exactly; Porter-Thomas chi^2_1 is its large-n limit",
            "head": f"Monte Carlo, {HEAD_MC_N} sphere-uniform vectors, seed {HEAD_MC_SEED}"}


# ---------------------------------------------------------------- allow-list, schedule
def check_models(models):
    bad = [m for m in models if m not in ALLOW]
    if bad:
        raise SystemExit(f"REFUSED: {bad} not in the allow-list {list(ALLOW)} (held out for a later sealed test)")


def step_of(rev):
    return int(rev[4:]) if rev.startswith("step") and rev[4:].isdigit() else -1


def schedule_revs():
    p = ROOT / "pythia_1.4b_schedule.txt"
    revs = p.read_text().split() if p.exists() else []
    return sorted(revs, key=step_of)


# ---------------------------------------------------------------- exact references
def E_mom(q, n):
    q = np.asarray(q, dtype=np.float64)
    return n * np.exp(betaln(q + 0.5, (n - 1) / 2) - betaln(0.5, (n - 1) / 2))


def E_box(q, n, ell):
    q = np.asarray(q, dtype=np.float64)
    return (n / ell) * np.exp(betaln(ell / 2 + q, (n - ell) / 2) - betaln(ell / 2, (n - ell) / 2))


def cdf_pt(x):
    return gammainc(0.5, np.asarray(x, dtype=np.float64) / 2)


def cdf_exact(x, n):
    return betainc(0.5, (n - 1) / 2, np.clip(np.asarray(x, dtype=np.float64) / n, 0, 1))


def sf_pt(x):
    """1 - cdf_pt without cancellation (P(chi^2_1 > 100) = 1.5e-23)."""
    return gammaincc(0.5, np.asarray(x, dtype=np.float64) / 2)


def sf_exact(x, n):
    return betainc((n - 1) / 2, 0.5, 1 - np.clip(np.asarray(x, dtype=np.float64) / n, 0, 1))


_HEAD_MC = {}


def head_mc_ref(n, H):
    """Haar reference for the per-head mass statistics: (mean max_h mu_h, mean entropy) over HEAD_MC_N vectors."""
    if (n, H) not in _HEAD_MC:
        rng = np.random.default_rng(HEAD_MC_SEED)
        tot = np.zeros(2)
        for _ in range(4):                       # 4 chunks of HEAD_MC_N/4 to bound memory at n = 8192
            g = rng.standard_normal((HEAD_MC_N // 4, n))
            p = g * g
            p /= p.sum(1, keepdims=True)
            mu = p.reshape(len(g), H, n // H).sum(2)
            tot += [mu.max(1).sum(), (-(mu * np.log(mu))).sum()]
        _HEAD_MC[(n, H)] = tot / HEAD_MC_N
    return _HEAD_MC[(n, H)]


def band_labels(edges):
    return ["spike" if b == 0 else f"{edges[b]}-{edges[b + 1]}" for b in range(len(edges) - 1)]


# ---------------------------------------------------------------- one layer file
def head_stats(sub, H):
    """sub (nb, 16, n) f16 -> (nb, 2): mean over valid vectors of (max_h mu_h, entropy of mu_h)."""
    x = sub.astype(np.float64)
    nrm = np.sqrt((x * x).sum(2))
    valid = nrm > 0.5
    out = np.full((sub.shape[0], 2), np.nan)
    for b in range(sub.shape[0]):
        v = valid[b]
        if not v.any():
            continue
        p = (x[b, v] / nrm[b, v][:, None]) ** 2
        mu = p.reshape(v.sum(), H, -1).sum(2)
        ent = -(np.where(mu > 0, mu * np.log(np.where(mu > 0, mu, 1)), 0)).sum(1)
        out[b] = [mu.max(1).mean(), ent.mean()]
    return out


def side_layer(z, M, s, suffix, edges, q):
    mom = z[f"mom_{s}_{M}{suffix}"].astype(np.float64)              # (r, 7)
    sub = z[f"sub_{s}_{M}{suffix}"]                                 # (nb, 16, n) f16
    n, nb = sub.shape[2], len(edges) - 1
    Em = E_mom(q, n)
    d = {"n": n,
         "mom": np.stack([mom[edges[b]:edges[b + 1]].mean(0) for b in range(nb)]),
         "mom_log": np.stack([np.log(mom[edges[b]:edges[b + 1]] / Em).mean(0) for b in range(nb)]),
         "hist": z[f"hist_{s}_{M}{suffix}"].astype(np.int64), "histof": z[f"histof_{s}_{M}{suffix}"].astype(np.int64)}
    if NESTED_SIDE.get(M) == s:
        ells = z["box_ell"].astype(int)
        box = z[f"box_{s}_{M}{suffix}"].astype(np.float64)          # (r, 4, 7)
        Eb = np.stack([E_box(q, n, ell) for ell in ells])           # (4, 7)
        d["box"] = np.stack([np.log(box[edges[b]:edges[b + 1]] / Eb).mean(0) for b in range(nb)])
        d["head"] = head_stats(sub, n // int(ells[-1]))
    return d


def layer_stats(path):
    z = np.load(path)
    edges = z["band_edges"].astype(int)
    q = z["q_grid"].astype(np.float64)
    out = {"edges": edges, "q": q, "box_ell": z["box_ell"].astype(int), "hist_edges": z["hist_edges"].astype(np.float64),
           "mats": {}}
    for M in MATS:
        m = {}
        for suf, tag in (("", "t"), ("_null", "n")):
            rn, cn = z[f"rownorm_{M}{suf}"], z[f"colnorm_{M}{suf}"]
            m[f"normcv_{tag}"] = np.array([rn.std() / rn.mean(), cn.std() / cn.mean()])
            for s in SIDES:
                m[(s, tag)] = side_layer(z, M, s, suf, edges, q)
        out["mats"][M] = m
    return out


# ---------------------------------------------------------------- one checkpoint (all layers): pool + derive
def hist_derived(hist, histof, hist_edges, n, hist_null, histof_null):
    """Per band: counts, KS-like max |CDF diff| vs PT / exact / null, tail masses above TAILS (trained, null, refs)."""
    nb = hist.shape[0]
    e = hist_edges
    le = np.log(e)
    F_pt, F_ex = cdf_pt(e), cdf_exact(e, n)
    out = {"count": np.zeros(nb), "ks_pt_t": np.zeros(nb), "ks_exact_t": np.zeros(nb), "ks_null": np.zeros(nb),
           "ks_pt_n": np.zeros(nb), "ks_exact_n": np.zeros(nb), "tail_t": np.zeros((nb, len(TAILS))),
           "tail_n": np.zeros((nb, len(TAILS))),
           "tail_pt": np.array([sf_pt(t) for t in TAILS]), "tail_exact": np.array([sf_exact(t, n) for t in TAILS])}

    def cdf(h, of):
        N = of[0] + h.sum() + of[1]
        return (of[0] + np.concatenate([[0], np.cumsum(h)])) / max(N, 1), N

    for b in range(nb):
        Ft, Nt = cdf(hist[b], histof[b])
        Fn, Nn = cdf(hist_null[b], histof_null[b])
        out["count"][b] = Nt
        out["ks_pt_t"][b], out["ks_exact_t"][b] = np.abs(Ft - F_pt).max(), np.abs(Ft - F_ex).max()
        out["ks_pt_n"][b], out["ks_exact_n"][b] = np.abs(Fn - F_pt).max(), np.abs(Fn - F_ex).max()
        out["ks_null"][b] = np.abs(Ft - Fn).max()
        for j, t in enumerate(TAILS):
            out["tail_t"][b, j] = 1 - np.interp(np.log(t), le, Ft)
            out["tail_n"][b, j] = 1 - np.interp(np.log(t), le, Fn)
    return out


def ckpt_stats(root, model, rev, layers=None):
    d = Path(root) / model / rev
    files = sorted(d.glob("L*.npz"))
    if layers is not None:
        files = [f for f in files if int(f.stem[1:]) in layers]
    if not files:
        return None
    L = [layer_stats(f) for f in files]
    q, edges, ells = L[0]["q"], L[0]["edges"], L[0]["box_ell"]
    res = {"model": model, "rev": rev, "step": step_of(rev), "n_layers": len(files), "done": (d / "DONE").exists(),
           "layers": [int(f.stem[1:]) for f in files], "q": q, "edges": edges, "bands": band_labels(edges),
           "box_ell": ells, "mats": {}}
    for M in MATS:
        m = {"normcv_t": np.mean([l["mats"][M]["normcv_t"] for l in L], 0),
             "normcv_n": np.mean([l["mats"][M]["normcv_n"] for l in L], 0)}
        for s in SIDES:
            T = [l["mats"][M][(s, "t")] for l in L]
            N = [l["mats"][M][(s, "n")] for l in L]
            n = T[0]["n"]
            Em = E_mom(q, n)
            momT, momN = np.stack([t["mom"] for t in T]), np.stack([t["mom"] for t in N])      # (nL, nb, 7)
            o = {"n": n, "class": SIDE_CLASS[(M, s)], "E_mom": Em,
                 "mom_trained": momT.mean(0) / Em, "mom_null": momN.mean(0) / Em,
                 "log_tn": np.log(momT.mean(0) / momN.mean(0)),
                 "log_tn_layer_sd": np.log(momT / momN).std(0, ddof=1) if len(L) > 1 else np.zeros(momT.shape[1:]),
                 "mom_logmean_trained": np.mean([t["mom_log"] for t in T], 0),
                 "mom_logmean_null": np.mean([t["mom_log"] for t in N], 0)}
            if "box" in T[0]:
                bT, bN = np.stack([t["box"] for t in T]), np.stack([t["box"] for t in N])
                o.update({"E_box": np.stack([E_box(q, n, ell) for ell in ells]), "box_trained": bT.mean(0),
                          "box_null": bN.mean(0), "box_diff": (bT - bN).mean(0),
                          "box_diff_layer_sd": (bT - bN).std(0, ddof=1) if len(L) > 1 else np.zeros(bT.shape[1:])})
                hT, hN = np.stack([t["head"] for t in T]), np.stack([t["head"] for t in N])
                H = n // int(ells[-1])
                mc = head_mc_ref(n, H)
                o.update({"H": H, "DH": int(ells[-1]), "head_max_trained": np.nanmean(hT[:, :, 0], 0),
                          "head_max_null": np.nanmean(hN[:, :, 0], 0), "head_max_haar_mc": mc[0],
                          "head_ent_trained": np.nanmean(hT[:, :, 1], 0), "head_ent_null": np.nanmean(hN[:, :, 1], 0),
                          "head_ent_haar_mc": mc[1], "head_ent_max": float(np.log(H))})
            hist = sum(t["hist"] for t in T); histof = sum(t["histof"] for t in T)
            histn = sum(t["hist"] for t in N); histofn = sum(t["histof"] for t in N)
            o["hist"] = hist_derived(hist, histof, L[0]["hist_edges"], n, histn, histofn)
            m[s] = o
        res["mats"][M] = m
    return res


def _job(args):
    root, model, rev, layers = args
    t0 = time.time()
    r = ckpt_stats(root, model, rev, layers)
    return model, rev, r, time.time() - t0


# ---------------------------------------------------------------- seed mean
def seed_mean(per_seed):
    """per_seed: {model: {rev: res}} -> {rev: res} with every float array replaced by its seed mean and a '<key>_sd'."""
    models = sorted(per_seed)
    revs = sorted(set.intersection(*[set(per_seed[m]) for m in models]), key=step_of)
    out = {}
    for rev in revs:
        R = [per_seed[m][rev] for m in models]
        base = R[0]
        res = {k: base[k] for k in ("step", "q", "edges", "bands", "box_ell")}
        res.update({"model": "pythia-410m-seedmean", "rev": rev, "seeds": models, "n_seeds": len(models),
                    "n_layers": base["n_layers"], "mats": {}})
        for M in MATS:
            m = {}
            for key in ("normcv_t", "normcv_n"):
                a = np.stack([r["mats"][M][key] for r in R]); m[key], m[key + "_sd"] = a.mean(0), a.std(0, ddof=1)
            for s in SIDES:
                o = {}
                for key, val in base["mats"][M][s].items():
                    vals = [r["mats"][M][s][key] for r in R]
                    if key == "hist":
                        h = {}
                        for hk in val:
                            a = np.stack([v[hk] for v in vals]); h[hk], h[hk + "_sd"] = a.mean(0), a.std(0, ddof=1)
                        o["hist"] = h
                    elif isinstance(val, (np.ndarray, float)) and not key.startswith("E_") and not key.endswith("haar_mc") \
                            and key not in ("head_ent_max",):
                        a = np.stack([np.asarray(v, dtype=np.float64) for v in vals])
                        o[key], o[key + "_sd"] = a.mean(0), a.std(0, ddof=1)
                    else:
                        o[key] = val
                m[s] = o
            res["mats"][M] = m
        out[rev] = res
    return out


# ---------------------------------------------------------------- writers
def _j(x):
    if isinstance(x, dict):
        return {str(k): _j(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_j(v) for v in x]
    if isinstance(x, np.ndarray):
        return _j(x.tolist())
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(f"{x:.7g}")
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def write_json(path, model, revs, extra=None):
    doc = {"model": model, "haar_reference": HAAR_REF, "tails": list(TAILS), "revs": {rev: revs[rev] for rev in revs}}
    if extra:
        doc.update(extra)
    path.write_text(json.dumps(_j(doc), indent=1))


def _row(o, key, idx, sd=False):
    a = o.get(key + "_sd" if sd else key)
    if a is None:
        return ""
    a = np.asarray(a)
    v = a[idx] if a.ndim else a
    return "" if not np.isfinite(v) else f"{float(v):.7g}"


def write_csvs(out, model, revs, seedmean=False):
    sd = seedmean
    rows = {"mom": [], "box": [], "head": [], "hist": [], "normcv": []}
    for rev, r in sorted(revs.items(), key=lambda kv: step_of(kv[0])):
        q, bands, ells = r["q"], r["bands"], r["box_ell"]
        for M in MATS:
            m = r["mats"][M]
            rows["normcv"].append({"rev": rev, "step": r["step"], "M": M, "rownorm_cv": _row(m, "normcv_t", 0),
                                   "colnorm_cv": _row(m, "normcv_t", 1), "rownorm_cv_null": _row(m, "normcv_n", 0),
                                   "colnorm_cv_null": _row(m, "normcv_n", 1)})
            for s in SIDES:
                o = m[s]
                common = {"rev": rev, "step": r["step"], "M": M, "side": s, "class": o["class"], "n": o["n"]}
                for b, band in enumerate(bands):
                    for i, qq in enumerate(q):
                        row = {**common, "band": band, "q": qq, "haar_E_mom": f"{o['E_mom'][i]:.7g}",
                               "trained_over_haar": _row(o, "mom_trained", (b, i)), "null_over_haar": _row(o, "mom_null", (b, i)),
                               "log_trained_over_null": _row(o, "log_tn", (b, i)), "log_tn_layer_sd": _row(o, "log_tn_layer_sd", (b, i)),
                               "logmean_trained": _row(o, "mom_logmean_trained", (b, i)), "logmean_null": _row(o, "mom_logmean_null", (b, i))}
                        if sd:
                            row.update({"log_tn_seed_sd": _row(o, "log_tn", (b, i), True), "trained_over_haar_seed_sd": _row(o, "mom_trained", (b, i), True),
                                        "null_over_haar_seed_sd": _row(o, "mom_null", (b, i), True), "n_seeds": r["n_seeds"]})
                        rows["mom"].append(row)
                    if "box_trained" in o:
                        for a, ell in enumerate(ells):
                            for i, qq in enumerate(q):
                                row = {**common, "band": band, "ell": int(ell), "q": qq, "haar_E_box": f"{o['E_box'][a, i]:.7g}",
                                       "logdep_trained": _row(o, "box_trained", (b, a, i)), "logdep_null": _row(o, "box_null", (b, a, i)),
                                       "diff": _row(o, "box_diff", (b, a, i)), "diff_layer_sd": _row(o, "box_diff_layer_sd", (b, a, i))}
                                if sd:
                                    row["diff_seed_sd"] = _row(o, "box_diff", (b, a, i), True)
                                rows["box"].append(row)
                        row = {**common, "band": band, "H": o["H"], "DH": o["DH"],
                               "headmax_trained": _row(o, "head_max_trained", b), "headmax_null": _row(o, "head_max_null", b),
                               "headmax_haar_mc": f"{o['head_max_haar_mc']:.7g}", "ent_trained": _row(o, "head_ent_trained", b),
                               "ent_null": _row(o, "head_ent_null", b), "ent_haar_mc": f"{o['head_ent_haar_mc']:.7g}",
                               "ent_max_logH": f"{o['head_ent_max']:.7g}"}
                        if sd:
                            row.update({"headmax_trained_seed_sd": _row(o, "head_max_trained", b, True), "ent_trained_seed_sd": _row(o, "head_ent_trained", b, True)})
                        rows["head"].append(row)
                    h = o["hist"]
                    row = {**common, "band": band, "count": _row(h, "count", b), "ks_pt_trained": _row(h, "ks_pt_t", b),
                           "ks_exact_trained": _row(h, "ks_exact_t", b), "ks_trained_vs_null": _row(h, "ks_null", b),
                           "ks_pt_null": _row(h, "ks_pt_n", b), "ks_exact_null": _row(h, "ks_exact_n", b)}
                    for j, t in enumerate(TAILS):
                        row.update({f"tail{t:g}_trained": _row(h, "tail_t", (b, j)), f"tail{t:g}_null": _row(h, "tail_n", (b, j)),
                                    f"tail{t:g}_pt": f"{h['tail_pt'][j]:.4g}", f"tail{t:g}_exact": f"{h['tail_exact'][j]:.4g}"})
                        if sd:
                            row[f"tail{t:g}_trained_seed_sd"] = _row(h, "tail_t", (b, j), True)
                    rows["hist"].append(row)
    for name, rr in rows.items():
        if rr:
            with open(out / f"{name}_{model}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rr[0]))
                w.writeheader(); w.writerows(rr)


def write_scaling(out, groups):
    """groups: {label: {rev: res}} (seedmean carries _sd). One row per (rev, M, side, band, q, group)."""
    rr = []
    for label, revs in groups.items():
        for rev, r in sorted(revs.items(), key=lambda kv: step_of(kv[0])):
            for M in MATS:
                for s in SIDES:
                    o = r["mats"][M][s]
                    for b, band in enumerate(r["bands"]):
                        for i, qq in enumerate(r["q"]):
                            rr.append({"group": label, "rev": rev, "step": r["step"], "M": M, "side": s, "class": o["class"],
                                       "n": o["n"], "log_n": f"{np.log(o['n']):.6g}", "band": band, "q": qq,
                                       "log_trained_over_haar": f"{np.log(o['mom_trained'][b, i]):.7g}",
                                       "log_trained_over_haar_seed_sd": (f"{o['mom_trained_sd'][b, i] / o['mom_trained'][b, i]:.4g}"
                                                                         if "mom_trained_sd" in o else ""),
                                       "log_null_over_haar": f"{np.log(o['mom_null'][b, i]):.7g}",
                                       "log_trained_over_null": f"{o['log_tn'][b, i]:.7g}",
                                       "log_trained_over_null_seed_sd": _row(o, "log_tn", (b, i), True),
                                       "n_seeds": r.get("n_seeds", 1)})
    with open(out / "scaling.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rr[0])); w.writeheader(); w.writerows(rr)


def write_summary(out, groups, notes):
    lines = ["# mf_explore SUMMARY (numbers only; exploratory; no verdicts)", "",
             f"Haar reference for moments: {HAAR_REF['mom']}. Entries are the 10 largest |log(trained/null)| of the band-mean",
             "M_q over (matrix, side, band, q != 1, checkpoint); trained/Haar and null/Haar are the band means divided by",
             "E_Haar[M_q](n). Seed-mean rows carry +- sd over seeds.", ""]
    lines += [f"- {n}" for n in notes] + [""]
    for label, revs in groups.items():
        ent = []
        for rev, r in revs.items():
            for M in MATS:
                for s in SIDES:
                    o = r["mats"][M][s]
                    for b, band in enumerate(r["bands"]):
                        for i, qq in enumerate(r["q"]):
                            if qq == 1.0:
                                continue
                            v = o["log_tn"][b, i]
                            if np.isfinite(v):
                                ent.append((abs(v), v, M, s, band, qq, rev, o["n"], o["E_mom"][i], o["mom_trained"][b, i],
                                            o["mom_null"][b, i], o.get("log_tn_sd", np.full(o["log_tn"].shape, np.nan))[b, i]))
        ent.sort(key=lambda e: -e[0])
        lines += [f"## {label}  ({len(revs)} checkpoints: {', '.join(sorted(revs, key=step_of))})", "",
                  "| rank | matrix | side | band | q | step | log(trained/null) | trained/Haar | null/Haar | E_Haar[M_q] | n |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for k, e in enumerate(ent[:10], 1):
            sd = "" if not np.isfinite(e[11]) else f" +- {e[11]:.3f}"
            lines.append(f"| {k} | {e[2]} | {e[3]} | {e[4]} | {e[5]:g} | {e[6]} | {e[1]:+.4f}{sd} | {e[9]:.4g} | {e[10]:.4g} | {e[8]:.4g} | {e[7]} |")
        lines.append("")
    (out / "SUMMARY.md").write_text("\n".join(lines))


# ---------------------------------------------------------------- figures (matplotlib Agg; one axis per panel)
BAND_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    return plt, LinearSegmentedColormap.from_list("blue_seq", SEQ), Normalize


def fig_a(out, label, revs, qi, qv):
    plt, cmap, Normalize = _mpl()
    order = sorted(revs, key=step_of)
    steps = np.array([step_of(r) for r in order], dtype=float)
    norm = Normalize(0, np.log10(steps.max() + 1))
    fig, axes = plt.subplots(2, 6, figsize=(20, 8), sharey="row")
    fig.subplots_adjust(left=0.05, right=0.92, top=0.9, bottom=0.12, hspace=0.55, wspace=0.15)
    for j, M in enumerate(MATS):
        for i, s in enumerate(SIDES):
            ax = axes[i, j]
            for rev in order:
                o = revs[rev]["mats"][M][s]
                y = o["log_tn"][:, qi]
                ax.plot(range(len(y)), y, "-o", ms=3, lw=1.5, color=cmap(norm(np.log10(step_of(rev) + 1))))
                if "log_tn_sd" in o:
                    ax.fill_between(range(len(y)), y - o["log_tn_sd"][:, qi], y + o["log_tn_sd"][:, qi],
                                    color=cmap(norm(np.log10(step_of(rev) + 1))), alpha=0.12, lw=0)
            ax.axhline(0, color="#888", lw=0.8)
            bands = revs[order[0]]["bands"]
            ax.set_xticks(range(len(bands))); ax.set_xticklabels(bands, rotation=45, fontsize=7, ha="right")
            ax.set_title(f"{M}  side {s} ({o['class']}, n={o['n']})", fontsize=9)
            if i == 1:
                ax.set_xlabel("index band")
            if j == 0:
                ax.set_ylabel(f"log(trained/null) band-mean M_{qv:g}")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
    cb = fig.colorbar(sm, ax=axes.ravel().tolist(), fraction=0.02, pad=0.01)
    cb.set_label("log10(step + 1)")
    fig.suptitle(f"{label}: log(trained / null) of the band-mean M_q, q={qv:g}, vs index band  (0 = Haar-identical to the null)", fontsize=11)
    fig.savefig(out / f"fig_a_momratio_q{qv:g}_{label}.png", dpi=110)
    plt.close(fig)


def fig_b(out, label, revs, qi=3):
    plt, cmap, Normalize = _mpl()
    order = sorted(revs, key=step_of)
    pick = [r for r in order if r in ("step0", "step512", "step4000", "step143000")] or order[:4]
    if len(pick) < 2 and len(order) >= 2:
        pick = [order[0], order[-1]]
    nested = [M for M in MATS if M in NESTED_SIDE]
    fig, axes = plt.subplots(len(pick), len(nested), figsize=(4.2 * len(nested), 3.2 * len(pick)), squeeze=False, sharey=True)
    for i, rev in enumerate(pick):
        for j, M in enumerate(nested):
            ax = axes[i, j]
            o = revs[rev]["mats"][M][NESTED_SIDE[M]]
            ells = revs[rev]["box_ell"]
            for b, band in enumerate(revs[rev]["bands"]):
                c = BAND_COLORS[b % len(BAND_COLORS)]
                ax.plot(ells, o["box_trained"][b, :, qi], "-o", ms=3, lw=1.5, color=c, label=band if (i == 0 and j == 0) else None)
                ax.plot(ells, o["box_null"][b, :, qi], "--", lw=1, color=c, alpha=0.7)
            ax.axhline(0, color="#888", lw=0.8)
            ax.set_xscale("log", base=2); ax.set_xticks(ells); ax.set_xticklabels([str(int(e)) for e in ells])
            ax.set_title(f"{M} side {NESTED_SIDE[M]}  {rev}", fontsize=9)
            if i == len(pick) - 1:
                ax.set_xlabel("box size ell (last = d_head)")
            if j == 0:
                ax.set_ylabel("band-mean log(box_2 / Haar)")
    axes[0, 0].legend(fontsize=7, title="band (solid trained, dashed null)", ncol=2)
    fig.suptitle(f"{label}: head-nested side box-moment departure from Haar at q=2 vs box size", fontsize=11)
    fig.tight_layout()
    fig.savefig(out / f"fig_b_box_q2_{label}.png", dpi=110)
    plt.close(fig)


def fig_c(out, label, revs, j=0):
    plt, cmap, Normalize = _mpl()
    order = sorted(revs, key=step_of)
    steps = np.array([step_of(r) for r in order], dtype=float)
    from matplotlib.ticker import NullLocator
    fig, axes = plt.subplots(2, 6, figsize=(20, 8), sharey=True)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.17, hspace=0.4, wspace=0.12)
    kmax = int(np.ceil(np.log10(max(steps.max(), 10))))
    for jj, M in enumerate(MATS):
        for i, s in enumerate(SIDES):
            ax = axes[i, jj]
            bands = revs[order[0]]["bands"]
            for b, band in enumerate(bands):
                c = BAND_COLORS[b % len(BAND_COLORS)]
                yt = np.array([revs[r]["mats"][M][s]["hist"]["tail_t"][b, j] for r in order])
                yn = np.array([revs[r]["mats"][M][s]["hist"]["tail_n"][b, j] for r in order])
                ax.plot(steps, yt, "-o", ms=3, lw=1.5, color=c, label=band if (i == 0 and jj == 0) else None)
                ax.plot(steps, yn, "--", lw=1, color=c, alpha=0.7)
                if "tail_t_sd" in revs[order[0]]["mats"][M][s]["hist"]:
                    sd = np.array([revs[r]["mats"][M][s]["hist"]["tail_t_sd"][b, j] for r in order])
                    ax.fill_between(steps, yt - sd, yt + sd, color=c, alpha=0.12, lw=0)
            o = revs[order[0]]["mats"][M][s]
            ax.axhline(o["hist"]["tail_pt"][j], color="#555", lw=0.8, ls=":")
            ax.set_xscale("symlog", linthresh=1); ax.set_yscale("log")
            ax.set_xticks([0] + [10 ** k for k in range(kmax + 1)])
            ax.set_xticklabels(["0"] + [f"1e{k}" for k in range(kmax + 1)], fontsize=7)
            ax.xaxis.set_minor_locator(NullLocator())
            ax.set_title(f"{M} side {s} ({o['class']}, n={o['n']})", fontsize=9)
            if i == 1:
                ax.set_xlabel("step")
            if jj == 0:
                ax.set_ylabel(f"fraction of entries with n*psi^2 > {TAILS[j]:g}")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=min(len(l), 8), fontsize=8, title="index band (solid trained, dashed null, dotted Porter-Thomas)")
    fig.suptitle(f"{label}: fraction of entries with n*psi^2 above {TAILS[j]:g} vs training step", fontsize=11)
    fig.savefig(out / f"fig_c_tail_{label}.png", dpi=110)
    plt.close(fig)


def make_figs(out, label, revs):
    if not revs:
        return
    q = list(np.round(revs[next(iter(revs))]["q"], 3))
    for qv in (2.0, 4.0):
        if qv in q:
            fig_a(out, label, revs, q.index(qv), qv)
    fig_b(out, label, revs, q.index(2.0) if 2.0 in q else 0)
    fig_c(out, label, revs)


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", required=True, help="cache/mf root")
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--revs", nargs="*", default=None, help="default: the 26 schedule steps that exist under <root>/<model>")
    ap.add_argument("--layers", type=str, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-figs", action="store_true")
    a = ap.parse_args(argv)
    check_models(a.models)
    root, out = Path(a.root), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    layers = [int(x) for x in a.layers.split(",")] if a.layers else None
    sched = a.revs if a.revs else schedule_revs()
    jobs, notes = [], []
    for m in a.models:
        have = [r for r in sched if (root / m / r).is_dir()] if sched else sorted((p.name for p in (root / m).glob("step*")), key=step_of)
        if not sched:
            notes.append(f"{m}: no schedule file; revisions taken from the directory listing")
        missing = [r for r in sched if r not in have]
        if missing:
            notes.append(f"{m}: {len(missing)} schedule revisions absent under {root}: {missing}")
        jobs += [(str(root), m, r, layers) for r in have]
    print(f"{len(jobs)} (model, rev) jobs, workers {a.workers}", flush=True)
    results = {m: {} for m in a.models}
    t0 = time.time()
    if a.workers > 1 and len(jobs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.workers) as pool:
            it = pool.imap_unordered(_job, jobs)
            for model, rev, r, dt in it:
                if r is not None:
                    results[model][rev] = r
                    print(f"  {model} {rev}: {r['n_layers']} layers{'' if r['done'] else ' (DONE absent)'} {dt:.1f}s", flush=True)
    else:
        for job in jobs:
            model, rev, r, dt = _job(job)
            if r is not None:
                results[model][rev] = r
                print(f"  {model} {rev}: {r['n_layers']} layers{'' if r['done'] else ' (DONE absent)'} {dt:.1f}s", flush=True)
    wall = time.time() - t0
    n_ck = sum(len(v) for v in results.values())
    notes.append(f"{n_ck} checkpoints processed in {wall:.1f}s wall ({wall / max(n_ck, 1):.2f}s per checkpoint at workers={a.workers})")
    for m, revs in results.items():
        for rev, r in revs.items():
            if not r["done"]:
                notes.append(f"{m} {rev}: DONE marker absent; {r['n_layers']} layer files used")
    groups = {}
    for m, revs in results.items():
        if revs:
            write_json(out / f"mf_explore_{m}.json", m, revs)
            write_csvs(out, m, revs)
            groups[m] = revs
    seeds = {m: results[m] for m in SEEDS if results.get(m)}
    if len(seeds) >= 2:
        sm = seed_mean(seeds)
        if sm:
            write_json(out / "mf_explore_pythia-410m-seedmean.json", "pythia-410m-seedmean", sm,
                       {"seeds": sorted(seeds), "sd": "sample sd over seeds (ddof=1) in every '<key>_sd'"})
            write_csvs(out, "pythia-410m-seedmean", sm, seedmean=True)
            groups["pythia-410m-seedmean"] = sm
    elif seeds:
        notes.append(f"only {len(seeds)} 410M seed(s) present: no seed mean")
    if groups:
        scal = {k: v for k, v in groups.items() if k in ("pythia-1.4b", "pythia-410m-seedmean")} or groups
        write_scaling(out, scal)
        write_summary(out, groups, notes)
        if not a.no_figs:
            for label, revs in groups.items():
                if label in SEEDS and "pythia-410m-seedmean" in groups:
                    continue              # individual seeds are summarised by the seed mean
                make_figs(out, label, revs)
    print("\n".join(notes), flush=True)
    print(f"wrote {sorted(p.name for p in out.iterdir())}", flush=True)
    return results


if __name__ == "__main__":
    main()
