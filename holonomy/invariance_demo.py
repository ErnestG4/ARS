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

N_FULL, N_W, A, L = 1200, 600, 0.25, 10.0
SEEDS, N_MAT = 200, 2048
# Each degree is tested against ITS OWN stated CI (from ridge_stageA.json).
# deg 9 is the demanding case -- half-width 0.13 against deg 13's 1.28 -- and it
# is also the load-bearing one, since SLOPE_RESOLVED rests on the deg 5/9/13
# centroids and deg 9 is the tightest of them. A guard that only ever runs
# against a loose CI has not been asked a hard question.
DEGS_CI = {9: [4.07, 4.33], 13: [4.84, 7.40]}
# the quantity's OWN stated uncertainty, from ridge_stageA.json -- the invariance
# tolerance is referenced to this rather than to an arbitrary percentage
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


def measure_row(deg, spectra):
    meas = {}
    for dial in ALL:                   # ONE measurement pass, reused by both arms
        ell = N_W / dial
        x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
        d = []
        for u in spectra:
            x = x_of_u(u)
            d.append(sigma2_at(p1_apply(x, "unfold_then_window", deg, N_W), [L])[0]
                     - sigma2_at(p1_apply(x, "window_then_unfold", deg, N_W), [L])[0])
        meas[dial] = float(np.mean(d))
    return meas


def main():
    spectra = []
    for s in range(SEEDS):
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        spectra.append(ua[lo:lo + N_FULL] - ua[lo])
    out = dict(seeds=SEEDS, grid_a=GRID_A, grid_b=GRID_B,
               overlap=sorted(set(GRID_A) & set(GRID_B)), by_deg={})
    for DEG, CI in DEGS_CI.items():
        half = (CI[1] - CI[0]) / 2.0
        print(f"\n=== deg {DEG}  (own CI {CI}, half-width {half:.3f}) ===", flush=True)
        meas = measure_row(DEG, spectra)
        arms = {}
        for tag, cond in (("RAW_ill_conditioned", False),
                          ("CONDITIONED_repaired", True)):
            res = {d: meas[d] - pred(d, DEG, cond) for d in ALL}
            r = dual_grid_statistic(lambda g: centroid(res, g), tuple(GRID_A),
                                    tuple(GRID_B), ci=CI,
                                    name=f"deg-{DEG} ridge centroid [{tag}]")
            arms[tag] = dict(residuals={str(k): v for k, v in res.items()},
                             **{k: v for k, v in r.items() if k != "name"})
            print(f"  {tag:22s} A {r['value_a']:.3f}  B {r['value_b']:.3f}  "
                  f"dev {r['abs_dev']:.3f} vs half-width {half:.3f}  -> "
                  f"{'AGREE' if r['agree'] else 'FIRES'}", flush=True)
        out["by_deg"][str(DEG)] = dict(ci=CI, ci_half_width=half, arms=arms)
    DEG = max(DEGS_CI)

    # TWO SEPARATE QUESTIONS, conflated in the first version of this script.
    # (a) DOES THE GUARD WORK? -> can it construct the failure it claims to rule
    #     out. That is answered by the RAW arm alone.
    # (b) IS THE REPAIRED QUANTITY GRID-STABLE? -> a fact about the data.
    # Requiring both for "GUARD_VALIDATED" made a property of the data decide
    # whether the instrument was sound, which is the same conflation the estimand
    # rule warns about.
    # THE CRITERION IS SENSITIVITY *AND* SPECIFICITY, not "fires everywhere".
    # First version scored the guard PARTIAL for not firing at deg 9 -- but at
    # deg 9 the raw and conditioned predictions are IDENTICAL, so there is no bug
    # there to detect and firing would have been a FALSE POSITIVE. Demanding that
    # a guard fire where nothing is wrong is the same defect as scoring an arm
    # that cannot fire: it treats non-evidence as a verdict. And a guard checked
    # only where it fires is calibrated on ONE side -- the session's own lesson.
    # So: a bug is PRESENT at a degree iff raw and conditioned disagree there;
    # the guard is correct at that degree iff it fires exactly when one is.
    BUG_TOL = 1e-6
    sens = spec = 0
    n_bug = n_clean = 0
    for k in DEGS_CI:
        a = out["by_deg"][str(k)]["arms"]
        bug = abs(a["RAW_ill_conditioned"]["value_b"]
                  - a["CONDITIONED_repaired"]["value_b"]) > BUG_TOL
        fires = not a["RAW_ill_conditioned"]["agree"]
        a_correct = (fires == bug)
        out["by_deg"][str(k)]["bug_present"] = bool(bug)
        out["by_deg"][str(k)]["guard_fires"] = bool(fires)
        out["by_deg"][str(k)]["guard_correct"] = bool(a_correct)
        if bug:
            n_bug += 1; sens += int(fires)
        else:
            n_clean += 1; spec += int(not fires)
    out["sensitivity"] = f"{sens}/{n_bug}"
    out["specificity"] = f"{spec}/{n_clean}"
    fired = bool(n_bug and sens == n_bug and spec == n_clean)
    fired_any = bool(sens)
    stable = all(out["by_deg"][str(k)]["arms"]["CONDITIONED_repaired"]["agree"]
                 for k in DEGS_CI)
    print(f"\n  bug present at {n_bug}/{len(DEGS_CI)} degrees; "
          f"sensitivity {sens}/{n_bug}, specificity {spec}/{n_clean}")
    out["guard_fires_on_known_bug"] = fired
    out["repaired_quantity_grid_stable"] = stable
    out["verdict_guard"] = (
        "GUARD_VALIDATED — the dual-grid check FIRES on the historical "
        f"ill-conditioned arithmetic wherever the bug EXISTS (sensitivity "
        f"{out['sensitivity']}) and stays silent where it does not (specificity "
        f"{out['specificity']}) — validated on BOTH sides, not just where it fires"
        if fired else
        f"GUARD_MISCALIBRATED — sensitivity {out['sensitivity']}, specificity "
        f"{out['specificity']}; a guard wrong in either direction is not usable"
        if fired_any else
        "GUARD_NOT_VALIDATED — it cannot construct the one deterministic failure "
        "it was built from and should not be trusted elsewhere")
    out["verdict_data"] = (
        "REPAIRED_QUANTITY_GRID_STABLE at every degree — each within its own "
        "stated CI, including deg 9 whose half-width is only 0.13" if stable else
        "REPAIRED_QUANTITY_GRID_DEPENDENT at some degree — beyond its own CI")
    out["verdict"] = out["verdict_guard"] + "  ||  " + out["verdict_data"]
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(f"{ROOT}/holonomy/invariance_demo.json", "w"), indent=1)


if __name__ == "__main__":
    main()
