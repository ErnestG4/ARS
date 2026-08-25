"""DOES A PAIRWISE HORIZON FIELD EARN A GRAPH DIMENSION? Measured on the shipped map.

COMMITTED GENERATOR of cross_substrate/brocot_map_dimension.json.
Predictions sealed here, before any output exists.

THE QUESTION, AND THE THING IT IS NOT
--------------------------------------
The obvious move after the parent theorem is "add the parent field to the map".
That move is FORBIDDEN and the reason is already measured: `brocot_dissolution_
curve` puts the coincidence rate above 0.9 by N = 7, and the shipped graph is
n_ops = 16. An N-way horizon field would read "everything coincides" on
essentially every node — a dimension with no variance, which is worse than no
dimension because it looks like information.

But a PAIRWISE reduction is well defined at any N. A patch with k enabled
operators has C(k,2) pairs; each pair has a horizon status and a gap, and the
node-level field is a statistic over those pairs. Nothing about that is vacuous
at N = 16.

Whether it EARNS a place is a different question from whether it is definable,
and it is the question this cell asks. Three ways a new dimension can be
worthless, all of which this arc has hit before:

  RAILED       it takes one value on nearly every node (`railed.py`: the
               distinct-value ratio is what separates a real concentration from
               a floor)
  REDUNDANT    it correlates with a field the map already has, so it adds a
               column and no information (bright, dense, odd, tonal, crit)
  A RELABELLING it varies between families and not within them, in which case
               it is `family` wearing a new name

THE ASYMMETRIC HORIZON, which this needs and the theorem did not state
----------------------------------------------------------------------
The published theorem assumes both modulators at the same index. A real patch
has per-operator indices, so for ops at (r1, I1) and (r2, I2) with
alpha = r2/r1 = p/q in lowest terms, a coincidence needs a*r1 + b*r2 = 0 with
|a| <= 2*order_bound(I1) and |b| <= 2*order_bound(I2), giving

    p <= 2*order_bound(I1)   AND   q <= 2*order_bound(I2)

The symmetric statement is the I1 = I2 case. The prefix argument behind the
convergent theorem survives asymmetry unchanged, because both bounds are
monotone in q — so the gap is still a continued-fraction walk and not a box
scan, which is what makes 3.6M pairs affordable.

PHYSICAL UNITS. Two partials of the pair differ by f_c * r1 * gap Hz, so the
separation carries r1 and is a real frequency, not a dimensionless residue.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ G1  NOT RAILED — the fuse-fraction field takes at least 50 distinct values   ║
║     across nodes, and no single value holds more than 60% of them.           ║
║ G2  NOT REDUNDANT — |Spearman| against every existing node field (bright,    ║
║     dense, odd, tonal, crit) is at most 0.60.                                ║
║ G3  NOT A RELABELLING OF FAMILY — the median within-family IQR of the field  ║
║     is at least 0.30x its global IQR. A field that only separates families   ║
║     is a colour for something the map already draws.                         ║
║ G4  MUSICALLY LIVE — at least 20% of nodes have a minimum pairwise           ║
║     separation strictly inside the beating range, 0 < sep < 20 Hz.           ║
║                                                                              ║
║ G2 IS THE ONE THAT DECIDES IT. A field can be beautifully derived and still  ║
║ be `dense` in a hat: partial-count and coincidence-count are plausibly the   ║
║ same thing seen twice. If G2 misses, the honest answer is that the horizon   ║
║ explains a dimension the map ALREADY has, which is a real result and NOT a   ║
║ new column — and it should be reported that way rather than shipped.         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import gzip
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np
from scipy import stats

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
BEAT_HZ = 20.0
EXISTING = ("bright", "dense", "odd", "tonal", "crit")

_path_cache = {}


def walk(path):
    """Stern-Brocot path string -> exact rational."""
    if path in _path_cache:
        return _path_cache[path]
    ln, ld, hn, hd = 0, 1, 1, 0
    for c in path:
        mn, md = ln + hn, ld + hd
        if c == "L":
            hn, hd = mn, md
        else:
            ln, ld = mn, md
    r = Fraction(ln + hn, ld + hd)
    _path_cache[path] = r
    return r


_gap_cache = {}


def pair_gap(alpha, A1, A2):
    """(fuses, gap) for |a1 + a2*alpha|, |a1| <= A1, |a2| <= A2. Exact.

    Uses the convergent theorem: the minimiser is a convergent of alpha, so
    this is a continued-fraction walk rather than a scan of the box."""
    key = (alpha, A1, A2)
    hit = _gap_cache.get(key)
    if hit is not None:
        return hit
    p, q = alpha.numerator, alpha.denominator
    if p <= A1 and q <= A2:
        out = (True, Fraction(0))
        _gap_cache[key] = out
        return out
    a, x = [], alpha
    while True:
        i = x.numerator // x.denominator
        a.append(i)
        x -= i
        if x == 0:
            break
        x = 1 / x
    h0, h1, k0, k1 = 0, 1, 1, 0
    best = None
    for i in a:
        h0, h1 = h1, i * h1 + h0
        k0, k1 = k1, i * k1 + k0
        if h1 <= A1 and k1 <= A2:
            v = abs(k1 * alpha - h1)
            if best is None or v < best:
                best = v
    if best is None:                        # not even a convergent fits the box
        best = min(abs(Fraction(a1) + Fraction(a2) * alpha)
                   for a1 in range(-A1, A1 + 1) for a2 in range(-A2, A2 + 1)
                   if (a1, a2) != (0, 0))
    out = (False, best)
    _gap_cache[key] = out
    return out


G = json.load(gzip.open(GRAPH))
FC = float(G.get("f_carrier_ref", 220.0))
nodes = G["nodes"]

fuse, minsep, npairs, fam = [], [], [], []
have = {k: [] for k in EXISTING}
for nd in nodes:
    ops = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    if len(ops) < 2:
        continue
    nf = nt = 0
    sep_best = None
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            r1, I1 = ops[i]
            r2, I2 = ops[j]
            if r1 == 0 or r2 == 0:
                continue
            A1, A2 = 2 * order_bound(I1), 2 * order_bound(I2)
            if A1 < 1 or A2 < 1:
                continue
            al = r2 / r1
            f, g = pair_gap(al, A1, A2)
            nt += 1
            nf += f
            s = float(g) * float(r1) * FC
            if sep_best is None or s < sep_best:
                sep_best = s
    if not nt:
        continue
    fuse.append(nf / nt)
    minsep.append(sep_best)
    npairs.append(nt)
    fam.append(nd["family"])
    for k in EXISTING:
        have[k].append(nd[k])

fuse = np.array(fuse)
minsep = np.array(minsep)
fam = np.array(fam)
N = fuse.size

vals, counts = np.unique(fuse, return_counts=True)
g1_distinct = int(vals.size)
g1_top = float(counts.max() / N)
rho = {k: float(abs(stats.spearmanr(fuse, np.array(v))[0])) for k, v in have.items()}
g2 = max(rho.values())


def iqr(a):
    return float(np.percentile(a, 75) - np.percentile(a, 25)) if a.size else 0.0


gi = iqr(fuse)
within = [iqr(fuse[fam == f]) for f in np.unique(fam) if (fam == f).sum() >= 30]
g3 = float(np.median(within) / gi) if gi > 0 and within else 0.0
g4 = float(((minsep > 0) & (minsep < BEAT_HZ)).mean())

# CEILINGS CORRECTED 2026-08-25 (adversarial review). B1a's ceiling was N, the
# node count -- but the field is nf/nt with nt <= C(16,2) = 120, so it can only
# take 4387 distinct values however many nodes there are. A value in
# (4387, 25772] is arithmetically impossible and would have gone unflagged: a
# ceiling 5.9x too loose, in the arc that produced the guard. B1b's floor
# followed from the same error.
N_ACHIEVABLE = 4387          # distinct a/b with 1 <= b <= 120, 0 <= a <= b
B1a = Bar("distinct values of the fuse field", 50, floor=1,
          ceiling=min(N, N_ACHIEVABLE),
          why=f"the field is nf/nt with nt <= C(16,2) = 120, so it can take at "
              f"most {N_ACHIEVABLE} distinct values regardless of node count")
B1b = Bar("largest single value's share", 0.60, direction="le",
          floor=1.0 / N_ACHIEVABLE, ceiling=1.0,
          why=f"with at most {N_ACHIEVABLE} achievable values, the most even "
              f"possible split still gives the largest 1/{N_ACHIEVABLE}")
B2 = Bar("max |Spearman| vs an existing field", 0.60, direction="le",
         floor=0.0, ceiling=1.0, why="|Spearman| is bounded by 1")
# CEILING CORRECTED, after out_of_range fired at 1.541. The first `why` read
# "a within-group spread cannot exceed the pooled spread it is a subset of",
# which is FALSE: when the pooled distribution is peaked, a family that spans
# widely has an IQR larger than the pooled IQR. The true bound is the field's
# full range over its global IQR, since no subgroup IQR can exceed the range.
# Third wrong ceiling in this arc, third caught by its own data.
# HONEST LIMIT, recorded 2026-08-25: this ceiling is DATA-DERIVED (the global
# IQR is measured), so `out_of_range` cannot independently audit it -- the bound
# is a rearrangement of the same numbers. reachable.py's doctrine says a range
# is a property of the DESIGN; this statistic has no design-side ceiling because
# its denominator is a measurement. Declared rather than disguised.
B3 = Bar("median within-family IQR / global IQR", 0.30, floor=0.0,
         ceiling=(float(fuse.max() - fuse.min()) / gi) if gi > 0 else 1.0,
         why="no subgroup IQR can exceed the field's full range, so the ratio "
             "is bounded by range / global IQR — NOTE: DATA-DERIVED, so the "
             "out_of_range audit on this bar is not independent")
B4 = Bar("nodes beating below 20 Hz", 0.20, floor=0.0, ceiling=1.0,
         why="a fraction of nodes: 0 to 1 by construction")

s1a, s1b, s2, s3, s4 = (B1a.score(g1_distinct), B1b.score(g1_top),
                        B2.score(g2), B3.score(g3), B4.score(g4))
not_railed = s1a["met"] and s1b["met"]

print(f"{os.path.basename(GRAPH)}: {len(nodes)} nodes, n_ops = {G['n_ops']}, "
      f"f_c = {FC:.0f} Hz")
print(f"nodes with >= 2 enabled operators: {N}   "
      f"pairs scored: {sum(npairs)}   gap cache: {len(_gap_cache)}\n")
print(f"fuse fraction  min {fuse.min():.3f}  median {np.median(fuse):.3f}  "
      f"max {fuse.max():.3f}   ({g1_distinct} distinct values)")
print(f"min separation min {minsep.min():.2f} Hz  median "
      f"{np.median(minsep):.2f} Hz  max {minsep.max():.1f} Hz\n")
print("Spearman against the fields the map already has:")
for k in EXISTING:
    print(f"    {k:>8s}  {rho[k]:+.3f}")
print()
for b, v, f in ((B1a, g1_distinct, "{:.0f}"), (B1b, g1_top, "{:.1%}"),
                (B2, g2, "{:.3f}"), (B3, g3, "{:.3f}"), (B4, g4, "{:.1%}")):
    print("  " + b.line(v, f))

v = compose([Arm("not_railed", EX_ROLE, not_railed,
                 value=g1_distinct, thresh=50,
                 claim="the field is not one value on nearly every node "
                       "(fuses B1a distinct-count AND B1b largest-share; "
                       "the cited value is B1a's)"),
             Arm.from_bar(s2, EX_ROLE, note="vs bright/dense/odd/tonal/crit"),
             # ROLE CORRECTED (adversarial review): the seal lists "A
             # RELABELLING" as one of the three ways the dimension is
             # WORTHLESS, so a G3 miss must be able to negate. It was wired
             # RESOLUTION, where it could only qualify. It passed at 1.54 so
             # the arm never fired, but its negating power had been removed
             # relative to the sealed semantics.
             Arm.from_bar(s3, EX_ROLE, note="within-family resolution",
                          claim="the field resolves inside families, so it is "
                                "not `family` under another name"),
             Arm.from_bar(s4, MECH_ROLE, note="the beat mechanism is live")],
            holds="EARNS_A_DIMENSION", fails="DOES_NOT_EARN_A_DIMENSION")
print(f"\nVERDICT: {v['citation']}")
if v["head"] == "EARNS_A_DIMENSION":
    print("  The pairwise horizon field is not railed, not a restatement of a")
    print("  column the map already has, and resolves within families. It is a")
    print("  new dimension, and the scope that forbids the N-way field does not")
    print("  reach it.")
else:
    print("  Report it as an explanation of an existing dimension, not as a new")
    print("  column. A field that duplicates `dense` is `dense` in a hat.")

ex = summarise("n_nodes_beating", [1 for m in minsep if 0 < m < BEAT_HZ],
               EXISTENCE)
with redpath("nodes with at least two enabled operators", expect_min=20000) as rp:
    rp.observed(N)

json.dump(dict(graph=os.path.basename(GRAPH), n_ops=G["n_ops"], f_c=FC,
               n_nodes_scored=int(N), n_pairs=int(sum(npairs)),
               fuse=dict(min=float(fuse.min()), median=float(np.median(fuse)),
                         max=float(fuse.max()), distinct=g1_distinct,
                         top_share=g1_top),
               min_separation_hz=dict(min=float(minsep.min()),
                                      median=float(np.median(minsep)),
                                      max=float(minsep.max())),
               spearman_vs_existing=rho,
               bars={s["name"]: s for s in (s1a, s1b, s2, s3, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_map_dimension.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_map_dimension.json")
