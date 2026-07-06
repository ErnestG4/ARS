"""
phase27/analysis2_ars_vs_fa.py — ARS metrics vs Williamson 2016
factor-analysis loadings on pvc-11 in-vivo data.

Question: are ARS per-unit continuous metrics (rep_med, ks_gue_med)
empirically orthogonal to FA factor loadings on the same data, or do
they capture variance the FA loadings already do?

Implementation:
  Step 1: Recompute factor analysis on the H2-analysis sessions
          (monkey1_natural_movie, monkey2_gratings_movie).  Williamson
          2016's convention: bin spike counts at moderate bin width
          (~200 ms in the noise-correlation regime where shared
          variability dominates), apply factor analysis to the bin ×
          unit matrix, with FA dimensionality determined by
          cross-validated log-likelihood.  Each unit's FA loadings is
          its row in the (n_factors × n_units) loading matrix.
  Step 2: For each pair (ARS metric, FA loading) compute Spearman
          correlation across units.  Build full correlation matrix.
  Step 3: For each ARS metric, regress on full set of FA loadings,
          report R².
  Step 4: Bootstrap CIs on the correlations and R².

Verdict: ORTHOGONAL / PARTIALLY-OVERLAPPING / SUBSUMED.

Note on Williamson session overlap: Williamson 2016's published FA
analysis used pvc-11 noise-correlation regime data.  The H2 sessions
(monkey1/monkey2 movie recordings) are from the same pvc-11 release.
This recomputation applies Williamson methodology to the H2 sessions
specifically.  Document the recomputation procedure explicitly.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import FactorAnalysis
from sklearn.model_selection import KFold


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))

from loader import load, MOVIE_TRIAL_SEC
from population_events import build_unit_matrix

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase27_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Williamson 2016 noise-correlation regime uses ~200 ms bins as the
# typical shared-variability timescale in V1 noise-correlation FA.
WILLIAMSON_BIN_MS = 200.0
H2_SESSIONS = ['monkey1_natural_movie', 'monkey2_gratings_movie']
N_BOOTSTRAP = 200

ARS_METRICS = ['rep_med', 'ks_gue_med']
PVC11_FUNCTIONAL = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
                      / 'h1_functional.parquet')
PVC11_ARS = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
               / 'h1_classifications.parquet')
H2_POP = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
            / 'h2_population_classifications.parquet')
UNIT_SEL = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
              / 'unit_selection.parquet')


def cv_factor_analysis_dim(X: np.ndarray, max_factors: int = 10,
                              n_splits: int = 5,
                              random_state: int = 0) -> int:
    """Williamson 2016-style cross-validated FA dimensionality.

    Returns the n_factors that maximises the held-out log-likelihood
    averaged across n_splits folds.  Searches 1..max_factors.
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    best_n, best_ll = 1, -np.inf
    for n in range(1, max_factors + 1):
        lls = []
        for tr, te in kf.split(X):
            try:
                fa = FactorAnalysis(n_components=n, random_state=random_state)
                fa.fit(X[tr])
                ll = fa.score(X[te])
            except Exception:
                ll = -np.inf
            lls.append(ll)
        ll_mean = float(np.mean(lls))
        if ll_mean > best_ll:
            best_ll, best_n = ll_mean, n
    return best_n


def fit_session_fa(session: str, bin_ms: float = WILLIAMSON_BIN_MS,
                     ) -> dict:
    """Load a session, build the binned spike-count matrix on H2
    units, cross-validate FA dimensionality, fit FA, return loadings
    matrix and metadata.
    """
    rec = load(session)
    sel = pd.read_parquet(UNIT_SEL)
    sel_h2 = sel[(sel['recording'] == session) & sel['h2_pass']]
    units = sel_h2['unit_idx'].astype(int).tolist()

    mat, total_dur = build_unit_matrix(rec, units, bin_ms=bin_ms)
    # mat is (n_units, n_bins); FA wants (n_samples, n_features) =
    # (n_bins, n_units).
    X = mat.T.astype(np.float64)
    # FA assumes Gaussian; spike counts are integer.  Williamson 2016
    # uses square-root variance-stabilising transform before FA — apply
    # the same convention.
    X_var = np.sqrt(X + 0.5)

    n_factors = cv_factor_analysis_dim(X_var, max_factors=8)
    fa = FactorAnalysis(n_components=n_factors, random_state=0)
    fa.fit(X_var)
    loadings = fa.components_       # shape (n_factors, n_units)

    # Per-unit DataFrame
    rows = []
    for i, u_idx in enumerate(units):
        row = dict(recording=session, unit_idx=int(u_idx),
                     unit_id=rec.unit_id(u_idx))
        for k in range(n_factors):
            row[f'fa_loading_{k}'] = float(loadings[k, i])
        rows.append(row)
    return dict(
        session=session,
        n_factors=int(n_factors),
        n_units=int(len(units)),
        n_bins=int(X_var.shape[0]),
        bin_ms=float(bin_ms),
        loadings_df=pd.DataFrame(rows),
        explained_variance_per_factor=fa.noise_variance_.tolist()
            if hasattr(fa, 'noise_variance_') else None,
    )


