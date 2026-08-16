"""Dated addenda to the holonomy seal (run once, 2026-08-16, post-banking
audit by Will).  COMMITTED GENERATOR of the seal's `addenda` block.  The
freeze list is untouched; every addendum row is three-event labeled where it
covers post-hoc work."""

import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
P = f"{ROOT}/holonomy/prereg_sealed.json"

seal = json.load(open(P))
assert "addenda" not in seal, "addenda already applied — run-once guard"

seal["addenda"] = [
    dict(
        id="ADD-1", date="2026-08-16",
        title="OP1 materiality pass — owed by brief §2, omitted at banking",
        three_event=["arc banked without the pass (defect: |Delta|=1.15 "
                     "qualifies under §2)",
                     "Will's post-arc audit flagged the omission",
                     "pass run: holonomy/op1_materiality.py"],
        result="NOT CLEAN: nearest downstream consumer is the RIGID_GUE "
               "gate (cross_substrate/longrange_discriminator.py); "
               "renewal-arm min 2.71 vs boundary 1.056 -> margin 1.65 = "
               "1.4x |Delta_bare| < k=3.  Criterion note: the k*|Delta| "
               "form was chosen at pass time (arc k=3); the flag fires at "
               "any threshold above 1.4 — conservative reading adopted, "
               "escalation to ORDER_RULING_REQUIRED followed (ADD-3).",
    ),
    dict(
        id="ADD-2", date="2026-08-16",
        title="NONCOMMUTING_UNPREDICTED — declaration of an "
              "implementation-time lattice completion",
        detail="Authored PRE-SEAL: lattice_h.py committed dc2448c "
               "(00:01:16) with the value present; sealed a583d9f "
               "(00:01:27); frozen blob 52a1e575 matches dc2448c exactly; "
               "measurement ran after.  Same class as the survey's "
               "CLASS_INCONSISTENT_ACROSS_TILES completion (the module "
               "split primary/measurement layers and needed a "
               "measurement-layer cell for law-misfit).  DEFECT: the "
               "survey seal DECLARED its completion; this seal did not — "
               "declared here after Will's audit asked for the timeline "
               "check.",
    ),
    dict(
        id="ADD-3", date="2026-08-16",
        title="OP1 ruling revised: original order RETRACTED; ruled content "
              "is the MATCHED_LENS invariant",
        three_event=["OP1 banked RULED_CONSISTENT('unfold_then_surrogate') "
                     "without a correctness leg",
                     "ADD-1 found the ruling load-bearing at the RIGID_GUE "
                     "gate; call-site search found live sites implement "
                     "surrogate-then-SHARED-lens deliberately ('# same "
                     "lens') — blanket enforcement of the original order "
                     "would have BROKEN the matched-lens design",
                     "correctness cell run (holonomy/op1_correctness.py, "
                     "prediction committed first): direction as predicted "
                     "(z_matched -0.04 vs z_mixed -0.32, mixed biases "
                     "marginal-class data rigid-ward) in BOTH runs "
                     "(8-seed first run banked in-file; one pre-committed "
                     "64-seed rerun), but separation 0.28+-0.20 does not "
                     "reach k=3"],
        ruling="MATCHED_LENS: surrogate and data must pass the IDENTICAL "
               "unfolding apparatus.  Basis RULED_CONSISTENT — biases do "
               "not separate at arc power — but with the leg RUN and the "
               "site-specific effect quantified (~0.3 sigma of the "
               "classification band, ~4x smaller than the bare-pair "
               "Delta measured on the trended substrate).  canonical.py "
               "row updated; the original blanket order is retracted.",
    ),
    dict(
        id="ADD-4", date="2026-08-16",
        title="C1 self-enforcement claim scoped",
        detail="The compute_nns internal renormalisation is unconditional "
               "IN CODE (runs on every input), but the measured "
               "'identical class calls under both orders' datum is "
               "zeta-window-only.  Other substrates inherit the MECHANISM, "
               "not the MEASUREMENT.  Registry row and table restated.",
    ),
    dict(
        id="ADD-5", date="2026-08-16",
        title="Site-hardening watch item registered (not this arc's gate)",
        detail="The long-range discriminator's renewal-to-RIGID absolute "
               "margin is 1.65 in Sigma^2(20) units against a renewal band "
               "sd of ~1.5 at (L=20, deg 6, n=1200) — thin in its own "
               "units, independent of order effects.  Its own "
               "validate_rate_unfold guard exists for exactly this; "
               "registered to the cross-substrate program as a watch item, "
               "owner: next arc that touches the RIGID_GUE gate.",
    ),
]
seal["addenda_artifacts"] = ["op1_materiality.py", "op1_materiality.json",
                             "op1_correctness.py", "op1_correctness.json",
                             "patch_addenda.py"]
json.dump(seal, open(P, "w"), indent=1)
print(f"addenda applied: {[a['id'] for a in seal['addenda']]}")
