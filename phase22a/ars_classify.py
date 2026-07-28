"""
phase22a/ars_classify.py — thin wrapper around joint_q_profile +
joint_quadrant_diagnostic with the Phase 22a defaults.

Outputs both the multi-order signature (full per-q DataFrame) and the
modal-quadrant collapse, so downstream code can choose the resolution
appropriate for each H1/H2 sub-question without re-running the engine.

Conventions (matched to Phase 21):
    Q_MAX = 30
    MIN_EVENTS_PER_Q = 30
    JPF_CAP = 1500     (subsample if events.size > JPF_CAP)

Pre-processing: input event-time array → unit-mean unfolding → engine.
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

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic


Q_MAX = 30
MIN_EVENTS_PER_Q = 30
JPF_CAP = 1500


def unfold_unit_mean(t: np.ndarray, cap: int = JPF_CAP) -> np.ndarray:
    """Unit-mean unfolding with optional event-count cap (decimation)."""
    t = np.asarray(t, dtype=np.float64)
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def unfold_unit_mean_windowed(t: np.ndarray, window: int = 200, cap: int = JPF_CAP) -> np.ndarray:
    """THE PROPAGATED REPAIR for the GLOBAL-normalisation defect
    (CLUSTERING_COUPLING_FINDINGS.md:101, "CV-16 drift").

    `unfold_unit_mean` divides by the GLOBAL mean spacing, which removes a constant rate but NOT
    within-cell drift: a cell whose rate halves partway through keeps that drift in its spacings,
    and every downstream spacing statistic reads the drift as structure. Normalising in windows of
    `window` spacings removes slow rate change while leaving short-range structure intact.

    Deployed `unfold_unit_mean` retained bit-identical -- banked numbers depend on it."""
    t = np.asarray(t, dtype=np.float64)
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    out = np.empty_like(sp)
    for i in range(0, sp.size, window):
        blk = sp[i:i + window]
        m = blk.mean()
        out[i:i + window] = blk / m if m > 0 else blk
    return np.cumsum(np.concatenate([[0.0], out]))


def classify(events: np.ndarray,
             q_max: int = Q_MAX,
             min_events_per_q: int = MIN_EVENTS_PER_Q,
             return_full: bool = True) -> dict:
    """Run the full ARS classification pipeline on a sorted event-time array.

    Returns:
        primary           — modal quadrant across well-powered q-bands
                            (e.g., 'BL', 'TR', 'BR_artifact', 'TL', 'underpowered')
        rep_med           — median rep_int_q across well-powered q-bands
        ks_gue_med        — median KS_GUE across well-powered q-bands
        n_events_in       — total events passed in (before unfolding/cap)
        n_events_used     — events after cap+unfold
        n_well            — number of well-powered q-bands
        per_q             — full DataFrame from joint_quadrant_diagnostic
                            (None when return_full=False)
    """
    n_in = int(np.asarray(events).size)
    if n_in < min_events_per_q:
        return dict(primary='underpowered', rep_med=np.nan, rep_med_signed=np.nan, ks_gue_med=np.nan,
                    n_events_in=n_in, n_events_used=0, n_well=0, per_q=None)
    ev_unit = unfold_unit_mean(events)
    n_used = int(ev_unit.size)
    if n_used < min_events_per_q:
        return dict(primary='underpowered', rep_med=np.nan, rep_med_signed=np.nan, ks_gue_med=np.nan,
                    n_events_in=n_in, n_events_used=n_used, n_well=0, per_q=None)
    j = joint_q_profile(ev_unit, q_max=q_max,
                         min_events_per_q=min_events_per_q)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return dict(primary='underpowered', rep_med=np.nan, rep_med_signed=np.nan, ks_gue_med=np.nan,
                    n_events_in=n_in, n_events_used=n_used, n_well=0,
                    per_q=qd if return_full else None)
    counts = well['quadrant'].value_counts()
    # REPAIR 2026-07-28 (R-173). `rep_med` is the median of the CLIPPED `rep_int_q`, which
    # saturates to exactly 0 for any clustered band, so a clustered cell reports 0.0000 and its
    # magnitude is erased. `rep_med_signed` is the same median over the SIGNED field. Added
    # ALONGSIDE, never replacing: `rep_med` stays bit-identical because every banked coordinate,
    # parquet and finding came off it, and the two must be comparable on the same cells.
    _signed = (float(well['rep_int_signed_q'].median())
               if 'rep_int_signed_q' in well.columns else float('nan'))
    return dict(
        primary=str(counts.idxmax()),
        rep_med=float(well['rep_int_q'].median()),
        rep_med_signed=_signed,
        ks_gue_med=float(well['ks_gue_q'].median()),
        n_events_in=n_in,
        n_events_used=n_used,
        n_well=int(len(well)),
        per_q=qd if return_full else None,
    )


def per_q_columns(per_q: Optional[pd.DataFrame]) -> dict:
    """Flatten the per-q DataFrame into a dict of arrays for parquet storage.

    Returns columns:
      quadrants_per_q : list[str]   length q_max
      rep_int_per_q   : list[float] length q_max
      ks_gue_per_q    : list[float] length q_max
      rf_amp_per_q    : list[float] length q_max
      rf_spike_per_q  : list[bool]  length q_max
    """
    if per_q is None:
        return dict(quadrants_per_q=None, rep_int_per_q=None,
                    ks_gue_per_q=None, rf_amp_per_q=None,
                    rf_spike_per_q=None)
    return dict(
        quadrants_per_q=per_q['quadrant'].tolist(),
        rep_int_per_q=per_q['rep_int_q'].tolist(),
        ks_gue_per_q=per_q['ks_gue_q'].tolist(),
        rf_amp_per_q=per_q['rf_amplitude_q'].tolist(),
        rf_spike_per_q=per_q['rf_spike'].tolist(),
    )


__all__ = [
    'Q_MAX', 'MIN_EVENTS_PER_Q', 'JPF_CAP',
    'unfold_unit_mean', 'classify', 'per_q_columns',
]
