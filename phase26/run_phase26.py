"""
phase26/run_phase26.py — Phase 26 orchestrator: per-(detector,
energy_channel) stratification on GRB 230307A's late-prompt TR region.

Pipeline:
  1.  calibrator zoo (verify_calibrators.py) — methodological commitment.
  2.  aspect angles (aspect_angles.compute_aspect_table) — TRIGDAT path.
  3.  energy binning (energy_binning.build_cell_table) — 8 quantile
       bands per detector.
  4.  per-cell classification (per_cell_classify.per_cell_classify) on
       [26, 30) s.
  5.  per-cell surrogate (per_cell_surrogate.per_cell_surrogate) —
       lightcurve-modulated Poisson at per-cell rates, 5 seeds.
  6.  cross-checks (cross_checks.{subwindow_stability,
       detector_pooling_persistence, time_window_control}).
  7.  statistical tests (statistical_tests.{test_within_detector_energy_variation,
       cross_detector_aspect_correlation, rate_dependence_within_energy,
       surrogate_survival, aggregate_verdict}).

Designed for stage-resume via the --stage flag.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase23'))
sys.path.insert(0, THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase26_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def stage_calibrators():
    """Re-verify calibrator zoo (Phase 22a script)."""
    from subprocess import run
    print("=" * 72)
    print("Stage 1 — calibrator zoo verification")
    print("=" * 72)
    res = run([sys.executable, '-u',
                str(Path(ROOT_DIR) / 'phase22a' / 'verify_calibrators.py')],
                capture_output=True, text=True, check=False)
    print(res.stdout)
    if res.returncode != 0:
        print("STDERR:", res.stderr)
    return res.returncode == 0


def stage_aspect():
    """Compute per-detector aspect angles from TRIGDAT."""
    from aspect_angles import compute_aspect_table
    trigdat = (Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'
                / 'raw' / 'bn230307656_aux'
                / 'glg_trigdat_all_bn230307656_v01.fit')
    if not trigdat.exists():
        raise FileNotFoundError(f"TRIGDAT missing at {trigdat}")
    df = compute_aspect_table(trigdat)
    df.to_parquet(OUT_DIR / 'detector_aspect.parquet', index=False)
    print(f"  → {OUT_DIR}/detector_aspect.parquet")


def stage_energy_binning():
    """Build per-detector quantile energy bands."""
    from energy_binning import build_cell_table
    panel = Path(ROOT_DIR) / 'data' / 'phase21_grb_panel' / 'GRB230307A.parquet'
    raw_dir = Path(ROOT_DIR) / 'data' / 'phase21_grb_panel' / 'raw' / 'bn230307656'
    df = build_cell_table(panel, raw_dir, 'bn230307656',
                            window_s=(26.0, 30.0), n_bands=8)
    df.to_parquet(OUT_DIR / 'energy_bands.parquet', index=False)
    print(f"  → {OUT_DIR}/energy_bands.parquet  ({len(df)} cells)")


def stage_per_cell_classify():
    """Per-(detector, band) ARS classification on [26, 30) s."""
    from per_cell_classify import per_cell_classify
    per_cell_classify()


def stage_per_cell_surrogate():
    """Per-(detector, band) lightcurve-modulated Poisson surrogate."""
    from per_cell_surrogate import per_cell_surrogate
    per_cell_surrogate()


def stage_cross_checks():
    """Sub-window stability, detector-pooling persistence, time-window
    control."""
    from cross_checks import (subwindow_stability, detector_pooling_persistence,
                                 time_window_control)
    print("=" * 72)
    print("Stage 6 — cross-checks")
    print("=" * 72)
    stab = subwindow_stability()
    print(f"  sub-window stability: {len(stab)} cells; "
          f"dominated-by-single: {stab['is_dominated_by_single'].mean()*100:.1f}%")
    pp = detector_pooling_persistence()
    print(f"  detector pooling persistence: per-cell aggregate vs "
          f"Phase 23 pooled, mean delta "
          f"{pp['aggregate_minus_pooled'].mean()*100:+.1f}%")
    print(f"  time-window control: re-classifying [10, 14) s...")
    time_window_control()


def stage_statistical_tests():
    """Three H_energy_band predictions + per-cell surrogate survival
    + aggregate verdict."""
    from statistical_tests import (test_within_detector_energy_variation,
                                       cross_detector_aspect_correlation,
                                       rate_dependence_within_energy,
                                       aggregate_verdict)
    print("=" * 72)
    print("Stage 7 — statistical tests + aggregate verdict")
    print("=" * 72)
    t1 = test_within_detector_energy_variation()
    print(f"  test 1 (within-detector Kruskal-Wallis): "
          f"{int(t1['reject_fdr'].sum())} / {len(t1)} detectors reject FDR")
    t2_df, t2_sum = cross_detector_aspect_correlation()
    print(f"  test 2 (cross-detector aspect): {t2_sum}")
    t3_df, t3_sum = rate_dependence_within_energy()
    print(f"  test 3 (rate within energy): {t3_sum}")

    # Surrogate survival: compare real vs surrogate per-cell TR fractions
    real_df = pd.read_parquet(OUT_DIR / 'per_cell_tr_summary.parquet')
    sur_path = OUT_DIR / 'per_cell_surrogate_summary.parquet'
    if sur_path.exists():
        sur_df = pd.read_parquet(sur_path)
        merged = real_df.merge(sur_df, on=['detector', 'band_idx'], how='left')
        merged['real_above_p95'] = (
            merged['tr_fraction'] > merged['surr_tr_p95']).astype(int)
        merged['real_below_p05'] = (
            merged['tr_fraction'] < merged['surr_tr_p05']).astype(int)
        merged['real_in_surr_band'] = (
            (merged['tr_fraction'] >= merged['surr_tr_p05']) &
            (merged['tr_fraction'] <= merged['surr_tr_p95'])).astype(int)
        merged.to_parquet(OUT_DIR / 'per_cell_survival.parquet', index=False)
        valid = merged.dropna(subset=['tr_fraction', 'surr_tr_median'])
        n_above = int(valid['real_above_p95'].sum())
        n_total = len(valid)
        print(f"  surrogate survival: {n_above}/{n_total} cells with real "
              f"TR > surrogate 95th pct")
        surr_summary = dict(
            n_cells=int(n_total),
            n_real_above_surr_p95=n_above,
            n_real_below_surr_p05=int(valid['real_below_p05'].sum()),
            n_real_within_surr_band=int(valid['real_in_surr_band'].sum()),
            mean_real_minus_surr=float(
                (valid['tr_fraction'] - valid['surr_tr_median']).mean()),
        )
    else:
        surr_summary = dict(error='surrogate not run')
        print(f"  WARN: surrogate summary parquet missing, skipping survival")

    verdict = aggregate_verdict(t1, t2_sum, t3_sum)
    verdict['surrogate_survival'] = surr_summary

    with open(OUT_DIR / 'aggregate_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)

    print()
    print("Aggregate verdict (H_energy_band):")
    print(json.dumps(verdict, indent=2))


STAGES = {
    'calibrators': stage_calibrators,
    'aspect': stage_aspect,
    'energy_binning': stage_energy_binning,
    'per_cell_classify': stage_per_cell_classify,
    'per_cell_surrogate': stage_per_cell_surrogate,
    'cross_checks': stage_cross_checks,
    'statistical_tests': stage_statistical_tests,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', action='append',
                    choices=list(STAGES.keys()) + ['all'],
                    default=[],
                    help='Stage(s) to run; default all')
    args = p.parse_args()
    stages = args.stage or ['all']
    if 'all' in stages:
        stages = list(STAGES.keys())

    for s in stages:
        t0 = time.time()
        STAGES[s]()
        print(f"  [{s}] ⏱{time.time()-t0:.0f}s")
        print()


if __name__ == '__main__':
    main()
