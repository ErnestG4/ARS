"""
run_phase21_classification.py — Phase 21 Tier 3.

Per-(event, sub-window) classification trajectory at TWO resolutions:

  1. Quadrant trajectory: sequence of joint_quadrant_diagnostic
     primary-quadrant labels across sub-windows.
  2. rep_med trajectory: rep_med per q-band per sub-window —
     the new analysis added per Phase 20.5 lessons (cross-domain
     timing signatures live predominantly at sub-quadrant
     resolution).

Per published QPO claim, the q-band corresponding to the claimed
frequency is computed via q ≈ event_rate / claimed_frequency, where
event_rate is the empirical pooled-detector rate in the sub-window
(events per second).  For ARS to detect a kHz-class QPO, event_rate
must be sufficiently high that q falls inside the joint_q_profile's
range (q ≤ q_max ≈ 50).  This holds for 230307A's 909 Hz claim
(rate ~16 K events/s pooled → q ≈ 18); it fails for 200415A's
2132/4250 Hz claims and SGR-1806-20's 1837 Hz, where event rates
during the brief MGF prompt are too high (~80 M events/s pooled)
for the QPO frequency to fall inside the joint-plane's natural
q-window.

Outputs:
  data/phase21_classification.parquet
  data/phase21_qpo_comparison.parquet
  plots/60_phase21_trajectory_per_event.png
  plots/61_phase21_qpo_replication.png
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
from transition_diagnostic import characterize_transition

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PANEL_DIR = DATA / 'phase21_grb_panel'
PLOTS.mkdir(parents=True, exist_ok=True)

Q_MAX = 30
MIN_EVENTS_PER_Q = 30
JPF_CAP = 1500


def unfold_unit_mean(t, cap=JPF_CAP):
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def classify_subwindow(events_us: np.ndarray) -> dict:
    """Return primary, rep_med, ks_gue_med, n_events, AND the full
    rep_int_q array for the sub-window's joint-plane reading."""
    if events_us.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n=int(events_us.size),
                     rep_int_q=None)
    ev = events_us.astype(np.float64) / 1_000_000
    ev_unit = unfold_unit_mean(ev)
    if ev_unit.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n=int(ev.size),
                     rep_int_q=None)
    j = joint_q_profile(ev_unit, q_max=Q_MAX,
                         min_events_per_q=MIN_EVENTS_PER_Q)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return dict(primary='underpowered', rep_med=np.nan,
                     ks_gue_med=np.nan, n=int(ev.size),
                     rep_int_q=None)
    counts = well['quadrant'].value_counts()
    return dict(
        primary=str(counts.idxmax()),
        rep_med=float(well['rep_int_q'].median()),
        ks_gue_med=float(well['ks_gue_q'].median()),
        n=int(ev.size),
        rep_int_q=j['rep_int_q'].to_numpy(),
    )


def per_event_trajectory(event: dict,
                          subwindow_sec: float = 1.0,
                          window_start_s: float = -10.0,
                          window_end_s: float = None,
                          ) -> pd.DataFrame:
    """Sub-window the event's pooled photon stream and classify each
    sub-window.  Returns DataFrame with one row per sub-window."""
    p = PANEL_DIR / f"{event['name']}.parquet"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p, columns=['time_us'])
    if window_end_s is None:
        window_end_s = event['t90'] + 30.0
    sub_us = int(subwindow_sec * 1_000_000)
    rows = []
    s_us = int(window_start_s * 1_000_000)
    e_us = int(window_end_s * 1_000_000)
    times = df['time_us'].to_numpy()
    for sub_start in range(s_us, e_us, sub_us):
        mask = (times >= sub_start) & (times < sub_start + sub_us)
        ev = times[mask]
        cls = classify_subwindow(ev)
        rows.append(dict(
            event=event['name'],
            sub_start_s=sub_start / 1e6,
            sub_end_s=(sub_start + sub_us) / 1e6,
            n_events=cls['n'],
            primary=cls['primary'],
            rep_med=cls['rep_med'],
            ks_gue_med=cls['ks_gue_med'],
            # store rep_int_q as a list (parquet-compatible)
            rep_int_q_list=(cls['rep_int_q'].tolist()
                              if cls['rep_int_q'] is not None else None),
        ))
    return pd.DataFrame(rows)


