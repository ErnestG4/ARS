"""
phase23/run_phase23_smoothing_diag.py — diagnostic on the
lightcurve-modulated Poisson surrogate's smoothing window.

Phase 23's targeted analysis showed real GRB 230307A has 22 of 40
sub-windows in t=26-30s post-trigger classified as TR uniformly
across ALL q-bands [1, 50]; the lightcurve-modulated Poisson
surrogate (with default 21-bin / ~21ms smoothing window) produces
only ~0.4 TR sub-windows per seed in the same time region.  The
TR signature is broadband, not narrowband at the 909 Hz q-band.

The most likely cause is the surrogate's smoothing kernel itself:
21ms smoothing destroys timing structure at <21ms (which is the
909 Hz timescale of 1.1ms and below).  This diagnostic re-runs
the surrogate with NO smoothing (window=1) and one with very
heavy smoothing (window=201, ~200ms).  If the TR sub-window
count is monotonic in smoothing window — confirmed: the "TR
excess" was a surrogate-smoothing artifact, not a positive
finding.

Outputs:
  data/phase23_results/phase23_smoothing_diag.parquet
  Stdout: smoothing-window scan summary.
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
sys.path.insert(0, THIS_DIR)

from lightcurve_modulated_surrogate import lightcurve_modulated_poisson
from run_phase23_targeted import (
    classify_subwindow, trajectory_classify, q_target_for,
    EVENT_NAME, TARGET_QPO_HZ, QPO_WINDOW_S, ANALYSIS_WINDOW_S,
    SUBWINDOW_S, Q_MAX, OUT_DIR, PANEL_DIR, N_PROC,
)


# Smoothing configurations to scan
# 1     = no smoothing (preserves all sub-bin structure)
# 5     = 5ms smoothing (above deadtime, below 909 Hz period)
# 21    = default Phase 21/23 (~21ms; the original surrogate config)
# 101   = ~100ms smoothing (heavy)
SMOOTHING_CONFIGS = [
    dict(label='lc_smooth_1',   window_bins=1),
    dict(label='lc_smooth_5',   window_bins=5),
    dict(label='lc_smooth_21',  window_bins=21),     # default (Phase 23 baseline)
    dict(label='lc_smooth_101', window_bins=101),
]
N_SEEDS_PER_CFG = 2     # smaller — diagnostic, not headline


def main():
    print("=" * 80)
    print("Phase 23 follow-up — surrogate smoothing-window scan diagnostic")
    print("=" * 80)
    print()

    # Real reference: TR sub-window count in 26-30s region
    real_traj = pd.read_parquet(OUT_DIR / 'phase23_targeted_classification.parquet')
    region = real_traj[(real_traj['sub_start_s'] >= 26.0)
                         & (real_traj['sub_start_s'] < 30.0)
                         & (real_traj['primary'] != 'underpowered')]
    n_real_tr = int((region['primary'] == 'TR').sum())
    n_real_total = int(len(region))
    print(f"Real reference (t=26-30s, well-powered): "
          f"{n_real_tr}/{n_real_total} TR sub-windows ({n_real_tr/n_real_total*100:.1f}%)")
    print()

    # Load pooled events
    p = PANEL_DIR / f'{EVENT_NAME}.parquet'
    df = pd.read_parquet(p, columns=['time_us'])
    times = df['time_us'].to_numpy()
    s_us = int(ANALYSIS_WINDOW_S[0] * 1e6)
    e_us = int(ANALYSIS_WINDOW_S[1] * 1e6)
    times = times[(times >= s_us) & (times < e_us)]

    rows = []
    for cfg in SMOOTHING_CONFIGS:
        for seed in range(N_SEEDS_PER_CFG):
            print(f"--- {cfg['label']}, seed {seed} ---")
            rng = np.random.default_rng(seed + 100)   # different from Phase 23 seeds
            t0 = time.time()
            sur_events = lightcurve_modulated_poisson(
                times, bin_us=1_000, smoothing_window=cfg['window_bins'],
                rng=rng)
            print(f"  surrogate events: {len(sur_events):,}  "
                  f"(generation ⏱{time.time()-t0:.0f}s)")
            t1 = time.time()
            traj = trajectory_classify(sur_events,
                                         ANALYSIS_WINDOW_S[0],
                                         ANALYSIS_WINDOW_S[1],
                                         label=f"{cfg['label']}_seed{seed}",
                                         progress_every=200)
            print(f"  trajectory ⏱{time.time()-t1:.0f}s")
            # Restrict to the diagnostic region
            reg = traj[(traj['sub_start_s'] >= 26.0)
                         & (traj['sub_start_s'] < 30.0)
                         & (traj['primary'] != 'underpowered')]
            n_tr = int((reg['primary'] == 'TR').sum())
            n_well = int(len(reg))
            rows.append(dict(
                config=cfg['label'], window_bins=cfg['window_bins'],
                seed=seed, n_well_in_region=n_well,
                n_tr_in_region=n_tr,
                fraction_tr=n_tr / max(n_well, 1),
                n_total_subwindows=int(len(traj)),
            ))
            print(f"  region [26, 30)s: {n_tr}/{n_well} TR "
                  f"({n_tr/max(n_well,1)*100:.1f}%)")
            print()

    out_df = pd.DataFrame(rows)
    out_df.to_parquet(OUT_DIR / 'phase23_smoothing_diag.parquet', index=False)
    print(f"  → {OUT_DIR}/phase23_smoothing_diag.parquet  ({len(out_df)} rows)")
    print()

    # Summary
    print("Summary — TR fraction in region [26, 30)s:")
    print(f"{'config':20s}  {'window_ms':>10s}  {'n_seeds':>7s}  "
          f"{'TR_frac mean ± std':>22s}")
    for cfg in SMOOTHING_CONFIGS:
        sub = out_df[out_df['config'] == cfg['label']]
        mean = sub['fraction_tr'].mean()
        std = sub['fraction_tr'].std()
        win_ms = cfg['window_bins']        # at bin_us=1000, window_bins ≈ ms
        print(f"  {cfg['label']:18s}  {win_ms:>10d}  {len(sub):>7d}  "
              f"{mean*100:>10.1f}% ± {std*100:.1f}%")
    print(f"  {'real (reference)':18s}  {'-':>10s}  {'-':>7s}  "
          f"{n_real_tr/n_real_total*100:>10.1f}%")
    print()
    print("Interpretation:")
    print("  - If TR_frac at smoothing=1 matches real (~55%) and TR_frac")
    print("    falls monotonically with smoothing → 'TR excess' was a")
    print("    surrogate-smoothing artifact, no QPO/structure finding.")
    print("  - If TR_frac at smoothing=1 is also low (~0%) → real signal")
    print("    that even the unsmoothed lightcurve doesn't reproduce.")


if __name__ == '__main__':
    main()
