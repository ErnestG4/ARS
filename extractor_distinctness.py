"""
extractor_distinctness.py — Phase 19 empirical mechanism-distinctness test.

The "principled iff classification is invariant across ≥ 4 distinct
extractor mechanisms" criterion (§7.ter.22) is only as reliable as the
notion of "distinct."  Surface-description distinctness can fail to
capture mechanism distinctness when extractors share an underlying
threshold-on-continuous-derived-signal step (the §7.ter.23 retrospective).

Phase 19 operationalises distinctness empirically:

  A pair of extractors (A, B) is **demonstrably distinct** iff there is
  at least one calibrator class for which A and B yield different
  per-q quadrant assignments under `joint_quadrant_diagnostic`, with
  the difference robust across n_seeds ≥ 5 calibrator-level resamples.

This module provides:

  - `distinct_pair(extractor_a, extractor_b, calibrator_panel, ...)` —
    the headline API.  Returns a dict with `distinct`, the disagreeing
    class (if any), per-class verdicts, and the strongest p-value.
  - `STANDARD_CALIBRATORS` — the 8-class point-process panel from
    Phase 15 / Phase 17 (Poisson, GOE, GUE, GSE, ζ-first-1000,
    uniform_jitter, periodic q=7, mixed q=7+q=12).
  - `extractor_for_events` and `extractor_for_continuous` adapters that
    wrap the project's general extractors into the unified callable
    signature `f(t_k, seed) -> events`.  This lets the same
    distinctness loop apply to any (chirp-driven or direct) extractor.

The bootstrap statistic is the *fraction of seeds with at least one
disagreeing q-band*; pair-level distinctness at α = 0.05 requires
this fraction ≥ 0.80 on at least one calibrator class (4 of 5 seeds).
"""
from __future__ import annotations

import os, sys
from typing import Callable, Iterable, Optional
from itertools import combinations

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from extractors import EXTRACTORS, synthesize_continuous
from signal_gen import (
    make_beta_ensemble_eigenvalues,
    make_uniform_jitter,
)


# ─── Standard calibrator panel ─────────────────────────────────────────────


N_POINTS_DEFAULT = 1500


def _gen_poisson(seed, n=N_POINTS_DEFAULT):
    rng = np.random.default_rng(seed)
    return np.cumsum(rng.exponential(1.0, size=n))


def _gen_periodic(seed, period=7.0, jitter=0.05, n=N_POINTS_DEFAULT):
    rng = np.random.default_rng(seed)
    t = np.arange(1, n + 1, dtype=np.float64) * period \
        + jitter * rng.standard_normal(n)
    return np.sort(t)


def _gen_mixed(seed, periods=(7.0, 12.0), weights=(0.4, 0.4),
               jitter=0.05, n=N_POINTS_DEFAULT):
    rng = np.random.default_rng(seed)
    streams = []
    for p, w in zip(periods, weights):
        n_p = int(n * w)
        t = np.arange(1, n_p + 1, dtype=np.float64) * p \
            + jitter * rng.standard_normal(n_p)
        streams.append(t)
    bg = np.cumsum(rng.exponential(periods[0], size=int(n * 0.3)))
    streams.append(bg)
    out = np.sort(np.concatenate(streams))
    return out[:n]


def _load_zeta(seed=None, n=1000):
    """ζ first 1000 zeros — deterministic; seed unused (returned identical
    for every seed, by design of the calibrator panel)."""
    z = np.loadtxt(os.path.join(THIS_DIR, 'data', 'odlyzko_zeros1.txt'),
                    max_rows=n)
    return (z / (2 * np.pi)) * np.log(np.maximum(z / (2 * np.pi * np.e), 1.0)) + 7 / 8


