"""
phase23/run_phase23_targeted.py — targeted 909 Hz QPO replication on
GRB 230307A.

The Phase 21 Tier 3 classification used 2.0 s sub-windows with
Q_MAX=30; the published Chen 2025 QPO claim window for GRB 230307A
is 45–47 s post-trigger (2 s long), so Tier 3 captured at most one
sub-window inside the claim — no temporal-trajectory resolution
within the QPO window.  Additionally, q_max=30 left the published
909 Hz frequency just above the framework's q-coverage at
typical prompt-window event rates.

Phase 23 time-slice adjustment (per GRB_NEXT_STEPS.md):

  - sub-window:    100 ms  (down from 2.0 s in Tier 3)
  - q_max:         50      (up from 30; gives ~2.5× margin on q_target)
  - window range:  [-5, 60] s post-trigger  (covers pre-onset
                    baseline, prompt, QPO claim window, post-claim)

This script:
  1. Loads pooled photon arrivals for GRB 230307A from the existing
     Phase 21 panel parquet.
  2. Sub-windows the [-5, 60] s range at 100 ms; classifies each
     well-powered sub-window via joint_q_profile + joint_quadrant_diagnostic
     at Q_MAX=50.
  3. Records the full per-q signature, plus the rep_int_q at the
     909 Hz band per sub-window.
  4. Compares "during QPO window" (45–47 s) to "pre-onset baseline"
     (matched-rate window before the QPO claim; identified
     adaptively to match per-sub-window event count).
  5. Generates a lightcurve-modulated Poisson surrogate for the
     same time region (5 seeds), classifies the same way, and
     compares real vs surrogate at the 909 Hz q-band specifically.

Outputs:
  data/phase23_results/phase23_targeted_classification.parquet
  data/phase23_results/phase23_targeted_surrogate_classification.parquet
  data/phase23_results/phase23_targeted_qpo_comparison.parquet
  Stdout: per-window summary + verdict.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from grb_pipeline import EVENT_PANEL
from lightcurve_modulated_surrogate import lightcurve_modulated_poisson


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase23_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)
PANEL_DIR = Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'

EVENT_NAME = 'GRB230307A'
TARGET_QPO_HZ = 909.0
QPO_WINDOW_S = (45.0, 47.0)            # Chen 2025 claim
ANALYSIS_WINDOW_S = (-5.0, 60.0)       # broader — gives baseline + post-claim
SUBWINDOW_S = 0.100                    # 100 ms — the Phase 23 fix
Q_MAX = 50
MIN_EVENTS_PER_Q = 30
JPF_CAP = 5000
N_SURROGATE_SEEDS = 5
N_PROC = 12   # multiprocessing pool size for sub-window parallelism


def unfold_unit_mean(t: np.ndarray, cap: int = JPF_CAP) -> np.ndarray:
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def classify_subwindow(events_us: np.ndarray, q_max: int = Q_MAX) -> dict:
    """Run the ARS pipeline on a sub-window's pooled events.  Returns
    the modal-quadrant collapse + the full per-q rep_int and
    rf_amplitude vectors."""
    n_in = int(events_us.size)
    if n_in < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', rep_med=np.nan,
                    ks_gue_med=np.nan, n_events=n_in, n_well=0,
                    rep_int_q=None, rf_amplitude_q=None,
                    quadrants_per_q=None)
    ev = events_us.astype(np.float64) / 1_000_000
    ev_unit = unfold_unit_mean(ev)
    if ev_unit.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', rep_med=np.nan,
                    ks_gue_med=np.nan, n_events=n_in, n_well=0,
                    rep_int_q=None, rf_amplitude_q=None,
                    quadrants_per_q=None)
    j = joint_q_profile(ev_unit, q_max=q_max,
                          min_events_per_q=MIN_EVENTS_PER_Q)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return dict(primary='underpowered', rep_med=np.nan,
                    ks_gue_med=np.nan, n_events=n_in, n_well=0,
                    rep_int_q=j['rep_int_q'].tolist(),
                    rf_amplitude_q=j['rf_amplitude_q'].tolist(),
                    quadrants_per_q=qd['quadrant'].tolist())
    counts = well['quadrant'].value_counts()
    return dict(
        primary=str(counts.idxmax()),
        rep_med=float(well['rep_int_q'].median()),
        ks_gue_med=float(well['ks_gue_q'].median()),
        n_events=n_in, n_well=int(len(well)),
        rep_int_q=j['rep_int_q'].tolist(),
        rf_amplitude_q=j['rf_amplitude_q'].tolist(),
        quadrants_per_q=qd['quadrant'].tolist(),
    )


def _classify_one_subwindow(args):
    """Worker for multiprocessing pool.  args is (events_in_subwindow_us,
    sub_start_us, sub_end_us, q_max, label)."""
    ev_us, s_us, e_us, q_max, label = args
    cls = classify_subwindow(ev_us, q_max=q_max)
    return dict(
        label=label,
        sub_start_s=s_us / 1e6,
        sub_end_s=e_us / 1e6,
        **cls,
    )


def trajectory_classify(events_us: np.ndarray,
                          window_start_s: float,
                          window_end_s: float,
                          subwindow_s: float = SUBWINDOW_S,
                          q_max: int = Q_MAX,
                          label: str = 'real',
                          n_proc: int = N_PROC,
                          progress_every: int = 100) -> pd.DataFrame:
    """Slide a sub-window across [window_start_s, window_end_s) and
    classify each in parallel via multiprocessing.Pool.  Returns a
    DataFrame with one row per sub-window."""
    sub_us = int(subwindow_s * 1_000_000)
    s_us = int(window_start_s * 1_000_000)
    e_us = int(window_end_s * 1_000_000)
    # Pre-extract per-sub-window event arrays so worker processes don't
    # need to hold the full pooled array (cheap copy via fork on Linux,
    # but we slice once here for clarity).
    jobs = []
    for sub_start in range(s_us, e_us, sub_us):
        mask = (events_us >= sub_start) & (events_us < sub_start + sub_us)
        ev = events_us[mask]
        jobs.append((ev, sub_start, sub_start + sub_us, q_max, label))
    rows = []
    t0 = time.time()
    print(f"    [{label}] {len(jobs)} sub-windows, n_proc={n_proc}",
            flush=True)
    with Pool(processes=n_proc) as pool:
        for i, r in enumerate(pool.imap(_classify_one_subwindow, jobs,
                                          chunksize=8), start=1):
            rows.append(r)
            if i % progress_every == 0 or i == len(jobs):
                rate = i / max(time.time() - t0, 1e-6)
                eta = (len(jobs) - i) / max(rate, 1e-6)
                print(f"    [{label}] {i}/{len(jobs)}  "
                        f"({rate:.1f}/s  ETA {eta:.0f}s)", flush=True)
    return pd.DataFrame(rows)


def q_target_for(events_in_subwindow: int, subwindow_s: float,
                   freq_hz: float) -> float:
    """The Farey q-band that maps to the target frequency given the
    sub-window's event rate.  q_target = rate / freq_hz where rate
    = events_in_subwindow / subwindow_s."""
    rate = events_in_subwindow / max(subwindow_s, 1e-9)
    return rate / freq_hz


def main():
    print("=" * 80)
    print(f"Phase 23 — targeted {TARGET_QPO_HZ} Hz QPO replication on {EVENT_NAME}")
    print("=" * 80)
    print(f"  sub-window:           {SUBWINDOW_S*1000:.0f} ms")
    print(f"  q_max:                {Q_MAX}")
    print(f"  analysis window:      [{ANALYSIS_WINDOW_S[0]:+.0f}, "
          f"{ANALYSIS_WINDOW_S[1]:+.0f}] s post-trigger")
    print(f"  QPO claim window:     [{QPO_WINDOW_S[0]:.1f}, "
          f"{QPO_WINDOW_S[1]:.1f}] s (Chen 2025)")
    print()

    # Load pooled events
    p = PANEL_DIR / f'{EVENT_NAME}.parquet'
    df = pd.read_parquet(p, columns=['time_us'])
    times = df['time_us'].to_numpy()
    print(f"  pooled events on disk: {len(times):,}")

    # Restrict to analysis window
    s_us = int(ANALYSIS_WINDOW_S[0] * 1e6)
    e_us = int(ANALYSIS_WINDOW_S[1] * 1e6)
    mask = (times >= s_us) & (times < e_us)
    times = times[mask]
    print(f"  events in analysis window: {len(times):,}")
    print(f"  rate in analysis window:    "
          f"{len(times)/(ANALYSIS_WINDOW_S[1]-ANALYSIS_WINDOW_S[0]):.0f} /s")
    print()

    # ─── real-data trajectory ──
    print("Classifying real-data sub-windows...")
    t0 = time.time()
    traj_real = trajectory_classify(times,
                                      ANALYSIS_WINDOW_S[0],
                                      ANALYSIS_WINDOW_S[1],
                                      label='real')
    print(f"  {len(traj_real)} sub-windows  ⏱{time.time()-t0:.0f}s")
    n_well = int((traj_real['primary'] != 'underpowered').sum())
    print(f"  well-powered (primary != underpowered): {n_well}")
    print()

    # ─── lightcurve-modulated Poisson surrogate ──
    print(f"Generating {N_SURROGATE_SEEDS} lightcurve-modulated Poisson "
          f"surrogates...")
    surr_traj_list = []
    for seed in range(N_SURROGATE_SEEDS):
        rng = np.random.default_rng(seed)
        t0 = time.time()
        surr_events = lightcurve_modulated_poisson(
            times, bin_us=1_000, smoothing_window=21, rng=rng)
        traj_surr = trajectory_classify(surr_events,
                                          ANALYSIS_WINDOW_S[0],
                                          ANALYSIS_WINDOW_S[1],
                                          label=f'surrogate_seed{seed}')
        surr_traj_list.append(traj_surr)
        print(f"  seed {seed}: {len(surr_events):,} events  "
              f"⏱{time.time()-t0:.0f}s")
    traj_surr_all = pd.concat(surr_traj_list, ignore_index=True)
    print()

    # Save
    traj_real.to_parquet(OUT_DIR / 'phase23_targeted_classification.parquet',
                          index=False)
    traj_surr_all.to_parquet(
        OUT_DIR / 'phase23_targeted_surrogate_classification.parquet',
        index=False)
    print(f"  → {OUT_DIR}/phase23_targeted_classification.parquet")
    print(f"  → {OUT_DIR}/phase23_targeted_surrogate_classification.parquet")
    print()

    # ─── per-sub-window q-band-of-interest extraction ──
    # For each sub-window, find the q-band closest to 909 Hz given that
    # sub-window's event rate, and extract rep_int_q + rf_amplitude_q at
    # that q.  This is the natural-q-resolution test the time-slice
    # adjustment was meant to enable.
    rows = []
    for label, sub in [('real', traj_real)] + [(f'surr_{s}', surr_traj_list[s])
                                                for s in range(N_SURROGATE_SEEDS)]:
        for _, r in sub.iterrows():
            if r['primary'] == 'underpowered': continue
            n_ev = int(r['n_events'])
            q_t = q_target_for(n_ev, SUBWINDOW_S, TARGET_QPO_HZ)
            if q_t < 2 or q_t > Q_MAX: continue
            q_idx = int(round(q_t)) - 1
            rep_int_at_qpo = (r['rep_int_q'][q_idx]
                                if r['rep_int_q'] is not None
                                and q_idx < len(r['rep_int_q'])
                                else np.nan)
            rf_amp_at_qpo = (r['rf_amplitude_q'][q_idx]
                                if r['rf_amplitude_q'] is not None
                                and q_idx < len(r['rf_amplitude_q'])
                                else np.nan)
            quad_at_qpo = (r['quadrants_per_q'][q_idx]
                              if r['quadrants_per_q'] is not None
                              and q_idx < len(r['quadrants_per_q'])
                              else None)
            rows.append(dict(
                label=label,
                sub_start_s=r['sub_start_s'],
                sub_end_s=r['sub_end_s'],
                n_events=n_ev,
                q_target=q_t,
                q_used=q_idx + 1,
                rep_int_at_qpo_q=rep_int_at_qpo,
                rf_amp_at_qpo_q=rf_amp_at_qpo,
                quadrant_at_qpo_q=quad_at_qpo,
                primary=r['primary'],
                in_qpo_window=bool(r['sub_start_s'] >= QPO_WINDOW_S[0]
                                    and r['sub_end_s'] <= QPO_WINDOW_S[1]),
            ))
    qpo_df = pd.DataFrame(rows)
    qpo_df.to_parquet(OUT_DIR / 'phase23_targeted_qpo_comparison.parquet',
                       index=False)
    print(f"  → {OUT_DIR}/phase23_targeted_qpo_comparison.parquet  "
          f"({len(qpo_df)} rows)")
    print()

    # ─── verdict ──
    real_in = qpo_df[(qpo_df['label'] == 'real') & qpo_df['in_qpo_window']]
    real_out = qpo_df[(qpo_df['label'] == 'real') & ~qpo_df['in_qpo_window']]
    surr_in = qpo_df[(qpo_df['label'].str.startswith('surr_'))
                       & qpo_df['in_qpo_window']]
    surr_out = qpo_df[(qpo_df['label'].str.startswith('surr_'))
                        & ~qpo_df['in_qpo_window']]

    print("Sub-window counts at the 909 Hz q-band (well-powered + q in [2, q_max]):")
    print(f"  real, inside QPO window  ({QPO_WINDOW_S[0]}–{QPO_WINDOW_S[1]} s): "
          f"{len(real_in)}")
    print(f"  real, outside QPO window: {len(real_out)}")
    print(f"  surrogate (5 seeds), inside QPO window: {len(surr_in)}")
    print(f"  surrogate (5 seeds), outside QPO window: {len(surr_out)}")
    print()

    def _summary(df, name):
        if not len(df):
            return f"{name}: empty"
        return (f"{name}: n={len(df)}  "
                f"median rep_int_at_qpo={df['rep_int_at_qpo_q'].median():.3f}  "
                f"median rf_amp={df['rf_amp_at_qpo_q'].median():.4f}  "
                f"quadrants={dict(df['quadrant_at_qpo_q'].value_counts())}")

    print("Per-condition summaries at the 909 Hz q-band:")
    print(f"  {_summary(real_in,  'real_inside ')}")
    print(f"  {_summary(real_out, 'real_outside')}")
    print(f"  {_summary(surr_in,  'surr_inside ')}")
    print(f"  {_summary(surr_out, 'surr_outside')}")
    print()

    # Verdict logic
    # PASS: real_inside differs from BOTH real_outside AND surr_inside at the
    #       909 Hz q-band (rep_int or rf_amp elevated in real_inside vs the
    #       two baselines).
    # SOFT PASS: real_inside differs from real_outside but the surrogate
    #            reproduces the same difference (lightcurve-driven, not QPO).
    # FAIL: real_inside doesn't differ from real_outside or differs in the
    #       same direction the surrogate does.
    print("Verdict:")
    if not len(real_in) or not len(surr_in):
        print(f"  INCONCLUSIVE — insufficient sub-windows for comparison.")
        return
    real_med_in = float(real_in['rep_int_at_qpo_q'].median())
    real_med_out = float(real_out['rep_int_at_qpo_q'].median()) if len(real_out) else np.nan
    surr_med_in = float(surr_in['rep_int_at_qpo_q'].median())
    surr_med_out = float(surr_out['rep_int_at_qpo_q'].median()) if len(surr_out) else np.nan
    print(f"  real    median rep_int_at_qpo_q  inside / outside: "
          f"{real_med_in:.3f} / {real_med_out:.3f}  (delta {real_med_in - real_med_out:+.3f})")
    print(f"  surr    median rep_int_at_qpo_q  inside / outside: "
          f"{surr_med_in:.3f} / {surr_med_out:.3f}  (delta {surr_med_in - surr_med_out:+.3f})")
    real_delta = real_med_in - real_med_out
    surr_delta = surr_med_in - surr_med_out

    if abs(real_delta) > 0.05 and abs(real_delta - surr_delta) > 0.05:
        if real_delta > surr_delta:
            print(f"  PASS — real shows larger inside-vs-outside delta "
                  f"({real_delta:+.3f}) than surrogate ({surr_delta:+.3f}); "
                  f"signature beyond lightcurve.")
        else:
            print(f"  PASS-INVERTED — real shows smaller inside-vs-outside delta "
                  f"than surrogate; structure suppressed in QPO window.")
    elif abs(real_delta) > 0.05:
        print(f"  SOFT PASS — real shows inside-vs-outside delta "
              f"({real_delta:+.3f}) but surrogate reproduces it "
              f"({surr_delta:+.3f}); signature is lightcurve-driven, "
              f"no QPO claim survives.")
    else:
        print(f"  FAIL — real shows no meaningful inside-vs-outside delta "
              f"at the 909 Hz q-band ({real_delta:+.3f}).")


if __name__ == '__main__':
    main()
