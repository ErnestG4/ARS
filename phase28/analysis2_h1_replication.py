"""
phase28/analysis2_h1_replication.py — H1 OSI ↔ ks_gue_med replication
note on Allen Neuropixels VISp units.

Phase 24 Full already performed this analysis on the same 12-session
Allen Neuropixels VISp dataset (meta-fix +0.363 per Phase 24 Full).
Phase 28 Analysis 2 reads those results, computes the verdict per
the Phase 28 brief's acceptance criteria, and notes that the
"Allen Neuropixels" framing in the Phase 28 brief is the SAME
dataset as Phase 24 (not a different modality — Phase 24 was already
on Neuropixels electrophysiology, not 2P optical).

Per the brief acceptance criteria:
  POSITIVE  : meta-aggregate ρ > 0.2, sign-consistent ≥75% of sessions.
  ATTENUATED: ρ in [0.1, 0.2] with mixed sign-consistency.
  NULL      : ρ < 0.1 or sign-inconsistent.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase28_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)
PH24_META = (Path(ROOT_DIR) / 'data' / 'phase24_results' / 'h1_meta_overall.parquet')


def main():
    print("=" * 72)
    print("Phase 28 Analysis 2 — H1 OSI ↔ ks_gue_med replication note")
    print("=" * 72)
    print()
    print("  Note: Phase 28 brief describes Allen Neuropixels as a third")
    print("  recording modality.  Phase 24 (Full) was already performed on")
    print("  Allen Neuropixels electrophysiology (the awake-mouse-V1")
    print("  recording was Neuropixels-based, not 2P optical).  Phase 28")
    print("  Analysis 2 reads the Phase 24 Full result rather than redoing.")
    print()
    if not PH24_META.exists():
        print(f"  ERROR: Phase 24 meta-aggregate parquet missing at {PH24_META}")
        return
    meta = pd.read_parquet(PH24_META)
    print("Phase 24 Full meta-aggregate (re-read):")
    print(meta.to_string(index=False))

    # Pull OSI ↔ ks_gue_med row
    row = meta[(meta['descriptor'].str.lower() == 'osi')
                  & (meta['ars_metric'] == 'ks_gue_med')]
    if not len(row):
        print("  ERROR: no OSI ↔ ks_gue_med row in Phase 24 meta")
        return
    row = row.iloc[0]
    rho = float(row['fixed_rho'])
    sig = float('nan')

    # Per-session sign consistency
    per_sess = pd.read_parquet(
        Path(ROOT_DIR) / 'data' / 'phase24_results'
        / 'per_session_h1_crossval.parquet')
    osi_ks = per_sess[(per_sess['descriptor'].str.lower() == 'osi')
                         & (per_sess['ars_metric'] == 'ks_gue_med')]
    sign_consistent = int((osi_ks['spearman_partial'] > 0).sum())
    n_sess = int(len(osi_ks))
    sign_frac = sign_consistent / max(n_sess, 1)
    print()
    print(f"  per-session sign consistency (positive rho): "
            f"{sign_consistent}/{n_sess} sessions ({sign_frac*100:.0f}%)")

    if rho > 0.2 and sign_frac >= 0.75:
        verdict = 'POSITIVE'
    elif rho > 0.1:
        verdict = 'ATTENUATED'
    else:
        verdict = 'NULL'

    result = dict(
        verdict=verdict,
        meta_aggregate_rho=rho,
        meta_aggregate_p=sig,
        n_sessions=n_sess,
        n_sessions_positive_sign=sign_consistent,
        sign_consistency_frac=sign_frac,
        note=("Phase 28 Analysis 2 uses Phase 24 (Full) results; the "
                "data is Allen Neuropixels electrophysiology, not 2P "
                "optical.  The verdict is read directly from Phase 24."),
    )
    with open(OUT_DIR / 'analysis2_verdict.json', 'w') as f:
        json.dump(result, f, indent=2)
    print()
    print(f"Aggregate verdict: {verdict}")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
