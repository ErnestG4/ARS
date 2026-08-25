"""Board row for the reachable-bar guard.

WHAT TURNS THIS RED:
  (a) reachable.py stops refusing the real inert bar, or stops requiring a
      stated range or a defended `why` — the guard going inert, which for a
      guard about inertness would be a particularly poor joke.
  (b) the HISTORICAL SITE stops carrying its power fields: if
      brocot_above_horizon.json loses `power.H2_span_ceiling`, or scores H2 as
      MISSED again rather than INAPPLICABLE_UNPOWERED, the defect this guard
      exists for has been silently reverted.
  (c) the ceiling recorded there stops agreeing with the node set it claims to
      bound. The span ceiling is exactly recomputable from the artifact's own
      rows; if the banked one and the recomputed one part company, one of them
      is wrong and the row says so. This check has already earned itself once:
      the first ceiling was defended with Dirichlet's theorem, which bounds the
      wrong coordinate for this box, and was wrong by 14%.

(c) is the part a schema check would miss. A `power` block that is present and
wrong is worse than one that is absent, because it looks discharged.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
CHECKS = []

# (a) the guard still refuses — run its own red paths
p = subprocess.run([PY, os.path.join(HERE, "reachable.py")],
                   capture_output=True, text=True, cwd=HERE)
CHECKS.append(("reachable.py still refuses an inert bar and an unstated range",
               p.returncode == 0 and "REACHABLE_SELF_TEST_PASS" in p.stdout,
               "" if p.returncode == 0 else
               (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))

# (b) + (c) the historical site still carries honest power, and it re-derives
ART = os.path.join(HERE, "cross_substrate", "brocot_above_horizon.json")
if not os.path.exists(ART):
    CHECKS.append(("brocot_above_horizon.json present", False, "artifact missing"))
else:
    d = json.load(open(ART))
    pw = d.get("power", {})
    CHECKS.append(("brocot_above_horizon records H2's reachable ceiling",
                   "H2_span_ceiling" in pw,
                   "" if "H2_span_ceiling" in pw else "power.H2_span_ceiling absent"))
    CHECKS.append(("H2 is scored INAPPLICABLE_UNPOWERED, not MISSED",
                   pw.get("H2_score") == "INAPPLICABLE_UNPOWERED",
                   f"H2_score = {pw.get('H2_score')!r}"))
    # (c) re-derive the ceiling from the artifact's own rows. The ceiling is a
    # property of the fixed node set, so it is exactly recomputable — and this
    # is the check that caught the FIRST ceiling, which was defended by
    # Dirichlet's theorem and was wrong by 14%.
    g = [r["gap"] for r in d["rows"] if r["above"]]
    want = (max(g) / min(g)) if g and min(g) > 0 else None
    got = pw.get("H2_span_ceiling")
    CHECKS.append(("the banked ceiling re-derives as max/min gap over the node set",
                   want is not None and got is not None and abs(want - got) < 1e-12,
                   f"banked {got!r} vs recomputed {want!r}"))
    CHECKS.append(("the sealed lattice verdict is reported unchanged",
                   d.get("verdict") == "NOT_DIFFERENTIATED",
                   f"verdict = {d.get('verdict')!r} — the seal must not be rewritten"))
    CHECKS.append(("the amended reading is recorded alongside it",
                   bool(d.get("verdict_amended")),
                   "verdict_amended absent"))

print("reachable-bar guard\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")

if bad:
    print("\nVERIFY_REACHABLE_BAR: FAIL")
    sys.exit(1)
print("\nVERIFY_REACHABLE_BAR: PASS — the guard refuses an unreachable bar, and "
      "the site that motivated it still records its power honestly.")
