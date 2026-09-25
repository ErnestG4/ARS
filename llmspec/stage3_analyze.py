"""Stage 3 analysis (STAGE3_PREREG.md; sealed 0cf53ba, pre-data amendment A0 in 76052ed).

Reads cache/s3/pythia-1.4b/<rev>/{L*.npz, GLOBAL.npz, MARKERS.npz} and results/stage3_witness.json.
Writes results/stage3_long.parquet (G5 columns), results/stage3_null.json (the sealed-null cell table + G0 +
G4 flags), results/stage3_changepoints.json, plots/stage3_*.png. Revisions without a DONE marker are skipped
and listed, never silently dropped.
"""
import json, sys, math
from pathlib import Path
from multiprocessing import Pool
import numpy as np
import pandas as pd
import s3stats as S

ROOT = Path(__file__).resolve().parent
MODEL = "pythia-1.4b"
SCHED = open(ROOT / "pythia_1.4b_schedule.txt").read().split()
FULL = {"Q": (2048, 2048), "K": (2048, 2048), "V": (2048, 2048), "O": (2048, 2048),
        "MLP_IN": (8192, 2048), "MLP_OUT": (2048, 8192)}
HEADS = ["Q", "K", "V", "O"]
TOL_RT, TOL_Q = 0.010, 0.10
EST = {"local": S.EST, "mp": "mp_fit_v1", "mle": "htsr_mle_v1", "liu": "liu_rankslope_v1",
       "vec": "vec_band_v1", "circ": "circuit_v1", "mk": "stage3-markers-v1"}
rows = []
import os
TAG = os.environ.get("STAGE3_TAG", "")      # e.g. "_early": writes results/stage3_*_early.* instead of the final files


def step_of(rev):
    return int(rev.replace("step", ""))


def put(rev, layer, matrix, head, band, metric, value, est):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return
    rows.append((MODEL, "base", step_of(rev), layer, matrix, head, band, metric, float(value), est))


def load(rev):
    d = ROOT / "cache" / "s3" / MODEL / rev
    if not (d / "DONE").exists():
        return None
    return {"L": [np.load(d / f"L{l:02d}.npz") for l in range(24)], "G": np.load(d / "GLOBAL.npz"),
            "MK": np.load(d / "MARKERS.npz")}


# ---------------- global estimators ----------------
def mp_cdf(c):
    a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    g = np.linspace(a, b, 40001)
    f = np.sqrt(np.clip((b - g) * (g - a), 0, None)) / (2 * np.pi * c * g + 1e-300)
    F = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(g))]); F /= F[-1]
    return g, F


def mp_fit_v1(sig, m, n, rms, tau_p, tau_m):
    """Scale from rms, iterate out the upper outliers, count departures at both edges."""
    s = rms
    fro2 = float((sig ** 2).sum())
    for _ in range(100):
        Ep = s * (np.sqrt(m) + np.sqrt(n))
        out = sig > tau_p * Ep
        s_new = math.sqrt(max(fro2 - float((sig[out] ** 2).sum()), 1e-300) / (m * n))
        if abs(s_new - s) <= 1e-12 * s:
            break
        s = s_new
    Ep = s * (np.sqrt(m) + np.sqrt(n)); Em = s * abs(np.sqrt(m) - np.sqrt(n))
    res = {"mp_scale": s, "n_upper_outliers": int((sig > tau_p * Ep).sum()), "sigma_max_over_Eplus": float(sig.max() / Ep)}
    if Em > 0 and tau_m is not None:
        res["n_lower_departures"] = int((sig < tau_m * Em).sum())
        res["sigma_min_over_Eminus"] = float(sig.min() / Em)
    else:   # square: KS of the lowest 10% against the MP law conditioned on its lowest 10%
        nmax, nmin = max(m, n), min(m, n)
        g, F = mp_cdf(nmin / nmax)
        x = np.sort(sig ** 2 / (nmax * s * s))
        k = max(1, int(0.10 * len(x)))
        xl = x[:k]
        q10 = np.interp(0.10, F, g)
        Fc = np.clip(np.interp(xl, g, F) / 0.10, 0, 1)
        i = np.arange(1, k + 1)
        res["lower10_ks"] = float(max((i / k - Fc).max(), (Fc - (i - 1) / k).max()))
        res["lower10_frac_below_mp_q10"] = float((x < q10).mean())
    return res


