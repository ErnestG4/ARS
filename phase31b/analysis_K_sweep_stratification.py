"""
phase31b/analysis_K_sweep_stratification.py — stratify the Phase 30
Analysis 1 +0.10 aggregate ks_med drift across the Kuramoto K-sweep.

Method: re-simulate Kuramoto at representative K_factors {0.0, 0.5, 1.0,
1.5, 2.0} (seed 0).  For each cell:
  1. Compute aggregate ks_gue_med, rep_med, and per-q RF spectrum.
  2. For each oscillator i, compute aggregate ARS classification with
     oscillator i removed (leave-one-out).  ΔKS_LOO[i] = ks_full −
     ks_loo[i] = oscillator i's contribution to the aggregate.
  3. Sort oscillators by ω_i (natural frequency) and by per-oscillator
     ks_gue_med; correlate with ΔKS_LOO.
  4. Per-q aggregate RF spectrum across K: which q-bands shift between
     K=0 and K=2 K_c?

Outputs:
  data/phase31b_results/Ksweep_aggregate_ks_per_K.parquet
  data/phase31b_results/Ksweep_loo_influence.parquet
  data/phase31b_results/Ksweep_per_q_rf_spectrum.parquet
  data/phase31b_results/Ksweep_stratification_verdict.json
"""
from __future__ import annotations

import os
import sys
import json
import time
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, THIS_DIR)

from kuramoto import simulate, critical_coupling, aggregate_spikes, per_oscillator_rates
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q
from loo_influence import loo_aggregate_influence, aggregate_rf_per_q

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Re-use Phase 30 sim parameters
OMEGA_0 = 2.0 * np.pi * 2.0
GAMMA = 2.0 * np.pi * 1.0
DT = 0.005
T_SIM = 1200.0
T_TRANSIENT = 200.0
N_OSC = 100
SEED = 0
K_FACTORS = [0.0, 0.5, 1.0, 1.5, 2.0]

N_WORKERS = min(16, cpu_count())

# Move kuramoto module onto path
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))


