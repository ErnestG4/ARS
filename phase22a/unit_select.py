"""
phase22a/unit_select.py — unit selection for Phase 22a.

Two selection regimes:

  H1-strict (per-unit ARS classification):
    Per-cell semantics matter; multi-units are mixtures and excluded.
    SNR ≥ SNR_H1, mean rate ≥ FR_H1, and total spike count per condition
    ≥ N_SPIKES_H1.  N_SPIKES_H1 is set to the canonical N_POINTS=400
    used by the Phase 19/20.5 distinctness machinery — fewer events
    leave joint_q_profile underpowered at q_max=30.

  H2-permissive (population-event analysis):
    Joint structure is the question, not per-cell semantics; multi-units
    can be retained.  Looser SNR + rate threshold; sensitivity to
    multi-unit inclusion run separately downstream.

The pvc-11 source code's canonical thresholds were:
    spontaneous (Williamson 2016 noise-corr example): SNR ≥ 2.75
    gratings (Cowley 2016):                            SNR ≥ 1.5
    movies (Cowley 2016):                              SNR ≥ 2.0
    firing rate floor:                                 ≥ 1.0 sp/s

Phase 22a chooses SNR ≥ 2.0 across all subsets for H1 (the movie-
subset convention; permissive enough to retain ~70-100 units per
array, strict enough to exclude marginal sortings) and ≥ 1.5 for H2.
The N_SPIKES_H1 ≥ 400 floor is the binding constraint at low rates.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from loader import (
    Recording, load, list_all_recordings, GRATING_TRIAL_SEC, MOVIE_TRIAL_SEC,
)


# Thresholds
SNR_H1 = 2.0
SNR_H2 = 1.5
FR_H1 = 1.0       # sp/s
FR_H2 = 0.5       # sp/s — population events care about coactivation, not solo rate
N_SPIKES_H1 = 400 # minimum total spikes per (unit, condition) for H1 ARS

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class UnitSelection:
    recording: str
    unit_idx: int
    unit_id: str
    snr: float
    n_spikes_total: int
    mean_rate: float
    h1_pass: bool
    h2_pass: bool
    h1_reason: str = ''
    h2_reason: str = ''


def select(rec: Recording) -> list[UnitSelection]:
    """Apply both H1 and H2 selection criteria to all units in a recording."""
    n_spk = rec.n_spikes_per_unit()
    rate = rec.mean_rate_per_unit()
    out: list[UnitSelection] = []
    for u in range(rec.n_units):
        snr_u = float(rec.snr[u])
        n_u = int(n_spk[u])
        r_u = float(rate[u])
        h1_pass = (snr_u >= SNR_H1) and (r_u >= FR_H1) and (n_u >= N_SPIKES_H1)
        h1_reason_parts = []
        if snr_u < SNR_H1: h1_reason_parts.append(f'SNR={snr_u:.2f}<{SNR_H1}')
        if r_u < FR_H1: h1_reason_parts.append(f'FR={r_u:.2f}<{FR_H1}')
        if n_u < N_SPIKES_H1: h1_reason_parts.append(f'n={n_u}<{N_SPIKES_H1}')
        h2_pass = (snr_u >= SNR_H2) and (r_u >= FR_H2)
        h2_reason_parts = []
        if snr_u < SNR_H2: h2_reason_parts.append(f'SNR={snr_u:.2f}<{SNR_H2}')
        if r_u < FR_H2: h2_reason_parts.append(f'FR={r_u:.2f}<{FR_H2}')
        out.append(UnitSelection(
            recording=rec.name, unit_idx=u, unit_id=rec.unit_id(u),
            snr=snr_u, n_spikes_total=n_u, mean_rate=r_u,
            h1_pass=h1_pass, h2_pass=h2_pass,
            h1_reason=','.join(h1_reason_parts) if h1_reason_parts else 'pass',
            h2_reason=','.join(h2_reason_parts) if h2_reason_parts else 'pass',
        ))
    return out


def build_master_table() -> pd.DataFrame:
    """Apply selection to every recording, return a master selection table."""
    rows = []
    for name in list_all_recordings():
        rec = load(name)
        for sel in select(rec):
            rows.append(dict(
                recording=sel.recording,
                subset=rec.subset,
                monkey=rec.monkey,
                unit_idx=sel.unit_idx, unit_id=sel.unit_id,
                snr=sel.snr, n_spikes_total=sel.n_spikes_total,
                mean_rate=sel.mean_rate,
                h1_pass=sel.h1_pass, h2_pass=sel.h2_pass,
                h1_reason=sel.h1_reason, h2_reason=sel.h2_reason,
            ))
    return pd.DataFrame(rows)


def main():
    print("=" * 72)
    print("Phase 22a Unit Selection")
    print("=" * 72)
    print(f"H1: SNR≥{SNR_H1}, FR≥{FR_H1}/s, n_spikes_total≥{N_SPIKES_H1}")
    print(f"H2: SNR≥{SNR_H2}, FR≥{FR_H2}/s")
    print()

    df = build_master_table()
    out = OUT_DIR / 'unit_selection.parquet'
    df.to_parquet(out, index=False)
    print(f"  → {out}  ({len(df)} units total)")

    print()
    print(f"{'recording':35s}  {'units':>5s}  {'h1':>5s}  {'h2':>5s}  "
          f"{'h1_kept':>8s}  {'h2_kept':>8s}")
    for rec, g in df.groupby('recording', sort=False):
        n = len(g)
        h1 = int(g['h1_pass'].sum())
        h2 = int(g['h2_pass'].sum())
        print(f"  {rec:35s}  {n:5d}  {h1:5d}  {h2:5d}  "
              f"{h1/n*100:6.1f}%  {h2/n*100:6.1f}%")
    print()
    print(f"Total: {len(df)} (unit, recording) pairs; "
          f"H1: {int(df['h1_pass'].sum())} pass; "
          f"H2: {int(df['h2_pass'].sum())} pass")


if __name__ == '__main__':
    main()
