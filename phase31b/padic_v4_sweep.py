"""
phase31b/padic_v4_sweep.py — apply padic_amplitude_v4 to cached
rf_amp_per_q arrays from Phase 22a/24/27/30 parquets.

The v4 p-adic engine sums RF amplitudes over q ∈ {p, p², p³, …} per
prime p and normalises against a noise floor.  The deployed
joint_q_profile already stores per-q RF amplitudes in every Phase
22a/24/27/30 parquet (column `rf_amp_per_q`, length 30 per
recording).  Applying v4 to those cached arrays is a one-pass
downstream operation — no re-classification needed.

Per recording, compute:
  - p_amplitude(p) = Σ_{q ∈ p-powers ≤ 30}  |a_q|
  - sum-normalised:        p_amplitude(p) / Σ_q |a_q|
  - per-q-power normalised: mean_{q ∈ p-powers} |a_q| / mean_{all q} |a_q|
  - dominant_prime_per_q  = arg-max of per-q-power normalised metric
  - confidence            = max(normalised_per_q)  (the discrimination
                            threshold is 1.5×; > 1.5 means clean
                            dominance, ≤ 1.5 means no signal)

Apply to surrogate parquets in parallel (Phase 22a h2_surrogate_*,
Phase 24 per_session_h2_surrogate_default) as a null check: do
rate-matched-Poisson surrogates show prime dominance, or is that
specifically a real-data signal?

Outputs:
  data/phase31b_results/padic_v4_pvc11.parquet
  data/phase31b_results/padic_v4_allen.parquet
  data/phase31b_results/padic_v4_phase27_clusters.parquet
  data/phase31b_results/padic_v4_pvc11_surrogates.parquet
  data/phase31b_results/padic_v4_allen_surrogates.parquet
  data/phase31b_results/padic_v4_kuramoto_a1.parquet  (Phase 30 A1
                                                       aggregate)
  data/phase31b_results/padic_v4_summary.json
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
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRIMES = (2, 3, 5, 7, 11, 13)
Q_MAX = 30
CONF_THRESHOLD = 1.5

# Cached arrays are stored as Python lists of length 30 per parquet row.


def _pure_power_bands(p: int, q_max: int = Q_MAX) -> list[int]:
    """Pure powers of p within [1, q_max]."""
    out = []
    q = p
    while q <= q_max:
        out.append(q)
        q *= p
    return out


def padic_v4_from_amps(amps: np.ndarray, primes=PRIMES,
                        q_max: int = Q_MAX) -> dict:
    """Apply v4 metric to a pre-computed |a_q| array of length q_max.

    Returns dict with per-prime amplitudes, dominant_prime_per_q, and
    confidence (= max per-q-power-normalised ratio).
    """
    amps = np.asarray(amps, dtype=np.float64)
    if amps.size != q_max or np.all(~np.isfinite(amps)):
        return dict(dominant_prime_per_q=0, confidence=np.nan,
                     per_prime={int(p): dict(amplitude=np.nan,
                                              normalised=np.nan,
                                              normalised_per_q=np.nan)
                                 for p in primes})
    # Total power excluding the DC (q=1) RF amplitude
    total_power = float(np.nansum(amps[1:])) + 1e-12
    mean_amp_all = float(np.nanmean(amps[1:])) + 1e-12

    per_prime = {}
    dom_per_q = (0, -1.0)
    dom_sum = (0, -1.0)
    for p in primes:
        bands = _pure_power_bands(p, q_max)
        if not bands:
            per_prime[int(p)] = dict(amplitude=0.0, normalised=0.0,
                                       normalised_per_q=0.0,
                                       n_bands=0, q_powers=[])
            continue
        amp_sum = float(np.nansum([amps[q - 1] for q in bands]))
        mean_p = amp_sum / len(bands)
        normed_sum = amp_sum / total_power
        normed_per_q = mean_p / mean_amp_all
        per_prime[int(p)] = dict(
            amplitude=amp_sum, normalised=normed_sum,
            normalised_per_q=normed_per_q,
            n_bands=len(bands), q_powers=bands,
        )
        if normed_per_q > dom_per_q[1]:
            dom_per_q = (int(p), normed_per_q)
        if normed_sum > dom_sum[1]:
            dom_sum = (int(p), normed_sum)
    return dict(
        dominant_prime_per_q=int(dom_per_q[0]),
        confidence=float(dom_per_q[1]),
        dominant_prime_sum=int(dom_sum[0]),
        confidence_sum=float(dom_sum[1]),
        per_prime=per_prime,
        mean_amplitude_all=mean_amp_all,
        total_power=total_power,
    )


def sweep_parquet(parquet_path: Path, label: str,
                    rf_col: str = 'rf_amp_per_q',
                    label_cols: list = None) -> pd.DataFrame:
    """Apply v4 to every row of a parquet, return summary DataFrame.

    label_cols: list of input-row columns to copy through to output
                (e.g., ['recording', 'subset'] for pvc-11)
    """
    if not parquet_path.exists():
        print(f"  [skip] {parquet_path} not found")
        return pd.DataFrame()
    df = pd.read_parquet(parquet_path)
    if rf_col not in df.columns:
        print(f"  [skip] {parquet_path}: no '{rf_col}' column")
        return pd.DataFrame()
    rows = []
    label_cols = label_cols or []
    for _, r in df.iterrows():
        amps = r[rf_col]
        if amps is None:
            continue
        try:
            amps_arr = np.asarray(amps, dtype=np.float64)
        except Exception:
            continue
        if amps_arr.size != Q_MAX:
            continue
        v4 = padic_v4_from_amps(amps_arr)
        out_row = {col: r[col] for col in label_cols if col in r}
        out_row.update(dict(
            source_parquet=label,
            dominant_prime_per_q=v4['dominant_prime_per_q'],
            confidence=v4['confidence'],
            dominant_prime_sum=v4['dominant_prime_sum'],
            confidence_sum=v4['confidence_sum'],
            above_threshold=bool(v4['confidence'] >= CONF_THRESHOLD),
            primary_modal=r.get('primary', None),
            n_events=int(r.get('n_events', 0)),
        ))
        for p in PRIMES:
            out_row[f'normed_per_q_p{p}'] = v4['per_prime'][int(p)]['normalised_per_q']
            out_row[f'normed_sum_p{p}'] = v4['per_prime'][int(p)]['normalised']
        rows.append(out_row)
    return pd.DataFrame(rows)


def main():
    print("=" * 72)
    print("Phase 31b — p-adic v4 sweep over existing parquets")
    print("=" * 72)
    summary = {'sweeps': []}

    # ─── Phase 22a pvc-11 (real population aggregates) ───
    p22a = Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'h2_population_classifications.parquet'
    df22a = sweep_parquet(p22a, 'phase22a_pvc11_real',
                            label_cols=['recording', 'subset', 'monkey', 'q_max'])
    df22a = df22a[df22a.get('q_max', 30) == 30] if 'q_max' in df22a.columns else df22a
    if len(df22a):
        df22a.to_parquet(OUT_DIR / 'padic_v4_pvc11.parquet', index=False)
        print(f"\n  pvc-11 real (Phase 22a):  {len(df22a)} recordings")
        print(df22a[['recording', 'subset', 'primary_modal',
                       'dominant_prime_per_q', 'confidence',
                       'above_threshold']].to_string(index=False))
        summary['sweeps'].append(dict(
            label='phase22a_pvc11_real', n=int(len(df22a)),
            n_above_threshold=int(df22a['above_threshold'].sum()),
            modal_prime=int(df22a['dominant_prime_per_q'].mode()[0])
                if len(df22a) else 0,
        ))

    # ─── Phase 22a pvc-11 surrogates (null) ───
    p22a_sur = Path(ROOT_DIR) / 'data' / 'phase22a_results' / 'h2_surrogate_classifications.parquet'
    df22a_sur = sweep_parquet(p22a_sur, 'phase22a_pvc11_surrogate',
                                label_cols=['recording', 'subset',
                                              'surrogate', 'seed', 'q_max'])
    if len(df22a_sur):
        # Filter to default q_max=30 if column exists
        if 'q_max' in df22a_sur.columns:
            df22a_sur = df22a_sur[df22a_sur['q_max'] == 30]
        df22a_sur.to_parquet(OUT_DIR / 'padic_v4_pvc11_surrogates.parquet', index=False)
        print(f"\n  pvc-11 surrogates:  {len(df22a_sur)} (recording × surrogate × seed)")
        print(f"  Above-threshold fraction by surrogate type:")
        by_sur = df22a_sur.groupby('surrogate')['above_threshold'].agg(['sum', 'count'])
        for sur, row in by_sur.iterrows():
            print(f"    {sur:24s}  {row['sum']:3d}/{row['count']:3d}  ({row['sum']/row['count']:.1%})")
        summary['sweeps'].append(dict(
            label='phase22a_pvc11_surrogate', n=int(len(df22a_sur)),
            n_above_threshold=int(df22a_sur['above_threshold'].sum()),
        ))

    # ─── Phase 24 Allen (real default-config) ───
    p24 = Path(ROOT_DIR) / 'data' / 'phase24_results' / 'per_session_h2_population.parquet'
    df24 = sweep_parquet(p24, 'phase24_allen_real',
                          label_cols=['session_id', 'cre_line', 'config',
                                       'condition'])
    if 'config' in df24.columns:
        df24 = df24[df24['config'] == 'default']
    if len(df24):
        df24.to_parquet(OUT_DIR / 'padic_v4_allen.parquet', index=False)
        print(f"\n  Allen real (Phase 24 default):  {len(df24)} session×condition")
        print(f"  Above-threshold by condition:")
        by_cond = df24.groupby('condition')['above_threshold'].agg(['sum', 'count'])
        for cond, row in by_cond.iterrows():
            print(f"    {cond:24s}  {row['sum']:3d}/{row['count']:3d}")
        # Per-recording dominant prime
        n_above = int(df24['above_threshold'].sum())
        print(f"  Total above-threshold: {n_above}/{len(df24)}")
        if n_above:
            print(f"  Dominant prime distribution for above-threshold rows:")
            print(df24[df24['above_threshold']]['dominant_prime_per_q'].value_counts().to_string())
        summary['sweeps'].append(dict(
            label='phase24_allen_real_default', n=int(len(df24)),
            n_above_threshold=n_above,
        ))

    # ─── Phase 24 Allen surrogates (null) ───
    p24_sur = Path(ROOT_DIR) / 'data' / 'phase24_results' / 'per_session_h2_surrogate_default.parquet'
    df24_sur = sweep_parquet(p24_sur, 'phase24_allen_surrogate',
                               label_cols=['session_id', 'cre_line',
                                             'surrogate', 'seed', 'condition'])
    if len(df24_sur):
        df24_sur.to_parquet(OUT_DIR / 'padic_v4_allen_surrogates.parquet', index=False)
        print(f"\n  Allen surrogates: {len(df24_sur)}")
        n_above = int(df24_sur['above_threshold'].sum())
        print(f"  Above-threshold: {n_above}/{len(df24_sur)} ({n_above/max(1,len(df24_sur)):.1%})")
        summary['sweeps'].append(dict(
            label='phase24_allen_surrogate', n=int(len(df24_sur)),
            n_above_threshold=n_above,
        ))

    # ─── Phase 27 local clusters ───
    p27 = Path(ROOT_DIR) / 'data' / 'phase27_results' / 'analysis3_per_cluster_real.parquet'
    df27 = sweep_parquet(p27, 'phase27_local_clusters_real',
                          label_cols=['session', 'cluster_idx', 'n_members'])
    if len(df27):
        df27.to_parquet(OUT_DIR / 'padic_v4_phase27_clusters.parquet', index=False)
        print(f"\n  Phase 27 local clusters: {len(df27)}")
        n_above = int(df27['above_threshold'].sum())
        print(f"  Above-threshold: {n_above}/{len(df27)} ({n_above/max(1,len(df27)):.1%})")
        if n_above:
            print(f"  Dominant prime distribution for above-threshold clusters:")
            print(df27[df27['above_threshold']]['dominant_prime_per_q'].value_counts().to_string())
        summary['sweeps'].append(dict(
            label='phase27_local_clusters_real', n=int(len(df27)),
            n_above_threshold=n_above,
        ))

    # ─── Phase 30 Kuramoto Analysis 1 (per-oscillator real) ───
    p30 = Path(ROOT_DIR) / 'data' / 'phase30_results' / 'analysis1_per_oscillator_real.parquet'
    df30 = sweep_parquet(p30, 'phase30_kuramoto_a1_per_osc',
                          label_cols=['K_factor', 'seed', 'i', 'omega_i'])
    if len(df30):
        df30.to_parquet(OUT_DIR / 'padic_v4_kuramoto_a1.parquet', index=False)
        print(f"\n  Phase 30 Kuramoto A1 per-oscillator: {len(df30)} (= 21 K × 3 seeds × 100 osc)")
        n_above = int(df30['above_threshold'].sum())
        print(f"  Above-threshold: {n_above}/{len(df30)} ({n_above/max(1,len(df30)):.1%})")
        if n_above:
            print(f"  Above-threshold rate by K_factor:")
            by_K = df30.groupby('K_factor')['above_threshold'].agg(['sum', 'count'])
            for K, row in by_K.iterrows():
                print(f"    K={K:.2f}*Kc  {row['sum']:3d}/{row['count']:3d}  ({row['sum']/row['count']:.1%})")
        summary['sweeps'].append(dict(
            label='phase30_kuramoto_a1_per_osc', n=int(len(df30)),
            n_above_threshold=n_above,
        ))

    with open(OUT_DIR / 'padic_v4_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n  → padic_v4_summary.json")


if __name__ == '__main__':
    main()