def main():
    K_c = critical_coupling(GAMMA)
    print("=" * 72)
    print("Phase 31b — K-sweep stratification of +0.10 aggregate ks_med drift")
    print("=" * 72)
    print(f"K_c = {K_c:.4f}   N_osc = {N_OSC}   seed = {SEED}")
    print(f"K_factors = {K_FACTORS}\n")

    aggregate_rows = []
    loo_rows = []
    rf_rows = []

    for K_factor in K_FACTORS:
        K = K_factor * K_c
        print(f"\n--- K_factor = {K_factor:.2f} (K = {K:.3f}) ---")
        t0 = time.time()
        sim = simulate(K=K, sigma=0.0, N=N_OSC,
                        omega_0=OMEGA_0, gamma=GAMMA,
                        dt=DT, T_sim=T_SIM, T_transient=T_TRANSIENT,
                        seed=SEED, record_r=True, r_downsample=200)
        rates = per_oscillator_rates(sim)
        agg_events = aggregate_spikes(sim)
        print(f"  sim ⏱{time.time()-t0:.1f}s  |r|={np.mean(sim.r_trace):.3f}  "
              f"n_agg_events={agg_events.size}")

        # Aggregate classification
        agg_cl = classify(agg_events, return_full=False, q_max=Q_MAX,
                            min_events_per_q=MIN_EVENTS_PER_Q)
        # Aggregate RF spectrum
        agg_rf = aggregate_rf_per_q(agg_events, q_max=Q_MAX)
        agg_row = dict(
            K_factor=float(K_factor), K=float(K),
            order_param_mean=float(np.mean(sim.r_trace)),
            n_agg_events=int(agg_events.size),
            agg_ks_gue_med=agg_cl['ks_gue_med'],
            agg_rep_med=agg_cl['rep_med'],
            agg_primary=agg_cl['primary'],
            rate_med=float(np.median(rates)),
        )
        aggregate_rows.append(agg_row)
        print(f"  agg: ks={agg_cl['ks_gue_med']:.4f}  rep={agg_cl['rep_med']:.4f}  "
              f"primary={agg_cl['primary']}")

        # RF spectrum per q
        for q in range(1, Q_MAX + 1):
            rf_rows.append(dict(
                K_factor=float(K_factor), q=int(q),
                rf_amp=float(agg_rf[q - 1]),
            ))

        # LOO influence per oscillator
        t0 = time.time()
        loo_df = loo_aggregate_influence(
            [s for s in sim.spikes], q_max=Q_MAX,
            min_events_per_q=MIN_EVENTS_PER_Q, n_workers=N_WORKERS,
        )
        # Tag with K_factor and oscillator metadata
        loo_df['K_factor'] = float(K_factor)
        loo_df['omega_i'] = sim.omegas[loo_df['i'].values]
        loo_df['rate_i'] = rates[loo_df['i'].values]
        loo_rows.append(loo_df)
        print(f"  LOO ⏱{time.time()-t0:.1f}s  "
              f"|Δks| max={loo_df['delta_ks'].abs().max():.4f}  "
              f"|Δks| mean={loo_df['delta_ks'].abs().mean():.5f}")

    # ─── save ───
    df_agg = pd.DataFrame(aggregate_rows)
    df_loo = pd.concat(loo_rows, ignore_index=True)
    df_rf = pd.DataFrame(rf_rows)

    df_agg.to_parquet(OUT_DIR / 'Ksweep_aggregate_ks_per_K.parquet', index=False)
    df_loo.to_parquet(OUT_DIR / 'Ksweep_loo_influence.parquet', index=False)
    df_rf.to_parquet(OUT_DIR / 'Ksweep_per_q_rf_spectrum.parquet', index=False)
    print(f"\n  → Ksweep_aggregate_ks_per_K.parquet ({len(df_agg)} rows)")
    print(f"  → Ksweep_loo_influence.parquet ({len(df_loo)} rows)")
    print(f"  → Ksweep_per_q_rf_spectrum.parquet ({len(df_rf)} rows)")

    # ─── interpretation ───
    print("\n=== Per-K aggregate classifications ===")
    print(df_agg[['K_factor', 'order_param_mean', 'agg_ks_gue_med',
                    'agg_rep_med', 'agg_primary', 'n_agg_events']].to_string(index=False))

    # K-axis ks drift
    ks_0 = df_agg[df_agg['K_factor'] == 0.0].iloc[0]['agg_ks_gue_med']
    ks_2 = df_agg[df_agg['K_factor'] == 2.0].iloc[0]['agg_ks_gue_med']
    delta_ks_axis = ks_2 - ks_0
    print(f"\nK-axis drift: Δks_agg from K=0 to K=2*Kc = {delta_ks_axis:+.4f}")

    # LOO: identify highly influential oscillators per K_factor
    print("\n=== LOO influence summary per K ===")
    for K_factor in K_FACTORS:
        sub = df_loo[df_loo['K_factor'] == K_factor]
        if not len(sub):
            continue
        print(f"\n  K={K_factor:.2f}*Kc:")
        # Top 5 oscillators by |Δks|
        top5 = sub.iloc[sub['delta_ks'].abs().argsort()[::-1][:5]]
        for _, r in top5.iterrows():
            print(f"    osc {int(r['i']):3d}  ω={r['omega_i']/(2*np.pi):.3f}Hz  "
                  f"rate={r['rate_i']:.2f}Hz  n_events={int(r['n_events_i']):4d}  "
                  f"Δks={r['delta_ks']:+.4f}")

    # Correlate Δks with rate and ω
    print("\n=== Δks correlation with oscillator properties ===")
    for K_factor in K_FACTORS:
        sub = df_loo[df_loo['K_factor'] == K_factor].copy()
        if len(sub) < 5:
            continue
        sub = sub.dropna(subset=['delta_ks'])
        if len(sub) < 5:
            continue
        rho_rate = sub['delta_ks'].corr(sub['rate_i'])
        rho_omega = sub['delta_ks'].corr(sub['omega_i'])
        rho_n = sub['delta_ks'].corr(sub['n_events_i'])
        print(f"  K={K_factor:.2f}*Kc:  ρ(Δks, rate)={rho_rate:+.3f}  "
              f"ρ(Δks, ω)={rho_omega:+.3f}  ρ(Δks, n_events)={rho_n:+.3f}")

    # RF per-q drift across K
    print("\n=== RF per-q drift K=0 → K=2*Kc ===")
    rf_0 = df_rf[df_rf['K_factor'] == 0.0].set_index('q')['rf_amp']
    rf_2 = df_rf[df_rf['K_factor'] == 2.0].set_index('q')['rf_amp']
    rf_delta = rf_2 - rf_0
    rf_delta_abs = rf_delta.abs()
    top10_q = rf_delta_abs.sort_values(ascending=False).head(10)
    print("  Top 10 q with largest |ΔRF| from K=0 to K=2*Kc:")
    for q, dabs in top10_q.items():
        d_signed = rf_delta[q]
        print(f"    q={q:3d}  ΔRF={d_signed:+.4f}  RF@K=0={rf_0[q]:.4f}  "
              f"RF@K=2={rf_2[q]:.4f}")

    # ─── verdict ───
    # Carrier identification: which oscillator subset carries the K-axis drift?
    # Find oscillator class that consistently shows large |Δks| across K.
    loo_high = df_loo[df_loo['delta_ks'].abs() > 0.005]
    n_high = len(loo_high)
    if n_high:
        median_rate_high = float(loo_high['rate_i'].median())
        median_omega_high = float(loo_high['omega_i'].median() / (2 * np.pi))
    else:
        median_rate_high = median_omega_high = np.nan

    # Carrier verdict
    rho_rate_all = []
    rho_omega_all = []
    for K_factor in K_FACTORS:
        sub = df_loo[df_loo['K_factor'] == K_factor].dropna(subset=['delta_ks'])
        if len(sub) >= 5:
            rho_rate_all.append(sub['delta_ks'].corr(sub['rate_i']))
            rho_omega_all.append(sub['delta_ks'].corr(sub['omega_i']))

    mean_rho_rate = float(np.nanmean(rho_rate_all))
    mean_rho_omega = float(np.nanmean(rho_omega_all))

    # Verdict logic
    if abs(delta_ks_axis) < 0.01:
        carrier_verdict = 'SIGNAL_TOO_SMALL'
    elif abs(mean_rho_rate) > 0.3 or abs(mean_rho_omega) > 0.3:
        carrier_verdict = 'CARRIED_BY_SPECIFIC_OSCILLATOR_CLASS'
    elif n_high <= 5:
        carrier_verdict = 'CARRIED_BY_FEW_OSCILLATORS'
    else:
        carrier_verdict = 'DISTRIBUTED_ACROSS_OSCILLATORS'

    summary = dict(
        delta_ks_K0_to_K2=float(delta_ks_axis),
        K_factors_tested=K_FACTORS,
        n_oscillators=N_OSC,
        carrier_verdict=carrier_verdict,
        mean_rho_delta_ks_vs_rate=mean_rho_rate,
        mean_rho_delta_ks_vs_omega=mean_rho_omega,
        n_high_loo=int(n_high),
        median_rate_high=median_rate_high,
        median_omega_high_hz=median_omega_high,
        rf_top10_q_at_K2_vs_K0=top10_q.to_dict(),
    )
    with open(OUT_DIR / 'Ksweep_stratification_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → Ksweep_stratification_verdict.json")
    print(f"\nVERDICT (sub-modal carrier identification): {carrier_verdict}")
    print(f"  Δks_K0→K2 = {delta_ks_axis:+.4f}")
    print(f"  Mean ρ(Δks_LOO, rate_i)   = {mean_rho_rate:+.3f}")
    print(f"  Mean ρ(Δks_LOO, ω_i)      = {mean_rho_omega:+.3f}")
    print(f"  Oscillators with |Δks_LOO| > 0.005: {n_high}")


if __name__ == '__main__':
    main()
