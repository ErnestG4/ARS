"""
phase24/run_per_session_h1.py — per-session H1 cross-validation across
all candidate sessions.

Per Phase 22a methodology, repeated independently per session:
  - per-unit ARS classification on drifting_pooled
  - functional categories (OSI/DSI/F1F0) recomputed from spikes
  - Spearman partial correlation of {rep_med, ks_gue_med} vs
    {OSI, DSI, F1/F0} controlling for mean firing rate

Outputs: data/phase24_results/per_session_h1.parquet (one row per
(session, descriptor, ars_metric) cell with the partial correlation).
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, t as student_t

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, THIS_DIR)

from loader import load_session
from ars_classify import classify, per_q_columns
from run_h1 import (per_direction_rate, osi_dsi, f1_f0_at_preferred,
                       _partial_spearman, H1_MIN_SPIKES, N_PROC,
                       _classify_one)


CANDIDATE_PATH = Path('$HOME/fmexplorer/allen_cache/phase24_candidate_sessions.csv')
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase24_results'


def process_session(srow):
    sid = int(srow['ecephys_session_id'])
    nwb_path = Path(os.path.expandvars(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb'))
    if not nwb_path.exists() or nwb_path.stat().st_size < 1_000_000_000:
        return None, None, None
    rec = load_session(sid)
    print(f"  session {sid} loaded: {rec.n_units_qc_passing} V1 units")

    # ARS classification on drifting_pooled per unit (with H1 spike filter)
    jobs = []
    for uid in rec.units.index:
        sp = rec.concatenated_spikes_drifting(uid)
        if sp.size >= H1_MIN_SPIKES:
            jobs.append((int(uid), 'drifting_pooled', sp))
    if not jobs:
        return None, None, None
    with Pool(processes=N_PROC) as pool:
        ars_rows = list(pool.imap(_classify_one, jobs, chunksize=4))
    df_ars = pd.DataFrame(ars_rows)
    df_ars['session_id'] = sid

    # Functional categories
    func_rows = []
    for uid in rec.units.index:
        per_dir = per_direction_rate(rec, int(uid))
        td = osi_dsi(per_dir)
        if not np.isnan(td['pref_dir_deg']):
            f1f0 = f1_f0_at_preferred(rec, int(uid), td['pref_dir_deg'])
        else:
            f1f0 = float('nan')
        sp = rec.spike_times[int(uid)]
        dur = float(sp.max() - sp.min()) if sp.size > 1 else 1.0
        func_rows.append(dict(
            session_id=sid, unit_id=int(uid),
            mean_rate=sp.size / max(dur, 1e-9),
            **td, f1_f0_pref=f1f0,
        ))
    df_func = pd.DataFrame(func_rows)

    # Cross-validation table
    j = df_ars.merge(df_func, on=['unit_id'])
    cv_rows = []
    for descriptor in ['osi', 'dsi', 'f1_f0_pref']:
        for ars_metric in ['rep_med', 'ks_gue_med']:
            sub = j.dropna(subset=[descriptor, ars_metric, 'mean_rate'])
            if len(sub) < 20: continue
            r_raw, p_raw = spearmanr(sub[ars_metric], sub[descriptor])
            r_par, p_par, n = _partial_spearman(sub[ars_metric], sub[descriptor],
                                                  sub['mean_rate'])
            cv_rows.append(dict(
                session_id=sid, cre_line=str(srow['cre_line']),
                descriptor=descriptor, ars_metric=ars_metric,
                n_units=int(n),
                spearman_raw=float(r_raw), p_raw=float(p_raw),
                spearman_partial=r_par, p_partial=p_par,
            ))

    return df_ars, df_func, pd.DataFrame(cv_rows)


def main():
    print("=" * 80)
    print("Phase 24 Full — per-session H1 cross-validation")
    print("=" * 80)

    candidates = pd.read_csv(CANDIDATE_PATH)
    print(f"  candidate sessions: {len(candidates)}")
    print()

    all_ars, all_func, all_cv = [], [], []
    for _, srow in candidates.iterrows():
        sid = int(srow['ecephys_session_id'])
        nwb_path = Path(os.path.expandvars(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb'))
        if not nwb_path.exists() or nwb_path.stat().st_size < 1_000_000_000:
            print(f"  session {sid}: NWB not ready; skip")
            continue
        print(f"\n--- session {sid} ({srow['cre_line']}) ---")
        t0 = time.time()
        try:
            ars, func, cv = process_session(srow)
        except Exception as e:
            print(f"  session {sid}: error: {e}")
            continue
        if ars is None: continue
        all_ars.append(ars)
        all_func.append(func)
        if cv is not None: all_cv.append(cv)
        print(f"  done in {time.time()-t0:.0f}s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if all_ars:
        pd.concat(all_ars).to_parquet(OUT_DIR / 'per_session_h1_ars.parquet',
                                          index=False)
        print(f"\n  → {OUT_DIR}/per_session_h1_ars.parquet")
    if all_func:
        pd.concat(all_func).to_parquet(OUT_DIR / 'per_session_h1_functional.parquet',
                                            index=False)
        print(f"  → {OUT_DIR}/per_session_h1_functional.parquet")
    if all_cv:
        cv_df = pd.concat(all_cv)
        cv_df.to_parquet(OUT_DIR / 'per_session_h1_crossval.parquet', index=False)
        print(f"  → {OUT_DIR}/per_session_h1_crossval.parquet  ({len(cv_df)} rows)")

        # Quick view
        print()
        print("Per-session OSI ↔ ks_gue_med partial correlations:")
        sub = cv_df[(cv_df['descriptor'] == 'osi')
                       & (cv_df['ars_metric'] == 'ks_gue_med')]
        print(sub[['session_id', 'cre_line', 'n_units',
                    'spearman_partial', 'p_partial']].to_string(index=False))


if __name__ == '__main__':
    main()
