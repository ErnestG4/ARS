"""Ridge map, stage A: homogeneous centroids at deg 5/9/13, then SEAL a
prediction for the untested degrees 7 and 11.
COMMITTED GENERATOR of holonomy/ridge_stageA.json.  DIAGNOSTIC.

The ridge and the form question are ONE OBJECT: the ridge location at a given
degree IS the straddle peak at that degree, so the FAIL cells and the centroid
measurements are two readings of one surface.  This run therefore closes both
open items at once.

Stage A measures deg 5, 9, 13 on a single dial grid at 200 seeds -- homogeneous,
unlike the existing set where deg 5's location came from a 24-seed ARGMAX and
the others from 200-seed centroids.  It then fits ridge(deg) and writes down
predictions for deg 7 and 11 BEFORE those degrees are ever run.  Stage B
(ridge_stageB.py) measures them.  7 and 11 are INTERPOLATION points, which is
the strongest form of this test: no extrapolation slack.

Three predictors are sealed rather than one, because the form is explicitly
UNRESOLVED and picking a single one would smuggle in a form claim:
  * LINEAR      ridge = a*deg + b fitted on the three points (1 dof, so the fit
                is itself testable)
  * QUADRATIC   exact interpolant through the three points
  * BASELINE    (deg-1)/2 -- the refuted candidate, kept as the discriminator.
                It is known to UNDER-predict with a signed, growing error, so
                measurements landing on the trend and away from BASELINE is the
                informative outcome.

THE TEST, fixed here: (i) does a ridge cell appear at all near the predicted
dial for each of deg 7 and 11 -- the qualitative claim that the mechanism is
predictive; (ii) does the measured centroid fall between the LINEAR and
QUADRATIC predictions; (iii) does it sit ABOVE the BASELINE, continuing the
signed deviation.  Failing (i) refutes the ridge as a predictive object.
"""
import json, sys, warnings
import numpy as np

warnings.filterwarnings("ignore")
ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")
from transitions import (gen_gue_unfolded, make_trend_maps, p1_apply,   # noqa: E402
                         sigma2_at)
import predict_p1 as PP
from condfit import fit_eval                                            # noqa: E402                                                 # noqa: E402

N_FULL, N_W, A, L = 1200, 600, 0.25, 10.0
SEEDS, N_MAT = 200, 2048
DIALS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
FIT_DEGS = [5, 9, 13]
HELD_OUT = [7, 11]


def predict_cont(dial, deg):
    ell = N_W / dial
    u = np.linspace(0.0, float(N_FULL), 48001)
    x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
    x = x_of_u(u)
    lo, hi = (N_FULL - N_W) / 2.0, (N_FULL + N_W) / 2.0
    w = (u >= lo) & (u <= hi)
    # CONDITIONED FIT (2026-08-19 repair): raw polyfit on x spanning 0..1200 has
    # Vandermonde cond 2.9e40 at deg 13 and produced a spurious 96-sem cell.
    # Basis change only — identical model, verified a no-op at the sealed deg 5.
    fA = fit_eval(x, u, deg, x[w])
    fB = fit_eval(x[w], u[w] - lo, deg, x[w])
    return float(PP.spurious_var(fA, u[w], L) - PP.spurious_var(fB, u[w], L))


def centroid(res, dials):
    e = np.clip(np.abs(res) - np.median(np.abs(res)), 0.0, None)
    return float(np.sum(np.asarray(dials) * e) / np.sum(e)) if e.sum() > 0 else np.nan


def measure(deg, spectra, rng, dials=DIALS):
    cols = []
    for dial in dials:
        ell = N_W / dial
        x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
        p = predict_cont(dial, deg)
        col = []
        for s in range(len(spectra)):
            x = x_of_u(spectra[s])
            sA = sigma2_at(p1_apply(x, "unfold_then_window", deg, N_W), [L])[0]
            sB = sigma2_at(p1_apply(x, "window_then_unfold", deg, N_W), [L])[0]
            col.append(sA - sB - p)
        cols.append(col)
    M = np.asarray(cols, float)
    mean, sem = np.nanmean(M, axis=1), np.nanstd(M, axis=1, ddof=1) / np.sqrt(M.shape[1])
    c = centroid(mean, dials)
    boots = [centroid(np.nanmean(M[:, rng.integers(0, M.shape[1], M.shape[1])], axis=1), dials)
             for _ in range(2000)]
    boots = np.asarray([b for b in boots if np.isfinite(b)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    fails = [dials[i] for i in range(len(dials)) if abs(mean[i]) > 3.0 * sem[i]]
    return dict(deg=deg, dials=dials, residuals=mean.tolist(), sems=sem.tolist(),
                centroid=c, ci95=[float(lo), float(hi)], fail_dials=fails,
                max_sem_ratio=float(np.max(np.abs(mean) / sem)))


def main():
    spectra = []
    for s in range(SEEDS):
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        spectra.append(ua[lo:lo + N_FULL] - ua[lo])
    print(f"{SEEDS} seeds cached; measuring fit degrees {FIT_DEGS}\n")
    rng = np.random.default_rng(31)
    out = dict(seeds=SEEDS, dials=DIALS, fit_degs=FIT_DEGS, held_out=HELD_OUT, rows={})
    for deg in FIT_DEGS:
        r = measure(deg, spectra, rng)
        out["rows"][str(deg)] = r
        print(f"deg {deg:>2}: centroid {r['centroid']:.2f} CI [{r['ci95'][0]:.2f},"
              f"{r['ci95'][1]:.2f}]  FAIL dials {r['fail_dials']}", flush=True)

    d = np.array(FIT_DEGS, float)
    c = np.array([out["rows"][str(k)]["centroid"] for k in FIT_DEGS])
    lin = np.polyfit(d, c, 1)
    quad = np.polyfit(d, c, 2)
    lin_resid = float(np.max(np.abs(np.polyval(lin, d) - c)))
    out["fit"] = dict(linear=lin.tolist(), quadratic=quad.tolist(),
                      linear_max_resid=lin_resid)
    out["SEALED_PREDICTION"] = {}
    print(f"\nlinear fit ridge = {lin[0]:.3f}*deg {lin[1]:+.3f} (max resid {lin_resid:.3f})")
    print("\nSEALED PREDICTIONS for the held-out degrees:")
    for h in HELD_OUT:
        out["SEALED_PREDICTION"][str(h)] = dict(
            linear=float(np.polyval(lin, h)), quadratic=float(np.polyval(quad, h)),
            baseline_deg_minus_1_over_2=(h - 1) / 2.0)
        p = out["SEALED_PREDICTION"][str(h)]
        print(f"  deg {h:>2}: LINEAR {p['linear']:.2f}   QUADRATIC {p['quadratic']:.2f}"
              f"   BASELINE (deg-1)/2 {p['baseline_deg_minus_1_over_2']:.1f}")
    out["test"] = ("(i) a ridge cell appears near the predicted dial; "
                   "(ii) measured centroid lies between LINEAR and QUADRATIC; "
                   "(iii) measured centroid sits ABOVE BASELINE")
    json.dump(out, open(f"{ROOT}/holonomy/ridge_stageA.json", "w"), indent=1)
    print("\nstage A sealed -> holonomy/ridge_stageA.json (COMMIT BEFORE RUNNING STAGE B)")


if __name__ == "__main__":
    main()
