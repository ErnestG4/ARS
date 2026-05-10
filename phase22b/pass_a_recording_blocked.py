"""
phase22b/pass_a_recording_blocked.py — Phase 22b Pass A.

Question: is the H1 ARS-functional correlation a within-recording
cell-to-cell signal, or is it driven by between-recording variation
that happens to correlate with OSI distributions across recordings?

Method:
  1. For each evoked recording with ≥ N_MIN H1-passing units, compute
     the Spearman partial correlation of {rep_med, ks_gue_med} vs
     {OSI, DSI, F1/F0} controlling for mean firing rate.
  2. Aggregate across recordings via Fisher-Z meta-analysis:
       - Fisher-Z transform: z_i = arctanh(rho_i)
       - Pooled fixed-effect:  z_pool = sum(w_i z_i) / sum(w_i),
                                w_i = n_i - 3 (effective sample size)
       - Random-effect (DerSimonian-Laird):  add tau^2 from Q statistic
       - Back-transform: rho_pool = tanh(z_pool)
  3. Compare to Phase 22a global partial correlation (the reference).

The N_MIN ≥ 20 floor is conservative: Spearman partial correlation on
< 20 points is too noisy to enter the pool, and Phase 22a's recording
counts (per-recording H1-passing counts: 57 to 109 for the grating
recordings; that's the relevant subset since OSI/DSI/F1F0 only exist
for grating-driven units) all comfortably exceed it.

Outputs:
  data/phase22b_results/pass_a_per_recording.parquet
  data/phase22b_results/pass_a_meta_analysis.parquet
  Stdout: per-recording table + meta-analytic aggregates + verdict.
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

ARS_PATH = OUT_DIR_22A / 'h1_classifications.parquet'
FUNC_PATH = OUT_DIR_22A / 'h1_functional.parquet'
GLOBAL_PATH = OUT_DIR_22A / 'h1_crossval_summary.parquet'

N_MIN = 20

DESCRIPTORS = [('osi', 'OSI'), ('dsi', 'DSI'), ('f1_f0_pref', 'F1/F0')]
ARS_METRICS = [('rep_med', 'rep_med'), ('ks_gue_med', 'ks_gue_med')]


def _partial_spearman(x, y, z) -> tuple[float, float, int]:
    """Spearman partial correlation rho(x, y | z) and a p-value via the
    Fisher-Z (n - 3) approximation."""
    df = pd.DataFrame({'x': x, 'y': y, 'z': z}).dropna()
    n = len(df)
    if n < 10:
        return (float('nan'), float('nan'), n)
    rxy, _ = spearmanr(df['x'], df['y'])
    rxz, _ = spearmanr(df['x'], df['z'])
    ryz, _ = spearmanr(df['y'], df['z'])
    denom = np.sqrt(max((1 - rxz**2) * (1 - ryz**2), 1e-15))
    if denom <= 0:
        return (float('nan'), float('nan'), n)
    rho = (rxy - rxz * ryz) / denom
    if n <= 4:
        return (float(rho), float('nan'), n)
    t_stat = rho * np.sqrt((n - 3) / max(1 - rho**2, 1e-15))
    p = 2 * (1 - student_t.cdf(abs(t_stat), df=n - 3))
    return (float(rho), float(p), n)


def fisher_z(rho: float) -> float:
    return float(np.arctanh(np.clip(rho, -0.999999, 0.999999)))


def inv_fisher_z(z: float) -> float:
    return float(np.tanh(z))


def meta_analyse(rhos: list[float], ns: list[int]) -> dict:
    """Fisher-Z meta-analysis (fixed and random effect).

    weights w_i = n_i - 3 (the inverse variance of arctanh(r) under
    Fisher's approximation).
    """
    rhos = np.asarray(rhos, dtype=np.float64)
    ns = np.asarray(ns, dtype=np.float64)
    keep = (~np.isnan(rhos)) & (ns >= N_MIN)
    if not keep.any():
        return dict(n_studies=0, fixed_rho=np.nan, fixed_z=np.nan,
                    random_rho=np.nan, random_z=np.nan,
                    Q=np.nan, I2=np.nan, tau2=np.nan)
    rhos = rhos[keep]
    ns = ns[keep]
    zs = np.array([fisher_z(r) for r in rhos])
    w = ns - 3
    z_pool = float(np.sum(w * zs) / np.sum(w))
    # Q statistic for heterogeneity (DerSimonian-Laird tau^2)
    Q = float(np.sum(w * (zs - z_pool) ** 2))
    k = len(rhos)
    if k <= 1:
        tau2 = 0.0
    else:
        denom = np.sum(w) - np.sum(w ** 2) / np.sum(w)
        tau2 = max(0.0, (Q - (k - 1)) / max(denom, 1e-12))
    w_re = 1.0 / (1.0 / w + tau2)
    z_pool_re = float(np.sum(w_re * zs) / np.sum(w_re))
    I2 = float(max(0.0, (Q - (k - 1)) / max(Q, 1e-12)) * 100.0) if k > 1 else 0.0
    return dict(
        n_studies=int(k),
        fixed_rho=inv_fisher_z(z_pool), fixed_z=z_pool,
        random_rho=inv_fisher_z(z_pool_re), random_z=z_pool_re,
        Q=Q, I2=I2, tau2=tau2,
    )


def main():
    print("=" * 72)
    print("Phase 22b Pass A — Recording-blocked H1 partial correlation")
    print("=" * 72)

    ars = pd.read_parquet(ARS_PATH)
    func = pd.read_parquet(FUNC_PATH)
    j = ars.merge(func, on=['recording', 'unit_idx', 'subset',
                              'monkey', 'unit_id'])
    print(f"  joined units: {len(j)}")

    # The functional descriptors live on grating recordings only.
    # gratings_movie has osi_movie / dsi_movie (different stimulus paradigm).
    # Restrict to drifting-grating recordings for OSI/DSI/F1F0; restrict to
    # gratings_movie for movie-tuning curves separately.
    grat = j[j['subset'] == 'gratings'].copy()
    print(f"  drifting-grating recordings: "
          f"{sorted(grat['recording'].unique())}")
    print()

    # Per-recording analysis on the grating subset
    rows = []
    for rec_name, group in grat.groupby('recording', sort=False):
        n_unit = len(group)
        for descriptor, dlabel in DESCRIPTORS:
            for ars_col, alabel in ARS_METRICS:
                if descriptor not in group: continue
                if 'mean_rate' not in group: continue
                rho, p, n = _partial_spearman(
                    group[ars_col].to_numpy(),
                    group[descriptor].to_numpy(),
                    group['mean_rate'].to_numpy(),
                )
                rows.append(dict(
                    recording=rec_name, n_units=n,
                    descriptor=dlabel, ars_metric=alabel,
                    spearman_partial=rho, p_partial=p,
                ))
    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR_22B / 'pass_a_per_recording.parquet', index=False)
    print(f"  → {OUT_DIR_22B}/pass_a_per_recording.parquet  "
          f"({len(df)} rows)")
    print()

    # Per-recording table
    pivot = df.pivot_table(index=['recording', 'n_units'],
                            columns=['descriptor', 'ars_metric'],
                            values='spearman_partial')
    print("Per-recording partial correlations:")
    print(pivot.round(3).to_string())
    print()

    # Meta-analysis per (descriptor, ARS metric) cell
    meta_rows = []
    for descriptor, dlabel in DESCRIPTORS:
        for ars_col, alabel in ARS_METRICS:
            sub = df[(df['descriptor'] == dlabel) &
                       (df['ars_metric'] == alabel)]
            if not len(sub): continue
            ma = meta_analyse(sub['spearman_partial'].tolist(),
                                sub['n_units'].tolist())
            meta_rows.append(dict(descriptor=dlabel, ars_metric=alabel,
                                    **ma))
    meta_df = pd.DataFrame(meta_rows)
    meta_df.to_parquet(OUT_DIR_22B / 'pass_a_meta_analysis.parquet',
                        index=False)
    print(f"  → {OUT_DIR_22B}/pass_a_meta_analysis.parquet  "
          f"({len(meta_df)} rows)")
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
            fixed_rho = float(mr['fixed_rho'].iloc[0])
            random_rho = float(mr['random_rho'].iloc[0])
            shrink = (1 - abs(fixed_rho) / max(abs(global_rho), 1e-9)) * 100
            cmp_rows.append(dict(
                descriptor=dlabel, ars_metric=alabel,
                global_22a=global_rho,
                meta_fixed=fixed_rho, meta_random=random_rho,
                pct_shrink_fixed=shrink,
                I2=float(mr['I2'].iloc[0]),
            ))
    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_parquet(OUT_DIR_22B / 'pass_a_comparison.parquet', index=False)
    print("Comparison vs Phase 22a global partial correlation:")
    print(cmp_df.round(3).to_string(index=False))
    print()
    # Verdict
    print("Verdict:")
    headline = cmp_df[(cmp_df['descriptor'] == 'OSI') &
                       (cmp_df['ars_metric'] == 'ks_gue_med')]
    if len(headline):
        h = headline.iloc[0]
        shrink = h['pct_shrink_fixed']
        if shrink < 25 and abs(h['meta_fixed']) > 0.5 * abs(h['global_22a']):
            print(f"  HEADLINE (OSI ↔ ks_gue_med): meta-fixed ρ = "
                  f"{h['meta_fixed']:+.3f}  vs Phase 22a global ρ = "
                  f"{h['global_22a']:+.3f}  →  PASS (within 25% shrink)")
        elif shrink < 50:
            print(f"  HEADLINE (OSI ↔ ks_gue_med): meta-fixed ρ = "
                  f"{h['meta_fixed']:+.3f}  vs Phase 22a global ρ = "
                  f"{h['global_22a']:+.3f}  →  SOFT PASS (≤50% shrink)")
        else:
            print(f"  HEADLINE (OSI ↔ ks_gue_med): meta-fixed ρ = "
                  f"{h['meta_fixed']:+.3f}  vs Phase 22a global ρ = "
                  f"{h['global_22a']:+.3f}  →  FAIL (>50% shrink)")


if __name__ == '__main__':
    main()
