"""
phase34d/run_prepilot_ars.py — Pre-pilot Step 4: ARS readout on
Gaussian prime angles.

This is the ARS-side companion to Step 3 (direct RW variance check).
Per Phase 34d brief §B bulk-vs-edge architectural note, NNS / RF Mode B /
p-adic v4 are bulk-dominated statistics that read the Wigner-Dyson
universality class but cannot distinguish CUE-vs-GUE — discrimination
between Circular ensembles requires the global moment σ²(K, X) computed
in Step 3. Step 4 reads "TR-best-fit vs BL-best-fit" against:

  - Poisson null: rate-matched Poisson on Hecke-unfolded coordinate.
    By Hecke equidistribution this IS the zeroth-order null — angles
    are uniformly distributed; the question is whether ARS detects
    departures.
  - CUE null: bulk-universal RMT right null. Per Proposition 5.3 of
    Rudnick-Waxman 2019, CUE/USp(2N)/SO(2N) all give the same min(n,N)
    bulk variance, so this is the appropriate single-family null.

Outputs
-------
data/phase34d_results/gaussian_prepilot_ars.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34c'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))

from gaussian_primes import gaussian_prime_angles, hecke_unfold_gaussian
from circular_sampler import circular_unit_mean_spacings
from arithmetic_toolkit import ramanujan_fourier
from survey_engine import (rf_mode_B, padic_v4_from_amplitudes,
                           nns_reproduction, within_window_stability,
                           poisson_unfolded_surrogate, rmt_unfolded_surrogate,
                           cap_events, N_MAX_SURVEY, Q_MAX, PRIMES,
                           RF_SPIKE_FACTOR, N_SEEDS, N_WINDOWS_STABILITY)

OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase34d_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def cue_unfolded_surrogate(n_events: int, seed: int,
                           memory_cap_N: int = 2000) -> np.ndarray:
    """Right-null surrogate: eigenphases of a Haar unitary matrix,
    unfolded to unit mean spacing.

    The Mezzadri 2007 QR recipe needs O(N²) memory which is infeasible at
    N ~ 10⁵. By Katz-Sarnak bulk universality, the bulk spacing statistics
    of CUE (Circular) and GUE (Hermite) β=2 ensembles are identical, so we
    fall back to the Dumitriu-Edelman β-Hermite β=2 tridiagonal (O(N²)
    flops, O(N) memory) when n_events > memory_cap_N. Per Phase 34d brief
    §B and RW Prop 5.3, the U(N) / USp / SO bulk variances are
    indistinguishable in the leading order, so this substitution preserves
    the right-null character.
    """
    rng = np.random.default_rng(seed)
    if n_events + 1 <= memory_cap_N:
        sp = circular_unit_mean_spacings(n_events + 1, 'CUE', rng)
        return np.cumsum(sp)
    # Fall back to GUE β=2 Hermite ensemble (bulk-universal with CUE)
    return rmt_unfolded_surrogate(n_events, beta=2.0, seed=seed)


def survey_vs_null_minimal(unfolded: np.ndarray, label: str,
                           null_kind: str,
                           n_seeds: int = 200,
                           q_max: int = Q_MAX) -> dict:
    """Light single-process survey: real vs n_seeds surrogates of given kind.

    null_kind: 'poisson' or 'cue'.
    """
    n_events = unfolded.size
    real_amps = rf_mode_B(unfolded, q_max=q_max)
    real_pv4 = padic_v4_from_amplitudes(real_amps, q_max=q_max,
                                        primes=PRIMES)
    rf_med = float(np.median(real_amps[1:]))
    threshold = RF_SPIKE_FACTOR * rf_med
    spike_qs = [q for q in range(2, q_max + 1)
                if real_amps[q - 1] > threshold]
    print(f"  [{label}] vs {null_kind}: real |a_q| median = {rf_med:.4f}, "
          f"spike q at 5×med: {spike_qs}")
    print(f"    p-adic dom_per_q (real): p={real_pv4['dominant_prime_per_q']}")

    t0 = time.perf_counter()
    sur_amps = np.zeros((n_seeds, q_max), dtype=np.float64)
    sur_dom = np.zeros(n_seeds, dtype=np.int32)
    for s in range(n_seeds):
        if null_kind == 'poisson':
            sur = poisson_unfolded_surrogate(n_events, s)
        elif null_kind == 'cue':
            sur = cue_unfolded_surrogate(n_events, s)
        else:
            raise ValueError(null_kind)
        a_q = rf_mode_B(sur, q_max=q_max)
        sur_amps[s] = a_q
        pv4_s = padic_v4_from_amplitudes(a_q, q_max=q_max, primes=PRIMES)
        sur_dom[s] = int(pv4_s.get('dominant_prime_per_q', 0))
    elapsed = time.perf_counter() - t0
    print(f"    {n_seeds} surrogates in {elapsed:.1f}s")

    # Survival p-values per q
    p_values = {}
    for q in range(2, q_max + 1):
        n_geq = int(np.sum(sur_amps[:, q - 1] >= real_amps[q - 1]))
        p_values[q] = (n_geq + 1) / (n_seeds + 1)

    # p-adic dom_per_q match probability
    real_dom = int(real_pv4['dominant_prime_per_q'])
    sur_dom_freq = {int(p): int(np.sum(sur_dom == p)) for p in PRIMES}
    p_dom = (sur_dom_freq.get(real_dom, 0) + 1) / (n_seeds + 1)

    return dict(
        null_kind=null_kind,
        n_seeds=n_seeds,
        real_amps=real_amps.tolist(),
        spike_qs=spike_qs,
        spike_threshold=threshold,
        median_amp=rf_med,
        p_values_per_q={int(q): float(v) for q, v in p_values.items()},
        dominant_prime_per_q_real=real_dom,
        dom_per_q_freq=sur_dom_freq,
        dom_per_q_pvalue=float(p_dom),
        sur_amps_mean=sur_amps.mean(axis=0).tolist(),
        sur_amps_std=sur_amps.std(axis=0).tolist(),
    )


def run_panel(label: str, angles: np.ndarray, sector_length: float,
              n_seeds: int = 200) -> dict:
    """Full per-panel Step 4 pre-pilot routine."""
    print()
    print("=" * 78)
    print(f"Phase 34d Step 4 — ARS pre-pilot — panel: {label}")
    print(f"  N = {len(angles)} angles, sector = [0, {sector_length:.4f})")
    print("=" * 78)

    # Hecke-unfold to unit-mean spacing coordinate
    N = len(angles)
    # Generic Hecke unfold: density = N / sector_length, so unfolded = angle * (N / sector_length)
    unfolded_full = angles * (N / sector_length)
    spacings = np.diff(unfolded_full)
    print(f"  unfolded: mean spacing = {np.mean(spacings):.4f}  CV = "
          f"{np.std(spacings)/np.mean(spacings):.4f}")
    # Cap to N_MAX_SURVEY=5000 events for RMT surrogate runtime, matching the
    # Phase 34c convention. Stride-decimation preserves mean spacing under
    # the unfolded coordinate. NNS, within-window, and Poisson-null comparisons
    # run on the FULL unfolded data (no decimation artifact). Only the GUE/CUE
    # surrogate uses the decimated unfolded due to Dumitriu-Edelman O(N²) cost.
    unfolded = cap_events(unfolded_full, cap=N_MAX_SURVEY)
    if unfolded.size != unfolded_full.size:
        print(f"  capped events for GUE surrogate: {unfolded_full.size} → "
              f"{unfolded.size} (stride-decimated); NNS/Poisson run on full N")

    # 1. NNS classification on FULL unfolded data (no decimation artifact)
    print()
    print(f"  --- NNS classification on FULL N (joint_q_profile, q_max={Q_MAX}) ---")
    nns_full = nns_reproduction(unfolded_full, label + '_full')

    # 2. NNS on CAPPED data (apples-to-apples with GUE surrogate)
    nns_capped = None
    if unfolded.size != unfolded_full.size:
        print()
        print(f"  --- NNS classification on CAPPED N (matches GUE surrogate) ---")
        nns_capped = nns_reproduction(unfolded, label + '_capped')

    # 3. Within-window stability falsifier (on FULL data)
    print()
    print(f"  --- within-window stability ({N_WINDOWS_STABILITY} windows) on FULL N ---")
    stability = within_window_stability(unfolded_full, label, q_max=Q_MAX)

    # 4. RF Mode B + p-adic v4 vs Poisson null (FULL N — Poisson surrogate fast at any N)
    print()
    print(f"  --- RF Mode B + p-adic v4 vs POISSON null (FULL N) ---")
    vs_poisson = survey_vs_null_minimal(unfolded_full, label, 'poisson',
                                        n_seeds=n_seeds)

    # 5. RF Mode B + p-adic v4 vs CUE null (capped N — GUE surrogate O(N²))
    print()
    print(f"  --- RF Mode B + p-adic v4 vs CUE null (CAPPED N for GUE surrogate cost) ---")
    vs_cue = survey_vs_null_minimal(unfolded, label, 'cue',
                                    n_seeds=n_seeds)

    return dict(
        label=label,
        n_events=int(N),
        n_events_capped=int(unfolded.size),
        sector_length=float(sector_length),
        mean_spacing_unfolded=float(np.mean(spacings)),
        cv_spacings=float(np.std(spacings) / np.mean(spacings)),
        nns_full=nns_full,
        nns_capped=nns_capped,
        stability=stability,
        vs_poisson=vs_poisson,
        vs_cue=vs_cue,
    )


def main():
    n_seeds = 200       # light pre-pilot; substantive run uses N_SEEDS=1000

    panels = {}

    # Gaussian primes at X = 10⁵ — un-decimated, N ≈ 9567 < N_MAX_SURVEY = 5000
    # ABOVE the cap, but we want to compare full-data classification to
    # decimated. Re-runs with stride-decimation cap unchanged.
    print("Generating Gaussian prime angles at X = 10⁵ (N~9.5K, capped to 5K)...")
    gauss_1e5 = gaussian_prime_angles(100_000, both_ideals=True)
    panels['gaussian_X1e5'] = run_panel('gaussian_X1e5', gauss_1e5,
                                        sector_length=np.pi / 2,
                                        n_seeds=n_seeds)

    print()
    print("Generating Gaussian prime angles at X = 10⁶ (N~78K, capped to 5K)...")
    gauss_1e6 = gaussian_prime_angles(1_000_000, both_ideals=True)
    panels['gaussian_X1e6'] = run_panel('gaussian_X1e6', gauss_1e6,
                                        sector_length=np.pi / 2,
                                        n_seeds=n_seeds)

    out_path = OUT_DIR / 'gaussian_prepilot_ars.json'
    with open(out_path, 'w') as f:
        json.dump({
            'phase': '34d',
            'step': 'pre-pilot Step 4 / ARS readout on Gaussian angles',
            'panels': panels,
        }, f, indent=2)
    print(f"\n→ wrote ARS pre-pilot results to {out_path}")


if __name__ == '__main__':
    main()
