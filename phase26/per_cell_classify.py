"""
phase26/per_cell_classify.py — per-(detector, energy_band) ARS
classification on the t = [26, 30) s broadband-TR region of GRB
230307A.

For each cell, slides 100ms sub-windows across the region, runs
joint_q_profile + joint_quadrant_diagnostic at q_max=50 (Phase 23's
time-slice adjustment), and aggregates per-sub-window modal quadrant.

Outputs:
  per_cell_subwindow_classifications.parquet  : one row per
        (detector, band, sub-window) with the full per-q signature.
  per_cell_tr_summary.parquet                 : one row per
        (detector, band) cell with TR fraction + sub-window count.

Reuses Phase 23's classification machinery (classify_subwindow,
trajectory_classify, q_target_for) directly.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase23'))
sys.path.insert(0, THIS_DIR)

from run_phase23_targeted import (
    trajectory_classify, SUBWINDOW_S, Q_MAX, N_PROC,
)
from energy_binning import assign_bands_to_events


PANEL_DIR = Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase26_results'

REGION_S = (26.0, 30.0)
TRIGGER_ID = 'bn230307656'
EVENT_NAME = 'GRB230307A'


def per_cell_classify(region_s: tuple = REGION_S,
                        subwindow_s: float = SUBWINDOW_S,
                        q_max: int = Q_MAX,
                        bands_parquet: Path = None,
                        out_prefix: str = '',
                        ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run per-cell ARS classification on region_s.

    Returns (per_subwindow_df, per_cell_summary_df) and writes both to
    OUT_DIR as parquets.  `out_prefix` is prepended to the output
    filenames (e.g. 'region_26_30__' vs 'region_10_14__' for
    time-window controls).
    """
    bands_parquet = bands_parquet or (OUT_DIR / 'energy_bands.parquet')
    cell_table = pd.read_parquet(bands_parquet)

    # Annotate every event with its band_idx.
    panel = PANEL_DIR / f'{EVENT_NAME}.parquet'
    df = assign_bands_to_events(panel, cell_table)

    s_us = int(region_s[0] * 1_000_000)
    e_us = int(region_s[1] * 1_000_000)
    df_w = df[(df['time_us'] >= s_us) & (df['time_us'] < e_us)].copy()

    all_subwindow_rows = []
    summary_rows = []

    detectors = sorted(df_w['detector'].unique())
    print(f"  classifying per (detector, band) cell on [{region_s[0]}, "
          f"{region_s[1]}) s; sub_us={int(subwindow_s*1e6)}; q_max={q_max}")
    t_total = time.time()
    for d in detectors:
        for band in range(8):
            mask = (df_w['detector'].values == d) & (df_w['band_idx'].values == band)
            ev_us = df_w.loc[mask, 'time_us'].to_numpy()
            if ev_us.size < 100:
                # Too sparse; record as empty row in summary.
                summary_rows.append(dict(
                    detector=d, band_idx=band,
                    n_events_in_region=int(ev_us.size),
                    n_subwindows_well=0, n_tr=0, n_bl=0,
                    tr_fraction=float('nan'),
                ))
                continue
            t0 = time.time()
            traj = trajectory_classify(ev_us, region_s[0], region_s[1],
                                          subwindow_s=subwindow_s,
                                          q_max=q_max,
                                          label=f'{d}__band{band}',
                                          n_proc=N_PROC,
                                          progress_every=10_000)
            traj['detector'] = d
            traj['band_idx'] = band
            all_subwindow_rows.append(traj)

            well = traj[traj['primary'] != 'underpowered']
            n_well = int(len(well))
            n_tr = int((well['primary'] == 'TR').sum())
            n_bl = int((well['primary'] == 'BL').sum())
            summary_rows.append(dict(
                detector=d, band_idx=band,
                n_events_in_region=int(ev_us.size),
                n_subwindows_well=n_well, n_tr=n_tr, n_bl=n_bl,
                tr_fraction=(n_tr / max(n_well, 1)) if n_well else float('nan'),
            ))
            dt = time.time() - t0
            print(f"    {d} band{band}: n_evt={ev_us.size:5d}  "
                  f"well={n_well:3d}  TR={n_tr:3d}/{n_well} "
                  f"({n_tr/max(n_well,1)*100:5.1f}%)  ⏱{dt:.1f}s",
                  flush=True)
    dt_total = time.time() - t_total
    print(f"  total ⏱{dt_total:.0f}s")

    sub_df = (pd.concat(all_subwindow_rows, ignore_index=True)
                if all_subwindow_rows else pd.DataFrame())
    sub_df.to_parquet(OUT_DIR / f'{out_prefix}per_cell_subwindow_classifications.parquet',
                       index=False)
    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_parquet(OUT_DIR / f'{out_prefix}per_cell_tr_summary.parquet',
                       index=False)
    return sub_df, sum_df


def main():
    print("=" * 72)
    print(f"Phase 26 — per-(detector, energy_band) classification on "
          f"GRB 230307A [{REGION_S[0]}, {REGION_S[1]}) s")
    print("=" * 72)
    sub_df, sum_df = per_cell_classify()
    print()
    print("Summary by detector (sorted by detector):")
    print(f"  {'det':3s}  {'b0':>5s}  {'b1':>5s}  {'b2':>5s}  {'b3':>5s}  "
          f"{'b4':>5s}  {'b5':>5s}  {'b6':>5s}  {'b7':>5s}  "
          f"{'mean':>5s}")
    for d, sub in sum_df.groupby('detector'):
        fracs = [sub[sub['band_idx'] == b]['tr_fraction'].iloc[0]
                  if len(sub[sub['band_idx'] == b]) else float('nan')
                  for b in range(8)]
        m = float(np.nanmean(fracs))
        line = '  '.join(f"{f*100:5.1f}" if not np.isnan(f) else "    -"
                          for f in fracs)
        print(f"  {d:3s}  {line}  {m*100:5.1f}")


if __name__ == '__main__':
    main()
