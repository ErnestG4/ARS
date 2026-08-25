"""HEARD AS: above the horizon, every ratio is a detuning of a below-horizon one.

COMMITTED GENERATOR of cross_substrate/brocot_above_horizon_parent.json.
Predictions sealed here, before any output exists. Every bar carries its own
reachable range via `reachable.Bar` — the seal will not run if an arm is inert.

WHERE THIS COMES FROM
---------------------
`brocot_above_horizon.json` established that above the horizon every ratio has a
strictly positive minimum gap and 79.2% of them beat below 20 Hz. It also
FALSIFIED the premise that the gap tracks 1/q (Spearman +0.277; the Bezout
argument ignored the box), and the falsification names the right object: the
minimum of |a1 + a2*alpha| over |a| <= A is a BEST RATIONAL APPROXIMATION with
bounded denominator, not a function of q.

That reframes the question Will asked. The minimising pair (a1, a2) is not just
a number — it points at a specific rational, parent = |a1|/|a2|, and

    alpha = parent + (a signed detuning of size gap/|a2|)

So the claim under test is a CATEGORISATION, which is what was asked for: above
the horizon a ratio is not undifferentiated, it is heard as its nearest in-box
rational plus a beat. The parent is the category; the gap is the coordinate
within it.

WHY THIS IS THE BROCOT TREE'S OWN QUESTION
-------------------------------------------
Best approximation with bounded denominator is exactly Stern-Brocot descent:
the ancestors of alpha in the tree ARE its convergents and semiconvergents. If
P2 holds, the synth's existing tree structure already computes the perceptual
category, and the map does not need a new coordinate — it needs to stop at the
horizon depth and read the node it stopped on.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ P1  The parent is itself BELOW the horizon (max(p',q') <= A) for at least     ║
║     90% of above-horizon nodes. If this fails the categorisation is empty:    ║
║     ratios would be heard as other ratios that are themselves inaudible as    ║
║     fusion, and nothing has been reduced.                                     ║
║ P2  The parent is a STERN-BROCOT ANCESTOR of alpha for at least 70% of        ║
║     nodes — the tree the synth already walks computes the category.           ║
║ P3  The partition is non-degenerate: at least 8 distinct parents are used,    ║
║     AND no single parent absorbs more than 40% of the nodes. A categorisation ║
║     that puts nearly everything in one box has differentiated nothing; this   ║
║     is the arm that can kill the finding while P1 and P2 both pass.           ║
║ P4  (parent, beat rate to 0.1 Hz) identifies the ratio for at least 90% of    ║
║     nodes — the two coordinates together are a near-complete label, not a     ║
║     lossy summary. 0.1 Hz is declared here as the readout resolution: a       ║
║     ten-second difference in beat period, before any data is seen.            ║
║                                                                              ║
║ P3 IS THE ONE THAT DECIDES WHETHER THIS SHIPS TO THE MAP. P1 and P2 can both  ║
║ pass while every ratio in the region collapses onto 1/1, which would be a     ║
║ true statement and a useless display. If P3 misses, the honest answer is      ║
║ "categorised, but the categories are lopsided", and the map gets the gap      ║
║ coordinate without the parent labels.                                        ║
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
from existence import summarise, EXISTENCE, CENTRAL_TENDENCY      # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
F_C = 220.0
HZ_RES = 0.1                    # declared readout resolution for P4
LO, HI, QMAX = 0.70, 1.40, 40

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 60)
                if LO <= p / q <= HI and gcd(p, q) == 1}, key=float)
BELOW = [f for f in NODES if max(f.numerator, f.denominator) <= A]
ABOVE = [f for f in NODES if max(f.numerator, f.denominator) > A]

# ---- bars, with their reachable ranges. An inert arm cannot get past here. ----
P1 = Bar("parent is below the horizon", 0.90, floor=0.0, ceiling=1.0,
         why="a fraction over the above-horizon nodes: 0 to 1 by construction")
P2 = Bar("parent is a Stern-Brocot ancestor", 0.70, floor=0.0, ceiling=1.0,
         why="a fraction over the above-horizon nodes: 0 to 1 by construction")
P3A = Bar("distinct parents used", 8, floor=1, ceiling=len(BELOW),
          why=f"a parent must be an in-box rational in [{LO},{HI}]; there are "
              f"{len(BELOW)} of them, and at least one is used")
P3B = Bar("largest parent class share", 0.40, direction="le",
          floor=1.0 / max(len(BELOW), 1), ceiling=1.0,
          why=f"with {len(BELOW)} available parents the most even possible "
              f"partition still gives the largest class 1/{len(BELOW)}")
P4 = Bar("(parent, beat) is injective", 0.90, floor=0.0, ceiling=1.0,
         why="a fraction over the above-horizon nodes: 0 to 1 by construction")


def minimiser(alpha):
    """(gap, a1, a2) at the minimum of |a1 + a2*alpha| over 0 < |a| <= A.

    Ties are broken toward the smallest max(|a1|,|a2|) — the shallowest tree
    node — and then toward a2 > 0, so the parent is well defined."""
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            v = abs(a1 * q + a2 * p)
            key = (v, max(abs(a1), abs(a2)), -a2)
            if best is None or key < best[0]:
                best = (key, Fraction(v, q), a1, a2)
    return best[1], best[2], best[3]


def brocot_ancestors(target):
    """Every node on the Stern-Brocot descent to `target`, target excluded."""
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    seen = []
    for _ in range(4000):
        mn, md = lo_n + hi_n, lo_d + hi_d
        med = Fraction(mn, md)
        if med == target:
            return seen
        seen.append(med)
        if target < med:
            hi_n, hi_d = mn, md
        else:
            lo_n, lo_d = mn, md
    return seen


rows = []
for f in ABOVE:
    g, a1, a2 = minimiser(f)
    par = Fraction(abs(a1), abs(a2)) if a2 else None
    anc = brocot_ancestors(f)
    rows.append(dict(
        ratio=str(f), value=float(f), q=f.denominator,
        maxpq=max(f.numerator, f.denominator),
        gap=float(g), beat_hz=float(g) * F_C,
        a1=a1, a2=a2, parent=str(par) if par is not None else None,
        parent_maxpq=(max(par.numerator, par.denominator) if par else None),
        parent_below=bool(par is not None and
                          max(par.numerator, par.denominator) <= A),
        parent_is_ancestor=bool(par is not None and par in anc),
        detune_cents=(1200.0 * (float(f) / float(par) - 1.0) / 0.0005777
                      if par else None)))

n = len(rows)
v1 = sum(r["parent_below"] for r in rows) / n
v2 = sum(r["parent_is_ancestor"] for r in rows) / n
parents = [r["parent"] for r in rows]
v3a = len(set(parents))
v3b = max(parents.count(p) for p in set(parents)) / n
labels = {(r["parent"], round(r["beat_hz"] / HZ_RES)) for r in rows}
v4 = len(labels) / n

s1, s2, s3a, s3b, s4 = (P1.score(v1), P2.score(v2), P3A.score(v3a),
                        P3B.score(v3b), P4.score(v4))
p3 = s3a["met"] and s3b["met"]

print(f"I = {I_MUS}, B = {B}, horizon max(p,q) <= {A}, f_c = {F_C:.0f} Hz")
print(f"{len(BELOW)} below-horizon ratios available as parents; "
      f"{n} above-horizon ratios to categorise\n")

from collections import Counter                                   # noqa: E402
cnt = Counter(parents)
print(f"{'parent':>8s} {'n':>4s} {'share':>7s}  {'beat Hz range':>16s}   example")
for par, c in cnt.most_common(10):
    mem = [r for r in rows if r["parent"] == par]
    hz = [r["beat_hz"] for r in mem]
    ex = min(mem, key=lambda r: r["beat_hz"])
    print(f"{par:>8s} {c:>4d} {c / n:>6.1%}  {min(hz):>6.1f}–{max(hz):<9.1f}  "
          f"{ex['ratio']} beats at {ex['beat_hz']:.1f} Hz")
if len(cnt) > 10:
    print(f"{'':>8s} ... and {len(cnt) - 10} more parents")

print()
for b, v, f in ((P1, v1, "{:.1%}"), (P2, v2, "{:.1%}"), (P3A, v3a, "{:.0f}"),
                (P3B, v3b, "{:.1%}"), (P4, v4, "{:.1%}")):
    print("  " + b.line(v, f))

verdict = ("HEARD_AS_A_DETUNED_PARENT" if (s1["met"] and s2["met"] and p3 and s4["met"])
           else "CATEGORISED_BUT_LOPSIDED" if (s1["met"] and s2["met"] and not p3)
           else "PARENT_LABEL_DOES_NOT_HOLD")
print(f"\nVERDICT: {verdict}")
if verdict == "HEARD_AS_A_DETUNED_PARENT":
    print("  Above the horizon a ratio is its nearest in-box rational plus a beat.")
    print("  The category is a Stern-Brocot ancestor the synth already computes;")
    print("  the coordinate within the category is the beat rate in Hz.")

ex = summarise("n_parents_below", [r["parent_below"] for r in rows], EXISTENCE)
ct = summarise("beat_hz", [r["beat_hz"] for r in rows], CENTRAL_TENDENCY)
with redpath("above-horizon nodes carrying a parent label", expect_min=100) as rp:
    rp.observed(sum(1 for r in rows if r["parent"] is not None))

json.dump(dict(I=I_MUS, B=B, horizon=A, f_c=F_C, hz_resolution=HZ_RES,
               n_above=n, n_parents_available=len(BELOW),
               bars={s["name"]: s for s in (s1, s2, s3a, s3b, s4)},
               parent_histogram=dict(cnt), beat_hz=ct, existence=ex,
               verdict=verdict, rows=rows),
          open(f"{HERE}/brocot_above_horizon_parent.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_above_horizon_parent.json")
