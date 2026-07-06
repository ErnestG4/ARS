"""
phase34a/surrogate.py — local-density rate-matched Poisson surrogate
for arithmetic point processes on integer positions.

The Mertens sign-change density drifts slowly with n (clusters near M
zero-crossings).  A global Poisson rate destroys this local structure
and is the wrong null — it gives the surrogate ensemble more spread
out events than the real sequence, inflating any apparent integer-
period signal.

This module implements the canonical local-density null:

  1. Partition [t.min(), t.max()] into K equal-width bins.
  2. Count real events per bin: k_i.
  3. Surrogate: sample Poisson(k_i) integer positions uniformly within
     each bin (no replacement to avoid stacked-event artefacts).
  4. Sort and return.

K defaults to 50.  Per the brief's adequacy requirement, K is chosen
so the per-bin count averages well above the Poisson detection
threshold (events_per_bin ≥ ~30 for N_events ≥ 1500; ≥ ~40 for the
3866-event Mertens sequence).

API:
    local_density_poisson(positions, seed, K=50) → np.ndarray
"""
from __future__ import annotations

import numpy as np


def local_density_poisson(positions: np.ndarray, seed: int,
                           K: int = 50,
                           t_min: int | None = None,
                           t_max: int | None = None) -> np.ndarray:
    """Sample a rate-matched Poisson surrogate at K-bin local density.

    Parameters
    ----------
    positions : 1-D integer array of real event positions.
    seed      : RNG seed.
    K         : number of equal-width density bins.
    t_min, t_max : optional explicit bin range; defaults to
                   positions.min(), positions.max().

    Returns
    -------
    np.ndarray (int64) of integer positions, sorted.

    Sampling within a bin uses np.random.Generator.choice without
    replacement on the integer range [bin_lo, bin_hi].  If the
    Poisson count for a bin exceeds the integer width, we cap at the
    width (rare, only matters for very dense events in tiny bins).
    """
    pos = np.asarray(positions, dtype=np.int64)
    if pos.size == 0:
        return pos.copy()
    rng = np.random.default_rng(seed)
    lo = int(pos.min()) if t_min is None else int(t_min)
    hi = int(pos.max()) if t_max is None else int(t_max)
    edges = np.linspace(lo, hi + 1, K + 1).astype(np.int64)
    edges[-1] = hi + 1     # inclusive right-end
    counts, _ = np.histogram(pos, bins=edges)

    out_chunks = []
    for i in range(K):
        bin_lo = int(edges[i])
        bin_hi = int(edges[i + 1])      # exclusive
        bin_width = bin_hi - bin_lo
        if bin_width < 1:
            continue
        k_pois = int(rng.poisson(counts[i]))
        if k_pois == 0:
            continue
        if k_pois > bin_width:
            k_pois = bin_width
        picks = rng.choice(bin_width, size=k_pois, replace=False)
        out_chunks.append(picks + bin_lo)

    if not out_chunks:
        return np.zeros(0, dtype=np.int64)
    out = np.concatenate(out_chunks).astype(np.int64)
    out.sort()
    return out


def _sanity_check():
    """Verify the surrogate reproduces the local density profile in
    expectation."""
    rng = np.random.default_rng(0)
    # Construct an inhomogeneous real-event sequence with density
    # decreasing with n.  Use a denser rate so per-bin counts are
    # well above Poisson noise floor.
    real = []
    for n in range(1, 10**6 + 1, 1):
        if rng.uniform() < 5e-3 / (1 + n / 1e5):
            real.append(n)
    real = np.array(real, dtype=np.int64)
    print(f"  real n_events: {real.size}")

    K = 50
    edges = np.linspace(real.min(), real.max() + 1, K + 1).astype(np.int64)
    real_counts, _ = np.histogram(real, bins=edges)

    n_seeds = 500
    sur_counts = np.zeros((n_seeds, K), dtype=np.int64)
    for s in range(n_seeds):
        sur = local_density_poisson(real, seed=s, K=K)
        c, _ = np.histogram(sur, bins=edges)
        sur_counts[s] = c
    mean_sur = sur_counts.mean(axis=0)
    diff = np.max(np.abs(mean_sur - real_counts) / np.maximum(real_counts, 1))
    print(f"  per-bin mean rel-error (over {n_seeds} surrogates): {diff:.3f}")
    print(f"  ✓ surrogate preserves local density"
          if diff < 0.1 else f"  ✗ density drift > 10%")


if __name__ == '__main__':
    print("=" * 60)
    print("Phase 34a local-density Poisson surrogate sanity test")
    print("=" * 60)
    _sanity_check()
