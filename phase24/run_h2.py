"""
phase24/run_h2.py — H2 pipeline on the chosen Allen session.

Per Phase 22a methodology:
  - Population events: k=5, w=5ms (defaults; sensitivity grid deferred
    to full Phase 24).
  - ARS classification at q_max=30 on the event timestamp point process.
  - Surrogate battery: rate_matched_poisson, cell_shuffle.
    **ln_evoked deferred**: Allen's stimulus templates are stored
    separately (natural_movie_1.h5 is actually a NumPy .npy file,
    not in the session NWB).  Integrating them into the surrogate
    pipeline is full-Phase-24 work, not triage work.  The triage
    proceeds with the two stimulus-agnostic surrogates; the H2
    verdict character is "structure beyond rate envelope + beyond
    cell-pair shuffle", not the fuller Phase 22a "structure beyond
    LN-Poisson" claim.

Conditions: drifting_pooled, natural_movie_one, spontaneous.
N_SEEDS = 5 (between Phase 22a's 3 and Phase 22b's 7).

Outputs:
  data/phase24_results/h2_population_classifications.parquet
  data/phase24_results/h2_surrogate_classifications.parquet
  data/phase24_results/h2_survival_summary.parquet
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

from loader import load_session, AllenRecording
from ars_classify import classify, per_q_columns


SESSION_ID = 732592105
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase24_results'

BIN_MS = 5.0
K_THRESH = 5
N_SEEDS = 5
Q_MAX = 30


def build_unit_matrix_from_chunks(rec: AllenRecording,
                                    unit_ids: list[int],
                                    chunks: list[tuple[float, float]],
                                    bin_ms: float = BIN_MS,
                                    ) -> tuple[np.ndarray, float]:
    """Build a (n_units × n_bins) per-bin spike-count matrix by
    concatenating the supplied (start_s, stop_s) chunks end-to-end.

    chunks: list of (start, stop) seconds in original recording time.
    """
    bin_s = bin_ms / 1000.0
    chunk_durs = [stop - start for start, stop in chunks]
    chunk_bins = [int(np.ceil(d / bin_s)) for d in chunk_durs]
    total_bins = sum(chunk_bins)
    total_dur = total_bins * bin_s
    mat = np.zeros((len(unit_ids), total_bins), dtype=np.int32)
    for i, uid in enumerate(unit_ids):
        sp = rec.spike_times.get(int(uid), np.zeros(0))
        offset_bins = 0
        for (start, stop), n_bins in zip(chunks, chunk_bins):
            mask = (sp >= start) & (sp < stop)
            ev = sp[mask] - start
            bin_idx = np.floor(ev / bin_s).astype(np.int64)
            bin_idx = bin_idx[(bin_idx >= 0) & (bin_idx < n_bins)]
            np.add.at(mat[i], bin_idx + offset_bins, 1)
            offset_bins += n_bins
    return mat, total_dur


def extract_events_synchronous(unit_matrix, bin_ms=BIN_MS, k=K_THRESH):
    """Synchronous-firing events: bins where ≥k units fire ≥1 spike."""
    binary = (unit_matrix > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    bin_idx = np.where(coact >= k)[0]
    return (bin_idx + 0.5) * (bin_ms / 1000.0)


# ─── condition chunks ──────────────────────────────────────────────────────


def chunks_drifting(rec):
    """All drifting-grating presentations end-to-end."""
    return [(float(r['start_time']), float(r['stop_time']))
              for _, r in rec.drifting_gratings.iterrows()]


def chunks_natural_movie_one(rec):
    """Per-block start/stop for natural_movie_one (one block = one full clip)."""
    out = []
    for blk, g in rec.natural_movie_one.groupby('stimulus_block', sort=True):
        out.append((float(g['start_time'].min()), float(g['stop_time'].max())))
    return out


def chunks_spontaneous(rec, min_block_sec=5.0):
    return [(float(r['start_time']), float(r['stop_time']))
              for _, r in rec.spontaneous.iterrows()
              if r['stop_time'] - r['start_time'] >= min_block_sec]


# ─── surrogates ────────────────────────────────────────────────────────────


def surrogate_rate_matched_poisson(real_mat: np.ndarray,
                                     rng: np.random.Generator) -> np.ndarray:
    n_units, n_bins = real_mat.shape
    rates = real_mat.sum(axis=1) / max(n_bins, 1)
    return rng.poisson(rates[:, None], size=(n_units, n_bins)).astype(np.int32)


def surrogate_cell_shuffle(real_mat: np.ndarray, chunk_sizes: list[int],
                              rng: np.random.Generator) -> np.ndarray:
    """Per-(unit, chunk) circular shift, preserving per-chunk count."""
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


# ─── orchestrator ──────────────────────────────────────────────────────────


def main():
    print("=" * 80)
    print(f"Phase 24 H2 — Allen session {SESSION_ID}")
    print("=" * 80)
    print(f"  bin: {BIN_MS}ms  k_thresh: {K_THRESH}  n_seeds: {N_SEEDS}  q_max: {Q_MAX}")
    print()

    rec = load_session(SESSION_ID)
    h2_units = rec.units.index.tolist()
    print(f"  H2-passing V1 units (Allen QC): {len(h2_units)}")
    print()

    cond_specs = [
        ('drifting_pooled',     chunks_drifting),
        ('natural_movie_one',   chunks_natural_movie_one),
        ('spontaneous',         chunks_spontaneous),
    ]

    real_rows = []
    surr_rows = []
    for cond_name, chunk_fn in cond_specs:
        print(f"--- {cond_name} ---")
        chunks = chunk_fn(rec)
        if not chunks:
            print(f"  no chunks; skip")
            continue
        bin_s = BIN_MS / 1000.0
        chunk_sizes = [int(np.ceil((stop - start) / bin_s)) for start, stop in chunks]
        t0 = time.time()
        real_mat, total_dur = build_unit_matrix_from_chunks(
            rec, h2_units, chunks)
        print(f"  matrix {real_mat.shape}, total_dur={total_dur:.1f}s  "
              f"({time.time()-t0:.0f}s)")

        # Real classification
        events = extract_events_synchronous(real_mat, BIN_MS, K_THRESH)
        rate_hz = events.size / max(total_dur, 1e-9)
        t0 = time.time()
        res = classify(events, return_full=True, q_max=Q_MAX)
        cols = per_q_columns(res['per_q'])
        print(f"  real: events={events.size:,}, rate={rate_hz:.1f}/s, "
              f"primary={res['primary']}, rep_med={res['rep_med']:.3f}  "
              f"({time.time()-t0:.0f}s)")
        real_rows.append(dict(
            condition=cond_name, n_units=len(h2_units),
            n_events=int(events.size), event_rate_hz=rate_hz,
            total_dur_sec=total_dur, primary=res['primary'],
            rep_med=res['rep_med'], ks_gue_med=res['ks_gue_med'],
            n_well=res['n_well'], **cols,
        ))

        # Surrogates
        for sur_name, gen in [
                ('rate_matched_poisson',
                 lambda m, rng: surrogate_rate_matched_poisson(m, rng)),
                ('cell_shuffle',
                 lambda m, rng: surrogate_cell_shuffle(m, chunk_sizes, rng)),
        ]:
            t0 = time.time()
            for seed in range(N_SEEDS):
                rng = np.random.default_rng(seed)
                sur_mat = gen(real_mat, rng)
                events = extract_events_synchronous(sur_mat, BIN_MS, K_THRESH)
                res = classify(events, return_full=True, q_max=Q_MAX)
                cols = per_q_columns(res['per_q'])
                surr_rows.append(dict(
                    condition=cond_name, surrogate=sur_name, seed=seed,
                    n_units=len(h2_units), n_events=int(events.size),
                    primary=res['primary'], rep_med=res['rep_med'],
                    ks_gue_med=res['ks_gue_med'], n_well=res['n_well'],
                    **cols,
                ))
            print(f"  {sur_name}: {N_SEEDS} seeds  ({time.time()-t0:.0f}s)")
        print()

    real_df = pd.DataFrame(real_rows)
    surr_df = pd.DataFrame(surr_rows)
    real_df.to_parquet(OUT_DIR / 'h2_population_classifications.parquet',
                        index=False)
    surr_df.to_parquet(OUT_DIR / 'h2_surrogate_classifications.parquet',
                        index=False)
    print(f"  → {OUT_DIR}/h2_population_classifications.parquet  "
          f"({len(real_df)} rows)")
    print(f"  → {OUT_DIR}/h2_surrogate_classifications.parquet  "
          f"({len(surr_df)} rows)")
    print()

    # ─── survival verdict ─────
    print("Survival verdict per (condition, surrogate):")
    surv_rows = []
    for _, real_row in real_df.iterrows():
        cond = real_row['condition']
        real_rep = np.array(list(real_row['rep_int_per_q']), dtype=float)
        real_quad = list(real_row['quadrants_per_q'])
        for sur_name in ('rate_matched_poisson', 'cell_shuffle'):
            sg = surr_df[(surr_df['condition'] == cond)
                          & (surr_df['surrogate'] == sur_name)]
            if not len(sg): continue
            arrs = [np.array(list(r['rep_int_per_q']), dtype=float)
                       for _, r in sg.iterrows()]
            stack = np.stack(arrs)
            pct95 = np.nanpercentile(stack, 95, axis=0)
            quad_modal = []
            for qi in range(real_rep.size):
                items = [r['quadrants_per_q'][qi]
                          for _, r in sg.iterrows()
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
                condition=cond, surrogate=sur_name,
                n_q_total=int(real_rep.size),
                n_q_rep_survives=n_rep, n_q_quad_diff=n_quad,
                n_q_both=n_both,
                survives_at_any_q=(n_both > 0),
            ))
            print(f"  {cond:20s} {sur_name:25s}  "
                  f"rep_survives={n_rep}/{real_rep.size}  "
                  f"quad_diff={n_quad}/{real_rep.size}  "
                  f"both={n_both}/{real_rep.size}")
    surv_df = pd.DataFrame(surv_rows)
    surv_df.to_parquet(OUT_DIR / 'h2_survival_summary.parquet', index=False)
    print()

    # Required-conjunction verdict per condition
    print("Per-condition required-conjunction verdict:")
    print("  (Allen H2 surrogate set: rate_matched_poisson + cell_shuffle;")
    print("   ln_evoked deferred — Allen stimulus templates need separate handling.)")
    for cond_name, _ in cond_specs:
        sub = surv_df[surv_df['condition'] == cond_name]
        if not len(sub): continue
        n_pass = int(sub['survives_at_any_q'].sum())
        all_pass = int(sub['survives_at_any_q'].all())
        verdict = ('PASS' if all_pass else 'PARTIAL' if n_pass > 0 else 'NULL')
        print(f"  {cond_name:25s}  {n_pass}/{len(sub)} surrogates pass — {verdict}")


if __name__ == '__main__':
    main()
