"""
phase24/run_meta_analysis.py — multi-session Fisher-Z meta-analysis on
per-session H1 partial correlations.

Reads `per_session_h1_crossval.parquet` and computes:
  - Overall Fisher-Z fixed + random effect across all sessions
  - Stratified by Cre line (where ≥ 2 sessions per line)
  - Stratified by per-session event-rate quartile (per-session mean
    firing rate as the rate-regime axis)

Outputs:
  data/phase24_results/h1_meta_overall.parquet
  data/phase24_results/h1_meta_by_cre.parquet
  data/phase24_results/h1_meta_by_rate_quartile.parquet
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22b'))
sys.path.insert(0, THIS_DIR)

# Reuse Phase 22b's Fisher-Z helpers
from pass_a_recording_blocked import meta_analyse, fisher_z, inv_fisher_z


CV_PATH = Path('/home/combust/fmexplorer/criticality_tool/data/phase24_results/per_session_h1_crossval.parquet')
FUNC_PATH = Path('/home/combust/fmexplorer/criticality_tool/data/phase24_results/per_session_h1_functional.parquet')
OUT_DIR = Path('/home/combust/fmexplorer/criticality_tool/data/phase24_results')


def main():
    print("=" * 80)
    print("Phase 24 Full — H1 Fisher-Z meta-analysis")
    print("=" * 80)

    cv = pd.read_parquet(CV_PATH)
    func = pd.read_parquet(FUNC_PATH)
    print(f"  per-session H1 cross-val rows: {len(cv)}")
    print(f"  sessions: {cv['session_id'].nunique()}")
    print(f"  Cre lines: {dict(cv.drop_duplicates('session_id')['cre_line'].value_counts())}")
    print()

    # ─── Overall meta ──
    print("Overall meta-analysis (all sessions):")
    rows = []
    for descriptor in ['osi', 'dsi', 'f1_f0_pref']:
        for ars_metric in ['rep_med', 'ks_gue_med']:
            sub = cv[(cv['descriptor'] == descriptor)
                       & (cv['ars_metric'] == ars_metric)]
            if not len(sub): continue
            ma = meta_analyse(sub['spearman_partial'].tolist(),
                                sub['n_units'].tolist())
            rows.append(dict(
                descriptor=descriptor, ars_metric=ars_metric,
                n_sessions=len(sub), **ma,
            ))
    overall = pd.DataFrame(rows)
    overall.to_parquet(OUT_DIR / 'h1_meta_overall.parquet', index=False)
    print(overall.round(3).to_string(index=False))
    print(f"\n  → {OUT_DIR}/h1_meta_overall.parquet")
    print()

    # ─── By Cre line (≥2 sessions) ──
    print("Stratified by Cre line:")
    cre_counts = cv.drop_duplicates('session_id')['cre_line'].value_counts()
    rows = []
    for cre in cre_counts[cre_counts >= 2].index:
        for descriptor in ['osi', 'dsi', 'f1_f0_pref']:
            for ars_metric in ['rep_med', 'ks_gue_med']:
                sub = cv[(cv['cre_line'] == cre)
                           & (cv['descriptor'] == descriptor)
                           & (cv['ars_metric'] == ars_metric)]
                if not len(sub): continue
                ma = meta_analyse(sub['spearman_partial'].tolist(),
                                    sub['n_units'].tolist())
                rows.append(dict(
                    cre_line=cre, descriptor=descriptor, ars_metric=ars_metric,
                    n_sessions=len(sub), **ma,
                ))
    by_cre = pd.DataFrame(rows)
    by_cre.to_parquet(OUT_DIR / 'h1_meta_by_cre.parquet', index=False)
    print(by_cre.round(3).to_string(index=False))
    print(f"\n  → {OUT_DIR}/h1_meta_by_cre.parquet")
    print()

    # ─── By per-session event-rate quartile ──
    print("Stratified by per-session mean firing-rate quartile:")
    sess_rate = func.groupby('session_id')['mean_rate'].mean().rename('sess_mean_rate')
    quart = pd.qcut(sess_rate.rank(method='first'), 4,
                      labels=['Q1_low', 'Q2', 'Q3', 'Q4_high']).rename('rate_quartile')
    cv = cv.merge(quart, left_on='session_id', right_index=True)
    rows = []
    for q in ['Q1_low', 'Q2', 'Q3', 'Q4_high']:
        for descriptor in ['osi', 'dsi', 'f1_f0_pref']:
            for ars_metric in ['rep_med', 'ks_gue_med']:
                sub = cv[(cv['rate_quartile'] == q)
                           & (cv['descriptor'] == descriptor)
                           & (cv['ars_metric'] == ars_metric)]
                if not len(sub): continue
                ma = meta_analyse(sub['spearman_partial'].tolist(),
                                    sub['n_units'].tolist())
                rows.append(dict(
                    rate_quartile=q, descriptor=descriptor, ars_metric=ars_metric,
                    n_sessions=len(sub), **ma,
                ))
    by_rate = pd.DataFrame(rows)
    by_rate.to_parquet(OUT_DIR / 'h1_meta_by_rate_quartile.parquet', index=False)
    print(by_rate.round(3).to_string(index=False))
    print(f"\n  → {OUT_DIR}/h1_meta_by_rate_quartile.parquet")
    print()

    # ─── Headline summary vs pvc-11 reference ──
    PVC11_REF = {
        ('osi', 'ks_gue_med'): +0.720,
        ('osi', 'rep_med'): -0.324,
        ('dsi', 'ks_gue_med'): +0.223,
        ('dsi', 'rep_med'): -0.060,
        ('f1_f0_pref', 'rep_med'): +0.388,
        ('f1_f0_pref', 'ks_gue_med'): -0.093,
    }
    print("Allen multi-session vs pvc-11 (H1 headlines):")
    print(f"{'descriptor':12s} {'ARS metric':12s} {'pvc-11 ρ':>10s} "
          f"{'Allen meta-fix':>14s} {'random':>8s} {'I²':>6s} "
          f"{'sign':>6s} {'verdict':>20s}")
    for (d, m), pvc_rho in PVC11_REF.items():
        row = overall[(overall['descriptor'] == d) & (overall['ars_metric'] == m)]
        if not len(row): continue
        r = row.iloc[0]
        sign_match = ('match' if (r['fixed_rho'] * pvc_rho) > 0
                       else 'flip' if (r['fixed_rho'] * pvc_rho) < 0 else '~0')
        if d == 'osi' and m == 'ks_gue_med':
            verdict = ('LOCKED' if abs(r['fixed_rho']) > 0.5 * abs(pvc_rho)
                                  and r['fixed_rho'] * pvc_rho > 0
                         else 'MODIFIED' if r['fixed_rho'] * pvc_rho > 0
                         else 'NOT REPLICATED')
        else:
            verdict = ('replicates' if r['fixed_rho'] * pvc_rho > 0
                         else 'sign-flip')
        print(f"{d:12s} {m:12s} {pvc_rho:+10.3f} {r['fixed_rho']:+14.3f} "
              f"{r['random_rho']:+8.3f} {r['I2']:>5.0f}% {sign_match:>6s} "
              f"{verdict:>20s}")


if __name__ == '__main__':
    main()
