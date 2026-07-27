"""
commensurable.py — the five-clause check, MECHANIZED.

Ten instances across four programs were one defect: the two sides of a comparison were not
commensurable. The rule was banked in memory as a principle, and a principle is exactly what the
sem-vs-CI rule was when it failed a FOURTH time one paragraph after being written down.

Rules that need remembering have failed here repeatedly. Rules in code have held. So:

    Measurement(value, sem, quantity=, units=, domain=, unit_of_analysis=, conditioning=)

carries the metadata the check needs, and `compare()` REFUSES rather than assumes. Three clauses
(units, domain, unit_of_analysis) are pure metadata equality; `quantity` and `conditioning` are too,
but they are the two that fail invisibly, so they are required with no default.

Also here, because it is the same failure mode: `bound()`, so that nobody hand-writes 1.96*se as a
bound on |theta| again. The bound is the FAR END of the interval, not its half-width.

SELF-TEST DISCIPLINE — welded here so it is not lost:

  The sensitivity corpus is this arc's OWN corpse pile, not invented cases. A guard tested against
  synthetic defects proves it catches defects someone could IMAGINE; a guard tested against the
  defects that actually got past proves it catches the ones intuition does not flag. Those are
  different sets and only the second matters.

  THEREFORE: every future slot error this guard fails to catch becomes the next sensitivity case.
  The corpus grows by REAL ESCAPES, never by invented ones -- otherwise it drifts back toward
  testing imagination instead of history.

  And sensitivity is tested SEPARATELY from specificity, with a battery on each. A guard that
  raises on everything scores 100% on a rejection-only suite; that is the always-red-light failure,
  and one control row is a single witness against it.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


class Incommensurable(Exception):
    """Raised when two sides of a comparison do not match on a required clause."""


CLAUSES = ("quantity", "units", "domain", "unit_of_analysis", "conditioning")


@dataclass(frozen=True)
class Measurement:
    value: float
    sem: Optional[float] = None
    n: Optional[int] = None
    quantity: str = ""            # WHAT is measured. "" is rejected -- no silent default.
    units: str = ""
    domain: str = ""              # EXTENT: the range/support the value was computed over.
    unit_of_analysis: str = ""    # polynomials? fields? blocks? events?
    conditioning: str = ""        # SELECTION on the values themselves. "none" is explicit.
    note: str = ""

    def __post_init__(self):
        missing = [c for c in CLAUSES if not getattr(self, c)]
        if missing:
            raise Incommensurable(
                f"Measurement '{self.quantity or '<unnamed>'}' is missing required clause(s): "
                f"{missing}. Every clause must be stated -- an unstated clause is the one that fails "
                f"invisibly. Use 'none' explicitly where a clause genuinely does not apply."
            )


def check(a: Measurement, b: Measurement, allow: tuple = ()) -> None:
    """Raise unless a and b agree on all five clauses. `allow` names clauses deliberately waived,
    which forces the waiver to be written down at the call site rather than assumed."""
    for side, m in (("first", a), ("second", b)):
        if not isinstance(m, Measurement):
            raise Incommensurable(
                f"{side} argument is {type(m).__name__}, not a Measurement. The clauses cannot be "
                "checked on a bare value -- which is precisely how an unstated clause takes a "
                "silent default. Wrap it: Measurement(value, quantity=..., units=..., domain=..., "
                "unit_of_analysis=..., conditioning=...)."
            )
    bad = []
    for c in CLAUSES:
        if c in allow:
            continue
        if getattr(a, c) != getattr(b, c):
            bad.append(f"{c}: {getattr(a, c)!r} vs {getattr(b, c)!r}")
    if bad:
        raise Incommensurable(
            "Not commensurable:\n  " + "\n  ".join(bad) +
            "\n  (waive explicitly with allow=(...) if the mismatch is intended and harmless)"
        )


def difference(a: Measurement, b: Measurement, allow: tuple = ()) -> Difference:
    """a - b after the five-clause check. Returns a Difference (NOT a tuple), so the follow-on
    operations are methods that cannot be mis-composed."""
    check(a, b, allow=allow)
    s = None
    if a.sem is not None and b.sem is not None:
        s = math.sqrt(a.sem ** 2 + b.sem ** 2)
    return Difference(a.value - b.value, s, a.quantity)


_Z = {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}


class _Scalar:
    """Base for typed scalars. Deliberately NOT float-convertible: the original defect was not a
    NAME collision (calling a half-width a bound) but a USAGE collision (passing a half-width where
    a bound was required). Naming alone leaves that advisory. Withholding __float__ makes the
    substitution a TypeError at the boundary instead of a wrong number in a sentence."""
    __slots__ = ("value", "level")

    def __init__(self, value, level):
        self.value, self.level = float(value), level

    def __repr__(self):
        return f"{type(self).__name__}({self.value:.6g}, level={self.level})"

    def __format__(self, spec):
        return format(self.value, spec)


class Bound(_Scalar):
    """A bound on |theta| at `level`: the FAR END of the interval."""


class HalfWidth(_Scalar):
    """A CI half-width. NOT a bound on |theta|. Cannot be passed where a Bound is required."""


def bound(estimate: float, sem: float, level: float = 0.95) -> Bound:
    """Bound on |theta|: |estimate| + z*sem -- the FAR END of the interval, not its half-width.

    1.96*sem was written as a bound FOUR times in one arc, the fourth one paragraph after the rule
    was banked. Returns a typed Bound so the result cannot be silently swapped for a half-width.
    """
    if level not in _Z:
        raise ValueError(f"level {level} not tabulated; add it rather than guessing z")
    return Bound(abs(estimate) + _Z[level] * abs(sem), level)


def half_width(sem: float, level: float = 0.95) -> HalfWidth:
    """The CI half-width. Typed distinctly so it cannot be USED as a bound, not merely named apart."""
    if level not in _Z:
        raise ValueError(f"level {level} not tabulated; add it rather than guessing z")
    return HalfWidth(_Z[level] * abs(sem), level)


def require_bound(x) -> Bound:
    """Boundary guard for anything that consumes a bound on |theta|."""
    if not isinstance(x, Bound):
        raise TypeError(
            f"expected a Bound (the far end of the interval); got {type(x).__name__}. "
            "A HalfWidth or a bare float is not a bound on |theta| -- use bound(estimate, sem)."
        )
    return x


@dataclass(frozen=True)
class Difference:
    """Result of difference(). Carries the correct follow-on operations as METHODS so nobody
    reconstructs 1.96*sem by hand from a returned tuple."""
    value: float
    sem: Optional[float]
    quantity: str

    def bound(self, level: float = 0.95) -> Bound:
        if self.sem is None:
            raise ValueError("no sem: cannot form a bound")
        return bound(self.value, self.sem, level)

    def half_width(self, level: float = 0.95) -> HalfWidth:
        if self.sem is None:
            raise ValueError("no sem: cannot form a half-width")
        return half_width(self.sem, level)

    def sem_units(self) -> float:
        if not self.sem:
            raise ValueError("no sem: cannot express in sem units")
        return self.value / self.sem


# ────────────────────────────────────────────────────────────────────────────
# Self-test: replay the arc's OWN documented failures. A guard that cannot construct
# the defect it prevents is inert (banked doctrine), so each of these must be caught.
# ────────────────────────────────────────────────────────────────────────────
def _selftest(verbose=True):
    cases = []

    def case(name, a, b, clause, allow=()):
        try:
            check(a, b, allow=allow)
            cases.append((name, clause, False, "NOT CAUGHT"))
        except Incommensurable as e:
            cases.append((name, clause, clause in str(e), str(e).split("\n")[1].strip()))

    base = dict(units="dimensionless", domain="full", unit_of_analysis="event", conditioning="none")

    # R-104: fungal's density derivatives used to size SOLAR's floor.
    case("fungal m' sizing solar's floor",
         Measurement(0.2530, quantity="dm/dc at c=1", **{**base, "domain": "fungal spacings"}),
         Measurement(0.2985, quantity="dm/dc at c=1", **{**base, "domain": "solar spacings"}),
         "domain")

    # R-078: 24 polynomials treated as 24 fields.
    case("polynomial units vs field units",
         Measurement(0.06119, sem=0.00113, quantity="events per unit u",
                     **{**base, "unit_of_analysis": "polynomial"}),
         Measurement(0.06148, sem=0.00101, quantity="events per unit u",
                     **{**base, "unit_of_analysis": "field"}),
         "unit_of_analysis")

    # R-084/R-077: P(g) vs P(g | event) -- passes the other four, fails on conditioning.
    case("P(g) vs P(g|event)",
         Measurement(0.0674, quantity="P(g=13)", **base),
         Measurement(0.1077, quantity="P(g=13)", **{**base, "conditioning": "lambda >= 20"}),
         "conditioning")

    # R-083: Gauss-Kuzmin a-tail used where the lambda-tail belongs.
    case("a-tail vs lambda-tail",
         Measurement(0.070389, quantity="P(a >= A)", **base),
         Measurement(0.072135, quantity="P(lambda >= A)", **base),
         "quantity")

    # R-114: solar's floor applied to fungal's row.
    case("solar floor applied to fungal",
         Measurement(0.20, quantity="mass03 margin", **{**base, "domain": "solar"}),
         Measurement(0.4098, quantity="mass03 margin", **{**base, "domain": "fungal"}),
         "domain")

    # R-088: mismatched certified domains.
    case("mismatched certified domains",
         Measurement(1.0, quantity="lambda", **{**base, "domain": "i < len(a0)-45"}),
         Measurement(1.0, quantity="lambda", **{**base, "domain": "k < len(a1)-45"}),
         "domain")

    # ── SPECIFICITY BATTERY ──────────────────────────────────────────────────
    # Seven rejection tests prove the guard REJECTS. A guard that raises on everything also scores
    # 7/7 on a rejection-only suite -- which is the always-red-light failure fixed in the ratchet one
    # item over. The control is the ONLY thing separating "live guard" from "always red", and one
    # control row is a single witness. So: a battery, across different clause-combinations, each of
    # which MUST pass.
    passes = []

    def must_pass(name, a, b, allow=()):
        try:
            check(a, b, allow=allow)
            passes.append((name, True, "passed"))
        except Incommensurable as e:
            passes.append((name, False, "FALSE POSITIVE: " + str(e).split(chr(10))[1].strip()))

    must_pass("identical clauses, different values",
              Measurement(0.06119, quantity="events per unit u", **base),
              Measurement(0.05987, quantity="events per unit u", **base))
    must_pass("differ only in sem",
              Measurement(1.0, sem=0.1, quantity="q", **base),
              Measurement(1.0, sem=0.9, quantity="q", **base))
    must_pass("differ only in n",
              Measurement(1.0, n=10, quantity="q", **base),
              Measurement(1.0, n=9000, quantity="q", **base))
    must_pass("differ only in note (not a clause)",
              Measurement(1.0, quantity="q", note="from run A", **base),
              Measurement(1.0, quantity="q", note="from run B", **base))
    must_pass("matched non-trivial conditioning",
              Measurement(0.11, quantity="P(g=t)", **{**base, "conditioning": "lambda >= 20"}),
              Measurement(0.10, quantity="P(g=t)", **{**base, "conditioning": "lambda >= 20"}))
    must_pass("matched field-level unit of analysis",
              Measurement(0.061, quantity="ev/u", **{**base, "unit_of_analysis": "field"}),
              Measurement(0.060, quantity="ev/u", **{**base, "unit_of_analysis": "field"}))
    must_pass("matched non-dimensionless units",
              Measurement(2.5, quantity="lag", **{**base, "units": "log-denominator"}),
              Measurement(2.6, quantity="lag", **{**base, "units": "log-denominator"}))
    must_pass("matched restricted domain",
              Measurement(1.0, quantity="q", **{**base, "domain": "n >= 200"}),
              Measurement(1.1, quantity="q", **{**base, "domain": "n >= 200"}))
    must_pass("DELIBERATE waiver via allow= is honoured",
              Measurement(1.0, quantity="q", **{**base, "domain": "fungal"}),
              Measurement(1.1, quantity="q", **{**base, "domain": "solar"}),
              allow=("domain",))

    # Interface tests: the USAGE collision, not just the name collision.
    iface = []

    def iface_test(name, fn):
        try:
            fn(); iface.append((name, False, "NOT CAUGHT"))
        except (TypeError, Incommensurable) as e:
            iface.append((name, True, type(e).__name__))

    iface_test("bare float rejected by check()", lambda: check(0.5, 0.6))
    iface_test("HalfWidth rejected by require_bound()", lambda: require_bound(half_width(0.0137)))
    iface_test("bare float rejected by require_bound()", lambda: require_bound(0.0269))
    iface_test("HalfWidth is not float-convertible", lambda: float(half_width(0.0137)))
    b_ = bound(-0.0169, 0.0137)
    iface.append(("Bound accepted by require_bound()", require_bound(b_) is b_, "ok"))
    iface.append(("bound() > half_width() on same sem", b_.value > half_width(0.0137).value,
                  f"{b_.value:.4f} > {half_width(0.0137).value:.4f}"))
    d_ = difference(Measurement(0.8838, sem=0.0102, quantity="recovery", **base),
                    Measurement(0.8914, sem=0.0103, quantity="recovery", **base))
    iface.append(("difference() returns Difference, not a tuple", isinstance(d_, Difference),
                  f"bound={d_.bound().value:.4f}"))

    n_sens = sum(1 for *_, c, _ in cases if not c)
    n_spec = sum(1 for _, ok, _ in passes if not ok)
    n_ifc = sum(1 for _, ok, _ in iface if not ok)
    if verbose:
        print("=== commensurable.py self-test ===")
        print("\n-- SENSITIVITY: does it catch the arc's OWN documented failures? --")
        for name, clause, caught, detail in cases:
            print(f"  [{'PASS' if caught else 'FAIL'}] {name:<40s} ({clause:<17s}) {detail[:52]}")
        print("\n-- SPECIFICITY: does it ACCEPT genuinely commensurable pairs? --")
        print("   (checked separately, and with a battery: sensitivity and specificity are")
        print("    orthogonal by construction, and one control row is a single witness)")
        for name, ok, detail in passes:
            print(f"  [{'PASS' if ok else 'FAIL'}] {name:<40s} {detail[:52]}")
        print("\n-- INTERFACE: is the USAGE collision closed, not just the name collision? --")
        for name, ok, detail in iface:
            print(f"  [{'PASS' if ok else 'FAIL'}] {name:<40s} {detail[:52]}")
        tot = len(cases) + len(passes) + len(iface)
        bad = n_sens + n_spec + n_ifc
        print(f"\n  sensitivity {len(cases)-n_sens}/{len(cases)}   "
              f"specificity {len(passes)-n_spec}/{len(passes)}   "
              f"interface {len(iface)-n_ifc}/{len(iface)}   ->  {tot-bad}/{tot}")
        print(f"  {'GUARD IS LIVE AND SPECIFIC.' if bad == 0 else 'GUARD FAILS ' + str(bad) + ' CASE(S).'}")
    return (n_sens + n_spec + n_ifc) == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
