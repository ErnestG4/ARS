"""
phase27/analysis3_spatial_scale.py — ARS spatial-scale dependence on
pvc-11 Utah array data.

Question: does ARS detect spatial-scale-dependent population
structure on pvc-11 at Utah-array-accessible scales (≥400 μm),
relating coarsely to Ohiorhenuan 2010's finding that high-order
correlations are local (<300 μm) but not distant (600–2500 μm) in
anaesthetised macaque V1?

**Spatial-resolution limitation:** Utah array pitch is 400 μm.  The
minimum between-channel distance is 400 μm (adjacent horizontal /
vertical), the minimum diagonal distance ~565 μm.  No between-channel
pairs are within Ohiorhenuan's 300 μm threshold; within-channel
multi-units are the only ≤300 μm sample and are methodologically
distinct.  This analysis cannot directly replicate the <300 μm vs
>800 μm comparison; it tests spatial-scale dependence at Utah-
accessible scales (400 μm and up) and frames the result relative to
Ohiorhenuan's coarser-grain prediction.

Methodology:
  Step 1: Per-unit (x, y) position from array_map + channels @ 400 μm
          pitch.
  Step 2: For each electrode, build a "local cluster" = all units
          within 600 μm radius.  k_thresh per cluster scales with
          cluster size (max(2, ceil(0.5 * n_local_units))).
  Step 3: Per-cluster population events at (k_thresh, w=5 ms),
          classified at q_max=30.
  Step 4: Recording-wide population events from Phase 22a's
          H2 population classification parquet (reference).
  Step 5: Per-cluster rate-matched Poisson surrogate (Phase 26 lesson —
          surrogate floor must match the local-scale rate).  5 seeds
          per cluster.

Outputs:
  analysis3_per_cluster_classifications.parquet  (per-electrode local
        cluster real classifications)
  analysis3_per_cluster_surrogate.parquet  (5 seeds × clusters)
  analysis3_verdict.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))

from loader import load, MOVIE_TRIAL_SEC
from population_events import build_unit_matrix, extract_events
from ars_classify import classify, per_q_columns

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase27_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

UTAH_PITCH_UM = 400.0
LOCAL_RADIUS_UM = 600.0      # capture NN (400 μm) + diagonal (565 μm)
EVENT_BIN_MS = 5.0
Q_MAX = 30
N_SURROGATE_SEEDS = 5

H2_SESSIONS = ['monkey1_natural_movie', 'monkey2_gratings_movie']

UNIT_SEL = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
              / 'unit_selection.parquet')
H2_POP_REF = (Path(ROOT_DIR) / 'data' / 'phase22a_results'
                / 'h2_population_classifications.parquet')


def compute_unit_positions(rec, unit_ids: list[int]
                              ) -> np.ndarray:
    """Compute (x, y) positions in μm for each unit.  Returns array
    shape (n_units, 2).  Multi-units on the same channel share
    coordinates."""
    # Build channel → (row, col) lookup, skipping inactive corners
    channel_to_rc = {}
    for r in range(10):
        for c in range(10):
            v = rec.array_map[r, c]
            if np.isnan(v): continue
            ch = int(v)
            if ch > 0:
                channel_to_rc[ch] = (r, c)

    pos = np.zeros((len(unit_ids), 2), dtype=float)
    for i, u in enumerate(unit_ids):
        ch = int(rec.channels[u, 0])
        if ch in channel_to_rc:
            r, c = channel_to_rc[ch]
            pos[i] = (c * UTAH_PITCH_UM, r * UTAH_PITCH_UM)
        else:
            pos[i] = (np.nan, np.nan)
    return pos


def build_local_clusters(pos: np.ndarray,
                           radius_um: float = LOCAL_RADIUS_UM
                           ) -> list[dict]:
    """For each unit, find all units within `radius_um` (inclusive of
    the unit itself).  Returns list of {'center_unit_idx', 'member_idx'}
    dicts.  De-duplicates clusters that are identical in membership
    (e.g., 4 units all within 600 μm of each other form one cluster
    regardless of which unit centres it).
    """
    n = len(pos)
    if n == 0: return []
    d = squareform(pdist(pos))
    seen = set()
    clusters = []
    for i in range(n):
        members = tuple(sorted(np.where(d[i] <= radius_um)[0].tolist()))
        if not members or len(members) < 3:
            # Skip singleton/pairs — too few units for population events.
            continue
        if members in seen:
            continue
        seen.add(members)
        clusters.append(dict(
            center_unit_idx=int(i),
            member_idx=list(members),
            n_members=len(members),
        ))
    return clusters


def extract_cluster_events(real_mat: np.ndarray,
                              cluster_member_idx: list[int],
                              k_thresh: int,
                              ) -> np.ndarray:
    """Build population events for one local cluster: bin at 5 ms,
    count distinct units firing per bin among cluster members, return
    event timestamps where coactivation ≥ k_thresh."""
    sub = real_mat[cluster_member_idx]
    binary = (sub > 0).astype(np.int32)
    coact = binary.sum(axis=0)
    bin_idx = np.where(coact >= k_thresh)[0]
    bin_s = EVENT_BIN_MS / 1000.0
    return (bin_idx + 0.5) * bin_s


def rate_matched_surrogate(real_mat: np.ndarray,
                              cluster_member_idx: list[int],
                              k_thresh: int,
                              seed: int) -> np.ndarray:
    """Per-cell rate-matched Poisson surrogate: for each member unit
    in the cluster, sample independent Poisson(rate_per_bin) where
    rate_per_bin = total_spikes/n_bins.  Then extract events the same
    way as real."""
    rng = np.random.default_rng(seed)
    sub = real_mat[cluster_member_idx]
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


def _classify_one(args):
    label, events = args
    res = classify(events, return_full=True, q_max=Q_MAX)
    return label, res


def analyse_session(session: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run per-cluster ARS classification + surrogate for one session.
    Returns (real_classifications_df, surrogate_classifications_df).
    """
    rec = load(session)
    sel = pd.read_parquet(UNIT_SEL)
    sel_h2 = sel[(sel['recording'] == session) & sel['h2_pass']]
    units = sel_h2['unit_idx'].astype(int).tolist()

    real_mat, total_dur = build_unit_matrix(rec, units, bin_ms=EVENT_BIN_MS)
    pos = compute_unit_positions(rec, units)

    clusters = build_local_clusters(pos, radius_um=LOCAL_RADIUS_UM)
    print(f"  [{session}] n_units={len(units)}  n_clusters={len(clusters)}")

    real_rows = []
    sur_rows = []
    for ci, cluster in enumerate(clusters):
        members = cluster['member_idx']
        n_mem = cluster['n_members']
        # k_thresh scales with cluster size: at least 2, capped at 6
        # (matches recording-wide k=5 scale; for small clusters we
        # require ≥half of members co-firing).
        k_thresh = int(np.clip(np.ceil(0.5 * n_mem), 2, 6))

        # Real cluster events
        events = extract_cluster_events(real_mat, members, k_thresh)
        if events.size < 30:
            real_rows.append(dict(
                session=session, cluster_idx=ci,
                center_unit_idx=cluster['center_unit_idx'],
                n_members=n_mem, k_thresh=k_thresh,
                n_events=int(events.size),
                primary='underpowered',
                rep_med=float('nan'), ks_gue_med=float('nan'),
                n_well=0,
                quadrants_per_q=None,
                rep_int_per_q=None,
                ks_gue_per_q=None,
                rf_amp_per_q=None,
                rf_spike_per_q=None,
            ))
            continue

        res = classify(events, return_full=True, q_max=Q_MAX)
        cols = per_q_columns(res['per_q'])
        real_rows.append(dict(
            session=session, cluster_idx=ci,
            center_unit_idx=cluster['center_unit_idx'],
            n_members=n_mem, k_thresh=k_thresh,
            n_events=int(events.size),
            primary=res['primary'],
            rep_med=res['rep_med'],
            ks_gue_med=res['ks_gue_med'],
            n_well=res['n_well'],
            **cols,
        ))

        # Per-cluster rate-matched surrogate (5 seeds)
        for seed in range(N_SURROGATE_SEEDS):
            sur_events = rate_matched_surrogate(real_mat, members,
                                                   k_thresh, seed)
            if sur_events.size < 30:
                sur_rows.append(dict(
                    session=session, cluster_idx=ci, seed=seed,
                    n_members=n_mem, k_thresh=k_thresh,
                    n_events=int(sur_events.size),
                    primary='underpowered',
                    rep_med=float('nan'), ks_gue_med=float('nan'),
                    n_well=0,
                ))
                continue
            sur_res = classify(sur_events, return_full=False, q_max=Q_MAX)
            sur_rows.append(dict(
                session=session, cluster_idx=ci, seed=seed,
                n_members=n_mem, k_thresh=k_thresh,
                n_events=int(sur_events.size),
                primary=sur_res['primary'],
                rep_med=sur_res['rep_med'],
                ks_gue_med=sur_res['ks_gue_med'],
                n_well=sur_res['n_well'],
            ))

    return pd.DataFrame(real_rows), pd.DataFrame(sur_rows)


