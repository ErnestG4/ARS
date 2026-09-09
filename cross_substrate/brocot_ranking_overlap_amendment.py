#!/usr/bin/env python3
"""AMENDMENT: the exact top-4 overlap distribution, counted rather than inverted.

POST-HOC AND UNSEALED. It recomputes ONE reported field of
brocot_coherence_ranking_census.json and changes no arm, no bar and no verdict.

THE DEFECT IT REPAIRS
---------------------
The census reported `shared_top4_distribution` by INVERTING the Jaccard index:
`k = round(4 * j / (1 + j))`. Two things are wrong with that line.

  * The coefficient is wrong. For two 4-sets sharing k members,
    J = k / (8 - k), so the inverse is k = 8J / (1 + J), not 4J / (1 + J).
  * Even with the right coefficient, inverting a float to recover an integer is
    the wrong move. J = 3/5 is not representable, so `4*j/(1+j)` evaluates to
    1.4999999999999998 and rounds DOWN where exact arithmetic would round up --
    the answer depends on which side of a tie the binary expansion falls.

Together they collapsed the five possible values into three buckets:
k in {0,1} -> 0, k in {2,3} -> 1, k = 4 -> 2. The published keys were therefore
a lossy bucket index labelled as a count of shared members.

NOTHING ELSE MOVED, and that is worth stating precisely rather than reassuringly:
every arm of the census (mean Jaccard, its SE, the per-index means) is computed
directly from the per-case J values and never touches this inversion. The
verdict RANKING_EFFECT_RESOLVED_MODEL_GAP_IS_DOCUMENTATION_ONLY stands as
banked.

THE FIX IS NOT A BETTER INVERSION. `|su & sl|` is already an integer sitting
right there in the loop; the census threw it away and then tried to reconstruct
it from a ratio. This amendment counts it. The general form of the mistake --
recovering a quantity you already had, through a lossy transform -- is the same
shape as comparing fitted shape parameters when a level crossing was available
(derivflow, 2026-09-08).

TIE TO THE SEALED RUN: P1 below requires the recomputed mean Jaccard to equal the
census's banked value to double precision. That is what makes this the same
measurement rather than a neighbouring one -- the distribution is new
information, the mean is the anchor.
"""
import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction
from math import ceil, log2

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
sys.path.insert(0, ROOT)
sys.path.insert(0, BROCOT)
from phase3.partial_prediction import order_bound                   # noqa: E402

GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"
CENSUS = json.load(open(os.path.join(HERE, "brocot_coherence_ranking_census.json")))
_h = hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()
if _h != CENSUS["graph_sha256"]:
    raise SystemExit(f"INPUT DRIFT: graph {_h[:16]}... != the census's "
                     f"{CENSUS['graph_sha256'][:16]}...; this amendment can only "
                     "speak about the run it amends.")

CENTS_TOL, MAX_ORDER, MIN_IDX = 12.0, 24, 0.02
MAXEXTRA, TOPN = 3, 4
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


def _shared(bins, total):
    if total <= 0:
        return 0.0
    return sum(be for be, mk in bins.values() if mk and (mk & (mk - 1))) / total


def comb_score(ops, cents):
    act = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(act) <= 63:
        return 0.0
    bins, total = {}, 0.0
    for k, (r0, I) in enumerate(act):
        order = max(1, min(int(ceil(I)) + 4, MAX_ORDER))
        for m in range(1, order + 1):
            e = float(jv(m, I)) ** 2
            if e <= 0:
                continue
            for nu in (1 + m * float(r0), abs(1 - m * float(r0))):
                if nu <= 1e-4:
                    continue
                total += e
                b = bins.setdefault(int(round(1200.0 * log2(nu) / cents)), [0.0, 0])
                b[0] += e
                b[1] |= 1 << k
    return _shared(bins, total)


def lattice_score(ops, cents):
    act = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(act) <= 6:
        return None
    orders = [order_bound(I) for _, I in act]
    bins, total = {}, 0.0
    idx = [range(-o, o + 1) for o in orders]

    def rec(k, nu, amp, vec):
        nonlocal total
        if k == len(act):
            if all(n == 0 for n in vec) or abs(nu) <= 1e-4:
                return
            e = amp * amp
            total += e
            b = bins.setdefault(int(round(1200.0 * log2(abs(nu)) / cents)),
                                [0.0, set()])
            b[0] += e
            b[1].add(tuple(vec))
            return
        r, I = act[k]
        for n in idx[k]:
            a = float(jv(n, I))
            if a == 0.0:
                continue
            rec(k + 1, nu + n * float(r), amp * a, vec + [n])

    rec(0, 1.0, 1.0, [])
    if total <= 0:
        return 0.0
    return sum(be for be, pts in bins.values() if len(pts) >= 2) / total


