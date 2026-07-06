"""
phase31b/allen_per_window_sst_replication.py — replicate the
session-760693773-Sst-natural_movie_one PER_WINDOW_STATIONARY p=7
finding on the second Sst session and Pvalb session to test whether
the per-window p=7 enrichment in Allen is Sst-specific or more general.

3 additional sessions:
  - 762602078 (Sst) — second Sst session
  - 797828357 (Pvalb) — already in Allen full 12-session but not in
    per-window first run
  - 755434585 (Vip)  — second Vip session

Output:
  data/phase31b_results/allen_per_window_sst_replication.parquet
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
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase24'))

from loader import load_session
from run_per_session_h2 import (
    build_unit_matrix_chunks, extract_events, chunks_for,
)
from arithmetic_toolkit import padic_amplitude_v4

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
Q_MAX_HIGH = 200
N_SEEDS = 5
N_WINDOWS = 5
PRIMES = (2, 3, 5, 7, 11, 13)
BIN_MS = 5.0
K_THRESH = 5

SESSIONS = [
    (762602078, 'Sst'),
    (797828357, 'Pvalb'),
    (755434585, 'Vip'),
]
CONDITIONS = ['drifting_pooled', 'spontaneous', 'natural_movie_one']


def analyze(rec, session_id, condition, cre_line):
    try:
        chunks = chunks_for(rec, condition)
    except Exception:
        return []
    if not chunks: return []
    unit_ids = list(rec.units.index)
    if not unit_ids: return []
    mat, total_dur, _ = build_unit_matrix_chunks(rec, unit_ids, chunks, BIN_MS)
    events = extract_events(mat, BIN_MS, K_THRESH)
    if events.size < 1000: return []
    win_dur = total_dur / N_WINDOWS
    rows = []
    for w in range(N_WINDOWS):
        t0 = w * win_dur
        t1 = (w + 1) * win_dur
        win_events = events[(events >= t0) & (events < t1)] - t0
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
        row = dict(session_id=session_id, cre_line=cre_line, condition=condition,
                    window_idx=w, n_events=int(win_events.size))
        for p in PRIMES:
            real = float(pad['per_prime'][p]['normalised_per_q'])
            sur = np.asarray(sur_per_prime[int(p)])
            row[f'real_p{p}'] = real
            row[f'z_p{p}'] = float((real - sur.mean()) / max(sur.std(), 1e-6))
        row['dominant_prime_per_q'] = int(pad['dominant_prime_per_q'])
        rows.append(row)
    return rows


def main():
    print("=" * 72)
    print("Phase 31b — Allen per-window p-adic Sst-replication (3 sessions)")
    print("=" * 72)

    all_rows = []
    for session_id, cre_line in SESSIONS:
        print(f"\n=== Loading {session_id} ({cre_line}) ===")
        try:
            rec = load_session(session_id)
        except Exception as e:
            print(f"  [error] {e}")
            continue
        for cond in CONDITIONS:
            rows = analyze(rec, session_id, cond, cre_line)
            if not rows: continue
            print(f"\n  {cond}:")
            for r in rows:
                z_str = " ".join(f"p{p}={r[f'z_p{p}']:+.1f}" for p in PRIMES)
                print(f"    win {r['window_idx']}: n={r['n_events']:5d}  dom={r['dominant_prime_per_q']:2d}  {z_str}")
            # Quick stationarity assessment per prime
            for p in PRIMES:
                z_vals = [r[f'z_p{p}'] for r in rows]
                n_z2 = sum(1 for z in z_vals if z > 2)
                if n_z2 >= 4:
                    print(f"    >> p={p}: PER_WINDOW_STATIONARY ({n_z2}/5 z>2)")
                elif n_z2 >= 2:
                    print(f"    >> p={p}: PER_WINDOW_MIXTURE ({n_z2}/5 z>2)")
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_parquet(OUT_DIR / 'allen_per_window_sst_replication.parquet', index=False)
    print(f"\n  → allen_per_window_sst_replication.parquet  ({len(df)} rows)")

    # Combined summary: original 3 + this 3 = 6 sessions
    orig = pd.read_parquet(OUT_DIR / 'allen_per_window_padic.parquet')
    orig['session_id'] = orig['session_id'].astype(int)
    df['session_id'] = df['session_id'].astype(int)
    combined = pd.concat([orig, df], ignore_index=True)
    # combine on common cols only
    common_cols = list(set(orig.columns) & set(df.columns))
    combined = pd.concat([orig[common_cols], df[common_cols]], ignore_index=True)
    combined.to_parquet(OUT_DIR / 'allen_per_window_padic_combined.parquet',
                          index=False)
    print(f"\n  Combined (6 Allen sessions, 90 cells): {len(combined)}")

    # Per-condition mean z(p=7) across all 6 sessions
    print("\n=== Per-condition mean z(p=7) across 6 Allen sessions ===")
    for cond, sub in combined.groupby('condition'):
        z = sub['z_p7']
        n_z2 = (z > 2).sum()
        print(f"  {cond:20s}  n={len(sub)}  mean z={z.mean():+.3f}  z>2: {n_z2}/{len(sub)}")

    # Per-cre-line mean z(p=7)
    print("\n=== Per-cre-line × per-condition mean z(p=7) ===")
    pivot = combined.pivot_table(values='z_p7', index='cre_line',
                                   columns='condition', aggfunc='mean')
    print(pivot.round(2).to_string())


if __name__ == '__main__':
    main()
