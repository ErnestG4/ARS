"""
phase34e/run_berry_robnik.py — Test 2 (anomaly-shape quantification).

Fit empirical P(s) to Berry-Robnik interpolation P_BR(s; ρ) capturing
the Poisson-leaning anomaly shape. ρ = 1 → pure GOE; ρ = 0 → pure
Poisson; ρ ∈ (0, 0.5) → Poisson-dominant Sarnak anomaly per published
empirical literature on SL(2,ℤ).

Berry-Robnik (1984) interpolation:
  P_BR(s; ρ) = exp(-(1−ρ) s) · [(1−ρ)² · erfc(√π ρ s / 2) +
                                  (2 ρ (1−ρ) + π ρ² s / 2) · exp(-π ρ² s² / 4)]

where erfc is the complementary error function and ρ ∈ [0, 1] is the
GOE-fraction parameter.

Outputs:
  data/phase34e_results/berry_robnik.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import erfc

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from maass_loader import load_eigenvalues_at_level, unfold_gamma0


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34e_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def berry_robnik_pdf(s: np.ndarray, rho: float) -> np.ndarray:
    """Berry-Robnik 1984 NNS density P_BR(s; ρ).

    ρ = 0 → P(s) = exp(-s)            (Poisson)
    ρ = 1 → P(s) = (π/2) s exp(-π s²/4)  (Wigner GOE)
    """
    rho = np.clip(rho, 0.0, 1.0)
    s = np.asarray(s, dtype=np.float64)
    one_minus = 1.0 - rho
    a = one_minus * s
    b = np.sqrt(np.pi) * rho * s / 2.0
    term1 = one_minus * one_minus * erfc(b)
    term2 = (2.0 * rho * one_minus + np.pi * rho * rho * s / 2.0) \
            * np.exp(-np.pi * rho * rho * s * s / 4.0)
    return np.exp(-a) * (term1 + term2)


def fit_rho(spacings: np.ndarray, n_bootstrap: int = 30) -> dict:
    """Fit ρ to empirical spacings by maximum-likelihood; bootstrap σ.

    Uses scipy.optimize.minimize_scalar with negative-log-likelihood.
    Spacings should be unfolded to unit-mean.
    """
    s = np.asarray(spacings, dtype=np.float64)
    s = s[s > 0]
    s = s[s < 10.0]  # clip extreme tails

    def neg_log_likelihood(rho):
        pdf_vals = berry_robnik_pdf(s, rho)
        pdf_vals = np.maximum(pdf_vals, 1e-300)
        return -np.sum(np.log(pdf_vals))

    res = minimize_scalar(neg_log_likelihood, bounds=(0.0, 1.0),
                           method='bounded', options={'xatol': 1e-4})
    rho_best = float(res.x)
    nll_best = float(res.fun)

    # Bootstrap σ: resample spacings with replacement, refit ρ
    boot_rhos = []
    N = len(s)
    for b in range(n_bootstrap):
        rng = np.random.default_rng(b)
        idx = rng.choice(N, size=N, replace=True)
        sub = s[idx]
        def nll_b(rho):
            pdf_vals = berry_robnik_pdf(sub, rho)
            pdf_vals = np.maximum(pdf_vals, 1e-300)
            return -np.sum(np.log(pdf_vals))
        rb = minimize_scalar(nll_b, bounds=(0.0, 1.0),
                              method='bounded', options={'xatol': 1e-3})
        boot_rhos.append(float(rb.x))
    boot_rhos = np.array(boot_rhos)
    return dict(
        rho_mle=rho_best,
        nll=nll_best,
        n_spacings=int(N),
        bootstrap_rho_mean=float(np.mean(boot_rhos)),
        bootstrap_rho_std=float(np.std(boot_rhos)),
        bootstrap_rho_p5=float(np.percentile(boot_rhos, 5)),
        bootstrap_rho_p95=float(np.percentile(boot_rhos, 95)),
    )


PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]


def main():
    print("=" * 78)
    print("Phase 34e Test 2 — Berry-Robnik ρ fitting")
    print("=" * 78)
    results = {}
    for lvl in PRIMARY_LEVELS:
        print(f"\nLevel Γ₀({lvl}):")
        r = load_eigenvalues_at_level(lvl)
        x = unfold_gamma0(r, lvl)
        s = np.diff(x)
        s = s / np.mean(s)  # unit-mean normalize for the fit
        fit = fit_rho(s, n_bootstrap=30)
        results[f'level_{lvl}'] = fit
        print(f"  ρ_MLE = {fit['rho_mle']:.4f}   "
              f"bootstrap = {fit['bootstrap_rho_mean']:.4f} ± "
              f"{fit['bootstrap_rho_std']:.4f}   "
              f"[p5, p95] = [{fit['bootstrap_rho_p5']:.3f}, "
              f"{fit['bootstrap_rho_p95']:.3f}]   "
              f"N_spacings = {fit['n_spacings']}")

    # Cross-level consistency
    print()
    print("=" * 78)
    print("Cross-level ρ consistency check")
    print("=" * 78)
    rhos = [results[f'level_{l}']['bootstrap_rho_mean'] for l in PRIMARY_LEVELS]
    sigmas = [results[f'level_{l}']['bootstrap_rho_std'] for l in PRIMARY_LEVELS]
    print(f"  mean ρ across levels: {np.mean(rhos):.4f}")
    print(f"  std  ρ across levels: {np.std(rhos):.4f}")
    print(f"  individual σ range:   {np.min(sigmas):.4f}–{np.max(sigmas):.4f}")
    cross_consistent = np.std(rhos) < 2.0 * np.mean(sigmas)
    print(f"  cross-level consistency (cross-σ < 2× individual-σ): "
          f"{cross_consistent}")

    out = OUT_DIR / 'berry_robnik.json'
    with open(out, 'w') as f:
        json.dump({'phase': '34e', 'test': 'Test 2 Berry-Robnik ρ fit',
                    'primary_levels': PRIMARY_LEVELS,
                    'cross_level_summary': dict(
                        rho_mean_across_levels=float(np.mean(rhos)),
                        rho_std_across_levels=float(np.std(rhos)),
                        cross_level_consistent=bool(cross_consistent),
                    ),
                    'results': results}, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
