"""
phase31b/h2_per_window_surrogate.py — Phase 31f, per-window H2 surrogate
battery on monkey1_natural_movie + monkey2_gratings_movie.

Phase 31b Follow-up 6 established that the locked H2 finding is
full-sequence-statistic-only: monkey1_natural_movie has rep_med
CV=0.64 across 10 windows and monkey2_gratings_movie has 5/5 TR vs
BR_artifact split.  The Phase 22a/22b surrogate battery never tested
whether H2 survives within stationary sub-windows.

This script applies the same surrogate battery (rate_matched_poisson
+ cell_shuffle + ln_evoked) at q_max=30 within each non-overlapping
window.  Per-window survival fraction is the stationarity-aware H2
claim.

Method per window:
  1. Compute real per-window ARS classification.
  2. For each (surrogate_kind, seed): generate full-recording
     surrogate event train, slice it into 10 windows of equal
     duration, classify each window separately.
  3. Per (window, q-band): survival flag = (real rep_int_q >
     surrogate-distribution 95th percentile of rep_int_q) AND
     (real quadrant != surrogate-modal quadrant).
  4. Conjunction across required surrogate types per subset.

Verdict criteria (per recording):
  - WINDOW_AWARE_LOCKED: ≥ 8/10 windows pass the conjunction at
    ≥ 1 q-band.
  - WINDOW_MIXTURE: 3-7 windows pass.
  - FULL_SEQUENCE_ARTIFACT: ≤ 2/10 windows pass.

Output:
  data/phase31b_results/H2_per_window_real.parquet
  data/phase31b_results/H2_per_window_surrogate.parquet
  data/phase31b_results/H2_per_window_survival.parquet
  data/phase31b_results/H2_per_window_verdict.json
"""
from __future__ import annotations

import os
import sys
import json
import time
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from loader import load
from population_events import build_unit_matrix, extract_events, BIN_MS_DEFAULT, K_THRESH_DEFAULT
from ars_classify import classify, per_q_columns, Q_MAX, MIN_EVENTS_PER_Q
from h2_surrogates import (
    surrogate_rate_matched_poisson, surrogate_cell_shuffle,
    surrogate_ln_evoked,
)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_WINDOWS = 10
N_SEEDS = 5    # ↓ from Pass-E 7 for tractability; verdict at 5 seeds
               # is robust enough for the per-window question
RECORDINGS = ['monkey1_natural_movie', 'monkey2_gratings_movie']
SURROGATE_KINDS = ['rate_matched_poisson', 'cell_shuffle', 'ln_evoked']
GENERATORS = {
    'rate_matched_poisson': surrogate_rate_matched_poisson,
    'cell_shuffle': surrogate_cell_shuffle,
    'ln_evoked': surrogate_ln_evoked,
}
N_WORKERS = min(16, cpu_count())


def get_h2_units(recording_name: str):
    sel = pd.read_parquet(Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'unit_selection.parquet')
    sub = sel[(sel['recording'] == recording_name) & (sel['h2_pass'])]
    return sub['unit_idx'].astype(int).tolist()


def slice_events_into_windows(events: np.ndarray, total_dur: float,
                                 n_windows: int) -> list[np.ndarray]:
    """Slice a sorted event-time array into n equal-duration windows.
    Each window's events are re-anchored to start at 0."""
    win_dur = total_dur / n_windows
    out = []
    for w in range(n_windows):
        t0 = w * win_dur
        t1 = (w + 1) * win_dur
        sub = events[(events >= t0) & (events < t1)]
        out.append(sub - t0)
    return out


def _classify_one_window(args):
    """Worker: classify one window's events at Q_MAX, return per-q DataFrame."""
    label, ev = args
    if ev.size < MIN_EVENTS_PER_Q:
        return (label, dict(primary='underpowered',
                             rep_med=np.nan, ks_gue_med=np.nan,
                             n_well=0, per_q=None))
    r = classify(ev, return_full=True, q_max=Q_MAX,
                  min_events_per_q=MIN_EVENTS_PER_Q)
    return (label, r)


