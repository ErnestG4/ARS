"""Board row for the verdict-lattice guard.

WHAT TURNS THIS RED:
  (a) verdictlattice.py stops refusing a roleless arm, a lattice with no
      EXISTENCE arm, or a MECHANISM miss that negates the head — OR stops
      NEGATING on an EXISTENCE miss. That last one was unguarded until
      2026-08-25: adversarial review replaced the head computation with
      `head = holds`, so the negative label became unreachable, and this board
      returned 8/8 PASS. Every check tested the positive direction. It is
      checked directly below, not only via the module's self-test, because a
      broken module could in principle also break its own self-test.
  (b) either HISTORICAL SITE stops carrying both labels. The discipline is that
      a mislabelled seal is REPORTED unchanged and corrected beside itself; a
      site that keeps only one of the two has either rewritten its seal or
      dropped the correction, and both are the failure this row is for.
  (c) the composed head stops re-deriving from the banked arm scores. This is
      the check a schema cannot make: a `composed` block that is present and
      disagrees with its own bars looks discharged and is not.
  (d) the composed block loses its CITATION. A head alone is a disposition and
      says nothing about which way the arms went — the mirror of (a)'s defect,
      committed in this arc when "the morph question is closed" was reported in
      place of "L2 = 0.985x against a bar of 3x". The quotable form carries the
      numbers or the guard is only covering one direction.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
sys.path.insert(0, HERE)
from verdictlattice import Arm, compose, EXISTENCE, RESOLUTION   # noqa: E402

CHECKS = []

# (a) the negation path, checked HERE and not only in the module's self-test
_neg = compose([Arm("holds", EXISTENCE, False)], holds="H", fails="N")
_mix = compose([Arm("a", EXISTENCE, True), Arm("b", EXISTENCE, False)],
               holds="H", fails="N")
CHECKS.append(("an EXISTENCE miss produces the negative head",
               _neg["head"] == "N" and _mix["head"] == "N",
               f"single-miss head {_neg['head']!r}, mixed head {_mix['head']!r} "
               "— compose() can no longer reach its own negative label"))

p = subprocess.run([PY, os.path.join(HERE, "verdictlattice.py")],
                   capture_output=True, text=True, cwd=HERE)
CHECKS.append(("verdictlattice.py still refuses a roleless arm and a headless lattice",
               p.returncode == 0 and "VERDICTLATTICE_SELF_TEST_PASS" in p.stdout,
               "" if p.returncode == 0 else
               (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))

# (b) both historical sites carry the sealed label AND its correction
SITES = {
    "cross_substrate/brocot_above_horizon.json":
        ("NOT_DIFFERENTIATED", "verdict_amended"),
    "cross_substrate/brocot_above_horizon_parent.json":
        ("PARENT_LABEL_DOES_NOT_HOLD", "composed"),
}
for rel, (sealed, corrected) in SITES.items():
    path = os.path.join(HERE, rel)
    if not os.path.exists(path):
        CHECKS.append((f"{os.path.basename(rel)} present", False, "artifact missing"))
        continue
    d = json.load(open(path))
    CHECKS.append((f"{os.path.basename(rel)} reports its sealed label unchanged",
                   d.get("verdict") == sealed,
                   f"verdict = {d.get('verdict')!r}, expected {sealed!r}"))
    CHECKS.append((f"{os.path.basename(rel)} carries the correction beside it",
                   bool(d.get(corrected)),
                   f"'{corrected}' absent — a seal corrected by deletion is not corrected"))

# (c) the parent site's composed head re-derives from its own banked bars
path = os.path.join(HERE, "cross_substrate", "brocot_above_horizon_parent.json")
if os.path.exists(path):
    d = json.load(open(path))
    bars = d.get("bars", {})
    try:
        ex = [Arm(k, EXISTENCE, v["met"]) for k, v in bars.items()
              if k in ("parent is below the horizon",
                       "parent is a Stern-Brocot ancestor")]
        res = [Arm(k, RESOLUTION, v["met"]) for k, v in bars.items()
               if k not in ("parent is below the horizon",
                            "parent is a Stern-Brocot ancestor")]
        head = compose(ex + res, holds="HEARD_AS_A_DETUNED_PARENT",
                       fails="PARENT_LABEL_DOES_NOT_HOLD")["head"]
    except Exception as e:                                   # noqa: BLE001
        head = f"<{e}>"
    banked = (d.get("composed") or {}).get("head")
    CHECKS.append(("the composed head re-derives from the banked bar scores",
                   head == banked, f"recomputed {head!r} vs banked {banked!r}"))
    # the quotable form must carry its arms' values, not just the head
    cited = (d.get("composed") or {}).get("citation")
    CHECKS.append(("the composed verdict carries a citation, not just a head",
                   bool(cited) and cited != banked,
                   f"citation = {cited!r} — a disposition standing in for a "
                   "finding is the mirror of the defect this guard exists for"))

    # and the head must NOT be driven by the resolution arms
    CHECKS.append(("no EXISTENCE arm missed, so the head is positive",
                   banked == "HEARD_AS_A_DETUNED_PARENT",
                   f"head = {banked!r} while both existence arms read 100%"))

print("verdict-lattice guard\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")

if bad:
    print("\nVERIFY_VERDICT_LATTICE: FAIL")
    sys.exit(1)
print("\nVERIFY_VERDICT_LATTICE: PASS — a resolution arm cannot negate an "
      "existence result, and both mislabelled seals still report themselves "
      "unchanged with their corrections beside them.")
