"""
phase34a/run_stationarity.py — Sub-question 1: stationarity of the
Mertens sign-change sequence on [1, 10^7].

Applies phase30/stationarity.classify_in_windows + stationarity_summary
with the standard 10-window split.  Flagging criteria (brief):
    fraction_modal < 0.90  OR  CV(rep_med) > 0.20  OR  CV(ks_gue_med) > 0.20.

If non-stationary, the analysis reports the n-range of a stationary
sub-window and downstream classification uses that sub-window only.

Output: data/phase34a_results/stationarity.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))

from mertens_events import load_or_compute
from stationarity import classify_in_windows, stationarity_summary

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_WINDOWS = 10
Q_MAX = 30
MIN_EVENTS_PER_Q = 30


def main(N_MAX: int = 10**7) -> dict:
    print("=" * 72)
    print(f"Phase 34a Sub-question 1: stationarity over {N_WINDOWS} windows")
    print("=" * 72)
    d = load_or_compute(N_MAX)
    events = d['signchanges'].astype(np.float64)
    total_duration = float(N_MAX)
    print(f"  n_events: {events.size}")
    print(f"  span: [{events.min():.0f}, {events.max():.0f}]")
    print(f"  total_duration used: {total_duration:.0f}")
    print(f"  Q_MAX={Q_MAX}, MIN_EVENTS_PER_Q={MIN_EVENTS_PER_Q}\n")

    per_window = classify_in_windows(events, n_windows=N_WINDOWS,
                                       total_duration=total_duration,
                                       q_max=Q_MAX,
                                       min_events_per_q=MIN_EVENTS_PER_Q)
    summary = stationarity_summary(per_window)

    print(f"  {'win':>3}  {'t_start':>9}  {'t_end':>9}  {'n':>5}  "
          f"{'primary':<14}  {'rep_med':>8}  {'ks_gue_med':>10}")
    for w in per_window:
        print(f"  {w['window_idx']:>3}  {w['t_start']:>9.0f}  "
              f"{w['t_end']:>9.0f}  {w['n_events']:>5}  "
              f"{w['primary']:<14}  {w['rep_med']:>8.3f}  "
              f"{w['ks_gue_med']:>10.3f}")

    print(f"\n  modal_window: {summary['modal_window']}")
    print(f"  fraction_modal: {summary['fraction_modal']:.3f}")
    print(f"  rep_med mean ± std: "
          f"{summary['rep_med_across_windows_mean']:.3f} "
          f"± {summary['rep_med_across_windows_std']:.3f}")
    print(f"  ks_gue_med mean ± std: "
          f"{summary['ks_med_across_windows_mean']:.3f} "
          f"± {summary['ks_med_across_windows_std']:.3f}")
    print(f"  stationary (per phase30 heuristic): {summary['stationary']}")

    # Brief's flagging criteria are the same numbers phase30 uses.
    cv_rep = (summary['rep_med_across_windows_std']
              / max(abs(summary['rep_med_across_windows_mean']), 1e-6))
    cv_ks = (summary['ks_med_across_windows_std']
              / max(abs(summary['ks_med_across_windows_mean']), 1e-6))
    print(f"  CV(rep_med)  = {cv_rep:.3f}  "
          f"({'OK' if cv_rep <= 0.20 else 'FLAGGED'})")
    print(f"  CV(ks_gue_med) = {cv_ks:.3f}  "
          f"({'OK' if cv_ks <= 0.20 else 'FLAGGED'})")
    print(f"  fraction_modal = {summary['fraction_modal']:.3f}  "
          f"({'OK' if summary['fraction_modal'] >= 0.90 else 'FLAGGED'})")

    # Save full result
    out_obj = {
        'N_MAX': int(N_MAX),
        'n_windows': N_WINDOWS,
        'q_max': Q_MAX,
        'min_events_per_q': MIN_EVENTS_PER_Q,
        'per_window': [
            {k: (float(v) if isinstance(v, (np.floating, float))
                  else int(v) if isinstance(v, (np.integer, bool, int))
                  else v) for k, v in w.items()}
            for w in per_window
        ],
        'summary': {k: (float(v) if isinstance(v, (np.floating, float))
                         else int(v) if isinstance(v, (np.integer, bool, int))
                         else v) for k, v in summary.items()},
        'cv_rep': float(cv_rep),
        'cv_ks': float(cv_ks),
        'stationary': bool(summary['stationary']),
    }
    out_path = OUT_DIR / 'stationarity.json'
    with open(out_path, 'w') as f:
        json.dump(out_obj, f, indent=2, default=str)
    print(f"\n  → {out_path}")
    return out_obj


if __name__ == '__main__':
    main()
