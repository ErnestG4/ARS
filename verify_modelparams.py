"""Board row for the instrument-parameter obligation.

WHAT TURNS THIS RED:
  (a) modelparams.py stops refusing an unclassified parameter, a one-point
      TESTED sweep, a DECLARED without its value, an undefended constant, or an
      empty model.
  (b) the HISTORICAL SITE stops carrying its instrument seal.
      brocot_masked_horizon is the cell that motivated this: it sealed its
      predictions against the margin and let sigma ride in unlisted, and sigma
      turned out to matter more. If its artifact loses `instrument`, or that
      block stops covering the two parameters whose sensitivity was actually
      measured, the defect has been silently reverted.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
CHECKS = []

p = subprocess.run([PY, os.path.join(HERE, "modelparams.py")],
                   capture_output=True, text=True, cwd=HERE)
CHECKS.append(("modelparams refuses an unclassified or unswept parameter",
               p.returncode == 0 and "MODELPARAMS_SELF_TEST_PASS" in p.stdout,
               (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))

ART = os.path.join(HERE, "cross_substrate", "brocot_masked_horizon.json")
if not os.path.exists(ART):
    CHECKS.append(("brocot_masked_horizon.json present", False, "absent"))
else:
    d = json.load(open(ART))
    inst = d.get("instrument") or {}
    names = {q["name"] for q in inst.get("params", [])}
    CHECKS.append(("the historical site carries an instrument seal",
                   bool(inst), "no `instrument` block in the artifact"))
    CHECKS.append(("it names the parameter that escaped (sigma_scale)",
                   "sigma_scale" in names,
                   f"params listed: {sorted(names)}"))
    tested = {q["name"] for q in inst.get("params", []) if q["kind"] == "TESTED"}
    CHECKS.append(("margin and sigma are both TESTED, not DECLARED",
                   {"margin_db", "sigma_scale"} <= tested,
                   f"TESTED: {sorted(tested)} — the two whose sensitivity was "
                   "measured must not be downgraded to DECLARED"))

print("instrument-parameter guard\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")
if bad:
    print("\nVERIFY_MODELPARAMS: FAIL")
    sys.exit(1)
print("\nVERIFY_MODELPARAMS: PASS — a criterion is only as sealed as the "
      "instrument that evaluates it, and the instrument is enumerated.")
