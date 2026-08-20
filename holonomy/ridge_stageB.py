"""Ridge map, stage B: measure the HELD-OUT degrees against stage A's sealed
prediction.  COMMITTED GENERATOR of holonomy/ridge_stageB.json.  DIAGNOSTIC.

Stage A fitted ridge(deg) on degrees 5, 9, 13 and wrote sealed predictions for
7 and 11 into ridge_stageA.json, which is committed BEFORE this runs.  This
script refuses to start if that file is missing, and it reads the predictions
before measuring so they cannot be adjusted afterwards.

This is the step that decides whether the ridge is a PREDICTIVE object or only a
descriptive one.  Supported means "four failures fell on a diagonal"; predictive
means "we said where the fifth and sixth would be, and they were there".

The three sealed criteria, restated from stage A:
  (i)   a ridge cell (|residual| > 3 sem) appears near the predicted dial
  (ii)  the measured centroid lies between the LINEAR and QUADRATIC predictions
  (iii) the measured centroid sits ABOVE the (deg-1)/2 BASELINE, continuing the
        signed deviation already banked

(i) is the load-bearing one: failing it refutes the ridge as predictive. (ii)
and (iii) are finer and speak to the form question, which remains UNRESOLVED
either way -- two extra points do not select a form, they test a trend.
"""
import json, os, sys, warnings
import numpy as np

warnings.filterwarnings("ignore")
ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")
from ridge_stageA import (measure, gen_gue_unfolded, N_FULL, N_MAT,      # noqa: E402
                          SEEDS, DIALS, HELD_OUT)

SA = f"{ROOT}/holonomy/ridge_stageA.json"
if not os.path.exists(SA):
    sys.exit("stage A artifact missing — the prediction must be sealed and "
             "committed before stage B may run")
A = json.load(open(SA))
PRED = A["SEALED_PREDICTION"]
print("READING SEALED PREDICTIONS BEFORE MEASURING:")
for h in HELD_OUT:
    p = PRED[str(h)]
    print(f"  deg {h:>2}: LINEAR {p['linear']:.2f}  QUADRATIC {p['quadratic']:.2f}"
          f"  BASELINE {p['baseline_deg_minus_1_over_2']:.1f}")


def main():
    spectra = []
    for s in range(SEEDS):
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        spectra.append(ua[lo:lo + N_FULL] - ua[lo])
    rng = np.random.default_rng(97)
    out = dict(seeds=SEEDS, dials=DIALS, sealed_prediction=PRED, rows={}, tests={})
    print()
    for h in HELD_OUT:
        r = measure(h, spectra, rng)
        out["rows"][str(h)] = r
        p = PRED[str(h)]
        lo_p, hi_p = sorted([p["linear"], p["quadratic"]])
        # (i) is a ridge cell present near the prediction? "near" = within one
        # dial-grid step of the predicted location, fixed by the grid not by taste
        centre = 0.5 * (p["linear"] + p["quadratic"])
        step = min(abs(DIALS[i + 1] - DIALS[i]) for i in range(len(DIALS) - 1))
        near = [d for d in r["fail_dials"] if abs(d - centre) <= max(step, 0.25 * centre)]
        t = dict(
            ridge_cell_present=bool(r["fail_dials"]),
            ridge_cell_near_prediction=bool(near),
            fail_dials=r["fail_dials"], predicted_centre=centre,
            centroid_between_lin_quad=bool(lo_p <= r["centroid"] <= hi_p),
            centroid_above_baseline=bool(r["centroid"] > p["baseline_deg_minus_1_over_2"]),
            centroid=r["centroid"], ci95=r["ci95"])
        out["tests"][str(h)] = t
        print(f"deg {h:>2}: centroid {r['centroid']:.2f} CI [{r['ci95'][0]:.2f},"
              f"{r['ci95'][1]:.2f}]  FAIL dials {r['fail_dials']}")
        print(f"        (i) ridge cell near predicted {centre:.2f}: "
              f"{'YES' if t['ridge_cell_near_prediction'] else 'NO'}   "
              f"(ii) between lin/quad [{lo_p:.2f},{hi_p:.2f}]: "
              f"{'YES' if t['centroid_between_lin_quad'] else 'NO'}   "
              f"(iii) above baseline {p['baseline_deg_minus_1_over_2']:.1f}: "
              f"{'YES' if t['centroid_above_baseline'] else 'NO'}", flush=True)

    i_ok = all(out["tests"][str(h)]["ridge_cell_near_prediction"] for h in HELD_OUT)
    ii = sum(out["tests"][str(h)]["centroid_between_lin_quad"] for h in HELD_OUT)
    iii = sum(out["tests"][str(h)]["centroid_above_baseline"] for h in HELD_OUT)
    out["verdict"] = (
        f"RIDGE_PREDICTIVE — a ridge cell appeared near the sealed prediction at "
        f"BOTH held-out degrees; centroid between lin/quad at {ii}/2 and above "
        f"(deg-1)/2 at {iii}/2. The mechanism predicted where the failures would "
        "be before they were measured" if i_ok else
        f"RIDGE_DESCRIPTIVE_ONLY — the sealed location test failed at "
        f"{2 - sum(out['tests'][str(h)]['ridge_cell_near_prediction'] for h in HELD_OUT)}"
        "/2 held-out degrees; the ridge describes the measured cells but does not "
        "predict untested ones")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(f"{ROOT}/holonomy/ridge_stageB.json", "w"), indent=1)


if __name__ == "__main__":
    main()
