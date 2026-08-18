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
