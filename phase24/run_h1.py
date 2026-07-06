"""
phase24/run_h1.py — H1 pipeline on the chosen Allen session.

Per Phase 22a methodology (carried through with q_max=30):
  1. Per-unit ARS classification on each condition
     (drifting_pooled, natural_movie_one, spontaneous).
  2. Functional categories computed from spikes
     (OSI/DSI from drifting per-direction tuning, F1/F0 at preferred
     direction, mean firing rate per condition).
  3. Compare recomputed functional categories to Allen's precomputed
     values from the analysis_metrics CSV (sanity check on
     methodology consistency).
  4. H1 cross-validation: Spearman partial correlation of {rep_med,
     ks_gue_med} vs {OSI, DSI, F1/F0} controlling for firing rate.

Outputs:
  data/phase24_results/h1_classifications.parquet
  data/phase24_results/h1_functional.parquet
  data/phase24_results/h1_allen_comparison.parquet
  data/phase24_results/h1_crossval_summary.parquet
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, t as student_t

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, THIS_DIR)

from loader import load_session
from ars_classify import classify, per_q_columns


SESSION_ID = 732592105
OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase24_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_PROC = 12
H1_MIN_SPIKES = 400      # carried from Phase 22a (matches N_POINTS=400)
DRIFTING_TRIAL_SEC = 2.0
NATURAL_MOVIE_DUR_SEC = 30.0


# ─── ARS classification helpers ─────────────────────────────────────────────


def _classify_one(args):
    """Worker for multiprocessing pool.  args = (unit_id, label, spike_times_arr)."""
    unit_id, label, sp = args
    res = classify(sp, return_full=True)
    cols = per_q_columns(res['per_q'])
    return dict(
        unit_id=int(unit_id), condition=label,
        primary=res['primary'], rep_med=res['rep_med'],
        ks_gue_med=res['ks_gue_med'],
        n_events_in=res['n_events_in'],
        n_events_used=res['n_events_used'],
        n_well=res['n_well'], **cols,
    )


# ─── Functional categories from spikes ──────────────────────────────────────


def per_direction_rate(rec, unit_id):
    """Per-direction firing rate (sp/s) on drifting gratings, averaged
    across all temporal frequencies.  Returns dict[orientation_deg → rate]."""
    sp = rec.spike_times[unit_id]
    out = {}
    for ori in sorted(rec.drifting_gratings['orientation'].dropna().unique()):
        pres = rec.drifting_gratings[rec.drifting_gratings['orientation'] == ori]
        n_total = 0
        total_dur = 0.0
        for _, row in pres.iterrows():
            mask = (sp >= row['start_time']) & (sp < row['stop_time'])
            n_total += int(mask.sum())
            total_dur += row['stop_time'] - row['start_time']
        out[float(ori)] = n_total / max(total_dur, 1e-9)
    return out


def osi_dsi(per_dir_rate: dict) -> dict:
    """Circular-vector OSI/DSI, matching Phase 22a."""
    if not per_dir_rate: return dict(osi=np.nan, dsi=np.nan,
                                       pref_ori_deg=np.nan, pref_dir_deg=np.nan)
    dirs = np.array(sorted(per_dir_rate.keys()))
    rates = np.array([per_dir_rate[d] for d in dirs])
    th = np.deg2rad(dirs)
    if rates.sum() <= 0:
        return dict(osi=np.nan, dsi=np.nan,
                    pref_ori_deg=np.nan, pref_dir_deg=np.nan)
    s_dir = float(np.abs(np.sum(rates * np.exp(1j * th))) / rates.sum())
    s_ori = float(np.abs(np.sum(rates * np.exp(1j * 2 * th))) / rates.sum())
    pref_dir = float((np.angle(np.sum(rates * np.exp(1j * th))) % (2 * np.pi))
                       * 180 / np.pi)
    pref_ori = float((np.angle(np.sum(rates * np.exp(1j * 2 * th))) % (2 * np.pi))
                       * 90 / np.pi)
    return dict(osi=s_ori, dsi=s_dir, pref_ori_deg=pref_ori,
                pref_dir_deg=pref_dir)


def f1_f0_at_preferred(rec, unit_id, pref_dir_deg, bin_ms=2.0) -> float:
    """F1/F0 at the unit's preferred direction.  TF used = preferred TF
    (computed by max per-presentation rate across TFs at the preferred dir)."""
    sp = rec.spike_times[unit_id]
    pres = rec.drifting_gratings[
        rec.drifting_gratings['orientation'] == round(pref_dir_deg / 45) * 45]
    if not len(pres): return float('nan')
    # Group by TF, find max-rate TF
    tf_rates = {}
    for tf in sorted(pres['temporal_frequency'].dropna().unique()):
        tf_pres = pres[pres['temporal_frequency'] == tf]
        n = 0; dur = 0.0
        for _, row in tf_pres.iterrows():
            mask = (sp >= row['start_time']) & (sp < row['stop_time'])
            n += int(mask.sum())
            dur += row['stop_time'] - row['start_time']
        tf_rates[tf] = n / max(dur, 1e-9)
    if not tf_rates: return float('nan')
    pref_tf = max(tf_rates, key=tf_rates.get)
    pref_pres = pres[pres['temporal_frequency'] == pref_tf]

    n_bins = int(DRIFTING_TRIAL_SEC * 1000 / bin_ms)
    psth = np.zeros(n_bins)
    n_pres = 0
    for _, row in pref_pres.iterrows():
        mask = (sp >= row['start_time']) & (sp < row['stop_time'])
        ev = sp[mask] - row['start_time']
        edges = np.linspace(0, DRIFTING_TRIAL_SEC, n_bins + 1)
        psth += np.histogram(ev, bins=edges)[0]
        n_pres += 1
    if n_pres == 0 or psth.sum() == 0: return float('nan')
    psth = psth / (n_pres * (bin_ms / 1000))   # spikes/sec
    f0 = float(psth.mean())
    if f0 <= 0: return float('nan')
    spec = np.abs(np.fft.rfft(psth - f0))
    freqs = np.fft.rfftfreq(n_bins, d=bin_ms / 1000)
    if not freqs.size: return float('nan')
    k = int(np.argmin(np.abs(freqs - pref_tf)))
    if k < 1: return float('nan')
    f1 = float(2.0 / n_bins * spec[k])
    return f1 / f0


# ─── H1 cross-validation ───────────────────────────────────────────────────


def _partial_spearman(x, y, z):
    df = pd.DataFrame({'x': x, 'y': y, 'z': z}).dropna()
    n = len(df)
    if n < 10: return (float('nan'), float('nan'), n)
    rxy, _ = spearmanr(df['x'], df['y'])
    rxz, _ = spearmanr(df['x'], df['z'])
    ryz, _ = spearmanr(df['y'], df['z'])
    denom = np.sqrt(max((1 - rxz**2) * (1 - ryz**2), 1e-15))
    if denom <= 0: return (float('nan'), float('nan'), n)
    rho = (rxy - rxz * ryz) / denom
    if n <= 4: return (float(rho), float('nan'), n)
    t_stat = rho * np.sqrt((n - 3) / max(1 - rho**2, 1e-15))
    p = 2 * (1 - student_t.cdf(abs(t_stat), df=n - 3))
    return (float(rho), float(p), n)


# ─── orchestrator ──────────────────────────────────────────────────────────


def main():
    print("=" * 80)
    print(f"Phase 24 H1 — Allen session {SESSION_ID}")
    print("=" * 80)

    rec = load_session(SESSION_ID)
    print(f"  loaded: {rec.n_units_qc_passing} V1 units after QC")
    print(f"  genotype: {rec.genotype}, sex: {rec.sex}, age: {rec.age_in_days}d")
    print()

    # Build per-(unit, condition) job list with H1 spike-count filter
    print("Building H1-passing (unit, condition) job list...")
    jobs = []
    for uid in rec.units.index:
        for label, fn in [('drifting_pooled',
                            lambda u: rec.concatenated_spikes_drifting(u)),
                           ('natural_movie_one',
                            lambda u: rec.concatenated_spikes_natural_movie_one(u)),
                           ('spontaneous',
                            lambda u: rec.concatenated_spikes_spontaneous(u))]:
            sp = fn(uid)
            if sp.size >= H1_MIN_SPIKES:
                jobs.append((int(uid), label, sp))
    print(f"  total (unit, condition) classifications: {len(jobs)}")
    by_cond = {}
    for j in jobs:
        by_cond.setdefault(j[1], 0)
        by_cond[j[1]] += 1
    for cond, n in by_cond.items():
        print(f"    {cond}: {n} units")
    print()

    # Run ARS classification with multiprocessing
    print(f"Running per-(unit, condition) ARS classification (n_proc={N_PROC})...")
    rows = []
    t0 = time.time()
    with Pool(processes=N_PROC) as pool:
        for i, r in enumerate(pool.imap(_classify_one, jobs, chunksize=4),
                                start=1):
            rows.append(r)
            if i % 50 == 0 or i == len(jobs):
                rate = i / max(time.time() - t0, 1e-6)
                print(f"  {i:4d}/{len(jobs)}  ({rate:.1f}/s)", flush=True)
    df_ars = pd.DataFrame(rows)
    df_ars.to_parquet(OUT_DIR / 'h1_classifications.parquet', index=False)
    print(f"\n  → {OUT_DIR}/h1_classifications.parquet  ({len(df_ars)} rows)")

    # Quadrant summary
    print()
    print("Modal-quadrant counts per condition:")
    for cond, g in df_ars.groupby('condition'):
        c = g['primary'].value_counts()
        print(f"  {cond:25s}  {dict(c)}")
    print()

    # ─── functional categories ─────
    print("Computing functional categories from spikes...")
    func_rows = []
    for uid in rec.units.index:
        per_dir = per_direction_rate(rec, int(uid))
        td = osi_dsi(per_dir)
        if not np.isnan(td['pref_dir_deg']):
            f1f0 = f1_f0_at_preferred(rec, int(uid), td['pref_dir_deg'])
        else:
            f1f0 = float('nan')
        # Mean firing rate over the recording session
        sp = rec.spike_times[int(uid)]
        dur = float(sp.max() - sp.min()) if sp.size > 1 else 1.0
        mean_rate = sp.size / max(dur, 1e-9)
        func_rows.append(dict(
            unit_id=int(uid),
            mean_rate=mean_rate,
            **td, f1_f0_pref=f1f0,
            per_dir_rate_str=str(per_dir),
        ))
    df_func = pd.DataFrame(func_rows)
    df_func.to_parquet(OUT_DIR / 'h1_functional.parquet', index=False)
    print(f"  → {OUT_DIR}/h1_functional.parquet  ({len(df_func)} rows)")

    # ─── Allen comparison ─────
    print()
    print("Comparing recomputed functional categories to Allen precomputed:")
    if len(rec.analysis_metrics):
        am = rec.analysis_metrics
        joined = df_func.merge(am[['g_osi_dg', 'g_dsi_dg', 'f1_f0_dg',
                                        'pref_ori_dg', 'firing_rate_dg']],
                                left_on='unit_id', right_index=True,
                                how='inner')
        print(f"  joined: {len(joined)} units (recomputed × Allen)")
        sub = joined.dropna(subset=['osi', 'g_osi_dg'])
        if len(sub):
            r_osi, p_osi = spearmanr(sub['osi'], sub['g_osi_dg'])
            r_dsi, p_dsi = spearmanr(sub.dropna(subset=['dsi', 'g_dsi_dg'])['dsi'],
                                       sub.dropna(subset=['dsi', 'g_dsi_dg'])['g_dsi_dg'])
            print(f"  Spearman recomputed-OSI vs Allen g_osi_dg: ρ={r_osi:+.3f}  p={p_osi:.2e}  n={len(sub)}")
            print(f"  Spearman recomputed-DSI vs Allen g_dsi_dg: ρ={r_dsi:+.3f}  p={p_dsi:.2e}")
        joined.to_parquet(OUT_DIR / 'h1_allen_comparison.parquet', index=False)
        print(f"  → {OUT_DIR}/h1_allen_comparison.parquet")
    else:
        print("  (no Allen analysis_metrics available)")
    print()

    # ─── H1 cross-validation ─────
    # Restrict ARS to drifting_pooled (where the OSI/DSI/F1F0 came from)
    print("H1 cross-validation: Spearman partial correlation "
            "(drifting_pooled ARS) controlling for firing rate")
    ars_drift = df_ars[df_ars['condition'] == 'drifting_pooled']
    j = ars_drift.merge(df_func, on='unit_id')
    rows = []
    for descriptor in ['osi', 'dsi', 'f1_f0_pref']:
        for ars_metric in ['rep_med', 'ks_gue_med']:
            sub = j.dropna(subset=[descriptor, ars_metric, 'mean_rate'])
            if len(sub) < 20: continue
            r_raw, p_raw = spearmanr(sub[ars_metric], sub[descriptor])
            r_par, p_par, n = _partial_spearman(sub[ars_metric], sub[descriptor],
                                                  sub['mean_rate'])
            rows.append(dict(
                descriptor=descriptor, ars_metric=ars_metric,
                n_units=int(n),
                spearman_raw=float(r_raw), p_raw=float(p_raw),
                spearman_partial=r_par, p_partial=p_par,
            ))
    cv = pd.DataFrame(rows)
    cv.to_parquet(OUT_DIR / 'h1_crossval_summary.parquet', index=False)
    print()
    print(cv.to_string(index=False))
    print()
    print(f"  → {OUT_DIR}/h1_crossval_summary.parquet")


if __name__ == '__main__':
    main()
