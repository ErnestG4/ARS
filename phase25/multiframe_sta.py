"""
phase25/multiframe_sta.py — multi-frame (spatiotemporal) STA computation
and projection.

Phase 22b's coupled-GLM used a single-frame STA: STA_i = (n_pixels,)
spatial filter, projected to a per-bin scalar drive.  On natural-movie
data this left the slow stim temporal autocorrelation (~30-40 ms)
unmodelled, and the GLM optimizer mis-routed it to the history kernel —
producing either runaway-positive history (unconstrained variant) or
both kernels collapsed (canonical variant).

Multi-frame STA: STA_i has temporal lag structure
    STA_i ∈ R^(n_lags × n_pixels)
so the projected drive at bin t becomes
    drive_i(t) = sum_τ STA_i[τ, :] · stim[t-τ, :]
which can absorb stim temporal autocorrelation over the lag window.

Convention (matches Phase 25 brief):
  - "n-frame STA" means the STA spans n bins of stim history (τ = 0 ..
    n-1).  Single-frame STA → n_lags=1 → instantaneous, spatial-only,
    equivalent to Phase 22b's baseline.  Temporal extent in ms is
    n_lags × bin_width_ms.
  - The lag axis is in bins, not movie frames.  At 5 ms bins a 4-frame
    STA covers 20 ms; at 20 ms bins it covers 80 ms.  The 2-D grid
    (n_lags × bin_width) sweeps the boundary at which the STA's
    temporal extent matches the ~40 ms stim autocorrelation.

Computation uses the across-trial average trick (Phase 22b): the
stimulus is identical every trial, so spike-triggered averaging reduces
to (avg_response_per_trial @ stim_at_lag) for each lag.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))

from loader import MOVIE_TRIAL_SEC


def build_per_bin_stim(Z: np.ndarray, bin_ms: float,
                        bins_per_trial: int) -> np.ndarray:
    """Up-sample (n_frames, n_pixels) movie matrix to per-bin stimulus at
    the given bin width.

    Returns (bins_per_trial, n_pixels) float32.  Pads with zeros if the
    stim is shorter than bins_per_trial after up-sampling; truncates if
    longer.  Uses the same nearest-frame up-sampling as Phase 22b's
    `_load_movie`-based pipeline.
    """
    n_frames = Z.shape[0]
    # Bins per movie frame at this bin width:
    bins_per_frame_movie = max(1, int(round(MOVIE_TRIAL_SEC * 1000
                                              / n_frames / bin_ms)))
    per_bin = np.repeat(Z, bins_per_frame_movie, axis=0).astype(np.float32)
    if per_bin.shape[0] > bins_per_trial:
        per_bin = per_bin[:bins_per_trial]
    elif per_bin.shape[0] < bins_per_trial:
        pad = np.zeros((bins_per_trial - per_bin.shape[0], Z.shape[1]),
                       dtype=np.float32)
        per_bin = np.concatenate([per_bin, pad], axis=0)
    return per_bin


def compute_multiframe_sta(real_mat: np.ndarray,
                             per_bin_stim: np.ndarray,
                             n_lags: int, n_trials: int,
                             bins_per_trial: int,
                             ) -> np.ndarray:
    """Compute per-unit spatiotemporal STA over n_lags bins of history.

    real_mat:      (n_units, n_trials*bins_per_trial) integer spike counts.
    per_bin_stim:  (bins_per_trial, n_pixels) per-bin stimulus
                    (same every trial — the movie is replayed identically).
    n_lags:        number of past bins to include in the STA (lag = 0..n_lags-1).
    Returns:       (n_units, n_lags, n_pixels) float32, mean-centred and
                    flat-L2-normalised per unit (so the projected drive
                    has comparable scale across units).
    """
    n_units = real_mat.shape[0]
    n_pixels = per_bin_stim.shape[1]

    # Average response across trials → (n_units, bins_per_trial)
    avg_response = (real_mat.astype(np.float32)
                     .reshape(n_units, n_trials, bins_per_trial)
                     .mean(axis=1))
    spike_totals_per_trial = avg_response.sum(axis=1, keepdims=True) + 1e-9

    sta = np.zeros((n_units, n_lags, n_pixels), dtype=np.float32)
    for tau in range(n_lags):
        # stim at lag τ: stim_at_lag[t] = per_bin_stim[t - τ], with
        # zero-fill for t < τ.  Across-trial averaging means we treat
        # each trial's pre-trial as zero (no stimulus prior to trial
        # onset within the loader's accounting).
        if tau == 0:
            stim_lag = per_bin_stim
        else:
            stim_lag = np.zeros_like(per_bin_stim)
            stim_lag[tau:] = per_bin_stim[:bins_per_trial - tau]
        # (n_units, bins_per_trial) @ (bins_per_trial, n_pixels)
        #   → (n_units, n_pixels), weighted by per-bin spike count
        sta[:, tau, :] = (avg_response @ stim_lag) / spike_totals_per_trial

    # Mean-centre and L2-normalise per unit (across flat lag×pixel).
    sta_flat = sta.reshape(n_units, -1)
    sta_flat = sta_flat - sta_flat.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(sta_flat, axis=1, keepdims=True) + 1e-9
    sta_flat = sta_flat / norms
    return sta_flat.reshape(n_units, n_lags, n_pixels)


def project_sta_to_drive(sta: np.ndarray,
                           per_bin_stim: np.ndarray,
                           bins_per_trial: int) -> np.ndarray:
    """Project per-bin stim through spatiotemporal STA to get per-unit
    scalar drive per bin.

    sta:           (n_units, n_lags, n_pixels)
    per_bin_stim:  (bins_per_trial, n_pixels)

    Returns:       (n_units, bins_per_trial)
        drive[i, t] = sum_τ sta[i, τ, :] · per_bin_stim[t - τ, :]
    with τ = 0..n_lags-1, zero-fill for t < τ (matches the STA's own
    zero-fill convention).
    """
    n_units, n_lags, _ = sta.shape
    drive = np.zeros((n_units, bins_per_trial), dtype=np.float32)
    for tau in range(n_lags):
        # contribution at lag τ: sta[:, τ, :] @ stim[t-τ, :]
        # Precompute per-bin projection through this lag's filter, then
        # shift it forward by τ bins.
        lag_proj = sta[:, tau, :] @ per_bin_stim.T   # (n_units, bins_per_trial)
        if tau == 0:
            drive += lag_proj
        else:
            drive[:, tau:] += lag_proj[:, :bins_per_trial - tau]
    return drive


__all__ = [
    'build_per_bin_stim', 'compute_multiframe_sta', 'project_sta_to_drive',
]
