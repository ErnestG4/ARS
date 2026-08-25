"""CENSUS BEFORE REPAIR: how often is CoherenceSuggest's criterion wrong?

COMMITTED GENERATOR of cross_substrate/brocot_suggest_census.json.
Predictions sealed here, before any output exists.

THE DEFECT CLASS, NAMED
------------------------
`source/audio/CoherenceSuggest.h` recommends prefix-EXTENSIONS of a base
Stern-Brocot path, on this stated ground:

    "Extensions share the base as an ancestor by construction — the structural
     fact behind the banked discovery (shared prefix => coincident sideband
     combs)."

The horizon theorem says that implication is FALSE in a specific regime. Sharing
a prefix says nothing about whether the pair's coincidence is REACHABLE: with
alpha = r_ext / r_base = p/q, a direct coincidence needs p <= 2B(I_base) and
q <= 2B(I_ext) (the asymmetric corollary, verified 4784/4784). An extension can
share five characters of path and still be silent, because extending the path
drives p and q up fast while the index — and therefore the horizon — sits where
the player left it.

And the engine is INDEX-BLIND on the base side: `suggestExtensions` takes
`newIndex` for the candidate and never consults the indices of `current`.

CENSUS, NOT REPAIR. The repair is one predicate. What is missing is the number
that says whether the repair matters, and it belongs in the changelog: "the
criterion is wrong" is a claim; "the criterion is wrong on X% of the candidates
the shipped engine enumerates at the instrument's own index" is a measurement.
This is the same move as the sweep — the defect class is named, so census it
before repairing, and the repair has a before.

SCOPE. This counts candidates the engine ENUMERATES (all L/R tails of length
1..maxExtra off each base, its exact candidate construction). It does not
reproduce the coherence score or the topN ranking, so it is a census of the
candidate POOL, not of what a user finally sees. Stated because the difference
matters: a pool rate is an upper bound on how often a shown suggestion is wrong.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ S1  The rate is NOT NEGLIGIBLE at the instrument's own index: at I = 0.9,    ║
║     more than 10% of enumerated candidate pairs share a prefix and are        ║
║     nonetheless above the horizon.                                           ║
║ S2  The rate FALLS as the index rises — the horizon moves out, so more        ║
║     candidates become reachable. Rate at I = 3.0 is below the rate at        ║
║     I = 0.9. This is the mechanism arm: if the rate does not move with I,    ║
║     the defect is not the horizon and the diagnosis is wrong.                ║
║ S3  It is worst where the engine reaches furthest: the rate at maxExtra = 3  ║
║     exceeds the rate at maxExtra = 1. Deeper extensions drive p, q up while  ║
║     the horizon stays put.                                                   ║
║                                                                              ║
║ S1 IS THE CHANGELOG NUMBER. If it misses, the criterion is wrong in          ║
║ principle and harmless in practice, the repair is a tidy-up rather than a    ║
║ correctness fix, and it should be described that way.                        ║
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
from existence import summarise, EXISTENCE                        # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import order_bound                 # noqa: E402

I_LIST = [0.9, 1.5, 2.0, 3.0]
MAXEXTRA = [1, 2, 3]                       # the engine's default is 3
BASE_LEN = range(1, 8)                     # base paths of length 1..7
NEAR_LO, NEAR_HI = Fraction(7, 10), Fraction(7, 5)   # the instrument's regime


def walk(path):
    ln, ld, hn, hd = 0, 1, 1, 0
    for c in path:
        mn, md = ln + hn, ld + hd
        if c == "L":
            hn, hd = mn, md
        else:
            ln, ld = mn, md
    return Fraction(ln + hn, ld + hd)


def paths(n):
    out = [""]
    for _ in range(n):
        out = [t + c for t in out for c in "LR"]
    return out


BASES = [p for n in BASE_LEN for p in paths(n)]


def reachable(r_base, r_ext, I_base, I_ext):
    """The asymmetric corollary, imported as the predicate the repair would use."""
    al = r_ext / r_base
    p, q = al.numerator, al.denominator
    return p <= 2 * order_bound(I_base) and q <= 2 * order_bound(I_ext)


rows = {}
for I in I_LIST:
    for mx in MAXEXTRA:
        tot = silent = n_tot = n_silent = 0
        for b in BASES:
            rb = walk(b)
            near = NEAR_LO <= rb <= NEAR_HI
            tails = [t for n in range(1, mx + 1) for t in paths(n)]
            for t in tails:
                re_ = walk(b + t)
                if re_ == rb:
                    continue                    # the engine skips duplicates
                bad = not reachable(rb, re_, I, I)
                tot += 1
                silent += bad
                if near:
                    n_tot += 1
                    n_silent += bad
        rows[(I, mx)] = dict(I=I, maxextra=mx, n=tot, silent=silent,
                             rate=silent / tot if tot else 0.0,
                             n_near=n_tot, silent_near=n_silent,
                             rate_near=n_silent / n_tot if n_tot else 0.0)

r_09 = rows[(0.9, 3)]["rate"]
r_30 = rows[(3.0, 3)]["rate"]
r_x1 = rows[(0.9, 1)]["rate"]
r_x3 = rows[(0.9, 3)]["rate"]

S1 = Bar("wrong-suggestion rate at I=0.9", 0.10, floor=0.0, ceiling=1.0,
         why="a fraction of enumerated candidates: 0 to 1 by construction")
S2 = Bar("rate at I=0.9 minus rate at I=3.0", 0.0, floor=-1.0, ceiling=1.0,
         why="a difference of two fractions each in [0,1]")
S3 = Bar("rate at maxExtra=3 minus at maxExtra=1", 0.0, floor=-1.0, ceiling=1.0,
         why="a difference of two fractions each in [0,1]")
s1, s2, s3 = S1.score(r_09), S2.score(r_09 - r_30), S3.score(r_x3 - r_x1)

print(f"bases: {len(BASES)} paths of length 1-5; the engine's own candidate "
      f"construction (all L/R tails of length 1..maxExtra)\n")
print(f"{'I':>5s} " + "".join(f"{'mx=' + str(m):>16s}" for m in MAXEXTRA))
for I in I_LIST:
    cells = "".join(f"{rows[(I, m)]['rate']:>9.1%}"
                    f" ({rows[(I, m)]['silent']:>4d})" for m in MAXEXTRA)
    print(f"{I:>5.1f} {cells}")
print("\n   cell = fraction of shared-prefix candidates that are ABOVE the "
      "horizon (count in brackets)")
print(f"\nNEAR-UNITY STRATUM — bases with ratio in [{float(NEAR_LO)}, "
      f"{float(NEAR_HI)}], reported not scored (amendment 1(ii)):")
print(f"{'I':>5s} " + "".join(f"{'mx=' + str(m):>16s}" for m in MAXEXTRA))
for I in I_LIST:
    cells = "".join(f"{rows[(I, m)]['rate_near']:>9.1%}"
                    f" ({rows[(I, m)]['silent_near']:>4d})" for m in MAXEXTRA)
    print(f"{I:>5.1f} {cells}")

print()
for b, v, f in ((S1, r_09, "{:.1%}"), (S2, r_09 - r_30, "{:+.1%}"),
                (S3, r_x3 - r_x1, "{:+.1%}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE, note="the changelog number"),
             Arm.from_bar(s2, MECH_ROLE, note="rate moves with the horizon"),
             Arm.from_bar(s3, RES_ROLE, note="worst where the engine reaches")],
            holds="CRITERION_WRONG_IN_PRACTICE",
            fails="CRITERION_WRONG_ONLY_IN_PRINCIPLE")
print(f"\nVERDICT: {v['citation']}")
if v["head"] == "CRITERION_WRONG_IN_PRACTICE":
    print(f"  At the instrument's own index, {r_09:.1%} of the candidates the")
    print("  shipped engine enumerates share a prefix and cannot coincide. The")
    print("  repair is a correctness fix and this is its before.")
else:
    print("  Wrong in principle, harmless in practice. The repair is a tidy-up")
    print("  and the changelog should say so.")

ex = summarise("n_silent_candidates", [rows[k]["silent"] for k in rows], EXISTENCE)
with redpath("candidate pairs censused", expect_min=20000) as rp:
    rp.observed(sum(r["n"] for r in rows.values()))

json.dump(dict(I_list=I_LIST, maxextra=MAXEXTRA, n_bases=len(BASES),
               rows=[dict(v) for v in rows.values()],
               rate_at_I09_mx3=r_09, rate_at_I30_mx3=r_30,
               rate_near_at_I09_mx3=rows[(0.9, 3)]["rate_near"],
               bars={s["name"]: s for s in (s1, s2, s3)},
               scope="candidate POOL, not the topN the user sees; a pool rate "
                     "is an upper bound on how often a shown suggestion is wrong",
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_suggest_census.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_suggest_census.json")
