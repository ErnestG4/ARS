"""
phase31b/allen_f1f0_rate_stratified.py — Allen F1/F0 ↔ rep_med rate-
stratified within-cell replication.

Tests whether Phase 24's substrate-systematic F1/F0 sign flip (Allen
−0.183 vs pvc-11 +0.388) holds under within-session rate-tertile
stratification.

Method.  For each Allen session × condition (drifting_pooled is the
F1/F0-relevant condition), merge per-unit ARS (rep_med, ks_gue_med)
with per-unit functional (f1_f0_pref, mean_rate).  Split units into
3 rate tertiles per session; compute Spearman ρ(f1_f0_pref, rep_med)
within each tertile.

Same survival criteria as Phase 31b H1 / F1/F0 pilot:
  - sign-consistent across tertiles in ≥ 70% of sessions
  - mean magnitude range across tertiles < 0.3

Output:
  data/phase31b_results/Allen_F1F0_rate_stratified.parquet
  data/phase31b_results/Allen_F1F0_rate_stratified_verdict.json
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


def signs_consistent(rho_low, rho_mid, rho_high) -> bool:
    vals = [v for v in (rho_low, rho_mid, rho_high) if np.isfinite(v)]
    if not vals:
        return False
    signs = [(1 if v > 0.05 else (-1 if v < -0.05 else 0)) for v in vals]
    nonzero = [s for s in signs if s != 0]
    if not nonzero:
        return True
    return all(s == nonzero[0] for s in nonzero)


def magnitude_range(rho_low, rho_mid, rho_high) -> float:
    vals = [v for v in (rho_low, rho_mid, rho_high) if np.isfinite(v)]
    if not vals:
        return np.nan
    return float(max(vals) - min(vals))


def main():
    print("=" * 72)
    print("Phase 31b — Allen F1/F0 ↔ rep_med rate-stratified replication")
    print("=" * 72)

    p24 = Path(ROOT_DIR) / 'data' / 'phase24_results'
    h1_func = pd.read_parquet(p24 / 'per_session_h1_functional.parquet')
    h1_ars = pd.read_parquet(p24 / 'per_session_h1_ars.parquet')
    print(f"  per_session_h1_functional rows: {len(h1_func)}")
    print(f"  per_session_h1_ars rows: {len(h1_ars)}\n")

    # F1/F0 is computed on drifting_gratings (which Phase 24 calls
    # `drifting_pooled` in the ARS pipeline)
    h1_ars_g = h1_ars[h1_ars['condition'] == 'drifting_pooled']

    merged = h1_ars_g.merge(
        h1_func[['session_id', 'unit_id', 'mean_rate', 'osi', 'dsi',
                  'f1_f0_pref']],
        on=['session_id', 'unit_id'], how='inner'
    )
    merged = merged.dropna(subset=['f1_f0_pref', 'rep_med', 'mean_rate'])
    print(f"  Merged rows (drifting_pooled): {len(merged)}")
    print(f"  Per-session unit counts:")
    print(merged.groupby('session_id').size().to_string())

    rows = []
    for session_id, sub in merged.groupby('session_id'):
        n = len(sub)
        if n < 9:
            continue
        # Per-session rate tertiles
        ranks = pd.Series(sub['mean_rate'].values).rank(method='first')
        bounds = np.quantile(ranks, [1/3, 2/3])

        def tertile(r):
            return 0 if r <= bounds[0] else (1 if r <= bounds[1] else 2)

        sub = sub.copy()
        sub['tertile'] = ranks.apply(tertile).values

        # Unstratified
        rho_all, p_all = spearmanr(sub['f1_f0_pref'], sub['rep_med'])
        rho_osi_all, _ = spearmanr(sub['osi'], sub['ks_gue_med'])
        rho_dsi_all, _ = spearmanr(sub['dsi'], sub['ks_gue_med'])

        tertile_rhos_ff = {}
        tertile_rhos_osi = {}
        for t in range(3):
            ts = sub[sub['tertile'] == t]
            if len(ts) >= 3:
                rho_ff_t, _ = spearmanr(ts['f1_f0_pref'], ts['rep_med'])
                rho_osi_t, _ = spearmanr(ts['osi'], ts['ks_gue_med'])
            else:
                rho_ff_t, rho_osi_t = np.nan, np.nan
            tertile_rhos_ff[t] = (rho_ff_t, len(ts))
            tertile_rhos_osi[t] = (rho_osi_t, len(ts))

        rows.append(dict(
            session_id=int(session_id), n_units=n,
            mean_rate_min=float(sub['mean_rate'].min()),
            mean_rate_max=float(sub['mean_rate'].max()),
            rho_ff_unstratified=float(rho_all),
            rho_ff_low=float(tertile_rhos_ff[0][0]),
            n_ff_low=int(tertile_rhos_ff[0][1]),
            rho_ff_mid=float(tertile_rhos_ff[1][0]),
            n_ff_mid=int(tertile_rhos_ff[1][1]),
            rho_ff_high=float(tertile_rhos_ff[2][0]),
            n_ff_high=int(tertile_rhos_ff[2][1]),
            rho_osi_unstratified=float(rho_osi_all),
            rho_osi_low=float(tertile_rhos_osi[0][0]),
            rho_osi_mid=float(tertile_rhos_osi[1][0]),
            rho_osi_high=float(tertile_rhos_osi[2][0]),
        ))

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_DIR / 'Allen_F1F0_rate_stratified.parquet', index=False)
    print(f"\n{df[['session_id', 'n_units', 'rho_ff_unstratified', 'rho_ff_low', 'rho_ff_mid', 'rho_ff_high']].round(3).to_string(index=False)}")

    # Per-finding survival check
    print("\n=== F1/F0 ↔ rep_med (Allen) ===")
    df['ff_signs_consistent'] = df.apply(
        lambda r: signs_consistent(r['rho_ff_low'], r['rho_ff_mid'],
                                      r['rho_ff_high']), axis=1)
    df['ff_mag_range'] = df.apply(
        lambda r: magnitude_range(r['rho_ff_low'], r['rho_ff_mid'],
                                     r['rho_ff_high']), axis=1)
    n_consistent = int(df['ff_signs_consistent'].sum())
    n_total = len(df)
    mean_mag_range = float(df['ff_mag_range'].mean())
    mean_unstrat = float(df['rho_ff_unstratified'].mean())
    mean_tertile = float(df[['rho_ff_low', 'rho_ff_mid',
                               'rho_ff_high']].mean(axis=1).mean())
    n_negative_unstrat = int((df['rho_ff_unstratified'] < 0).sum())
    n_negative_tertile_mean = int(
        (df[['rho_ff_low', 'rho_ff_mid', 'rho_ff_high']].mean(axis=1) < 0).sum()
    )

    print(f"  Sign-consistent (3 tertiles) across sessions: "
          f"{n_consistent}/{n_total}")
    print(f"  Mean magnitude range across tertiles: {mean_mag_range:.3f}")
    print(f"  Mean unstratified ρ (Allen): {mean_unstrat:+.3f}")
    print(f"  Mean tertile-mean ρ:          {mean_tertile:+.3f}")
    print(f"  Sessions with negative unstratified ρ: {n_negative_unstrat}/{n_total}")
    print(f"  Sessions with negative tertile-mean ρ:  {n_negative_tertile_mean}/{n_total}")

    if mean_unstrat < -0.05 and mean_tertile < -0.05 \
       and n_negative_unstrat / max(n_total, 1) >= 0.7 \
       and n_negative_tertile_mean / max(n_total, 1) >= 0.7:
        verdict = 'SUBSTRATE_SYSTEMATIC_SURVIVES_STRATIFIED'
    elif n_consistent / max(n_total, 1) >= 0.7 and mean_mag_range < 0.3:
        verdict = 'PER_SESSION_STABLE_BUT_SIGN_MIXED'
    elif n_consistent / max(n_total, 1) >= 0.5:
        verdict = 'PARTIAL_SURVIVAL'
    else:
        verdict = 'MATERIAL_SHIFT'

    # Also report OSI (already known to survive at pvc-11 level)
    print("\n=== OSI ↔ ks_gue_med (Allen) — cross-check ===")
    df['osi_signs_consistent'] = df.apply(
        lambda r: signs_consistent(r['rho_osi_low'], r['rho_osi_mid'],
                                      r['rho_osi_high']), axis=1)
    df['osi_mag_range'] = df.apply(
        lambda r: magnitude_range(r['rho_osi_low'], r['rho_osi_mid'],
                                     r['rho_osi_high']), axis=1)
    n_osi_consistent = int(df['osi_signs_consistent'].sum())
    mean_osi_mag = float(df['osi_mag_range'].mean())
    mean_osi_unstrat = float(df['rho_osi_unstratified'].mean())
    n_pos_osi_unstrat = int((df['rho_osi_unstratified'] > 0).sum())
    print(f"  Sign-consistent (3 tertiles): {n_osi_consistent}/{n_total}")
    print(f"  Mean magnitude range: {mean_osi_mag:.3f}")
    print(f"  Mean unstratified ρ: {mean_osi_unstrat:+.3f}")
    print(f"  Sessions with positive unstratified ρ: {n_pos_osi_unstrat}/{n_total}")

    summary = dict(
        n_sessions=n_total,
        ff_verdict=verdict,
        ff_n_consistent=n_consistent,
        ff_mean_magnitude_range=mean_mag_range,
        ff_mean_unstratified=mean_unstrat,
        ff_mean_tertile=mean_tertile,
        ff_n_negative_unstrat=n_negative_unstrat,
        ff_n_negative_tertile=n_negative_tertile_mean,
        osi_n_consistent=n_osi_consistent,
        osi_mean_magnitude_range=mean_osi_mag,
        osi_mean_unstratified=mean_osi_unstrat,
        osi_n_positive_unstrat=n_pos_osi_unstrat,
    )
    with open(OUT_DIR / 'Allen_F1F0_rate_stratified_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → Allen_F1F0_rate_stratified_verdict.json")
    print(f"\nVERDICT (F1/F0 substrate-systematic Allen): {verdict}")


if __name__ == '__main__':
    main()