def merge_with_ars(fa_loadings_df: pd.DataFrame) -> pd.DataFrame:
    """Merge the FA loadings DataFrame with the per-unit ARS metrics
    (rep_med, ks_gue_med) from h1_classifications.  Aggregate the
    ARS metrics per unit across conditions if present (median over
    conditions).
    """
    ars = pd.read_parquet(PVC11_ARS)
    # Median-aggregate ARS metrics per (recording, unit_idx)
    ars_unit = (ars.groupby(['recording', 'unit_idx'])
                   .agg(rep_med=('rep_med', 'median'),
                          ks_gue_med=('ks_gue_med', 'median'))
                   .reset_index())
    return fa_loadings_df.merge(ars_unit, on=['recording', 'unit_idx'],
                                  how='left')


def correlation_matrix(merged: pd.DataFrame, fa_cols: list[str]
                         ) -> tuple[pd.DataFrame, dict]:
    """Spearman ρ(ARS metric, FA loading) for every pair, with
    bootstrap percentile CIs.

    Returns (long-form DataFrame with one row per pair, summary dict
    with mean_abs_rho, max_abs_rho, etc.).
    """
    rows = []
    for metric in ARS_METRICS:
        for col in fa_cols:
            sub = merged[[metric, col]].dropna()
            if len(sub) < 8: continue
            rho, p = stats.spearmanr(sub[metric], sub[col])
            # Bootstrap CI on rho
            boots = []
            rng = np.random.default_rng(0)
            for _ in range(N_BOOTSTRAP):
                idx = rng.integers(0, len(sub), len(sub))
                b = sub.iloc[idx]
                r, _ = stats.spearmanr(b[metric], b[col])
                if np.isfinite(r): boots.append(r)
            boots = np.asarray(boots) if boots else np.asarray([np.nan])
            rows.append(dict(
                ars_metric=metric, fa_loading=col,
                n_units=int(len(sub)),
                spearman_rho=float(rho), p_value=float(p),
                rho_ci_lo=float(np.nanpercentile(boots, 2.5)),
                rho_ci_hi=float(np.nanpercentile(boots, 97.5)),
            ))
    df = pd.DataFrame(rows)
    summary = dict(
        n_pairs=len(df),
        mean_abs_rho=float(df['spearman_rho'].abs().mean()) if len(df) else float('nan'),
        max_abs_rho=float(df['spearman_rho'].abs().max()) if len(df) else float('nan'),
        n_pairs_significant_p05=int((df['p_value'] < 0.05).sum()) if len(df) else 0,
    )
    return df, summary


def r2_decomposition(merged: pd.DataFrame, fa_cols: list[str]) -> dict:
    """For each ARS metric, fit OLS of metric on the full set of FA
    loadings; report R² (in-sample, since FA is also fit on the same
    units — this is the empirical-variance-shared measure)."""
    out = {}
    for metric in ARS_METRICS:
        sub = merged[[metric] + fa_cols].dropna()
        if len(sub) < len(fa_cols) + 2:
            out[metric] = float('nan')
            continue
        X = sub[fa_cols].to_numpy()
        X = np.column_stack([np.ones(len(X)), X])
        y = sub[metric].to_numpy()
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        yhat = X @ beta
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - ss_res / max(ss_tot, 1e-12)
        # Bootstrap CI
        boots = []
        rng = np.random.default_rng(0)
        n = len(sub)
        for _ in range(N_BOOTSTRAP):
            idx = rng.integers(0, n, n)
            bX = X[idx]; by = y[idx]
            try:
                bb, *_ = np.linalg.lstsq(bX, by, rcond=None)
                byhat = bX @ bb
                br = 1.0 - np.sum((by - byhat) ** 2) / max(
                    np.sum((by - by.mean()) ** 2), 1e-12)
                boots.append(br)
            except Exception:
                pass
        boots = np.asarray(boots) if boots else np.asarray([np.nan])
        out[metric] = dict(
            r2=float(r2),
            r2_ci_lo=float(np.nanpercentile(boots, 2.5)),
            r2_ci_hi=float(np.nanpercentile(boots, 97.5)),
            n_units=int(len(sub)),
            n_factors=len(fa_cols),
        )
    return out


def aggregate_verdict(corr_summary: dict, r2_results: dict) -> str:
    """Compose the H_orthogonal verdict per the brief's vocabulary."""
    max_rho = corr_summary.get('max_abs_rho', float('nan'))
    mean_rho = corr_summary.get('mean_abs_rho', float('nan'))
    r2_max = max((v['r2'] for v in r2_results.values()
                    if isinstance(v, dict)), default=float('nan'))
    r2_max_metric = max(((k, v['r2'])
                            for k, v in r2_results.items()
                            if isinstance(v, dict)),
                           key=lambda x: x[1], default=(None, float('nan')))

    if (np.isfinite(mean_rho) and mean_rho < 0.3
            and np.isfinite(max_rho) and max_rho < 0.5
            and np.isfinite(r2_max) and r2_max < 0.3):
        return 'ORTHOGONAL'
    if ((np.isfinite(mean_rho) and mean_rho > 0.6)
            or (np.isfinite(r2_max) and r2_max > 0.6)):
        return 'SUBSUMED'
    return 'PARTIALLY-OVERLAPPING'


