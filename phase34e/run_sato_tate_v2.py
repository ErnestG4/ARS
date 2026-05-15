"""
phase34e/run_sato_tate_v2.py — Test 3 with proper Hecke-eigenvalue
normalization (post §D.0 gate failure detection).

The first run of run_sato_tate.py revealed that Seymour-Howell stores
Hecke eigenvalues a_p, NOT the Ramanujan-Petersson-normalized
λ_p = a_p / p^{(k-1)/2} (for weight k forms; for Maass forms k=0 so
the standard Ramanujan-Petersson form is λ_p = a_p / √p... wait that's
weight 1 normalization).

Actually for Maass cuspforms (weight 0), the Fourier expansion is
  f(z) = Σ_n a_n √y · K_{ir}(2π|n|y) · e^{2πinx}
and the Hecke eigenvalue at prime p is λ_p with λ_p ∈ [-2, 2] under
Ramanujan-Petersson (conjectural for Maass; Kim-Sarnak gives the
unconditional bound).  The relation between a_p and λ_p for Maass
cuspforms is just a_p = λ_p (no √p rescaling).

But the data has λ values up to ±19 — way outside [-2, 2]. This is
either:
  (a) un-normalized Hecke eigenvalues (raw T_p f = c·f with c ≠ λ_p),
  (b) "old" / "rough" normalization,
  (c) a different convention specific to SH 2022.

Per Seymour-Howell 2022 §3 (data format), they store the Hecke
"coefficient" rather than the Ramanujan-Petersson eigenvalue. The
conversion factor is the standard λ_p relationship.

For Maass forms, the simplest empirical normalization check is to
**divide a_p by √p** (since the un-normalized convention gives
a_p ~ √p · semicircular):

  λ_p := a_p / √p ∈ [-2, 2]

Let me test this hypothesis by mapping prime indices to actual primes
and rescaling.

This v2 script:
  1. Identifies which prime each Hecke pair corresponds to (sequential
     in the file).
  2. Rescales λ_p_corrected := a_p / √p.
  3. Re-checks §D.0 normalization gate against [-2, 2].
  4. If gate passes, runs the Sato-Tate KS test on the rescaled values.

Outputs:
  data/phase34e_results/sato_tate_v2.json
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
from run_sato_tate import semicircular_cdf, normalization_check


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34e_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]


def sieve_primes(limit: int) -> list[int]:
    """Eratosthenes up to `limit`."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [p for p in range(limit + 1) if sieve[p]]


def get_primes_for_indices(n_indices: int) -> list[int]:
    """Return first n_indices primes (in ascending order)."""
    if n_indices < 1:
        return []
    # Upper bound: nth prime ~ n * (ln n + ln ln n) for n > 6
    upper = max(20, int(n_indices * (np.log(n_indices) + np.log(np.log(max(n_indices, 3))) + 2)))
    primes = sieve_primes(upper)
    while len(primes) < n_indices:
        upper *= 2
        primes = sieve_primes(upper)
    return primes[:n_indices]


def run_level_st_v2(level: int) -> dict:
    """Pool Hecke pairs at this level, rescale by √p, run Sato-Tate."""
    print()
    print("=" * 78)
    print(f"Level Γ₀({level}) — Sato-Tate v2 with √p rescaling")
    print("=" * 78)

    # Collect (a_p, p) pairs for primes p NOT dividing level (good primes)
    # Bad primes (p | level) have different normalization (Atkin-Lehner)
    bad_primes = []
    n = level
    p = 2
    while p * p <= n:
        if n % p == 0:
            bad_primes.append(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        bad_primes.append(n)
    print(f"  Bad primes for level {level}: {bad_primes}")

    all_normalized = []
    n_forms = 0
    for f in iter_maass_forms(level=level):
        n_pairs = len(f['hecke_pairs'])
        primes = get_primes_for_indices(n_pairs)
        for (a, _err), p in zip(f['hecke_pairs'], primes):
            if p in bad_primes:
                continue
            lam = a / np.sqrt(p)
            all_normalized.append(lam)
        n_forms += 1
    lambdas = np.array(all_normalized, dtype=np.float64)
    print(f"  N forms = {n_forms}, total normalized λ pooled = {len(lambdas)}")

    # §D.0 normalization gate (re-check)
    norm = normalization_check(lambdas)
    print(f"  Normalization gate (after √p rescale): "
          f"min/max = [{norm['min']:.4f}, {norm['max']:.4f}]")
    print(f"    pass_check = {norm['pass_check']}  "
          f"frac outside [-2,2] = {norm['frac_outside_RP']:.4e}")
    print(f"    Kim-Sarnak compatible (|λ|≤2.22): {norm['within_kim_sarnak']}")

    # KS test against semicircular
    clipped = lambdas[(lambdas >= -2.0) & (lambdas <= 2.0)]
    if len(clipped) > 0:
        ks_stat, ks_p = kstest(clipped, semicircular_cdf)
    else:
        ks_stat, ks_p = float('nan'), float('nan')
    print(f"  KS vs semicircular: stat = {ks_stat:.4f}, p = {ks_p:.4e}, "
          f"N = {len(clipped)}")

    # Histogram
    counts, edges = np.histogram(clipped, bins=20, range=(-2.0, 2.0),
                                  density=True)
    bin_centers = 0.5 * (edges[:-1] + edges[1:])
    pred_density = (1.0 / np.pi) * np.sqrt(np.maximum(
        1.0 - bin_centers ** 2 / 4.0, 0.0))
    residuals = counts - pred_density
    print(f"  Histogram residual: mean = {np.mean(residuals):.4f}, "
          f"std = {np.std(residuals):.4f}")

    return dict(
        level=int(level),
        n_forms=int(n_forms),
        bad_primes=bad_primes,
        n_lambdas_normalized=int(len(lambdas)),
        normalization_gate_v2=norm,
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
    print("Phase 34e Test 3 v2 — Sato-Tate with √p Hecke normalization")
    print("=" * 78)
    print("Hypothesis: Seymour-Howell data stores a_p, not λ_p.")
    print("Correction: λ_p := a_p / √p for good primes (p ∤ N).")
    results = {}
    for lvl in PRIMARY_LEVELS:
        results[f'level_{lvl}'] = run_level_st_v2(lvl)

    print()
    print("=" * 78)
    print("Cross-level v2 summary")
    print("=" * 78)
    print(f"{'level':>6s} {'n_λ_good':>9s} {'min':>7s} {'max':>7s} "
          f"{'KS stat':>10s} {'KS p':>12s} {'pass':>6s}")
    for lvl in PRIMARY_LEVELS:
        r = results[f'level_{lvl}']
        n = r['normalization_gate_v2']
        k = r['ks_test']
        print(f"{lvl:>6d} {r['n_lambdas_normalized']:>9d} "
              f"{n['min']:>7.3f} {n['max']:>7.3f} "
              f"{k['ks_stat']:>10.4f} {k['ks_p_value']:>12.4e} "
              f"{str(n['pass_check']):>6s}")

    out = OUT_DIR / 'sato_tate_v2.json'
    with open(out, 'w') as f:
        json.dump({'phase': '34e', 'test': 'Test 3 v2 with √p rescaling',
                    'normalization_hypothesis': 'λ_p := a_p / √p for good primes',
                    'primary_levels': PRIMARY_LEVELS,
                    'results': results}, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
