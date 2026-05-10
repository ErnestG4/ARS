"""
run_phase21_calibrators.py — Phase 21 Tier 2.

GRB-specific calibration:

  - **Deadtime synthetic**: Poisson at peak rate with deletions inside
    the detector's deadtime window (~2.6 μs Fermi GBM).  Run
    joint_q_profile.  Expected: BR_artifact at high q with structural
    mass<0.3 = 0 reflecting deadtime cutoff.
  - **Per-instrument quiescent baseline**: pre-trigger window (T-200 s
    to T-1 s) per (event, detector) → joint_q_profile.  Documents
    per-instrument bias before Tier 3 interprets prompt-window
    classifications.
  - **MGF positive control (GRB 200415A)**: the priority-1 MGF bridge
    case from Castro-Tirado 2021 has published high-frequency QPOs at
    836, 1444, 2132, 4250 Hz during the prompt window (T0 to T0+0.139s).
    Verify the framework detects these at the corresponding q-bands.
    For sub-window of duration ΔT, q-band ≈ ΔT × f.  At ΔT = 0.139 s:
      f = 836  → q ≈ 116
      f = 1444 → q ≈ 200
      f = 2132 → q ≈ 296
      f = 4250 → q ≈ 591
    The framework's joint_q_profile must use q_max ≥ 600 to span the
    full claimed QPO frequency range.  This is a substantially higher
    q_max than the q_max=30–50 used in Phase 19/20; in this phase we
    use q_max=300 for general analysis (covering 836/1444/2132 Hz
    band) and document that 4250 Hz is at the resolution edge.

Outputs:
  data/phase21_calibrators.parquet
  plots/58_phase21_deadtime.png
  plots/59_phase21_quiescent_baseline.png
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from grb_pipeline import EVENT_PANEL

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PANEL_DIR = DATA / 'phase21_grb_panel'

Q_MAX_GRB = 50                   # general-analysis q_max
Q_MAX_GRB_QPO = 300              # extended q_max for MGF QPO-band scan
MIN_EVENTS_PER_Q = 30
JPF_CAP = 5000                   # joint_q_profile event cap


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


def primary_quadrant(events: np.ndarray, q_max: int = Q_MAX_GRB):
    if events.size < MIN_EVENTS_PER_Q:
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    j = joint_q_profile(events, q_max=q_max,
                         min_events_per_q=MIN_EVENTS_PER_Q)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    counts = well['quadrant'].value_counts()
    return (str(counts.idxmax()),
            float(well['rep_int_q'].median()),
            float(well['ks_gue_q'].median()),
            int(events.size))


# ─── Deadtime synthetic ────────────────────────────────────────────────────


def synthesise_deadtime_signal(rate_per_sec: float = 100_000.0,
                                duration_sec: float = 1.0,
                                deadtime_us: float = 2.6,
                                seed: int = 0) -> np.ndarray:
    """Poisson at rate_per_sec for duration_sec, with deletions of any
    event arriving within deadtime_us of a previously-kept event.
    Returns event times in microseconds (int64)."""
    rng = np.random.default_rng(seed)
    n_expected = int(rate_per_sec * duration_sec * 1.5)  # over-generate
    iei = rng.exponential(1.0 / rate_per_sec, size=n_expected)
    raw_times = np.cumsum(iei)
    raw_times = raw_times[raw_times < duration_sec]
    # Deadtime filter
    kept = []
    last_kept = -np.inf
    for t in raw_times:
        if t - last_kept >= deadtime_us / 1e6:
            kept.append(t)
            last_kept = t
    return (np.array(kept) * 1e6).astype(np.int64)


def deadtime_calibration():
    print("=" * 80)
    print("Tier 2.1 — Detector deadtime calibration")
    print("=" * 80)
    rows = []
    for det_type, deadtime_us in [('Fermi GBM NaI', 2.6),
                                    ('BATSE', 5.0),
                                    ('RHESSI', 6.0)]:
        for rate in [10_000, 50_000, 200_000]:
            ev_us = synthesise_deadtime_signal(
                rate_per_sec=rate, duration_sec=1.0,
                deadtime_us=deadtime_us, seed=0)
            ev = ev_us.astype(np.float64) / 1_000_000
            ev_unit = unfold_unit_mean(ev)
            primary, rep, ks, n = primary_quadrant(ev_unit, q_max=Q_MAX_GRB)
            rows.append(dict(
                kind='deadtime_synthetic',
                detector=det_type,
                deadtime_us=deadtime_us,
                rate_per_sec=rate,
                primary=primary, rep_med=rep, ks_gue_med=ks,
                n_events=n))
            print(f"  {det_type} rate={rate:,}/s  deadtime={deadtime_us}μs:  "
                  f"primary={primary} rep={rep:.3f} n={n:,}")
    return rows


# ─── Quiescent baseline per event ──────────────────────────────────────────


def quiescent_baseline():
    print("\n" + "=" * 80)
    print("Tier 2.2 — Per-(event, detector) quiescent baseline (T-200..T-1)")
    print("=" * 80)
    rows = []
    for event in EVENT_PANEL:
        if event['priority'] > 3:
            continue
        p = PANEL_DIR / f"{event['name']}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p, columns=['detector', 'time_us'])
        # Pre-trigger window
        bg = df[(df['time_us'] >= -200_000_000) & (df['time_us'] < -1_000_000)]
        # Pool across detectors first (gives more events for stable
        # joint_q_profile); then per-detector breakdown
        pooled = bg['time_us'].to_numpy()
        ev = pooled.astype(np.float64) / 1_000_000
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        rows.append(dict(
            kind='quiescent_baseline_pooled',
            event=event['name'],
            detector='POOLED',
            primary=primary, rep_med=rep, ks_gue_med=ks,
            n_events=n))
        print(f"  {event['name']} POOLED: n={n:,}, primary={primary}, "
              f"rep_med={rep:.3f}")
    return rows


# ─── MGF positive control ─────────────────────────────────────────────────


def mgf_positive_control():
    """For GRB 200415A (priority-1 MGF bridge), classify the prompt
    window and inspect whether RF amplitudes peak at the q-bands
    corresponding to claimed QPO frequencies (836, 1444, 2132, 4250 Hz).
    """
    print("\n" + "=" * 80)
    print("Tier 2.3 — MGF positive control: GRB 200415A "
          "(Castro-Tirado 2021 QPOs)")
    print("=" * 80)
    p = PANEL_DIR / 'GRB200415A.parquet'
    if not p.exists():
        print("  GRB 200415A parquet missing")
        return [], None

    df = pd.read_parquet(p, columns=['detector', 'time_us'])
    # Prompt window: T0 to T0 + T90 (0.139 s)
    t90_us = int(0.139 * 1_000_000)
    prompt = df[(df['time_us'] >= 0) & (df['time_us'] < t90_us)]
    print(f"  Prompt window [0, {t90_us/1000:.1f} ms]: {len(prompt):,} events "
          f"pooled across {prompt['detector'].nunique()} detectors")

    # The QPO claim is a transient on a 0.139s window — pool all detectors
    pooled_us = prompt['time_us'].to_numpy()
    if pooled_us.size < 1000:
        print("  Insufficient prompt-window events for QPO analysis")
        return [], None

    ev = pooled_us.astype(np.float64) / 1_000_000
    ev_unit = unfold_unit_mean(ev, cap=10_000)   # higher cap for QPO range
    print(f"  Subsampled for joint_q_profile: {ev_unit.size:,} events")

    # Compute joint_q_profile at q_max=300 to span 836/1444/2132 Hz
    # (q ≈ ΔT × f — but ΔT is the unfolded unit-mean spacing; for the
    # QPO claim's frequency to appear, the original TIME duration must
    # be encoded in the unfolded units.  Since the prompt window is
    # 0.139 s and 836–2132 Hz signals have periods 0.47–1.20 ms, the
    # corresponding q-bands depend on the empirical mean spacing of
    # the events in the prompt window.)
    j = joint_q_profile(ev_unit, q_max=Q_MAX_GRB_QPO,
                          min_events_per_q=MIN_EVENTS_PER_Q)
    qd = joint_quadrant_diagnostic(j)

    # Compute mean spacing in the prompt window in seconds
    sp = np.diff(pooled_us)
    sp = sp[sp > 0]
    mean_sp_us = float(sp.mean()) if sp.size else 1.0
    mean_sp_s = mean_sp_us / 1e6
    # In unfolded units (mean spacing 1.0), q corresponds to a period of q
    # unit-spacings, which in time is q × mean_sp seconds.  A frequency
    # f (Hz) in time → period 1/f s → q = 1/(f × mean_sp_s).
    # But the joint_q_profile's q indexes into Farey-rational PLLs at
    # frequency a/q.  Resonance at frequency f maps to q where the
    # mean-event-spacing × f / (a/q) is integer.  Approximation:
    # q ≈ 1 / (f × mean_sp_s) for fundamental.
    print(f"\n  Mean prompt-window event spacing: {mean_sp_s*1e6:.2f} μs")
    print(f"  Implied q for claimed QPOs:")
    for f_hz in [836, 1444, 2132, 4250]:
        q_est = 1.0 / (f_hz * mean_sp_s)
        print(f"    f={f_hz} Hz → q ≈ {q_est:.1f}")
    # Flag any q-band with elevated rf_amplitude_q vs median
    rf_med = float(j.loc[j['q'] >= 2, 'rf_amplitude_q'].median())
    rf_thresh = 5.0 * rf_med
    elevated = j[(j['q'] >= 2) & (j['rf_amplitude_q'] > rf_thresh)]
    print(f"\n  RF-amplitude median (q≥2): {rf_med:.4f}")
    print(f"  q-bands with rf > 5 × median ({rf_thresh:.4f}):")
    if len(elevated) == 0:
        print(f"    (none)")
    else:
        for _, row in elevated.head(15).iterrows():
            print(f"    q={int(row['q']):3d}  rf={row['rf_amplitude_q']:.4f}  "
                  f"rep_int_q={row['rep_int_q']:.3f}  "
                  f"ks_gue_q={row['ks_gue_q']:.3f}")
    rows = [dict(
        kind='mgf_positive_control',
        event='GRB200415A',
        detector='POOLED',
        n_events_prompt=int(pooled_us.size),
        n_events_used=int(ev_unit.size),
        mean_spacing_us=float(mean_sp_us),
        rf_median=float(rf_med),
        n_rf_spike_qbands=int(len(elevated)),
    )]
    return rows, j


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    rows = []
    rows.extend(deadtime_calibration())
    rows.extend(quiescent_baseline())
    mgf_rows, mgf_j = mgf_positive_control()
    rows.extend(mgf_rows)

    out = DATA / 'phase21_calibrators.parquet'
    pd.DataFrame(rows).to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(rows)} rows)")

    # Plot 58: deadtime
    fig, ax = plt.subplots(figsize=(9, 5))
    dt_rows = [r for r in rows if r['kind'] == 'deadtime_synthetic']
    for det in {r['detector'] for r in dt_rows}:
        sel = [r for r in dt_rows if r['detector'] == det]
        rates = [r['rate_per_sec'] for r in sel]
        reps = [r['rep_med'] for r in sel]
        ax.plot(rates, reps, marker='o', label=det)
    ax.set_xscale('log')
    ax.set_xlabel('Poisson rate (events/s)')
    ax.set_ylabel('rep_med')
    ax.set_title('Phase 21 Tier 2.1 — Detector deadtime artifact\n'
                  '(synthetic Poisson + deadtime → joint_q_profile)')
    ax.legend(); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS / '58_phase21_deadtime.png', dpi=130)
    plt.close()
    print(f"  → {PLOTS}/58_phase21_deadtime.png")

    # Plot 59: quiescent baseline
    fig, ax = plt.subplots(figsize=(9, 5))
    qb_rows = [r for r in rows if r['kind'] == 'quiescent_baseline_pooled']
    if qb_rows:
        events = [r['event'] for r in qb_rows]
        reps = [r['rep_med'] for r in qb_rows]
        ks = [r['ks_gue_med'] for r in qb_rows]
        x = np.arange(len(events))
        ax.bar(x - 0.2, reps, width=0.4, label='rep_med')
        ax.bar(x + 0.2, ks, width=0.4, label='KS_GUE_med')
        ax.set_xticks(x)
        ax.set_xticklabels(events, rotation=20, ha='right')
        ax.set_ylim(0, 1)
        ax.set_title('Phase 21 Tier 2.2 — Per-event quiescent baseline '
                      '(T-200..T-1 s, pooled detectors)')
        ax.legend(); ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(PLOTS / '59_phase21_quiescent_baseline.png', dpi=130)
        plt.close()
        print(f"  → {PLOTS}/59_phase21_quiescent_baseline.png")


if __name__ == '__main__':
    main()
