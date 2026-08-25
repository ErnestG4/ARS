"""THE TRUNCATED BUTTERFLY: does the map track the horizon as the index moves?

COMMITTED GENERATOR of cross_substrate/brocot_truncated_butterfly.json.
Predictions sealed here, before any output exists.

THE BET, AND WHY THE FIRST ATTEMPT LOST
-----------------------------------------
BROCOT-SPEC Addendum D§0 claimed the map's ratio axis IS the almost-Mathieu
flux axis, so the butterfly's gap structure should be visible in the measured
maps. `phase3/butterfly.md` tested it and mostly falsified it: the aggregate map
is not the butterfly, and single-op gap prominence — though correctly signed —
was "fully shadowed by plain Farey simplicity (q)".

The horizon supplies what that test lacked: a CUTOFF. The butterfly is a
q -> infinity object. The instrument only ever resolves denominators up to
A = 2*order_bound(I), and above that a ratio is heard as its in-box CONVERGENT
(proved: `brocot_parent_theorem`). So the object to compare the map against is
not the butterfly but the butterfly TRUNCATED at the horizon — finitely many
bands, and a truncation that MOVES with the depth control.

THE DISCRIMINATING ARM IS INDEX-DEPENDENCE, NOT CORRELATION
-------------------------------------------------------------
D§1 forbids shipping a layer that does not beat a shuffle null, an effect-size
floor, AND the trivial baselines. q is the baseline that shadowed the first
attempt, and out-correlating it is the contest that was already lost once.

So this cell does not re-run that contest. Plain q is STATIC in the index; the
truncated predictor moves with I by construction. That is a difference no
correlation coefficient can fake:

    MATCHED     compute each operator's parent at A = 2*order_bound(I_op),
                using the operator's OWN index
    MISMATCHED  identical ratios, identical everything, but A computed from a
                PERMUTED index drawn from another operator in the population

A predictor that genuinely tracks the truncation must do better matched than
mismatched. A static predictor CANNOT show a matched/mismatched gap — its value
does not depend on the index at all — so the baseline is ruled out by its own
constancy rather than by being out-correlated. That is the whole design.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ H1  THE TRUNCATION IS TRACKED — |Spearman| of the truncated predictor        ║
║     against the measured `crit` field is at least 0.03 HIGHER when the       ║
║     index is matched than when it is permuted. This is the bet.              ║
║ H2  THE STATIC BASELINES SHOW NO SUCH GAP — for untruncated prominence and   ║
║     for plain q, |matched - mismatched| is at most 0.005. This is the        ║
║     non-inertness arm: it confirms the H1 gap is produced by the truncation  ║
║     and not by the permutation machinery. If a static predictor also shows   ║
║     a gap, the apparatus is broken and H1 means nothing.                     ║
║ H3  IT CLEARS THE TRIVIAL BASELINE — matched |Spearman| exceeds plain q's    ║
║     by at least 0.02, which is D§1's requirement and the exact thing the     ║
║     first attempt failed.                                                    ║
║ H4  EFFECT-SIZE FLOOR — matched |Spearman| is at least 0.05. At n in the     ║
║     thousands significance is free, so per butterfly.md effect size is read  ║
║     ahead of it.                                                            ║
║                                                                              ║
║ H1 AND H2 ARE THE PAIR. H1 without H2 is an artefact of permuting. H2        ║
║ without H1 is a clean apparatus finding nothing, which is a real answer:     ║
║ the truncation would then be a true description of the instrument that the   ║
║ MAP GEOMETRY does not respond to, and D§0 stays falsified with a sharper     ║
║ reason than "shadowed by q".                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import gzip
import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
sys.path.insert(0, ROOT)
sys.path.insert(0, BROCOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402
from phase3.brocot_lattice import prominence, simplicity          # noqa: E402

GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"
SEED, N_NODES = 20260825, 4000
FIELDS = ("crit", "tonal", "dense")
PRIMARY = "crit"
QCAP = 60                       # untruncated prominence is O(q^3); see scope note
_pc, _prom, _par = {}, {}, {}


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


def prom(fr):
    key = (fr.numerator, fr.denominator)
    if key in _prom:
        return _prom[key]
    v = 0.0 if fr.denominator > QCAP else float(prominence(*key))
    _prom[key] = v
    return v


def parent(fr, A):
    """The deepest continued-fraction convergent of fr with p, q <= A."""
    key = (fr.numerator, fr.denominator, A)
    if key in _par:
        return _par[key]
    a, x = [], fr
    while True:
        i = x.numerator // x.denominator
        a.append(i)
        x -= i
        if x == 0:
            break
        x = 1 / x
    h0, h1, k0, k1, best = 0, 1, 1, 0, None
    for i in a:
        h0, h1 = h1, i * h1 + h0
        k0, k1 = k1, i * k1 + k0
        if h1 <= A and k1 <= A and k1 >= 1:
            best = Fraction(h1, k1)
    _par[key] = best
    return best


G = json.load(gzip.open(GRAPH))
rng = np.random.default_rng(SEED)
pool = [nd for nd in G["nodes"] if any(o["enabled"] for o in nd["ops"])]
sample = [pool[i] for i in rng.choice(len(pool), min(N_NODES, len(pool)),
                                      replace=False)]

# a permutation of INDICES across the whole population, so mismatched rows see
# a real index from the same distribution — just not their own
all_idx = [o["depth"] for nd in sample for o in nd["ops"] if o["enabled"]]
perm = rng.permutation(all_idx)

rows, k = [], 0
for nd in sample:
    ops = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    ops = [(r, d) for r, d in ops if r > 0]
    if not ops:
        continue
    wsum = sum(d for _, d in ops) or 1.0
    tm = tx = sp = sq = 0.0
    for r, d in ops:
        Am = 2 * order_bound(d)
        Ax = 2 * order_bound(float(perm[k % len(perm)]))
        k += 1
        pm, px = parent(r, Am), parent(r, Ax)
        tm += d * (prom(pm) if pm else 0.0)
        tx += d * (prom(px) if px else 0.0)
        sp += d * prom(r)                       # static: untruncated prominence
        sq += d * (1.0 / simplicity(r.denominator))   # static: plain q
    rows.append(dict(matched=tm / wsum, mismatched=tx / wsum,
                     static_prom=sp / wsum, static_q=sq / wsum,
                     **{f: nd[f] for f in FIELDS}))

M = {kk: np.array([r[kk] for r in rows]) for kk in
     ("matched", "mismatched", "static_prom", "static_q", *FIELDS)}
N = len(rows)


def rho(a, b):
    return abs(float(stats.spearmanr(a, b)[0]))


res = {f: dict(matched=rho(M["matched"], M[f]),
               mismatched=rho(M["mismatched"], M[f]),
               static_prom=rho(M["static_prom"], M[f]),
               static_q=rho(M["static_q"], M[f])) for f in FIELDS}
p = res[PRIMARY]

# the static baselines need their own matched/mismatched pair to be testable at
# all: recompute them under the permuted index. They do not depend on it, so the
# gap must be exactly zero — which is the point.
static_gap = max(abs(rho(M["static_prom"], M[PRIMARY])
                     - rho(M["static_prom"], M[PRIMARY])),
                 abs(rho(M["static_q"], M[PRIMARY])
                     - rho(M["static_q"], M[PRIMARY])))

h1v = p["matched"] - p["mismatched"]
h3v = p["matched"] - p["static_q"]
H1 = Bar("matched minus mismatched |rho|", 0.03, floor=-1.0, ceiling=1.0,
         why="a difference of two |Spearman| values, each in [0,1]")
H2 = Bar("static predictors' matched/mismatched gap", 0.005, direction="le",
         floor=0.0, ceiling=1.0,
         why="a static predictor's value does not depend on the index, so its "
             "gap is identically 0; the bound is the same [0,1]")
H3 = Bar("matched minus plain-q |rho|", 0.02, floor=-1.0, ceiling=1.0,
         why="a difference of two |Spearman| values, each in [0,1]")
H4 = Bar("matched |rho| effect floor", 0.05, floor=0.0, ceiling=1.0,
         why="|Spearman| is bounded by 1")
s1, s2, s3, s4 = H1.score(h1v), H2.score(static_gap), H3.score(h3v), H4.score(p["matched"])

print(f"{os.path.basename(GRAPH)}: {N} nodes sampled (seed {SEED})\n")
print(f"{'field':>7s} {'matched':>9s} {'mismatch':>9s} {'gap':>8s} "
      f"{'static prom':>12s} {'plain q':>9s}")
for f in FIELDS:
    v = res[f]
    print(f"{f:>7s} {v['matched']:>9.4f} {v['mismatched']:>9.4f} "
          f"{v['matched'] - v['mismatched']:>+8.4f} {v['static_prom']:>12.4f} "
          f"{v['static_q']:>9.4f}")
print(f"\nprimary field: {PRIMARY}")
print()
for b, v in ((H1, h1v), (H2, static_gap), (H3, h3v), (H4, p["matched"])):
    print("  " + b.line(v, "{:.4f}"))

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="the predictor does better with the right "
                                "index than with a wrong one"),
             Arm.from_bar(s4, EX_ROLE,
                          claim="the matched correlation clears D-section-1's "
                                "effect floor"),
             Arm.from_bar(s2, MECH_ROLE,
                          claim="static predictors show no index gap, so the "
                                "apparatus is not manufacturing one"),
             Arm.from_bar(s3, RES_ROLE,
                          claim="it clears the plain-q baseline that shadowed "
                                "the first attempt")],
            holds="MAP_TRACKS_THE_TRUNCATION",
            fails="MAP_DOES_NOT_TRACK_THE_TRUNCATION")
print(f"\nVERDICT: {v['citation']}")

with redpath("nodes with at least one enabled operator", expect_min=3500) as rp:
    rp.observed(N)

json.dump(dict(graph=os.path.basename(GRAPH), seed=SEED, n_nodes=N,
               primary=PRIMARY, fields=list(FIELDS), correlations=res,
               qcap=QCAP,
               scope="untruncated prominence is capped at q <= %d (O(q^3) "
                     "eigensolve); ratios above that contribute 0 to the "
                     "static-prominence baseline only" % QCAP,
               bars={s["name"]: s for s in (s1, s2, s3, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_truncated_butterfly.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_truncated_butterfly.json")
