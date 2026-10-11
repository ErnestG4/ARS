"""PH2S Stage 2 pre-read (twenty-sixth round: "on to the F2 pre-read with estimator B"; nineteenth round: GUE baselines,
power, false-positive splits before the F2 seal). No F2 zero is read: F2 enters only through its pinned height ranges.

  python s2_preread.py secorr OUT    SE calibration of estimator B for the zeros, from theory: under a Gaussian model of
                                     the window sums with CS08's predicted lag correlations ρ_k (cs4/results/diag_wincov),
                                     the variance inflation of mean D (D_i = (S_{i+1} − S_i)²/2) from lags 0–2 (the SE
                                     formula in tapered.pooled_diff) against all available lags.
  python s2_preread.py seemp OUT     the same question measured: SE of v̂_B from lags 0–2 (pooled_diff), from the D
                                     autocovariances summed to lag K, and from batch means over m contiguous batches.
                                     F1 (seen data; descriptive) and the 16 Stage 1 GUE sequences (one batch each).
  python s2_preread.py guecal OUT    calibration of z = (ĝ_B − g)/SE_g at F2's window counts on GUE: pseudo-files of n(b)
                                     windows drawn i.i.d. from the pooled Stage 1 GUE window sums (GUE windows 3b apart
                                     are independent to |ρ₁| ≤ 3e-3), against the pool's own g. Tail rates of |z|.
  python s2_preread.py opchar OUT    operating characteristics of candidate arm-P rules on F2 (size, power against
                                     alternatives, resolvability against GUE), from the per-file SE model
                                     rel SE(v̂_B(b)) = κ·√(3/(n(b) − 1)) (Gaussian successive differences; κ = 1, and the
                                     worst F1 ratio κ = 1.37 from `seemp`), with v̂ ~ v·χ²_ν/ν and plug-in SEs.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WINCOV = os.path.join(HERE, "..", "cs4", "results", "diag_wincov")
ELLS = ("15.7502", "16.4972", "17.2491", "19.5003", "21.75")


def dcorr(rho):
    """rho[0] = 1, rho[k] = predicted lag-k correlation of S. Returns c_k = Corr(ΔS_i, ΔS_{i+k}), k = 1 … len − 2."""
    r = np.asarray(rho)
    k = np.arange(1, len(r) - 1)
    return (2 * r[k] - r[k - 1] - r[k + 1]) / (2 * (1 - r[1]))


def secorr(out):
    res = {}
    for ell in ELLS:
        w = json.load(open(os.path.join(WINCOV, f"wincov_L{ell}.json")))
        res[ell] = {}
        for b, row in w.items():
            lags = [x for x in row.get("lags", []) if x.get("mass_inside", 0) >= 1.0 - 1e-12]
            if len(lags) < 3:
                continue
            rho = np.array([1.0] + [x["rho"] for x in sorted(lags, key=lambda x: x["k"])])
            c = dcorr(rho)
            c2 = c ** 2                                   # Gaussian: Corr(D_i, D_{i+k}) = c_k²
            n = row["n_windows"] - 1
            K = len(c2)
            f2 = 1 + 2 * float(c2[:2].sum())
            fK = 1 + 2 * float(np.sum((1 - np.arange(1, K + 1) / n) * c2))
            tail = float(c2[K // 2:].mean())              # per-lag level over the far half of the available lags
            f_ext = fK + 2 * tail * sum(1 - k / n for k in range(K + 1, n))
            res[ell][b] = dict(n_diffs=n, lags=K, c1=float(c[0]), c2=float(c[1]), infl_lag02=f2, infl_allK=fK,
                               c2_tail_mean=tail, infl_extrap_all_n=f_ext,
                               se_ratio_allK_vs_02=math.sqrt(fK / f2), se_ratio_extrap_vs_02=math.sqrt(f_ext / f2))
            print("ℓ=%-8s b=%5s n=%5d lags %3d | c1 %+.4f c2 %+.4f | infl 0–2 %.4f, all %d lags %.4f, tail c² %.1e,"
                  " extrap to n %.3f | SE ratio %.3f (avail) %.3f (extrap)"
                  % (ell, b, n, K, c[0], c[1], f2, K, fK, tail, f_ext, math.sqrt(fK / f2), math.sqrt(f_ext / f2)))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "secorr.json"), "w"), indent=1)


TAP = os.path.join(HERE, "results", "tapered")
LADDER = (100, 300, 1000, 3000, 10_000)
KS = (2, 10, 30, 100)
MS = (5, 10, 20)


def d_series(sums):
    return np.diff(np.asarray(sums)) ** 2 / 2


def se_lagK(D, K):
    """SE of mean D with autocovariances summed to lag K (Bartlett-free, as pooled_diff at K = 2; floor at lag 0)."""
    N, m = len(D), D.mean()
    g = [float(np.dot(D[: N - k] - m, D[k:] - m)) / N for k in range(K + 1)]
    return math.sqrt(max(g[0] + 2 * sum(g[1:]), g[0]) / N)


def se_batch(D, M):
    """Batch means: M contiguous batches of D; SE of the overall mean = SD(batch means)/√M."""
    B = np.array_split(D, M)
    bm = np.array([x.mean() for x in B])
    return float(bm.std(ddof=1) / math.sqrt(M))


def seemp(out):
    res = {}
    for f in sorted(os.listdir(TAP)):
        if not f.startswith("zeros_F1"):
            continue
        r = json.load(open(os.path.join(TAP, f)))
        name = r["bin"]
        res[name] = {}
        for b in LADDER:
            D = d_series(r["ladder"][str(b)]["sums"])
            m = D.mean()
            row = dict(n=len(D), vB=m / b)
            row.update({f"se_lag{K}_rel": se_lagK(D, K) / m for K in KS if K < len(D) // 4})
            row.update({f"se_batch{M}_rel": se_batch(D, M) / m for M in MS if len(D) >= 4 * M})
            res[name][b] = row
            print("%s b=%5d n=%5d  rel SE: " % (name, b, len(D))
                  + "  ".join("%s %.4f" % (k.replace("_rel", ""), v) for k, v in row.items() if k.endswith("_rel")))
    G = [json.load(open(os.path.join(TAP, f))) for f in sorted(os.listdir(TAP)) if f.startswith("gue_gue_L1000000")]
    res["GUE"] = {}
    for b in LADDER:
        Ds = [d_series(g["ladder"][str(b)]["sums"]) for g in G]
        per = np.array([D.mean() for D in Ds])
        allD = np.concatenate(Ds)
        n = np.array([len(D) for D in Ds])
        # spread across the 16 independent sequences, scaled to one sequence's length, against the per-sequence formulas
        emp = float(per.std(ddof=1) / per.mean())
        f02 = float(np.mean([se_lagK(D, 2) / D.mean() for D in Ds]))
        res["GUE"][b] = dict(n_per_seq=float(n.mean()), between_seq_rel_sd=emp, lag02_rel_se_per_seq=f02,
                             ratio=emp / f02, vB=float(allD.mean() / b))
        print("GUE b=%5d n/seq %.0f  between-sequence rel SD %.4f  vs lag-0–2 formula %.4f  ratio %.2f"
              % (b, n.mean(), emp, f02, emp / f02))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "seemp.json"), "w"), indent=1)


GS_B = os.path.join(HERE, "..", "cs4", "results", "gs_zeta", "gs_zeta_B_summary.json")
G_GUE_B = 0.959137                                   # sine kernel through the same assembly (gs_unitary_lag1)


def f2_geometry():
    """n_windows(b) per F2 file, exactly as tapered.py lays them out (cs4/diag_wincov.n_windows)."""
    T = {"15.7502": (42_446_000, 44_546_000), "16.4972": (90_746_000, 92_846_000),
         "17.2491": (193_646_000, 195_746_000), "19.5003": (1_848_446_000, 1_850_546_000),
         "21.75": (17_541_746_000, 17_543_846_000)}
    nbar = lambda t: t / (2 * math.pi) * math.log(t / (2 * math.pi * math.e)) + 7 / 8
    out = {}
    for ell, (t0, t1) in T.items():
        lo, hi = nbar(t0), nbar(t1)
        out[ell] = dict(levels=hi - lo, n={b: len(np.arange(lo + 4 * b / math.sqrt(2 * math.pi),
                                                               hi - 4 * b / math.sqrt(2 * math.pi), 3 * b))
                                            for b in LADDER})
    return out


def se_v_rel(D):
    m = D.mean()
    return se_lagK(D, 2) / m


def guecal(out, reps=4000, seed=20261011):
    rng = np.random.default_rng(seed)
    G = [json.load(open(os.path.join(TAP, f))) for f in sorted(os.listdir(TAP)) if f.startswith("gue_gue_L1000000")]
    pool = {b: np.concatenate([np.asarray(g["ladder"][str(b)]["sums"]) for g in G]) for b in (100, 10_000)}
    # the pool's own v_B (successive differences within each sequence) is the truth for the resampled pseudo-files
    vtrue = {b: float(np.mean(np.concatenate([d_series(g["ladder"][str(b)]["sums"]) for g in G])) / b) for b in (100, 10_000)}
    gtrue = math.sqrt(vtrue[10_000] / vtrue[100])
    geo = f2_geometry()
    res = dict(pool_windows={b: len(p) for b, p in pool.items()}, g_pool=gtrue, files={})
    for ell, gg in geo.items():
        z = np.empty(reps)
        for k in range(reps):
            v, se = {}, {}
            for b in (100, 10_000):
                S = rng.choice(pool[b], size=gg["n"][b], replace=True)
                D = d_series(S)
                v[b], se[b] = D.mean() / b, se_v_rel(D)
            g = math.sqrt(v[10_000] / v[100])
            z[k] = (g - gtrue) / (0.5 * g * math.sqrt(se[100] ** 2 + se[10_000] ** 2))
        res["files"][ell] = dict(n=gg["n"], z_mean=float(z.mean()), z_sd=float(z.std()),
                                 rate_abs_gt2=float(np.mean(np.abs(z) > 2)), rate_abs_gt3=float(np.mean(np.abs(z) > 3)),
                                 rate_lo_gt2=float(np.mean(z < -2)), rate_hi_gt2=float(np.mean(z > 2)))
        r = res["files"][ell]
        print("ℓ=%-8s n(100) %5d n(1e4) %3d | z mean %+.3f sd %.3f | P(|z|>2) %.4f (nominal 0.0455)  P(|z|>3) %.4f "
              "(0.0027) | P(z<−2) %.4f P(z>2) %.4f"
              % (ell, gg["n"][100], gg["n"][10_000], r["z_mean"], r["z_sd"], r["rate_abs_gt2"], r["rate_abs_gt3"],
                 r["rate_lo_gt2"], r["rate_hi_gt2"]))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "guecal.json"), "w"), indent=1)


def simulate_g(g_true, n, kappa, rng, reps):
    """ĝ and its plug-in SE for one file: v̂(b) = v(b)·χ²_ν/ν, ν = 2/relSE², relSE = κ√(3/(n − 1)); v(100) := 1."""
    out_g, out_se = np.empty(reps), np.empty(reps)
    rs = {b: kappa * math.sqrt(3 / (n[b] - 1)) for b in (100, 10_000)}
    v1 = rng.chisquare(2 / rs[100] ** 2, reps) / (2 / rs[100] ** 2)
    v2 = g_true ** 2 * rng.chisquare(2 / rs[10_000] ** 2, reps) / (2 / rs[10_000] ** 2)
    out_g = np.sqrt(v2 / v1)
    out_se = 0.5 * out_g * math.sqrt(rs[100] ** 2 + rs[10_000] ** 2)
    return out_g, out_se


def opchar(out, reps=200_000, seed=20261012):
    rng = np.random.default_rng(seed)
    geo = f2_geometry()
    pred = {ell: row["g_B"] for ell, row in json.load(open(GS_B)).items() if ell != "gue_B"}
    ells = list(geo)
    eps_list = (-0.5, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5, 1.0)       # g = g_pred + ε(g_GUE,B − g_pred); ε = 1: GUE
    res = dict(pred=pred, g_gue_B=G_GUE_B, geometry=geo, kappa={})
    for kappa in (1.0, 1.37):
        rows = {}
        per_file_se = {ell: float(np.mean(simulate_g(pred[ell], geo[ell]["n"], kappa, rng, 20_000)[1])) for ell in ells}
        for eps in eps_list:
            Z, SEs = [], []
            for ell in ells:
                gt = pred[ell] + eps * (G_GUE_B - pred[ell])
                g, se = simulate_g(gt, geo[ell]["n"], kappa, rng, reps)
                Z.append((g - pred[ell]) / se)
                SEs.append(se)
            Z, SEs = np.array(Z), np.array(SEs)                              # (files, reps)
            w = 1 / SEs ** 2
            d = np.array([g_ for g_ in Z]) * SEs                             # ĝ − g_pred per file
            zpool = (w * d).sum(0) / w.sum(0) / np.sqrt(1 / w.sum(0))
            row = {}
            for k in (2.0, 3.0):
                agree = (np.abs(Z) <= k).sum(0)
                row[f"k{k:g}"] = dict(R1_pass=float(np.mean(agree >= 4)), R2_pass=float(np.mean(np.abs(zpool) <= k)),
                                      R1R2_pass=float(np.mean((agree >= 4) & (np.abs(zpool) <= k))))
            rows[eps] = row
        res["kappa"][kappa] = dict(per_file_se_g=per_file_se, rules=rows)
        print("κ = %.2f  per-file SE(ĝ_B): %s" % (kappa, "  ".join("%s %.4f" % (e, s) for e, s in per_file_se.items())))
        print("   ε (0 = prediction true, 1 = GUE) | k=2: R1 R2 R1∧R2 | k=3: R1 R2 R1∧R2   (P(PASS))")
        for eps, row in rows.items():
            print("   %+5.2f | %.4f %.4f %.4f | %.4f %.4f %.4f" % (eps, *[row["k2"][x] for x in ("R1_pass", "R2_pass", "R1R2_pass")],
                                                                 *[row["k3"][x] for x in ("R1_pass", "R2_pass", "R1R2_pass")]))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "opchar.json"), "w"), indent=1)


def file_stats(sums100, sums1e4):
    v, se = {}, {}
    for b, s in ((100, sums100), (10_000, sums1e4)):
        D = d_series(s)
        v[b], se[b] = D.mean() / b, se_v_rel(D)
    g = math.sqrt(v[10_000] / v[100])
    return g, 0.5 * g * math.sqrt(se[100] ** 2 + se[10_000] ** 2), v


def rules(rows, k):
    z = np.array([r["z"] for r in rows])
    d = np.array([r["g"] - r["g_pred"] for r in rows])
    se = np.array([r["se_g"] for r in rows])
    w = 1 / se ** 2
    zp = float((w * d).sum() / w.sum() / math.sqrt(1 / w.sum()))
    agree = int((np.abs(z) <= k).sum())
    return dict(agree=agree, z_pool=zp, R1="PASS" if agree >= 4 else "FAIL",
                R2="PASS" if abs(zp) <= k else "FAIL")


def dryrun(out, seed=20261013):
    pred = {float(ell): row["g_B"] for ell, row in json.load(open(GS_B)).items() if ell != "gue_B"}
    xs = sorted(pred)
    interp = lambda l: float(np.interp(l, xs, [pred[x] for x in xs]))        # clamped outside [15.75, 21.75]
    import sys as _s
    _s.path.insert(0, os.path.join(HERE, "..", "ph2s"))
    res = dict(F1={}, GUE_standin={})
    print("F1 (seen data; prediction interpolated in ℓ, clamped outside the F2 range — descriptive)")
    ells_f1 = dict(F1a=14.4625, F1b=15.4741, F1c=17.7481, F1d=19.2500, F1e=21.5000, F1x=22.1000)
    rows = []
    for f in sorted(os.listdir(TAP)):
        if f.startswith("zeros_F1"):
            r = json.load(open(os.path.join(TAP, f)))
            g, se, _ = file_stats(r["ladder"]["100"]["sums"], r["ladder"]["10000"]["sums"])
            gp = interp(ells_f1[r["bin"]])
            row = dict(file=r["bin"], ell=ells_f1[r["bin"]], g=g, se_g=se, g_pred=gp, z=(g - gp) / se)
            res["F1"][r["bin"]] = row
            print("  %s ℓ %.2f  ĝ_B %.4f ± %.4f  g_pred %.4f  z %+.2f" % (r["bin"], row["ell"], g, se, gp, row["z"]))
            if r["bin"] != "F1x":
                rows.append(row)
    for k in (2.0, 3.0):
        res["F1"][f"rules_k{k:g}"] = rules(rows, k)
        print("  core five, k = %g: %s" % (k, res["F1"][f"rules_k{k:g}"]))
    rng = np.random.default_rng(seed)
    G = [json.load(open(os.path.join(TAP, f))) for f in sorted(os.listdir(TAP)) if f.startswith("gue_gue_L1000000")]
    pool = {b: np.concatenate([np.asarray(g["ladder"][str(b)]["sums"]) for g in G]) for b in (100, 10_000)}
    geo = f2_geometry()
    for target in ("zeta", "gue"):
        rows = []
        for ell, gg in geo.items():
            g, se, _ = file_stats(rng.choice(pool[100], gg["n"][100]), rng.choice(pool[10_000], gg["n"][10_000]))
            gp = pred[float(ell)] if target == "zeta" else G_GUE_B
            rows.append(dict(file=ell, g=g, se_g=se, g_pred=gp, z=(g - gp) / se))
        res["GUE_standin"][target] = dict(rows=rows, **{f"rules_k{k:g}": rules(rows, k) for k in (2.0, 3.0)})
        print("GUE stand-in at F2 geometry vs the %s prediction: %s | k=2 %s | k=3 %s"
              % ("ζ" if target == "zeta" else "GUE", " ".join("z %+.1f" % r["z"] for r in rows),
                 res["GUE_standin"][target]["rules_k2"], res["GUE_standin"][target]["rules_k3"]))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "dryrun.json"), "w"), indent=1)


if __name__ == "__main__":
    {"secorr": secorr, "seemp": seemp, "guecal": guecal, "opchar": opchar, "dryrun": dryrun}[sys.argv[1]](sys.argv[2])
