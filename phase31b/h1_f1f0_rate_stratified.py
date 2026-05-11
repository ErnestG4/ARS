"""
phase31b/h1_f1f0_rate_stratified.py — pilot rate-stratified-within-cell
on the H1 OSI↔ks_gue_med and F1/F0↔rep_med locked findings.

Per the Phase 31b rate-matched stratification finding: per-cell
rate-matched Poisson surrogate is necessary but not sufficient — the
dynamics signal is itself rate-dependent within each cell.  The H1 and
F1/F0 correlations were computed across all units pooled per recording
or meta-analyzed across recordings.  Whether they survive a
**within-recording rate-tertile stratified comparison** is the
load-bearing audit.

Method.  For pvc-11 (Phase 22a) and Allen (Phase 24):

  1. Match per-unit OSI / DSI / F1/F0 (from h1_functional) with
     per-unit ks_gue_med / rep_med (from h1_classifications).
  2. Within each recording, split units into rate tertiles
     (low / mid / high).
  3. Compute Spearman ρ(OSI, ks_gue_med), ρ(DSI, ks_gue_med),
     ρ(F1/F0, rep_med) within each tertile.
  4. Compare: do tertile-specific correlations match the unstratified
     correlation?  If all tertiles show the same sign and similar
     magnitude → SURVIVES (grandfather).  If signs flip across tertiles
     or magnitudes differ ≥ 0.2 → MATERIAL SHIFT (revisit).

Output:
  data/phase31b_results/H1_F1F0_rate_stratified_pvc11.parquet
  data/phase31b_results/H1_F1F0_rate_stratified_verdict.json
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def stratified_correlations(df: pd.DataFrame, group_col: str,
                              metric_col: str, descriptor_cols: list,
                              rate_col: str = 'mean_rate',
                              n_tertiles: int = 3) -> pd.DataFrame:
    """For each (recording, descriptor), compute within-recording
    Spearman correlation between descriptor and ARS metric for each
    rate tertile.  Also report the unstratified correlation."""
    rows = []
    for recording, sub in df.groupby(group_col):
        n_units = len(sub)
        if n_units < 9:
            continue
        # Rate tertiles by within-recording rank
        rates = sub[rate_col].values
        ranks = pd.Series(rates).rank(method='first')
        tertile_boundaries = np.quantile(ranks, [1/3, 2/3])

        def assign_tertile(r):
            return 0 if r <= tertile_boundaries[0] else (
                    1 if r <= tertile_boundaries[1] else 2)

        sub = sub.copy()
        sub['tertile'] = ranks.apply(assign_tertile).values

        for desc in descriptor_cols:
            mask_full = sub[[desc, metric_col]].notna().all(axis=1)
            full_sub = sub[mask_full]
            if len(full_sub) >= 3:
                rho_all, p_all = spearmanr(full_sub[desc],
                                              full_sub[metric_col])
            else:
                rho_all, p_all = np.nan, np.nan

            tertile_rhos = {}
            for t in range(n_tertiles):
                tertile_sub = full_sub[full_sub['tertile'] == t]
                if len(tertile_sub) >= 3:
                    rho_t, p_t = spearmanr(tertile_sub[desc],
                                              tertile_sub[metric_col])
                else:
                    rho_t, p_t = np.nan, np.nan
                tertile_rhos[t] = (rho_t, p_t, len(tertile_sub))

            rows.append(dict(
                recording=str(recording),
                descriptor=desc, metric=metric_col,
                n_units_total=int(n_units),
                rho_unstratified=float(rho_all),
                p_unstratified=float(p_all),
                rho_low=float(tertile_rhos[0][0]),
                p_low=float(tertile_rhos[0][1]),
                n_low=int(tertile_rhos[0][2]),
                rho_mid=float(tertile_rhos[1][0]),
                p_mid=float(tertile_rhos[1][1]),
                n_mid=int(tertile_rhos[1][2]),
                rho_high=float(tertile_rhos[2][0]),
                p_high=float(tertile_rhos[2][1]),
                n_high=int(tertile_rhos[2][2]),
            ))
    return pd.DataFrame(rows)


def signs_consistent(rho_low, rho_mid, rho_high) -> bool:
    """All three rho values have the same sign (within rounding)."""
    vals = [v for v in (rho_low, rho_mid, rho_high) if np.isfinite(v)]
    if not vals:
        return False
    signs = [(1 if v > 0.05 else (-1 if v < -0.05 else 0)) for v in vals]
    nonzero_signs = [s for s in signs if s != 0]
    if not nonzero_signs:
        return True
    return all(s == nonzero_signs[0] for s in nonzero_signs)


def magnitude_range(rho_low, rho_mid, rho_high) -> float:
    vals = [v for v in (rho_low, rho_mid, rho_high) if np.isfinite(v)]
    if not vals:
        return np.nan
    return float(max(vals) - min(vals))


def main():
    print("=" * 72)
    print("Phase 31b — H1 / F1/F0 rate-stratified within-cell pilot")
    print("=" * 72)

    # ─── pvc-11 ───
    p22a = Path(ROOT_DIR) / 'data' / 'phase22a_results'
    h1_class = pd.read_parquet(p22a / 'h1_classifications.parquet')
    h1_func = pd.read_parquet(p22a / 'h1_functional.parquet')

    # Restrict to gratings subset (only place F1/F0 + OSI + DSI are defined)
    h1_func = h1_func[h1_func['subset'] == 'gratings']
    h1_class_g = h1_class[h1_class['subset'] == 'gratings']

    # Merge per-unit (recording, unit_idx) on classification → functional
    merged = h1_class_g.merge(
        h1_func[['recording', 'unit_idx', 'mean_rate', 'osi', 'dsi',
                  'f1_f0_pref', 'snr']],
        on=['recording', 'unit_idx'], how='inner'
    )
    print(f"\nMerged pvc-11 gratings rows: {len(merged)}")
    print(f"Recordings: {merged['recording'].nunique()}")
    print(f"Per-recording n_units:")
    print(merged.groupby('recording').size().to_string())

    # H1 OSI ↔ ks_gue_med
    print("\n--- H1: OSI ↔ ks_gue_med (rate-stratified) ---")
    h1_stratified = stratified_correlations(
        merged, group_col='recording',
        metric_col='ks_gue_med',
        descriptor_cols=['osi', 'dsi'],
    )
    print(h1_stratified.round(3).to_string(index=False))

    # F1/F0 ↔ rep_med
    print("\n--- F1/F0 ↔ rep_med (rate-stratified) ---")
    ff_stratified = stratified_correlations(
        merged, group_col='recording',
        metric_col='rep_med',
        descriptor_cols=['f1_f0_pref'],
    )
    print(ff_stratified.round(3).to_string(index=False))

    pvc_combined = pd.concat([h1_stratified, ff_stratified],
                              ignore_index=True)
    pvc_combined.to_parquet(OUT_DIR / 'H1_F1F0_rate_stratified_pvc11.parquet',
                              index=False)
    print(f"\n  → H1_F1F0_rate_stratified_pvc11.parquet")

    # ─── Per-finding survival check ───
    print("\n=== Per-finding survival check ===")
    survival = []
    for finding, fpfilt in [
        ('H1_OSI_ks_gue_med', (pvc_combined['descriptor'] == 'osi')
                                & (pvc_combined['metric'] == 'ks_gue_med')),
        ('DSI_ks_gue_med', (pvc_combined['descriptor'] == 'dsi')
                            & (pvc_combined['metric'] == 'ks_gue_med')),
        ('F1F0_rep_med', (pvc_combined['descriptor'] == 'f1_f0_pref')
                          & (pvc_combined['metric'] == 'rep_med')),
    ]:
        sub = pvc_combined[fpfilt].copy()
        sub['signs_consistent'] = sub.apply(
            lambda r: signs_consistent(r['rho_low'], r['rho_mid'],
                                          r['rho_high']),
            axis=1
        )
        sub['mag_range'] = sub.apply(
            lambda r: magnitude_range(r['rho_low'], r['rho_mid'],
                                         r['rho_high']),
            axis=1
        )
        n_consistent = int(sub['signs_consistent'].sum())
        n_total = len(sub)
        mean_mag_range = float(sub['mag_range'].mean())
        # Unstratified vs mean-across-tertiles
        mean_tertile_rho = sub[['rho_low', 'rho_mid', 'rho_high']].mean(axis=1)
        unstrat_vs_tertile_diff = (sub['rho_unstratified'] - mean_tertile_rho).abs().mean()

        if n_consistent / max(n_total, 1) >= 0.7 and mean_mag_range < 0.3:
            verdict = 'SURVIVES_STRATIFIED'
        elif n_consistent / max(n_total, 1) >= 0.5:
            verdict = 'PARTIAL_SURVIVAL'
        else:
            verdict = 'MATERIAL_SHIFT'

        print(f"\n  {finding}: {verdict}")
        print(f"    sign-consistent across tertiles: "
              f"{n_consistent}/{n_total}  (need 70%+ → SURVIVE)")
        print(f"    mean magnitude range across tertiles: {mean_mag_range:.3f}  "
              f"(need < 0.3 → SURVIVE)")
        print(f"    mean |unstratified − tertile-mean|: "
              f"{unstrat_vs_tertile_diff:.3f}")
        survival.append(dict(
            finding=finding, verdict=verdict,
            n_consistent=n_consistent, n_total=n_total,
            mean_magnitude_range=mean_mag_range,
            mean_unstrat_minus_tertile=float(unstrat_vs_tertile_diff),
        ))
    survival_df = pd.DataFrame(survival)

    summary = dict(
        n_recordings_pvc11=int(merged['recording'].nunique()),
        n_units_total=int(len(merged)),
        per_finding=survival,
    )
    with open(OUT_DIR / 'H1_F1F0_rate_stratified_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → H1_F1F0_rate_stratified_verdict.json")


if __name__ == '__main__':
    main()
