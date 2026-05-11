"""
phase31b/sensitivity.py — finite-difference sensitivities for the deployed
ARS classifier (NNS engine global; RF engine per-q).

Per Phase 31a derivation: the deployed `joint_q_profile` has two engines,
only one of which is genuinely q-resolved.

  - **NNS engine** (pooled passage NNS): produces scalar ks_gue_med and
    rep_med.  Sensitivity is single-channel — ∂(ks_gue_med)/∂t_k,
    ∂(rep_med)/∂t_k — indexed by event k, not by q.
  - **RF engine** (Ramanujan–Fourier amplitudes): produces per-q
    amplitudes |a_q|.  Sensitivity is per-q — ∂|a_q|/∂t_k indexed by
    both event k and q-band.

Implementation: numerical finite-difference (two-sided).  For each event
in the subsample, perturb t_k → t_k ± ε, recompute the relevant
statistic, take centered difference / (2ε).

Subsampling: with N events and q_max=30, full per-event sensitivity costs
2N classify calls (~1–2 sec each at N=2000).  Subsample M=100 events
uniformly to bring cost to ~100–200 sec per recording.  Standard error
of the subsampled mean drops as 1/√M; M=100 gives ~10% precision on
mean sensitivity — sufficient for the stratification questions.
"""
from __future__ import annotations

import os
import sys
from typing import Optional
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q
from arithmetic_toolkit import ramanujan_fourier


# Default epsilon for finite-difference: 0.001 × mean-IEI.  Small enough
# to be linear in the local response; large enough that q=q_max=30 phase
# resolution (1/30 ≈ 0.033 mean-IEI) is still well above ε.
EPS_FRAC = 0.001


def _sample_indices(N: int, M: int, seed: int = 0) -> np.ndarray:
    """Pick M event indices uniformly across the recording (avoids
    edge events where unfolding behaves differently)."""
    if M >= N:
        return np.arange(N, dtype=np.int64)
    rng = np.random.default_rng(seed)
    # Uniform stratified sample — one event per uniform bin of [0, N).
    return np.sort(rng.choice(N, size=M, replace=False))


def nns_sensitivity(t_k: np.ndarray, M: int = 100, eps_frac: float = EPS_FRAC,
                     seed: int = 0, q_max: int = Q_MAX,
                     min_events_per_q: int = MIN_EVENTS_PER_Q,
                     n_workers: int = 8) -> pd.DataFrame:
    """∂(ks_gue_med)/∂t_k and ∂(rep_med)/∂t_k via two-sided finite
    difference at M sampled events.  Returns DataFrame with columns:
        k_idx, t_k, dks_dt, drep_dt, primary_unperturbed
    """
    t_k = np.sort(np.asarray(t_k, dtype=np.float64))
    N = t_k.size
    if N < 2 * min_events_per_q:
        return pd.DataFrame(columns=['k_idx', 't_k', 'dks_dt', 'drep_dt',
                                       'primary_unperturbed'])

    iei = np.diff(t_k)
    mean_iei = float(iei.mean()) if iei.size > 0 else 1.0
    eps = eps_frac * mean_iei

    sample_idx = _sample_indices(N, M, seed=seed)

    # Baseline classification
    base = classify(t_k, return_full=False, q_max=q_max,
                     min_events_per_q=min_events_per_q)
    base_primary = base['primary']

    # Build perturbation jobs
    args_list = []
    for k in sample_idx:
        t_plus = t_k.copy()
        t_plus[k] += eps
        t_plus = np.sort(t_plus)
        t_minus = t_k.copy()
        t_minus[k] -= eps
        t_minus = np.sort(t_minus)
        args_list.append(('plus', int(k), t_plus, q_max, min_events_per_q))
        args_list.append(('minus', int(k), t_minus, q_max, min_events_per_q))

    if n_workers > 1:
        with Pool(min(n_workers, cpu_count())) as pool:
            results = list(pool.imap(_classify_worker, args_list,
                                       chunksize=8))
    else:
        results = [_classify_worker(a) for a in args_list]

    # Pair up plus/minus by k
    by_k = {}
    for r in results:
        by_k.setdefault(r['k'], {})[r['side']] = r

    rows = []
    for k in sample_idx:
        if int(k) not in by_k:
            continue
        pp = by_k[int(k)].get('plus')
        mm = by_k[int(k)].get('minus')
        if pp is None or mm is None:
            continue
        dks = (pp['ks'] - mm['ks']) / (2.0 * eps) if np.isfinite(pp['ks']) and np.isfinite(mm['ks']) else np.nan
        drep = (pp['rep'] - mm['rep']) / (2.0 * eps) if np.isfinite(pp['rep']) and np.isfinite(mm['rep']) else np.nan
        rows.append(dict(k_idx=int(k), t_k=float(t_k[k]),
                          dks_dt=float(dks), drep_dt=float(drep),
                          primary_unperturbed=base_primary,
                          ks_med_base=base['ks_gue_med'],
                          rep_med_base=base['rep_med']))
    return pd.DataFrame(rows)


