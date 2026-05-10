"""
phase22a/population_events.py — population-event extraction for H2.

Population events are the timestamps of synchronous-firing patterns
across the H2-passing units of a recording.  Two definitions are
implemented; the modal one is exposed via `extract_events`.

  (1) Synchronous-firing definition (default):
        Bin every unit's spike train at BIN_MS resolution.  Sum the
        binary "≥1 spike in bin" indicator across units to get a
        population coactivation count per bin.  An event is the
        timestamp of any bin whose coactivation ≥ K_THRESH units.

  (2) Population-rate envelope:
        Sum spike *counts* across units per bin (not the binary
        indicator).  An event is a peak in the population-count
        signal above the (mean + N_SIGMA × std) threshold, with
        peaks separated by ≥ MIN_REFRACTORY_MS.

Default (1) corresponds most directly to the "≥k units firing within
window w" formulation in the brief.  Sensitivity scans over (k, w)
are exposed via the `extract_events_sensitivity_grid` helper.

For pvc-11 population sizes (70-100 units in H2), k=4-8 in 5-10 ms
bins is a sensible starting range.  We default to k=5, w=5 ms.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)


# Default parameters (sensitivity-scanned downstream)
BIN_MS_DEFAULT = 5.0
K_THRESH_DEFAULT = 5


def build_unit_matrix(rec, unit_ids: list[int],
                       bin_ms: float = BIN_MS_DEFAULT,
                       trial_concat_gap_sec: float = 0.0,
                       ) -> tuple[np.ndarray, float]:
    """Stack selected units' spike trains into a (n_units, n_bins)
    matrix of integer spike counts per bin.

    Concatenates trials end-to-end (with optional gap_sec silence)
    using the same offset bookkeeping as Recording.concatenated_spikes.
    Returns (matrix, total_duration_sec).
    """
    from loader import (
        GRATING_TRIAL_SEC, GRATING_OFFSET_SEC, MOVIE_TRIAL_SEC,
    )
    bin_s = bin_ms / 1000.0
    if rec.subset == 'spontaneous':
        # All units share the same spontaneous duration.
        max_t = max((np.asarray(rec.spike_times[u]).max()
                     if np.asarray(rec.spike_times[u]).size else 0.0)
                    for u in unit_ids)
        total_dur = float(max_t)
        n_bins = int(np.ceil(total_dur / bin_s))
        edges = np.linspace(0, n_bins * bin_s, n_bins + 1)
        mat = np.zeros((len(unit_ids), n_bins), dtype=np.int32)
        for i, u in enumerate(unit_ids):
            sp = np.asarray(rec.spike_times[u]).flatten()
            if sp.size:
                mat[i] = np.histogram(sp, bins=edges)[0]
        return mat, total_dur

    if rec.subset == 'gratings':
        per_trial_dur = GRATING_TRIAL_SEC
        n_chunks = rec.n_conditions * rec.n_trials
    else:  # movies
        per_trial_dur = MOVIE_TRIAL_SEC
        n_chunks = rec.n_trials

    chunk_bins = int(np.ceil(per_trial_dur / bin_s))
    total_bins = n_chunks * chunk_bins
    total_dur = total_bins * bin_s
    mat = np.zeros((len(unit_ids), total_bins), dtype=np.int32)

    chunk_idx = 0
    for i, u in enumerate(unit_ids):
        chunk_idx = 0
        if rec.subset == 'gratings':
            for c in range(rec.n_conditions):
                for t in range(rec.n_trials):
                    sp = np.asarray(rec.spike_times[u][c][t]).flatten()
                    sp = sp[(sp >= GRATING_OFFSET_SEC) &
                             (sp <  GRATING_OFFSET_SEC + GRATING_TRIAL_SEC)]
                    sp = sp - GRATING_OFFSET_SEC
                    bin_indices = np.floor(sp / bin_s).astype(np.int64)
                    bin_indices = bin_indices[(bin_indices >= 0) &
                                                (bin_indices < chunk_bins)]
                    bin_offset = chunk_idx * chunk_bins
                    np.add.at(mat[i], bin_indices + bin_offset, 1)
                    chunk_idx += 1
        else:
            for t in range(rec.n_trials):
                sp = np.asarray(rec.spike_times[u][t]).flatten()
                sp = sp[(sp >= 0) & (sp < per_trial_dur)]
                bin_indices = np.floor(sp / bin_s).astype(np.int64)
                bin_indices = bin_indices[(bin_indices >= 0) &
                                            (bin_indices < chunk_bins)]
                bin_offset = chunk_idx * chunk_bins
                np.add.at(mat[i], bin_indices + bin_offset, 1)
                chunk_idx += 1
    return mat, total_dur


def extract_events(unit_matrix: np.ndarray,
                    bin_ms: float = BIN_MS_DEFAULT,
                    k_thresh: int = K_THRESH_DEFAULT) -> np.ndarray:
    """Synchronous-firing population events: timestamps of bins where
    ≥ k_thresh distinct units fired ≥1 spike.

    Returns event timestamps in seconds, taken at the bin centre.
    """
    binary = (unit_matrix > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    bin_idx = np.where(coact >= k_thresh)[0]
    bin_s = bin_ms / 1000.0
    return (bin_idx + 0.5) * bin_s


def extract_events_envelope(unit_matrix: np.ndarray,
                              bin_ms: float = BIN_MS_DEFAULT,
                              n_sigma: float = 2.0,
                              min_refractory_ms: float = 20.0) -> np.ndarray:
    """Envelope-based events: peaks in the population spike-count
    summed across units, above (mean + n_sigma × std), separated by
    at least min_refractory_ms."""
    from scipy.signal import find_peaks
    pop_count = unit_matrix.sum(axis=0).astype(np.float64)
    if not pop_count.size: return np.zeros(0)
    thr = pop_count.mean() + n_sigma * pop_count.std()
    distance = max(1, int(round(min_refractory_ms / bin_ms)))
    peaks, _ = find_peaks(pop_count, height=thr, distance=distance)
    return (peaks + 0.5) * (bin_ms / 1000.0)


__all__ = [
    'BIN_MS_DEFAULT', 'K_THRESH_DEFAULT',
    'build_unit_matrix', 'extract_events', 'extract_events_envelope',
]
