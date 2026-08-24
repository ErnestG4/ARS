"""MAKING THE WORMHOLE LINEAR: arc-length reparameterisation of a ratio morph.

COMMITTED GENERATOR of cross_substrate/brocot_linear_morph.json.
Predictions sealed here, before any output exists.

THE PROBLEM, MEASURED
---------------------
`source/pull/Landscape.h` walks waypoints by PARAMETER distance and
`PullIndex::morph` interpolates between them. `brocot_ratio_sensitivity.json`
measured the timbral gradient across the instrument's defining ratio range at
I = 0.9: p90/p10 = 12x, and 6.5x higher near simple rationals than in the
plateaus.

So a morph taking uniform steps in RATIO takes wildly non-uniform steps in
TIMBRE. Audibly: it lurches through the near-rational regions and stalls in the
plateaus. That is a property of the soundspace, so no amount of smoothing inside
the interpolator fixes it — the fix has to change WHERE the waypoints go.

THE FIX
-------
Reparameterise by arc length in timbre rather than in ratio. Let

    s(alpha) = integral of |du/dalpha| from alpha_0 to alpha

and place waypoints at equal increments of s instead of equal increments of
alpha. Steps then carry equal timbral change by construction. s is a 1-D
cumulative integral of a quantity already computed offline, so this costs one
extra precomputed array per axis and nothing at all at runtime.

WHAT IS BEING TESTED
--------------------
Whether the reparameterisation actually equalises per-step timbral change on a
real path through the instrument's own range, at its own modulation index.
Measured by the coefficient of variation (sd/mean) of per-step |delta u| — low CV
means every step of the morph moves the timbre by about the same amount, which is
what "linear" means for a wormhole.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ W1  The UNIFORM-in-ratio morph has high per-step variability: CV >= 0.8.     ║
║ W2  Arc-length reparameterisation cuts it by at least 3x.                    ║
║ W3  The reparameterised path spends MORE waypoints in the high-gradient      ║
║     (near-rational) regions and fewer in the plateaus — which is the         ║
║     mechanism, not a side effect: linear travel means slowing down where the ║
║     ground moves fast.                                                       ║
║ W4  The worst single step shrinks: max |delta u| per step falls by >= 2x.    ║
║                                                                              ║
║ W2 COULD FAIL HONESTLY. If u(alpha) is not merely steep in places but        ║
║ genuinely rough -- non-monotone at the sampling scale -- then arc length is   ║
║ estimated from a noisy derivative and reparameterising on it will not         ║
║ equalise anything. That outcome would say the wormhole cannot be linearised   ║
║ by reweighting alone, and would point at smoothing u first. Stated here so    ║
║ the negative result has somewhere to land.                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS = 0.9
A0, A1 = 0.75, 1.3333333333333333     # 3/4 -> 4/3, across the defining regime
GRID = 1401                            # dense sampling for the arc-length integral
N_WAY = 24                             # waypoints a morph would actually place


def u_of(alpha):
    sp = predict_partials([1.0, float(alpha)], [I_MUS, I_MUS], f_carrier=220.0)
    if sp.freqs.size < 20:
        return np.nan
    v = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    return np.nan if v is None else float(v)


grid = np.linspace(A0, A1, GRID)
u = np.array([u_of(a) for a in grid])
good = np.isfinite(u)
# interpolate across the degenerate points (1/1 collapses to 6 partials) rather
# than dropping them: a morph has to cross them, so the path must be defined there
u_i = np.interp(grid, grid[good], u[good])

du = np.abs(np.gradient(u_i, grid))
s = np.concatenate([[0.0], np.cumsum((du[1:] + du[:-1]) / 2 * np.diff(grid))])


def steps_for(alphas):
    vals = np.array([u_of(a) for a in alphas])
    ok = np.isfinite(vals)
    vals = np.interp(alphas, alphas[ok], vals[ok]) if ok.sum() > 1 else vals
    return np.abs(np.diff(vals))


uniform = np.linspace(A0, A1, N_WAY)
arclen = np.interp(np.linspace(0, s[-1], N_WAY), s, grid)

su, sa = steps_for(uniform), steps_for(arclen)
cv_u = float(su.std() / su.mean())
cv_a = float(sa.std() / sa.mean())


def near_frac(x, mq=6):
    return min(abs(x - round(x * q) / q) for q in range(1, mq + 1) if round(x * q) != 0)


near_u = int(sum(near_frac(a) < 0.02 for a in uniform))
near_a = int(sum(near_frac(a) < 0.02 for a in arclen))

w1 = cv_u >= 0.8
w2 = cv_a <= cv_u / 3.0
w3 = near_a > near_u
w4 = sa.max() <= su.max() / 2.0

B = order_bound(I_MUS)
print(f"path {Fraction(A0).limit_denominator(8)} -> "
      f"{Fraction(A1).limit_denominator(8)} at I={I_MUS} "
      f"(structure horizon max(p,q) <= {2*B})")
print(f"grid {GRID} points, {N_WAY} waypoints, total timbral arc length "
      f"s = {s[-1]:.2f}\n")
print(f"{'parameterisation':>22s} {'CV of per-step |du|':>21s} {'max step':>10s} "
      f"{'mean step':>10s} {'waypoints near p/q':>20s}")
print(f"{'uniform in ratio':>22s} {cv_u:>21.3f} {su.max():>10.3f} {su.mean():>10.3f} "
      f"{near_u:>20d}")
print(f"{'arc length in timbre':>22s} {cv_a:>21.3f} {sa.max():>10.3f} {sa.mean():>10.3f} "
      f"{near_a:>20d}")

print(f"\nW1  uniform CV {cv_u:.3f} >= 0.8   {'MET' if w1 else 'MISSED'}")
print(f"W2  arc-length CV {cv_a:.3f} <= {cv_u/3:.3f}  ({cv_u/cv_a:.1f}x reduction)   "
      f"{'MET' if w2 else 'MISSED'}")
print(f"W3  waypoints near a simple ratio: {near_u} uniform -> {near_a} arc-length   "
      f"{'MET' if w3 else 'MISSED'}")
print(f"W4  worst step {su.max():.3f} -> {sa.max():.3f}  ({su.max()/sa.max():.1f}x)   "
      f"{'MET' if w4 else 'MISSED'}")

verdict = ("LINEARISABLE" if w1 and w2 else
           "ALREADY_LINEAR" if not w1 else "NOT_LINEARISABLE_BY_REWEIGHTING")
print(f"\nVERDICT: {verdict}")

with redpath("finite u samples on the morph grid", expect_min=int(0.9 * GRID)) as rp:
    rp.observed(int(good.sum()))

json.dump(dict(I=I_MUS, a0=A0, a1=A1, grid=GRID, n_waypoints=N_WAY,
               arc_length_total=float(s[-1]), structure_horizon=2 * B,
               cv_uniform=cv_u, cv_arclength=cv_a,
               cv_reduction=float(cv_u / cv_a),
               max_step_uniform=float(su.max()), max_step_arclength=float(sa.max()),
               waypoints_near_simple=dict(uniform=near_u, arclength=near_a),
               degenerate_grid_points=int((~good).sum()),
               predictions=dict(W1=bool(w1), W2=bool(w2), W3=bool(w3), W4=bool(w4)),
               verdict=verdict,
               waypoints_uniform=uniform.tolist(), waypoints_arclength=arclen.tolist()),
          open(f"{HERE}/brocot_linear_morph.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_linear_morph.json")