def survival_per_qband(real_per_q: pd.DataFrame,
                         sur_per_q_list: list[pd.DataFrame]) -> dict:
    """For a single (window, surrogate_kind), compare real per-q DataFrame
    against the stacked surrogate per-q DataFrames (one per seed).
    Returns dict of per-q-band survival flags.
    """
    if real_per_q is None:
        return dict(survives=np.zeros(Q_MAX, dtype=bool),
                     n_qbands_survive=0)
    real_rep = real_per_q['rep_int_q'].values
    real_quad = real_per_q['quadrant'].values
    real_uw = real_per_q['underpowered'].values

    # Stack surrogate rep_int_q into shape (n_seeds, n_q)
    sur_reps = []
    sur_quads = []
    for sur in sur_per_q_list:
        if sur is None:
            continue
        sur_reps.append(sur['rep_int_q'].values)
        sur_quads.append(sur['quadrant'].values)
    if not sur_reps:
        return dict(survives=np.zeros(len(real_rep), dtype=bool),
                     n_qbands_survive=0)
    sur_reps = np.stack(sur_reps)   # (seeds, q_max)
    sur_quads = np.stack(sur_quads)
    sur_p95 = np.percentile(sur_reps, 95.0, axis=0)
    # surrogate-modal quadrant per q
    sur_modal = np.empty(sur_reps.shape[1], dtype=object)
    for q in range(sur_reps.shape[1]):
        vals, counts = np.unique(sur_quads[:, q], return_counts=True)
        sur_modal[q] = vals[counts.argmax()]

    survives = np.zeros(len(real_rep), dtype=bool)
    for q in range(len(real_rep)):
        if real_uw[q]:
            continue
        rep_pass = real_rep[q] > sur_p95[q]
        quad_pass = (real_quad[q] != sur_modal[q]
                       and str(real_quad[q]) != 'ambiguous')
        survives[q] = rep_pass and quad_pass
    return dict(survives=survives,
                 n_qbands_survive=int(survives.sum()),
                 sur_p95=sur_p95.tolist(),
                 real_rep=real_rep.tolist(),
                 sur_modal=sur_modal.tolist(),
                 real_quad=real_quad.tolist())


