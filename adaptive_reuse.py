"""Has this corpus been queried adaptively — and does sealing protect against it?

COMMITTED GENERATOR of adaptive_reuse.json.
Predictions sealed here, before any output exists.

THE QUESTION, AND WHY IT IS NOT RHETORICAL
------------------------------------------
Dwork, Feldman, Hardt, Pitassi, Reingold & Roth, "The reusable holdout:
Preserving validity in adaptive data analysis," Science 349(6248), 2015, show
that when an analyst's QUERIES DEPEND ON PRIOR ANSWERS FROM THE SAME DATA, the
classical guarantees fail — because those guarantees assume the analysis was
fixed before the data were seen. Naive holdout reuse degrades after a number of
queries LINEAR in the sample size; their Thresholdout mechanism, answering
through a differentially-private channel, buys validity for exponentially many.

This programme has run several hundred cells against a corpus that does not
change: banked coordinate files, a fixed list of Riemann zeros, fixed spike
trains. Every cell's design was informed by the cells before it. That is the
definition of adaptive data analysis, and it has never been named here.

THE DISTINCTION THAT DECIDES WHO IS EXPOSED
-------------------------------------------
Not every claim is at risk, and conflating the two would overstate the problem.

  CLAIMS ABOUT THE BANKED OBJECT ITSELF are immune. "Over 2306 candidate
  detunes, none returns the bystander spectrum to itself" is exact arithmetic
  about a specified finite set. Query it a thousand times adaptively; it stays
  true. There is no generalisation step for adaptivity to corrupt.

  CLAIMS THAT GENERALISE FROM THE CORPUS are exposed. "This substrate is
  GUE-class", "the ladder orders thus across substrates", "clustering is
  orthogonal to coupling" — each treats the banked data as a SAMPLE standing in
  for something larger, and each was reached after many prior looks at the same
  sample. That is exactly the regime Dwork addresses.

This repo already has the vocabulary for the distinction and has not connected
it: `marginal != class` and `sealing ⊥ coverage` are the same boundary seen from
inside.

AND THE POINT THAT MATTERS MOST: SEALING IS NOT A HOLDOUT.
A sealed cell fixes its analysis before seeing ITS OWN output. It does nothing
about the fact that the DECISION to run that cell — which substrate, which
coordinate, which threshold, which contrast — was informed by every previous
cell on the same corpus. Sealing addresses WITHIN-cell adaptivity. Dwork's
concern is ACROSS-cell adaptivity, and the two are orthogonal. A programme can
be scrupulously pre-registered cell by cell and still be, in aggregate, a long
adaptive query sequence against one fixed dataset.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the corpus really is reused at scale: the most-consulted data  ║
║     file is opened by at least 15 distinct generators. If nothing is reused, ║
║     adaptivity is not this programme's problem and nothing below matters.    ║
║                                                                              ║
║ E1  SEALING IS THE HOUSE HABIT — at least 30 cells carry sealed              ║
║     pre-registered predictions. This is the control the repo already has.    ║
║                                                                              ║
║ E2  HOLDOUT IS NOT — at most 6 artifacts show the blind/held-out pattern     ║
║     (a sealed prediction whose data was measured only afterwards). THIS IS   ║
║     THE CELL: if sealing is ubiquitous and holdout is rare, then the         ║
║     protection in place is the one that does not address adaptive reuse.     ║
║                                                                              ║
║ M1  MECHANISM — the two are separated by an order of magnitude: sealed       ║
║     cells outnumber held-out instances by at least 10x. That ratio is the    ║
║     quantitative form of "sealing is not a holdout".                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

WHAT THIS CELL DOES NOT CLAIM. Not that any specific banked result is wrong.
Adaptive analysis inflates the RATE of false discovery over a sequence; it does
not identify which member of the sequence is false, and this cell has no power
to do that either. Nor does it claim Dwork's mechanism is applicable —
Thresholdout needs a designated holdout and a privacy budget, and this programme
has neither. What transfers is the DIAGNOSIS and one cheap practice: for a claim
that generalises, hold a substrate or a range back and do not look at it until
the claim is sealed. The repo has done exactly that a handful of times, and
those instances are the model.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE, MECHANISM as MECH_ROLE)

SELF = {"./adaptive_reuse.py", "./adaptive_reuse.json"}


def files_matching(pattern, include="*.py"):
    r = subprocess.run(["grep", "-rlE", pattern, "--include=" + include, "."],
                       cwd=ROOT, capture_output=True, text=True)
    return [l for l in r.stdout.splitlines()
            if not l.startswith("./.git") and l not in SELF]


# --- P1: how many distinct generators OPEN each fixed data file?
# Counting a substring like "zeta" would count mentions; this counts references
# to an actual path, which is the closest cheap proxy for a read.
corpus = {}
for d, pat in (("data/odlyzko_zeros1.txt", r"odlyzko_zeros1"),
               ("data/odlyzko_zeros6.txt", r"odlyzko_zeros6"),
               ("zeros_1000.npy", r"zeros_1000"),
               ("zeros_2000.npy", r"zeros_2000")):
    corpus[d] = len(files_matching(pat))
for f in sorted(os.listdir(os.path.join(ROOT, "cross_substrate", "coordinates"))
                if os.path.isdir(os.path.join(ROOT, "cross_substrate",
                                              "coordinates")) else []):
    if f.endswith(".jsonl"):
        stem = f[:-6]
        n = len(files_matching(re.escape(stem)))
        if n >= 3:
            corpus["coordinates/" + f] = n
top = max(corpus.values()) if corpus else 0

# --- E1: cells carrying sealed pre-registered predictions
sealed = files_matching(r"SEALED PREDICTION|sealed here, before any output")
# --- E2: artifacts showing the blind / held-out pattern
blind = files_matching(r"BLIND|seal not opened|held-out|out-of-sample",
                       include="*.json")

print("adaptive reuse — has this corpus been queried adaptively?\n")
print(f"  {'most-consulted fixed data files':44s}")
for k, v in sorted(corpus.items(), key=lambda x: -x[1])[:8]:
    print(f"    {k:42s} opened by {v:3d} generators")
print(f"\n  cells carrying SEALED pre-registered predictions : {len(sealed)}")
print(f"  artifacts showing a BLIND / held-out measurement : {len(blind)}")
ratio = len(sealed) / max(len(blind), 1)
print(f"  ratio                                            : {ratio:.1f}x")

P1 = Bar("generators opening the most-consulted data file", 15,
         floor=0, ceiling=2000,
         why="a count of files; 0 is attainable if nothing is shared and the "
             "ceiling is every python file in the tree")
E1 = Bar("cells carrying sealed predictions", 30, floor=0, ceiling=2000,
         why="a count of files on the same scale")
E2 = Bar("artifacts showing a blind/held-out measurement", 6,
         direction="le", floor=0, ceiling=2000,
         why="a count on the same scale; a LARGE value would mean holdout is "
             "already the habit and this cell's concern is misplaced")
M1 = Bar("sealed-to-heldout ratio", 10.0, floor=0.0, ceiling=2000.0,
         why="a ratio of the two counts; 1.0 is 'the repo holds out as often "
             "as it seals' and is attainable")

sP, s1 = P1.score(top), E1.score(len(sealed))
s2, sM = E2.score(len(blind)), M1.score(ratio)
print()
for b, v, f in ((P1, top, "{:.0f}"), (E1, len(sealed), "{:.0f}"),
                (E2, len(blind), "{:.0f}"), (M1, ratio, "{:.1f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(sP, PRE_ROLE, claim="the corpus is reused at scale"),
             Arm.from_bar(s1, EX_ROLE, claim="sealing is the house habit"),
             Arm.from_bar(s2, EX_ROLE, claim="holdout is not"),
             Arm.from_bar(sM, MECH_ROLE,
                          claim="because sealing and holdout are different "
                                "protections and only one is practised")],
            holds="ACROSS_CELL_ADAPTIVITY_IS_UNADDRESSED",
            fails="HOLDOUT_PRACTICE_IS_ALREADY_IN_PLACE")
print(f"\nVERDICT: {v['citation']}")

with redpath("corpus files censused", expect_min=4) as rp:
    rp.observed(len(corpus))

json.dump(dict(corpus=corpus, top_reuse=top, n_sealed=len(sealed),
               n_blind=len(blind), ratio=ratio,
               sealed_examples=sorted(sealed)[:8],
               blind_examples=sorted(blind)[:8],
               anchor="Dwork, Feldman, Hardt, Pitassi, Reingold & Roth, "
                      "'The reusable holdout: Preserving validity in adaptive "
                      "data analysis', Science 349(6248), 2015",
               scope_note="claims ABOUT THE BANKED OBJECT are immune (exact "
                          "arithmetic over a specified finite set); claims that "
                          "GENERALISE from the corpus are exposed. Sealing "
                          "addresses within-cell adaptivity; Dwork's concern is "
                          "across-cell, and they are orthogonal.",
               bars={s["name"]: s for s in (sP, s1, s2, sM)},
               verdict=v["head"], composed=v),
          open(f"{ROOT}/adaptive_reuse.json", "w"), indent=1)
print("\nwritten -> adaptive_reuse.json")
