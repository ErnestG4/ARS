"""
phase30/analysis2_Ksigma_phase_space.py — Phase 30 Analysis 2: ARS
classification of stochastic Kuramoto across the (K, σ) plane.

Per Phase 30 brief:
  - Stochastic Kuramoto (Euler–Maruyama, additive white Gaussian noise).
  - K from 0.5 K_c to 2 K_c in steps of 0.25 K_c (focus on critical regime).
  - σ from 0 to ω_0 in 6 steps (noise small to comparable to natural freq).
  - Per-oscillator and recording-wide ARS at q_max=30.
  - Multi-order falsification (full per-q DataFrame stored).
  - Per-oscillator rate-matched Poisson surrogate per (K, σ) cell.
  - Phase-space map: ARS classifications as a function of (K, σ).

Outputs:
  data/phase30_results/analysis2_per_oscillator_real.parquet
  data/phase30_results/analysis2_per_oscillator_surrogate.parquet
  data/phase30_results/analysis2_aggregate.parquet
  data/phase30_results/analysis2_summary_by_cell.parquet
  data/phase30_results/analysis2_verdict.json
"""
from __future__ import annotations

import os
import sys
import time
import json
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from kuramoto import (
    simulate, critical_coupling, per_oscillator_rates,
    aggregate_spikes, rate_matched_poisson_surrogate,
)
from stationarity import classify_in_windows, stationarity_summary
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
from ars_classify import classify, per_q_columns, Q_MAX, MIN_EVENTS_PER_Q

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase30_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

OMEGA_0 = 2.0 * np.pi * 2.0
GAMMA = 2.0 * np.pi * 1.0
DT = 0.005
T_SIM = 1200.0
T_TRANSIENT = 200.0
N_DEFAULT = 100

K_FACTORS = np.array([0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0])
# σ in units of ω_0.  σ=0 reproduces classical Kuramoto.
SIGMA_FACTORS = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
SEEDS = [0, 1, 2]

# Stationarity check parameters (per user course-correction).  Always
# 4-window check on aggregate; denser 10-window at K_c boundary band
# OR at transition cells (high-noise where order param is small).
N_WINDOWS_DEFAULT = 4
N_WINDOWS_BOUNDARY = 10
BOUNDARY_K_RANGE = (0.75, 1.25)

N_WORKERS = min(16, cpu_count())


def _classify_one(args):
    i, ev, q_max = args
    if ev.size < MIN_EVENTS_PER_Q:
        return dict(i=i, primary='underpowered', rep_med=np.nan,
                    ks_gue_med=np.nan, n_well=0, n_events=int(ev.size),
                    per_q=None)
    r = classify(ev, return_full=True, q_max=q_max)
    cols = per_q_columns(r['per_q'])
    return dict(i=i, primary=r['primary'], rep_med=r['rep_med'],
                ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
                n_events=int(ev.size), **cols)


def parallel_classify(events_list, q_max=Q_MAX):
    args = [(i, ev, q_max) for i, ev in enumerate(events_list)]
    with Pool(N_WORKERS) as pool:
        return list(pool.imap_unordered(_classify_one, args, chunksize=4))


