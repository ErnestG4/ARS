"""
phase34b/run_stationarity.py — Sub-question 1 on the L(n) sign-change
sequence.

Two configurations:
  - cluster: 132 events in [906,150,257, 906,488,081].  10 windows
    leave ~13 events/window — below MIN_EVENTS_PER_Q (30).  Stationarity
    via phase30 module would flag all-underpowered; we drop to 4 windows
    (~33 events/window) for a meaningful stationarity-within-cluster
    check.
  - full: 133 events in [1, 10⁹], including the n=3 outlier — the
    cluster IS the only well-populated region, so full-sequence
    stationarity is structurally non-stationary by construction.
    Reported for transparency rather than as primary scope.

Output: data/phase34b_results/stationarity.json
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

from liouville_events import load_or_compute
from stationarity import classify_in_windows, stationarity_summary

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34b_results'

Q_MAX = 30
MIN_EVENTS_PER_Q = 30
CLUSTER_LO = 906150257
CLUSTER_HI = 906488081
CLUSTER_WIDTH = CLUSTER_HI - CLUSTER_LO + 1


def run_stationarity(events: np.ndarray, label: str,
                      n_windows: int, total_duration: float,
                      base: int = 0) -> dict:
    print(f"\n[{label}] n_events={events.size}, n_windows={n_windows}, "
          f"total_duration={total_duration:.0f}")
    ev = (events - base).astype(np.float64)
    per_window = classify_in_windows(ev, n_windows=n_windows,
                                       total_duration=total_duration,
                                       q_max=Q_MAX,
                                       min_events_per_q=MIN_EVENTS_PER_Q)
    summary = stationarity_summary(per_window)
    print(f"  {'win':>3}  {'t_start':>10}  {'t_end':>10}  {'n':>4}  "
          f"{'primary':<14}  {'rep_med':>8}  {'ks_gue_med':>10}")
    for w in per_window:
        rep = w['rep_med'] if w['rep_med'] is not None else float('nan')
        ks = w['ks_gue_med'] if w['ks_gue_med'] is not None else float('nan')
        print(f"  {w['window_idx']:>3}  {w['t_start']:>10.0f}  "
              f"{w['t_end']:>10.0f}  {w['n_events']:>4}  "
              f"{w['primary']:<14}  {rep:>8.3f}  {ks:>10.3f}")
    print(f"  modal: {summary['modal_window']}, "
          f"fraction_modal: {summary['fraction_modal']:.3f}, "
          f"stationary: {summary['stationary']}")
    return dict(per_window=[{k: (float(v) if isinstance(v, (np.floating, float))
                                  else int(v) if isinstance(v, (np.integer,
                                                                   bool, int))
                                  else v) for k, v in w.items()}
                              for w in per_window],
                 summary={k: (float(v) if isinstance(v, (np.floating, float))
                                else int(v) if isinstance(v, (np.integer, bool,
                                                                int))
                                else v) for k, v in summary.items()})


def main(N_MAX: int = 10**9) -> dict:
    print("=" * 72)
    print("Phase 34b Sub-question 1: stationarity on L(n) sign-changes")
    print("=" * 72)
    d = load_or_compute(N_MAX)
    sc = d['signchanges']
    cluster_mask = (sc >= CLUSTER_LO) & (sc <= CLUSTER_HI)
    cluster_events = sc[cluster_mask]
    print(f"  total events: {sc.size}")
    print(f"  cluster events [{CLUSTER_LO}, {CLUSTER_HI}]: "
          f"{cluster_events.size}")

    out = {
        'N_MAX': int(N_MAX),
        'cluster_lo': int(CLUSTER_LO),
        'cluster_hi': int(CLUSTER_HI),
    }
    # Primary: cluster, 4 windows (~33 events each)
    out['cluster_4_windows'] = run_stationarity(
        cluster_events, label='cluster [4 windows]',
        n_windows=4, total_duration=float(CLUSTER_WIDTH),
        base=CLUSTER_LO)
    # Robustness: cluster, 10 windows (~13 events each — likely all
    # underpowered, reported for transparency)
    out['cluster_10_windows'] = run_stationarity(
        cluster_events, label='cluster [10 windows]',
        n_windows=10, total_duration=float(CLUSTER_WIDTH),
        base=CLUSTER_LO)
    # Full-sequence 10-window: structurally non-stationary by design
    # (cluster + isolated n=3 outlier).
    out['full_10_windows'] = run_stationarity(
        sc, label='full [10 windows]',
        n_windows=10, total_duration=float(N_MAX),
        base=0)

    out_path = OUT_DIR / 'stationarity.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  → {out_path}")
    return out


if __name__ == '__main__':
    main()
