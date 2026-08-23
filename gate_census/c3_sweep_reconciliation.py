"""RECONCILE the completed 20-decision inventory against the sweep's verdict rows.

COMMITTED GENERATOR of gate_census/c3_sweep_reconciliation.json.
DESCRIPTIVE ONLY. Ordered by ruling to land BEFORE any migration.

WHAT IS BEING RECONCILED
------------------------
Two instruments counted the same population and got different numbers:

    sweep  (gate_census/run_sweep.py)  -> 11 distinct implementations
                                          + 4 B4 extraction rows = 15 units
                                          covering 19 FILES
    inventory (c3_inline_inventory.py) -> 20 DECISION SITES across 19 files

Under Ruling R4 the census unit is the DECISION, not the file. So every decision
site either carries a verdict row of its own or it is UNSWEPT POPULATION. This
generator enumerates which, using countrecon: the difference must be explained
with the exact delta or the run raises.

WHY IT MATTERS FOR THE STANDING PRESUMPTION
-------------------------------------------
The presumption's base rate is "9 of 11". Eleven is the count of DISTINCT
DEF-EXTRACTABLE IMPLEMENTATIONS. It is not the count of classifiers in this
codebase, and quoting it as a codebase-wide rate silently promotes a stratum
statistic to a population statistic -- which is the same move the extractor bias
already punished once. This generator restates the denominator; it DOES NOT
re-score the sweep. Retro-scoring under a rule adopted afterwards is exactly what
Ruling 2 and Amendment 1 both refused, and the refusal is not weaker here because
the new number would be more flattering or less.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from countrecon import CountLedger   # noqa: E402
from redpath import redpath          # noqa: E402

INV = json.load(open(f"{HERE}/c3_inline_divergences.json"))
SWEEP = json.load(open(f"{HERE}/sweep_table.json"))
DEDUP = json.load(open(f"{HERE}/copy_dedup.json"))

rows = INV["rows"]
by_site = SWEEP["by_site"]
def_extractable = {p for ps in DEDUP["groups"].values() for p in ps}

# ── per-decision coverage ────────────────────────────────────────────────────
# A sweep row is keyed by FILE. A file with one decision is covered unambiguously.
# A file with N>1 decisions has one row for N decisions: the row cannot be
# attributed to a particular decision, so the SECOND and later decisions at that
# file are unswept as distinct units.
per_file = {}
for r in rows:
    per_file.setdefault(r["path"], []).append(r)

covered, unswept = [], []
for path, decisions in per_file.items():
    decisions.sort(key=lambda r: r["line"])
    for i, r in enumerate(decisions):
        rec = dict(path=path, line=r["line"], mechanism=r["mechanism"],
                   scope=r["scope"],
                   stratum=("def-extractable" if path in def_extractable
                            else "inline / not def-extractable"),
                   sweep_verdict=by_site.get(path))
        if path not in by_site:
            rec["coverage"] = "NO ROW AT ALL"
            unswept.append(rec)
        elif i == 0:
            rec["coverage"] = "covered by the file's row"
            covered.append(rec)
        else:
            rec["coverage"] = ("UNSWEPT AS A DISTINCT UNIT — the file's single row "
                               "cannot be attributed to this decision")
            unswept.append(rec)

# ── the ledger: the difference must close ────────────────────────────────────
led = CountLedger("classifier decision sites")
led.report("inventory.decision_sites", len(rows))
led.report("inventory.files", len(per_file))
led.report("sweep.verdict_rows_by_file", len(by_site))
led.report("sweep.units_impl_plus_b4", SWEEP["n_impl_rows"])
led.report("sweep.distinct_impls_sealed", SWEEP["N_distinct_sealed"])
led.report("inventory.decisions_covered_by_a_row", len(covered))
led.report("inventory.decisions_unswept", len(unswept))

led.explain("inventory.decision_sites", "sweep.verdict_rows_by_file", len(rows) - len(by_site),
            "files holding more than one decision: " + ", ".join(
                f"{p}:{[d['line'] for d in ds]}" for p, ds in sorted(per_file.items())
                if len(ds) > 1) + " — the sweep keys rows by file, so extra decisions "
            "in an already-rowed file get no unit of their own")
led.explain("inventory.decision_sites", "inventory.decisions_covered_by_a_row",
            len(rows) - len(covered), "decisions unswept as distinct units (see above)")
led.explain("inventory.files", "sweep.verdict_rows_by_file", len(per_file) - len(by_site),
            "every file carrying a decision has a sweep row; file coverage is complete")
led.explain("sweep.verdict_rows_by_file", "sweep.units_impl_plus_b4",
            len(by_site) - SWEEP["n_impl_rows"],
            "four identical-body copies share one implementation row (362c40e9: "
            "run_mertens_liouville + run_lmfdb_postprocess + run_dirichlet_family + "
            "run_lmfdb_extend) and one pair shares another (9fc4073c: "
            "run_zeta_height_convergence + run_earthquake_nns), so 19 files collapse "
            "to 15 units")
led.explain("sweep.units_impl_plus_b4", "sweep.distinct_impls_sealed",
            SWEEP["n_impl_rows"] - SWEEP["N_distinct_sealed"],
            "the four B4 extraction rows (run_controls, run_analytical_nns, "
            "run_per_pll_nns, universality) sit outside the sealed 11, which counts "
            "only def-extractable distinct bodies")
led.explain("inventory.decisions_covered_by_a_row", "inventory.decisions_unswept",
            len(covered) - len(unswept), "arithmetic complement of the split above")
led.explain("inventory.decision_sites", "inventory.files", len(rows) - len(per_file),
            "same multi-decision files as above")
led.explain("inventory.files", "sweep.units_impl_plus_b4",
            len(per_file) - SWEEP["n_impl_rows"], "identical-body collapse, as above")
led.explain("inventory.files", "sweep.distinct_impls_sealed",
            len(per_file) - SWEEP["N_distinct_sealed"],
            "identical-body collapse plus the four B4 rows outside the sealed 11")
led.explain("inventory.decision_sites", "sweep.units_impl_plus_b4",
            len(rows) - SWEEP["n_impl_rows"], "multi-decision files plus identical-body collapse")
led.explain("inventory.decision_sites", "sweep.distinct_impls_sealed",
            len(rows) - SWEEP["N_distinct_sealed"],
            "multi-decision files, identical-body collapse, and the four B4 rows")
led.explain("inventory.decisions_covered_by_a_row", "sweep.verdict_rows_by_file",
            len(covered) - len(by_site), "one covered decision per rowed file")
led.explain("inventory.decisions_covered_by_a_row", "sweep.units_impl_plus_b4",
            len(covered) - SWEEP["n_impl_rows"], "identical-body collapse, as above")
led.explain("inventory.decisions_covered_by_a_row", "sweep.distinct_impls_sealed",
            len(covered) - SWEEP["N_distinct_sealed"],
            "identical-body collapse plus the four B4 rows")
led.explain("inventory.decisions_unswept", "sweep.verdict_rows_by_file",
            len(unswept) - len(by_site), "complement; unswept units carry no row by definition")
led.explain("inventory.decisions_unswept", "sweep.units_impl_plus_b4",
            len(unswept) - SWEEP["n_impl_rows"], "as above")
led.explain("inventory.decisions_unswept", "sweep.distinct_impls_sealed",
            len(unswept) - SWEEP["N_distinct_sealed"], "as above")
led.explain("inventory.decisions_unswept", "inventory.files",
            len(unswept) - len(per_file), "as above")

led.settle()

# ── stratum restatement of the presumption's denominator ─────────────────────
in_stratum = [r for r in rows if r["path"] in def_extractable]
out_stratum = [r for r in rows if r["path"] not in def_extractable]

print("\nSTRATUM RESTATEMENT — what '9 of 11' is a rate over")
print(f"  def-extractable stratum        : {len(set(r['path'] for r in in_stratum))} files, "
      f"{len(in_stratum)} decisions, {SWEEP['N_distinct_sealed']} distinct bodies  <- the sealed denominator")
print(f"  outside that stratum (inline)  : {len(set(r['path'] for r in out_stratum))} files, "
      f"{len(out_stratum)} decisions")
print(f"  completed population           : {len(per_file)} files, {len(rows)} decisions")
print("  the sealed rate is 9 of 11 DISTINCT DEF-EXTRACTABLE IMPLEMENTATIONS.")
print("  it is NOT 9 of 11 classifiers-in-the-codebase, and is not restated here.")

print("\nUNSWEPT AS DISTINCT UNITS:")
for r in unswept:
    print(f"  {r['path']}:{r['line']}  mech={r['mechanism']}  ({r['stratum']})")
    print(f"      {r['coverage']}")

# NON-VACUITY: run_analytical_nns:249 is known by hand to be a second decision in
# an already-rowed file. A reconciliation that finds NOTHING unswept has lost the
# very unit that motivated it.
with redpath("decisions unswept as distinct units", expect_min=1) as rp:
    rp.observed(len(unswept))

out = dict(decision_sites=len(rows), files=len(per_file),
           sweep_rows_by_file=len(by_site), sweep_units=SWEEP["n_impl_rows"],
           sealed_distinct_impls=SWEEP["N_distinct_sealed"],
           covered=covered, unswept=unswept,
           denominator_restatement={
               "sealed_rate": "9 of 11",
               "denominator_is": "distinct def-extractable implementations",
               "denominator_is_not": "classifiers in the codebase",
               "def_extractable_decisions": len(in_stratum),
               "inline_decisions": len(out_stratum),
               "population_decisions": len(rows),
               "retro_scored": False})
json.dump(out, open(f"{HERE}/c3_sweep_reconciliation.json", "w"), indent=1)
print(f"\nwritten -> gate_census/c3_sweep_reconciliation.json")
print("\nRECONCILED — every count difference carries an enumerated explanation, "
      "and the unswept units are named rather than absorbed.")
