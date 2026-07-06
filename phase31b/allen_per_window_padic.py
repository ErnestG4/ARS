"""
phase31b/allen_per_window_padic.py — Allen per-window p-adic v4 at
q_max=200 to test whether Allen's p=2 dominance is per-window-stable
or also full-recording-aggregation (as pvc-11 p=7 turned out to be).

3 representative Allen sessions (wt, Vip, Sst) × 3 conditions × 5
windows × 6 primes.

If Allen p=2 is PER_WINDOW_STATIONARY: the substrate-systematic
pvc-11-vs-Allen difference is per-window-real (pvc-11 has p=2 MIX,
Allen has p=2 STATIONARY in some recordings).
If Allen p=2 is also PER_WINDOW_NULL or MIXTURE: both substrates have
full-recording-aggregation p-adic signatures with per-window
non-stationarity.

Output:
  data/phase31b_results/allen_per_window_padic.parquet
  data/phase31b_results/allen_per_window_padic_verdict.json
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
    (732592105, 'wt'),
    (791319847, 'Vip'),
    (760693773, 'Sst'),
]
CONDITIONS = ['drifting_pooled', 'spontaneous', 'natural_movie_one']


def analyze(rec, session_id, condition, cre_line):
    try:
        chunks = chunks_for(rec, condition)
    except Exception as e:
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
        row = dict(
            session_id=session_id, cre_line=cre_line, condition=condition,
            window_idx=w, n_events=int(win_events.size),
            t_start=float(t0), t_end=float(t1),
        )
        for p in PRIMES:
            real = float(pad['per_prime'][p]['normalised_per_q'])
            sur = np.asarray(sur_per_prime[int(p)])
            z = (real - sur.mean()) / max(sur.std(), 1e-6)
            row[f'real_p{p}'] = real
            row[f'z_p{p}'] = float(z)
            row[f'above_thr_p{p}'] = bool(real > 1.5)
        row['dominant_prime_per_q'] = int(pad['dominant_prime_per_q'])
        rows.append(row)
    return rows


def main():
    print("=" * 72)
    print("Phase 31b — Allen per-window p-adic v4 @ q_max=200")
    print("=" * 72)

    all_rows = []
    verdicts = {}
    for session_id, cre_line in SESSIONS:
        print(f"\n=== Loading {session_id} ({cre_line}) ===")
        rec = load_session(session_id)
        for cond in CONDITIONS:
            rows = analyze(rec, session_id, cond, cre_line)
            if not rows: continue
            print(f"\n  {cond}:")
            for r in rows:
                z_str = " ".join(f"p{p}={r[f'z_p{p}']:+.1f}" for p in PRIMES)
                print(f"    win {r['window_idx']}: n={r['n_events']:5d}  dom={r['dominant_prime_per_q']:2d}  {z_str}")
            doms = [r['dominant_prime_per_q'] for r in rows]
            unique_doms = pd.Series(doms).value_counts()
            modal_dom = int(unique_doms.idxmax())
            modal_frac = float(unique_doms.max() / len(doms))
            # Per-prime stationarity within this session × condition
            per_prime = {}
            for p in PRIMES:
                z_vals = [r[f'z_p{p}'] for r in rows]
                n_z2 = sum(1 for z in z_vals if z > 2)
                if n_z2 >= 4: v = 'PER_WINDOW_STATIONARY'
                elif n_z2 >= 2: v = 'PER_WINDOW_MIXTURE'
                elif n_z2 >= 1: v = 'PER_WINDOW_RARE'
                else: v = 'PER_WINDOW_NULL'
                per_prime[int(p)] = dict(verdict=v, n_z_gt_2=n_z2,
                                           mean_z=float(np.mean(z_vals)))
            verdicts[f"{session_id}_{cond}"] = dict(
                cre_line=cre_line,
                modal_dom_prime=modal_dom, modal_dom_frac=modal_frac,
                per_prime=per_prime,
            )
            stat = [p for p, v in per_prime.items() if v['verdict'] == 'PER_WINDOW_STATIONARY']
            mix = [p for p, v in per_prime.items() if v['verdict'] == 'PER_WINDOW_MIXTURE']
            print(f"    dom prime modal: {modal_dom} ({modal_frac:.0%})  STAT: {stat}  MIX: {mix}")
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_parquet(OUT_DIR / 'allen_per_window_padic.parquet', index=False)
    with open(OUT_DIR / 'allen_per_window_padic_verdict.json', 'w') as f:
        json.dump(verdicts, f, indent=2, default=str)
    print(f"\n  → allen_per_window_padic.parquet  ({len(df)} rows)")
    print(f"  → allen_per_window_padic_verdict.json")

    print("\n=== Cross-Allen per-prime stationarity counts ===")
    counts = {int(p): {'STAT': 0, 'MIX': 0, 'RARE': 0, 'NULL': 0}
                for p in PRIMES}
    for k, v in verdicts.items():
        for p, pv in v['per_prime'].items():
            verdict_key = pv['verdict'].replace('PER_WINDOW_', '')
            counts[int(p)][verdict_key] += 1
    for p in PRIMES:
        c = counts[int(p)]
        print(f"  p={p:2d}  STAT: {c['STAT']:2d}  MIX: {c['MIX']:2d}  "
              f"RARE: {c['RARE']:2d}  NULL: {c['NULL']:2d}")


if __name__ == '__main__':
    main()