def main():
    print("=" * 72)
    print("Phase 27 Analysis 2 — ARS vs Williamson FA loadings on pvc-11")
    print("=" * 72)

    session_results = {}
    all_loadings = []
    for sess in H2_SESSIONS:
        print(f"\n  fitting FA on {sess}...")
        res = fit_session_fa(sess, bin_ms=WILLIAMSON_BIN_MS)
        print(f"    n_units={res['n_units']}  n_bins={res['n_bins']}  "
                f"n_factors (CV)={res['n_factors']}  bin_ms={res['bin_ms']}")
        session_results[sess] = res
        all_loadings.append(res['loadings_df'])

    fa_df = pd.concat(all_loadings, ignore_index=True)
    fa_df.to_parquet(OUT_DIR / 'analysis2_fa_loadings.parquet', index=False)
    print(f"\n  FA loadings: {len(fa_df)} units, "
            f"columns={[c for c in fa_df.columns if c.startswith('fa_')]}")

    merged = merge_with_ars(fa_df)
    merged.to_parquet(OUT_DIR / 'analysis2_merged.parquet', index=False)

    fa_cols_all = sorted([c for c in merged.columns
                            if c.startswith('fa_loading_')])
    print(f"  ARS-FA merged: {len(merged)} units")

    # Per-session correlation matrix (avoid pooling across sessions
    # with different n_factors — compute per session, then aggregate)
    per_session_corr = []
    per_session_r2 = {}
    summary_per_session = {}
    for sess, res in session_results.items():
        sub = merged[merged['recording'] == sess]
        n_fa = res['n_factors']
        fa_cols = [f'fa_loading_{k}' for k in range(n_fa)]
        corr_df, corr_sum = correlation_matrix(sub, fa_cols)
        corr_df['session'] = sess
        per_session_corr.append(corr_df)
        r2_res = r2_decomposition(sub, fa_cols)
        per_session_r2[sess] = r2_res
        summary_per_session[sess] = corr_sum

    corr_df_all = pd.concat(per_session_corr, ignore_index=True)
    corr_df_all.to_parquet(OUT_DIR / 'analysis2_correlation_matrix.parquet',
                            index=False)

    # Aggregate across sessions: weight by n_units
    print()
    print("Per-session results:")
    for sess in H2_SESSIONS:
        s = summary_per_session[sess]
        r2 = per_session_r2[sess]
        print(f"  {sess}:")
        print(f"    n_pairs={s['n_pairs']}  "
                f"mean|ρ|={s['mean_abs_rho']:.3f}  max|ρ|={s['max_abs_rho']:.3f}  "
                f"n_sig(p<0.05)={s['n_pairs_significant_p05']}")
        for metric, v in r2.items():
            if isinstance(v, dict):
                print(f"    R²[{metric}]: {v['r2']:.3f}  "
                        f"[{v['r2_ci_lo']:.3f}, {v['r2_ci_hi']:.3f}]")

    # Pooled across-session summary (median of per-session metrics)
    all_mean_rho = [s['mean_abs_rho'] for s in summary_per_session.values()]
    all_max_rho = [s['max_abs_rho'] for s in summary_per_session.values()]
    all_r2 = []
    for r2_res in per_session_r2.values():
        for v in r2_res.values():
            if isinstance(v, dict):
                all_r2.append(v['r2'])
    pooled_summary = dict(
        median_mean_abs_rho_across_sessions=float(np.median(all_mean_rho)),
        max_max_abs_rho_across_sessions=float(np.max(all_max_rho)),
        max_r2_across_metrics_and_sessions=float(np.max(all_r2)) if all_r2 else float('nan'),
        per_session=summary_per_session,
    )

    verdict = aggregate_verdict(
        dict(mean_abs_rho=pooled_summary['median_mean_abs_rho_across_sessions'],
              max_abs_rho=pooled_summary['max_max_abs_rho_across_sessions']),
        {f'pooled_max': dict(r2=pooled_summary['max_r2_across_metrics_and_sessions'])},
    )

    result = dict(
        verdict=verdict,
        pooled_summary=pooled_summary,
        per_session_r2=per_session_r2,
        sessions=H2_SESSIONS,
        bin_ms=WILLIAMSON_BIN_MS,
        n_factors_per_session={s: r['n_factors']
                                 for s, r in session_results.items()},
    )
    with open(OUT_DIR / 'analysis2_verdict.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print()
    print(f"Aggregate verdict: {verdict}")
    print(f"  pooled median mean|ρ| = "
            f"{pooled_summary['median_mean_abs_rho_across_sessions']:.3f}")
    print(f"  pooled max |ρ|        = "
            f"{pooled_summary['max_max_abs_rho_across_sessions']:.3f}")
    print(f"  pooled max R²         = "
            f"{pooled_summary['max_r2_across_metrics_and_sessions']:.3f}")


if __name__ == '__main__':
    main()
