"""
phase34c/run_pooling_artifact_check.py — verify whether the q=17 RMT-
survival in ec-root-minus-SO-odd is a pooling artifact.

Hypothesis: 17 = number of root-minus EC curves in the cohort.  Pooling
17 separate unfolded coordinates (each with its own range and spacing
distribution) and sorting can produce quasi-periodic structure at
period N_pooled = 17 because sorted events from K curves with
overlapping unfolded ranges alternate between curves at frequency K.

Test: re-run the same RF+pooling analysis with random sub-pools of
size K ∈ {5, 10, 17, 25, 35, 50} drawn from the 87-curve EC L-zero
cohort.  If the hypothesis holds:
  - Sub-pool size K produces an RF spike at q ≈ K (where applicable
    within q_max=30)
  - The K=17 spike replicates the panel result
  - The RMT-unfolded null does NOT contain this artifact (because it
    is a single-ensemble draw, not a pooled draw of K ensembles)

A pooled-RMT-null variant — generate K independent β=1 ensembles
each of matched size, unfold each, pool, and use that as the null —
should NOT show survival at q=K because the surrogate carries the
same pooling structure.

This is the multi-order falsification on the q=17 survival per the
PHASE34C_BRIEF.md sub-4 protocol.

Output: data/phase34c_results/pooling_artifact.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from collections import Counter

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from zeros_loaders import load_ec_curves, ec_by_root_number
from unfolding import pool_unfolded
from survey_engine import (rf_mode_B, padic_v4_from_amplitudes, cap_events,
                              N_MAX_SURVEY, PRIMES, Q_MAX, RF_SPIKE_FACTOR)
from rmt_sampler import sample_rmt_unfolded

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34c_results'

# Sub-pool sizes to test (including K=17 which matches the original
# panel; K∈{5,10} for clear in-range artifact; K=25/35 push the
# artifact above q_max=30 so it should disappear).
SUB_POOL_SIZES = [5, 10, 17, 25, 35, 50]


def pooled_rmt_surrogate(K: int, per_object_size: int, beta: float,
                            seed: int) -> np.ndarray:
    """Generate K independent β-Hermite ensembles of size per_object_size,
    unfold each separately, concatenate.

    This is the *pooling-matched* RMT null: it preserves the K-fold
    pooling structure so the q=K artifact would NOT survive against it.
    """
    rng = np.random.default_rng(seed)
    parts = []
    for _ in range(K):
        local_rng = np.random.default_rng(rng.integers(0, 2**31 - 1))
        nt = sample_rmt_unfolded(per_object_size, beta,
                                   edge_exclude_frac=0.075,
                                   rng=local_rng)
        nt = nt[~np.isnan(nt)]
        # Re-shift each ensemble's range so they overlap (mimics the real
        # per-curve unfolded ranges that overlap on the global axis)
        parts.append(nt)
    return np.sort(np.concatenate(parts))


def run_subpool_test(curves: list[dict], K: int,
                      n_seeds_per_K: int = 5) -> dict:
    """For each of n_seeds_per_K random sub-pools of K curves, compute
    mode-B RF amplitudes; report top-3 q ranked by |a_q|.
    """
    rng = np.random.default_rng(34 + K)
    spike_qs_per_seed = []
    a_q_at_K_per_seed = []
    for s in range(n_seeds_per_K):
        idx = rng.choice(len(curves), size=K, replace=False)
        sub_curves = [curves[i] for i in idx]
        unf = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                 for c in sub_curves], substrate='ec')
        if unf.size == 0:
            continue
        unf = cap_events(unf, cap=N_MAX_SURVEY)
        amps = rf_mode_B(unf, q_max=Q_MAX)
        rf_med = float(np.median(amps[1:]))
        threshold = RF_SPIKE_FACTOR * rf_med
        spike_qs = [q for q in range(2, Q_MAX + 1) if amps[q - 1] > threshold]
        spike_qs_per_seed.append(spike_qs)
        # |a_q| at q = K (if in range)
        a_q_K = float(amps[K - 1]) if 1 <= K <= Q_MAX else float('nan')
        a_q_at_K_per_seed.append(a_q_K)
    return dict(K=K,
                 spike_qs_per_seed=spike_qs_per_seed,
                 a_q_at_K_per_seed=a_q_at_K_per_seed,
                 rf_median_q_ge_2_last=float(rf_med) if 'rf_med' in
                     dir() else float('nan'))


def main() -> dict:
    print("=" * 72)
    print("Phase 34c pooling-artifact check on q=17 (ec-root-minus-SO-odd)")
    print("=" * 72)
    e = load_ec_curves()
    minus = ec_by_root_number(e, -1)
    plus = ec_by_root_number(e, +1)
    print(f"  EC curves available: root_minus={len(minus)}, "
          f"root_plus={len(plus)}")

    out = {'sub_pool_results_root_minus': [],
           'sub_pool_results_root_plus_for_control': []}

    for K in SUB_POOL_SIZES:
        if K > len(minus):
            print(f"  K={K} > root-minus pool size {len(minus)}, skipping")
            continue
        r = run_subpool_test(minus, K)
        out['sub_pool_results_root_minus'].append(r)
        if K <= Q_MAX:
            a_at_K_vals = r['a_q_at_K_per_seed']
            print(f"  root-minus K={K:>2}: |a_{K}| per seed = "
                  f"{[f'{v:.3e}' for v in a_at_K_vals]}")
            print(f"    spike_qs_per_seed: {r['spike_qs_per_seed']}")

    print()
    for K in SUB_POOL_SIZES:
        if K > len(plus):
            continue
        r = run_subpool_test(plus, K)
        out['sub_pool_results_root_plus_for_control'].append(r)
        if K <= Q_MAX:
            a_at_K_vals = r['a_q_at_K_per_seed']
            print(f"  root-plus  K={K:>2}: |a_{K}| per seed = "
                  f"{[f'{v:.3e}' for v in a_at_K_vals]}")
            print(f"    spike_qs_per_seed: {r['spike_qs_per_seed']}")

    # ── Pooling-matched RMT null on the real K=17 root-minus panel ───
    print(f"\n[pooled-RMT null on root-minus K=17 panel]")
    # Real
    minus_unf = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                   for c in minus], substrate='ec')
    minus_unf = cap_events(minus_unf, cap=N_MAX_SURVEY)
    real_amps = rf_mode_B(minus_unf, q_max=Q_MAX)
    print(f"  real |a_{17}| = {real_amps[16]:.3e}")
    # Surrogate: 17 independent β=1 ensembles, ~per-curve size 2000,
    # pooled
    N_SEEDS = 500
    t0 = time.perf_counter()
    sur_amps_17 = []
    rng = np.random.default_rng(34)
    for s in range(N_SEEDS):
        sur_unf = pooled_rmt_surrogate(K=17, per_object_size=2000,
                                          beta=1.0,
                                          seed=int(rng.integers(0, 2**31 - 1)))
        sur_unf = cap_events(sur_unf, cap=N_MAX_SURVEY)
        if sur_unf.size < 100:
            continue
        amps = rf_mode_B(sur_unf, q_max=Q_MAX)
        sur_amps_17.append(amps)
    sur_amps_17 = np.asarray(sur_amps_17)
    elapsed = time.perf_counter() - t0
    print(f"  {N_SEEDS} pooled-RMT surrogates in {elapsed:.1f}s")
    p_val_q17 = float(np.mean(sur_amps_17[:, 16] >= real_amps[16]))
    ratio = float(real_amps[16] / max(sur_amps_17[:, 16].mean(), 1e-30))
    print(f"  q=17 vs pooled-RMT null: real={real_amps[16]:.3e}, "
          f"sur_mean={sur_amps_17[:, 16].mean():.3e}, "
          f"ratio={ratio:.2f}×, p={p_val_q17:.4f}, "
          f"survives_p<0.001={p_val_q17 < 0.001}")

    out['pooled_rmt_null_q17_root_minus'] = dict(
        real_a17=float(real_amps[16]),
        sur_mean_a17=float(sur_amps_17[:, 16].mean()),
        sur_std_a17=float(sur_amps_17[:, 16].std()),
        ratio=ratio,
        p_value=p_val_q17,
        survives_p_lt_0p001=bool(p_val_q17 < 0.001),
        n_seeds=int(N_SEEDS),
    )
    out_path = OUT_DIR / 'pooling_artifact.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n→ {out_path}")
    return out


if __name__ == '__main__':
    main()