def aggregate_verdict(real_all: pd.DataFrame,
                        sur_all: pd.DataFrame,
                        h2_ref: pd.DataFrame) -> dict:
    """Compose the spatial-scale verdict per the brief's vocabulary:

    SPATIAL-SCALE-DEPENDENT : local-scale ARS classifications differ
        characteristically from recording-wide.
    SCALE-INVARIANT         : local-scale and recording-wide ARS are
        similar.
    NULL                    : local-scale ARS returns no meaningful
        classifications (high underpowered fraction).
    CONTRA-OHIORHENUAN      : local-scale shows *less* structure than
        recording-wide.
    """
    well = real_all[real_all['primary'] != 'underpowered']
    n_well = len(well)
    n_total = len(real_all)
    underpowered_frac = 1 - n_well / max(n_total, 1)

    if n_well < 5:
        return dict(verdict='NULL',
                      reason='too few well-powered clusters',
                      n_well_clusters=int(n_well),
                      n_total_clusters=int(n_total),
                      underpowered_frac=float(underpowered_frac))

    # Per-session comparison: local-scale modal primary vs recording-wide
    per_session = []
    for sess in H2_SESSIONS:
        sess_real = well[well['session'] == sess]
        if not len(sess_real): continue
        local_primary_counts = sess_real['primary'].value_counts()
        local_rep_med = float(sess_real['rep_med'].median())
        local_ks_gue = float(sess_real['ks_gue_med'].median())
        # Recording-wide from Phase 22a's H2 classification at q_max=30
        ref = h2_ref[(h2_ref['recording'] == sess) & (h2_ref['q_max'] == Q_MAX)]
        if len(ref):
            rwide_primary = ref['primary'].iloc[0]
            rwide_rep_med = float(ref['rep_med'].iloc[0])
            rwide_ks_gue = float(ref['ks_gue_med'].iloc[0])
        else:
            rwide_primary = None
            rwide_rep_med = float('nan')
            rwide_ks_gue = float('nan')
        # Surrogate comparison
        sur_well = sur_all[(sur_all['session'] == sess)
                             & (sur_all['primary'] != 'underpowered')]
        sur_primary_counts = sur_well['primary'].value_counts() if len(sur_well) else None
        sur_rep_med = (float(sur_well['rep_med'].median())
                          if len(sur_well) else float('nan'))
        per_session.append(dict(
            session=sess,
            n_local_clusters_well=int(len(sess_real)),
            local_modal_primary=str(local_primary_counts.idxmax()) if len(local_primary_counts) else None,
            local_primary_counts=dict(local_primary_counts),
            local_median_rep=local_rep_med,
            local_median_ks_gue=local_ks_gue,
            recording_wide_primary=str(rwide_primary) if rwide_primary else None,
            recording_wide_rep=rwide_rep_med,
            recording_wide_ks_gue=rwide_ks_gue,
            surrogate_local_modal_primary=str(sur_primary_counts.idxmax())
                if sur_primary_counts is not None and len(sur_primary_counts) else None,
            surrogate_local_median_rep=sur_rep_med,
            delta_local_minus_rwide_rep=local_rep_med - rwide_rep_med,
            delta_local_minus_rwide_ks_gue=local_ks_gue - rwide_ks_gue,
        ))

    # Aggregate verdict logic
    # Two questions:
    #   (a) Do local-scale classifications differ characteristically from
    #       recording-wide?  Look at primary-quadrant shift and rep_med
    #       delta.
    #   (b) Is the difference in the direction Ohiorhenuan predicts (local
    #       shows MORE structure than distant/recording-wide)?  Hard to
    #       define cleanly; proxy: local clusters classify TR (Wigner-
    #       class) when recording-wide is BL/uniform.
    same_primary_count = sum(1 for s in per_session
                                if s['local_modal_primary'] == s['recording_wide_primary'])
    diff_primary_count = len(per_session) - same_primary_count

    median_rep_delta = float(np.mean([s['delta_local_minus_rwide_rep']
                                          for s in per_session
                                          if np.isfinite(s['delta_local_minus_rwide_rep'])]))
    median_ks_delta = float(np.mean([s['delta_local_minus_rwide_ks_gue']
                                          for s in per_session
                                          if np.isfinite(s['delta_local_minus_rwide_ks_gue'])]))

    # Verdict
    if diff_primary_count == len(per_session) and abs(median_rep_delta) > 0.10:
        # All sessions differ; local-scale rep is substantially different
        # from recording-wide.
        if median_rep_delta > 0:
            # Local rep is higher than recording-wide → MORE structure
            # at local scale (consistent-ish with Ohiorhenuan local-rich
            # prediction).
            verdict = 'SPATIAL-SCALE-DEPENDENT'
        else:
            verdict = 'CONTRA-OHIORHENUAN'
    elif same_primary_count == len(per_session) and abs(median_rep_delta) < 0.10:
        verdict = 'SCALE-INVARIANT'
    else:
        # Mixed: some shift but not strong/consistent
        verdict = 'SCALE-INVARIANT'  # default to invariant when ambiguous

    return dict(
        verdict=verdict,
        n_well_clusters=int(n_well),
        n_total_clusters=int(n_total),
        underpowered_frac=float(underpowered_frac),
        per_session=per_session,
        mean_local_minus_rwide_rep=median_rep_delta,
        mean_local_minus_rwide_ks_gue=median_ks_delta,
        spatial_resolution_caveat=(
            "Utah array 400 μm pitch.  No between-channel pairs within "
            "Ohiorhenuan's <300 μm threshold; this analysis cannot "
            "directly replicate <300 μm vs >800 μm.  The local-scale "
            "definition here (≤600 μm radius around each electrode) is "
            "above Ohiorhenuan's local threshold but well below their "
            "distant threshold.  Within-channel multi-units provide "
            "the only ≤300 μm sample but are methodologically distinct "
            "and not used in this analysis."),
    )


