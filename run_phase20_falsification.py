"""
run_phase20_falsification.py — Phase 20 Tier 4.

Apply Phase 18 surrogates plus the topology-aware Hawkes surrogate to
the per-collector cascade-peak classification.  The headline question
is whether topology-aware Hawkes reproduces the empirical per-collector
trajectory; if yes, the cascade-shape signature reduces to "BGP follows
topology-aware Hawkes dynamics" (no separate dynamical-system finding).
If no, the gap is the structural finding.

Pipeline:

  1. Identify cascade-peak sub-window per collector (from Tier 3
     trajectory data).
  2. Apply Phase 18 surrogates (hawkes_matched, phase_randomized_iei,
     cumulant_matched) to the cascade-peak event sequence per collector.
     Compare classifications.
  3. Build topology-aware Hawkes fit per AS-distance bin from the
     event-window data.
  4. Verify topology-aware Hawkes recovers parameters on synthetic
     ground truth (acceptance test: ≤ 15% rate error on the high-rate
     bins).
  5. Per collector: simulate topology-aware Hawkes weighted by that
     collector's per-bin peer fraction.  Sub-window the synthetic to
     5-min slices and run joint_q_profile.  Compare to empirical
     trajectory.

Outputs:
  data/phase20_falsification.parquet
  plots/57_phase20_surrogate_survival.png
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
from dfa import dfa_hurst
from surrogates import (
    phase_randomized_iei_events,
    hawkes_matched_events,
    cumulant_matched_events,
)
from topology_hawkes import (
    fit_topology_hawkes, per_collector_bin_weights, simulate_collector,
    verify_topology_kernel_recovery, DEFAULT_DISTANCE_BINS,
)
from as_topology import (
    load_as_graph, bfs_distances_from, FACEBOOK_AS,
    peer_asns_from_parquet,
)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = Path(THIS_DIR) / 'data'
PLOTS = Path(THIS_DIR) / 'plots'
PARQUET_ROOT = DATA / 'phase20_facebook_2021'
TOPO_FILE = DATA / 'phase20_topology' / 'caida_as_rel_20211001.txt.bz2'

Q_MAX = 60
MIN_EVENTS = 30
SUBWINDOW_SECONDS = 5 * 60
EVENT_ONSET_UTC = datetime(2021, 10, 4, 15, 39, tzinfo=timezone.utc)


JPF_CAP = 5000   # joint_q_profile event cap (matches Tier 2/3)


def unfold_unit_mean(t, cap: int = JPF_CAP):
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
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


def classify_per_subwindow(events_seconds: np.ndarray,
                             window_start_sec: float,
                             window_end_sec: float,
                             subwindow_sec: float = SUBWINDOW_SECONDS,
                             ) -> pd.DataFrame:
    rows = []
    s = window_start_sec
    while s < window_end_sec:
        e = s + subwindow_sec
        mask = (events_seconds >= s) & (events_seconds < e)
        ev = events_seconds[mask]
        if ev.size < MIN_EVENTS:
            rows.append(dict(subwindow_start_us=int(s * 1_000_000),
                              n_events=int(ev.size),
                              primary='underpowered',
                              rep_med=float('nan'),
                              ks_gue_med=float('nan')))
            s = e
            continue
        ev_unit = unfold_unit_mean(ev)
        primary, rep, ks, n = primary_quadrant(ev_unit)
        rows.append(dict(subwindow_start_us=int(s * 1_000_000),
                          n_events=int(ev.size),
                          primary=primary, rep_med=rep,
                          ks_gue_med=ks))
        s = e
    return pd.DataFrame(rows)


def main():
    PLOTS.mkdir(parents=True, exist_ok=True)

    # 1. Topology-aware Hawkes synthetic-recovery acceptance check
    print("=" * 80)
    print("Tier 4.0 — verify topology-aware Hawkes on synthetic ground truth")
    print("=" * 80)
    rec = verify_topology_kernel_recovery(seed=0, T=4000.0)
    print("  per-bin recovery error:")
    for e in rec['errors']:
        print(f"    bin {e['bin']}: rate {e['rate_hat']:.3f} vs "
              f"{e['rate_true']:.3f} (rel err {e['rel_rate_err']:.3f})")
    high_rate_err = max(e['rel_rate_err'] for e in rec['errors'][:2])
    if high_rate_err > 0.15:
        print(f"  ⚠ high-rate-bin recovery exceeds 15% (max err "
              f"{high_rate_err:.3f}); proceeding with caveat")
    else:
        print(f"  ✓ high-rate-bin recovery within 15%")

    # 2. Load AS graph and per-collector peer-distance maps
    print("\n" + "=" * 80)
    print("Tier 4.1 — load AS graph and per-collector peer distances")
    print("=" * 80)
    if not TOPO_FILE.exists():
        print("  AS graph file missing; cannot run topology-aware Hawkes")
        return
    g = load_as_graph(TOPO_FILE)
    dist_map = bfs_distances_from(g, FACEBOOK_AS, max_distance=10)
    print(f"  AS graph: {len(g):,} ASNs; "
          f"reachable from AS{FACEBOOK_AS}: {len(dist_map):,}")

    # Per-collector peer-bin weights
    per_collector_weights = {}
    for collector in COLLECTORS:
        p = PARQUET_ROOT / f"{collector}_event.parquet"
        if not cell_parquet_exists(p):
            print(f"  {collector}: event parquet missing; skipping")
            continue
        peers = peer_asns_from_parquet(p)
        w = per_collector_bin_weights(peers, dist_map,
                                        DEFAULT_DISTANCE_BINS)
        per_collector_weights[collector] = w
        print(f"  {collector}: {len(peers)} peer ASNs, bin weights "
              f"{w.round(3).tolist()}")

    # 3. Fit topology-aware Hawkes from pooled event-window data
    print("\n" + "=" * 80)
    print("Tier 4.2 — fit topology-aware Hawkes (pooled across collectors)")
    print("=" * 80)
    pooled_chunks = []
    for collector in COLLECTORS:
        p = PARQUET_ROOT / f"{collector}_event.parquet"
        if cell_parquet_exists(p):
            chunk = load_cell_parquet(p, columns=['timestamp_us',
                                                     'peer_asn'])
            pooled_chunks.append(chunk)
    if not pooled_chunks:
        print("  no event-window data; aborting")
        return
    pooled = pd.concat(pooled_chunks, ignore_index=True)
    print(f"  pooled events: {len(pooled):,}")
    win_start_sec = WINDOWS['event']['start'].timestamp()
    win_end_sec = WINDOWS['event']['end'].timestamp()
    T_event = float(win_end_sec - win_start_sec)
    # Pre-restrict pooled events to the cascade-onset ±2-hour window
    # to focus the Hawkes fit on the cascade dynamics rather than
    # baseline.  Onset is 15:39 UTC; window 13:39–17:39 UTC.
    onset_sec = EVENT_ONSET_UTC.timestamp()
    cascade_lo = int((onset_sec - 2 * 3600) * 1_000_000)
    cascade_hi = int((onset_sec + 2 * 3600) * 1_000_000)
    cascade_pooled = pooled[(pooled['timestamp_us'] >= cascade_lo)
                              & (pooled['timestamp_us'] < cascade_hi)]
    print(f"  cascade-window events (±2h around onset): "
          f"{len(cascade_pooled):,}")
    T_cascade = 4 * 3600.0
    fit = fit_topology_hawkes(cascade_pooled, dist_map,
                                distance_bins=DEFAULT_DISTANCE_BINS,
                                T_window_seconds=T_cascade,
                                max_events_per_bin=10_000)
    print("  per-bin fit:")
    for i, (mu, a, b) in enumerate(fit['per_bin_params']):
        rate = mu / max(1 - a / b, 1e-9) if b > 0 else 0
        print(f"    bin {i} [{fit['bin_edges'][i]}-"
              f"{fit['bin_edges'][i + 1]}]: "
              f"μ={mu:.3f} α={a:.3f} β={b:.3f} "
              f"rate={rate:.3f} n={fit['per_bin_n_events'][i]:,}")

    # 4. Identify cascade-peak sub-window per collector and apply
    #    Phase 18 surrogates
    print("\n" + "=" * 80)
    print("Tier 4.3 — Phase 18 surrogates on cascade peak per collector")
    print("=" * 80)
    rows = []
    onset_us = int(EVENT_ONSET_UTC.timestamp() * 1_000_000)
    classification_path = DATA / 'phase20_classification.parquet'
    if not classification_path.exists():
        print(f"  classification file missing; cascade-peak ID needs Tier 3")
        return
    cls_df = pd.read_parquet(classification_path)
    for collector in COLLECTORS:
        sub = cls_df[cls_df['collector'] == collector]
        if sub.empty:
            continue
        post_onset = sub[sub['subwindow_start_us'] >= onset_us]
        if post_onset.empty:
            continue
        # Cascade-peak: sub-window with highest n_events post-onset
        peak_idx = post_onset['n_events'].idxmax()
        peak_row = sub.loc[peak_idx]
        peak_us = int(peak_row['subwindow_start_us'])
        # Pull events for this 5-min window
        p = PARQUET_ROOT / f"{collector}_event.parquet"
        df = load_cell_parquet(p, columns=['timestamp_us'])
        ts = df['timestamp_us'].to_numpy()
        peak_events = ts[(ts >= peak_us)
                          & (ts < peak_us + SUBWINDOW_SECONDS * 1_000_000)]
        peak_events_sec = peak_events.astype(np.float64) / 1_000_000
        if peak_events_sec.size < MIN_EVENTS:
            continue
        # Original
        ev_unit = unfold_unit_mean(peak_events_sec)
        orig_q, orig_rep, orig_ks, orig_n = primary_quadrant(ev_unit)
        rows.append(dict(collector=collector, surrogate='ORIGINAL',
                          primary=orig_q, rep_med=orig_rep,
                          ks_gue_med=orig_ks, n=orig_n,
                          peak_us=peak_us))
        print(f"  {collector} peak (n={orig_n:,}): {orig_q} "
              f"rep={orig_rep:.3f}")
        # Phase 18 surrogates on the cascade-peak event sequence.
        # `hawkes_matched_events` is excluded for Phase 20: its
        # unconstrained ML fit on the cascade-peak window converges to
        # the same numerically pathological regime documented in
        # `topology_hawkes.fit_topology_hawkes`'s sanity-guard branch
        # (μ ≈ 1e-130, α/β both ≈ 1e305), and the resulting Ogata
        # simulation enters an effectively non-terminating loop where
        # λ_bar is extreme and inter-event waits collapse to ~0.  The
        # remaining two Phase 18 surrogates (phase_randomized_iei,
        # cumulant_matched) plus the topology-aware Hawkes (which
        # *does* have the guard) cover the falsification dimensions
        # the Phase 20 verdict map requires.
        for surr_name, surr_fn in [
                ('phase_randomized_iei', phase_randomized_iei_events),
                ('cumulant_matched',      cumulant_matched_events)]:
            for seed in range(3):
                rng = np.random.default_rng(seed * 100
                                              + abs(hash(surr_name)) % 50000)
                try:
                    surr_ev = surr_fn(peak_events_sec, rng=rng)
                except Exception as e:
                    rows.append(dict(collector=collector,
                                      surrogate=surr_name, seed=seed,
                                      primary='error', rep_med=float('nan'),
                                      ks_gue_med=float('nan'), n=0,
                                      peak_us=peak_us))
                    continue
                surr_unit = unfold_unit_mean(surr_ev)
                primary, rep, ks, n = primary_quadrant(surr_unit)
                rows.append(dict(collector=collector,
                                  surrogate=surr_name, seed=seed,
                                  primary=primary, rep_med=rep,
                                  ks_gue_med=ks, n=n,
                                  peak_us=peak_us))
            print(f"    {surr_name:<22} (3 seeds): "
                   f"primaries = {[r['primary'] for r in rows[-3:]]}")

    # 5. Topology-aware Hawkes per-collector synthetic
    print("\n" + "=" * 80)
    print("Tier 4.4 — topology-aware Hawkes per-collector synthetic")
    print("=" * 80)
    # Simulate over the cascade window (4 hours around onset), which
    # matches the Hawkes-fit window.  Per-collector projection thins
    # global synthetic events by the collector's per-bin peer fraction.
    for collector in per_collector_weights:
        w = per_collector_weights[collector]
        for seed in range(3):
            rng = np.random.default_rng(seed * 1000 + 42)
            t0 = time.time()
            sim = simulate_collector(fit, w, T_cascade, rng)
            if sim.size < MIN_EVENTS:
                continue
            # Trajectory at sub-window resolution; the synthetic time
            # axis is [0, T_cascade], with the synthetic "onset" at
            # the centre of the cascade window (i.e., 2h offset).
            traj = classify_per_subwindow(sim, 0.0, T_cascade,
                                            SUBWINDOW_SECONDS)
            onset_offset = 2 * 3600.0   # synthetic onset at +2h
            post_onset_traj = traj[traj['subwindow_start_us']
                                     >= int(onset_offset * 1_000_000)]
            if post_onset_traj.empty:
                continue
            valid = post_onset_traj[post_onset_traj['primary']
                                      != 'underpowered']
            if valid.empty:
                continue
            peak_idx = valid['n_events'].idxmax()
            peak = valid.loc[peak_idx]
            rows.append(dict(collector=collector,
                              surrogate='topology_hawkes', seed=seed,
                              primary=peak['primary'],
                              rep_med=float(peak['rep_med']),
                              ks_gue_med=float(peak['ks_gue_med']),
                              n=int(peak['n_events']),
                              peak_us=int(peak['subwindow_start_us'])))
            print(f"  {collector} seed={seed}: synthetic peak primary="
                  f"{peak['primary']} rep={peak['rep_med']:.3f} "
                  f"n={peak['n_events']:,}  ⏱{time.time() - t0:.0f}s")

    df_out = pd.DataFrame(rows)
    out_path = DATA / 'phase20_falsification.parquet'
    df_out.to_parquet(out_path, index=False)
    print(f"\n  → {out_path}")

    # ─── Verdict map (Delta 2 — revised vs original) ─────────────────
    print("\n" + "=" * 80)
    print("Tier 4 verdict map (Delta-revised — Kitsak/Matcharashvili-aware)")
    print("=" * 80)
    # Compute per-collector survival summary from the rows we just wrote
    by_col = df_out.groupby(['collector', 'surrogate']).agg(
        primary_mode=('primary', lambda x: x.mode().iloc[0]
                        if not x.mode().empty else 'n/a'),
        rep_median=('rep_med', 'median'),
    ).reset_index()
    # ORIGINAL-vs-surrogate comparison per collector
    verdict_inputs = {}
    for collector in df_out['collector'].unique():
        sub = by_col[by_col['collector'] == collector]
        orig_row = sub[sub['surrogate'] == 'ORIGINAL']
        topo_row = sub[sub['surrogate'] == 'topology_hawkes']
        if orig_row.empty:
            continue
        orig_q = orig_row['primary_mode'].iloc[0]
        topo_q = topo_row['primary_mode'].iloc[0] if not topo_row.empty \
                 else None
        verdict_inputs[collector] = dict(orig=orig_q, topo=topo_q)
    print("  per-collector:")
    for c, v in verdict_inputs.items():
        print(f"    {c:<22} ORIGINAL={v['orig']}  topology_hawkes={v['topo']}")

    # Apply the revised verdict map heuristically — the writeup section
    # makes the final verdict call.  We just emit the inputs.
    n_distinct_orig = len({v['orig'] for v in verdict_inputs.values()
                             if v['orig'] not in (None, 'n/a',
                                                   'underpowered')})
    topo_matches_orig = sum(1 for v in verdict_inputs.values()
                              if v['orig'] == v['topo']
                              and v['orig'] not in (None, 'n/a',
                                                     'underpowered'))
    print()
    print(f"  distinct ORIGINAL classifications across collectors: "
          f"{n_distinct_orig}")
    print(f"  collectors where topology_hawkes matches ORIGINAL: "
          f"{topo_matches_orig}/{len(verdict_inputs)}")
    if n_distinct_orig <= 1:
        print("  → 'synchronised classifications across collectors' "
              "(verdict candidate: methodology too coarse OR negative)")
    elif topo_matches_orig == len(verdict_inputs):
        print("  → 'topology-aware Hawkes accounts for everything' "
              "(verdict candidate: methodological note, no full study)")
    else:
        print("  → 'cascade trajectory distinct, topology-aware Hawkes "
              "differs' (verdict candidate: real finding — but only if "
              "Tier 3 trajectory shows topological correlation, AND if "
              "the joint-plane reading distinguishes cascade dynamics "
              "from baseline beyond what Kitsak/Matcharashvili measures "
              "already capture; see §7.ter.27 Relation-to-prior-work)")

    # 6. Plot 57 — surrogate survival summary
    if not df_out.empty:
        fig, ax = plt.subplots(figsize=(11, 5))
        # group by (collector, surrogate); aggregate
        agg = df_out.groupby(['collector', 'surrogate']).agg(
            primary_mode=('primary', lambda x: x.mode().iloc[0]
                            if not x.mode().empty else 'n/a'),
            rep_median=('rep_med', 'median'),
        ).reset_index()
        # Pivot
        labels = ['ORIGINAL', 'phase_randomized_iei', 'hawkes_matched',
                   'cumulant_matched', 'topology_hawkes']
        collectors = sorted(agg['collector'].unique())
        x = np.arange(len(collectors))
        width = 0.16
        for i, lab in enumerate(labels):
            sub = agg[agg['surrogate'] == lab]
            vals = [float(sub[sub['collector'] == c]['rep_median'].iloc[0])
                    if not sub[sub['collector'] == c].empty else float('nan')
                    for c in collectors]
            ax.bar(x + i * width, vals, width=width, label=lab)
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(collectors, rotation=20, ha='right', fontsize=9)
        ax.set_ylabel('rep_med at cascade peak')
        ax.set_ylim(0, 1)
        ax.set_title('Phase 20 Tier 4 — surrogate survival per collector\n'
                      '(rep_med at cascade-peak sub-window: '
                      'original vs surrogates)')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(PLOTS / '57_phase20_surrogate_survival.png', dpi=130)
        plt.close()
        print(f"  → {PLOTS}/57_phase20_surrogate_survival.png")


if __name__ == '__main__':
    main()
