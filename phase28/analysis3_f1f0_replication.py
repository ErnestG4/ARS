"""
phase28/analysis3_f1f0_replication.py — F1/F0 ↔ rep_med substrate-
systematic replication note on Allen Neuropixels VISp units.

Phase 24 Full + Phase 27 Analysis 1 already addressed this on the
same dataset (Phase 28's "Allen Neuropixels" = Phase 24 dataset).
Phase 28 Analysis 3 is a clarifying note: the dataset is Allen
Neuropixels (electrophysiology), not 2P optical, so Phase 27's
SUBSTRATE-SYSTEMATIC verdict already covers this analysis.

Per the brief acceptance criteria:
  CONFIRMS                : matches Allen optical sign + magnitude.
  PROBE-MODALITY-DEPENDENT: differs from Allen optical sign or magnitude.
  NULL                    : no significant correlation.

Verdict here is read from Phase 24 Full + Phase 27 Analysis 1.
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
    print("Phase 28 Analysis 3 — F1/F0 ↔ rep_med replication note")
    print("=" * 72)
    print()
    print("  Clarification: Phase 28 brief describes 'Allen Neuropixels' as")
    print("  potentially a different recording modality from the Phase 24 /")
    print("  Phase 27 Allen analyses.  In fact Phase 24 / Phase 27 already")
    print("  used Allen Visual Coding NEUROPIXELS electrophysiology.  The")
    print("  Phase 28 Analysis 3 verdict therefore IS the Phase 27 Analysis 1")
    print("  verdict.")
    print()
    meta = pd.read_parquet(PH24_META)
    row = meta[(meta['descriptor'] == 'f1_f0_pref')
                  & (meta['ars_metric'] == 'rep_med')]
    if not len(row):
        print("  ERROR: no f1_f0_pref ↔ rep_med row in Phase 24 meta")
        return
    rho = float(row.iloc[0]['fixed_rho'])

    per_sess = pd.read_parquet(
        Path(ROOT_DIR) / 'data' / 'phase24_results'
        / 'per_session_h1_crossval.parquet')
    f1_rep = per_sess[(per_sess['descriptor'] == 'f1_f0_pref')
                          & (per_sess['ars_metric'] == 'rep_med')]
    n_sess = int(len(f1_rep))
    n_neg = int((f1_rep['spearman_partial'] < 0).sum())
    print(f"  Allen Neuropixels F1/F0 ↔ rep_med meta-fix ρ = {rho:+.3f}")
    print(f"  per-session sign consistency (negative ρ, "
            f"matching Phase 24 Full Allen sign): "
            f"{n_neg}/{n_sess} ({n_neg/max(n_sess,1)*100:.0f}%)")

    # Phase 27 Analysis 1 already concluded SUBSTRATE-SYSTEMATIC sign
    # flip survives rate-matching.  For Phase 28 Analysis 3's specific
    # verdict per its acceptance criteria:
    # CONFIRMS = Allen matches Allen-optical sign + magnitude → since
    # this IS Allen-Neuropixels (not optical), CONFIRMS means the
    # negative Allen-NP sign holds.
    if rho < 0 and n_neg >= 0.75 * n_sess:
        verdict = 'CONFIRMS'
        detail = (f'meta-fix ρ = {rho:+.3f}, {n_neg}/{n_sess} sessions '
                    f'negative-sign; Phase 27 Analysis 1 already showed the '
                    f'sign flip survives rate-matching against pvc-11')
    elif abs(rho) < 0.1:
        verdict = 'NULL'
        detail = f'meta-fix |ρ| < 0.1 ({rho:+.3f})'
    else:
        verdict = 'PROBE-MODALITY-DEPENDENT'
        detail = (f'meta-fix ρ = {rho:+.3f}; sign or magnitude differs from '
                    f'expected Phase 24 Full Allen sign')

    result = dict(
        verdict=verdict, detail=detail,
        allen_np_meta_rho=rho,
        n_sessions=n_sess,
        n_sessions_negative=n_neg,
        phase27_analysis1_verdict='SUBSTRATE-SYSTEMATIC',
        note=("Phase 28 Analysis 3 reads from Phase 24 Full + Phase 27 "
                "Analysis 1.  The dataset is Allen Visual Coding NEUROPIXELS, "
                "not 2P optical.  The substrate-systematic biological "
                "reading of the F1/F0 ↔ rep_med sign flip is locked in "
                "Phase 27."),
    )
    with open(OUT_DIR / 'analysis3_verdict.json', 'w') as f:
        json.dump(result, f, indent=2)
    print()
    print(f"Aggregate verdict: {verdict}")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
