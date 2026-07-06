"""
phase27/analysis1_f1f0_rate_matched.py — F1/F0 rate-matched check.

Question: does the F1/F0 ↔ rep_med substrate-systematic sign flip
(Phase 24 Full: Allen meta-fix −0.183 vs pvc-11 +0.388) survive
per-cell rate-matching, or is it a Hietanen 2013 spike-count-bias
artifact of cross-substrate firing-rate-regime differences?

Methods:
  0. Per-substrate firing-rate distribution baseline + overlap analysis.
  A. Within-substrate spike-count tertile partial correlations of
     rep_med ↔ F1/F0 controlling for mean firing rate.
  B. Rate-matched cross-substrate subsamples (Allen → pvc-11 nearest-
     rate match within ±20% by default), correlation in matched subset.
  C. Fisher-Z meta-analysis with spike-count covariate added to the
     partial correlation (alongside the existing rate covariate).

Inputs:
  pvc-11:  data/phase22a_results/h1_functional.parquet +
            h1_classifications.parquet (recording-level F1/F0, rate,
            n_events_in for spike count; ARS metrics).
  Allen:   data/phase24_results/per_session_h1_functional.parquet +
            per_session_h1_ars.parquet (12-session multi-session).

Verdict: SUBSTRATE-SYSTEMATIC / PARTIALLY-CONFOUNDED / DEFLATIONARY /
UNDERPOWERED.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase27_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Phase 22a (pvc-11 anaesthetised macaque) and Phase 24 Full (Allen
# awake mouse) per-unit tables.
PVC11_FUNCTIONAL = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
                      / 'h1_functional.parquet')
PVC11_ARS = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
               / 'h1_classifications.parquet')
ALLEN_FUNCTIONAL = (Path(ROOT_DIR) / 'data' / 'phase24_results'
                      / 'per_session_h1_functional.parquet')
ALLEN_ARS = (Path(ROOT_DIR) / 'data' / 'phase24_results'
               / 'per_session_h1_ars.parquet')


def load_substrate_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load per-unit tables for pvc-11 and Allen, merging functional
    and ARS classifications on unit_id (Allen) or (recording, unit_idx)
    (pvc-11).  Each output has columns:
        substrate, unit_id_key, recording, mean_rate, f1_f0_pref,
        n_events_in, rep_med, ks_gue_med, primary
    """
    pvc_f = pd.read_parquet(PVC11_FUNCTIONAL)
    pvc_a = pd.read_parquet(PVC11_ARS)
    # pvc-11 H1 classifications: per (recording, unit_idx, condition)
    # — use the 'all' or whole-recording condition for the cross-
    # substrate comparison.  Phase 22a stored per-condition ARS for the
    # gratings recordings.  Use the modal recording-level estimate by
    # averaging per-unit ARS across conditions when condition='gratings'.
    pvc_a_unit = (pvc_a.groupby(['recording', 'unit_idx'])
                     .agg(rep_med=('rep_med', 'median'),
                            ks_gue_med=('ks_gue_med', 'median'),
                            primary=('primary', lambda s: s.iloc[0]),
                            n_events_in=('n_events_in', 'sum'))
                     .reset_index())
    pvc = pvc_f.merge(pvc_a_unit, on=['recording', 'unit_idx'])
    pvc['substrate'] = 'pvc11'
    pvc['unit_id_key'] = pvc['unit_id']
    pvc = pvc[['substrate', 'unit_id_key', 'recording', 'mean_rate',
                'f1_f0_pref', 'n_events_in', 'rep_med', 'ks_gue_med',
                'primary']]

    allen_f = pd.read_parquet(ALLEN_FUNCTIONAL)
    allen_a = pd.read_parquet(ALLEN_ARS)
    allen_a_unit = (allen_a.groupby(['session_id', 'unit_id'])
                       .agg(rep_med=('rep_med', 'median'),
                              ks_gue_med=('ks_gue_med', 'median'),
                              primary=('primary', lambda s: s.iloc[0]),
                              n_events_in=('n_events_in', 'sum'))
                       .reset_index())
    allen = allen_f.merge(allen_a_unit, on=['session_id', 'unit_id'])
    allen['substrate'] = 'allen'
    allen['unit_id_key'] = allen['unit_id'].astype(str)
    allen = allen.rename(columns={'session_id': 'recording'})
    allen['recording'] = allen['recording'].astype(str)
    allen = allen[['substrate', 'unit_id_key', 'recording', 'mean_rate',
                    'f1_f0_pref', 'n_events_in', 'rep_med', 'ks_gue_med',
                    'primary']]
    return pvc, allen


