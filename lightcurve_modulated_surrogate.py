"""
lightcurve_modulated_surrogate.py — Phase 21 Tier 4.

GRB-specific lightcurve-modulated Poisson surrogate: generate
synthetic photon arrivals with a time-varying rate matching the
empirical lightcurve.  This is the GRB analogue of Phase 20's
topology-aware Hawkes — the strongest available domain-natural null
model.

If the framework's QPO classification reproduces on the surrogate,
the empirical signature is reproducible from the lightcurve shape
alone (an inhomogeneous Poisson process at the empirical rate); if
the classification differs, there is timing structure beyond the
rate envelope.

API:

    surrogate_events = lightcurve_modulated_poisson(
        empirical_times_us, bin_us, smoothing_window, rng=None)

The empirical lightcurve is computed by binning events at `bin_us`
microseconds and smoothing with a Savitzky-Golay filter at the
specified window.  Synthetic events are then drawn from an
inhomogeneous Poisson process whose rate piecewise matches the
smoothed lightcurve.
"""
from __future__ import annotations

import numpy as np
from typing import Optional


def empirical_lightcurve(
        events_us: np.ndarray,
        bin_us: int = 1_000,
        window_bins: int = 21,
        ) -> tuple[np.ndarray, np.ndarray]:
    """Bin photon arrival times into bin_us-wide bins; smooth with a
    centered moving average of `window_bins` bins.

    Returns (bin_edges_us, smoothed_rate_per_bin).  Smoothed rate is
    in events-per-bin (multiply by 1e6/bin_us for events-per-second).
    """
    if events_us.size < 2:
        return np.array([0]), np.array([0.0])
    t_lo = int(events_us.min())
    t_hi = int(events_us.max())
    n_bins = max(1, (t_hi - t_lo) // bin_us + 1)
    edges = np.arange(t_lo, t_lo + (n_bins + 1) * bin_us, bin_us)
    counts, _ = np.histogram(events_us, bins=edges)
    # Centered moving average smoothing (Savitzky-Golay degenerates to
    # this at degree 0; we use the simple moving average for speed and
    # to avoid scipy.signal dep here).
    if window_bins > 1 and counts.size > window_bins:
        kernel = np.ones(window_bins) / window_bins
        smoothed = np.convolve(counts.astype(np.float64), kernel,
                                 mode='same')
    else:
        smoothed = counts.astype(np.float64)
    return edges, smoothed


def lightcurve_modulated_poisson(
        events_us: np.ndarray,
        bin_us: int = 1_000,
        smoothing_window: int = 21,
        rng: Optional[np.random.Generator] = None,
        ) -> np.ndarray:
    """Generate inhomogeneous Poisson events with rate matching the
    smoothed empirical lightcurve.

    For each bin: draw the count from Poisson(λ = empirical_smoothed),
    then place each event uniformly at random within the bin.

    Returns sorted event times in microseconds (int64).
    """
    if rng is None:
        rng = np.random.default_rng()
    edges, smoothed = empirical_lightcurve(events_us, bin_us=bin_us,
                                              window_bins=smoothing_window)
    if smoothed.size == 0:
        return np.zeros(0, dtype=np.int64)
    # Per-bin Poisson sample
    counts = rng.poisson(np.maximum(smoothed, 0.0))
    out = []
    for i, c in enumerate(counts):
        if c <= 0:
            continue
        # Place c events uniformly in [edges[i], edges[i+1])
        u = rng.uniform(edges[i], edges[i + 1], size=int(c))
        out.append(u)
    if not out:
        return np.zeros(0, dtype=np.int64)
    return np.sort(np.concatenate(out)).astype(np.int64)


__all__ = ['empirical_lightcurve', 'lightcurve_modulated_poisson']
