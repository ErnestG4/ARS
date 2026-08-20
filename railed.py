"""Read-through accessor for bounded estimators: the rail status travels WITH the value.

WHY THIS EXISTS.  `cross_substrate/axes.py:294` records rail audit R-178, which
measured `I.8_brody_q` as ENTIRELY RAIL on the Tier-B substrates (allen-hpf-cell
100.0%, buzsaki-port-cell 99.4%, pvc-11 99.4%) and states plainly that those
coordinates "carry no information at all".  An unbounded estimator was written in
response and installed in the registry.  **15,174 banked values are still railed
— 73.8% of every bounded Brody q in the corpus.**

The reason is not neglect.  The bit-identical-retention convention requires that
`I.8_brody_q` keep its key and its value so banked numbers stay comparable, and
that convention is CORRECT and should be kept.  But it cannot distinguish
"stable because correct" from "stable because frozen" — so the defect is
preserved BY THE AUDIT TRAIL, visibly, in a form that reads as evidence of care.
That is worse than an invisible failure mode: it produces a positive signal
pointing the wrong way.

THE FIX COSTS THE CONVENTION NOTHING: keep the key, keep the value, but make the
value unreadable WITHOUT its status.  An advisory flag would not do it — that is
exactly what `I8_brody_q_unbounded` already was (available, optional, unused) and
what `fit_rejected` would have been if nobody consulted it.  So `__float__`
RAISES on a railed value.  A consumer must either read the unbounded companion,
or explicitly acknowledge the rail.  Same shape as k/n for boundary rates, and
the same reason: **the caveat travels with the number or it does not travel.**
"""
import math


class RailedValueError(ValueError):
    pass


class Bounded:
    """A bounded-estimator reading. Railed values refuse silent float use."""

    __slots__ = ("value", "boundary", "tol", "unbounded", "name")

    def __init__(self, value, boundary, tol=1e-3, unbounded=None, name="value"):
        self.value = None if value is None else float(value)
        self.boundary = float(boundary)
        self.tol = float(tol)
        self.unbounded = None if unbounded is None else float(unbounded)
        self.name = name

    @property
    def railed(self):
        return (self.value is not None
                and math.isfinite(self.value)
                and abs(self.value - self.boundary) <= self.tol)

    @property
    def informative(self):
        return not self.railed

    def __float__(self):
        if self.railed:
            raise RailedValueError(
                f"{self.name}={self.value} is AT the boundary {self.boundary} — "
                "it means 'at or beyond this bound, cannot tell which' and has no "
                "information in that direction. Read `.unbounded` "
                + (f"(= {self.unbounded})" if self.unbounded is not None
                   else "(NOT BANKED for this row — recompute or annotate)")
                + ", or call .acknowledge_rail() if the rail itself is the point.")
        return self.value

    def acknowledge_rail(self):
        """Explicit opt-in: return the raw float even though it is railed."""
        return self.value

    def best(self):
        """The informative reading: unbounded if railed and available."""
        if self.railed:
            if self.unbounded is None:
                return None
            return self.unbounded
        return self.value

    def __repr__(self):
        s = "RAILED" if self.railed else "ok"
        u = "" if self.unbounded is None else f", unbounded={self.unbounded:.4f}"
        return f"<Bounded {self.name}={self.value} [{s}] bound={self.boundary}{u}>"


def brody_q(record, tol=1e-3):
    """Read I.8_brody_q from a coordinate record WITH its rail status."""
    def _get(d, *keys):
        for k in keys:
            if isinstance(d, dict) and k in d:
                return d[k]
        return None
    axes = record.get("axes_computed", record) if isinstance(record, dict) else {}
    return Bounded(_get(axes, "I.8_brody_q"), boundary=0.0, tol=tol,
                   unbounded=_get(axes, "I.8_brody_q_unbounded"),
                   name="I.8_brody_q")
