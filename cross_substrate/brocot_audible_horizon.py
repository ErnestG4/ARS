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

AMENDMENT 1 — RETRACTING A "LADDER" I ASSERTED ONE COMMIT EARLIER.

Reading the printed top rows at I = 0.9 (-6.0, -37.3, -53.6, -69.9, -88.8,
-107.7 dB) I described the witness levels as "a near-exact ladder, roughly
16-19 dB per rung", and wrote into a commit message that the audible horizon is
therefore set by the dynamic-range budget at about one rung per 17 dB, calling
that "more robust than any particular count and the durable finding here".

Computing the full per-rung series rather than the sorted head:

    I = 0.9   10.4, 16.3, 16.3,  2.6, 35.2                      mean 16.2
    I = 1.5    4.8, 11.6, 11.6,  2.7, 25.9,  2.0, 14.3          mean 10.4
    I = 2.0    0.1,  8.7,  8.7,  2.8, 20.3,  2.1, 11.6, ...     mean 11.0
    I = 3.0   -1.8,  0.8,  3.9,  3.5, 11.3,  2.4,  7.4, ...     mean  6.7

The scatter runs from -1.8 to +35.2 dB and the mean FALLS with the index. There
is no 17 dB law. The step size depends on how p and q split into Bessel orders,
which turns on their parity, so adjacent rungs can be nearly free or cost 35 dB.

The retraction matters more than the claim did: I read a regular series off six
sorted rows, which is the shape of every argmax-without-an-error-bar mistake in
this repo, and asserted it was the durable finding while the arms that were
actually sealed sat right beside it. E1-E4 are what this cell measured. The
ladder was a decoration I added on the way out.

WHAT SURVIVES: the counts, which were sealed and scored. At I = 0.9, thirteen
structurally-fusing ratios are three audible ones at -40 dB and five at -60 dB.
And E4, which failed, says the count is floor-sensitive -- so even those numbers
travel with their floor attached.

AMENDMENT 2 — E1 WAS INERT, and `reachable.Bar` now refuses it.

E1 was "audible share at -60 dB <= 1.0". A share is bounded by 1 by
construction, so every possible value meets it: the arm could not MISS, and the
MET it reported was non-evidence. I sealed it describing it as "a weak arm on
purpose", which is a description of a weak arm, not of a dead one.

`reachable.Bar` refused only bars that could not be MET until adversarial review
pointed out the mirror. It now refuses both, and refused this one on the next
run -- an inert arm from this same session, caught by the guard hardened hours
later.

E1 is therefore NOT SCORED. It is reported as INERT_BY_CONSTRUCTION and dropped
from the verdict, per the rule that a dead arm never sits in a tally.

AMENDMENT 3 — AND SO WAS E3, WHICH I CALLED "THE ONE THAT COSTS SOMETHING".

"regions surviving at -40 dB <= 13" was sealed against a ceiling of 13 (there
are 13 below-horizon ratios, so at most 13 can survive). Every possible value
meets it. Off by one: a bar of 12 would have been the real claim -- "strictly
fewer than thirteen" -- and would have been met at 3. That is a counterfactual
and is stated as one, not scored.

So BOTH arms I designated EXISTENCE were dead, and the cell as sealed could not
have failed to find what it found. The measurement is unaffected -- 3 of 13
audible at -40 dB is a computation, not a test -- but the SEAL certified
nothing, and that distinction is the whole point of sealing.

E2 IS RE-ROLED TO EXISTENCE, recorded here rather than done quietly. Its claim,
"fewer than half of structurally-fusing ratios are audibly fusing", is the
existence proposition the head names; it has a real bar (0.50 against a [0,1]
range) and it discriminates. E4 stays MECHANISM. The head is therefore carried
by the one arm that was alive, which is less than the seal promised and is what
there is.

WHAT THE THREE DEAD ARMS HAVE IN COMMON: each set a bound at the edge of its own
declared range. That is what an inert bar looks like from the inside, and it is
why `reachable.Bar` now refuses both edges instead of one.
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

# E1 IS NOT CONSTRUCTED. "share <= 1.0" against a ceiling of 1.0 cannot miss;
# reachable.Bar refuses it, correctly. See amendment 2. The value is still
# computed and printed, as an observation rather than as a scored arm.
E2 = Bar("audible share at -40 dB", 0.50, direction="le", floor=0.0,
         ceiling=1.0, why="a fraction of below-horizon ratios: 0 to 1")
# E3 IS NOT CONSTRUCTED EITHER — "<= 13" against a ceiling of 13. See
# amendment 3. The count is computed and printed as an observation.
E4 = Bar("relative change in count, -40 vs -60 dB", 0.25, direction="le",
         floor=0.0, ceiling=float(n9),
         why="a relative change against the -60 dB count, which is at least 1")
s2, s4 = E2.score(e2), E4.score(e4)

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
print(f"  audible share at -60 dB: {e1:.1%}   INERT_BY_CONSTRUCTION "
      f"(bar 1.0 == ceiling 1.0; not scored — amendment 2)")
print(f"  regions surviving at -40 dB: {e3:.0f} of {n9}   INERT_BY_CONSTRUCTION "
      f"(bar {n9} == ceiling {n9}; not scored — amendment 3)")
for b, v, f in ((E2, e2, "{:.1%}"), (E4, e4, "{:.1%}")):
    print("  " + b.line(v, f))

v = compose([Arm("audible share at -60 dB", EX_ROLE, met=False, inert=True,
                 note="bar 1.0 == ceiling 1.0; cannot miss",
                 claim="not every structurally-fusing ratio is audibly fusing"),
             Arm("regions surviving at -40 dB", EX_ROLE, met=False, inert=True,
                 note=f"bar {n9} == ceiling {n9}; cannot miss",
                 claim="the shipped 13-region field shrinks"),
             Arm.from_bar(s2, EX_ROLE,
                          claim="fewer than half of structurally-fusing ratios "
                                "are audibly fusing"),
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
               e1_inert=dict(value=e1, reason="bar 1.0 == ceiling 1.0; "
                             "cannot miss; not scored"),
               inert_arms=dict(E1=dict(value=e1, reason="bar 1.0 == ceiling 1.0"),
                               E3=dict(value=e3, reason=f"bar {n9} == ceiling {n9}")),
               regions_surviving_at_40db=e3, n_below_horizon=n9,
               bars={s["name"]: s for s in (s2, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_audible_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_audible_horizon.json")
