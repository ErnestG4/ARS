"""
phase32a/extract_natural_movie_comparison.py — Phase 32a.

Extracts the load-bearing missing comparator flagged in
EPISTEMIC_STATE.md: pvc-11 anesthetised macaque V1 natural-movie
per-window p-adic at q_max=200, side-by-side with Allen awake mouse V1
natural_movie_one per-window p-adic at q_max=200.

The Phase 31b sweep already wrote pvc-11 per-window p-adic at q_max=200
for all 15 recordings to `pvc11_per_window_padic_all.parquet`, and
Allen per-window p-adic for 6 sessions x 3 conditions x 5 windows to
`allen_per_window_padic_combined.parquet`.  Both pipelines use:
N_WINDOWS=5, N_SEEDS=5, Q_MAX=200, PRIMES=(2,3,5,7,11,13), and the same
rate-matched Poisson surrogate.  This script reads those parquets,
filters to the cells that disambiguate the substrate-vs-state confound
documented in EPISTEMIC_STATE.md, and produces the comparison table
and verdict that fills the 2x2 grid.

No new compute: this is an extraction + comparison pass over already-
computed Round 4 outputs.

Outputs to `data/phase32a_results/`:
  - natural_movie_per_window_padic_comparison.parquet
  - natural_movie_per_window_padic_verdict.json
  - PHASE32A_FINDINGS.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PVC_PATH = ROOT / 'data' / 'phase31b_results' / 'pvc11_per_window_padic_all.parquet'
ALLEN_PATH = ROOT / 'data' / 'phase31b_results' / 'allen_per_window_padic_combined.parquet'
OUT = ROOT / 'data' / 'phase32a_results'

PRIMES = (2, 3, 5, 7, 11, 13)


def stationarity_verdict(z_values: np.ndarray) -> str:
    """Same convention as Phase 31b pvc11 verdict file."""
    n_z_gt_2 = int((z_values > 2.0).sum())
    n_total = int(z_values.size)
    if n_total == 0:
        return 'NO_DATA'
    if n_z_gt_2 >= 4:
        return 'PER_WINDOW_STATIONARY'
    if n_z_gt_2 >= 2:
        return 'PER_WINDOW_MIXTURE'
    if n_z_gt_2 == 1:
        return 'PER_WINDOW_RARE'
    return 'PER_WINDOW_NULL'


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    pvc = pd.read_parquet(PVC_PATH)
    allen = pd.read_parquet(ALLEN_PATH)

    # === PVC-11 natural-movie recordings ===
    pvc_nm = pvc[pvc.recording.isin(['monkey1_natural_movie',
                                     'monkey2_natural_movie'])].copy()
    pvc_gm = pvc[pvc.recording.isin(['monkey1_gratings_movie',
                                     'monkey2_gratings_movie'])].copy()
    pvc_no = pvc[pvc.recording.isin(['monkey1_noise_movie',
                                     'monkey2_noise_movie'])].copy()

    # === Allen natural_movie_one ===
    allen_nm = allen[allen.condition == 'natural_movie_one'].copy()

    # === Per-prime per-recording verdicts ===
    rows = []

    def collect_pvc(df, group_name):
        for rec, grp in df.groupby('recording'):
            grp = grp.sort_values('window_idx')
            row = dict(
                substrate='pvc11_anesthetised_macaque',
                group=group_name,
                identifier=rec,
                n_windows=len(grp),
                mean_n_events=float(grp['n_events'].mean()),
            )
            for p in PRIMES:
                zs = grp[f'z_p{p}'].values
                reals = grp[f'real_p{p}'].values
                row[f'mean_z_p{p}'] = float(zs.mean())
                row[f'frac_z_gt_2_p{p}'] = float((zs > 2.0).mean())
                row[f'n_z_gt_2_p{p}'] = int((zs > 2.0).sum())
                row[f'frac_above_1p5_p{p}'] = float((reals > 1.5).mean())
                row[f'verdict_p{p}'] = stationarity_verdict(zs)
            rows.append(row)

    def collect_allen(df, group_name):
        # one row per (session_id, cre_line)
        for (sess, cre), grp in df.groupby(['session_id', 'cre_line']):
            grp = grp.sort_values('window_idx')
            row = dict(
                substrate='allen_awake_mouse',
                group=group_name,
                identifier=f'{sess}_{cre}',
                n_windows=len(grp),
                mean_n_events=float(grp['n_events'].mean()),
            )
            for p in PRIMES:
                zs = grp[f'z_p{p}'].values
                reals = grp[f'real_p{p}'].values
                row[f'mean_z_p{p}'] = float(zs.mean())
                row[f'frac_z_gt_2_p{p}'] = float((zs > 2.0).mean())
                row[f'n_z_gt_2_p{p}'] = int((zs > 2.0).sum())
                row[f'frac_above_1p5_p{p}'] = float((reals > 1.5).mean())
                row[f'verdict_p{p}'] = stationarity_verdict(zs)
            rows.append(row)

    collect_pvc(pvc_nm, 'pvc11_natural_movie')
    collect_pvc(pvc_gm, 'pvc11_gratings_movie')
    collect_pvc(pvc_no, 'pvc11_noise_movie')
    collect_allen(allen_nm, 'allen_natural_movie_one')

    comp = pd.DataFrame(rows)
    comp.to_parquet(OUT / 'natural_movie_per_window_padic_comparison.parquet',
                    index=False)

    # === Aggregate verdict for the load-bearing cell ===
    # Primary comparison: pvc11_natural_movie p=7 vs allen_natural_movie_one p=7
    pvc_nm_p7_zs = np.concatenate([
        pvc_nm[pvc_nm.recording == r]['z_p7'].values
        for r in pvc_nm.recording.unique()
    ])
    allen_nm_p7_zs = allen_nm['z_p7'].values

    pvc_nm_p7_mean_z = float(pvc_nm_p7_zs.mean())
    pvc_nm_p7_frac_gt2 = float((pvc_nm_p7_zs > 2.0).mean())
    allen_nm_p7_mean_z = float(allen_nm_p7_zs.mean())
    allen_nm_p7_frac_gt2 = float((allen_nm_p7_zs > 2.0).mean())

    # Per-Cre-line means for Allen
    allen_per_cre_p7 = {}
    for cre, grp in allen_nm.groupby('cre_line'):
        zs = grp['z_p7'].values
        allen_per_cre_p7[str(cre)] = dict(
            mean_z=float(zs.mean()),
            n_windows=int(zs.size),
            n_z_gt_2=int((zs > 2.0).sum()),
            frac_z_gt_2=float((zs > 2.0).mean()),
        )

    # Verdict per the brief's three-reading framework
    def assign_verdict(pvc_mean_z, pvc_frac_gt2,
                       allen_mean_z, allen_frac_gt2):
        pvc_present = (pvc_mean_z > 1.5) and (pvc_frac_gt2 >= 0.4)
        allen_present = (allen_mean_z > 1.5) and (allen_frac_gt2 >= 0.4)
        if pvc_present and allen_present:
            return ('PER_WINDOW_STATE_CONSISTENT',
                    'Both anesthetised-macaque and awake-mouse natural-movie '
                    'produce per-window p=7 enrichment; the substrate-vs-'
                    'state confound resolves toward natural-movie viewing as '
                    'the load-bearing axis.')
        if (not pvc_present) and allen_present:
            return ('PER_WINDOW_SUBSTRATE_CONSISTENT',
                    'Anesthetised-macaque natural-movie does NOT produce '
                    'per-window p=7 while awake-mouse natural-movie does; the '
                    'substrate-vs-state confound resolves toward substrate or '
                    'state (anesthetised macaque vs awake mouse), not the '
                    'natural-movie stimulus itself.')
        if pvc_present and (not allen_present):
            return ('PER_WINDOW_PVC11_UNEXPECTED',
                    'Anesthetised-macaque natural-movie produces per-window '
                    'p=7 while awake-mouse does not — inverts the prior '
                    'asymmetry direction.')
        return ('PER_WINDOW_BOTH_NULL',
                'Neither substrate produces per-window p=7 in natural-movie '
                'recordings — the Allen-positive result needs re-examination.')

    verdict_code, verdict_text = assign_verdict(
        pvc_nm_p7_mean_z, pvc_nm_p7_frac_gt2,
        allen_nm_p7_mean_z, allen_nm_p7_frac_gt2,
    )

    verdict = dict(
        protocol=dict(
            n_windows=5,
            n_seeds=5,
            q_max=200,
            primes=list(PRIMES),
            surrogate='rate_matched_uniform_poisson',
            engine='padic_amplitude_v4 / RF amplitude axis',
            source_parquets=dict(
                pvc11='data/phase31b_results/pvc11_per_window_padic_all.parquet',
                allen='data/phase31b_results/allen_per_window_padic_combined.parquet',
            ),
        ),
        primary_cell=dict(
            pvc11_natural_movie_p7=dict(
                recordings=['monkey1_natural_movie', 'monkey2_natural_movie'],
                n_total_windows=int(pvc_nm_p7_zs.size),
                mean_z=pvc_nm_p7_mean_z,
                n_z_gt_2=int((pvc_nm_p7_zs > 2.0).sum()),
                frac_z_gt_2=pvc_nm_p7_frac_gt2,
                z_values=pvc_nm_p7_zs.tolist(),
            ),
            allen_natural_movie_one_p7=dict(
                sessions=sorted(allen_nm.session_id.unique().tolist()),
                cre_lines=sorted(allen_nm.cre_line.unique().tolist()),
                n_total_windows=int(allen_nm_p7_zs.size),
                mean_z=allen_nm_p7_mean_z,
                n_z_gt_2=int((allen_nm_p7_zs > 2.0).sum()),
                frac_z_gt_2=allen_nm_p7_frac_gt2,
                per_cre_line=allen_per_cre_p7,
            ),
        ),
        verdict=verdict_code,
        verdict_text=verdict_text,
    )

    with open(OUT / 'natural_movie_per_window_padic_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)

    print("=" * 72)
    print("Phase 32a — pvc-11 natural-movie per-window p-adic comparison")
    print("=" * 72)
    print()
    print(f"PROTOCOL: 5 windows, 5 seeds, q_max=200, rate-matched Poisson")
    print(f"  identical to Phase 31b Round 4 sweep (no new compute)")
    print()
    print(f"PVC-11 natural-movie p=7 (anesthetised macaque V1):")
    print(f"  recordings: monkey1_natural_movie + monkey2_natural_movie")
    print(f"  n_windows = {pvc_nm_p7_zs.size} (5 per recording x 2)")
    print(f"  mean window-z = {pvc_nm_p7_mean_z:+.3f}")
    print(f"  frac windows z>2 = {pvc_nm_p7_frac_gt2:.2f} "
          f"({(pvc_nm_p7_zs > 2.0).sum()}/{pvc_nm_p7_zs.size})")
    print()
    print(f"Allen natural_movie_one p=7 (awake mouse V1):")
    print(f"  sessions = {len(allen_nm.session_id.unique())}, "
          f"Cre lines = {sorted(allen_nm.cre_line.unique())}")
    print(f"  n_windows = {allen_nm_p7_zs.size}")
    print(f"  mean window-z = {allen_nm_p7_mean_z:+.3f}")
    print(f"  frac windows z>2 = {allen_nm_p7_frac_gt2:.2f} "
          f"({(allen_nm_p7_zs > 2.0).sum()}/{allen_nm_p7_zs.size})")
    print()
    print("Per-Cre-line Allen p=7 (replicates the Phase 31b cross-Cre-line discipline):")
    for cre, d in allen_per_cre_p7.items():
        print(f"  {cre:6s}: mean_z={d['mean_z']:+.3f}  z>2 in "
              f"{d['n_z_gt_2']}/{d['n_windows']} windows  "
              f"frac={d['frac_z_gt_2']:.2f}")
    print()
    print(f"VERDICT: {verdict_code}")
    print(f"  {verdict_text}")
    print()
    print("Outputs:")
    print(f"  {OUT}/natural_movie_per_window_padic_comparison.parquet")
    print(f"  {OUT}/natural_movie_per_window_padic_verdict.json")

    return verdict, comp


if __name__ == '__main__':
    main()
