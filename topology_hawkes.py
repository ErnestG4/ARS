"""
topology_hawkes.py — Phase 20 topology-aware Hawkes surrogate.

Standard `hawkes_matched` (Phase 18) preserves clustering intensity but
not spatial-temporal cascade structure.  The topology-aware variant
stratifies the Hawkes fit by AS-distance to the cascade source
(AS 32934 for the Facebook outage), giving one Hawkes process per
distance bin.  Synthetic generation samples each bin's Hawkes
independently, then aggregates per-collector by weighting each bin's
contribution according to the fraction of that collector's peer-ASes
that fall in the bin.

API:

    fit(events_df, peer_distance_map, distance_bins=...) -> dict
      Per-bin (μ, α, β) Hawkes parameters.

    simulate_collector(per_bin_params, peer_bin_weights, T, rng)
      Synthetic event sequence as observed by a collector with the
      given per-distance-bin peer weights.

The `events_df` is the Tier 1 parquet (timestamp_us, peer_asn, …);
`peer_distance_map` is {peer_asn: distance_to_target_AS} from
as_topology.bfs_distances_from(graph, target_AS).

Verification: `verify_topology_kernel_recovery` runs a synthetic-input
recovery test — generates a topology-aware Hawkes cascade with known
per-bin parameters, fits, and reports the recovery error.
"""
from __future__ import annotations
import os, sys
from typing import Optional

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from surrogates import _fit_hawkes_exponential, _simulate_hawkes


# Default distance bins: close (peers FB), medium (1 hop away from
# direct peers), distant (≥3 hops).
DEFAULT_DISTANCE_BINS = (0, 1, 2, 3, 4, 99)


def _bin_index(distance: int, bin_edges: tuple) -> int:
    """Return the bin index in bin_edges for a given distance.  Returns
    -1 if distance is below the lowest edge."""
    for i in range(len(bin_edges) - 1):
        if bin_edges[i] <= distance < bin_edges[i + 1]:
            return i
    return -1


