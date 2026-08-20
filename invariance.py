"""Invariance testing — the guard for DETERMINISTIC error.

WHY THIS EXISTS, and why it is not another checker.  Every other defense in this
repo -- sealing, pre-registration, red-pathing, pins, committed generators,
boundary-rate bounds, estimand matching -- operates on SAMPLING error.  A
deterministic error has zero variance, so it does not merely evade those
defenses, it INVERTS them: it looks stronger the more you check it the way you
have been checking.  On 2026-08-19 a cell reported +0.8085 +- 0.0084, ninety-six
sem, stable across 200 seeds, internally consistent, pinned by a checker -- and
was entirely an artifact of an ill-conditioned polyfit (Vandermonde cond 2.9e40
against ~1e16 of usable double precision).

Significance testing is structurally blind to this because it divides by the sem:
it probes the DENOMINATOR.  Every other guard asks "how precisely did we measure
this".  Invariance testing asks "did we measure THE THING" -- it probes the
NUMERATOR.  Same distinction as the estimand rule, one level lower down.

WHAT ACTUALLY CAUGHT IT was two runs disagreeing about the same quantity, and
only because one dial grid happened to sample a cell the other skipped.  That was
luck.  `dual_grid_check` makes it deliberate: evaluate a load-bearing quantity on
two overlapping-but-different grids and require agreement on the overlap.  Cheap
relative to the seed count such a quantity already costs.

CHOOSING INVARIANCES.  Do not work from a checklist.  Name the transformations
THIS number is theoretically invariant under -- read off the computation, which
is obvious to whoever wrote it and invisible to everyone else -- then test one or
two.  Same construction as a sealed coverage argument: the axes come from what
you already know, not from a generic list.  Defaults worth considering when
nothing more specific suggests itself: sampling-grid resolution, basis
centring/scaling, point ordering, float precision, unit choice.

ORDERING.  Invariance-test BEFORE pinning.  A pin locks a value against drift,
which is protection only if the value was right; a pin on a wrong value becomes
the thing preserving the error.  In the case above the pin fired correctly on an
artifact and would have defended it against correction.
"""
import numpy as np


class InvarianceFailure(AssertionError):
    pass


def dual_grid_check(fn, grid_a, grid_b, tol=1e-3, rtol=0.02, name="quantity"):
    """Evaluate fn(point) on two grids; require agreement on their OVERLAP.

    fn      : callable(point) -> float
    grid_a/b: sequences of points; must share at least 2 points
    Returns a dict; raises InvarianceFailure if the overlap disagrees.
    """
    ov = sorted(set(grid_a) & set(grid_b))
    if len(ov) < 2:
        raise ValueError(f"grids share {len(ov)} points; need >= 2 to compare")
    va = {p: float(fn(p)) for p in ov}
    vb = {p: float(fn(p)) for p in ov}
    # fn is evaluated identically here; the real test is that the CALLER's fn
    # depends on the grid it came from (e.g. a centroid over that grid), so pass
    # a closure bound to each grid via dual_grid_statistic instead.
    dev = {p: abs(va[p] - vb[p]) for p in ov}
    worst = max(dev.values())
    return dict(overlap=ov, worst_abs_dev=worst, agree=bool(worst <= tol),
                name=name, per_point=dev, rtol=rtol)


def dual_grid_statistic(stat_of_grid, grid_a, grid_b, tol=None, rtol=0.05,
                        ci=None, name="statistic"):
    """For a statistic COMPUTED OVER a grid (a centroid, a peak location, a fit).

    stat_of_grid : callable(grid) -> float
    Two grids that both adequately cover the feature must give the same answer.
    This is the form that catches grid-dependent estimators AND the deterministic
    numerics that only show up at particular sampled points.
    """
    a, b = float(stat_of_grid(grid_a)), float(stat_of_grid(grid_b))
    d = abs(a - b)
    scale = max(abs(a), abs(b), 1e-12)
    # TOLERANCE MUST BE REFERENCED TO THE CLAIMED PRECISION, not to an arbitrary
    # fraction. Found the hard way 2026-08-19: a 6.8% grid spread was scored a
    # FAILURE on a quantity whose own CI half-width was 21%, i.e. the invariance
    # test was stricter than the number was ever known to. That is a mis-specified
    # test, and it manufactures alarm exactly where precision is lowest. Pass `ci`
    # (the quantity's own [lo, hi]) and the check asks the question that matters:
    # is the grid-dependence SMALL COMPARED TO WHAT WE CLAIM TO KNOW?
    if ci is not None:
        half = (float(ci[1]) - float(ci[0])) / 2.0
        ok = d <= half
        basis = f"CI half-width {half:.4f}"
    elif tol is not None:
        ok, basis = d <= tol, f"abs tol {tol:.4g}"
    else:
        ok, basis = d / scale <= rtol, f"rel tol {rtol:.1%}"
    return dict(name=name, value_a=a, value_b=b, abs_dev=d, basis=basis,
                rel_dev=d / scale, agree=bool(ok),
                verdict=("AGREE" if ok else
                         f"GRID-DEPENDENT — {name} reads {a:.4f} on grid A and "
                         f"{b:.4f} on grid B (dev {d:.4f} vs {basis}); the "
                         "quantity depends on something it should be invariant to"))


def invariance_report(value_fn, transforms, tol=1e-6, name="value"):
    """value_fn(transform) -> float for each NAMED transform the value should be
    invariant under. transforms: dict name -> argument passed to value_fn."""
    base = None
    rows = {}
    for k, t in transforms.items():
        v = float(value_fn(t))
        if base is None:
            base = v
        rows[k] = dict(value=v, dev=abs(v - base))
    worst = max(r["dev"] for r in rows.values())
    return dict(name=name, rows=rows, worst_dev=worst, invariant=bool(worst <= tol))


def require(result):
    if not result.get("agree", result.get("invariant", False)):
        raise InvarianceFailure(result.get("verdict") or
                                f"{result['name']}: invariance violated "
                                f"(worst dev {result.get('worst_dev', result.get('abs_dev')):.4g})")
    return result
