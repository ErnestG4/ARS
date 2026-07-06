"""
phase30/pilot_analysis1.py — pilot for Analysis 1.

Per Phase 30 brief: "Pilot first.  Before full sweep, run at three K
values (K=0, K=K_c, K=2 K_c) with N=100 to verify the pipeline produces
interpretable classifications.  Adjust N, simulation duration, and any
other parameters based on pilot."

Verifies:
  1. Per-oscillator ARS classification (ks_gue_med, rep_med, primary
     quadrant) at K=0 lands near Poisson (BL); at K=2 K_c lands away
     from Poisson.
  2. Recording-wide aggregate ARS classification produces a sensible
     verdict at each K.
  3. Per-oscillator rate-matched Poisson surrogate at each K classifies
     near Poisson (sanity check on the surrogate).
  4. Tags whether N=100 is enough or N=200 is preferred for stability.

Output: stdout log + data/phase30_results/pilot_summary.parquet
"""
from __future__ import annotations

import os
import sys
import time
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
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q


N_WORKERS = min(16, cpu_count())


def _classify_one(args):
    """Top-level worker function for multiprocessing.Pool."""
    i, ev, q_max = args
    if ev.size < MIN_EVENTS_PER_Q:
        return dict(i=i, primary='underpowered', rep_med=np.nan,
                    ks_gue_med=np.nan, n_well=0, n_events=int(ev.size))
    r = classify(ev, return_full=False, q_max=q_max)
    return dict(i=i, primary=r['primary'], rep_med=r['rep_med'],
                ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
                n_events=int(ev.size))


