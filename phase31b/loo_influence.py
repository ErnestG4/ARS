"""
phase31b/loo_influence.py — leave-one-out (per-component) influence on
aggregate ARS classification.

Per Phase 31b finding (smoke test result): single-event finite-difference
sensitivity of ks_gue_med and rep_med is near-zero across the recording
because the median-across-q aggregation absorbs single-q perturbations.
The deployed classifier is **event-level robust** at the modal scale.

The natural stratification unit for the Phase 30 Kuramoto aggregate is
**per-oscillator** — each of the 100 oscillators contributes ~2400 events
to the aggregate, and the sub-modal drift question becomes: which
oscillators carry the +0.10 ks_med shift across K?

API:
    loo_aggregate_influence(events_per_component, q_max) → DataFrame
        per-component aggregate-classification influence (compare
        aggregate with vs without that component).

    aggregate_rf_per_q(events_per_component, q_max) → ndarray
        aggregate-level Ramanujan–Fourier amplitudes per q for the
        concatenated events.
"""
from __future__ import annotations

import os
import sys
from typing import Sequence
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q
from arithmetic_toolkit import ramanujan_fourier


def _classify_pooled(args):
    pool_idx, events, q_max, min_events_per_q = args
    if events.size < min_events_per_q:
        return dict(pool_idx=pool_idx, ks_gue_med=np.nan,
                     rep_med=np.nan, primary='underpowered',
                     n_events=int(events.size))
    r = classify(np.sort(events), return_full=False,
                  q_max=q_max, min_events_per_q=min_events_per_q)
    return dict(pool_idx=pool_idx, ks_gue_med=r['ks_gue_med'],
                 rep_med=r['rep_med'], primary=r['primary'],
                 n_events=int(events.size))


def loo_aggregate_influence(events_per_component: Sequence[np.ndarray],
                              q_max: int = Q_MAX,
                              min_events_per_q: int = MIN_EVENTS_PER_Q,
                              n_workers: int = 8) -> pd.DataFrame:
    """For each component i, compute the aggregate classification
    of (all-components) and of (all-components excluding i).  The
    influence Δks_i = ks_full − ks_leave_i_out tells you how much
    component i is pulling the aggregate classification.

    Returns DataFrame with columns:
        i, n_events_i, ks_med_full, ks_med_loo, delta_ks,
        rep_med_full, rep_med_loo, delta_rep, primary_full,
        primary_loo
    """
    N = len(events_per_component)
    n_per = np.asarray([e.size for e in events_per_component])

    full = np.sort(np.concatenate([e for e in events_per_component if e.size > 0]))
    full_result = classify(full, return_full=False, q_max=q_max,
                            min_events_per_q=min_events_per_q)
    ks_full = full_result['ks_gue_med']
    rep_full = full_result['rep_med']
    primary_full = full_result['primary']

    # Build LOO event pools
    args_list = []
    for i in range(N):
        loo_events = np.concatenate([events_per_component[j]
                                       for j in range(N) if j != i and events_per_component[j].size > 0])
        loo_events = np.sort(loo_events)
        args_list.append((i, loo_events, q_max, min_events_per_q))

    if n_workers > 1:
        with Pool(min(n_workers, cpu_count())) as pool:
            results = list(pool.imap(_classify_pooled, args_list, chunksize=4))
    else:
        results = [_classify_pooled(a) for a in args_list]

    rows = []
    for r in results:
        i = r['pool_idx']
        delta_ks = ks_full - r['ks_gue_med'] if np.isfinite(r['ks_gue_med']) else np.nan
        delta_rep = rep_full - r['rep_med'] if np.isfinite(r['rep_med']) else np.nan
        rows.append(dict(
            i=int(i), n_events_i=int(n_per[i]),
            ks_med_full=float(ks_full),
            ks_med_loo=float(r['ks_gue_med']),
            delta_ks=float(delta_ks),
            rep_med_full=float(rep_full),
            rep_med_loo=float(r['rep_med']),
            delta_rep=float(delta_rep),
            primary_full=str(primary_full),
            primary_loo=str(r['primary']),
        ))
    return pd.DataFrame(rows)


def aggregate_rf_per_q(events: np.ndarray, q_max: int = Q_MAX) -> np.ndarray:
    """Aggregate-level indicator-mode Ramanujan–Fourier amplitudes per q.

    Returns the |a_q| array of length q_max."""
    rf = ramanujan_fourier(np.sort(events), q_max=q_max, normalize=False)
    amps = np.abs(np.asarray(rf.get('amplitudes', []), dtype=np.float64))
    if amps.size != q_max:
        amps = np.full(q_max, np.nan)
    return amps


def rf_drift_across_conditions(condition_events: dict[str, np.ndarray],
                                q_max: int = Q_MAX) -> pd.DataFrame:
    """For each condition label and its aggregate event train, compute
    per-q RF amplitudes.  Returns long-form DataFrame:
        condition, q, rf_amplitude, rf_amplitude_rel_to_mean
    """
    rows = []
    for label, events in condition_events.items():
        amps = aggregate_rf_per_q(events, q_max=q_max)
        mean_amp = float(np.nanmean(amps[1:]))   # exclude DC at q=1
        for q in range(1, q_max + 1):
            rows.append(dict(
                condition=label, q=int(q),
                rf_amplitude=float(amps[q - 1]),
                rf_relative=float(amps[q - 1] / max(mean_amp, 1e-12)),
            ))
    return pd.DataFrame(rows)


__all__ = ['loo_aggregate_influence', 'aggregate_rf_per_q',
            'rf_drift_across_conditions']