def method0_rate_distribution(pvc: pd.DataFrame, allen: pd.DataFrame
                                 ) -> dict:
    """Method 0 — firing-rate distribution comparison.  Returns a dict
    with per-substrate quantile summary + overlap region characterised
    by the union of central 95% quantile ranges of each substrate."""
    pvc_r = pvc['mean_rate'].dropna()
    allen_r = allen['mean_rate'].dropna()
    summary = dict(
        pvc11_n=int(len(pvc_r)),
        pvc11_median=float(np.median(pvc_r)),
        pvc11_q05=float(np.quantile(pvc_r, 0.05)),
        pvc11_q25=float(np.quantile(pvc_r, 0.25)),
        pvc11_q75=float(np.quantile(pvc_r, 0.75)),
        pvc11_q95=float(np.quantile(pvc_r, 0.95)),
        allen_n=int(len(allen_r)),
        allen_median=float(np.median(allen_r)),
        allen_q05=float(np.quantile(allen_r, 0.05)),
        allen_q25=float(np.quantile(allen_r, 0.25)),
        allen_q75=float(np.quantile(allen_r, 0.75)),
        allen_q95=float(np.quantile(allen_r, 0.95)),
    )
    # Overlap region = intersection of [q05, q95] for each substrate
    overlap_lo = max(summary['pvc11_q05'], summary['allen_q05'])
    overlap_hi = min(summary['pvc11_q95'], summary['allen_q95'])
    summary['overlap_lo'] = float(overlap_lo)
    summary['overlap_hi'] = float(overlap_hi)
    summary['n_pvc11_in_overlap'] = int(((pvc_r >= overlap_lo)
                                            & (pvc_r <= overlap_hi)).sum())
    summary['n_allen_in_overlap'] = int(((allen_r >= overlap_lo)
                                            & (allen_r <= overlap_hi)).sum())
    summary['overlap_fraction_pvc11'] = (summary['n_pvc11_in_overlap']
                                            / max(len(pvc_r), 1))
    summary['overlap_fraction_allen'] = (summary['n_allen_in_overlap']
                                            / max(len(allen_r), 1))
    # KS test for distribution-equality null
    ks_stat, ks_p = stats.ks_2samp(np.log10(pvc_r.clip(lower=1e-3)),
                                      np.log10(allen_r.clip(lower=1e-3)))
    summary['log10_rate_ks_stat'] = float(ks_stat)
    summary['log10_rate_ks_p'] = float(ks_p)
    return summary


def _spearman_partial_controlling_for(df: pd.DataFrame, x: str, y: str,
                                          controls: list[str]) -> tuple[float, float, int]:
    """Spearman partial correlation: rank-transform x, y, controls, then
    fit OLS of x and y on controls and Spearman the residuals.  Returns
    (rho, p, n)."""
    sub = df[[x, y] + controls].dropna()
    n = len(sub)
    if n < 8:
        return (float('nan'), float('nan'), n)
    ranks = sub.rank()
    X = ranks[controls].to_numpy()
    X = np.column_stack([np.ones(n), X])
    rx = ranks[x].to_numpy()
    ry = ranks[y].to_numpy()
    bx, *_ = np.linalg.lstsq(X, rx, rcond=None)
    by, *_ = np.linalg.lstsq(X, ry, rcond=None)
    resx = rx - X @ bx
    resy = ry - X @ by
    rho, p = stats.spearmanr(resx, resy)
    return float(rho), float(p), int(n)


