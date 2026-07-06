"""
phase23/run_phase23_energy_strat.py — Phase 23 follow-up: energy-band
stratified targeted classification.

Activated only if the headline targeted analysis shows a non-trivial
real-vs-surrogate signature at the 909 Hz q-band (i.e., not a clean
substantive FAIL).  The Chen 2025 magnetar-central-engine
interpretation predicts the QPO should be energy-dependent; an
energy-band-stratified analysis would either support that prediction
(QPO signature is concentrated in a specific energy channel) or
falsify it (signature is energy-broad, more consistent with
instrument-level structure).

Splits GRB 230307A pooled events by energy_ch into two halves
(low / high), runs the same targeted-classification trajectory on
each half, and compares.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from run_phase23_targeted import (
    classify_subwindow, trajectory_classify, q_target_for,
    EVENT_NAME, TARGET_QPO_HZ, QPO_WINDOW_S, ANALYSIS_WINDOW_S,
    SUBWINDOW_S, Q_MAX, OUT_DIR, PANEL_DIR,
)


def main():
    print("=" * 80)
    print(f"Phase 23 follow-up — energy-band stratified targeted classification")
    print("=" * 80)
    p = PANEL_DIR / f'{EVENT_NAME}.parquet'
    df = pd.read_parquet(p, columns=['time_us', 'energy_ch'])
    print(f"  pooled events: {len(df):,}")
    print(f"  energy_ch range: {df['energy_ch'].min()}–{df['energy_ch'].max()}")
    print(f"  energy_ch median: {df['energy_ch'].median():.1f}")

    s_us = int(ANALYSIS_WINDOW_S[0] * 1e6)
    e_us = int(ANALYSIS_WINDOW_S[1] * 1e6)
    df_w = df[(df['time_us'] >= s_us) & (df['time_us'] < e_us)]
    print(f"  events in analysis window: {len(df_w):,}")

    # Energy-channel median split (simple binary low/high)
    median_ch = float(df_w['energy_ch'].median())
    low_mask = df_w['energy_ch'] <= median_ch
    high_mask = ~low_mask
    print(f"  median split at energy_ch={median_ch:.1f}: "
          f"{int(low_mask.sum()):,} low / {int(high_mask.sum()):,} high")
    print()

    rows = []
    for label, mask in [('low_energy', low_mask), ('high_energy', high_mask)]:
        events_us = df_w[mask]['time_us'].to_numpy()
        print(f"Classifying {label}-band sub-windows...")
        traj = trajectory_classify(events_us,
                                     ANALYSIS_WINDOW_S[0],
                                     ANALYSIS_WINDOW_S[1],
                                     label=label)
        traj.to_parquet(OUT_DIR / f'phase23_energy_{label}.parquet',
                         index=False)
        print(f"  → {OUT_DIR}/phase23_energy_{label}.parquet  ({len(traj)} rows)")
        # Per-sub-window q-band-of-interest extraction
        for _, r in traj.iterrows():
            if r['primary'] == 'underpowered': continue
            n_ev = int(r['n_events'])
            q_t = q_target_for(n_ev, SUBWINDOW_S, TARGET_QPO_HZ)
            if q_t < 2 or q_t > Q_MAX: continue
            q_idx = int(round(q_t)) - 1
            rep_at = (r['rep_int_q'][q_idx]
                       if r['rep_int_q'] is not None
                       and q_idx < len(r['rep_int_q']) else np.nan)
            rf_at = (r['rf_amplitude_q'][q_idx]
                       if r['rf_amplitude_q'] is not None
                       and q_idx < len(r['rf_amplitude_q']) else np.nan)
            rows.append(dict(
                energy_band=label, sub_start_s=r['sub_start_s'],
                sub_end_s=r['sub_end_s'], n_events=n_ev,
                q_target=q_t, q_used=q_idx + 1,
                rep_int_at_qpo_q=rep_at, rf_amp_at_qpo_q=rf_at,
                primary=r['primary'],
                in_qpo_window=bool(r['sub_start_s'] >= QPO_WINDOW_S[0]
                                     and r['sub_end_s'] <= QPO_WINDOW_S[1]),
            ))
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(OUT_DIR / 'phase23_energy_qpo_comparison.parquet',
                       index=False)
    print(f"  → {OUT_DIR}/phase23_energy_qpo_comparison.parquet  "
          f"({len(df_out)} rows)")
    print()
    # Per-band summary at the 909 Hz q-band
    for band in ['low_energy', 'high_energy']:
        sub = df_out[df_out['energy_band'] == band]
        sub_in = sub[sub['in_qpo_window']]
        sub_out = sub[~sub['in_qpo_window']]
        if not len(sub_in) or not len(sub_out): continue
        print(f"  {band}:")
        print(f"    inside  QPO window:  n={len(sub_in)}  "
              f"median rep={sub_in['rep_int_at_qpo_q'].median():.3f}")
        print(f"    outside QPO window:  n={len(sub_out)}  "
              f"median rep={sub_out['rep_int_at_qpo_q'].median():.3f}")
        delta = (float(sub_in['rep_int_at_qpo_q'].median()) -
                  float(sub_out['rep_int_at_qpo_q'].median()))
        print(f"    delta (in − out):    {delta:+.3f}")


if __name__ == '__main__':
    main()
