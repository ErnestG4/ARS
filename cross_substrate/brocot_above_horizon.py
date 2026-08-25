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
    """min over nonzero |a| <= A of |a1 + a2*alpha|, exact."""
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            v = abs(a1 * q + a2 * p)
            if v and (best is None or v < best):
                best = v
                if best == 1:
                    return Fraction(1, q)
    return Fraction(best, q) if best is not None else None


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
h2 = span >= 10
rho = float(stats.spearmanr([r["gap"] for r in above],
                            [1.0 / r["q"] for r in above])[0])
h3 = rho >= 0.9
beats = np.array([r["beat_hz"] for r in above])
frac_audible = float((beats < BEAT_HZ).mean())
h4 = frac_audible >= 1 / 3

verdict = ("ORDERED_BY_BEAT_RATE" if (h1 and h2 and h3 and h4) else
           "DIFFERENTIATED_BUT_NOT_AS_BEATING" if (h1 and h2 and h3) else
           "NOT_DIFFERENTIATED")

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
print(f"H2  above-horizon gap spans {span:.1f}×   (≥ 10 ?)  {'MET' if h2 else 'MISSED'}")
print(f"H3  gap tracks 1/q: Spearman {rho:+.3f}   (≥ 0.9 ?)  {'MET' if h3 else 'MISSED'}")
print(f"H4  {frac_audible:.1%} of above-horizon nodes beat below {BEAT_HZ:.0f} Hz   "
      f"(≥ 33% ?)  {'MET' if h4 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
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
               verdict=verdict, rows=rows),
          open(f"{HERE}/brocot_above_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_above_horizon.json")
