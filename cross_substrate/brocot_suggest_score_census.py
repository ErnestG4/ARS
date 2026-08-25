"""DOES THE SHIPPED RANKING INHERIT THE DEFECT? Coherence.h's score, censused.

COMMITTED GENERATOR of cross_substrate/brocot_suggest_score_census.json.
Predictions sealed here, before any output exists.

THE EXPLICIT IOU
----------------
`brocot_suggest_census` measured CoherenceSuggest's stated criterion and found
it false at 97.5% of enumerated candidates (99.7-100% in the near-unity regime).
It deliberately did NOT call `Coherence.h`'s score, and recorded that limit: the
docstring's justification is false, but whether the RANKING a user sees inherits
that is a separate question. This is that question.

WHY IT MIGHT NOT INHERIT, WHICH IS WHY IT NEEDS MEASURING RATHER THAN ASSUMING
-------------------------------------------------------------------------------
The horizon governs EXACT coincidence. `Coherence.h` does not test exact
coincidence: it bins partials by `llround(1200*log2(nu) / centsTolerance)` with
centsTolerance = 12, and counts energy landing in a bin touched by two or more
operators. Twelve cents at a 220 Hz partial is about 1.5 Hz — a slow BEAT, not
a fusion. So the score may be measuring near-coincidence, which the horizon says
nothing about, and the ranking could be perfectly sound while its stated
justification is false.

It could also be the opposite: if the shared energy is dominated by partials
that are EXACTLY equal, the score is an exact-coincidence detector wearing a
tolerance, and the horizon critique reaches all the way to the topN.

That is a measurable difference, and it is the whole question. Ratios here are
exact rationals, so nu = 1 + m*r is an exact rational and "exactly shared" is
decidable, not approximate.

NOTE ON A BINNING WEAKNESS, recorded because it bears on interpretation: the
score bins by ROUNDING to a grid, not by a tolerance window. Two partials 1 cent
apart that straddle a grid boundary land in different bins and are not counted
as shared, while two partials 11 cents apart inside one bin are. This is the
engine's behaviour and is reproduced faithfully here rather than corrected.

HEAD NAMING, per the limit recorded in verdictlattice: the heads below are named
for WHAT THE ARMS TEST (does the ranking depend on exact coincidence) and not
for a conclusion about blame.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ C1  THE RECOMMENDATIONS DO NOT FUSE — fewer than 50% of top-1 suggestions    ║
║     are horizon-reachable against their base. This is the direct read of     ║
║     whether the topN a user sees consists of pairs that can coincide.        ║
║ C2  THE SCORE IS NOT AN EXACT-COINCIDENCE DETECTOR — less than 50% of the    ║
║     energy the score counts as SHARED comes from exactly-equal partials.     ║
║     THIS IS THE ARM THAT DECIDES BLAME. If it holds, the score measures      ║
║     near-coincidence, the horizon does not govern it, and the ranking is     ║
║     exonerated whatever C1 says. If it misses, the score is an exact         ║
║     detector and C1's rate is a defect rate.                                 ║
║ C3  A HORIZON FILTER WOULD CHANGE WHAT IS SHOWN — mean Jaccard overlap       ║
║     between the shipped top-4 and a horizon-filtered top-4 is at most 0.5.   ║
║     If the two agree, no repair is warranted regardless of C1 and C2.        ║
║                                                                              ║
║ THE THREE ARMS ARE DELIBERATELY NOT REDUNDANT. C1 says what is shown, C2     ║
║ says whether the horizon has jurisdiction over it, C3 says whether a repair  ║
║ would change anything. Any two can hold with the third failing, and each     ║
║ combination writes a different sentence in the docstring.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import gzip
import json
import os
import sys
from fractions import Fraction
from math import ceil, gcd, log2

import numpy as np
from scipy.special import jv

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
SEED, N_NODES = 20260825, 300
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


def score(ops):
    """Faithful reproduction of Coherence.h::score, plus an exactness split.

    ops: list of (ratio as Fraction, index float). Returns
    (coherence, shared_energy, exactly_shared_energy)."""
    active = [(r, I) for r, I in ops if I > MIN_IDX and r > 0]
    if not 2 <= len(active) <= 63:
        return 0.0, 0.0, 0.0
    bins = {}
    total = 0.0
    for k, (r0, I) in enumerate(active):
        order = max(1, min(int(ceil(I)) + 4, MAX_ORDER))
        for m in range(1, order + 1):
            w = float(jv(m, I))
            e = w * w
            if e <= 0.0:
                continue
            for nu_x in (1 + m * r0, abs(1 - m * r0)):     # exact Fractions
                nu = float(nu_x)
                if nu <= 1.0e-4:
                    continue
                total += e
                key = int(round(1200.0 * log2(nu) / CENTS_TOL))
                b = bins.setdefault(key, [0.0, 0, {}])
                b[0] += e
                b[1] |= 1 << k
                b[2].setdefault(nu_x, [0.0, 0])
                b[2][nu_x][0] += e
                b[2][nu_x][1] |= 1 << k
    if total <= 0.0:
        return 0.0, 0.0, 0.0
    shared = exact = 0.0
    for _, (be, mask, exacts) in bins.items():
        if mask and (mask & (mask - 1)):
            shared += be
            for _, (ee, emask) in exacts.items():
                if emask and (emask & (emask - 1)):
                    exact += ee
    return shared / total, shared, exact


def reachable(r_base, r_cand, I_base, I_cand):
    al = r_cand / r_base
    return (al.numerator <= 2 * order_bound(I_base)
            and al.denominator <= 2 * order_bound(I_cand))


def tails(mx):
    out, cur = [], [""]
    for _ in range(mx):
        cur = [t + c for t in cur for c in "LR"]
        out += cur
    return out


TAILS = tails(MAXEXTRA)
G = json.load(gzip.open(GRAPH))
rng = np.random.default_rng(SEED)
cands_pool = [nd for nd in G["nodes"]
              if 1 <= sum(1 for o in nd["ops"] if o["enabled"]) <= 4
              and any(o["enabled"] for o in nd["ops"])]
sample = [cands_pool[i] for i in rng.choice(len(cands_pool), N_NODES,
                                            replace=False)]

top1_reach, jacc, sh_tot, ex_tot, n_cases = 0, [], 0.0, 0.0, 0
for nd in sample:
    cur = [(walk(o["path"]), o["depth"]) for o in nd["ops"] if o["enabled"]]
    cur = [(r, d) for r, d in cur if r > 0]
    if not cur:
        continue
    base_path = next(o["path"] for o in nd["ops"] if o["enabled"])
    base_r = walk(base_path)
    new_idx = float(np.median([d for _, d in cur])) or 0.9
    scored = []
    for t in TAILS:
        cr = walk(base_path + t)
        if any(abs(float(cr) - float(r)) < 1e-9 for r, _ in cur):
            continue
        coh, sh, ex = score(cur + [(cr, new_idx)])
        scored.append((coh, base_path + t, cr, sh, ex))
    if len(scored) < TOPN:
        continue
    scored.sort(key=lambda x: -x[0])
    n_cases += 1
    top = scored[:TOPN]
    top1_reach += reachable(base_r, top[0][2], new_idx, new_idx)
    for _, _, _, sh, ex in top:
        sh_tot += sh
        ex_tot += ex
    filt = [s for s in scored if reachable(base_r, s[2], new_idx, new_idx)]
    ftop = set(p for _, p, _, _, _ in filt[:TOPN])
    stop = set(p for _, p, _, _, _ in top)
    jacc.append(len(stop & ftop) / len(stop | ftop) if (stop | ftop) else 1.0)

c1 = top1_reach / n_cases
c2 = ex_tot / sh_tot if sh_tot else 0.0
c3 = float(np.mean(jacc))

C1 = Bar("top-1 suggestions that are horizon-reachable", 0.50, direction="le",
         floor=0.0, ceiling=1.0, why="a fraction of cases: 0 to 1")
C2 = Bar("shared energy that is EXACTLY coincident", 0.50, direction="le",
         floor=0.0, ceiling=1.0,
         why="exactly-shared energy is a subset of shared energy, so the "
             "ratio lies in [0,1]")
C3 = Bar("Jaccard(shipped top-4, horizon-filtered top-4)", 0.50, direction="le",
         floor=0.0, ceiling=1.0, why="a Jaccard index lies in [0,1]")
s1, s2, s3 = C1.score(c1), C2.score(c2), C3.score(c3)

print(f"{os.path.basename(GRAPH)}: {n_cases} suggestion cases "
      f"(seed {SEED}), {len(TAILS)} candidates each")
print(f"score reproduced from Coherence.h: {CENTS_TOL:.0f}-cent bins, "
      f"maxOrder {MAX_ORDER}, min index {MIN_IDX}\n")
print(f"top-1 horizon-reachable      {top1_reach}/{n_cases} = {c1:.1%}")
print(f"shared energy total          {sh_tot:.4f}")
print(f"  of which EXACTLY shared    {ex_tot:.4f} = {c2:.1%}")
print(f"mean Jaccard vs filtered     {c3:.3f}\n")
for b, v in ((C1, c1), (C2, c2), (C3, c3)):
    print("  " + b.line(v, "{:.1%}"))

v = compose([Arm.from_bar(s1, EX_ROLE, note="what the user is shown"),
             Arm.from_bar(s2, MECH_ROLE, note="does the horizon have jurisdiction"),
             Arm.from_bar(s3, RES_ROLE, note="would a filter change anything")],
            holds="RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE",
            fails="RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE")
print(f"\nVERDICT: {v['citation']}")
print(f"\n  C2 is the jurisdiction arm: {c2:.1%} of the energy the score counts")
if s2["met"]:
    print("  as shared comes from exactly-equal partials, so the score is")
    print("  measuring NEAR-coincidence inside a 12-cent bin. The horizon")
    print("  governs exact coincidence and therefore does not govern this")
    print("  ranking. The false docstring justified a sound instrument.")
else:
    print("  as shared comes from exactly-equal partials, so the score IS")
    print("  substantially an exact-coincidence detector and the horizon")
    print("  critique reaches the ranking, not only the docstring.")

ex = summarise("n_reachable_top1", [top1_reach], EXISTENCE)
with redpath("suggestion cases scored", expect_min=250) as rp:
    rp.observed(n_cases)

json.dump(dict(graph=os.path.basename(GRAPH), seed=SEED, n_cases=n_cases,
               cents_tolerance=CENTS_TOL, max_order=MAX_ORDER,
               maxextra=MAXEXTRA, topn=TOPN,
               top1_reachable_rate=c1, exact_share_of_shared=c2,
               mean_jaccard=c3,
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_suggest_score_census.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_suggest_score_census.json")
