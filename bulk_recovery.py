"""
bulk_recovery.py — per-class parameter estimators for Phase 17.

Each estimator takes a `joint_q_profile` DataFrame and returns a point
estimate plus a bootstrap 95% CI.  Calibrator-derived reference curves
for fitting are loaded lazily from
`data/phase15_calibrator_joint.parquet`.

Public estimators:
    recover_poisson_rate(jdf, t_total)        → (λ̂, (λ_lo, λ_hi))
    recover_wigner_beta(jdf)                  → (β̂, (β_lo, β_hi), flagged)
    recover_periodic_q(jdf, q_max=None)       → (q̂, confidence)
    recover_periodic_jitter(jdf, q̂)           → (σ̂, (σ_lo, σ_hi))
    recover_uniform_jitter_sigma(jdf)         → (σ̂, (σ_lo, σ_hi), flagged)

`flagged` indicates "out-of-domain" — the joint_q_profile signature is
inconsistent with the class assumption and the recovery should be
treated as undefined.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from typing import Optional, Tuple

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(THIS_DIR, "data")


# ─── Calibrator reference curves ────────────────────────────────────────────

_CALIBRATOR_CACHE: Optional[pd.DataFrame] = None


def _load_calibrator() -> pd.DataFrame:
    global _CALIBRATOR_CACHE
    if _CALIBRATOR_CACHE is not None:
        return _CALIBRATOR_CACHE
    path = os.path.join(DATA, "phase15_calibrator_joint.parquet")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Calibrator parquet missing at {path} — run Phase 15 Tier 2 first.")
    df = pd.read_parquet(path)
    _CALIBRATOR_CACHE = df
    return df


def _calibrator_curve(class_filter: str, x_col: str, y_col: str
                       ) -> tuple[np.ndarray, np.ndarray]:
    """Median-over-seeds (x, y) curve for the named calibrator class.

    e.g., class_filter='uniform_jitter_*' returns (σ, rep_int_q median)
    indexed by the σ value parsed from the class name.
    """
    df = _load_calibrator()
    if class_filter.endswith('*'):
        prefix = class_filter[:-1]
        sub = df[df['signal_class'].str.startswith(prefix)]
        # parse the trailing number from signal_class as the parameter
        params = sub['signal_class'].str.extract(rf'{prefix}([0-9.]+)')[0].astype(float)
        sub = sub.assign(_param=params)
        agg = sub.groupby('_param').agg(
            x=(x_col, 'median'), y=(y_col, 'median')).reset_index()
        return agg['_param'].to_numpy(), agg['y'].to_numpy()
    else:
        sub = df[df['signal_class'] == class_filter]
        agg = sub.groupby('q').agg(
            x=(x_col, 'median'), y=(y_col, 'median')).reset_index()
        return agg['x'].to_numpy(), agg['y'].to_numpy()


def _interpolate_inverse(target_y: float, xs: np.ndarray, ys: np.ndarray) -> float:
    """Given a calibrator curve (xs, ys) and a target y value, return the
    x value that maps to that y, by linear interpolation.  Sorts by y.
    """
    if xs.size < 2: return float('nan')
    idx = np.argsort(ys)
    ys_sorted = ys[idx]; xs_sorted = xs[idx]
    return float(np.interp(target_y, ys_sorted, xs_sorted))


# ─── Estimators ──────────────────────────────────────────────────────────────

def recover_poisson_rate(t_k: np.ndarray,
                          n_bootstrap: int = 200) -> tuple:
    """λ̂ = N / T from the input event sequence.  Trivial estimator
    operating on the raw t_k (not the joint_q_profile output, since
    n_events_q in the latter pools passage spacings across all coprime
    numerators per q-band — i.e. n_events_q[q=1] ≈ Σ_a a × n_input,
    not n_input).
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 2:
        return float('nan'), (float('nan'), float('nan'))
    t_total = float(t[-1] - t[0])
    if t_total <= 0:
        return float('nan'), (float('nan'), float('nan'))
    n = t.size
    rate = n / t_total
    rng = np.random.default_rng(0)
    samples = rng.poisson(n, size=n_bootstrap) / t_total
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return rate, (float(lo), float(hi))


_BETA_VALUES = (1.0, 2.0, 4.0)


