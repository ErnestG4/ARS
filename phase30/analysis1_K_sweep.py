"""
phase30/analysis1_K_sweep.py — Phase 30 Analysis 1: ARS classification of
classical Kuramoto across K.

Per Phase 30 brief:
  - Classical Kuramoto (sigma=0).
  - Sweep K from 0 to 2 K_c in steps of 0.1 K_c (21 K values).
  - N oscillators set by pilot (default N=100; pilot validated this is
    enough for stable classifications and runs ~3× faster than N=200).
  - Per oscillator and aggregate ARS at q_max=30, MIN_EVENTS_PER_Q=30.
  - Per-oscillator rate-matched Poisson surrogate at each K (Phase 26
    rate-matching lesson).
  - Multi-order falsification: full per-q DataFrame stored as flattened
    columns (quadrants_per_q, rep_int_per_q, ks_gue_per_q).
  - 3 seeds per K cell (replicates the variability under different
    Lorentzian-frequency draws).

Outputs:
  data/phase30_results/analysis1_per_oscillator_real.parquet
  data/phase30_results/analysis1_per_oscillator_surrogate.parquet
  data/phase30_results/analysis1_aggregate.parquet
  data/phase30_results/analysis1_summary_by_K.parquet
  data/phase30_results/analysis1_verdict.json
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

# Sim parameters (locked after pilot validation)
OMEGA_0 = 2.0 * np.pi * 2.0
GAMMA = 2.0 * np.pi * 1.0
DT = 0.005
T_SIM = 1200.0
T_TRANSIENT = 200.0
N_DEFAULT = 100

K_FACTORS = np.round(np.arange(0.0, 2.01, 0.1), 2)   # 0.0, 0.1, …, 2.0
SEEDS = [0, 1, 2]

# Stationarity check parameters per user course-correction.  Default 4
# non-overlapping windows on every cell's aggregate; denser 10-window
# check on every cell within the boundary regime |K - K_c| ≤ 0.2 K_c.
N_WINDOWS_DEFAULT = 4
N_WINDOWS_BOUNDARY = 10
BOUNDARY_K_RANGE = (0.8, 1.2)        # K_factor range considered "near K_c"

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


def run_one_cell(K: float, seed: int, N: int) -> tuple[list[dict], list[dict], dict]:
    """Returns (real_per_osc_rows, sur_per_osc_rows, aggregate_row)."""
    sim = simulate(K=K, sigma=0.0, N=N,
                    omega_0=OMEGA_0, gamma=GAMMA,
                    dt=DT, T_sim=T_SIM, T_transient=T_TRANSIENT,
                    seed=seed, record_r=True, r_downsample=200)
    rates = per_oscillator_rates(sim)
    K_c = sim.K_c

    # Real per-oscillator
    raw_real = parallel_classify(sim.spikes)
    real_rows = []
    for r in raw_real:
        i = r['i']
        real_rows.append(dict(
            K=K, K_factor=K / K_c, seed=seed, N=N,
            i=i, n_events=r['n_events'], rate=float(rates[i]),
            omega_i=float(sim.omegas[i]),
            primary=r['primary'], rep_med=r['rep_med'],
            ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
            quadrants_per_q=r.get('quadrants_per_q'),
            rep_int_per_q=r.get('rep_int_per_q'),
            ks_gue_per_q=r.get('ks_gue_per_q'),
            rf_amp_per_q=r.get('rf_amp_per_q'),
            rf_spike_per_q=r.get('rf_spike_per_q'),
        ))

    # Surrogate per-oscillator
    sur = rate_matched_poisson_surrogate(sim, seed=seed)
    raw_sur = parallel_classify(sur)
    sur_rows = []
    for r in raw_sur:
        i = r['i']
        sur_rows.append(dict(
            K=K, K_factor=K / K_c, seed=seed, N=N,
            i=i, n_events=r['n_events'],
            primary=r['primary'], rep_med=r['rep_med'],
            ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
            quadrants_per_q=r.get('quadrants_per_q'),
            rep_int_per_q=r.get('rep_int_per_q'),
            ks_gue_per_q=r.get('ks_gue_per_q'),
        ))

    # Recording-wide aggregate
    agg = aggregate_spikes(sim)
    if agg.size >= MIN_EVENTS_PER_Q:
        r_agg = classify(agg, return_full=True, q_max=Q_MAX)
        agg_cols = per_q_columns(r_agg['per_q'])
    else:
        r_agg = dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n_well=0, n_events_used=int(agg.size))
        agg_cols = dict(quadrants_per_q=None, rep_int_per_q=None,
                        ks_gue_per_q=None, rf_amp_per_q=None, rf_spike_per_q=None)

    # Stationarity check on the aggregate.  Always 4 windows; denser
    # 10-window check at K_factor in the boundary regime (per user
    # course-correction: critical slowing down at K≈K_c can produce
    # transient sync that the full-sequence statistic averages over).
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
        per_win = []
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
        K=K, K_factor=K_factor_val, seed=seed, N=N,
        n_events_total=int(agg.size),
        agg_primary=r_agg['primary'], agg_rep_med=r_agg['rep_med'],
        agg_ks_med=r_agg['ks_gue_med'], agg_n_well=r_agg['n_well'],
        order_param_mean=float(np.mean(sim.r_trace)),
        order_param_std=float(np.std(sim.r_trace)),
        rate_med=float(np.median(rates)),
        rate_min=float(rates.min()),
        rate_max=float(rates.max()),
        n_well_oscillators=int(sum(1 for r in raw_real if r['n_well'] > 0)),
        # Stationarity columns (prefixed `stat_`)
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
        **{f'agg_{k}': v for k, v in agg_cols.items()},
    )
    return real_rows, sur_rows, aggregate_row


def main():
    print("=" * 72)
    print("Phase 30 — Analysis 1: K-sweep on classical Kuramoto")
    print("=" * 72)
    K_c = critical_coupling(GAMMA)
    print(f"omega_0 = {OMEGA_0:.4f} rad/s ({OMEGA_0/(2*np.pi):.2f} Hz)")
    print(f"gamma   = {GAMMA:.4f} rad/s ({GAMMA/(2*np.pi):.2f} Hz HWHM)")
    print(f"K_c     = {K_c:.4f} rad/s")
    print(f"T_sim   = {T_SIM}s   T_transient = {T_TRANSIENT}s   dt = {DT}s")
    print(f"N       = {N_DEFAULT}   seeds = {SEEDS}   q_max = {Q_MAX}")
    print(f"K_factors = {K_FACTORS.tolist()}\n")

    real_all, sur_all, agg_all = [], [], []
    for K_factor in K_FACTORS:
        K = float(K_factor) * K_c
        for seed in SEEDS:
            t0 = time.time()
            real_rows, sur_rows, agg_row = run_one_cell(K, seed, N_DEFAULT)
            real_all.extend(real_rows)
            sur_all.extend(sur_rows)
            agg_all.append(agg_row)
            dt_wall = time.time() - t0
            print(
                f"  K={K_factor:.2f}*Kc seed={seed}  "
                f"⏱{dt_wall:5.1f}s  "
                f"|r|={agg_row['order_param_mean']:.3f}  "
                f"agg-prim={agg_row['agg_primary']:13s} "
                f"ks={agg_row['agg_ks_med']:.3f} rep={agg_row['agg_rep_med']:.3f}  "
                f"|  n_well_osc={agg_row['n_well_oscillators']}/{N_DEFAULT}"
            )

    df_real = pd.DataFrame(real_all)
    df_sur = pd.DataFrame(sur_all)
    df_agg = pd.DataFrame(agg_all)

    df_real.to_parquet(OUT_DIR / 'analysis1_per_oscillator_real.parquet',
                        index=False)
    df_sur.to_parquet(OUT_DIR / 'analysis1_per_oscillator_surrogate.parquet',
                       index=False)
    df_agg.to_parquet(OUT_DIR / 'analysis1_aggregate.parquet', index=False)
    print(f"\n  → analysis1_per_oscillator_real.parquet  ({len(df_real)} rows)")
    print(f"  → analysis1_per_oscillator_surrogate.parquet  ({len(df_sur)} rows)")
    print(f"  → analysis1_aggregate.parquet  ({len(df_agg)} rows)")

    # ─── per-K summary across seeds ───
    summary_rows = []
    for K_factor in K_FACTORS:
        sub_real = df_real[np.isclose(df_real['K_factor'], K_factor)]
        sub_sur = df_sur[np.isclose(df_sur['K_factor'], K_factor)]
        sub_agg = df_agg[np.isclose(df_agg['K_factor'], K_factor)]

        # Per-oscillator modal across all (seeds, oscillators)
        well_real = sub_real[sub_real['primary'] != 'underpowered']
        if len(well_real):
            modal_real = well_real['primary'].value_counts().idxmax()
            ks_real = float(well_real['ks_gue_med'].median())
            rep_real = float(well_real['rep_med'].median())
        else:
            modal_real, ks_real, rep_real = 'underpowered', np.nan, np.nan

        well_sur = sub_sur[sub_sur['primary'] != 'underpowered']
        if len(well_sur):
            modal_sur = well_sur['primary'].value_counts().idxmax()
            ks_sur = float(well_sur['ks_gue_med'].median())
            rep_sur = float(well_sur['rep_med'].median())
        else:
            modal_sur, ks_sur, rep_sur = 'underpowered', np.nan, np.nan

        modal_agg = sub_agg['agg_primary'].value_counts().idxmax() if len(sub_agg) else 'NA'
        ks_agg = float(sub_agg['agg_ks_med'].median())
        rep_agg = float(sub_agg['agg_rep_med'].median())

        summary_rows.append(dict(
            K_factor=float(K_factor),
            K=float(K_factor) * K_c,
            order_param_mean=float(sub_agg['order_param_mean'].mean()),
            order_param_std=float(sub_agg['order_param_mean'].std()),
            rate_med=float(sub_real['rate'].median()),
            n_seeds=int(sub_agg['seed'].nunique()),
            n_oscillators_total=int(len(sub_real)),
            n_well_real=int(len(well_real)),
            per_osc_modal_real=modal_real,
            per_osc_ks_med_real=ks_real,
            per_osc_rep_med_real=rep_real,
            per_osc_modal_sur=modal_sur,
            per_osc_ks_med_sur=ks_sur,
            per_osc_rep_med_sur=rep_sur,
            agg_modal=modal_agg,
            agg_ks_med=ks_agg,
            agg_rep_med=rep_agg,
        ))
    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_parquet(OUT_DIR / 'analysis1_summary_by_K.parquet', index=False)
    print(f"  → analysis1_summary_by_K.parquet  ({len(df_summary)} rows)\n")

    # ─── verdict ───
    # Heuristic: SENSIBLE if per-osc modal differs across {0, K_c, 2K_c}
    # OR if agg modal differs across them OR if rep_med trends with K_factor
    # by > 0.2 between K=0 and K=2K_c.
    print("Per-K summary (real per-osc | aggregate):")
    for _, r in df_summary.iterrows():
        print(
            f"  K={r['K_factor']:.1f}*Kc  "
            f"|r|={r['order_param_mean']:.3f}  "
            f"per-osc: {r['per_osc_modal_real']:13s} ks={r['per_osc_ks_med_real']:.3f} rep={r['per_osc_rep_med_real']:.3f}  "
            f"|  agg: {r['agg_modal']:13s} ks={r['agg_ks_med']:.3f} rep={r['agg_rep_med']:.3f}"
        )

    # Compute trend
    K0 = df_summary[df_summary['K_factor'] == 0.0].iloc[0]
    K2 = df_summary[df_summary['K_factor'] == 2.0].iloc[0]
    drep_per_osc = K2['per_osc_rep_med_real'] - K0['per_osc_rep_med_real']
    dks_per_osc = K2['per_osc_ks_med_real'] - K0['per_osc_ks_med_real']
    drep_agg = K2['agg_rep_med'] - K0['agg_rep_med']
    dks_agg = K2['agg_ks_med'] - K0['agg_ks_med']

    n_modal_per_osc = df_summary['per_osc_modal_real'].nunique()
    n_modal_agg = df_summary['agg_modal'].nunique()

    rate_max = float(df_summary['rate_med'].max())
    rate_min = float(df_summary['rate_med'].min())
    rate_drift = (rate_max - rate_min) / max(rate_min, 1e-9)

    sensible_per_osc = (n_modal_per_osc >= 2 or abs(drep_per_osc) > 0.2 or abs(dks_per_osc) > 0.2)
    sensible_agg = (n_modal_agg >= 2 or abs(drep_agg) > 0.2 or abs(dks_agg) > 0.2)
    sensible = sensible_per_osc or sensible_agg

    # Stationarity-based amendment per user course-correction.  Look at
    # per-window modal classifications at boundary K cells (K_c ± 0.2 K_c).
    # If full-sequence verdict is INSENSITIVE but per-window stationarity
    # fails at the critical band (fraction_modal < 0.9 or CV(rep) > 0.2),
    # promote to TIME-VARYING-AT-CRITICAL.
    boundary_agg = df_agg[
        (df_agg['K_factor'] >= BOUNDARY_K_RANGE[0]) &
        (df_agg['K_factor'] <= BOUNDARY_K_RANGE[1])
    ]
    n_nonstationary_boundary = int((~boundary_agg['stat_stationary'].astype(bool)).sum())
    n_total_boundary = int(len(boundary_agg))
    boundary_nonstationary_frac = (n_nonstationary_boundary / max(n_total_boundary, 1))

    if rate_drift > 0.3:
        verdict = 'RATE_REGIME_CONFOUNDED'
    elif sensible:
        modal_list = df_summary['per_osc_modal_real'].tolist()
        changes = sum(1 for a, b in zip(modal_list, modal_list[1:]) if a != b)
        verdict = 'SENSIBLE' if changes <= 4 else 'NON_MONOTONIC'
    elif boundary_nonstationary_frac >= 0.5:
        # Full-sequence is INSENSITIVE but the critical band is
        # non-stationary — slow critical fluctuations produce transient
        # synchronization that the full-sequence statistic averages over.
        verdict = 'TIME_VARYING_AT_CRITICAL'
    else:
        verdict = 'INSENSITIVE'

    summary = dict(
        verdict=verdict,
        n_K=len(K_FACTORS), n_seeds=len(SEEDS), N=N_DEFAULT,
        K_c=float(K_c), omega_0=float(OMEGA_0), gamma=float(GAMMA),
        T_sim=float(T_SIM), T_transient=float(T_TRANSIENT),
        n_modal_per_osc_distinct=int(n_modal_per_osc),
        n_modal_agg_distinct=int(n_modal_agg),
        delta_rep_per_osc=float(drep_per_osc),
        delta_ks_per_osc=float(dks_per_osc),
        delta_rep_agg=float(drep_agg),
        delta_ks_agg=float(dks_agg),
        rate_drift_fraction=float(rate_drift),
        K0_per_osc_modal=K0['per_osc_modal_real'],
        K0_agg_modal=K0['agg_modal'],
        Kc_per_osc_modal=df_summary[df_summary['K_factor'] == 1.0].iloc[0]['per_osc_modal_real'],
        Kc_agg_modal=df_summary[df_summary['K_factor'] == 1.0].iloc[0]['agg_modal'],
        K2_per_osc_modal=K2['per_osc_modal_real'],
        K2_agg_modal=K2['agg_modal'],
        # Stationarity diagnostics (user course-correction)
        n_windows_default=N_WINDOWS_DEFAULT,
        n_windows_boundary=N_WINDOWS_BOUNDARY,
        boundary_K_range=list(BOUNDARY_K_RANGE),
        boundary_nonstationary_frac=float(boundary_nonstationary_frac),
        n_nonstationary_boundary=int(n_nonstationary_boundary),
        n_total_boundary=int(n_total_boundary),
    )
    with open(OUT_DIR / 'analysis1_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → analysis1_verdict.json")
    print(f"\nVERDICT: {verdict}")
    print(f"  K=0  per-osc modal: {summary['K0_per_osc_modal']}  agg: {summary['K0_agg_modal']}")
    print(f"  K=Kc per-osc modal: {summary['Kc_per_osc_modal']}  agg: {summary['Kc_agg_modal']}")
    print(f"  K=2Kc per-osc modal: {summary['K2_per_osc_modal']}  agg: {summary['K2_agg_modal']}")
    print(f"  Δrep_per_osc = {drep_per_osc:+.3f}   Δks_per_osc = {dks_per_osc:+.3f}")
    print(f"  Δrep_agg     = {drep_agg:+.3f}     Δks_agg     = {dks_agg:+.3f}")
    print(f"  rate_drift_fraction = {rate_drift:.3f}")
    print(f"  boundary non-stationary cells: "
          f"{n_nonstationary_boundary}/{n_total_boundary} "
          f"({boundary_nonstationary_frac:.1%}) "
          f"[critical band {BOUNDARY_K_RANGE} K_factor]")


if __name__ == '__main__':
    main()
