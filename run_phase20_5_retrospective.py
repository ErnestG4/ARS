"""
run_phase20_5_retrospective.py — Phase 20.5 Tier 3.

Apply `characterize_transition` to Phase 20's per-collector BGP cascade
trajectory data, retroactively.  Tabulate per-collector transition
shape; compare across collectors.

Outputs:
  data/phase20_retrospective.parquet
  plots/58_phase20_retrospective_transitions.png
"""
from __future__ import annotations
import os, sys
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from transition_diagnostic import characterize_transition

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PLOTS.mkdir(parents=True, exist_ok=True)

EVENT_ONSET_UTC = datetime(2021, 10, 4, 15, 39, tzinfo=timezone.utc)


def main():
    p = DATA / 'phase20_classification.parquet'
    if not p.exists():
        print(f"  missing: {p}")
        return
    df = pd.read_parquet(p)
    print("=" * 80)
    print("Phase 20.5 Tier 3 — retroactive transition characterisation "
          "of BGP cascade trajectories")
    print("=" * 80)

    rows = []
    onset_us = int(EVENT_ONSET_UTC.timestamp() * 1_000_000)
    collectors = sorted(df['collector'].unique())
    per_collector_traj = {}

    for collector in collectors:
        sub = df[df['collector'] == collector].sort_values(
            'subwindow_start_us').reset_index(drop=True)
        # Apply diagnostic to full trajectory
        full = characterize_transition(sub[['primary', 'rep_med']])
        # Cascade-onset and cascade-decay halves: split at onset
        pre_onset = sub[sub['subwindow_start_us'] < onset_us].reset_index(drop=True)
        post_onset = sub[sub['subwindow_start_us'] >= onset_us].reset_index(drop=True)
        # Onset shape: pre-onset sub-windows + first half of post-onset
        n_post = len(post_onset)
        n_half = n_post // 2
        onset_traj = pd.concat([pre_onset, post_onset.iloc[:n_half]],
                                ignore_index=True)
        decay_traj = post_onset.iloc[n_half:].reset_index(drop=True)
        onset_res = characterize_transition(
            onset_traj[['primary', 'rep_med']]) if len(onset_traj) > 4 \
            else dict(transition_detected=False, shape_estimate='underpowered')
        decay_res = characterize_transition(
            decay_traj[['primary', 'rep_med']]) if len(decay_traj) > 4 \
            else dict(transition_detected=False, shape_estimate='underpowered')

        rows.append(dict(
            collector=collector,
            n_subwindows=len(sub),
            full_origin=full['origin_class'],
            full_destination=full['destination_class'],
            full_shape=full['shape_estimate'],
            full_confidence=float(full['shape_confidence']),
            full_transition_detected=bool(full['transition_detected']),
            full_metastable_class=full['metastable_state_class'],
            full_metastable_duration=full['metastable_duration'],
            full_period_doubling=bool(
                full['period_doubling_signature'] is not None),
            onset_shape=onset_res.get('shape_estimate'),
            onset_origin=onset_res.get('origin_class'),
            onset_destination=onset_res.get('destination_class'),
            decay_shape=decay_res.get('shape_estimate'),
            decay_origin=decay_res.get('origin_class'),
            decay_destination=decay_res.get('destination_class'),
        ))
        per_collector_traj[collector] = sub
        print(f"\n  {collector}:")
        print(f"    full:  origin={full['origin_class']}, "
              f"destination={full['destination_class']}, "
              f"shape={full['shape_estimate']} "
              f"(conf {full['shape_confidence']:.2f})")
        if full.get('metastable_state_class'):
            print(f"           metastable middle: "
                  f"{full['metastable_state_class']} "
                  f"({full['metastable_duration']} sub-windows)")
        print(f"    onset half: shape={onset_res.get('shape_estimate')}, "
              f"origin→dest={onset_res.get('origin_class')}→"
              f"{onset_res.get('destination_class')}")
        print(f"    decay half: shape={decay_res.get('shape_estimate')}, "
              f"origin→dest={decay_res.get('origin_class')}→"
              f"{decay_res.get('destination_class')}")

    out = pd.DataFrame(rows)
    out_path = DATA / 'phase20_retrospective.parquet'
    out.to_parquet(out_path, index=False)
    print(f"\n  → {out_path}")

    # Cross-collector shape comparison
    print()
    print("=" * 80)
    print("Cross-collector shape consistency")
    print("=" * 80)
    shapes_full = out['full_shape'].tolist()
    consistent_full = len(set(shapes_full)) == 1
    print(f"  full-window shape: "
          f"{'CONSISTENT (' + shapes_full[0] + ')' if consistent_full else 'VARIES'}: "
          f"{shapes_full}")
    onset_shapes = out['onset_shape'].tolist()
    consistent_onset = len(set(onset_shapes)) == 1
    print(f"  cascade-onset shape: "
          f"{'CONSISTENT (' + str(onset_shapes[0]) + ')' if consistent_onset else 'VARIES'}: "
          f"{onset_shapes}")
    decay_shapes = out['decay_shape'].tolist()
    consistent_decay = len(set(decay_shapes)) == 1
    print(f"  cascade-decay shape: "
          f"{'CONSISTENT (' + str(decay_shapes[0]) + ')' if consistent_decay else 'VARIES'}: "
          f"{decay_shapes}")

    # ─── Plot 58 — per-collector transition characterisation ───────────────
    fig, axes = plt.subplots(len(collectors), 1,
                              figsize=(12, 2.0 * len(collectors)),
                              sharex=False)
    if len(collectors) == 1:
        axes = [axes]
    quad_colors = {'BL': '#2ca02c', 'TR': '#1f77b4',
                    'BR_artifact': '#d62728', 'BR_novel': '#9467bd',
                    'TL': '#ff7f0e', 'underpowered': '#cccccc',
                    'ambiguous': '#888888'}
    for i, collector in enumerate(collectors):
        ax = axes[i]
        sub = per_collector_traj[collector]
        t_hours = (sub['subwindow_start_us']
                    - sub['subwindow_start_us'].min()) / (3600 * 1_000_000)
        for _, row in sub.iterrows():
            x = (row['subwindow_start_us']
                 - sub['subwindow_start_us'].min()) / (3600 * 1_000_000)
            color = quad_colors.get(row['primary'], '#888')
            y = row['rep_med'] if not np.isnan(row['rep_med']) else 0
            ax.bar(x, y, width=0.08, color=color, edgecolor='none',
                    align='edge')
        ax.axvline((onset_us - sub['subwindow_start_us'].min())
                    / (3600 * 1_000_000),
                    color='black', ls='--', lw=1)
        info = out[out['collector'] == collector].iloc[0]
        ax.set_title(f"{collector} | full: {info['full_shape']} | "
                      f"onset: {info['onset_shape']} | "
                      f"decay: {info['decay_shape']}", fontsize=10)
        ax.set_ylabel('rep_med')
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel('hours from window start (12:00 UTC Oct 4 2021)')
    fig.suptitle('Phase 20.5 Tier 3 — retroactive transition '
                  'characterisation of Phase 20 BGP cascade trajectories',
                  fontsize=11)
    plt.tight_layout()
    plt.savefig(PLOTS / '58_phase20_retrospective_transitions.png',
                 dpi=130, bbox_inches='tight')
    plt.close()
    print(f"\n  → {PLOTS}/58_phase20_retrospective_transitions.png")


if __name__ == '__main__':
    main()
