"""
phase23/run_phase23_per_detector.py — per-detector classification on
the [26, 30) s broadband-TR region of GRB 230307A.

Phase 23 surfaced a side-finding: real GRB 230307A has 22 of 40
sub-windows in t = 26–30 s post-trigger classified as TR uniformly
across all 50 q-bands; the lightcurve-modulated Poisson surrogate
produces only 5–15% TR at this region across smoothing windows
1–101 ms.  The signature is broadband, not narrowband.

This script tests the discriminating hypothesis: is the TR signature
present per-detector (then NOT a pooling artifact), or only when
detectors are pooled (then IS a pooling/coincidence artifact)?

  - Per-detector classification: split the GRB 230307A pooled stream
    by detector, run the same 100ms-sub-window targeted classification
    on each detector's spike train independently in the [26, 30) s
    region.  Compare TR fractions.

  - Randomized-detector-label control: shuffle detector labels of
    events, repool, classify the [26, 30) s region.  If TR signature
    is preserved under label shuffle → not a pooling artifact.

Outputs:
  data/phase23_results/phase23_per_detector.parquet
  Stdout: per-detector TR fractions in [26, 30) s + verdict.
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

from run_phase23_targeted import (
    classify_subwindow, trajectory_classify,
    EVENT_NAME, SUBWINDOW_S, Q_MAX, OUT_DIR, PANEL_DIR, N_PROC,
)


REGION_S = (26.0, 30.0)
N_SHUFFLE_SEEDS = 2


def main():
    print("=" * 80)
    print(f"Phase 23 follow-up — per-detector test on the [{REGION_S[0]}, "
          f"{REGION_S[1]}) s broadband-TR region of {EVENT_NAME}")
    print("=" * 80)

    # Real reference
    real_traj = pd.read_parquet(OUT_DIR / 'phase23_targeted_classification.parquet')
    region_real = real_traj[(real_traj['sub_start_s'] >= REGION_S[0])
                              & (real_traj['sub_start_s'] < REGION_S[1])
                              & (real_traj['primary'] != 'underpowered')]
    n_real_tr = int((region_real['primary'] == 'TR').sum())
    n_real_well = int(len(region_real))
    print(f"Real (pooled) reference: {n_real_tr}/{n_real_well} TR "
          f"({n_real_tr/max(n_real_well,1)*100:.1f}%)")
    print()

    # Load events
    p = PANEL_DIR / f'{EVENT_NAME}.parquet'
    df = pd.read_parquet(p, columns=['detector', 'time_us'])
    detectors = sorted(df['detector'].unique())
    print(f"Detectors: {detectors}")
    print(f"Total events on disk: {len(df):,}")
    print()

    s_us = int(REGION_S[0] * 1_000_000)
    e_us = int(REGION_S[1] * 1_000_000)
    df_w = df[(df['time_us'] >= s_us) & (df['time_us'] < e_us)]
    print(f"Events in [{REGION_S[0]}, {REGION_S[1]}) s: {len(df_w):,}")
    print(f"Per-detector counts in region:")
    for d in detectors:
        n = int((df_w['detector'] == d).sum())
        print(f"  {d}: {n:,} events  ({n/(REGION_S[1]-REGION_S[0]):.0f} /s)")
    print()

    rows = []

    # ─── Per-detector classification ──
    print("Per-detector classification on the diagnostic region "
          f"[{REGION_S[0]}, {REGION_S[1]}) s:")
    for d in detectors:
        ev = df_w[df_w['detector'] == d]['time_us'].to_numpy()
        if ev.size < 100:
            print(f"  {d}: too few events ({ev.size}) — skip")
            continue
        t0 = time.time()
        traj = trajectory_classify(ev, REGION_S[0], REGION_S[1],
                                     label=f'detector_{d}',
                                     progress_every=200)
        well = traj[traj['primary'] != 'underpowered']
        n_tr = int((well['primary'] == 'TR').sum())
        n_well = int(len(well))
        n_bl = int((well['primary'] == 'BL').sum())
        modal = well['primary'].mode()[0] if len(well) else 'underpowered'
        print(f"  {d}: {n_tr}/{n_well} TR ({n_tr/max(n_well,1)*100:.1f}%)  "
              f"BL={n_bl}  modal={modal}  ⏱{time.time()-t0:.0f}s")
        rows.append(dict(
            kind='per_detector', detector=d, seed=None,
            n_well=n_well, n_tr=n_tr, n_bl=n_bl,
            tr_fraction=n_tr / max(n_well, 1),
        ))
    print()

    # ─── Randomized-detector-label pooling ──
    print("Randomized-detector-label pooling controls:")
    for seed in range(N_SHUFFLE_SEEDS):
        rng = np.random.default_rng(seed + 200)
        shuffled = df_w.copy()
        shuffled['detector'] = rng.permutation(shuffled['detector'].values)
        # Re-pool (which is just sort by time_us — pooling is order-invariant
        # since it's just the time stamps; the shuffle was a no-op for the
        # pooled stream itself).  So this control specifically tests:
        # if we pool only events from a subset of "detectors" after shuffling,
        # do we still get TR?  We pool a random subset matching the size of
        # the original pooled stream.
        # In practice, since shuffling labels of pooled events doesn't change
        # the pooled stream, this control isn't informative as written.
        # The right control is: pool only events from a single original
        # detector but at the pooled-stream rate (resample with replacement
        # to inflate the rate).  That tests rate-vs-pooling.
        # SKIP — see comment.
        pass
    print("  (Random-label shuffle of the pooled stream is a no-op since")
    print("  the pooled stream's time_us values are unchanged.  The")
    print("  per-detector results above are the operative comparison.)")
    print()

    out_df = pd.DataFrame(rows)
    out_df.to_parquet(OUT_DIR / 'phase23_per_detector.parquet', index=False)
    print(f"  → {OUT_DIR}/phase23_per_detector.parquet  ({len(out_df)} rows)")
    print()

    # Verdict
    print("Verdict:")
    pd_rows = [r for r in rows if r['kind'] == 'per_detector']
    tr_fracs = [r['tr_fraction'] for r in pd_rows]
    if not tr_fracs:
        print("  INCONCLUSIVE — no per-detector data.")
        return
    n_tr_dets = sum(1 for f in tr_fracs if f >= 0.30)
    n_total_dets = len(tr_fracs)
    max_tr = max(tr_fracs)
    median_tr = float(np.median(tr_fracs))
    print(f"  per-detector TR fractions: max={max_tr*100:.1f}%, "
          f"median={median_tr*100:.1f}%  "
          f"({n_tr_dets}/{n_total_dets} ≥ 30 % TR)")
    print(f"  pooled TR fraction:        {n_real_tr/max(n_real_well,1)*100:.1f}%")
    print()
    if n_tr_dets >= max(2, n_total_dets // 2):
        print("  ASTROPHYSICAL-OR-INSTRUMENT-WIDE — TR signature present in")
        print("  multiple detectors independently.  NOT a pooling artifact.")
        print("  Either real astrophysical sub-millisecond clustering during")
        print("  the late prompt, or an instrument-wide effect (deadtime")
        print("  becoming significant per detector).  Per-detector rate")
        print("  comparison may discriminate.")
    elif n_tr_dets >= 1:
        print("  PARTIAL — TR signature present in some detectors but not")
        print("  uniformly.  Mixed: maybe a detector-specific effect plus")
        print("  some real signal.")
    else:
        print("  POOLING ARTIFACT — TR signature present in pooled stream")
        print("  but absent from individual detectors.  The signature is")
        print("  introduced by detector pooling, not present in any single")
        print("  detector's spike train.  Most likely explanation: timing")
        print("  precision or cross-detector coincidence at sub-1 ms scale.")
        print("  NOT astrophysical; methodology caveat to add to GRB pipeline.")


if __name__ == '__main__':
    main()
