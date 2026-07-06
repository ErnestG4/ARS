"""
phase22a/h2_population.py — H2 population-event ARS classification.

For each recording (spontaneous + evoked):
  1. Restrict to H2-passing units.
  2. Build the (units × bins) binary coactivation matrix.
  3. Extract population events (default: synchronous-firing, k=5, 5ms bin).
  4. Run ARS classification on the event timestamp point process at TWO
     q_max settings (30 = canonical, 100 = slow-regime extension).
  5. Save full per-q signature plus the time-frequency coverage band.

q-band time-frequency coverage.  For event-rate r Hz and q ∈ [1, Q],
the joint_q_profile probes periods r/q seconds (frequencies r·q⁻¹ Hz).
For anesthetised V1 the dominant joint-structure timescales are:
    Up/Down state alternation:  0.5–3 Hz  (period 0.3–2 s)
    Mid-frequency synchrony:    5–30 Hz   (period 30–200 ms)
At default (k=5, w=5ms) the typical pvc-11 event rate is ~30–60 Hz,
so q_max=30 covers ~1–60 Hz (catches the upper edge of Up/Down only)
and q_max=100 reaches ~0.3 Hz (full Up/Down coverage).  The
sensitivity grid additionally varies k and w to get lower event-rates
where q_max=30 alone reaches longer periods.

Sensitivity scan: (k, w) ∈ {(4,5ms), (5,5ms), (8,5ms), (5,10ms)} ×
q_max ∈ {30, 100}.

Outputs:
  data/phase22a_results/h2_population_classifications.parquet
  data/phase22a_results/h2_sensitivity.parquet
  data/phase22a_results/h2_coverage.parquet  (per-recording time-frequency
                                               band coverage at each cfg)
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

from loader import load, list_all_recordings
from ars_classify import classify, per_q_columns
from population_events import (
    build_unit_matrix, extract_events,
    BIN_MS_DEFAULT, K_THRESH_DEFAULT,
)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
SEL_PATH = OUT_DIR / 'unit_selection.parquet'

Q_MAX_DEFAULT = 30
Q_MAX_SLOW = 100   # extends q-band to slower timescales (Up/Down regime)

SENSITIVITY_GRID = [
    dict(bin_ms=5.0, k_thresh=4, label='k=4_w=5ms'),
    dict(bin_ms=5.0, k_thresh=5, label='k=5_w=5ms_DEFAULT'),
    dict(bin_ms=5.0, k_thresh=8, label='k=8_w=5ms'),
    dict(bin_ms=10.0, k_thresh=5, label='k=5_w=10ms'),
]


def _classify_recording(recording_name: str, h2_units: list[int],
                          bin_ms: float, k_thresh: int,
                          q_max: int = Q_MAX_DEFAULT) -> dict:
    """Build matrix, extract events, classify at the given q_max.
    Also reports the time-frequency band the q-grid spans."""
    rec = load(recording_name)
    if not h2_units:
        return dict(recording=recording_name, n_units=0,
                    n_events=0, primary='no_units', rep_med=np.nan,
                    ks_gue_med=np.nan, n_well=0, per_q=None,
                    q_max=q_max, freq_band_lo_hz=np.nan,
                    freq_band_hi_hz=np.nan)
    mat, total_dur = build_unit_matrix(rec, h2_units, bin_ms=bin_ms)
    events = extract_events(mat, bin_ms=bin_ms, k_thresh=k_thresh)
    n_ev = int(events.size)
    rate_hz = float(n_ev / max(total_dur, 1e-9))
    # The q-grid spans periods rate/q = q seconds (in unit-mean spacing) →
    # frequencies rate·q⁻¹ Hz.  q=1 → rate Hz; q=q_max → rate/q_max Hz.
    # After JPF_CAP subsampling the effective rate scales — but the q-band
    # always spans rate_eff Hz (q=1) to rate_eff / q_max Hz (q=q_max).
    res = classify(events, return_full=True, q_max=q_max)
    cols = per_q_columns(res['per_q'])
    # JPF_CAP decimation subsamples spacings but does NOT change the
    # mean-spacing → frequency mapping (the IEI distribution is
    # preserved under subsampling).  Period at Farey rational a/q in
    # unit-mean coordinates = q × original-mean-spacing seconds, so
    # frequency at q-band = original_event_rate / q Hz.
    return dict(
        recording=recording_name,
        subset=rec.subset,
        monkey=rec.monkey,
        n_units=len(h2_units),
        n_events=n_ev,
        bin_ms=float(bin_ms),
        k_thresh=int(k_thresh),
        q_max=int(q_max),
        total_dur_sec=float(total_dur),
        event_rate_hz=rate_hz,
        n_events_used=res['n_events_used'],
        freq_band_hi_hz=rate_hz,                    # q=1
        freq_band_lo_hz=rate_hz / q_max,            # q=q_max
        primary=res['primary'],
        rep_med=res['rep_med'],
        ks_gue_med=res['ks_gue_med'],
        n_well=res['n_well'],
        **cols,
    )


def main():
    print("=" * 72)
    print("Phase 22a H2 — population-event ARS classification")
    print("=" * 72)

    sel = pd.read_parquet(SEL_PATH)
    sel_h2 = sel[sel['h2_pass']].copy()
    print(f"H2-passing units: {len(sel_h2)} across "
          f"{sel_h2['recording'].nunique()} recordings\n")

    # Default-parameter pass at TWO q_max settings
    rows = []
    for q_max in (Q_MAX_DEFAULT, Q_MAX_SLOW):
        print(f"\n--- q_max={q_max} ---")
        for rec_name, group in sel_h2.groupby('recording', sort=False):
            units = group['unit_idx'].astype(int).tolist()
            t0 = time.time()
            r = _classify_recording(rec_name, units,
                                      bin_ms=BIN_MS_DEFAULT,
                                      k_thresh=K_THRESH_DEFAULT,
                                      q_max=q_max)
            dt = time.time() - t0
            rows.append(r)
            print(f"  {rec_name:35s}  units={r['n_units']:3d}  "
                  f"events={r['n_events']:6d}  rate={r['event_rate_hz']:6.1f}/s  "
                  f"band=[{r['freq_band_lo_hz']:5.2f},{r['freq_band_hi_hz']:5.1f}]Hz  "
                  f"primary={r['primary']:13s}  ⏱{dt:.0f}s")

    df = pd.DataFrame(rows)
    out = OUT_DIR / 'h2_population_classifications.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(df)} rows)")

    # Time-frequency coverage table
    cov = df[['recording', 'subset', 'monkey', 'q_max', 'bin_ms', 'k_thresh',
              'n_events', 'event_rate_hz',
              'freq_band_lo_hz', 'freq_band_hi_hz']].copy()
    cov.to_parquet(OUT_DIR / 'h2_coverage.parquet', index=False)
    print(f"  → {OUT_DIR}/h2_coverage.parquet  ({len(cov)} rows)")

    # Sensitivity grid (default q_max only — keep size sane)
    print()
    print("Sensitivity grid (q_max=30):")
    sens_rows = []
    for cfg in SENSITIVITY_GRID:
        for rec_name, group in sel_h2.groupby('recording', sort=False):
            units = group['unit_idx'].astype(int).tolist()
            r = _classify_recording(rec_name, units,
                                      bin_ms=cfg['bin_ms'],
                                      k_thresh=cfg['k_thresh'],
                                      q_max=Q_MAX_DEFAULT)
            r['cfg_label'] = cfg['label']
            sens_rows.append(r)
        # Compact per-config summary
        sub = pd.DataFrame([row for row in sens_rows if row['cfg_label'] == cfg['label']])
        prim_counts = sub['primary'].value_counts()
        print(f"  {cfg['label']:20s}  primaries: {dict(prim_counts)}")
    sens_df = pd.DataFrame(sens_rows)
    out_sens = OUT_DIR / 'h2_sensitivity.parquet'
    sens_df.to_parquet(out_sens, index=False)
    print(f"\n  → {out_sens}  ({len(sens_df)} rows)")


if __name__ == '__main__':
    main()
