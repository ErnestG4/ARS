"""
phase28/pilot_bins.py — pilot one session to check per-spatial-bin
event rate distribution and ARS-operating-envelope viability.

For session 732592105 VISp units, builds pairwise distance matrix
using (vert, horiz) probe positions, groups into bins, and for each
spatial bin counts:
  - n_units, n_pairs in bin
  - per-bin cluster size (median, max) when used as anchors
  - per-bin total event rate at k_thresh = max(2, ceil(0.5 * cluster_size))
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase24'))

from loader import load_session

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase28_results'
PILOT_SESSION = 732592105

EVENT_BIN_MS = 5.0

SPATIAL_BINS = [
    ('fine-local',  (0, 100)),
    ('local',       (100, 300)),
    ('mid',         (300, 800)),
    ('distant',     (800, 5000)),
]


def main():
    print("=" * 72)
    print(f"Phase 28 pilot — spatial-bin event-rate distribution on session "
            f"{PILOT_SESSION}")
    print("=" * 72)
    pos_df = pd.read_parquet(OUT_DIR / 'spatial_positions'
                                / f'session_{PILOT_SESSION}.parquet')
    print(f"  n VISp QC-passing units: {len(pos_df)}")

    # Positions
    pos = pos_df[['probe_vertical_position_um',
                    'probe_horizontal_position_um']].to_numpy()
    d = squareform(pdist(pos))
    np.fill_diagonal(d, np.nan)
    print(f"  vertical range: {pos_df['probe_vertical_position_um'].min():.0f}-"
            f"{pos_df['probe_vertical_position_um'].max():.0f}μm")
    print(f"  horizontal positions: {sorted(pos_df['probe_horizontal_position_um'].unique())}")
    print(f"  pairwise distance percentiles (μm): "
            f"min={np.nanmin(d):.0f}  q25={np.nanpercentile(d, 25):.0f}  "
            f"q50={np.nanpercentile(d, 50):.0f}  "
            f"q75={np.nanpercentile(d, 75):.0f}  max={np.nanmax(d):.0f}")

    # Bins:
    for label, (lo, hi) in SPATIAL_BINS:
        npairs = (((d > lo) & (d <= hi)).sum()) // 2
        # Cluster size: for each unit, count neighbours within hi (cumulative)
        cs = ((d > 0) & (d <= hi)).sum(axis=1)
        # Restrict to neighbours within [lo, hi]
        # For "local" type bins, anchor + neighbours in (lo, hi]
        ns_in_band = ((d > lo) & (d <= hi)).sum(axis=1)
        ns_all_up_to_hi = ((d > 0) & (d <= hi)).sum(axis=1) + 1  # include anchor
        print(f"  {label} ({lo}-{hi}μm):  pairs={npairs}  "
                f"median cluster size (anchor+within-{hi}μm)={np.median(ns_all_up_to_hi):.0f}  "
                f"max={int(ns_all_up_to_hi.max())}")

    # Load spike data for the pilot session — need to actually bin & extract events
    print()
    print("  loading spike data...")
    rec = load_session(int(PILOT_SESSION))
    # Use natural_movie_one as the stimulus context (matches Phase 24 H2)
    print(f"  n natural_movie_one presentations: {len(rec.natural_movie_one)}")

    # For each unit, get spike train concatenated over natural_movie_one
    # (this is the H2 analysis context).
    print("  binning spike trains at 5ms...")
    if not len(rec.natural_movie_one):
        print("  WARN: no natural_movie_one, falling back to spontaneous")
        return

    # Get per-unit binned spike trains within all natural_movie_one blocks
    unit_ids = pos_df['unit_id'].astype(int).tolist()
    bin_s = EVENT_BIN_MS / 1000.0
    nm = rec.natural_movie_one
    blocks = nm.groupby('stimulus_block', sort=True)
    block_durations = []
    block_ranges = []
    for bid, grp in blocks:
        t0 = float(grp['start_time'].min())
        t1 = float(grp['stop_time'].max())
        block_durations.append(t1 - t0)
        block_ranges.append((t0, t1))
    total_dur = sum(block_durations)
    n_bins_per_block = [int(np.ceil(d / bin_s)) for d in block_durations]
    total_bins = sum(n_bins_per_block)
    print(f"    {len(block_ranges)} blocks, total duration {total_dur:.1f}s, "
            f"total bins {total_bins}")

    mat = np.zeros((len(unit_ids), total_bins), dtype=np.int32)
    for ui, uid in enumerate(unit_ids):
        sp = rec.spike_times.get(int(uid), np.zeros(0))
        offset = 0
        for (t0, t1), nb in zip(block_ranges, n_bins_per_block):
            in_block = sp[(sp >= t0) & (sp < t1)]
            bin_idx = np.floor((in_block - t0) / bin_s).astype(np.int64)
            bin_idx = bin_idx[(bin_idx >= 0) & (bin_idx < nb)]
            np.add.at(mat[ui], bin_idx + offset, 1)
            offset += nb

    # Now compute per-spatial-bin event rate for cluster events at
    # k_thresh = max(2, ceil(0.5 * cluster_size))
    print()
    print("  per-spatial-bin event-rate test:")
    for label, (lo, hi) in SPATIAL_BINS:
        # Take a few anchor units evenly distributed in the V1 unit set
        n_anchors = 5
        anchors = np.linspace(0, len(unit_ids) - 1, n_anchors).astype(int)
        for ai in anchors:
            members = np.where((d[ai] > lo) & (d[ai] <= hi))[0].tolist()
            if not members or ((lo == 0) and (ai not in members)):
                # For fine-local include the anchor itself
                members = sorted([ai] + members)
            cluster_size = len(members)
            if cluster_size < 2: continue
            # Phase 22a convention: k=5 fixed for awake mouse low-synchrony
            # regime; Phase 27's 0.5*N was tuned for pvc-11 anaesthetised
            # high-synchrony and underestimates events for awake mouse.
            k_thresh = max(2, min(5, cluster_size - 1))
            sub = mat[members]
            binary = (sub > 0).astype(np.int32)
            coact = binary.sum(axis=0)
            n_events = int((coact >= k_thresh).sum())
            rate = n_events / max(total_dur, 1e-9)
            print(f"    {label:12s} anchor=unit{ai:3d}  n_members={cluster_size:2d}  "
                    f"k={k_thresh}  n_events={n_events:5d}  rate={rate:6.2f}/s")


if __name__ == '__main__':
    main()
