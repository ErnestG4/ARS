"""
phase34d/run_x_rate_scan.py — X-dependence rate scan of the saturation-
regime deficit on σ²(K, X)/(N/K).

Per the post-amendment critical-read (2026-05-14): the saturation regime
empirical saturates at 0.78-0.91 vs RW asymptote 1.0, with 3-7σ deficit
at X = 10⁷ in tight bootstrap error.  Two unresolved interpretations:
finite-X correction with predicted form, vs genuine substrate departure
from the RW asymptote.

**The discriminator is the X-dependence rate, not magnitude at a single X.**
Chen-Kim-Lichtman-Miller-Shubina-Sweitzer-Waxman-Winsor-Yang 2019
(arXiv:1901.07386, Refined Conjecture for Variance of Gaussian Primes
Across Sectors) gives the explicit NLO prediction:

  Var(ψ_K,X) / (C_f X^{1-λ}) = C_Φ log X + Δ_Φ + O(X^{-ε})   (saturation: 1/2 < λ < 1)

For sharp count N_K,X via the heuristic Λ(p) → log X:
  σ²(N_K,X) / (N/K)  =  1 + (C_f Δ_Φ) / log X + O(1 / (log X)²)

Predicted deficit shape:
  deficit(X) := 1 − σ²_emp(K, X) / (N/K)  ∝  1 / log X

Scan plan (Cornacchia O(log² p) makes X = 10⁸ tractable):
  - Substrate × X: gaussian × {10⁶, 10⁷, 10⁸}, eisenstein × {10⁶, 10⁷, 10⁸}
  - Fine β grid at each X: K chosen so β = log K / log N is at
    {0.55, 0.65, 0.75, 0.85, 0.95} in the saturation regime, plus
    {0.20, 0.30, 0.40} in the rigidity regime.
  - 50-bootstrap half-sample partitions per cell.

Then fit deficit(X) at fixed β across the three X values:
  - "Finite-X with predicted rate": deficit ~ a / log X with consistent
    constant a across substrates and β.
  - "Constant deficit" → substrate departure: deficit(X) ≈ const,
    independent of log X.
  - "Finite-X with off-prediction rate": deficit decays but with
    different functional shape (e.g., 1/log² X, X^{-c}, etc.).

Note from Will's critique: Katz 2017 function-field NLO is a DIFFERENT
finite-q correction structure (with q the field size; here X is the norm
cap, not a field-size parameter).  The function-field correction is NOT
interchangeable with the Chen 2019 number-field NLO — they live on
different parameter axes.  This scan tests the number-field prediction.

Outputs:
  data/phase34d_results/x_rate_scan.json
  plots/phase34d_x_rate_scan.png
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from gaussian_primes import gaussian_prime_angles
from eisenstein_primes import eisenstein_prime_angles
from run_rw_variance_direct import variance_in_arcs
from run_amendments import bootstrap_variance

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34d_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def k_for_beta(beta: float, N: int) -> int:
    """Pick K so that log K / log N ≈ beta."""
    return max(2, int(round(N ** beta)))


def run_substrate_x_scan(substrate: str, gen, sector_length: float,
                          X_values: list[int],
                          beta_targets: list[float],
                          n_boot: int = 50,
                          n_grid: int = 2000) -> list[dict]:
    records = []
    for X in X_values:
        t0 = time.time()
        angles = gen(X)
        N = len(angles)
        gen_time = time.time() - t0
        log_N = math.log(N)
        print(f"\n  [{substrate}] X = {X:.0e}, N = {N}, gen = {gen_time:.1f}s, log N = {log_N:.3f}")
        for beta_target in beta_targets:
            K = k_for_beta(beta_target, N)
            rng = np.random.default_rng(hash((substrate, X, K)) % 2**32)
            rec = bootstrap_variance(angles, K, sector_length,
                                      n_boot=n_boot, n_grid=n_grid, rng=rng)
            rec['substrate'] = substrate
            rec['X'] = X
            rec['log_N'] = log_N
            rec['log_X'] = math.log(X)
            rec['beta_target'] = beta_target
            rec['rw_pred'] = float(min(1.0, 2.0 * rec['beta_mean']))
            rec['deficit'] = float(rec['rw_pred'] - rec['ratio_mean'])
            rec['deficit_2sigma'] = 2.0 * rec['ratio_std']
            records.append(rec)
            print(f"    β_target={beta_target:.2f}  K={K:>6d}  β_actual={rec['beta_mean']:.3f}  "
                  f"σ²/(N/K) = {rec['ratio_mean']:.3f} ± {rec['ratio_std']:.3f}  "
                  f"RW = {rec['rw_pred']:.3f}  deficit = {rec['deficit']:+.3f}")
    return records


def fit_deficit_vs_log_x(records: list[dict],
                          beta_targets: list[float]) -> dict:
    """Fit deficit(X) ~ a / log X + b at fixed β across X values.

    Returns per-β fit results including:
      - a, b (linear fit of deficit vs 1/log X)
      - residual at X = 10⁸ (the prediction at largest X)
      - whether deficit decreases with X (finite-X correction direction)
    """
    from collections import defaultdict
    by_substrate_beta = defaultdict(list)
    for r in records:
        key = (r['substrate'], r['beta_target'])
        by_substrate_beta[key].append(r)

    fits = []
    for (substrate, beta_t), recs in by_substrate_beta.items():
        if len(recs) < 2:
            continue
        log_X = np.array([r['log_X'] for r in recs])
        deficits = np.array([r['deficit'] for r in recs])
        deficit_errs = np.array([r['ratio_std'] for r in recs])
        # Fit deficit = a / log_X + b (linear in 1/log_X)
        inv_log_X = 1.0 / log_X
        # Weighted least squares
        w = 1.0 / np.maximum(deficit_errs, 1e-6) ** 2
        A = np.column_stack([inv_log_X, np.ones_like(inv_log_X)])
        WA = A * w[:, np.newaxis]
        Wd = deficits * w
        try:
            coefs, resid, rank, sv = np.linalg.lstsq(WA, Wd, rcond=None)
        except Exception:
            continue
        a, b = coefs
        # Predicted deficit at each X
        pred = a * inv_log_X + b
        chi2 = float(np.sum(((deficits - pred) / np.maximum(deficit_errs, 1e-6)) ** 2))
        dof = max(1, len(recs) - 2)
        fits.append(dict(
            substrate=substrate,
            beta_target=float(beta_t),
            n_X=len(recs),
            a_over_logX=float(a),
            b_offset=float(b),
            chi2=chi2,
            dof=int(dof),
            chi2_over_dof=chi2 / dof,
            X_values=[r['X'] for r in recs],
            deficits=deficits.tolist(),
            deficit_errs=deficit_errs.tolist(),
            log_X=log_X.tolist(),
        ))
    return dict(fits=fits)


def main():
    rigidity_beta = [0.20, 0.30, 0.40]
    saturation_beta = [0.55, 0.65, 0.75, 0.85, 0.95]
    beta_targets = rigidity_beta + saturation_beta
    X_values = [1_000_000, 10_000_000, 100_000_000]

    print("=" * 78)
    print("Phase 34d X-rate scan — saturation-deficit X-dependence")
    print("=" * 78)
    print(f"X values: {X_values}")
    print(f"β targets: {beta_targets}")

    all_records = []
    all_records += run_substrate_x_scan(
        'gaussian', lambda X: gaussian_prime_angles(X, both_ideals=True),
        np.pi / 2, X_values, beta_targets, n_boot=50)
    all_records += run_substrate_x_scan(
        'eisenstein', lambda X: eisenstein_prime_angles(X, both_factors=True),
        np.pi / 3, X_values, beta_targets, n_boot=50)

    # Fit deficit(X) at each (substrate, β)
    fit_results = fit_deficit_vs_log_x(all_records, beta_targets)

    out = OUT_DIR / 'x_rate_scan.json'
    with open(out, 'w') as f:
        json.dump({
            'phase': '34d-X-rate amendment',
            'method': 'three-X scan with fine β grid; bootstrap σ² + linear fit deficit = a / log X + b',
            'records': all_records,
            'fits': fit_results['fits'],
        }, f, indent=2)
    print(f"\n→ wrote {out}")

    # Summary table
    print()
    print("=" * 78)
    print("Fit summary: deficit(X) = a / log X + b at fixed (substrate, β)")
    print("=" * 78)
    print(f"{'substrate':>10s} {'β':>6s}  {'a':>8s}   {'b':>8s}   {'χ²/dof':>7s}   interpretation")
    for f in fit_results['fits']:
        # Interpretation:
        # if b ≈ 0 within error: pure finite-X correction (deficit → 0 as X → ∞)
        # if b > 2σ from 0: residual deficit → genuine substrate departure
        # if a < 0 (deficit grows with X): wrong sign — neither finite-X nor RW
        a = f['a_over_logX']
        b = f['b_offset']
        chi2_dof = f['chi2_over_dof']
        # Crude error from chi2-fit (a 1-sigma proxy on b is ~ sqrt(chi2 / df) · representative error)
        avg_err = np.mean(f['deficit_errs'])
        b_err_proxy = avg_err  # rough
        z_b = b / max(b_err_proxy, 1e-6)
        if abs(z_b) < 1.5 and a > 0:
            interp = "FINITE-X (b≈0, a>0)"
        elif abs(z_b) >= 1.5 and b > 0:
            interp = f"SUBSTRATE-DEPARTURE residual b={b:+.3f}"
        elif a < 0:
            interp = "WRONG-SIGN — deficit not finite-X"
        else:
            interp = "AMBIGUOUS"
        print(f"{f['substrate']:>10s} {f['beta_target']:>6.2f}  {a:>+8.3f}  {b:>+8.3f}  "
              f"{chi2_dof:>7.2f}  {interp}")

    return all_records, fit_results


if __name__ == '__main__':
    main()
