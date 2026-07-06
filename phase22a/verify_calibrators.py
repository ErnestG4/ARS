"""
phase22a/verify_calibrators.py — calibrator-zoo no-drift verification.

Phase 22a methodological commitment: the calibrator zoo runs first, no
exceptions.  Before applying ARS to any pvc-11 unit we must confirm
that the per-q quadrant verdicts on canonical inputs (Poisson, Wigner
GOE/GUE/GSE, periodic q=7, mixed q=7+q=12, uniform_jitter, ζ-first-N)
still land in the expected quadrants.

This script:
  1. Generates each STATIONARY_CALIBRATORS class at N_POINTS=400 (the
     canonical distinctness-matrix size used since Phase 19).
  2. Runs joint_q_profile + joint_quadrant_diagnostic at the same
     Q_MAX / MIN_EVENTS_PER_Q used by Phase 21 (Q_MAX=30, MIN=30).
  3. Records the modal (primary) quadrant across well-powered q-bands
     plus the per-q-band breakdown.
  4. Compares the primary against the expected ground-truth label for
     each class and emits a pass/fail per class.

Expected ground truth (modal quadrant under the current toolkit's per-q
diagnostic, after unit-mean unfolding — the standard pre-processing path):
    poisson         → BL  (low rep_int, no RF spike)
    beta=1_GOE      → TR  (Wigner-class, mid rep_int)
    beta=2_GUE      → TR
    beta=4_GSE      → TR
    zeta_first_400  → TR  (Wigner-class)
    uniform_jitter  → BR  (uniform-like, high rep_int saturation)
    periodic_q7     → BR  (after unit-mean unfolding the period maps to
                            DC; high rep_int, no integer-q RF spike → BR)
    mixed_q7_q12    → TR  (jittered super-Poisson tail dominates the
                            modal quadrant; TL spike does appear at low q)

Acceptance: at least 7/8 calibrators land in their expected modal
quadrant.  The 1 wiggle-room slot reserves for boundary classes whose
modal verdict can flip with seed (e.g., GSE shows up as TR in most
seeds but its tail sometimes drifts toward BR).

Output: stdout log + data/phase22a_results/calibrator_verification.parquet
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from calibrator_panel import STATIONARY_CALIBRATORS

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

Q_MAX = 30
MIN_EVENTS_PER_Q = 30
N_SEEDS = 3   # 3 seeds per calibrator; modal verdict across seeds

EXPECTED = {
    'poisson':          'BL',
    'beta=1_GOE':       'TR',
    'beta=2_GUE':       'TR',
    'beta=4_GSE':       'TR',
    'zeta_first_400':   'TR',
    'uniform_jitter':   'BR_artifact',
    'periodic_q7':      'BR_artifact',
    'mixed_q7_q12':     'TR',
}


def unfold_unit_mean(t: np.ndarray) -> np.ndarray:
    if t.size < 2:
        return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return t.copy()
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def classify_one(events: np.ndarray) -> dict:
    """Run joint_q_profile + joint_quadrant_diagnostic, return primary +
    per-q breakdown."""
    if events.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', n=int(events.size),
                     quadrants_str='', well_count=0)
    ev_unit = unfold_unit_mean(events.astype(np.float64))
    if ev_unit.size < MIN_EVENTS_PER_Q:
        return dict(primary='underpowered', n=int(ev_unit.size),
                     quadrants_str='', well_count=0)
    j = joint_q_profile(ev_unit, q_max=Q_MAX,
                         min_events_per_q=MIN_EVENTS_PER_Q)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return dict(primary='underpowered', n=int(ev_unit.size),
                     quadrants_str='', well_count=0)
    counts = well['quadrant'].value_counts()
    quadrants_str = ','.join(f"{q}={c}" for q, c in counts.items())
    # Treat BR_artifact / BR_novel both as BR for ground-truth comparison.
    return dict(primary=str(counts.idxmax()),
                 n=int(ev_unit.size),
                 quadrants_str=quadrants_str,
                 well_count=int(len(well)))


def main():
    print("=" * 72)
    print("Phase 22a Calibrator-Zoo Verification")
    print("=" * 72)
    print(f"Q_MAX={Q_MAX}, MIN_EVENTS_PER_Q={MIN_EVENTS_PER_Q}, "
          f"N_SEEDS={N_SEEDS}\n")

    rows = []
    overall_pass = 0
    overall_total = 0

    for name, gen_fn in STATIONARY_CALIBRATORS:
        expected = EXPECTED.get(name, '?')
        seed_primaries = []
        t0 = time.time()
        for seed in range(N_SEEDS):
            events = gen_fn(seed)
            res = classify_one(events)
            seed_primaries.append(res['primary'])
            rows.append(dict(
                calibrator=name, expected=expected,
                seed=seed, primary=res['primary'],
                n_events=res['n'], well_count=res['well_count'],
                quadrants_str=res['quadrants_str'],
            ))
        # Modal primary across seeds (treat BR_artifact and BR_novel as BR)
        normed = [p.split('_')[0] if p.startswith('BR') else p
                   for p in seed_primaries]
        from collections import Counter
        modal = Counter(normed).most_common(1)[0][0]
        # For BR_artifact/BR_novel comparison, normalise expected too
        expected_normed = expected.split('_')[0] if expected.startswith('BR') else expected
        passed = (modal == expected_normed)
        overall_pass += int(passed)
        overall_total += 1
        flag = "✓" if passed else "✗"
        print(f"  {flag}  {name:18s}  expected={expected:13s}  "
              f"got={modal:13s}  seeds={seed_primaries}  "
              f"⏱{time.time()-t0:.0f}s")

    df = pd.DataFrame(rows)
    out_file = OUT_DIR / 'calibrator_verification.parquet'
    df.to_parquet(out_file, index=False)
    print(f"\n  → {out_file}  ({len(df)} rows)")
    print(f"\nVerdict: {overall_pass}/{overall_total} calibrator classes "
          f"land in expected quadrant.")
    if overall_pass >= 7:
        print("PASS — calibrator zoo is in spec; safe to proceed with pvc-11.")
        return 0
    print("FAIL — calibrator drift detected.  Investigate before pvc-11 work.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
