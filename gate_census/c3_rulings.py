"""C3 RULINGS — the five adjudicated decisions as a module, plus the ordering condition.

Rulings-as-code, per house doctrine: a verdict lattice lands as a shared module and is
never re-typed as if/elif, so a later pass cannot quietly re-litigate a decided question
in prose. Companion to gate_census/rulings.py (the gate-sweep rulings).

Adjudicated 2026-08-22 against gate_census/C3_DIVERGENCE_DOCKET.md.

╔══════════════════════════════════════════════════════════════════════════════╗
║ ORDERING CONDITION — MIGRATION IS NOT YET AUTHORISED                         ║
║   1. sweep-row reconciliation lands            [DONE, c3_sweep_reconciliation]║
║   2. R3 artifact baselines captured            [NOT DONE]                     ║
║ Baseline before write. That is the house style this whole arc started from,   ║
║ and the one time it lapsed a --limit flag truncated 1159 records to 3.        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rulings import classify_guard, GUARD_GENERIC, GUARD_DERIVED   # noqa: E402,F401


class RulingViolation(AssertionError):
    pass


# ── R1 — THE GUARD FORK (50 / 5 / none) ──────────────────────────────────────
#
# All three are free constants; under Ruling 1 none is a negative set and
# therefore NONE HAS A CLAIM TO INHERIT. The prohibition is the operative part:
#
#   A CONVENTION CHOSEN IS A CONVENTION. A CONVENTION INHERITED IS AN ACCIDENT
#   WEARING ONE'S CLOTHES.
#
# Sequence, in order:
#   (a) attempt DERIVATION from the reconciled classifier's own validity. Worked
#       precedent: MIN_N = 1/RAIL_RATIO, below which an arm provably cannot fire.
#       If the KS machinery or the discriminator implies a floor, THAT is the
#       guard, and its derivation is written down.
#   (b) failing that, ONE convention constant, chosen explicitly and passed as a
#       typed admission that it is policy.
#
# Forbidden: silent inheritance from whichever variant the migration starts at.
R1_SEQUENCE = ("derive-from-validity", "one-explicit-convention")
R1_FORBIDDEN = "silent inheritance of a guard constant from the migration's starting variant"

_UNSET = object()


def guard_decision(n_min=_UNSET, derivation=None):
    """The reconciled classifier's guard MUST come through here.

    `n_min` has no default, deliberately. A default is silent inheritance with
    extra steps: it picks one variant's free constant and makes every call site
    that omits the argument agree with it without anyone deciding anything.
    """
    if n_min is _UNSET:
        raise RulingViolation(
            "R1: n_min was not supplied. The 50/5/none fork is three free "
            "constants, none of which has a claim to inherit — choose one "
            "explicitly, or derive one and name the derivation. " + R1_FORBIDDEN)
    kind = classify_guard(n_min, derivation)
    return dict(n_min=int(n_min), kind=kind, derivation=derivation,
                admitted_as_policy=(kind == GUARD_GENERIC))


# ── R2 — ONE CANONICAL VOCABULARY, WITH A COMMITTED TRANSLATION TABLE ─────────
#
# Which vocabulary wins is nearly arbitrary. That it is singular and MAPPED is
# not. Banked data speaks the legacy labels and must stay interpretable without
# archaeology.
#
# Two constraints:
#   (i)  no legacy label may be reused with an ALTERED MEANING — a label that
#        changes referent is worse than a new label, because old readings stay
#        syntactically valid while becoming false;
#   (ii) the table is DATA THE CERTIFIER CONSUMES, not prose in a document.
CANONICAL_LABELS = ("Poisson", "GOE", "GUE")

LABEL_TRANSLATION = {
    # legacy vocabulary          -> canonical
    "Poiss":    "Poisson",
    "Poisson":  "Poisson",
    "poisson":  "Poisson",
    "GOE":      "GOE",
    "goe":      "GOE",
    "GUE":      "GUE",
    "gue":      "GUE",
}

# Sites reading each legacy vocabulary, from c3_inline_divergences.json.
LABEL_VOCABULARIES = {
    "Poiss/GOE/GUE":     17,
    "Poisson/GOE/GUE":    2,
    "poisson/goe/gue":    1,
}


def to_canonical(label):
    if label not in LABEL_TRANSLATION:
        raise RulingViolation(
            f"R2: '{label}' is in no committed vocabulary. Add it to "
            "LABEL_TRANSLATION with its referent stated, or it is a new class.")
    return LABEL_TRANSLATION[label]


def check_no_altered_referent():
    """Constraint (i), mechanically: a legacy label must map to the class it
    always denoted. Reuse with an altered referent is refused here rather than
    discovered by a reader of old artifacts."""
    for legacy, canon in LABEL_TRANSLATION.items():
        if legacy.lower().startswith("poiss") and canon != "Poisson":
            raise RulingViolation(f"R2: '{legacy}' re-pointed to {canon}")
        if legacy.lower() == "goe" and canon != "GOE":
            raise RulingViolation(f"R2: '{legacy}' re-pointed to {canon}")
        if legacy.lower() == "gue" and canon != "GUE":
            raise RulingViolation(f"R2: '{legacy}' re-pointed to {canon}")
    return True


# ── R3 — THE CRITERIA GENERALIZE, THEY DO NOT EXEMPT ─────────────────────────
#
# Bit-identity of a returned dict was always a PROXY for the real invariant:
#
#       IDENTICAL INPUTS PRODUCE IDENTICAL OBSERVABLE OUTPUTS.
#
# Function sites: the observable is the dict — brief clause 1 as written.
# Script sites:   the observable is whatever the straight-line code emits —
#                 banked values, printed results, written files — and the
#                 criterion is bit-identity of THOSE artifacts under identical
#                 inputs, captured as a baseline BEFORE migration.
#
# This is derivation-shaped: it extends the clause from its instance to its
# principle without bending it. Exempting the five would exclude precisely the
# stratum the extractor already missed once, and the docket records what that
# stratum contains.
R3_INVARIANT = "identical inputs produce identical observable outputs"

OBSERVABLE_BY_SCOPE = {
    "def":    "returned dict (best, gap, ks_p, ks_o, ks_u, n, mass03), repr round-trip",
    "module": "emitted artifacts: printed lines, written files, and the assigned "
              "`best` label — bit-identical under identical inputs",
}


def acceptance_observable(scope):
    if scope not in OBSERVABLE_BY_SCOPE:
        raise RulingViolation(f"R3: no observable defined for scope '{scope}'")
    return OBSERVABLE_BY_SCOPE[scope]


def migration_authorised(site_scope, baseline_captured):
    """Migration may introduce a function call where there was script code ONLY
    under the artifact-identity gate. Baseline before write."""
    if not baseline_captured:
        raise RulingViolation(
            f"R3: no baseline captured for a '{site_scope}' site. The observable "
            f"is: {acceptance_observable(site_scope)}. Capture it before writing.")
    return True


# ── R4 — THE CENSUS UNIT IS THE DECISION, NOT THE FILE ───────────────────────
#
# A file is a storage convention. One file holding two decisions by two
# mechanisms gets two rows, two verdicts, two migrations. This also explains part
# of the 11-vs-20 gap, and is stated here so no future census re-derives it.
COUNTING_RULE = ("the census unit is the DECISION SITE — a min()/argmin() over a "
                 "Poisson/GOE/GUE KS triple. A file is a storage convention. "
                 "run_analytical_nns.py holds two decisions (min at :184, "
                 "np.argmin at :249) and is two rows, two verdicts, two migrations.")

UNSWEPT_AS_DISTINCT_UNITS = ("run_analytical_nns.py:249",)


# ── R5 — SCOPE OF THE COMPARE-DIRECTIVE, AND ITS LINEAGE WARRANT ─────────────
#
# Promote every _ks_pvalue-idiom quantity and kin: in the reconciled classifier
# each is COMPARED against a threshold. The threshold is a constant, so it goes
# through classify_guard like any other — 0.05 named as convention unless
# someone derives it, which nobody will.
PROMOTED_FAMILIES = ("ks_*", "pv_*", "p_*")
REJECTION_ALPHA = 0.05

# THE LINEAGE FINDING — belongs in the reconciled source itself, because every
# future reader will wonder whether clause 8 was editorial.
#
# `p_two` appears at five sites, computed by the same _ks_pvalue idiom:
#     run_decisive.py:247       if ks_two > 0.10 and p_two < 0.05     COMPARED
#     run_controls.py:287       if ks_two < 0.10 and p_two > 0.05     COMPARED
#     run_calibration.py:318    (ks_two > 0.10 and p_two < 0.05)      COMPARED
#     run_analytical_nns.py:266 print(f"... p={p_two:.4f}")           PRINTED ONLY
#
# The comparison at run_decisive:247 is the ANCESTOR'S BEHAVIOUR, SHED BY
# DESCENDANT COPIES. So the COMPARE-DIRECTIVE restores a rejection region the
# population demonstrably had — it does not impose a policy preference. The
# negative set carried the answer, which is the discriminator's whole thesis
# vindicated at the lineage level.
CLAUSE_8_LINEAGE_RECORD = (
    "COMPARE-DIRECTIVE warrant: p_two is compared against 0.05 at "
    "run_decisive.py:247, run_controls.py:287 and run_calibration.py:318, and "
    "printed without comparison at run_analytical_nns.py:266. The rejection "
    "region is ancestral and was shed by copying. This directive RESTORES it; "
    "it is not an editorial preference. Certified: D2 sensitivity 1/1, "
    "specificity 3/3 against that nearest confusable (gate_census/c3_certify_d2.py)."
)


def threshold_decision(alpha=REJECTION_ALPHA, derivation=None):
    """R5: the rejection threshold is a constant and is typed like any other."""
    return dict(alpha=alpha, kind=classify_guard(alpha, derivation),
                derivation=derivation)


# ── ORDERING CONDITION, mechanical ───────────────────────────────────────────
PRECONDITIONS = {
    "sweep_row_reconciliation": True,    # c3_sweep_reconciliation.json, committed
    "r3_artifact_baselines": False,      # NOT captured
}


def migration_may_begin():
    missing = [k for k, v in PRECONDITIONS.items() if not v]
    if missing:
        raise RulingViolation(
            "MIGRATION NOT AUTHORISED — outstanding preconditions: "
            + ", ".join(missing)
            + ". Baseline before write; the one lapse of that rule this arc cost "
              "1159 records truncated to 3.")
    return True


if __name__ == "__main__":
    print("C3 RULINGS — self-check\n")

    print("R1  silent inheritance is refused:")
    try:
        guard_decision()
        raise SystemExit("R1 FAILED: an unsupplied guard was accepted")
    except RulingViolation as e:
        print(f"    raised: {str(e)[:96]}...")
    print(f"    explicit convention : {guard_decision(50)}")
    print(f"    derived             : {guard_decision(37, derivation='1/RAIL_RATIO')}")

    print("\nR2  translation table:")
    check_no_altered_referent()
    print(f"    canonical {CANONICAL_LABELS}, {len(LABEL_TRANSLATION)} legacy labels mapped")
    print(f"    'Poiss' -> {to_canonical('Poiss')}   'poisson' -> {to_canonical('poisson')}")
    try:
        to_canonical("Wigner")
        raise SystemExit("R2 FAILED: an unmapped label was accepted")
    except RulingViolation as e:
        print(f"    unmapped label raised: {str(e)[:70]}...")

    print("\nR3  observables:")
    for sc in OBSERVABLE_BY_SCOPE:
        print(f"    {sc:7s} {acceptance_observable(sc)}")
    try:
        migration_authorised("module", baseline_captured=False)
        raise SystemExit("R3 FAILED: migration allowed with no baseline")
    except RulingViolation as e:
        print(f"    no-baseline migration raised: {str(e)[:70]}...")

    print(f"\nR4  {COUNTING_RULE}")
    print(f"    unswept as distinct units: {UNSWEPT_AS_DISTINCT_UNITS}")

    print(f"\nR5  promoted families {PROMOTED_FAMILIES}, alpha {REJECTION_ALPHA}")
    print(f"    threshold typing: {threshold_decision()}")

    print("\nORDERING CONDITION:")
    try:
        migration_may_begin()
        raise SystemExit("ORDERING FAILED: migration authorised with baselines uncaptured")
    except RulingViolation as e:
        print(f"    {e}")

    print("\nC3_RULINGS_SELF_TEST_PASS — every ruling refuses its own violation, "
          "and migration remains unauthorised until R3 baselines are captured.")
