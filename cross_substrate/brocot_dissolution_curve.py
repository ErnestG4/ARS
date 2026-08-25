"""FROM FOUR POINTS TO A CURVE: predicting the dissolution rate from (N, B, heights).

COMMITTED GENERATOR of cross_substrate/brocot_dissolution_curve.json.
Predictions sealed here, before any output exists.

WHY THIS IS WARRANTED AND NOT ORNAMENT
---------------------------------------
`brocot_horizon_extensions.json` measured the horizon dissolving at four operator
counts: 4.7% / 17.3% / 44.5% / 65.9% at N = 2,3,4,5. Two of those settle their own
question — N = 2 predicts, N = 5 does not. **N = 3 at 17.3% does not settle
anything**, and the shipped map carries a great many three-operator patches. Four
points cannot say whether N = 3 is usable; a formula can, and it also reaches the
N = 6…16 the instrument actually spans, which no feasible enumeration will.

THE ESTIMATOR
-------------
A coincidence needs Σ aᵢ·cᵢ = 0 over the box |aᵢ| ≤ A = 2B, where cᵢ are the
integer ratio coefficients on a common denominator. That sum is a lattice random
walk: with aᵢ uniform on [−A, A],

    Var(aᵢ) = A(A+1)/3          σ² = (A(A+1)/3) · Σ cᵢ²

The walk lands only on multiples of d = gcd(cᵢ), so a local CLT gives the density
at the origin as d/(σ√(2π)). With (2A+1)^N vectors in the box,

    E[solutions] ≈ (2A+1)^N · d / (σ √(2π))

Subtract the all-zero vector and treat occupancy as Poisson:

    P(coincidence) ≈ 1 − exp( −(E − 1) )

Nothing here is new machinery — it is the standard geometry-of-numbers count of
lattice points on a hyperplane through a box. **What is being tested is whether it
predicts THIS system**, where the cᵢ are ratio numerators and denominators rather
than generic integers, and where the horizon's whole point is that at N = 2 the
count is NOT well-approximated by an average.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ C1  The estimator tracks the measured rates at N = 2…5: every predicted rate  ║
║     within 0.15 of measured.                                                 ║
║ C2  It is WORST at N = 2, and that failure is expected rather than            ║
║     embarrassing — at N = 2 the solution set is one line, so an average-      ║
║     density argument is exactly the wrong tool and the horizon is the reason. ║
║     Concretely: |error| at N = 2 exceeds |error| at N = 5.                    ║
║ C3  Extrapolated to the instrument's range, the curve says the horizon is     ║
║     gone well before N = 16: predicted rate > 0.9 by N = 8.                   ║
║                                                                              ║
║ C1 IS THE ONE THAT DECIDES WHETHER THE CURVE SHIPS. If the estimator cannot   ║
║ reproduce four points it was fitted to nothing on, it has no business         ║
║ extrapolating to twelve. A miss means the dissolution profile stays four      ║
║ measured points and the N = 3 question stays open — which is a worse but      ║
║ honest answer.                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import math
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from existence import summarise, TREND                            # noqa: E402
from ratiopinned import counts as rp_counts                       # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B                       # box half-width
SEED, N_SETS = 20260824, 220    # same seed and sample size as the measured run
NS_MEASURED = [2, 3, 4, 5]
NS_CURVE = list(range(2, 17))
LO, HI, QMAX = 0.70, 1.40, 20

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 34)
                if LO <= p / q <= HI and gcd(p, q) == 1}, key=float)
MEASURED = json.load(open(f"{HERE}/brocot_horizon_extensions.json"))["operators"]


def coeffs(ratios):
    Q = 1
    for r in ratios:
        Q = Q * r.denominator // gcd(Q, r.denominator)
    return [r.numerator * (Q // r.denominator) for r in ratios]


def predict_rate(ratios):
    """P(a nonzero solution exists in the box), by local CLT."""
    c = coeffs(ratios)
    d = 0
    for ci in c:
        d = gcd(d, abs(ci))
    d = d or 1
    var = (A * (A + 1) / 3.0) * sum(ci * ci for ci in c)
    if var <= 0:
        return 1.0
    sigma = math.sqrt(var)
    total = (2 * A + 1) ** len(c)
    E = total * d / (sigma * math.sqrt(2 * math.pi))
    lam = max(E - 1.0, 0.0)
    return 1.0 - math.exp(-lam)


# measured rates come from the banked artifact; predicted are computed here
rows = []
for N in NS_CURVE:
    r = np.random.default_rng(SEED + N)
    preds = []
    for _ in range(N_SETS):
        idx = r.choice(len(NODES), size=min(N, len(NODES)), replace=False)
        preds.append(predict_rate([NODES[i] for i in idx]))
    row = dict(N=N, predicted=float(np.mean(preds)))
    key = str(N)
    if key in MEASURED:
        row["measured"] = MEASURED[key]["above_rate"]
        row["error"] = row["predicted"] - row["measured"]
    rows.append(row)

paired = [r for r in rows if "measured" in r]
c1 = all(abs(r["error"]) <= 0.15 for r in paired)
err2 = abs(next(r for r in paired if r["N"] == 2)["error"])
err5 = abs(next(r for r in paired if r["N"] == 5)["error"])
c2 = err2 > err5
by8 = next(r for r in rows if r["N"] == 8)["predicted"]
c3 = by8 > 0.9

trend = summarise("predicted", [r["predicted"] for r in rows], TREND, acknowledge=0.9)

print(f"I = {I_MUS}, B = {B}, box half-width A = 2B = {A}, {N_SETS} samples per N\n")
print(f"{'N':>3s} {'predicted':>10s} {'measured':>9s} {'error':>8s}")
for r in rows:
    m = f"{r['measured']:.3f}" if "measured" in r else "—"
    e = f"{r['error']:+.3f}" if "error" in r else ""
    print(f"{r['N']:>3d} {r['predicted']:>10.3f} {m:>9s} {e:>8s}")

print(f"\nC1  all |error| ≤ 0.15 over N = 2…5   {'MET' if c1 else 'MISSED'}")
print(f"C2  worst at N = 2 ({err2:.3f}) vs N = 5 ({err5:.3f})   {'MET' if c2 else 'MISSED'}")
print(f"C3  predicted > 0.9 by N = 8 ({by8:.3f})   {'MET' if c3 else 'MISSED'}")
print(f"\ncurve is {trend['direction']}, monotone={trend['monotone']}, "
      f"crosses 0.9 at N = {NS_CURVE[trend['crossing_index']] if trend['crossing_index'] is not None else '—'}")

verdict = "CURVE_VALIDATED" if c1 else "STAYS_FOUR_POINTS"
print(f"\nVERDICT: {verdict}")
if c1:
    n3 = next(r for r in rows if r["N"] == 3)
    print(f"  N = 3 answered: predicted {n3['predicted']:.1%} of above-horizon sets")
    print(f"  coincide anyway (measured {n3['measured']:.1%}) — the horizon is")
    print("  already substantially degraded at three operators.")
else:
    print("  The dissolution profile stays four measured points and the N = 3")
    print("  question stays open. Better a worse answer than a fitted one.")

with redpath("operator counts on the curve", expect_min=len(NS_CURVE)) as rp:
    rp.observed(len(rows))

json.dump(dict(I=I_MUS, B=B, A=A, n_sets=N_SETS, seed=SEED, rows=rows,
               errors={str(r["N"]): r["error"] for r in paired},
               trend=trend,
               predictions=dict(C1=bool(c1), C2=bool(c2), C3=bool(c3)),
               verdict=verdict),
          open(f"{HERE}/brocot_dissolution_curve.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_dissolution_curve.json")
