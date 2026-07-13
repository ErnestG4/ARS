"""
phase24/run_sensitivity_grid.py — (k_thresh, w) sensitivity grid for
the H2 population-event extraction across all candidate sessions.

Per the Phase 24 Full brief: Allen's higher event rate (3.4× pvc-11)
means the pvc-11-derived (k=5, w=5ms) defaults probe at a different
effective resolution.  This grid identifies the (k, w) configuration
per session whose population-event rate is closest to pvc-11
monkey1_natural_movie's 24.3 Hz — the "rate-matched" configuration —
which the full H2 pipeline then runs surrogates at, alongside the
default.

Real-data only (no surrogates) — fast.

Outputs:
  data/phase24_results/sensitivity_grid.parquet
  data/phase24_results/rate_matched_configs.parquet
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
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, THIS_DIR)

from loader import load_session, AllenRecording
from ars_classify import classify, per_q_columns


CANDIDATE_PATH = Path(os.path.expandvars(os.path.expanduser("$HOME/fmexplorer/allen_cache/phase24_candidate_sessions.csv")))
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase24_results'

K_GRID = [5, 8, 12, 17]
W_GRID_MS = [5.0, 10.0, 20.0]
PVC11_RATE_HZ = 24.3   # pvc-11 monkey1_natural_movie reference rate
Q_MAX = 30
PRIMARY_CONDITION = 'natural_movie_one'   # the rate-matching anchor


def build_unit_matrix_chunks(rec, unit_ids, chunks, bin_ms):
    bin_s = bin_ms / 1000.0
    chunk_durs = [stop - start for start, stop in chunks]
    chunk_bins = [int(np.ceil(d / bin_s)) for d in chunk_durs]
    total_bins = sum(chunk_bins)
    total_dur = total_bins * bin_s
    mat = np.zeros((len(unit_ids), total_bins), dtype=np.int32)
    for i, uid in enumerate(unit_ids):
        sp = rec.spike_times.get(int(uid), np.zeros(0))
        offset = 0
        for (start, stop), n_b in zip(chunks, chunk_bins):
            mask = (sp >= start) & (sp < stop)
            ev = sp[mask] - start
            bin_idx = np.floor(ev / bin_s).astype(np.int64)
            bin_idx = bin_idx[(bin_idx >= 0) & (bin_idx < n_b)]
            np.add.at(mat[i], bin_idx + offset, 1)
            offset += n_b
    return mat, total_dur


def extract_events(unit_matrix, bin_ms, k):
    binary = (unit_matrix > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    bin_idx = np.where(coact >= k)[0]
    return (bin_idx + 0.5) * (bin_ms / 1000.0)


def chunks_for(rec, condition):
    if condition == 'natural_movie_one':
        return [(float(g['start_time'].min()), float(g['stop_time'].max()))
                  for _, g in rec.natural_movie_one.groupby('stimulus_block', sort=True)]
    if condition == 'drifting_pooled':
        return [(float(r['start_time']), float(r['stop_time']))
                  for _, r in rec.drifting_gratings.iterrows()]
    if condition == 'spontaneous':
        return [(float(r['start_time']), float(r['stop_time']))
                  for _, r in rec.spontaneous.iterrows()
                  if r['stop_time'] - r['start_time'] >= 5.0]
    raise ValueError(condition)


def main():
    print("=" * 80)
    print("Phase 24 Full — (k, w) sensitivity grid")
    print("=" * 80)

    candidates = pd.read_csv(CANDIDATE_PATH)
    print(f"  candidate sessions: {len(candidates)}")
    print(f"  K grid: {K_GRID}")
    print(f"  W grid (ms): {W_GRID_MS}")
    print(f"  PVC-11 reference rate (natural_movie_one): {PVC11_RATE_HZ} Hz")
    print()

    rows = []
    for _, srow in candidates.iterrows():
        sid = int(srow['ecephys_session_id'])
        nwb_path = Path(os.path.expandvars(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb'))
        if not nwb_path.exists() or nwb_path.stat().st_size < 1_000_000_000:
            print(f"  session {sid}: NWB not ready; skip")
            continue
        try:
            rec = load_session(sid)
        except Exception as e:
            print(f"  session {sid}: load error: {e}")
            continue
        unit_ids = list(rec.units.index)
        print(f"\n--- session {sid} ({srow['cre_line']}, n_v1={len(unit_ids)}) ---")
        for cond in ['natural_movie_one', 'drifting_pooled', 'spontaneous']:
            chunks = chunks_for(rec, cond)
            if not chunks:
                continue
            for w_ms in W_GRID_MS:
                t0 = time.time()
                mat, total_dur = build_unit_matrix_chunks(rec, unit_ids, chunks, w_ms)
                for k in K_GRID:
                    events = extract_events(mat, w_ms, k)
                    rate = events.size / max(total_dur, 1e-9)
                    res = classify(events, return_full=False, q_max=Q_MAX)
                    rows.append(dict(
                        session_id=sid, cre_line=srow['cre_line'],
                        condition=cond, k_thresh=int(k), w_ms=float(w_ms),
                        n_units=len(unit_ids),
                        n_events=int(events.size),
                        event_rate_hz=float(rate),
                        total_dur_sec=float(total_dur),
                        primary=res['primary'],
                        rep_med=res['rep_med'],
                        ks_gue_med=res['ks_gue_med'],
                        n_well=res['n_well'],
                    ))
                print(f"  {cond:20s} w={w_ms:.0f}ms: "
                        f"rates={[f'{r:.1f}' for r in [next(x['event_rate_hz'] for x in rows if x['session_id']==sid and x['condition']==cond and x['w_ms']==w_ms and x['k_thresh']==k) for k in K_GRID]]}  "
                        f"⏱{time.time()-t0:.0f}s")

    df = pd.DataFrame(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_DIR / 'sensitivity_grid.parquet', index=False)
    print(f"\n  → {OUT_DIR}/sensitivity_grid.parquet  ({len(df)} rows)")

    # ─── identify rate-matched (k, w) per session for natural_movie_one ──
    print()
    print("Rate-matched (k, w) per session for natural_movie_one "
            f"(target {PVC11_RATE_HZ} Hz):")
    rm_rows = []
    nmo = df[df['condition'] == PRIMARY_CONDITION]
    for sid, g in nmo.groupby('session_id'):
        # closest-rate combo
        g = g.copy()
        g['rate_diff'] = (g['event_rate_hz'] - PVC11_RATE_HZ).abs()
        best = g.loc[g['rate_diff'].idxmin()]
        rm_rows.append(dict(
            session_id=int(sid),
            cre_line=best['cre_line'],
            rate_matched_k=int(best['k_thresh']),
            rate_matched_w_ms=float(best['w_ms']),
            rate_matched_event_rate_hz=float(best['event_rate_hz']),
            default_event_rate_hz=float(g[(g['k_thresh']==5) & (g['w_ms']==5.0)]['event_rate_hz'].iloc[0])
                                          if len(g[(g['k_thresh']==5) & (g['w_ms']==5.0)]) else float('nan'),
        ))
        print(f"  session {sid}: rate_matched (k={int(best['k_thresh'])}, w={best['w_ms']:.0f}ms) → "
              f"{best['event_rate_hz']:.1f} Hz  (default 5/5ms gives "
              f"{rm_rows[-1]['default_event_rate_hz']:.1f} Hz)")
    rm_df = pd.DataFrame(rm_rows)
    rm_df.to_parquet(OUT_DIR / 'rate_matched_configs.parquet', index=False)
    print(f"\n  → {OUT_DIR}/rate_matched_configs.parquet  ({len(rm_df)} rows)")


if __name__ == '__main__':
    main()
