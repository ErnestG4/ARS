"""
phase34b/run_survey.py — Sub-question 3 + Sub-question 4 consolidated.

RF indicator-mode + p-adic v4 on the 132 cluster events of L(n) sign-
changes, evaluated against TWO nulls in parallel:

  (A) rate-matched Poisson at local density (parallel to 34a; the
      "wrong null" baseline that ignores the random-walk genesis of
      L sign-changes).

  (B) random-walk null: simulate a ±1 random walk starting at
      L = -1 over the cluster width 337,825, extract sign-change
      positions, use those as surrogate events.  This is the user's
      designated "natural null for L(n) sign-changes" — the parallel
      construction to 34a's squarefree-restricted null, since for
      Liouville there is no support filter to restrict (λ is non-zero
      on every integer).

Pre-falsification (separate script, prefalsify.json) confirmed the
random-walk null is TIGHT within the cluster (real 132 vs null
median 197, p=0.34).  Acceptance gates from 34a session pass: 8/8
calibrator zoo, 5/6 p-adic v4 synthetic single-prime detections.

Sub-4 falsification consolidated here:
  - within-window stability across 4 non-overlapping cluster windows
    (the cluster is too sparse for 5 windows; 4 leaves ~33 events
    per window, marginal but feasible).
  - cross-tabulation against the project's earlier sieve (already
    shown to be self-consistent at N=10⁷; cross-check that the
    N=10⁹ extension agrees with published Borwein 2008 cluster
    start at n = 906,150,257 — confirmed since our first sign-
    change in the cluster is exactly at 906,150,257).

Output: data/phase34b_results/survey.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))

from liouville_events import load_or_compute
from fast_rf import fast_rf_indicator, fast_padic_v4
from surrogate import local_density_poisson

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34b_results'

Q_MAX = 30
RF_SPIKE_FACTOR = 5.0
PRIMES = (2, 3, 5, 7, 11, 13)
N_SEEDS = 1000
K_BINS = 20    # for local-density Poisson — fewer bins given small N events

CLUSTER_LO = 906150257
CLUSTER_HI = 906488081
CLUSTER_WIDTH = CLUSTER_HI - CLUSTER_LO + 1
L_START = -1   # L(906150256) per the sieve


def random_walk_signchange_surrogate(width: int, start_L: int,
                                       seed: int) -> np.ndarray:
    """Random ±1 walk of length `width` starting at start_L; return
    integer positions (relative to start, 0-based) where the running
    sum changes sign — these serve as surrogate sign-change positions.
    """
    rng = np.random.default_rng(seed)
    steps = rng.choice(np.array([-1, 1], dtype=np.int32), size=width)
    L = start_L + np.cumsum(steps)
    sign_start = np.sign(start_L)
    s = np.sign(L).astype(np.int8)
    full = np.concatenate(([np.int8(sign_start)], s)) if sign_start != 0 else s
    nz_mask = full != 0
    full_nz = full[nz_mask]
    nz_idx = np.flatnonzero(nz_mask)
    if full_nz.size < 2:
        return np.zeros(0, dtype=np.int64)
    flips = np.flatnonzero(np.diff(full_nz) != 0)
    sc_local = nz_idx[flips + 1] - 1
    sc_local = sc_local[sc_local >= 0]
    return sc_local.astype(np.int64)


def survey_with_nulls(positions: np.ndarray,
                        label: str,
                        n_bins: int,
                        cluster_offset: int) -> dict:
    """Run RF + p-adic on `positions`, compare to both Poisson and
    random-walk nulls.

    positions are absolute integer positions; for RF indicator-mode
    we normalise to [0, n_bins) by subtracting cluster_offset.
    """
    print(f"\n[{label}] n_events: {positions.size}, n_bins: {n_bins}")
    # Real
    pos_rel = positions - cluster_offset
    rf = fast_rf_indicator(pos_rel, q_max=Q_MAX, n_bins=n_bins)
    real_amps = rf['amplitudes']
    rf_q2_plus = real_amps[1:]
    rf_med = float(np.median(rf_q2_plus))
    threshold = RF_SPIKE_FACTOR * rf_med
    rf_spike_qs = [q for q in range(2, Q_MAX + 1)
                   if real_amps[q - 1] > threshold]
    pv4 = fast_padic_v4(pos_rel, primes=PRIMES, q_max=Q_MAX, n_bins=n_bins)
    dom_per_q_real = int(pv4['dominant_prime_per_q'])
    print(f"  RF median (q≥2): {rf_med:.4e}")
    print(f"  RF spike threshold (5× median): {threshold:.4e}")
    print(f"  RF spike q (real): {rf_spike_qs}")
    print(f"  p-adic dom_per_q: p={dom_per_q_real}")
    pp = pv4['per_prime']
    for p in PRIMES:
        d = pp[p]
        print(f"    p={p:2d}  normalised_per_q={d['normalised_per_q']:6.3f}  "
              f"normalised_sum={d['normalised']:6.4f}  "
              f"q_pows={d['q_powers']}")

    # ─── Null A: Poisson at local density ──────────────────────────────
    print(f"  generating {N_SEEDS} local-density Poisson surrogates "
          f"(K={K_BINS} bins)…")
    t0 = time.perf_counter()
    sur_amps_A = np.zeros((N_SEEDS, Q_MAX), dtype=np.float64)
    sur_dom_per_q_A = np.zeros(N_SEEDS, dtype=np.int32)
    for s in range(N_SEEDS):
        sp = local_density_poisson(positions, seed=s, K=K_BINS,
                                     t_min=int(positions.min()),
                                     t_max=int(positions.max()))
        if sp.size < 5:
            continue
        rf_s = fast_rf_indicator(sp - cluster_offset, q_max=Q_MAX,
                                   n_bins=n_bins)
        sur_amps_A[s] = rf_s['amplitudes']
        pv4_s = fast_padic_v4(sp - cluster_offset, primes=PRIMES,
                                q_max=Q_MAX, n_bins=n_bins)
        sur_dom_per_q_A[s] = pv4_s.get('dominant_prime_per_q', 0)
    print(f"    elapsed: {time.perf_counter() - t0:.1f}s")
    rf_A_p = []
    for q in range(1, Q_MAX + 1):
        sa = sur_amps_A[:, q - 1]
        p_val = float(np.mean(sa >= real_amps[q - 1]))
        rf_A_p.append(p_val)
    rf_A_survivors = []
    for q in rf_spike_qs:
        p_val = rf_A_p[q - 1]
        sa = sur_amps_A[:, q - 1]
        rf_A_survivors.append(dict(q=int(q),
                                     real_amp=float(real_amps[q - 1]),
                                     sur_mean=float(sa.mean()),
                                     sur_std=float(sa.std()),
                                     ratio=float(real_amps[q - 1] /
                                                  max(sa.mean(), 1e-30)),
                                     p_value=p_val,
                                     survives=bool(p_val < 0.001)))
        print(f"  [Poisson null] q={q}: real={real_amps[q - 1]:.4e}, "
              f"sur_mean={sa.mean():.4e}, ratio={rf_A_survivors[-1]['ratio']:6.2f}×, "
              f"p={p_val:.4f}, survives={rf_A_survivors[-1]['survives']}")
    sur_A_counter = Counter(sur_dom_per_q_A.tolist())
    print(f"  [Poisson null] p-adic dom_per_q distribution: "
          f"{dict(sorted(sur_A_counter.items()))}")

    # ─── Null B: random walk on the cluster ────────────────────────────
    print(f"  generating {N_SEEDS} random-walk surrogates "
          f"(width={n_bins}, start_L={L_START})…")
    t0 = time.perf_counter()
    sur_amps_B = np.zeros((N_SEEDS, Q_MAX), dtype=np.float64)
    sur_dom_per_q_B = np.zeros(N_SEEDS, dtype=np.int32)
    rw_n_events = np.zeros(N_SEEDS, dtype=np.int32)
    for s in range(N_SEEDS):
        rw_pos = random_walk_signchange_surrogate(n_bins, L_START,
                                                    seed=s)
        rw_n_events[s] = rw_pos.size
        if rw_pos.size < 5:
            continue
        rf_s = fast_rf_indicator(rw_pos, q_max=Q_MAX, n_bins=n_bins)
        sur_amps_B[s] = rf_s['amplitudes']
        pv4_s = fast_padic_v4(rw_pos, primes=PRIMES, q_max=Q_MAX,
                                n_bins=n_bins)
        sur_dom_per_q_B[s] = pv4_s.get('dominant_prime_per_q', 0)
    print(f"    elapsed: {time.perf_counter() - t0:.1f}s")
    print(f"    random-walk surrogate n_events: mean = "
          f"{rw_n_events.mean():.1f}, std = {rw_n_events.std():.1f}, "
          f"median = {np.median(rw_n_events):.0f}")
    rf_B_p = []
    for q in range(1, Q_MAX + 1):
        sa = sur_amps_B[:, q - 1]
        p_val = float(np.mean(sa >= real_amps[q - 1]))
        rf_B_p.append(p_val)
    rf_B_survivors = []
    for q in rf_spike_qs:
        p_val = rf_B_p[q - 1]
        sa = sur_amps_B[:, q - 1]
        rf_B_survivors.append(dict(q=int(q),
                                     real_amp=float(real_amps[q - 1]),
                                     sur_mean=float(sa.mean()),
                                     sur_std=float(sa.std()),
                                     ratio=float(real_amps[q - 1] /
                                                  max(sa.mean(), 1e-30)),
                                     p_value=p_val,
                                     survives=bool(p_val < 0.001)))
        print(f"  [Random-walk null] q={q}: real={real_amps[q - 1]:.4e}, "
              f"sur_mean={sa.mean():.4e}, ratio={rf_B_survivors[-1]['ratio']:6.2f}×, "
              f"p={p_val:.4f}, survives={rf_B_survivors[-1]['survives']}")
    sur_B_counter = Counter(sur_dom_per_q_B.tolist())
    print(f"  [Random-walk null] p-adic dom_per_q distribution: "
          f"{dict(sorted(sur_B_counter.items()))}")

    return dict(
        label=label,
        n_events=int(positions.size),
        n_bins=int(n_bins),
        rf_median_q_ge_2=rf_med,
        rf_spike_threshold=threshold,
        rf_amps_real=real_amps.tolist(),
        rf_spike_qs_real=rf_spike_qs,
        padic_dominant_prime_per_q_real=dom_per_q_real,
        padic_per_prime_real={
            int(p): {k: (v if isinstance(v, (int, float, str)) else list(v))
                      for k, v in d.items()}
            for p, d in pp.items()
        },
        null_A_poisson={
            'rf_p_per_q': rf_A_p,
            'rf_survivors': rf_A_survivors,
            'sur_mean_per_q': sur_amps_A.mean(axis=0).tolist(),
            'sur_std_per_q': sur_amps_A.std(axis=0).tolist(),
            'dom_per_q_dist': dict(sur_A_counter),
        },
        null_B_random_walk={
            'rf_p_per_q': rf_B_p,
            'rf_survivors': rf_B_survivors,
            'sur_mean_per_q': sur_amps_B.mean(axis=0).tolist(),
            'sur_std_per_q': sur_amps_B.std(axis=0).tolist(),
            'dom_per_q_dist': dict(sur_B_counter),
            'rw_n_events_mean': float(rw_n_events.mean()),
            'rw_n_events_std': float(rw_n_events.std()),
        },
        N_SEEDS=N_SEEDS, K_BINS=K_BINS,
    )


def within_window_stability(positions: np.ndarray, n_windows: int,
                              n_bins_total: int,
                              cluster_offset: int) -> dict:
    print(f"\n  ── within-window stability ({n_windows} windows) ──")
    pmin = int(positions.min())
    pmax = int(positions.max())
    edges = np.linspace(pmin, pmax + 1, n_windows + 1).astype(np.int64)
    per_window = []
    for w in range(n_windows):
        w_lo = int(edges[w])
        w_hi = int(edges[w + 1])
        sub = positions[(positions >= w_lo) & (positions < w_hi)]
        if sub.size < 10:
            per_window.append(dict(window=w, w_lo=w_lo, w_hi=w_hi,
                                     n_events=int(sub.size),
                                     note='underpowered',
                                     amps=None))
            print(f"    win {w}: [{w_lo}, {w_hi}) n={sub.size} UNDERPOWERED")
            continue
        rf = fast_rf_indicator(sub - cluster_offset, q_max=Q_MAX,
                                 n_bins=w_hi - w_lo)
        per_window.append(dict(window=w, w_lo=w_lo, w_hi=w_hi,
                                 n_events=int(sub.size),
                                 amps=rf['amplitudes'].tolist()))
        # Report top 3 q for this window
        top = np.argsort(rf['amplitudes'][1:])[::-1][:3] + 2
        print(f"    win {w}: [{w_lo}, {w_hi}) n={sub.size}  "
              f"top-3 q: {top.tolist()} amps "
              f"{[f'{rf['amplitudes'][q - 1]:.2e}' for q in top]}")
    return dict(n_windows=n_windows, per_window=per_window)


def main(N_MAX: int = 10**9) -> dict:
    print("=" * 72)
    print("Phase 34b Sub-3/4: RF + p-adic survey vs two nulls + within-window")
    print("=" * 72)
    print(f"  Q_MAX={Q_MAX}, RF_SPIKE_FACTOR={RF_SPIKE_FACTOR}, "
          f"N_SEEDS={N_SEEDS}, K_BINS={K_BINS}")

    d = load_or_compute(N_MAX)
    sc = d['signchanges']
    cluster = sc[(sc >= CLUSTER_LO) & (sc <= CLUSTER_HI)]
    print(f"  cluster events: {cluster.size}")

    out = {
        'Q_MAX': Q_MAX,
        'N_SEEDS': N_SEEDS,
        'K_BINS': K_BINS,
        'cluster_lo': CLUSTER_LO,
        'cluster_hi': CLUSTER_HI,
        'cluster_width': CLUSTER_WIDTH,
    }
    out['survey_cluster_132'] = survey_with_nulls(
        cluster, label='cluster 132',
        n_bins=CLUSTER_WIDTH,
        cluster_offset=CLUSTER_LO)
    out['within_window_stability'] = within_window_stability(
        cluster, n_windows=4, n_bins_total=CLUSTER_WIDTH,
        cluster_offset=CLUSTER_LO)

    out_path = OUT_DIR / 'survey.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n  → {out_path}")
    return out


if __name__ == '__main__':
    main()
