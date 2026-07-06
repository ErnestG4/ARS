"""
phase31b/allen_per_window_remaining6.py — extend Allen per-window
p-adic to the remaining 6 of 12 Phase 24 sessions.

First batch (6 sessions): 732592105 wt, 791319847 Vip, 760693773 Sst,
762602078 Sst, 797828357 Pvalb, 755434585 Vip.

This batch (6 sessions): 754312389 wt, 754829445 wt, 755434585 [done — wait]

Actually the 6 done already are:
  732592105 (wt) — initial 3
  791319847 (Vip) — initial 3
  760693773 (Sst) — initial 3
  762602078 (Sst) — replication
  797828357 (Pvalb) — replication
  755434585 (Vip) — replication

Remaining 6:
  754312389 (wt)
  754829445 (wt)
  757216464 (wt)
  757970808 (wt)
  762120172 (Vip)
  798911424 (Vip)

Output:
  data/phase31b_results/allen_per_window_remaining6.parquet
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
    (754312389, 'wt'),
    (754829445, 'wt'),
    (757216464, 'wt'),
    (757970808, 'wt'),
    (762120172, 'Vip'),
    (798911424, 'Vip'),
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
    print("Phase 31b — Allen per-window p-adic remaining 6 sessions")
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
            mean_z7 = np.mean([r['z_p7'] for r in rows])
            mean_z2 = np.mean([r['z_p2'] for r in rows])
            n_p7_z2 = sum(1 for r in rows if r['z_p7'] > 2)
            n_p2_z2 = sum(1 for r in rows if r['z_p2'] > 2)
            print(f"  {cond:20s}  mean z(p=2)={mean_z2:+.2f} ({n_p2_z2}/5)  mean z(p=7)={mean_z7:+.2f} ({n_p7_z2}/5)")
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_parquet(OUT_DIR / 'allen_per_window_remaining6.parquet', index=False)
    print(f"\n  → allen_per_window_remaining6.parquet  ({len(df)} rows)")

    # Combine with previous Allen per-window data
    df1 = pd.read_parquet(OUT_DIR / 'allen_per_window_padic.parquet')
    df2 = pd.read_parquet(OUT_DIR / 'allen_per_window_sst_replication.parquet')
    common_cols = list(set(df1.columns) & set(df2.columns) & set(df.columns))
    full = pd.concat([df1[common_cols], df2[common_cols], df[common_cols]],
                      ignore_index=True)
    full.to_parquet(OUT_DIR / 'allen_per_window_all_12.parquet', index=False)
    print(f"  → allen_per_window_all_12.parquet  ({len(full)} rows)")

    print("\n=== Per-condition p=7 across all 12 Allen sessions ===")
    for cond, sub in full.groupby('condition'):
        z = sub['z_p7']
        n_z2 = (z > 2).sum()
        print(f"  {cond:20s}  n={len(sub)}  mean z={z.mean():+.3f}  z>2: {n_z2}/{len(sub)}")

    print("\n=== Per-cre-line × per-condition mean z(p=7) ===")
    pivot = full.pivot_table(values='z_p7', index='cre_line', columns='condition', aggfunc='mean')
    print(pivot.round(2).to_string())


if __name__ == '__main__':
    main()