def qpo_comparison_row(event: dict, traj: pd.DataFrame) -> dict:
    """For an event with a published QPO claim, identify the sub-windows
    overlapping the claim window and compare the framework's reading
    at the corresponding q-band."""
    if event.get('qpo_claim_hz') is None:
        return dict(event=event['name'], qpo_claim_hz=None,
                     resolved_q=None, applicable=False)
    f_hz = event['qpo_claim_hz']
    qpo_window = event.get('qpo_window_after_t0', (0.0, event['t90']))
    qpo_lo, qpo_hi = qpo_window

    # Identify sub-windows overlapping the QPO window
    overlap = traj[(traj['sub_end_s'] > qpo_lo)
                    & (traj['sub_start_s'] < qpo_hi)]
    if overlap.empty:
        return dict(event=event['name'], qpo_claim_hz=f_hz,
                     resolved_q=None, applicable=False,
                     reason='no overlapping sub-windows')

    # Estimate event rate in QPO window: pooled event count / window duration
    rate_per_s = float(overlap['n_events'].sum()
                          / max(qpo_hi - qpo_lo, 1e-3))
    q_target = rate_per_s / f_hz
    if q_target > Q_MAX:
        return dict(event=event['name'], qpo_claim_hz=f_hz,
                     rate_per_s=rate_per_s,
                     resolved_q=q_target, applicable=False,
                     reason=f'q_target {q_target:.0f} > q_max {Q_MAX}')
    if q_target < 2:
        return dict(event=event['name'], qpo_claim_hz=f_hz,
                     rate_per_s=rate_per_s,
                     resolved_q=q_target, applicable=False,
                     reason=f'q_target {q_target:.1f} < 2 (Nyquist)')

    q_band = int(round(q_target))
    # Pull rep_int_q at q_band from each overlapping sub-window
    rep_at_qpo_q = []
    for _, row in overlap.iterrows():
        if row['rep_int_q_list'] is None:
            continue
        rq = row['rep_int_q_list']
        if q_band - 1 < len(rq):
            rep_at_qpo_q.append(float(rq[q_band - 1]))
    # Pre-onset baseline rep_int_q at same q
    pre = traj[traj['sub_end_s'] < qpo_lo]
    rep_pre = []
    for _, row in pre.iterrows():
        if row['rep_int_q_list'] is None:
            continue
        rq = row['rep_int_q_list']
        if q_band - 1 < len(rq):
            rep_pre.append(float(rq[q_band - 1]))
    return dict(
        event=event['name'],
        qpo_claim_hz=f_hz,
        qpo_reference=event.get('qpo_reference'),
        qpo_window_s=qpo_window,
        rate_per_s=rate_per_s,
        resolved_q=int(q_band),
        resolved_q_target=q_target,
        applicable=True,
        rep_med_during=float(np.nanmean(rep_at_qpo_q)) if rep_at_qpo_q else np.nan,
        rep_med_pre=float(np.nanmean(rep_pre)) if rep_pre else np.nan,
        rep_during_minus_pre=(float(np.nanmean(rep_at_qpo_q))
                                - float(np.nanmean(rep_pre)))
                                if rep_at_qpo_q and rep_pre else np.nan,
        primary_quadrants_during=str(list(overlap['primary'])),
        n_overlapping_subwindows=int(len(overlap)),
    )


