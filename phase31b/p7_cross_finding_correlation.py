"""
phase31b/p7_cross_finding_correlation.py — does the p=7 enrichment in
pvc-11 correlate with any biological feature already measured?

Using the all-pvc-11-recordings p-adic q_max=200 results from
pvc11_all_qmax200, correlate per-recording p=7 z-score with:
  - mean firing rate
  - total event count
  - H2 surrogate-survival success
  - subset (categorical)
  - monkey identity (categorical)
  - duration
  - modal aggregate classification

Also: does monkey4_spontaneous (z=+6.09, strongest p=7 signal) have
distinguishing biological features?

Output:
  data/phase31b_results/p7_cross_finding_correlation.json
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'


def main():
    print("=" * 72)
    print("Phase 31b — p=7 cross-finding correlation (pvc-11)")
    print("=" * 72)

    # Load pvc-11 p-adic results
    pvc_all = pd.read_parquet(OUT_DIR / 'pvc11_all_qmax200_per_prime.parquet')
    # Add monkey3_gratings results from Follow-up 1
    m3_grat = pd.read_parquet(OUT_DIR / 'padic_v4_pvc11.parquet')
    m3_grat = m3_grat[m3_grat['recording'].isin(
        ['monkey1_gratings', 'monkey2_gratings', 'monkey3_gratings'])]

    # Merge monkey1/2_gratings q_max=200 results
    m12_verdict_path = OUT_DIR / 'monkey12_gratings_qmax200_verdict.json'
    with open(m12_verdict_path) as f:
        m12 = json.load(f)
    # m12['recordings'] is a list of dicts
    gratings_rows = []
    for rec in m12.get('recordings', []):
        row = dict(
            recording=rec['recording'], subset='gratings',
            n_events=rec['n_events'],
            rate_hz=rec['n_events'] / max(rec['total_dur'], 1e-9),
            duration_sec=rec['total_dur'],
            real_p7=rec['per_prime_real'][str(7)] if str(7) in rec['per_prime_real']
                else rec['per_prime_real'].get(7),
            z_p7=rec['per_prime_z'][str(7)] if str(7) in rec['per_prime_z']
                else rec['per_prime_z'].get(7),
            real_p2=rec['per_prime_real'][str(2)] if str(2) in rec['per_prime_real']
                else rec['per_prime_real'].get(2),
            z_p2=rec['per_prime_z'][str(2)] if str(2) in rec['per_prime_z']
                else rec['per_prime_z'].get(2),
            above_thr_p7=rec['per_prime_real'].get(str(7),
                rec['per_prime_real'].get(7, 0)) > 1.5,
            source='m12_grat',
        )
        gratings_rows.append(row)

    # Also monkey3_gratings from monkey3_gratings_qmax200_verdict
    m3_path = OUT_DIR / 'monkey3_gratings_qmax200_verdict.json'
    with open(m3_path) as f:
        m3 = json.load(f)
    gratings_rows.append(dict(
        recording='monkey3_gratings', subset='gratings',
        n_events=m3['n_real_events'],
        rate_hz=m3['n_real_events'] / max(m3['total_duration_sec'], 1e-9),
        duration_sec=m3['total_duration_sec'],
        real_p7=m3['real_p7_normalised_per_q'],
        z_p7=m3['p7_z_score'],
        real_p2=m3['per_prime_real_ratios'].get('2', 0),
        z_p2=(m3['per_prime_real_ratios'].get('2', 0) - 2.359) / 0.464,  # from earlier
        above_thr_p7=m3['real_above_threshold'],
        source='m3_grat',
    ))

    gratings_df = pd.DataFrame(gratings_rows)
    print(f"\nGratings (3 recordings):")
    print(gratings_df[['recording', 'rate_hz', 'real_p7', 'z_p7']].to_string(index=False))

    # All other pvc-11 recordings (from pvc11_all_qmax200)
    other = pvc_all[['recording', 'subset', 'rate_hz', 'real_p7', 'z_p7',
                      'real_p2', 'z_p2', 'above_thr_p7', 'n_events',
                      'duration_sec']].copy()
    other['source'] = 'pvc11_all'

    # Concat all
    all_df = pd.concat([
        gratings_df[['recording', 'subset', 'rate_hz', 'real_p7', 'z_p7',
                      'real_p2', 'z_p2', 'above_thr_p7', 'n_events',
                      'duration_sec', 'source']],
        other,
    ], ignore_index=True)

    print(f"\nAll pvc-11 recordings (n={len(all_df)}):")
    print(all_df[['recording', 'subset', 'rate_hz', 'z_p7', 'above_thr_p7']]
            .sort_values('z_p7', ascending=False).to_string(index=False))

    # ─── Correlations ───
    print("\n=== Cross-feature correlations on z_p7 (all 15 recordings) ===")
    for feat in ['rate_hz', 'n_events', 'duration_sec', 'real_p7', 'real_p2',
                  'z_p2']:
        sub = all_df.dropna(subset=['z_p7', feat])
        if len(sub) < 3:
            continue
        rho, p = spearmanr(sub['z_p7'], sub[feat])
        print(f"  ρ(z_p7, {feat:14s}) = {rho:+.3f}  p={p:.3f}  n={len(sub)}")

    # By subset (categorical)
    print("\n=== z_p7 by subset ===")
    by_subset = all_df.groupby('subset').agg(
        n=('z_p7', 'count'),
        mean_z=('z_p7', 'mean'),
        std_z=('z_p7', 'std'),
        max_z=('z_p7', 'max'),
        n_z_gt_2=('z_p7', lambda x: (x > 2).sum()),
    )
    print(by_subset.round(3).to_string())

    # By monkey identity
    all_df['monkey'] = all_df['recording'].str.extract(r'(monkey\d+)')
    print("\n=== z_p7 by monkey ===")
    by_monkey = all_df.groupby('monkey').agg(
        n=('z_p7', 'count'),
        mean_z=('z_p7', 'mean'),
        max_z=('z_p7', 'max'),
        recordings=('recording', lambda x: list(x)),
    )
    print(by_monkey[['n', 'mean_z', 'max_z']].round(3).to_string())

    # Standout
    print("\n=== Top 5 strongest p=7 signals ===")
    top5 = all_df.sort_values('z_p7', ascending=False).head(5)
    print(top5[['recording', 'subset', 'rate_hz', 'real_p7', 'z_p7']].to_string(index=False))

    print("\n=== Bottom 5 (suppressed) p=7 ===")
    bot5 = all_df.sort_values('z_p7').head(5)
    print(bot5[['recording', 'subset', 'rate_hz', 'real_p7', 'z_p7']].to_string(index=False))

    # ─── Final structured summary ───
    summary = dict(
        n_recordings=int(len(all_df)),
        correlations=dict(),
        by_subset=by_subset.to_dict('index'),
        by_monkey=by_monkey[['n', 'mean_z', 'max_z']].to_dict('index'),
        top5=top5[['recording', 'subset', 'z_p7']].to_dict('records'),
        bottom5=bot5[['recording', 'subset', 'z_p7']].to_dict('records'),
    )
    for feat in ['rate_hz', 'n_events', 'duration_sec', 'real_p7', 'real_p2', 'z_p2']:
        sub = all_df.dropna(subset=['z_p7', feat])
        if len(sub) >= 3:
            rho, p = spearmanr(sub['z_p7'], sub[feat])
            summary['correlations'][feat] = dict(rho=float(rho), p=float(p),
                                                    n=int(len(sub)))

    with open(OUT_DIR / 'p7_cross_finding_correlation.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → p7_cross_finding_correlation.json")


if __name__ == '__main__':
    main()
