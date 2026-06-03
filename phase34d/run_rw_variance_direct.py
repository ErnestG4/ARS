"""
phase34d/run_rw_variance_direct.py — direct measurement of the
Rudnick-Waxman variance σ²(K, X) for Gaussian (and Eisenstein) prime
angles. Pre-pilot Step 3.

This is the **load-bearing analytical check** per the Phase 34d brief §B
bulk-vs-edge architectural note: NNS / RF / p-adic are bulk statistics
that read "Poisson-like" on prime-angle substrates; the discriminating
measurement against the RW conjecture lives in the GLOBAL MOMENT σ²(K, X).

What is computed
----------------
For each (X, K) cell, the angles θ_p ∈ [0, π/2) for Gaussian (or
[0, π/3) for Eisenstein) prime ideals of norm ≤ X are binned into K
arcs of equal length, and the *variance* of the bin counts is recorded:

    σ²_emp(K, X) := Var_{j=1..K} ( N_{K,X}(θ_j) )

The Rudnick-Waxman 2019 Conjecture 1.2 predicts:

    σ²_RW(K, X) = (N/K) · min(1, 2 log K / log N)

where N = total angle count (~ X / log X) and the crossover at K = √N
separates the Poisson regime (K > √N, σ² ~ N/K) from the rigidity
regime (K < √N, σ² < N/K).

Plotting σ²_emp / (N/K) versus β := log K / log N reproduces RW's
Figure 1 (a min(1, 2β) shape). Successful pre-pilot Step 3 → the
empirical points trace the min(1, 2β) curve, validating that the
substrate genuinely follows the RW prediction.

Outputs
-------
data/phase34d_results/rw_variance_direct.json with one record per (X, K, substrate)
cell, including:
  - N (total angle count)
  - K (number of arcs)
  - beta = log K / log N
  - sigma2_emp (measured variance)
  - sigma2_poisson = N/K
  - sigma2_rw = (N/K) · min(1, 2β)
  - ratio_emp = sigma2_emp / (N/K)
  - ratio_rw = min(1, 2β)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

from phase34d.gaussian_primes import gaussian_prime_angles
from phase34d.eisenstein_primes import eisenstein_prime_angles

OUT_DIR = Path('$HOME/fmexplorer/criticality_tool/data/phase34d_results')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def variance_in_arcs(angles: np.ndarray,
                     K: int,
                     sector_length: float,
                     n_grid: int = 5000) -> float:
    """Compute the **continuous sliding-window variance** σ²(K, X) per RW 2019 eq. (1.2).

    RW defines:
        Var(N_{K,x}) := ∫_0^{L} |N_{K,x}(θ) − ⟨N_{K,x}⟩|² · dθ / L
    where L = sector_length, N_{K,x}(θ) = #{p : θ_p ∈ [θ − w/2, θ + w/2]}
    with arc width w = L/K.

    Implementation: discretise θ over a fine grid of n_grid uniformly spaced
    centers in [0, L), compute count_window(θ_i) at each grid point, then take
    np.var() over the grid (which gives the integral approximation
    ⟨(N − ⟨N⟩)²⟩ over the grid).

    For circular geometry (treating [0, L) as a circle of length L), the
    sliding window wraps around the boundary. This matches RW's
    u(p) = e^{i·k·θ} natural periodicity (period π/2 for Gaussian k=4,
    period π/3 for Eisenstein k=6).

    Parameters
    ----------
    angles        : 1D sorted array of angles in [0, sector_length).
    K             : number of equal-length arcs (window width = L/K).
    sector_length : total length of fundamental sector.
    n_grid        : number of grid points for sliding-window center θ.
    """
    L = sector_length
    w = L / K
    # Sorted angles → use np.searchsorted for fast window counting
    centers = np.linspace(0.0, L, n_grid, endpoint=False)
    counts = np.empty(n_grid, dtype=np.int64)
    for i, c in enumerate(centers):
        lo = c - 0.5 * w
        hi = c + 0.5 * w
        # Handle circular wrap-around at boundaries
        if lo < 0:
            count_low = (np.searchsorted(angles, hi, side='right')
                        - np.searchsorted(angles, 0, side='left'))
            count_high = (np.searchsorted(angles, L, side='right')
                         - np.searchsorted(angles, lo + L, side='left'))
            counts[i] = count_low + count_high
        elif hi > L:
            count_low = (np.searchsorted(angles, L, side='right')
                        - np.searchsorted(angles, lo, side='left'))
            count_high = (np.searchsorted(angles, hi - L, side='right')
                         - np.searchsorted(angles, 0, side='left'))
            counts[i] = count_low + count_high
        else:
            counts[i] = (np.searchsorted(angles, hi, side='right')
                        - np.searchsorted(angles, lo, side='left'))
    return float(np.var(counts))


def run_substrate(substrate: str,
                  X_values: list[int],
                  K_scan: dict[int, list[int]]) -> list[dict]:
    """Run variance scan on a substrate.

    Parameters
    ----------
    substrate : 'gaussian' or 'eisenstein'
    X_values  : norm caps to scan
    K_scan    : dict mapping X → list of K values to test at that X

    Returns
    -------
    records : list of dicts (one per (X, K) cell)
    """
    records = []

    if substrate == 'gaussian':
        sector_length = np.pi / 2
        gen = lambda X: gaussian_prime_angles(X, both_ideals=True)
    elif substrate == 'eisenstein':
        sector_length = np.pi / 3
        gen = lambda X: eisenstein_prime_angles(X, both_factors=True)
    else:
        raise ValueError(substrate)

    for X in X_values:
        t0 = time.time()
        angles = gen(X)
        N = len(angles)
        t_gen = time.time() - t0
        print(f"[{substrate}] X = {X:.0e}, N = {N}, sqrt(N) = {np.sqrt(N):.1f}, "
              f"gen time = {t_gen:.1f}s")
        log_N = np.log(N)
        for K in K_scan.get(X, []):
            sigma2_emp = variance_in_arcs(angles, K, sector_length)
            mean_count = N / K
            beta = np.log(K) / log_N
            rw_ratio = min(1.0, 2.0 * beta)
            rec = {
                'substrate': substrate,
                'X': X,
                'N': N,
                'K': K,
                'beta_logK_over_logN': beta,
                'mean_count_NoverK': mean_count,
                'sigma2_emp': sigma2_emp,
                'sigma2_poisson_NoverK': mean_count,
                'sigma2_rw': mean_count * rw_ratio,
                'ratio_emp_over_NoverK': sigma2_emp / mean_count if mean_count > 0 else float('nan'),
                'ratio_rw': rw_ratio,
            }
            records.append(rec)
            print(f"    K = {K:>6d}  β = {beta:.3f}  N/K = {mean_count:7.2f}  "
                  f"σ²_emp = {sigma2_emp:8.2f}  σ²/N·K = {rec['ratio_emp_over_NoverK']:.3f}  "
                  f"RW min(1,2β) = {rw_ratio:.3f}")
    return records


def main():
    # X scan and matched K scan per Phase 34d brief §Step 3
    gaussian_scan = {
        100_000:    [3, 10, 30, 100, 300],
        1_000_000:  [10, 30, 100, 300, 1000],
        10_000_000: [30, 100, 300, 1000, 3000, 10000],
    }
    eisenstein_scan = {
        100_000:    [3, 10, 30, 100, 300],
        1_000_000:  [10, 30, 100, 300, 1000],
        10_000_000: [30, 100, 300, 1000, 3000, 10000],
    }

    all_records = []
    print("=" * 78)
    print("Phase 34d Step 3 — direct Rudnick-Waxman variance check")
    print("=" * 78)
    all_records += run_substrate('gaussian', list(gaussian_scan.keys()), gaussian_scan)
    print()
    all_records += run_substrate('eisenstein', list(eisenstein_scan.keys()), eisenstein_scan)

    out_path = OUT_DIR / 'rw_variance_direct.json'
    with open(out_path, 'w') as f:
        json.dump({
            'phase': '34d',
            'step': 'pre-pilot Step 3 / direct RW variance check',
            'records': all_records,
            'notes': (
                'σ²_emp = empirical variance of arc-count over K equal-length arcs. '
                'RW Conjecture 1.2 predicts σ²/(N/K) ~ min(1, 2 log K / log N) = '
                'min(1, 2β). Saturation regime (β > 0.5, K > √N): Poisson-like. '
                'Rigidity regime (β < 0.5, K < √N): variance suppressed below '
                'N/K by factor 2β.'
            ),
        }, f, indent=2)
    print(f"\n→ wrote {len(all_records)} records to {out_path}")

    # Print a compact summary table
    print()
    print("=" * 78)
    print("Summary — ratio σ²_emp / (N/K) vs RW prediction min(1, 2β)")
    print("=" * 78)
    print(f"{'substrate':>11s} {'X':>10s} {'K':>7s} {'β':>7s} {'σ²/(N/K)':>10s} {'RW':>7s} {'Δ':>7s}")
    for r in all_records:
        delta = r['ratio_emp_over_NoverK'] - r['ratio_rw']
        print(f"{r['substrate']:>11s} {r['X']:>10.0e} {r['K']:>7d} "
              f"{r['beta_logK_over_logN']:>7.3f} {r['ratio_emp_over_NoverK']:>10.3f} "
              f"{r['ratio_rw']:>7.3f} {delta:>+7.3f}")


if __name__ == '__main__':
    main()
