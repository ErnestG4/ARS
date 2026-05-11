"""
phase31b/monkey3_gratings_qmax200.py — re-classify pvc-11
monkey3_gratings at q_max=200 to verify whether the p-adic v4 prime-7
dominance (z=+5.36 at q_max=30) persists at the §7.ter.13-validated
regime.

Phase 31b's p-adic v4 sweep over existing parquets at q_max=30
identified monkey3_gratings as the only pvc-11 recording with a clean
above-rate-matched-surrogate p-adic signal (dominant prime = 7, z =
+5.36 vs surrogate floor).  But the §7.ter.13 acceptance test was
validated at q_max=200 — at q_max=30, finite-band variance dominates
and 95.6 % of surrogates pass the absolute 1.5× threshold.  The
matched z-score discrimination at q_max=30 is suggestive but not
threshold-validated.

This script re-classifies monkey3_gratings population events at
q_max=200 (preserving Phase 22a interface: k_thresh=5, bin_ms=5 ms),
runs padic_amplitude_v4, and tests:

  1. Does the q_max=200 confidence (per-q-power-normalised ratio for
     p=7) exceed the §7.ter.13 validated threshold of 1.5×?
  2. Is the q_max=200 dominant_prime_per_q still p=7?
  3. How does the result compare to rate-matched Poisson surrogate
     at q_max=200 (3 seeds)?

Output:
  data/phase31b_results/monkey3_gratings_qmax200_verdict.json
  data/phase31b_results/monkey3_gratings_qmax200_real.json
  data/phase31b_results/monkey3_gratings_qmax200_surrogates.json
"""
from __future__ import annotations

import os
import sys
import json
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from loader import load
from population_events import build_unit_matrix, extract_events, BIN_MS_DEFAULT, K_THRESH_DEFAULT
from arithmetic_toolkit import ramanujan_fourier, padic_amplitude_v4

import pandas as pd

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

Q_MAX_HIGH = 200
N_SEEDS = 3