def fit_topology_hawkes(
        events_df: pd.DataFrame,
        peer_distance_map: dict[int, int],
        distance_bins: tuple = DEFAULT_DISTANCE_BINS,
        T_window_seconds: Optional[float] = None,
        max_events_per_bin: int = 20_000,
        ) -> dict:
    """Fit one univariate exponential-kernel Hawkes process per
    AS-distance bin.

    `max_events_per_bin`: cap per-bin event count for the ML fit
    (default 20,000).  The Ozaki recursion in `_fit_hawkes_exponential`
    is a Python for-loop over n events per log-likelihood evaluation;
    n above ~50K causes the L-BFGS-B fit to take prohibitively long.
    Stride-subsampling keeps the bin's effective rate (events / T)
    proportional, with the absolute rate of the subsampled series
    rescaled in the simulation step.

    events_df must contain columns 'timestamp_us' and 'peer_asn'.

    Returns dict with:
      bin_edges, per_bin_params (list of (mu, alpha, beta), one per
      bin), per_bin_n_events_full (true count in window),
      per_bin_n_events_used (count used in fit), per_bin_T_seconds,
      per_bin_subsample_factor (n_full / n_used, ≥ 1).
    """
    if 'peer_asn' not in events_df.columns:
        raise ValueError("events_df must have 'peer_asn' column")
    df = events_df[['timestamp_us', 'peer_asn']].copy()
    df['distance'] = df['peer_asn'].map(peer_distance_map)
    df = df.dropna(subset=['distance'])
    df['distance'] = df['distance'].astype(int)

    n_bins = len(distance_bins) - 1
    per_bin_params = []
    per_bin_n_full = []
    per_bin_n_used = []
    per_bin_T = []
    per_bin_subsample = []
    for i in range(n_bins):
        lo, hi = distance_bins[i], distance_bins[i + 1]
        sel = df[(df['distance'] >= lo) & (df['distance'] < hi)]
        n_full = len(sel)
        if n_full < 20:
            per_bin_params.append((0.0, 0.0, 1.0))
            per_bin_n_full.append(int(n_full))
            per_bin_n_used.append(int(n_full))
            per_bin_T.append(0.0)
            per_bin_subsample.append(1.0)
            continue
        t_sec = sel['timestamp_us'].to_numpy(dtype=np.float64) / 1_000_000
        t_sec = np.sort(t_sec)
        T = T_window_seconds if T_window_seconds is not None \
            else float(t_sec[-1] - t_sec[0])
        # Window-truncate: instead of stride-subsampling (which doesn't
        # preserve Hawkes structure), restrict the fit to the first
        # `max_events_per_bin` events and rescale the time window
        # proportionally.  This gives a clean Hawkes fit on a
        # genuine sub-window of the original process, with the same
        # rate per second as the full window (assuming approximate
        # stationarity over the truncation).  Simulation then needs
        # no rescaling.
        if n_full > max_events_per_bin:
            t_sec = t_sec[:max_events_per_bin]
            T_used = float(t_sec[-1] - t_sec[0])
            stride = float(n_full) / float(t_sec.size)
        else:
            T_used = T
            stride = 1.0
        t_shift = t_sec - t_sec[0]
        mu, alpha, beta = _fit_hawkes_exponential(t_shift, T=T_used)
        # Sanity guards: the unconstrained ML fit can diverge into
        # numerically pathological regions (μ, α at ~1e283 with α/β
        # near the soft-stability boundary).  Detect and replace with a
        # rate-matched Poisson fallback (μ = n/T, α = 0, β = 1) — which
        # is what the SESSION-PLAN ground rules call for when
        # topology-aware Hawkes can't be reliably fit and the
        # standard-Hawkes (Phase 18) surrogate is the principled
        # fallback.
        rate = mu / max(1.0 - alpha / max(beta, 1e-9), 1e-9) \
               if beta > 0 else float('inf')
        # Pathological-fit detection: the unconstrained ML fit can
        # converge to (i) μ small and α,β both huge (μ~1e-132,
        # α,β~1e305 — degenerate vanishing-baseline regime), (ii)
        # α/β > 0.99 (near-explosive branching), (iii) μ alone huge
        # (overflow region).  All three should be rejected.
        empirical_rate = float(t_sec.size) / max(T_used, 1.0)
        if (not np.isfinite(mu) or not np.isfinite(alpha)
                or not np.isfinite(beta)
                or rate > 1e6
                or alpha / max(beta, 1e-9) > 0.99
                or mu > 1e4
                or mu < empirical_rate * 1e-3   # μ collapsed
                or alpha > 1e6                  # α extreme
                or beta > 1e6):                 # β extreme
            mu = empirical_rate
            alpha = 0.0
            beta = 1.0
        per_bin_params.append((mu, alpha, beta))
        per_bin_n_full.append(int(n_full))
        per_bin_n_used.append(int(t_sec.size))
        per_bin_T.append(T_used)
        per_bin_subsample.append(float(stride))
    return dict(
        bin_edges=distance_bins,
        per_bin_params=per_bin_params,
        per_bin_n_events=per_bin_n_full,                  # alias for back-compat
        per_bin_n_events_full=per_bin_n_full,
        per_bin_n_events_used=per_bin_n_used,
        per_bin_T_seconds=per_bin_T,
        per_bin_subsample_factor=per_bin_subsample,
    )


def simulate_topology_hawkes_global(
        fit: dict,
        T: float,
        rng: Optional[np.random.Generator] = None,
        ) -> dict:
    """Sample one Hawkes process per distance bin on [0, T], return
    {bin_index: event_times_sec}."""
    if rng is None:
        rng = np.random.default_rng()
    out = {}
    for i, (mu, alpha, beta) in enumerate(fit['per_bin_params']):
        if mu <= 0 and alpha == 0:
            out[i] = np.zeros(0)
            continue
        sim = _simulate_hawkes(mu, alpha, beta, T, rng)
        out[i] = sim
    return out


def per_collector_bin_weights(
        peer_asns: list[int],
        peer_distance_map: dict[int, int],
        distance_bins: tuple = DEFAULT_DISTANCE_BINS,
        ) -> np.ndarray:
    """For a collector with the given peer-ASN set, return the fraction
    of its peer-ASNs in each distance bin.  Returns array of length
    (len(distance_bins)-1)."""
    n_bins = len(distance_bins) - 1
    counts = np.zeros(n_bins, dtype=int)
    n_total = 0
    for asn in peer_asns:
        d = peer_distance_map.get(int(asn))
        if d is None:
            continue
        bi = _bin_index(d, distance_bins)
        if bi >= 0:
            counts[bi] += 1
            n_total += 1
    if n_total == 0:
        return np.zeros(n_bins)
    return counts / n_total


