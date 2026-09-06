"""Bank an aggregate WITH its n and its spread, or do not bank it.

WHY THIS IS A MODULE AND NOT A CHECKER
--------------------------------------
Session F banked `"genus2_rate_ratio": 0.9583126741064829` -- a mean over curves
whose spread is sd 0.296 across the range 0.650 to 1.862, recorded with no n and
no error bar. The number is not wrong. It is UNFALSIFIABLE AS WRITTEN, because
nothing beside it says how much of it is signal, and a reader meeting it cannot
tell a constant from a mean over a wide distribution.

TWO SWEEPS FOR SIBLINGS BOTH FAILED, and the failures are the argument for doing
this at construction time. `aggregate_dispersion_triage.py` keeps the record:

  * keying on PRECISION returned 2410 hits across 50 files, because JSON
    serialises full float precision and every computed float in this repo
    carries seventeen digits. The tell was incidental to the defect.
  * keying on a MISSING DISPERSION COMPANION gave a clean-looking 54.1% of
    6698 -- until four of the top hits were hand-checked and all four were
    false positives, each differently: `separation` was carried by
    `separation_se`; a spread was recoverable from a `rows` array; `worst_*` is
    an extremum that wants no error bar; a fraction sat beside its own numerator
    and denominator.

Widening the regex cannot fix that. `rows` counts because a human can read the
array; `worst_` is exempt because of what the word MEANS. The defect is SEMANTIC
and semantic defects have no syntactic tell, so a census gives a lower bound
whose misses are the hard tail.

The rule therefore has to live where aggregates are WRITTEN. `banked()` returns a
dict, never a scalar, so the spread cannot be dropped by forgetting -- only by
deliberately reaching past the API, which leaves a visible reach.

WHAT IT REFUSES, AND WHY EACH REFUSAL EXISTS
--------------------------------------------
  n < 2                a single observation has no spread. Banking its "mean"
                       as a constant is the Session F failure in miniature, so
                       it must be acknowledged rather than defaulted.
  a bare scalar        the whole point. If you already collapsed the sample you
                       cannot recover its spread, and passing the collapsed
                       value is how the defect gets in.
  an EXTREMUM by name  `worst_*`, `max_*`, `min_*`, `best_*` do NOT want an
                       error bar, and demanding one would be the false-positive
                       the second sweep produced. Use `extremum()`, which banks
                       the value with its n and the population it was taken
                       over -- because a max over 9 configurations is a
                       selected maximum, which is the defect the swing rule
                       exists for.
"""
import math

__all__ = ["banked", "extremum", "AggregateWithoutSpread"]

_EXTREMUM_WORDS = ("worst", "best", "max", "min", "peak", "argmax", "argmin")


class AggregateWithoutSpread(AssertionError):
    """Raised when an aggregate is banked in a form that hides its dispersion."""


def _looks_like_extremum(name):
    low = name.lower()
    return any(w in low for w in _EXTREMUM_WORDS)


def banked(name, values, kind="mean", acknowledge=None):
    """Bank an aggregate with everything needed to read it.

    Returns a dict: value, kind, n, sd, sem, minimum, maximum, spread_ratio.
    Never a scalar -- that is the enforcement.
    """
    if isinstance(values, (int, float)):
        raise AggregateWithoutSpread(
            f"'{name}': banked() was handed the COLLAPSED value {values!r}. The "
            "sample is what carries the spread, and once you have collapsed it "
            "the dispersion cannot be recovered -- which is exactly how "
            "genus2_rate_ratio came to be seventeen significant figures with no "
            "n. Pass the values, not the mean.")
    vals = [float(v) for v in values
            if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if len(vals) < 2 and acknowledge is None:
        raise AggregateWithoutSpread(
            f"'{name}': {len(vals)} usable value(s). An aggregate over fewer "
            "than two observations has no spread, so banking it as a constant "
            "asserts a precision nothing supports. Pass "
            "acknowledge='<why a single value is the right thing here>'.")
    if _looks_like_extremum(name) and acknowledge is None:
        raise AggregateWithoutSpread(
            f"'{name}': the name reads as an EXTREMUM. An extremum does not "
            "want an error bar -- demanding one is the false positive the "
            "census sweep produced four times out of four. Use extremum(), "
            "which records the population it was selected over, or "
            "acknowledge='<why this really is a central-tendency claim>'.")
    n = len(vals)
    if n == 0:
        return dict(name=name, kind=kind, value=None, n=0, sd=None, sem=None,
                    minimum=None, maximum=None, spread_ratio=None,
                    acknowledged=acknowledge)
    mean = sum(vals) / n
    if kind == "median":
        s = sorted(vals)
        value = (s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2]))
    else:
        value = mean
    sd = (math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
          if n > 1 else None)
    lo, hi = min(vals), max(vals)
    return dict(name=name, kind=kind, value=value, n=n, sd=sd,
                sem=(sd / math.sqrt(n) if sd is not None else None),
                minimum=lo, maximum=hi,
                spread_ratio=(hi / lo if lo > 0 else None),
                acknowledged=acknowledge)


def extremum(name, values, kind="max", over=None):
    """Bank an extremum WITH the population it was selected over.

    A maximum is not a measurement of a quantity; it is a measurement of a
    quantity AND of how many chances it had. brocot_cue_salience bootstrapped a
    max over nine configurations and reported the interval as a CI; the swing
    rule was minted from it. So the population size travels with the value, and
    `over` names what was searched.
    """
    vals = [float(v) for v in values
            if v is not None and not (isinstance(v, float) and math.isnan(v))]
    if not vals:
        return dict(name=name, kind=kind, value=None, n_candidates=0, over=over)
    value = max(vals) if kind == "max" else min(vals)
    if over is None:
        raise AggregateWithoutSpread(
            f"'{name}': extremum() needs `over=` naming the population it was "
            f"selected from. {len(vals)} candidates were searched, and a value "
            "selected from many is not the same claim as a value measured once "
            "-- that difference is what the swing rule exists to keep visible.")
    mean = sum(vals) / len(vals)
    return dict(name=name, kind=kind, value=value, n_candidates=len(vals),
                over=over, population_mean=mean,
                population_min=min(vals), population_max=max(vals),
                selection_margin=abs(value - mean))