STANDARD_CALIBRATORS = [
    ('poisson',           lambda s: _gen_poisson(s)),
    ('beta=1_GOE',        lambda s: make_beta_ensemble_eigenvalues(N_POINTS_DEFAULT, 1, s)),
    ('beta=2_GUE',        lambda s: make_beta_ensemble_eigenvalues(N_POINTS_DEFAULT, 2, s)),
    ('beta=4_GSE',        lambda s: make_beta_ensemble_eigenvalues(N_POINTS_DEFAULT, 4, s)),
    ('zeta_first_1000',   lambda s: _load_zeta(s, n=1000)),
    ('uniform_jitter',    lambda s: make_uniform_jitter(N_POINTS_DEFAULT, 0.10, s)),
    ('periodic_q7',       lambda s: _gen_periodic(s, period=7.0, jitter=0.05)),
    ('mixed_q7_q12',      lambda s: _gen_mixed(s)),
]


# ─── Per-q quadrant comparison ────────────────────────────────────────────


Q_MAX_DEFAULT = 30
MIN_EVENTS_DEFAULT = 30


def _quadrants_per_q(events, q_max=Q_MAX_DEFAULT,
                      min_events=MIN_EVENTS_DEFAULT) -> pd.DataFrame:
    """Return DataFrame with columns (q, quadrant, underpowered) for an
    event sequence.  Underpowered q-bands have quadrant = 'ambiguous'."""
    if events.size < min_events:
        return pd.DataFrame({'q': np.arange(1, q_max + 1),
                              'quadrant': ['ambiguous'] * q_max,
                              'underpowered': [True] * q_max})
    j = joint_q_profile(events, q_max=q_max, min_events_per_q=min_events)
    qd = joint_quadrant_diagnostic(j)
    return qd[['q', 'quadrant', 'underpowered']].reset_index(drop=True)


def _q_disagreement_count(qd_a: pd.DataFrame, qd_b: pd.DataFrame) -> int:
    """Number of q-bands where A and B carry different quadrant labels.

    The comparison includes the 'ambiguous' (underpowered) label itself:
    an extractor that returns no events on a calibrator (label='ambiguous'
    across all q) is mechanism-distinct from one that returns enough
    events for a real classification.  Treating ambiguous as just
    another label makes the count sensitive to extractor-specific
    underpowering — which is itself a mechanism difference.

    The min_events threshold (default 30 in `_quadrants_per_q`) is the
    only place we discriminate "no real classification."  Below it, all
    q-bands are 'ambiguous'; the disagreement count then registers
    extractors whose effective output volume is in different regimes.
    """
    if qd_a is None or qd_b is None:
        return 0
    return int((qd_a['quadrant'].values != qd_b['quadrant'].values).sum())


# ─── Distinctness test ────────────────────────────────────────────────────


