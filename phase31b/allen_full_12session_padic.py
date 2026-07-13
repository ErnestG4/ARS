"""
phase31b/allen_full_12session_padic.py — extend the 5-session Allen
p-adic v4 q_max=200 test to all 12 Phase 24 sessions × 3 conditions.

Strengthens the P7_PVC11_SPECIFIC verdict and characterizes Allen's
substrate-systematic prime preference if any.

Output:
  data/phase31b_results/allen_full_12session_padic.parquet
  data/phase31b_results/allen_full_12session_verdict.json
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
PRIMES = (2, 3, 5, 7, 11, 13)
BIN_MS = 5.0
K_THRESH = 5
CONDITIONS = ['drifting_pooled', 'spontaneous', 'natural_movie_one']

# All 12 Phase 24 sessions
CANDIDATE_CSV = Path(os.path.expandvars(os.path.expanduser("$HOME/fmexplorer/allen_cache/phase24_candidate_sessions.csv")))


def analyze(rec, session_id, condition, cre_line):
    try:
        chunks = chunks_for(rec, condition)
    except Exception as e:
        return None
    if not chunks:
        return None
    unit_ids = list(rec.units.index)
    if not unit_ids:
        return None
    mat, total_dur, _ = build_unit_matrix_chunks(rec, unit_ids, chunks, BIN_MS)
    events = extract_events(mat, BIN_MS, K_THRESH)
    if events.size < 200:
        return None

    pad = padic_amplitude_v4(events, q_max=Q_MAX_HIGH)
    real_ratios = {int(p): float(pad['per_prime'][p]['normalised_per_q'])
                     for p in PRIMES}
    sur_ratios = {int(p): [] for p in PRIMES}
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 12345)
        sur_events = np.sort(rng.uniform(0, total_dur, size=events.size))
        pad_sur = padic_amplitude_v4(sur_events, q_max=Q_MAX_HIGH)
        for p in PRIMES:
            sur_ratios[int(p)].append(
                float(pad_sur['per_prime'][p]['normalised_per_q']))
    sur_means = {p: float(np.mean(v)) for p, v in sur_ratios.items()}
    sur_stds = {p: float(np.std(v)) for p, v in sur_ratios.items()}
    z_scores = {p: (real_ratios[p] - sur_means[p]) / max(sur_stds[p], 1e-6)
                 for p in PRIMES}
    return dict(
        session_id=session_id, cre_line=cre_line, condition=condition,
        n_units=len(unit_ids), n_events=int(events.size),
        rate_hz=float(events.size / total_dur),
        duration_sec=float(total_dur),
        **{f'real_p{p}': real_ratios[p] for p in PRIMES},
        **{f'sur_mean_p{p}': sur_means[p] for p in PRIMES},
        **{f'z_p{p}': z_scores[p] for p in PRIMES},
        **{f'above_thr_p{p}': bool(real_ratios[p] > 1.5) for p in PRIMES},
        dominant_prime_per_q=int(pad['dominant_prime_per_q']),
    )


def main():
    print("=" * 72)
    print("Phase 31b — Allen full 12-session p-adic v4 @ q_max=200")
    print("=" * 72)

    cand = pd.read_csv(CANDIDATE_CSV)
    sessions = list(zip(cand['ecephys_session_id'].astype(int),
                          cand['cre_line']))
    print(f"  {len(sessions)} candidate sessions")

    rows = []
    for session_id, cre_line in sessions:
        print(f"\n=== Session {session_id} ({cre_line}) ===")
        t0 = time.time()
        try:
            rec = load_session(session_id)
        except Exception as e:
            print(f"  [error] load failed: {e}")
            continue
        print(f"  loaded {time.time()-t0:.0f}s  n_units_qc={rec.n_units_qc_passing}")
        for cond in CONDITIONS:
            row = analyze(rec, session_id, cond, cre_line)
            if row is not None:
                rows.append(row)
                p7_z = row['z_p7']
                marker = ' ✓z>2' if p7_z > 2 else ''
                print(f"  {cond:20s}: p7 z={p7_z:+.2f}  ratio={row['real_p7']:.2f}  "
                      f"dom={row['dominant_prime_per_q']}{marker}")

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'allen_full_12session_padic.parquet', index=False)
    print(f"\n  → allen_full_12session_padic.parquet  ({len(df)} rows)")

    # Per-condition summary
    print("\n=== Per-condition p=7 summary (full 12-session) ===")
    by_cond = {}
    for cond, sub in df.groupby('condition'):
        n_above = int(sub['above_thr_p7'].sum())
        n_z2 = int((sub['z_p7'] > 2).sum())
        n_total = len(sub)
        mean_z = float(sub['z_p7'].mean())
        mean_ratio = float(sub['real_p7'].mean())
        print(f"  {cond:20s}: n={n_total}  above-1.5×: {n_above}/{n_total}  "
              f"z>2: {n_z2}/{n_total}  mean z={mean_z:+.2f}  ratio={mean_ratio:.2f}")
        by_cond[cond] = dict(n=n_total, n_above=n_above, n_z_gt_2=n_z2,
                              mean_z=mean_z, mean_ratio=mean_ratio)

    # Per-prime dominance distribution
    print("\n=== Dominant prime distribution (all conditions) ===")
    print(df['dominant_prime_per_q'].value_counts().to_string())

    # Substrate-systematic prime check: which primes have mean z > 0 across Allen?
    print("\n=== Per-prime mean z across Allen (sign indicates substrate preference) ===")
    for p in PRIMES:
        col = f'z_p{p}'
        mean_z = float(df[col].mean())
        n_z2 = int((df[col] > 2).sum())
        print(f"  p={p:2d}  mean z={mean_z:+.3f}  n z>2: {n_z2}/{len(df)}")

    verdict = 'P7_PVC11_SPECIFIC_CONFIRMED' \
        if by_cond.get('spontaneous', {}).get('mean_z', 0) < 0 else \
        'P7_PARTIAL_CROSS_SPECIES'

    summary = dict(
        verdict=verdict,
        n_sessions_loaded=df['session_id'].nunique(),
        n_session_condition_cells=len(df),
        by_condition=by_cond,
        per_prime_mean_z={int(p): float(df[f'z_p{p}'].mean()) for p in PRIMES},
    )
    with open(OUT_DIR / 'allen_full_12session_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → allen_full_12session_verdict.json")
    print(f"\nVERDICT: {verdict}")


if __name__ == '__main__':
    main()
