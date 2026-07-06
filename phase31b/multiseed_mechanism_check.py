"""
phase31b/multiseed_mechanism_check.py — verify that the K-axis rate-
distribution-narrowing mechanism (Phase 31b finding) generalizes across
the 3 Phase 30 Analysis 1 seeds.

The single-seed re-simulation (seed=0) gave aggregate ks_med drift
+0.0798 from K=0 to K=2 K_c, attributable to per-oscillator-rate-
variance narrowing under locking.  Phase 30's headline multi-seed
result was +0.10.  This script checks:

  1. Does per-oscillator-rate variance decrease monotonically with K
     across all 3 seeds?
  2. Does the aggregate ks_med drift +0.10 reproduce in all 3 seeds?
  3. Is the rate-variance vs aggregate-ks_med relationship consistent
     across seeds?

Uses the existing Phase 30 Analysis 1 parquets — no re-simulation
needed.

Output:
  data/phase31b_results/multiseed_mechanism_check.parquet
  data/phase31b_results/multiseed_mechanism_verdict.json
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
PHASE30 = Path(ROOT_DIR) / 'data' / 'phase30_results'


def main():
    print("=" * 72)
    print("Phase 31b — Multi-seed mechanism check (rate narrowing under locking)")
    print("=" * 72)

    real_df = pd.read_parquet(PHASE30 / 'analysis1_per_oscillator_real.parquet')
    agg_df = pd.read_parquet(PHASE30 / 'analysis1_aggregate.parquet')
    print(f"  per-oscillator rows: {len(real_df)}")
    print(f"  aggregate rows: {len(agg_df)}")
    print(f"  K_factors: {sorted(real_df['K_factor'].unique())}")
    print(f"  seeds: {sorted(real_df['seed'].unique())}\n")

    # ─── per-(K, seed) rate statistics ───
    rate_stats = real_df.groupby(['K_factor', 'seed']).agg(
        rate_mean=('rate', 'mean'),
        rate_std=('rate', 'std'),
        rate_iqr=('rate', lambda x: np.subtract(*np.percentile(x, [75, 25]))),
        rate_min=('rate', 'min'),
        rate_max=('rate', 'max'),
        n_oscillators=('rate', 'count'),
    ).reset_index()

    # ─── merge with aggregate ks_med ───
    merged = rate_stats.merge(
        agg_df[['K_factor', 'seed', 'agg_ks_med', 'agg_rep_med',
                 'agg_primary', 'order_param_mean']],
        on=['K_factor', 'seed']
    )
    merged.to_parquet(OUT_DIR / 'multiseed_mechanism_check.parquet', index=False)

    # ─── Q1: rate std monotone in K per seed? ───
    print("=== Q1: Does per-oscillator-rate STD decrease monotonically with K per seed? ===")
    q1_per_seed = []
    for seed in sorted(merged['seed'].unique()):
        sub = merged[merged['seed'] == seed].sort_values('K_factor')
        rate_stds = sub['rate_std'].values
        K_factors = sub['K_factor'].values

        # Spearman correlation: K vs rate_std (should be negative for narrowing)
        from scipy.stats import spearmanr
        rho_K_rstd, p_K_rstd = spearmanr(K_factors, rate_stds)

        # Endpoints
        rstd_K0 = float(rate_stds[0])
        rstd_K2 = float(rate_stds[-1])
        delta_rstd = rstd_K2 - rstd_K0
        rstd_drop_frac = (rstd_K0 - rstd_K2) / max(rstd_K0, 1e-9)

        # Monotonicity: check that rate_std at K=2*Kc < rate_std at K=Kc < rate_std at K=0
        # Use the trend over K_factor∈[0, 0.5, 1.0, 1.5, 2.0]
        idx_K0 = np.argmin(np.abs(K_factors - 0.0))
        idx_Kc = np.argmin(np.abs(K_factors - 1.0))
        idx_K2 = np.argmin(np.abs(K_factors - 2.0))
        monotone_endpoints = (rate_stds[idx_K2] < rate_stds[idx_Kc]
                                < rate_stds[idx_K0])

        q1_per_seed.append(dict(
            seed=int(seed),
            rate_std_K0=rstd_K0,
            rate_std_Kc=float(rate_stds[idx_Kc]),
            rate_std_K2=rstd_K2,
            delta_rate_std=float(delta_rstd),
            rate_std_drop_fraction=float(rstd_drop_frac),
            spearman_rho_K_vs_rstd=float(rho_K_rstd),
            monotone_endpoints=bool(monotone_endpoints),
        ))
        print(f"  seed {seed}: rate_std at K=0 → K_c → 2K_c: "
              f"{rstd_K0:.3f} → {rate_stds[idx_Kc]:.3f} → {rstd_K2:.3f}  "
              f"(drop {rstd_drop_frac:.1%})  "
              f"Spearman ρ(K, rate_std) = {rho_K_rstd:+.3f}  "
              f"monotone endpoints: {monotone_endpoints}")

    q1_results = pd.DataFrame(q1_per_seed)

    # ─── Q2: aggregate ks_med drift K=0 → K=2*Kc per seed ───
    print("\n=== Q2: Aggregate Δks_K0→K2 per seed ===")
    q2_per_seed = []
    for seed in sorted(merged['seed'].unique()):
        sub = merged[merged['seed'] == seed]
        ks_K0 = float(sub[sub['K_factor'] == 0.0]['agg_ks_med'].iloc[0]) if (sub['K_factor'] == 0.0).any() else np.nan
        ks_K2 = float(sub[sub['K_factor'] == 2.0]['agg_ks_med'].iloc[0]) if (sub['K_factor'] == 2.0).any() else np.nan
        delta_ks = ks_K2 - ks_K0
        q2_per_seed.append(dict(
            seed=int(seed),
            agg_ks_med_K0=ks_K0,
            agg_ks_med_K2=ks_K2,
            delta_ks=float(delta_ks),
        ))
        print(f"  seed {seed}: agg_ks_med K=0 → K=2*Kc: "
              f"{ks_K0:.4f} → {ks_K2:.4f}  Δ={delta_ks:+.4f}")
    q2_results = pd.DataFrame(q2_per_seed)

    # ─── Q3: rate-std vs aggregate-ks_med correlation across (K, seed) ───
    print("\n=== Q3: Correlation between rate_std and agg_ks_med across all (K, seed) ===")
    from scipy.stats import spearmanr
    rho_rs_ks, p_rs_ks = spearmanr(merged['rate_std'], merged['agg_ks_med'])
    rho_ropm_ks, p_ropm_ks = spearmanr(merged['order_param_mean'], merged['agg_ks_med'])
    rho_rs_K, p_rs_K = spearmanr(merged['K_factor'], merged['rate_std'])
    print(f"  ρ(rate_std, agg_ks_med)        = {rho_rs_ks:+.3f}  (p={p_rs_ks:.2e})")
    print(f"  ρ(order_param, agg_ks_med)     = {rho_ropm_ks:+.3f}  (p={p_ropm_ks:.2e})")
    print(f"  ρ(K_factor, rate_std)          = {rho_rs_K:+.3f}  (p={p_rs_K:.2e})")

    # ─── Per-K (across seeds) mean ks_med drift ───
    print("\n=== Per-K mean aggregate ks_med (multi-seed) ===")
    per_K = merged.groupby('K_factor').agg(
        mean_ks=('agg_ks_med', 'mean'),
        std_ks=('agg_ks_med', 'std'),
        mean_rate_std=('rate_std', 'mean'),
        std_rate_std=('rate_std', 'std'),
        mean_order_param=('order_param_mean', 'mean'),
        n_seeds=('seed', 'count'),
    )
    print(per_K.round(4).to_string())

    # ─── Verdict ───
    rate_narrowing_seed_robust = all(q['rate_std_drop_fraction'] > 0.1
                                       and q['monotone_endpoints']
                                       for q in q1_per_seed)
    delta_ks_per_seed = [q['delta_ks'] for q in q2_per_seed]
    delta_ks_mean = float(np.mean(delta_ks_per_seed))
    delta_ks_std = float(np.std(delta_ks_per_seed))
    multi_seed_delta_ks_consistent = (
        delta_ks_std < 0.3 * abs(delta_ks_mean)
        and all(d > 0 for d in delta_ks_per_seed)
    )

    if rate_narrowing_seed_robust and multi_seed_delta_ks_consistent and abs(rho_rs_ks) > 0.3:
        verdict = 'MECHANISM_GENERALIZES'
    elif rate_narrowing_seed_robust:
        verdict = 'NARROWING_GENERALIZES_DELTA_KS_INCONSISTENT'
    elif multi_seed_delta_ks_consistent:
        verdict = 'DELTA_KS_GENERALIZES_NARROWING_SEED_SPECIFIC'
    else:
        verdict = 'MECHANISM_SEED_SPECIFIC'

    summary = dict(
        verdict=verdict,
        q1_per_seed=q1_per_seed,
        q1_rate_narrowing_seed_robust=bool(rate_narrowing_seed_robust),
        q2_per_seed=q2_per_seed,
        q2_delta_ks_mean=delta_ks_mean,
        q2_delta_ks_std=delta_ks_std,
        q2_multi_seed_consistent=bool(multi_seed_delta_ks_consistent),
        q3_rho_rate_std_vs_agg_ks_med=float(rho_rs_ks),
        q3_rho_K_vs_rate_std=float(rho_rs_K),
        q3_rho_order_param_vs_agg_ks_med=float(rho_ropm_ks),
    )
    with open(OUT_DIR / 'multiseed_mechanism_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → multiseed_mechanism_verdict.json")
    print(f"\nVERDICT: {verdict}")
    print(f"  Q1 (rate narrowing seed-robust): {rate_narrowing_seed_robust}")
    print(f"  Q2 (Δks K=0→K=2*Kc multi-seed): mean {delta_ks_mean:+.4f}  "
          f"std {delta_ks_std:.4f}  consistent: {multi_seed_delta_ks_consistent}")
    print(f"  Q3 (rate_std → agg_ks_med correlation): ρ = {rho_rs_ks:+.3f}")


if __name__ == '__main__':
    main()