def tails(mx):
    out, cur = [], [""]
    for _ in range(mx):
        cur = [t + c for t in cur for c in "LR"]
        out += cur
    return out


TAILS = tails(MAXEXTRA)
G = json.load(gzip.open(GRAPH))
pool = [nd for nd in G["nodes"]
        if 1 <= sum(1 for o in nd["ops"] if o["enabled"]) <= 2]
print(f"recomputing the overlap over {len(pool)} pool nodes", flush=True)

jac, kdist = [], {}
for n, nd in enumerate(pool):
    cur = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    cur = [(r, d) for r, d in cur if r > 0]
    if not cur:
        continue
    base = next(o["path"] for o in nd["ops"] if o["enabled"])
    nidx = float(np.median([d for _, d in cur])) or 0.9
    scored = []
    for t in TAILS:
        cr = walk(base + t)
        if any(abs(float(cr) - float(r)) < 1e-9 for r, _ in cur):
            continue
        ops = list(cur) + [(cr, nidx)]
        c = comb_score(ops, CENTS_TOL)
        L = lattice_score(ops, CENTS_TOL)
        if L is None:
            continue
        scored.append((c, L, base + t))
    if len(scored) < TOPN:
        continue
    su = {p for _, _, p in sorted(scored, key=lambda x: -x[0])[:TOPN]}
    sl = {p for _, _, p in sorted(scored, key=lambda x: -x[1])[:TOPN]}
    k = len(su & sl)                      # COUNTED, not inverted
    kdist[k] = kdist.get(k, 0) + 1
    jac.append(len(su & sl) / len(su | sl))
    if (n + 1) % 2000 == 0:
        print(f"  {n + 1}/{len(pool)}", flush=True)

mean_j = float(np.mean(jac))
banked = CENSUS["mean_jaccard"]
tie_ok = (mean_j == banked)
N = len(jac)

print(f"\nP1 tie to the sealed run: recomputed mean {mean_j!r}")
print(f"                          banked   mean {banked!r}")
print(f"                          identical: {tie_ok}")
print(f"\nEXACT top-4 overlap distribution over {N} cases:")
for k in sorted(kdist):
    print(f"   {k} of 4 shared : {kdist[k]:>5d}  ({100.0 * kdist[k] / N:5.1f}%)"
          f"   J = {k}/{8 - k}")
print(f"\n  as the census reported it (lossy buckets): "
      f"{CENSUS['shared_top4_distribution']}")
if not tie_ok:
    print("\n  P1 FAILED — this is not the same measurement; do not use it to "
          "amend the census.")
    sys.exit(1)

json.dump(dict(
    status="POST-HOC, UNSEALED AMENDMENT to brocot_coherence_ranking_census.json",
    amends="shared_top4_distribution only; no arm, bar or verdict changes",
    defect="the census inverted the Jaccard to recover k: round(4*j/(1+j)). The "
           "coefficient is wrong (k = 8J/(1+J) for two 4-sets) AND inverting a "
           "float to recover an integer is the wrong move at all -- J=3/5 is "
           "unrepresentable, so the expression lands at 1.4999999999999998 and "
           "rounds the wrong way. Together they collapsed five values into three "
           "buckets: {0,1}->0, {2,3}->1, {4}->2.",
    fix="count |su & sl| directly; it was already an integer in the loop and the "
        "census threw it away to reconstruct it from a ratio",
    n_cases=N, mean_jaccard_recomputed=mean_j, mean_jaccard_banked=banked,
    tie_to_sealed_run_exact=tie_ok,
    exact_overlap_distribution={str(k): kdist[k] for k in sorted(kdist)},
    census_lossy_buckets=CENSUS["shared_top4_distribution"],
    arms_unaffected="mean Jaccard, its SE and the per-index means are all "
                    "computed from the per-case J values and never touch the "
                    "inversion; the banked verdict stands"),
    open(os.path.join(HERE, "brocot_ranking_overlap_amendment.json"), "w"), indent=1)
print("\nwrote brocot_ranking_overlap_amendment.json")
