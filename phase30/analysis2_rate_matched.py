"""
phase30/analysis2_rate_matched.py — rate-matched within-σ verification
of the Phase 30 Analysis 2 RATE_REGIME_CONFOUNDED verdict.

Per user course-correction during Phase 30 writeup review: the
PHASE30_FINDINGS.md claim that "rate-matched within-σ analysis would
collapse the σ-axis variation to a Poisson-class regime regardless of
σ" was a prediction, not a measurement.  This script empirically
checks the prediction.

Method.  Analysis 2 already computed per-oscillator rate-matched
Poisson surrogates at every (K, σ) cell (stored in
`analysis2_per_oscillator_surrogate.parquet`, 12 600 rows = 42 cells ×
100 oscillators × 3 seeds).  Rate-matched Poisson by construction is
pure-rate-effect with zero dynamics — so per-(K, σ) surrogate modal
*is* the rate-driven classification.  Compare real vs surrogate
per-cell:
  - real_modal == surrogate_modal → cell is rate-driven (no
    dynamics signal beyond rate at the modal level).
  - real_modal != surrogate_modal → real cell has a dynamics signal
    that the rate-matched surrogate does not reproduce.

If the σ-axis variation is rate-confounded (as the verdict claims),
we expect: surrogate modal varies with σ in the same direction as
real modal.  If σ-axis variation has dynamics content beyond rate,
we expect: real differs from surrogate at some σ cells.

Output: data/phase30_results/analysis2_rate_match_check.parquet
        data/phase30_results/analysis2_rate_match_verdict.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'data' / 'phase30_results'


def main():
    print("=" * 72)
    print("Phase 30 — Analysis 2 rate-matched within-σ verification")
    print("=" * 72)

    real = pd.read_parquet(OUT_DIR / 'analysis2_per_oscillator_real.parquet')
    sur = pd.read_parquet(OUT_DIR / 'analysis2_per_oscillator_surrogate.parquet')
    print(f"  real per-oscillator rows: {len(real)}")
    print(f"  surrogate per-oscillator rows: {len(sur)}\n")

    # Modal classification per (K, σ) cell (pooled across seeds and oscillators)
    def modal_per_cell(df, label):
        rows = []
        for (K, sf), sub in df.groupby(['K_factor', 'sigma_factor']):
            well = sub[sub['primary'] != 'underpowered']
            n_well = len(well)
            n_total = len(sub)
            if n_well == 0:
                rows.append(dict(K_factor=K, sigma_factor=sf,
                                  modal=f'{label}_underpowered',
                                  ks_med=np.nan, rep_med=np.nan,
                                  n_well=0, n_total=int(n_total),
                                  frac_modal=np.nan,
                                  primary_counts={}))
                continue
            counts = well['primary'].value_counts()
            modal = str(counts.idxmax())
            ks_med = float(well['ks_gue_med'].median())
            rep_med = float(well['rep_med'].median())
            rows.append(dict(
                K_factor=float(K), sigma_factor=float(sf),
                modal=modal, ks_med=ks_med, rep_med=rep_med,
                n_well=int(n_well), n_total=int(n_total),
                frac_modal=float(counts.max() / n_well),
                primary_counts=dict(counts.head(4)),
            ))
        return pd.DataFrame(rows)

    real_modal = modal_per_cell(real, 'real')
    sur_modal = modal_per_cell(sur, 'sur')

    merged = real_modal.merge(
        sur_modal, on=['K_factor', 'sigma_factor'],
        suffixes=('_real', '_sur'),
    )
    merged['modal_agreement'] = merged['modal_real'] == merged['modal_sur']
    merged['delta_ks'] = merged['ks_med_real'] - merged['ks_med_sur']
    merged['delta_rep'] = merged['rep_med_real'] - merged['rep_med_sur']

    print("Per-(K, σ) modal: real vs rate-matched Poisson surrogate")
    print()
    print("real modal:")
    print(merged.pivot(index='sigma_factor', columns='K_factor', values='modal_real').to_string())
    print()
    print("surrogate modal:")
    print(merged.pivot(index='sigma_factor', columns='K_factor', values='modal_sur').to_string())
    print()
    print("modal_agreement (True = surrogate reproduces real modal at this cell):")
    print(merged.pivot(index='sigma_factor', columns='K_factor', values='modal_agreement').to_string())
    print()
    print("Δks_med (real − surrogate):")
    pivot_dks = merged.pivot(index='sigma_factor', columns='K_factor', values='delta_ks')
    print(pivot_dks.round(3).to_string())
    print()
    print("Δrep_med (real − surrogate):")
    pivot_drep = merged.pivot(index='sigma_factor', columns='K_factor', values='delta_rep')
    print(pivot_drep.round(3).to_string())

    # Verdict on the rate-confound claim
    n_total = len(merged)
    n_agree = int(merged['modal_agreement'].sum())
    n_disagree = n_total - n_agree
    frac_agree = n_agree / n_total

    # Per-σ agreement breakdown
    print()
    print("Agreement by σ_factor:")
    for sf, sub in merged.groupby('sigma_factor'):
        n_sub_agree = int(sub['modal_agreement'].sum())
        modal_real_top = sub['modal_real'].value_counts().idxmax()
        modal_sur_top = sub['modal_sur'].value_counts().idxmax()
        print(f"  σ={sf:.1f}*ω₀  real={modal_real_top:13s}  "
              f"sur={modal_sur_top:13s}  agree={n_sub_agree}/{len(sub)}  "
              f"mean Δks={sub['delta_ks'].mean():+.3f}  "
              f"mean Δrep={sub['delta_rep'].mean():+.3f}")

    # Verdict: rate-confound claim is supported if the per-σ surrogate modal
    # tracks the real modal across the σ-axis.  Specifically — agreement >=
    # 80 % of cells.  If <50 %, real has dynamics signal beyond rate.
    if frac_agree >= 0.80:
        verdict = 'RATE_CONFOUND_CONFIRMED'
    elif frac_agree >= 0.50:
        verdict = 'PARTIAL_RATE_CONFOUND'
    else:
        verdict = 'DYNAMICS_BEYOND_RATE'

    summary = dict(
        verdict=verdict,
        n_cells=int(n_total),
        n_modal_agree=n_agree,
        n_modal_disagree=n_disagree,
        frac_modal_agree=float(frac_agree),
        mean_delta_ks=float(merged['delta_ks'].mean()),
        mean_delta_rep=float(merged['delta_rep'].mean()),
        max_abs_delta_ks=float(merged['delta_ks'].abs().max()),
        max_abs_delta_rep=float(merged['delta_rep'].abs().max()),
    )
    out_csv = OUT_DIR / 'analysis2_rate_match_check.parquet'
    merged_save = merged.copy()
    # Drop the dict column for parquet
    merged_save = merged_save.drop(columns=['primary_counts_real',
                                              'primary_counts_sur'],
                                     errors='ignore')
    merged_save.to_parquet(out_csv, index=False)
    print(f"\n  → {out_csv}")

    with open(OUT_DIR / 'analysis2_rate_match_verdict.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  → analysis2_rate_match_verdict.json")
    print(f"\nVERDICT: {verdict}")
    print(f"  modal-agreement = {n_agree}/{n_total} cells ({frac_agree:.1%})")
    print(f"  mean Δks (real − sur) = {summary['mean_delta_ks']:+.3f}  "
          f"max |Δks| = {summary['max_abs_delta_ks']:.3f}")
    print(f"  mean Δrep (real − sur) = {summary['mean_delta_rep']:+.3f}  "
          f"max |Δrep| = {summary['max_abs_delta_rep']:.3f}")


if __name__ == '__main__':
    main()
