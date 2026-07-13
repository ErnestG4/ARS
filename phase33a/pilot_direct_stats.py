import os
"""
phase33a/pilot_direct_stats.py — Phase 33a lightweight pilot.

Rather than running the full Farey-decomposition `joint_q_profile`
(which is slow on long-duration multi-million-second NANOGrav data),
compute the load-bearing summary statistics directly per the
§7.ter.10 band-invariance proposition: under unit-mean normalization,
the NNS engine output is fully determined by the unit-mean-normalized
inter-event spacing distribution.  This bypasses the Farey/RF
decomposition and gives us the essential summary numbers in seconds
rather than minutes per pulsar.

Statistics per pulsar × mode:
  - inter-event spacing CV (coefficient of variation)
  - mass<0.3 (fraction of normalized spacings below 0.3 — BR_artifact
    indicator)
  - rep_int (repulsion integral on normalized NNS)
  - KS distance to GUE Wigner-surmise: π/2 · x · exp(-π x² / 4)
  - KS distance to Poisson: exp(-x)
  - Same on rate-matched uniform-Poisson surrogate (10 seeds for
    robust z)
  - z-scores for KS_GUE and rep against the surrogate distribution

Outputs: data/phase33a_results/pilot_direct_stats.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(os.path.expandvars(os.path.expanduser("$HOME/fmexplorer/criticality_tool")))
DATA = ROOT / 'data' / 'phase33a_results'

PULSARS = ['B1855+09', 'J0030+0451', 'J0613-0200', 'J1909-3744',
           'J0740+6620']


def gue_cdf(x: np.ndarray) -> np.ndarray:
    """CDF of GUE Wigner surmise for unit-mean spacings."""
    return 1.0 - np.exp(-np.pi * x ** 2 / 4.0)


def poisson_cdf(x: np.ndarray) -> np.ndarray:
    return 1.0 - np.exp(-x)


def ks_distance(s: np.ndarray, target_cdf) -> float:
    s = np.sort(s)
    n = len(s)
    if n < 2:
        return np.nan
    emp = np.arange(1, n + 1) / n
    th = target_cdf(s)
    return float(np.max(np.abs(emp - th)))


def rep_int(s: np.ndarray, kappa: float = 0.3) -> float:
    """Repulsion integral: fraction of normalized spacings > kappa."""
    s = np.asarray(s)
    return float((s > kappa).mean())


def normalize_unit_mean(events: np.ndarray) -> np.ndarray:
    iei = np.diff(np.sort(events))
    iei = iei[iei > 0]
    if iei.size == 0:
        return iei
    return iei / iei.mean()


def stats_for(events: np.ndarray) -> dict:
    s = normalize_unit_mean(events)
    if s.size < 30:
        return None
    return dict(
        n_intervals=int(s.size),
        cv=float(s.std() / s.mean()),
        mass_lt_0p3=float((s < 0.3).mean()),
        rep_med=rep_int(s, 0.3),
        ks_gue_med=ks_distance(s, gue_cdf),
        ks_poisson=ks_distance(s, poisson_cdf),
        spacing_min=float(s.min()),
        spacing_max=float(s.max()),
        spacing_median=float(np.median(s)),
    )


def epoch_collapse(toas: np.ndarray, eps_seconds: float = 3600.0
                   ) -> np.ndarray:
    toas_sorted = np.sort(toas)
    iei = np.diff(toas_sorted)
    is_first = np.concatenate([[True], iei > eps_seconds])
    return toas_sorted[is_first]


def run_one(pulsar: str, events: np.ndarray, mode: str,
            n_seeds: int = 10) -> dict:
    events = np.sort(events.astype(float))
    events = events - events[0]
    n = len(events)
    dur = float(events[-1])
    if dur <= 0 or n < 30:
        return None

    real = stats_for(events)
    if real is None:
        return None

    # Rate-matched uniform-Poisson surrogates
    sur_ks_gue, sur_ks_poi, sur_rep, sur_cv, sur_mass = [], [], [], [], []
    for seed in range(n_seeds):
        rng = np.random.default_rng(20260511 + seed)
        sur = np.sort(rng.uniform(0, dur, size=n))
        st = stats_for(sur)
        sur_ks_gue.append(st['ks_gue_med'])
        sur_ks_poi.append(st['ks_poisson'])
        sur_rep.append(st['rep_med'])
        sur_cv.append(st['cv'])
        sur_mass.append(st['mass_lt_0p3'])

    sur_ks_gue = np.asarray(sur_ks_gue)
    sur_ks_poi = np.asarray(sur_ks_poi)
    sur_rep = np.asarray(sur_rep)
    sur_cv = np.asarray(sur_cv)
    sur_mass = np.asarray(sur_mass)

    def z(real_v, sur_arr):
        return float((real_v - sur_arr.mean()) /
                     max(sur_arr.std(), 1e-12))

    row = dict(
        pulsar=pulsar, mode=mode, n_events=int(n), n_full=int(len(events)),
        duration_sec=dur, duration_yr=dur / (365.25 * 86400),
        ks_gue_med=real['ks_gue_med'], rep_med=real['rep_med'],
        ks_poisson=real['ks_poisson'], cv=real['cv'],
        mass_lt_0p3=real['mass_lt_0p3'],
        spacing_min=real['spacing_min'], spacing_max=real['spacing_max'],
        spacing_median=real['spacing_median'],
        sur_ks_gue_mean=float(sur_ks_gue.mean()),
        sur_ks_poi_mean=float(sur_ks_poi.mean()),
        sur_rep_mean=float(sur_rep.mean()),
        sur_cv_mean=float(sur_cv.mean()),
        sur_mass_mean=float(sur_mass.mean()),
        z_ks_gue=z(real['ks_gue_med'], sur_ks_gue),
        z_ks_poi=z(real['ks_poisson'], sur_ks_poi),
        z_rep=z(real['rep_med'], sur_rep),
        z_cv=z(real['cv'], sur_cv),
        z_mass=z(real['mass_lt_0p3'], sur_mass),
    )
    return row


def main():
    rows = []
    for pulsar in PULSARS:
        df = pd.read_feather(DATA / f'{pulsar}.feather')
        toas = df['toas'].values
        print(f"\n=== {pulsar} ===  full n={len(toas)}", flush=True)

        # Mode A: raw TOAs
        r = run_one(pulsar, toas, 'raw_toas')
        if r is not None:
            rows.append(r)
            print(f"  raw_toas (n={r['n_events']}):")
            print(f"    CV={r['cv']:.2f}  (sur {r['sur_cv_mean']:.2f}, z={r['z_cv']:+.1f})")
            print(f"    mass<0.3={r['mass_lt_0p3']:.3f}  (sur {r['sur_mass_mean']:.3f}, z={r['z_mass']:+.1f})")
            print(f"    KS_GUE={r['ks_gue_med']:.3f}  (sur {r['sur_ks_gue_mean']:.3f}, z={r['z_ks_gue']:+.1f})")
            print(f"    KS_Poi={r['ks_poisson']:.3f}  (sur {r['sur_ks_poi_mean']:.3f}, z={r['z_ks_poi']:+.1f})")
            print(f"    rep_med={r['rep_med']:.3f}  (sur {r['sur_rep_mean']:.3f}, z={r['z_rep']:+.1f})")
            print(f"    median spacing (norm): {r['spacing_median']:.4f}  min {r['spacing_min']:.6f}  max {r['spacing_max']:.1f}")

        # Mode B: epoch-collapsed
        ec = epoch_collapse(toas)
        r = run_one(pulsar, ec, 'epoch_collapsed')
        if r is not None:
            rows.append(r)
            print(f"  epoch_collapsed (n={r['n_events']}):")
            print(f"    CV={r['cv']:.2f}  (sur {r['sur_cv_mean']:.2f}, z={r['z_cv']:+.1f})")
            print(f"    mass<0.3={r['mass_lt_0p3']:.3f}  (sur {r['sur_mass_mean']:.3f}, z={r['z_mass']:+.1f})")
            print(f"    KS_GUE={r['ks_gue_med']:.3f}  (sur {r['sur_ks_gue_mean']:.3f}, z={r['z_ks_gue']:+.1f})")
            print(f"    KS_Poi={r['ks_poisson']:.3f}  (sur {r['sur_ks_poi_mean']:.3f}, z={r['z_ks_poi']:+.1f})")
            print(f"    rep_med={r['rep_med']:.3f}  (sur {r['sur_rep_mean']:.3f}, z={r['z_rep']:+.1f})")
            print(f"    median spacing (norm): {r['spacing_median']:.4f}  min {r['spacing_min']:.6f}  max {r['spacing_max']:.1f}")

    out = pd.DataFrame(rows)
    out.to_parquet(DATA / 'pilot_direct_stats.parquet', index=False)
    print(f"\nWrote {DATA}/pilot_direct_stats.parquet ({len(out)} rows)", flush=True)


if __name__ == '__main__':
    main()
