"""
phase31b/monkey1_spont_10window_p7.py — characterize the only pvc-11
recording with PER_WINDOW_STATIONARY_P7 (monkey1_spontaneous) at
finer temporal resolution (10 windows × 123s each instead of 5 × 247s).

If p=7 STATIONARITY holds at 10 windows (≥8/10 z>2), the signal is
robust to ~2-min-scale temporal granularity.  If it degrades to
MIXTURE (4-7/10), the signal has a temporal scale longer than 2 min.

Output:
  data/phase31b_results/monkey1_spont_10window_p7.json
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
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from loader import load
from population_events import build_unit_matrix, extract_events, BIN_MS_DEFAULT, K_THRESH_DEFAULT
from arithmetic_toolkit import padic_amplitude_v4

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
Q_MAX_HIGH = 200
N_SEEDS = 5
PRIMES = (2, 3, 5, 7, 11, 13)


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def main():
    rec = load('monkey1_spontaneous')
    units = get_h2_units('monkey1_spontaneous')
    mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
    events = extract_events(mat, bin_ms=BIN_MS_DEFAULT, k_thresh=K_THRESH_DEFAULT)
    print(f"monkey1_spontaneous: n_events={events.size}  dur={total_dur:.0f}s  rate={events.size/total_dur:.2f}Hz")

    results = {}
    for n_windows in [5, 10, 20]:
        win_dur = total_dur / n_windows
        rows = []
        for w in range(n_windows):
            t0 = w * win_dur
            t1 = (w + 1) * win_dur
            win_events = events[(events >= t0) & (events < t1)] - t0
            if win_events.size < 100:
                continue
            pad = padic_amplitude_v4(win_events, q_max=Q_MAX_HIGH)
            sur_p7 = []
            for seed in range(N_SEEDS):
                rng = np.random.default_rng(seed + 12345)
                sur = np.sort(rng.uniform(0, win_dur, size=win_events.size))
                pad_sur = padic_amplitude_v4(sur, q_max=Q_MAX_HIGH)
                sur_p7.append(pad_sur['per_prime'][7]['normalised_per_q'])
            sur_p7 = np.asarray(sur_p7)
            real_p7 = pad['per_prime'][7]['normalised_per_q']
            z = (real_p7 - sur_p7.mean()) / max(sur_p7.std(), 1e-6)
            rows.append(dict(w=w, n_events=int(win_events.size),
                              real_p7=float(real_p7),
                              z_p7=float(z)))
        n_z2 = sum(1 for r in rows if r['z_p7'] > 2)
        mean_z = float(np.mean([r['z_p7'] for r in rows]))
        if n_z2 >= len(rows) * 0.8:
            v = 'PER_WINDOW_STATIONARY'
        elif n_z2 >= len(rows) * 0.4:
            v = 'PER_WINDOW_MIXTURE'
        elif n_z2 >= 1:
            v = 'PER_WINDOW_RARE'
        else:
            v = 'PER_WINDOW_NULL'
        results[n_windows] = dict(
            n_windows=n_windows, n_rows=len(rows),
            win_dur=float(win_dur), verdict=v,
            n_z_gt_2=n_z2, mean_z=mean_z,
            per_window=rows,
        )
        print(f"\n  {n_windows:2d} windows × {win_dur:.0f}s:")
        for r in rows:
            mk = ' ✓z>2' if r['z_p7'] > 2 else ''
            print(f"    win {r['w']:2d}: n={r['n_events']:5d}  real_p7={r['real_p7']:.3f}  z={r['z_p7']:+.2f}{mk}")
        print(f"  Verdict: {v}  ({n_z2}/{len(rows)} z>2, mean z={mean_z:+.2f})")

    with open(OUT_DIR / 'monkey1_spont_10window_p7.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  → monkey1_spont_10window_p7.json")


if __name__ == '__main__':
    main()