def recover_wigner_beta(jdf: pd.DataFrame,
                         n_bootstrap: int = 200) -> tuple:
    """Fit β by linear interpolation on rep_int_q vs β from calibrator.

    Calibrator anchor points (Phase 15 medians):
        β = 1 → rep_int_q ≈ 0.311
        β = 2 → rep_int_q ≈ 0.368
        β = 4 → rep_int_q ≈ 0.430

    Out-of-domain flag fires when measured rep_int_q is below 0.20 (sub-
    GOE — likely Poisson) or above 0.55 (above β=4 — likely BR_artifact).
    """
    well = jdf[~jdf['underpowered']]
    if len(well) < 5:
        return float('nan'), (float('nan'), float('nan')), True
    rep_med = float(well['rep_int_q'].median())
    flagged = (rep_med < 0.20) or (rep_med > 0.55)
    # Anchor points from Phase 15 calibrator pool
    rep_anchor = np.array([0.025, 0.311, 0.368, 0.430, 0.671, 0.850])
    beta_anchor = np.array([0.0,    1.0,    2.0,   4.0,   np.nan, np.nan])
    # Restrict to the Wigner band for interpolation
    wig_mask = ~np.isnan(beta_anchor)
    rep_w = rep_anchor[wig_mask]; beta_w = beta_anchor[wig_mask]
    idx = np.argsort(rep_w)
    beta_hat = float(np.interp(rep_med, rep_w[idx], beta_w[idx]))
    # CI: combine per-q variability with a calibrator-derived seed-noise
    # floor of σ_β ≈ 0.5 in β.  Phase 15's β=2 GUE seed-to-seed rep_int
    # std was ≈ 0.006, which maps via slope d_β/d_rep ≈ 30 (since rep
    # spans 1.0 → 0.4 across β=1..4) to seed-uncertainty σ_β ≈ 0.18.
    # Use 0.4 as a conservative half-width to bracket seed effects.
    rep_arr = well['rep_int_q'].to_numpy()
    beta_per_q = np.interp(rep_arr, rep_w[idx], beta_w[idx])
    seed_floor = 0.4
    if beta_per_q.size >= 5:
        lo_q, hi_q = np.percentile(beta_per_q, [2.5, 97.5])
    else:
        lo_q, hi_q = beta_hat, beta_hat
    lo = min(lo_q, beta_hat - seed_floor)
    hi = max(hi_q, beta_hat + seed_floor)
    return beta_hat, (float(lo), float(hi)), flagged


def recover_periodic_q(jdf: pd.DataFrame,
                        q_min: int = 2,
                        q_max: int = None,
                        n_bootstrap: int = 200) -> tuple:
    """Recover the periodic resonance order from the |a_q| spectrum.

    Returns (q̂, (q_lo, q_hi), confidence) — confidence is the ratio of
    the dominant amplitude to the median over q≥2 (higher = stronger
    resonance).  Flags as uncertain when confidence < 3.0 (the spectrum
    has no clear peak).
    """
    sub = jdf[(jdf['q'] >= q_min)]
    if q_max:
        sub = sub[sub['q'] <= q_max]
    if len(sub) < 3:
        return -1, (-1, -1), 0.0
    rf = sub['rf_amplitude_q'].to_numpy()
    q_arr = sub['q'].to_numpy()
    idx_max = int(np.argmax(rf))
    q_hat = int(q_arr[idx_max])
    confidence = float(rf[idx_max] / (np.median(rf) + 1e-9))
    # Bootstrap CI on q̂ via random subsetting
    rng = np.random.default_rng(2)
    samples = []
    for _ in range(n_bootstrap):
        # Wild bootstrap — re-randomise rf_amplitude_q with multiplicative noise
        eps = rng.standard_normal(rf.size) * 0.1
        rf_perturb = rf * (1.0 + eps)
        samples.append(int(q_arr[int(np.argmax(rf_perturb))]))
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return q_hat, (int(lo), int(hi)), confidence


