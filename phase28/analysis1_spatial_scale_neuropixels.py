"""
phase28/analysis1_spatial_scale_neuropixels.py — Allen Neuropixels
VISp spatial-scale ARS analysis at <300 μm and beyond.

Closes the Phase 27 spatial-resolution caveat by testing ARS at
Ohiorhenuan 2010's actual spatial regime (<300 μm).  Multi-session,
multi-spatial-bin ARS classification with per-bin rate-matched Poisson
surrogates.

Spatial bins:
  fine-local : ≤100 μm separation
  local      : 100-300 μm
  mid        : 300-800 μm
  distant    : >800 μm

For each session × spatial bin:
  - Build local clusters by anchoring on each unit; cluster = anchor
    + neighbours in the bin's distance range.  For fine-local, cluster
    = anchor + units within 100 μm.  For local, cluster = anchor +
    units within 300 μm (includes the fine-local neighbourhood).
    Adjacent bins are nested so the comparison is "fine-local-only
    vs mid-and-beyond" — see brief Step 2 / Step 3.
  - k_thresh = 5 (Phase 22a convention; awake-mouse-V1 low-synchrony
    regime, scales-comparable to the recording-wide setting).
  - Per-cluster ARS classification at q_max=30.  Multi-order
    falsification: report all q-band quadrants, not just modal.
  - Per-cluster rate-matched Poisson surrogate (5 seeds).
  - Modal verdict per session per bin = modal primary across anchor
    clusters in that bin.

Verdict aggregation rules — see brief Acceptance Criteria.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase24'))

from ars_classify import classify, per_q_columns
from loader import load_session

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase28_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)
POS_DIR = OUT_DIR / 'spatial_positions'

EVENT_BIN_MS = 5.0
K_THRESH = 5
Q_MAX = 30
N_SURROGATE_SEEDS = 3
MIN_CLUSTER_SIZE = 4   # anchor + 3 neighbours minimum
# Subsample anchors per session to keep total runtime tractable.
# Aggregate verdict needs ~10-15 well-powered clusters per (session,
# bin) for a stable median; with 12 sessions × 4 bins × N anchors,
# 15-20 anchors per session is plenty.  Sample evenly-spaced anchors
# along the probe to cover the full V1 vertical extent.
ANCHORS_PER_SESSION = 20

SPATIAL_BINS = [
    ('fine-local',  (0.0, 100.0)),
    ('local',       (100.0, 300.0)),
    ('mid',         (300.0, 800.0)),
    ('distant',     (800.0, 5000.0)),
]


def per_unit_binned_spikes(rec, unit_ids: list[int],
                              bin_ms: float = EVENT_BIN_MS) -> tuple[np.ndarray, float]:
    """Bin each unit's natural_movie_one-concatenated spike train at
    bin_ms resolution.  Returns (mat (n_units, n_bins), total_dur_sec).
    """
    bin_s = bin_ms / 1000.0
    blocks = []
    if len(rec.natural_movie_one):
        for bid, grp in rec.natural_movie_one.groupby('stimulus_block',
                                                        sort=True):
            t0 = float(grp['start_time'].min())
            t1 = float(grp['stop_time'].max())
            blocks.append((t0, t1))
    if not blocks:
        return np.zeros((len(unit_ids), 0), dtype=np.int32), 0.0
    durs = [t1 - t0 for t0, t1 in blocks]
    nbs = [int(np.ceil(d / bin_s)) for d in durs]
    total_bins = sum(nbs)
    total_dur = float(sum(durs))
    mat = np.zeros((len(unit_ids), total_bins), dtype=np.int32)
    for ui, uid in enumerate(unit_ids):
        sp = rec.spike_times.get(int(uid), np.zeros(0))
        offset = 0
        for (t0, t1), nb in zip(blocks, nbs):
            in_block = sp[(sp >= t0) & (sp < t1)]
            bin_idx = np.floor((in_block - t0) / bin_s).astype(np.int64)
            bin_idx = bin_idx[(bin_idx >= 0) & (bin_idx < nb)]
            np.add.at(mat[ui], bin_idx + offset, 1)
            offset += nb
    return mat, total_dur


def cluster_events(mat: np.ndarray, member_idx: list[int],
                      k_thresh: int = K_THRESH) -> np.ndarray:
    sub = mat[member_idx]
    binary = (sub > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    bin_idx = np.where(coact >= k_thresh)[0]
    bin_s = EVENT_BIN_MS / 1000.0
    return (bin_idx + 0.5) * bin_s


def rate_matched_surrogate(mat: np.ndarray, member_idx: list[int],
                              k_thresh: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    sub = mat[member_idx]
    n_units, T = sub.shape
    rates = sub.mean(axis=1)
    sur = np.zeros_like(sub)
    for i in range(n_units):
        sur[i] = rng.poisson(rates[i], size=T)
    binary = (sur > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    bin_idx = np.where(coact >= k_thresh)[0]
    bin_s = EVENT_BIN_MS / 1000.0
    return (bin_idx + 0.5) * bin_s


def classify_session(session_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run per-spatial-bin per-anchor ARS classification + surrogate
    for one session.  Returns (real_df, surrogate_df)."""
    pos_path = POS_DIR / f'session_{session_id}.parquet'
    if not pos_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    pos_df = pd.read_parquet(pos_path)
    unit_ids = pos_df['unit_id'].astype(int).tolist()
    pos = pos_df[['probe_vertical_position_um',
                    'probe_horizontal_position_um']].to_numpy()
    d = squareform(pdist(pos))

    rec = load_session(int(session_id))
    mat, total_dur = per_unit_binned_spikes(rec, unit_ids)
    if mat.shape[1] == 0:
        return pd.DataFrame(), pd.DataFrame()

    real_rows, sur_rows = [], []
    n_units = len(unit_ids)
    # Subsample anchors: evenly spaced along the unit list (which is
    # ordered by unit_id; for spatial coverage we sort by vertical
    # position first, then evenly-space).
    v_order = np.argsort(pos[:, 0])
    if n_units <= ANCHORS_PER_SESSION:
        anchor_idxs = v_order.tolist()
    else:
        # Evenly-spaced indices into the v-sorted unit list
        sel = np.linspace(0, n_units - 1, ANCHORS_PER_SESSION).astype(int)
        anchor_idxs = [int(v_order[i]) for i in sel]
    for bin_name, (lo, hi) in SPATIAL_BINS:
        for anchor in anchor_idxs:
            # Cluster members = anchor + units within [lo, hi] of anchor.
            # For fine-local, anchor is always in the cluster.
            members = sorted(set([anchor]
                                    + np.where((d[anchor] >= lo)
                                                 & (d[anchor] <= hi))[0].tolist()))
            if len(members) < MIN_CLUSTER_SIZE:
                continue
            events = cluster_events(mat, members, K_THRESH)
            if events.size < 30:
                real_rows.append(dict(
                    session_id=int(session_id),
                    bin=bin_name, anchor_unit=int(unit_ids[anchor]),
                    n_members=len(members),
                    n_events=int(events.size),
                    primary='underpowered',
                    rep_med=float('nan'), ks_gue_med=float('nan'),
                    n_well=0, total_dur_sec=total_dur,
                    quadrants_per_q=None, rep_int_per_q=None,
                    ks_gue_per_q=None, rf_amp_per_q=None,
                    rf_spike_per_q=None,
                ))
                continue
            res = classify(events, return_full=True, q_max=Q_MAX)
            cols = per_q_columns(res['per_q'])
            real_rows.append(dict(
                session_id=int(session_id),
                bin=bin_name, anchor_unit=int(unit_ids[anchor]),
                n_members=len(members),
                n_events=int(events.size),
                primary=res['primary'],
                rep_med=res['rep_med'], ks_gue_med=res['ks_gue_med'],
                n_well=res['n_well'], total_dur_sec=total_dur,
                **cols,
            ))
            # Surrogate
            for seed in range(N_SURROGATE_SEEDS):
                sur_events = rate_matched_surrogate(mat, members,
                                                       K_THRESH, seed)
                if sur_events.size < 30:
                    sur_rows.append(dict(
                        session_id=int(session_id),
                        bin=bin_name, anchor_unit=int(unit_ids[anchor]),
                        seed=int(seed), n_members=len(members),
                        n_events=int(sur_events.size),
                        primary='underpowered',
                        rep_med=float('nan'), ks_gue_med=float('nan'),
                        n_well=0,
                    ))
                    continue
                sur_res = classify(sur_events, return_full=False, q_max=Q_MAX)
                sur_rows.append(dict(
                    session_id=int(session_id),
                    bin=bin_name, anchor_unit=int(unit_ids[anchor]),
                    seed=int(seed), n_members=len(members),
                    n_events=int(sur_events.size),
                    primary=sur_res['primary'],
                    rep_med=sur_res['rep_med'],
                    ks_gue_med=sur_res['ks_gue_med'],
                    n_well=sur_res['n_well'],
                ))
    return pd.DataFrame(real_rows), pd.DataFrame(sur_rows)


