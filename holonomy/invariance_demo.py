"""Would the dual-grid check have caught the 96-sem artifact? RED-PATH PROOF.
COMMITTED GENERATOR of holonomy/invariance_demo.json.

A guard earns its verdict when it can CONSTRUCT the failure it claims to rule
out (TOOLKIT: powered falsifier that fires).  So this runs the deg-13 ridge
centroid on the two grids that historically disagreed --

  GRID A  the original coarse dial set, which SKIPPED dial 5.0
  GRID B  the finer set, which sampled it

-- under BOTH predictions: the raw ill-conditioned polyfit that produced the
+0.8085 (96 sem) cell, and the conditioned fit that repaired it.  The
measurement is identical in both arms, so this differences one measurement pass
against two predictions; the only thing that varies is the arithmetic under test.

EXPECTED, committed before the run: with the RAW prediction the two grids
disagree grossly (the artifact sits on a dial only grid B samples), and
`dual_grid_statistic` FIRES.  With the CONDITIONED prediction the two grids
agree and it passes.  If the raw arm does NOT fire, this guard cannot detect the
one failure it was built from and should not be trusted on any other.
"""
import json, sys, warnings
import numpy as np

warnings.filterwarnings("ignore")
ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")
sys.path.insert(0, ROOT)
from transitions import (gen_gue_unfolded, make_trend_maps, p1_apply,   # noqa: E402
                         sigma2_at)
import predict_p1 as PP                                                 # noqa: E402
from condfit import fit_eval                                            # noqa: E402
from invariance import dual_grid_statistic                              # noqa: E402

N_FULL, N_W, A, L, DEG = 1200, 600, 0.25, 10.0, 13
SEEDS, N_MAT = 200, 2048
GRID_A = [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]              # historically skipped 5.0
GRID_B = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
ALL = sorted(set(GRID_A) | set(GRID_B))


def pred(dial, deg, conditioned):
    ell = N_W / dial
    u = np.linspace(0.0, float(N_FULL), 48001)
    x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
    x = x_of_u(u)
    lo, hi = (N_FULL - N_W) / 2.0, (N_FULL + N_W) / 2.0
    w = (u >= lo) & (u <= hi)
    if conditioned:
        fA, fB = fit_eval(x, u, deg, x[w]), fit_eval(x[w], u[w] - lo, deg, x[w])
    else:
        fA = np.polyval(np.polyfit(x, u, deg), x[w])
        fB = np.polyval(np.polyfit(x[w], u[w] - lo, deg), x[w])
    return float(PP.spurious_var(fA, u[w], L) - PP.spurious_var(fB, u[w], L))


def centroid(res_by_dial, grid):
    r = np.array([res_by_dial[d] for d in grid], float)
    e = np.clip(np.abs(r) - np.median(np.abs(r)), 0.0, None)
    return float(np.sum(np.asarray(grid) * e) / np.sum(e)) if e.sum() > 0 else np.nan


def main():
    spectra = []
    for s in range(SEEDS):
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        spectra.append(ua[lo:lo + N_FULL] - ua[lo])
    meas = {}
    for dial in ALL:                       # ONE measurement pass, reused by both arms
        ell = N_W / dial
        x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
        d = []
        for u in spectra:
            x = x_of_u(u)
            d.append(sigma2_at(p1_apply(x, "unfold_then_window", DEG, N_W), [L])[0]
                     - sigma2_at(p1_apply(x, "window_then_unfold", DEG, N_W), [L])[0])
        meas[dial] = float(np.mean(d))
        print(f"  measured dial {dial:>5}: {meas[dial]:+.4f}", flush=True)

    out = dict(deg=DEG, seeds=SEEDS, grid_a=GRID_A, grid_b=GRID_B,
               overlap=sorted(set(GRID_A) & set(GRID_B)), arms={})
    for tag, cond in (("RAW_ill_conditioned", False), ("CONDITIONED_repaired", True)):
        res = {d: meas[d] - pred(d, DEG, cond) for d in ALL}
        r = dual_grid_statistic(lambda g: centroid(res, g), tuple(GRID_A),
                                tuple(GRID_B), rtol=0.05,
                                name=f"deg-{DEG} ridge centroid [{tag}]")
        out["arms"][tag] = dict(residuals={str(k): v for k, v in res.items()}, **{
            k: v for k, v in r.items() if k != "name"})
        print(f"\n{tag}:")
        print(f"  centroid grid A {r['value_a']:.3f}   grid B {r['value_b']:.3f}   "
              f"rel dev {r['rel_dev']:.1%}   -> {'AGREE' if r['agree'] else 'FIRES'}")

    fired = not out["arms"]["RAW_ill_conditioned"]["agree"]
    passed = out["arms"]["CONDITIONED_repaired"]["agree"]
    out["guard_fires_on_known_bug"] = fired
    out["guard_passes_after_repair"] = passed
    out["verdict"] = (
        "GUARD_VALIDATED — the dual-grid check FIRES on the historical "
        "ill-conditioned arithmetic and PASSES after the repair, so it detects "
        "the one deterministic failure it was built from" if (fired and passed)
        else f"GUARD_NOT_VALIDATED — fires_on_bug={fired}, passes_after_repair="
             f"{passed}; a guard that cannot construct its own failure should not "
             "be trusted elsewhere")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(f"{ROOT}/holonomy/invariance_demo.json", "w"), indent=1)


if __name__ == "__main__":
    main()
