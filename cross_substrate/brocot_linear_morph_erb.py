"""LINEARISING THE MORPH ON THE COORDINATE THE PLAYER HEARS.

COMMITTED GENERATOR of cross_substrate/brocot_linear_morph_erb.json.
Predictions sealed here, before any output exists.

WHY THIS REOPENS A CLOSED QUESTION
-----------------------------------
Three linearisation attempts failed and the arc concluded "a smooth wormhole is
not available by any waypoint policy" — a sentence now merged into
COINCIDENCE-HORIZON.md as a property of the soundspace.

Every one of those attempts ran on **u**, the Brody statistic. Two measurements
since then say that was the wrong coordinate:

  * Spearman(|du|, |dERB|) = **+0.202**, CI [+0.122, +0.282]. The two agree that
    jumps happen and disagree about WHERE. u is not a proxy for what a player
    hears.
  * Only **5.7%** of top-decile ERB jumps sit at a partial-set change (baseline
    1.9%). So ERB's roughness is ~94% CONTINUOUS partial motion through critical
    bands — not discontinuities.

And that distinction is exactly the one the failure rested on. Arc-length
reparameterisation cannot smooth a PUNCTUATED coordinate, because a
discontinuity survives any reparameterisation. It is precisely the right tool for
a coordinate that is merely ROUGH. ERB is rougher than u overall (step CV 9.553
against 5.022) — and rougher is not punctuated.

So: the same method, the same path, the same 3x bar, on the coordinate that was
never tried.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ L1  Uniform-in-ratio spacing is badly non-uniform in ERB: step CV >= 0.8.    ║
║ L2  Arc-length reparameterisation ON ERB cuts that CV by at least 3x — the   ║
║     bar all three u-based attempts missed (1.6x, 1.31x, 1.74x).             ║
║ L3  It beats the best u-based attempt (1.74x).                              ║
║ L4  The worst single step shrinks by at least 2x — the arm that got WORSE    ║
║     on u (2.235 -> 2.670) and was the clearest sign the method was wrong     ║
║     for that coordinate.                                                    ║
║                                                                              ║
║ L2 IS THE CELL. If it holds, the merged document's universal sentence is     ║
║ wrong as written and becomes coordinate-relative: not linearisable on u,     ║
║ linearisable on ERB — and the feature flips back from "mark the jumps" to    ║
║ "morph smoothly, on the right metric".                                      ║
║                                                                              ║
║ If it misses, the universal claim survives a genuine attempt to break it on  ║
║ the coordinate most likely to break it, which is worth more than the         ║
║ original three failures combined.                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import predict_partials            # noqa: E402

I_MUS = 0.9
A0, A1 = 0.75, 1.3333333333333333      # the path the u-based attempt used
GRID, N_WAY = 1401, 24                 # and its waypoint count
FMIN, FMAX = 50.0, 12000.0
ERB_C = np.geomspace(FMIN, FMAX, 400)
U_BEST = 1.74                          # best u-based reduction, brocot_horizon_resolution


def erb_vec(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    f = np.asarray(sp.freqs, float)
    am = np.abs(np.asarray(sp.amps, float))
    m = (f >= FMIN) & (f <= FMAX) & (am > 0)
    f, am = f[m], am[m]
    v = np.zeros(len(ERB_C))
    for fr, pa in zip(f, am):
        w = 24.7 * (4.37 * fr / 1000.0 + 1.0)
        v += (pa * pa) * np.exp(-0.5 * ((ERB_C - fr) / w) ** 2)
    v = np.sqrt(v)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


grid = np.linspace(A0, A1, GRID)
V = [erb_vec(a) for a in grid]
d = np.array([float(np.linalg.norm(V[i + 1] - V[i])) for i in range(len(V) - 1)])
s = np.concatenate([[0.0], np.cumsum(d)])          # cumulative ERB arc length


def steps_for(alphas):
    W = [erb_vec(a) for a in alphas]
    return np.array([float(np.linalg.norm(W[i + 1] - W[i]))
                     for i in range(len(W) - 1)])


uniform = np.linspace(A0, A1, N_WAY)
arclen = np.interp(np.linspace(0, s[-1], N_WAY), s, grid)

su, sa = steps_for(uniform), steps_for(arclen)
cv_u = float(su.std() / su.mean())
cv_a = float(sa.std() / sa.mean())
red = cv_u / cv_a if cv_a > 0 else float("inf")

l1 = cv_u >= 0.8
l2 = red >= 3.0
l3 = red > U_BEST
l4 = sa.max() <= su.max() / 2.0

verdict = ("LINEARISABLE_ON_ERB" if l2 else
           "IMPROVED_NOT_LINEARISED" if l3 else "NOT_LINEARISABLE_ON_ERB")

print(f"path {A0:.4f} -> {A1:.4f} at I={I_MUS}, {N_WAY} waypoints, "
      f"ERB arc length {s[-1]:.3f}\n")
print(f"{'parameterisation':>22s} {'CV of per-step ERB':>20s} {'max step':>10s} "
      f"{'mean step':>10s}")
print(f"{'uniform in ratio':>22s} {cv_u:>20.3f} {su.max():>10.5f} {su.mean():>10.5f}")
print(f"{'arc length in ERB':>22s} {cv_a:>20.3f} {sa.max():>10.5f} {sa.mean():>10.5f}")

print(f"\nL1  uniform CV {cv_u:.3f} >= 0.8   {'MET' if l1 else 'MISSED'}")
print(f"L2  reduction {red:.2f}x >= 3   {'MET' if l2 else 'MISSED'}")
print(f"L3  beats the best u-based attempt ({U_BEST}x)   {'MET' if l3 else 'MISSED'}")
print(f"L4  worst step {su.max():.5f} -> {sa.max():.5f} "
      f"({su.max()/sa.max():.2f}x)   {'MET' if l4 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if l2:
    print("  The merged document's universal sentence is wrong as written. A smooth")
    print("  wormhole IS available -- on the coordinate a player hears. The feature")
    print("  flips back from 'mark the jumps' to 'morph smoothly, on ERB'.")
else:
    print("  The universal claim survives an attempt to break it on the coordinate")
    print("  most likely to break it, which is worth more than the three u-based")
    print("  failures combined. The document still needs the scope edit: the")
    print("  evidence is now u AND ERB, not u alone.")

with redpath("waypoint steps measured under both policies", expect_min=2 * (N_WAY - 2)) as rp:
    rp.observed(int(np.isfinite(su).sum() + np.isfinite(sa).sum()))

json.dump(dict(I=I_MUS, a0=A0, a1=A1, grid=GRID, n_way=N_WAY,
               arc_length=float(s[-1]), cv_uniform=cv_u, cv_arclength=cv_a,
               reduction=red, u_best_reduction=U_BEST,
               max_uniform=float(su.max()), max_arclength=float(sa.max()),
               predictions=dict(L1=bool(l1), L2=bool(l2), L3=bool(l3), L4=bool(l4)),
               verdict=verdict,
               waypoints_arclength=arclen.tolist()),
          open(f"{HERE}/brocot_linear_morph_erb.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_linear_morph_erb.json")
