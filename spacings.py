"""Unfolded spacings that carry the estimator that produced them.

A guard module in the shape of `reachable.py`, `railed.py` and `knownanswer.py`:
importable, no side effects, and it REFUSES rather than reports.

WHY THIS EXISTS, AND WHY IT IS NARROW
-------------------------------------
"Unfolded spacings" is the one quantity in this repo where two defensible
derivations produce DIFFERENT NUMBERS rather than merely different labels. The
same three words mean at least:

  * unfolded against an ANALYTIC reference (Gate D: semicircle, exact),
  * unfolded against an EMPIRICAL reference (the science: F_empirical of a finite
    seed, free-convolved),
  * with the RAW CDF at bandwidth eps, or with the RICHARDSON pair 2F(eps)-F(2eps),
  * over the CENTRAL bulk window, or over some other section.

Measured cost of conflating the first pair: an additive contribution of 2.6e-03
to 1-<r~> (recert_finite_seed, 2026-09-13) -- larger than every reading the
science makes past k=16. Measured cost of conflating the third pair: a
configuration placed by inverting the raw CDF and read back through the
Richardson pair read +8.92% against a known answer, with the discrepancy
identical at two grid densities so it could not be interpolation. Three of the
seven failed Gate D constructions were this collision.

Full symbol tagging across the ~90 files that use `q` for four different things
is too heavy to retrofit. This targets the one place the collision has actually
cost measurements, and does it at CONSTRUCTION TIME, which is the rule this
repo already applies to ranges (`reachable.Bar` refuses an unreachable bar) and
to rails (`railed.Bounded.__float__` refuses a railed value).

WHAT IT DOES NOT CATCH. Two genuinely different quantities that happen to share
an `Unfolding` tag will still combine freely -- the tag is only as good as the
fields you put in it. And it says nothing about the MIRROR failure, where two
routes agree because they secretly share machinery; that is what a lineage
declaration is for, not this.
"""
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

__all__ = ["Unfolding", "Spacings", "Tagged", "ProvenanceMismatch"]


class ProvenanceMismatch(TypeError):
    """Two values were combined whose unfolding estimators are not the same."""


@dataclass(frozen=True)
class Unfolding:
    """The estimator that turned positions into spacings. All fields required.

    No defaults, deliberately: a default would let a caller omit the field that
    distinguishes their case from someone else's, which is the failure this
    module exists to prevent.
    """
    reference: str        # "analytic-semicircle" | "empirical-n4096" | ...
    arm: str              # "richardson" | "raw-eps" | "raw-2eps"
    eps_over_delta: float # bandwidth in units of the local mean spacing
    window: str           # "bulk-0.20" | "section-0.95-0.05" | "full"

    def key(self) -> Tuple:
        return (self.reference, self.arm, round(float(self.eps_over_delta), 12),
                self.window)

    def __str__(self) -> str:
        return (f"{self.reference}/{self.arm}@{self.eps_over_delta:g}"
                f"/{self.window}")


def _check(a: "Unfolding", b: "Unfolding", op: str) -> None:
    if a.key() != b.key():
        diff = [f for f in ("reference", "arm", "eps_over_delta", "window")
                if getattr(a, f) != getattr(b, f)]
        raise ProvenanceMismatch(
            f"refusing {op}: these were unfolded differently, and the difference "
            f"is in {', '.join(diff)}.\n    left  = {a}\n    right = {b}\n"
            "  Unfolded spacings from different estimators are different "
            "quantities, not the same quantity measured twice. If the comparison "
            "is genuinely intended, re-unfold one side or state the conversion "
            "explicitly.")


@dataclass(frozen=True)
class Tagged:
    """A scalar that remembers how it was unfolded. Arithmetic ACROSS tags refuses.

    `float(t)` always works -- unlike `railed.Bounded`, the tag is not a rail and
    the value is not suspect on its own. What is suspect is combining it with a
    value that came from a different estimator.
    """
    value: float
    unfolding: Unfolding
    name: str = ""

    def __float__(self) -> float:
        return float(self.value)

    def _binop(self, other, fn, op):
        if isinstance(other, Tagged):
            _check(self.unfolding, other.unfolding, op)
            return Tagged(fn(self.value, other.value), self.unfolding,
                          f"({self.name} {op} {other.name})")
        return Tagged(fn(self.value, float(other)), self.unfolding, self.name)

    def __sub__(self, o):      return self._binop(o, lambda a, b: a - b, "-")
    def __add__(self, o):      return self._binop(o, lambda a, b: a + b, "+")
    def __truediv__(self, o):  return self._binop(o, lambda a, b: a / b, "/")
    def __mul__(self, o):      return self._binop(o, lambda a, b: a * b, "*")

    def ratio_to(self, other: "Tagged") -> float:
        """Bias-style ratio. Refuses across estimators; returns a bare float."""
        _check(self.unfolding, other.unfolding, "ratio_to")
        return float(self.value) / float(other.value)

    def __repr__(self) -> str:
        return (f"Tagged({self.value!r}, {self.unfolding}"
                + (f", {self.name!r})" if self.name else ")"))


@dataclass(frozen=True)
class Spacings:
    """Unfolded spacings plus the estimator that produced them."""
    values: np.ndarray
    unfolding: Unfolding
    substrate: str

    @staticmethod
    def from_positions(positions, unfolding: Unfolding, substrate: str,
                       allow_nonpositive: bool = False) -> "Spacings":
        s = np.diff(np.asarray(positions, dtype=np.float64))
        bad = int(np.count_nonzero(s <= 0))
        if bad and not allow_nonpositive:
            raise ValueError(
                f"{bad} of {s.size} gaps are non-positive: the unfolding is not "
                "monotone, so these are not spacings. Pass "
                "allow_nonpositive=True only if you intend to measure that.")
        return Spacings(s, unfolding, substrate)

    def statistic(self, fn, name: str = "") -> Tagged:
        """Apply a gap statistic and keep the provenance attached to the result."""
        return Tagged(float(fn(self.values)), self.unfolding,
                      name or getattr(fn, "__name__", "stat"))

    def rtilde_distance(self) -> Tagged:
        """1 - <r~>, computed as track0_harness.rtilde computes it: no filter."""
        a, b = self.values[:-1], self.values[1:]
        return Tagged(float(1.0 - np.mean(np.minimum(a, b) / np.maximum(a, b))),
                      self.unfolding, "1-<rtilde>")

    def __len__(self) -> int:
        return int(self.values.size)
