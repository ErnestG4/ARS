"""DOES A WIDER HORIZON LINEARISE THE MORPH? The pre-named follow-up.

COMMITTED GENERATOR of cross_substrate/brocot_horizon_resolution.json.
Predictions sealed here, before any output exists.

THE QUESTION, COMMITTED IN ADVANCE
-----------------------------------
`brocot_waypoint_scorer.json` missed the 3x bar at 1.31x and its sealed clause
named the follow-up rather than leaving it to be invented afterwards:

    "the honest conclusion is that the punctuation is not merely a
     parameterisation problem but a RESOLUTION limit of the tree itself at this
     index, and the fix would be to raise the index (widening the horizon, which
     admits more nodes) rather than to select more cleverly among the ones
     there."

The theorem makes that testable: the horizon is 2*order_bound(I), so raising I
mechanically admits more ringing nodes. If the residual roughness is granularity,
more nodes should smooth it. If it is scale-free — the space equally punctuated
at every resolution — more nodes will not help, and the morph is unlinearisable
in principle rather than in practice.

COMMENSURABILITY, FIXED THIS TIME
----------------------------------
The previous run compared a 12-waypoint node-pool reduction against a
24-waypoint continuous-grid reduction and called it like-for-like. It was not,
and the comparison was withdrawn. Here EVERY index uses the same waypoint count,
the same path, the same pool construction and the same metric, so only the index
varies and the cross-index comparison is valid by construction.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ R1  The below-horizon node count grows with I. (Mechanical from the theorem; ║
║     it is here as a liveness check on the sweep, not as a discovery.)        ║
║ R2  The reduction ratio RATIO_CV / TIMBRAL_CV improves monotonically with I. ║
║ R3  At some index within the instrument's stated range (I <= 3.0) the 3x bar ║
║     is met.                                                                  ║
║                                                                              ║
║ R3 IS THE ONE THAT DECIDES IT. If it misses, the punctuation is SCALE-FREE   ║
║ within the musical range: the space is equally rough at every resolution the ║
║ instrument can reach, and a smooth wormhole is not available by any waypoint ║
║ policy. That is a real result about the soundspace rather than a failure of  ║
║ method, and it would redirect the feature from "make morphs smooth" to       ║
║ "show the player where the jumps are" — which the horizon already computes.  ║
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

INDICES = [0.9, 1.5, 2.0, 3.0]
A0, A1 = Fraction(3, 4), Fraction(4, 3)
QMAX, N_WAY = 40, 12          # held FIXED across indices

POOL = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 60)
               if float(A0) <= p / q <= float(A1) and np.gcd(p, q) == 1}, key=float)


def u_of(alpha, I):
    sp = predict_partials([1.0, float(alpha)], [I, I], f_carrier=220.0)
    if sp.freqs.size < 20:
        return np.nan
    v = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    return np.nan if v is None else float(v)


def cv_max(seq, U):
    steps = np.abs(np.diff([U[f] for f in seq]))
    steps = steps[np.isfinite(steps)]
    if steps.size < 2 or steps.mean() <= 0:
        return np.nan, np.nan
    return float(steps.std() / steps.mean()), float(steps.max())


def pick_ratio(pool, n):
    out = []
    for t in np.linspace(float(A0), float(A1), n):
        c = min(pool, key=lambda f: abs(float(f) - t))
        if not out or c != out[-1]:
            out.append(c)
    return out


def pick_timbral(pool, n, U):
    seq = sorted(pool, key=float)
    d = [abs(U[seq[i + 1]] - U[seq[i]]) for i in range(len(seq) - 1)]
    total = float(np.nansum(d))
    if total <= 0:
        return seq[:n]
    step, acc, out = total / (n - 1), 0.0, [seq[0]]
    for i, inc in enumerate(d):
        acc += 0.0 if np.isnan(inc) else inc
        if acc >= step and len(out) < n - 1:
            out.append(seq[i + 1]); acc = 0.0
    out.append(seq[-1])
    return out


rows = {}
for I in INDICES:
    B = order_bound(I)
    hor = 2 * B
    U = {f: u_of(f, I) for f in POOL}
    usable = [f for f in POOL if np.isfinite(U[f])]
    below = [f for f in usable if max(f.numerator, f.denominator) <= hor]
    if len(below) < 4:
        rows[I] = dict(I=I, horizon=hor, n_below=len(below),
                       status="TOO_FEW_NODES")
        continue
    r_seq = pick_ratio(below, N_WAY)
    t_seq = pick_timbral(below, N_WAY, U)
    cv_r, mx_r = cv_max(r_seq, U)
    cv_t, mx_t = cv_max(t_seq, U)
    rows[I] = dict(I=I, order_bound=B, horizon=hor, status="MEASURED",
                   n_usable=len(usable), n_below=len(below),
                   cv_ratio=cv_r, cv_timbral=cv_t,
                   max_ratio=mx_r, max_timbral=mx_t,
                   reduction=(cv_r / cv_t) if cv_t and cv_t > 0 else np.nan)

print(f"path {A0} -> {A1}, {N_WAY} waypoints, pool q<={QMAX} "
      f"({len(POOL)} nodes) — held fixed across indices\n")
print(f"{'I':>5s} {'horizon':>8s} {'nodes below':>12s} {'CV ratio':>9s} "
      f"{'CV timbral':>11s} {'reduction':>10s} {'max step':>9s}")
for I in INDICES:
    r = rows[I]
    if r["status"] != "MEASURED":
        print(f"{I:>5.1f} {r['horizon']:>8d} {r['n_below']:>12d}  {r['status']}")
        continue
    print(f"{I:>5.1f} {r['horizon']:>8d} {r['n_below']:>12d} {r['cv_ratio']:>9.3f} "
          f"{r['cv_timbral']:>11.3f} {r['reduction']:>10.2f} {r['max_timbral']:>9.3f}")

meas = [rows[I] for I in INDICES if rows[I]["status"] == "MEASURED"]
counts = [r["n_below"] for r in meas]
reds = [r["reduction"] for r in meas]
r1 = all(a <= b for a, b in zip(counts, counts[1:]))
r2 = all(a <= b + 1e-9 for a, b in zip(reds, reds[1:]))
r3 = any(x >= 3.0 for x in reds)

verdict = ("LINEARISABLE_AT_HIGHER_INDEX" if r3 else
           "PUNCTUATION_IS_SCALE_FREE")

print(f"\nR1  below-horizon node count grows with I: {counts}   {'MET' if r1 else 'MISSED'}")
print(f"R2  reduction improves monotonically: {[round(x, 2) for x in reds]}   "
      f"{'MET' if r2 else 'MISSED'}")
print(f"R3  3x bar met somewhere in I <= 3.0   {'MET' if r3 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if not r3:
    print("  The punctuation is SCALE-FREE within the instrument's range: the space")
    print("  is equally rough at every resolution the depth slider can reach, so a")
    print("  smooth wormhole is not available by any waypoint policy. Per the sealed")
    print("  clause this redirects the feature from 'make morphs smooth' to 'show")
    print("  the player where the jumps are' — which the horizon already computes.")

with redpath("indices with a measured reduction", expect_min=3) as rp:
    rp.observed(len(meas))

json.dump(dict(indices=INDICES, a0=str(A0), a1=str(A1), n_way=N_WAY, qmax=QMAX,
               rows={str(k): v for k, v in rows.items()},
               node_counts=counts, reductions=reds,
               predictions=dict(R1=bool(r1), R2=bool(r2), R3=bool(r3)),
               verdict=verdict),
          open(f"{HERE}/brocot_horizon_resolution.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_horizon_resolution.json")