def simulate_collector(
        fit: dict,
        peer_bin_weights: np.ndarray,
        T: float,
        rng: Optional[np.random.Generator] = None,
        sample_per_bin: bool = True,
        ) -> np.ndarray:
    """Project per-bin Hawkes simulations onto a single collector view.

    Each bin's events are thinned by `peer_bin_weights[bin]` — the
    fraction of the collector's peers in that bin.  This is the
    "weighted per-collector observation" projection.
    """
    if rng is None:
        rng = np.random.default_rng()
    if sample_per_bin:
        per_bin = simulate_topology_hawkes_global(fit, T, rng)
    else:
        per_bin = simulate_topology_hawkes_global(fit, T, rng)
    out_chunks = []
    for bi, t_arr in per_bin.items():
        if t_arr.size == 0:
            continue
        w = float(peer_bin_weights[bi]) if bi < len(peer_bin_weights) else 0.0
        if w <= 0:
            continue
        # Bernoulli thinning: keep each event w.p. w
        keep = rng.random(t_arr.size) < w
        kept = t_arr[keep]
        out_chunks.append(kept)
    if not out_chunks:
        return np.zeros(0)
    return np.sort(np.concatenate(out_chunks))


# ─── Verification on synthetic ground truth ──────────────────────────────


def verify_topology_kernel_recovery(seed: int = 0,
                                      T: float = 4000.0) -> dict:
    """Generate a synthetic 3-bin cascade with known parameters; fit and
    measure recovery error.  Used as a Tier 4 acceptance test."""
    rng = np.random.default_rng(seed)
    # Ground-truth bin parameters
    true_params = [
        (0.5, 0.6, 1.4),      # bin 0: high-rate close-to-source
        (0.2, 0.5, 1.2),      # bin 1: medium
        (0.05, 0.3, 1.1),     # bin 2: low-rate distant
    ]
    bin_edges = (0, 1, 2, 3)
    # Simulate per bin and tag events with synthetic peer_asn (one ASN
    # range per bin)
    rows = []
    for i, (mu, alpha, beta) in enumerate(true_params):
        t_arr = _simulate_hawkes(mu, alpha, beta, T, rng)
        for t in t_arr:
            # Synthetic peer ASN: range 1000+i*100 to 1099+i*100
            asn = 1000 + i * 100 + rng.integers(0, 100)
            rows.append(dict(timestamp_us=int(t * 1_000_000),
                              peer_asn=int(asn)))
    df = pd.DataFrame(rows)
    # Distance map: ASNs in [1000+i*100, 1099+i*100) → distance=i
    distance_map = {}
    for i in range(3):
        for a in range(1000 + i * 100, 1100 + i * 100):
            distance_map[a] = i

    fit = fit_topology_hawkes(df, distance_map, distance_bins=bin_edges,
                                T_window_seconds=T)
    errors = []
    for i, ((mu_t, alpha_t, beta_t),
             (mu_h, alpha_h, beta_h)) in enumerate(zip(true_params,
                                                         fit['per_bin_params'])):
        rate_true = mu_t / max(1 - alpha_t / beta_t, 1e-9)
        rate_hat = mu_h / max(1 - alpha_h / beta_h, 1e-9)
        rel_rate_err = abs(rate_hat - rate_true) / rate_true
        branch_true = alpha_t / beta_t
        branch_hat = alpha_h / beta_h
        rel_branch_err = abs(branch_hat - branch_true) / max(branch_true, 1e-9)
        errors.append(dict(
            bin=i, true_mu=mu_t, true_alpha=alpha_t, true_beta=beta_t,
            fit_mu=mu_h, fit_alpha=alpha_h, fit_beta=beta_h,
            rate_true=rate_true, rate_hat=rate_hat,
            rel_rate_err=rel_rate_err, rel_branch_err=rel_branch_err,
        ))
    return dict(fit=fit, errors=errors)


__all__ = [
    'DEFAULT_DISTANCE_BINS',
    'fit_topology_hawkes',
    'simulate_topology_hawkes_global',
    'per_collector_bin_weights',
    'simulate_collector',
    'verify_topology_kernel_recovery',
]
