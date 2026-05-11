"""
phase25/reverdict.py — recompute fit-quality verdicts from saved
fits__*.parquet + state__*.npz outputs, using the current
fit_quality.py logic.

Used to repair verdicts on cells fit before a fit_quality.py update,
without re-running the GLM fits themselves.  Surrogate rate-ratio is
re-derived by simulating one seed at the GLM bin width from the saved
state files.
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
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22b'))
sys.path.insert(0, THIS_DIR)

from loader import load, MOVIE_TRIAL_SEC
from population_events import build_unit_matrix

from glm_fit import simulate_glm_population
from fit_quality import per_unit_pass, configuration_verdict


OUT_DIR_22A = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR_25 = Path(ROOT_DIR) / 'data' / 'phase25_results'
SEL_PATH = OUT_DIR_22A / 'unit_selection.parquet'

RECORDING = 'monkey1_natural_movie'
N_LAGS_GRID = [1, 4, 8]
BIN_MS_GRID = [5.0, 10.0, 20.0, 40.0]
VARIANTS = ['canonical', 'unconstrained']


def reverdict_cell(n_lags: int, bin_ms: float, variant: str,
                     real_total_by_bw: dict, rec, units: list[int],
                     ) -> dict:
    tag = f"nlags{n_lags}__bin{int(bin_ms)}ms__{variant}"
    fits_path = OUT_DIR_25 / f'fits__{tag}.parquet'
    state_path = OUT_DIR_25 / f'state__{tag}.npz'
    if not fits_path.exists() or not state_path.exists():
        return None

    fits_df = pd.read_parquet(fits_path)
    n_units = len(fits_df)
    st = np.load(state_path)
    params_all = st['params_all']
    stim_drive = st['stim_drive']
    history_basis = st['history_basis']
    stim_basis = st['stim_basis']
    bins_per_trial = int(st['bins_per_trial'])
    n_trials = int(st['n_trials'])
    n_stim_basis = int(st['cfg_n_stim_basis'])

    rng = np.random.default_rng(0)
    sim_mat = simulate_glm_population(params_all, stim_drive,
                                         history_basis, stim_basis,
                                         n_stim_basis, bins_per_trial,
                                         n_trials, rng)
    sur_total_per_unit = sim_mat.sum(axis=1)

    real_total_per_unit = real_total_by_bw[bin_ms]

    per_unit_results = []
    for i in range(n_units):
        d = fits_df.iloc[i].to_dict()
        r = per_unit_pass(d, variant, int(real_total_per_unit[i]),
                            int(sur_total_per_unit[i]))
        r['unit_idx'] = int(d['unit_idx'])
        per_unit_results.append(r)

    dev_med = float(fits_df['dev_explained'].median())
    verdict = configuration_verdict(per_unit_results, dev_med, variant)
    n_pass = sum(int(r['unit_pass']) for r in per_unit_results)

    return dict(
        n_lags=n_lags, bin_ms=bin_ms, variant=variant,
        verdict=verdict, dev_med=dev_med,
        n_units_pass=n_pass, n_units_total=n_units,
        sur_total_spikes=int(sim_mat.sum()),
        real_total_spikes=int(real_total_per_unit.sum()),
    )


def main():
    sel = pd.read_parquet(SEL_PATH)
    sel_h2 = sel[(sel['recording'] == RECORDING) & sel['h2_pass']]
    units = sel_h2['unit_idx'].astype(int).tolist()
    rec = load(RECORDING)

    # Cache real per-unit spike totals at each bin width
    real_total_by_bw = {}
    for bw in BIN_MS_GRID:
        real_mat, _ = build_unit_matrix(rec, units, bin_ms=bw)
        real_total_by_bw[bw] = real_mat.sum(axis=1)
        print(f"  real total spikes at {bw} ms: {int(real_mat.sum())} "
              f"(across {len(units)} units)")

    rows = []
    for nl in N_LAGS_GRID:
        for bw in BIN_MS_GRID:
            for v in VARIANTS:
                row = reverdict_cell(nl, bw, v, real_total_by_bw, rec, units)
                if row is None:
                    print(f"  nlags{nl} bin{int(bw)}ms {v}: skip (no fits yet)")
                    continue
                rows.append(row)
                print(f"  nlags{nl} bin{int(bw)}ms {v:13s}  "
                       f"verdict={row['verdict']:32s}  "
                       f"pass={row['n_units_pass']:2d}/{row['n_units_total']}  "
                       f"dev_med={row['dev_med']:+.4f}  "
                       f"sur/real={row['sur_total_spikes']/max(row['real_total_spikes'],1):.2f}")

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR_25 / 'fit_quality_grid.parquet', index=False)
    print(f"  → wrote fit_quality_grid.parquet ({len(df)} cells)")


if __name__ == '__main__':
    main()
