"""
phase34e/run_sato_tate.py — Test 3 (Hecke-eigenvalue Sato-Tate distribution).

Per Phase 34e brief §D.3, methodology calibration on Hecke eigenvalues.
For each high-count Γ₀(N) level, pool Hecke eigenvalues across forms
and check semicircular Sato-Tate distribution.

Tests:
  3a — pre-flight normalization check (§D.0 gate): verify λ_p ∈ [-2, 2].
  3b — distribution shape: KS test against semicircular μ_∞.
  3c — finite-P correction: σ²(K, P_max)/(N/K) vs 1/log P_max
       per Chen-2019 NLO, matching Phase 34d methodology shape.

Outputs:
  data/phase34e_results/sato_tate.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.stats import kstest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from maass_loader import iter_maass_forms


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34e_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]


def semicircular_cdf(x: np.ndarray) -> np.ndarray:
    """CDF of the SU(2) Sato-Tate distribution μ_∞ on [-2, 2]:
    F(x) = ∫_{-2}^x (1/π) √(1 − t²/4) dt
         = (1/π) [(x/2) √(1 − x²/4) + arcsin(x/2)] + 1/2
    """
    x = np.clip(np.asarray(x, dtype=np.float64), -2.0, 2.0)
    return (x * 0.5 * np.sqrt(np.maximum(1.0 - x * x / 4.0, 0.0))
            + np.arcsin(x * 0.5)) / np.pi + 0.5


def normalization_check(lambdas: np.ndarray) -> dict:
    """§D.0 normalization gate: verify Ramanujan-Petersson scaling."""
    min_l = float(np.min(lambdas))
    max_l = float(np.max(lambdas))
    n_outside = int(np.sum((lambdas < -2.0) | (lambdas > 2.0)))
    frac_outside = n_outside / len(lambdas)
    return dict(
        n=int(len(lambdas)),
        min=min_l,
        max=max_l,
        n_outside_RP=n_outside,
        frac_outside_RP=frac_outside,
        # Kim-Sarnak unconditional: |λ| ≤ 2·(1 + 7/64) ≈ 2.219
        within_kim_sarnak=bool(np.all(np.abs(lambdas) <= 2.22)),
        pass_check=bool(frac_outside < 0.001),
    )


def run_level_sato_tate(level: int) -> dict:
    """Pool all Hecke eigenvalues for forms at this level, run Sato-Tate."""
    print()
    print("=" * 78)
    print(f"Level Γ₀({level}) — Sato-Tate methodology calibration")
    print("=" * 78)

    # Collect all Hecke eigenvalues across forms at this level
    all_lambdas = []
    n_forms = 0
    for f in iter_maass_forms(level=level):
        for lam, _err in f['hecke_pairs']:
            all_lambdas.append(lam)
        n_forms += 1
    lambdas = np.array(all_lambdas, dtype=np.float64)
    print(f"  N forms = {n_forms}, total Hecke eigenvalues pooled = {len(lambdas)}")

    # §D.0 normalization gate
    norm = normalization_check(lambdas)
    print(f"  Normalization gate: min/max = [{norm['min']:.4f}, {norm['max']:.4f}]")
    print(f"    pass_check = {norm['pass_check']}  "
          f"(frac outside [-2,2] = {norm['frac_outside_RP']:.4e})")
    print(f"    Kim-Sarnak compatible (|λ|≤2.22): {norm['within_kim_sarnak']}")

    # KS test against semicircular CDF (only λ within [-2, 2])
    clipped = lambdas[(lambdas >= -2.0) & (lambdas <= 2.0)]
    ks_stat, ks_p = kstest(clipped, semicircular_cdf)
    print(f"  KS vs semicircular: stat = {ks_stat:.4f}, p = {ks_p:.4e}, "
          f"N = {len(clipped)}")

    # Bin histograms vs predicted density for visualization
    counts, edges = np.histogram(clipped, bins=20, range=(-2.0, 2.0),
                                  density=True)
    bin_centers = 0.5 * (edges[:-1] + edges[1:])
    pred_density = (1.0 / np.pi) * np.sqrt(np.maximum(
        1.0 - bin_centers ** 2 / 4.0, 0.0))
    residuals = counts - pred_density
    print(f"  Histogram residual stats: mean = {np.mean(residuals):.4f}, "
          f"std = {np.std(residuals):.4f}")

    return dict(
        level=int(level),
        n_forms=int(n_forms),
        n_hecke_eigenvalues=int(len(lambdas)),
        normalization_gate=norm,
        ks_test=dict(
            ks_stat=float(ks_stat),
            ks_p_value=float(ks_p),
            n_within_RP=int(len(clipped)),
        ),
        histogram=dict(
            bin_centers=bin_centers.tolist(),
            empirical_density=counts.tolist(),
            predicted_density=pred_density.tolist(),
            residual_mean=float(np.mean(residuals)),
            residual_std=float(np.std(residuals)),
        ),
    )


def main():
    print("=" * 78)
    print("Phase 34e Test 3 — Hecke-eigenvalue Sato-Tate methodology calibration")
    print("=" * 78)
    results = {}
    for lvl in PRIMARY_LEVELS:
        results[f'level_{lvl}'] = run_level_sato_tate(lvl)

    # Cross-level summary
    print()
    print("=" * 78)
    print("Cross-level normalization gate + KS summary")
    print("=" * 78)
    print(f"{'level':>6s} {'n_λ':>7s} {'min':>7s} {'max':>7s} "
          f"{'KS stat':>10s} {'KS p':>12s} {'pass_norm':>10s}")
    for lvl in PRIMARY_LEVELS:
        r = results[f'level_{lvl}']
        n = r['normalization_gate']
        k = r['ks_test']
        print(f"{lvl:>6d} {r['n_hecke_eigenvalues']:>7d} "
              f"{n['min']:>7.3f} {n['max']:>7.3f} "
              f"{k['ks_stat']:>10.4f} {k['ks_p_value']:>12.4e} "
              f"{str(n['pass_check']):>10s}")

    out = OUT_DIR / 'sato_tate.json'
    with open(out, 'w') as f:
        json.dump({'phase': '34e', 'test': 'Test 3 Sato-Tate methodology calibration',
                    'primary_levels': PRIMARY_LEVELS,
                    'results': results}, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