def get_h2_units():
    """Read the H2-passing units for monkey3_gratings from Phase 22a
    unit selection."""
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == 'monkey3_gratings') & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def main():
    print("=" * 72)
    print("Phase 31b — monkey3_gratings q_max=200 reclassification")
    print("=" * 72)

    rec = load('monkey3_gratings')
    units = get_h2_units()
    print(f"  Recording: monkey3_gratings  n_units(H2-passing)={len(units)}")

    mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
    real_events = extract_events(mat, bin_ms=BIN_MS_DEFAULT,
                                   k_thresh=K_THRESH_DEFAULT)
    print(f"  Real population events (k=5, w=5ms): {real_events.size}")
    print(f"  Rate: {real_events.size / total_dur:.2f} Hz over {total_dur:.0f} s")

    # ─── Real-data RF at q_max=200 + p-adic v4 ───
    print(f"\n--- Real data at q_max={Q_MAX_HIGH} ---")
    t0 = time.time()
    rf_real = ramanujan_fourier(real_events, q_max=Q_MAX_HIGH, normalize=False)
    amps_real = np.abs(np.asarray(rf_real['amplitudes'], dtype=np.float64))
    pad_real = padic_amplitude_v4(real_events, q_max=Q_MAX_HIGH)
    print(f"  ⏱{time.time()-t0:.1f}s")
    print(f"  dominant_prime_per_q = {pad_real['dominant_prime_per_q']}  "
          f"dominant_prime_sum = {pad_real['dominant_prime']}")
    print(f"  Per-prime normalised_per_q ratios (>1.5× = validated threshold):")
    for p, info in pad_real['per_prime'].items():
        marker = " ✓" if info['normalised_per_q'] > 1.5 else "  "
        print(f"    p={p:2d}  n_bands={info['q_powers'] and len(info['q_powers']) or 0:2d}  "
              f"normalised_per_q={info['normalised_per_q']:7.3f}{marker}  "
              f"q_powers={info['q_powers']}")

    real_conf = pad_real['per_prime'][pad_real['dominant_prime_per_q']]['normalised_per_q']
    print(f"  Real confidence (max per-q-power-normalised) = {real_conf:.3f}")

    # ─── Rate-matched Poisson surrogate at q_max=200 ───
    print(f"\n--- Rate-matched Poisson surrogate at q_max={Q_MAX_HIGH} (n_seeds={N_SEEDS}) ---")
    sur_results = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed + 12345)
        n_real = real_events.size
        sur_events = np.sort(rng.uniform(0, total_dur, size=n_real))
        t0 = time.time()
        pad_sur = padic_amplitude_v4(sur_events, q_max=Q_MAX_HIGH)
        sur_conf = pad_sur['per_prime'][pad_sur['dominant_prime_per_q']]['normalised_per_q']
        sur_results.append(dict(
            seed=seed,
            dominant_prime=int(pad_sur['dominant_prime_per_q']),
            confidence=float(sur_conf),
            per_prime_normed_per_q={int(p): float(info['normalised_per_q'])
                                       for p, info in pad_sur['per_prime'].items()},
        ))
        print(f"  seed {seed}: dom_prime={pad_sur['dominant_prime_per_q']}  "
              f"confidence={sur_conf:.3f}  ⏱{time.time()-t0:.1f}s")

    sur_confs = np.asarray([s['confidence'] for s in sur_results])
    sur_p7_ratios = np.asarray([s['per_prime_normed_per_q'][7] for s in sur_results])
    real_p7 = pad_real['per_prime'][7]['normalised_per_q']

    print(f"\n  Surrogate confidence: mean={sur_confs.mean():.3f}  "
          f"std={sur_confs.std():.3f}  max={sur_confs.max():.3f}")
    print(f"  Real p=7 ratio:        {real_p7:.3f}")
    print(f"  Surrogate p=7 ratios:  mean={sur_p7_ratios.mean():.3f}  "
          f"std={sur_p7_ratios.std():.3f}  max={sur_p7_ratios.max():.3f}")

    # Z-score on p=7 specifically
    p7_z = (real_p7 - sur_p7_ratios.mean()) / max(sur_p7_ratios.std(), 1e-6)
    print(f"  z-score for p=7 (real vs surrogate): {p7_z:+.2f}")

    # ─── Verdict ───
    real_above_threshold = real_p7 > 1.5
    real_dominant_p7 = pad_real['dominant_prime_per_q'] == 7
    real_above_sur_max = real_p7 > sur_p7_ratios.max()

    if real_dominant_p7 and real_above_threshold and real_above_sur_max:
        verdict = 'PRIME7_PERSISTS_AT_VALIDATED_THRESHOLD'
    elif real_dominant_p7 and real_above_threshold:
        verdict = 'PRIME7_DOMINATES_BUT_NOT_ABOVE_SUR_MAX'
    elif real_dominant_p7:
        verdict = 'PRIME7_DOMINATES_BUT_BELOW_THRESHOLD'
    elif real_above_threshold:
        verdict = 'ABOVE_THRESHOLD_BUT_DIFFERENT_PRIME'
    else:
        verdict = 'NOT_PERSIST'

    summary = dict(
        recording='monkey3_gratings',
        q_max=Q_MAX_HIGH,
        verdict=verdict,
        n_real_events=int(real_events.size),
        total_duration_sec=float(total_dur),
        real_dominant_prime_per_q=int(pad_real['dominant_prime_per_q']),
        real_confidence=float(real_conf),
        real_p7_normalised_per_q=float(real_p7),
        real_above_threshold=bool(real_above_threshold),
        real_above_sur_max=bool(real_above_sur_max),
        sur_confidence_mean=float(sur_confs.mean()),
        sur_confidence_std=float(sur_confs.std()),
        sur_p7_ratio_mean=float(sur_p7_ratios.mean()),
        sur_p7_ratio_std=float(sur_p7_ratios.std()),
        p7_z_score=float(p7_z),
        per_prime_real_ratios={int(p): float(info['normalised_per_q'])
                                  for p, info in pad_real['per_prime'].items()},
        per_prime_real_q_powers={int(p): info['q_powers']
                                    for p, info in pad_real['per_prime'].items()},
        sur_per_prime=sur_results,
    )
    with open(OUT_DIR / 'monkey3_gratings_qmax200_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → monkey3_gratings_qmax200_verdict.json")
    print(f"\nVERDICT: {verdict}")
    print(f"  real dominant prime = {pad_real['dominant_prime_per_q']}")
    print(f"  real p=7 ratio = {real_p7:.3f}  (threshold 1.5)")
    print(f"  real p=7 ratio above surrogate max ({sur_p7_ratios.max():.3f}): "
          f"{real_above_sur_max}")
    print(f"  p=7 z-score = {p7_z:+.2f}")


if __name__ == '__main__':
    main()