def mp_fit_v2(sig, m, n, tau_p, tau_m):
    """POST-HOC AMENDMENT (2026-09-25, found on the step143000 anchor before the full analysis): mp_fit_v1's
    'iterate the scale correction to a fixed point' COLLAPSES when the bulk is not MP-shaped (trained Q/K: every
    round removes more mass, s -> 0, all 2048 sigma become 'outliers'). v2 takes the scale from the MEDIAN
    singular value matched to the MP median (Gavish-Donoho style), which outliers cannot drag, and counts
    departures at both edges against that scale with the same witness margins tau+/tau-."""
    nmax, nmin = max(m, n), min(m, n)
    g, F = mp_cdf(nmin / nmax)
    med_x = float(np.interp(0.5, F, g))                        # median of sigma^2 / (nmax s^2) under MP
    s = float(np.median(sig)) / math.sqrt(nmax * med_x)
    Ep = s * (np.sqrt(m) + np.sqrt(n)); Em = s * abs(np.sqrt(m) - np.sqrt(n))
    res = {"mp2_scale": s, "mp2_scale_over_rms": None, "mp2_n_upper_outliers": int((sig > tau_p * Ep).sum()),
           "mp2_sigma_max_over_Eplus": float(sig.max() / Ep)}
    if Em > 0 and tau_m is not None:
        res["mp2_n_lower_departures"] = int((sig < tau_m * Em).sum())
    return res


