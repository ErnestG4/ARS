"""
phase34e/run_nns_classification.py — Test 1 (bulk-NNS classification).

Per Phase 34e brief §D.1, pivoted from N=1 (not in Zenodo dump) to
representative Γ₀(N) squarefree levels per per-level analysis.

For each high-count level N ∈ {91, 95, 85, 77, 93, 87}:
  1. Load all rigorous Maass-form spectral parameters at that level.
  2. Unfold via x_j = ([SL(2,ℤ):Γ₀(N)] / 12) · r_j².
  3. Compute NNS s_j and ⟨s⟩ ≈ 1 sanity check.
  4. Run NNS engine (deployed joint_q_profile.classify).
  5. 20-seed 80%-subsample replicate per §7.ter.22 discipline.
  6. Compare to Wigner-Dyson β=1 (BGS-naive right null) and Poisson
     (Sarnak-anomaly expected outcome).

Outputs:
  data/phase34e_results/nns_classification.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34c'))

from maass_loader import (load_eigenvalues_at_level, unfold_gamma0,
                            gamma0_N_index, load_level_index)
from sl2z_unfolding import mean_spacing_check
from ars_classify import classify


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34e_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]  # top 6 levels by count


def run_level(level: int, n_seeds: int = 20, subsample_frac: float = 0.8,
              q_max: int = 30) -> dict:
    """Run bulk-NNS classification for one Γ₀(N) level."""
    print()
    print("=" * 78)
    print(f"Level Γ₀({level}) — bulk NNS classification")
    print("=" * 78)

    # Load + unfold
    r = load_eigenvalues_at_level(level)
    N = len(r)
    print(f"  N eigenvalues = {N}")
    x = unfold_gamma0(r, level)
    s = np.diff(x)
    msc = mean_spacing_check(s, tolerance=0.10)
    print(f"  unfolded ⟨s⟩ = {msc['mean']:.4f}  CV = {msc['CV']:.4f}  "
          f"pass_check = {msc['pass_check']}")
    if not msc['pass_check']:
        print("  WARNING: mean spacing deviates from 1 beyond tolerance — "
              "Weyl-law unfolding may need subleading corrections.")

    # Full-data NNS classification
    r_full = classify(x.astype(np.float64), q_max=q_max,
                       min_events_per_q=30, return_full=False)
    print(f"  Full-N classification: primary = {r_full['primary']}  "
          f"rep_med = {r_full['rep_med']:.3f}  "
          f"ks_gue_med = {r_full['ks_gue_med']:.3f}  "
          f"n_well = {r_full['n_well']}/{q_max}")

    # 20-seed 80%-subsample replicate (§7.ter.22 discipline from 34d)
    print(f"  Running {n_seeds} subsample replicates ({int(subsample_frac*100)}%) ...")
    n_sub = int(N * subsample_frac)
    primaries, rep_meds, ks_gues = [], [], []
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        idx = rng.choice(N, size=n_sub, replace=False)
        sub_x = np.sort(x[idx])
        rr = classify(sub_x.astype(np.float64), q_max=q_max,
                       min_events_per_q=30, return_full=False)
        primaries.append(rr['primary'])
        rep_meds.append(float(rr['rep_med']))
        ks_gues.append(float(rr['ks_gue_med']))
    pri_counts = dict(Counter(primaries))
    print(f"  Primary distribution: {pri_counts}")
    print(f"  rep_med = {np.mean(rep_meds):.3f} ± {np.std(rep_meds):.3f}  "
          f"[min {np.min(rep_meds):.3f}, max {np.max(rep_meds):.3f}]")
    print(f"  ks_gue_med = {np.mean(ks_gues):.3f} ± {np.std(ks_gues):.3f}")

    return dict(
        level=int(level),
        gamma0_index=gamma0_N_index(level),
        N_eigenvalues=int(N),
        weyl_unfolding_constant=gamma0_N_index(level) / 12.0,
        mean_spacing_check=msc,
        full_n_classification=dict(
            primary=r_full['primary'],
            rep_med=float(r_full['rep_med']),
            ks_gue_med=float(r_full['ks_gue_med']),
            n_well=int(r_full['n_well']),
            n_events_used=int(r_full['n_events_used']),
        ),
        seed_replicate=dict(
            n_seeds=int(n_seeds),
            subsample_frac=float(subsample_frac),
            N_sub=int(n_sub),
            primary_counts=pri_counts,
            rep_meds=rep_meds,
            rep_med_mean=float(np.mean(rep_meds)),
            rep_med_std=float(np.std(rep_meds)),
            rep_med_min=float(np.min(rep_meds)),
            rep_med_max=float(np.max(rep_meds)),
            ks_gues=ks_gues,
            ks_gue_mean=float(np.mean(ks_gues)),
            ks_gue_std=float(np.std(ks_gues)),
        ),
    )


def main():
    print("=" * 78)
    print("Phase 34e Test 1 — bulk-NNS classification on Γ₀(N) squarefree levels")
    print("=" * 78)
    print(f"Levels to scan: {PRIMARY_LEVELS}")
    print()

    counts = load_level_index()
    print("Level eigenvalue-count check:")
    for lvl in PRIMARY_LEVELS:
        print(f"  Γ₀({lvl}): {counts.get(lvl, 0)} forms")

    results = {}
    for lvl in PRIMARY_LEVELS:
        t0 = time.time()
        results[f'level_{lvl}'] = run_level(lvl)
        results[f'level_{lvl}']['runtime_s'] = time.time() - t0

    # Cross-level summary
    print()
    print("=" * 78)
    print("Cross-level summary: Sarnak anomaly across Γ₀(N) squarefree levels")
    print("=" * 78)
    print(f"{'level':>6s} {'N':>6s} {'primary(full)':>14s} {'primary 20-seed':>20s} "
          f"{'rep_med ± σ':>18s} {'ks_gue ± σ':>16s}")
    for lvl in PRIMARY_LEVELS:
        r = results[f'level_{lvl}']
        full_pri = r['full_n_classification']['primary']
        seed = r['seed_replicate']
        rep_str = f"{seed['rep_med_mean']:.3f} ± {seed['rep_med_std']:.3f}"
        ks_str = f"{seed['ks_gue_mean']:.3f} ± {seed['ks_gue_std']:.3f}"
        pri_str = str(seed['primary_counts'])[:18]
        print(f"{lvl:>6d} {r['N_eigenvalues']:>6d} {full_pri:>14s} "
              f"{pri_str:>20s} {rep_str:>18s} {ks_str:>16s}")

    out = OUT_DIR / 'nns_classification.json'
    with open(out, 'w') as f:
        json.dump({'phase': '34e', 'test': 'Test 1 bulk-NNS classification',
                    'primary_levels': PRIMARY_LEVELS,
                    'results': results}, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
