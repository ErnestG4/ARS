"""
phase31b/allen_f1f0_per_session_profiles.py — per-session rate-tertile
profiles for Allen F1/F0 ↔ rep_med.

The Allen F1/F0 rate-stratified replication (Follow-up 4) established
that the substrate-systematic negative correlation concentrates in
mid-to-high-rate Allen units.  This script characterizes whether that
concentration is uniform across Allen sessions or session-heterogeneous.

For each Allen session:
  - Per-tertile rho (low / mid / high)
  - Per-tertile sample size + mean rate

Stratify Allen sessions by whether they show the canonical "low-positive,
mid-negative, high-negative" profile vs alternative profiles.

Output:
  data/phase31b_results/allen_f1f0_per_session_profiles.parquet
  data/phase31b_results/allen_f1f0_per_session_profiles_verdict.json
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

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase31b_results'


def classify_profile(low, mid, high) -> str:
    """Classify a session's rate-tertile rho profile into canonical types."""
    def sign(x, eps=0.05):
        if not np.isfinite(x): return '?'
        return '+' if x > eps else ('-' if x < -eps else '0')
    s = f"{sign(low)}{sign(mid)}{sign(high)}"
    canonical_negative_concentrated = {
        '0--': 'CANONICAL_LOW_NULL_MID_HIGH_NEG',
        '+--': 'CANONICAL_LOW_POS_MID_HIGH_NEG',
        '0-0': 'MID_NEGATIVE_ONLY',
        '--0': 'LOW_MID_NEG_HIGH_NULL',
    }
    all_negative = {'---': 'ALL_NEGATIVE'}
    mixed = {
        '+-+': 'MIXED_LOW_HIGH_POS_MID_NEG',
        '++-': 'LOW_MID_POS_HIGH_NEG',
        '-++': 'LOW_NEG_MID_HIGH_POS',
    }
    if s in canonical_negative_concentrated:
        return canonical_negative_concentrated[s]
    if s in all_negative:
        return all_negative[s]
    if s in mixed:
        return mixed[s]
    return f'OTHER_{s}'


def main():
    print("=" * 72)
    print("Phase 31b — Allen F1/F0 per-session rate-tertile profiles")
    print("=" * 72)

    df = pd.read_parquet(OUT_DIR / 'Allen_F1F0_rate_stratified.parquet')
    df['profile'] = df.apply(
        lambda r: classify_profile(r['rho_ff_low'], r['rho_ff_mid'],
                                      r['rho_ff_high']),
        axis=1
    )

    print(f"\nPer-session profile classification ({len(df)} sessions):")
    print(df[['session_id', 'n_units', 'mean_rate_min', 'mean_rate_max',
                'rho_ff_low', 'rho_ff_mid', 'rho_ff_high',
                'profile']].round(3).to_string(index=False))

    print("\nProfile distribution:")
    print(df['profile'].value_counts().to_string())

    # Cross-check: does the rate distribution differ between
    # canonical-profile vs others?
    df['canonical'] = df['profile'].str.startswith('CANONICAL_')
    print(f"\nCanonical-profile sessions: {df['canonical'].sum()}/{len(df)}")

    df.to_parquet(OUT_DIR / 'allen_f1f0_per_session_profiles.parquet',
                    index=False)

    summary = dict(
        n_sessions=len(df),
        profile_distribution=df['profile'].value_counts().to_dict(),
        n_canonical=int(df['canonical'].sum()),
        per_session_profiles=df[['session_id', 'profile', 'rho_ff_low',
                                    'rho_ff_mid', 'rho_ff_high']].to_dict('records'),
    )
    with open(OUT_DIR / 'allen_f1f0_per_session_profiles_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  → allen_f1f0_per_session_profiles_*.parquet/json")


if __name__ == '__main__':
    main()
