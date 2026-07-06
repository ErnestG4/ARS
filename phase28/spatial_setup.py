"""
phase28/spatial_setup.py — extract per-session per-unit (vertical,
horizontal) probe positions for Allen Neuropixels VISp units.

For each Phase 24 session, find the V1 (VISp) probe and produce a
per-session DataFrame with one row per VISp-area QC-passing unit:

  unit_id, peak_channel_id, probe_id,
  probe_vertical_position_um, probe_horizontal_position_um,
  mean_rate, n_spikes

Per-session output saved to data/phase28_results/spatial_positions/
session_{session_id}.parquet.

Aggregated index of all sessions saved to
data/phase28_results/spatial_positions_all.parquet.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pynwb

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase24'))

from loader import ALLEN_CACHE, allen_default_qc

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase28_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)
POS_DIR = OUT_DIR / 'spatial_positions'
POS_DIR.mkdir(parents=True, exist_ok=True)

AREA = 'VISp'


def get_session_positions(session_id: int,
                              cache_dir: Path = ALLEN_CACHE,
                              area: str = AREA) -> pd.DataFrame:
    """Load NWB for one session; extract per-unit probe positions for
    QC-passing VISp units."""
    nwb_path = cache_dir / f'session_{session_id}' / f'session_{session_id}.nwb'
    if not nwb_path.exists():
        return pd.DataFrame()
    io = pynwb.NWBHDF5IO(str(nwb_path), 'r', load_namespaces=True)
    nwb = io.read()
    units_df = nwb.units.to_dataframe()
    elec_df = nwb.electrodes.to_dataframe()

    # Map peak_channel_id → area + position
    peak_to_loc = elec_df['location']
    peak_to_v = elec_df['probe_vertical_position']
    peak_to_h = elec_df['probe_horizontal_position']
    peak_to_probe = elec_df['probe_id']

    units_df['area'] = units_df['peak_channel_id'].map(
        lambda ch: peak_to_loc.get(ch, 'unknown'))
    in_area = units_df[units_df['area'] == area].copy()
    qc = in_area[allen_default_qc(in_area)].copy()

    qc['probe_vertical_position_um'] = qc['peak_channel_id'].map(
        lambda ch: float(peak_to_v.get(ch, np.nan)))
    qc['probe_horizontal_position_um'] = qc['peak_channel_id'].map(
        lambda ch: float(peak_to_h.get(ch, np.nan)))
    qc['probe_id'] = qc['peak_channel_id'].map(
        lambda ch: int(peak_to_probe.get(ch, -1)))

    # Per-unit total spike count for rate
    spike_times_table = nwb.units
    id_to_row = {uid: i for i, uid in enumerate(list(spike_times_table.id[:]))}
    n_spikes = []
    for uid in qc.index:
        row_idx = id_to_row[uid]
        sp = np.asarray(spike_times_table['spike_times'][row_idx])
        n_spikes.append(int(sp.size))
    qc['n_spikes'] = n_spikes

    out = pd.DataFrame(dict(
        unit_id=qc.index.astype(int).tolist(),
        session_id=int(session_id),
        peak_channel_id=qc['peak_channel_id'].astype(int).tolist(),
        probe_id=qc['probe_id'].astype(int).tolist(),
        probe_vertical_position_um=qc['probe_vertical_position_um'].tolist(),
        probe_horizontal_position_um=qc['probe_horizontal_position_um'].tolist(),
        firing_rate_allen=qc['firing_rate'].astype(float).tolist(),
        n_spikes=qc['n_spikes'].tolist(),
    ))
    io.close()
    return out


def main():
    print("=" * 72)
    print("Phase 28 spatial setup — extract VISp probe positions per session")
    print("=" * 72)
    sessions = pd.read_parquet(
        Path(ROOT_DIR) / 'data' / 'phase24_results'
        / 'per_session_h1_functional.parquet')['session_id'].unique()
    print(f"  {len(sessions)} sessions to process")

    rows = []
    for sid in sessions:
        df = get_session_positions(int(sid))
        if not len(df):
            print(f"    session {sid}: no VISp units")
            continue
        df.to_parquet(POS_DIR / f'session_{sid}.parquet', index=False)
        n_probes = df['probe_id'].nunique()
        v_min = df['probe_vertical_position_um'].min()
        v_max = df['probe_vertical_position_um'].max()
        print(f"    session {sid}: n_visp_units={len(df)}  n_probes={n_probes}  "
                f"v_range=[{v_min:.0f}, {v_max:.0f}]μm")
        rows.append(df)
    if rows:
        all_df = pd.concat(rows, ignore_index=True)
        all_df.to_parquet(OUT_DIR / 'spatial_positions_all.parquet', index=False)
        print(f"\n  → {OUT_DIR}/spatial_positions_all.parquet  ({len(all_df)} units)")


if __name__ == '__main__':
    main()
