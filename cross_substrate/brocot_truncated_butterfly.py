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

AMENDMENT 1 — H2 AS FIRST WRITTEN WAS INERT, and it was the non-inertness arm.

The code computed

    max(abs(rho(static_prom, crit) - rho(static_prom, crit)), ...)

which subtracts an expression from itself. It is identically 0.0 and cannot
fail for any data. The arm whose entire job was to prove the apparatus does not
manufacture matched/mismatched gaps was itself incapable of reporting one — the
defect this arc audits, in the guard against it, written by its auditor. It
passed on the first run at exactly 0.0000, which is what an inert arm looks like
and why a suspiciously perfect number is worth a second read.

The mistake was thinking a STATIC predictor could test the machinery. It cannot:
static means index-independent, so its two conditions are the same computation
and the gap is 0 by definition, not by measurement.

REPLACED WITH A REAL NULL. The machinery is run end to end against a SHUFFLED
`crit` field: if permuting indices manufactures a matched/mismatched gap, it
will manufacture one against noise too. The arm now reports the maximum |gap|
over those shuffles, and can fail. The bar and direction are unchanged.

AMENDMENT 2 — H2's BAR TESTS THE WRONG THING, and it is left MISSED rather than
repaired into a pass.

Keeping the bar at 0.005 asked "is the null gap small in absolute terms". That
is not the question. Two different predictors correlated against the same
shuffled field differ by chance, so the null gap has real spread and nothing
pins it near zero — the right question is whether the REAL gap stands out from
that spread, which is a permutation test, not a magnitude threshold.

The sealed arm is reported as it fell: MISSED. The permutation p-value is
reported beside it as an explicitly POST-HOC statistic, and the shuffle count is
raised from 20 to 200 so that p-value has resolution finer than 0.05. Raising
resolution on a statistic is not the same as moving a bar to clear it, and the
distinction is the reason the sealed arm stays failed.

READ THE RESULT CONSERVATIVELY. Even at its best this is a small effect on one
field: matched 0.137 against plain q's 0.111 on `crit`, while plain q dominates
`tonal` (0.217 vs 0.090) and `dense` (0.309 vs 0.083). The truncated predictor
wins only on the field it was sealed against. A single-field win with a
permutation p is suggestive; it is not the layer D-section-1 would let ship.

AMENDMENT — AFTER OUTPUT, 2026-09-09. **H3 NO LONGER HOLDS ON THE CURRENT
GRAPH, AND THE HEAD DOES NOT SHOW IT.**

brocot regenerated `landscape_graph_16mix.json.gz` on 2026-08-31, four working
days after this cell was banked (2026-08-25). `graph_staleness_census` re-ran
this committed generator unchanged on the current graph: 19 of 40 numeric fields
move, and **H3 reverses sign** —

    matched minus plain-q |rho|   +0.025801 (MET, bar 0.02)  ->  -0.009335 (MISSED)

The composed head is a function of EXISTENCE arms alone, so it still reads
MAP_TRACKS_THE_TRUNCATION on both graphs. That is the lattice working as
designed, and it is exactly why the head is not the whole report: **H3 is the
RESOLUTION arm whose claim is "it clears the plain-q baseline that shadowed the
first attempt", and on the current graph it does not clear it.** The shadow this
cell was written to escape is back, and a reader who checked only the verdict
would not learn that.

RE-BANKED 2026-09-09 (operator decision). The banked numbers above stand as what
was measured on the graph they were measured against; the current-graph run is
banked separately as `brocot_truncated_butterfly_regraph.json`, with the graph
pinned by sha256 and full provenance -- the same treatment
`brocot_filter_worth_it_regraph.json` got. Nothing here is edited, because a
number measured against a specific input is not made wrong by that input moving;
it is made SCOPED to it.

What the two artifacts say together, arm by arm:

    H1  matched minus mismatched |rho|   0.04337 -> 0.04268   MET both
    H2  shuffled-field gap               0.03524 -> 0.03917   MISSED both
                                         (it was ALREADY missing before the move)
    H3  matched minus plain-q |rho|      0.02580 -> -0.00934  MET -> MISSED
    H4  matched |rho| effect floor       0.13698 ->  0.09880  MET both, down 28%

**DO NOT CITE H3 WITHOUT ITS GRAPH.** On the current map the matched predictor is
very slightly WORSE than plain q, so the single-field win this cell was written to
establish is gone -- while the head, which reads EXISTENCE arms only, is unchanged
on both graphs. The conservative reading above ("a single-field win with a
permutation p is suggestive; it is not the layer D-section-1 would let ship") was
already the right one, and is now the only one.
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

h1v_pre = res[PRIMARY]["matched"] - res[PRIMARY]["mismatched"]
h1v = h1v_pre
# AMENDMENT 1: a real null. Run the SAME matched-vs-mismatched comparison
# against a shuffled field. If permuting indices manufactures a gap, it will
# manufacture one against noise. This can fail; the first version could not.
N_SHUF = 200
shuf_rng = np.random.default_rng(SEED + 1)
shuf_gaps = []
for _ in range(N_SHUF):
    y = shuf_rng.permutation(M[PRIMARY])
    shuf_gaps.append(abs(rho(M["matched"], y) - rho(M["mismatched"], y)))
static_gap = float(max(shuf_gaps))
shuf_mean = float(np.mean(shuf_gaps))
# post-hoc, amendment 2: the test the arm should have been.
perm_p = float((np.sum(np.array(shuf_gaps) >= abs(h1v)) + 1) / (N_SHUF + 1))

h1v = p["matched"] - p["mismatched"]

h3v = p["matched"] - p["static_q"]
H1 = Bar("matched minus mismatched |rho|", 0.03, floor=-1.0, ceiling=1.0,
         why="a difference of two |Spearman| values, each in [0,1]")
H2 = Bar("matched/mismatched gap against a SHUFFLED field", 0.005,
         direction="le", floor=0.0, ceiling=1.0,
         why="an absolute difference of two |Spearman| values, each in [0,1]; "
             "under a shuffled field both are near 0 but neither is pinned "
             "there, so this arm can and does vary")
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
print(f"shuffled-field null over {N_SHUF} draws: max |gap| {static_gap:.4f}, "
      f"mean {shuf_mean:.4f}   (real gap {h1v:.4f})")
print(f"POST-HOC permutation p (amendment 2, NOT the sealed arm): {perm_p:.4f}")
print(f"static predictors are index-INDEPENDENT, so their own gap is 0 by "
      f"definition and is not scored")
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
                          claim="permuting indices does not manufacture a gap "
                                "against a shuffled field"),
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
               shuffle_null=dict(n=N_SHUF, max_gap=static_gap,
                                 mean_gap=shuf_mean, real_gap=h1v,
                                 permutation_p_posthoc=perm_p),
               bars={s["name"]: s for s in (s1, s2, s3, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_truncated_butterfly.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_truncated_butterfly.json")
