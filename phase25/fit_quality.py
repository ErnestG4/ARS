"""
phase25/fit_quality.py — fit-quality verification for the multi-frame
coupled-GLM at each (n_lags, bin_width, variant) configuration.

Verdict vocabulary (refined Phase 25):

  FIT-PROPER                       — the GLM converged to a biologically-
                                      reasonable optimum.  Survival-testable.
                                      Canonical-variant requirements:
                                        * non-trivial history L2,
                                        * refractory negative lobe at
                                          short lags (hist_min ≤ -0.03),
                                        * stim kernel L2 above the
                                          collapse threshold,
                                        * forward-sim rate within
                                          [1/1.5, 1.5] × real rate,
                                        * median dev_explained > 0.005.
                                      Unconstrained-variant requirements:
                                        * sign structure present (refractory
                                          negative lobe present, hist_min ≤
                                          -0.03, not uniformly positive),
                                        * hist_max bounded (not runaway),
                                        * the other thresholds match.

  FIT-DEGENERATE-BY-RESOLUTION     — bin width / lag structure makes
                                      the model class incapable of
                                      representing what's there.  Most
                                      common cases:
                                        * canonical at coarse bins
                                          (refractory sub-bin → history
                                          collapses to 0 under non-
                                          positive constraint);
                                        * both stim and history
                                          collapsed jointly (Phase 22b's
                                          5 ms canonical failure pattern,
                                          where single-frame STA failed
                                          to absorb stim variance).

  FIT-PATHOLOGICAL-BY-CONSTRAINT   — GLM converged but to a biologically-
                                      implausible optimum.  The canonical
                                      unconstrained-history runaway: history
                                      kernel uniformly positive, no refractory
                                      lobe, surrogate event rate > 1.5× real.

  FIT-OTHER                        — fails fit-quality for unidentified
                                      reasons (low dev_explained, partial
                                      kernel collapse, non-convergence,
                                      …).  Treated like FIT-DEGENERATE
                                      for survival eligibility but logged
                                      separately so we can spot
                                      idiosyncratic edge cases.

Survival-testable means FIT-PROPER only.  Configurations classified as
FIT-DEGENERATE or FIT-PATHOLOGICAL or FIT-OTHER do not contribute to
the H_PassD verdict — they map the methodological landscape but don't
bind H_PassD either way.

Per-unit thresholds:
"""
from __future__ import annotations

import numpy as np


HISTORY_L2_MIN = 0.05           # any variant: kernel must have non-trivial L2
HISTORY_REFRACTORY_MAX = -0.03  # any variant: short-lag refractory dip
HISTORY_KMAX_RUNAWAY_THR = 0.40 # unconstrained: max above → runaway
STIM_L2_MIN = 0.015             # any variant: stim coefficients not collapsed
RATE_TOL_FACTOR = 1.5           # surrogate rate within this factor of real

DEV_EXPLAINED_MIN_CELL = 0.005  # configuration-level dev_explained threshold


