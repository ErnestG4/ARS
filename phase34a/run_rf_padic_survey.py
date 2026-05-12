"""
phase34a/run_rf_padic_survey.py — Sub-question 3: RF engine + p-adic v4
orthogonal-channel survey on Mertens sign-change positions.

Pipeline:
  1. RF indicator-mode |a_q| for q ∈ [1, Q_MAX] on the real positions.
     Flag any q ≥ 2 with |a_q| > 5 × median(|a_q|, q ≥ 2) — the TL
     quadrant criterion.
  2. p-adic v4 dominant_prime_per_q on the real positions, primes
     {2, 3, 5, 7, 11, 13}.
  3. Generate N_SEEDS rate-matched Poisson surrogates with local
     density (K=50 bins).  Per surrogate, recompute (1) and (2).
  4. For each flagged-by-TL q: p-value = #{surrogate |a_q| ≥ real |a_q|}
     / N_SEEDS.  Survival criterion: p < 0.001.
  5. For p-adic: compare real dominant_prime_per_q against the
     surrogate distribution (fraction of surrogates with the same
     dominant prime).

Two configurations:
  - dense window [1, 4e6]:   primary, density-stationary
  - full sequence [1, 1e7]:  robustness check

Output: data/phase34a_results/rf_padic_survey.json
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

from mertens_events import load_or_compute
from fast_rf import fast_rf_indicator, fast_padic_v4
from surrogate import local_density_poisson

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)

Q_MAX = 30
RF_SPIKE_FACTOR = 5.0
PRIMES = (2, 3, 5, 7, 11, 13)
N_SEEDS = 1000
K_BINS = 50


def survey(positions: np.ndarray, label: str, n_bins: int) -> dict:
    print(f"\n[{label}] n_events: {positions.size}  n_bins: {n_bins}")
    # Real RF and p-adic
    rf = fast_rf_indicator(positions, q_max=Q_MAX, n_bins=n_bins)
    real_amps = rf['amplitudes']        # |a_q| for q=1..Q_MAX
    rf_q2 = real_amps[1:]                # q ≥ 2
    rf_med = float(np.median(rf_q2))
    rf_spike_threshold = RF_SPIKE_FACTOR * rf_med
    rf_spike_qs = [q for q in range(2, Q_MAX + 1)
                   if real_amps[q - 1] > rf_spike_threshold]
    pv4 = fast_padic_v4(positions, primes=PRIMES, q_max=Q_MAX, n_bins=n_bins)

    print(f"  RF median (q≥2): {rf_med:.4e}")
    print(f"  RF spike threshold (5× median): {rf_spike_threshold:.4e}")
    print(f"  RF spike q (real): {rf_spike_qs}")
    print(f"  p-adic v4 dominant_prime_per_q: p={pv4['dominant_prime_per_q']}")
    pp = pv4['per_prime']
    for p in PRIMES:
        d = pp[p]
        print(f"    p={p:2d}  normalised_per_q={d['normalised_per_q']:6.3f}  "
              f"normalised_sum={d['normalised']:6.4f}  "
              f"q_pows={d['q_powers']}")

    # Surrogate ensemble
    print(f"  generating {N_SEEDS} local-density Poisson surrogates "
          f"(K={K_BINS} bins)…")
    t0 = time.perf_counter()
    sur_amps = np.zeros((N_SEEDS, Q_MAX), dtype=np.float64)
    sur_dom_per_q = np.zeros(N_SEEDS, dtype=np.int32)
    sur_dom = np.zeros(N_SEEDS, dtype=np.int32)
    pos_min = int(positions.min())
    pos_max = int(positions.max())
    for s in range(N_SEEDS):
        sur_pos = local_density_poisson(positions, seed=s, K=K_BINS,
                                          t_min=pos_min, t_max=pos_max)
        if sur_pos.size < 10:
            sur_amps[s] = 0.0
            continue
        rf_s = fast_rf_indicator(sur_pos, q_max=Q_MAX, n_bins=n_bins)
        sur_amps[s] = rf_s['amplitudes']
        pv4_s = fast_padic_v4(sur_pos, primes=PRIMES, q_max=Q_MAX,
                                n_bins=n_bins)
        sur_dom_per_q[s] = pv4_s.get('dominant_prime_per_q', 0)
        sur_dom[s] = pv4_s.get('dominant_prime', 0)
    print(f"    elapsed: {time.perf_counter() - t0:.1f}s")

    # Surrogate ensemble summary at each q
    sur_med_per_q = np.median(sur_amps[:, 1:], axis=1)    # surrogate-level
    sur_amp_p_le_real_per_q = []
    for q in range(1, Q_MAX + 1):
        sa = sur_amps[:, q - 1]
        p_val = float(np.mean(sa >= real_amps[q - 1]))
        sur_amp_p_le_real_per_q.append(p_val)

    # Per spike-q, evaluate survival
    rf_survivors = []
    for q in rf_spike_qs:
        p_val = sur_amp_p_le_real_per_q[q - 1]
        survives = p_val < 0.001
        rf_survivors.append(dict(q=int(q),
                                  real_amp=float(real_amps[q - 1]),
                                  sur_amp_mean=float(sur_amps[:, q - 1].mean()),
                                  sur_amp_std=float(sur_amps[:, q - 1].std()),
                                  p_value=p_val,
                                  survives_p_lt_0p001=bool(survives)))
        print(f"  flagged q={q}: real |a_q|={real_amps[q - 1]:.4e}, "
              f"sur mean={sur_amps[:, q - 1].mean():.4e}, "
              f"p={p_val:.4f}, survives={survives}")

    # p-adic verdict
    dom_per_q_real = int(pv4['dominant_prime_per_q'])
    sur_dom_counter = Counter(sur_dom_per_q.tolist())
    surrogate_modal_prime = (sur_dom_counter.most_common(1)[0][0]
                              if sur_dom_counter else 0)
    frac_same_prime = float(sur_dom_counter.get(dom_per_q_real, 0) / N_SEEDS)
    print(f"  p-adic v4: real dom_per_q = p={dom_per_q_real}, "
          f"surrogate modal = p={surrogate_modal_prime}, "
          f"fraction surrogates matching real = {frac_same_prime:.3f}")
    # Decision rule: if the surrogate modal prime equals real's dom prime
    # AND the real's concentration metric isn't a tail outlier, it's null.
    # We also report the per-prime concentration tail probability.
    pp_real_per_q = pv4['per_prime'][dom_per_q_real]['normalised_per_q']
    # Build surrogate distribution of normalised_per_q at this prime
    # (would require re-running pv4 to get per-prime stats from surrogates;
    # the dominance-prime alone is the brief's diagnostic).

    return dict(
        label=label,
        n_events=int(positions.size),
        n_bins=int(n_bins),
        rf_median_q_ge_2=rf_med,
        rf_spike_threshold=rf_spike_threshold,
        rf_amps_real=real_amps.tolist(),
        rf_spike_qs_real=rf_spike_qs,
        rf_survivors=rf_survivors,
        rf_sur_p_per_q=sur_amp_p_le_real_per_q,
        rf_sur_mean_per_q=sur_amps[:, :].mean(axis=0).tolist(),
        rf_sur_std_per_q=sur_amps[:, :].std(axis=0).tolist(),
        padic_dominant_prime_per_q_real=dom_per_q_real,
        padic_dominant_prime_real=int(pv4['dominant_prime']),
        padic_per_prime_real={
            int(p): {k: (v if isinstance(v, (int, float, str)) else list(v))
                      for k, v in d.items()}
            for p, d in pp.items()
        },
        padic_sur_dom_per_q_distribution=dict(sur_dom_counter),
        padic_sur_dom_distribution=dict(Counter(sur_dom.tolist())),
        surrogate_n_seeds=N_SEEDS,
        surrogate_K_bins=K_BINS,
    )


def main(N_MAX: int = 10**7) -> dict:
    print("=" * 72)
    print("Phase 34a Sub-question 3: RF + p-adic v4 orthogonal-channel survey")
    print("=" * 72)
    print(f"  Q_MAX={Q_MAX}  RF_SPIKE_FACTOR={RF_SPIKE_FACTOR}  "
          f"N_SEEDS={N_SEEDS}  K_BINS={K_BINS}")

    d = load_or_compute(N_MAX)
    sc = d['signchanges']

    out_obj: dict = {
        'Q_MAX': Q_MAX,
        'RF_SPIKE_FACTOR': RF_SPIKE_FACTOR,
        'PRIMES': list(PRIMES),
        'N_SEEDS': N_SEEDS,
        'K_BINS': K_BINS,
    }

    # Primary: dense window [1, 4e6]
    dense = sc[sc < 4 * 10**6]
    dense_n_bins = 4 * 10**6  # span used for normalisation
    out_obj['dense_1_to_4e6'] = survey(dense, 'dense [1, 4e6]',
                                         n_bins=dense_n_bins)

    # Robustness: full sequence
    full_n_bins = N_MAX
    out_obj['full'] = survey(sc, 'full [1, 1e7]', n_bins=full_n_bins)

    out_path = OUT_DIR / 'rf_padic_survey.json'
    with open(out_path, 'w') as f:
        json.dump(out_obj, f, indent=2, default=str)
    print(f"\n  → {out_path}")
    return out_obj


if __name__ == '__main__':
    main()
