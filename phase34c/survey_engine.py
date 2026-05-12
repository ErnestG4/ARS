"""
phase34c/survey_engine.py — shared survey routines for spectral-
coordinate substrates.

Implements the four per-panel survey steps:
  (1) stationarity (phase30 module, 10-window)
  (2) NNS-engine reproduction (deployed joint_q_profile, Q_MAX=30,
      JPF_CAP=1500)
  (3) within-window stability — surrogate-independent falsifier
      (5 non-overlapping sub-windows)
  (4) RF + p-adic v4 against TWO nulls:
        - wrong null: rate-matched Poisson on unfolded coordinate
        - right null: substrate-family RMT-unfolded surrogate
                       (β-Hermite via Dumitriu–Edelman, central 85%)

RF mode B (normalize=True on unfolded spacings) is primary;
RF mode A (indicator-mode on discretised γ) is run as a robustness
panel with bin-width sensitivity across 3-5 nearby widths.
"""
from __future__ import annotations

import os
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase22a'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase30'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'phase34a'))

from arithmetic_toolkit import (ramanujan_fourier, padic_amplitude_v4,
                                  _phi)
from fast_rf import fast_rf_indicator, fast_padic_v4
from ars_classify import classify
from stationarity import classify_in_windows, stationarity_summary
from rmt_sampler import sample_rmt_unfolded


Q_MAX = 30
Q_MAX_ROBUST = 20            # EC L robustness panel
PRIMES = (2, 3, 5, 7, 11, 13)
N_SEEDS = 1000
N_WINDOWS_STAT = 10
N_WINDOWS_STABILITY = 5
RF_SPIKE_FACTOR = 5.0
N_MAX_SURVEY = 5_000        # cap for RF surrogate ensemble runtime
                              # RMT eigenvalue sampling via Dumitriu–
                              # Edelman tridiagonal is O(N²); at N=5K
                              # one sample takes ~250 ms → 1000 surr.
                              # = ~4 min/panel.  Stride-decimation
                              # preserves spacing distribution since
                              # the unfolded sequence has unit mean
                              # spacing by construction.


