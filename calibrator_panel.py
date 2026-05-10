"""
calibrator_panel.py — unified standard calibrator panel for the
extractor-distinctness machinery (Phase 19) and the trajectory
diagnostic (Phase 20.5).

Pre-Phase-20.5 the panel was implicit in
`extractor_distinctness.STANDARD_CALIBRATORS` (eight stationary
universality classes).  Phase 20.5 adds two new families — blended
constructive transitions (six shapes × eight class pairs) and
parameter-driven dynamical transitions (logistic-map regimes,
Mackey-Glass regimes) — and the principled-claim discipline
(§7.ter.26) says any classification claim needs extractor-distinctness
verification on the *current* panel, not just the pre-Phase-20.5 one.

This module provides:

  - `STATIONARY_CALIBRATORS`        — the eight pre-Phase-20.5 classes
                                      (verbatim from
                                      `extractor_distinctness`).
  - `TRANSITION_CALIBRATORS`        — a representative subset of the
                                      Phase 20.5 blended-panel and
                                      parameter-driven calibrators
                                      (six entries, kept small to
                                      keep the pairwise distinctness
                                      matrix tractable).
  - `EXTENDED_CALIBRATORS`          — concatenation of the two.

Each entry is a (name, gen_fn) tuple where gen_fn(seed) returns a
unit-mean event-time sequence of ≥ ~400 events (the size used in the
Phase 19 distinctness matrix, `DIST_N_POINTS = 400`).
"""
from __future__ import annotations

import os, sys

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from extractor_distinctness import (
    _gen_poisson, _gen_periodic, _gen_mixed, _load_zeta,
)
from signal_gen import (
    make_beta_ensemble_eigenvalues, make_uniform_jitter,
)
from transition_calibrators_blended import gen_blended_transition
from transition_calibrators_dynamical import (
    logistic_iterate, logistic_to_events,
)


N_POINTS = 400


# ─── Stationary calibrators (eight classes — pre-Phase-20.5 panel) ─────────


STATIONARY_CALIBRATORS = [
    ('poisson',           lambda s: _gen_poisson(s, n=N_POINTS)),
    ('beta=1_GOE',        lambda s: make_beta_ensemble_eigenvalues(N_POINTS, 1, s)),
    ('beta=2_GUE',        lambda s: make_beta_ensemble_eigenvalues(N_POINTS, 2, s)),
    ('beta=4_GSE',        lambda s: make_beta_ensemble_eigenvalues(N_POINTS, 4, s)),
    ('zeta_first_400',    lambda s: _load_zeta(s, n=N_POINTS)),
    ('uniform_jitter',    lambda s: make_uniform_jitter(N_POINTS, 0.10, s)),
    ('periodic_q7',       lambda s: _gen_periodic(s, period=7.0, jitter=0.05,
                                                     n=N_POINTS)),
    ('mixed_q7_q12',      lambda s: _gen_mixed(s, n=N_POINTS)),
]


# ─── Transition calibrators (Phase 20.5 — representative subset) ───────────


def _gen_logistic_chaos(seed: int) -> np.ndarray:
    """Logistic map at r = 3.7 (chaotic regime) → IEI-mode events."""
    rng = np.random.default_rng(seed)
    # Use seed to perturb x0 across calibrator-resamples
    x0 = 0.5 + (rng.uniform() - 0.5) * 0.05
    x = logistic_iterate(r=3.7, x0=x0, n_iter=N_POINTS * 4, discard=200)
    ev = logistic_to_events(x, mode='iei')
    if ev.size > N_POINTS:
        ev = ev[:N_POINTS]
    return ev


def _gen_logistic_period_4(seed: int) -> np.ndarray:
    """Logistic map at r = 3.5 (period-4 limit cycle)."""
    rng = np.random.default_rng(seed)
    x0 = 0.5 + (rng.uniform() - 0.5) * 0.05
    x = logistic_iterate(r=3.5, x0=x0, n_iter=N_POINTS * 4, discard=200)
    ev = logistic_to_events(x, mode='iei')
    if ev.size > N_POINTS:
        ev = ev[:N_POINTS]
    return ev


def _gen_blended_GUE_to_Poisson_sharp(seed: int) -> np.ndarray:
    """Wigner GUE → Poisson sharp-step transition."""
    return gen_blended_transition('GUE', 'Poisson', 'sharp_step',
                                    n_points=N_POINTS, seed=seed)


def _gen_blended_Poisson_to_GUE_sigmoidal(seed: int) -> np.ndarray:
    """Poisson → Wigner GUE sigmoidal transition."""
    return gen_blended_transition('Poisson', 'GUE', 'sigmoidal',
                                    n_points=N_POINTS, seed=seed)


def _gen_blended_metastable_GUE_TL_GUE(seed: int) -> np.ndarray:
    """GUE → TL → GUE (metastable middle, periodic intermediate)."""
    return gen_blended_transition('GUE', 'GUE', 'metastable_middle',
                                    n_points=N_POINTS, seed=seed,
                                    middle_class='TL')


def _gen_blended_Poisson_to_TL_linear(seed: int) -> np.ndarray:
    """Poisson → periodic linear ramp."""
    return gen_blended_transition('Poisson', 'TL', 'linear_ramp',
                                    n_points=N_POINTS, seed=seed)


TRANSITION_CALIBRATORS = [
    ('blended_GUE_to_Poisson_sharp',     _gen_blended_GUE_to_Poisson_sharp),
    ('blended_Poisson_to_GUE_sigmoidal', _gen_blended_Poisson_to_GUE_sigmoidal),
    ('blended_GUE_TL_GUE_metastable',    _gen_blended_metastable_GUE_TL_GUE),
    ('blended_Poisson_to_TL_linear',     _gen_blended_Poisson_to_TL_linear),
    ('logistic_chaos_r=3.7',             _gen_logistic_chaos),
    ('logistic_period_4_r=3.5',          _gen_logistic_period_4),
]


EXTENDED_CALIBRATORS = STATIONARY_CALIBRATORS + TRANSITION_CALIBRATORS


__all__ = [
    'STATIONARY_CALIBRATORS', 'TRANSITION_CALIBRATORS',
    'EXTENDED_CALIBRATORS', 'N_POINTS',
]
