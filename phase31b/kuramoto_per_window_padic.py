"""
phase31b/kuramoto_per_window_padic.py — apply per-window p-adic v4 at
q_max=200 to Phase 30 Kuramoto simulations at representative K values.

Tests whether deterministic Kuramoto (which Phase 30 established is
inherently BR_artifact at every K) shows per-window p-adic structure
that the modal classification doesn't see, and how it compares to
Allen's per-window-rich natural_movie_one finding.

Simulates fresh at K_factors {0, K_c, 2*K_c}, N=100, seed=0.  Same
window scheme as pvc-11 / Allen per-window (5 windows).

Output:
  data/phase31b_results/kuramoto_per_window_padic.parquet
  data/phase31b_results/kuramoto_per_window_padic_verdict.json
"""
from __future__ import annotations

import os
import sys
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))

from kuramoto import simulate, critical_coupling, aggregate_spikes
from arithmetic_toolkit import padic_amplitude_v4

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
Q_MAX_HIGH = 200
N_SEEDS = 5
N_WINDOWS = 5
PRIMES = (2, 3, 5, 7, 11, 13)

OMEGA_0 = 2.0 * np.pi * 2.0
GAMMA = 2.0 * np.pi * 1.0
DT = 0.005
T_SIM = 1200.0
T_TRANSIENT = 200.0
N_OSC = 100
SEED = 0
K_FACTORS = [0.0, 1.0, 2.0]


def main():
    print("=" * 72)
    print("Phase 31b — Kuramoto per-window p-adic v4 @ q_max=200")
    print("=" * 72)
    K_c = critical_coupling(GAMMA)
    rows = []
    for kf in K_FACTORS:
        K = kf * K_c
        print(f"\n--- K_factor = {kf:.2f} ---")
        t0 = time.time()
        sim = simulate(K=K, sigma=0.0, N=N_OSC,
                        omega_0=OMEGA_0, gamma=GAMMA,
                        dt=DT, T_sim=T_SIM, T_transient=T_TRANSIENT,
                        seed=SEED, record_r=True, r_downsample=200)
        agg_events = aggregate_spikes(sim)
        # Kuramoto spike times are absolute (relative to t=0 of simulation),
        # not relative to T_transient.  Real events span [T_transient, T_sim].
        agg_events = agg_events - T_TRANSIENT
        post_dur = T_SIM - T_TRANSIENT
        print(f"  sim ⏱{time.time()-t0:.1f}s  |r|={np.mean(sim.r_trace):.3f}  "
              f"n_agg_events={agg_events.size}  post_dur={post_dur:.0f}s")
        win_dur = post_dur / N_WINDOWS

        # Per-window p-adic on aggregate
        for w in range(N_WINDOWS):
            t_w0 = w * win_dur
            t_w1 = (w + 1) * win_dur
            win_events = agg_events[(agg_events >= t_w0) & (agg_events < t_w1)] - t_w0
            if win_events.size < 100: continue
            pad = padic_amplitude_v4(win_events, q_max=Q_MAX_HIGH)
            sur_per_prime = {int(p): [] for p in PRIMES}
            for seed in range(N_SEEDS):
                rng = np.random.default_rng(seed + 12345)
                sur = np.sort(rng.uniform(0, win_dur, size=win_events.size))
                pad_sur = padic_amplitude_v4(sur, q_max=Q_MAX_HIGH)
                for p in PRIMES:
                    sur_per_prime[int(p)].append(
                        float(pad_sur['per_prime'][p]['normalised_per_q']))
            row = dict(K_factor=kf, K=float(K), window_idx=w,
                        n_events=int(win_events.size),
                        order_param=float(np.mean(sim.r_trace)))
            for p in PRIMES:
                real = float(pad['per_prime'][p]['normalised_per_q'])
                sur = np.asarray(sur_per_prime[int(p)])
                row[f'real_p{p}'] = real
                row[f'z_p{p}'] = float((real - sur.mean()) / max(sur.std(), 1e-6))
            row['dominant_prime_per_q'] = int(pad['dominant_prime_per_q'])
            rows.append(row)
            z_str = " ".join(f"p{p}={row[f'z_p{p}']:+.1f}" for p in PRIMES)
            print(f"  win {w}: n={win_events.size:6d}  dom={row['dominant_prime_per_q']:2d}  {z_str}")

        # Stationarity per prime
        K_rows = [r for r in rows if r['K_factor'] == kf]
        for p in PRIMES:
            z_vals = [r[f'z_p{p}'] for r in K_rows]
            n_z2 = sum(1 for z in z_vals if z > 2)
            if n_z2 >= 4: v = 'STATIONARY'
            elif n_z2 >= 2: v = 'MIXTURE'
            elif n_z2 >= 1: v = 'RARE'
            else: v = 'NULL'
            mean_z = float(np.mean(z_vals))
            if v != 'NULL':
                print(f"  >> p={p}: {v}  ({n_z2}/5 z>2, mean z={mean_z:+.2f})")

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'kuramoto_per_window_padic.parquet', index=False)
    print(f"\n  → kuramoto_per_window_padic.parquet  ({len(df)} rows)")

    print("\n=== Per-K_factor per-prime stationarity ===")
    for kf in K_FACTORS:
        K_rows = [r for r in rows if r['K_factor'] == kf]
        print(f"  K={kf:.1f}*Kc:")
        for p in PRIMES:
            z_vals = [r[f'z_p{p}'] for r in K_rows]
            n_z2 = sum(1 for z in z_vals if z > 2)
            print(f"    p={p:2d}  n z>2: {n_z2}/5  mean z: {np.mean(z_vals):+.2f}")


if __name__ == '__main__':
    main()
