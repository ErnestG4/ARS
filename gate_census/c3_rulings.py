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
_CHOSEN = {}          # R1: ONE convention constant, process-wide


def guard_decision(n_min=_UNSET, derivation=None, _registry=_CHOSEN):
    """The reconciled classifier's guard MUST come through here.

    `n_min` has no default, deliberately. A default is silent inheritance with
    extra steps: it picks one variant's free constant and makes every call site
    that omits the argument agree with it without anyone deciding anything.

    DERIVATION MUST CLOSE, NOT MERELY BE NAMED (amended 2026-08-23).
    The sealed `classify_guard` treats naming as the test — "a derivation you
    cannot write is a derivation you do not have" — and that sealed contract is
    left alone. But an audit demonstrated `derivation="banana"` minting DERIVED,
    so naming is one bit: said-nothing vs said-anything. The GENERIC side stays
    sound (silence is correctly typed as policy); the DERIVED side certified
    nothing.

    So here `derivation` must be a CALLABLE that is EVALUATED and must return
    the constant. This is countrecon's literal-delta lesson in another coat: a
    claim derived from the thing it certifies is no claim, and the arithmetic
    closing is what forces the derivation to be real. A string is still accepted
    and still types as GENERIC — naming without closing is policy.

    R1 SINGULARITY: the ruling says ONE convention constant. A second, different
    free constant in the same process is the 50/5 fork surviving migration one
    call site at a time, so it is refused.
    """
    if n_min is _UNSET:
        raise RulingViolation(
            "R1: n_min was not supplied. The 50/5/none fork is free constants, "
            "none of which has a claim to inherit — choose one explicitly, or "
            "derive one and let the derivation close. " + R1_FORBIDDEN)

    if callable(derivation):
        produced = derivation()
        if produced != n_min:
            raise RulingViolation(
                f"R1: the derivation returned {produced!r} but the guard is "
                f"{n_min!r}. A derivation that does not reproduce the constant "
                "is not the constant's derivation.")
        kind = classify_guard(n_min, getattr(derivation, "__name__", "derivation"))
        name = getattr(derivation, "__name__", "<callable>")
    else:
        if derivation:
            # named but not closing: policy wearing a derivation's clothes
            kind, name = GUARD_GENERIC, f"{derivation} (NAMED, NOT CLOSED)"
        else:
            kind, name = GUARD_GENERIC, None

    if kind == GUARD_GENERIC:
        prev = _registry.get("convention")
        if prev is not None and prev != int(n_min):
            raise RulingViolation(
                f"R1: a convention guard of {prev} was already chosen; {int(n_min)} "
                "is a second one. The ruling permits ONE convention constant — a "
                "second is the 50/5 fork surviving migration one call site at a time.")
        _registry["convention"] = int(n_min)

    return dict(n_min=int(n_min), kind=kind, derivation=name,
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


# F4: the check derived the expected referent from the label's own SPELLING, so
# any entry outside those three patterns passed with an arbitrary referent
# (`LABEL_TRANSLATION["Wigner"]="Poisson"` was accepted). The error message
# demanded a referent be "stated" while the table had nowhere to state one. It
# does now, and every entry must appear here.
LABEL_REFERENT = {
    "Poiss":   "Poisson",  "Poisson": "Poisson",  "poisson": "Poisson",
    "GOE":     "GOE",      "goe":     "GOE",
    "GUE":     "GUE",      "gue":     "GUE",
}


def check_no_altered_referent():
    """Constraint (i), mechanically: a legacy label must map to the class it
    always denoted. Reuse with an altered referent is refused here rather than
    discovered by a reader of old artifacts."""
    for legacy, canon in LABEL_TRANSLATION.items():
        if legacy not in LABEL_REFERENT:
            raise RulingViolation(
                f"R2: '{legacy}' is in the translation table with no DECLARED "
                "referent. Add it to LABEL_REFERENT — an entry whose meaning is "
                "asserted only by its spelling is what constraint (i) forbids.")
        if LABEL_REFERENT[legacy] != canon:
            raise RulingViolation(
                f"R2: '{legacy}' is declared to denote {LABEL_REFERENT[legacy]} "
                f"but maps to {canon}. A label that changes referent is worse "
                "than a new label: old readings stay valid while becoming false.")
        if canon not in CANONICAL_LABELS:
            raise RulingViolation(f"R2: '{legacy}' maps outside the canonical set")
    for legacy in LABEL_REFERENT:
        if legacy not in LABEL_TRANSLATION:
            raise RulingViolation(f"R2: '{legacy}' declares a referent but maps nowhere")
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


def migration_authorised(site_scope, baseline_path=None, expected_sha=None):
    """Migration may introduce a function call where there was script code ONLY
    under the artifact-identity gate. Baseline before write.

    AMENDED 2026-08-23: this took a caller-supplied boolean, so
    `migration_authorised("module", baseline_captured=True)` returned True with
    no baseline anywhere in existence — the one gate the arc's next step depends
    on, enforced by self-report. It also validated `site_scope` only on the
    failure branch, so an unknown scope passed. Both are fixed: the scope is
    checked FIRST, and the baseline must be a FILE THAT EXISTS whose sha256
    matches what the caller claims.
    """
    observable = acceptance_observable(site_scope)      # validates scope on BOTH paths
    if not baseline_path:
        raise RulingViolation(
            f"R3: no baseline path given for a '{site_scope}' site. The observable "
            f"is: {observable}. Capture it to a file before writing.")
    if not os.path.exists(baseline_path):
        raise RulingViolation(
            f"R3: baseline '{baseline_path}' does not exist. A gate that accepts "
            "the claim of a baseline instead of the baseline is not a gate.")
    import hashlib
    actual = hashlib.sha256(open(baseline_path, "rb").read()).hexdigest()
    if expected_sha and actual != expected_sha:
        raise RulingViolation(
            f"R3: baseline '{baseline_path}' hashes {actual[:16]}…, expected "
            f"{expected_sha[:16]}…. The baseline moved before the migration it gates.")
    return dict(scope=site_scope, baseline=baseline_path, sha256=actual)


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
    """R5: the rejection threshold is a constant and is typed like any other —
    including the closing requirement. `derivation="vibes"` minted DERIVED before
    2026-08-23."""
    if callable(derivation):
        produced = derivation()
        if produced != alpha:
            raise RulingViolation(
                f"R5: the derivation returned {produced!r}, not the threshold {alpha!r}")
        return dict(alpha=alpha, kind=classify_guard(alpha, "closed"),
                    derivation=getattr(derivation, "__name__", "<callable>"))
    return dict(alpha=alpha, kind=GUARD_GENERIC,
                derivation=(f"{derivation} (NAMED, NOT CLOSED)" if derivation else None))


# ── ORDERING CONDITION, mechanical ───────────────────────────────────────────
PRECONDITIONS = {
    "sweep_row_reconciliation": True,    # c3_sweep_reconciliation.json, committed
    "r3_artifact_baselines": False,      # NOT captured
}

# Obligations that outlive this module and must travel INTO the migration.
# Tracked here rather than left as a comment saying where they belong — a
# deferred obligation with no slot is a deferred obligation nobody discharges.
DEFERRED_OBLIGATIONS = {
    "clause_8_lineage_into_reconciled_source": {
        "text": CLAUSE_8_LINEAGE_RECORD,
        "destination": "the reconciled classifier's own source",
        "discharged": False},
    "label_translation_routed_at_call_sites": {
        "text": "every label literal in the reconciled classifier passes through "
                "to_canonical(); R2(ii) requires the table be consumed, not stored",
        "destination": "post-migration board row",
        "discharged": False},
    "guard_routed_through_guard_decision": {
        "text": "every guard in the reconciled classifier is obtained from "
                "guard_decision(); enforced by nothing until call sites exist",
        "destination": "post-migration board row",
        "discharged": False},
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
    import tempfile

    print("C3 RULINGS — self-check\n")

    print("R1  refusals:")
    for label, call in (
            ("omitted n_min",            lambda: guard_decision()),
            ("derivation that does not close",
             lambda: guard_decision(50, derivation=lambda: 37)),
    ):
        try:
            call(); raise SystemExit(f"R1 FAILED: {label} was accepted")
        except RulingViolation as e:
            print(f"    {label:34s} raised: {str(e)[:64]}...")
    print(f"    closing derivation  : {guard_decision(37, derivation=lambda: 37)}")
    named = guard_decision(50, derivation='it just is', _registry={})
    print(f"    NAMED but not closed: {named}")
    if named["kind"] != GUARD_GENERIC:
        raise SystemExit("R1 FAILED: a non-closing derivation minted DERIVED")
    reg = {}
    guard_decision(50, _registry=reg)
    try:
        guard_decision(5, _registry=reg)
        raise SystemExit("R1 FAILED: a second convention constant was accepted")
    except RulingViolation as e:
        print(f"    second convention   raised: {str(e)[:62]}...")

    print("\nR2  translation table:")
    check_no_altered_referent()
    print(f"    canonical {CANONICAL_LABELS}, {len(LABEL_TRANSLATION)} legacy labels mapped")
    print(f"    'Poiss' -> {to_canonical('Poiss')}   'poisson' -> {to_canonical('poisson')}")
    for label, mutate in (
            ("unmapped label", lambda: to_canonical("Wigner")),
            ("undeclared referent",
             lambda: (LABEL_TRANSLATION.__setitem__("Wigner", "Poisson"),
                      check_no_altered_referent())),
            ("re-pointed referent",
             lambda: (LABEL_TRANSLATION.__setitem__("Poiss", "GOE"),
                      check_no_altered_referent())),
    ):
        snapshot = dict(LABEL_TRANSLATION)
        try:
            mutate(); raise SystemExit(f"R2 FAILED: {label} accepted")
        except RulingViolation as e:
            print(f"    {label:22s} raised: {str(e)[:58]}...")
        finally:
            LABEL_TRANSLATION.clear(); LABEL_TRANSLATION.update(snapshot)

    print("\nR3  observables + the artifact gate:")
    for sc in OBSERVABLE_BY_SCOPE:
        print(f"    {sc:7s} {acceptance_observable(sc)}")
    for label, call in (
            ("unknown scope",   lambda: migration_authorised("banana", "x", None)),
            ("no baseline path", lambda: migration_authorised("module")),
            ("baseline absent",  lambda: migration_authorised("module", "/nonexistent/b.json")),
    ):
        try:
            call(); raise SystemExit(f"R3 FAILED: {label} accepted")
        except RulingViolation as e:
            print(f"    {label:17s} raised: {str(e)[:56]}...")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        fh.write('{"baseline": true}'); tmp = fh.name
    ok = migration_authorised("module", tmp)
    print(f"    real baseline accepted: sha {ok['sha256'][:16]}...")
    try:
        migration_authorised("module", tmp, expected_sha="0" * 64)
        raise SystemExit("R3 FAILED: a mismatched hash was accepted")
    except RulingViolation as e:
        print(f"    hash mismatch     raised: {str(e)[:56]}...")
    os.unlink(tmp)

    print(f"\nR4  {COUNTING_RULE}")
    print(f"    unswept as distinct units: {UNSWEPT_AS_DISTINCT_UNITS}")

    print(f"\nR5  promoted families {PROMOTED_FAMILIES}, alpha {REJECTION_ALPHA}")
    bogus = threshold_decision(0.5, derivation="vibes")
    print(f"    threshold, named not closed: {bogus}")
    if bogus["kind"] != GUARD_GENERIC:
        raise SystemExit("R5 FAILED: a non-closing threshold derivation minted DERIVED")

    print("\nDEFERRED OBLIGATIONS (travel into the migration):")
    for k, v in DEFERRED_OBLIGATIONS.items():
        print(f"    [{'x' if v['discharged'] else ' '}] {k} -> {v['destination']}")

    print("\nORDERING CONDITION:")
    try:
        migration_may_begin()
        raise SystemExit("ORDERING FAILED: migration authorised with baselines uncaptured")
    except RulingViolation as e:
        print(f"    {e}")

    print("\nC3_RULINGS_SELF_TEST_PASS — every ruling refuses its own violation, "
          "derivations must CLOSE, the R3 gate checks an artifact, and migration "
          "remains unauthorised until R3 baselines are captured.")
