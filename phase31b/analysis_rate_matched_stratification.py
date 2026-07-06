"""
phase31b/analysis_rate_matched_stratification.py — stratify the Phase 30
Analysis 2 +0.23 Δks_med residual between real Kuramoto and rate-matched
Poisson surrogate.

Method: use the per-oscillator parquets already saved in Phase 30
Analysis 2 — they contain ks_gue_med, rep_med per (oscillator, K, σ,
seed) for both real and rate-matched-Poisson surrogate.  No re-simulation
needed.  Compute per-oscillator Δks = real − surrogate; correlate with
oscillator properties; identify which oscillator subsets carry the
residual.

Also compute, for representative cells in the modal-agreement band
σ ∈ [0.4, 0.8] (where real-modal = surrogate-modal = BL but Δks_med ≠ 0),
the per-q RF spectrum of real vs surrogate to test whether the +0.23
residual concentrates at specific q-bands.

Outputs:
  data/phase31b_results/RateMatch_per_oscillator_delta.parquet
  data/phase31b_results/RateMatch_correlation_summary.parquet
  data/phase31b_results/RateMatch_stratification_verdict.json
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
OUT_DIR.mkdir(parents=True, exist_ok=True)

PHASE30 = Path(ROOT_DIR) / 'data' / 'phase30_results'


def main():
    print("=" * 72)
    print("Phase 31b — rate-matched +0.23 Δks residual stratification")
    print("=" * 72)

    real_df = pd.read_parquet(PHASE30 / 'analysis2_per_oscillator_real.parquet')
    sur_df = pd.read_parquet(PHASE30 / 'analysis2_per_oscillator_surrogate.parquet')
    print(f"  real per-oscillator rows: {len(real_df)}")
    print(f"  surrogate per-oscillator rows: {len(sur_df)}\n")

    # Match real and surrogate by (K_factor, sigma_factor, seed, i)
    merge_keys = ['K_factor', 'sigma_factor', 'seed', 'i']
    real_cols = merge_keys + ['ks_gue_med', 'rep_med', 'primary', 'rate',
                                'omega_i', 'n_events']
    sur_cols = merge_keys + ['ks_gue_med', 'rep_med', 'primary', 'n_events']

    real_sub = real_df[real_cols].rename(columns={
        'ks_gue_med': 'ks_real', 'rep_med': 'rep_real',
        'primary': 'primary_real', 'n_events': 'n_events_real'
    })
    sur_sub = sur_df[sur_cols].rename(columns={
        'ks_gue_med': 'ks_sur', 'rep_med': 'rep_sur',
        'primary': 'primary_sur', 'n_events': 'n_events_sur'
    })

    merged = real_sub.merge(sur_sub, on=merge_keys, how='inner')
    merged['delta_ks'] = merged['ks_real'] - merged['ks_sur']
    merged['delta_rep'] = merged['rep_real'] - merged['rep_sur']
    merged['modal_agree'] = merged['primary_real'] == merged['primary_sur']

    print(f"  merged rows: {len(merged)}")
    print(f"  modal agreement: {merged['modal_agree'].sum()}/{len(merged)} "
          f"({merged['modal_agree'].mean():.1%})")
    print(f"  overall Δks: mean={merged['delta_ks'].mean():+.4f}  "
          f"median={merged['delta_ks'].median():+.4f}  "
          f"std={merged['delta_ks'].std():.4f}")
    print()

    merged.to_parquet(OUT_DIR / 'RateMatch_per_oscillator_delta.parquet',
                       index=False)

    # ─── per-(K, σ) Δks summary ───
    print("=== Per-(K, σ) Δks summary ===")
    summary_cells = merged.groupby(['K_factor', 'sigma_factor']).agg(
        n=('i', 'count'),
        mean_delta_ks=('delta_ks', 'mean'),
        median_delta_ks=('delta_ks', 'median'),
        std_delta_ks=('delta_ks', 'std'),
        modal_agree_frac=('modal_agree', 'mean'),
        rho_dks_rate=('delta_ks', lambda x: x.corr(merged.loc[x.index, 'rate'])),
        rho_dks_omega=('delta_ks', lambda x: x.corr(merged.loc[x.index, 'omega_i'])),
    ).reset_index()
    print(summary_cells.round(4).to_string(index=False))
    summary_cells.to_parquet(OUT_DIR / 'RateMatch_correlation_summary.parquet',
                              index=False)

    # ─── highlight: modal-agreement band σ ∈ [0.4, 0.8] (where Phase 30 said modal-matches)
    band = merged[(merged['sigma_factor'].isin([0.4, 0.6, 0.8]))
                    & (merged['modal_agree'])].copy()
    print(f"\n=== Modal-agreement band σ ∈ [0.4, 0.8] ===")
    print(f"  n cells: {len(band)}")
    print(f"  mean Δks = {band['delta_ks'].mean():+.4f}  "
          f"(Phase 30 claimed +0.23)")
    print(f"  mean Δrep = {band['delta_rep'].mean():+.4f}")
    print(f"  ρ(Δks, rate) = {band['delta_ks'].corr(band['rate']):+.3f}")
    print(f"  ρ(Δks, ω)    = {band['delta_ks'].corr(band['omega_i']):+.3f}")

    # ─── top oscillators by |Δks| in modal-agreement band ───
    band_sorted = band.sort_values('delta_ks', key=lambda x: x.abs(),
                                     ascending=False)
    print("\n  Top 10 oscillators by |Δks| in modal-agreement band:")
    print(band_sorted.head(10)[['K_factor', 'sigma_factor', 'seed', 'i',
                                  'omega_i', 'rate', 'ks_real', 'ks_sur',
                                  'delta_ks']].to_string(index=False))

    # ─── Δks vs rate stratified by σ band ───
    print(f"\n=== Δks-vs-rate by σ band ===")
    for sf in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
        sub = merged[np.isclose(merged['sigma_factor'], sf)]
        if not len(sub):
            continue
        rho_rate = sub['delta_ks'].corr(sub['rate'])
        rho_omega = sub['delta_ks'].corr(sub['omega_i'])
        mean_dks = sub['delta_ks'].mean()
        rate_min, rate_max = sub['rate'].min(), sub['rate'].max()
        n_modal_agree = sub['modal_agree'].sum()
        print(f"  σ={sf:.1f}*ω₀:  mean Δks={mean_dks:+.4f}  "
              f"ρ(Δks, rate)={rho_rate:+.3f}  ρ(Δks, ω)={rho_omega:+.3f}  "
              f"rate ∈ [{rate_min:.1f}, {rate_max:.1f}]Hz  "
              f"modal-agree {n_modal_agree}/{len(sub)}")

    # ─── verdict ───
    mean_dks_band = float(band['delta_ks'].mean())
    rho_rate_band = float(band['delta_ks'].corr(band['rate']))
    rho_omega_band = float(band['delta_ks'].corr(band['omega_i']))

    # Identify carrier
    if abs(mean_dks_band) < 0.05:
        carrier_verdict = 'SIGNAL_TOO_SMALL'
    elif abs(rho_rate_band) > 0.3:
        carrier_verdict = 'CARRIED_BY_RATE_REGIME'
    elif abs(rho_omega_band) > 0.3:
        carrier_verdict = 'CARRIED_BY_FREQUENCY_REGIME'
    else:
        carrier_verdict = 'DISTRIBUTED_ACROSS_OSCILLATORS'

    summary = dict(
        n_merged=int(len(merged)),
        overall_mean_delta_ks=float(merged['delta_ks'].mean()),
        overall_median_delta_ks=float(merged['delta_ks'].median()),
        modal_agreement_fraction=float(merged['modal_agree'].mean()),
        modal_agreement_band=dict(
            sigma_factors=[0.4, 0.6, 0.8],
            n_cells=int(len(band)),
            mean_delta_ks=mean_dks_band,
            mean_delta_rep=float(band['delta_rep'].mean()),
            rho_dks_rate=rho_rate_band,
            rho_dks_omega=rho_omega_band,
        ),
        carrier_verdict=carrier_verdict,
        per_sigma_summary={
            float(sf): dict(
                mean_delta_ks=float(
                    merged[np.isclose(merged['sigma_factor'], sf)]
                    ['delta_ks'].mean()),
                rho_dks_rate=float(
                    merged[np.isclose(merged['sigma_factor'], sf)]
                    ['delta_ks'].corr(
                        merged[np.isclose(merged['sigma_factor'], sf)]['rate'])),
            )
            for sf in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        },
    )
    with open(OUT_DIR / 'RateMatch_stratification_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → RateMatch_per_oscillator_delta.parquet")
    print(f"  → RateMatch_correlation_summary.parquet")
    print(f"  → RateMatch_stratification_verdict.json")
    print(f"\nVERDICT (rate-matched residual carrier): {carrier_verdict}")
    print(f"  Modal-agreement band σ ∈ [0.4, 0.8]:")
    print(f"    mean Δks = {mean_dks_band:+.4f}")
    print(f"    ρ(Δks, rate) = {rho_rate_band:+.3f}")
    print(f"    ρ(Δks, ω)    = {rho_omega_band:+.3f}")


if __name__ == '__main__':
    main()