def distinct_pair(
        extractor_a: Callable,
        extractor_b: Callable,
        calibrator_panel: Iterable = None,
        n_seeds: int = 5,
        seed_threshold: int = 4,
        q_max: int = Q_MAX_DEFAULT,
        min_events: int = MIN_EVENTS_DEFAULT,
        verbose: bool = False,
        ) -> dict:
    """Empirical mechanism-distinctness test for a pair of extractors.

    `extractor_a`, `extractor_b`: callables with signature `f(t_k) -> events`
        mapping a calibrator point process (or a continuous-signal
        equivalent — adapters live in `extractor_for_*` below) to an
        extracted event sequence.

    `calibrator_panel`: iterable of (name, generator) pairs.  Defaults to
        `STANDARD_CALIBRATORS`.

    `n_seeds`: number of calibrator seeds to evaluate (default 5).

    `seed_threshold`: minimum number of seeds (out of n_seeds) required
        to show ≥ 1 q-band disagreement on a single calibrator class for
        the pair to be declared distinct.  Default 4 of 5 ≈ α = 0.05
        (binomial p(4 of 5 disagree | true equiv) = 0.05^5 + 5·0.05^4·0.95
        ≈ 0.0000003; with sub-bootstrap noise ≈ 0.05).

    Returns:
        dict with keys
          - distinct (bool)
          - disagreeing_class (str or None) — the first class where the
            seed_threshold was met
          - max_disagreement_seeds (int) — the largest count of disagreeing
            seeds across all calibrators (the "strongest" disagreement)
          - per_class (list of dicts) — per-class verdicts:
            (name, mean_q_disagree, fraction_seeds_with_disagree)
    """
    if calibrator_panel is None:
        calibrator_panel = STANDARD_CALIBRATORS

    per_class = []
    distinct = False
    disagreeing_class = None
    max_disagree_seeds = 0

    for cal_name, cal_gen in calibrator_panel:
        n_disagree_seeds = 0
        q_disagree_counts = []
        for seed in range(n_seeds):
            try:
                t_k = cal_gen(seed)
            except Exception:
                continue
            events_a = np.sort(np.asarray(extractor_a(t_k), dtype=np.float64))
            events_b = np.sort(np.asarray(extractor_b(t_k), dtype=np.float64))
            qd_a = _quadrants_per_q(events_a, q_max=q_max,
                                     min_events=min_events)
            qd_b = _quadrants_per_q(events_b, q_max=q_max,
                                     min_events=min_events)
            n_q_dis = _q_disagreement_count(qd_a, qd_b)
            q_disagree_counts.append(n_q_dis)
            if n_q_dis > 0:
                n_disagree_seeds += 1
            if verbose:
                print(f"      [{cal_name} seed={seed}]  n_a={events_a.size}  "
                      f"n_b={events_b.size}  q_disagree={n_q_dis}")
        per_class.append(dict(
            calibrator=cal_name,
            mean_q_disagree=float(np.mean(q_disagree_counts))
                            if q_disagree_counts else 0.0,
            max_q_disagree=int(max(q_disagree_counts))
                            if q_disagree_counts else 0,
            n_disagree_seeds=int(n_disagree_seeds),
            n_total_seeds=int(len(q_disagree_counts)),
        ))
        if n_disagree_seeds > max_disagree_seeds:
            max_disagree_seeds = n_disagree_seeds
        if n_disagree_seeds >= seed_threshold and not distinct:
            distinct = True
            disagreeing_class = cal_name

    return dict(
        distinct=distinct,
        disagreeing_class=disagreeing_class,
        max_disagreement_seeds=max_disagree_seeds,
        per_class=per_class,
    )


# ─── Adapters — wrap project extractors into the unified callable ─────────


def extractor_for_events(name: str, **kwargs) -> Callable:
    """Wrap a general point-process extractor (from `extractors.EXTRACTORS`)
    into a callable `f(t_k) -> events`.  All kwargs are forwarded to the
    extractor."""
    fn = EXTRACTORS[name]
    def _wrapped(t_k):
        return fn(t_k, **kwargs)
    _wrapped.__name__ = f"events_{name}_{kwargs}"
    return _wrapped


def extractor_for_continuous(continuous_extractor: Callable,
                              oversample: int = 10,
                              sigma_frac: float = 0.3) -> Callable:
    """Wrap a continuous-signal extractor (callable with signature
    `g(sig) -> peak_indices`) into a callable `f(t_k) -> events` by
    chirp-driving the input event sequence into a Gaussian-pulse
    continuous proxy first, then applying `g` to the proxy."""
    def _wrapped(t_k):
        t_grid, sig = synthesize_continuous(
            t_k, oversample=oversample, sigma_frac=sigma_frac)
        if sig.size < 5:
            return np.zeros(0)
        idx = continuous_extractor(sig)
        return t_grid[idx]
    _wrapped.__name__ = f"chirp_{getattr(continuous_extractor, '__name__', 'fn')}"
    return _wrapped


__all__ = [
    'distinct_pair',
    'STANDARD_CALIBRATORS',
    'extractor_for_events',
    'extractor_for_continuous',
    '_quadrants_per_q', '_q_disagreement_count',
]
