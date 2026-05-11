"""
phase26/statistical_tests.py — three H_energy_band predictions.

Predictions (per brief):
  (1) Within-detector energy variation: TR fraction varies across
      bands within each detector.  Kruskal-Wallis test on the
      per-sub-window primary∈{TR, non-TR} flag, grouped by band, per
      detector.  FDR-adjusted across detectors (Benjamini-Hochberg
      α=0.05).

  (2) Cross-detector aspect-correlation at approximately-energy-
      aligned bands: each NaI detector contributes its (TR_fraction,
      aspect_angle) pair to each "energy bucket" defined by binning
      median photon energies across detectors.  Spearman correlation
      of TR fraction vs aspect angle per energy bucket.

  (3) Rate-dependence reduction within energy: for each energy bucket,
      Spearman correlation of TR fraction vs per-detector event rate.
      If the inverse-rate effect from Phase 23 was mediated by
      energy-band sensitivity, this within-bucket correlation should
      be weaker than the across-detector pooled correlation.

The H_energy_band aggregate verdict aggregates the three predictions
per the Phase 26 brief's CONFIRMED / PARTIALLY-CONFIRMED / FALSIFIED
schema.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase26_results'

FDR_ALPHA = 0.05
NaI_DETECTORS = ['n0', 'n1', 'n2', 'n5', 'n6', 'n7', 'n8', 'n9', 'na', 'nb']


def _fdr_bh(pvals: list[float], alpha: float = FDR_ALPHA) -> list[bool]:
    """Benjamini-Hochberg FDR correction.  Returns per-test reject flags."""
    n = len(pvals)
    if n == 0: return []
    idx = np.argsort(pvals)
    sorted_p = np.asarray(pvals)[idx]
    thresh = alpha * (np.arange(1, n + 1) / n)
    below = sorted_p <= thresh
    # Reject all up to the largest index with sorted_p <= thresh
    if not below.any():
        keep_n = 0
    else:
        keep_n = int(np.where(below)[0].max() + 1)
    reject = np.zeros(n, dtype=bool)
    reject[idx[:keep_n]] = True
    return reject.tolist()


def test_within_detector_energy_variation(
        per_subwindow_parquet: Path = None,
        ) -> pd.DataFrame:
    """Kruskal-Wallis: for each detector, test whether TR-vs-non-TR
    differs across band groups using each sub-window as an observation.

    Returns DataFrame: detector, n_bands_tested, kw_stat, p_value,
    n_well_total, reject_fdr.
    """
    per_subwindow_parquet = (per_subwindow_parquet
                                or OUT_DIR / 'per_cell_subwindow_classifications.parquet')
    df = pd.read_parquet(per_subwindow_parquet)
    df = df[df['primary'] != 'underpowered'].copy()
    df['is_tr'] = (df['primary'] == 'TR').astype(int)
    rows = []
    for d, sub in df.groupby('detector'):
        # Group by band, collect is_tr arrays
        groups = []
        for b, gsub in sub.groupby('band_idx'):
            if len(gsub) >= 5:
                groups.append(gsub['is_tr'].to_numpy())
        if len(groups) < 2:
            rows.append(dict(detector=d, n_bands_tested=len(groups),
                              kw_stat=float('nan'), p_value=float('nan'),
                              n_well_total=int(len(sub))))
            continue
        try:
            kw = stats.kruskal(*groups)
            kw_stat, p_value = float(kw.statistic), float(kw.pvalue)
        except Exception:
            kw_stat, p_value = float('nan'), float('nan')
        rows.append(dict(detector=d, n_bands_tested=len(groups),
                          kw_stat=kw_stat, p_value=p_value,
                          n_well_total=int(len(sub))))
    df_out = pd.DataFrame(rows)
    pvals = df_out['p_value'].fillna(1.0).tolist()
    df_out['reject_fdr'] = _fdr_bh(pvals, FDR_ALPHA)
    df_out.to_parquet(OUT_DIR / 'test1_within_detector_kruskal.parquet', index=False)
    return df_out


def cross_detector_aspect_correlation(
        per_cell_summary_path: Path = None,
        energy_bands_path: Path = None,
        aspect_path: Path = None,
        n_energy_buckets: int = 4,
        nai_only: bool = True,
        ) -> tuple[pd.DataFrame, dict]:
    """For each cross-detector energy bucket (binning median photon
    energies across NaI detectors), compute Spearman correlation of
    TR fraction vs aspect angle.

    Returns (per_bucket_df, summary_dict).
    """
    per_cell = pd.read_parquet(per_cell_summary_path
                                or OUT_DIR / 'per_cell_tr_summary.parquet')
    bands = pd.read_parquet(energy_bands_path
                               or OUT_DIR / 'energy_bands.parquet')
    aspect = pd.read_parquet(aspect_path
                                or OUT_DIR / 'detector_aspect.parquet')
    df = per_cell.merge(bands[['detector', 'band_idx', 'e_median_kev']],
                          on=['detector', 'band_idx'])
    df = df.merge(aspect[['detector', 'aspect_deg', 'detector_type']],
                    on='detector')
    if nai_only:
        df = df[df['detector_type'] == 'NaI']
    df = df[~df['tr_fraction'].isna()].copy()

    # Define cross-detector energy buckets using equal-quantile binning
    # over log(e_median_kev) so very-different energy regimes get equal
    # buckets.
    log_e = np.log10(df['e_median_kev'].clip(lower=1.0))
    quantiles = np.linspace(0, 1, n_energy_buckets + 1)
    edges = np.quantile(log_e, quantiles)
    df['energy_bucket'] = np.digitize(log_e, edges[1:-1])

    rows = []
    for b, sub in df.groupby('energy_bucket'):
        if len(sub) < 4:
            continue
        # Group within bucket (some buckets may have multiple bands per
        # detector — average TR fraction per detector within bucket)
        gp = (sub.groupby('detector')
                  .agg(tr_fraction=('tr_fraction', 'mean'),
                         aspect_deg=('aspect_deg', 'first'),
                         e_median_kev=('e_median_kev', 'mean'),
                         n_subwindows_well=('n_subwindows_well', 'sum'))
                  .reset_index())
        if len(gp) < 4:
            continue
        rho, p = stats.spearmanr(gp['aspect_deg'], gp['tr_fraction'])
        rows.append(dict(
            energy_bucket=int(b),
            n_detectors=int(len(gp)),
            e_med_lo_kev=float(sub['e_median_kev'].min()),
            e_med_hi_kev=float(sub['e_median_kev'].max()),
            spearman_rho=float(rho),
            p_value=float(p),
        ))
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(OUT_DIR / 'test2_cross_detector_aspect.parquet', index=False)
    if not len(df_out):
        return df_out, dict(verdict='INCONCLUSIVE',
                              reason='no_buckets_with_enough_detectors')

    # Summary: are correlations consistently in the same direction?
    rhos = df_out['spearman_rho'].dropna().to_numpy()
    direction = 'positive' if rhos.mean() > 0 else 'negative'
    any_sig = bool((df_out['p_value'] < 0.05).any())
    summary = dict(
        n_buckets=len(df_out),
        mean_rho=float(rhos.mean()) if rhos.size else float('nan'),
        direction=direction,
        any_significant=any_sig,
        verdict=('CORRELATED' if any_sig else 'NULL'),
    )
    return df_out, summary


def rate_dependence_within_energy(
        per_cell_summary_path: Path = None,
        energy_bands_path: Path = None,
        aspect_path: Path = None,
        n_energy_buckets: int = 4,
        ) -> tuple[pd.DataFrame, dict]:
    """For each cross-detector energy bucket, compute Spearman
    correlation of TR fraction vs per-detector event rate.

    Compare to the across-detector "pooled" rate correlation (from
    Phase 23 per-detector data, or recomputed here).  If energy-band
    sensitivity mediates the rate effect, within-bucket rho should be
    attenuated (closer to zero) than the across-bucket pooled rho.
    """
    per_cell = pd.read_parquet(per_cell_summary_path
                                or OUT_DIR / 'per_cell_tr_summary.parquet')
    bands = pd.read_parquet(energy_bands_path
                               or OUT_DIR / 'energy_bands.parquet')
    aspect = pd.read_parquet(aspect_path
                                or OUT_DIR / 'detector_aspect.parquet')
    df = per_cell.merge(bands[['detector', 'band_idx', 'e_median_kev']],
                          on=['detector', 'band_idx'])
    df = df.merge(aspect[['detector', 'aspect_deg', 'detector_type']],
                    on='detector')
    df = df[df['detector_type'] == 'NaI']
    df = df[~df['tr_fraction'].isna()].copy()

    # Use per-cell event count as rate proxy (events in [26, 30) s ÷ 4 s)
    df['rate_per_s'] = df['n_events_in_region'] / 4.0

    log_e = np.log10(df['e_median_kev'].clip(lower=1.0))
    quantiles = np.linspace(0, 1, n_energy_buckets + 1)
    edges = np.quantile(log_e, quantiles)
    df['energy_bucket'] = np.digitize(log_e, edges[1:-1])

    rows = []
    for b, sub in df.groupby('energy_bucket'):
        gp = (sub.groupby('detector')
                  .agg(tr_fraction=('tr_fraction', 'mean'),
                         rate_per_s=('rate_per_s', 'mean'),
                         aspect_deg=('aspect_deg', 'first'))
                  .reset_index())
        if len(gp) < 4: continue
        rho, p = stats.spearmanr(gp['rate_per_s'], gp['tr_fraction'])
        rows.append(dict(
            energy_bucket=int(b),
            n_detectors=int(len(gp)),
            spearman_rho_rate=float(rho), p_value_rate=float(p),
        ))
    bucket_df = pd.DataFrame(rows)
    bucket_df.to_parquet(OUT_DIR / 'test3_rate_within_energy.parquet', index=False)

    # Pooled (across all cells, all bucket info ignored) reference:
    gp_all = (df.groupby('detector')
                .agg(tr_fraction=('tr_fraction', 'mean'),
                       rate_per_s=('rate_per_s', 'mean'),
                       aspect_deg=('aspect_deg', 'first'))
                .reset_index())
    if len(gp_all) >= 4:
        rho_all, p_all = stats.spearmanr(gp_all['rate_per_s'], gp_all['tr_fraction'])
    else:
        rho_all, p_all = float('nan'), float('nan')

    mean_within_rho = (float(bucket_df['spearman_rho_rate'].mean())
                          if len(bucket_df) else float('nan'))
    attenuation = abs(rho_all) - abs(mean_within_rho)
    summary = dict(
        pooled_rho_rate=float(rho_all),
        pooled_p_rate=float(p_all),
        mean_within_bucket_rho=mean_within_rho,
        attenuation=float(attenuation),
        verdict=('ATTENUATED' if attenuation > 0.10
                  else 'NOT_ATTENUATED'),
    )
    return bucket_df, summary


def aggregate_verdict(test1_df: pd.DataFrame,
                        test2_summary: dict, test3_summary: dict,
                        ) -> dict:
    """Compose the H_energy_band aggregate verdict per the brief's
    CONFIRMED / PARTIALLY-CONFIRMED / FALSIFIED schema.

    CONFIRMED  : test1 significant ≥4 detectors, test2 CORRELATED,
                  test3 ATTENUATED.
    PARTIALLY  : some hold but not all.
    FALSIFIED  : test1 fails AND (test2 NULL OR test3 NOT_ATTENUATED).
    """
    n_t1_sig = int(test1_df['reject_fdr'].sum()) if len(test1_df) else 0
    t1_pass = n_t1_sig >= 4
    t2_pass = (test2_summary.get('verdict') == 'CORRELATED')
    t3_pass = (test3_summary.get('verdict') == 'ATTENUATED')

    n_pass = int(t1_pass) + int(t2_pass) + int(t3_pass)

    if n_pass == 3:
        verdict = 'CONFIRMED'
    elif n_pass == 0:
        verdict = 'FALSIFIED'
    else:
        verdict = 'PARTIALLY-CONFIRMED'

    return dict(
        h_energy_band_verdict=verdict,
        test1_within_detector_pass=bool(t1_pass),
        test1_n_significant=int(n_t1_sig),
        test2_cross_detector_aspect=str(test2_summary.get('verdict')),
        test2_mean_rho=test2_summary.get('mean_rho'),
        test3_rate_within_energy=str(test3_summary.get('verdict')),
        test3_pooled_rho=test3_summary.get('pooled_rho_rate'),
        test3_mean_within_rho=test3_summary.get('mean_within_bucket_rho'),
        test3_attenuation=test3_summary.get('attenuation'),
    )


def main():
    print("=" * 72)
    print("Phase 26 statistical tests — H_energy_band predictions")
    print("=" * 72)
    print()
    print("Test 1 — within-detector energy variation (Kruskal-Wallis, FDR α=0.05):")
    t1 = test_within_detector_energy_variation()
    print(t1.to_string(index=False))
    print()
    print("Test 2 — cross-detector aspect correlation at energy-aligned buckets (NaI only):")
    t2_df, t2_sum = cross_detector_aspect_correlation()
    print(t2_df.to_string(index=False))
    print(f"  Summary: {t2_sum}")
    print()
    print("Test 3 — rate dependence within energy buckets (NaI only):")
    t3_df, t3_sum = rate_dependence_within_energy()
    print(t3_df.to_string(index=False))
    print(f"  Summary: {t3_sum}")
    print()
    print("Aggregate verdict:")
    verdict = aggregate_verdict(t1, t2_sum, t3_sum)
    print(json.dumps(verdict, indent=2))
    with open(OUT_DIR / 'aggregate_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)


if __name__ == '__main__':
    main()
