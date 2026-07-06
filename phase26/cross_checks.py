"""
phase26/cross_checks.py — three required cross-checks for the
per-(detector, band) Phase 26 analysis:

(1) Sub-window stability — TR fractions stable within each cell across
    sub-windows, not driven by a single anomalous sub-window.

(2) Detector-pooling persistence — per-(detector, band) TR signal
    reproduces the per-detector signal from Phase 23 (re-aggregated
    across bands).

(3) Time-window control — repeat the per-cell classification on a
    control time window [10, 14) s (pre-TR-region) and confirm the
    TR signature is specific to [26, 30) s.
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
sys.path.insert(0, THIS_DIR)

from per_cell_classify import per_cell_classify


PANEL_DIR = Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase26_results'

CONTROL_REGION_S = (10.0, 14.0)


def subwindow_stability(per_subwindow_parquet: Path = None,
                          ) -> pd.DataFrame:
    """Per-cell within-cell sub-window stability:
      - n_sub_well, n_tr
      - tr_fraction
      - longest consecutive-TR run
      - fraction of sub-windows where modal quadrant != TR
      - is_dominated_by_single: True if removing the single highest-TR
        sub-window changes the TR fraction by > 25%
    """
    per_subwindow_parquet = (per_subwindow_parquet
                                or OUT_DIR / 'per_cell_subwindow_classifications.parquet')
    df = pd.read_parquet(per_subwindow_parquet)
    rows = []
    for (d, band), sub in df.groupby(['detector', 'band_idx']):
        well = sub[sub['primary'] != 'underpowered'].sort_values('sub_start_s')
        n_well = int(len(well))
        if n_well == 0:
            continue
        is_tr = (well['primary'] == 'TR').to_numpy()
        n_tr = int(is_tr.sum())
        # Longest consecutive TR run
        max_run = 0
        cur_run = 0
        for x in is_tr:
            if x:
                cur_run += 1
                max_run = max(max_run, cur_run)
            else:
                cur_run = 0
        # Drop-one test:
        # If we remove the single best sub-window, does the TR fraction
        # change substantially?  (Robustness check for "is the signal
        # driven by one anomalous sub-window?")
        is_dominated = False
        if n_tr > 0:
            tr_frac_full = n_tr / n_well
            tr_frac_drop = (n_tr - 1) / max(n_well - 1, 1)
            is_dominated = abs(tr_frac_full - tr_frac_drop) > 0.25
        rows.append(dict(
            detector=d, band_idx=int(band),
            n_subwindows_well=n_well, n_tr=n_tr,
            tr_fraction=n_tr / n_well,
            longest_tr_run=max_run,
            tr_run_to_n_well_ratio=max_run / n_well,
            is_dominated_by_single=bool(is_dominated),
        ))
    out = pd.DataFrame(rows)
    out.to_parquet(OUT_DIR / 'subwindow_stability.parquet', index=False)
    return out


def detector_pooling_persistence(per_cell_summary: pd.DataFrame = None,
                                    ) -> pd.DataFrame:
    """Aggregate per-(detector, band) TR fractions back to per-detector
    estimates, compare against Phase 23's per-detector parquet.

    Aggregate methods:
      mean_tr_across_bands: weighted by n_subwindows_well per band.
      max_tr_across_bands:  highest TR fraction across this detector's bands.

    Phase 23's per-detector parquet at phase23_per_detector.parquet has
    `tr_fraction` per detector (pooled across energy).  We compare:
      - the aggregate per-detector TR fraction from energy-split bands
      - the Phase 23 pooled per-detector TR fraction
    The hypothesis: per-(detector, band) signal aggregates to comparable
    or higher TR fractions than the pooled-detector measurement —
    suggesting pooling masks rather than reveals the signal.
    """
    per_cell_summary = (per_cell_summary
                         if per_cell_summary is not None
                         else pd.read_parquet(OUT_DIR / 'per_cell_tr_summary.parquet'))
    phase23_pd_path = (Path(ROOT_DIR) / 'data' / 'phase23_results'
                         / 'phase23_per_detector.parquet')
    if not phase23_pd_path.exists():
        ph23 = pd.DataFrame()
    else:
        ph23 = pd.read_parquet(phase23_pd_path)

    rows = []
    for d, sub in per_cell_summary.groupby('detector'):
        valid = sub[~sub['tr_fraction'].isna()]
        if not len(valid): continue
        w = valid['n_subwindows_well'].to_numpy().astype(float)
        f = valid['tr_fraction'].to_numpy()
        agg_mean = float(np.average(f, weights=w)) if w.sum() > 0 else float('nan')
        agg_max = float(f.max())
        # Look up Phase 23 pooled TR fraction for this detector
        ph23_row = ph23[(ph23['detector'] == d) & (ph23['kind'] == 'per_detector')]
        ph23_tr = (float(ph23_row['tr_fraction'].iloc[0])
                     if len(ph23_row) else float('nan'))
        rows.append(dict(
            detector=d,
            n_bands_with_signal=int(len(valid)),
            mean_tr_across_bands=agg_mean,
            max_tr_across_bands=agg_max,
            phase23_pooled_tr=ph23_tr,
            aggregate_minus_pooled=(
                agg_mean - ph23_tr if not np.isnan(ph23_tr) else float('nan')),
        ))
    out = pd.DataFrame(rows)
    out.to_parquet(OUT_DIR / 'detector_pooling_persistence.parquet', index=False)
    return out


def time_window_control(control_region_s: tuple = CONTROL_REGION_S):
    """Re-run per-cell classification on a control time window
    (pre-TR-region).  Confirms TR signature is specific to [26, 30) s
    and not a global feature of the burst.

    Returns the control window's per-cell summary DataFrame.
    """
    print(f"  classifying control window [{control_region_s[0]}, "
          f"{control_region_s[1]}) s")
    _, sum_df = per_cell_classify(region_s=control_region_s,
                                     out_prefix='control_')
    return sum_df


def main():
    print("=" * 72)
    print(f"Phase 26 cross-checks")
    print("=" * 72)

    print()
    print("(1) Sub-window stability:")
    stab = subwindow_stability()
    print(f"  {'det':3s}  {'band':>4s}  {'n_well':>6s}  {'TR':>3s}  "
          f"{'frac':>5s}  {'longest_run':>11s}  {'dominated?':>10s}")
    for _, r in stab.iterrows():
        print(f"  {r['detector']:3s}  {r['band_idx']:4d}  "
              f"{r['n_subwindows_well']:6d}  {r['n_tr']:3d}  "
              f"{r['tr_fraction']*100:4.0f}%  "
              f"{r['longest_tr_run']:11d}  {str(bool(r['is_dominated_by_single'])):>10s}")
    print(f"  fraction dominated-by-single: "
          f"{stab['is_dominated_by_single'].mean()*100:.1f}%")

    print()
    print("(2) Detector-pooling persistence:")
    pp = detector_pooling_persistence()
    print(f"  {'det':3s}  {'mean_tr':>7s}  {'max_tr':>6s}  {'phase23_pool':>11s}  "
          f"{'agg-pool':>8s}")
    for _, r in pp.iterrows():
        print(f"  {r['detector']:3s}  "
              f"{r['mean_tr_across_bands']*100:6.1f}%  "
              f"{r['max_tr_across_bands']*100:5.1f}%  "
              f"{r['phase23_pooled_tr']*100:10.1f}%  "
              f"{r['aggregate_minus_pooled']*100:+7.1f}%")

    print()
    print("(3) Time-window control on [10, 14) s:")
    ctrl = time_window_control()
    print(f"  control window TR fractions:")
    print(f"  {'det':3s}  " + "  ".join(f"{f'b{i}':>5s}" for i in range(8))
            + "  " + f"{'mean':>5s}")
    for d, sub in ctrl.groupby('detector'):
        fracs = [sub[sub['band_idx'] == b]['tr_fraction'].iloc[0]
                  if len(sub[sub['band_idx'] == b]) else float('nan')
                  for b in range(8)]
        m = float(np.nanmean(fracs))
        line = '  '.join(f"{f*100:5.1f}" if not np.isnan(f) else "    -"
                          for f in fracs)
        print(f"  {d:3s}  {line}  {m*100:5.1f}")


if __name__ == '__main__':
    main()
