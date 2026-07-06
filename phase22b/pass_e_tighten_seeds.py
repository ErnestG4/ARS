"""
phase22b/pass_e_tighten_seeds.py — Phase 22b Pass E (optional).

Re-run the Phase 22a surrogate battery (rate_matched_poisson,
cell_shuffle, ln_evoked) at N_SEEDS=7 (up from 3) for the two
cleanly-passing H2 recordings (monkey1_natural_movie,
monkey2_gratings_movie) and recompute the 95th-percentile threshold.
Verify the Phase 22a verdicts hold under tighter null estimation.

This addresses the "3 seeds is noisier than 5+" caveat directly.
Likely overkill for the cleanly-passing cases (Phase 22a real values
are ~6× the surrogate median), but eliminates the caveat fully.

Outputs:
  data/phase22b_results/pass_e_surrogate_classifications.parquet
  data/phase22b_results/pass_e_survival.parquet
  Stdout: per-recording survival counts vs Phase 22a 3-seed.
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

from loader import load
from ars_classify import classify, per_q_columns
from population_events import (
    build_unit_matrix, extract_events,
    BIN_MS_DEFAULT, K_THRESH_DEFAULT,
)
from h2_surrogates import (
    surrogate_rate_matched_poisson, surrogate_cell_shuffle,
    surrogate_ln_evoked,
)


OUT_DIR_22A = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR_22B = Path(ROOT_DIR) / 'data' / 'phase22b_results'
OUT_DIR_22B.mkdir(parents=True, exist_ok=True)
SEL_PATH = OUT_DIR_22A / 'unit_selection.parquet'

N_SEEDS = 7
RECORDINGS = ['monkey1_natural_movie', 'monkey2_gratings_movie']
SURROGATE_KINDS = {
    'rate_matched_poisson': surrogate_rate_matched_poisson,
    'cell_shuffle':         surrogate_cell_shuffle,
    'ln_evoked':            surrogate_ln_evoked,
}
BIN_MS = BIN_MS_DEFAULT
K_THRESH = K_THRESH_DEFAULT
Q_MAX = 30


def main():
    print("=" * 72)
    print("Phase 22b Pass E — tighten surrogate replicates 3→7 on cleanly-")
    print("passing H2 recordings (monkey1_natural_movie, monkey2_gratings_movie)")
    print("=" * 72)

    sel = pd.read_parquet(SEL_PATH)
    real_pop = pd.read_parquet(OUT_DIR_22A / 'h2_population_classifications.parquet')

    surrogate_rows = []
    for rec_name in RECORDINGS:
        rec = load(rec_name)
        h2_units = sel[(sel['recording'] == rec_name) &
                         sel['h2_pass']]['unit_idx'].astype(int).tolist()
        print(f"\n--- {rec_name}, {len(h2_units)} H2 units ---")
        for kind, fn in SURROGATE_KINDS.items():
            t0 = time.time()
            for seed in range(N_SEEDS):
                sur_mat = fn(rec, h2_units, BIN_MS, seed)
                events = extract_events(sur_mat, bin_ms=BIN_MS,
                                          k_thresh=K_THRESH)
                res = classify(events, return_full=True, q_max=Q_MAX)
                cols = per_q_columns(res['per_q'])
                surrogate_rows.append(dict(
                    recording=rec_name, surrogate=kind, seed=seed,
                    q_max=Q_MAX, n_units=len(h2_units),
                    n_events=int(events.size),
                    primary=res['primary'], rep_med=res['rep_med'],
                    ks_gue_med=res['ks_gue_med'], n_well=res['n_well'],
                    **cols,
                ))
            print(f"    {kind:25s}  {N_SEEDS} seeds  ⏱{time.time()-t0:.0f}s")

    sur_df = pd.DataFrame(surrogate_rows)
    sur_df.to_parquet(OUT_DIR_22B / 'pass_e_surrogate_classifications.parquet',
                       index=False)
    print(f"\n  → {OUT_DIR_22B}/pass_e_surrogate_classifications.parquet  "
          f"({len(sur_df)} rows)")

    # Survival vs Phase 22a real
    from collections import Counter
    surv_rows = []
    for rec_name in RECORDINGS:
        real_row = real_pop[(real_pop['recording'] == rec_name) &
                              (real_pop['q_max'] == Q_MAX)]
        if not len(real_row): continue
        real_row = real_row.iloc[0]
        real_rep = np.array(list(real_row['rep_int_per_q']), dtype=float)
        real_quad = list(real_row['quadrants_per_q'])

        for kind in SURROGATE_KINDS:
            sg = sur_df[(sur_df['recording'] == rec_name) &
                          (sur_df['surrogate'] == kind)]
            if not len(sg): continue
            sur_reps = np.stack([np.array(list(r['rep_int_per_q']),
                                            dtype=float)
                                   for _, r in sg.iterrows()])
            pct_hi = np.nanpercentile(sur_reps, 95, axis=0)
            quad_modal = []
            for qi in range(real_rep.size):
                items = [r['quadrants_per_q'][qi]
                          for _, r in sg.iterrows()
                          if r['quadrants_per_q'] is not None
                          and qi < len(r['quadrants_per_q'])]
                items = [x for x in items if x is not None]
                if items:
                    quad_modal.append(Counter(items).most_common(1)[0][0])
                else:
                    quad_modal.append(None)
            n_rep = n_quad = n_both = 0
            for qi in range(real_rep.size):
                sr = (not np.isnan(real_rep[qi])
                       and not np.isnan(pct_hi[qi])
                       and real_rep[qi] > pct_hi[qi])
                rq = real_quad[qi] if qi < len(real_quad) else None
                sq = quad_modal[qi]
                sq_diff = (rq is not None and sq is not None and rq != sq)
                sb = sr and sq_diff
                n_rep += int(sr); n_quad += int(sq_diff); n_both += int(sb)
            surv_rows.append(dict(
                recording=rec_name, surrogate=kind, n_seeds=N_SEEDS,
                q_max=Q_MAX, n_q_total=int(real_rep.size),
                n_q_rep_survives=n_rep,
                n_q_quad_diff=n_quad, n_q_both=n_both,
            ))

    surv_df = pd.DataFrame(surv_rows)
    surv_df.to_parquet(OUT_DIR_22B / 'pass_e_survival.parquet', index=False)
    print()
    print("Pass E survival vs Phase 22a real-data q_max=30 (tightened to 7 seeds):")
    print(surv_df.to_string(index=False))
    print()

    # Verdict
    print("Verdict per recording:")
    for rec_name in RECORDINGS:
        sub = surv_df[surv_df['recording'] == rec_name]
        if not len(sub): continue
        all_pass = all(r['n_q_both'] >= 1 for _, r in sub.iterrows())
        n_pass = int((sub['n_q_both'] >= 1).sum())
        print(f"  {rec_name}: {n_pass}/{len(sub)} surrogates pass (both rep + quad criteria) "
              f"— Phase 22a verdict {'CONFIRMED' if all_pass else 'WEAKENED'}")


if __name__ == '__main__':
    main()
