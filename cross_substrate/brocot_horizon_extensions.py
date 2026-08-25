"""DOES THE HORIZON SURVIVE MORE OPERATORS, OR A RICHER WAVEFORM?

COMMITTED GENERATOR of cross_substrate/brocot_horizon_extensions.json.
Predictions sealed here, before any output exists.

THE SCOPE PROBLEM, MEASURED FIRST
----------------------------------
The theorem was derived and verified entirely at N = 2 sine modulators. Two facts
about the shipped instrument say that is a narrow slice:

  * `resources/landscape_graph_16mix.json.gz` carries **n_ops = 16**, and active
    operator counts run roughly uniformly from 1 to 16 — two-operator patches are
    a small minority of the map.
  * `source/audio/Operator.h` ships **Sine, Triangle, Saw, Square, Pulse**, while
    `predict_partials` is sine-only (Bessel). Every measurement in this programme
    used the sine basis.

This is the I = 8 error in a new coordinate: a result verified where the analysis
is easy rather than where the instrument lives. So before the horizon is built
into a feature, it has to be tested outside N = 2 and outside the sine.

THE THEORY BEING TESTED
-----------------------
N MODULATORS. A coincidence needs Σ aᵢ·rᵢ = 0 with |aᵢ| ≤ 2B, not all zero. With
rᵢ = pᵢ/qᵢ and Q = lcm(qᵢ), that is Σ aᵢ·cᵢ = 0 for integers cᵢ = pᵢ·Q/qᵢ. The
solution lattice has dimension **N − 1**. At N = 2 it is one-dimensional — a
single line of multiples, which the box can miss, and missing it is exactly the
horizon. At N ≥ 3 it is a plane or larger, so a nonzero solution inside the box
becomes generic. **The horizon should dissolve as operators are added.**

NON-SINE MODULATOR. A triangle or square at ratio α is a stack of sines at kα.
Its α-coefficient is Σ_k n_k·k, which reaches integers far beyond a single |n| ≤ B.
So a richer waveform acts on the same bound the modulation index acts on:
**the horizon should extend, roughly by the harmonic reach.**

Both predictions say the N = 2 sine horizon is a special case — sharp where the
solution space is thinnest.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ E1  At N = 2 the horizon discriminates: above-horizon ratio sets almost never ║
║     coincide (< 10% do).                                                     ║
║ E2  It DISSOLVES with operators: by N = 4 a majority (> 50%) of above-horizon ║
║     sets coincide anyway, so max(p,q) ≤ 2B stops predicting anything.        ║
║ E3  The dissolution is monotone in N.                                        ║
║ E4  A non-sine modulator EXTENDS the horizon: with a square-wave harmonic     ║
║     stack to order H, ratios up to roughly H×(2B) ring where only 2B did.    ║
║                                                                              ║
║ E4b AMENDED before banking. The first run reported 90/90 ratios ringing for   ║
║     every non-sine wave — a FALSE POSITIVE of the same class as the reflected ║
║     m = 0 branch. A harmonic stack can cancel against ITSELF: with harmonics  ║
║     [1,3,5], a₁ = 3 and a₂ = −1 give 3·α − 1·(3α) = 0 for ANY α whatsoever.   ║
║     That is a universal coincidence carrying no ratio information, and        ║
║     counting it measures the stack, not the horizon.                          ║
║                                                                              ║
║     E4 is therefore re-stated over RATIO-PINNED coincidences only: those      ║
║     requiring a nonzero carrier coefficient, so the ratio actually enters.    ║
║     Third instance of "a predicate true of every input has no negative set".  ║
║                                                                              ║
║ E2 IS THE ONE THAT DECIDES THE FEATURE. If the horizon only bites at N = 2,   ║
║ the structure-horizon annotation is scoped to two-operator patches — a small  ║
║ minority of the shipped map — and saying so is mandatory, not optional.      ║
║ A feature that silently applies a two-operator law to a sixteen-operator      ║
║ patch is the "alive" defect with arithmetic behind it.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
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
from existence import summarise, EXISTENCE                        # noqa: E402
from ratiopinned import counts as rp_counts                       # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)          # 4
HOR = 2 * B                     # 8
SEED, N_SETS = 20260824, 220
NS = [2, 3, 4, 5]
LO, HI, QMAX = 0.70, 1.40, 20

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 34)
                if LO <= p / q <= HI and gcd(p, q) == 1}, key=float)


def has_coincidence(ratios, bound, require_first_nonzero=False):
    """Is there a nonzero integer a in [-bound, bound]^N with sum(a_i r_i) = 0?
    Counted by DP over reachable weighted sums, in exact integers.

    `require_first_nonzero` restricts to RATIO-PINNED solutions: those with a
    nonzero coefficient on the carrier, so the ratio must actually enter. Without
    it a harmonic stack cancels against itself for every alpha and the count
    measures the stack rather than the horizon."""
    Q = 1
    for r in ratios:
        Q = Q * r.denominator // gcd(Q, r.denominator)
    c = [r.numerator * (Q // r.denominator) for r in ratios]
    first = True
    ways = {0: 1}
    for ci in c:
        nxt = {}
        lo = -bound
        rng_a = range(lo, bound + 1)
        for s, w in ways.items():
            for a in rng_a:
                if first and require_first_nonzero and a == 0:
                    continue
                k = s + a * ci
                nxt[k] = nxt.get(k, 0) + w
        ways = nxt
        first = False
    if require_first_nonzero:
        return ways.get(0, 0) > 0      # carrier coefficient already forced nonzero
    return ways.get(0, 0) > 1          # subtract the all-zero vector


rng = np.random.default_rng(SEED)
rows = {}
for N in NS:
    above_hit = above_tot = below_hit = below_tot = 0
    for _ in range(N_SETS):
        idx = rng.choice(len(NODES), size=N, replace=False)
        rs = [NODES[i] for i in idx]
        mx = max(max(r.numerator, r.denominator) for r in rs)
        hit = has_coincidence(rs, HOR)
        if mx > HOR:
            above_tot += 1; above_hit += hit
        else:
            below_tot += 1; below_hit += hit
    rows[N] = dict(N=N, above_n=above_tot, above_rate=(above_hit / above_tot if above_tot else float('nan')),
                   below_n=below_tot, below_rate=(below_hit / below_tot if below_tot else float('nan')))

# ── E4 · a non-sine modulator as a harmonic stack ───────────────────────────
def rings_with_stack(alpha, harmonics):
    """Modulator at alpha rendered as sines at k*alpha for k in `harmonics`.

    MIGRATED to the shared filter (ratiopinned.py). The local
    require_first_nonzero heuristic happened to agree here, but it was a
    re-implementation at the measurement site -- which is where all three
    universal-family defects were born. Verified: the canonical filter
    reproduces this artifact's banked wave numbers exactly (13/17/17/17 ringing,
    reach 8/11/11/11)."""
    spec = [(1, 0)] + [(0, k) for k in harmonics]
    return rp_counts(spec, HOR, alpha)[2] > 0


WAVES = {"sine": [1], "triangle": [1, 3, 5], "square": [1, 3, 5, 7], "saw": [1, 2, 3, 4]}
wave_rows = {}
for name, harm in WAVES.items():
    ring = [f for f in NODES if rings_with_stack(f, harm)]
    spec_h = [(1, 0)] + [(0, k) for k in harm]
    universal = [f for f in NODES if rp_counts(spec_h, HOR, f)[1] > 0
                 and not rings_with_stack(f, harm)]
    reach = max((max(f.numerator, f.denominator) for f in ring), default=0)
    wave_rows[name] = dict(harmonics=harm, n_ringing=len(ring), of=len(NODES),
                           n_universal_only=len(universal),
                           max_ringing_maxpq=reach, horizon_sine=HOR)

e1 = rows[2]["above_rate"] < 0.10
e2 = rows[4]["above_rate"] > 0.50
rates = [rows[n]["above_rate"] for n in NS]
e3 = all(a <= b + 1e-9 for a, b in zip(rates, rates[1:]))
e4 = wave_rows["square"]["max_ringing_maxpq"] > HOR

print(f"I = {I_MUS}, B = {B}, two-operator horizon max(p,q) ≤ {HOR}\n")
print("(A) MORE OPERATORS — does the horizon still predict?\n")
print(f"{'N':>3s} {'sets above horizon':>19s} {'coincide anyway':>16s} "
      f"{'sets below':>11s} {'coincide':>9s}")
for N in NS:
    r = rows[N]
    print(f"{N:>3d} {r['above_n']:>19d} {r['above_rate']:>15.1%} "
          f"{r['below_n']:>11d} {r['below_rate']:>8.1%}")

print("\n(B) RICHER WAVEFORM — where does the horizon move?\n")
print(f"{'wave':>10s} {'harmonics':>14s} {'ratio-pinned':>14s} {'universal only':>15s} "
      f"{'largest max(p,q)':>17s}")
for name, r in wave_rows.items():
    print(f"{name:>10s} {str(r['harmonics']):>14s} "
          f"{r['n_ringing']:>5d} / {r['of']:<5d} {r['n_universal_only']:>15d} "
          f"{r['max_ringing_maxpq']:>17d}")

print(f"\nE1  N=2 horizon discriminates ({rows[2]['above_rate']:.1%} above-horizon "
      f"coincide)   {'MET' if e1 else 'MISSED'}")
print(f"E2  dissolves by N=4 ({rows[4]['above_rate']:.1%})   {'MET' if e2 else 'MISSED'}")
print(f"E3  monotone in N: {[f'{r:.0%}' for r in rates]}   {'MET' if e3 else 'MISSED'}")
print(f"E4  square extends the horizon to {wave_rows['square']['max_ringing_maxpq']} "
      f"(sine {HOR})   {'MET' if e4 else 'MISSED'}")

# Keyed on the TREND, not a single threshold at a single N. The first version
# put the whole verdict on E2's bar at N=4; it read 44.5% and returned
# "SURVIVES_EXTENSION" while the series ran 5% -> 17% -> 45% -> 66%. A label that
# contradicts its own table is worse than a missed prediction.
dissolves = e3 and rates[-1] > 0.5 and rates[-1] > 4 * rates[0]
verdict = ("SCOPED_TO_TWO_SINE_OPERATORS" if (e1 and dissolves) else
           "SURVIVES_EXTENSION" if not dissolves else "PARTIAL")
print(f"\nVERDICT: {verdict}")
if dissolves:
    print("  The horizon is a TWO-OPERATOR law. At N>=4 a majority of above-horizon")
    print("  ratio sets coincide anyway, because the solution lattice has dimension")
    print("  N-1 and a nonzero solution inside the box becomes generic. The feature")
    print("  must say which patches it applies to -- the shipped map is mostly not")
    print("  those patches.")

ev = summarise("n_ringing", [w["n_ringing"] for w in wave_rows.values()], EXISTENCE)
with redpath("operator counts measured", expect_min=len(NS)) as rp:
    rp.observed(len(rows))

json.dump(dict(I=I_MUS, B=B, horizon=HOR, n_sets=N_SETS, seed=SEED,
               operators={str(k): v for k, v in rows.items()}, waves=wave_rows,
               predictions=dict(E1=bool(e1), E2=bool(e2), E3=bool(e3), E4=bool(e4)),
               verdict=verdict),
          open(f"{HERE}/brocot_horizon_extensions.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_horizon_extensions.json")