def method_a_within_substrate_tertiles(pvc: pd.DataFrame,
                                          allen: pd.DataFrame,
                                          n_bins: int = 3) -> pd.DataFrame:
    """Method A — within-substrate spike-count partial correlations
    binned into n_bins tertiles (or quartiles if n_bins=4).

    Returns a long-form DataFrame: substrate × recording × bin_idx with
    columns n, count_lo, count_hi, partial_rho, partial_p.
    """
    rows = []
    for substrate_name, df in [('pvc11', pvc), ('allen', allen)]:
        # Bin within each recording (Phase 22a / Phase 24 convention:
        # per-recording analysis to control for between-recording state).
        for rec, sub in df.groupby('recording'):
            if len(sub) < 8: continue
            # Spike-count tertiles within this recording
            sub = sub.dropna(subset=['n_events_in', 'f1_f0_pref',
                                       'rep_med', 'mean_rate']).copy()
            if len(sub) < 8: continue
            try:
                sub['bin'] = pd.qcut(sub['n_events_in'], n_bins,
                                       labels=False, duplicates='drop')
            except ValueError:
                continue
            for b in sorted(sub['bin'].dropna().unique()):
                bsub = sub[sub['bin'] == b]
                if len(bsub) < 6: continue
                rho, p, n = _spearman_partial_controlling_for(
                    bsub, 'f1_f0_pref', 'rep_med', ['mean_rate'])
                rows.append(dict(
                    substrate=substrate_name, recording=rec,
                    bin_idx=int(b), n_units=int(n),
                    count_lo=float(bsub['n_events_in'].min()),
                    count_hi=float(bsub['n_events_in'].max()),
                    partial_rho=rho, partial_p=p,
                ))
    return pd.DataFrame(rows)


def method_b_rate_matched_subsamples(pvc: pd.DataFrame,
                                        allen: pd.DataFrame,
                                        tol: float = 0.20) -> dict:
    """Method B — rate-matched cross-substrate subsamples.

    For each Allen unit, find the closest pvc-11 unit by mean firing
    rate within ±tol relative.  Restrict each substrate to the matched
    subset, compute partial Spearman of f1_f0_pref ↔ rep_med
    controlling for mean rate.

    Returns dict with matched subsample sizes + partial correlations
    per substrate in the matched subset.  Each side restricted to its
    matched units only.

    NOTE: "matched" here is a 1-to-1 nearest-neighbour pairing without
    replacement (Allen unit → unused pvc-11 unit).
    """
    pvc_r = pvc.dropna(subset=['mean_rate', 'f1_f0_pref', 'rep_med']).copy()
    allen_r = allen.dropna(subset=['mean_rate', 'f1_f0_pref', 'rep_med']).copy()
    pvc_r = pvc_r.reset_index(drop=True)
    allen_r = allen_r.reset_index(drop=True)
    used = np.zeros(len(pvc_r), dtype=bool)
    matches = []
    for i, ar in allen_r.iterrows():
        rate_a = ar['mean_rate']
        diffs = np.abs(pvc_r['mean_rate'].to_numpy() - rate_a) / max(rate_a, 1e-6)
        diffs[used] = np.inf
        j = int(np.argmin(diffs))
        if not np.isfinite(diffs[j]) or diffs[j] > tol:
            continue
        used[j] = True
        matches.append((i, j, rate_a, float(pvc_r.iloc[j]['mean_rate'])))

    if not matches:
        return dict(error='no_matches_found',
                      tol=tol, n_pvc11=int(len(pvc_r)),
                      n_allen=int(len(allen_r)))

    allen_idx = [m[0] for m in matches]
    pvc_idx = [m[1] for m in matches]
    allen_m = allen_r.iloc[allen_idx].copy()
    pvc_m = pvc_r.iloc[pvc_idx].copy()

    # Partial correlations in the matched subsets
    r_pvc, p_pvc, n_pvc = _spearman_partial_controlling_for(
        pvc_m, 'f1_f0_pref', 'rep_med', ['mean_rate'])
    r_allen, p_allen, n_allen = _spearman_partial_controlling_for(
        allen_m, 'f1_f0_pref', 'rep_med', ['mean_rate'])

    return dict(
        tol=tol,
        n_matches=int(len(matches)),
        n_pvc11_orig=int(len(pvc_r)), n_allen_orig=int(len(allen_r)),
        matched_rate_median_pvc11=float(pvc_m['mean_rate'].median()),
        matched_rate_median_allen=float(allen_m['mean_rate'].median()),
        rho_pvc11_matched=r_pvc, p_pvc11_matched=p_pvc,
        n_pvc11_matched_well=n_pvc,
        rho_allen_matched=r_allen, p_allen_matched=p_allen,
        n_allen_matched_well=n_allen,
        delta_rho_matched=r_pvc - r_allen,
    )


