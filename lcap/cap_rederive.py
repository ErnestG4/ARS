"""Cap re-derivation with the estimator's OWN variance measured — the check
that determines whether LC-ADD-2 found anything.  COMMITTED GENERATOR of
lcap/cap_rederive.json.

WHY THIS RUNS BEFORE ANYTHING ELSE (Will's ruling, 2026-08-16): the cap
estimator is a MAX over a monotone condition ("largest L separated at that L
and all smaller").  Extrema of noisy quantities are systematically biased
DOWNWARD — one unlucky draw at a small L truncates the whole run.  That bias
pushes discrimination_L down, which pushes rows OUTSIDE their window.  So the
estimator's known failure mode points in the SAME DIRECTION as the finding,
and until that is ruled out the finding is not load-bearing.  This arc has
already produced one number that dissolved on inspection (ADD-5's 1.1 sigma);
a third would be a pattern rather than an accident.

Design:
  * draws are generated ONCE per (n, seed) and evaluated at every L, so the
    z(L) curve is PAIRED across L — which is both cheaper and more correct
    than independent draws per L;
  * BOOTSTRAP over draws gives each cap its own sampling distribution
    instead of a point value, so "outside the window" becomes a statement
    with a margin rather than an inequality between two noisy numbers;
  * TWO ESTIMATORS are compared on the same bootstrap replicates — the hard
    max rule, and a smooth crossing (linear fit of z against log L solved at
    Z_SEP) which does not truncate on a single point.  Their difference IS
    the downward bias, measured rather than argued.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402
from policy import goe_positions                                # noqa: E402

Z_SEP = 3.0
N_GRID = [343, 1200, 2000]
L_SCAN = [3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0]
N_DRAWS = 32                      # GUE and GOE realizations per n
N_BOOT = 400
DEG = 6


def matched_L(n):
    return float(np.clip(0.02 * n, 5.0, 50.0))


def curves(n):
    """Sigma^2(L) for N_DRAWS GUE and N_DRAWS GOE realizations, paired
    across L (each realization evaluated at every L)."""
    gue = np.empty((N_DRAWS, len(L_SCAN)))
    goe = np.empty((N_DRAWS, len(L_SCAN)))
    for k in range(N_DRAWS):
        pg = G.gue_positions(n, np.random.default_rng(83_000 + k))
        po = goe_positions(n, np.random.default_rng(84_000 + k))
        for j, L in enumerate(L_SCAN):
            gue[k, j] = G.sigma2(pg, L, DEG)
            goe[k, j] = G.sigma2(po, L, DEG)
        if (k + 1) % 8 == 0:
            print(f"    n={n}: {k + 1}/{N_DRAWS} realizations", flush=True)
    return gue, goe


def z_of(gue, goe):
    """z(L) = (mean GOE - mean GUE) / sd(GUE), per L."""
    return (goe.mean(0) - gue.mean(0)) / gue.std(0, ddof=1)


def cap_hardmax(z):
    """The deployed rule: largest L separated at that L AND all smaller."""
    best = None
    for j, L in enumerate(L_SCAN):
        if z[j] >= Z_SEP:
            best = L
        else:
            break
    return best


def cap_smooth(z):
    """Smooth crossing: least-squares line through z vs log L, solved at
    Z_SEP.  Uses every point, so a single unlucky L cannot truncate it."""
    x = np.log(np.asarray(L_SCAN, float))
    m, b = np.polyfit(x, z, 1)
    if m >= -1e-9:
        return L_SCAN[-1] if z.mean() >= Z_SEP else None
    xc = (Z_SEP - b) / m
    return float(np.clip(np.exp(xc), L_SCAN[0], L_SCAN[-1]))


def main():
    out = dict(Z_SEP=Z_SEP, L_scan=L_SCAN, n_draws=N_DRAWS, n_boot=N_BOOT,
               by_n={})
    for n in N_GRID:
        print(f"  n={n}: generating {N_DRAWS} GUE + {N_DRAWS} GOE "
              f"realizations", flush=True)
        gue, goe = curves(n)
        z_point = z_of(gue, goe)
        hm_point, sm_point = cap_hardmax(z_point), cap_smooth(z_point)
        rng = np.random.default_rng(85_000 + n)
        hm_boot, sm_boot = [], []
        for _ in range(N_BOOT):
            ig = rng.integers(0, N_DRAWS, N_DRAWS)
            io = rng.integers(0, N_DRAWS, N_DRAWS)
            zb = z_of(gue[ig], goe[io])
            h, s = cap_hardmax(zb), cap_smooth(zb)
            if h is not None:
                hm_boot.append(h)
            if s is not None:
                sm_boot.append(s)
        hm_boot, sm_boot = np.array(hm_boot, float), np.array(sm_boot, float)
        mL = matched_L(n)
        # "outside" with a margin: is matched_L above the cap's UPPER bound?
        hi_hm = float(np.percentile(hm_boot, 95)) if hm_boot.size else np.nan
        hi_sm = float(np.percentile(sm_boot, 95)) if sm_boot.size else np.nan
        out["by_n"][str(n)] = dict(
            matched_L=mL, z_curve=z_point.tolist(),
            hard_max=dict(point=hm_point, mean=float(hm_boot.mean()),
                          p05=float(np.percentile(hm_boot, 5)), p95=hi_hm),
            smooth=dict(point=sm_point, mean=float(sm_boot.mean()),
                        p05=float(np.percentile(sm_boot, 5)), p95=hi_sm),
            downward_bias=float(sm_boot.mean() - hm_boot.mean()),
            outside_vs_hardmax_p95=bool(mL > hi_hm),
            outside_vs_smooth_p95=bool(mL > hi_sm))
        r = out["by_n"][str(n)]
        print(f"  n={n}: matched_L={mL:.2f} | hard-max cap "
              f"{hm_boot.mean():.1f} [{r['hard_max']['p05']:.1f},"
              f"{hi_hm:.1f}] | smooth cap {sm_boot.mean():.1f} "
              f"[{r['smooth']['p05']:.1f},{hi_sm:.1f}] | bias "
              f"{r['downward_bias']:+.1f} | OUTSIDE vs smooth p95: "
              f"{r['outside_vs_smooth_p95']}", flush=True)

    biases = [v["downward_bias"] for v in out["by_n"].values()]
    out["estimator_bias"] = dict(
        mean_smooth_minus_hardmax=float(np.mean(biases)),
        hardmax_is_downward_biased=bool(np.mean(biases) > 0),
        note="positive = the hard-max rule reports a SMALLER cap than the "
             "smooth crossing on the same bootstrap replicates, i.e. it is "
             "downward-biased exactly as the max-of-noisy-quantities "
             "argument predicts")
    out["conclusion_survives"] = bool(
        all(v["outside_vs_smooth_p95"] for v in out["by_n"].values()))
    json.dump(out, open(f"{ROOT}/lcap/cap_rederive.json", "w"), indent=1)
    print(f"\nestimator bias (smooth - hardmax) = "
          f"{out['estimator_bias']['mean_smooth_minus_hardmax']:+.2f}",
          flush=True)
    print(f"CONCLUSION SURVIVES the unbiased estimator + 95% margin: "
          f"{out['conclusion_survives']}", flush=True)


if __name__ == "__main__":
    main()
