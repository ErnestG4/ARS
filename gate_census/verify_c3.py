"""Board checker for the C3 arc. Re-derives, it does not restate.

WHAT WOULD TURN THIS RED — named up front, because a checker whose failure mode
nobody can state is a checker nobody has red-pathed:

  (a) the inventory or the sweep table changes and the reconciliation no longer
      closes -> countrecon raises. THIS IS THE POINT OF THE ROW: an edit to
      either instrument that leaves the counts unexplained is the exact defect
      the arc was built on, and it must not be able to land quietly again.
  (b) c3_inline_divergences.json drifts from what the sealed generator produces.
  (c) the D2 detector stops separating printed-only from compared, so
      COMPUTED_UNUSED at the newly visible sites loses its warrant.
  (d) any ruling in c3_rulings.py stops refusing its own violation.

NOT CHECKED HERE, deliberately: whether migration is authorised. That would be a
row asserting `migration_may_begin()` raises -- true today, and it must become
false the moment R3 baselines are captured. A row that has to be deleted to make
progress is a row people learn to delete, and this repo has already recorded what
a permanently-red row is worth: nothing. The ordering condition is enforced at
the CALL SITE by the function itself, which is where it can actually stop work.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

CHECKS = []


def run(label, script):
    p = subprocess.run([PY, os.path.join(HERE, script)],
                       capture_output=True, text=True, cwd=ROOT)
    CHECKS.append((label, p.returncode == 0,
                   "" if p.returncode == 0 else
                   (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))
    return p


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# (b) inventory reproducibility, and (a) reconciliation closure
inv = os.path.join(HERE, "c3_inline_divergences.json")
rec = os.path.join(HERE, "c3_sweep_reconciliation.json")
before = sha(inv), sha(rec)
banked = json.load(open(rec))          # BANKED content, read before regeneration
run("inventory regenerates identically", "c3_inline_inventory.py")
run("sweep reconciliation closes", "c3_sweep_reconciliation.py")
after = sha(inv), sha(rec)
CHECKS.append(("banked inventory + reconciliation bit-identical",
               before == after,
               "" if before == after else "regenerated output differs from banked"))

# (c) detector still discriminates
run("D2 certified on the nearest confusable", "c3_certify_d2.py")

# (d) rulings still refuse their own violations
run("C3 rulings refuse their violations", "c3_rulings.py")
p = subprocess.run([PY, os.path.join(ROOT, "countrecon.py")],
                   capture_output=True, text=True, cwd=ROOT)
CHECKS.append(("countrecon fires on both historical shapes", p.returncode == 0,
               "" if p.returncode == 0 else "self-test failed"))

# content, not schema: the unswept unit must still be named
r = banked          # the banked object, not the freshly regenerated one
unswept = {f"{u['path']}:{u['line']}" for u in r["unswept"]}
CHECKS.append(("run_analytical_nns.py:249 still named as unswept",
               "run_analytical_nns.py:249" in unswept,
               "" if "run_analytical_nns.py:249" in unswept else f"got {unswept}"))
CHECKS.append(("denominator recorded as the def-extractable stratum",
               r["denominator_restatement"]["denominator_is"]
               == "distinct def-extractable implementations"
               and r["denominator_restatement"]["retro_scored"] is False,
               "" if (r["denominator_restatement"]["denominator_is"]
                      == "distinct def-extractable implementations"
                      and r["denominator_restatement"]["retro_scored"] is False)
               else "denominator restatement altered"))

print("C3 arc verification\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")
if bad:
    print("\nVERIFY_C3: FAIL")
    sys.exit(1)
print("\nVERIFY_C3: PASS — inventory reproduces, counts reconcile, D2 discriminates, "
      "rulings refuse.")
