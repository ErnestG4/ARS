"""The P1 dial-2.0 residual — is it a missing continuum TERM or a finite-n FLOOR?
COMMITTED GENERATOR of holonomy/p1_residual_scaling.json.

The residual is ISOLATED: at L=10 the measured-minus-predicted values across
the dial ladder are -0.003, +0.001, -0.008, **+0.224**, -0.006, with sems
~0.01-0.03.  Four dials agree with the continuum law to within noise and one
does not.  It is not a trend, it is a spike at a single point.

What is special about that point: dial 2.0 / L=10 is the ONLY cell in the
whole grid where the continuum prediction is NEGATIVE (-0.0128) — the
prediction passes through zero there.  The two candidate readings:

  MISSING TERM   — the continuum derivation omits a contribution that
                   happens to matter most where the leading term cancels.
                   A missing term is a property of the continuum, so it
                   SURVIVES as n grows.

  FINITE-n FLOOR — the near-total cancellation the continuum predicts is
                   exact only in the continuum; at finite n the fluctuation
                   floor breaks it, and where the leading term vanishes the
                   floor is all that is left.  A floor SHRINKS as n grows.

These make opposite predictions and the test is a clean scaling run.  The
geometry is held fixed — n_full, n_W, ell and L all scale together, so the
dial (n_W/ell) and L/W are identical at every n and only the point DENSITY
changes.  If the residual falls roughly as a power of n, it is the floor; if
it is flat, the continuum law is missing something.

PREDICTION, COMMITTED BEFORE THE RUN: the residual SHRINKS.  The absorption
term already computed for this arc (~0.003) is one finite-n effect of exactly
this kind and it was ~80x too small on its own; the reading here is that
several such effects, none individually large, are collectively what shows
through when the continuum term cancels.  A flat residual would falsify that
and send the derivation back for a missing term.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from transitions import gen_trended_set, p1_apply, sigma2_at, make_trend_maps  # noqa: E402
import predict_p1 as PP                                                        # noqa: E402

A = 0.25
DEG = 5
DIAL = 2.0
L_FRAC = 1.0 / 60          # the cell: L = n_W/60
SEEDS = 24
# SCALES: the substrate is a GUE spectrum, so scale k costs an O((2048k)^3)
# eigensolve — scale 4 (N=8192) is hours, not minutes. Two points give the
# direction (shrink vs flat), which is what the test needs; the power-law
# exponent from two points is reported but explicitly weak.
SCALES = [1, 2]             # n_full = 1200 * scale


def predict(n_full, n_W, ell, L):
    u = np.linspace(0.0, float(n_full), 48001)
    x_of_u, _ = make_trend_maps(A, ell, u_hi=float(n_full))
    x = x_of_u(u)
    lo, hi = (n_full - n_W) / 2.0, (n_full + n_W) / 2.0
    w = (u >= lo) & (u <= hi)
    cA = np.polyfit(x, u, DEG)
    cB = np.polyfit(x[w], u[w] - lo, DEG)
    return (PP.spurious_var(np.polyval(cA, x[w]), u[w], L)
            - PP.spurious_var(np.polyval(cB, x[w]), u[w], L))


def main():
    out = dict(dial=DIAL, L_frac=L_FRAC, deg=DEG, a=A, seeds=SEEDS,
               prediction="residual SHRINKS with n (finite-n floor); flat "
                          "would falsify and imply a missing continuum term",
               rows={})
    for sc in SCALES:
        n_full = 1200 * sc
        n_W = n_full // 2
        ell = n_W / DIAL
        L = L_FRAC * n_W
        pred = predict(n_full, n_W, ell, L)
        d = []
        for s in range(SEEDS):
            st = gen_trended_set(seed=s, N=int(2048 * sc), n_keep=n_full,
                                 a=A, ell=ell)
            Aq = p1_apply(st["x"], "unfold_then_window", DEG, n_W)
            Bq = p1_apply(st["x"], "window_then_unfold", DEG, n_W)
            sA = sigma2_at(Aq, [L])[0]
            sB = sigma2_at(Bq, [L])[0]
            d.append(sA - sB)
        d = np.asarray(d, float)
        d = d[np.isfinite(d)]
        meas = float(d.mean())
        sem = float(d.std(ddof=1) / np.sqrt(d.size))
        resid = meas - pred
        out["rows"][str(n_full)] = dict(
            n_full=n_full, n_W=n_W, ell=float(ell), L=float(L),
            predicted=float(pred), measured=meas, sem=sem,
            residual=float(resid), residual_over_sem=float(resid / sem))
        print(f"  n_full={n_full:>5} (n_W={n_W}, ell={ell:.0f}, L={L:.1f}): "
              f"meas {meas:+.4f}+-{sem:.4f}  pred {pred:+.4f}  "
              f"RESIDUAL {resid:+.4f} ({resid / sem:+.1f} sem)", flush=True)

    r = [out["rows"][str(1200 * s)]["residual"] for s in SCALES]
    n = [1200 * s for s in SCALES]
    # fit residual ~ n^alpha
    finite = [(x, y) for x, y in zip(n, r) if y > 0]
    if len(finite) >= 2:
        lx = np.log([f[0] for f in finite])
        ly = np.log([f[1] for f in finite])
        alpha = float(np.polyfit(lx, ly, 1)[0])
    else:
        alpha = None
    shrinks = bool(alpha is not None and alpha < -0.2)
    out["scaling"] = dict(residuals=r, n=n, power_law_exponent=alpha,
                          shrinks_with_n=shrinks,
                          verdict=("FINITE_N_FLOOR — the residual falls with "
                                   "n, so the continuum law is not missing a "
                                   "term; the cancellation it predicts is "
                                   "exact only in the continuum"
                                   if shrinks else
                                   "MISSING_TERM — the residual survives "
                                   "growing n, so the continuum derivation "
                                   "omits a real contribution"))
    json.dump(out, open(f"{ROOT}/holonomy/p1_residual_scaling.json", "w"),
              indent=1)
    print(f"\nresiduals {['%.4f' % x for x in r]} at n {n}")
    print(f"power-law exponent {alpha}  ->  {out['scaling']['verdict']}")


if __name__ == "__main__":
    main()