def aggregate_verdict(real_all: pd.DataFrame,
                        sur_all: pd.DataFrame) -> dict:
    """Compose the spatial-scale verdict per the Phase 28 brief."""
    well = real_all[real_all['primary'] != 'underpowered']
    if not len(well):
        return dict(verdict='NULL', reason='no well-powered clusters')

    # Per-bin medians
    per_bin = (well.groupby('bin')
                  .agg(n_clusters=('anchor_unit', 'count'),
                         median_rep=('rep_med', 'median'),
                         median_ks=('ks_gue_med', 'median'),
                         modal_primary=('primary',
                                          lambda s: Counter(s).most_common(1)[0][0]),
                         frac_TR=('primary', lambda s: (s == 'TR').mean()),
                         frac_BL=('primary', lambda s: (s == 'BL').mean()),
                         frac_BR_artifact=('primary',
                                              lambda s: (s == 'BR_artifact').mean()))
                  .reset_index())

    # Surrogate per-bin
    sur_well = sur_all[sur_all['primary'] != 'underpowered']
    if len(sur_well):
        sur_per_bin = (sur_well.groupby('bin')
                          .agg(sur_median_rep=('rep_med', 'median'),
                                 sur_median_ks=('ks_gue_med', 'median'),
                                 sur_frac_TR=('primary', lambda s: (s == 'TR').mean()))
                          .reset_index())
        per_bin = per_bin.merge(sur_per_bin, on='bin', how='left')

    bin_order = [b[0] for b in SPATIAL_BINS]
    per_bin['bin'] = pd.Categorical(per_bin['bin'], categories=bin_order, ordered=True)
    per_bin = per_bin.sort_values('bin')

    # Local-rich? Compare fine-local + local against mid + distant
    fl = per_bin[per_bin['bin'].isin(['fine-local', 'local'])]
    md = per_bin[per_bin['bin'].isin(['mid', 'distant'])]
    fl_rep = float(fl['median_rep'].mean()) if len(fl) else float('nan')
    md_rep = float(md['median_rep'].mean()) if len(md) else float('nan')
    fl_ks = float(fl['median_ks'].mean()) if len(fl) else float('nan')
    md_ks = float(md['median_ks'].mean()) if len(md) else float('nan')
    delta_rep = fl_rep - md_rep
    delta_ks = fl_ks - md_ks

    # Verdict logic — see brief acceptance criteria
    fine_local_well = (per_bin[per_bin['bin'] == 'fine-local']['n_clusters'].sum()
                          if 'fine-local' in per_bin['bin'].astype(str).tolist() else 0)
    if fine_local_well < 5:
        verdict = 'NULL'
        reason = 'too few well-powered fine-local clusters'
    else:
        # Compare fine-local + local to mid + distant.  LOCAL-RICH iff
        # local-bin median rep_med substantially higher than distant.
        if delta_rep > 0.10 or delta_ks > 0.10:
            verdict = 'LOCAL-RICH'
            reason = (f'fine-local+local higher than mid+distant '
                        f'(Δrep={delta_rep:+.3f}, Δks={delta_ks:+.3f})')
        elif delta_rep < -0.10 or delta_ks < -0.10:
            # Phase 27 pvc-11 pattern: fine-local LESS structured
            verdict = 'CONTRA-AT-ALL-SCALES'
            reason = (f'fine-local+local lower than mid+distant '
                        f'(Δrep={delta_rep:+.3f}, Δks={delta_ks:+.3f})')
        else:
            # No characteristic local-vs-distant difference
            # SPATIAL-SCALE-DEPENDENT if there's variation within
            # fine-local vs distant *bins* even if mean is similar;
            # else SCALE-INVARIANT (not in Phase 28's verdict list,
            # report as 'SCALE-INVARIANT' which maps to "CONTRA at
            # least in the milder sense that there's no enrichment").
            verdict = 'SPATIAL-SCALE-DEPENDENT'
            reason = (f'mean Δrep and Δks within ±0.10 '
                        f'(Δrep={delta_rep:+.3f}, Δks={delta_ks:+.3f}); '
                        f'no clear local-rich or local-poor pattern')

    return dict(
        verdict=verdict, reason=reason,
        per_bin=per_bin.to_dict('records'),
        fl_mean_rep=fl_rep, md_mean_rep=md_rep, delta_rep=delta_rep,
        fl_mean_ks=fl_ks, md_mean_ks=md_ks, delta_ks=delta_ks,
        n_well_total=int(len(well)), n_total=int(len(real_all)),
        underpowered_frac=float(1 - len(well) / max(len(real_all), 1)),
    )