def run_one_cell(K: float, sigma: float, seed: int, N: int):
    sim = simulate(K=K, sigma=sigma, N=N,
                    omega_0=OMEGA_0, gamma=GAMMA,
                    dt=DT, T_sim=T_SIM, T_transient=T_TRANSIENT,
                    seed=seed, record_r=True, r_downsample=200)
    rates = per_oscillator_rates(sim)
    K_c = sim.K_c

    raw_real = parallel_classify(sim.spikes)
    real_rows = []
    for r in raw_real:
        i = r['i']
        real_rows.append(dict(
            K=K, K_factor=K / K_c, sigma=sigma,
            sigma_factor=sigma / OMEGA_0, seed=seed, N=N,
            i=i, n_events=r['n_events'], rate=float(rates[i]),
            omega_i=float(sim.omegas[i]),
            primary=r['primary'], rep_med=r['rep_med'],
            ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
            quadrants_per_q=r.get('quadrants_per_q'),
            rep_int_per_q=r.get('rep_int_per_q'),
            ks_gue_per_q=r.get('ks_gue_per_q'),
        ))

    sur = rate_matched_poisson_surrogate(sim, seed=seed)
    raw_sur = parallel_classify(sur)
    sur_rows = [
        dict(K=K, K_factor=K / K_c, sigma=sigma,
             sigma_factor=sigma / OMEGA_0, seed=seed, N=N,
             i=r['i'], n_events=r['n_events'],
             primary=r['primary'], rep_med=r['rep_med'],
             ks_gue_med=r['ks_gue_med'])
        for r in raw_sur
    ]

    agg = aggregate_spikes(sim)
    if agg.size >= MIN_EVENTS_PER_Q:
        r_agg = classify(agg, return_full=False, q_max=Q_MAX)
    else:
        r_agg = dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n_well=0)

    K_factor_val = K / K_c
    in_boundary = BOUNDARY_K_RANGE[0] <= K_factor_val <= BOUNDARY_K_RANGE[1]
    n_win = N_WINDOWS_BOUNDARY if in_boundary else N_WINDOWS_DEFAULT
    if agg.size >= n_win * MIN_EVENTS_PER_Q:
        per_win = classify_in_windows(agg, n_windows=n_win,
                                        total_duration=T_SIM - T_TRANSIENT,
                                        q_max=Q_MAX,
                                        min_events_per_q=MIN_EVENTS_PER_Q)
        stat = stationarity_summary(per_win, full_sequence=r_agg)
    else:
        stat = dict(n_windows=0, stationary=True, modal_window=None,
                     fraction_modal=np.nan, agree_with_full=False,
                     rep_med_across_windows_mean=np.nan,
                     rep_med_across_windows_std=np.nan,
                     ks_med_across_windows_mean=np.nan,
                     ks_med_across_windows_std=np.nan,
                     cv_rep_across_windows=np.nan,
                     cv_ks_across_windows=np.nan,
                     primaries_per_window=[])

    aggregate_row = dict(
        K=K, K_factor=K_factor_val, sigma=sigma,
        sigma_factor=sigma / OMEGA_0,
        seed=seed, N=N,
        n_events_total=int(agg.size),
        agg_primary=r_agg['primary'], agg_rep_med=r_agg['rep_med'],
        agg_ks_med=r_agg['ks_gue_med'], agg_n_well=r_agg['n_well'],
        order_param_mean=float(np.mean(sim.r_trace)),
        order_param_std=float(np.std(sim.r_trace)),
        rate_med=float(np.median(rates)),
        stat_n_windows=int(stat.get('n_windows', 0)),
        stat_modal_window=stat.get('modal_window'),
        stat_fraction_modal=stat.get('fraction_modal', np.nan),
        stat_rep_mean=stat.get('rep_med_across_windows_mean', np.nan),
        stat_rep_std=stat.get('rep_med_across_windows_std', np.nan),
        stat_ks_mean=stat.get('ks_med_across_windows_mean', np.nan),
        stat_ks_std=stat.get('ks_med_across_windows_std', np.nan),
        stat_cv_rep=stat.get('cv_rep_across_windows', np.nan),
        stat_cv_ks=stat.get('cv_ks_across_windows', np.nan),
        stat_stationary=bool(stat.get('stationary', True)),
        stat_agree_with_full=bool(stat.get('agree_with_full', False)),
        stat_primaries_per_window=stat.get('primaries_per_window', []),
    )
    return real_rows, sur_rows, aggregate_row


