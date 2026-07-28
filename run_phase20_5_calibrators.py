"""
run_phase20_5_calibrators.py — Phase 20.5 Tier 2 calibrator validation.

Run the full blended panel + parameter-driven calibrators through the
trajectory diagnostic.  Compute shape-classification accuracy,
parameter-recovery error, period-doubling detection.

Outputs:
  data/phase20_5_calibrators.parquet
  plots/55_phase20_5_trajectory_examples.png
  plots/56_phase20_5_transition_recovery.png
  plots/57_phase20_5_period_doubling.png
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from transition_calibrators_blended import (
    enumerate_blended_panel, gen_blended_transition,
    gen_stationary_control, CLASS_PAIRS, SHAPES_TWO_STATE,
    SHAPES_THREE_STATE, CLASS_GENERATORS,
)
from transition_calibrators_dynamical import (
    logistic_iterate, logistic_iterate_swept_r, logistic_to_events,
    LOGISTIC_REGIMES, mackey_glass, mackey_glass_to_events,
    MACKEY_GLASS_EXTRACTORS, MACKEY_GLASS_REGIMES,
    logistic_period_doubling_sweep,
)
from transition_diagnostic import (
    characterize_transition, trajectory_from_events,
)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
DATA.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)

N_POINTS = 6000
N_SUBWINDOWS = 30
MIN_EVENTS_PER_SUB = 100
Q_MAX = 25


def evaluate_calibrator(spec: dict, seed: int = 0) -> dict:
    """Generate calibrator from spec, sub-window into trajectory,
    run diagnostic.  Returns flat dict for parquet."""
    rng_seed = spec.get('seed', seed)
    if spec['kind'] == 'blended_two_state':
        ev = gen_blended_transition(
            spec['origin'], spec['destination'], spec['shape'],
            n_points=N_POINTS, seed=rng_seed,
            shape_kwargs=spec.get('shape_kwargs') or {})
        true_origin = spec['origin']
        true_destination = spec['destination']
        true_shape = spec['shape']
    elif spec['kind'] == 'blended_three_state':
        ev = gen_blended_transition(
            spec['origin'], spec['destination'], spec['shape'],
            n_points=N_POINTS, seed=rng_seed,
            shape_kwargs=spec.get('shape_kwargs') or {},
            middle_class=spec.get('middle_class'))
        true_origin = spec['origin']
        true_destination = spec['destination']
        true_shape = spec['shape']    # 'metastable_middle'
    elif spec['kind'] == 'stationary':
        ev = gen_stationary_control(spec['class_name'],
                                      n_points=N_POINTS, seed=rng_seed)
        true_origin = spec['class_name']
        true_destination = spec['class_name']
        true_shape = 'stationary'
    else:
        raise ValueError(f"unknown spec kind: {spec.get('kind')}")
    traj = trajectory_from_events(ev,
                                    n_subwindows=N_SUBWINDOWS,
                                    min_events=MIN_EVENTS_PER_SUB,
                                    q_max=Q_MAX)
    res = characterize_transition(traj)
    return dict(
        name=spec['name'],
        kind=spec['kind'],
        true_origin=true_origin,
        true_destination=true_destination,
        true_shape=true_shape,
        n_events=int(ev.size),
        detected=bool(res['transition_detected']),
        origin_est=res['origin_class'],
        destination_est=res['destination_class'],
        shape_est=res['shape_estimate'],
        shape_confidence=float(res['shape_confidence']),
        transition_window_start=res['transition_window'][0],
        transition_window_end=res['transition_window'][1],
        period_doubling_detected=bool(
            res['period_doubling_signature'] is not None),
        period_doubling_ratio=(
            res['period_doubling_signature']['median_ratio']
            if res['period_doubling_signature'] else float('nan')),
        n_subwindows=res['trajectory_features'].get('n_subwindows', 0),
        monotonicity=res['trajectory_features'].get('monotonicity'),
        steepness=res['trajectory_features'].get('steepness'),
    )


def main():
    print("=" * 80)
    print("Phase 20.5 Tier 2 — calibrator validation")
    print("=" * 80)

    panel = enumerate_blended_panel(seeds=(0,))
    print(f"  blended panel: {len(panel)} entries")
    rows = []
    t_start = time.time()
    for i, spec in enumerate(panel):
        t0 = time.time()
        try:
            row = evaluate_calibrator(spec)
        except Exception as e:
            print(f"  [{i+1:3d}/{len(panel)}] {spec['name']}: FAILED {e}")
            continue
        rows.append(row)
        if (i + 1) % 8 == 0 or i == len(panel) - 1:
            tag = 'detected' if row['detected'] else 'no transition'
            print(f"  [{i+1:3d}/{len(panel)}] {row['name'][:55]:<55} "
                  f"{row['shape_est']:<22} {tag}  "
                  f"⏱{time.time()-t0:.1f}s  "
                  f"(cum {time.time()-t_start:.0f}s)")

    # Add parameter-driven calibrators
    print("\n  Logistic-map regimes:")
    for name, r, desc in LOGISTIC_REGIMES:
        x = logistic_iterate(r=r, x0=0.5, n_iter=N_POINTS)
        ev = logistic_to_events(x, mode='iei')
        if ev.size < MIN_EVENTS_PER_SUB * 5:
            print(f"  logistic {name} (r={r}): only {ev.size} events; skip")
            continue
        traj = trajectory_from_events(ev, n_subwindows=N_SUBWINDOWS,
                                        min_events=MIN_EVENTS_PER_SUB,
                                        q_max=Q_MAX)
        res = characterize_transition(traj)
        rows.append(dict(
            name=f"logistic_{name}_r={r}",
            kind='logistic_stationary',
            true_origin=name, true_destination=name, true_shape='stationary',
            n_events=int(ev.size),
            detected=bool(res['transition_detected']),
            origin_est=res['origin_class'],
            destination_est=res['destination_class'],
            shape_est=res['shape_estimate'],
            shape_confidence=float(res['shape_confidence']),
            transition_window_start=res['transition_window'][0],
            transition_window_end=res['transition_window'][1],
            period_doubling_detected=bool(
                res['period_doubling_signature'] is not None),
            period_doubling_ratio=(
                res['period_doubling_signature']['median_ratio']
                if res['period_doubling_signature'] else float('nan')),
            n_subwindows=res['trajectory_features'].get('n_subwindows', 0),
            monotonicity=res['trajectory_features'].get('monotonicity'),
            steepness=res['trajectory_features'].get('steepness'),
        ))
        print(f"    {name} (r={r}): {ev.size} events, "
              f"shape={res['shape_estimate']}, "
              f"period_doubling={res['period_doubling_signature'] is not None}")

    # Logistic period-doubling sweep
    print("\n  Logistic period-doubling sweep (r 2.5→3.9):")
    x = logistic_period_doubling_sweep(r_start=2.5, r_end=3.9,
                                          n_iter=8000, x0=0.5)
    ev = logistic_to_events(x, mode='iei')
    if ev.size > MIN_EVENTS_PER_SUB * 5:
        traj = trajectory_from_events(ev, n_subwindows=N_SUBWINDOWS * 2,
                                        min_events=MIN_EVENTS_PER_SUB,
                                        q_max=Q_MAX)
        res = characterize_transition(traj)
        rows.append(dict(
            name="logistic_sweep_2.5_to_3.9",
            kind='logistic_sweep',
            true_origin='stable_fp', true_destination='chaos',
            true_shape='period_doubling_cascade',
            n_events=int(ev.size),
            detected=bool(res['transition_detected']),
            origin_est=res['origin_class'],
            destination_est=res['destination_class'],
            shape_est=res['shape_estimate'],
            shape_confidence=float(res['shape_confidence']),
            transition_window_start=res['transition_window'][0],
            transition_window_end=res['transition_window'][1],
            period_doubling_detected=bool(
                res['period_doubling_signature'] is not None),
            period_doubling_ratio=(
                res['period_doubling_signature']['median_ratio']
                if res['period_doubling_signature'] else float('nan')),
            n_subwindows=res['trajectory_features'].get('n_subwindows', 0),
            monotonicity=res['trajectory_features'].get('monotonicity'),
            steepness=res['trajectory_features'].get('steepness'),
        ))
        pds = res['period_doubling_signature']
        if pds:
            print(f"    sweep: shape={res['shape_estimate']}, "
                  f"period_doubling median ratio = "
                  f"{pds['median_ratio']:.3f} (target 4.669)")
        else:
            print(f"    sweep: shape={res['shape_estimate']}, "
                  f"no period-doubling cascade detected")

    # Mackey-Glass regimes (one extractor for compute budget; the
    # 3-extractor consensus check is embedded in test_transition_calibrators.py)
    print("\n  Mackey-Glass regimes (envelope_upcrossings extractor):")
    for name, tau, desc in MACKEY_GLASS_REGIMES:
        x = mackey_glass(tau=tau, n_steps=N_POINTS * 2, dt=0.5, x0=1.2)
        ev = mackey_glass_to_events(x, 'envelope_upcrossings')
        if ev.size < MIN_EVENTS_PER_SUB * 3:
            # Fall back to local maxima (more events)
            ev = mackey_glass_to_events(x, 'local_maxima_prominence')
        if ev.size < MIN_EVENTS_PER_SUB * 3:
            print(f"  MG {name} (tau={tau}): {ev.size} events; skip")
            continue
        traj = trajectory_from_events(ev,
                                        n_subwindows=N_SUBWINDOWS // 2,
                                        min_events=MIN_EVENTS_PER_SUB // 4,
                                        q_max=Q_MAX)
        res = characterize_transition(traj)
        rows.append(dict(
            name=f"mackey_glass_{name}_tau={tau}",
            kind='mackey_glass_stationary',
            true_origin=name, true_destination=name, true_shape='stationary',
            n_events=int(ev.size),
            detected=bool(res['transition_detected']),
            origin_est=res['origin_class'],
            destination_est=res['destination_class'],
            shape_est=res['shape_estimate'],
            shape_confidence=float(res['shape_confidence']),
            transition_window_start=res['transition_window'][0],
            transition_window_end=res['transition_window'][1],
            period_doubling_detected=bool(
                res['period_doubling_signature'] is not None),
            period_doubling_ratio=(
                res['period_doubling_signature']['median_ratio']
                if res['period_doubling_signature'] else float('nan')),
            n_subwindows=res['trajectory_features'].get('n_subwindows', 0),
            monotonicity=res['trajectory_features'].get('monotonicity'),
            steepness=res['trajectory_features'].get('steepness'),
        ))
        print(f"    MG {name} (tau={tau}): {ev.size} events, "
              f"shape={res['shape_estimate']}")

    df = pd.DataFrame(rows)
    out = DATA / 'phase20_5_calibrators.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(df)} rows)")

    # ─── Summary stats ──────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("Validation summary")
    print("=" * 80)

    # Stationary controls: should NOT report transition_detected
    stat = df[df['true_shape'] == 'stationary']
    n_false_pos = int(stat['detected'].sum())
    print(f"  Stationary controls: {len(stat)} cells, "
          f"{n_false_pos} false-positive transitions "
          f"({100*n_false_pos/max(len(stat),1):.1f}%)")

    # Blended: shape classification accuracy (true_shape vs shape_est)
    blended = df[df['kind'].str.startswith('blended')]
    if len(blended):
        blended = blended[blended['detected']]
        # Define correct: shape_est == true_shape OR for sigmoidal/
        # exponential acceptable as 'smooth' if any of {sigmoidal,
        # exponential_approach, linear_ramp}
        smooth_shapes = {'sigmoidal', 'exponential_approach',
                          'linear_ramp', 'damped_oscillatory'}
        def correct(row):
            if row['true_shape'] == row['shape_est']:
                return True
            if (row['true_shape'] in smooth_shapes
                    and row['shape_est'] in smooth_shapes):
                return True
            return False
        blended_correct = blended.apply(correct, axis=1)
        acc = float(blended_correct.mean())
        print(f"  Blended shape accuracy (smooth-cluster grouping): "
              f"{acc*100:.1f}% ({int(blended_correct.sum())}/"
              f"{len(blended)})")

    # Period-doubling detection
    sweep_rows = df[df['kind'] == 'logistic_sweep']
    for _, row in sweep_rows.iterrows():
        print(f"  {row['name']}: "
              f"period_doubling_detected={row['period_doubling_detected']}, "
              f"ratio={row['period_doubling_ratio']:.3f} (target 4.669)")

    # Plot 55: trajectory examples
    plot_trajectory_examples(df)
    # Plot 56: transition recovery confusion
    plot_transition_recovery(df)
    # Plot 57: period-doubling
    plot_period_doubling()


def plot_trajectory_examples(df: pd.DataFrame):
    fig, axes = plt.subplots(3, 2, figsize=(13, 10))
    examples = [
        ('blend_GUE_to_Poisson_sharp_step_s0', 'Sharp step'),
        ('blend_Poisson_to_GUE_sigmoidal_s0', 'Sigmoidal'),
        ('blend_Poisson_to_TL_metastable_middle_s0', 'Metastable middle'),
        ('blend_GUE_to_TL_linear_ramp_s0', 'Linear ramp'),
        ('logistic_chaos_r=3.7', 'Logistic chaos'),
        ('logistic_sweep_2.5_to_3.9', 'Logistic sweep (period doubling)'),
    ]
    from transition_diagnostic import distance_trajectory
    from transition_calibrators_blended import (gen_blended_transition,
        gen_stationary_control)
    for ax, (name, title) in zip(axes.flat, examples):
        try:
            if name.startswith('blend_'):
                # Reconstruct trajectory from spec
                pieces = name.split('_')
                # name format: blend_<o>_to_<d>_<shape>_s<seed>
                # parse e.g. blend_GUE_to_Poisson_sharp_step_s0
                # Find 'to' in pieces
                to_idx = pieces.index('to')
                origin = pieces[1]
                destination = pieces[to_idx + 1]
                shape_parts = pieces[to_idx + 2:-1]
                shape = '_'.join(shape_parts)
                seed = int(pieces[-1].lstrip('s'))
                ev = gen_blended_transition(origin, destination, shape,
                    n_points=N_POINTS, seed=seed)
                traj = trajectory_from_events(ev,
                    n_subwindows=N_SUBWINDOWS,
                    min_events=MIN_EVENTS_PER_SUB,
                    q_max=Q_MAX)
            elif name == 'logistic_chaos_r=3.7':
                x = logistic_iterate(r=3.7, x0=0.5, n_iter=N_POINTS)
                ev = logistic_to_events(x, mode='iei')
                traj = trajectory_from_events(ev,
                    n_subwindows=N_SUBWINDOWS,
                    min_events=MIN_EVENTS_PER_SUB,
                    q_max=Q_MAX)
            elif name == 'logistic_sweep_2.5_to_3.9':
                x = logistic_period_doubling_sweep(2.5, 3.9, 8000, 0.5)
                ev = logistic_to_events(x, mode='iei')
                traj = trajectory_from_events(ev,
                    n_subwindows=N_SUBWINDOWS * 2,
                    min_events=MIN_EVENTS_PER_SUB,
                    q_max=Q_MAX)
            else:
                ax.set_title(f'{title} (skipped)')
                continue
            primaries = list(traj['primary'])
            origin = primaries[0] if primaries else 'BL'
            d = distance_trajectory(primaries, origin)
            ax.plot(d, marker='o', markersize=3, linewidth=1)
            ax.set_title(f'{title}\n({name[:50]})', fontsize=9)
            ax.set_xlabel('sub-window index')
            ax.set_ylabel('distance from origin')
            ax.grid(alpha=0.3)
        except Exception as e:
            ax.text(0.5, 0.5, f'failed: {e}', transform=ax.transAxes,
                    ha='center', fontsize=9)
            ax.set_title(title)
    plt.tight_layout()
    plt.savefig(PLOTS / '55_phase20_5_trajectory_examples.png', dpi=130)
    plt.close()
    print(f"  → {PLOTS}/55_phase20_5_trajectory_examples.png")


def plot_transition_recovery(df: pd.DataFrame):
    """Confusion-matrix-style heatmap: true shape × estimated shape."""
    blended = df[df['kind'].str.startswith('blended')]
    if blended.empty:
        return
    true_shapes = sorted(blended['true_shape'].unique())
    est_shapes = sorted(blended['shape_est'].unique())
    M = np.zeros((len(true_shapes), len(est_shapes)), dtype=int)
    for i, ts in enumerate(true_shapes):
        for j, es in enumerate(est_shapes):
            M[i, j] = int(((blended['true_shape'] == ts)
                            & (blended['shape_est'] == es)).sum())
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(M, aspect='auto', cmap='Blues')
    ax.set_xticks(range(len(est_shapes)))
    ax.set_xticklabels(est_shapes, rotation=20, ha='right', fontsize=9)
    ax.set_yticks(range(len(true_shapes)))
    ax.set_yticklabels(true_shapes, fontsize=9)
    ax.set_xlabel('estimated shape')
    ax.set_ylabel('true shape')
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if M[i, j]:
                ax.text(j, i, str(M[i, j]), ha='center', va='center',
                        color='white' if M[i, j] > M.max() / 2 else 'black')
    ax.set_title('Phase 20.5 Tier 2 — shape recovery confusion matrix')
    plt.colorbar(im, ax=ax, label='count')
    plt.tight_layout()
    plt.savefig(PLOTS / '56_phase20_5_transition_recovery.png', dpi=130)
    plt.close()
    print(f"  → {PLOTS}/56_phase20_5_transition_recovery.png")


def plot_period_doubling():
    """Logistic map sweep across r showing period-doubling cascade."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 7))
    # Bifurcation-like view: x_n vs r
    ax = axes[0]
    rs = np.linspace(2.8, 4.0, 600)
    for r in rs:
        x = logistic_iterate(r=r, x0=0.5, n_iter=200, discard=500)
        ax.plot([r] * x.size, x, 'k.', markersize=0.3, alpha=0.3)
    ax.set_xlabel('r')
    ax.set_ylabel('x_n (after transient)')
    ax.set_title('Logistic map bifurcation diagram')
    ax.grid(alpha=0.3)
    # Sweep trajectory diagnostic distance
    ax = axes[1]
    x = logistic_period_doubling_sweep(2.5, 3.9, 8000, 0.5)
    ev = logistic_to_events(x, mode='iei')
    traj = trajectory_from_events(ev, n_subwindows=N_SUBWINDOWS * 2,
                                    min_events=MIN_EVENTS_PER_SUB,
                                    q_max=Q_MAX)
    from transition_diagnostic import distance_trajectory
    primaries = list(traj['primary'])
    origin = primaries[0] if primaries else 'BL'
    d = distance_trajectory(primaries, origin)
    ax.plot(d, marker='o', markersize=3)
    ax.set_xlabel('sub-window index (along r=2.5→3.9 sweep)')
    ax.set_ylabel('distance from origin classification')
    ax.set_title('Trajectory diagnostic: distance from origin '
                  'across logistic sweep')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS / '57_phase20_5_period_doubling.png', dpi=130)
    plt.close()
    print(f"  → {PLOTS}/57_phase20_5_period_doubling.png")


if __name__ == '__main__':
    main()