def main():
    print("=" * 72)
    print("Phase 31f — per-window H2 surrogate battery")
    print("=" * 72)
    print(f"  N_windows={N_WINDOWS}  N_seeds={N_SEEDS}\n")

    all_real_rows = []
    all_sur_rows = []
    all_survival_rows = []
    recording_verdicts = {}

    for rec_name in RECORDINGS:
        print(f"\n--- {rec_name} ---")
        rec = load(rec_name)
        units = get_h2_units(rec_name)
        mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS_DEFAULT)
        real_events = extract_events(mat, bin_ms=BIN_MS_DEFAULT,
                                       k_thresh=K_THRESH_DEFAULT)
        print(f"  n_units={len(units)}  n_events={real_events.size}  "
              f"dur={total_dur:.0f}s  rate={real_events.size/total_dur:.2f}Hz")

        # Real per-window classification (with full per-q DataFrames)
        real_windows = slice_events_into_windows(real_events, total_dur,
                                                    N_WINDOWS)
        print(f"  Computing real per-window classifications...")
        t0 = time.time()
        real_per_window = []
        for w, ev in enumerate(real_windows):
            if ev.size < MIN_EVENTS_PER_Q:
                real_per_window.append(None)
                continue
            r = classify(ev, return_full=True, q_max=Q_MAX,
                          min_events_per_q=MIN_EVENTS_PER_Q)
            real_per_window.append(r['per_q'])
            all_real_rows.append(dict(
                recording=rec_name, window_idx=w,
                n_events=int(ev.size),
                primary=r['primary'], rep_med=r['rep_med'],
                ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
            ))
        print(f"  ⏱{time.time()-t0:.1f}s")

        # Surrogate per-window: generate full-recording surrogates,
        # slice, classify each window per seed.
        for kind in SURROGATE_KINDS:
            print(f"  Surrogate '{kind}' × {N_SEEDS} seeds...")
            t0 = time.time()
            sur_per_window_per_seed = [[None] * N_WINDOWS for _ in range(N_SEEDS)]
            for seed in range(N_SEEDS):
                try:
                    sur_mat = GENERATORS[kind](rec, units, BIN_MS_DEFAULT, seed)
                    sur_events = extract_events(sur_mat, bin_ms=BIN_MS_DEFAULT,
                                                  k_thresh=K_THRESH_DEFAULT)
                except Exception as e:
                    print(f"    [error] seed {seed}: {e}")
                    continue
                # Slice into windows
                sur_windows = slice_events_into_windows(sur_events,
                                                          total_dur, N_WINDOWS)
                # Classify each window in parallel
                args = [(w, ev) for w, ev in enumerate(sur_windows)]
                with Pool(N_WORKERS) as pool:
                    results = list(pool.imap(_classify_one_window, args,
                                               chunksize=2))
                for w_idx, r in results:
                    sur_per_window_per_seed[seed][w_idx] = r.get('per_q')
                    all_sur_rows.append(dict(
                        recording=rec_name, surrogate=kind, seed=seed,
                        window_idx=w_idx,
                        n_events=int(sur_windows[w_idx].size),
                        primary=r['primary'], rep_med=r['rep_med'],
                        ks_gue_med=r['ks_gue_med'], n_well=r['n_well'],
                    ))
            print(f"    ⏱{time.time()-t0:.1f}s")

            # Survival per window
            for w in range(N_WINDOWS):
                if real_per_window[w] is None:
                    continue
                sur_for_window = [sur_per_window_per_seed[s][w]
                                    for s in range(N_SEEDS)]
                sur_for_window = [s for s in sur_for_window if s is not None]
                if not sur_for_window:
                    continue
                surv = survival_per_qband(real_per_window[w], sur_for_window)
                all_survival_rows.append(dict(
                    recording=rec_name, surrogate=kind, window_idx=w,
                    n_qbands_survive=surv['n_qbands_survive'],
                    survives_any=bool(surv['n_qbands_survive'] > 0),
                ))

        # Compute per-recording conjunction: ≥ 1 q-band survives ALL
        # required surrogate types per the Phase 22a brief
        if rec.subset == 'natural_movie' or rec.subset == 'gratings_movie' or rec.subset == 'noise_movie':
            required = ['rate_matched_poisson', 'cell_shuffle', 'ln_evoked']
        else:
            required = ['rate_matched_poisson', 'cell_shuffle']

        per_window_pass = []
        for w in range(N_WINDOWS):
            wsubs = [r for r in all_survival_rows
                       if r['recording'] == rec_name and r['window_idx'] == w]
            kinds = {r['surrogate']: r['n_qbands_survive'] for r in wsubs}
            # Conjunction: all required surrogates must show > 0 survival
            all_required_survive = all(kinds.get(k, 0) > 0 for k in required)
            per_window_pass.append(all_required_survive)
        n_pass = sum(per_window_pass)
        if n_pass >= 8:
            verdict = 'WINDOW_AWARE_LOCKED'
        elif n_pass >= 3:
            verdict = 'WINDOW_MIXTURE'
        else:
            verdict = 'FULL_SEQUENCE_ARTIFACT'
        recording_verdicts[rec_name] = dict(
            n_pass=int(n_pass), n_windows=N_WINDOWS,
            per_window_pass=[bool(p) for p in per_window_pass],
            verdict=verdict,
        )
        print(f"\n  Per-window required-conjunction pass: "
              f"{n_pass}/{N_WINDOWS}  →  {verdict}")

    # ─── save ───
    pd.DataFrame(all_real_rows).to_parquet(
        OUT_DIR / 'H2_per_window_real.parquet', index=False)
    pd.DataFrame(all_sur_rows).to_parquet(
        OUT_DIR / 'H2_per_window_surrogate.parquet', index=False)
    pd.DataFrame(all_survival_rows).to_parquet(
        OUT_DIR / 'H2_per_window_survival.parquet', index=False)
    with open(OUT_DIR / 'H2_per_window_verdict.json', 'w') as f:
        json.dump(recording_verdicts, f, indent=2, default=str)
    print(f"\n  → H2_per_window_*.parquet, H2_per_window_verdict.json\n")

    print("=== VERDICTS ===")
    for rec, v in recording_verdicts.items():
        print(f"  {rec}: {v['verdict']}  ({v['n_pass']}/{v['n_windows']} windows)")
        print(f"    pass mask: {v['per_window_pass']}")


if __name__ == '__main__':
    main()