def parallel_classify(events_list, q_max=Q_MAX, n_workers=N_WORKERS):
    """Parallel per-oscillator classify across a Pool."""
    args = [(i, ev, q_max) for i, ev in enumerate(events_list)]
    with Pool(n_workers) as pool:
        return list(pool.imap_unordered(_classify_one, args, chunksize=4))

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase30_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Default sim parameters (chosen so each oscillator gets ~2000+ events
# at the Lorentzian-bulk rate and the simulator runs in seconds, not
# minutes).  Smoke-tested in pre-pilot.
OMEGA_0 = 2.0 * np.pi * 2.0      # 2 Hz mean intrinsic frequency (rad/s)
GAMMA = 2.0 * np.pi * 1.0         # HWHM 1 Hz (rad/s)
DT = 0.005                         # 5 ms time step
T_SIM = 1200.0                     # 20 min simulated time
T_TRANSIENT = 200.0                # discard first ~3 min
SEED_BASE = 0


def run_one(K: float, N: int, sigma: float, seed: int) -> dict:
    """Simulate Kuramoto, classify each oscillator, classify aggregate,
    classify rate-matched Poisson surrogate.  Return summary dict."""
    sim = simulate(K=K, sigma=sigma, N=N,
                    omega_0=OMEGA_0, gamma=GAMMA,
                    dt=DT, T_sim=T_SIM, T_transient=T_TRANSIENT,
                    seed=seed)
    rates = per_oscillator_rates(sim)
    n_spikes = np.asarray([s.size for s in sim.spikes])

    # Per-oscillator ARS (parallel across the Pool)
    raw_po = parallel_classify(sim.spikes)
    per_osc = []
    for r in raw_po:
        per_osc.append(dict(
            i=r['i'], n_events=r['n_events'], rate=float(rates[r['i']]),
            primary=r['primary'], rep_med=r['rep_med'],
            ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
        ))
    df_po = pd.DataFrame(per_osc)

    # Modal classification across oscillators (ignore underpowered)
    well = df_po[df_po['primary'] != 'underpowered'].copy()
    if len(well) > 0:
        modal_per_osc = well['primary'].value_counts().idxmax()
        ks_med = float(well['ks_gue_med'].median())
        rep_med = float(well['rep_med'].median())
    else:
        modal_per_osc, ks_med, rep_med = 'underpowered', np.nan, np.nan

    # Recording-wide aggregate ARS
    agg = aggregate_spikes(sim)
    r_agg = classify(agg, return_full=False, q_max=Q_MAX)

    # Rate-matched Poisson surrogate per oscillator (parallel)
    sur = rate_matched_poisson_surrogate(sim, seed=seed)
    raw_sur = parallel_classify(sur)
    sur_per_osc = [
        dict(i=r['i'], primary=r['primary'], rep_med=r['rep_med'],
             ks_gue_med=r['ks_gue_med'])
        for r in raw_sur
    ]
    df_sur = pd.DataFrame(sur_per_osc)
    if len(df_sur) > 0:
        sur_well = df_sur[df_sur['primary'] != 'underpowered']
        sur_modal = (sur_well['primary'].value_counts().idxmax()
                      if len(sur_well) else 'underpowered')
        sur_ks = float(sur_well['ks_gue_med'].median()) if len(sur_well) else np.nan
        sur_rep = float(sur_well['rep_med'].median()) if len(sur_well) else np.nan
    else:
        sur_modal, sur_ks, sur_rep = 'underpowered', np.nan, np.nan

    r_mean = float(np.mean(sim.r_trace))
    return dict(
        K=K, K_c=sim.K_c, K_factor=K / sim.K_c,
        sigma=sigma, N=N, seed=seed,
        omega_0=OMEGA_0, gamma=GAMMA,
        T_sim=T_SIM, T_transient=T_TRANSIENT,
        n_oscillators=N,
        n_well_oscillators=int(len(well)),
        rate_med=float(np.median(rates)),
        rate_min=float(rates.min()),
        rate_max=float(rates.max()),
        n_spikes_med=int(np.median(n_spikes)),
        order_param_mean=r_mean,
        # Per-oscillator (modal across well-powered)
        per_osc_modal=modal_per_osc,
        per_osc_ks_med=ks_med,
        per_osc_rep_med=rep_med,
        # Recording-wide aggregate
        agg_n_events=int(agg.size),
        agg_primary=r_agg['primary'],
        agg_ks_med=r_agg['ks_gue_med'],
        agg_rep_med=r_agg['rep_med'],
        agg_n_well=r_agg['n_well'],
        # Surrogate per-oscillator (modal)
        sur_modal=sur_modal,
        sur_ks_med=sur_ks,
        sur_rep_med=sur_rep,
    )


def main():
    print("=" * 72)
    print("Phase 30 — Pilot for Analysis 1 (Kuramoto K-sweep)")
    print("=" * 72)
    print(f"omega_0 = {OMEGA_0:.4f} rad/s ({OMEGA_0/(2*np.pi):.2f} Hz)")
    print(f"gamma   = {GAMMA:.4f} rad/s ({GAMMA/(2*np.pi):.2f} Hz HWHM)")
    print(f"K_c     = {critical_coupling(GAMMA):.4f} rad/s")
    print(f"T_sim   = {T_SIM}s   T_transient = {T_TRANSIENT}s   dt = {DT}s\n")

    rows = []
    for N in (100, 200):
        for K_factor in (0.0, 1.0, 2.0):
            K = K_factor * critical_coupling(GAMMA)
            t0 = time.time()
            r = run_one(K=K, N=N, sigma=0.0, seed=SEED_BASE)
            dt_wall = time.time() - t0
            rows.append(r)
            print(
                f"  N={N:3d}  K={K_factor:.1f}*Kc  ⏱{dt_wall:5.1f}s  "
                f"|r|={r['order_param_mean']:.3f}  "
                f"per-osc-modal={r['per_osc_modal']:13s}  "
                f"ks={r['per_osc_ks_med']:.3f}  rep={r['per_osc_rep_med']:.3f}  "
                f"|  agg-prim={r['agg_primary']:13s} "
                f"ks={r['agg_ks_med']:.3f}  rep={r['agg_rep_med']:.3f}  "
                f"|  sur-modal={r['sur_modal']:13s}"
            )

    df = pd.DataFrame(rows)
    out = OUT_DIR / 'pilot_summary.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(df)} rows)")

    print("\n--- Pilot interpretation ---")
    for K_factor in (0.0, 1.0, 2.0):
        sub = df[np.isclose(df['K_factor'], K_factor)]
        if not len(sub):
            continue
        N100 = sub[sub['N'] == 100].iloc[0]
        N200 = sub[sub['N'] == 200].iloc[0]
        print(f"  K={K_factor:.1f}*Kc  per-osc-modal: N=100 → {N100['per_osc_modal']}  "
              f"N=200 → {N200['per_osc_modal']}  "
              f"agg: N=100 → {N100['agg_primary']}  N=200 → {N200['agg_primary']}")


if __name__ == '__main__':
    main()
