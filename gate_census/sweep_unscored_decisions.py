"""SWEEP THE UNSCORED DECISIONS — the stratum the original sweep could not reach.

COMMITTED GENERATOR of gate_census/sweep_unscored.json.

WHY THIS IS A NEW MEASUREMENT, NOT A RE-SCORE
---------------------------------------------
The sealed sweep scored 15 units over 19 FILES and returned 9 of 11 distinct
def-extractable implementations with no rejection region. That number stands
where it was taken and is NOT restated here — the forward-only discipline of
Ruling 2 and Amendment 1.

But under R4 the census unit is the DECISION, and two decisions have never been
scored for a rejection region at all:

    run_analytical_nns.py:249   np.argmin over named ks_p/ks_o/ks_u
    run_analytical_nns.py:297   np.argmin over ANONYMOUS inline ks_to(...) calls

Their file carries a B4 row, but a file-level row cannot be attributed to one of
several decisions. So this is a fresh measurement of a stratum that has no
verdict, reported ALONGSIDE the sealed rate.

WHY THE STRATUM MATTERS MORE THAN ITS SIZE
------------------------------------------
Two sites is a small sample, but it is not a random one, and the direction of the
bias is known: the extractor's blind spot was CORRELATED with the defect. Of the
four files the original extractor could not reach, THREE were the COMPUTED_UNUSED
sites. So the unscored stratum is drawn from exactly the region where the defect
concentrated, and a clean result there would be more surprising than a dirty one.

THE MAPPING IS THE SEALED ONE, ported from run_sweep.judge() unchanged
---------------------------------------------------------------------
  * fit-quality quantity present AND compared -> MEASURED_NEGATIVE_SET if the
    threshold is calibrated against measured non-members, else UNMEASURED
  * present but NEVER compared              -> COMPUTED_UNUSED (Ruling 2's
    forward-applicable extension; this is a forward measurement, so it applies)
  * neither                                 -> NO_NAMED_SET
Consumption by min()/argmin() is NOT use for rejection (Ruling 2).

SCOPE: module-wide, matching the C3 inventory's rule for module-level sites. That
is the STRICTER test — a script that compares ks_p two hundred lines below its
decision has still compared it — so a COMPUTED_UNUSED here is a stronger finding
than one taken under a function-scoped search.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTION, committed with this generator, before any output exists    ║
║                                                                              ║
║ P-A  Neither decision has a rejection region: both land in the                ║
║      {NO_NAMED_SET, COMPUTED_UNUSED} family. 0 of 2 can say "none of these".  ║
║ P-B  :249 lands COMPUTED_UNUSED — its argmin consumes NAMED ks_p/ks_o/ks_u    ║
║      which the module never compares.                                        ║
║ P-C  :297 lands NO_NAMED_SET under the sealed name-based rule, NOT            ║
║      COMPUTED_UNUSED — its KS values are anonymous inline call results, never ║
║      bound to a name, so a name-based fit-quality detector finds nothing to   ║
║      call computed-and-ignored. If that is what happens it is a finding about ║
║      the TAXONOMY, not about the site: the same computes-and-discards         ║
║      behaviour changes verdict slot depending on whether the programmer chose ║
║      to name an intermediate.                                                 ║
║                                                                              ║
║ P-C is the one worth being wrong about. If :297 comes back COMPUTED_UNUSED,   ║
║ the taxonomy is more robust to spelling than I expect.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from redpath import redpath          # noqa: E402
from countrecon import CountLedger   # noqa: E402

INV = json.load(open(f"{HERE}/c3_inline_divergences.json"))
REC = json.load(open(f"{HERE}/c3_sweep_reconciliation.json"))
SWEEP = json.load(open(f"{HERE}/sweep_table.json"))

# the sealed sweep's own fit-quality name pattern
FITQ = re.compile(r"\b(best_ks|ks_crit\w*|fit_poor|fit_rejected|pv_[poun]|p_[poun]|p_two)\b")

UNSCORED = {f"{u['path']}:{u['line']}" for u in REC["unswept"]}


def judge_decision(path, line):
    """run_sweep.judge()'s mapping, applied to ONE decision with module scope."""
    src = open(os.path.join(ROOT, path), errors="replace").read()
    tree = ast.parse(src)

    fitq_names = sorted(set(m[0] if isinstance(m, tuple) else m
                            for m in FITQ.findall(src)))

    compared = False
    compared_names = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare):
            dumped = ast.dump(n)
            for k in ("best_ks", "ks_crit", "pv_", "pvalue", "p_value"):
                if k in dumped:
                    compared = True
                    compared_names.append(k)
            for nm in fitq_names:
                if f"id='{nm}'" in dumped:
                    compared = True
                    compared_names.append(nm)

    # what THIS decision consumes, and whether those values are ever named
    node = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n, "lineno", None) == line:
            node = n
            break
    if node is None:
        for n in ast.walk(tree):
            if isinstance(n, ast.stmt) and n.lineno <= line <= (n.end_lineno or n.lineno):
                node = n
    seg = ast.get_source_segment(src, node) or ""
    consumed_names = sorted(set(FITQ.findall(seg)))
    anonymous = not consumed_names and "ks_to(" in seg

    has_none_branch = bool(re.search(r"'none'|\"none\"|REFUSE|UNCLASSIFIED", seg))

    if fitq_names and compared:
        calibrated = "fit_poor" in src and "KS_NONMEMBER" in src
        return dict(verdict="MEASURED_NEGATIVE_SET" if calibrated else "UNMEASURED",
                    why="rejection region present and COMPARED somewhere in the module",
                    fitq_names=fitq_names, compared_via=sorted(set(compared_names)))
    if fitq_names and not compared:
        return dict(verdict="COMPUTED_UNUSED",
                    why=("fit-quality quantities COMPUTED and never COMPARED anywhere "
                         "in the module (the stricter, module-wide test); consumption "
                         "by argmin is not use for rejection"),
                    fitq_names=fitq_names, consumed_names=consumed_names,
                    values_are_anonymous=anonymous)
    return dict(verdict="NO_NAMED_SET", has_none_branch=has_none_branch,
                why="argmin over a fixed class set with no fit-quality quantity present",
                fitq_names=fitq_names, consumed_names=consumed_names,
                values_are_anonymous=anonymous)


