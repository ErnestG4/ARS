"""ADJUDICATED RULINGS on the gate enumeration — the verdict lattice as a module.

Rulings-as-code: verdict lattices land as shared modules, never re-typed if/elif,
so a later sweep cannot quietly re-litigate a decided question in prose.

Adjudicated 2026-08-22 against gate_census/SWEEP_TRIAGE_TABLE.md.
"""

# ── RULING 1 — the size-guard clause, UPHELD, with the exception made operational
#
# A PRECONDITION refusal ("I cannot measure") is not a NEGATIVE SET ("this is
# outside my classes"), because an instrument with only the former will still,
# given sufficient n, classify anything into [rigid ... Poisson].
#
# EXCEPTION: guards DERIVED from the classification's own validity. Worked example
# MIN_N = 1/RAIL_RATIO, below which an arm provably cannot fire.
#
# OPERATIONAL TEST, so future sweeps do not re-litigate it:
#     Can the guard's constant be DELETED and RE-DERIVED from the classifier's own
#     parameters?  yes -> rejection-region work.  no (free constant chosen from
#     statistical custom: 5, 50) -> generic.
GUARD_GENERIC, GUARD_DERIVED = "GENERIC", "DERIVED"


def classify_guard(constant, derivation=None):
    """`derivation` must NAME the classifier parameters the constant follows from.
    Passing None is the admission that it is a free constant. The naming is the
    test: a derivation you cannot write is a derivation you do not have."""
    if not derivation:
        return GUARD_GENERIC
    return GUARD_DERIVED


# Applied to the 8 rows at adjudication: every guard (5, 50) is a FREE CONSTANT.
# All 8 rows STAY NO_NAMED_SET. The sweep's headline stands as measured.
RULING_1_RESULT = {"rows_affected": 8, "outcome": "all remain NO_NAMED_SET",
                   "basis": "every guard constant is free (5, 50), none re-derivable"}

# ── RULING 2 — the taxonomy EXTENDS: COMPUTED_UNUSED, forward-applicable
#
# DEFINITION: the site computes a quantity whose DESIGNED USE is hypothesis
# rejection, and NO control path compares it to any threshold.
# Incorporates the min()-is-not-a-comparison finding: **consumption by argmin does
# NOT count as use for rejection.**
VERDICTS_SEALED = ("MEASURED_NEGATIVE_SET", "UNMEASURED", "NO_NAMED_SET",
                   "NEEDS_JUDGMENT", "NOT_A_GATE")
VERDICTS_ADJUDICATED = VERDICTS_SEALED + ("COMPUTED_UNUSED",)

RECLASSIFIED = {                      # NEEDS_JUDGMENT -> COMPUTED_UNUSED
    "run_phase4.py": "COMPUTED_UNUSED",
    "run_analytical_nns.py": "COMPUTED_UNUSED",
    "run_per_pll_nns.py": "COMPUTED_UNUSED",
    "universality.py": "COMPUTED_UNUSED",
}
UNCHANGED = {"run_controls.py": "NO_NAMED_SET"}

# FORWARD-APPLICABLE ONLY. The sealed score of 9/11 was taken under
# VERDICTS_SEALED and STAYS SCORED THERE. The extension changes the descriptive
# table, not the scoring -- which is exactly why it waited for adjudication.
SCORING_UNCHANGED = {"sealed_score": "9 of 11", "taxonomy": "VERDICTS_SEALED",
                     "note": "extension is forward-applicable; the score is not restated"}

# ── RULING 3 — the severity gradient is the ORGANIZING AXIS
SEVERITY = ("NO_REJECTION_REGION", "COMPUTES_AND_IGNORES", "COMPUTES_AND_ACTS")


def severity_rank(v):
    return {"NO_NAMED_SET": 0, "COMPUTED_UNUSED": 1,
            "UNMEASURED": 2, "MEASURED_NEGATIVE_SET": 2}.get(v)


# MECHANISM OBSERVATION, promoted into the class-space finding: FOUR sites on the
# middle rung is a POPULATION, not an anomaly. One site holding-and-discarding is
# a near miss; four is a pattern of near misses. So the house default is not only
# "instruments that cannot refuse" but includes "instruments that MANUFACTURE the
# refusal information and DROP it." One-sidedness arises not from ignorance of the
# negative-set question but from NON-CONSUMPTION OF ITS ANSWER.
MECHANISM = ("one-sidedness arises not from failing to ask the question but from "
             "computing the answer and never reading it")

# C3 DIRECTIVE inherited from this ruling: where variants differ on comparison
# state, THE RECONCILED CLASSIFIER COMPARES. Computed-but-unused quantities are
# not merely preserved under acceptance clause 6 -- they are PROMOTED TO USED,
# because four sites already paid the compute cost and dropped the benefit.
C3_DIRECTIVE = ("where variants differ on comparison state, the reconciled "
                "classifier COMPARES; computed-unused quantities are promoted to "
                "used, not merely preserved")

# ── RULING 4 — the DECLARED label is DISCHARGED
MAPPING_STATUS = "ADJUDICATED (Ruling 1 fixes the clause; Ruling 2 extends the taxonomy)"