def _fisher_z(rho: float) -> float:
    return 0.5 * np.log((1 + rho) / (1 - rho)) if abs(rho) < 1 else 0.0


def _fisher_z_inv(z: float) -> float:
    return float(np.tanh(z))


def method_c_meta_with_count_covariate(pvc: pd.DataFrame,
                                          allen: pd.DataFrame) -> dict:
    """Method C — per-recording partial correlation with mean_rate AND
    n_events_in as covariates, Fisher-Z meta-analyse.

    Compared against partial correlation with only mean_rate as
    covariate (the Phase 22a/24 convention).
    """
    out = {'recordings': []}
    for substrate, df in [('pvc11', pvc), ('allen', allen)]:
        per_rec = []
        for rec, sub in df.groupby('recording'):
            if len(sub) < 8: continue
            sub = sub.dropna(subset=['mean_rate', 'f1_f0_pref',
                                       'rep_med', 'n_events_in'])
            if len(sub) < 8: continue
            r_rate, _, n_rate = _spearman_partial_controlling_for(
                sub, 'f1_f0_pref', 'rep_med', ['mean_rate'])
            r_both, _, n_both = _spearman_partial_controlling_for(
                sub, 'f1_f0_pref', 'rep_med', ['mean_rate', 'n_events_in'])
            per_rec.append(dict(
                substrate=substrate, recording=str(rec),
                n_units=int(n_rate),
                rho_rate_only=r_rate, rho_rate_count=r_both,
                attenuation=r_rate - r_both,
            ))
        if not per_rec: continue
        out['recordings'].extend(per_rec)
        # Fisher-Z meta per covariate set
        per_df = pd.DataFrame(per_rec)
        for col in ['rho_rate_only', 'rho_rate_count']:
            zs = per_df[col].apply(_fisher_z).to_numpy()
            ws = (per_df['n_units'] - 3).to_numpy().astype(float)
            ws = np.where(ws < 1, 1, ws)
            z_fixed = float(np.sum(ws * zs) / max(np.sum(ws), 1e-6))
            rho_fixed = _fisher_z_inv(z_fixed)
            out[f'{substrate}_{col}_meta_fix'] = rho_fixed
    return out


