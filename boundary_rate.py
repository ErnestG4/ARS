"""Boundary-rate reporting — ONE implementation, ONE named convention.

Why this module exists: a rate at 0.0 or 1.0 has no visible variance, so its
uncertainty must be supplied explicitly.  Two standard intervals DISAGREE at
the borderline — for 4/4, Clopper-Pearson gives a lower bound of 0.398 and
Wilson gives 0.510, i.e. one calls the row uninformative and the other calls
it a result.  A sweep that used one convention and a later re-run that used
the other would flip such a row SILENTLY, and a green board would stay green
through the flip.  So the convention is named here, asserted by checkers, and
computed in one place.

CONVENTION (chosen, and recorded as chosen — see below):

    CONVENTION = "clopper-pearson"   at ALPHA = 0.05

Clopper-Pearson is the exact/conservative interval.  It is the right choice
because a boundary rate is an "AT LEAST" claim: reporting 1.00 asserts a
lower bound, and the conservative bound is the honest one to attach to an
assertion of that shape.

THE 0.5 SPLIT IS A CHOSEN CONVENTION, NOT A DERIVED THRESHOLD.  A rate whose
conservative bound leaves it consistent with a coin flip carries no result;
one whose bound excludes a coin flip is a real but overstated finding.  0.5
is the natural line for an "at least" claim about a fraction, and a bright
line has to sit somewhere -- but nothing derives it, and it should not be
back-justified later as though something did.  It is load-bearing at the
margin: the n=6 row (bound 0.541) sits close enough that a slightly
different convention would move it.
"""

# ── LITERATURE ────────────────────────────────────────────────────────────────
# Swept 2026-09-06. FULLY NAMED — and the literature says something sharper
# than this module currently does. Nothing here is ours.
LITERATURE = dict(
    status="NAMED",
    note="THE CITATION TRAP, and it is the actionable part. Brown, Cai & "
         "DasGupta, Statistical Science 16(2), 2001, explicitly REJECT our "
         "convention in general: 'The Clopper-Pearson interval is wastefully "
         "conservative and is not a good choice for practical use.' Citing BCD "
         "as endorsing Clopper-Pearson would be caught instantly by a careful "
         "reader. BUT their §4.1 'Boundary modification' is the section that "
         "governs THIS module, and there the position reverses.",
    anchors=[
        "Brown, Cai & DasGupta, Statist. Sci. 16(2), 2001, 101-133. Headline: "
        "Wilson or Jeffreys for n <= 40, Agresti-Coull for n >= 40. §4.1: "
        "Wilson's coverage has downward spikes near 0 and 1 that 'exist for "
        "all n and alpha' — i.e. PLAIN WILSON IS KNOWN-DEFECTIVE IN EXACTLY "
        "THE REGION THIS MODULE GOVERNS.",
        "AND THE BOUNDARY FIX IS ARITHMETICALLY OURS. BCD's modified-Jeffreys "
        "sets L(n) = (alpha/2)^(1/n). VERIFIED HERE at n=4, alpha=0.05: "
        "L(n) = 0.397635364, Clopper-Pearson lower = 0.397635364, identical to "
        "double precision. Agresti & Coull's published Comment says it "
        "outright: 'substituting the Clopper-Pearson limits in those cases' is "
        "the fix at x=0 and x=n.",
        "Clopper & Pearson, Biometrika 26, 1934; Wilson, JASA 22, 1927; "
        "Agresti & Coull, Am. Statistician 52(2), 1998.",
        "Hanley & Lippman-Hand, JAMA 249(13), 1983 — the RULE OF THREE for "
        "zero numerators, [0, 3/n]. Good only for n > 30: at n=4 it gives "
        "0.75 against an exact CP upper of 0.602, so it does NOT apply at this "
        "module's scale.",
        "The silent-flip half is named too: multiverse analysis (Steegen et "
        "al., PPS 11(5), 2016) and vibration of effects (Patel, Burford & "
        "Ioannidis, J Clin Epidemiol 68(9), 2015).",
    ],
    cite_this_way="BCD §4.1 (boundary modification) and the Agresti & Coull "
                  "Comment — NOT the headline recommendation, which rejects "
                  "Clopper-Pearson for interior use.",
    searched="binomial-interval literature, 2026-09-06. THE STRONGEST-BACKED "
             "ENTRY IN THIS REPO'S ANCHORS, and deliberately so: the BCD paper "
             "was retrieved and text-extracted in full (33 pages), and every "
             "NUMERICAL claim was then RE-COMPUTED IN-REPO rather than taken "
             "from the review — CP lower for 4/4 = 0.397635364, Wilson lower = "
             "0.510109163, BCD's modified-Jeffreys L(n) = (alpha/2)^(1/n) = "
             "0.397635364, identical to CP to double precision. When the same "
             "sweep's Rule 1 and Rule 3 sections were withdrawn as fabricated, "
             "this section stood, and the independent arithmetic is why it can "
             "be trusted rather than merely believed.",
)


