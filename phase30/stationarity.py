"""
phase30/stationarity.py — non-overlapping-window NNS stationarity check.

Per Phase 30 user course-correction: before reporting full-sequence ARS
classification, split each spike train into non-overlapping time windows
and re-classify per window.  If modal classification and continuous
metrics (ks_gue_med, rep_med) are stable across windows, the full-
sequence analysis is fine.  If not, the analysis is time-aware and the
report should distinguish stable vs transient structure.

Special importance near K_c: slow order-parameter fluctuations
(critical slowing down) can produce time-varying effective
synchronization that the full-sequence statistic averages over.  At
critical-regime cells we run a finer split (default 10 windows) to
detect transient TR/BR/BL phases.

API:
    classify_in_windows(events, n_windows, total_duration, q_max) → list[dict]
    stationarity_summary(per_window_classifications) → dict
"""
from __future__ import annotations

import os
import sys
from typing import Optional

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q


def classify_in_windows(events: np.ndarray, n_windows: int,
                          total_duration: float, q_max: int = Q_MAX,
                          min_events_per_q: int = MIN_EVENTS_PER_Q) -> list[dict]:
    """Split events into n_windows non-overlapping time windows of equal
    duration; classify each window separately.

    Returns a list of n_windows dicts with keys:
        window_idx, t_start, t_end, n_events,
        primary, rep_med, ks_gue_med, n_well
    Windows with too few events return primary='underpowered'.
    """
    out = []
    win_dur = total_duration / n_windows
    events = np.asarray(events, dtype=np.float64)
    for w in range(n_windows):
        t0 = w * win_dur
        t1 = (w + 1) * win_dur
        sub = events[(events >= t0) & (events < t1)]
        if sub.size < min_events_per_q:
            out.append(dict(window_idx=w, t_start=t0, t_end=t1,
                             n_events=int(sub.size),
                             primary='underpowered',
                             rep_med=np.nan, ks_gue_med=np.nan, n_well=0))
            continue
        # Re-anchor sub to the window start so the unit-mean unfolding works
        # on the within-window IEI distribution.
        r = classify(sub - t0, return_full=False, q_max=q_max,
                       min_events_per_q=min_events_per_q)
        out.append(dict(window_idx=w, t_start=t0, t_end=t1,
                         n_events=int(sub.size),
                         primary=r['primary'], rep_med=r['rep_med'],
                         ks_gue_med=r['ks_gue_med'], n_well=r['n_well']))
    return out


def stationarity_summary(per_window: list[dict],
                          full_sequence: Optional[dict] = None) -> dict:
    """Summarise per-window classifications.

    Returns a dict with:
        n_windows, n_well_windows, modal_window, fraction_modal,
        rep_med_across_windows_mean, rep_med_across_windows_std,
        ks_med_across_windows_mean, ks_med_across_windows_std,
        stationary  — bool: True if modal stable across all well-powered
                      windows AND continuous-metric std/mean ≤ 0.2
        agree_with_full  — bool: True if full-sequence modal == modal_window
    """
    if not per_window:
        return dict(n_windows=0, stationary=True, modal_window=None,
                     agree_with_full=True)
    well = [w for w in per_window if w['primary'] != 'underpowered']
    n = len(per_window)
    n_well = len(well)
    if n_well == 0:
        return dict(n_windows=n, n_well_windows=0,
                     modal_window='underpowered', fraction_modal=np.nan,
                     rep_med_across_windows_mean=np.nan,
                     rep_med_across_windows_std=np.nan,
                     ks_med_across_windows_mean=np.nan,
                     ks_med_across_windows_std=np.nan,
                     stationary=True, agree_with_full=False)
    primaries = [w['primary'] for w in well]
    counts = pd.Series(primaries).value_counts()
    modal = counts.idxmax()
    frac_modal = float(counts.max() / n_well)
    reps = np.asarray([w['rep_med'] for w in well], dtype=np.float64)
    kss = np.asarray([w['ks_gue_med'] for w in well], dtype=np.float64)
    rep_mean, rep_std = float(np.nanmean(reps)), float(np.nanstd(reps))
    ks_mean, ks_std = float(np.nanmean(kss)), float(np.nanstd(kss))
    # Stationarity heuristic: modal stable in ≥ 90% of windows AND
    # continuous-metric coefficient-of-variation ≤ 0.2.
    cv_rep = rep_std / max(abs(rep_mean), 1e-6)
    cv_ks = ks_std / max(abs(ks_mean), 1e-6)
    stationary = (frac_modal >= 0.90 and cv_rep <= 0.2 and cv_ks <= 0.2)
    agree_with_full = (full_sequence is not None
                        and full_sequence.get('primary') == modal)
    return dict(
        n_windows=n,
        n_well_windows=n_well,
        modal_window=modal,
        fraction_modal=frac_modal,
        rep_med_across_windows_mean=rep_mean,
        rep_med_across_windows_std=rep_std,
        ks_med_across_windows_mean=ks_mean,
        ks_med_across_windows_std=ks_std,
        cv_rep_across_windows=float(cv_rep),
        cv_ks_across_windows=float(cv_ks),
        stationary=bool(stationary),
        agree_with_full=bool(agree_with_full),
        primaries_per_window=primaries,
    )


__all__ = ['classify_in_windows', 'stationarity_summary']
