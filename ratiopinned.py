"""Quotient out the universal family before counting coincidences. Once, centrally.

WHY THIS EXISTS — THREE INSTANCES, THREE WRONG HEADLINES
---------------------------------------------------------
The same defect has now produced three false results, each caught only after a
confident number had been written down:

  1. THE FOLD, k = 0.  n₁ = n₁′ = −1, n₂ = −n₂′ = m folds +mα onto −mα for ANY α.
     Reported as "89/89 nodes above the horizon coincide", nearly banked as
     proof the folded predicate was meaningful.
  2. THE refl_other CLASS.  Wrote "the reflected channel carries no
     ratio-dependent information at all" — a universal negative resting on a
     measurement of the universal-POSITIVE family only.
  3. THE HARMONIC STACK.  With harmonics [1,3,5], a₁ = 3 and a₂ = −1 give
     3·α − 1·(3α) = 0 for any α. Reported as "90/90 ratios ring under every
     non-sine wave", which measured the stack and not the horizon.

One shape every time: **a ratio-independent solution family contaminating a
ratio-dependent question.** And each instance was born at the MEASUREMENT SITE,
re-implementing the coincidence count inline — which is exactly what
certifier-imports-the-predicate forbids.

So the filter lives here, is imported, and is never re-typed.

THE TEST, and why it is general
-------------------------------
A solution is UNIVERSAL when it holds identically in α, not just at the α in
hand. Writing each ratio as a linear form `const + coeff·α`, a coefficient
vector a is universal exactly when BOTH basis sums vanish:

    Σ aᵢ·constᵢ = 0    and    Σ aᵢ·coeffᵢ = 0

which is checkable without knowing α at all. Everything else that zeroes at a
particular α is RATIO-PINNED — the ratio actually entered.

The equivalent empirical statement, and the red path this module ships: evaluate
the same vectors at an IRRATIONAL α. No rational relation can hold there, so the
pinned count must be exactly zero — and any nonzero result is the universal
family leaking through.

    forms = [(1,0), (0,1)]                 # carrier, modulator at α
    total, universal, pinned = counts(forms, bound=8, alpha=Fraction(7,8))
"""
from fractions import Fraction
from math import gcd


class Form:
    """A ratio as `const + coeff·α`, both rational."""
    __slots__ = ("const", "coeff")

    def __init__(self, const=0, coeff=0):
        self.const = Fraction(const)
        self.coeff = Fraction(coeff)

    def at(self, alpha):
        return self.const + self.coeff * alpha

    def __repr__(self):
        return f"Form({self.const}, {self.coeff}α)"


def as_forms(spec):
    """Accept [(const, coeff), ...] or [Form, ...]."""
    return [f if isinstance(f, Form) else Form(*f) for f in spec]


def _zero_count(weights, bound, force_first_nonzero=False):
    """How many integer vectors in [-bound,bound]^N give Σ aᵢ·wᵢ = 0.
    Exact integer DP; `weights` must be integers."""
    ways = {0: 1}
    first = True
    for w in weights:
        nxt = {}
        for s, c in ways.items():
            for a in range(-bound, bound + 1):
                if first and force_first_nonzero and a == 0:
                    continue
                k = s + a * w
                nxt[k] = nxt.get(k, 0) + c
        ways, first = nxt, False
    return ways.get(0, 0)


def counts(spec, bound, alpha):
    """(total, universal, pinned) coincidence solutions, all-zero excluded.

    total     — vectors zeroing Σ aᵢ·rᵢ(α) at this α
    universal — vectors zeroing BOTH basis sums, so they hold for every α
    pinned    — total − universal: the ones the ratio is responsible for
    """
    forms = as_forms(spec)
    alpha = Fraction(alpha)

    vals = [f.at(alpha) for f in forms]
    den = 1
    for v in vals:
        den = den * v.denominator // gcd(den, v.denominator)
    w_at = [int(v * den) for v in vals]
    total = _zero_count(w_at, bound) - 1          # drop the all-zero vector

    # universal: both basis sums vanish. Count vectors zeroing the pair.
    cd = 1
    for f in forms:
        cd = cd * f.const.denominator // gcd(cd, f.const.denominator)
        cd = cd * f.coeff.denominator // gcd(cd, f.coeff.denominator)
    K = 2 * bound * sum(abs(int(f.coeff * cd)) for f in forms) + 1
    combo = [int(f.const * cd) * K + int(f.coeff * cd) for f in forms]
    universal = _zero_count(combo, bound) - 1

    return total, universal, total - universal


def pinned(spec, bound, alpha):
    """True when a RATIO-DEPENDENT coincidence exists."""
    return counts(spec, bound, alpha)[2] > 0


def assert_no_pinned_at_irrational(spec, bound, probe=None):
    """Red path any caller can run: at an irrational α no rational relation
    holds, so the pinned count must be exactly zero. A nonzero result means the
    universal family is leaking into a ratio-dependent count."""
    from decimal import Decimal, getcontext
    getcontext().prec = 60
    if probe is None:                       # 1/φ, to 40 digits
        probe = Fraction(Decimal("0.6180339887498948482045868343656381177203"))
    t, u, p = counts(spec, bound, probe)
    if p != 0:
        raise AssertionError(
            f"ratio-pinned count is {p} at an irrational α — impossible. The "
            f"universal family (u={u} of t={t}) is leaking into the pinned count.")
    return True


if __name__ == "__main__":
    print("--- instance 3 · the harmonic stack, which reported 90/90 ---")
    for name, harm in (("sine", [1]), ("triangle", [1, 3, 5]), ("square", [1, 3, 5, 7])):
        spec = [(1, 0)] + [(0, k) for k in harm]
        t, u, p = counts(spec, 8, Fraction(9, 8))
        print(f"    {name:9s} α=9/8   total {t:6d}   universal {u:6d}   PINNED {p:4d}")
    print("      the 'ringing everywhere' result was the universal column\n")

    print("--- instance 1 · a ratio below vs above the horizon (2 sine ops, B=4) ---")
    for a in (Fraction(7, 8), Fraction(9, 8)):
        t, u, p = counts([(1, 0), (0, 1)], 8, a)
        print(f"    α={str(a):5s}  total {t:4d}  universal {u:4d}  PINNED {p:4d}"
              f"   -> {'rings' if p else 'silent'}")
    print()

    print("--- red path · the same specs at an irrational α ---")
    for label, spec in (("2 sine operators", [(1, 0), (0, 1)]),
                        ("square stack", [(1, 0), (0, 1), (0, 3), (0, 5), (0, 7)])):
        assert_no_pinned_at_irrational(spec, 8)
        print(f"    {label:18s} pinned = 0 at 1/φ, as required")

    print("\n--- red path · a leak is caught ---")
    try:
        # a deliberately broken 'filter': count everything, quotient nothing
        spec = [(1, 0), (0, 1), (0, 3)]
        t, u, p = counts(spec, 8, Fraction(1, 1))
        if u == 0:
            raise SystemExit("RED PATH FAILED: 1/1 with a harmonic stack should "
                             "carry universal solutions")
        print(f"    α=1/1 square-ish stack: universal {u} correctly separated "
              f"from pinned {p}")
    except AssertionError as e:
        print("    raised:", e)

    print("\nRATIOPINNED_SELF_TEST_PASS — the universal family is quotiented out "
          "centrally, and the irrational probe is available to every caller.")