from scipy.stats import beta

CONVENTION = "clopper-pearson"
ALPHA = 0.05
COIN_FLIP_SPLIT = 0.5          # chosen, not derived (see module docstring)


def interval(k: int, n: int, alpha: float = ALPHA):
    """Exact (Clopper-Pearson) two-sided interval for k successes of n."""
    if n <= 0:
        raise ValueError("a rate needs a denominator — that is the whole point")
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def classify(k: int, n: int, alpha: float = ALPHA) -> dict:
    """Treatment for a banked boundary rate.

    UNINFORMATIVE          — the interval is consistent with a coin flip; the
                             row carries no result and must be marked so.
    OVERSTATED_RESTATE     — a real finding, but the point value overstates
                             it; restate at the bound.
    NOT_AT_BOUNDARY        — ordinary rate; this module has nothing to add.
    """
    lo, hi = interval(k, n, alpha)
    if k == n:
        kind = ("UNINFORMATIVE" if lo < COIN_FLIP_SPLIT else "OVERSTATED_RESTATE")
        claim = f">= {lo:.3f}"
    elif k == 0:
        kind = ("UNINFORMATIVE" if hi > COIN_FLIP_SPLIT else "OVERSTATED_RESTATE")
        claim = f"<= {hi:.3f}"
    else:
        kind, claim = "NOT_AT_BOUNDARY", f"[{lo:.3f}, {hi:.3f}]"
    return dict(k=k, n=n, rate=k / n, lo=lo, hi=hi, convention=CONVENTION,
                alpha=alpha, split=COIN_FLIP_SPLIT, treatment=kind,
                honest_claim=claim)


# orientation table, and the self-test that pins the convention
_EXPECTED_CP_LOWER = {4: 0.398, 6: 0.541, 8: 0.631, 10: 0.692, 12: 0.735,
                      17: 0.805, 32: 0.891, 60: 0.940}


def self_test() -> None:
    """Assert the named convention actually is what is computed. A checker
    calls this, so a re-run under a different convention fails loudly instead
    of silently reclassifying rows."""
    assert CONVENTION == "clopper-pearson", CONVENTION
    for n, want in _EXPECTED_CP_LOWER.items():
        got = interval(n, n)[0]
        assert abs(got - want) < 5e-4, (n, got, want)
    # the borderline row: the convention DECIDES it
    assert classify(4, 4)["treatment"] == "UNINFORMATIVE"
    assert classify(6, 6)["treatment"] == "OVERSTATED_RESTATE"


if __name__ == "__main__":
    self_test()
    print(f"convention = {CONVENTION}, alpha = {ALPHA}, "
          f"split = {COIN_FLIP_SPLIT} (chosen, not derived)")
    for n in sorted(_EXPECTED_CP_LOWER):
        c = classify(n, n)
        print(f"  {n:>3}/{n:<3} lower {c['lo']:.3f}  {c['treatment']}")
