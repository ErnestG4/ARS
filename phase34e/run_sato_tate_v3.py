"""
phase34e/run_sato_tate_v3.py — Test 3 with CORRECT Hecke normalization.

Normalization investigation closed via Seymour-Howell 2022 §3
(arXiv:2201.08760):

  "we define the Hecke eigenvalues a(n) of a level N Maass form f by
   a(n) f = T_n f, where T_n f(z) = (1/√|n|) Σ_{ad=n,(a,N)=1,d>0} ...
   For newforms, we normalise by setting a(1) = 1.
   Kim-Sarnak gives |a_p| ≤ p^{7/64}+p^{-7/64} ⟹ |a_n/√n| ≤ θ ≈ 1.758"

KEY: the 1/√|n| prefactor is **built into the Hecke operator T_n**, so
a(p) at a PRIME p is ALREADY the Ramanujan-Petersson-normalized
Satake variable ∈ [-2, 2] (conjecturally; Kim-Sarnak unconditional
bound slightly above 2 for large p).  **No √p rescaling needed.**

Errors in prior versions:
  - v1 pooled a(n) for ALL n (including composites where a(n) ~ √n,
    giving values up to ±19) → §D.0 gate correctly flagged this.
  - v2 took a(p) at primes but divided by √p → over-corrected,
    shrinking the distribution to [-1.15, 1.15] (non-semicircular).

v3 (correct): a(p) at PRIME indices p with p ∤ N (good primes),
NO rescaling.  These are the Satake parameters; Sato-Tate predicts
the semicircular SU(2) measure on [-2, 2].

File-format note: hecke_pairs[0] = a(1) = 1 (newform normalization),
hecke_pairs[1] = a(2), ..., hecke_pairs[k] = a(k+1).  So a(p) is at
index p-1.

Outputs:
  data/phase34e_results/sato_tate_v3.json
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
from run_sato_tate_v2 import sieve_primes


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34e_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]


def bad_primes_of(level: int) -> set[int]:
    bad = set()
    n = level
    p = 2
    while p * p <= n:
        if n % p == 0:
            bad.add(p)
            while n % p == 0:
                n //= p
        p += 1
    if n > 1:
        bad.add(n)
    return bad


def run_level_st_v3(level: int, primes: list[int]) -> dict:
    print()
    print("=" * 78)
    print(f"Level Γ₀({level}) — Sato-Tate v3 (CORRECT: a(p) at primes, no rescale)")
    print("=" * 78)
    bad = bad_primes_of(level)
    print(f"  Bad primes (p | {level}): {sorted(bad)}")

    # prime → index in hecke_pairs (a(1)=index0, a(p)=index p-1)
    all_ap = []
    n_forms = 0
    for f in iter_maass_forms(level=level):
        pairs = f['hecke_pairs']
        n_pairs = len(pairs)
        for p in primes:
            idx = p - 1  # a(p) at hecke_pairs[p-1]
            if idx >= n_pairs:
                break
            if p in bad:
                continue
            a_p = pairs[idx][0]
            all_ap.append(a_p)
        n_forms += 1
    ap = np.array(all_ap, dtype=np.float64)
    print(f"  N forms = {n_forms}, a(p) at good primes pooled = {len(ap)}")

    norm = normalization_check(ap)
    print(f"  Normalization gate: min/max = [{norm['min']:.4f}, {norm['max']:.4f}]")
    print(f"    pass_check = {norm['pass_check']}  "
          f"frac outside [-2,2] = {norm['frac_outside_RP']:.4e}")
    print(f"    Kim-Sarnak compatible (|a|≤2.22): {norm['within_kim_sarnak']}")

    clipped = ap[(ap >= -2.0) & (ap <= 2.0)]
    if len(clipped) > 1:
        ks_stat, ks_p = kstest(clipped, semicircular_cdf)
    else:
        ks_stat, ks_p = float('nan'), float('nan')
    print(f"  KS vs semicircular: stat = {ks_stat:.4f}, p = {ks_p:.4e}, "
          f"N = {len(clipped)}")

    counts, edges = np.histogram(clipped, bins=20, range=(-2.0, 2.0),
                                  density=True)
    bc = 0.5 * (edges[:-1] + edges[1:])
    pred = (1.0 / np.pi) * np.sqrt(np.maximum(1.0 - bc * bc / 4.0, 0.0))
    resid = counts - pred
    print(f"  Histogram residual: mean = {np.mean(resid):.4f}, "
          f"std = {np.std(resid):.4f}")

    return dict(
        level=int(level),
        n_forms=int(n_forms),
        bad_primes=sorted(bad),
        n_ap=int(len(ap)),
        normalization_gate_v3=norm,
        ks_test=dict(ks_stat=float(ks_stat), ks_p_value=float(ks_p),
                     n_within_RP=int(len(clipped))),
        histogram=dict(bin_centers=bc.tolist(),
                       empirical_density=counts.tolist(),
                       predicted_density=pred.tolist(),
                       residual_mean=float(np.mean(resid)),
                       residual_std=float(np.std(resid))),
    )


def main():
    print("=" * 78)
    print("Phase 34e Test 3 v3 — Sato-Tate with CORRECT a(p)-at-primes (no rescale)")
    print("=" * 78)
    print("SH 2022 §3: T_n has 1/√|n| built in ⟹ a(p) is the RP-normalized")
    print("Satake variable directly. v1 pooled all a(n); v2 over-divided by √p.")

    primes = sieve_primes(2100)  # a(n) goes up to n ≤ 2000

    results = {}
    for lvl in PRIMARY_LEVELS:
        results[f'level_{lvl}'] = run_level_st_v3(lvl, primes)

    print()
    print("=" * 78)
    print("Cross-level v3 summary")
    print("=" * 78)
    print(f"{'level':>6s} {'n_ap':>9s} {'min':>7s} {'max':>7s} "
          f"{'KS stat':>10s} {'KS p':>12s} {'pass':>6s}")
    for lvl in PRIMARY_LEVELS:
        r = results[f'level_{lvl}']
        n = r['normalization_gate_v3']
        k = r['ks_test']
        print(f"{lvl:>6d} {r['n_ap']:>9d} {n['min']:>7.3f} {n['max']:>7.3f} "
              f"{k['ks_stat']:>10.4f} {k['ks_p_value']:>12.4e} "
              f"{str(n['pass_check']):>6s}")

    out = OUT_DIR / 'sato_tate_v3.json'
    with open(out, 'w') as f:
        json.dump({'phase': '34e', 'test': 'Test 3 v3 CORRECT a(p)-at-primes',
                    'normalization_resolution': 'SH 2022 §3: T_n has 1/√|n| built in; a(p) at prime p is RP-normalized Satake variable, no rescale',
                    'primary_levels': PRIMARY_LEVELS,
                    'results': results}, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
