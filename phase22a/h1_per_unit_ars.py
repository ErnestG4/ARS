"""
phase22a/h1_per_unit_ars.py — H1 per-unit ARS classification.

For every H1-passing (recording, unit) pair, run the ARS pipeline on
the concatenated spike-time stream for that unit.  For drifting-grating
recordings, both pooled-across-directions and per-direction
classifications are produced (per-direction is what enables direction-
selective consistency tests in H1 cross-validation).

Outputs:
  data/phase22a_results/h1_classifications.parquet   — pooled per (rec, unit)
  data/phase22a_results/h1_classifications_grating_dirs.parquet
                                                      — per direction × unit
                                                        for grating recordings

Parallelisation: one subprocess per (rec, unit) ARS call.  Uses
multiprocessing.Pool with imap_unordered so progress is incremental.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from loader import load, list_all_recordings
from ars_classify import classify, per_q_columns

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_PROC = 12

# Selection table built earlier
SELECTION_PATH = OUT_DIR / 'unit_selection.parquet'


def _classify_one(args):
    """Worker: load recording, extract one unit's spike stream, classify.

    Returns (recording, unit_idx, unit_id, condition_label, result_dict).
    `args` is (recording_name, unit_idx, condition).  condition is None
    for "pooled all conditions"; an int for grating-direction subselect;
    or a string movie kind (already implicit in the recording name).
    """
    recording_name, unit_idx, condition = args
    rec = load(recording_name)
    if condition is None:
        ev = rec.concatenated_spikes(unit_idx)
        cond_label = 'pooled'
    else:
        ev = rec.concatenated_spikes(unit_idx, condition=int(condition))
        cond_label = f'dir_{int(condition):02d}'
    res = classify(ev, return_full=True)
    cols = per_q_columns(res['per_q'])
    return dict(
        recording=recording_name,
        subset=rec.subset,
        monkey=rec.monkey,
        unit_idx=int(unit_idx),
        unit_id=rec.unit_id(unit_idx),
        condition=cond_label,
        primary=res['primary'],
        rep_med=res['rep_med'],
        ks_gue_med=res['ks_gue_med'],
        n_events_in=res['n_events_in'],
        n_events_used=res['n_events_used'],
        n_well=res['n_well'],
        **cols,
    )


def main():
    print("=" * 72)
    print("Phase 22a H1 — per-unit ARS classification")
    print("=" * 72)

    sel = pd.read_parquet(SELECTION_PATH)
    sel_h1 = sel[sel['h1_pass']].copy()
    print(f"H1-passing units: {len(sel_h1)} across "
          f"{sel_h1['recording'].nunique()} recordings")

    # Build the work list
    pooled_jobs = []
    dir_jobs = []
    for _, row in sel_h1.iterrows():
        pooled_jobs.append((row['recording'], int(row['unit_idx']), None))
        if row['subset'] == 'gratings':
            for d in range(12):
                dir_jobs.append((row['recording'], int(row['unit_idx']), d))

    print(f"  pooled jobs: {len(pooled_jobs)}")
    print(f"  per-direction jobs (grating recordings): {len(dir_jobs)}")
    total = len(pooled_jobs) + len(dir_jobs)
    print(f"  total ARS calls: {total}")
    print()

    # ─── Pooled ──
    rows_pooled = []
    t0 = time.time()
    with Pool(processes=N_PROC) as pool:
        for i, r in enumerate(pool.imap_unordered(_classify_one, pooled_jobs,
                                                    chunksize=4), start=1):
            rows_pooled.append(r)
            if i % 50 == 0 or i == len(pooled_jobs):
                rate = i / max(time.time() - t0, 1e-6)
                eta = (len(pooled_jobs) - i) / max(rate, 1e-6)
                print(f"  pooled  {i:5d}/{len(pooled_jobs)}  "
                      f"({rate:.1f}/s  ETA {eta:.0f}s)")

    df_pool = pd.DataFrame(rows_pooled)
    out_pool = OUT_DIR / 'h1_classifications.parquet'
    df_pool.to_parquet(out_pool, index=False)
    print(f"\n  → {out_pool}  ({len(df_pool)} rows)")

    # ─── Per-grating-direction ──
    rows_dir = []
    if dir_jobs:
        t0 = time.time()
        with Pool(processes=N_PROC) as pool:
            for i, r in enumerate(pool.imap_unordered(_classify_one, dir_jobs,
                                                        chunksize=8), start=1):
                rows_dir.append(r)
                if i % 200 == 0 or i == len(dir_jobs):
                    rate = i / max(time.time() - t0, 1e-6)
                    eta = (len(dir_jobs) - i) / max(rate, 1e-6)
                    print(f"  per-dir  {i:5d}/{len(dir_jobs)}  "
                          f"({rate:.1f}/s  ETA {eta:.0f}s)")
        df_dir = pd.DataFrame(rows_dir)
        out_dir = OUT_DIR / 'h1_classifications_grating_dirs.parquet'
        df_dir.to_parquet(out_dir, index=False)
        print(f"\n  → {out_dir}  ({len(df_dir)} rows)")

    # ─── Summary ──
    print()
    print(f"{'recording':35s}  {'units':>5s}  {'BL':>4s}  {'TR':>4s}  "
          f"{'BR':>4s}  {'TL':>4s}  {'amb':>4s}  {'und':>4s}")
    for rec, g in df_pool.groupby('recording', sort=False):
        c = g['primary'].value_counts()
        bl = int(c.get('BL', 0))
        tr = int(c.get('TR', 0))
        br = int(c.get('BR_artifact', 0)) + int(c.get('BR_novel', 0))
        tl = int(c.get('TL', 0))
        amb = int(c.get('ambiguous', 0))
        und = int(c.get('underpowered', 0))
        print(f"  {rec:35s}  {len(g):5d}  {bl:4d}  {tr:4d}  {br:4d}  "
              f"{tl:4d}  {amb:4d}  {und:4d}")


if __name__ == '__main__':
    main()