def aggregate_verdict(method_0: dict, method_a: pd.DataFrame,
                        method_b: dict, method_c: dict) -> dict:
    """Compose Phase 27 H_F1F0 verdict per the brief:

    SUBSTRATE-SYSTEMATIC : sign flip persists under A, B, AND C.
    PARTIALLY-CONFOUNDED : attenuation but not reversal.
    DEFLATIONARY         : sign flip vanishes/reverses under rate matching.
    UNDERPOWERED         : Method B subsample too small.
    """
    # Phase 24 Full baseline: Allen meta-fix −0.183 vs pvc-11 +0.388 →
    # opposite-sign in two substrates is the sign flip we're testing.
    pvc_meta_rate = method_c.get('pvc11_rho_rate_only_meta_fix', float('nan'))
    pvc_meta_both = method_c.get('pvc11_rho_rate_count_meta_fix', float('nan'))
    al_meta_rate = method_c.get('allen_rho_rate_only_meta_fix', float('nan'))
    al_meta_both = method_c.get('allen_rho_rate_count_meta_fix', float('nan'))

    # Sign-flip status with each covariate set
    sign_flip_rate_only = (pvc_meta_rate > 0) and (al_meta_rate < 0)
    sign_flip_with_count = (pvc_meta_both > 0) and (al_meta_both < 0)

    # Method B
    b_matches = method_b.get('n_matches', 0)
    underpowered_b = b_matches < 50
    if not underpowered_b:
        b_pvc = method_b.get('rho_pvc11_matched', float('nan'))
        b_allen = method_b.get('rho_allen_matched', float('nan'))
        b_sign_flip = (b_pvc > 0) and (b_allen < 0)
    else:
        b_sign_flip = None

    # Method A — within-substrate heterogeneity
    method_a_pvc = method_a[method_a['substrate'] == 'pvc11']
    method_a_allen = method_a[method_a['substrate'] == 'allen']
    pvc_signs = (method_a_pvc['partial_rho'] > 0).sum() / max(len(method_a_pvc), 1)
    al_signs = (method_a_allen['partial_rho'] < 0).sum() / max(len(method_a_allen), 1)
    a_pvc_consistent = pvc_signs >= 0.6
    a_allen_consistent = al_signs >= 0.6

    if underpowered_b:
        verdict = 'UNDERPOWERED' if not (sign_flip_with_count and a_pvc_consistent and a_allen_consistent) else 'SUBSTRATE-SYSTEMATIC'
    else:
        if (sign_flip_with_count and b_sign_flip and a_pvc_consistent and a_allen_consistent):
            verdict = 'SUBSTRATE-SYSTEMATIC'
        elif (sign_flip_rate_only and not b_sign_flip):
            verdict = 'DEFLATIONARY'
        elif (sign_flip_rate_only and sign_flip_with_count and not b_sign_flip):
            verdict = 'DEFLATIONARY'
        else:
            verdict = 'PARTIALLY-CONFOUNDED'

    return dict(
        verdict=verdict,
        sign_flip_rate_only_meta=bool(sign_flip_rate_only),
        sign_flip_with_count_meta=bool(sign_flip_with_count),
        sign_flip_in_method_b=(bool(b_sign_flip) if b_sign_flip is not None
                                  else 'underpowered'),
        method_a_pvc11_pct_positive=float(pvc_signs),
        method_a_allen_pct_negative=float(al_signs),
        method_b_n_matches=int(b_matches),
        method_b_rho_pvc11_matched=method_b.get('rho_pvc11_matched'),
        method_b_rho_allen_matched=method_b.get('rho_allen_matched'),
        method_c_pvc11_meta_rate_only=pvc_meta_rate,
        method_c_pvc11_meta_with_count=pvc_meta_both,
        method_c_allen_meta_rate_only=al_meta_rate,
        method_c_allen_meta_with_count=al_meta_both,
        method_c_attenuation_pvc11=pvc_meta_rate - pvc_meta_both,
        method_c_attenuation_allen=al_meta_rate - al_meta_both,
        method_0=method_0,
    )


