"""
phase31b/h2_stationarity_check.py — apply Phase 30 stationarity module
to the H2 surviving pvc-11 recordings (monkey1_natural_movie,
monkey2_gratings_movie).

The Phase 22a H2 finding is that the population-event NNS structure on
these two recordings survives the rate-matched / cell-shuffle / LN-evoked
surrogate battery at 30/30 q-bands × 7 surrogate seeds.  The surviving
structure is a full-sequence statistic.

This script tests whether that surviving structure is **time-stationary**
or whether the full-sequence average is masking hidden within-recording
variation.  Method: split the population-event train into 10
non-overlapping windows, classify each window separately, report per-
window primary classification + continuous metrics.

Verdict criteria (per Phase 31 stationarity module):
  - fraction_modal ≥ 0.90 across windows AND
  - CV(rep_med) ≤ 0.20 AND CV(ks_gue_med) ≤ 0.20 → STATIONARY
  - otherwise → TIME_VARYING

Output:
  data/phase31b_results/H2_stationarity_check.parquet
  data/phase31b_results/H2_stationarity_verdict.json
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
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))

from loader import load
from population_events import build_unit_matrix, extract_events, BIN_MS_DEFAULT, K_THRESH_DEFAULT
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q
from stationarity import classify_in_windows, stationarity_summary

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'

H2_RECORDINGS = ['monkey1_natural_movie', 'monkey2_gratings_movie']
N_WINDOWS = 10


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def main():
    print("=" * 72)
    print("Phase 31b — H2 stationarity check on pvc-11 surviving recordings")
    print("=" * 72)
    print(f"  N_windows = {N_WINDOWS}")

    results = {}
    all_window_rows = []
    for rec_name in H2_RECORDINGS:
        print(f"\n--- {rec_name} ---")
        rec = load(rec_name)
        units = get_h2_units(rec_name)
        mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
        events = extract_events(mat, bin_ms=BIN_MS_DEFAULT,
                                  k_thresh=K_THRESH_DEFAULT)
        print(f"  n_units(H2-passing)={len(units)}  n_events={events.size}  "
              f"rate={events.size/total_dur:.2f} Hz  dur={total_dur:.0f}s")

        # Full-sequence baseline
        t0 = time.time()
        full_cl = classify(events, return_full=False, q_max=Q_MAX,
                              min_events_per_q=MIN_EVENTS_PER_Q)
        print(f"  Full-sequence:  primary={full_cl['primary']}  "
              f"ks_gue_med={full_cl['ks_gue_med']:.4f}  "
              f"rep_med={full_cl['rep_med']:.4f}  ⏱{time.time()-t0:.1f}s")

        # Per-window
        per_win = classify_in_windows(events, n_windows=N_WINDOWS,
                                        total_duration=total_dur,
                                        q_max=Q_MAX,
                                        min_events_per_q=MIN_EVENTS_PER_Q)
        print(f"  Per-window classifications ({N_WINDOWS} windows):")
        for w in per_win:
            print(f"    win {w['window_idx']:2d}: t={w['t_start']:.0f}-{w['t_end']:.0f}s  "
                  f"n_events={w['n_events']:6d}  primary={w['primary']:13s}  "
                  f"ks={w['ks_gue_med']:.4f}  rep={w['rep_med']:.4f}")
            all_window_rows.append(dict(
                recording=rec_name, **w
            ))

        stat = stationarity_summary(per_win, full_sequence=full_cl)
        results[rec_name] = dict(
            full_primary=full_cl['primary'],
            full_ks_gue_med=full_cl['ks_gue_med'],
            full_rep_med=full_cl['rep_med'],
            stationarity=stat,
            n_events=int(events.size),
            total_duration=float(total_dur),
        )
        print(f"  Stationarity:")
        print(f"    modal across windows: {stat.get('modal_window')} ({stat.get('fraction_modal'):.1%})")
        print(f"    rep_med across windows: mean={stat.get('rep_med_across_windows_mean'):.4f}  "
              f"std={stat.get('rep_med_across_windows_std'):.4f}  "
              f"CV={stat.get('cv_rep_across_windows'):.3f}")
        print(f"    ks_gue_med across windows: mean={stat.get('ks_med_across_windows_mean'):.4f}  "
              f"std={stat.get('ks_med_across_windows_std'):.4f}  "
              f"CV={stat.get('cv_ks_across_windows'):.3f}")
        print(f"    STATIONARY: {stat.get('stationary')}  "
              f"agree-with-full: {stat.get('agree_with_full')}")

    df_windows = pd.DataFrame(all_window_rows)
    df_windows.to_parquet(OUT_DIR / 'H2_stationarity_check.parquet', index=False)
    print(f"\n  → H2_stationarity_check.parquet  ({len(df_windows)} rows)")

    # Aggregate verdict
    all_stationary = all(r['stationarity']['stationary'] for r in results.values())
    all_agree = all(r['stationarity']['agree_with_full'] for r in results.values())
    if all_stationary and all_agree:
        verdict = 'H2_STATIONARY'
    elif all_agree:
        verdict = 'H2_AGREES_WITH_FULL_BUT_NOT_STRICTLY_STATIONARY'
    else:
        verdict = 'H2_TIME_VARYING'

    summary = dict(
        verdict=verdict,
        n_windows=N_WINDOWS,
        recordings=results,
    )
    with open(OUT_DIR / 'H2_stationarity_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → H2_stationarity_verdict.json")
    print(f"\nVERDICT: {verdict}")


if __name__ == '__main__':
    main()