def mle_fit(lam_desc, kmin=50):
    """Clauset: x_min over the top half (n_tail >= kmin) by minimum KS D. lam_desc sorted descending."""
    n = len(lam_desc)
    logs = np.log(lam_desc)
    cs = np.cumsum(logs)
    best = None
    for k in range(kmin, n // 2 + 1):
        xmin = lam_desc[k - 1]
        denom = cs[k - 1] - k * math.log(xmin)
        if denom <= 0:
            continue
        a = 1 + k / denom
        tail = lam_desc[:k][::-1]                    # ascending
        F = 1 - (tail / xmin) ** (-(a - 1))
        i = np.arange(1, k + 1)
        D = max((i / k - F).max(), (F - (i - 1) / k).max())
        if best is None or D < best[0]:
            best = (D, a, xmin, k)
    return best


def htsr_mle_v1(sig, n_boot=100, seed=0):
    lam = np.sort(sig.astype(np.float64) ** 2)[::-1]
    lam = lam[lam > 0]
    D, a, xmin, k = mle_fit(lam)
    rng = np.random.default_rng(seed)
    body = lam[k:]
    n = len(lam)
    ge = 0
    for _ in range(n_boot):
        nt = rng.binomial(n, k / n)
        synth_tail = xmin * (1 - rng.random(nt)) ** (-1 / (a - 1))
        synth_body = rng.choice(body, n - nt, replace=True) if n - nt > 0 else np.array([])
        syn = np.sort(np.concatenate([synth_tail, synth_body]))[::-1]
        b = mle_fit(syn)
        if b is not None and b[0] >= D:
            ge += 1
    p = ge / n_boot
    return {"alpha": a if p >= 0.1 else None, "alpha_raw": a, "ks_D": D, "x_min": xmin, "n_tail": k,
            "boot_p": p, "powerlaw_fit_fails": p < 0.1}


def liu_rankslope_v1(sig):
    s = np.sort(sig)[::-1]
    k = max(2, int(0.2 * len(s)))
    i = np.arange(1, k + 1)
    return float(np.polyfit(np.log(i), np.log(s[:k]), 1)[0])


def global_job(args):
    rev, layer, M, sig, rms, tau_p, tau_m = args
    m, n = FULL[M]
    out = {"stable_rank": float((sig ** 2).sum() / sig.max() ** 2)}
    p = sig ** 2 / (sig ** 2).sum()
    out["spectral_entropy"] = float(-(p[p > 0] * np.log(p[p > 0])).sum() / math.log(len(sig)))
    v1 = mp_fit_v1(sig, m, n, rms, tau_p, tau_m)
    v1["mp_v1_DEGENERATE"] = bool(v1["n_upper_outliers"] > 0.5 * len(sig))   # iteration collapsed; not evidence
    out.update(v1)
    v2 = mp_fit_v2(sig, m, n, tau_p, tau_m)
    v2["mp2_scale_over_rms"] = v2["mp2_scale"] / rms
    out.update(v2)
    out.update({f"mle_{k}": v for k, v in htsr_mle_v1(sig, seed=layer).items()})
    out["liu_rankslope"] = liu_rankslope_v1(sig)
    return rev, layer, M, out


# ---------------- vectors ----------------
def band_of_desc(n):
    """band label per index of a DESCENDING-sigma array, from ascending rank quantiles."""
    lab = np.empty(n, dtype=object)
    asc_rank = (n - 1 - np.arange(n)) / n
    for b, (lo, hi) in S.BANDS.items():
        lab[(asc_rank >= lo) & (asc_rank < hi)] = b
    return lab


def principal_cos(A, B, k):
    return np.linalg.svd(A[:, :k].T.astype(np.float64) @ B[:, :k].astype(np.float64), compute_uv=False)


# ---------------- change points ----------------
def changepoints(x, y, min_seg=3):
    """Binary segmentation, piecewise-linear, BIC penalty. Returns breakpoint indices (into x) as intervals."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(y); x, y = x[ok], y[ok]
    n = len(y)

    def rss(a, b):
        if b - a < 2:
            return 0.0
        A = np.vstack([x[a:b], np.ones(b - a)]).T
        r = np.linalg.lstsq(A, y[a:b], rcond=None)[1]
        return float(r[0]) if len(r) else 0.0

    def bic(r, k):
        return n * math.log(max(r, 1e-300) / n) + k * math.log(n)

    segs = [(0, n)]
    cps = []
    while True:
        best = None
        for (a, b) in segs:
            for c in range(a + min_seg, b - min_seg + 1):
                gain = rss(a, b) - rss(a, c) - rss(c, b)
                if best is None or gain > best[0]:
                    best = (gain, a, b, c)
        if best is None:
            break
        total_now = sum(rss(a, b) for a, b in segs)
        k_now = 3 * len(segs) - 1
        if bic(total_now - best[0], k_now + 3) >= bic(total_now, k_now):
            break
        _, a, b, c = best
        segs.remove((a, b)); segs += [(a, c), (c, b)]; cps.append(c)
    return sorted(cps), x


def main():
    wit = json.loads((ROOT / "results" / "stage3_witness.json").read_text())
    have = [r for r in SCHED if (ROOT / "cache" / "s3" / MODEL / r / "DONE").exists()]
    missing = [r for r in SCHED if r not in have]
    have.sort(key=step_of)
    print("revisions:", len(have), "missing:", missing, flush=True)
    null_cells, g0 = [], {}
    jobs = []
    data = {}
    for rev in have:
        D = load(rev)
        data[rev] = D
        # ---- local statistics + sealed null
        for M in FULL:
            spectra = [z[f"sig_{M}"] for z in D["L"]]
            for T, sp in ((M, spectra),) + (((f"head_{M}", list(np.concatenate([z[f"sighead_{M}"] for z in D["L"]]))),)
                                            if M in HEADS else ()):
                w = wit["types"][T]
                ref = w["runs"]["witness_fp16_final"]
                for band in S.BANDS:
                    r = S.local_stats(sp, band)
                    for key in ("rt", "q_kde", "q_local"):
                        put(rev, -1, T, -1, band, key, r[key], EST["local"])
                        put(rev, -1, T, -1, band, key + "_minus_witness", None if r[key] is None else r[key] - ref[f"{band}:{key}"]["mean"], EST["local"])
                    if band == "bulk":
                        for j, L in enumerate(S.LS):
                            put(rev, -1, T, -1, band, f"sigma2_L{L}", r["sigma2"][j], EST["local"])
                            put(rev, -1, T, -1, band, f"delta3_L{L}", r["delta3"][j], EST["local"])
                        d_rt = r["rt"] - ref["bulk:rt"]["mean"]
                        d_q = None if r["q_kde"] is None else r["q_kde"] - ref["bulk:q_kde"]["mean"]
                        if not w["scale_invariant"]:
                            verdict = "UNRESOLVED_WITNESS_SCALE_DEPENDENT"
                        elif d_q is None:
                            verdict = "UNRESOLVED_Q_REFUSED"
                        else:
                            verdict = "HOLDS" if abs(d_rt) <= TOL_RT and abs(d_q) <= TOL_Q else "VIOLATED"
                        null_cells.append({"step": step_of(rev), "type": T, "rt": r["rt"], "q": r["q_kde"],
                                           "d_rt": d_rt, "d_q": d_q, "verdict": verdict})
        # ---- global jobs
        for l, z in enumerate(D["L"]):
            for M in FULL:
                w = wit["types"][M]
                jobs.append((rev, l, M, z[f"sig_{M}"], float(z[f"rms_{M}"]), w["tau_plus"], w["tau_minus"]))
        # ---- markers
        mk = D["MK"]
        for key in ("loss_text", "loss_rep2", "sink_frac"):
            put(rev, -1, "MODEL", -1, "all", key, float(mk[key]), EST["mk"])
        put(rev, -1, "MODEL", -1, "all", "sink_mean_all", float(mk["sink_mean"].mean()), EST["mk"])
        put(rev, -1, "MODEL", -1, "all", "induction_max", float(mk["induction"].max()), EST["mk"])
        put(rev, -1, "MODEL", -1, "all", "n_induction_heads_gt0.3", float((mk["induction"] > 0.3).sum()), EST["mk"])
        for l in range(24):
            for h in range(16):
                put(rev, l, "ATTN", h, "all", "induction", float(mk["induction"][l, h]), EST["mk"])
                put(rev, l, "ATTN", h, "all", "sink_mean", float(mk["sink_mean"][l, h]), EST["mk"])
        # ---- vectors
        for l, z in enumerate(D["L"]):
            for M in FULL:
                n = len(z[f"sig_{M}"])
                lab = band_of_desc(n)
                for side in ("u", "v"):
                    ipr, pt = z[f"ipr_{side}_{M}"], z[f"pt_{side}_{M}"]
                    dim = FULL[M][0] if side == "u" else FULL[M][1]
                    for b in S.BANDS:
                        sel = lab == b
                        put(rev, l, M, -1, b, f"ipr_{side}_x_dim_median", float(np.median(ipr[sel]) * dim), EST["vec"])
                        put(rev, l, M, -1, b, f"pt_ks_{side}_median", float(np.median(pt[sel])), EST["vec"])
        # ---- circuits
        for l, z in enumerate(D["L"]):
            for h in range(16):
                ov, cp = z["ov_eig"][h], z["copy_eig"][h]
                put(rev, l, "OV", h, "all", "copy_score_elhage", float(cp.real.sum() / np.abs(cp).sum()), EST["circ"])
                put(rev, l, "OV", h, "all", "copy_frac_re_pos", float((cp.real > 0).mean()), EST["circ"])
                put(rev, l, "OV", h, "all", "ov_score", float(ov.real.sum() / np.abs(ov).sum()), EST["circ"])
                put(rev, l, "OV", h, "all", "ov_frac_real", float((np.abs(ov.imag) < 1e-9 * np.abs(ov).max()).mean()), EST["circ"])
                put(rev, l, "QK", h, "all", "qk_sym_nr", float(z["qk_sym_nr"][h]), EST["circ"])
                put(rev, l, "QK", h, "all", "qk_sym_full_ROTARY_CONTAMINATED", float(z["qk_sym_full"][h]), EST["circ"])
                qe = z["qk_eig_nr"][h]
                put(rev, l, "QK", h, "all", "qk_nr_frac_re_pos", float((qe.real > 0).mean()), EST["circ"])
        # G0 at step 0: per-matrix MP KS vs the witness 95th percentile (binomial), plus the bulk null at step 0
        if step_of(rev) == 0:
            from scipy.stats import binom
            for M in FULL:
                m, n = FULL[M]; nmax, nmin = max(m, n), min(m, n)
                g, F = mp_cdf(nmin / nmax)
                ks = []
                for z in D["L"]:
                    s = float(z[f"rms_{M}"]); x = np.sort(z[f"sig_{M}"] ** 2 / (nmax * s * s))
                    Fx = np.interp(x, g, F); i = np.arange(1, len(x) + 1)
                    ks.append(max((i / len(x) - Fx).max(), (Fx - (i - 1) / len(x)).max()))
                k_above = int((np.array(ks) > wit["types"][M]["ks95"]).sum())
                p = float(binom.sf(k_above - 1, 24, 0.05)) if k_above else 1.0
                g0[M] = {"k_above_ks95": k_above, "binom_p": p, "mp_pass": p >= 0.01,
                         "ks_median": float(np.median(ks)), "ks95_witness": wit["types"][M]["ks95"]}
    # ---- principal angles (consecutive + vs final), top-k U and V
    final = have[-1]
    for i, rev in enumerate(have):
        for l in range(24):
            for M in FULL:
                for side in ("U", "V"):
                    A = data[rev]["L"][l][f"{side}32_{M}"]
                    for ref_name, ref_rev in (("prev", have[i - 1] if i else None), ("final", final)):
                        if ref_rev is None:
                            continue
                        B = data[ref_rev]["L"][l][f"{side}32_{M}"]
                        for k in (1, 4, 8, 16, 32):
                            c = principal_cos(A, B, k)
                            put(rev, l, M, -1, f"top{k}", f"{side}_overlap_{ref_name}", float((c ** 2).mean()), EST["vec"])
    # ---- global estimators in parallel (bootstrap is the cost)
    with Pool(8) as pool:
        for rev, l, M, out in pool.imap_unordered(global_job, jobs, chunksize=4):
            for k, v in out.items():
                if isinstance(v, bool):
                    v = float(v)
                put(rev, l, M, -1, "all", k, v, EST["mle"] if k.startswith("mle_") else (EST["liu"] if k.startswith("liu") else
                                                ("mp_fit_v2" if k.startswith("mp2_") else EST["mp"])))
    df = pd.DataFrame(rows, columns=["model", "variant", "step", "layer", "matrix", "head", "band", "metric", "value",
                                     "estimator_version"])
    df.to_parquet(ROOT / "results" / f"stage3_long{TAG}.parquet")
    verdicts = pd.DataFrame(null_cells)
    summary = {"n_cells": len(verdicts), "counts": verdicts.verdict.value_counts().to_dict(), "missing_revisions": missing,
               "G0_mp_step0": g0,
               "G0_bulk_null_step0": verdicts[verdicts.step == 0][["type", "verdict", "d_rt", "d_q"]].to_dict("records"),
               "G4_lower_band_fp16_effect": {T: w["G4_lower_rt_fp16_minus_fp64"] for T, w in wit["types"].items()},
               "witness_scale_invariant": {T: w["scale_invariant"] for T, w in wit["types"].items()},
               "cells": null_cells, "tolerances": {"rt": TOL_RT, "q": TOL_Q}}
    (ROOT / "results" / f"stage3_null{TAG}.json").write_text(json.dumps(summary, indent=1, default=float))
    print(json.dumps({k: summary[k] for k in ("n_cells", "counts", "missing_revisions", "G0_mp_step0")}, indent=1, default=float))
    # ---- change points on layer-mean trajectories (steps >= 1)
    cp_out = {}
    agg = df[(df.step >= 1) & (df.band.isin(["all", "bulk"]))].groupby(["matrix", "band", "metric", "step"]).value.mean().reset_index()
    for (M, b, met), g in agg.groupby(["matrix", "band", "metric"]):
        g = g.sort_values("step")
        if len(g) < 8:
            continue
        cps, xs = changepoints(np.log10(g.step.values), g.value.values)
        steps = g.step.values
        cp_out[f"{M}|{b}|{met}"] = [[int(steps[c - 1]), int(steps[c])] for c in cps]
    (ROOT / "results" / f"stage3_changepoints{TAG}.json").write_text(json.dumps(cp_out, indent=1))
    print("change-point series:", len(cp_out), "with >=1 change:", sum(1 for v in cp_out.values() if v))


if __name__ == "__main__":
    main()
