"""Board row for the exposure-window audit.

WHAT TURNS THIS RED: `exposure_audit.json` names an exposure — a cell that, as
it stood at the baseline commit, no longer constructs under the hardened guards
— which is not disclosed in `exposure_audit.py`'s DISCLOSED map.

WHY THE CHECK AND THE AUDIT ARE SEPARATE. Regenerating the audit reconstructs
nine cells at a past commit and re-runs them against the current guards; that is
minutes to an hour and has no business on every board run. This row is the cheap
half: it reads the banked result and enforces the rule that an exposure must be
disclosed with where its output travelled. Run `python3 exposure_audit.py` to
regenerate after any guard repair — the audit is a TOOL, this is the tripwire.

The rule it enforces: repairing a cell does not discharge what that cell
certified while the guard was broken. Those are different facts and only one of
them is fixed by an edit.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "exposure_audit.json")
CHECKS = []

if not os.path.exists(ART):
    print("exposure-window audit\n\n  FAIL  exposure_audit.json absent — run "
          "`python3 exposure_audit.py`\n\nVERIFY_EXPOSURE_WINDOW: FAIL")
    sys.exit(1)

d = json.load(open(ART))
refused = [r["cell"] for r in d["rows"] if r["state"] == "REFUSED"]
disclosed = d.get("disclosed", {})
undisclosed = [c for c in refused if c not in disclosed]

CHECKS.append(("every exposure is disclosed with where its output travelled",
               not undisclosed, f"undisclosed: {undisclosed}"))
CHECKS.append(("the audit records a baseline commit it was run against",
               bool(d.get("baseline")), "no baseline recorded"))
CHECKS.append(("no cell is unaccounted for",
               all(r["state"] in ("SURVIVES", "REFUSED", "NO-BASELINE")
                   for r in d["rows"]),
               "an unknown state appears in the audit"))

print(f"exposure-window audit (baseline {d.get('baseline')})\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
print(f"\n  {d.get('n_surviving')}/{len(d['rows'])} baseline cells survive the "
      f"hardened guards; {len(refused)} exposure(s), all disclosed"
      if not undisclosed else "")
for c in refused:
    print(f"      EXPOSED  {c}")

bad = [c for c in CHECKS if not c[1]]
if bad:
    print("\nVERIFY_EXPOSURE_WINDOW: FAIL")
    sys.exit(1)
print("\nVERIFY_EXPOSURE_WINDOW: PASS — repairing a cell does not discharge "
      "what it certified while the guard was broken, and every such case is "
      "named with where its output went.")