def main():
    print("=" * 72)
    print("Phase 27 Analysis 1 — F1/F0 rate-matched check")
    print("=" * 72)
    pvc, allen = load_substrate_tables()
    print(f"  pvc-11 units (F1/F0 + ARS): {len(pvc)}")
    print(f"  Allen units (F1/F0 + ARS): {len(allen)}")

    print()
    print("Method 0 — firing-rate distribution comparison:")
    m0 = method0_rate_distribution(pvc, allen)
    print(f"  pvc-11: median={m0['pvc11_median']:.2f} sp/s  "
            f"[q05={m0['pvc11_q05']:.2f}, q95={m0['pvc11_q95']:.2f}]")
    print(f"  Allen:  median={m0['allen_median']:.2f} sp/s  "
            f"[q05={m0['allen_q05']:.2f}, q95={m0['allen_q95']:.2f}]")
    print(f"  overlap region: [{m0['overlap_lo']:.2f}, {m0['overlap_hi']:.2f}] sp/s")
    print(f"  pvc-11 in overlap: {m0['n_pvc11_in_overlap']} / {m0['pvc11_n']}  "
            f"({m0['overlap_fraction_pvc11']*100:.1f}%)")
    print(f"  Allen in overlap:  {m0['n_allen_in_overlap']} / {m0['allen_n']}  "
            f"({m0['overlap_fraction_allen']*100:.1f}%)")
    print(f"  KS test on log10(rate): D={m0['log10_rate_ks_stat']:.3f}  "
            f"p={m0['log10_rate_ks_p']:.2e}")

    print()
    print("Method A — within-substrate spike-count tertile partials:")
    m_a = method_a_within_substrate_tertiles(pvc, allen, n_bins=3)
    m_a.to_parquet(OUT_DIR / 'analysis1_method_a.parquet', index=False)
    for substrate, sub in m_a.groupby('substrate'):
        print(f"  {substrate}:")
        for _, r in sub.iterrows():
            print(f"    {r['recording']:32s} bin{r['bin_idx']} "
                    f"(n={r['n_units']}, count {r['count_lo']:.0f}-{r['count_hi']:.0f}):  "
                    f"ρ_partial={r['partial_rho']:+.3f}  p={r['partial_p']:.3f}")

    print()
    print("Method B — rate-matched cross-substrate subsamples (tol=20%):")
    m_b = method_b_rate_matched_subsamples(pvc, allen, tol=0.20)
    with open(OUT_DIR / 'analysis1_method_b.json', 'w') as f:
        json.dump(m_b, f, indent=2)
    print(f"  n matches: {m_b.get('n_matches', 0)}")
    if m_b.get('n_matches', 0):
        print(f"  matched-rate median: pvc-11 {m_b['matched_rate_median_pvc11']:.2f} "
                f"vs Allen {m_b['matched_rate_median_allen']:.2f} sp/s")
        print(f"  ρ_partial (matched, controlling for mean_rate):")
        print(f"    pvc-11: {m_b['rho_pvc11_matched']:+.3f}  p={m_b['p_pvc11_matched']:.3f}  "
                f"n={m_b['n_pvc11_matched_well']}")
        print(f"    Allen:  {m_b['rho_allen_matched']:+.3f}  p={m_b['p_allen_matched']:.3f}  "
                f"n={m_b['n_allen_matched_well']}")
        print(f"    delta:  {m_b['delta_rho_matched']:+.3f}")

    print()
    print("Method C — per-recording partial + Fisher-Z meta with count covariate:")
    m_c = method_c_meta_with_count_covariate(pvc, allen)
    with open(OUT_DIR / 'analysis1_method_c.json', 'w') as f:
        json.dump(m_c, f, indent=2)
    for substrate in ['pvc11', 'allen']:
        rate_meta = m_c.get(f'{substrate}_rho_rate_only_meta_fix', float('nan'))
        both_meta = m_c.get(f'{substrate}_rho_rate_count_meta_fix', float('nan'))
        print(f"  {substrate}: meta-fix rho (rate-only)={rate_meta:+.3f}  "
                f"vs (rate+count)={both_meta:+.3f}  attenuation={rate_meta - both_meta:+.3f}")

    print()
    print("Aggregate verdict:")
    verdict = aggregate_verdict(m0, m_a, m_b, m_c)
    with open(OUT_DIR / 'analysis1_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2, default=str)
    print(json.dumps({k: v for k, v in verdict.items() if k != 'method_0'},
                       indent=2, default=str))


if __name__ == '__main__':
    main()
