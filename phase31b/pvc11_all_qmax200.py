"""
phase31b/pvc11_all_qmax200.py — extend the p=7 class-signal test to
all pvc-11 movie + spontaneous recordings at q_max=200.

Follow-up 5 confirmed p=7 enrichment across all 3 pvc-11 gratings
recordings.  This script tests whether the p=7 signal generalizes to:
  - natural-movie recordings (beta-band hypothesis test)
  - noise-movie recordings (random-stimulus control)
  - gratings-movie recordings (different gratings-stimulus design)
  - spontaneous recordings (stimulus-free baseline)

If p=7 is beta-band: should be present in natural_movie / gratings_movie,
absent or weaker in noise_movie / spontaneous.
If p=7 is gratings-stimulus-specific: should be present only in gratings.
If p=7 is V1-intrinsic: should be present in all 6 recordings.

Output:
  data/phase31b_results/pvc11_all_qmax200_verdict.json
  data/phase31b_results/pvc11_all_qmax200_per_prime.parquet
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

# All pvc-11 recordings except gratings (already in Follow-up 1+5)
RECORDINGS = [
    'monkey1_spontaneous', 'monkey2_spontaneous', 'monkey3_spontaneous',
    'monkey4_spontaneous', 'monkey5_spontaneous', 'monkey6_spontaneous',
    'monkey1_gratings_movie', 'monkey2_gratings_movie',
    'monkey1_natural_movie', 'monkey2_natural_movie',
    'monkey1_noise_movie', 'monkey2_noise_movie',
]


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def main():
    print("=" * 72)
    print("Phase 31b — pvc-11 all recordings p-adic v4 @ q_max=200")
    print("=" * 72)

    rows = []
    for rec_name in RECORDINGS:
        try:
            rec = load(rec_name)
            units = get_h2_units(rec_name)
            if not units:
                print(f"\n--- {rec_name}: NO H2-passing units, skipping ---")
                continue
            mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
            events = extract_events(mat, bin_ms=BIN_MS_DEFAULT,
                                      k_thresh=K_THRESH_DEFAULT)
        except Exception as e:
            print(f"\n--- {rec_name}: load error: {e}, skipping ---")
            continue

        rate = events.size / total_dur if total_dur > 0 else 0.0
        if events.size < 200:
            print(f"\n--- {rec_name}: too few events ({events.size}), skipping ---")
            continue

        print(f"\n--- {rec_name} ---")
        print(f"  n_units={len(units)}  n_events={events.size}  rate={rate:.2f}Hz  dur={total_dur:.0f}s")

        # Real
        pad = padic_amplitude_v4(events, q_max=Q_MAX_HIGH)
        real_ratios = {int(p): float(pad['per_prime'][p]['normalised_per_q'])
                         for p in PRIMES}

        # Surrogate (rate-matched Poisson)
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
        sur_maxes = {p: float(np.max(v)) for p, v in sur_ratios.items()}
        z_scores = {p: (real_ratios[p] - sur_means[p]) / max(sur_stds[p], 1e-6)
                     for p in PRIMES}
        above_thresh = {p: bool(real_ratios[p] > 1.5) for p in PRIMES}
        above_sur_max = {p: bool(real_ratios[p] > sur_maxes[p]) for p in PRIMES}

        # Print summary
        print(f"  p=7: real={real_ratios[7]:.3f}  "
              f"sur={sur_means[7]:.3f}±{sur_stds[7]:.3f}  "
              f"z={z_scores[7]:+.2f}  "
              f"{'(p7-CLASS)' if z_scores[7] > 2 else ''}")
        dom_z = max(z_scores.items(), key=lambda kv: kv[1])
        print(f"  dominant by z: p={dom_z[0]}  z={dom_z[1]:+.2f}")
        print(f"  primes above 1.5×: " +
              ", ".join(f"p={p}({real_ratios[p]:.2f})"
                          for p in PRIMES if above_thresh[p]))

        rows.append(dict(
            recording=rec_name, subset=rec.subset,
            n_events=int(events.size), rate_hz=float(rate),
            duration_sec=float(total_dur),
            dominant_prime_per_q=int(pad['dominant_prime_per_q']),
            **{f'real_p{p}': real_ratios[p] for p in PRIMES},
            **{f'sur_mean_p{p}': sur_means[p] for p in PRIMES},
            **{f'sur_std_p{p}': sur_stds[p] for p in PRIMES},
            **{f'z_p{p}': z_scores[p] for p in PRIMES},
            **{f'above_thr_p{p}': above_thresh[p] for p in PRIMES},
            **{f'above_sur_max_p{p}': above_sur_max[p] for p in PRIMES},
        ))

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'pvc11_all_qmax200_per_prime.parquet', index=False)

    print("\n\n=== Cross-subset p=7 summary ===")
    print(df[['recording', 'subset', 'rate_hz', 'real_p7', 'sur_mean_p7',
                'z_p7', 'above_thr_p7']].to_string(index=False))

    # Per-subset p7 class signal aggregate
    print("\n=== Per-subset p=7 enrichment ===")
    by_subset = {}
    for subset, sub in df.groupby('subset'):
        n_above_thr = int(sub['above_thr_p7'].sum())
        n_z2 = int((sub['z_p7'] > 2).sum())
        n_total = len(sub)
        mean_z = float(sub['z_p7'].mean())
        mean_ratio = float(sub['real_p7'].mean())
        print(f"  {subset:18s}: n={n_total}  "
              f"above-1.5×: {n_above_thr}/{n_total}  "
              f"z>2: {n_z2}/{n_total}  "
              f"mean z={mean_z:+.2f}  mean ratio={mean_ratio:.2f}")
        by_subset[str(subset)] = dict(
            n=int(n_total), n_above_threshold=n_above_thr,
            n_z_gt_2=n_z2, mean_z=mean_z, mean_ratio=mean_ratio,
            recordings=sub['recording'].tolist(),
        )

    # Verdict
    movie_subsets = ['natural_movie', 'gratings_movie', 'noise_movie']
    n_movie_z2 = sum(by_subset.get(s, {}).get('n_z_gt_2', 0)
                       for s in movie_subsets)
    n_movie_total = sum(by_subset.get(s, {}).get('n', 0) for s in movie_subsets)
    n_spont_z2 = by_subset.get('spontaneous', {}).get('n_z_gt_2', 0)
    n_spont_total = by_subset.get('spontaneous', {}).get('n', 0)

    if n_movie_z2 >= 2 and n_spont_z2 <= n_spont_total / 3:
        verdict = 'P7_STIMULUS_DRIVEN'
    elif n_movie_z2 >= 2 and n_spont_z2 >= n_spont_total / 2:
        verdict = 'P7_V1_INTRINSIC'
    elif n_movie_z2 == 0:
        verdict = 'P7_GRATINGS_SPECIFIC'
    else:
        verdict = 'P7_PARTIAL'

    summary = dict(
        verdict=verdict,
        by_subset=by_subset,
        n_recordings_tested=len(df),
    )
    with open(OUT_DIR / 'pvc11_all_qmax200_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → pvc11_all_qmax200_*.parquet/json")
    print(f"\nVERDICT (p=7 class signal generalization): {verdict}")
    print(f"  Movie subsets z>2: {n_movie_z2}/{n_movie_total}")
    print(f"  Spontaneous z>2:    {n_spont_z2}/{n_spont_total}")


if __name__ == '__main__':
    main()
