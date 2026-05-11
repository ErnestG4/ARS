"""
phase31b/allen_qmax200_padic.py — apply p-adic v4 at q_max=200 to
representative Allen sessions, testing whether p=7 enrichment crosses
species to mouse V1.

Phase 31b Follow-up 5 established p=7 as a class signal across all 3
pvc-11 gratings recordings.  Phase 31b pvc11_all_qmax200 extended:
p=7 present in spontaneous (6/6 above threshold, 2/6 z>2) and gratings
(3/3 above threshold), SUPPRESSED in movies (0/6 above threshold across
natural+gratings_movie+noise_movie).

This script tests cross-species:
  - 4 representative Allen sessions (wt × 2, Vip × 1, Sst × 1, Pvalb × 1)
  - Conditions: drifting_pooled + spontaneous (the pvc-11-positive
    conditions)
  - Apply padic_amplitude_v4 at q_max=200; surrogate via rate-matched
    Poisson, 5 seeds.

If p=7 is V1-intrinsic and cross-species: should show enrichment in
Allen spontaneous + drifting_gratings.
If pvc-11 species-specific: Allen should be null.
If gratings-stimulus-design-specific (Allen uses different gratings
schedule from pvc-11): Allen drifting_pooled may not match.

Output:
  data/phase31b_results/allen_qmax200_padic.parquet
  data/phase31b_results/allen_qmax200_padic_verdict.json
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
OUT_DIR.mkdir(parents=True, exist_ok=True)

Q_MAX_HIGH = 200
N_SEEDS = 5
PRIMES = (2, 3, 5, 7, 11, 13)
BIN_MS = 5.0
K_THRESH = 5

# Representative sessions (one per Cre line)
SESSIONS = [
    (732592105, 'wt'),
    (754312389, 'wt'),
    (791319847, 'Vip'),
    (760693773, 'Sst'),
    (797828357, 'Pvalb'),
]
CONDITIONS = ['drifting_pooled', 'spontaneous', 'natural_movie_one']


def analyze(rec, session_id, condition, cre_line):
    print(f"\n--- session {session_id} ({cre_line}) — {condition} ---")
    try:
        chunks = chunks_for(rec, condition)
    except Exception as e:
        print(f"  [skip] chunks_for error: {e}")
        return None
    if not chunks:
        print(f"  [skip] no chunks for {condition}")
        return None

    # Use all QC-passing V1 units in this session
    unit_ids = list(rec.units.index)
    if not unit_ids:
        print(f"  [skip] no QC-passing units")
        return None

    mat, total_dur, _ = build_unit_matrix_chunks(rec, unit_ids, chunks, BIN_MS)
    events = extract_events(mat, BIN_MS, K_THRESH)
    if events.size < 200:
        print(f"  [skip] too few events ({events.size})")
        return None
    rate = events.size / total_dur
    print(f"  n_units={len(unit_ids)}  n_events={events.size}  "
          f"rate={rate:.2f}Hz  dur={total_dur:.0f}s")

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
    above_thresh = {p: real_ratios[p] > 1.5 for p in PRIMES}

    dom_z = max(z_scores.items(), key=lambda kv: kv[1])
    print(f"  p=7: real={real_ratios[7]:.3f}  sur={sur_means[7]:.3f}±{sur_stds[7]:.3f}  z={z_scores[7]:+.2f}")
    print(f"  dominant by z: p={dom_z[0]} z={dom_z[1]:+.2f}")
    print(f"  above-thr: " + ", ".join(f"p={p}({real_ratios[p]:.2f})"
                                          for p in PRIMES if above_thresh[p]))

    return dict(
        session_id=session_id, cre_line=cre_line, condition=condition,
        n_units=len(unit_ids), n_events=int(events.size),
        rate_hz=float(rate), duration_sec=float(total_dur),
        **{f'real_p{p}': real_ratios[p] for p in PRIMES},
        **{f'sur_mean_p{p}': sur_means[p] for p in PRIMES},
        **{f'sur_std_p{p}': sur_stds[p] for p in PRIMES},
        **{f'z_p{p}': z_scores[p] for p in PRIMES},
        **{f'above_thr_p{p}': bool(above_thresh[p]) for p in PRIMES},
        dominant_prime_per_q=int(pad['dominant_prime_per_q']),
    )


def main():
    print("=" * 72)
    print("Phase 31b — Allen p-adic v4 @ q_max=200 (cross-species)")
    print("=" * 72)

    rows = []
    for session_id, cre_line in SESSIONS:
        print(f"\n=== Loading session {session_id} ({cre_line}) ===")
        t0 = time.time()
        try:
            rec = load_session(session_id)
        except Exception as e:
            print(f"  [error] load_session failed: {e}")
            continue
        print(f"  loaded in {time.time()-t0:.1f}s  n_units_qc_passing={rec.n_units_qc_passing}")
        for cond in CONDITIONS:
            row = analyze(rec, session_id, cond, cre_line)
            if row is not None:
                rows.append(row)

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'allen_qmax200_padic.parquet', index=False)
    print(f"\n  → allen_qmax200_padic.parquet  ({len(df)} rows)")

    # Per-condition aggregate
    print("\n=== Per-condition p=7 summary ===")
    by_cond = {}
    for cond, sub in df.groupby('condition'):
        n_above = int(sub['above_thr_p7'].sum())
        n_z2 = int((sub['z_p7'] > 2).sum())
        n_total = len(sub)
        mean_z = float(sub['z_p7'].mean())
        mean_ratio = float(sub['real_p7'].mean())
        print(f"  {cond:20s}: n={n_total}  above-1.5×: {n_above}/{n_total}  "
              f"z>2: {n_z2}/{n_total}  mean z={mean_z:+.2f}  mean ratio={mean_ratio:.2f}")
        by_cond[str(cond)] = dict(
            n=n_total, n_above_threshold=n_above, n_z_gt_2=n_z2,
            mean_z=mean_z, mean_ratio=mean_ratio,
        )

    # Verdict
    n_drift_z2 = by_cond.get('drifting_pooled', {}).get('n_z_gt_2', 0)
    n_drift_total = by_cond.get('drifting_pooled', {}).get('n', 0)
    n_spont_z2 = by_cond.get('spontaneous', {}).get('n_z_gt_2', 0)
    n_spont_total = by_cond.get('spontaneous', {}).get('n', 0)

    if (n_drift_z2 >= n_drift_total / 2 or n_spont_z2 >= n_spont_total / 2):
        verdict = 'P7_CROSS_SPECIES'
    elif n_drift_z2 == 0 and n_spont_z2 == 0:
        verdict = 'P7_PVC11_SPECIFIC'
    else:
        verdict = 'P7_CROSS_SPECIES_PARTIAL'

    summary = dict(
        verdict=verdict, by_condition=by_cond,
        n_sessions=len(SESSIONS), n_session_condition_cells=len(df),
    )
    with open(OUT_DIR / 'allen_qmax200_padic_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → allen_qmax200_padic_verdict.json")
    print(f"\nVERDICT (p=7 cross-species): {verdict}")


if __name__ == '__main__':
    main()
