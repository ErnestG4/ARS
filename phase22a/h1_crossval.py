"""
phase22a/h1_crossval.py — H1 cross-validation analysis.

Three sub-questions, each addressed separately:

  (A) Mutual information between ARS class and functional category.
      Builds a contingency table over the H1-passing units' (primary
      ARS quadrant, functional cluster) pairs and computes MI plus
      bootstrapped 95% CI.

  (B) Partial correlation against firing-rate baseline.
      Does ARS rep_med predict functional descriptors (OSI, DSI, F1/F0)
      beyond what mean firing rate predicts?  Spearman partial
      correlation: ρ(rep_med, descriptor | mean_rate).

  (C) Cross-stimulus consistency.
      For monkey1 and monkey2 the three movies (gratings_movie,
      natural_movie, noise_movie) share matched units (per pvc-11
      preprocessing).  Per unit, compare ARS classifications across
      the 3 movies: agreement rate, modal-quadrant stability, and
      rep_med correlation across movies.  This is the
      stimulus-invariance test required by H1.

Outputs:
  data/phase22a_results/h1_crossval_summary.parquet
  data/phase22a_results/h1_crossval_perunit.parquet
  Stdout: verdict per sub-question.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
ARS_PATH = OUT_DIR / 'h1_classifications.parquet'
FUNC_PATH = OUT_DIR / 'h1_functional.parquet'
SEL_PATH = OUT_DIR / 'unit_selection.parquet'

# Quadrants → ordinal numeric (for partial-correlation analyses)
QUAD_ORDINAL = {
    'BL': 0, 'TR': 1, 'TL': 2,
    'BR_artifact': 3, 'BR_novel': 3,
    'ambiguous': np.nan, 'underpowered': np.nan,
}


# ─── (A) MI between ARS class and functional cluster ───────────────────────


def _mi_from_contingency(c: np.ndarray) -> float:
    """Discrete MI in bits from a contingency table (no smoothing)."""
    c = np.asarray(c, dtype=np.float64)
    n = c.sum()
    if n <= 0: return 0.0
    p_xy = c / n
    p_x = p_xy.sum(axis=1, keepdims=True)
    p_y = p_xy.sum(axis=0, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = p_xy / (p_x @ p_y + 1e-15)
        terms = np.where(p_xy > 0, p_xy * np.log2(ratio + 1e-15), 0.0)
    return float(np.sum(terms))


def _bootstrap_mi(joined: pd.DataFrame, x_col: str, y_col: str,
                   n_boot: int = 200, seed: int = 0) -> tuple[float, float, float]:
    """Bootstrap (median, lo95, hi95) MI on the (x_col, y_col) pair."""
    rng = np.random.default_rng(seed)
    sub = joined[[x_col, y_col]].dropna()
    if len(sub) < 20: return (np.nan, np.nan, np.nan)
    base = pd.crosstab(sub[x_col], sub[y_col]).to_numpy()
    base_mi = _mi_from_contingency(base)
    boot = np.zeros(n_boot)
    n = len(sub)
    sub = sub.reset_index(drop=True)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        s = sub.iloc[idx].reset_index(drop=True)
        ct = pd.crosstab(s[x_col], s[y_col]).to_numpy()
        boot[b] = _mi_from_contingency(ct)
    return base_mi, float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def mi_ars_vs_functional(joined: pd.DataFrame) -> pd.DataFrame:
    """Compute MI between ARS primary-quadrant and several functional
    partitions: simple/complex (F1/F0 ≷ 1), high/low OSI (median split),
    high/low DSI (median split)."""
    rows = []
    if 'f1_f0_pref' in joined:
        s = joined.dropna(subset=['primary', 'f1_f0_pref'])
        if len(s):
            s = s.copy()
            s['type_F1F0'] = (s['f1_f0_pref'] > 1.0).map({True: 'simple', False: 'complex'})
            mi, lo, hi = _bootstrap_mi(s, 'primary', 'type_F1F0')
            rows.append(dict(
                axis='simple_vs_complex',
                n_units=len(s),
                mi_bits=mi, mi_lo95=lo, mi_hi95=hi,
                ars_categories=s['primary'].nunique(),
                func_categories=s['type_F1F0'].nunique(),
            ))
    for axis_col, axis_label in [('osi', 'OSI'), ('dsi', 'DSI')]:
        if axis_col in joined:
            s = joined.dropna(subset=['primary', axis_col])
            if len(s) >= 20:
                s = s.copy()
                med = float(s[axis_col].median())
                s['axis_split'] = (s[axis_col] > med).map({True: 'high', False: 'low'})
                mi, lo, hi = _bootstrap_mi(s, 'primary', 'axis_split')
                rows.append(dict(
                    axis=f'{axis_label}_high_vs_low_split{med:.3f}',
                    n_units=len(s),
                    mi_bits=mi, mi_lo95=lo, mi_hi95=hi,
                    ars_categories=s['primary'].nunique(),
                    func_categories=2,
                ))
    return pd.DataFrame(rows)


# ─── (B) partial correlation rep_med vs functional | firing rate ───────────


def _partial_spearman(x, y, z) -> tuple[float, float]:
    """Spearman partial correlation ρ(x, y | z) and its p-value."""
    df = pd.DataFrame({'x': x, 'y': y, 'z': z}).dropna()
    if len(df) < 10: return (np.nan, np.nan)
    rxy, _ = spearmanr(df['x'], df['y'])
    rxz, _ = spearmanr(df['x'], df['z'])
    ryz, _ = spearmanr(df['y'], df['z'])
    denom = np.sqrt(max((1 - rxz**2) * (1 - ryz**2), 1e-15))
    if denom <= 0: return (np.nan, np.nan)
    rho = (rxy - rxz * ryz) / denom
    n = len(df)
    if n <= 4: return (rho, np.nan)
    # Approximate p via t-distribution (Fisher z-transform)
    from scipy.stats import t as student_t
    t_stat = rho * np.sqrt((n - 3) / max(1 - rho**2, 1e-15))
    p = 2 * (1 - student_t.cdf(abs(t_stat), df=n - 3))
    return (float(rho), float(p))


def partial_corr_table(joined: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for descriptor in ['osi', 'dsi', 'f1_f0_pref']:
        if descriptor not in joined.columns: continue
        for ars_metric in ['rep_med', 'ks_gue_med']:
            sub = joined.dropna(subset=[descriptor, ars_metric, 'mean_rate'])
            if len(sub) < 20: continue
            r_raw, p_raw = spearmanr(sub[ars_metric], sub[descriptor])
            r_par, p_par = _partial_spearman(sub[ars_metric], sub[descriptor],
                                              sub['mean_rate'])
            rows.append(dict(
                descriptor=descriptor, ars_metric=ars_metric,
                n_units=len(sub),
                spearman_raw=float(r_raw), p_raw=float(p_raw),
                spearman_partial=r_par, p_partial=p_par,
            ))
    return pd.DataFrame(rows)


# ─── (C) cross-stimulus consistency ────────────────────────────────────────


def cross_stim_consistency(ars_df: pd.DataFrame) -> pd.DataFrame:
    """Per (monkey, unit_id), compare ARS classifications across the
    3 matched movies.  Returns one row per unit with agreement
    counts, modal-quadrant stability, and rep_med variance."""
    movies = ['gratings_movie', 'natural_movie', 'noise_movie']
    sel = ars_df[ars_df['subset'].isin(movies)].copy()
    if not len(sel): return pd.DataFrame()

    # Pivot per (monkey, unit_id) → primary per movie
    rows = []
    for (monkey, unit_id), g in sel.groupby(['monkey', 'unit_id']):
        present = {row['subset']: row for _, row in g.iterrows()}
        if len(present) < 2: continue
        prim = {m: present[m]['primary'] for m in movies if m in present}
        rep = {m: present[m]['rep_med'] for m in movies if m in present}
        # Treat BR_novel/BR_artifact as one for stability
        norm_prim = {m: ('BR' if v.startswith('BR') else v)
                     for m, v in prim.items()}
        n_unique = len(set(norm_prim.values()))
        stable = (n_unique == 1)
        rep_arr = np.array([v for v in rep.values() if not np.isnan(v)])
        rep_var = float(rep_arr.std()) if rep_arr.size >= 2 else np.nan
        rep_mean = float(rep_arr.mean()) if rep_arr.size else np.nan
        rows.append(dict(
            monkey=monkey, unit_id=unit_id,
            n_movies_present=len(present),
            primary_gratings_movie=norm_prim.get('gratings_movie'),
            primary_natural_movie=norm_prim.get('natural_movie'),
            primary_noise_movie=norm_prim.get('noise_movie'),
            n_unique_quadrants=n_unique,
            stable=stable,
            rep_med_mean=rep_mean,
            rep_med_std=rep_var,
        ))
    return pd.DataFrame(rows)


# ─── orchestrator ──────────────────────────────────────────────────────────


def main():
    print("=" * 72)
    print("Phase 22a H1 — cross-validation analysis")
    print("=" * 72)

    if not ARS_PATH.exists():
        print(f"  Missing {ARS_PATH} — run h1_per_unit_ars.py first.")
        return 1

    ars = pd.read_parquet(ARS_PATH)
    func = pd.read_parquet(FUNC_PATH)
    print(f"  ars rows:  {len(ars)}")
    print(f"  func rows: {len(func)}")

    # Join on (recording, unit_idx)
    joined = ars.merge(func, on=['recording', 'unit_idx', 'subset',
                                    'monkey', 'unit_id'],
                       how='inner', suffixes=('_ars', '_func'))
    print(f"  joined:    {len(joined)}")
    # mean_rate exists on both; use the func version (per-condition)
    if 'mean_rate_func' in joined.columns:
        joined['mean_rate'] = joined['mean_rate_func']

    # ─── (A) MI ──
    print()
    print("(A) MI between ARS quadrant and functional partitions")
    mi_df = mi_ars_vs_functional(joined)
    print(mi_df.to_string(index=False) if len(mi_df) else "  (no rows)")

    # ─── (B) partial correlation ──
    print()
    print("(B) Spearman partial correlation: ARS metric ↔ descriptor | firing rate")
    pc_df = partial_corr_table(joined)
    print(pc_df.to_string(index=False) if len(pc_df) else "  (no rows)")

    # ─── (C) cross-stimulus consistency on the 3 movies ──
    print()
    print("(C) Cross-stimulus consistency on matched-unit movie set")
    cc_df = cross_stim_consistency(ars)
    if len(cc_df):
        n = len(cc_df)
        n_three = int((cc_df['n_movies_present'] == 3).sum())
        n_stable = int(cc_df['stable'].sum())
        n_stable_three = int(((cc_df['n_movies_present'] == 3) & cc_df['stable']).sum())
        rep_corr = cc_df.dropna(subset=['rep_med_std'])
        print(f"  units in cross-stimulus pool: {n}")
        print(f"  units with all 3 movies:      {n_three}")
        print(f"  stable (single quadrant):     {n_stable}/{n} = "
              f"{n_stable/max(n,1)*100:.1f}%")
        print(f"  stable AND 3-movie:           {n_stable_three}/{n_three} = "
              f"{n_stable_three/max(n_three,1)*100:.1f}%")
        print(f"  rep_med std across movies (median, when ≥2 movies): "
              f"{rep_corr['rep_med_std'].median():.3f}")
        # Quadrant transition matrix (gratings_movie → natural_movie)
        triple = cc_df[cc_df['n_movies_present'] == 3].copy()
        if len(triple):
            ct = pd.crosstab(triple['primary_gratings_movie'],
                              triple['primary_natural_movie'])
            print()
            print("  Transition table (rows: gratings_movie, cols: natural_movie):")
            print(ct.to_string())

    # Save outputs
    summary_rows = []
    for _, r in mi_df.iterrows():
        summary_rows.append({'family': 'MI', **r.to_dict()})
    for _, r in pc_df.iterrows():
        summary_rows.append({'family': 'partial_corr', **r.to_dict()})
    pd.DataFrame(summary_rows).to_parquet(OUT_DIR / 'h1_crossval_summary.parquet',
                                            index=False)
    if len(cc_df):
        cc_df.to_parquet(OUT_DIR / 'h1_crossval_perunit.parquet', index=False)
    print()
    print(f"  → {OUT_DIR}/h1_crossval_summary.parquet")
    print(f"  → {OUT_DIR}/h1_crossval_perunit.parquet")


if __name__ == '__main__':
    main()
