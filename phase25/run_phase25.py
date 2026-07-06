"""
phase25/run_phase25.py — Multi-Frame STA Pass D Revisit on
pvc-11 monkey1_natural_movie.

Sweeps a 3 (n_lags ∈ {1, 4, 8}) × 4 (bin_ms ∈ {5, 10, 20, 40}) × 2
(variant ∈ {canonical, unconstrained}) configuration grid.

Two stages:
  1.  Per-config GLM fit + fit-quality verification (cheap; no
      surrogate forward sim).  Each (n_lags, bin_ms, variant) cell
      produces a fits.parquet plus a fit-quality verdict.
  2.  For configurations passing fit-quality, generate 5 surrogate
      replicates per cell, extract events at (k=5, w=5 ms) — the
      Phase 22a / 22b event definition for survival comparability —
      classify via ARS at q_max=30, compute survival vs the
      Phase 22a monkey1_natural_movie real classification.

Outputs (per cell):
  data/phase25_results/fits__nlags{N}__bin{B}ms__{variant}.parquet
  data/phase25_results/surrogate_classifications__... .parquet (if PASS)
  data/phase25_results/survival__... .parquet (if PASS)
  data/phase25_results/fit_quality_grid.parquet (one row per cell)
  data/phase25_results/aggregate_verdict.json

The H_PassD verdict aggregates across all cells; the
stim-mis-routing diagnostic is derived by comparing canonical vs
unconstrained kernels at each n_lags > 1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
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
from ars_classify import classify, per_q_columns
from population_events import build_unit_matrix, extract_events
from h2_surrogates import _load_movie

from multiframe_sta import (build_per_bin_stim, compute_multiframe_sta,
                              project_sta_to_drive)
from glm_fit import (basis_config, fit_one_unit, simulate_glm_population,
                      resample_to_5ms, raised_cosine_basis)
from fit_quality import per_unit_pass, configuration_verdict


OUT_DIR_22A = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR_25 = Path(ROOT_DIR) / 'data' / 'phase25_results'
OUT_DIR_25.mkdir(parents=True, exist_ok=True)
SEL_PATH = OUT_DIR_22A / 'unit_selection.parquet'

RECORDING = 'monkey1_natural_movie'
EVENT_BIN_MS = 5.0       # population-event definition fixed at (k=5, w=5ms)
K_THRESH = 5
N_SEEDS = 5
Q_MAX = 30

N_LAGS_GRID = [1, 4, 8]
BIN_MS_GRID = [5.0, 10.0, 20.0, 40.0]
VARIANTS = ['canonical', 'unconstrained']


def cell_tag(n_lags: int, bin_ms: float, variant: str) -> str:
    return f"nlags{n_lags}__bin{int(bin_ms)}ms__{variant}"


def fit_cell(real_mat_event_bin: np.ndarray,
              rec, units: list[int],
              Z: np.ndarray,
              n_lags: int, bin_ms: float, variant: str,
              verbose: bool = True) -> dict:
    """Fit the GLM at one (n_lags, bin_ms, variant) cell.

    real_mat_event_bin is the (n_units, T_at_5ms) real population
    matrix at the 5 ms event-extraction resolution — only used here to
    pass through to the caller for downstream rate comparisons.  The
    GLM is fit at bin_ms (which may differ from 5 ms).

    Returns dict with fit results, per-unit diagnostics, the fitted
    params, and the stim_drive (needed for forward simulation later).
    """
    bin_s = bin_ms / 1000.0
    bins_per_trial = int(round(MOVIE_TRIAL_SEC / bin_s))
    n_trials = rec.n_trials

    if verbose:
        print(f"  [{cell_tag(n_lags, bin_ms, variant)}]")
    t_step = time.time()
    real_mat_glm, _ = build_unit_matrix(rec, units, bin_ms=bin_ms)
    n_units = real_mat_glm.shape[0]
    if verbose: print(f"    build_unit_matrix: {time.time()-t_step:.1f}s  "
                         f"bins_per_trial={bins_per_trial}  n_units={n_units}  "
                         f"n_lags={n_lags}")

    t_step = time.time()
    per_bin_stim = build_per_bin_stim(Z, bin_ms, bins_per_trial)
    if verbose: print(f"    build_per_bin_stim: {time.time()-t_step:.1f}s  "
                         f"shape={per_bin_stim.shape}")

    # Multi-frame STA + projection to per-unit drive.
    t_step = time.time()
    sta = compute_multiframe_sta(real_mat_glm, per_bin_stim,
                                   n_lags, n_trials, bins_per_trial)
    if verbose: print(f"    compute_multiframe_sta: {time.time()-t_step:.1f}s")

    t_step = time.time()
    stim_drive = project_sta_to_drive(sta, per_bin_stim, bins_per_trial)
    if verbose: print(f"    project_sta_to_drive: {time.time()-t_step:.1f}s  "
                         f"drive_l2={float(np.linalg.norm(stim_drive)):.2f}")
                                                                 # (n_units, bins_per_trial)

    cfg = basis_config(bin_ms)
    history_basis = raised_cosine_basis(cfg['n_history_bins'],
                                           cfg['n_history_basis'],
                                           min_offset=0.5, stretch=1.0)
    stim_basis = raised_cosine_basis(cfg['n_stim_bins'],
                                        cfg['n_stim_basis'],
                                        min_offset=0.5, stretch=1.0)

    non_positive = (variant == 'canonical')
    n_p_total = 1 + cfg['n_stim_basis'] + cfg['n_history_basis']
    params_all = np.zeros((n_units, n_p_total))
    fit_rows = []
    t0 = time.time()
    for i in range(n_units):
        unit_stim = np.tile(stim_drive[i], n_trials)
        try:
            params_i, diag = fit_one_unit(real_mat_glm[i].astype(np.float64),
                                            unit_stim, history_basis,
                                            stim_basis, bins_per_trial,
                                            non_positive_history=non_positive)
        except Exception as exc:
            params_i = np.zeros(n_p_total)
            params_i[0] = float(np.log(max(real_mat_glm[i].mean(), 1e-6)))
            diag = dict(converged=False, dev_explained=float('nan'),
                          n_spikes=int(real_mat_glm[i].sum()),
                          n_bins=int(real_mat_glm[i].size),
                          stim_kernel_l2=0.0, stim_kernel_max=0.0,
                          stim_kernel_min=0.0, history_kernel_l2=0.0,
                          history_kernel_max=0.0, history_kernel_min=0.0,
                          history_kernel=[0.0] * cfg['n_history_bins'],
                          stim_kernel=[0.0] * cfg['n_stim_bins'],
                          bias=float(params_i[0]), n_iter=0,
                          ll_glm=float('nan'), ll_null=float('nan'),
                          error=str(exc))
        params_all[i] = params_i
        fit_rows.append(dict(unit_idx=units[i], unit_id=rec.unit_id(units[i]),
                                **diag))
        if verbose and ((i + 1) % 10 == 0 or i == n_units - 1 or i < 2):
            dt = time.time() - t0
            print(f"      {i+1:3d}/{n_units}  ⏱{dt:.0f}s  "
                  f"conv={diag.get('converged', '?')}  "
                  f"dev={diag.get('dev_explained', float('nan')):+.4f}")

    fits_df = pd.DataFrame(fit_rows)

    return dict(
        cfg=cfg, params_all=params_all, stim_drive=stim_drive,
        history_basis=history_basis, stim_basis=stim_basis,
        bins_per_trial=bins_per_trial, n_trials=n_trials,
        n_units=n_units, fits_df=fits_df, real_mat_glm=real_mat_glm,
    )


def verify_fit_quality(cell_state: dict, variant: str,
                         verbose: bool = True) -> dict:
    """Per-unit fit-quality + configuration-level verdict.

    Forward-simulate one seed at the GLM bin width to assess rate
    fidelity (check #4).  This is the only forward sim done in stage 1.
    """
    cfg = cell_state['cfg']
    params_all = cell_state['params_all']
    stim_drive = cell_state['stim_drive']
    real_mat_glm = cell_state['real_mat_glm']
    bins_per_trial = cell_state['bins_per_trial']
    n_trials = cell_state['n_trials']
    n_units = cell_state['n_units']

    rng = np.random.default_rng(0)
    sim_mat = simulate_glm_population(params_all, stim_drive,
                                         cell_state['history_basis'],
                                         cell_state['stim_basis'],
                                         cfg['n_stim_basis'],
                                         bins_per_trial, n_trials, rng)

    real_spk = real_mat_glm.sum(axis=1)
    sur_spk = sim_mat.sum(axis=1)

    fits_df = cell_state['fits_df']
    per_unit_results = []
    for i in range(n_units):
        d = fits_df.iloc[i].to_dict()
        r = per_unit_pass(d, variant, int(real_spk[i]), int(sur_spk[i]))
        r['unit_idx'] = int(d['unit_idx'])
        per_unit_results.append(r)

    dev_med = float(fits_df['dev_explained'].median())
    verdict = configuration_verdict(per_unit_results, dev_med, variant)
    n_pass = sum(int(r['unit_pass']) for r in per_unit_results)
    sur_total = int(sim_mat.sum())
    real_total = int(real_mat_glm.sum())

    if verbose:
        print(f"    fit-quality: {verdict}  "
              f"units_pass={n_pass}/{n_units}  "
              f"dev_med={dev_med:+.4f}  "
              f"sur_rate/real_rate={sur_total/max(real_total,1):.2f}")

    return dict(
        verdict=verdict, dev_med=dev_med,
        n_units_pass=n_pass, n_units_total=n_units,
        sur_total_spikes=sur_total, real_total_spikes=real_total,
        per_unit_results=per_unit_results,
    )


def generate_and_classify_surrogate(cell_state: dict,
                                       bin_ms: float, seed: int,
                                       ) -> dict:
    """Forward-simulate one seed, resample to 5 ms, extract events,
    classify."""
    cfg = cell_state['cfg']
    rng = np.random.default_rng(1_000_000 + seed)
    sim_mat = simulate_glm_population(cell_state['params_all'],
                                         cell_state['stim_drive'],
                                         cell_state['history_basis'],
                                         cell_state['stim_basis'],
                                         cfg['n_stim_basis'],
                                         cell_state['bins_per_trial'],
                                         cell_state['n_trials'], rng)
    sim_5ms = resample_to_5ms(sim_mat, bin_ms, rng)
    events = extract_events(sim_5ms, bin_ms=EVENT_BIN_MS, k_thresh=K_THRESH)
    res = classify(events, return_full=True, q_max=Q_MAX)
    cols = per_q_columns(res['per_q'])
    return dict(
        seed=seed, n_events=int(events.size),
        primary=res['primary'], rep_med=res['rep_med'],
        ks_gue_med=res['ks_gue_med'], n_well=res['n_well'],
        **cols,
    )


def compute_survival(real_rep: np.ndarray, real_quad: list,
                       surrogate_rows: list[dict]) -> tuple[pd.DataFrame, dict]:
    """Compute per-q survival vs the supplied surrogate replicates.

    Survival rules (Phase 22a / 22b convention):
      survives_rep   — real rep_int_q > 95th pct of surrogate rep_int_q.
      survives_quad  — real quadrant differs from surrogate modal quad.
      survives_both  — both true (strict survival).
    """
    sur_reps = np.stack([np.array(list(r['rep_int_per_q']), dtype=float)
                          for r in surrogate_rows])
    pct_hi = np.nanpercentile(sur_reps, 95, axis=0)
    quad_modal = []
    for qi in range(real_rep.size):
        items = [r['quadrants_per_q'][qi] for r in surrogate_rows
                  if r['quadrants_per_q'] is not None
                  and qi < len(r['quadrants_per_q'])]
        items = [x for x in items if x is not None]
        if items:
            quad_modal.append(Counter(items).most_common(1)[0][0])
        else:
            quad_modal.append(None)

    surv_rows = []
    n_rep = n_quad = n_both = 0
    for qi in range(real_rep.size):
        sr = ((not np.isnan(real_rep[qi])) and (not np.isnan(pct_hi[qi]))
                and (real_rep[qi] > pct_hi[qi]))
        rq = real_quad[qi] if qi < len(real_quad) else None
        sq = quad_modal[qi]
        sq_diff = (rq is not None and sq is not None and rq != sq)
        sb = sr and sq_diff
        n_rep += int(sr); n_quad += int(sq_diff); n_both += int(sb)
        surv_rows.append(dict(
            q=qi + 1, real_rep_int=float(real_rep[qi]),
            surr_rep_int_p95=float(pct_hi[qi]),
            real_quadrant=rq, surr_modal_quadrant=sq,
            survives_rep=sr, survives_quad=sq_diff, survives_both=sb,
        ))
    surv_df = pd.DataFrame(surv_rows)
    return surv_df, dict(
        n_rep=n_rep, n_quad=n_quad, n_both=n_both,
        n_qbands=int(real_rep.size),
    )


def run_grid(stage: str = 'all', cells: list[tuple] = None,
              verbose: bool = True):
    """Main orchestrator.

    stage ∈ {'fit', 'surrogate', 'all'} controls which pipeline stages
    run.  cells=[(n_lags, bin_ms, variant), ...] restricts to a subset
    of the grid (default: full grid).
    """
    if cells is None:
        cells = [(nl, bw, v) for nl in N_LAGS_GRID
                  for bw in BIN_MS_GRID for v in VARIANTS]

    print("=" * 72)
    print(f"Phase 25 — Multi-Frame STA Pass D Revisit (stage={stage})")
    print(f"  recording: {RECORDING}, cells: {len(cells)}")
    print("=" * 72)

    sel = pd.read_parquet(SEL_PATH)
    sel_h2 = sel[(sel['recording'] == RECORDING) & sel['h2_pass']]
    units = sel_h2['unit_idx'].astype(int).tolist()
    rec = load(RECORDING)
    Z, _ = _load_movie('natural_movie', rec.monkey)

    # Cache real classification for survival comparison.
    real_pop = pd.read_parquet(OUT_DIR_22A / 'h2_population_classifications.parquet')
    real_row = real_pop[(real_pop['recording'] == RECORDING)
                          & (real_pop['q_max'] == Q_MAX)]
    if not len(real_row):
        raise RuntimeError("no Phase 22a real-data row for "
                           f"{RECORDING} q_max={Q_MAX}")
    real_rep = np.array(list(real_row.iloc[0]['rep_int_per_q']), dtype=float)
    real_quad = list(real_row.iloc[0]['quadrants_per_q'])

    quality_rows = []
    # In stage=surrogate (without fit), load verdicts from disk so we
    # know which cells passed fit-quality.
    if stage == 'surrogate':
        grid_path = OUT_DIR_25 / 'fit_quality_grid.parquet'
        if grid_path.exists():
            quality_rows = pd.read_parquet(grid_path).to_dict('records')
            if verbose: print(f"  loaded {len(quality_rows)} verdicts from disk")

    for n_lags, bin_ms, variant in cells:
        tag = cell_tag(n_lags, bin_ms, variant)
        fits_path = OUT_DIR_25 / f'fits__{tag}.parquet'
        if stage in ('fit', 'all'):
            cell_state = fit_cell(None, rec, units, Z, n_lags, bin_ms, variant,
                                    verbose=verbose)
            cell_state['fits_df'].to_parquet(fits_path, index=False)
            quality = verify_fit_quality(cell_state, variant, verbose=verbose)
            qrow = dict(n_lags=n_lags, bin_ms=bin_ms, variant=variant,
                          **{k: v for k, v in quality.items()
                              if k != 'per_unit_results'})
            quality_rows.append(qrow)
            # Persist cell state for stage-2 surrogate generation.
            state_path = OUT_DIR_25 / f'state__{tag}.npz'
            np.savez(state_path,
                       params_all=cell_state['params_all'],
                       stim_drive=cell_state['stim_drive'],
                       history_basis=cell_state['history_basis'],
                       stim_basis=cell_state['stim_basis'],
                       bins_per_trial=cell_state['bins_per_trial'],
                       n_trials=cell_state['n_trials'],
                       cfg_n_stim_basis=cell_state['cfg']['n_stim_basis'])

        if stage in ('surrogate', 'all'):
            qrow = [r for r in quality_rows
                      if (r['n_lags'], r['bin_ms'], r['variant'])
                          == (n_lags, bin_ms, variant)]
            if qrow and qrow[0]['verdict'] != 'FIT-PROPER':
                if verbose: print(f"    [{tag}] skip surrogate (verdict={qrow[0]['verdict']})")
                continue
            # Reload state (works for both fresh and resumed stage-2 runs)
            state_path = OUT_DIR_25 / f'state__{tag}.npz'
            if not state_path.exists():
                if verbose: print(f"    [{tag}] no state file — skip")
                continue
            st = np.load(state_path)
            cell_state = dict(
                cfg=dict(n_stim_basis=int(st['cfg_n_stim_basis'])),
                params_all=st['params_all'], stim_drive=st['stim_drive'],
                history_basis=st['history_basis'], stim_basis=st['stim_basis'],
                bins_per_trial=int(st['bins_per_trial']),
                n_trials=int(st['n_trials']),
            )
            if verbose: print(f"    [{tag}] generating {N_SEEDS} surrogates...")
            sur_rows = []
            for seed in range(N_SEEDS):
                t0 = time.time()
                r = generate_and_classify_surrogate(cell_state, bin_ms, seed)
                r.update(n_lags=n_lags, bin_ms=bin_ms, variant=variant,
                          surrogate='multiframe_glm', q_max=Q_MAX,
                          n_units=cell_state['params_all'].shape[0])
                sur_rows.append(r)
                if verbose:
                    print(f"      seed {seed}: events={r['n_events']:6d}  "
                          f"primary={r['primary']:13s}  rep_med={r['rep_med']:.3f}  "
                          f"⏱{time.time()-t0:.0f}s")
            sur_df = pd.DataFrame(sur_rows)
            sur_df.to_parquet(OUT_DIR_25 / f'surrogate_classifications__{tag}.parquet',
                                index=False)
            surv_df, surv_summary = compute_survival(real_rep, real_quad, sur_rows)
            surv_df.to_parquet(OUT_DIR_25 / f'survival__{tag}.parquet', index=False)
            if verbose:
                print(f"      survival: rep={surv_summary['n_rep']}/{surv_summary['n_qbands']}  "
                      f"quad={surv_summary['n_quad']}  both={surv_summary['n_both']}")

    if quality_rows:
        pd.DataFrame(quality_rows).to_parquet(
            OUT_DIR_25 / 'fit_quality_grid.parquet', index=False)

    return quality_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', default='all',
                    choices=['fit', 'surrogate', 'all'])
    p.add_argument('--n-lags', type=int, default=None,
                    help='restrict to one n_lags value')
    p.add_argument('--bin-ms', type=float, default=None,
                    help='restrict to one bin_ms value')
    p.add_argument('--variant', default=None,
                    choices=[None, 'canonical', 'unconstrained'])
    p.add_argument('--quiet', action='store_true')
    args = p.parse_args()

    cells = [(nl, bw, v) for nl in N_LAGS_GRID
              for bw in BIN_MS_GRID for v in VARIANTS]
    if args.n_lags is not None:
        cells = [c for c in cells if c[0] == args.n_lags]
    if args.bin_ms is not None:
        cells = [c for c in cells if c[1] == args.bin_ms]
    if args.variant is not None:
        cells = [c for c in cells if c[2] == args.variant]

    run_grid(stage=args.stage, cells=cells, verbose=not args.quiet)


if __name__ == '__main__':
    main()
