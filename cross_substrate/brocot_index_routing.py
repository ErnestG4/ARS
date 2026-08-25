"""IS THE SHIPPED COLUMN CONDITIONED ON A ROUTING CONVENTION?

COMMITTED GENERATOR of cross_substrate/brocot_index_routing.json.
Predictions sealed here, before any output exists.

WHY THIS FOLLOWS FROM A4
-------------------------
`brocot_asymmetric_horizon` established that fusion is NOT invariant under
moving the higher index between two operators: holding both ratios fixed, the
condition goes from (p <= 2B1, q <= 2B2) to (p <= 2B2, q <= 2B1), and 468
ratios flip on the tested grid. Which operator is driven harder is a fusion
parameter, not only a brightness parameter.

That has an immediate consequence for a column already shipped. The
fusion-density field in `brocot_map_dimension` evaluated every pair under the
patch's ACTUAL index assignment. If brocot's 30k patches systematically put the
higher index on one side, the column's values are conditioned on that
convention — and a reader is entitled to know which side, because the same map
generated under the opposite convention would carry different numbers.

This is a read-only census. Nothing is recomputed or corrected; the question is
whether the convention exists and whether it moves the column.

DEFINITIONS, so the direction is not chosen after the fact
-----------------------------------------------------------
For an ordered pair of enabled operators (i, j) with ratios r_i, r_j and indices
I_i, I_j, write alpha = r_j / r_i = p/q. The pair FUSES iff
p <= 2*order_bound(I_i) and q <= 2*order_bound(I_j).

  SWAP-SENSITIVE   the verdict differs between the actual assignment and the
                   one with I_i and I_j exchanged. Exactly one of the two fuses.
  ALIGNED          among swap-sensitive pairs, the ACTUAL assignment is the one
                   that fuses. Alignment rate 0.5 means no convention; anything
                   else is one, and its direction is read off the sign.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ W1  SWAP-SENSITIVITY IS NON-NEGLIGIBLE — at least 5% of enabled operator     ║
║     pairs in the shipped map change verdict when the two indices are         ║
║     exchanged. If this misses, A4 is a true statement about a corner of the  ║
║     ratio space the instrument does not occupy, and nothing downstream needs ║
║     to change.                                                               ║
║ W2  A CONVENTION EXISTS — the alignment rate differs from 0.5 by at least    ║
║     0.05. Direction deliberately NOT predicted: the point is to read it off, ║
║     and predicting it would invite reading the sign I expected.              ║
║ W3  IT MOVES THE COLUMN — the median absolute change in a node's fusion      ║
║     density under a global index swap is at least 0.01. A convention that    ║
║     exists but does not move the values is a curiosity, not a caveat.        ║
║                                                                              ║
║ W1 AND W3 ARE THE PAIR THAT DECIDES THE DOC. W2 without W3 means the         ║
║ convention is real and inert, and the honest note is one sentence. W1 and    ║
║ W3 together mean the column carries a conditioning statement.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import gzip
import json
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
sys.path.insert(0, ROOT)
sys.path.insert(0, BROCOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from existence import summarise, EXISTENCE                        # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"
_pc = {}


def walk(path):
    if path in _pc:
        return _pc[path]
    ln, ld, hn, hd = 0, 1, 1, 0
    for c in path:
        mn, md = ln + hn, ld + hd
        if c == "L":
            hn, hd = mn, md
        else:
            ln, ld = mn, md
    _pc[path] = Fraction(ln + hn, ld + hd)
    return _pc[path]


G = json.load(gzip.open(GRAPH))
nodes = G["nodes"]

n_pairs = n_sens = n_aligned = 0
dens_actual, dens_swapped, higher_on_larger = [], [], 0
n_diff_index = 0
for nd in nodes:
    ops = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    ops = [(r, d) for r, d in ops if r != 0]
    if len(ops) < 2:
        continue
    fa = fs = tot = 0
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            ri, Ii = ops[i]
            rj, Ij = ops[j]
            Bi, Bj = order_bound(Ii), order_bound(Ij)
            if Bi < 1 or Bj < 1:
                continue
            al = rj / ri
            p, q = al.numerator, al.denominator
            act = (p <= 2 * Bi) and (q <= 2 * Bj)
            swp = (p <= 2 * Bj) and (q <= 2 * Bi)
            tot += 1
            fa += act
            fs += swp
            n_pairs += 1
            if act != swp:
                n_sens += 1
                n_aligned += act
            if Ii != Ij:
                n_diff_index += 1
                higher_on_larger += ((Ii > Ij) == (ri > rj))
    if tot:
        dens_actual.append(fa / tot)
        dens_swapped.append(fs / tot)

da = np.array(dens_actual)
ds = np.array(dens_swapped)
w1 = n_sens / n_pairs
align = n_aligned / n_sens if n_sens else 0.5
w2 = abs(align - 0.5)
w3 = float(np.median(np.abs(da - ds)))
larger_rate = higher_on_larger / n_diff_index if n_diff_index else 0.5

W1 = Bar("swap-sensitive share of pairs", 0.05, floor=0.0, ceiling=1.0,
         why="a fraction of enabled operator pairs: 0 to 1 by construction")
W2 = Bar("|alignment rate - 0.5|", 0.05, floor=0.0, ceiling=0.5,
         why="an alignment rate lies in [0,1], so its distance from 0.5 is "
             "bounded by 0.5")
W3 = Bar("median |change in fusion density|", 0.01, floor=0.0, ceiling=1.0,
         why="fusion density is a fraction in [0,1], so a change is bounded by 1")
s1, s2, s3 = W1.score(w1), W2.score(w2), W3.score(w3)

print(f"{os.path.basename(GRAPH)}: {len(da)} nodes, {n_pairs} enabled pairs\n")
print(f"swap-sensitive pairs        {n_sens:>8d}  ({w1:.1%})")
print(f"  of those, ACTUAL fuses    {n_aligned:>8d}  (alignment {align:.1%})")
print(f"pairs with unequal indices  {n_diff_index:>8d}")
print(f"  higher index on the LARGER ratio  {larger_rate:.1%}")
print(f"\nfusion density  actual median {np.median(da):.4f}   "
      f"swapped median {np.median(ds):.4f}")
print(f"median |change| {w3:.4f}   nodes changed at all: "
      f"{float((da != ds).mean()):.1%}\n")
for b, v, f in ((W1, w1, "{:.1%}"), (W2, w2, "{:.3f}"), (W3, w3, "{:.4f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE, note="A4 reaches the instrument"),
             Arm.from_bar(s3, EX_ROLE, note="and moves the column"),
             Arm.from_bar(s2, MECH_ROLE, note="a routing convention exists")],
            holds="COLUMN_IS_CONDITIONED_ON_ROUTING",
            fails="ROUTING_DOES_NOT_REACH_THE_COLUMN")
print(f"\nVERDICT: {v['citation']}")
if v["head"] == "COLUMN_IS_CONDITIONED_ON_ROUTING":
    side = ("the LARGER-ratio operator" if larger_rate > 0.5
            else "the SMALLER-ratio operator")
    print(f"  The map drives {side} harder in {max(larger_rate, 1 - larger_rate):.1%}")
    print(f"  of unequal-index pairs, and {w1:.1%} of pairs would change verdict")
    print("  under a swap. The fusion-density column's values are conditioned on")
    print("  that convention and the doc must name the side.")

ex = summarise("n_swap_sensitive_pairs", [n_sens], EXISTENCE)
with redpath("enabled operator pairs censused", expect_min=500000) as rp:
    rp.observed(n_pairs)

json.dump(dict(graph=os.path.basename(GRAPH), n_nodes=len(da),
               n_pairs=n_pairs, n_swap_sensitive=n_sens,
               swap_sensitive_share=w1, alignment_rate=align,
               n_unequal_index=n_diff_index,
               higher_index_on_larger_ratio_rate=larger_rate,
               median_density_actual=float(np.median(da)),
               median_density_swapped=float(np.median(ds)),
               median_abs_change=w3,
               nodes_changed=float((da != ds).mean()),
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_index_routing.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_index_routing.json")
