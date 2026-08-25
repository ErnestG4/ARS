"""IS THE HORIZON AUDIBLE? Putting the floor on the product, not on one factor.

COMMITTED GENERATOR of cross_substrate/brocot_audible_horizon.json.
Predictions sealed here, before any output exists.

THE CHALLENGE, FROM AN INDEPENDENT REVIEW
-------------------------------------------
`order_bound(I)` is defined by an amplitude floor eps = 1e-3 on a SINGLE Bessel
factor |J_n(I)|. COINCIDENCE-HORIZON section 3 already concedes the weakness --
"a partial's amplitude is a PRODUCT of Bessel terms, so a single surviving J_n
does not make an audible partial" -- and then leaves the floor on the factor
anyway.

The consequence is not small, and it reproduces exactly on independent
computation: a coincidence witness sits at the CORNER of the box, where both
factors are near-floor. At the eps horizon the witness partials measure
**-78 to -92 dB** below the strongest partial in the spectrum, across
I = 0.9 to 3.0. Classification is being done by partials no listener could hear
in a dense spectrum.

WHAT REPRODUCED AND WHAT DID NOT. The review's witness levels reproduced to the
decibel. Its headline -- that a psychoacoustic floor roughly HALVES the horizon
-- did not: a first independent pass gave 8 -> 5 at -40 dB but 8 -> 8 at -60 dB
for I = 0.9. So the direction is confirmed and the magnitude is floor-dependent,
which is exactly the disagreement worth sealing a cell over rather than adopting
either number.

THE RIGHT QUANTITY IS PER-RATIO, NOT A SINGLE HORIZON. "The audible horizon is
M" presumes every ratio at max(p,q) = M behaves alike. It does not: the witness
amplitude depends on how p and q split into Bessel orders, so two ratios with
the same max can differ by tens of dB. This cell therefore measures AUDIBILITY
PER RATIO and reports the horizon as a distribution, not a number.

DEFINITION. For alpha = p/q below the eps horizon, the minimal witness is
(ceil(p/2), -floor(q/2)) and (-floor(p/2), ceil(q/2)); the coincidence is
audible at floor X dB when BOTH witness partials exceed the strongest lattice
partial minus X. Both, because a coincidence is two partials landing together --
one audible partial arriving at a frequency where nothing else is does not fuse
with anything.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ E1  THE eps HORIZON OVERSTATES AUDIBILITY — at I = 0.9 and a -60 dB floor,   ║
║     fewer than 100% of below-horizon ratios have an audible coincidence.     ║
║     A weak arm on purpose: if even this fails, eps is fine and the review's  ║
║     concern is void.                                                         ║
║ E2  MATERIALLY, AT A CONSERVATIVE FLOOR — at -40 dB, fewer than 50% of       ║
║     below-horizon ratios are audible at I = 0.9.                             ║
║ E3  THE SHIPPED FIELD SHRINKS — re-cutting the I = 0.9 map field with the    ║
║     -40 dB audible criterion leaves fewer than 13 regions.                   ║
║ E4  THE PRODUCT FLOOR IS FLOOR-ROBUST — the review's claim that a product    ║
║     floor is far less convention-sensitive than eps. Operationalised: the    ║
║     count of audible ratios at I = 0.9 changes by at most 25% between -40    ║
║     and -60 dB. MY OWN FIRST PASS SUGGESTS THIS FAILS; it is sealed anyway   ║
║     because a claim worth adopting is worth testing, and a review's headline ║
║     is a hypothesis like any other.                                          ║
║                                                                              ║
║ E3 IS THE ONE THAT COSTS SOMETHING. If the field shrinks, MAP-FIELD.md's     ║
║ thirteen regions are a structural count, not an audible one, and the         ║
║ document owes a second table rather than a correction — both are true, they  ║
║ answer different questions, and only one of them is what a player hears.     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_LIST = [0.9, 1.5, 2.0, 3.0]
FLOORS = [30.0, 40.0, 50.0, 60.0, 80.0]
LO, HI = Fraction(7, 10), Fraction(7, 5)
PRIMARY_I, PRIMARY_FLOOR = 0.9, 40.0


def strongest(I, B):
    return max(abs(jv(n1, I) * jv(n2, I))
               for n1 in range(-B, B + 1) for n2 in range(-B, B + 1))


def witness_level(p, q, I, B, ref):
    """min(|J*J|) over the two witness partials, in dB re the strongest."""
    n1, n1p = -(-p // 2), -(p // 2)
    n2, n2p = -(q // 2), -(-q // 2)
    if max(abs(n1), abs(n1p)) > B or max(abs(n2), abs(n2p)) > B:
        return None
    a = min(abs(jv(n1, I) * jv(n2, I)), abs(jv(n1p, I) * jv(n2p, I)))
    return -np.inf if a <= 0 else float(20 * np.log10(a / ref))


per_I = {}
for I in I_LIST:
    B = order_bound(I)
    A = 2 * B
    ref = strongest(I, B)
    ratios = [Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
              if gcd(p, q) == 1 and LO <= Fraction(p, q) <= HI
              and max(p, q) <= A]
    rows = []
    for f in sorted(set(ratios), key=float):
        lv = witness_level(f.numerator, f.denominator, I, B, ref)
        if lv is None:
            continue
        rows.append(dict(ratio=str(f), maxpq=max(f.numerator, f.denominator),
                         level_db=lv,
                         audible={str(x): bool(lv > -x) for x in FLOORS}))
    per_I[I] = dict(B=B, A=A, n=len(rows), rows=rows)

p9 = per_I[PRIMARY_I]
n9 = p9["n"]
aud = {x: sum(r["audible"][str(x)] for r in p9["rows"]) for x in FLOORS}
e1 = aud[60.0] / n9
e2 = aud[40.0] / n9
e3 = aud[PRIMARY_FLOOR]                       # regions == audible parents
e4 = abs(aud[40.0] - aud[60.0]) / max(aud[60.0], 1)

E1 = Bar("audible share at -60 dB", 1.0, direction="le", floor=0.0, ceiling=1.0,
         why="a fraction of below-horizon ratios: 0 to 1")
E2 = Bar("audible share at -40 dB", 0.50, direction="le", floor=0.0,
         ceiling=1.0, why="a fraction of below-horizon ratios: 0 to 1")
E3 = Bar("regions surviving at -40 dB", 13, direction="le", floor=0,
         ceiling=n9, why="a region per audible below-horizon ratio; at most all "
                         f"{n9} of them")
E4 = Bar("relative change in count, -40 vs -60 dB", 0.25, direction="le",
         floor=0.0, ceiling=float(n9),
         why="a relative change against the -60 dB count, which is at least 1")
s1, s2, s3, s4 = E1.score(e1), E2.score(e2), E3.score(e3), E4.score(e4)

print("witness level at the eps horizon, re the strongest lattice partial:")
print(f"{'I':>5s} {'B':>3s} {'A':>3s} {'n ratios':>9s} " +
      "".join(f"{'aud@-' + str(int(x)):>10s}" for x in FLOORS))
for I in I_LIST:
    d = per_I[I]
    cells = "".join(f"{sum(r['audible'][str(x)] for r in d['rows']):>10d}"
                    for x in FLOORS)
    print(f"{I:>5.1f} {d['B']:>3d} {d['A']:>3d} {d['n']:>9d}{cells}")

print(f"\nI = {PRIMARY_I}: the {n9} below-horizon ratios, by witness level")
for r in sorted(p9["rows"], key=lambda r: -r["level_db"])[:6]:
    print(f"    {r['ratio']:>6s}  max(p,q) {r['maxpq']:>2d}  "
          f"{r['level_db']:>7.1f} dB")
print("    ...")
for r in sorted(p9["rows"], key=lambda r: -r["level_db"])[-3:]:
    print(f"    {r['ratio']:>6s}  max(p,q) {r['maxpq']:>2d}  "
          f"{r['level_db']:>7.1f} dB")

print()
for b, v, f in ((E1, e1, "{:.1%}"), (E2, e2, "{:.1%}"), (E3, e3, "{:.0f}"),
                (E4, e4, "{:.1%}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="not every structurally-fusing ratio is "
                                "audibly fusing"),
             Arm.from_bar(s3, EX_ROLE,
                          claim="the shipped 13-region field shrinks under an "
                                "audibility floor"),
             Arm.from_bar(s2, RES_ROLE,
                          claim="the reduction is large at a conservative floor"),
             Arm.from_bar(s4, MECH_ROLE,
                          claim="the product floor is floor-robust, as the "
                                "review claimed")],
            holds="EPS_HORIZON_OVERSTATES_AUDIBILITY",
            fails="EPS_HORIZON_IS_AUDIBLY_FAITHFUL")
print(f"\nVERDICT: {v['citation']}")

with redpath("below-horizon ratios levelled", expect_min=40) as rp:
    rp.observed(sum(d["n"] for d in per_I.values()))

json.dump(dict(I_list=I_LIST, floors=FLOORS, lo=str(LO), hi=str(HI),
               primary_I=PRIMARY_I, primary_floor=PRIMARY_FLOOR,
               per_I={str(k): dict(B=d["B"], A=d["A"], n=d["n"],
                                   audible={str(x): sum(r["audible"][str(x)]
                                                        for r in d["rows"])
                                            for x in FLOORS},
                                   rows=d["rows"]) for k, d in per_I.items()},
               bars={s["name"]: s for s in (s1, s2, s3, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_audible_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_audible_horizon.json")
