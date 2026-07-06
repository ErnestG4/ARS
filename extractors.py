"""
extractors.py — Unified boundary-extractor API for Phase 16 invariance test.

Six methods, all input a sorted point-process `t_k` (np.float64 array) and
output a sorted point-process `t_k_out` (np.float64 array).  For
continuous-signal extractors, an internal `synthesize_continuous` routine
first builds a Gaussian-smoothed event density on a fine grid; the
extractor then operates on that synthetic continuous trace.  This is the
spec's "drive a signal from each event position, then apply the extractor
to the filtered signal" protocol — testing whether the
event → continuous → extractor → events round trip preserves the
underlying universality class.

The six extractors:

    direct_events           — identity (point process passes through)
    pll_passage             — analytical passage through PLL at q=1
                              (calibrated baseline)
    find_peaks_prominence   — scipy.signal.find_peaks on synthesized
                              signal (the §7.ter.19 mechanism)
    derivative_zeros        — local maxima via dy/dx sign change
    threshold_crossing      — upcrossings of mean + k·σ
    modular_bin_events      — events at integer time bins (output: bin
                              indices that contain events)
"""
from __future__ import annotations
import numpy as np
from typing import Optional


# ─── Continuous-signal synthesis ────────────────────────────────────────────

def synthesize_continuous(t_k: np.ndarray,
                          oversample: int = 10,
                          sigma_frac: float = 0.3,
                          ) -> tuple[np.ndarray, np.ndarray]:
    """Build a Gaussian-smoothed event-density signal from point process.

    Each event contributes a Gaussian pulse with σ = sigma_frac × mean
    spacing.  Output grid samples at oversample × per-mean-spacing.
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 2:
        return np.array([t[0] if t.size else 0.0]), np.zeros(1)
    mean_sp = float(np.mean(np.diff(t)))
    if mean_sp <= 0:
        return np.array([t[0]]), np.zeros(1)
    sigma = max(sigma_frac * mean_sp, 1e-9)
    dt = mean_sp / oversample
    pad = max(5 * sigma, mean_sp)
    t_grid = np.arange(t[0] - pad, t[-1] + pad + dt, dt)
    sig = np.zeros_like(t_grid)
    # Chunked vectorized accumulation to avoid (n_grid × n_events) blow-up.
    chunk_size = max(1, 200)
    for i in range(0, t.size, chunk_size):
        ev = t[i:i + chunk_size]
        diff = (t_grid[:, None] - ev[None, :]) / sigma
        sig += np.exp(-0.5 * diff * diff).sum(axis=1)
    return t_grid, sig


# ─── Extractors ──────────────────────────────────────────────────────────────

def extract_direct_events(t_k: np.ndarray) -> np.ndarray:
    """Identity — point process passes through unchanged."""
    return np.sort(np.asarray(t_k, dtype=np.float64))


def extract_pll_passage(t_k: np.ndarray, fc_ref: float = 1.0) -> np.ndarray:
    """Analytical passage through the q=1 PLL band (baseline).

    Returns the unit-mean-normalised passage spacings cumulatively
    summed back into an event sequence.  For a unit-mean point process,
    this is the identity (since passage = t·1 − 1 just shifts t and
    spacings normalize to 1 per spacing).  Provides the calibrated
    baseline for class invariance under the canonical ARS metric.
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    passage = (t * fc_ref - 1.0)
    passage = passage[passage > 0]
    if passage.size < 2:
        return passage
    sp = np.diff(passage)
    if sp.size == 0 or sp.mean() <= 0:
        return passage
    return np.cumsum(sp / sp.mean())


def extract_find_peaks_prominence(t_k: np.ndarray,
                                   prominence: float = 0.3,
                                   oversample: int = 10,
                                   sigma_frac: float = 0.3) -> np.ndarray:
    """find_peaks on synthesized continuous trace (the §7.ter.19 mechanism).

    Uses the prominence threshold = prominence × signal std.  Tests
    whether the find_peaks artifact survives the round trip
    point-process → continuous → find_peaks → event positions.
    """
    from scipy.signal import find_peaks
    t_grid, sig = synthesize_continuous(t_k, oversample=oversample,
                                         sigma_frac=sigma_frac)
    if sig.size < 5: return np.zeros(0)
    prom_thr = max(prominence * float(sig.std()), 1e-9)
    peaks, _ = find_peaks(sig, prominence=prom_thr)
    return t_grid[peaks]


def extract_derivative_zeros(t_k: np.ndarray,
                              oversample: int = 10,
                              sigma_frac: float = 0.3) -> np.ndarray:
    """Local maxima via discrete derivative sign change (no prominence)."""
    t_grid, sig = synthesize_continuous(t_k, oversample=oversample,
                                         sigma_frac=sigma_frac)
    if sig.size < 3: return np.zeros(0)
    ds = np.diff(sig)
    # Local maxima: sign goes from + to -
    is_peak = (ds[:-1] > 0) & (ds[1:] <= 0)
    idx = np.where(is_peak)[0] + 1
    return t_grid[idx]


def extract_threshold_crossing(t_k: np.ndarray,
                                k: float = 1.0,
                                oversample: int = 10,
                                sigma_frac: float = 0.3) -> np.ndarray:
    """Upcrossings of mean + k·σ on the synthesized continuous trace."""
    t_grid, sig = synthesize_continuous(t_k, oversample=oversample,
                                         sigma_frac=sigma_frac)
    if sig.size < 2: return np.zeros(0)
    thr = sig.mean() + k * sig.std()
    above = sig > thr
    if above.sum() < 2: return np.zeros(0)
    transitions = np.diff(above.astype(np.int8))
    upcross_idx = np.where(transitions == 1)[0] + 1
    return t_grid[upcross_idx]


def extract_modular_bin_events(t_k: np.ndarray,
                                n_bins: Optional[int] = None) -> np.ndarray:
    """Bin events at integer time positions; output bin indices that
    contain events.  Tests whether integer-binning imposes its own
    rhythm on the point process."""
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 2: return t
    if n_bins is None:
        n_bins = int(np.ceil(t.max() - t.min())) + 1
    if n_bins < 5: return t
    bin_idx = np.clip(np.floor(t - t.min()).astype(np.int64), 0, n_bins - 1)
    counts = np.bincount(bin_idx, minlength=n_bins)
    bins_with_events = np.where(counts > 0)[0]
    return bins_with_events.astype(np.float64)


# ─── Registry / dispatch ─────────────────────────────────────────────────────

EXTRACTORS = {
    'direct_events':           extract_direct_events,
    'pll_passage':             extract_pll_passage,
    'find_peaks_prominence':   extract_find_peaks_prominence,
    'derivative_zeros':        extract_derivative_zeros,
    'threshold_crossing':      extract_threshold_crossing,
    'modular_bin_events':      extract_modular_bin_events,
}


def extract(t_k, name: str, **kwargs) -> np.ndarray:
    """Dispatch by name.  Returns sorted t_k_out (float64)."""
    if name not in EXTRACTORS:
        raise ValueError(f"unknown extractor: {name!r}; "
                          f"valid: {list(EXTRACTORS)}")
    out = EXTRACTORS[name](t_k, **kwargs)
    return np.sort(np.asarray(out, dtype=np.float64))


__all__ = list(EXTRACTORS.keys()) + ['extract', 'EXTRACTORS', 'synthesize_continuous']