def main():
    print("=" * 80)
    print("Phase 21 Tier 3 — per-event multi-resolution classification "
          "trajectory")
    print("=" * 80)

    all_traj = []
    all_qpo = []
    for event in EVENT_PANEL:
        if event['priority'] > 3:
            continue
        # Adaptive sub-window resolution by category — sized to keep
        # the total sub-window count tractable (joint_q_profile at
        # q_max=30 with cap=1500 takes ~3-5s per call; aim for <100
        # sub-windows per event).
        if event['category'] == 'extragalactic_MGF':
            subwindow_sec = 0.020   # 20 ms — MGF is ~140 ms total
            window_start = -1.0
            window_end = event['t90'] + 1.0
        elif event['name'] == 'GRB221009A':
            subwindow_sec = 10.0    # 10 s — BOAT, 300s prompt
            window_start = -30.0
            window_end = event['t90'] + 60.0
        else:
            subwindow_sec = 2.0     # 2 s for moderate-T90 events
            window_start = -30.0
            window_end = event['t90'] + 30.0
        print(f"\n  {event['name']}: sub-window={subwindow_sec}s, "
              f"window=[{window_start}, {window_end}]s rel-trig")
        t0 = time.time()
        traj = per_event_trajectory(event,
                                      subwindow_sec=subwindow_sec,
                                      window_start_s=window_start,
                                      window_end_s=window_end)
        if traj.empty:
            print(f"    (no data)")
            continue
        n_well = (traj['primary'] != 'underpowered').sum()
        print(f"    {len(traj)} sub-windows, {n_well} well-powered  "
              f"⏱{time.time()-t0:.0f}s")
        all_traj.append(traj)

        # Per-event transition characterisation (full trajectory)
        if not traj.empty:
            char = characterize_transition(traj[['primary', 'rep_med']])
            print(f"    transition shape: {char['shape_estimate']} "
                  f"(detected={char['transition_detected']}, "
                  f"origin={char.get('origin_class')}, "
                  f"destination={char.get('destination_class')})")

        # QPO-claim comparison row
        qpo_row = qpo_comparison_row(event, traj)
        print(f"    QPO claim: f={event.get('qpo_claim_hz')} Hz, "
              f"resolved_q={qpo_row.get('resolved_q')}, "
              f"applicable={qpo_row.get('applicable')}")
        if qpo_row.get('applicable'):
            print(f"      rep_med during QPO window: "
                  f"{qpo_row['rep_med_during']:.3f}")
            print(f"      rep_med pre-onset:         "
                  f"{qpo_row['rep_med_pre']:.3f}")
            print(f"      delta (during − pre):      "
                  f"{qpo_row['rep_during_minus_pre']:+.3f}")
        else:
            print(f"      reason: {qpo_row.get('reason', 'n/a')}")
        all_qpo.append(qpo_row)

    if all_traj:
        full = pd.concat(all_traj, ignore_index=True)
        # Drop the rep_int_q_list before parquet to keep file size sane;
        # store summary columns only.  We'll re-compute from raw if
        # Tier 4 needs it.
        full_save = full.drop(columns=['rep_int_q_list'])
        full_save.to_parquet(DATA / 'phase21_classification.parquet',
                              index=False)
        print(f"\n  → {DATA}/phase21_classification.parquet  "
              f"({len(full_save)} rows)")

    if all_qpo:
        qpo_df = pd.DataFrame([
            {k: (str(v) if isinstance(v, (tuple, list, dict)) else v)
             for k, v in r.items()} for r in all_qpo])
        qpo_df.to_parquet(DATA / 'phase21_qpo_comparison.parquet',
                            index=False)
        print(f"  → {DATA}/phase21_qpo_comparison.parquet")
        print()
        print(qpo_df[['event', 'qpo_claim_hz', 'resolved_q',
                       'applicable', 'rep_med_during', 'rep_med_pre',
                       'rep_during_minus_pre']].to_string(index=False))

    # Plot 60: per-event trajectories
    if all_traj:
        fig, axes = plt.subplots(len(all_traj), 1,
                                  figsize=(13, 2.0 * len(all_traj)),
                                  sharex=False)
        if len(all_traj) == 1:
            axes = [axes]
        quad_colors = {'BL': '#2ca02c', 'TR': '#1f77b4',
                        'BR_artifact': '#d62728', 'BR_novel': '#9467bd',
                        'TL': '#ff7f0e', 'underpowered': '#cccccc',
                        'ambiguous': '#888888'}
        for ax, traj in zip(axes, all_traj):
            event_name = traj['event'].iloc[0]
            for _, row in traj.iterrows():
                color = quad_colors.get(row['primary'], '#888')
                y = row['rep_med'] if not np.isnan(row['rep_med']) else 0
                width = (row['sub_end_s'] - row['sub_start_s']) * 0.9
                ax.bar(row['sub_start_s'], y, width=width, color=color,
                        edgecolor='none', align='edge')
            ax.axvline(0, color='black', ls='--', lw=1, label='T0')
            ax.set_title(f'{event_name}', fontsize=9)
            ax.set_ylabel('rep_med')
            ax.set_ylim(0, 1)
            ax.grid(alpha=0.3)
        axes[-1].set_xlabel('seconds relative to trigger')
        fig.suptitle('Phase 21 Tier 3 — per-event classification trajectory',
                      fontsize=11)
        plt.tight_layout()
        plt.savefig(PLOTS / '60_phase21_trajectory_per_event.png', dpi=130)
        plt.close()
        print(f"\n  → {PLOTS}/60_phase21_trajectory_per_event.png")


if __name__ == '__main__':
    main()
