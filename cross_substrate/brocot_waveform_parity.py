"""DOES EVEN-HARMONIC SUPPRESSION TOUCH THE HORIZON? And what does a stack extend?

COMMITTED GENERATOR of cross_substrate/brocot_waveform_parity.json.
Predictions sealed here, before any output exists.

WHY THIS EXISTS
---------------
Ian Fritz's Double-Pulse Waveform Generator builds a waveform from a positive
pulse and a negative pulse placed half a period apart. That gives half-wave
antisymmetry, f(t + T/2) = -f(t), so the even harmonics of the two pulses cancel
and only odd ones survive -- and his timbre control sweeps CONTINUOUSLY between
a single pulse (all harmonics) and the antisymmetric double pulse (odd only).
brocot has discrete `Wave { Sine, Triangle, Saw, Square, Pulse }` and no such
continuous axis.

Before proposing it as a feature, the question the horizon programme has to ask
is whether it interacts with the theorem at all. `brocot_horizon_extensions`
already measured richer waveforms and banked "the horizon moves 8 -> 11 -- a
real extension, not a dissolution", with triangle, square and saw all giving 17
of 90. That result does not distinguish PARITY from EXTENT, and it reports a
single number for a bound that may not be symmetric.

Exploratory runs before sealing (house practice: scout before pre-registering)
suggested two things this cell tests properly. They are stated so the seal is
honest about not being blind: the scouts indicated that parity does not matter
and that 11 is a range artifact. What is sealed is whether that survives a
controlled test.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed, thresholds strictly inside ranges      ║
║                                                                              ║
║ W1  PARITY IS IRRELEVANT — stacks matched on sum-of-harmonics but differing   ║
║     in parity content ring on IDENTICAL ratio sets: the symmetric difference  ║
║     is 0 across every matched pair. If it misses, even-suppression is a       ║
║     horizon-relevant control and the theorem's scope must name parity.       ║
║ W2  THE EXTENSION IS ASYMMETRIC — a stack on the modulator leaves the maximum ║
║     ringing NUMERATOR at the sine value 2B = 8 while the maximum DENOMINATOR  ║
║     grows. Measured as: max numerator equals 8 for every stack tested.       ║
║ W3  "8 -> 11" IS A RANGE ARTIFACT — widening the ratio range downward raises  ║
║     the maximum ringing denominator to at least 24, while the maximum        ║
║     numerator stays at 8. If W3 holds, the banked figure describes brocot's   ║
║     window and not the waveform, and the paper owes a correction.            ║
║                                                                              ║
║ W1 IS THE ONE THE FEATURE QUESTION TURNS ON. If parity is irrelevant, a       ║
║ continuous even-suppression control is ORTHOGONAL to the horizon -- worth     ║
║ having for timbre, and provably not disturbing anything the theorem says.     ║
║ Orthogonality is a result, not an absence of one.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from ratiopinned import pinned, assert_no_pinned_at_irrational    # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
BOUND = 2 * B
LO, HI = 0.70, 1.40
WIDE_LO = 0.20
QMAX, PMAX = 40, 40

# matched on sum-of-harmonics, differing only in parity content
MATCHED = [
    ("odd  [1,3,5]", [1, 3, 5]),
    ("mix  [1,2,6]", [1, 2, 6]),
    ("mix  [1,4,4]", [1, 4, 4]),
]
REAL = [("sine", [1]), ("triangle", [1, 3, 5]), ("square", [1, 3, 5, 7]),
        ("saw", [1, 2, 3, 4])]


def spec(hs):
    return [(1, 0)] + [(0, h) for h in hs]


def nodes(lo, hi):
    return sorted({Fraction(p, q) for q in range(1, QMAX + 1)
                   for p in range(1, PMAX + 1)
                   if gcd(p, q) == 1 and lo <= p / q <= hi}, key=float)


def ringing(hs, ns):
    return {a for a in ns if pinned(spec(hs), BOUND, a)}


NARROW = nodes(LO, HI)
WIDE = nodes(WIDE_LO, HI)

# the module's own red path, run here so a leak cannot masquerade as a finding
for _, hs in REAL + MATCHED:
    assert_no_pinned_at_irrational(spec(hs), BOUND)

matched_sets = {name: ringing(hs, NARROW) for name, hs in MATCHED}
pairs, symdiff = [], 0
names = [n for n, _ in MATCHED]
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        d = matched_sets[names[i]] ^ matched_sets[names[j]]
        pairs.append((names[i], names[j], len(d)))
        symdiff += len(d)

real_sets = {name: ringing(hs, NARROW) for name, hs in REAL}
max_num = {n: max((a.numerator for a in s), default=0)
           for n, s in real_sets.items()}
max_den = {n: max((a.denominator for a in s), default=0)
           for n, s in real_sets.items()}
w2 = max(max_num.values())

wide_tri = ringing([1, 3, 5], WIDE)
wide_sine = ringing([1], WIDE)
w3_den = max(a.denominator for a in wide_tri)
w3_num = max(a.numerator for a in wide_tri)

W1 = Bar("symmetric difference over matched-parity pairs", 0, direction="le",
         floor=0, ceiling=len(NARROW),
         why=f"a symmetric difference of subsets of {len(NARROW)} nodes; "
             f"0 to {len(NARROW)}")
W2 = Bar("max ringing numerator over all waves", BOUND, direction="le",
         floor=1, ceiling=PMAX,
         why=f"a numerator in the enumerated set, 1 to {PMAX}")
W3 = Bar("max ringing denominator, range widened down", 24, floor=1,
         ceiling=QMAX, why=f"a denominator in the enumerated set, 1 to {QMAX}")
s1, s2, s3 = W1.score(symdiff), W2.score(w2), W3.score(w3_den)

print(f"I = {I_MUS}, B = {B}, box bound 2B = {BOUND}, "
      f"{len(NARROW)} nodes in [{LO}, {HI}]\n")
print("W1 — stacks MATCHED on sum-of-harmonics, differing in parity:")
for name, hs in MATCHED:
    print(f"    {name:>13s}  sum {sum(hs):>2d}   rings {len(matched_sets[name]):>2d}")
for a, b, d in pairs:
    print(f"    {a} vs {b}: symmetric difference {d}")

print(f"\nW2 — the real waves, in brocot's own range:")
print(f"{'wave':>9s} {'harmonics':>14s} {'rings':>6s} {'max num':>8s} {'max den':>8s}")
for name, hs in REAL:
    print(f"{name:>9s} {str(hs):>14s} {len(real_sets[name]):>6d} "
          f"{max_num[name]:>8d} {max_den[name]:>8d}")
extra = sorted(real_sets["triangle"] - real_sets["sine"], key=float)
print(f"    triangle adds exactly: {[str(x) for x in extra]}")

print(f"\nW3 — range widened to [{WIDE_LO}, {HI}] ({len(WIDE)} nodes):")
print(f"    sine     max den {max(a.denominator for a in wide_sine):>3d}   "
      f"max num {max(a.numerator for a in wide_sine):>3d}")
print(f"    triangle max den {w3_den:>3d}   max num {w3_num:>3d}")

print()
for b, v, f in ((W1, symdiff, "{:.0f}"), (W2, w2, "{:.0f}"), (W3, w3_den, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="parity-matched stacks ring on identical sets, "
                                "so even-suppression is horizon-orthogonal"),
             Arm.from_bar(s2, MECH_ROLE,
                          claim="the numerator bound is unchanged: a modulator "
                                "stack extends its own side only"),
             Arm.from_bar(s3, RES_ROLE,
                          claim="the banked 8->11 figure is bound by brocot's "
                                "ratio window, not by the waveform")],
            holds="PARITY_IS_HORIZON_ORTHOGONAL",
            fails="PARITY_TOUCHES_THE_HORIZON")
print(f"\nVERDICT: {v['citation']}")

with redpath("ratios tested for ringing", expect_min=200) as rp:
    rp.observed(len(NARROW) * len(REAL) + len(WIDE) * 2)

json.dump(dict(I=I_MUS, B=B, bound=BOUND, lo=LO, hi=HI, wide_lo=WIDE_LO,
               n_narrow=len(NARROW), n_wide=len(WIDE),
               matched={n: sorted(str(a) for a in s) for n, s in matched_sets.items()},
               matched_pairs=[dict(a=a, b=b, symdiff=d) for a, b, d in pairs],
               real={n: dict(harmonics=hs, n_ringing=len(real_sets[n]),
                             max_numerator=max_num[n], max_denominator=max_den[n])
                     for n, hs in REAL},
               triangle_adds=[str(x) for x in extra],
               wide=dict(triangle_max_den=w3_den, triangle_max_num=w3_num,
                         sine_max_den=max(a.denominator for a in wide_sine)),
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_waveform_parity.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_waveform_parity.json")
