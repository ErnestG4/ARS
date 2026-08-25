"""JUMP DISPLAY v3: mark PARENT CHANGES. The category boundary, in closed form.

COMMITTED GENERATOR of cross_substrate/brocot_jump_display_v3.json.
Predictions sealed here, before any output exists.

WHY v3
------
v1 marked coincidence events: 55% coverage, 1.97x contrast, FALSIFIED.
v2 marked partial-count changes: 37.7% held-out coverage, 1.14x contrast,
NOT_VALIDATED. Both marker sets were about WHERE PARTIALS MERGE.

`brocot_above_horizon_parent.json` says the region is organised differently.
Every ratio above the horizon is heard as a DETUNING OF A PARENT — the in-box
rational |a1|/|a2| minimising |a1 + a2*alpha| — at 100% of nodes, and that
parent is a Stern-Brocot ancestor at 100%. The parent is the perceptual
CATEGORY. So the structural event on a morph path is not a merge; it is the
moment the category changes, when the ratio stops being heard as a detuned 4/3
and starts being heard as a detuned 5/4.

THE MARKER SET IS ANALYTIC, WHICH IS WHY THIS IS NOT A REDESCRIPTION
---------------------------------------------------------------------
v2 recorded the standing risk: a marker set built by DETECTING changes on a
grid scores well by construction and tells a player nothing. This set never
touches the audio measurement. The parent is an argmin over the box, so it can
only change where two box vectors tie:

    |a1 + a2*alpha| = |b1 + b2*alpha|   ->   alpha = -(a1 +/- b1)/(a2 +/- b2)

Every tie point is therefore a rational with numerator and denominator bounded
by 2A = 16 — a Stern-Brocot set, enumerable exactly, with no grid in it. Those
are CANDIDATES; the boundaries kept are the ones where the exact parent,
evaluated at the rational midpoints between consecutive candidates, actually
differs. Closed form throughout.

Note what that predicts: the marker set is NOT the horizon set. The horizon is
max(p,q) <= A = 8; the category boundaries reach to 2A = 16. If the jumps sit
on the second set and not the first, the display needs the parent, not the
theorem's own node list — and v1's falsification gets a mechanism.

BARS CARRY THEIR REACHABLE RANGES (`reachable.Bar`), and the contrast ceiling
is the ORACLE: the contrast a marker set achieves when placed exactly on the
largest jumps. Comparing to the ideal rather than to the best observed is the
one-sided-calibration lesson, applied at the measurement arm.

VERDICT VIA `verdictlattice.compose`, with roles declared: whether the jumps
are explained is an EXISTENCE question, whether the PARENT is what explains
them is a MECHANISM question, and marker economy is RESOLUTION. A mechanism or
resolution miss cannot negate the existence result -- which this arc has now
got wrong three times by hand.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ J1  COVERAGE — at least 80% of large jumps (|du| >= ABS_JUMP) on the fine    ║
║     grid fall within DELTA_STEPS of a parent-change marker.                  ║
║ J2  CONTRAST — median |du| near a marker is at least 3x the median away.     ║
║ J3  IT IS THE PARENT DOING THE WORK — parent-change coverage is at least     ║
║     1.5x the coverage of v1's horizon-node marker set on the SAME grid with  ║
║     the SAME rule. This is the arm that says the new object earns its keep;  ║
║     without it a bigger marker set could win J1 by covering everything.      ║
║ J4  MARKER ECONOMY — the parent set is at most 3x as dense as the horizon-   ║
║     node set. Coverage bought by carpet-bombing is not a display.            ║
║                                                                              ║
║ J3 AND J4 ARE A PAIR AND MUST BE READ TOGETHER. J3 alone can be won by       ║
║ marking more; J4 alone can be won by marking less. If J3 passes and J4 fails ║
║ the honest reading is "the parent boundaries contain the jumps but the set   ║
║ is too dense to display", which is a real result and a worse feature.        ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — AFTER OUTPUT, 2026-08-24. The sealed bars stand; what follows is
the mechanism behind the miss, and it is analytic rather than statistical.

COVERAGE WAS 0.0%, AND THAT IS A THEOREM, NOT AN ACCIDENT. A below-horizon node
is its own parent with gap exactly 0, so a whole neighbourhood of it takes that
node as its parent; the argmin can only switch strictly BETWEEN two nodes, and
the kept markers duly land on their mediants (8/9 between 7/8 and 1, 9/8
between 1 and 8/7, 9/7 between 5/4 and 4/3). The measured jumps sit on the
nodes themselves — the eight largest are 1.5 grid steps from a node marker and
89 to 140 steps from any parent boundary.

So the two objects are DISJOINT BY CONSTRUCTION: the perceptual category
boundary is the point farthest from either category's spectral event. The
premise of v3 — "the structural event is the moment the category changes" — is
false, and false for a reason worth keeping: a category change is not a
spectral change. Nothing merges at a mediant. The parent switches while the
partial set moves continuously.

THIS IS A DESIGN RESULT, NOT ONLY A NEGATIVE. It says the map needs two layers
and that they cannot collide:

    REGION  parent identity — a categorical field, piecewise constant, whose
            boundaries are mediants of node pairs. 13 regions across [0.7, 1.4].
    EVENT   spectral discontinuity — at and beside the nodes, where partials
            merge or cross the amplitude floor. v1/v2's marker set.

A display that draws the region fill and the event ticks together has no
contention for the same pixel, because the events sit at region CENTRES and the
boundaries sit where nothing happens. That is a better property than the one
this cell set out to demonstrate.

STILL UNEXPLAINED, AND UNCHANGED FROM v2: the node set covers only 30.4% of
large jumps. The remaining ~70% are amplitude-threshold crossings, which no
Farey-enumerable set will ever mark. That was v2's finding and v3 does not
improve on it.
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
from reachable import Bar                                         # noqa: E402
from existence import summarise, EXISTENCE                        # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
A0, A1 = 0.70, 1.40
FINE = 3501
DELTA_STEPS = 3                  # inherited from v2, unchanged: grid-relative
ABS_JUMP = 0.05                  # inherited from v2, unchanged: absolute


def parent_of(alpha):
    """The in-box rational |a1|/|a2| minimising |a1 + a2*alpha|. Exact."""
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            key = (abs(a1 * q + a2 * p), max(abs(a1), abs(a2)), -a2)
            if best is None or key < best[0]:
                best = (key, a1, a2)
    _, a1, a2 = best
    return Fraction(abs(a1), abs(a2)) if a2 else None


# ── candidate ties: rationals with |num|,|den| <= 2A, in range. No grid. ─────
cands = sorted({Fraction(n, d) for n in range(1, 2 * A + 1)
                for d in range(1, 2 * A + 1)
                if A0 <= Fraction(n, d) <= A1})
edges = [Fraction(A0).limit_denominator(10**6)] + cands + \
        [Fraction(A1).limit_denominator(10**6)]
mids = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
pars = [parent_of(m) for m in mids]
markers = [dict(value=float(cands[i - 1]), ratio=str(cands[i - 1]),
                left=str(pars[i - 1]), right=str(pars[i]))
           for i in range(1, len(mids)) if pars[i] != pars[i - 1]]
pos = np.array([m["value"] for m in markers])

# v1's horizon-node marker set, on the same rule: the below-horizon rationals
node_pos = np.array(sorted(float(f) for f in
                           {Fraction(n, d) for n in range(1, A + 1)
                            for d in range(1, A + 1)}
                           if A0 <= f <= A1))


def probe(a):
    sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=220.0)
    n = sp.freqs.size
    u = (I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
         if n >= 20 else None)
    return n, (np.nan if u is None else float(u))


g = np.linspace(A0, A1, FINE)
U = np.array([probe(a)[1] for a in g], float)
mid = (g[:-1] + g[1:]) / 2
jump = np.abs(np.diff(U))
ok = np.isfinite(jump)
d = (A1 - A0) / (FINE - 1)
win = DELTA_STEPS * d

near = np.array([np.any(np.abs(x - pos) <= win) for x in mid])
near_node = np.array([np.any(np.abs(x - node_pos) <= win) for x in mid])
big = ok & (jump >= ABS_JUMP)

cov = float(near[big].mean())
cov_node = float(near_node[big].mean())
m_near = float(np.median(jump[ok & near])) if (ok & near).any() else 0.0
m_far = float(np.median(jump[ok & ~near])) if (ok & ~near).any() else 0.0
contrast = (m_near / m_far) if m_far > 0 else float("inf")
dens_ratio = len(pos) / len(node_pos)

# ── ceilings. Computed from the DESIGN and from the ORACLE, not from the
# ── marker set under test. The oracle is a marker set sitting exactly on the
# ── large jumps: the best contrast any marker set could achieve here.
orc = big.copy()
o_near = float(np.median(jump[ok & orc])) if (ok & orc).any() else 0.0
o_far = float(np.median(jump[ok & ~orc])) if (ok & ~orc).any() else 0.0
contrast_ceiling = (o_near / o_far) if o_far > 0 else float("inf")
cov_ceiling = 1.0 / cov_node if cov_node > 0 else float("inf")
dens_floor = 1.0 / len(node_pos)

J1 = Bar("coverage of large jumps", 0.80, floor=0.0, ceiling=1.0,
         why="a fraction of the large-jump steps: 0 to 1 by construction")
J2 = Bar("contrast near vs away", 3.0, floor=0.0, ceiling=contrast_ceiling,
         why="the ORACLE marker set — markers placed exactly on the large "
             "jumps — is the best contrast any marker set can reach on this "
             "series; compare to the ideal, not to the best observed")
J3 = Bar("parent coverage / node coverage", 1.5, floor=0.0, ceiling=cov_ceiling,
         why="coverage cannot exceed 1, so the ratio cannot exceed 1/cov_node")
J4 = Bar("marker density vs node set", 3.0, direction="le",
         floor=dens_floor, ceiling=float(len(cands)) / len(node_pos),
         why="at least one marker; at most every candidate tie point, which is "
             "the full |num|,|den| <= 2A set in range")

s1, s2, s3, s4 = (J1.score(cov), J2.score(contrast),
                  J3.score(cov / cov_node if cov_node else float("inf")),
                  J4.score(dens_ratio))

print(f"I = {I_MUS}, B = {B}, A = 2B = {A}, alpha in [{A0}, {A1}], grid {FINE}")
print(f"candidate tie points (|num|,|den| <= {2 * A}): {len(cands)}")
print(f"PARENT-CHANGE markers kept: {len(pos)}   "
      f"horizon-node markers: {len(node_pos)}\n")
print(f"{'alpha':>8s}  {'ratio':>7s}   parent change")
for m in markers[:12]:
    print(f"{m['value']:>8.4f}  {m['ratio']:>7s}   {m['left']} -> {m['right']}")
if len(markers) > 12:
    print(f"{'':>8s}  ... and {len(markers) - 12} more")

print(f"\nlarge jumps on the fine grid: {int(big.sum())}  "
      f"(|du| >= {ABS_JUMP}, window {DELTA_STEPS} steps = {win:.5f})")
print(f"median |du| near a parent marker {m_near:.4f}, away {m_far:.4f}")
print()
for b, v, f in ((J1, cov, "{:.1%}"), (J2, contrast, "{:.2f}"),
                (J3, s3["value"], "{:.2f}"), (J4, dens_ratio, "{:.2f}")):
    print("  " + b.line(v, f))
print(f"      v1's horizon-node set covers {cov_node:.1%} on the same grid, "
      f"same rule")

v = compose([Arm.from_bar(s1, EX_ROLE), Arm.from_bar(s2, EX_ROLE),
             Arm.from_bar(s3, MECH_ROLE, note="vs the horizon-node marker set"),
             Arm.from_bar(s4, RES_ROLE, note="marker economy")],
            holds="JUMPS_ARE_PARENT_CHANGES", fails="JUMPS_NOT_EXPLAINED")
print(f"\nVERDICT: {v['head']}")
if v["qualifiers"]:
    print(f"   qualified by: {', '.join(v['qualifiers'])}")
if v["dropped"]:
    print(f"   inert arms dropped: {v['dropped']}")

ex = summarise("n_markers", [1] * len(pos), EXISTENCE)
with redpath("parent-change markers in range", expect_min=5) as rp:
    rp.observed(len(pos))

json.dump(dict(I=I_MUS, B=B, A=A, a0=A0, a1=A1, grid=FINE,
               delta_steps=DELTA_STEPS, abs_jump=ABS_JUMP,
               n_candidates=len(cands), n_markers=len(pos),
               n_node_markers=int(len(node_pos)), n_large_jumps=int(big.sum()),
               coverage=cov, coverage_node_set=cov_node, contrast=contrast,
               median_near=m_near, median_far=m_far,
               contrast_oracle_ceiling=contrast_ceiling,
               density_ratio=dens_ratio,
               bars={s["name"]: s for s in (s1, s2, s3, s4)},
               verdict=v["head"], composed=v, markers=markers),
          open(f"{HERE}/brocot_jump_display_v3.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_jump_display_v3.json")