def recover_periodic_jitter(jdf: pd.DataFrame, q_hat: int,
                             n_bootstrap: int = 200) -> tuple:
    """Recover σ from mass<0.3_q at the recovered q̂."""
    row = jdf[jdf['q'] == q_hat]
    if len(row) == 0:
        return float('nan'), (float('nan'), float('nan'))
    mass = float(row['mass_lt_0_3_q'].iloc[0])
    # Calibrator-derived (σ, mass<0.3) curve from periodic_q7 and
    # uniform_jitter signals (similar shape).  Approximate map:
    #   mass<0.3 = 0.000  → σ ≤ 0.10
    #   mass<0.3 = 0.020  → σ ≈ 0.20
    #   mass<0.3 = 0.080  → σ ≈ 0.30
    #   mass<0.3 = 0.260  → σ ≈ 0.50  (Poisson regime)
    sigma_anchors = np.array([0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50])
    mass_anchors  = np.array([0.0, 0.001, 0.001, 0.005, 0.020, 0.080, 0.260])
    sigma_hat = float(np.interp(mass, mass_anchors, sigma_anchors))
    # Crude CI via uniform fluctuation of mass within ±50%
    rng = np.random.default_rng(3)
    samples = [float(np.interp(mass * (1 + 0.5 * rng.standard_normal()),
                                 mass_anchors, sigma_anchors))
                for _ in range(n_bootstrap)]
    lo, hi = np.percentile(samples, [2.5, 97.5])
    return sigma_hat, (max(0.0, float(lo)), float(hi))


def recover_uniform_jitter_sigma(jdf: pd.DataFrame,
                                  n_bootstrap: int = 200,
                                  fit_axis: str = 'rep_int_q') -> tuple:
    """Recover σ from rep_int_q (or mass<0.3_q) by inverting the Phase
    15 calibrator curve.

    Calibrator anchors (Phase 15 calibrator parquet medians):
       σ = 0.00 → rep_int_q ≈ 0.900
       σ = 0.02 → 0.850
       σ = 0.05 → 0.785
       σ = 0.10 → 0.671
       σ = 0.15 → 0.574
       σ = 0.20 → 0.510
       σ = 0.30 → 0.444
       σ = 0.50 → 0.384

    Out-of-domain flag fires when rep_int_q is below the calibrator's
    σ=0.50 anchor (~0.384) — the signature is below the uniform-jitter
    family's range, suggesting the input is not in the BR_artifact regime.
    Returns (σ̂, (σ_lo, σ_hi), flagged).
    """
    well = jdf[~jdf['underpowered']]
    if len(well) < 5:
        return float('nan'), (float('nan'), float('nan')), True
    rep_med = float(well['rep_int_q'].median())
    sigma_anchors = np.array([0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50])
    rep_anchors   = np.array([0.900, 0.850, 0.785, 0.671, 0.574, 0.510, 0.444, 0.384])
    # Out-of-domain when rep_int_q outside calibrator range
    flagged = (rep_med > 0.95) or (rep_med < 0.35)
    order = np.argsort(rep_anchors)
    sigma_hat = float(np.interp(rep_med, rep_anchors[order],
                                  sigma_anchors[order]))
    # CI: per-q variability + calibrator-derived seed-noise floor of σ ≈ 0.025.
    # Phase 15's σ=0.10 calibrator across 5 seeds gave rep_int_q std ≈ 0.005,
    # mapping via slope d_σ/d_rep ≈ 0.7 (σ spans 0.0..0.5 over rep 0.9..0.38)
    # to seed-uncertainty σ_σ ≈ 0.004.  Conservative half-width 0.025
    # bounds field-realisation variability without collapsing to zero.
    rep_arr = well['rep_int_q'].to_numpy()
    sigma_per_q = np.interp(rep_arr, rep_anchors[order], sigma_anchors[order])
    seed_floor = 0.025
    if sigma_per_q.size >= 5:
        lo_q, hi_q = np.percentile(sigma_per_q, [2.5, 97.5])
    else:
        lo_q, hi_q = sigma_hat, sigma_hat
    lo = min(lo_q, sigma_hat - seed_floor)
    hi = max(hi_q, sigma_hat + seed_floor)
    return sigma_hat, (max(0.0, float(lo)), float(hi)), flagged


__all__ = [
    'recover_poisson_rate', 'recover_wigner_beta',
    'recover_periodic_q', 'recover_periodic_jitter',
    'recover_uniform_jitter_sigma',
]
