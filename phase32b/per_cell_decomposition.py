"""
phase32b/per_cell_decomposition.py — Phase 32b per-cell follow-up.

The Phase 32b cross-engine result on Allen at n=6 sessions returned
INDEPENDENT_AXES at the per-session aggregate level (cross-engine
Spearman |rho| <= 0.093 across four scoring variants).  The follow-up
question, flagged at the bottom of PHASE32B_FINDINGS.md, is whether the
cross-engine independence holds at the per-cell level: regress per-cell
per-window p=7 aggregate against the per-cell Williamson-FA loadings
the Phase 27 protocol established, and replicate the Phase 27 SUBSUMED
(ks_gue_med) / ORTHOGONAL (rep_med) pattern on Allen for direct cross-
substrate comparison.

Verdict categories (per V1 close brief):
  - BOTH_ORTHOGONAL: per-window p=7 ORTHOGONAL to FA, rep_med
    ORTHOGONAL.  Two novel substrate-systematic axes outside the FA.
    Strongest INDEPENDENT_AXES reading.
  - p7_ABSORBED_F1F0_ORTHOGONAL: per-window p=7 SUBSUMED by FA,
    rep_med ORTHOGONAL.  INDEPENDENT_AXES reduces to one novel +
    one FA-loadable axis.
  - BOTH_ABSORBED: per-window p=7 and rep_med both SUBSUMED by FA on
    Allen.  Cross-engine result is FA-decomposable cross-engine
    agreement.
  - MIXED: partial absorption / per-factor heterogeneity.
  - SAMPLE-SIZE-BOUNDED: per-cell event counts insufficient for
    confident per-window p=7 aggregation.

Methodological notes:
  - "Williamson-FA" here means the Phase 27 Analysis 2 protocol: bin
    spike counts at 200 ms, sqrt(x+0.5) variance-stabilising transform,
    fit FactorAnalysis with CV-selected n_factors (up to 8), per-unit
    loadings are columns of fa.components_.  This is FA on the
    *noise-correlation regime spike-count matrix*, not on single-cell
    properties.  The brief's "FA on single-cell properties" phrasing is
    a misunderstanding; we follow the Phase 27 actual methodology for
    cross-substrate fidelity.
  - Two FA fits per session: one on natural_movie_one (matches the
    p=7 measurement condition) and one on drifting_pooled (matches the
    rep_med / ks_gue_med measurement condition).  Each ARS metric is
    regressed against the FA computed on the same condition the metric
    was measured.
  - Per-cell per-window p=7: cell's own spike train in the
    natural_movie_one chunks, partitioned into 5 windows of equal
    total duration (matching Phase 31b's allen_per_window_padic.py),
    padic_v4 z(p=7) per window vs N_SEEDS=3 rate-matched Poisson
    surrogates, aggregated as mean z and frac z>2 across well-powered
    windows.  Cells with fewer than 3 well-powered windows are flagged
    UNDERCOUNT.
  - Robustness panel: also regress against raw per-cell properties
    (osi, dsi, f1_f0_pref, mean_rate) in addition to FA loadings.
  - 132-event floor lesson from Phase 34b: per-cell event counts are
    reported alongside; sample-size-bounded cells are flagged
    explicitly.

Outputs:
  - data/phase32b_results/per_cell_p7_padic.parquet
    (per-cell per-window p=7 z-scores plus aggregates)
  - data/phase32b_results/per_cell_fa_loadings_nmo.parquet
  - data/phase32b_results/per_cell_fa_loadings_drift.parquet
  - data/phase32b_results/per_cell_decomposition_merged.parquet
  - data/phase32b_results/per_cell_decomposition_verdict.json
  - phase32b/PHASE32B_PER_CELL_FINDINGS.md (written by hand)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import FactorAnalysis
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase24'))

from loader import load_session
from run_per_session_h2 import (
    build_unit_matrix_chunks, chunks_for,
)
from arithmetic_toolkit import padic_amplitude_v4

OUT = Path(ROOT_DIR) / 'data' / 'phase32b_results'
OUT.mkdir(parents=True, exist_ok=True)

# 6 Allen sessions with per-window p-adic available (Phase 31b Round 4)
SESSIONS = [
    (732592105, 'wt'),
    (791319847, 'Vip'),
    (760693773, 'Sst'),
    (762602078, 'Sst'),
    (797828357, 'Pvalb'),
    (755434585, 'Vip'),
]

# p-adic parameters (matching Phase 31b)
Q_MAX = 200
N_SEEDS = 3
N_WINDOWS = 5
PRIMES = (7,)
MIN_EVENTS_PER_WINDOW = 30
MIN_GOOD_WINDOWS = 3

# FA parameters (matching Phase 27)
BIN_MS_FA = 200.0
MAX_FACTORS = 8

# Spike-binning resolution for matrix construction (irrelevant to
# per-cell p=7 since we extract raw spike times below, but reused for
# convenience to extract per-condition chunks)
BIN_MS_MAT = 5.0

# Verdict thresholds (Phase 27 convention)
R2_SUBSUMED_FLOOR = 0.50
R2_ORTHOGONAL_CEIL = 0.20

ARS_PATH = (Path(ROOT_DIR) / 'data' / 'phase24_results'
            / 'per_session_h1_ars.parquet')
H1F_PATH = (Path(ROOT_DIR) / 'data' / 'phase24_results'
            / 'per_session_h1_functional.parquet')


# ---- per-cell per-window p=7 ---------------------------------------------


def per_cell_per_window_p7(spike_times: np.ndarray,
                           t_start: float, t_end: float,
                           n_windows: int = N_WINDOWS,
                           q_max: int = Q_MAX,
                           n_seeds: int = N_SEEDS,
                           min_events: int = MIN_EVENTS_PER_WINDOW
                           ) -> dict:
    """Per-cell per-window p=7 with rate-matched Poisson surrogate.

    Takes the cell's spike times restricted to [t_start, t_end),
    partitions into n_windows equal-duration windows, and for each
    window computes padic_v4 z(p=7) vs n_seeds rate-matched Poisson
    surrogates (uniform on [0, win_dur) with same event count).

    Returns
    -------
    dict with keys
      - per_window_z      list of z(p=7) per window (NaN for undercount)
      - per_window_n      list of n_events per window
      - mean_z            mean of valid z values
      - frac_z_gt2        fraction of valid z values exceeding 2
      - n_windows_used    number of valid windows
      - total_events      total events in [t_start, t_end)
      - status            'OK' | 'UNDERCOUNT'
    """
    sp = spike_times[(spike_times >= t_start) & (spike_times < t_end)] - t_start
    win_dur = (t_end - t_start) / n_windows
    z_list, n_list = [], []
    for w in range(n_windows):
        t0 = w * win_dur
        t1 = (w + 1) * win_dur
        win = sp[(sp >= t0) & (sp < t1)] - t0
        n = int(win.size)
        n_list.append(n)
        if n < min_events:
            z_list.append(np.nan)
            continue
        pad = padic_amplitude_v4(win, q_max=q_max)
        real_p7 = float(pad['per_prime'][7]['normalised_per_q'])
        sur_vals = []
        for seed in range(n_seeds):
            rng = np.random.default_rng(seed + 98765)
            sur = np.sort(rng.uniform(0, win_dur, size=n))
            pad_sur = padic_amplitude_v4(sur, q_max=q_max)
            sur_vals.append(float(pad_sur['per_prime'][7]['normalised_per_q']))
        sur_arr = np.asarray(sur_vals)
        z = (real_p7 - sur_arr.mean()) / max(sur_arr.std(), 1e-6)
        z_list.append(float(z))
    z_arr = np.asarray(z_list)
    valid = ~np.isnan(z_arr)
    n_valid = int(valid.sum())
    return dict(
        per_window_z=z_list,
        per_window_n=n_list,
        mean_z=float(np.nanmean(z_arr)) if n_valid > 0 else float('nan'),
        frac_z_gt2=float(np.nansum(z_arr > 2) / n_valid) if n_valid > 0 else float('nan'),
        n_windows_used=n_valid,
        total_events=int(sp.size),
        status='OK' if n_valid >= MIN_GOOD_WINDOWS else 'UNDERCOUNT',
    )


# ---- Williamson noise-correlation FA -------------------------------------


def cv_fa_dim(X: np.ndarray, max_factors: int = MAX_FACTORS,
              n_splits: int = 5) -> int:
    """Phase 27 Analysis 2 protocol: pick n_factors maximising mean
    held-out log-likelihood via 5-fold CV, searching 1..max_factors.
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=0)
    best_n, best_ll = 1, -np.inf
    for n in range(1, max_factors + 1):
        if n >= X.shape[1]:
            break
        lls = []
        for tr, te in kf.split(X):
            try:
                fa = FactorAnalysis(n_components=n, random_state=0)
                fa.fit(X[tr])
                lls.append(fa.score(X[te]))
            except Exception:
                lls.append(-np.inf)
        m = float(np.mean(lls))
        if m > best_ll:
            best_ll, best_n = m, n
    return best_n


