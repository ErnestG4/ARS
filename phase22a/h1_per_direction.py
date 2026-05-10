"""
phase22a/h1_per_direction.py — within-unit per-direction modulation
analysis for the H1 ARS results.

Question: does the OSI ↔ ks_gue_med correspondence (ρ_partial = +0.720,
n=210, p < 1e-37) reported in the between-unit cross-validation reflect
stimulus-driven modulation of NNS structure within a unit (preferred
direction → larger ks_gue_med than null direction on the same unit),
or only between-unit variation in cell-intrinsic NNS properties?

Procedure: for every drifting-grating-recording unit with both
preferred and null direction (180°) classifications, compute
delta_ks_gue = ks_gue_med(pref) − ks_gue_med(null) and similarly for
rep_med.  Sign test, Wilcoxon signed-rank, and Spearman of the deltas
against the unit's OSI.

Output: data/phase22a_results/h1_per_direction_modulation.parquet
        plus printed summary for the writeup.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
DIRS_PATH = OUT_DIR / 'h1_classifications_grating_dirs.parquet'
FUNC_PATH = OUT_DIR / 'h1_functional.parquet'


def main():
    print("=" * 72)
    print("Phase 22a H1 — per-direction within-unit modulation analysis")
    print("=" * 72)

    dirs = pd.read_parquet(DIRS_PATH)
    func = pd.read_parquet(FUNC_PATH)
    g = func[func['subset'] == 'gratings'].copy()

    dirs = dirs.copy()
    dirs['dir_idx'] = dirs['condition'].str.replace('dir_', '').astype(int)
    m = dirs.merge(g[['unit_id', 'recording', 'pref_idx', 'osi', 'dsi',
                       'f1_f0_pref', 'pref_dir_deg']],
                   on=['unit_id', 'recording'])
    m['null_idx'] = (m['pref_idx'] + 6) % 12     # 180° opposite
    m['is_pref'] = m['dir_idx'] == m['pref_idx']
    m['is_null'] = m['dir_idx'] == m['null_idx']

    pref = (m[m['is_pref']]
              .set_index('unit_id')[['ks_gue_med', 'rep_med', 'primary',
                                       'pref_idx', 'osi', 'dsi', 'f1_f0_pref']])
    null = (m[m['is_null']]
              .set_index('unit_id')[['ks_gue_med', 'rep_med', 'primary']])
    j = pref.join(null, lsuffix='_pref', rsuffix='_null', how='inner')
    j = j.dropna(subset=['ks_gue_med_pref', 'ks_gue_med_null'])
    j['delta_ks_gue'] = j['ks_gue_med_pref'] - j['ks_gue_med_null']
    j['delta_rep'] = j['rep_med_pref'] - j['rep_med_null']

    print(f"  Units with both pref + null ARS: {len(j)}")
    print()

    rows = []

    for col, label in [('delta_ks_gue', 'ks_gue_med'),
                        ('delta_rep', 'rep_med')]:
        n_gt = int((j[col] > 0).sum())
        n_lt = int((j[col] < 0).sum())
        n_eq = int((j[col] == 0).sum())
        median = float(j[col].median())
        mean = float(j[col].mean())
        nz = j[j[col] != 0]
        if len(nz):
            w_stat, w_p = wilcoxon(nz[col])
        else:
            w_stat, w_p = float('nan'), float('nan')
        sub = j.dropna(subset=['osi', col])
        rho_osi, p_osi = (spearmanr(sub['osi'], sub[col])
                            if len(sub) >= 10 else (float('nan'), float('nan')))
        sub = j.dropna(subset=['dsi', col])
        rho_dsi, p_dsi = (spearmanr(sub['dsi'], sub[col])
                            if len(sub) >= 10 else (float('nan'), float('nan')))

        rows.append(dict(
            metric=label,
            n_units=len(j),
            n_pref_gt_null=n_gt, n_pref_lt_null=n_lt, n_equal=n_eq,
            median_delta=median, mean_delta=mean,
            wilcoxon_n_nonzero=int(len(nz)),
            wilcoxon_W=float(w_stat),
            wilcoxon_p=float(w_p),
            spearman_OSI_vs_delta=float(rho_osi),
            spearman_OSI_p=float(p_osi),
            spearman_DSI_vs_delta=float(rho_dsi),
            spearman_DSI_p=float(p_dsi),
        ))
        print(f"  {label}:")
        print(f"    delta median={median:+.4f}  mean={mean:+.4f}")
        print(f"    sign test: pref>null {n_gt}  pref<null {n_lt}  ==0 {n_eq}")
        print(f"    Wilcoxon (n_nonzero={len(nz)}): W={w_stat:.1f}  p={w_p:.3e}")
        print(f"    Spearman OSI vs delta: rho={rho_osi:+.3f}  p={p_osi:.3e}")
        print(f"    Spearman DSI vs delta: rho={rho_dsi:+.3f}  p={p_dsi:.3e}")
        print()

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'h1_per_direction_modulation.parquet', index=False)
    print(f"  → {OUT_DIR}/h1_per_direction_modulation.parquet")
    print()
    print("Interpretation:")
    print("  Statistically negligible delta_ks_gue (Wilcoxon p > 0.5) AND no")
    print("  OSI correlation of the modulation (Spearman p > 0.05) means the")
    print("  OSI ↔ ks_gue_med correspondence reported in the between-unit")
    print("  partial-correlation analysis is a unit-intrinsic property, NOT")
    print("  stimulus-driven modulation of NNS structure within a unit.")


if __name__ == '__main__':
    main()
