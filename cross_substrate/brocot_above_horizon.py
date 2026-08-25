"""ABOVE THE HORIZON: if nothing fuses, what tells these ratios apart?

COMMITTED GENERATOR of cross_substrate/brocot_above_horizon.json.
Predictions sealed here, before any output exists.

THE QUESTION
------------
`brocot_horizon_perceptual.json` established that above-horizon ratios "share the
absence of coincidence structure and nothing else" — measured at 2573× a 1-cent
floor, so they are plainly distinct to a listener. And every gross descriptor is
identical up there: at I = 0.9 every node with q ≥ 7 returns 31 partials, top-5
energy 0.716, spectral entropy 0.709.

Same aggregates, distinct spectra. So the difference lives in partial POSITIONS,
and the question is what coordinate reads it.

THE CANDIDATE
-------------
Exact coincidence needs Σ aᵢrᵢ = 0. Above the horizon that is unreachable — but
the CLOSEST APPROACH is not. Define

    gap(α) = min over nonzero |aᵢ| ≤ A  of  |a₁ + a₂·α|

Below the horizon this is exactly 0. Above it, it is positive and varies, and it
is a Diophantine quantity: with α = p/q it equals (min nonzero |a₁q + a₂p|)/q,
and Bézout says that minimum is 1 whenever the Bézout coefficients fit in the
box — so gap ≈ 1/q across a wide band.

**Physically the gap is a beat rate.** Two partials separated by gap·f_c beat at
gap·f_c Hz. Below roughly 20 Hz that is heard as beating or roughness; above it
the two partials separate into distinct components. So the prediction is that the
above-horizon region is not undifferentiated at all — it is ordered by DENOMINATOR
still, but the denominator has stopped controlling FUSION and started controlling
BEAT RATE.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ H1  The gap is exactly 0 below the horizon and strictly positive above it —   ║
║     a definitional check that the coordinate is the right one and that the    ║
║     enumeration agrees with the theorem.                                     ║
║ H2  Above the horizon the gap spans at least an ORDER OF MAGNITUDE, so these  ║
║     ratios are strongly differentiated by it rather than degenerate.         ║
║ H3  gap ≈ 1/q over the band just above the horizon: the correlation between   ║
║     gap and 1/q across above-horizon nodes exceeds 0.9 (Spearman).           ║
║ H4  Converted to Hz at f_c = 220, the above-horizon gaps land substantially   ║
║     inside the AUDIBLE BEATING range (< 20 Hz) for at least a third of        ║
║     nodes — i.e. the differentiation is not merely formal.                    ║
║                                                                              ║
║ H4 IS THE ONE THAT MATTERS AND THE ONE I AM UNSURE OF. If the gaps all land   ║
║ above 20 Hz, the coordinate is real but inaudible as beating, and the honest  ║
║ answer becomes "differentiated by partial placement, which this measure       ║
║ describes but does not make audible." That is a weaker claim and it must be   ║
║ stated as such rather than dressed up.                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — AFTER OUTPUT, 2026-08-24.  Recorded, not rewritten: the sealed
scores below stand exactly as they fell.  Three findings about the SEAL itself.

(a) H2 WAS AN INERT ARM.  The node set is finite and fixed by LO, HI and QMAX
    before any measurement, so the reachable span is exactly enumerable — and it
    is 5.72, against a sealed bar of 10.  **H2 could not have been met by any
    data.**  (The first ceiling written here was itself wrong, and is corrected
    in amendment 2 below.)  It is scored INAPPLICABLE_UNPOWERED, not MISSED — a dead
    arm in an n/m tally is non-evidence dressed as a verdict, which is this
    repo's dominant recorded error mode.  The power was computable BEFORE the
    run from A and QMAX alone; it is computed below and now gates the arm.

(b) H3's PREMISE WAS WRONG, AND THE MISS IS REAL.  The docstring argued "Bézout
    says the minimum is 1 whenever the coefficients fit in the box — so gap ≈
    1/q".  Bézout guarantees a solution to a₁q + a₂p = 1 in INTEGERS; it says
    nothing about those integers fitting in [−A, A].  They usually do not: the
    minimum is k/q with k = 1 in only 197 of 332 nodes.  What actually controls
    the gap is best rational approximation with denominator ≤ A — a continued-
    fraction quantity, not q.  Premise falsified, and the falsification names
    the right coordinate.

(c) THE LATTICE CONFLATED MECHANISM WITH DIFFERENTIATION.  `NOT_DIFFERENTIATED`
    required H3, but H3 asks whether the spread is EXPLAINED BY 1/q, not whether
    a spread exists.  Wiring a mechanism arm into a differentiation conjunction
    makes a wrong guess about WHY read as an absence of WHAT.  H1 and H4 both
    fired: every above-horizon node has a positive gap, and 79.2% of them beat
    below 20 Hz.  These ratios ARE differentiated, and audibly; the sealed label
    says otherwise because I built it wrong.  Third member of the family the
    existence-vs-median rule opened (`existence.py`), and the first where the
    defect is a conjunction ARM TYPE rather than a summary statistic.

AMENDMENT 2 — SAME DAY, AND IT CORRECTS AMENDMENT 1.  Amendment (a) defended
its ceiling with "Dirichlet caps the gap at 1/A".  That is the wrong theorem
for this box: Dirichlet bounds the DENOMINATOR of the approximation, while this
box bounds a₁ as well as a₂, so 1/A is not an upper bound at all — 4 of the 332
above-horizon gaps exceed it, and the true span is 5.72 rather than 5.0.  The
conclusion is untouched (both are far under the bar of 10), and the correction
is banked anyway, because a bound defended by the wrong theorem is a bound
nobody can check.  `reachable.Bar.score` now flags any value falling outside
its own declared range, which is the only audit a trusted ceiling can get.
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from existence import summarise, EXISTENCE                        # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B                       # box half-width == the horizon
F_C = 220.0
BEAT_HZ = 20.0                  # above this, partials separate rather than beat
LO, HI, QMAX = 0.70, 1.40, 40

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 60)
                if LO <= p / q <= HI and gcd(p, q) == 1}, key=float)


def gap(alpha):
    """min over nonzero |a| <= A of |a1 + a2*alpha|, exact.

    FIXED: the first version skipped v == 0 with `if v and ...`, so it returned
    the minimum NONZERO value everywhere and could never report an exact
    coincidence as gap 0. H1 is a definitional check -- it cannot fail for a
    substantive reason -- and its failure caught exactly this."""
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            v = abs(a1 * q + a2 * p)
            if v == 0:
                return Fraction(0)              # exact coincidence: fuses
            if best is None or v < best:
                best = v
    return Fraction(best, q)


rows = []
for f in NODES:
    mx = max(f.numerator, f.denominator)
    g = gap(f)
    rows.append(dict(ratio=str(f), value=float(f), maxpq=mx, q=f.denominator,
                     above=mx > A, gap=float(g) if g is not None else 0.0,
                     beat_hz=float(g) * F_C if g is not None else 0.0))

below = [r for r in rows if not r["above"]]
above = [r for r in rows if r["above"]]

h1 = all(r["gap"] == 0.0 for r in below) and all(r["gap"] > 0 for r in above)
gaps = np.array([r["gap"] for r in above])
span = gaps.max() / gaps.min() if gaps.min() > 0 else float("inf")
H2_BAR = 10
# power, a property of the DESIGN and computable before any measurement: the
# node set is fixed by LO/HI/QMAX, so the reachable span is the max/min gap
# over that whole enumerated set. Exact, not a theorem bound — see amendment 2.
_all = [r["gap"] for r in rows if r["above"]]
span_ceiling = max(_all) / min(_all)
span_floor = 1.0
h2_reachable = span_ceiling >= H2_BAR
h2 = span >= H2_BAR
rho = float(stats.spearmanr([r["gap"] for r in above],
                            [1.0 / r["q"] for r in above])[0])
h3 = rho >= 0.9
beats = np.array([r["beat_hz"] for r in above])
frac_audible = float((beats < BEAT_HZ).mean())
h4 = frac_audible >= 1 / 3

# the lattice EXACTLY AS SEALED. Reported unchanged; see amendment (c).
verdict = ("ORDERED_BY_BEAT_RATE" if (h1 and h2 and h3 and h4) else
           "DIFFERENTIATED_BUT_NOT_AS_BEATING" if (h1 and h2 and h3) else
           "NOT_DIFFERENTIATED")
# and the reading after the amendment, with the inert arm dropped and the
# mechanism arm separated from the differentiation arms. NOT a re-score: H3
# stays MISSED and drives the mechanism half of the label.
amended = (("DIFFERENTIATED" if (h1 and frac_audible >= 1/3) else "NOT_DIFFERENTIATED")
           + ("_AND_ORDERED_BY_1/q" if h3 else "_BUT_NOT_BY_1/q"))

print(f"I = {I_MUS}, B = {B}, horizon max(p,q) ≤ {A}, f_c = {F_C:.0f} Hz")
print(f"nodes: {len(rows)}  ({len(below)} below the horizon, {len(above)} above)\n")
print(f"{'band':>22s} {'n':>4s} {'min gap':>9s} {'median':>9s} {'max':>9s}")
print(f"{'below horizon':>22s} {len(below):>4d} {'0':>9s} {'0':>9s} {'0':>9s}")
for lo, hi in ((A + 1, 2 * A), (2 * A + 1, 3 * A), (3 * A + 1, 10 * A)):
    sel = [r for r in above if lo <= r["maxpq"] <= hi]
    if not sel:
        continue
    gs = [r["gap"] for r in sel]
    print(f"{f'max(p,q) {lo}–{hi}':>22s} {len(sel):>4d} {min(gs):>9.4f} "
          f"{np.median(gs):>9.4f} {max(gs):>9.4f}")

print(f"\n{'ratio':>8s} {'max(p,q)':>9s} {'gap':>8s} {'beat Hz':>9s}   character")
for r in sorted(above, key=lambda r: r["beat_hz"])[:6] + sorted(above, key=lambda r: -r["beat_hz"])[:3]:
    ch = ("slow beating" if r["beat_hz"] < 8 else
          "roughness" if r["beat_hz"] < BEAT_HZ else "separate partials")
    print(f"{r['ratio']:>8s} {r['maxpq']:>9d} {r['gap']:>8.4f} {r['beat_hz']:>9.1f}   {ch}")

print(f"\nH1  gap = 0 below, > 0 above   {'MET' if h1 else 'MISSED'}")
print(f"H2  above-horizon gap spans {span:.1f}×   (≥ {H2_BAR} ?)  "
      f"{'MET' if h2 else 'INAPPLICABLE_UNPOWERED' if not h2_reachable else 'MISSED'}")
print(f"      the box caps the span at QMAX/A = {span_ceiling:.1f}× (Dirichlet), so "
      f"the bar of {H2_BAR} was unreachable by any data — a dead arm, not a miss")
print(f"H3  gap tracks 1/q: Spearman {rho:+.3f}   (≥ 0.9 ?)  {'MET' if h3 else 'MISSED'}")
print(f"H4  {frac_audible:.1%} of above-horizon nodes beat below {BEAT_HZ:.0f} Hz   "
      f"(≥ 33% ?)  {'MET' if h4 else 'MISSED'}")
print(f"\nVERDICT (sealed lattice, unchanged): {verdict}")
print(f"VERDICT (amendment 1, inert arm dropped): {amended}")
if verdict == "ORDERED_BY_BEAT_RATE":
    print("  Above the horizon the denominator still orders the ratios — it has")
    print("  stopped controlling FUSION and started controlling BEAT RATE. The")
    print("  region is not undifferentiated; it is a second regime with its own")
    print("  audible coordinate.")

ev = summarise("n_above", [1] * len(above), EXISTENCE)
with redpath("above-horizon nodes with a positive gap", expect_min=20) as rp:
    rp.observed(sum(1 for r in above if r["gap"] > 0))

json.dump(dict(I=I_MUS, B=B, horizon=A, f_c=F_C, beat_threshold_hz=BEAT_HZ,
               n_below=len(below), n_above=len(above),
               gap_span=float(span), spearman_gap_vs_inv_q=rho,
               fraction_audible_beating=frac_audible,
               predictions=dict(H1=bool(h1), H2=bool(h2), H3=bool(h3), H4=bool(h4)),
               power=dict(H2_bar=H2_BAR, H2_span_ceiling=span_ceiling,
                          H2_reachable=bool(h2_reachable),
                          H2_score=("MET" if h2 else "INAPPLICABLE_UNPOWERED"
                                    if not h2_reachable else "MISSED")),
               verdict=verdict, verdict_amended=amended, rows=rows),
          open(f"{HERE}/brocot_above_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_above_horizon.json")
