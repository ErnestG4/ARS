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
    # Session G, registered 2026-09-02 when the arc was merged back. It reads
    # DECLARED and that is the honest label: MORNING_G.md says "Sealed
    # byte-locked before measuring", which may well be true of what happened,
    # but seal and measurement entered the record in the SAME commit and the
    # graph cannot show the order. Registered anyway -- an unregistered pair is
    # not "not DECLARED", it is unexamined, and this one was consumed by
    # H_arm1_seal.py on a branch where the seal was absent entirely.
    ("approximability/G_fifth_prediction_SEALED.json",
     "approximability/G_fifth_measured.json",
     "the sealed out-of-sample dim predictions for fifth depths 10-13"),
    # Session D, registered 2026-09-05 when its branch was landed. Same shape as
    # Session G's: generator and sealed output in ONE commit (352231a), so the
    # honest label is DECLARED. Registered because the sealed JSON had been on
    # this branch since 44a7ca1 with its GENERATOR on no reachable branch at
    # all -- an unregistered pair is not "not DECLARED", it is unexamined.
    ("approximability/pi292_thouless_prediction.py",
     "approximability/pi292_prediction_SEALED.json",
     "the locked pi-292 Thouless depth predictions"),
    # Session F's independent replication, 2026-09-05. This one is a genuine
    # SEALED: sealgen committed the generator alone, then it ran.
    ("approximability/F_reproduce.py", "approximability/F_reproduce.json",
     "the declared curve family and the gate/rate predictions over it"),
    # criterion-scope, 2026-09-06. v1: sealgen committed the generator (and a
    # path fix, pre-output) before the output; its INVALID head is the banked
    # record of R2 catching filter_worth_it's stale input. v2: same flow.
    ("cross_substrate/brocot_criterion_scope.py",
     "cross_substrate/brocot_criterion_scope.json",
     "v1's criterion-region predictions, R1/R2 premises included"),
    ("cross_substrate/brocot_criterion_scope_v2.py",
     "cross_substrate/brocot_criterion_scope_v2.json",
     "v2's corrected premise (regraph-pinned) and inherited bars"),
    # derivflow correlated-error repair, 2026-09-08. sealgen committed the
    # generator alone, then it ran for 5477s; the output landed separately.
    ("derivflow/zbeta_correlated_error.py",
     "derivflow/zbeta_correlated_error.json",
     "the replicate-sharing error model and its C2 directional prediction"),
    # GUE-adapted isoconfig probe, 2026-09-08. Generator committed alone (dedc4ba)
    # while still blind to the zbeta result, then run. Its POST-HOC amendment
    # (gue_isoconfig_kstar_amendment) is deliberately NOT registered here: the
    # only label this checker could give it is DECLARED, and DECLARED would
    # overstate a generator written after its subject had been read.
    ("derivflow/gue_isoconfig_adapted.py",
     "derivflow/gue_isoconfig_adapted.json",
     "the adapted-design mechanism arms and the binding slow-subpopulation secondary"),
    ("cross_substrate/brocot_normative_anchor.py",
     "cross_substrate/brocot_normative_anchor.json",
     "the resolvability calibration and its pre-registered permissive direction"),
    # F_window_exponent, 2026-09-08: executes the test F_genus_exponent queued in
    # its own amendment. Its POST-HOC companion (F_oscillation_amendment) is
    # deliberately NOT registered, for the same reason as the isoconfig one.
    ("approximability/F_window_exponent.py",
     "approximability/F_window_exponent.json",
     "the vmax sweep and the queued gap-shrinks decision rule"),
    ("derivflow/seed_roster_beta.py", "derivflow/seed_roster_beta.json",
     "the beta-roster surface, its matched-design premise and the k* ordering"),
]


def first_commit(path):
    # --full-history IS LOad-BEARING, added 2026-09-02. Without it git applies
    # history simplification and can attribute a file to a LATER commit on the
    # mainline, hiding the earlier commit on a since-merged branch that really
    # introduced it. Found landing Session G: G_fifth_measured.json and its
    # G_fifth_prediction_SEALED.json are in ONE commit (af5349f) and are
    # therefore DECLARED -- but the simplified log reported the measurement at
    # 479de0b, twelve hours LATER, which would have made the pair read SEALED.
    # This checker exists so that "SEALED" is a property of the graph rather
    # than of recollection; a traversal flag that manufactures the label is the
    # same defect one level down. No existing registered pair changes verdict
    # under the fix, which is how it was verified safe.
    r = subprocess.run(["git", "log", "--full-history", "--format=%H %ct",
                        "--diff-filter=A", "--", path],
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
