"""WAYPOINT SELECTION OVER TREE NODES, scored by timbral distance.

COMMITTED GENERATOR of cross_substrate/brocot_waypoint_scorer.json.
Predictions and verdict lattice sealed here, before any output exists.

WHERE THIS COMES FROM
---------------------
`brocot_linear_morph.json` tried to linearise a ratio morph by arc-length
reparameterisation of a CONTINUOUS coordinate and failed: CV fell 1.6x against a
3x bar, and the worst step got worse. The diagnosis was that ratio space is
PUNCTUATED — coincidences appear and vanish discontinuously at every p/q below
the horizon — so no reparameterisation of a continuous coordinate can smooth it.

The redirect was to stop treating the path as continuous and choose WAYPOINTS
OVER TREE NODES, which is what Stern-Brocot navigation already is. This tests
that redirect against the same bar, on the same path, with the same metric, so
the comparison is like-for-like rather than a new number in a new frame.

THREE SELECTION POLICIES, same node pool, same waypoint count
--------------------------------------------------------------
  RATIO      the node nearest each uniformly-spaced ratio  (what Landscape does
             today: parameter distance)
  TIMBRAL    nodes walked in ratio order, placing a waypoint each time the
             accumulated |delta u| crosses total/N  (equal timbral travel)
  HORIZON    TIMBRAL, restricted to nodes with max(p,q) <= 2*order_bound(I) —
             the ones that can actually ring

PRIMARY METRIC IS |delta u|, deliberately. The ERB spectral distance is a richer
timbral measure and is reported alongside, but the 3x bar was set against |delta
u| in the failed continuous attempt, and moving the metric at the same time as
the method would make the comparison meaningless.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ N1  TIMBRAL selection beats RATIO selection on step-size CV by at least 3x   ║
║     — the bar the continuous attempt missed at 1.6x.                         ║
║ N2  It also beats the continuous arc-length result (1.6x reduction) on the   ║
║     same path and metric.                                                    ║
║ N3  HORIZON restriction does not make CV worse than TIMBRAL: excluding nodes ║
║     that cannot ring costs nothing in smoothness.                            ║
║                                                                              ║
║ I AM GENUINELY UNSURE ABOUT N1, and it is the whole point of the run. The    ║
║ node pool is DISCRETE, so waypoints cannot be placed at exactly equal         ║
║ timbral spacing — granularity sets a floor on CV that no policy can beat.    ║
║ If N1 misses, the honest conclusion is that the punctuation is not merely a  ║
║ parameterisation problem but a RESOLUTION limit of the tree itself at this   ║
║ index, and the fix would be to raise the index (widening the horizon, which  ║
║ admits more nodes) rather than to select more cleverly among the ones there. ║
║ That is a testable follow-up, not a retreat, and it is named here so it       ║
║ cannot be invented afterwards.                                               ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   SELECTION_LINEARISES      N1 holds                                          ║
║   IMPROVED_BUT_SHORT        beats continuous (N2) but misses the 3x bar      ║
║   NO_BETTER_THAN_CONTINUOUS N2 fails                                          ║
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
A0, A1 = Fraction(3, 4), Fraction(4, 3)
QMAX = 24
N_WAY = 12
FMIN, FMAX = 50.0, 12000.0
ERB_CENTRES = np.geomspace(FMIN, FMAX, 400)
CONTINUOUS_REDUCTION = 1.6      # banked in brocot_linear_morph.json

POOL = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 40)
               if float(A0) <= p / q <= float(A1) and np.gcd(p, q) == 1}, key=float)


def u_of(alpha):
    sp = predict_partials([1.0, float(alpha)], [I_MUS, I_MUS], f_carrier=220.0)
    if sp.freqs.size < 20:
        return np.nan
    v = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
    return np.nan if v is None else float(v)


def erb_vec(alpha):
    sp = predict_partials([1.0, float(alpha)], [I_MUS, I_MUS], f_carrier=220.0)
    f = np.asarray(sp.freqs, float)
    a = np.abs(np.asarray(sp.amps, float))
    m = (f >= FMIN) & (f <= FMAX) & (a > 0)
    f, a = f[m], a[m]
    v = np.zeros(len(ERB_CENTRES))
    for freq, amp in zip(f, a):
        w = 24.7 * (4.37 * freq / 1000.0 + 1.0)
        v += (amp * amp) * np.exp(-0.5 * ((ERB_CENTRES - freq) / w) ** 2)
    v = np.sqrt(v)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


U = {f: u_of(f) for f in POOL}
E = {f: erb_vec(f) for f in POOL}
usable = [f for f in POOL if np.isfinite(U[f])]      # 1/1 collapses; it is not a waypoint


def cv_of(seq, metric):
    if metric == "u":
        steps = np.abs(np.diff([U[f] for f in seq]))
    else:
        steps = np.array([np.linalg.norm(E[seq[i + 1]] - E[seq[i]])
                          for i in range(len(seq) - 1)])
    steps = steps[np.isfinite(steps)]
    return (float(steps.std() / steps.mean()) if steps.mean() > 0 else np.nan,
            float(steps.max()) if steps.size else np.nan)


def pick_ratio(pool, n):
    targets = np.linspace(float(A0), float(A1), n)
    out = []
    for t in targets:
        cand = min(pool, key=lambda f: abs(float(f) - t))
        if not out or cand != out[-1]:
            out.append(cand)
    return out


def pick_timbral(pool, n):
    """Walk nodes in ratio order; emit a waypoint each time accumulated |du|
    crosses total/n. The node-restricted analogue of arc length."""
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


B = order_bound(I_MUS)
HOR = 2 * B
below = [f for f in usable if max(f.numerator, f.denominator) <= HOR]

policies = {
    "RATIO": pick_ratio(usable, N_WAY),
    "TIMBRAL": pick_timbral(usable, N_WAY),
    "HORIZON": pick_timbral(below, min(N_WAY, len(below))),
}

res = {}
for name, seq in policies.items():
    cu, mu = cv_of(seq, "u")
    ce, me = cv_of(seq, "erb")
    res[name] = dict(n_waypoints=len(seq), cv_u=cu, max_step_u=mu,
                     cv_erb=ce, max_step_erb=me,
                     waypoints=[str(f) for f in seq])

print(f"path {A0} -> {A1} at I={I_MUS}   pool {len(POOL)} nodes "
      f"({len(usable)} usable, {len(below)} below horizon max(p,q)<={HOR})\n")
print(f"{'policy':>10s} {'waypoints':>10s} {'CV |du|':>9s} {'max |du|':>9s} "
      f"{'CV erb':>8s} {'max erb':>8s}")
for name in ("RATIO", "TIMBRAL", "HORIZON"):
    r = res[name]
    print(f"{name:>10s} {r['n_waypoints']:>10d} {r['cv_u']:>9.3f} {r['max_step_u']:>9.3f} "
          f"{r['cv_erb']:>8.3f} {r['max_step_erb']:>8.3f}")

red_t = res["RATIO"]["cv_u"] / res["TIMBRAL"]["cv_u"]
red_h = res["RATIO"]["cv_u"] / res["HORIZON"]["cv_u"]
n1 = red_t >= 3.0
n2 = red_t > CONTINUOUS_REDUCTION
n3 = res["HORIZON"]["cv_u"] <= res["TIMBRAL"]["cv_u"] * 1.05

verdict = ("SELECTION_LINEARISES" if n1 else
           "IMPROVED_BUT_SHORT" if n2 else "NO_BETTER_THAN_CONTINUOUS")

print(f"\nN1  TIMBRAL beats RATIO by {red_t:.2f}x  (>= 3 ?)   {'MET' if n1 else 'MISSED'}")
print(f"N2  and beats the continuous arc-length result ({CONTINUOUS_REDUCTION}x)   "
      f"{'MET' if n2 else 'MISSED'}")
print(f"N3  HORIZON restriction costs nothing ({red_h:.2f}x)   {'MET' if n3 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if not n1:
    print("  Per the sealed clause: the residual is a RESOLUTION limit of the node")
    print("  pool at this index, not a selection failure. The follow-up is to raise")
    print("  the index — which widens the horizon and admits more nodes — not to")
    print("  select more cleverly among the ones available.")

with redpath("policies producing a usable waypoint sequence", expect_min=3) as rp:
    rp.observed(sum(1 for r in res.values() if r["n_waypoints"] >= 3
                    and np.isfinite(r["cv_u"])))

json.dump(dict(I=I_MUS, a0=str(A0), a1=str(A1), n_way=N_WAY, qmax=QMAX,
               horizon=HOR, pool=len(POOL), usable=len(usable), below=len(below),
               continuous_reduction=CONTINUOUS_REDUCTION,
               reduction_timbral=red_t, reduction_horizon=red_h,
               policies=res,
               predictions=dict(N1=bool(n1), N2=bool(n2), N3=bool(n3)),
               verdict=verdict),
          open(f"{HERE}/brocot_waypoint_scorer.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_waypoint_scorer.json")