def _classify_worker(args):
    side, k, t_perturbed, q_max, min_events_per_q = args
    r = classify(t_perturbed, return_full=False, q_max=q_max,
                  min_events_per_q=min_events_per_q)
    return dict(side=side, k=int(k), ks=r['ks_gue_med'], rep=r['rep_med'])


def rf_per_q_sensitivity(t_k: np.ndarray, M: int = 100,
                          eps_frac: float = EPS_FRAC, seed: int = 0,
                          q_max: int = Q_MAX,
                          n_workers: int = 8) -> tuple[pd.DataFrame, np.ndarray]:
    """∂|a_q|/∂t_k per q via two-sided finite difference at M sampled events.

    Returns:
      df  — long-form DataFrame with columns:
              k_idx, t_k, q, drf_dt   (M*q_max rows)
      base_amps — (q_max,) array of baseline |a_q| values for reference.
    """
    t_k = np.sort(np.asarray(t_k, dtype=np.float64))
    N = t_k.size
    if N < 30:
        return (pd.DataFrame(columns=['k_idx', 't_k', 'q', 'drf_dt']),
                np.zeros(q_max))
    iei = np.diff(t_k)
    mean_iei = float(iei.mean()) if iei.size > 0 else 1.0
    eps = eps_frac * mean_iei

    # Baseline RF amplitudes (indicator-mode, matches joint_q_profile)
    rf_base = ramanujan_fourier(t_k, q_max=q_max, normalize=False)
    base_amps = np.abs(np.asarray(rf_base.get('amplitudes', []), dtype=np.float64))
    if base_amps.size != q_max:
        base_amps = np.full(q_max, np.nan)

    sample_idx = _sample_indices(N, M, seed=seed)

    args_list = []
    for k in sample_idx:
        t_plus = t_k.copy()
        t_plus[k] += eps
        t_plus = np.sort(t_plus)
        t_minus = t_k.copy()
        t_minus[k] -= eps
        t_minus = np.sort(t_minus)
        args_list.append(('plus', int(k), t_plus, q_max))
        args_list.append(('minus', int(k), t_minus, q_max))

    if n_workers > 1:
        with Pool(min(n_workers, cpu_count())) as pool:
            results = list(pool.imap(_rf_worker, args_list, chunksize=8))
    else:
        results = [_rf_worker(a) for a in args_list]

    by_k = {}
    for r in results:
        by_k.setdefault(r['k'], {})[r['side']] = r['amps']

    rows = []
    for k in sample_idx:
        if int(k) not in by_k:
            continue
        ap = by_k[int(k)].get('plus')
        am = by_k[int(k)].get('minus')
        if ap is None or am is None:
            continue
        drf_dt = (ap - am) / (2.0 * eps)
        for q in range(1, q_max + 1):
            rows.append(dict(k_idx=int(k), t_k=float(t_k[k]),
                              q=q, drf_dt=float(drf_dt[q - 1]),
                              base_rf=float(base_amps[q - 1])))
    return pd.DataFrame(rows), base_amps


def _rf_worker(args):
    side, k, t_perturbed, q_max = args
    rf = ramanujan_fourier(t_perturbed, q_max=q_max, normalize=False)
    amps = np.abs(np.asarray(rf.get('amplitudes', []), dtype=np.float64))
    if amps.size != q_max:
        amps = np.full(q_max, np.nan)
    return dict(side=side, k=int(k), amps=amps)


def sensitivity_summary(nns_df: pd.DataFrame,
                          rf_df: pd.DataFrame,
                          base_amps: np.ndarray) -> dict:
    """Compute summary statistics on the per-event sensitivity arrays."""
    summary = dict()
    if len(nns_df) > 0:
        summary['nns_n_events_sampled'] = int(len(nns_df))
        summary['mean_dks_dt'] = float(nns_df['dks_dt'].abs().mean())
        summary['max_dks_dt'] = float(nns_df['dks_dt'].abs().max())
        summary['mean_drep_dt'] = float(nns_df['drep_dt'].abs().mean())
        summary['max_drep_dt'] = float(nns_df['drep_dt'].abs().max())
        # Fraction of events where perturbation would move ks_med by > 0.01
        summary['frac_high_ks_sensitivity'] = float(
            (nns_df['dks_dt'].abs() > 0.01 / max(1e-9, nns_df['dks_dt'].abs().median() * 100)).mean()
        )
    if len(rf_df) > 0:
        # Per-q sensitivity summary
        per_q = rf_df.groupby('q')['drf_dt'].agg(['mean', 'std', lambda x: x.abs().mean()])
        per_q.columns = ['mean_drf', 'std_drf', 'mean_abs_drf']
        summary['rf_per_q'] = per_q.to_dict('index')
        summary['base_rf_amps'] = base_amps.tolist()
    return summary


__all__ = ['nns_sensitivity', 'rf_per_q_sensitivity', 'sensitivity_summary']