def cap_events(unfolded: np.ndarray, cap: int = N_MAX_SURVEY) -> np.ndarray:
    """Stride-decimate the unfolded sequence to ≤ cap events.  Mean
    spacing 1 is preserved (the sub-sequence's spacing distribution
    has mean ≈ stride × 1 = stride, but spacings are renormalised to
    unit mean by `ramanujan_fourier(normalize=True)` downstream).
    """
    if unfolded.size <= cap:
        return unfolded
    stride = max(1, unfolded.size // cap)
    return unfolded[::stride][:cap]


# ─── Mode-B normalised RF (spacing-coordinate; primary) ──────────────────────


def rf_mode_B(unfolded: np.ndarray, q_max: int = Q_MAX) -> np.ndarray:
    """Return |a_q| for q = 1..q_max via normalize=True RF on the
    unit-mean unfolded sequence."""
    rf = ramanujan_fourier(unfolded.astype(np.float64),
                            q_max=q_max, normalize=True)
    amps = np.asarray(rf.get('amplitudes', []), dtype=np.float64)
    if amps.size != q_max:
        return np.full(q_max, np.nan)
    return np.abs(amps)


def padic_v4_from_amplitudes(amps: np.ndarray,
                              q_max: int = Q_MAX,
                              primes: tuple = PRIMES) -> dict:
    """Compute p-adic v4 amplitudes from a pre-computed |a_q| array
    (used for normalize-mode RF where the deployed padic_amplitude_v4
    is hard-coded to normalize=False)."""
    if amps.size != q_max:
        return dict(error='wrong amps size', dominant_prime=0,
                     dominant_prime_per_q=0)
    total_power = float(np.sum(amps[1:])) + 1e-12
    mean_amp_all = float(np.mean(amps[1:])) + 1e-12

    per_prime = {}
    dom_sum = (None, -1.0)
    dom_per_q = (None, -1.0)
    for p in primes:
        q_pows = []
        q_pow = p
        while q_pow <= q_max:
            q_pows.append(int(q_pow))
            q_pow *= p
        if not q_pows:
            per_prime[int(p)] = dict(amplitude=0.0, normalised=0.0,
                                       normalised_per_q=0.0, q_powers=[])
            continue
        p_power = float(sum(amps[q - 1] for q in q_pows))
        mean_p = p_power / len(q_pows)
        normed_sum = p_power / total_power
        normed_per_q = mean_p / mean_amp_all
        per_prime[int(p)] = dict(amplitude=p_power, normalised=normed_sum,
                                   normalised_per_q=normed_per_q,
                                   mean_amplitude=mean_p,
                                   q_powers=q_pows)
        if normed_sum > dom_sum[1]:
            dom_sum = (int(p), normed_sum)
        if normed_per_q > dom_per_q[1]:
            dom_per_q = (int(p), normed_per_q)
    return dict(per_prime=per_prime, total_power=total_power,
                 mean_amplitude=mean_amp_all,
                 dominant_prime=int(dom_sum[0]) if dom_sum[0] is not None else 0,
                 dominant_prime_per_q=int(dom_per_q[0]) if dom_per_q[0] is not None else 0)


# ─── Null generators ─────────────────────────────────────────────────────────


def poisson_unfolded_surrogate(n_events: int, seed: int) -> np.ndarray:
    """±1-rate Poisson process surrogate on the unfolded coordinate.

    Generates n_events exponential(1) spacings, cumulates → unfolded
    coordinate with mean spacing 1.  This is the wrong null for
    spectral-coordinate substrates (destroys the Wigner-Dyson level
    repulsion that the unfolding-respecting null would preserve).
    """
    rng = np.random.default_rng(seed)
    spacings = rng.exponential(scale=1.0, size=n_events)
    return np.cumsum(spacings)


def rmt_unfolded_surrogate(n_events: int, beta: float, seed: int,
                             edge_exclude_frac: float = 0.075) -> np.ndarray:
    """RMT right-null surrogate via Dumitriu–Edelman β-Hermite.

    Inflates n_events to account for edge-exclusion: N_raw = n_events /
    (1 - 2·edge_exclude_frac) so the retained bulk is approximately
    n_events.
    """
    N_raw = int(np.ceil(n_events / (1.0 - 2.0 * edge_exclude_frac)))
    rng = np.random.default_rng(seed)
    nt = sample_rmt_unfolded(N_raw, beta, edge_exclude_frac=edge_exclude_frac,
                               rng=rng)
    nt = nt[~np.isnan(nt)]
    # Sort and trim to n_events to keep apples-to-apples sample size
    nt = np.sort(nt)
    if nt.size > n_events:
        # Take a contiguous middle slice
        excess = nt.size - n_events
        start = excess // 2
        nt = nt[start:start + n_events]
    return nt


# ─── Per-panel survey ───────────────────────────────────────────────────────


def stationarity_check(unfolded: np.ndarray, label: str) -> dict:
    """Run phase30 10-window stationarity check on unfolded coords."""
    total_duration = float(unfolded.max() - unfolded.min()) + 1.0
    ev = unfolded - unfolded.min()
    per_window = classify_in_windows(ev, n_windows=N_WINDOWS_STAT,
                                       total_duration=total_duration,
                                       q_max=Q_MAX, min_events_per_q=30)
    summary = stationarity_summary(per_window)
    print(f"  [{label}] stationarity: modal={summary['modal_window']}, "
          f"frac_modal={summary['fraction_modal']:.3f}, "
          f"stationary={summary['stationary']}")
    return dict(per_window=[{k: (float(v) if isinstance(v, (np.floating, float))
                                  else int(v) if isinstance(v, (np.integer,
                                                                   bool, int))
                                  else v) for k, v in w.items()}
                              for w in per_window],
                 summary={k: (float(v) if isinstance(v, (np.floating, float))
                                else int(v) if isinstance(v, (np.integer, bool,
                                                                int))
                                else v) for k, v in summary.items()})


def nns_reproduction(unfolded: np.ndarray, label: str) -> dict:
    """Deployed joint_q_profile NNS reproduction."""
    r = classify(unfolded.astype(np.float64), q_max=Q_MAX,
                  min_events_per_q=30, return_full=True)
    print(f"  [{label}] NNS: primary={r['primary']}, "
          f"rep_med={r['rep_med']:.3f}, ks_gue_med={r['ks_gue_med']:.3f}, "
          f"n_well={r['n_well']}/{Q_MAX}")
    per_q = r['per_q']
    return dict(primary=r['primary'], rep_med=float(r['rep_med']),
                 ks_gue_med=float(r['ks_gue_med']),
                 n_events_in=int(r['n_events_in']),
                 n_events_used=int(r['n_events_used']),
                 n_well=int(r['n_well']),
                 per_q_quadrants=(per_q['quadrant'].tolist()
                                    if per_q is not None else []),
                 per_q_rep_int=(per_q['rep_int_q'].tolist()
                                  if per_q is not None else []),
                 per_q_ks_gue=(per_q['ks_gue_q'].tolist()
                                 if per_q is not None else []),
                 per_q_rf_amp=(per_q['rf_amplitude_q'].tolist()
                                 if per_q is not None else []))


def within_window_stability(unfolded: np.ndarray, label: str,
                              q_max: int = Q_MAX) -> dict:
    """Surrogate-independent falsifier across 5 non-overlapping windows.

    For each window, compute mode-B RF amplitudes.  Stability of |a_q|
    at flagged q across windows is the primary falsifier independent
    of any null choice.
    """
    print(f"  [{label}] within-window stability ({N_WINDOWS_STABILITY} "
          f"windows):")
    lo, hi = float(unfolded.min()), float(unfolded.max())
    edges = np.linspace(lo, hi + 1e-6, N_WINDOWS_STABILITY + 1)
    per_window = []
    for w in range(N_WINDOWS_STABILITY):
        sub = unfolded[(unfolded >= edges[w]) & (unfolded < edges[w + 1])]
        if sub.size < 30:
            per_window.append(dict(window=w, w_lo=float(edges[w]),
                                     w_hi=float(edges[w + 1]),
                                     n_events=int(sub.size),
                                     amps=None, note='underpowered'))
            print(f"    win {w}: n={sub.size} UNDERPOWERED")
            continue
        amps = rf_mode_B(sub, q_max=q_max)
        top = np.argsort(amps[1:])[::-1][:3] + 2
        per_window.append(dict(window=w, w_lo=float(edges[w]),
                                 w_hi=float(edges[w + 1]),
                                 n_events=int(sub.size),
                                 amps=amps.tolist()))
        cells = "  ".join(f"q={q}:{amps[q - 1]:.3e}" for q in top.tolist())
        print(f"    win {w}: n={sub.size}  top-3: {cells}")
    # CV per q across well-powered windows
    well_amps = [w['amps'] for w in per_window if w['amps'] is not None]
    if len(well_amps) < 2:
        cv_per_q = {}
    else:
        well_arr = np.asarray(well_amps)
        mean_q = well_arr.mean(axis=0)
        std_q = well_arr.std(axis=0)
        cv_q = np.where(np.abs(mean_q) > 1e-30, std_q / np.abs(mean_q),
                          np.nan)
        cv_per_q = {int(q): float(cv_q[q - 1]) for q in range(2, q_max + 1)}
    return dict(per_window=per_window, cv_per_q=cv_per_q)


def _one_surrogate_amps(args):
    """Top-level worker for multiprocessing: generate one surrogate +
    compute mode-B |a_q| + p-adic dom_per_q."""
    null_name, n_events, seed, beta_right, q_max = args
    if null_name == 'poisson':
        sur = poisson_unfolded_surrogate(n_events, seed)
    elif null_name == 'rmt':
        sur = rmt_unfolded_surrogate(n_events, beta_right, seed)
    else:
        raise ValueError(f"unknown null: {null_name}")
    if sur.size < 30:
        return np.zeros(q_max), 0
    a_q = rf_mode_B(sur, q_max=q_max)
    pv4_s = padic_v4_from_amplitudes(a_q, q_max=q_max, primes=PRIMES)
    return a_q, int(pv4_s.get('dominant_prime_per_q', 0))


def survey_vs_null(unfolded: np.ndarray, label: str,
                     null_name: str, *, null_kind: str, beta_right: float,
                     n_seeds: int = N_SEEDS,
                     q_max: int = Q_MAX,
                     n_workers: int = 16) -> dict:
    """Run RF + p-adic v4 (mode B) on real and n_seeds surrogates of
    `null_kind` ∈ {'poisson', 'rmt'}; flag spikes via 5×median;
    survival vs null at p < 0.001.

    Surrogates run in a process pool (n_workers parallel) so the RMT
    eigenvalue diagonalization can scale across cores.
    """
    from concurrent.futures import ProcessPoolExecutor

    n_events = unfolded.size
    real_amps = rf_mode_B(unfolded, q_max=q_max)
    real_pv4 = padic_v4_from_amplitudes(real_amps, q_max=q_max,
                                            primes=PRIMES)
    rf_med = float(np.median(real_amps[1:]))
    threshold = RF_SPIKE_FACTOR * rf_med
    spike_qs = [q for q in range(2, q_max + 1)
                if real_amps[q - 1] > threshold]
    print(f"  [{label}] vs {null_name}: spike q at 5× median: {spike_qs}")
    print(f"    p-adic dom_per_q (real): p={real_pv4['dominant_prime_per_q']}",
          flush=True)

    t0 = time.perf_counter()
    sur_amps = np.zeros((n_seeds, q_max), dtype=np.float64)
    sur_dom_per_q = np.zeros(n_seeds, dtype=np.int32)
    args_list = [(null_kind, n_events, s, beta_right, q_max)
                  for s in range(n_seeds)]
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        for s, (amps_s, dom_s) in enumerate(ex.map(_one_surrogate_amps,
                                                      args_list,
                                                      chunksize=20)):
            sur_amps[s] = amps_s
            sur_dom_per_q[s] = dom_s
    elapsed = time.perf_counter() - t0
    print(f"    {n_seeds} surrogates in {elapsed:.1f}s "
          f"({n_workers}-way parallel)", flush=True)

    rf_p = np.array([float(np.mean(sur_amps[:, q - 1] >= real_amps[q - 1]))
                      for q in range(1, q_max + 1)])
    survivors = []
    for q in spike_qs:
        p_val = float(rf_p[q - 1])
        ratio = float(real_amps[q - 1] / max(sur_amps[:, q - 1].mean(), 1e-30))
        survives = p_val < 0.001
        survivors.append(dict(q=int(q),
                                real_amp=float(real_amps[q - 1]),
                                sur_mean=float(sur_amps[:, q - 1].mean()),
                                sur_std=float(sur_amps[:, q - 1].std()),
                                ratio=ratio,
                                p_value=p_val,
                                survives_p_lt_0p001=bool(survives)))
        print(f"    q={q}: real={real_amps[q - 1]:.3e}, sur_mean="
              f"{sur_amps[:, q - 1].mean():.3e}, ratio={ratio:5.2f}×, "
              f"p={p_val:.4f}, survives={survives}")
    sur_dom_counter = Counter(sur_dom_per_q.tolist())
    print(f"    p-adic dom_per_q surrogate distribution: "
          f"{dict(sorted(sur_dom_counter.items()))}")
    return dict(
        null_name=null_name,
        n_events=int(n_events), n_seeds=int(n_seeds),
        rf_median_q_ge_2=rf_med,
        rf_spike_threshold=threshold,
        rf_spike_qs_real=spike_qs,
        rf_amps_real=real_amps.tolist(),
        rf_survivors=survivors,
        rf_sur_mean_per_q=sur_amps.mean(axis=0).tolist(),
        rf_sur_std_per_q=sur_amps.std(axis=0).tolist(),
        padic_dom_per_q_real=int(real_pv4['dominant_prime_per_q']),
        padic_dom_per_q_sur_dist=dict(sur_dom_counter),
        padic_per_prime_real={int(p): {k: (v if isinstance(v, (int, float, str))
                                                else list(v))
                                          for k, v in d.items()}
                                for p, d in real_pv4['per_prime'].items()},
    )


def run_panel(unfolded: np.ndarray, label: str, beta_right: float,
                q_max: int = Q_MAX) -> dict:
    """Full panel: stationarity → NNS → within-window → vs Poisson →
    vs RMT.

    For the RF surrogate-ensemble surveys, decimate to N_MAX_SURVEY
    events to bound runtime; stationarity / NNS / within-window run
    on the full unfolded data (those caps are handled internally per
    each step's deployed convention).
    """
    print(f"\n========== panel: {label}  (β_right = {beta_right}, "
          f"n_events = {unfolded.size}) ==========")
    out = dict(label=label, beta_right=float(beta_right),
                 n_events=int(unfolded.size), q_max=int(q_max))
    out['stationarity'] = stationarity_check(unfolded, label)
    out['nns_reproduction'] = nns_reproduction(unfolded, label)
    out['within_window_stability'] = within_window_stability(unfolded, label,
                                                                q_max=q_max)

    # Cap for surrogate-ensemble RF surveys
    survey_unfolded = cap_events(unfolded, cap=N_MAX_SURVEY)
    print(f"  → RF surveys use {survey_unfolded.size} events "
          f"(decimated from {unfolded.size})", flush=True)

    out['vs_poisson_wrong_null'] = survey_vs_null(
        survey_unfolded, label, 'Poisson (wrong null)',
        null_kind='poisson', beta_right=beta_right, q_max=q_max)
    out['vs_rmt_right_null'] = survey_vs_null(
        survey_unfolded, label, f'RMT β={beta_right} (right null)',
        null_kind='rmt', beta_right=beta_right, q_max=q_max)
    return out
