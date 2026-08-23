"""ONE VERDICT PER DECISION SITE, all 21 — SEALED_CRITERIA §6.1.

COMMITTED GENERATOR of overnight_2026_08_23/site_verdicts.json.

§6.1 requires "all 21 sites, each with exactly one verdict, and no site absent".
The def-site artifacts already satisfy that. The module-site artifacts do NOT:
they carry one verdict per SCRIPT, and three scripts hold five decision sites, so
five sites were sharing three verdicts. Under R4 the unit is the DECISION, and a
per-file verdict is exactly the collapse R4 was ruled to prevent — the arc's own
counting rule, not applied to the arc's own reporting.

A script-level CAPTURED does not transfer unchanged to each site it contains:

  * run_analytical_nns.py:184 has an OBSERVABLE_ABSENT component (its p-values),
    though its `best` does reach stdout;
  * run_analytical_nns.py:297 emits NO stdout at all — its only witness is a PNG
    hash, which reports THAT something changed and never WHAT.

So the per-site verdict is the script verdict QUALIFIED by that site's observable,
and the qualification is carried in the verdict rather than in a footnote.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from redpath import redpath      # noqa: E402
from countrecon import CountLedger   # noqa: E402

INV = json.load(open(f"{ROOT}/gate_census/c3_inline_divergences.json"))
MUT_DEF = json.load(open(f"{HERE}/mutations_def.json"))
BASE_MOD = json.load(open(f"{HERE}/baselines_module.json"))
MUT_MOD_PATH = f"{HERE}/mutations_module.json"
MUT_MOD = json.load(open(MUT_MOD_PATH)) if os.path.exists(MUT_MOD_PATH) else None

# Observable qualifications, from the module capture's own declarations.
QUALIFIED = {}
QUALIFIED.update({k: ("OBSERVABLE_ABSENT", v)
                  for k, v in BASE_MOD.get("observable_absent", {}).items()})
QUALIFIED.update({k: ("OBSERVABLE_IS_FIGURE_ONLY", v)
                  for k, v in BASE_MOD.get("observable_figure_only", {}).items()})

rows = {}
for r in INV["rows"]:
    key = f"{r['path']}:{r['line']}"
    if r["scope"] == "def":
        m = MUT_DEF["rows"].get(key, {})
        rows[key] = dict(scope="def", verdict=m.get("verdict", "NOT_ATTEMPTED"),
                         discrimination=f"{m.get('n_detected', 0)}/{m.get('n_applicable', 0)}"
                         " applicable attacks detected",
                         qualification=None, source="mutations_def.json")
    else:
        script = r["path"]
        base = BASE_MOD["scripts"].get(script, {})
        script_verdict = base.get("verdict", "NOT_ATTEMPTED")
        if MUT_MOD is None:
            disc = "NOT_ATTEMPTED — module mutation testing did not run"
            verdict = (script_verdict if script_verdict != "CAPTURED"
                       else "CAPTURED_UNATTACKED")
        else:
            mm = MUT_MOD["rows"].get(script, {})
            disc = (f"{mm.get('n_detected', 0)}/{mm.get('n_applicable', 0)}"
                    " applicable attacks detected (script-level)")
            verdict = mm.get("verdict", script_verdict)
        qual = QUALIFIED.get(key)
        rows[key] = dict(scope="module", verdict=verdict, discrimination=disc,
                         qualification=(qual[0] if qual else None),
                         qualification_reason=(qual[1] if qual else None),
                         source="baselines_module.json + mutations_module.json")

# A qualified site cannot carry an unqualified CAPTURED: the qualification IS the
# statement that part of it is unobserved.
for key, r in rows.items():
    if r.get("qualification") and r["verdict"].startswith("CAPTURED"):
        r["verdict"] = f"{r['verdict']}_{r['qualification']}"

led = CountLedger("decision sites with a verdict")
led.report("inventory.decision_sites", len(INV["rows"]))
led.report("site_verdicts.rows", len(rows))
led.report("def.rows", sum(1 for r in rows.values() if r["scope"] == "def"))
led.report("module.rows", sum(1 for r in rows.values() if r["scope"] == "module"))
led.explain("inventory.decision_sites", "site_verdicts.rows", 0,
            "every decision site in the inventory receives exactly one verdict here")
# The strata must each connect to the TOTAL, not merely to each other: the first
# version explained def-vs-module and left both standing apart from the
# population, which countrecon refused. Two counts that reconcile with one
# another can still both be unreconciled with the thing they partition.
led.explain("inventory.decision_sites", "def.rows",
            len(INV["rows"]) - sum(1 for r in rows.values() if r["scope"] == "def"),
            "the module-scope stratum: 5 straight-line decisions in 3 scripts")
led.explain("def.rows", "module.rows",
            sum(1 for r in rows.values() if r["scope"] == "def")
            - sum(1 for r in rows.values() if r["scope"] == "module"),
            "the two strata: 16 def-scope sites and 5 module-scope decisions in 3 scripts")
led.settle()

print(f"\n{'site':38s} {'scope':7s} verdict")
for key in sorted(rows):
    r = rows[key]
    print(f"  {key:36s} {r['scope']:7s} {r['verdict']}")
    if r.get("qualification"):
        print(f"        {r['qualification_reason'][:100]}")

tally = {}
for r in rows.values():
    tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
print(f"\nverdict tally over {len(rows)} sites: {tally}")

unqualified = sum(1 for r in rows.values() if r["verdict"] == "CAPTURED")
print(f"\nsites at a plain, unqualified CAPTURED: {unqualified} of {len(rows)}")
print("SEALED_CRITERIA §6.5 unblocks migration only when EVERY site is CAPTURED.")

# NON-VACUITY: no site may be missing, and none may be silently absent.
with redpath("decision sites carrying a verdict", expect_min=len(INV["rows"])) as rp:
    rp.observed(len(rows))

json.dump(dict(n_sites=len(rows), tally=tally, unqualified_captured=unqualified,
               module_mutation_ran=MUT_MOD is not None, rows=rows),
          open(f"{HERE}/site_verdicts.json", "w"), indent=1)
print("\nwritten -> overnight_2026_08_23/site_verdicts.json")
