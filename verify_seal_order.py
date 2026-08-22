"""Is a "SEALED" label true of the COMMIT GRAPH, or only of someone's recollection?

WHY: twice in two days a generator and its output entered the record in the same
commit (3b501fe, 8ba9d52). Both times the rule inside the generator genuinely was
written before the run — and both times the graph could not show it, so the honest
label was DECLARED, not SEALED. `sealgen.sh` enforces the shape at COMMIT time.
This enforces it at READ time, so "SEALED" is a machine-checkable property rather
than a claim about how sealgen was used. Same relationship checkrun has to exit
codes: the discipline exists, then a line no human types confirms it was followed.

VERDICTS, per (rule-artifact, output-artifact) pair:
  SEALED    rule's introducing commit strictly PRECEDES the output's
  DECLARED  same commit — written first, unprovable from the graph
  INVERTED  output precedes the rule. Not a labelling nuance; the rule cannot
            have constrained a result that already existed.
  UNTRACKED either path has no introducing commit

This checker does NOT fail the board on DECLARED. A DECLARED pair is honest when
labelled honestly; it fails only on INVERTED, which no honest label can rescue.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# (rule/generator, output it constrains, what the rule claims to fix)
PAIRS = [
    ("gate_census/TRIAGE_CRITERIA_SEALED.md", "gate_census/sweep_table.json",
     "the four questions + verdict vocabulary"),
    ("gate_census/run_sweep.py", "gate_census/sweep_table.json",
     "code-feature -> verdict mapping"),
    ("gate_census/measure_copy_dedup.py", "gate_census/copy_dedup.json",
     "normalisation spec + denominator"),
    ("bounded_census/CLASSIFICATION_SEALED.md", "bounded_census/rail_fractions.json",
     "convention-vs-mathematical classification"),
    ("c2_acceptance/verify_pvc11_retention.py", "c2_acceptance/c2_pvc11_summary.json",
     "C2 acceptance criteria"),
    ("c2_acceptance/pvc11_bounded_baseline.json", "c2_acceptance/c2_pvc11_summary.json",
     "the retention baseline"),
    ("holonomy/ridge_stageA.json", "holonomy/ridge_stageB.json",
     "sealed ridge predictions for the held-out degrees"),
]


def first_commit(path):
    r = subprocess.run(["git", "log", "--format=%H %ct", "--diff-filter=A", "--", path],
                       cwd=ROOT, capture_output=True, text=True)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if not lines:
        return None
    h, t = lines[-1].split()          # oldest introducing commit
    return h, int(t)


rows, bad = [], []
for rule, out, what in PAIRS:
    a, b = first_commit(rule), first_commit(out)
    if a is None or b is None:
        v = "UNTRACKED"
    elif a[0] == b[0]:
        v = "DECLARED"
    elif a[1] < b[1]:
        v = "SEALED"
    else:
        v = "INVERTED"
    rows.append((v, rule, out, what, (a[0][:8] if a else "-"), (b[0][:8] if b else "-")))
    if v == "INVERTED":
        bad.append((rule, out))

w = max(len(r[1]) for r in rows)
print(f"{'verdict':9s} {'rule artifact':{w}s}  {'rule@':9s} {'out@':9s} constrains")
for v, rule, out, what, ha, hb in sorted(rows, key=lambda r: r[0]):
    print(f"{v:9s} {rule:{w}s}  {ha:9s} {hb:9s} {what}")

n_sealed = sum(1 for r in rows if r[0] == "SEALED")
n_decl = sum(1 for r in rows if r[0] == "DECLARED")
print(f"\n  SEALED {n_sealed}   DECLARED {n_decl}   INVERTED {len(bad)}")
print("  DECLARED is honest when labelled honestly; it is not a failure. INVERTED is.")
if bad:
    print("\nVERIFY_SEAL_ORDER: FAIL — a rule entered the record AFTER the output it "
          "claims to constrain; no label rescues that")
    sys.exit(1)
print("\nVERIFY_SEAL_ORDER: PASS — no rule postdates the output it constrains")
