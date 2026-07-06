"""
phase34c/run_cross_phase.py — three-way cross-comparison
(ζ × Dirichlet × EC L) + bilateral 34a/b × 34c, with explicit two-
layer surface/deep enumeration per PHASE34C_BRIEF.md.

Surface layer: each substrate's RF |a_q| profile vs rate-matched
Poisson (the wrong null for spectral-coordinate substrates).
Deep layer: each substrate vs its right RMT-unfolded null.

The brief's pre-execution prediction:
  - Surface: DIVERGENT (Mertens/Liouville share p=2/q=2 wrong-null
    artefact from support-restricted / random-walk-generated families;
    spectral-coordinate has no small-prime modular flavor and should
    not join the p=2/q=2 equivalence class)
  - Deep: PARALLEL_NULL (all five substrates survive their right nulls)

EC L stratification stability sub-comparison: combined vs per-stratum
(root number ± separately).

Output: data/phase34c_results/cross_phase.json
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34b'))

from survey_engine import rf_mode_B, padic_v4_from_amplitudes, Q_MAX
from zeros_loaders import (load_zeta_zeros, load_dirichlet, load_ec_curves,
                             dirichlet_by_character_type, ec_by_root_number)
from unfolding import zeta_unfold, pool_unfolded
# 34a/34b loaders
from mertens_events import load_or_compute as load_mertens_full
from liouville_events import load_or_compute as load_liouville_full
from fast_rf import fast_rf_indicator, fast_padic_v4

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34c_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def amps_and_dom_modeB(unfolded: np.ndarray, q_max: int = Q_MAX) -> tuple[np.ndarray, int]:
    """Mode-B (normalize=True) RF |a_q| for q=1..q_max + dom_per_q."""
    amps = rf_mode_B(unfolded, q_max=q_max)
    pv4 = padic_v4_from_amplitudes(amps, q_max=q_max)
    return amps[1:], int(pv4['dominant_prime_per_q'])     # drop q=1 DC


def amps_and_dom_indicator(positions: np.ndarray, n_bins: int,
                              q_max: int = Q_MAX) -> tuple[np.ndarray, int]:
    """Indicator-mode RF (34a/34b convention) for the bilateral
    comparison with Mertens / Liouville sign-changes."""
    rf = fast_rf_indicator(positions.astype(np.int64), q_max=q_max,
                             n_bins=n_bins)
    pv4 = fast_padic_v4(positions.astype(np.int64), q_max=q_max,
                          n_bins=n_bins)
    return rf['amplitudes'][1:], int(pv4['dominant_prime_per_q'])


def main() -> dict:
    print("=" * 72)
    print("Phase 34c Sub-4: cross-phase three-way + bilateral 34a/b × 34c")
    print("=" * 72)

    # ─── Build mode-B amps for each 34c substrate ──────────────────────────
    print("\n[34c substrates: mode-B RF (normalize=True on unfolded spacings)]")
    zeta_full = load_zeta_zeros('odlyzko_zeros6.txt')
    zeta_low = zeta_unfold(zeta_full[:10_000])
    zeta_mid = zeta_unfold(zeta_full[100_000:200_000])
    d = load_dirichlet()
    dir_real_pool = pool_unfolded([(e['conductor'], np.asarray(e['zeros']))
                                       for e in dirichlet_by_character_type(d, True)],
                                      substrate='dirichlet')
    dir_comp_pool = pool_unfolded([(e['conductor'], np.asarray(e['zeros']))
                                       for e in dirichlet_by_character_type(d, False)],
                                      substrate='dirichlet')
    ec = load_ec_curves()
    ec_plus_pool = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                       for c in ec_by_root_number(ec, +1)],
                                      substrate='ec')
    ec_minus_pool = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                        for c in ec_by_root_number(ec, -1)],
                                       substrate='ec')
    ec_combined_pool = pool_unfolded([(c['conductor'], np.asarray(c['zeros']))
                                          for c in ec],
                                         substrate='ec')

    # Cap each to 5000 events (matches survey decimation)
    def cap_to(arr, n=5000):
        if arr.size <= n: return arr
        stride = max(1, arr.size // n)
        return arr[::stride][:n]

    substrates_modeB = {
        'zeta-low-bulk':     cap_to(zeta_low),
        'zeta-mid-height':   cap_to(zeta_mid),
        'dirichlet-real':    cap_to(dir_real_pool),
        'dirichlet-complex': cap_to(dir_comp_pool),
        'ec-root-plus':      cap_to(ec_plus_pool),
        'ec-root-minus':     cap_to(ec_minus_pool),
        'ec-combined':       cap_to(ec_combined_pool),
    }
    modeB_amps = {}
    modeB_doms = {}
    for label, arr in substrates_modeB.items():
        amps, dom = amps_and_dom_modeB(arr)
        modeB_amps[label] = amps
        modeB_doms[label] = dom
        print(f"  {label:20s}  n={arr.size:5d}  dom_per_q=p={dom}")

    # ─── Three-way pairwise correlation (within 34c) ───────────────────────
    print("\n[Three-way pairwise RF |a_q| correlation, q ∈ [2, 30]]")
    main_keys = ['zeta-low-bulk', 'zeta-mid-height',
                 'dirichlet-real', 'dirichlet-complex',
                 'ec-root-plus', 'ec-root-minus']
    pairwise_r = {}
    for i, a in enumerate(main_keys):
        for b in main_keys[i + 1:]:
            r = float(np.corrcoef(modeB_amps[a], modeB_amps[b])[0, 1])
            pairwise_r[f"{a} vs {b}"] = r
            print(f"  r({a}, {b}) = {r:+.3f}")

    # ─── Bilateral 34a × 34c, 34b × 34c (apples-to-apples: indicator-mode
    # on 34a/b raw integer positions + indicator-mode on 34c unfolded
    # coordinate discretised to integer grid; both at n=132) ────────────────
    print("\n[Bilateral 34a/b × 34c at matched sample size 132 events, "
          "indicator-mode RF apples-to-apples]")
    m_data = load_mertens_full(10**7)
    m_sc = m_data['signchanges']
    m_dense = m_sc[m_sc < 4 * 10 ** 6]
    rng = np.random.default_rng(34)
    m_idx = rng.choice(m_dense.size, size=132, replace=False)
    m_sub = np.sort(m_dense[m_idx])
    m_amps_ind, m_dom_ind = amps_and_dom_indicator(m_sub, n_bins=4 * 10 ** 6)
    print(f"  Mertens 132-event sub-sample (indicator mode): "
          f"dom_per_q = p={m_dom_ind}")

    l_data = load_liouville_full(10**9)
    l_sc = l_data['signchanges']
    l_cluster = l_sc[(l_sc >= 906_150_257) & (l_sc <= 906_488_081)]
    l_min = int(l_cluster.min())
    l_max = int(l_cluster.max())
    l_amps_ind, l_dom_ind = amps_and_dom_indicator(l_cluster - l_min,
                                                       n_bins=l_max - l_min + 1)
    print(f"  Liouville 132-event cluster (indicator mode): "
          f"dom_per_q = p={l_dom_ind}")

    # 34c at n=132: discretise unfolded coordinate to integer grid via
    # scale=10 (so unfolded mean spacing 1 → integer spacing ~10) and run
    # indicator-mode RF.  Apples-to-apples with 34a/b.
    bilateral = {}
    DISC_SCALE = 10.0
    for ckey in main_keys:
        arr = substrates_modeB[ckey]
        if arr.size < 132:
            continue
        rng_c = np.random.default_rng(34 + hash(ckey) % 1000)
        idx_c = rng_c.choice(arr.size, size=132, replace=False)
        sub_c = np.sort(arr[idx_c])
        # Discretise unfolded coords to integer grid
        disc_c = np.round(sub_c * DISC_SCALE).astype(np.int64)
        disc_c = disc_c - int(disc_c.min())
        n_bins_c = int(disc_c.max()) + 1
        a_c, d_c = amps_and_dom_indicator(disc_c, n_bins=n_bins_c)
        # Pearson r at the indicator-mode amps (same mode for all three)
        r_to_m = float(np.corrcoef(m_amps_ind, a_c)[0, 1])
        r_to_l = float(np.corrcoef(l_amps_ind, a_c)[0, 1])
        bilateral[ckey] = dict(dom_per_q_indicator=int(d_c),
                                 r_vs_mertens=r_to_m,
                                 r_vs_liouville=r_to_l)
        print(f"  34c={ckey:20s}  dom_ind=p={d_c:>2}  "
              f"r(34a Mertens)={r_to_m:+.3f}  r(34b Liouville)={r_to_l:+.3f}")

    # ─── Cross-phase verdict synthesis ────────────────────────────────────
    print("\n[Cross-phase verdict synthesis]")
    # Surface layer: which substrates share dom=p=2? (Mertens, Liouville;
    # 34c substrates' dom_per_q values)
    print(f"  Mertens dom = p=2 (34a §7.ter.47)")
    print(f"  Liouville dom = p=2 (34b §7.ter.48)")
    print(f"  34c substrate dom_per_q (mode-B on unfolded spacings):")
    for k, v in modeB_doms.items():
        print(f"    {k:20s}: p={v}")
    n_34c_at_p2 = sum(1 for v in modeB_doms.values() if v == 2)
    print(f"  → {n_34c_at_p2}/{len(modeB_doms)} 34c substrates at dom=p=2 "
          f"(wrong-null Poisson)")

    # Brief-time prediction was DIVERGENT at surface: 34a/b at p=2,
    # 34c not at p=2 (different generative family).  Tested here.
    if n_34c_at_p2 == 0:
        surface_verdict = ('DIVERGENT — 34a/b share p=2 wrong-null artefact, '
                           '34c (spectral-coordinate) does NOT join the p=2 '
                           'equivalence class.  Confirms brief-time prediction.')
    elif n_34c_at_p2 == len(modeB_doms):
        surface_verdict = ('PARALLEL_SIGNAL — all five substrates land at '
                           'p=2 wrong-null signature.  SURPRISE outcome '
                           'per brief: wrong-null artefact is substrate-'
                           'independent in a way the support-filter / '
                           'random-walk explanations do not predict.')
    else:
        surface_verdict = (f'MIXED — {n_34c_at_p2}/{len(modeB_doms)} 34c '
                           'substrates at p=2.  Stratification-specific.')
    print(f"\n  Surface-layer cross-phase verdict: {surface_verdict}")

    # Deep layer summary deferred to surveys.json's right-null survivors
    out = {
        'substrates_modeB_dom_per_q': {k: int(v) for k, v in modeB_doms.items()},
        'pairwise_pearson_r': pairwise_r,
        'bilateral_34a_b_x_34c': bilateral,
        'mertens_dom_per_q_indicator_132': int(m_dom_ind),
        'liouville_dom_per_q_indicator_132': int(l_dom_ind),
        'n_34c_at_p2': int(n_34c_at_p2),
        'surface_verdict': surface_verdict,
        'modeB_amps_per_q_2_to_30': {k: v.tolist()
                                          for k, v in modeB_amps.items()},
    }
    out_path = OUT_DIR / 'cross_phase.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\n→ {out_path}")
    return out


if __name__ == '__main__':
    main()
