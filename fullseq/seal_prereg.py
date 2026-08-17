"""Full-sequence holonomy seal.  COMMITTED GENERATOR of
fullseq/prereg_sealed.json.

Written and run BEFORE S0.  The kill criterion is restated in 1-D terms here,
with the targets NAMED and their CURRENT MARGINS RECORDED, so the threshold
cannot drift toward whatever the measurement turns out to find — the same
protection the pairwise arc used, applied to a criterion that had to be
re-authored for a new dialect.
"""

import hashlib
import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
FREEZE = ["transitions_1d.py", "run_fullseq.py"]


def blob(p):
    d = open(p, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


seal = dict(
    sealed_utc_date="2026-08-17",
    arc="Full-sequence holonomy (FULL_SEQUENCE_BRIEF.md), Option B — 1-D "
        "home dialect, sequence length 5.",
    posture="Protocol arc. Synthetic data and already-banked substrates "
            "only; NO new science claims. Nothing under cross_substrate/ or "
            "survey/ is written; no banked row is re-verdicted.",
    debug_freeze="BINDING: the debugging window closes with this seal.",

    pipeline_choice=dict(
        chosen="1-D home dialect",
        reason_recorded_verbatim=(
            "A and B answer different questions. A (survey) asks 'is "
            "anything currently banked at risk' and is a safety check with a "
            "near-certain null; B (1-D) asks 'does the composition law hold' "
            "and is the science. B is chosen BECAUSE THE LAW IS WANTED, not "
            "because A would come back empty. Choosing the dialect where the "
            "effect is largest would otherwise be choosing the dialect most "
            "likely to produce a positive result — that selection hazard is "
            "recorded here so it cannot be laundered into the result."),
        survey_side_cell="A's kill criterion runs anyway as a bankable "
                         "one-hour side cell; its answer belongs on the "
                         "board regardless of where this arc goes."),

    kill_criterion=dict(
        statement="If the largest reordering effect is far below every "
                  "banked 1-D decision margin, the arc aborts as NO_RISK "
                  "and banks that as a protocol result.",
        rule="ABORT iff Delta_max < 0.1 * min(named margins), in the "
             "decision layer's own units.",
        threshold_sigma=0.201,
        derivation="0.1 x the SMALLEST named margin (brocot/golden at "
                   "2.01 sigma) = 0.201 sigma.",
        targets_named_with_current_margins=[
            dict(target="RIGID_GUE gate, brocot/golden",
                 z=0.49, boundary=2.5, margin_sigma=2.01,
                 source="verify/tier2_results.md:46-47"),
            dict(target="RIGID_GUE gate, zeta_first_2000 (post-L-policy)",
                 z=-9.10, boundary=-2.5, margin_sigma=6.60,
                 source="lcap/lcap_measured.json"),
            dict(target="NNS class call, zeta ks_gue vs ks_goe",
                 ks_gue=0.0434, ks_goe=0.1114, margin_ks=0.0680,
                 source="holonomy/p1_measured.json zeta.nns_ks"),
        ],
        recorded_before_S0=True),

    sequence=dict(
        length=5,
        transitions=["T1 WINDOW", "T2 UNFOLD", "T3 THIN", "T4 RESCALE",
                     "T5 POOL"],
        reference_order=["T1", "T2", "T3", "T4", "T5"],
        type_constraint="T1 must precede T5 (pooling before windowing is a "
                        "different pipeline, not a reordering of this one)",
        prng_discipline="T3's per-point randomness is PRE-DRAWN once before "
                        "any ordering runs and consumed by whichever "
                        "position T3 occupies; otherwise the orderings "
                        "consume the stream against different inputs and "
                        "the difference measures stream drift, not order."),

    permutation_sample=dict(
        rule="all adjacent transpositions of the reference order, all "
             "3-cycles on the first three slots, the full reversal, and a "
             "fixed random draw of 6 — all filtered by the type constraint",
        seed=4242, fixed_before_measurement=True),

    statistics=dict(primary="sigma2(L) at L=20", control="rtilde",
                    note="rtilde is predicted order-insensitive; a firing "
                         "control is an instrument defect, not holonomy"),

    first_order_predictor=dict(
        form="Delta_pred(sigma) = sum over inverted pairs of delta_ij "
             "evaluated at the MID-STACK dial (from S0), not the "
             "bare-substrate dial",
        falsifier="H(sigma) = Delta_measured - Delta_pred is the higher-"
                  "order holonomy; its size, sign and structure are the "
                  "arc's primary result"),

    verdicts=["FIRST_ORDER_SUFFICIENT", "HIGHER_ORDER_MEASURED",
              "VERDICT_FLIP_RISK", "NO_RISK", "UNDERPOWERED"],
    verdict_flip_rule="VERDICT_FLIP_RISK licenses FLAGGING a row, NOT "
                      "re-running it: full-sequence canonicalisation is what "
                      "this arc is trying to establish, so re-deriving "
                      "banked results under a sequence chosen mid-flight "
                      "would repeat the OP1 error at pipeline scale.",
    extension_rule="UNDERPOWERED only: one doubling of the seed count, "
                   "fires once.",
    code_freeze_blob_shas={f: blob(f"{ROOT}/fullseq/{f}") for f in FREEZE},
)
json.dump(seal, open(f"{ROOT}/fullseq/prereg_sealed.json", "w"), indent=1)
print(f"SEALED: fullseq/prereg_sealed.json ({len(FREEZE)} files frozen)")
print(f"  kill threshold: Delta_max < {seal['kill_criterion']['threshold_sigma']} "
      f"sigma -> NO_RISK abort")
