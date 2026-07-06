"""
phase34b/run_nns_classify.py — Sub-question 2: NNS-engine reproduction
on L(n) sign-changes via the deployed joint_q_profile.

The L(n) sign-changes are sparse (1 isolated at n=3, 132 in the Tanaka
cluster near 9×10⁸).  Three configurations:
  (a) cluster only (132 events, [906150257, 906488081])
  (b) cluster + n=3 (133 events, full)
  (c) first 91 sub-cluster (events ∈ [906150257, ~906234713])
  (d) last 41 sub-cluster (events ∈ [~906404325, 906488081])

Expected: BL Poisson per §15 capability-report.  Sample size cap at
JPF_CAP=1500 is not binding (we have ≪ 1500 events).

Output: data/phase34b_results/nns_classify.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))

from liouville_events import load_or_compute
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q, JPF_CAP

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34b_results'

CLUSTER_LO = 906150257
CLUSTER_HI = 906488081


def classify_subset(events: np.ndarray, label: str) -> dict:
    print(f"\n[{label}] n_events_in: {events.size}")
    if events.size < MIN_EVENTS_PER_Q:
        print(f"  underpowered (need ≥ {MIN_EVENTS_PER_Q})")
        return dict(label=label, n_events_in=int(events.size),
                     primary='underpowered')
    r = classify(events.astype(np.float64), q_max=Q_MAX,
                  min_events_per_q=MIN_EVENTS_PER_Q,
                  return_full=True)
    per_q = r['per_q']
    print(f"  primary: {r['primary']}")
    print(f"  rep_med: {r['rep_med']:.3f}, ks_gue_med: {r['ks_gue_med']:.3f}")
    print(f"  n_events_used: {r['n_events_used']} (JPF_CAP={JPF_CAP})")
    print(f"  n_well-powered q-bands: {r['n_well']} / {Q_MAX}")
    if per_q is not None:
        from collections import Counter
        well = per_q[~per_q['underpowered']]
        c = Counter(well['quadrant'])
        print(f"  per-q quadrant breakdown: {dict(sorted(c.items()))}")
    return dict(
        label=label,
        n_events_in=int(events.size),
        primary=str(r['primary']),
        rep_med=float(r['rep_med']),
        ks_gue_med=float(r['ks_gue_med']),
        n_events_used=int(r['n_events_used']),
        n_well=int(r['n_well']),
        per_q_quadrants=(per_q['quadrant'].tolist()
                          if per_q is not None else []),
    )


def main(N_MAX: int = 10**9) -> dict:
    print("=" * 72)
    print("Phase 34b Sub-question 2: NNS-engine reproduction on L(n)")
    print("=" * 72)
    print(f"  Q_MAX={Q_MAX}, MIN_EVENTS_PER_Q={MIN_EVENTS_PER_Q}, "
          f"JPF_CAP={JPF_CAP}")
    d = load_or_compute(N_MAX)
    sc = d['signchanges']
    cluster = sc[(sc >= CLUSTER_LO) & (sc <= CLUSTER_HI)]
    # Find sub-cluster boundaries: gaps > 1000 separate sub-clusters
    gaps = np.diff(cluster)
    sub_boundary = int(np.argmax(gaps)) + 1 if gaps.size and gaps.max() > 1000 else len(cluster)
    sub_lo = cluster[:sub_boundary]
    sub_hi = cluster[sub_boundary:]
    print(f"  cluster events: {cluster.size}")
    print(f"  sub-cluster low ({sub_lo[0] if sub_lo.size else '-'}→"
          f"{sub_lo[-1] if sub_lo.size else '-'}): {sub_lo.size} events")
    print(f"  sub-cluster high ({sub_hi[0] if sub_hi.size else '-'}→"
          f"{sub_hi[-1] if sub_hi.size else '-'}): {sub_hi.size} events")

    out = {
        'q_max': Q_MAX,
        'min_events_per_q': MIN_EVENTS_PER_Q,
        'jpf_cap': JPF_CAP,
    }
    out['cluster_132'] = classify_subset(cluster, 'cluster 132')
    out['full_133'] = classify_subset(sc, 'full 133 (includes n=3)')
    out['sub_low'] = classify_subset(sub_lo, f'sub-cluster low ({sub_lo.size})')
    out['sub_high'] = classify_subset(sub_hi, f'sub-cluster high ({sub_hi.size})')

    out_path = OUT_DIR / 'nns_classify.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  → {out_path}")
    return out


if __name__ == '__main__':
    main()
