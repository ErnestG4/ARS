"""
run_phase20_classification.py — Phase 20 Tier 3.

Per-collector temporal classification trajectory across the event window.

Produces:

  - 144 5-minute sub-window classifications per collector × 4 collectors
    = 576 cells.
  - Per-collector trajectory descriptors:
      * cascade arrival time (first sub-window after 15:39 UTC where
        primary quadrant differs from quiescent baseline)
      * cascade depth (max classification distance from quiescent)
      * cascade duration (number of consecutive sub-windows away from
        quiescent before return)
  - Topology-trajectory R² correlation against per-collector AS-distance
    to AS 32934.

Outputs:
  data/phase20_classification.parquet
  plots/55_phase20_trajectory_per_collector.png
  plots/56_phase20_topology_vs_trajectory.png
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from bgp_pipeline import COLLECTORS, WINDOWS, load_cell_parquet, \
    cell_parquet_exists

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PARQUET_ROOT = DATA / 'phase20_facebook_2021'
TOPO_FILE = DATA / 'phase20_topology' / 'per_collector_distance.parquet'

Q_MAX = 60
MIN_EVENTS = 30
SUBWINDOW_SECONDS = 5 * 60

# Reference moment: Facebook outage onset at ~15:39 UTC, 2021-10-04.
EVENT_ONSET_UTC = datetime(2021, 10, 4, 15, 39, tzinfo=timezone.utc)


def unfold_unit_mean(t: np.ndarray) -> np.ndarray:
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def primary_quadrant(events):
    if events.size < MIN_EVENTS:
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    counts = well['quadrant'].value_counts()
    return (str(counts.idxmax()),
            float(well['rep_int_q'].median()),
            float(well['ks_gue_q'].median()),
            int(events.size))


def classify_event_window(parquet_path: Path,
                            window_start_us: int,
                            window_end_us: int,
                            subwindow_us: int,
                            ) -> pd.DataFrame:
    """Apply joint_q_profile per 5-minute sub-window across the event
    window."""
    df = load_cell_parquet(parquet_path, columns=['timestamp_us'])
    if len(df) == 0:
        return pd.DataFrame()
    ts = df['timestamp_us'].to_numpy()
    rows = []
    for s in range(window_start_us, window_end_us, subwindow_us):
        e = s + subwindow_us
        mask = (ts >= s) & (ts < e)
        ev = ts[mask].astype(np.float64) / 1_000_000
        if ev.size < MIN_EVENTS:
            rows.append(dict(subwindow_start_us=s, n_events=int(ev.size),
                              primary='underpowered',
                              rep_med=float('nan'),
                              ks_gue_med=float('nan')))
            continue
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        rows.append(dict(subwindow_start_us=s, n_events=int(ev.size),
                          primary=primary, rep_med=rep, ks_gue_med=ks))
    return pd.DataFrame(rows)


def quadrant_distance(quadrant: str, baseline: str) -> float:
    """Symbolic distance between quadrant labels: 0 if same, 1 if
    different (and both well-powered).  NaN if either is
    underpowered/ambiguous."""
    if quadrant in ('underpowered', 'ambiguous') or \
       baseline in ('underpowered', 'ambiguous'):
        return float('nan')
    return 0.0 if quadrant == baseline else 1.0


def trajectory_descriptors(traj: pd.DataFrame,
                            baseline_quadrant: str,
                            baseline_rep_med: float,
                            event_onset_us: int,
                            ) -> dict:
    """Cascade arrival time, depth, duration."""
    # Symbolic cascade distance: rep_med - baseline (numeric metric)
    rep_dev = (traj['rep_med'] - baseline_rep_med).abs()
    quad_dev = traj['primary'].apply(
        lambda x: quadrant_distance(x, baseline_quadrant))
    after_onset = traj['subwindow_start_us'] >= event_onset_us
    onset_idx = traj.index[after_onset & (quad_dev > 0)]
    arrival_us = (int(traj.loc[onset_idx[0], 'subwindow_start_us'])
                   if len(onset_idx) else None)
    arrival_minutes = (
        (arrival_us - event_onset_us) / 60_000_000
        if arrival_us is not None else None)
    cascade_depth = float(rep_dev.max())
    # Duration: longest consecutive run of away-from-baseline sub-windows
    away = (quad_dev > 0).astype(int).values
    if away.sum() == 0:
        duration_subwins = 0
    else:
        run_lens = []
        cur = 0
        for x in away:
            if x:
                cur += 1
            else:
                if cur > 0:
                    run_lens.append(cur)
                cur = 0
        if cur > 0:
            run_lens.append(cur)
        duration_subwins = max(run_lens) if run_lens else 0
    return dict(
        cascade_arrival_minutes=arrival_minutes,
        cascade_depth_rep_dev=cascade_depth,
        cascade_duration_subwindows=int(duration_subwins),
        n_subwindows_away=int(away.sum()),
        n_subwindows_total=int(len(away)),
    )


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)

    win = WINDOWS['event']
    win_start_us = int(win['start'].timestamp() * 1_000_000)
    win_end_us = int(win['end'].timestamp() * 1_000_000)
    subwindow_us = SUBWINDOW_SECONDS * 1_000_000
    onset_us = int(EVENT_ONSET_UTC.timestamp() * 1_000_000)

    print("=" * 80)
    print(f"Phase 20 Tier 3 — temporal trajectory classification")
    print(f"  event window: {win['start']} → {win['end']}")
    print(f"  sub-window: {SUBWINDOW_SECONDS}s, "
          f"q_max={Q_MAX}, min_events={MIN_EVENTS}")
    print("=" * 80)

    # 1. Per-collector quiescent baseline classification
    baselines = {}
    for collector in COLLECTORS:
        p = PARQUET_ROOT / f"{collector}_quiescent.parquet"
        if not cell_parquet_exists(p):
            print(f"  {collector}: quiescent parquet missing")
            continue
        df = load_cell_parquet(p, columns=['timestamp_us'])
        ev = df['timestamp_us'].to_numpy(dtype=np.float64) / 1_000_000
        # Subsample for speed
        if ev.size > 10_000:
            ev = ev[::max(1, ev.size // 10_000)]
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        baselines[collector] = dict(primary=primary, rep_med=rep,
                                      ks_gue_med=ks, n=n)
        print(f"  {collector} BASELINE: n={n:,} primary={primary} "
              f"rep_med={rep:.3f}")

    # 2. Per-collector event-window trajectory
    print()
    rows = []
    trajectories = {}
    for collector in COLLECTORS:
        p = PARQUET_ROOT / f"{collector}_event.parquet"
        if not cell_parquet_exists(p):
            print(f"  {collector}/event: parquet missing")
            continue
        t0 = time.time()
        traj = classify_event_window(p, win_start_us, win_end_us,
                                       subwindow_us)
        if traj.empty:
            print(f"  {collector}/event: empty trajectory")
            continue
        traj['collector'] = collector
        rows.append(traj)
        trajectories[collector] = traj
        n_well = (traj['primary'] != 'underpowered').sum()
        print(f"  {collector}/event: {len(traj)} sub-windows, "
              f"{n_well} well-powered  ⏱{time.time() - t0:.0f}s")

    if not rows:
        print("\n  no trajectories; cannot proceed")
        return
    full = pd.concat(rows, ignore_index=True)
    full.to_parquet(DATA / 'phase20_classification.parquet', index=False)
    print(f"\n  → {DATA}/phase20_classification.parquet")

    # 3. Trajectory descriptors per collector
    print("\n" + "=" * 80)
    print("Trajectory descriptors per collector")
    print("=" * 80)
    desc_rows = []
    for collector, traj in trajectories.items():
        if collector not in baselines:
            continue
        b = baselines[collector]
        d = trajectory_descriptors(traj, b['primary'], b['rep_med'],
                                     onset_us)
        d['collector'] = collector
        d['baseline_primary'] = b['primary']
        desc_rows.append(d)
        print(f"  {collector}: arrival={d['cascade_arrival_minutes']} min, "
              f"depth={d['cascade_depth_rep_dev']:.3f}, "
              f"duration={d['cascade_duration_subwindows']} sub-windows "
              f"(of {d['n_subwindows_total']}), "
              f"away={d['n_subwindows_away']}")
    desc_df = pd.DataFrame(desc_rows)
    desc_df.to_parquet(DATA / 'phase20_trajectory_descriptors.parquet',
                        index=False)

    # 4. Topology-trajectory correlation
    print("\n" + "=" * 80)
    print("Topology vs trajectory correlation")
    print("=" * 80)
    if not TOPO_FILE.exists():
        print(f"  topology file missing: {TOPO_FILE}")
        topo_df = None
    else:
        topo_df = pd.read_parquet(TOPO_FILE)
        merged = desc_df.merge(topo_df, on='collector', how='left')
        for descriptor in ('cascade_arrival_minutes',
                            'cascade_depth_rep_dev',
                            'cascade_duration_subwindows'):
            mask = (~merged[descriptor].isna()) \
                   & (~merged['median_distance'].isna())
            if mask.sum() < 2:
                print(f"  {descriptor}: insufficient data for R²")
                continue
            x = merged.loc[mask, 'median_distance'].to_numpy()
            y = merged.loc[mask, descriptor].astype(float).to_numpy()
            if x.std() == 0 or y.std() == 0:
                r2 = float('nan')
            else:
                r = np.corrcoef(x, y)[0, 1]
                r2 = float(r ** 2)
            print(f"  {descriptor:<32} vs median_distance:  R²={r2:.3f}")

    # 5. Plot 55 — per-collector trajectory
    print("\n  plotting…")
    fig, axes = plt.subplots(len(trajectories), 1,
                              figsize=(13, 2.0 * len(trajectories)),
                              sharex=True)
    if len(trajectories) == 1:
        axes = [axes]
    quad_colors = {'BL': '#2ca02c', 'TR': '#1f77b4',
                    'BR_artifact': '#d62728', 'BR_novel': '#9467bd',
                    'TL': '#ff7f0e', 'underpowered': '#cccccc',
                    'ambiguous': '#888888'}
    for i, (collector, traj) in enumerate(trajectories.items()):
        ax = axes[i]
        t_hours = (traj['subwindow_start_us'] - win_start_us) \
                  / (3600 * 1_000_000)
        # Bar plot of rep_med colored by primary
        for _, row in traj.iterrows():
            x = (row['subwindow_start_us'] - win_start_us) \
                / (3600 * 1_000_000)
            color = quad_colors.get(row['primary'], '#888')
            y = row['rep_med'] if not np.isnan(row['rep_med']) else 0
            ax.bar(x, y, width=SUBWINDOW_SECONDS / 3600, color=color,
                    edgecolor='none', align='edge')
        ax.set_ylabel(collector, fontsize=9)
        ax.set_ylim(0, 1)
        ax.axvline((onset_us - win_start_us) / (3600 * 1_000_000),
                    color='black', ls='--', lw=1, label='15:39 UTC onset')
        ax.grid(alpha=0.3)
        if i == 0:
            ax.legend(loc='upper right', fontsize=8)
    axes[-1].set_xlabel('hours from window start (12:00 UTC Oct 4)')
    fig.suptitle('Phase 20 Tier 3 — temporal classification trajectory '
                  'per collector (rep_med colored by primary quadrant)',
                  fontsize=11)
    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=l) for l, c in quad_colors.items()]
    fig.legend(handles=handles, loc='lower right',
                bbox_to_anchor=(1.0, 0.0), fontsize=8, ncol=4)
    plt.tight_layout()
    plt.savefig(PLOTS / '55_phase20_trajectory_per_collector.png',
                 dpi=130, bbox_inches='tight')
    plt.close()
    print(f"  → {PLOTS}/55_phase20_trajectory_per_collector.png")

    # 6. Plot 56 — topology vs trajectory descriptors
    if topo_df is not None and len(desc_df) >= 2:
        merged = desc_df.merge(topo_df, on='collector', how='left')
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        for ax, desc in zip(axes, ['cascade_arrival_minutes',
                                     'cascade_depth_rep_dev',
                                     'cascade_duration_subwindows']):
            mask = (~merged[desc].isna()) \
                   & (~merged['median_distance'].isna())
            if mask.sum() < 2:
                ax.text(0.5, 0.5, 'insufficient data',
                         transform=ax.transAxes, ha='center')
                ax.set_title(desc, fontsize=10)
                continue
            x = merged.loc[mask, 'median_distance'].to_numpy()
            y = merged.loc[mask, desc].astype(float).to_numpy()
            ax.scatter(x, y, s=80)
            for _, row in merged[mask].iterrows():
                ax.annotate(row['collector'],
                             (row['median_distance'], float(row[desc])),
                             fontsize=7, alpha=0.7)
            if x.std() > 0 and y.std() > 0:
                r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
                ax.set_title(f'{desc}\nR²={r2:.3f}', fontsize=10)
            else:
                ax.set_title(desc, fontsize=10)
            ax.set_xlabel('median AS-hop distance to AS32934')
            ax.grid(alpha=0.3)
        fig.suptitle('Phase 20 Tier 3 — topology vs cascade trajectory',
                      fontsize=11)
        plt.tight_layout()
        plt.savefig(PLOTS / '56_phase20_topology_vs_trajectory.png',
                     dpi=130)
        plt.close()
        print(f"  → {PLOTS}/56_phase20_topology_vs_trajectory.png")


if __name__ == '__main__':
    main()
