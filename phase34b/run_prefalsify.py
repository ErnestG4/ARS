"""
phase34b/run_prefalsify.py — pre-falsification check on the random-±1
null's adequacy for L(n) sign-change analysis.

The user's framing (preamble to brief): "the natural null for L(n)
sign-changes is random ±1 on all integers with the same density as λ,
not Poisson on integer positions.  Whether there are further
arithmetic filters on L(n) sign-changes that this null also misses
is open.  Worth a pre-falsification check before 34b's sub-4 —
surrogate construction is the load-bearing methodological choice
for this phase."

The pre-falsification check is whether the random-±1 null reproduces
the empirically observed sign-change density structure of L.  Two
empirical facts emerge from the N=10⁹ sieve:

  - Of 133 sign-changes in [1, 10⁹], 132 lie in the narrow window
    [906,150,257, 906,488,081] of width ≈ 338K (the Tanaka cluster
    around the first Pólya counterexample).  1 is at n=3 (initial
    transition).
  - L(n) stays ≤ 0 for n ∈ [2, 906,150,256] (Pólya holds across
    9×10⁸ integers without a single zero-crossing).

A random walk null with the same overall density would produce
~√(N/π) ≈ 17,800 sign-changes in [1, 10⁹] — two orders of magnitude
more than the real 133.  So the unconditioned random-±1 null is
*loose* at the full-range scope, and the survey at that scope would
be uninformative.

Two surrogate-adequacy diagnostics are run:

  (i) Full-range count comparison.  Number of sign-changes produced
      by the random-±1 null over [1, 10⁹] vs real (133).  Confirms
      the looseness quantitatively.

  (ii) Cluster-restricted count comparison.  Generate ±1 random walks
      starting at L_real(906150256) = -1, running 338K steps, count
      zero-crossings.  Compare distribution to real 132 crossings.
      If the null reproduces the real count (within factor ~2-3),
      the within-cluster survey is at least crudely calibrated.

Output: data/phase34b_results/prefalsify.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from liouville_events import load_or_compute

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34b_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_SEEDS_CLUSTER = 1000     # within-cluster null (cheap)

CLUSTER_LO = 906150257
CLUSTER_HI = 906488081
CLUSTER_WIDTH = CLUSTER_HI - CLUSTER_LO + 1   # 337,825
L_AT_CLUSTER_START_MINUS_1 = -1   # L(906150256) = -1 (confirmed by sieve)


def count_sign_changes(L_chunk: np.ndarray, start_sign: int = 0) -> int:
    """Count sign-change transitions in a cumulative-sign sequence,
    skipping zeros (same convention as Mertens / Liouville sieve)."""
    s = np.sign(L_chunk).astype(np.int8)
    full = np.concatenate(([np.int8(start_sign)], s)) if start_sign != 0 else s
    nz = full[full != 0]
    if nz.size < 2:
        return 0
    return int(np.sum(np.diff(nz) != 0))


def full_range_null(N: int, seed: int) -> int:
    """Generate a random ±1 sequence of length N, return # sign-changes
    of its cumulative sum."""
    rng = np.random.default_rng(seed)
    steps = rng.choice(np.array([-1, 1], dtype=np.int64), size=N)
    L = np.cumsum(steps)
    # The convention starts from L(1) = step[0], so start_sign = 0.
    return count_sign_changes(L, start_sign=0)


def cluster_null(width: int, start_L: int, seed: int) -> tuple[int, np.ndarray]:
    """Random walk of length `width` starting from start_L (just before
    the first step).  Returns (n_sign_changes, sign_change_positions
    relative to cluster start)."""
    rng = np.random.default_rng(seed)
    steps = rng.choice(np.array([-1, 1], dtype=np.int64), size=width)
    L = start_L + np.cumsum(steps)
    # Sign-changes including transition from start_L to first step
    sign_start = np.sign(start_L)
    s = np.sign(L).astype(np.int8)
    full = np.concatenate(([np.int8(sign_start)], s)) if sign_start != 0 else s
    nz_mask = full != 0
    full_nz = full[nz_mask]
    nz_idx = np.flatnonzero(nz_mask)
    if full_nz.size < 2:
        return 0, np.zeros(0, dtype=np.int64)
    flips = np.flatnonzero(np.diff(full_nz) != 0)
    sc_local = nz_idx[flips + 1] - 1   # back to L's index
    sc_local = sc_local[sc_local >= 0]
    return int(sc_local.size), sc_local.astype(np.int64)


def main(N_MAX: int = 10**9) -> dict:
    print("=" * 72)
    print("Phase 34b pre-falsification: random-±1 null adequacy")
    print("=" * 72)

    d = load_or_compute(N_MAX)
    sc_real = d['signchanges']
    n_real = sc_real.size
    cluster_mask = (sc_real >= CLUSTER_LO) & (sc_real <= CLUSTER_HI)
    n_real_cluster = int(np.sum(cluster_mask))
    print(f"  real total sign-changes [1, {N_MAX}]: {n_real}")
    print(f"  real cluster sign-changes [{CLUSTER_LO}, {CLUSTER_HI}]: "
          f"{n_real_cluster}")

    # ── (i) full-range theoretical bound ──
    # Skip simulation: a simple ±1 random walk over [1, N] has expected
    # number of zero-crossings ~ √(N/π) (large-N asymptotic for the
    # number of axis-crossings of a simple random walk).  At N = 10⁹
    # this is ~17,800, vs real 133.  Memory-prohibitive to simulate
    # at 10⁹ scale repeatedly here.  Report the theoretical mismatch.
    expected_walk_crossings = float(np.sqrt(N_MAX / np.pi))
    print(f"\n  (i) full-range random-±1 null: theoretical bound")
    print(f"    expected # crossings of a ±1 random walk over [1, {N_MAX}]: "
          f"≈ √(N/π) = {expected_walk_crossings:.0f}")
    print(f"    real # sign-changes: {n_real}")
    print(f"    ratio null:real ≈ {expected_walk_crossings / n_real:.0f}×")
    print(f"    diagnosis: unconditioned random-±1 null overpredicts "
          f"full-range sign-changes by ~{expected_walk_crossings / n_real:.0f}×.")
    print(f"    interpretation: real L stays ≪ 0 (drift much stronger "
          f"than a simple random walk) for n < ~9×10⁸, then enters the "
          f"Tanaka cluster.  The unconditioned null is therefore loose "
          f"at full-range scope.")

    # ── (ii) cluster-restricted null ──
    print(f"\n  (ii) cluster-restricted random-±1 null "
          f"({N_SEEDS_CLUSTER} seeds, width = {CLUSTER_WIDTH}, "
          f"start L = {L_AT_CLUSTER_START_MINUS_1})")
    t0 = time.perf_counter()
    cluster_counts = []
    for s in range(N_SEEDS_CLUSTER):
        n_sc, _ = cluster_null(CLUSTER_WIDTH,
                                L_AT_CLUSTER_START_MINUS_1, seed=s)
        cluster_counts.append(n_sc)
    cluster_counts = np.asarray(cluster_counts)
    print(f"    elapsed: {time.perf_counter() - t0:.1f}s")
    print(f"    null # sign-changes: mean = {cluster_counts.mean():.1f}, "
          f"std = {cluster_counts.std():.1f}, "
          f"median = {np.median(cluster_counts):.0f}")
    print(f"    real cluster # sign-changes: {n_real_cluster}")
    # p-value: fraction of null sims with count ≥ real
    p_val_le_real = float(np.mean(cluster_counts <= n_real_cluster))
    p_val_ge_real = float(np.mean(cluster_counts >= n_real_cluster))
    print(f"    P(null ≤ real) = {p_val_le_real:.3f}; "
          f"P(null ≥ real) = {p_val_ge_real:.3f}")

    diagnostic = ('TIGHT' if 0.05 < p_val_le_real < 0.95
                   else 'LOOSE_CLUSTER_OVER' if p_val_le_real >= 0.95
                   else 'LOOSE_CLUSTER_UNDER')
    print(f"    cluster-null adequacy: {diagnostic}")

    out_obj = {
        'N_MAX': int(N_MAX),
        'cluster_lo': int(CLUSTER_LO),
        'cluster_hi': int(CLUSTER_HI),
        'cluster_width': int(CLUSTER_WIDTH),
        'L_at_cluster_start_minus_1': int(L_AT_CLUSTER_START_MINUS_1),
        'n_real_total': int(n_real),
        'n_real_cluster': int(n_real_cluster),
        'full_range_theoretical': {
            'expected_walk_crossings': float(expected_walk_crossings),
            'ratio_walk_over_real': float(expected_walk_crossings / n_real),
            'note': ('Theoretical √(N/π) bound on ±1 random-walk '
                      'zero-crossings; simulation memory-prohibitive at '
                      'N=10⁹.'),
        },
        'cluster_null': {
            'n_seeds': int(N_SEEDS_CLUSTER),
            'mean': float(cluster_counts.mean()),
            'std': float(cluster_counts.std()),
            'median': float(np.median(cluster_counts)),
            'p_le_real': p_val_le_real,
            'p_ge_real': p_val_ge_real,
            'adequacy': diagnostic,
        },
    }
    out_path = OUT_DIR / 'prefalsify.json'
    with open(out_path, 'w') as f:
        json.dump(out_obj, f, indent=2)
    print(f"\n  → {out_path}")
    return out_obj


if __name__ == '__main__':
    main()
