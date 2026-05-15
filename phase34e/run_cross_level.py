"""
phase34e/run_cross_level.py — Test 4 (cross-LEVEL reproducibility).

Pivot from cross-DATASET (PHASE34E_BRIEF.md §D.4 original) to cross-LEVEL
reproducibility: the Seymour-Howell Zenodo dump does NOT include
N=1 (SL(2,ℤ) trivial level), so the cross-dataset reproducibility
discipline pivots to checking verdict agreement across 6 representative
Γ₀(N) squarefree levels at the same precision tier (rigorous,
Seymour-Howell 2022).

Test 4 reads outputs from Tests 1-3 and reports:
  - Per-level NNS primary verdict agreement
  - Berry-Robnik ρ cross-level consistency (bootstrap-σ overlap)
  - Sato-Tate KS-test cross-level consistency

This file is the consolidated cross-level reporter; the actual
classification work is done in Tests 1-3.

Outputs:
  data/phase34e_results/cross_level_test4.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34e_results'

PRIMARY_LEVELS = [91, 95, 85, 77, 93, 87]


def main():
    print("=" * 78)
    print("Phase 34e Test 4 — cross-level reproducibility (pivot from cross-dataset)")
    print("=" * 78)
    print()
    print("PIVOT NOTE: Seymour-Howell 2022 Zenodo dump lacks N=1 (SL(2,ℤ)).")
    print("Cross-dataset reproducibility (BSV / Then / SH at N=1) pivoted to")
    print("cross-LEVEL reproducibility across 6 representative Γ₀(N) squarefree")
    print("levels at SAME precision tier (rigorous, Seymour-Howell 2022).")
    print()

    # Load Test 1 output (NNS classification per level)
    try:
        with open(OUT_DIR / 'nns_classification.json') as f:
            t1 = json.load(f)
    except FileNotFoundError:
        print("ERROR: Test 1 results not found. Run run_nns_classification.py first.")
        return
    try:
        with open(OUT_DIR / 'berry_robnik.json') as f:
            t2 = json.load(f)
    except FileNotFoundError:
        t2 = None
        print("WARNING: Test 2 (Berry-Robnik) results not found; partial Test 4 output")
    try:
        with open(OUT_DIR / 'sato_tate.json') as f:
            t3 = json.load(f)
    except FileNotFoundError:
        t3 = None
        print("WARNING: Test 3 (Sato-Tate) results not found; partial Test 4 output")

    print()
    print("=" * 78)
    print("Cross-level Test 1 verdicts: NNS primary classification")
    print("=" * 78)
    primary_full = {}
    primary_seed = {}
    rep_meds = {}
    rep_med_sigmas = {}
    for lvl in PRIMARY_LEVELS:
        r = t1['results'].get(f'level_{lvl}', None)
        if r is None:
            continue
        primary_full[lvl] = r['full_n_classification']['primary']
        primary_seed[lvl] = r['seed_replicate']['primary_counts']
        rep_meds[lvl] = r['seed_replicate']['rep_med_mean']
        rep_med_sigmas[lvl] = r['seed_replicate']['rep_med_std']
    print(f"{'level':>6s} {'full-N':>10s} {'20-seed':>20s} {'rep_med ± σ':>18s}")
    for lvl in PRIMARY_LEVELS:
        if lvl not in primary_full:
            continue
        print(f"{lvl:>6d} {primary_full[lvl]:>10s} "
              f"{str(primary_seed[lvl])[:18]:>20s} "
              f"{rep_meds[lvl]:.3f} ± {rep_med_sigmas[lvl]:.3f}")

    primary_set = set(primary_full.values())
    primary_seed_modal_set = set()
    for lvl in PRIMARY_LEVELS:
        if lvl in primary_seed:
            modal = max(primary_seed[lvl], key=primary_seed[lvl].get)
            primary_seed_modal_set.add(modal)
    test1_consistent = len(primary_seed_modal_set) == 1
    print()
    print(f"  Full-N primary distinct verdicts: {primary_set}")
    print(f"  20-seed modal verdicts (distinct): {primary_seed_modal_set}")
    print(f"  Test 1 cross-level consistent: {test1_consistent}")

    if t2 is not None:
        print()
        print("=" * 78)
        print("Cross-level Test 2: Berry-Robnik ρ consistency")
        print("=" * 78)
        rhos, sigmas = [], []
        for lvl in PRIMARY_LEVELS:
            r = t2['results'].get(f'level_{lvl}')
            if r is None:
                continue
            rho = r['bootstrap_rho_mean']
            sig = r['bootstrap_rho_std']
            rhos.append(rho)
            sigmas.append(sig)
            print(f"  Γ₀({lvl}): ρ = {rho:.4f} ± {sig:.4f}")
        rho_mean = np.mean(rhos)
        rho_std = np.std(rhos)
        max_sigma = np.max(sigmas) if sigmas else 0.0
        test2_consistent = rho_std < 2.0 * max_sigma
        print(f"  Mean ρ across levels: {rho_mean:.4f} ± {rho_std:.4f}")
        print(f"  Test 2 cross-level consistent (cross-σ < 2× indiv-σ): {test2_consistent}")
    else:
        rho_mean = rho_std = None
        test2_consistent = None

    if t3 is not None:
        print()
        print("=" * 78)
        print("Cross-level Test 3: Sato-Tate KS test consistency")
        print("=" * 78)
        ks_stats, ks_ps = [], []
        norm_pass = []
        for lvl in PRIMARY_LEVELS:
            r = t3['results'].get(f'level_{lvl}')
            if r is None:
                continue
            ks_stats.append(r['ks_test']['ks_stat'])
            ks_ps.append(r['ks_test']['ks_p_value'])
            norm_pass.append(r['normalization_gate']['pass_check'])
            print(f"  Γ₀({lvl}): KS_stat = {r['ks_test']['ks_stat']:.4f}, "
                  f"KS_p = {r['ks_test']['ks_p_value']:.4e}, "
                  f"norm_pass = {r['normalization_gate']['pass_check']}")
        all_norm_pass = all(norm_pass)
        # KS_stat consistency: all stats within similar magnitude (within 2x)
        ks_consistent = max(ks_stats) < 2.0 * min(ks_stats) if min(ks_stats) > 0 else False
        print(f"  All normalization gates pass: {all_norm_pass}")
        print(f"  KS stats consistent across levels (max/min < 2): {ks_consistent}")
    else:
        all_norm_pass = ks_consistent = None

    # Final cross-level verdict
    print()
    print("=" * 78)
    print("Cross-level Test 4 verdict")
    print("=" * 78)
    summary = dict(
        test1_consistent=bool(test1_consistent) if test1_consistent is not None else None,
        test2_consistent=bool(test2_consistent) if test2_consistent is not None else None,
        test3_normalization_all_pass=bool(all_norm_pass) if all_norm_pass is not None else None,
        test3_ks_consistent=bool(ks_consistent) if ks_consistent is not None else None,
    )
    fully_consistent = (
        test1_consistent
        and (test2_consistent if test2_consistent is not None else True)
        and (all_norm_pass if all_norm_pass is not None else True)
    )
    if fully_consistent:
        verdict = "SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE — cross-level verdict consistency confirms methodology"
    elif test1_consistent:
        verdict = "SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE_PARTIAL — Test 1 NNS consistent across levels; some quantitative parameters diverge"
    else:
        verdict = "METHODOLOGY_INCONSISTENT_ACROSS_LEVELS — bulk-NNS verdict diverges across levels; debugging required"
    print(f"  → {verdict}")
    print(f"  Summary: {summary}")

    out = OUT_DIR / 'cross_level_test4.json'
    with open(out, 'w') as f:
        json.dump({
            'phase': '34e',
            'test': 'Test 4 cross-level reproducibility (pivot from cross-dataset)',
            'pivot_note': 'Seymour-Howell 2022 Zenodo dump lacks N=1 (SL(2,ℤ)). Cross-dataset reproducibility pivoted to cross-LEVEL reproducibility across 6 representative Γ₀(N) squarefree levels.',
            'primary_levels': PRIMARY_LEVELS,
            'summary': summary,
            'verdict': verdict,
        }, f, indent=2)
    print(f"\n→ wrote {out}")


if __name__ == '__main__':
    main()
