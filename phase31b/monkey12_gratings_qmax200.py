"""
phase31b/monkey12_gratings_qmax200.py — replicate the monkey3_gratings
q_max=200 p-adic analysis on monkey1_gratings + monkey2_gratings.

Tests whether the multi-prime structure (p=2 dominant 4.06×, p=7
secondary 1.77×) found on monkey3_gratings is a gratings-stimulus
class signal or recording-specific.

Output:
  data/phase31b_results/monkey12_gratings_qmax200_verdict.json
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
N_SEEDS = 3


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def analyze(recording_name: str):
    print(f"\n--- {recording_name} ---")
    rec = load(recording_name)
    units = get_h2_units(recording_name)
    mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
    events = extract_events(mat, bin_ms=BIN_MS_DEFAULT,
                              k_thresh=K_THRESH_DEFAULT)
    print(f"  n_units(H2-passing)={len(units)}  n_events={events.size}  "
          f"rate={events.size/total_dur:.2f} Hz  dur={total_dur:.0f}s")

    pad = padic_amplitude_v4(events, q_max=Q_MAX_HIGH)
    print(f"  Real p-adic v4 @ q_max={Q_MAX_HIGH}:")
    for p, info in pad['per_prime'].items():
        marker = ' ✓' if info['normalised_per_q'] > 1.5 else '  '
        print(f"    p={p:2d}  normalised_per_q={info['normalised_per_q']:7.3f}{marker}  "
              f"n_bands={len(info['q_powers'])}")

    # Surrogate
    sur_results = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 12345)
        sur_events = np.sort(rng.uniform(0, total_dur, size=events.size))
        pad_sur = padic_amplitude_v4(sur_events, q_max=Q_MAX_HIGH)
        sur_results.append({int(p): float(info['normalised_per_q'])
                              for p, info in pad_sur['per_prime'].items()})
    print(f"  Surrogate (n={N_SEEDS}):")
    for p in pad['per_prime'].keys():
        sur_vals = np.asarray([s[int(p)] for s in sur_results])
        real_val = pad['per_prime'][p]['normalised_per_q']
        z = (real_val - sur_vals.mean()) / max(sur_vals.std(), 1e-6)
        flag = ' ✓ above-sur-max' if real_val > sur_vals.max() else ''
        print(f"    p={p:2d}  real={real_val:.3f}  sur_mean={sur_vals.mean():.3f}±{sur_vals.std():.3f}  "
              f"z={z:+.2f}{flag}")

    return dict(
        recording=recording_name,
        n_events=int(events.size),
        total_dur=float(total_dur),
        dominant_prime_per_q=int(pad['dominant_prime_per_q']),
        per_prime_real={int(p): float(info['normalised_per_q'])
                          for p, info in pad['per_prime'].items()},
        per_prime_sur_means={int(p): float(np.mean([s[int(p)] for s in sur_results]))
                                for p in pad['per_prime'].keys()},
        per_prime_sur_stds={int(p): float(np.std([s[int(p)] for s in sur_results]))
                               for p in pad['per_prime'].keys()},
        per_prime_sur_max={int(p): float(np.max([s[int(p)] for s in sur_results]))
                              for p in pad['per_prime'].keys()},
        per_prime_z={int(p): float(
                (pad['per_prime'][p]['normalised_per_q'] -
                 np.mean([s[int(p)] for s in sur_results]))
                / max(np.std([s[int(p)] for s in sur_results]), 1e-6))
            for p in pad['per_prime'].keys()},
    )


def main():
    print("=" * 72)
    print("Phase 31b — monkey1/2_gratings p-adic v4 @ q_max=200")
    print("=" * 72)

    results = []
    for rec in ('monkey1_gratings', 'monkey2_gratings'):
        results.append(analyze(rec))

    # Compare to monkey3
    print("\n=== Comparison to monkey3_gratings (Phase 31b Follow-up 1) ===")
    print(f"  monkey3: p=2 ratio=4.060 (z=+3.67), p=7 ratio=1.766 (z=+1.90)")
    print(f"  Class signal hypothesis: do monkey1/2 also have multi-prime p=2+p=7?")

    summary = dict(recordings=results)
    # Class signal check
    p2_real = [r['per_prime_real'][2] for r in results]
    p7_real = [r['per_prime_real'][7] for r in results]
    p2_z = [r['per_prime_z'][2] for r in results]
    p7_z = [r['per_prime_z'][7] for r in results]
    summary['p2_real_ratios'] = p2_real
    summary['p7_real_ratios'] = p7_real
    summary['p2_z_scores'] = p2_z
    summary['p7_z_scores'] = p7_z

    # Verdict
    p2_above_threshold = sum(r > 1.5 for r in p2_real)
    p7_above_threshold = sum(r > 1.5 for r in p7_real)
    p2_above_sur = sum(z > 2 for z in p2_z)
    p7_above_sur = sum(z > 2 for z in p7_z)
    print(f"\n  p=2 above threshold (>1.5×): {p2_above_threshold}/2  "
          f"above-sur (z>2): {p2_above_sur}/2  (monkey3 was both)")
    print(f"  p=7 above threshold (>1.5×): {p7_above_threshold}/2  "
          f"above-sur (z>2): {p7_above_sur}/2  (monkey3 was both)")

    if p2_above_threshold >= 1 and p2_above_sur >= 1 \
       and p7_above_threshold >= 1 and p7_above_sur >= 1:
        verdict = 'CLASS_SIGNAL_LIKELY'
    elif p2_above_threshold >= 1 and p7_above_threshold == 0:
        verdict = 'P2_CLASS_SIGNAL_BUT_NOT_P7'
    elif p2_above_threshold == 0 and p7_above_threshold == 0:
        verdict = 'MONKEY3_SPECIFIC'
    else:
        verdict = 'PARTIAL'
    summary['verdict'] = verdict
    with open(OUT_DIR / 'monkey12_gratings_qmax200_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → monkey12_gratings_qmax200_verdict.json")
    print(f"\nVERDICT (class signal): {verdict}")


if __name__ == '__main__':
    main()
