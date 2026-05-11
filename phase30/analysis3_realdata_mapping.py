"""
phase30/analysis3_realdata_mapping.py — Phase 30 Analysis 3: locate
real-data ARS classifications on the Kuramoto (K, σ) phase-space map
produced by Analysis 2.

Per Phase 30 brief:
  Step 1 — assemble real-data classification summaries.  pvc-11
    monkey1_natural_movie + monkey2_gratings_movie (Phase 22a),
    Allen sessions (Phase 24 Full), local-cluster classifications
    (Phase 27 Analysis 3).
  Step 2 — locate each real-data point in the Kuramoto phase-space
    map.  Match on per-osc / aggregate modal classification + Euclidean
    distance in (ks_gue_med, rep_med) coordinates.  Report match
    quality (clean / ambiguous / no match).
  Step 3 — cross-reference real-data findings with Kuramoto-region
    predictions.

Outputs:
  data/phase30_results/analysis3_realdata_summary.parquet
  data/phase30_results/analysis3_kuramoto_match.parquet
  data/phase30_results/analysis3_verdict.json
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

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase30_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── Real-data ETL ─────────────────────────────────────────────────────


def load_pvc11() -> pd.DataFrame:
    """Phase 22a H2 population classifications at q_max=30."""
    p = Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'h2_population_classifications.parquet'
    df = pd.read_parquet(p)
    df = df[df['q_max'] == 30].copy()
    df = df.rename(columns={'recording': 'label'})
    df['source'] = 'phase22a_pvc11'
    df['scale'] = 'recording_wide_aggregate'
    df['n_units'] = df['n_units']
    return df[['source', 'label', 'subset', 'monkey', 'n_units', 'n_events',
                 'event_rate_hz', 'primary', 'rep_med', 'ks_gue_med', 'n_well',
                 'scale']]


def load_allen() -> pd.DataFrame:
    """Phase 24 per-session H2 (Allen Brain Observatory NP), default config."""
    p = Path(ROOT_DIR) / 'data' / 'phase24_results' / 'per_session_h2_population.parquet'
    df = pd.read_parquet(p)
    df = df[(df['config'] == 'default')].copy()
    df['source'] = 'phase24_allen'
    df['scale'] = 'recording_wide_aggregate'
    df['label'] = df.apply(
        lambda r: f"{r['session_id']}_{r['cre_line']}_{r['condition']}", axis=1)
    df['event_rate_hz'] = df['event_rate_hz']
    return df[['source', 'label', 'session_id', 'cre_line', 'condition',
                 'n_units', 'n_events', 'event_rate_hz', 'primary',
                 'rep_med', 'ks_gue_med', 'n_well', 'scale']]


def load_phase27_local_clusters() -> pd.DataFrame:
    """Phase 27 Analysis 3 — per-local-cluster classifications on pvc-11
    (CONTRA-OHIORHENUAN cluster results)."""
    p = Path(ROOT_DIR) / 'data' / 'phase27_results' / 'analysis3_per_cluster_real.parquet'
    df = pd.read_parquet(p)
    df['source'] = 'phase27_local_cluster'
    df['scale'] = 'local_cluster'
    df['label'] = df.apply(
        lambda r: f"{r['session']}_cluster{r['cluster_idx']:03d}_n{r['n_members']}", axis=1)
    return df[['source', 'label', 'session', 'cluster_idx', 'n_members',
                 'k_thresh', 'n_events', 'primary', 'rep_med',
                 'ks_gue_med', 'n_well', 'scale']]


def assemble_realdata() -> pd.DataFrame:
    pvc = load_pvc11()
    allen = load_allen()
    p27 = load_phase27_local_clusters()
    print(f"  pvc-11 (Phase 22a):           {len(pvc)} recordings")
    print(f"  Allen (Phase 24 default):     {len(allen)} session×conditions")
    print(f"  Local cluster (Phase 27):     {len(p27)} clusters")
    keep_cols = ['source', 'label', 'scale', 'n_events', 'primary',
                  'rep_med', 'ks_gue_med', 'n_well']
    return pd.concat([pvc[keep_cols], allen[keep_cols], p27[keep_cols]],
                      ignore_index=True)


# ─── Kuramoto map loading ──────────────────────────────────────────────


def load_kuramoto_map() -> pd.DataFrame:
    """Load Analysis 2 per-cell summary."""
    p = OUT_DIR / 'analysis2_summary_by_cell.parquet'
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found — run analysis2_Ksigma_phase_space.py first.")
    return pd.read_parquet(p)


# ─── Match-on-map ──────────────────────────────────────────────────────


# Tunable thresholds for match-quality discrimination.
DIST_CLEAN = 0.10        # ≤ this → clean match in (ks, rep) space
DIST_AMBIG_FACTOR = 1.5  # ratio nearest:second-nearest > this → unique


def locate_on_map(real_row, kmap: pd.DataFrame) -> dict:
    """For a single real-data row, find the nearest Kuramoto (K, σ) cell.

    Match metric: Euclidean distance in (ks_gue_med, rep_med) joint space,
    additionally restricted to cells whose modal classification matches
    the real-data primary.  If no modal-matching cell exists, fall back to
    Euclidean over all cells with a `modal_mismatch` flag.
    """
    ks_r = real_row['ks_gue_med']
    rep_r = real_row['rep_med']
    if not np.isfinite(ks_r) or not np.isfinite(rep_r):
        return dict(label=real_row['label'], match_quality='underpowered',
                     nearest_K_factor=np.nan, nearest_sigma_factor=np.nan,
                     nearest_distance=np.nan, modal_match=False)
    primary = real_row['primary']

    # Restrict candidates to modal-matching aggregate cells where possible
    mod_cands = kmap[kmap['agg_modal'] == primary].copy()
    used_modal = True
    if len(mod_cands) == 0:
        mod_cands = kmap.copy()
        used_modal = False

    d = np.sqrt(
        (mod_cands['agg_ks_med'].values - ks_r) ** 2
        + (mod_cands['agg_rep_med'].values - rep_r) ** 2
    )
    order = np.argsort(d)
    nearest = mod_cands.iloc[order[0]]
    if len(d) > 1:
        ratio = d[order[1]] / max(d[order[0]], 1e-9)
    else:
        ratio = np.inf

    if d[order[0]] <= DIST_CLEAN and ratio > DIST_AMBIG_FACTOR and used_modal:
        match_quality = 'clean'
    elif d[order[0]] <= DIST_CLEAN and used_modal:
        match_quality = 'ambiguous'
    elif d[order[0]] <= DIST_CLEAN and not used_modal:
        match_quality = 'modal_mismatch_close'
    else:
        match_quality = 'no_match'

    return dict(
        label=real_row['label'], source=real_row['source'],
        scale=real_row['scale'], n_events=real_row.get('n_events', np.nan),
        primary_real=primary, rep_med_real=rep_r, ks_gue_med_real=ks_r,
        match_quality=match_quality, modal_match=used_modal,
        nearest_K_factor=float(nearest['K_factor']),
        nearest_sigma_factor=float(nearest['sigma_factor']),
        nearest_distance=float(d[order[0]]),
        nearest_modal=str(nearest['agg_modal']),
        nearest_ks_med=float(nearest['agg_ks_med']),
        nearest_rep_med=float(nearest['agg_rep_med']),
        nearest_order_param=float(nearest['order_param_mean']),
        next_distance=float(d[order[1]]) if len(d) > 1 else np.nan,
    )


def main():
    print("=" * 72)
    print("Phase 30 — Analysis 3: real-data location on Kuramoto map")
    print("=" * 72)

    print("\n--- Step 1: assemble real-data classification summaries ---")
    real_df = assemble_realdata()
    print(f"\nTotal real-data rows: {len(real_df)}")
    print(real_df.head().to_string())
    real_df.to_parquet(OUT_DIR / 'analysis3_realdata_summary.parquet', index=False)
    print(f"\n  → analysis3_realdata_summary.parquet  ({len(real_df)} rows)")

    print("\n--- Step 2: load Kuramoto (K, σ) map ---")
    kmap = load_kuramoto_map()
    print(f"  Map cells: {len(kmap)}")
    print(f"  K_factors:    {sorted(kmap['K_factor'].unique())}")
    print(f"  sigma_factors: {sorted(kmap['sigma_factor'].unique())}")

    print("\n--- Step 3: locate each real-data point on the map ---")
    rows = []
    for _, r in real_df.iterrows():
        rows.append(locate_on_map(r, kmap))
    match_df = pd.DataFrame(rows)
    match_df.to_parquet(OUT_DIR / 'analysis3_kuramoto_match.parquet', index=False)
    print(f"\n  → analysis3_kuramoto_match.parquet  ({len(match_df)} rows)\n")

    # Print per-finding match summary
    findings = {
        'pvc11_monkey1_natural_movie':
            real_df['label'] == 'monkey1_natural_movie',
        'pvc11_monkey2_gratings_movie':
            real_df['label'] == 'monkey2_gratings_movie',
        'pvc11_all_h2_passing':
            real_df['source'] == 'phase22a_pvc11',
        'allen_natural_movie_one':
            (real_df['source'] == 'phase24_allen')
            & (real_df['label'].str.contains('natural_movie_one', na=False)),
        'phase27_local_clusters':
            real_df['source'] == 'phase27_local_cluster',
    }
    finding_summary = []
    print("Per-finding location on Kuramoto (K_factor, sigma_factor) map:")
    for name, mask in findings.items():
        sub_real = real_df[mask].reset_index(drop=True)
        if len(sub_real) == 0:
            continue
        sub_match = match_df[match_df['label'].isin(sub_real['label'])]
        if len(sub_match) == 0:
            continue
        clean = (sub_match['match_quality'] == 'clean').sum()
        ambig = (sub_match['match_quality'] == 'ambiguous').sum()
        modal_mm = (sub_match['match_quality'] == 'modal_mismatch_close').sum()
        no_match = (sub_match['match_quality'] == 'no_match').sum()
        underp = (sub_match['match_quality'] == 'underpowered').sum()

        nm_str = (
            f"clean={clean}  ambig={ambig}  modal_mismatch_close={modal_mm}  "
            f"no_match={no_match}  underp={underp}"
        )
        Kf_med = float(sub_match['nearest_K_factor'].median())
        sf_med = float(sub_match['nearest_sigma_factor'].median())
        d_med = float(sub_match['nearest_distance'].median())
        modal_real_top = sub_match['primary_real'].value_counts().index[0]
        modal_nearest_top = sub_match['nearest_modal'].value_counts().index[0]
        print(f"  {name:38s}  n={len(sub_match):3d}  "
              f"primary={modal_real_top:13s} → "
              f"map-modal={modal_nearest_top:13s}  "
              f"K_med={Kf_med:.2f} σ_med={sf_med:.2f}  "
              f"d_med={d_med:.3f}  | {nm_str}")
        finding_summary.append(dict(
            finding=name, n=int(len(sub_match)), n_clean=int(clean),
            n_ambiguous=int(ambig), n_modal_mismatch_close=int(modal_mm),
            n_no_match=int(no_match), n_underpowered=int(underp),
            modal_real_top=modal_real_top, modal_nearest_top=modal_nearest_top,
            K_factor_median=Kf_med, sigma_factor_median=sf_med,
            distance_median=d_med,
        ))

    # ─── verdict ───
    n_clean = int((match_df['match_quality'] == 'clean').sum())
    n_ambig = int((match_df['match_quality'] == 'ambiguous').sum())
    n_modal_mm = int((match_df['match_quality'] == 'modal_mismatch_close').sum())
    n_no = int((match_df['match_quality'] == 'no_match').sum())
    n_underp = int((match_df['match_quality'] == 'underpowered').sum())
    n_total = len(match_df)
    frac_clean = n_clean / max(n_total - n_underp, 1)
    frac_no = (n_no + n_modal_mm) / max(n_total - n_underp, 1)

    if frac_clean >= 0.7:
        verdict = 'MECHANISTIC_INTERPRETATION_FOUND'
    elif frac_no >= 0.7:
        verdict = 'NO_MECHANISTIC_MATCH'
    elif n_clean >= 1 and n_no >= 1:
        verdict = 'PARTIAL_MATCH_ACROSS_FINDINGS'
    else:
        verdict = 'AMBIGUOUS_MATCH'

    summary = dict(
        verdict=verdict,
        n_total=n_total, n_clean=n_clean, n_ambiguous=n_ambig,
        n_modal_mismatch_close=n_modal_mm, n_no_match=n_no,
        n_underpowered=n_underp,
        frac_clean=float(frac_clean),
        frac_no_match_or_modal_mismatch=float(frac_no),
        finding_summaries=finding_summary,
    )
    with open(OUT_DIR / 'analysis3_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n  → analysis3_verdict.json")
    print(f"\nVERDICT: {verdict}")
    print(f"  clean={n_clean}  ambiguous={n_ambig}  "
          f"modal_mismatch_close={n_modal_mm}  no_match={n_no}  "
          f"underp={n_underp}  total={n_total}")
    print(f"  fraction_clean = {frac_clean:.2f}   "
          f"fraction_no_match = {frac_no:.2f}")


if __name__ == '__main__':
    main()
