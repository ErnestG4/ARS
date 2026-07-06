"""
phase31b/padic_v4_real_vs_surrogate.py — matched real-vs-surrogate
comparison for p-adic v4 confidence.

Phase 31b smoke test revealed that the 1.5× per-q-power-normalised
threshold validated at q_max=200 in §7.ter.13 is **underpowered at
q_max=30** for the deployed parquets — rate-matched Poisson surrogates
pass the threshold 95.6 % of the time on pvc-11, vs 67 % for real
data.

The correct discrimination is **per-recording real-vs-surrogate
confidence delta**: does the real data's max per-q-power-normalised
ratio exceed the surrogate's at the same recording?

Outputs:
  data/phase31b_results/padic_v4_real_vs_surrogate_pvc11.parquet
  data/phase31b_results/padic_v4_real_vs_surrogate_allen.parquet
  data/phase31b_results/padic_v4_real_vs_surrogate_verdict.json
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'

PRIMES = [2, 3, 5, 7, 11, 13]


def match_real_vs_surrogate(real_df, sur_df, key_col):
    """Match each real recording to its surrogate average confidence.
    Returns DataFrame with: recording, confidence_real, confidence_sur_mean,
    confidence_sur_max, delta, real_dom_prime, real_above_sur_max.
    """
    rows = []
    for key, real_row in real_df.groupby(key_col):
        # Single real row per key
        rr = real_row.iloc[0]
        sub_sur = sur_df[sur_df[key_col] == key]
        if not len(sub_sur):
            rows.append(dict(
                recording=str(key),
                confidence_real=float(rr['confidence']),
                confidence_sur_mean=np.nan,
                confidence_sur_max=np.nan,
                confidence_sur_std=np.nan,
                n_sur=0,
                delta_vs_sur_mean=np.nan,
                delta_vs_sur_max=np.nan,
                real_dom_prime=int(rr['dominant_prime_per_q']),
                real_above_sur_max=False,
                z_score=np.nan,
            ))
            continue
        c_real = float(rr['confidence'])
        c_sur_mean = float(sub_sur['confidence'].mean())
        c_sur_max = float(sub_sur['confidence'].max())
        c_sur_std = float(sub_sur['confidence'].std())
        z = (c_real - c_sur_mean) / max(c_sur_std, 1e-6)
        rows.append(dict(
            recording=str(key),
            confidence_real=c_real,
            confidence_sur_mean=c_sur_mean,
            confidence_sur_max=c_sur_max,
            confidence_sur_std=c_sur_std,
            n_sur=int(len(sub_sur)),
            delta_vs_sur_mean=float(c_real - c_sur_mean),
            delta_vs_sur_max=float(c_real - c_sur_max),
            real_dom_prime=int(rr['dominant_prime_per_q']),
            real_above_sur_max=bool(c_real > c_sur_max),
            z_score=float(z),
        ))
    return pd.DataFrame(rows)


def per_prime_delta(real_df, sur_df, key_col):
    """For each (recording, prime), compute real − surrogate-mean of
    `normed_per_q_p{prime}`.  Identifies which primes carry the signal
    above the surrogate floor."""
    rows = []
    for key, real_row in real_df.groupby(key_col):
        rr = real_row.iloc[0]
        sub_sur = sur_df[sur_df[key_col] == key]
        for p in PRIMES:
            col = f'normed_per_q_p{p}'
            if col not in rr.index:
                continue
            r_val = float(rr[col])
            if len(sub_sur):
                s_mean = float(sub_sur[col].mean())
                s_std = float(sub_sur[col].std())
                z = (r_val - s_mean) / max(s_std, 1e-6)
            else:
                s_mean, s_std, z = np.nan, np.nan, np.nan
            rows.append(dict(
                recording=str(key), prime=p,
                real_ratio=r_val,
                sur_mean=s_mean, sur_std=s_std,
                delta=r_val - s_mean if not np.isnan(s_mean) else np.nan,
                z_score=z,
            ))
    return pd.DataFrame(rows)


def main():
    print("=" * 72)
    print("Phase 31b — p-adic v4 real-vs-surrogate matched comparison")
    print("=" * 72)

    # pvc-11
    real_pvc = pd.read_parquet(OUT_DIR / 'padic_v4_pvc11.parquet')
    sur_pvc = pd.read_parquet(OUT_DIR / 'padic_v4_pvc11_surrogates.parquet')
    # Surrogate parquet has q_max column; filter to q_max=30
    if 'q_max' in sur_pvc.columns:
        sur_pvc = sur_pvc[sur_pvc['q_max'] == 30]
    # Restrict to rate-matched-Poisson surrogate (the cleanest null)
    sur_pvc_rm = sur_pvc[sur_pvc['surrogate'] == 'rate_matched_poisson']

    print(f"\npvc-11: {len(real_pvc)} real recordings, "
          f"{len(sur_pvc_rm)} rate-matched-Poisson surrogate (×3 seeds typically)")
    pvc_match = match_real_vs_surrogate(real_pvc, sur_pvc_rm,
                                          key_col='recording')
    pvc_match.to_parquet(OUT_DIR / 'padic_v4_real_vs_surrogate_pvc11.parquet',
                          index=False)
    print()
    print(pvc_match[['recording', 'confidence_real', 'confidence_sur_mean',
                      'confidence_sur_max', 'delta_vs_sur_mean',
                      'real_above_sur_max', 'z_score',
                      'real_dom_prime']].to_string(index=False))

    pvc_z = pvc_match['z_score'].dropna()
    print(f"\n  pvc-11 z-score summary: mean={pvc_z.mean():+.2f}  "
          f"max={pvc_z.max():+.2f}  min={pvc_z.min():+.2f}")
    print(f"  Recordings with real > sur_max: {pvc_match['real_above_sur_max'].sum()}/{len(pvc_match)}")
    print(f"  Recordings with z > 2: {(pvc_z > 2).sum()}/{len(pvc_z)}")

    # Per-prime
    pvc_per_p = per_prime_delta(real_pvc, sur_pvc_rm, key_col='recording')
    pvc_per_p.to_parquet(OUT_DIR / 'padic_v4_real_vs_surrogate_pvc11_per_prime.parquet',
                          index=False)
    print(f"\n  pvc-11 per-prime z-score by prime (positive = real > sur):")
    by_p = pvc_per_p.groupby('prime')['z_score'].agg(['mean', 'std', 'max'])
    print(by_p.to_string())

    # Allen
    real_allen = pd.read_parquet(OUT_DIR / 'padic_v4_allen.parquet')
    sur_allen = pd.read_parquet(OUT_DIR / 'padic_v4_allen_surrogates.parquet')
    sur_allen_rm = sur_allen[sur_allen['surrogate'] == 'rate_matched_poisson']
    print(f"\nAllen: {len(real_allen)} real × condition, "
          f"{len(sur_allen_rm)} rate-matched-Poisson surrogate")
    real_allen['rec_cond'] = real_allen['session_id'].astype(str) + '_' + real_allen['condition'].astype(str)
    sur_allen_rm = sur_allen_rm.copy()
    sur_allen_rm['rec_cond'] = sur_allen_rm['session_id'].astype(str) + '_' + sur_allen_rm['condition'].astype(str)
    allen_match = match_real_vs_surrogate(real_allen, sur_allen_rm,
                                            key_col='rec_cond')
    allen_match.to_parquet(OUT_DIR / 'padic_v4_real_vs_surrogate_allen.parquet',
                            index=False)
    a_z = allen_match['z_score'].dropna()
    print(f"\n  Allen z-score summary: mean={a_z.mean():+.2f}  "
          f"max={a_z.max():+.2f}  min={a_z.min():+.2f}")
    print(f"  Recordings with real > sur_max: {allen_match['real_above_sur_max'].sum()}/{len(allen_match)}")
    print(f"  Recordings with z > 2: {(a_z > 2).sum()}/{len(a_z)}")

    allen_per_p = per_prime_delta(real_allen, sur_allen_rm, key_col='rec_cond')
    allen_per_p.to_parquet(OUT_DIR / 'padic_v4_real_vs_surrogate_allen_per_prime.parquet',
                            index=False)
    print(f"\n  Allen per-prime z-score by prime:")
    by_p = allen_per_p.groupby('prime')['z_score'].agg(['mean', 'std', 'max'])
    print(by_p.to_string())

    summary = dict(
        pvc11=dict(
            n_recordings=int(len(pvc_match)),
            n_real_above_sur_max=int(pvc_match['real_above_sur_max'].sum()),
            mean_z=float(pvc_z.mean()) if len(pvc_z) else np.nan,
            max_z=float(pvc_z.max()) if len(pvc_z) else np.nan,
            recordings_z_gt_2=pvc_match[pvc_match['z_score'] > 2]['recording'].tolist(),
        ),
        allen=dict(
            n_recordings=int(len(allen_match)),
            n_real_above_sur_max=int(allen_match['real_above_sur_max'].sum()),
            mean_z=float(a_z.mean()) if len(a_z) else np.nan,
            max_z=float(a_z.max()) if len(a_z) else np.nan,
            recordings_z_gt_2=allen_match[allen_match['z_score'] > 2]['recording'].tolist(),
        ),
    )
    with open(OUT_DIR / 'padic_v4_real_vs_surrogate_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → padic_v4_real_vs_surrogate_verdict.json")


if __name__ == '__main__':
    main()