def main():
    print("=" * 72)
    print("Phase 27 Analysis 3 — ARS spatial-scale dependence on pvc-11")
    print("=" * 72)
    print(f"  Utah pitch: {UTAH_PITCH_UM} μm  |  local radius: {LOCAL_RADIUS_UM} μm")
    print(f"  event bin: {EVENT_BIN_MS} ms  |  q_max: {Q_MAX}")
    print(f"  surrogate seeds per cluster: {N_SURROGATE_SEEDS}")

    h2_ref = pd.read_parquet(H2_POP_REF)
    all_real, all_sur = [], []
    for sess in H2_SESSIONS:
        t0 = time.time()
        r, s = analyse_session(sess)
        all_real.append(r); all_sur.append(s)
        print(f"  [{sess}] ⏱{time.time()-t0:.0f}s  "
                f"clusters={len(r)}  well={int((r['primary']!='underpowered').sum())}")

    real_all = pd.concat(all_real, ignore_index=True)
    sur_all = pd.concat(all_sur, ignore_index=True)
    real_all.to_parquet(OUT_DIR / 'analysis3_per_cluster_real.parquet',
                         index=False)
    sur_all.to_parquet(OUT_DIR / 'analysis3_per_cluster_surrogate.parquet',
                        index=False)
    print()
    print("Per-cluster real-classification summary:")
    print(real_all.groupby(['session', 'primary']).size())
    print()

    verdict = aggregate_verdict(real_all, sur_all, h2_ref)
    with open(OUT_DIR / 'analysis3_verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2, default=str)
    print(f"Aggregate verdict: {verdict['verdict']}")
    print(f"  n_well_clusters: {verdict['n_well_clusters']} / "
            f"{verdict['n_total_clusters']}  "
            f"(underpowered: {verdict['underpowered_frac']*100:.1f}%)")
    print(f"  mean local-minus-recording-wide rep_med:    "
            f"{verdict['mean_local_minus_rwide_rep']:+.3f}")
    print(f"  mean local-minus-recording-wide ks_gue_med: "
            f"{verdict['mean_local_minus_rwide_ks_gue']:+.3f}")
    print()
    print("Per-session detail:")
    for s in verdict['per_session']:
        print(f"  {s['session']}:")
        print(f"    local clusters well={s['n_local_clusters_well']}  "
                f"modal={s['local_modal_primary']}  "
                f"rep_med={s['local_median_rep']:.3f}  "
                f"ks_gue_med={s['local_median_ks_gue']:.3f}")
        print(f"    recording-wide        modal={s['recording_wide_primary']}  "
                f"rep_med={s['recording_wide_rep']:.3f}  "
                f"ks_gue_med={s['recording_wide_ks_gue']:.3f}")
        print(f"    surrogate-local       modal={s['surrogate_local_modal_primary']}  "
                f"rep_med={s['surrogate_local_median_rep']:.3f}")
        print(f"    delta local−rwide:    rep {s['delta_local_minus_rwide_rep']:+.3f}  "
                f"ks_gue {s['delta_local_minus_rwide_ks_gue']:+.3f}")


if __name__ == '__main__':
    main()
