"""
phase24/run_per_session_h2.py — per-session H2 with surrogate battery
at default (k=5, w=5ms) AND rate-matched (k, w) configurations.

Per-condition surrogate set:
  natural_movie_one: rate_matched_poisson + cell_shuffle + ln_evoked
  drifting_pooled:   rate_matched_poisson + cell_shuffle + ln_evoked (grating template)
  spontaneous:       rate_matched_poisson + cell_shuffle (no ln_evoked — stimulus-free)

5 seeds per (config, surrogate, session).

The rate-matched (k, w) per session comes from
`data/phase24_results/rate_matched_configs.parquet` (output of
run_sensitivity_grid.py).  Default config is (k=5, w=5ms) for all sessions.

Outputs:
  data/phase24_results/per_session_h2_population.parquet
  data/phase24_results/per_session_h2_surrogate.parquet
  data/phase24_results/per_session_h2_survival.parquet
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, THIS_DIR)

from loader import (load_session, load_natural_movie_one_template,
                       align_movie_template_to_population_bins,
                       grating_template_per_bin)
from ars_classify import classify, per_q_columns


CANDIDATE_PATH = Path('$HOME/fmexplorer/allen_cache/phase24_candidate_sessions.csv')
RATE_MATCHED_PATH = Path('$HOME/fmexplorer/criticality_tool/data/phase24_results/rate_matched_configs.parquet')
OUT_DIR = Path('$HOME/fmexplorer/criticality_tool/data/phase24_results')

N_SEEDS = 5
Q_MAX = 30
ETA_MAX_SIM = 5.0


# ─── matrix construction (shared) ──────────────────────────────────────────


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
    return mat, total_dur, chunk_bins


def extract_events(unit_matrix, bin_ms, k):
    binary = (unit_matrix > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    return (np.where(coact >= k)[0] + 0.5) * (bin_ms / 1000.0)


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


# ─── surrogates ────────────────────────────────────────────────────────────


def surrogate_rate_matched_poisson(real_mat, rng):
    n_units, n_bins = real_mat.shape
    rates = real_mat.sum(axis=1) / max(n_bins, 1)
    return rng.poisson(rates[:, None], size=(n_units, n_bins)).astype(np.int32)


def surrogate_cell_shuffle(real_mat, chunk_sizes, rng):
    n_units, n_bins = real_mat.shape
    sur = np.empty_like(real_mat)
    for i in range(n_units):
        offset = 0
        for cs in chunk_sizes:
            sl = slice(offset, offset + cs)
            shift = int(rng.integers(0, max(cs, 1)))
            sur[i, sl] = np.roll(real_mat[i, sl], shift)
            offset += cs
    return sur


def surrogate_ln_evoked(real_mat, stim_per_bin, chunk_sizes, rng):
    """Per-unit STA-based LN-Poisson surrogate.  stim_per_bin is the
    (n_bins, n_pixels) stimulus matrix matching real_mat's bin layout
    (same total_bins, same chunk boundaries).

    Per-unit fit: STA + linear gain + bias + Poisson sampling.  Forward
    rates clipped to exp(ETA_MAX_SIM) to keep simulation stable.
    """
    n_units, n_bins = real_mat.shape
    if stim_per_bin.shape[0] != n_bins:
        # Length mismatch — fall back to rate-matched Poisson
        return surrogate_rate_matched_poisson(real_mat, rng)
    real32 = real_mat.astype(np.float32)
    # Per-unit STA: weighted-by-spike average of stim
    weights = real32.sum(axis=1, keepdims=True) + 1e-9
    sta = (real32 @ stim_per_bin) / weights              # (n_units, n_pix)
    sta = sta - sta.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(sta, axis=1, keepdims=True) + 1e-9
    sta = sta / norms
    # Drive per (unit, bin) = STA · stim
    drive = sta @ stim_per_bin.T                          # (n_units, n_bins)
    drive_pos = np.maximum(drive, 0)
    # Per-unit: rate = base + gain * drive_pos
    base = np.zeros(n_units)
    gain = np.zeros(n_units)
    for i in range(n_units):
        d = drive_pos[i]; r = real32[i]
        A = np.column_stack([np.ones_like(d), d])
        try:
            beta, *_ = np.linalg.lstsq(A, r, rcond=None)
            base[i] = max(float(beta[0]), 0.0)
            gain[i] = max(float(beta[1]), 0.0)
        except Exception:
            base[i] = float(r.mean()); gain[i] = 0.0
    rates = base[:, None] + gain[:, None] * drive_pos
    rates = np.clip(rates, 0, np.exp(ETA_MAX_SIM))
    return rng.poisson(rates).astype(np.int32)


# ─── orchestrator per session ──────────────────────────────────────────────


def process_session(srow, rate_matched_row, template_movie):
    sid = int(srow['ecephys_session_id'])
    nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')
    if not nwb_path.exists() or nwb_path.stat().st_size < 1_000_000_000:
        return [], [], []
    rec = load_session(sid)
    unit_ids = list(rec.units.index)

    rm_k = int(rate_matched_row['rate_matched_k']) if rate_matched_row is not None else 5
    rm_w = float(rate_matched_row['rate_matched_w_ms']) if rate_matched_row is not None else 5.0

    pop_rows, sur_rows, surv_rows = [], [], []
    for cfg_label, (k, w) in [('default', (5, 5.0)),
                                  ('rate_matched', (rm_k, rm_w))]:
        if cfg_label == 'rate_matched' and (k == 5 and w == 5.0):
            continue   # rate-matched is the default; skip duplicate
        for cond in ['natural_movie_one', 'drifting_pooled', 'spontaneous']:
            chunks = chunks_for(rec, cond)
            if not chunks: continue
            t0 = time.time()
            mat, total_dur, chunk_bins = build_unit_matrix_chunks(
                rec, unit_ids, chunks, w)
            events = extract_events(mat, w, k)
            res = classify(events, return_full=True, q_max=Q_MAX)
            cols = per_q_columns(res['per_q'])
            pop_rows.append(dict(
                session_id=sid, cre_line=srow['cre_line'],
                config=cfg_label, k_thresh=int(k), w_ms=float(w),
                condition=cond, n_units=len(unit_ids),
                n_events=int(events.size),
                event_rate_hz=float(events.size / max(total_dur, 1e-9)),
                total_dur_sec=float(total_dur),
                primary=res['primary'], rep_med=res['rep_med'],
                ks_gue_med=res['ks_gue_med'], n_well=res['n_well'],
                **cols,
            ))

            # Build stim_per_bin for ln_evoked if applicable
            stim_per_bin = None
            if cond == 'natural_movie_one' and template_movie is not None:
                try:
                    stim_per_bin, _ = align_movie_template_to_population_bins(
                        rec, template_movie, bin_ms=w, downsample=12)
                    # truncate or pad to match mat columns
                    if stim_per_bin.shape[0] != mat.shape[1]:
                        m = min(stim_per_bin.shape[0], mat.shape[1])
                        stim_per_bin = stim_per_bin[:m]
                except Exception as e:
                    stim_per_bin = None
            elif cond == 'drifting_pooled':
                try:
                    stim_per_bin, _ = grating_template_per_bin(
                        rec, 'drifting', bin_ms=w, grid_pixels=16)
                    if stim_per_bin.shape[0] != mat.shape[1]:
                        m = min(stim_per_bin.shape[0], mat.shape[1])
                        stim_per_bin = stim_per_bin[:m]
                except Exception:
                    stim_per_bin = None

            # Surrogates
            sur_kinds = [('rate_matched_poisson', None),
                            ('cell_shuffle', None)]
            if cond != 'spontaneous' and stim_per_bin is not None and stim_per_bin.shape[0] == mat.shape[1]:
                sur_kinds.append(('ln_evoked', stim_per_bin))
            for sur_name, stim_data in sur_kinds:
                for seed in range(N_SEEDS):
                    rng = np.random.default_rng(seed)
                    if sur_name == 'rate_matched_poisson':
                        sur = surrogate_rate_matched_poisson(mat, rng)
                    elif sur_name == 'cell_shuffle':
                        sur = surrogate_cell_shuffle(mat, chunk_bins, rng)
                    else:  # ln_evoked
                        sur = surrogate_ln_evoked(mat, stim_data, chunk_bins, rng)
                    ev = extract_events(sur, w, k)
                    sres = classify(ev, return_full=True, q_max=Q_MAX)
                    scols = per_q_columns(sres['per_q'])
                    sur_rows.append(dict(
                        session_id=sid, cre_line=srow['cre_line'],
                        config=cfg_label, k_thresh=int(k), w_ms=float(w),
                        condition=cond, surrogate=sur_name, seed=int(seed),
                        n_units=len(unit_ids),
                        n_events=int(ev.size),
                        primary=sres['primary'], rep_med=sres['rep_med'],
                        ks_gue_med=sres['ks_gue_med'], n_well=sres['n_well'],
                        **scols,
                    ))

            # Survival per surrogate
            real_rep = np.array(list(res['per_q']['rep_int_q'].tolist()),
                                  dtype=float)
            real_quad = list(res['per_q']['quadrant'].tolist())
            for sur_name, _ in sur_kinds:
                sg = [r for r in sur_rows
                        if r['session_id'] == sid and r['config'] == cfg_label
                        and r['condition'] == cond and r['surrogate'] == sur_name]
                if not sg: continue
                stack = np.stack([np.array(list(r['rep_int_per_q']), dtype=float)
                                    for r in sg])
                pct95 = np.nanpercentile(stack, 95, axis=0)
                quad_modal = []
                for qi in range(real_rep.size):
                    items = [r['quadrants_per_q'][qi] for r in sg
                              if r['quadrants_per_q'] is not None
                              and qi < len(r['quadrants_per_q'])]
                    items = [x for x in items if x is not None]
                    quad_modal.append(Counter(items).most_common(1)[0][0]
                                        if items else None)
                n_rep = n_quad = n_both = 0
                for qi in range(real_rep.size):
                    sr = (not np.isnan(real_rep[qi])
                           and not np.isnan(pct95[qi])
                           and real_rep[qi] > pct95[qi])
                    rq = real_quad[qi] if qi < len(real_quad) else None
                    sq = quad_modal[qi]
                    sq_diff = (rq is not None and sq is not None and rq != sq)
                    sb = sr and sq_diff
                    n_rep += int(sr); n_quad += int(sq_diff); n_both += int(sb)
                surv_rows.append(dict(
                    session_id=sid, cre_line=srow['cre_line'],
                    config=cfg_label, k_thresh=int(k), w_ms=float(w),
                    condition=cond, surrogate=sur_name,
                    n_q_total=int(real_rep.size),
                    n_q_rep_survives=n_rep,
                    n_q_quad_diff=n_quad,
                    n_q_both=n_both,
                    survives_at_any_q=(n_both > 0),
                ))
            print(f"  {cfg_label:12s} {cond:20s} k={k} w={w:.0f}ms: "
                    f"events={events.size:5d}, real={res['primary']:13s} rep={res['rep_med']:.3f}  "
                    f"⏱{time.time()-t0:.0f}s",
                    flush=True)

    return pop_rows, sur_rows, surv_rows


def main():
    print("=" * 80)
    print("Phase 24 Full — per-session H2 with surrogates at default + rate-matched")
    print("=" * 80)

    candidates = pd.read_csv(CANDIDATE_PATH)
    rate_matched = (pd.read_parquet(RATE_MATCHED_PATH).set_index('session_id')
                       if RATE_MATCHED_PATH.exists() else None)
    if rate_matched is None:
        print("  WARN: rate_matched_configs.parquet not found; using default for all")
    else:
        print(f"  rate-matched configs loaded for {len(rate_matched)} sessions")

    template_movie = None
    try:
        template_movie = load_natural_movie_one_template()
        print(f"  natural_movie_one template loaded: {template_movie.shape}")
    except Exception as e:
        print(f"  WARN: natural_movie_one template not available: {e}")

    pop_all, sur_all, surv_all = [], [], []
    for _, srow in candidates.iterrows():
        sid = int(srow['ecephys_session_id'])
        nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')
        if not nwb_path.exists() or nwb_path.stat().st_size < 1_000_000_000:
            print(f"\n  session {sid}: NWB not ready; skip")
            continue
        rate_matched_row = (rate_matched.loc[sid].to_dict()
                              if rate_matched is not None and sid in rate_matched.index
                              else None)
        print(f"\n--- session {sid} ({srow['cre_line']}) ---")
        t0 = time.time()
        try:
            pop, sur, surv = process_session(srow, rate_matched_row, template_movie)
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"  session {sid}: error: {e}")
            continue
        pop_all.extend(pop); sur_all.extend(sur); surv_all.extend(surv)
        print(f"  session done in {time.time()-t0:.0f}s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if pop_all:
        pd.DataFrame(pop_all).to_parquet(OUT_DIR / 'per_session_h2_population.parquet',
                                              index=False)
        print(f"\n  → per_session_h2_population.parquet  ({len(pop_all)} rows)")
    if sur_all:
        pd.DataFrame(sur_all).to_parquet(OUT_DIR / 'per_session_h2_surrogate.parquet',
                                              index=False)
        print(f"  → per_session_h2_surrogate.parquet  ({len(sur_all)} rows)")
    if surv_all:
        surv_df = pd.DataFrame(surv_all)
        surv_df.to_parquet(OUT_DIR / 'per_session_h2_survival.parquet', index=False)
        print(f"  → per_session_h2_survival.parquet  ({len(surv_df)} rows)")
        # Quick verdict
        print()
        for cfg in ('default', 'rate_matched'):
            print(f"--- {cfg} config H2 PASS counts ---")
            sub = surv_df[surv_df['config'] == cfg]
            for cond in ('natural_movie_one', 'drifting_pooled', 'spontaneous'):
                ssub = sub[sub['condition'] == cond]
                if not len(ssub): continue
                # Per-session: pass if ALL surrogates for that session pass
                per_sess = ssub.groupby('session_id')['survives_at_any_q'].all()
                n_pass = int(per_sess.sum())
                n_total = len(per_sess)
                print(f"  {cond:25s}  {n_pass}/{n_total} sessions pass all surrogates")


if __name__ == '__main__':
    main()
