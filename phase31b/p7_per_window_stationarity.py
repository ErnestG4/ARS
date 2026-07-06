"""
phase31b/p7_per_window_stationarity.py — per-window p=7 stationarity
check on the strongest pvc-11 p=7 signals.

The cross-finding correlation analysis identified monkey1_gratings
z=+9.77 and monkey4_spontaneous z=+6.09 as the strongest p=7 signals.
This script tests whether those signals are time-stationary or
burst-driven:

  1. Split each recording's population events into 5 non-overlapping
     windows.
  2. Compute padic_amplitude_v4 per window at q_max=200.
  3. Generate rate-matched-Poisson surrogate per window (5 seeds).
  4. Report per-window p=7 z-score.

If z>2 in ≥ 4/5 windows → per-window-stationary p=7 signal.  Strengthens
the class signal claim.

Output:
  data/phase31b_results/p7_per_window_stationarity.parquet
  data/phase31b_results/p7_per_window_stationarity_verdict.json
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
N_WINDOWS = 5    # fewer than 10 since q_max=200 needs more events
RECORDINGS = [
    ('monkey1_gratings', 'strongest gratings z=+9.77'),
    ('monkey4_spontaneous', 'strongest spontaneous z=+6.09'),
    ('monkey3_spontaneous', 'second spontaneous z=+2.93'),
    ('monkey1_spontaneous', 'third spontaneous z=+1.91'),
]


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def analyze_window(events, total_dur):
    if events.size < 200:
        return None
    pad = padic_amplitude_v4(events, q_max=Q_MAX_HIGH)
    sur_p7 = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 12345)
        sur = np.sort(rng.uniform(0, total_dur, size=events.size))
        pad_sur = padic_amplitude_v4(sur, q_max=Q_MAX_HIGH)
        sur_p7.append(pad_sur['per_prime'][7]['normalised_per_q'])
    sur_p7 = np.asarray(sur_p7)
    real_p7 = pad['per_prime'][7]['normalised_per_q']
    z = (real_p7 - sur_p7.mean()) / max(sur_p7.std(), 1e-6)
    return dict(n_events=int(events.size),
                 real_p7=float(real_p7),
                 sur_p7_mean=float(sur_p7.mean()),
                 sur_p7_std=float(sur_p7.std()),
                 z_p7=float(z))


def main():
    print("=" * 72)
    print("Phase 31b — p=7 per-window stationarity")
    print("=" * 72)

    rows = []
    verdicts = {}
    for rec_name, note in RECORDINGS:
        print(f"\n--- {rec_name} ({note}) ---")
        rec = load(rec_name)
        units = get_h2_units(rec_name)
        mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
        events = extract_events(mat, bin_ms=BIN_MS_DEFAULT, k_thresh=K_THRESH_DEFAULT)
        win_dur = total_dur / N_WINDOWS
        print(f"  total: n_events={events.size}  dur={total_dur:.0f}s  rate={events.size/total_dur:.2f}Hz")
        print(f"  per-window duration: {win_dur:.0f}s")

        per_window = []
        for w in range(N_WINDOWS):
            t0 = w * win_dur
            t1 = (w + 1) * win_dur
            win_events = events[(events >= t0) & (events < t1)] - t0
            r = analyze_window(win_events, win_dur)
            if r is None:
                print(f"  win {w}: too few events ({win_events.size})")
                continue
            print(f"  win {w}: n={r['n_events']:5d}  real p7={r['real_p7']:.3f}  "
                  f"sur={r['sur_p7_mean']:.3f}±{r['sur_p7_std']:.3f}  "
                  f"z={r['z_p7']:+.2f}  {'✓z>2' if r['z_p7'] > 2 else ''}")
            r['recording'] = rec_name
            r['window_idx'] = w
            r['t_start'] = float(t0)
            r['t_end'] = float(t1)
            per_window.append(r)
            rows.append(r)

        # Verdict per recording
        n_z2 = sum(1 for r in per_window if r['z_p7'] > 2)
        n_total = len(per_window)
        mean_z = float(np.mean([r['z_p7'] for r in per_window])) if per_window else np.nan
        if n_z2 >= 4:
            verdict = 'PER_WINDOW_STATIONARY_P7'
        elif n_z2 >= 2:
            verdict = 'PER_WINDOW_MIXTURE_P7'
        elif n_z2 >= 1:
            verdict = 'PER_WINDOW_RARE_P7'
        else:
            verdict = 'PER_WINDOW_NULL_P7'
        verdicts[rec_name] = dict(
            verdict=verdict, n_z_gt_2=n_z2, n_total=n_total,
            mean_z=mean_z,
            per_window_z=[r['z_p7'] for r in per_window],
        )
        print(f"  → {verdict}  ({n_z2}/{n_total} windows z>2)  mean z={mean_z:+.2f}")

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'p7_per_window_stationarity.parquet', index=False)
    with open(OUT_DIR / 'p7_per_window_stationarity_verdict.json', 'w') as f:
        json.dump(verdicts, f, indent=2, default=str)
    print(f"\n  → p7_per_window_stationarity.parquet")
    print(f"  → p7_per_window_stationarity_verdict.json")

    print("\n=== VERDICTS ===")
    for rec, v in verdicts.items():
        print(f"  {rec}: {v['verdict']}  ({v['n_z_gt_2']}/{v['n_total']} z>2, mean z={v['mean_z']:+.2f})")


if __name__ == '__main__':
    main()