def main():
    print("=" * 72)
    print("Phase 30 — Analysis 2: (K, σ) phase-space, stochastic Kuramoto")
    print("=" * 72)
    K_c = critical_coupling(GAMMA)
    print(f"omega_0 = {OMEGA_0:.4f} rad/s ({OMEGA_0/(2*np.pi):.2f} Hz)")
    print(f"gamma   = {GAMMA:.4f} rad/s ({GAMMA/(2*np.pi):.2f} Hz HWHM)")
    print(f"K_c     = {K_c:.4f} rad/s")
    print(f"K_factors = {K_FACTORS.tolist()}  ({len(K_FACTORS)})")
    print(f"sigma_factors (× omega_0) = {SIGMA_FACTORS.tolist()}  ({len(SIGMA_FACTORS)})")
    print(f"seeds = {SEEDS}\n")

    real_all, sur_all, agg_all = [], [], []
    n_cells = len(K_FACTORS) * len(SIGMA_FACTORS) * len(SEEDS)
    cell_i = 0
    t_total = time.time()
    for sigma_factor in SIGMA_FACTORS:
        sigma = float(sigma_factor) * OMEGA_0
        for K_factor in K_FACTORS:
            K = float(K_factor) * K_c
            for seed in SEEDS:
                cell_i += 1
                t0 = time.time()
                real_rows, sur_rows, agg_row = run_one_cell(K, sigma, seed, N_DEFAULT)
                real_all.extend(real_rows)
                sur_all.extend(sur_rows)
                agg_all.append(agg_row)
                dt_wall = time.time() - t0
                t_elapsed = time.time() - t_total
                eta = (n_cells - cell_i) * (t_elapsed / cell_i)
                print(
                    f"  [{cell_i:3d}/{n_cells}] K={K_factor:.2f}*Kc σ={sigma_factor:.2f}*ω₀ "
                    f"seed={seed}  ⏱{dt_wall:5.1f}s  "
                    f"|r|={agg_row['order_param_mean']:.3f}  "
                    f"agg-prim={agg_row['agg_primary']:13s} "
                    f"ks={agg_row['agg_ks_med']:.3f} rep={agg_row['agg_rep_med']:.3f}  "
                    f"ETA {eta/60:.0f}min"
                )

    df_real = pd.DataFrame(real_all)
    df_sur = pd.DataFrame(sur_all)
    df_agg = pd.DataFrame(agg_all)
    df_real.to_parquet(OUT_DIR / 'analysis2_per_oscillator_real.parquet', index=False)
    df_sur.to_parquet(OUT_DIR / 'analysis2_per_oscillator_surrogate.parquet', index=False)
    df_agg.to_parquet(OUT_DIR / 'analysis2_aggregate.parquet', index=False)
    print(f"\n  → analysis2_per_oscillator_real.parquet  ({len(df_real)} rows)")
    print(f"  → analysis2_per_oscillator_surrogate.parquet  ({len(df_sur)} rows)")
    print(f"  → analysis2_aggregate.parquet  ({len(df_agg)} rows)")

    # ─── per-cell summary ───
    summary_rows = []
    for sigma_factor in SIGMA_FACTORS:
        for K_factor in K_FACTORS:
            sub_real = df_real[
                np.isclose(df_real['K_factor'], K_factor)
                & np.isclose(df_real['sigma_factor'], sigma_factor)
            ]
            sub_agg = df_agg[
                np.isclose(df_agg['K_factor'], K_factor)
                & np.isclose(df_agg['sigma_factor'], sigma_factor)
            ]
            well_real = sub_real[sub_real['primary'] != 'underpowered']
            if len(well_real):
                modal_real = well_real['primary'].value_counts().idxmax()
                ks_real = float(well_real['ks_gue_med'].median())
                rep_real = float(well_real['rep_med'].median())
            else:
                modal_real, ks_real, rep_real = 'underpowered', np.nan, np.nan
            modal_agg = sub_agg['agg_primary'].value_counts().idxmax() if len(sub_agg) else 'NA'
            ks_agg = float(sub_agg['agg_ks_med'].median())
            rep_agg = float(sub_agg['agg_rep_med'].median())

            summary_rows.append(dict(
                K_factor=float(K_factor), sigma_factor=float(sigma_factor),
                order_param_mean=float(sub_agg['order_param_mean'].mean()),
                rate_med=float(sub_real['rate'].median()),
                per_osc_modal=modal_real,
                per_osc_ks_med=ks_real,
                per_osc_rep_med=rep_real,
                agg_modal=modal_agg,
                agg_ks_med=ks_agg,
                agg_rep_med=rep_agg,
                n_seeds=int(sub_agg['seed'].nunique()),
            ))
    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_parquet(OUT_DIR / 'analysis2_summary_by_cell.parquet', index=False)
    print(f"  → analysis2_summary_by_cell.parquet  ({len(df_summary)} rows)\n")

    # Print phase-space maps as text grids.
    print("Per-oscillator modal classification (K_factor → cols, sigma_factor → rows):")
    pivot_modal = df_summary.pivot(index='sigma_factor', columns='K_factor',
                                     values='per_osc_modal')
    print(pivot_modal.to_string())
    print("\nAggregate modal:")
    pivot_agg = df_summary.pivot(index='sigma_factor', columns='K_factor',
                                   values='agg_modal')
    print(pivot_agg.to_string())
    print("\nPer-oscillator rep_med:")
    pivot_rep = df_summary.pivot(index='sigma_factor', columns='K_factor',
                                   values='per_osc_rep_med')
    print(pivot_rep.round(3).to_string())
    print("\nAggregate ks_gue_med:")
    pivot_ks = df_summary.pivot(index='sigma_factor', columns='K_factor',
                                  values='agg_ks_med')
    print(pivot_ks.round(3).to_string())

    # ─── verdict ───
    n_modal_per_osc = df_summary['per_osc_modal'].nunique()
    n_modal_agg = df_summary['agg_modal'].nunique()

    # Check rate drift across the (K, σ) plane
    rate_drift = float((df_summary['rate_med'].max() - df_summary['rate_med'].min())
                         / max(df_summary['rate_med'].min(), 1e-9))

    # Test "noise dominated": across each row (fixed σ), modal varies less
    # than across each column (fixed K).  And vice versa.
    K_axis_variation = 0
    sigma_axis_variation = 0
    for sf in SIGMA_FACTORS:
        sub = df_summary[np.isclose(df_summary['sigma_factor'], sf)]
        K_axis_variation += sub['per_osc_modal'].nunique() - 1
    for kf in K_FACTORS:
        sub = df_summary[np.isclose(df_summary['K_factor'], kf)]
        sigma_axis_variation += sub['per_osc_modal'].nunique() - 1

    # Stationarity diagnostics on the boundary K cells
    boundary_agg = df_agg[
        (df_agg['K_factor'] >= BOUNDARY_K_RANGE[0])
        & (df_agg['K_factor'] <= BOUNDARY_K_RANGE[1])
    ]
    n_nonstationary_boundary = int((~boundary_agg['stat_stationary'].astype(bool)).sum())
    n_total_boundary = int(len(boundary_agg))
    boundary_nonstationary_frac = n_nonstationary_boundary / max(n_total_boundary, 1)

    # Verdict logic
    if rate_drift > 0.5:
        verdict = 'RATE_REGIME_CONFOUNDED'
    elif n_modal_per_osc <= 1 and n_modal_agg <= 1 and boundary_nonstationary_frac < 0.3:
        verdict = 'DEGENERATE_MAP'
    elif sigma_axis_variation > 2 * max(K_axis_variation, 1):
        verdict = 'NOISE_DOMINATED'
    elif boundary_nonstationary_frac >= 0.5 and n_modal_agg <= 1:
        verdict = 'TIME_VARYING_AT_CRITICAL'
    else:
        verdict = 'CLEAN_PHASE_SPACE_STRUCTURE'

    summary = dict(
        verdict=verdict,
        n_K=len(K_FACTORS), n_sigma=len(SIGMA_FACTORS), n_seeds=len(SEEDS),
        N=N_DEFAULT, K_c=float(K_c), omega_0=float(OMEGA_0), gamma=float(GAMMA),
        T_sim=float(T_SIM), T_transient=float(T_TRANSIENT),
        n_modal_per_osc_distinct=int(n_modal_per_osc),
        n_modal_agg_distinct=int(n_modal_agg),
        rate_drift_fraction=float(rate_drift),
        K_axis_modal_variation=int(K_axis_variation),
        sigma_axis_modal_variation=int(sigma_axis_variation),
        n_windows_default=N_WINDOWS_DEFAULT,
        n_windows_boundary=N_WINDOWS_BOUNDARY,
        boundary_K_range=list(BOUNDARY_K_RANGE),
        boundary_nonstationary_frac=float(boundary_nonstationary_frac),
        n_nonstationary_boundary=int(n_nonstationary_boundary),
        n_total_boundary=int(n_total_boundary),
    )
    with open(OUT_DIR / 'analysis2_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → analysis2_verdict.json")
    print(f"\nVERDICT: {verdict}")
    print(f"  n_modal per-osc distinct = {n_modal_per_osc}")
    print(f"  n_modal aggregate distinct = {n_modal_agg}")
    print(f"  K-axis modal variation = {K_axis_variation} "
          f"(across rows of fixed σ, summed over rows)")
    print(f"  σ-axis modal variation = {sigma_axis_variation} "
          f"(across cols of fixed K, summed over cols)")
    print(f"  rate_drift_fraction = {rate_drift:.3f}")
    print(f"  boundary non-stationary cells: "
          f"{n_nonstationary_boundary}/{n_total_boundary} "
          f"({boundary_nonstationary_frac:.1%}) "
          f"[critical band {BOUNDARY_K_RANGE} K_factor]")


if __name__ == '__main__':
    main()
