"""
phase34a/run_nns_classify.py — Sub-question 2: NNS-engine reproduction
on Mertens sign-change positions via the deployed joint_q_profile.

Brief expectations: BL (Poisson) on the bulk, consistent with the §15
capability-report entry for Mertens/Liouville sign-change sequences.

Runs three configurations to bound the verdict against the
non-stationarity flagged in sub-question 1:
    (a) full   — all 3866 sign changes in [1, 10^7]
    (b) dense  — restricted to [1, 4*10^6] where windows 0-3 are all
                 cleanly BL
    (c) tail   — [5*10^6, 10^7] where density drops; reported as
                 underpowered if it falls below MIN_EVENTS_PER_Q.

Output: data/phase34a_results/nns_classify.json
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

from mertens_events import load_or_compute
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q, JPF_CAP

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


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
        well = per_q[~per_q['underpowered']]
        from collections import Counter
        c = Counter(well['quadrant'])
        print(f"  per-q quadrant breakdown: "
              f"{dict(sorted(c.items()))}")
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
        per_q_rep_int=(per_q['rep_int_q'].tolist()
                        if per_q is not None else []),
        per_q_ks_gue=(per_q['ks_gue_q'].tolist()
                       if per_q is not None else []),
        per_q_rf_amp=(per_q['rf_amplitude_q'].tolist()
                       if per_q is not None else []),
        per_q_rf_spike=(per_q['rf_spike'].tolist()
                         if per_q is not None else []),
    )


def main(N_MAX: int = 10**7) -> dict:
    print("=" * 72)
    print("Phase 34a Sub-question 2: NNS-engine reproduction on Mertens "
          "sign-changes")
    print("=" * 72)
    print(f"  Q_MAX={Q_MAX}, MIN_EVENTS_PER_Q={MIN_EVENTS_PER_Q}, "
          f"JPF_CAP={JPF_CAP}")

    d = load_or_compute(N_MAX)
    sc = d['signchanges']

    # (a) full sequence
    res_full = classify_subset(sc, 'full')

    # (b) density-stationary sub-window [1, 4e6]: windows 0-3 from
    # sub-question 1, all BL with rep_med=0.
    dense = sc[sc < 4 * 10**6]
    res_dense = classify_subset(dense, 'dense [1, 4e6]')

    # (c) sparse tail [5e6, 10^7]
    tail = sc[(sc >= 5 * 10**6) & (sc < 10**7)]
    res_tail = classify_subset(tail, 'tail [5e6, 1e7]')

    out_obj = {
        'q_max': Q_MAX,
        'min_events_per_q': MIN_EVENTS_PER_Q,
        'jpf_cap': JPF_CAP,
        'full': res_full,
        'dense_1_to_4e6': res_dense,
        'tail_5e6_to_1e7': res_tail,
    }
    out_path = OUT_DIR / 'nns_classify.json'
    with open(out_path, 'w') as f:
        json.dump(out_obj, f, indent=2, default=str)
    print(f"\n  → {out_path}")
    return out_obj


if __name__ == '__main__':
    main()
