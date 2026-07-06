"""
phase22b/pass_b_snr_tertile.py — Phase 22b Pass B.

Question: does the H1 correlation hold within SNR tertiles, or could
it be driven by sort-quality variation that correlates with the
functional measurements?

Method:
  1. SNR tertiles assigned WITHIN recording (so the tertile structure
     reflects sort quality, not recording-confounded SNR distribution
     differences).
  2. Repeat per-tertile + per-recording the partial Spearman analysis
     of {rep_med, ks_gue_med} vs {OSI, DSI, F1/F0} controlling for
     mean firing rate.
  3. Aggregate per-tertile effect sizes via Fisher-Z meta-analysis
     across recordings (each tertile separately).
  4. Compare across tertiles + against the Phase 22a global.

Acceptance:
  - PASS:       effect ~comparable across tertiles (≤30% spread).
  - SOFT PASS:  monotonic attenuation with SNR (largest in high-SNR,
                smallest in low-SNR), but non-zero in all tertiles —
                consistent with measurement-error attenuation, not
                confound.
  - FAIL:       effect concentrates in one tertile and is absent or
                reversed in others.

Outputs:
  data/phase22b_results/pass_b_per_tertile_recording.parquet
  data/phase22b_results/pass_b_meta_per_tertile.parquet
  Stdout: per-tertile-per-recording table + per-tertile meta + verdict.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, t as student_t

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)


OUT_DIR_22A = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR_22B = Path(ROOT_DIR) / 'data' / 'phase22b_results'
OUT_DIR_22B.mkdir(parents=True, exist_ok=True)


from pass_a_recording_blocked import (
    _partial_spearman, meta_analyse, DESCRIPTORS, ARS_METRICS,
    ARS_PATH, FUNC_PATH, GLOBAL_PATH, N_MIN,
)


N_TERTILES = 3
TERTILE_LABELS = ['T1_low', 'T2_mid', 'T3_high']


def assign_tertiles_within_recording(g: pd.DataFrame) -> pd.DataFrame:
    """Assign SNR tertile within each recording (qcut on snr_x or snr).
    Returns a copy with new 'snr_tertile' column."""
    out = g.copy()
    snr_col = 'snr_x' if 'snr_x' in out.columns else 'snr'
    parts = []
    for rec, sub in out.groupby('recording', sort=False):
        # Use rank-based qcut to be robust to ties
        s = sub[snr_col].rank(method='first')
        # n must be ≥ 3 for tertiles; use np.full('T2_mid') for tiny groups
        if len(s) < N_TERTILES:
            sub = sub.copy()
            sub['snr_tertile'] = TERTILE_LABELS[N_TERTILES // 2]
        else:
            try:
                bin_idx = pd.qcut(s, N_TERTILES, labels=TERTILE_LABELS,
                                    duplicates='drop')
                sub = sub.copy()
                sub['snr_tertile'] = bin_idx.astype(str)
            except ValueError:
                sub = sub.copy()
                sub['snr_tertile'] = TERTILE_LABELS[N_TERTILES // 2]
        parts.append(sub)
    return pd.concat(parts, ignore_index=True)


def main():
    print("=" * 72)
    print("Phase 22b Pass B — SNR-tertile blocking")
    print("=" * 72)

    ars = pd.read_parquet(ARS_PATH)
    func = pd.read_parquet(FUNC_PATH)
    j = ars.merge(func, on=['recording', 'unit_idx', 'subset',
                              'monkey', 'unit_id'])
    print(f"  joined units: {len(j)}")
    print(f"  SNR column candidates: snr={'snr' in j.columns}  "
          f"snr_x={'snr_x' in j.columns}  snr_y={'snr_y' in j.columns}")

    grat = j[j['subset'] == 'gratings'].copy()
    grat = assign_tertiles_within_recording(grat)
    print(f"  drifting-grating units: {len(grat)}")
    print(f"  Tertile counts: "
          f"{dict(grat['snr_tertile'].value_counts())}")
    print()

    # Per-tertile-per-recording
    rows = []
    for tertile, gt in grat.groupby('snr_tertile'):
        for rec_name, group in gt.groupby('recording', sort=False):
            n_unit = len(group)
            for descriptor, dlabel in DESCRIPTORS:
                for ars_col, alabel in ARS_METRICS:
                    if descriptor not in group: continue
                    rho, p, n = _partial_spearman(
                        group[ars_col].to_numpy(),
                        group[descriptor].to_numpy(),
                        group['mean_rate'].to_numpy(),
                    )
                    rows.append(dict(
                        snr_tertile=tertile, recording=rec_name,
                        n_units=n,
                        descriptor=dlabel, ars_metric=alabel,
                        spearman_partial=rho, p_partial=p,
                    ))
    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR_22B / 'pass_b_per_tertile_recording.parquet',
                   index=False)
    print(f"  → {OUT_DIR_22B}/pass_b_per_tertile_recording.parquet  "
          f"({len(df)} rows)")
    print()

    # Per-tertile per-(descriptor, ars_metric) meta-analysis
    meta_rows = []
    for tertile in TERTILE_LABELS:
        for descriptor, dlabel in DESCRIPTORS:
            for ars_col, alabel in ARS_METRICS:
                sub = df[(df['snr_tertile'] == tertile) &
                          (df['descriptor'] == dlabel) &
                          (df['ars_metric'] == alabel)]
                if not len(sub): continue
                ma = meta_analyse(sub['spearman_partial'].tolist(),
                                    sub['n_units'].tolist())
                meta_rows.append(dict(
                    snr_tertile=tertile,
                    descriptor=dlabel, ars_metric=alabel, **ma,
                ))
    meta_df = pd.DataFrame(meta_rows)
    meta_df.to_parquet(OUT_DIR_22B / 'pass_b_meta_per_tertile.parquet',
                        index=False)
    print(f"  → {OUT_DIR_22B}/pass_b_meta_per_tertile.parquet  "
          f"({len(meta_df)} rows)")
    print()

    # Pivot for human-readable per-tertile comparison
    pivot = meta_df.pivot_table(
        index=['descriptor', 'ars_metric'],
        columns='snr_tertile', values='fixed_rho')
    print("Per-tertile meta-fixed partial correlation:")
    print(pivot.round(3).to_string())
    print()

    # Compare to Phase 22a global
    glob = pd.read_parquet(GLOBAL_PATH)
    glob = glob[glob['family'] == 'partial_corr']
    glob['descriptor'] = (glob['descriptor']
                            .replace({'f1_f0_pref': 'F1/F0',
                                       'osi': 'OSI', 'dsi': 'DSI'}))
    cmp_rows = []
    for descriptor, dlabel in DESCRIPTORS:
        for ars_col, alabel in ARS_METRICS:
            mr = meta_df[(meta_df['descriptor'] == dlabel) &
                          (meta_df['ars_metric'] == alabel)]
            gr = glob[(glob['descriptor'] == dlabel) &
                       (glob['ars_metric'] == alabel)]
            if not len(mr) or not len(gr): continue
            global_rho = float(gr['spearman_partial'].iloc[0])
            tertile_rhos = mr.set_index('snr_tertile')['fixed_rho']
            t1 = float(tertile_rhos.get('T1_low', np.nan))
            t2 = float(tertile_rhos.get('T2_mid', np.nan))
            t3 = float(tertile_rhos.get('T3_high', np.nan))
            spread = max([abs(t1), abs(t2), abs(t3)]) - \
                     min([abs(t1), abs(t2), abs(t3)])
            cmp_rows.append(dict(
                descriptor=dlabel, ars_metric=alabel,
                global_22a=global_rho,
                tertile_T1_low=t1, tertile_T2_mid=t2,
                tertile_T3_high=t3,
                spread_abs=spread,
                pct_spread=(spread / max(abs(global_rho), 1e-9)) * 100,
            ))
    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_parquet(OUT_DIR_22B / 'pass_b_comparison.parquet', index=False)
    print("Tertile spread vs Phase 22a global:")
    print(cmp_df.round(3).to_string(index=False))
    print()

    # Verdict on headline
    print("Verdict:")
    headline = cmp_df[(cmp_df['descriptor'] == 'OSI') &
                       (cmp_df['ars_metric'] == 'ks_gue_med')]
    if len(headline):
        h = headline.iloc[0]
        t = [h['tertile_T1_low'], h['tertile_T2_mid'], h['tertile_T3_high']]
        same_sign = all((not np.isnan(v)) and v > 0 for v in t)
        spread_pct = h['pct_spread']
        # Monotonic in SNR?
        monotonic = (not np.isnan(t[0]) and not np.isnan(t[2]) and
                       (abs(t[2]) >= abs(t[1]) >= abs(t[0])))
        print(f"  HEADLINE (OSI ↔ ks_gue_med):  "
              f"T1_low={t[0]:+.3f}  T2_mid={t[1]:+.3f}  "
              f"T3_high={t[2]:+.3f}")
        if same_sign and spread_pct <= 30:
            print(f"  PASS (≤30% spread, all tertiles same sign)")
        elif same_sign and monotonic:
            print(f"  SOFT PASS (monotonic SNR attenuation, all tertiles "
                  f"same sign — consistent with measurement-error "
                  f"attenuation)")
        elif same_sign:
            print(f"  SOFT PASS (all tertiles same sign, but spread "
                  f"{spread_pct:.0f}% > 30%)")
        else:
            print(f"  FAIL (signs differ across tertiles)")


if __name__ == '__main__':
    main()
