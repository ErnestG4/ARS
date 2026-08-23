"""CERTIFY R2 — route every label literal in the population through the table.

R2 constraint (ii): the translation table must be DATA A CERTIFIER CONSUMES, not
prose in a dict. Audited 2026-08-23: nothing consumed it. `LABEL_TRANSLATION` and
`to_canonical` had zero importers outside the module that defines them, so the
constraint was encoded as its own violation — a table stored, never read.

This is the consumer, and it can run BEFORE migration because the thing it
certifies is a property of the population as it stands today: every label literal
at every one of the 20 decision sites must translate, and every entry in the
table must correspond to something the population actually says.

BOTH DIRECTIONS, deliberately:
  UNMAPPED   — a spelling in the code with no entry. The table is incomplete, and
               migration would silently drop or mistranslate a banked label.
  DEAD ENTRY — an entry no site uses. Not an error, but reported: an unexercised
               row is a row whose correctness nothing has ever tested, and the
               arc's own base rate for unexercised things is poor.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from c3_rulings import (LABEL_TRANSLATION, CANONICAL_LABELS, to_canonical,   # noqa: E402
                        check_no_altered_referent, RulingViolation)
from redpath import redpath   # noqa: E402

INV = json.load(open(f"{HERE}/c3_inline_divergences.json"))

check_no_altered_referent()

population = {}
for r in INV["rows"]:
    for lab in r["labels"]:
        population.setdefault(lab, []).append(f"{r['path']}:{r['line']}")

unmapped, translated = {}, {}
for lab, where in sorted(population.items()):
    try:
        translated[lab] = to_canonical(lab)
    except RulingViolation:
        unmapped[lab] = where

dead = sorted(set(LABEL_TRANSLATION) - set(population))

print(f"label literals in the population: {len(population)} distinct, "
      f"across {len(INV['rows'])} decision sites\n")
print(f"{'legacy':10s} {'canonical':10s} {'sites':>6s}")
for lab in sorted(translated):
    print(f"  {lab:10s} {translated[lab]:10s} {len(population[lab]):>4d}")

if unmapped:
    print("\nUNMAPPED — a spelling the code uses and the table does not know:")
    for lab, where in unmapped.items():
        print(f"  {lab!r} at {', '.join(where[:4])}")

print(f"\nDEAD ENTRIES (in the table, unused by any site): {dead or 'none'}")
print("  a dead entry is not an error, but nothing has ever exercised it")

# every translated label must land in the canonical set
bad = {k: v for k, v in translated.items() if v not in CANONICAL_LABELS}

# NON-VACUITY: the population is known to hold three distinct vocabularies, so a
# certifier that finds fewer than three label spellings is not reading the
# population it claims to certify.
with redpath("distinct label spellings routed through the table", expect_min=3) as rp:
    rp.observed(len(translated))

if unmapped or bad:
    print("\nR2_CERTIFY: FAIL")
    sys.exit(1)

print(f"\nR2_CERTIFIED — {len(translated)} distinct spellings across "
      f"{sum(len(v) for v in population.values())} label occurrences all translate "
      f"into {CANONICAL_LABELS}. The table is consumed, which is what "
      "constraint (ii) requires of it.")
