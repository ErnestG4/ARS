"""Declare what a cell SHARES, so two results cannot be cited as independent when they are one.

A guard module in the shape of `reachable.py`, `railed.py`, `knownanswer.py` and
`spacings.py`: importable, no side effects, and it REFUSES rather than reports.

THE FAILURE IT CATCHES -- the mirror of a variable collision. A collision puts a
correct value in the wrong slot and CORRUPTS a number. This one puts two copies
of the same route in two slots and INFLATES confidence: two results agree, the
agreement is read as independent corroboration, and they were never independent.
It is the more dangerous of the pair precisely because independent-route
agreement is the main defence against everything else.

THIS ARC COMMITTED IT. Stage 2a's P2 arm was written as a CONTINUITY premise:
its central-window reading must agree with Stage 1's. But 2a shares Stage 1's
entire construction -- same analytic semicircle reference, same bisection
placement, same primitive, same statistic. That is one route reported twice. An
independent audit put it exactly right: the check "cannot distinguish 'the two
cells measure the same thing' from 'both are noise around zero'" -- and in fact
the two readings DISAGREE IN SIGN (-0.121% vs +0.727%) and pass only because the
bar is 2.25 sigma of their combined error. I called shared machinery continuity
and banked it as a premise.

INDEPENDENCE IS ALWAYS ABOUT SOMETHING. Two cells sharing a fitter but not data
are independent evidence about the DATA and not about the FITTER. So
`assert_independent` takes the dimension the claim is being made along, and
refuses only if the two cells share THAT dimension. A blanket notion of
independence would either refuse everything useful or permit the case above.
"""
from dataclasses import dataclass
from typing import List

__all__ = ["Lineage", "SharedLineage", "assert_independent", "DIMENSIONS"]

DIMENSIONS = ("construction", "data", "protocol")


class SharedLineage(AssertionError):
    """Two cells were cited as independent along a dimension they share."""


@dataclass(frozen=True)
class Lineage:
    """What a cell is built from. All fields required; a default hides a share.

    construction -- the physical/numerical object and how it was built
                    ("analytic-semicircle + bisection placement")
    data         -- which banked or generated numbers it reads
                    ("gate-D perturbed lattice, eta sweep" / "science n=4096")
    protocol     -- the estimator, fitter, error model, bootstrap
                    ("F3 multi-start, absolute_sigma, replicate bootstrap")
    """
    cell: str
    construction: str
    data: str
    protocol: str

    def shared_with(self, other: "Lineage") -> List[str]:
        return [d for d in DIMENSIONS if getattr(self, d) == getattr(other, d)]

    def record(self) -> dict:
        return dict(cell=self.cell, construction=self.construction,
                    data=self.data, protocol=self.protocol)


def assert_independent(a: Lineage, b: Lineage, about: str) -> None:
    """REFUSE unless `a` and `b` are independent along `about`.

    Call this wherever two cells' agreement is about to be used as
    corroboration. Raises SharedLineage; returns None on success.
    """
    if about not in DIMENSIONS:
        raise ValueError(f"`about` must be one of {DIMENSIONS}, got {about!r}")
    if getattr(a, about) == getattr(b, about):
        shared = a.shared_with(b)
        raise SharedLineage(
            f"refusing to treat {a.cell!r} and {b.cell!r} as independent "
            f"evidence about {about!r}: they share it.\n"
            f"    {a.cell}.{about} = {getattr(a, about)!r}\n"
            f"    {b.cell}.{about} = {getattr(b, about)!r}\n"
            f"  shared dimensions: {', '.join(shared)}\n"
            "  Their agreement is one route reported twice. Agreement between "
            "cells that share the dimension under claim is not corroboration; "
            "it is reproduction, and should be reported as such.")
