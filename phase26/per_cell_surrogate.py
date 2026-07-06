"""
phase26/per_cell_surrogate.py — per-(detector, band) lightcurve-modulated
Poisson surrogate.

For each cell, generates `n_seeds` (default 5) lightcurve-modulated
Poisson surrogate streams preserving the cell's per-bin rate profile,
classifies each with the same Phase 23 100ms-sub-window machinery,
and aggregates per-seed TR fractions for comparison against the real
cell's TR fraction.

Same surrogate generator as Phase 23 — `lightcurve_modulated_poisson`
from `lightcurve_modulated_surrogate.py`.

The cell-level survival test: real per-cell TR fraction *not*
reproduced by surrogate (at p < 0.05 from the 5-seed surrogate
distribution) implies the cell's TR signature is beyond what
lightcurve-rate modulation alone explains.  Per-cell pooling rules
this out as a pooling artifact.
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
from lightcurve_modulated_surrogate import lightcurve_modulated_poisson
from energy_binning import assign_bands_to_events


PANEL_DIR = Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase26_results'

REGION_S = (26.0, 30.0)
EVENT_NAME = 'GRB230307A'
N_SEEDS = 5


def per_cell_surrogate(region_s: tuple = REGION_S,
                         n_seeds: int = N_SEEDS,
                         subwindow_s: float = SUBWINDOW_S,
                         q_max: int = Q_MAX,
                         bands_parquet: Path = None,
                         out_prefix: str = '',
                         ) -> pd.DataFrame:
    """Generate lightcurve-modulated surrogates per cell; classify; output
    per-cell surrogate TR fractions (one row per (detector, band, seed))
    plus aggregate per-cell statistics.

    Returns the per-(detector, band, seed) DataFrame; also writes
    per_cell_surrogate_summary.parquet with aggregated per-cell
    median / 5th-pct / 95th-pct of TR fraction across seeds.
    """
    bands_parquet = bands_parquet or (OUT_DIR / 'energy_bands.parquet')
    cell_table = pd.read_parquet(bands_parquet)
    panel = PANEL_DIR / f'{EVENT_NAME}.parquet'
    df = assign_bands_to_events(panel, cell_table)

    s_us = int(region_s[0] * 1_000_000)
    e_us = int(region_s[1] * 1_000_000)
    df_w = df[(df['time_us'] >= s_us) & (df['time_us'] < e_us)].copy()

    rows = []
    detectors = sorted(df_w['detector'].unique())
    print(f"  surrogate: {n_seeds} seeds × {len(detectors)} detectors × 8 bands")
    t_total = time.time()
    for d in detectors:
        for band in range(8):
            mask = (df_w['detector'].values == d) & (df_w['band_idx'].values == band)
            ev_us = df_w.loc[mask, 'time_us'].to_numpy()
            if ev_us.size < 100:
                continue
            for seed in range(n_seeds):
                rng = np.random.default_rng(int(1e6) + seed * 100
                                              + ord(d[0]) * 11 + band)
                t0 = time.time()
                surr_us = lightcurve_modulated_poisson(
                    ev_us, bin_us=1_000, smoothing_window=21, rng=rng)
                traj = trajectory_classify(surr_us, region_s[0], region_s[1],
                                              subwindow_s=subwindow_s,
                                              q_max=q_max,
                                              label=f'{d}__band{band}__seed{seed}',
                                              n_proc=N_PROC,
                                              progress_every=10_000)
                well = traj[traj['primary'] != 'underpowered']
                n_well = int(len(well))
                n_tr = int((well['primary'] == 'TR').sum())
                rows.append(dict(
                    detector=d, band_idx=band, seed=seed,
                    n_events=int(surr_us.size),
                    n_subwindows_well=n_well, n_tr=n_tr,
                    tr_fraction=(n_tr / max(n_well, 1)) if n_well else float('nan'),
                ))
                dt = time.time() - t0
                if seed == 0 or (seed == n_seeds - 1):
                    print(f"    {d} band{band} seed{seed}: "
                          f"n_evt={surr_us.size:5d}  TR={n_tr:3d}/{n_well}  "
                          f"({n_tr/max(n_well,1)*100:5.1f}%)  ⏱{dt:.1f}s",
                          flush=True)
    print(f"  total ⏱{time.time()-t_total:.0f}s")
    df_out = pd.DataFrame(rows)
    df_out.to_parquet(OUT_DIR / f'{out_prefix}per_cell_surrogate_seeds.parquet',
                       index=False)

    # Aggregate per-cell statistics
    summary = (df_out.groupby(['detector', 'band_idx'])['tr_fraction']
                  .agg(['median', lambda x: np.percentile(x, 5),
                          lambda x: np.percentile(x, 95), 'std'])
                  .reset_index())
    summary.columns = ['detector', 'band_idx', 'surr_tr_median',
                        'surr_tr_p05', 'surr_tr_p95', 'surr_tr_std']
    summary.to_parquet(OUT_DIR / f'{out_prefix}per_cell_surrogate_summary.parquet',
                        index=False)
    return df_out


def main():
    print("=" * 72)
    print(f"Phase 26 — per-(detector, energy_band) lightcurve-modulated "
          f"Poisson surrogate on GRB 230307A [{REGION_S[0]}, "
          f"{REGION_S[1]}) s")
    print("=" * 72)
    per_cell_surrogate()


if __name__ == '__main__':
    main()