def fit_session_fa(rec, unit_ids: list[int], condition: str,
                   bin_ms: float = BIN_MS_FA
                   ) -> tuple[pd.DataFrame, int]:
    """Build (n_bins, n_units) at bin_ms over the condition's chunks,
    sqrt-stabilise, CV-FA up to MAX_FACTORS, return per-unit loadings."""
    chunks = chunks_for(rec, condition)
    mat, total_dur, _ = build_unit_matrix_chunks(rec, unit_ids, chunks, bin_ms)
    X = mat.T.astype(np.float64)
    X_var = np.sqrt(X + 0.5)
    n_factors = cv_fa_dim(X_var, max_factors=MAX_FACTORS)
    fa = FactorAnalysis(n_components=n_factors, random_state=0)
    fa.fit(X_var)
    loadings = fa.components_   # (n_factors, n_units)
    rows = []
    for i, u in enumerate(unit_ids):
        row = dict(session_id=int(rec.session_id) if hasattr(rec, 'session_id') else None,
                   unit_id=int(u))
        for k in range(n_factors):
            row[f'fa_loading_{k}'] = float(loadings[k, i])
        rows.append(row)
    return pd.DataFrame(rows), int(n_factors)


# ---- regression ---------------------------------------------------------


def r2_with_bootstrap(X: np.ndarray, y: np.ndarray,
                      n_boot: int = 1000, random_state: int = 0
                      ) -> dict:
    mask = ~np.isnan(y) & np.all(~np.isnan(X), axis=1)
    Xc, yc = X[mask], y[mask]
    if Xc.shape[0] < Xc.shape[1] + 2:
        return dict(r2=float('nan'), r2_ci=(float('nan'), float('nan')),
                    n=int(Xc.shape[0]))
    lr = LinearRegression().fit(Xc, yc)
    r2 = float(lr.score(Xc, yc))
    rng = np.random.default_rng(random_state)
    r2_boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, Xc.shape[0], size=Xc.shape[0])
        try:
            r2_b = float(LinearRegression().fit(Xc[idx], yc[idx]).score(Xc[idx], yc[idx]))
            r2_boots.append(r2_b)
        except Exception:
            pass
    if r2_boots:
        lo, hi = float(np.percentile(r2_boots, 2.5)), float(np.percentile(r2_boots, 97.5))
    else:
        lo = hi = float('nan')
    return dict(r2=r2, r2_ci=(lo, hi), n=int(Xc.shape[0]),
                coef=lr.coef_.tolist(), intercept=float(lr.intercept_))