rows = {}
for key in sorted(UNSCORED):
    path, line = key.rsplit(":", 1)
    rows[key] = judge_decision(path, int(line))

print("SWEEP OF THE PREVIOUSLY UNSCORED DECISIONS\n")
for key, r in rows.items():
    print(f"  {key}")
    print(f"      verdict : {r['verdict']}")
    print(f"      why     : {r['why']}")
    print(f"      fit-quality names in module : {r['fitq_names']}")
    if "consumed_names" in r:
        print(f"      names consumed at THIS decision: {r['consumed_names'] or '(none — anonymous)'}")
    if "compared_via" in r:
        print(f"      compared via: {r['compared_via']}")

has_rejection = [k for k, r in rows.items()
                 if r["verdict"] in ("MEASURED_NEGATIVE_SET", "UNMEASURED")]
no_rejection = [k for k, r in rows.items()
                if r["verdict"] in ("NO_NAMED_SET", "COMPUTED_UNUSED")]

print(f"\n  can say 'none of these' : {len(has_rejection)} of {len(rows)}")
print(f"  cannot                  : {len(no_rejection)} of {len(rows)}")

print("\nSEALED PREDICTIONS, scored:")
pa = len(has_rejection) == 0
pb = rows.get("run_analytical_nns.py:249", {}).get("verdict") == "COMPUTED_UNUSED"
pc = rows.get("run_analytical_nns.py:297", {}).get("verdict") == "NO_NAMED_SET"
for name, ok, txt in (("P-A", pa, "0 of 2 have a rejection region"),
                      ("P-B", pb, ":249 lands COMPUTED_UNUSED"),
                      ("P-C", pc, ":297 lands NO_NAMED_SET, not COMPUTED_UNUSED")):
    print(f"  {name}  {'MET  ' if ok else 'MISSED'}  {txt}")

led = CountLedger("classifier decisions scored for a rejection region")
led.report("inventory.decision_sites", INV["n_decision_sites"])
led.report("sealed_sweep.units", SWEEP["n_impl_rows"])
led.report("newly_scored.decisions", len(rows))
led.explain("inventory.decision_sites", "sealed_sweep.units",
            INV["n_decision_sites"] - SWEEP["n_impl_rows"],
            "identical-body collapse (19 files -> 15 units) plus the two decisions "
            "scored here, which had no unit of their own")
led.explain("sealed_sweep.units", "newly_scored.decisions",
            SWEEP["n_impl_rows"] - len(rows),
            "the sealed sweep's own units, scored in 2026-08-21 and not restated")
led.settle()

# NON-VACUITY: the stratum is known to contain exactly the two decisions the
# reconciliation named. A sweep that scores none of them has measured nothing.
with redpath("previously unscored decisions given a verdict", expect_min=2) as rp:
    rp.observed(len(rows))

json.dump(dict(rows=rows, has_rejection=has_rejection, no_rejection=no_rejection,
               predictions=dict(P_A=pa, P_B=pb, P_C=pc),
               sealed_rate_not_restated="9 of 11 distinct def-extractable implementations"),
          open(f"{HERE}/sweep_unscored.json", "w"), indent=1)
print("\nwritten -> gate_census/sweep_unscored.json")
