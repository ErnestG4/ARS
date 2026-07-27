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

Self-test at the bottom replays the arc's own documented failures and asserts each is caught. A
checker that cannot construct the defect it claims to prevent is an inert guard.
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


def difference(a: Measurement, b: Measurement, allow: tuple = ()) -> tuple:
    """a - b with its sem, after the five-clause check. Returns (diff, sem_or_None)."""
    check(a, b, allow=allow)
    d = a.value - b.value
    s = None
    if a.sem is not None and b.sem is not None:
        s = math.sqrt(a.sem ** 2 + b.sem ** 2)
    return d, s


def bound(estimate: float, sem: float, level: float = 0.95) -> float:
    """Bound on |theta| supported at `level`: the FAR END of the interval, not its half-width.

    This exists because 1.96*sem was written as a bound FOUR times in one arc, the fourth one
    paragraph after the rule was banked. Never compute it by hand again.
    """
    z = {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}.get(level)
    if z is None:
        raise ValueError(f"level {level} not tabulated; add it rather than guessing z")
    return abs(estimate) + z * abs(sem)


def half_width(sem: float, level: float = 0.95) -> float:
    """The CI half-width -- provided separately and named differently so it cannot be mistaken
    for a bound on |theta|."""
    z = {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}[level]
    return z * abs(sem)


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

    # Control: genuinely commensurable pair must NOT raise.
    ok = True
    try:
        check(Measurement(0.06119, quantity="events per unit u", **base),
              Measurement(0.05987, quantity="events per unit u", **base))
    except Incommensurable:
        ok = False
    cases.append(("CONTROL: commensurable pair passes", "-", ok, "no exception" if ok else "FALSE POSITIVE"))

    # bound() vs half_width(): the R-110/R-113 defect.
    b_ = bound(-0.0169, 0.0137)
    hw = half_width(0.0137)
    bound_ok = abs(b_ - 0.0438) < 1e-3 and abs(hw - 0.0269) < 1e-3 and b_ > hw
    cases.append(("bound() != half_width() (R-110/R-113)", "-", bound_ok,
                  f"bound {b_:.4f} vs half-width {hw:.4f}"))

    if verbose:
        print("=== commensurable.py self-test: does the guard catch the arc's OWN failures? ===")
        for name, clause, caught, detail in cases:
            print(f"  [{'PASS' if caught else 'FAIL'}] {name:<42s} ({clause:<17s}) {detail[:60]}")
    n_bad = sum(1 for *_, c, _ in cases if not c)
    if verbose:
        print(f"\n  {len(cases)-n_bad}/{len(cases)} caught. "
              f"{'GUARD IS LIVE.' if n_bad == 0 else 'GUARD IS INERT ON ' + str(n_bad) + ' CASE(S).'}")
    return n_bad == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