def classify_r2(r2: float) -> str:
    if np.isnan(r2):
        return 'UNDEFINED'
    if r2 < R2_ORTHOGONAL_CEIL:
        return 'ORTHOGONAL'
    if r2 >= R2_SUBSUMED_FLOOR:
        return 'SUBSUMED'
    return 'PARTIAL'


def zscore_within(df: pd.DataFrame, cols: list[str], by: str) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c + '_z'] = out.groupby(by)[c].transform(
            lambda s: (s - s.mean()) / (s.std() if s.std() > 0 else 1.0))
    return out


# ---- orchestrator -------------------------------------------------------


def main():
    print("=" * 72)
    print("Phase 32b — per-cell decomposition")
    print("=" * 72)

    t0_outer = time.time()

    ars = pd.read_parquet(ARS_PATH)
    ars = ars[ars['condition'] == 'drifting_pooled'][
        ['session_id', 'unit_id', 'rep_med', 'ks_gue_med', 'n_events_used']]
    h1f = pd.read_parquet(H1F_PATH)[
        ['session_id', 'unit_id', 'mean_rate', 'osi', 'dsi',
         'pref_ori_deg', 'pref_dir_deg', 'f1_f0_pref']]

    all_p7 = []
    all_fa_nmo = []
    all_fa_drift = []
    per_session_meta = []

    for session_id, cre_line in SESSIONS:
        print(f"\n=== session {session_id} ({cre_line}) ===")
        t_sess = time.time()
        rec = load_session(session_id)
        rec.session_id = session_id   # attribute for FA bookkeeping

        # Restrict to H1∩ARS-pass units
        ars_ids = set(ars[ars['session_id'] == session_id]['unit_id'])
        h1_ids = set(h1f[h1f['session_id'] == session_id]['unit_id'])
        avail_ids = list(rec.units.index)
        unit_ids = sorted([int(u) for u in avail_ids if u in ars_ids and u in h1_ids])
        print(f"  H1∩ARS units: {len(unit_ids)}")

        # Per-cell per-window p=7 on natural_movie_one
        nmo_chunks = chunks_for(rec, 'natural_movie_one')
        # Match Phase 31b: concatenate chunks via build_unit_matrix_chunks,
        # then events on the concatenated time axis; partition into 5
        # windows of total_dur/5.  For per-cell, replicate that
        # construction by collecting each unit's per-chunk spike times
        # into a single concatenated array.
        bin_s = BIN_MS_MAT / 1000.0
        chunk_durs = [stop - start for start, stop in nmo_chunks]
        chunk_bins = [int(np.ceil(d / bin_s)) for d in chunk_durs]
        total_dur = float(sum(chunk_bins) * bin_s)
        # cumulative_offsets[c] = start of chunk c in concatenated time
        cumulative_offsets = np.concatenate(([0.0],
            np.cumsum([nb * bin_s for nb in chunk_bins])))
        for ui_idx, u in enumerate(unit_ids):
            sp_all = np.asarray(rec.spike_times.get(int(u), np.zeros(0)))
            concat_sp = []
            for c_idx, ((cstart, _cstop), nb) in enumerate(
                    zip(nmo_chunks, chunk_bins)):
                cdur = nb * bin_s
                m = (sp_all >= cstart) & (sp_all < cstart + cdur)
                concat_sp.append(sp_all[m] - cstart
                                  + cumulative_offsets[c_idx])
            sp_cat = (np.sort(np.concatenate(concat_sp))
                      if concat_sp else np.zeros(0))
            res = per_cell_per_window_p7(sp_cat, 0.0, total_dur)
            row = dict(session_id=session_id, cre_line=cre_line,
                       unit_id=int(u),
                       p7_mean_z=res['mean_z'],
                       p7_frac_gt2=res['frac_z_gt2'],
                       p7_n_windows_used=res['n_windows_used'],
                       p7_total_events=res['total_events'],
                       p7_status=res['status'])
            for w_idx, (z, n) in enumerate(zip(res['per_window_z'],
                                               res['per_window_n'])):
                row[f'z_w{w_idx}'] = z
                row[f'n_w{w_idx}'] = n
            all_p7.append(row)
            if (ui_idx + 1) % 25 == 0:
                print(f"    p=7 progress: {ui_idx + 1}/{len(unit_ids)}")

        # FA on natural_movie_one
        print(f"  fitting FA on natural_movie_one ...")
        fa_nmo_df, n_fa_nmo = fit_session_fa(rec, unit_ids, 'natural_movie_one')
        fa_nmo_df['cre_line'] = cre_line
        all_fa_nmo.append(fa_nmo_df)

        # FA on drifting_pooled
        print(f"  fitting FA on drifting_pooled ...")
        fa_drift_df, n_fa_drift = fit_session_fa(rec, unit_ids, 'drifting_pooled')
        fa_drift_df['cre_line'] = cre_line
        all_fa_drift.append(fa_drift_df)

        per_session_meta.append(dict(
            session_id=session_id, cre_line=cre_line,
            n_units=len(unit_ids),
            n_fa_nmo=int(n_fa_nmo), n_fa_drift=int(n_fa_drift),
            nmo_total_dur=total_dur,
            elapsed_sec=float(time.time() - t_sess),
        ))
        print(f"  n_fa_nmo={n_fa_nmo}  n_fa_drift={n_fa_drift}  "
              f"elapsed={time.time() - t_sess:.1f}s")

    # Persist per-cell tables
    df_p7 = pd.DataFrame(all_p7)
    df_p7.to_parquet(OUT / 'per_cell_p7_padic.parquet', index=False)
    df_fa_nmo = pd.concat(all_fa_nmo, ignore_index=True)
    df_fa_nmo.to_parquet(OUT / 'per_cell_fa_loadings_nmo.parquet', index=False)
    df_fa_drift = pd.concat(all_fa_drift, ignore_index=True)
    df_fa_drift.to_parquet(OUT / 'per_cell_fa_loadings_drift.parquet', index=False)

    # Merge per-cell p=7, FA loadings (both conditions), and ARS metrics
    merged = df_p7.merge(
        df_fa_nmo.add_prefix('fa_nmo_').rename(
            columns={'fa_nmo_session_id': 'session_id',
                     'fa_nmo_unit_id': 'unit_id',
                     'fa_nmo_cre_line': 'cre_line'}),
        on=['session_id', 'unit_id', 'cre_line'], how='left')
    merged = merged.merge(
        df_fa_drift.add_prefix('fa_drift_').rename(
            columns={'fa_drift_session_id': 'session_id',
                     'fa_drift_unit_id': 'unit_id',
                     'fa_drift_cre_line': 'cre_line'}),
        on=['session_id', 'unit_id', 'cre_line'], how='left')
    merged = merged.merge(ars, on=['session_id', 'unit_id'], how='left')
    merged = merged.merge(h1f, on=['session_id', 'unit_id'], how='left')

    merged.to_parquet(OUT / 'per_cell_decomposition_merged.parquet', index=False)
    print(f"\n  → per_cell_decomposition_merged.parquet ({len(merged)} rows)")

    # Within-session z-score predictors and targets for pooled regressions
    fa_nmo_cols = [c for c in merged.columns if c.startswith('fa_nmo_fa_loading_')]
    fa_drift_cols = [c for c in merged.columns if c.startswith('fa_drift_fa_loading_')]
    raw_cols = ['mean_rate', 'osi', 'dsi', 'f1_f0_pref']

    merged_z = zscore_within(merged,
                              fa_nmo_cols + fa_drift_cols + raw_cols
                              + ['p7_mean_z', 'p7_frac_gt2', 'rep_med',
                                 'ks_gue_med'],
                              by='session_id')

    # Filter to OK status for p=7 analyses
    ok = merged_z[merged_z['p7_status'] == 'OK'].copy()
    print(f"\n  cells OK on p=7: {len(ok)} / {len(merged_z)} "
          f"({len(merged_z) - len(ok)} flagged UNDERCOUNT)")

    # Regressions: per-metric × per-FA-condition × pooled
    regression_results = {}
    fa_kinds = [('fa_nmo', [c + '_z' for c in fa_nmo_cols]),
                 ('fa_drift', [c + '_z' for c in fa_drift_cols])]

    print()
    print("=" * 72)
    print("REGRESSIONS  (target_z ~ FA loadings, within-session z-scored)")
    print("=" * 72)

    targets = [
        ('p7_mean_z', ok, 'per-window p=7 mean z'),
        ('p7_frac_gt2', ok, 'per-window p=7 frac z>2'),
        ('rep_med', merged_z, 'rep_med'),
        ('ks_gue_med', merged_z, 'ks_gue_med'),
    ]

    for target_name, df_t, label in targets:
        regression_results[target_name] = {}
        print(f"\n  TARGET: {label} ({target_name})")
        for fa_label, fa_z_cols in fa_kinds:
            X = df_t[fa_z_cols].to_numpy()
            y = df_t[target_name + '_z'].to_numpy()
            res = r2_with_bootstrap(X, y, n_boot=1000)
            res['fa_condition'] = fa_label
            res['classification'] = classify_r2(res['r2'])
            regression_results[target_name][fa_label] = res
            lo, hi = res['r2_ci']
            print(f"    FA on {fa_label:9s}: R² = {res['r2']:+.3f}  "
                  f"95%CI [{lo:+.3f}, {hi:+.3f}]  "
                  f"n = {res['n']:4d}  → {res['classification']}")
        # Raw per-cell properties robustness panel
        Xr = df_t[[c + '_z' for c in raw_cols]].to_numpy()
        y = df_t[target_name + '_z'].to_numpy()
        res_raw = r2_with_bootstrap(Xr, y, n_boot=1000)
        res_raw['classification'] = classify_r2(res_raw['r2'])
        regression_results[target_name]['raw_per_cell'] = res_raw
        lo, hi = res_raw['r2_ci']
        print(f"    raw per-cell : R² = {res_raw['r2']:+.3f}  "
              f"95%CI [{lo:+.3f}, {hi:+.3f}]  n = {res_raw['n']:4d}  "
              f"→ {res_raw['classification']}")

    # Verdict construction
    p7_cls_nmo = regression_results['p7_mean_z']['fa_nmo']['classification']
    rep_cls = regression_results['rep_med']['fa_drift']['classification']
    ks_cls = regression_results['ks_gue_med']['fa_drift']['classification']

    if p7_cls_nmo == 'ORTHOGONAL' and rep_cls == 'ORTHOGONAL':
        verdict = 'BOTH_ORTHOGONAL'
    elif p7_cls_nmo == 'SUBSUMED' and rep_cls == 'ORTHOGONAL':
        verdict = 'p7_ABSORBED_F1F0_ORTHOGONAL'
    elif p7_cls_nmo == 'SUBSUMED' and rep_cls == 'SUBSUMED':
        verdict = 'BOTH_ABSORBED'
    elif p7_cls_nmo == 'UNDEFINED':
        verdict = 'SAMPLE_SIZE_BOUNDED'
    else:
        verdict = 'MIXED'

    print()
    print("=" * 72)
    print(f"VERDICT: {verdict}")
    print(f"  per-window p=7 (FA on natural_movie_one): {p7_cls_nmo}")
    print(f"  rep_med (FA on drifting_pooled):          {rep_cls}")
    print(f"  ks_gue_med (FA on drifting_pooled):       {ks_cls}")
    print("=" * 72)

    out_json = dict(
        method=dict(
            sessions=len(SESSIONS),
            condition_for_p7='natural_movie_one',
            condition_for_fa_p7='natural_movie_one',
            condition_for_fa_ars='drifting_pooled',
            q_max=Q_MAX, n_seeds=N_SEEDS, n_windows=N_WINDOWS,
            min_events_per_window=MIN_EVENTS_PER_WINDOW,
            min_good_windows=MIN_GOOD_WINDOWS,
            bin_ms_fa=BIN_MS_FA, max_factors=MAX_FACTORS,
            r2_subsumed_floor=R2_SUBSUMED_FLOOR,
            r2_orthogonal_ceil=R2_ORTHOGONAL_CEIL,
        ),
        per_session=per_session_meta,
        regressions=regression_results,
        verdict=verdict,
        per_cell_p7_summary=dict(
            n_total=int(len(merged_z)),
            n_OK=int(len(ok)),
            n_UNDERCOUNT=int(len(merged_z) - len(ok)),
        ),
        elapsed_sec=float(time.time() - t0_outer),
    )
    with open(OUT / 'per_cell_decomposition_verdict.json', 'w') as f:
        json.dump(out_json, f, indent=2, default=str)

    print(f"\n  → per_cell_decomposition_verdict.json")
    print(f"  total elapsed: {time.time() - t0_outer:.1f}s")
    return out_json


if __name__ == '__main__':
    main()
