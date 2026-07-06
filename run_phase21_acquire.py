"""
run_phase21_acquire.py — Phase 21 Tier 1 driver.

Acquire Fermi GBM TTE for the priority-1, priority-2, priority-3 events.
Parse to per-event parquet (detector, time_us, energy_ch).  Compute
basic statistics + burst detector selection.

Outputs:
  data/phase21_grb_panel/raw/{trigger_id}/glg_tte_*.fit
  data/phase21_grb_panel/{name}.parquet
  data/phase21_grb_panel/_acquisition_summary.parquet
  data/phase21_grb_panel/detector_geometry.parquet
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from grb_pipeline import (
    EVENT_PANEL, GBM_DETECTORS_ALL, GBM_DETECTORS_NAI, GBM_DETECTORS_BGO,
    acquire_event, write_event_parquet, select_burst_detectors,
)


DATA = Path(THIS_DIR) / 'data' / 'phase21_grb_panel'
RAW = DATA / 'raw'


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("Phase 21 Tier 1 — GRB TTE acquisition")
    print("=" * 80)

    summary_rows = []
    geometry_rows = []
    for event in EVENT_PANEL:
        if event['priority'] > 3:
            print(f"\n  {event['name']}: priority {event['priority']} "
                  f"(deferred per session-plan)")
            continue
        print(f"\n  {event['name']} (priority {event['priority']}, "
              f"category={event['category']}):")
        t0 = time.time()
        per_det = acquire_event(event, RAW, progress=True)
        if not per_det:
            print(f"    NO data available; skipping {event['name']}")
            continue
        # Burst detector selection — only keep detectors with strong
        # prompt-window response over background
        t90_us = int(event['t90'] * 1_000_000)
        burst_dets = select_burst_detectors(per_det, t90_us=t90_us,
                                              min_burst_counts=2000)
        print(f"    burst detectors: {burst_dets}")
        # Restrict per_det to burst detectors only
        burst_only = {d: per_det[d] for d in burst_dets if d in per_det}
        if not burst_only:
            print(f"    {event['name']}: no burst detectors; falling back to "
                  f"all available")
            burst_only = per_det
        out_path = DATA / f"{event['name']}.parquet"
        write_event_parquet(event, burst_only, out_path)
        total_events = sum(d['times_us'].size for d in burst_only.values())
        print(f"    → {out_path.name}: {total_events:,} events across "
              f"{len(burst_only)} detectors  ⏱{time.time()-t0:.0f}s")
        summary_rows.append(dict(
            event=event['name'],
            trigger_id=event['trigger_id'],
            priority=event['priority'],
            category=event['category'],
            t90_seconds=event['t90'],
            n_detectors_burst=len(burst_only),
            n_detectors_all=len(per_det),
            total_events=total_events,
            qpo_claim_hz=event.get('qpo_claim_hz'),
            qpo_reference=event.get('qpo_reference'),
        ))
        # Detector geometry record per (event, detector)
        for det in burst_only:
            sample = burst_only[det]
            geometry_rows.append(dict(
                event=event['name'],
                detector=det,
                detector_name=sample.get('detector', ''),
                detector_type='NaI' if det.startswith('n') else 'BGO',
                trigtime=sample.get('trigtime', 0.0),
                tstart_relative_s=float(sample['times_us'].min() / 1e6),
                tstop_relative_s=float(sample['times_us'].max() / 1e6),
                n_events=int(sample['times_us'].size),
            ))

    # Save summaries
    if summary_rows:
        pd.DataFrame(summary_rows).to_parquet(
            DATA / '_acquisition_summary.parquet', index=False)
    if geometry_rows:
        pd.DataFrame(geometry_rows).to_parquet(
            DATA / 'detector_geometry.parquet', index=False)
    print()
    print("=" * 80)
    print("Acquisition summary:")
    print("=" * 80)
    if summary_rows:
        df = pd.DataFrame(summary_rows)
        print(df[['event', 'priority', 'n_detectors_burst', 'total_events',
                   'qpo_claim_hz']].to_string(index=False))


if __name__ == '__main__':
    main()
