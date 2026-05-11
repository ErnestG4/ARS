"""
phase31b/pvc11_per_window_padic_all.py — apply p-adic v4 within each
non-overlapping window of all 12 pvc-11 recordings, all 6 primes.

User direction (2026-05-11): "Run p-adic v4 within each non-overlapping
window of the 12 pvc-11 recordings; report per-window dominant prime
stability."

The Phase 31b initial p=7 per-window stationarity test (4 recordings)
revealed that 3/4 strong full-recording p=7 signals are
PER_WINDOW_NULL.  This extends to all 12 pvc-11 recordings × all 6
primes to map the full stationarity landscape.

For each (recording, window, prime), compute:
  - real ratio
  - rate-matched-Poisson surrogate ratio (5 seeds)
  - z-score
  - above-1.5×-threshold flag

Per-recording per-prime stability verdicts:
  - PER_WINDOW_STATIONARY: z>2 in ≥ 4/5 windows
  - PER_WINDOW_MIXTURE: z>2 in 2-3/5 windows
  - PER_WINDOW_RARE: z>2 in 1/5
  - PER_WINDOW_NULL: z>2 in 0/5

Output:
  data/phase31b_results/pvc11_per_window_padic_all.parquet
  data/phase31b_results/pvc11_per_window_padic_verdict.json
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
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from loader import load
from population_events import build_unit_matrix, extract_events, BIN_MS_DEFAULT, K_THRESH_DEFAULT
from arithmetic_toolkit import padic_amplitude_v4

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
Q_MAX_HIGH = 200
N_SEEDS = 5
N_WINDOWS = 5
PRIMES = (2, 3, 5, 7, 11, 13)

RECORDINGS = [
    'monkey1_spontaneous', 'monkey2_spontaneous', 'monkey3_spontaneous',
    'monkey4_spontaneous', 'monkey5_spontaneous', 'monkey6_spontaneous',
    'monkey1_gratings', 'monkey2_gratings', 'monkey3_gratings',
    'monkey1_gratings_movie', 'monkey2_gratings_movie',
    'monkey1_natural_movie', 'monkey2_natural_movie',
    'monkey1_noise_movie', 'monkey2_noise_movie',
]


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def main():
    print("=" * 72)
    print("Phase 31b — pvc-11 all-recordings per-window p-adic v4 @ q_max=200")
    print("=" * 72)
    print(f"  N_windows = {N_WINDOWS}  N_seeds = {N_SEEDS}\n")

    all_rows = []
    verdicts = {}

    for rec_name in RECORDINGS:
        try:
            rec = load(rec_name)
            units = get_h2_units(rec_name)
            if not units:
                continue
            mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
            events = extract_events(mat, bin_ms=BIN_MS_DEFAULT,
                                      k_thresh=K_THRESH_DEFAULT)
        except Exception as e:
            print(f"\n[skip] {rec_name}: {e}")
            continue
        if events.size < 1000:
            print(f"\n[skip] {rec_name}: too few events ({events.size})")
            continue
        win_dur = total_dur / N_WINDOWS

        print(f"\n--- {rec_name} ({rec.subset}) ---")
        print(f"  n_events={events.size}  total_dur={total_dur:.0f}s  win_dur={win_dur:.0f}s")

        rec_per_window = []
        for w in range(N_WINDOWS):
            t0 = w * win_dur
            t1 = (w + 1) * win_dur
            win_events = events[(events >= t0) & (events < t1)] - t0
            if win_events.size < 100:
                continue
            pad = padic_amplitude_v4(win_events, q_max=Q_MAX_HIGH)
            sur_per_prime = {int(p): [] for p in PRIMES}
            for seed in range(N_SEEDS):
                rng = np.random.default_rng(seed + 12345)
                sur = np.sort(rng.uniform(0, win_dur, size=win_events.size))
                pad_sur = padic_amplitude_v4(sur, q_max=Q_MAX_HIGH)
                for p in PRIMES:
                    sur_per_prime[int(p)].append(
                        float(pad_sur['per_prime'][p]['normalised_per_q']))
            row = dict(
                recording=rec_name, subset=rec.subset, window_idx=w,
                n_events=int(win_events.size),
                t_start=float(t0), t_end=float(t1),
            )
            for p in PRIMES:
                real = float(pad['per_prime'][p]['normalised_per_q'])
                sur = np.asarray(sur_per_prime[int(p)])
                z = (real - sur.mean()) / max(sur.std(), 1e-6)
                row[f'real_p{p}'] = real
                row[f'sur_mean_p{p}'] = float(sur.mean())
                row[f'sur_std_p{p}'] = float(sur.std())
                row[f'z_p{p}'] = float(z)
                row[f'above_thr_p{p}'] = bool(real > 1.5)
            row['dominant_prime_per_q'] = int(pad['dominant_prime_per_q'])
            rec_per_window.append(row)
            all_rows.append(row)

        # Per-recording per-prime stability
        rec_verdict = {}
        for p in PRIMES:
            z_vals = [r[f'z_p{p}'] for r in rec_per_window]
            n_z2 = sum(1 for z in z_vals if z > 2)
            n_total = len(z_vals)
            if n_total < 1:
                continue
            mean_z = float(np.mean(z_vals))
            if n_z2 >= 4:
                v = 'PER_WINDOW_STATIONARY'
            elif n_z2 >= 2:
                v = 'PER_WINDOW_MIXTURE'
            elif n_z2 >= 1:
                v = 'PER_WINDOW_RARE'
            else:
                v = 'PER_WINDOW_NULL'
            rec_verdict[int(p)] = dict(
                verdict=v, n_z_gt_2=n_z2, n_total=n_total,
                mean_z=mean_z, z_values=z_vals,
            )
        # Dominant per-window prime stability
        doms = [r['dominant_prime_per_q'] for r in rec_per_window]
        unique_doms = pd.Series(doms).value_counts()
        modal_dom = int(unique_doms.idxmax())
        modal_dom_frac = float(unique_doms.max() / len(doms))
        rec_verdict['modal_dominant_prime'] = modal_dom
        rec_verdict['modal_dominant_fraction'] = modal_dom_frac
        rec_verdict['n_distinct_dominant_primes'] = int(len(unique_doms))

        verdicts[rec_name] = rec_verdict

        # Print compact per-recording summary
        print(f"  per-window dominant primes: {doms}  modal={modal_dom} ({modal_dom_frac:.0%})")
        stat_primes = [p for p in PRIMES if rec_verdict.get(int(p), {}).get('verdict') == 'PER_WINDOW_STATIONARY']
        mix_primes = [p for p in PRIMES if rec_verdict.get(int(p), {}).get('verdict') == 'PER_WINDOW_MIXTURE']
        rare_primes = [p for p in PRIMES if rec_verdict.get(int(p), {}).get('verdict') == 'PER_WINDOW_RARE']
        if stat_primes:
            print(f"  STATIONARY primes: {stat_primes}")
        if mix_primes:
            print(f"  MIXTURE primes:    {mix_primes}")
        if rare_primes:
            print(f"  RARE primes:       {rare_primes}")

    df = pd.DataFrame(all_rows)
    df.to_parquet(OUT_DIR / 'pvc11_per_window_padic_all.parquet', index=False)
    with open(OUT_DIR / 'pvc11_per_window_padic_verdict.json', 'w') as f:
        json.dump(verdicts, f, indent=2, default=str)
    print(f"\n  → pvc11_per_window_padic_all.parquet  ({len(df)} rows)")
    print(f"  → pvc11_per_window_padic_verdict.json")

    # Cross-recording summary: which primes are per-window-stationary in which subsets?
    print("\n=== Cross-recording per-prime stationarity summary ===")
    stationary_counts = {int(p): {'n_stationary': 0, 'n_mixture': 0,
                                      'n_rare': 0, 'n_null': 0}
                            for p in PRIMES}
    by_subset_stationary = {}
    for rec_name, v in verdicts.items():
        subset = next((r['subset'] for r in all_rows if r['recording'] == rec_name), '?')
        for p in PRIMES:
            pv = v.get(int(p), {})
            verdict_val = pv.get('verdict', 'PER_WINDOW_NULL')
            if verdict_val == 'PER_WINDOW_STATIONARY':
                stationary_counts[int(p)]['n_stationary'] += 1
            elif verdict_val == 'PER_WINDOW_MIXTURE':
                stationary_counts[int(p)]['n_mixture'] += 1
            elif verdict_val == 'PER_WINDOW_RARE':
                stationary_counts[int(p)]['n_rare'] += 1
            else:
                stationary_counts[int(p)]['n_null'] += 1
            by_subset_stationary.setdefault(subset, {}).setdefault(int(p), 0)
            if verdict_val == 'PER_WINDOW_STATIONARY':
                by_subset_stationary[subset][int(p)] += 1

    print("Per-prime stationarity counts (out of all pvc-11 recordings tested):")
    for p in PRIMES:
        s = stationary_counts[int(p)]
        print(f"  p={p:2d}  STAT: {s['n_stationary']:2d}  MIX: {s['n_mixture']:2d}  "
              f"RARE: {s['n_rare']:2d}  NULL: {s['n_null']:2d}")

    print("\nPer-subset PER_WINDOW_STATIONARY counts (by prime):")
    for subset, counts in by_subset_stationary.items():
        print(f"  {subset:20s}: " + " ".join(f"p={p}:{counts.get(int(p),0)}" for p in PRIMES))

    overall = dict(
        n_recordings=len(verdicts),
        n_total_cells=len(all_rows),
        stationary_counts_per_prime={int(p): stationary_counts[int(p)] for p in PRIMES},
        by_subset_stationary={k: {int(kk): vv for kk, vv in v.items()}
                                 for k, v in by_subset_stationary.items()},
    )
    with open(OUT_DIR / 'pvc11_per_window_padic_overall.json', 'w') as f:
        json.dump(overall, f, indent=2, default=str)
    print(f"\n  → pvc11_per_window_padic_overall.json")


if __name__ == '__main__':
    main()
