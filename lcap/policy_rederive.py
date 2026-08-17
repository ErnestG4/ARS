"""Per-realization policy re-derivation — COMMITTED GENERATOR of
lcap/policy_rederive.json.

The rescoped work: caps derived from the OPERATIONALLY CORRECT estimand
(per-realization error rates, both directions) against thresholds fixed in
advance in RELIABILITY_THRESHOLDS.md — FP <= 0.05 AND FN <= 0.05, each at the
95th percentile of a bootstrap over realizations, at every candidate cap.

  FP = fraction of GOE realizations that earn RIGID_GUE
       (nearest confusable known class admitted)
  FN = fraction of GUE realizations that FAIL to earn RIGID_GUE
       (true class rejected — includes HYPER_RIGID and the Poisson-side cells)

DISJOINT REFERENCE: the band is built from one set of GUE draws and the FN
test uses a DIFFERENT set.  Testing draws against a band they helped define
would bias FN optimistically — the draw pulls the mean toward itself.  This
is the same estimand-hygiene point one level down, and it is why the two
GUE sets carry different seed bases.

TWO CAP ESTIMATORS, both reported (the max-rule bias lesson): the hard-max
rule that the previous derivation used, and a smooth crossing of the
interpolated error curves.  Reporting both means the bias is visible in the
output rather than argued about afterwards.
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

N_GRID = [343, 1200, 2000]
L_SCAN = [3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0]
N_REF, N_TEST = 28, 28
N_BOOT = 500
MULT, DEG = 2.5, 6
FP_MAX = FN_MAX = 0.05          # RELIABILITY_THRESHOLDS.md, fixed in advance


def sigma2_curves(sampler, n, n_draws, seed0):
    out = np.empty((n_draws, len(L_SCAN)))
    for k in range(n_draws):
        pts = sampler(n, np.random.default_rng(seed0 + k))
        for j, L in enumerate(L_SCAN):
            out[k, j] = G.sigma2(pts, L, DEG)
    return out


def rates(ref, gue_t, goe_t, j):
    """FP and FN at L-index j from a reference band and disjoint test sets."""
    gm, gs = ref[:, j].mean(), ref[:, j].std(ddof=1)
    lo, hi = gm - MULT * gs, gm + MULT * gs
    fp = float(np.mean((goe_t[:, j] >= lo) & (goe_t[:, j] <= hi)))
    fn = float(np.mean((gue_t[:, j] < lo) | (gue_t[:, j] > hi)))
    return fp, fn


def cap_hardmax(ok):
    best = None
    for j, L in enumerate(L_SCAN):
        if ok[j]:
            best = L
        else:
            break
    return best


def cap_smooth(fp_c, fn_c):
    """Largest L where the linear-in-log-L fits of BOTH curves stay under
    their thresholds; uses every point, so one bad L cannot truncate."""
    x = np.log(np.asarray(L_SCAN, float))
    grid = np.exp(np.linspace(x[0], x[-1], 400))
    ok = np.ones(grid.size, bool)
    for curve, thr in ((fp_c, FP_MAX), (fn_c, FN_MAX)):
        m, b = np.polyfit(x, curve, 1)
        ok &= (m * np.log(grid) + b) <= thr
    return float(grid[ok].max()) if ok.any() else None


def main():
    out = dict(thresholds=dict(FP_MAX=FP_MAX, FN_MAX=FN_MAX, mult=MULT),
               n_ref=N_REF, n_test=N_TEST, n_boot=N_BOOT, L_scan=L_SCAN,
               disjoint_reference=True, by_n={})
    for n in N_GRID:
        print(f"  n={n}: {N_REF} reference + {N_TEST} test GUE + {N_TEST} GOE",
              flush=True)
        ref = sigma2_curves(G.gue_positions, n, N_REF, 90_000)
        gue_t = sigma2_curves(G.gue_positions, n, N_TEST, 91_000)   # disjoint
        goe_t = sigma2_curves(goe_positions, n, N_TEST, 92_000)
        fp_c, fn_c, rows = [], [], {}
        rng = np.random.default_rng(93_000 + n)
        for j, L in enumerate(L_SCAN):
            fp, fn = rates(ref, gue_t, goe_t, j)
            bfp, bfn = [], []
            for _ in range(N_BOOT):
                ir = rng.integers(0, N_REF, N_REF)
                ig = rng.integers(0, N_TEST, N_TEST)
                io = rng.integers(0, N_TEST, N_TEST)
                a, b = rates(ref[ir], gue_t[ig], goe_t[io], j)
                bfp.append(a)
                bfn.append(b)
            fp95, fn95 = (float(np.percentile(bfp, 95)),
                          float(np.percentile(bfn, 95)))
            fp_c.append(fp)
            fn_c.append(fn)
            rows[str(L)] = dict(FP=fp, FP_p95=fp95, FN=fn, FN_p95=fn95,
                                admissible=bool(fp95 <= FP_MAX
                                                and fn95 <= FN_MAX))
            print(f"    L={L:5.1f}: FP {fp:.2f} (p95 {fp95:.2f})  "
                  f"FN {fn:.2f} (p95 {fn95:.2f})  "
                  f"{'ok' if rows[str(L)]['admissible'] else 'INADMISSIBLE'}",
                  flush=True)
        ok = [rows[str(L)]["admissible"] for L in L_SCAN]
        hm, sm = cap_hardmax(ok), cap_smooth(fp_c, fn_c)
        out["by_n"][str(n)] = dict(
            rows=rows, cap_hardmax=hm, cap_smooth=sm,
            matched_L=float(np.clip(0.02 * n, 5.0, 50.0)),
            binding=("FP" if any(rows[str(L)]["FP_p95"] > FP_MAX
                                 for L in L_SCAN) else "")
                    + ("FN" if any(rows[str(L)]["FN_p95"] > FN_MAX
                                   for L in L_SCAN) else ""))
        r = out["by_n"][str(n)]
        print(f"  n={n}: cap hard-max={hm} smooth={sm if sm is None else round(sm,1)} "
              f"| matched_L={r['matched_L']:.1f} | binding arm(s): "
              f"{r['binding'] or 'none'}", flush=True)

    json.dump(out, open(f"{ROOT}/lcap/policy_rederive.json", "w"), indent=1)
    print("\nSUMMARY (cap = largest L with FP_p95 <= .05 AND FN_p95 <= .05)",
          flush=True)
    for n, v in out["by_n"].items():
        verdict = ("OUTSIDE" if v["cap_smooth"] is not None
                   and v["matched_L"] > v["cap_smooth"] else "inside/undet")
        print(f"  n={n:>5}: matched_L={v['matched_L']:5.1f} "
              f"cap_smooth={v['cap_smooth'] if v['cap_smooth'] is None else round(v['cap_smooth'],1)} "
              f"-> default policy {verdict}", flush=True)


if __name__ == "__main__":
    main()
