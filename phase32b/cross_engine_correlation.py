"""
phase32b/cross_engine_correlation.py — Phase 32b.

Cross-engine correlation analysis between the NNS engine's F1/F0 ↔
rep_med signal and the RF engine's p=7 enrichment signal, across
recordings (pvc-11) and sessions (Allen).  Tests whether the two
formally distinct engines are reading projections of one underlying
substrate-systematic axis (SHARED_AXIS) or independent substrate-
systematic axes that happen to share direction (INDEPENDENT_AXES).

Methodology:
  - For each pvc-11 recording (9 with gratings-derived F1/F0):
      per-recording F1/F0 ↔ rep_med score = Spearman(f1_f0_pref,
        rep_med) over units within that recording.
      per-recording p=7 score = full-recording p=7 z-score against
        rate-matched Poisson surrogate at q_max=200.
  - For each Allen session (6 with per-window p-adic):
      per-session F1/F0 ↔ rep_med score = Spearman(f1_f0_pref, rep_med)
        over units within that session (drifting_pooled condition).
      per-session p=7 score = mean per-window z(p=7) across the 5
        natural_movie_one windows.
  - Cross-engine correlation = within-substrate Spearman(F1/F0_score,
    p7_score) across recordings/sessions.

Verdict per the brief's three-reading framework:
  - SHARED_AXIS: |ρ| > 0.5 in both substrates → two engines reading
    one axis.
  - INDEPENDENT_AXES: |ρ| < 0.2 in both substrates → two independent
    axes that happen to share direction.
  - MIXED: strong in one substrate, weak in the other, or signs
    differ → substrate-specific shared-vs-independent structure.

Outputs:
  - data/phase32b_results/pvc11_per_recording_scores.parquet
  - data/phase32b_results/allen_per_session_scores.parquet
  - data/phase32b_results/cross_engine_verdict.json
  - data/phase32b_results/PHASE32B_FINDINGS.md (separate, written by hand)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'phase32b_results'
OUT.mkdir(parents=True, exist_ok=True)


def pvc11_per_recording_scores() -> pd.DataFrame:
    """For each pvc-11 recording, compute:
       - Spearman(f1_f0_pref, rep_med) across units (using
         h1_functional + h1_classifications joined on unit_id).
       - full-recording p=7 z-score (from pvc11_all_qmax200_per_prime
         parquet + monkey12/monkey3 gratings verdict JSONs).
    """
    func = pd.read_parquet(ROOT / 'data' / 'phase22a_results'
                           / 'h1_functional.parquet')
    cls = pd.read_parquet(ROOT / 'data' / 'phase22a_results'
                          / 'h1_classifications.parquet')

    # h1_functional only has the 9 stim-driven recordings (no
    # spontaneous since F1/F0 is computed against drifting stim).
    func = func[['recording', 'unit_id', 'f1_f0_pref', 'mean_rate']].copy()
    cls = cls[['recording', 'unit_id', 'rep_med', 'ks_gue_med']].copy()

    merged = func.merge(cls, on=['recording', 'unit_id'], how='inner')
    merged = merged.dropna(subset=['f1_f0_pref', 'rep_med'])

    # Per-recording Spearman
    rows = []
    for rec, grp in merged.groupby('recording'):
        if len(grp) < 5:
            continue
        rho, p = spearmanr(grp['f1_f0_pref'], grp['rep_med'])
        rows.append(dict(
            recording=rec,
            n_units=len(grp),
            f1f0_repmed_rho=float(rho),
            f1f0_repmed_p=float(p),
            f1f0_mean=float(grp['f1_f0_pref'].mean()),
            repmed_mean=float(grp['rep_med'].mean()),
        ))
    pvc_f1f0 = pd.DataFrame(rows)

    # Full-recording p=7 z-scores
    p7_rows = []
    main = pd.read_parquet(ROOT / 'data' / 'phase31b_results'
                           / 'pvc11_all_qmax200_per_prime.parquet')
    for _, r in main.iterrows():
        p7_rows.append(dict(recording=r['recording'],
                            p7_z=float(r['z_p7']),
                            p7_real=float(r['real_p7']),
                            n_events_p7=int(r['n_events']),
                            duration_p7=float(r['duration_sec'])))

    # Add 3 gratings recordings from verdict JSONs
    with open(ROOT / 'data' / 'phase31b_results'
              / 'monkey12_gratings_qmax200_verdict.json') as f:
        m12 = json.load(f)
    for r in m12['recordings']:
        p7_rows.append(dict(recording=r['recording'],
                            p7_z=float(r['per_prime_z']['7']),
                            p7_real=float(r['per_prime_real']['7']),
                            n_events_p7=int(r['n_events']),
                            duration_p7=float(r['total_dur'])))
    with open(ROOT / 'data' / 'phase31b_results'
              / 'monkey3_gratings_qmax200_verdict.json') as f:
        m3 = json.load(f)
    p7_rows.append(dict(recording=m3['recording'],
                        p7_z=float(m3['p7_z_score']),
                        p7_real=float(m3['real_p7_normalised_per_q']),
                        n_events_p7=int(m3['n_real_events']),
                        duration_p7=float(m3['total_duration_sec'])))
    pvc_p7 = pd.DataFrame(p7_rows)

    out = pvc_f1f0.merge(pvc_p7, on='recording', how='inner')
    return out


def allen_per_session_scores() -> pd.DataFrame:
    """For each Allen session, compute:
       - Spearman(f1_f0_pref, rep_med) across units (joining
         per_session_h1_functional + per_session_h1_ars).
       - mean per-window z(p=7) across the 5 natural_movie_one windows
         (only the 6 sessions with per-window p-adic).
    """
    func = pd.read_parquet(ROOT / 'data' / 'phase24_results'
                           / 'per_session_h1_functional.parquet')
    ars = pd.read_parquet(ROOT / 'data' / 'phase24_results'
                          / 'per_session_h1_ars.parquet')

    func = func[['session_id', 'unit_id', 'f1_f0_pref',
                 'mean_rate']].copy()
    ars = ars[['session_id', 'unit_id', 'rep_med', 'ks_gue_med',
               'condition']].copy()
    ars = ars[ars['condition'] == 'drifting_pooled']

    merged = func.merge(ars, on=['session_id', 'unit_id'], how='inner')
    merged = merged.dropna(subset=['f1_f0_pref', 'rep_med'])

    rows = []
    for sess, grp in merged.groupby('session_id'):
        if len(grp) < 5:
            continue
        rho, p = spearmanr(grp['f1_f0_pref'], grp['rep_med'])
        rows.append(dict(
            session_id=int(sess),
            n_units=len(grp),
            f1f0_repmed_rho=float(rho),
            f1f0_repmed_p=float(p),
            f1f0_mean=float(grp['f1_f0_pref'].mean()),
            repmed_mean=float(grp['rep_med'].mean()),
        ))
    allen_f1f0 = pd.DataFrame(rows)

    # Per-session per-window mean z(p=7) on natural_movie_one
    pw = pd.read_parquet(ROOT / 'data' / 'phase31b_results'
                         / 'allen_per_window_padic_combined.parquet')
    pw_nm = pw[pw['condition'] == 'natural_movie_one']
    p7_per_sess = pw_nm.groupby('session_id').agg(
        p7_window_mean_z=('z_p7', 'mean'),
        p7_window_frac_gt2=('z_p7', lambda s: (s > 2).mean()),
        p7_window_n=('z_p7', 'size'),
        cre_line=('cre_line', 'first'),
    ).reset_index()
    p7_per_sess['session_id'] = p7_per_sess['session_id'].astype(int)

    out = allen_f1f0.merge(p7_per_sess, on='session_id', how='inner')
    return out


def assign_verdict(pvc_rho: float, pvc_p: float,
                   allen_rho: float, allen_p: float,
                   thr_shared: float = 0.5,
                   thr_indep: float = 0.2) -> tuple[str, str]:
    pvc_strong = abs(pvc_rho) > thr_shared
    pvc_weak = abs(pvc_rho) < thr_indep
    allen_strong = abs(allen_rho) > thr_shared
    allen_weak = abs(allen_rho) < thr_indep

    if pvc_strong and allen_strong:
        return ('SHARED_AXIS',
                'Both substrates show strong cross-engine correlation '
                '(|ρ| > 0.5).  The two engines are reading projections '
                'of one underlying substrate-systematic axis.  Cross-'
                'engine agreement is one finding viewed two ways, not '
                'two independent findings.')
    if pvc_weak and allen_weak:
        return ('INDEPENDENT_AXES',
                'Both substrates show weak cross-engine correlation '
                '(|ρ| < 0.2).  The two engines are reading independent '
                'substrate-systematic axes that happen to share '
                'direction.  Cross-engine agreement is genuinely two '
                'findings, not one.')
    return ('MIXED',
            'Cross-engine correlation strength differs between '
            'substrates or signs disagree.  The shared-vs-independent '
            'question is substrate-specific.  Per-cell decomposition '
            'is the natural follow-up.')


def main():
    print("=" * 72)
    print("Phase 32b — cross-engine correlation: F1/F0 ↔ rep_med vs p=7")
    print("=" * 72)

    pvc = pvc11_per_recording_scores()
    allen = allen_per_session_scores()

    pvc.to_parquet(OUT / 'pvc11_per_recording_scores.parquet', index=False)
    allen.to_parquet(OUT / 'allen_per_session_scores.parquet', index=False)

    print("\nPVC-11 per-recording scores (9 recordings):")
    print(pvc[['recording', 'n_units', 'f1f0_repmed_rho',
               'f1f0_repmed_p', 'p7_z', 'p7_real']].to_string(index=False))

    print("\nAllen per-session scores (6 sessions with per-window p-adic):")
    print(allen[['session_id', 'cre_line', 'n_units', 'f1f0_repmed_rho',
                 'f1f0_repmed_p', 'p7_window_mean_z',
                 'p7_window_frac_gt2']].to_string(index=False))

    # Cross-engine Spearman within substrate
    pvc_rho, pvc_p = spearmanr(pvc['f1f0_repmed_rho'], pvc['p7_z'])
    allen_rho, allen_p = spearmanr(allen['f1f0_repmed_rho'],
                                   allen['p7_window_mean_z'])
    allen_rho_frac, allen_p_frac = spearmanr(
        allen['f1f0_repmed_rho'], allen['p7_window_frac_gt2'])

    print()
    print("=" * 72)
    print("CROSS-ENGINE SPEARMAN (within-substrate)")
    print("=" * 72)
    print(f"pvc-11   (n={len(pvc)} recordings): "
          f"ρ(F1/F0_rho, p7_z) = {pvc_rho:+.3f}  p = {pvc_p:.3f}")
    print(f"Allen    (n={len(allen)} sessions):  "
          f"ρ(F1/F0_rho, p7_window_mean_z) = {allen_rho:+.3f}  "
          f"p = {allen_p:.3f}")
    print(f"Allen    (n={len(allen)} sessions):  "
          f"ρ(F1/F0_rho, p7_window_frac>2) = {allen_rho_frac:+.3f}  "
          f"p = {allen_p_frac:.3f}")

    verdict, verdict_text = assign_verdict(pvc_rho, pvc_p,
                                           allen_rho, allen_p)
    print()
    print(f"VERDICT: {verdict}")
    print(f"  {verdict_text}")

    result = dict(
        method=dict(
            pvc11_n_recordings=int(len(pvc)),
            pvc11_F1F0_score='per-recording Spearman(f1_f0_pref, rep_med) '
                             'across units in h1_functional ∩ '
                             'h1_classifications',
            pvc11_p7_score='full-recording z(p=7) at q_max=200 vs '
                           'rate-matched Poisson (Phase 31b)',
            allen_n_sessions=int(len(allen)),
            allen_F1F0_score='per-session Spearman(f1_f0_pref, rep_med) '
                             'on drifting_pooled units in '
                             'per_session_h1_functional ∩ per_session_h1_ars',
            allen_p7_score='per-session mean z(p=7) across 5 '
                           'natural_movie_one windows at q_max=200',
            verdict_thresholds=dict(shared_axis='|ρ| > 0.5 in both',
                                    independent_axes='|ρ| < 0.2 in both',
                                    mixed='otherwise'),
        ),
        pvc11=dict(
            n=int(len(pvc)),
            cross_engine_rho=float(pvc_rho),
            cross_engine_p=float(pvc_p),
            per_recording=pvc[['recording', 'n_units',
                               'f1f0_repmed_rho', 'p7_z']
                              ].to_dict(orient='records'),
        ),
        allen=dict(
            n=int(len(allen)),
            cross_engine_rho_mean_z=float(allen_rho),
            cross_engine_p_mean_z=float(allen_p),
            cross_engine_rho_frac_gt2=float(allen_rho_frac),
            cross_engine_p_frac_gt2=float(allen_p_frac),
            per_session=allen[['session_id', 'cre_line', 'n_units',
                               'f1f0_repmed_rho',
                               'p7_window_mean_z', 'p7_window_frac_gt2']
                              ].to_dict(orient='records'),
        ),
        verdict=verdict,
        verdict_text=verdict_text,
    )

    with open(OUT / 'cross_engine_verdict.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)

    print()
    print("Outputs:")
    print(f"  {OUT}/pvc11_per_recording_scores.parquet")
    print(f"  {OUT}/allen_per_session_scores.parquet")
    print(f"  {OUT}/cross_engine_verdict.json")

    return result


if __name__ == '__main__':
    main()
