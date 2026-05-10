"""
dfa.py — Detrended fluctuation analysis (DFA) Hurst-exponent estimator.

Implements the standard Peng et al. 1994 DFA1 (linear-detrend) algorithm:

  1. Integrate the zero-mean series: Y(i) = Σ_{k=1}^{i} (X(k) − ⟨X⟩).
  2. Partition Y into non-overlapping boxes of length n (forwards and
     backwards, then averaged).
  3. Within each box, linear-detrend Y; compute mean-square fluctuation.
  4. Average across boxes to get F(n).  F(n) ∝ n^H asymptotically.
  5. Linear regression of log F(n) vs log n recovers the Hurst exponent H.

Interpretation:
  H ≈ 0.5  → uncorrelated (or short-range correlated) series.
  H > 0.5  → positive long-range correlation (persistence).
  H < 0.5  → anti-persistence.

Used in Phase 20 to verify Kitsak-consistency on quiescent BGP IEI
sequences (Kitsak et al. 2015 reported H ≈ 0.7–0.9 for backbone BGP).
"""
from __future__ import annotations
import numpy as np


def dfa_hurst(
        series: np.ndarray,
        scales: np.ndarray | None = None,
        order: int = 1,
        ) -> dict:
    """Detrended fluctuation analysis on a real-valued series.

    Parameters
    ----------
    series : array-like
        The input (typically inter-event-interval sequence, or a
        time-binned event-count signal).  Must have ≥ 64 samples.
    scales : array of int, optional
        Box sizes at which to evaluate F(n).  Default: 16 logarithmically
        spaced scales between 4 and len(series)//4.
    order : int
        Polynomial detrending order.  1 = linear (DFA1, default).

    Returns
    -------
    dict with keys
      - hurst: float — slope of log F(n) vs log n.
      - intercept: float
      - r2: float — goodness-of-fit of the linear regression.
      - scales: 1-D array of n values used.
      - F: 1-D array of fluctuation values F(n).
    """
    x = np.asarray(series, dtype=np.float64).ravel()
    if x.size < 64:
        raise ValueError(f"series too short ({x.size}) for DFA; need ≥ 64")
    # 1. Integrate the zero-mean series.
    y = np.cumsum(x - x.mean())
    # 2. Choose default scales if not supplied.
    if scales is None:
        n_min = 4
        n_max = max(8, x.size // 4)
        scales = np.unique(np.round(np.geomspace(n_min, n_max,
                                                   16)).astype(int))
    scales = np.asarray(scales, dtype=int)
    F_vals = []
    for n in scales:
        if n < order + 2 or n > x.size:
            F_vals.append(np.nan)
            continue
        n_boxes = x.size // n
        if n_boxes < 4:
            F_vals.append(np.nan)
            continue
        # Reshape into (n_boxes, n) — reuse for forward direction.
        # Standard DFA also runs backward; for simplicity we run forward
        # only here (forward-only DFA1 is the most common variant in
        # practice and what Peng 1994 originally specified).
        boxes = y[:n_boxes * n].reshape(n_boxes, n)
        t_local = np.arange(n)
        fluct_sq = []
        for box in boxes:
            coefs = np.polyfit(t_local, box, deg=order)
            trend = np.polyval(coefs, t_local)
            fluct_sq.append(np.mean((box - trend) ** 2))
        F = float(np.sqrt(np.mean(fluct_sq)))
        F_vals.append(F)
    F_vals = np.asarray(F_vals, dtype=np.float64)
    valid = np.isfinite(F_vals) & (F_vals > 0)
    if valid.sum() < 4:
        return dict(hurst=float('nan'), intercept=float('nan'),
                     r2=float('nan'), scales=scales, F=F_vals)
    log_n = np.log(scales[valid].astype(np.float64))
    log_F = np.log(F_vals[valid])
    slope, intercept = np.polyfit(log_n, log_F, 1)
    pred = slope * log_n + intercept
    ss_res = float(np.sum((log_F - pred) ** 2))
    ss_tot = float(np.sum((log_F - log_F.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return dict(hurst=float(slope), intercept=float(intercept),
                 r2=float(r2), scales=scales, F=F_vals)


__all__ = ['dfa_hurst']