def per_unit_pass(diag: dict, variant: str,
                    real_n_spikes: int, sur_n_spikes: int) -> dict:
    """Apply the per-unit fit-quality checks.  A unit is "PROPER" if it
    passes all checks for the given variant.

    See module docstring for the criteria.  Returns dict of flags +
    `unit_pass` overall.  `failure_mode` reports which check first
    failed when `unit_pass` is False.
    """
    converged = bool(diag.get('converged', False))
    hist_l2 = float(diag.get('history_kernel_l2', 0.0))
    hist_max = float(diag.get('history_kernel_max', 0.0))
    hist_min = float(diag.get('history_kernel_min', 0.0))
    stim_l2 = float(diag.get('stim_kernel_l2', 0.0))

    refractory_present = hist_min <= HISTORY_REFRACTORY_MAX
    history_l2_ok = hist_l2 >= HISTORY_L2_MIN
    # Runaway = unconstrained kernel that is uniformly positive AND
    # large (no refractory dip, large positive feedback).  Canonical's
    # softplus constraint makes runaway impossible.
    if variant == 'canonical':
        runaway = False
    else:
        runaway = (hist_max > HISTORY_KMAX_RUNAWAY_THR and hist_min > 0)

    if variant == 'canonical':
        history_ok = history_l2_ok and refractory_present
    else:
        history_ok = history_l2_ok and refractory_present and not runaway

    stim_ok = stim_l2 >= STIM_L2_MIN
    rate_ratio = sur_n_spikes / max(real_n_spikes, 1)
    rate_ok = (RATE_TOL_FACTOR ** -1) <= rate_ratio <= RATE_TOL_FACTOR

    overall = converged and history_ok and stim_ok and rate_ok

    # Failure mode ordering: runaway (constraint pathology) is checked
    # BEFORE refractory-absence and other resolution-driven modes, so
    # the uniformly-positive-large kernel is correctly diagnosed as
    # pathological-by-constraint rather than degenerate-by-resolution.
    if overall:
        failure_mode = ''
    elif not converged:
        failure_mode = 'non-convergence'
    elif runaway:
        failure_mode = 'history-runaway'
    elif not history_l2_ok:
        failure_mode = 'history-collapsed'
    elif not refractory_present:
        failure_mode = 'no-refractory'
    elif not stim_ok:
        failure_mode = 'stim-collapsed'
    elif not rate_ok:
        failure_mode = 'rate-mismatch'
    else:
        failure_mode = 'other'

    return dict(
        converged=converged, history_ok=history_ok, stim_ok=stim_ok,
        rate_ok=rate_ok, runaway=runaway,
        refractory_present=refractory_present,
        rate_ratio=rate_ratio, hist_l2=hist_l2,
        hist_max=hist_max, hist_min=hist_min, stim_l2=stim_l2,
        unit_pass=overall, failure_mode=failure_mode,
    )


def configuration_verdict(per_unit_results: list[dict],
                            dev_explained_median: float,
                            variant: str) -> str:
    """Aggregate per-unit checks into a configuration-level verdict.

    See module docstring for vocabulary.  Uses cell-level kernel
    statistics to diagnose the dominant failure mode — the per-unit
    failure-mode counter can be misleading when the L-BFGS doesn't
    converge cleanly on the unconstrained variant (e.g. unconstrained
    5 ms × 1-lag: 36/74 units flag 'non-convergence' as a symptom of
    runaway-induced ill-conditioning, masking the underlying
    pathology).
    """
    n_units = len(per_unit_results)
    if n_units == 0: return 'FIT-OTHER'

    n_pass = sum(int(r['unit_pass']) for r in per_unit_results)
    frac_pass = n_pass / n_units

    if frac_pass >= 0.5 and dev_explained_median > DEV_EXPLAINED_MIN_CELL:
        return 'FIT-PROPER'

    # Cell-level kernel statistics — robust to per-unit fitting noise.
    hist_l2_med = float(np.median([r['hist_l2'] for r in per_unit_results]))
    hist_max_med = float(np.median([r['hist_max'] for r in per_unit_results]))
    hist_min_med = float(np.median([r['hist_min'] for r in per_unit_results]))
    rate_ratio_med = float(np.median(
        [r['rate_ratio'] for r in per_unit_results]))

    # Constraint pathology: unconstrained variant with cell-level
    # uniformly-positive kernel above the runaway threshold AND
    # surrogate rate inflated.  Either median-hist-max > thr or
    # median-rate-ratio > rate-tol suffices — the kernel and the
    # surrogate-rate inflation are the same phenomenon viewed two
    # ways and the optimizer's per-unit failures can mask one or the
    # other.
    if variant != 'canonical':
        runaway_kernel = (hist_max_med > HISTORY_KMAX_RUNAWAY_THR
                            and hist_min_med > 0)
        runaway_rate = rate_ratio_med > RATE_TOL_FACTOR
        if runaway_kernel or runaway_rate:
            return 'FIT-PATHOLOGICAL-BY-CONSTRAINT'

    # Resolution-driven degeneracy: history L2 collapsed (refractory
    # sub-bin under non-positive constraint at coarse bins, or both
    # kernels collapsed jointly under insufficient stim absorption at
    # fine bins).
    if hist_l2_med < HISTORY_L2_MIN:
        return 'FIT-DEGENERATE-BY-RESOLUTION'

    return 'FIT-OTHER'


__all__ = [
    'HISTORY_L2_MIN', 'HISTORY_REFRACTORY_MAX', 'HISTORY_KMAX_RUNAWAY_THR',
    'STIM_L2_MIN', 'RATE_TOL_FACTOR', 'DEV_EXPLAINED_MIN_CELL',
    'per_unit_pass', 'configuration_verdict',
]