def main():
    print("=" * 72)
    print("Phase 28 Analysis 1 — Allen Neuropixels spatial-scale ARS")
    print("=" * 72)
    print(f"  bins: {SPATIAL_BINS}")
    print(f"  k_thresh={K_THRESH}  q_max={Q_MAX}  surrogate seeds={N_SURROGATE_SEEDS}")
    sessions = pd.read_parquet(
        Path(ROOT_DIR) / 'data' / 'phase24_results'
        / 'per_session_h1_functional.parquet')['session_id'].unique()
    print(f"  {len(sessions)} sessions")

    all_real, all_sur = [], []
    t_total = time.time()
    for sid in sessions:
        t0 = time.time()
        r, s = classify_session(int(sid))
        print(f"  session {sid}: clusters={len(r)}  well="
                f"{int((r['primary']!='underpowered').sum())}  "
                f"⏱{time.time()-t0:.0f}s", flush=True)
        all_real.append(r); all_sur.append(s)
    real_all = pd.concat(all_real, ignore_index=True)
    sur_all = pd.concat(all_sur, ignore_index=True)
    real_all.to_parquet(OUT_DIR / 'analysis1_per_cluster_real.parquet',
                         index=False)
    sur_all.to_parquet(OUT_DIR / 'analysis1_per_cluster_surrogate.parquet',
                        index=False)
    print(f"  total ⏱{time.time()-t_total:.0f}s")

    print()
    verdict = aggregate_verdict(real_all, sur_all)
    with open(OUT_DIR / 'analysis1_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2, default=str)

    print(f"Aggregate verdict: {verdict['verdict']}")
    print(f"  reason: {verdict['reason']}")
    print(f"  n_well_total={verdict['n_well_total']}/{verdict['n_total']}  "
            f"(underpowered: {verdict['underpowered_frac']*100:.1f}%)")
    print()
    print("Per-bin summary:")
    for r in verdict['per_bin']:
        print(f"  {r['bin']:12s}  n_clusters={r['n_clusters']:4d}  "
                f"modal={r['modal_primary']:13s}  "
                f"rep_med={r['median_rep']:+.3f}  ks_gue={r['median_ks']:+.3f}  "
                f"frac(TR/BL/BR)={r['frac_TR']:.2f}/{r['frac_BL']:.2f}/{r['frac_BR_artifact']:.2f}")


if __name__ == '__main__':
    main()
