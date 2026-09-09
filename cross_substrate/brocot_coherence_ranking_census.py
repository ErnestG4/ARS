#!/usr/bin/env python3
"""FULL-POOL CENSUS: does the model gap change what the engine RECOMMENDS?

COMMITTED GENERATOR of cross_substrate/brocot_coherence_ranking_census.json.
Predictions sealed here, before any full-pool output exists.

THE QUEUED ROW, IN THE CELL'S OWN WORDS
----------------------------------------
`brocot_coherence_model`'s amendment 3 refused to let a near-bar result stand as
a verdict: M3 came in at Jaccard 0.5171 with a 95% interval of [0.4677, 0.5664]
over 140 cases, and the 0.50 bar sits INSIDE that interval. It reported the arm
MISSED exactly as it fell, amended the head to RANKING_EFFECT_UNRESOLVED, and
computed what resolving it would take: `cases_to_resolve: 1170`.

Two things have changed since, both of which make the census stronger than the
1170-case resample it asked for.

  1. THE POOL IS ONLY 6,386 NODES. At 1170 the interval merely grazes the bar
     (half-width 0.0171 against an excess of 0.0171). The whole population of
     1-2-operator nodes is affordable, so this runs a CENSUS rather than a
     larger sample, and the mean over the shipped map becomes exact rather than
     estimated. Sampling error stops being the question.
  2. THE BANKED ARTIFACT IS STALE. `graph_staleness_census` (2026-09-09) found
     brocot regenerated the 16mix graph on 2026-08-31, four days after the
     coherence cell was banked: 17 of its 44 numeric fields no longer re-derive,
     and mean_jaccard moves 0.5171 -> 0.5309 on the current graph. So the right
     act is not to add cases to a stale estimate but to supersede it on a graph
     PINNED BY HASH, which this cell does and fails closed on.

PRIOR LOOK, DISCLOSED IN FULL. I know both values above -- 0.5171 banked, 0.5309
on the current graph at n = 140 -- before sealing. C1 is therefore stated
DIRECTIONALLY and in the direction those numbers point, because a two-sided bar
here would be an artifact of pretending not to know. What the census can still
settle, and what those 140 cases cannot, is whether the population mean clears
0.50 at all: both estimates sit within one standard error of the bar.

WHAT A MEAN JACCARD ABOVE 0.50 MEANS. Jaccard between two 4-sets takes only the
values {0, 1/7, 1/3, 3/5, 1} as they share 0..4 members, so 0.50 is not an
achievable per-case value -- it is a threshold on the mean, sitting between
"share 2 of 4" (0.333) and "share 3 of 4" (0.600). Above it, the shipped ranking
and the true-lattice ranking agree on the majority of what a player is shown; the
model gap is then documentation rather than a user-visible defect. Below it, the
gap changes recommendations and the docstring is not the only thing to fix.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    the scorers are the banked cell's. Their ANALYTIC quantity --  ║
║                omitted cross-partial energy (1 - J0(I)^2)^2 at the three      ║
║                indices -- reproduces brocot_coherence_model.json exactly,     ║
║                mismatches <= 0.5 of 3. This is deliberately the               ║
║                graph-INDEPENDENT tie: the banked graph-dependent numbers are  ║
║                known stale, so reproducing THEM would be the wrong premise.   ║
║ P2  PREMISE    the census is a census: scored cases >= 6000 of the 6,386      ║
║                pool nodes. Below that it is a large sample with an unstated   ║
║                selection rule, and the exactness claim above evaporates.      ║
║ C1  EXISTENCE  DIRECTIONAL, prior look disclosed: population mean Jaccard     ║
║                > 0.50. The rankings agree on more than the bar.               ║
║ C2  MECHANISM  and not by a hair: the mean exceeds 0.50 by more than the 95%  ║
║                half-width, so the finding would survive resampling and is     ║
║                not the boundary call amendment 3 refused to make.             ║
║ C3  RESOLUTION and pooling is not hiding a reversal: recomputed at each       ║
║                FIXED index in {0.9, 1.5, 2.0}, the mean clears 0.50 at all    ║
║                three. The banked cell already found the model gap's size      ║
║                varies strongly with index (omitted energy 12% -> 90%), so a   ║
║                pooled-only answer would be exactly the within-substrate       ║
║                failure this repo has filed before.                           ║
║                                                                              ║
║ C3 IS THE CELL. C1 can be carried by whichever index dominates the nidx       ║
║ distribution; C3 is the claim that the answer does not depend on that.       ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE: this supersedes M3 of brocot_coherence_model on the current graph. It does
NOT re-open M1/M2/M4, and it does not touch that cell's other amendments.
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
from reachable import Bar                                          # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,     # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED              # noqa: E402
from redpath import redpath                                        # noqa: E402
from phase3.partial_prediction import order_bound                   # noqa: E402

GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"
GRAPH_SHA256 = "1b6c755f4174ca38dfe8411f5c03b52df4eac7d9229cd9873fb86f26feeaa30c"
_h = hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()
if _h != GRAPH_SHA256:
    raise SystemExit(f"INPUT DRIFT: {GRAPH} sha256 {_h[:16]}... != pinned "
                     f"{GRAPH_SHA256[:16]}.... This cell supersedes a stale "
                     "artifact and must not itself become one: re-pin "
                     "DELIBERATELY and re-run graph_staleness_census.")

CENTS_TOL, MAX_ORDER, MIN_IDX = 12.0, 24, 0.02
MAXEXTRA, TOPN = 3, 4
I_LIST = [0.9, 1.5, 2.0]
BAR = 0.50

INSTRUMENT = Model("comb vs product-lattice ranking, full pool", [
    Param("pool", DECLARED, value="all nodes with 1-2 enabled operators",
          why="the banked cell's own pool rule, unchanged; taking ALL of it is "
              "what turns the estimate into a census"),
    Param("index", TESTED, sweep=I_LIST,
          why="C3 recomputes the ranking at each FIXED index because the model "
              "gap's size varies strongly with it (omitted energy 12%->90%), so "
              "a pooled answer could be carried by one index alone"),
    Param("cents_tol", DECLARED, value=CENTS_TOL,
          why="Coherence.h's own binning width; changing it would compare a "
              "different pair of models"),
    Param("max_order", DECLARED, value=MAX_ORDER,
          why="the comb model's Bessel order cap, as shipped"),
    Param("graph_sha256", DECLARED, value=GRAPH_SHA256[:16] + "...",
          why="pinned and fail-closed. The artifact this supersedes was stale "
              "precisely because it named its input by path"),
])

_pc = {}


def walk(path):                                        # VERBATIM
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


def _shared(bins, total):                              # VERBATIM
    if total <= 0:
        return 0.0
    return sum(be for be, mk in bins.values() if mk and (mk & (mk - 1))) / total


def comb_score(ops, cents):                            # VERBATIM
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


def lattice_score(ops, cents):                         # VERBATIM (amendment 1 form)
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


def tails(mx):                                         # VERBATIM
    out, cur = [], [""]
    for _ in range(mx):
        cur = [t + c for t in cur for c in "LR"]
        out += cur
    return out


TAILS = tails(MAXEXTRA)
G = json.load(gzip.open(GRAPH))
pool = [nd for nd in G["nodes"]
        if 1 <= sum(1 for o in nd["ops"] if o["enabled"]) <= 2]
print(f"census over the FULL pool: {len(pool)} nodes", flush=True)


def jaccard_for(cur, base, index_override=None):
    """Top-4 agreement between the comb ranking and the lattice ranking."""
    nidx = index_override
    if nidx is None:
        nidx = float(np.median([d for _, d in cur])) or 0.9
    ops_base = ([(r, index_override) for r, _ in cur] if index_override
                else list(cur))
    scored = []
    for t in TAILS:
        cr = walk(base + t)
        if any(abs(float(cr) - float(r)) < 1e-9 for r, _ in cur):
            continue
        ops = ops_base + [(cr, nidx)]
        c = comb_score(ops, CENTS_TOL)
        L = lattice_score(ops, CENTS_TOL)
        if L is None:
            continue
        scored.append((c, L, base + t))
    if len(scored) < TOPN:
        return None
    su = {p for _, _, p in sorted(scored, key=lambda x: -x[0])[:TOPN]}
    sl = {p for _, _, p in sorted(scored, key=lambda x: -x[1])[:TOPN]}
    return len(su & sl) / len(su | sl)


jac, per_I, shared_k = [], {I: [] for I in I_LIST}, {}
for n, nd in enumerate(pool):
    cur = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    cur = [(r, d) for r, d in cur if r > 0]
    if not cur:
        continue
    base = next(o["path"] for o in nd["ops"] if o["enabled"])
    j = jaccard_for(cur, base)
    if j is None:
        continue
    jac.append(j)
    k = round(4 * j / (1 + j))                      # J = k/(8-k)  ->  k
    shared_k[k] = shared_k.get(k, 0) + 1
    for I in I_LIST:
        ji = jaccard_for(cur, base, index_override=I)
        if ji is not None:
            per_I[I].append(ji)
    if (n + 1) % 1000 == 0:
        print(f"  {n + 1}/{len(pool)} nodes, {len(jac)} scored", flush=True)

mean_j = float(np.mean(jac))
se = float(np.std(jac, ddof=1) / np.sqrt(len(jac)))
hw = 1.96 * se
means_I = {I: (float(np.mean(v)) if v else 0.0) for I, v in per_I.items()}

# ---- P1: the analytic, graph-INDEPENDENT tie to the banked cell ----
bank = json.load(open(os.path.join(HERE, "brocot_coherence_model.json")))
mism = 0
for I in I_LIST:
    want = bank["omitted_energy"][str(I)]
    got = (1.0 - float(jv(0, I)) ** 2) ** 2
    if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
        mism += 1
P1 = Bar("analytic-quantity mismatches vs the banked cell", 0.5, direction="le",
         floor=0, ceiling=3,
         why="omitted cross-partial energy at 3 indices; a count of "
             "disagreements, 0 to 3")
p1 = P1.score(mism)

P2 = Bar("scored cases", 6000, floor=0, ceiling=len(pool),
         why=f"a count over the {len(pool)}-node pool; below 6000 this is a "
             "sample with an unstated selection rule, not a census")
p2 = P2.score(len(jac))

C1 = Bar("population mean Jaccard", BAR, floor=0.0, ceiling=1.0,
         why="a Jaccard index lies in [0,1]; 0.50 sits between 'share 2 of 4' "
             "(0.333) and 'share 3 of 4' (0.600)")
c1 = C1.score(mean_j)

C2 = Bar("mean Jaccard minus 0.50, in 95% half-widths", 1.0,
         floor=-100.0, ceiling=100.0,
         why="a signed distance from the bar in units of its own interval; "
             "negative means below the bar")
c2 = C2.score((mean_j - BAR) / hw if hw > 0 else 0.0)

n_idx_clear = sum(1 for I in I_LIST if means_I[I] > BAR)
C3 = Bar("fixed indices where the mean clears 0.50", 2.5, floor=0, ceiling=3,
         why="a count over the 3 swept indices")
c3 = C3.score(n_idx_clear)

print(INSTRUMENT.report())
print(f"\nscored {len(jac)} of {len(pool)} pool nodes")
print(f"  population mean Jaccard {mean_j:.6f}  (SE {se:.6f}, 95% "
      f"[{mean_j - hw:.6f}, {mean_j + hw:.6f}])")
print(f"  banked (stale, 140 cases): 0.517075   |  same generator, current "
      f"graph, 140 cases: 0.530884")
print(f"\n  top-4 members shared: " + ", ".join(
    f"{k}:{v} ({100.0 * v / len(jac):.1f}%)" for k, v in sorted(shared_k.items())))
print(f"\n  by fixed index: " + ", ".join(
    f"I={I}: {means_I[I]:.4f}" for I in I_LIST))
print()
for b, v, f in ((P1, mism, "{:.0f}"), (P2, len(jac), "{:.0f}"),
                (C1, mean_j, "{:.6f}"),
                (C2, (mean_j - BAR) / hw if hw > 0 else 0.0, "{:.2f}"),
                (C3, n_idx_clear, "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="the scorers are the banked cell's"),
             Arm.from_bar(p2, PREM_ROLE,
                          claim="this is a census of the pool, not a sample"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="the two rankings agree on more than half"),
             Arm.from_bar(c2, MECH_ROLE,
                          claim="and clear of the bar by more than its own "
                                "interval, so it is not a boundary call"),
             Arm.from_bar(c3, RES_ROLE,
                          claim="at every fixed index, so pooling is not hiding "
                                "a reversal")],
            holds="RANKING_EFFECT_RESOLVED_MODEL_GAP_IS_DOCUMENTATION_ONLY",
            fails="RANKING_EFFECT_STILL_UNRESOLVED")
print(f"\nVERDICT: {v['citation']}")

with redpath("pool nodes scored on both models", expect_min=5000) as rp:
    rp.observed(len(jac))

json.dump(dict(
    graph=os.path.basename(GRAPH), graph_sha256=GRAPH_SHA256,
    pool_size=len(pool), n_cases=len(jac),
    mean_jaccard=mean_j, jaccard_se=se, jaccard_ci=[mean_j - hw, mean_j + hw],
    bar=BAR, excess_in_halfwidths=(mean_j - BAR) / hw if hw > 0 else 0.0,
    shared_top4_distribution=shared_k,
    mean_by_fixed_index={str(I): means_I[I] for I in I_LIST},
    n_indices_clearing=n_idx_clear,
    supersedes=dict(cell="brocot_coherence_model.json M3",
                    banked_value=bank["mean_jaccard"],
                    banked_n=bank["n_cases"],
                    why="that artifact is stale against the 2026-08-31 graph "
                        "regeneration (graph_staleness_census: 17 of 44 numeric "
                        "fields move, mean_jaccard 0.5171 -> 0.5309), and its "
                        "interval spanned the bar"),
    prior_look="0.5171 banked and 0.5309 on the current graph at n=140 were both "
               "known before sealing; C1 is stated directionally for that reason",
    bars={s["name"]: s for s in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="supersedes M3 of brocot_coherence_model on the pinned current graph; "
          "does not re-open M1/M2/M4",
    verdict=v["head"], composed=v),
    open(os.path.join(HERE, "brocot_coherence_ranking_census.json"), "w"), indent=1)
print("\nwrote brocot_coherence_ranking_census.json")
