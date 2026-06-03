"""
phase33b/pilot_mass_spectrum.py — Phase 33b pilot.

The CMS Open Data CSV releases (record 545) provide muon kinematics
per dimuon event but no wall-clock timestamps; NanoAOD likewise
records only Run/LumiBlock/Event IDs.  Time-domain ARS framing is
unavailable at the most accessible CERN Open Data processing level —
the data is post-trigger and post-luminosity-block aggregation.

The alternative framing this pilot tests: treat the **invariant mass
spectrum** as a point process in mass space.  Each event contributes
one M value computed from the two-muon 4-vectors:

    M² = 2 · pt1 · pt2 · (cosh(η1 - η2) - cos(φ1 - φ2))
    (massless-muon approximation, valid for M ≫ m_µ = 0.106 GeV)

The mass distribution has known physics structure: peaks at J/ψ
(3.1 GeV), Υ (~9.5 GeV), Z (91 GeV) plus continuum.  ARS on the
mass-spaced point process is the LMFDB / arithmetic-instrument-
validation analog: a 1D point process in spectral coordinate where
the physics is in peak structure relative to continuum, not in time
ordering.

Direct-stats per §7.ter.10 band-invariance: CV, mass<0.3, KS to
GUE Wigner surmise, KS to Poisson, rep_int.  Surrogate: rate-matched
uniform-in-mass-range (preserves event count and mass span; should
produce flat distribution).

Outputs: data/phase33b_results/pilot_mass_spectrum_stats.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('$HOME/fmexplorer/criticality_tool')
DATA = ROOT / 'data' / 'phase33b_results'

CSV_FILES = {
    'Zmumu':       'Zmumu.csv',
    'Jpsimumu':    'Jpsimumu.csv',
    'Ymumu':       'Ymumu.csv',
    'Dimuon_full': 'Dimuon_DoubleMu.csv',
}


def gue_cdf(x):
    return 1.0 - np.exp(-np.pi * x ** 2 / 4.0)


def poisson_cdf(x):
    return 1.0 - np.exp(-x)


def ks_distance(s, target_cdf):
    s = np.sort(s)
    n = len(s)
    if n < 2:
        return np.nan
    emp = np.arange(1, n + 1) / n
    th = target_cdf(s)
    return float(np.max(np.abs(emp - th)))


def rep_int(s, kappa=0.3):
    return float((np.asarray(s) > kappa).mean())


def normalize_unit_mean(events):
    iei = np.diff(np.sort(events))
    iei = iei[iei > 0]
    if iei.size == 0:
        return iei
    return iei / iei.mean()


def stats_for(events):
    s = normalize_unit_mean(events)
    if s.size < 30:
        return None
    return dict(
        n=int(s.size),
        cv=float(s.std() / s.mean()),
        mass_lt_0p3=float((s < 0.3).mean()),
        rep_med=rep_int(s, 0.3),
        ks_gue_med=ks_distance(s, gue_cdf),
        ks_poisson=ks_distance(s, poisson_cdf),
        median=float(np.median(s)),
        smin=float(s.min()),
        smax=float(s.max()),
    )


def compute_invariant_mass(df):
    """Massless-muon invariant mass: M² = 2 pt1 pt2 (cosh(Δη) - cos(Δφ))."""
    pt1, eta1, phi1 = df['pt1'].values, df['eta1'].values, df['phi1'].values
    pt2, eta2, phi2 = df['pt2'].values, df['eta2'].values, df['phi2'].values
    deta = eta1 - eta2
    dphi = phi1 - phi2
    m2 = 2.0 * pt1 * pt2 * (np.cosh(deta) - np.cos(dphi))
    m2 = np.where(m2 > 0, m2, 0.0)
    return np.sqrt(m2)


def run_one(name, masses, n_seeds=10):
    masses = np.sort(masses[np.isfinite(masses) & (masses > 0)])
    if masses.size < 30:
        return None
    real = stats_for(masses)
    if real is None:
        return None

    # Rate-matched uniform-in-mass-range surrogate
    m_min, m_max = float(masses.min()), float(masses.max())
    sur_stats = {k: [] for k in
                 ['cv', 'mass_lt_0p3', 'rep_med', 'ks_gue_med',
                  'ks_poisson']}
    for seed in range(n_seeds):
        rng = np.random.default_rng(20260511 + seed)
        sur = np.sort(rng.uniform(m_min, m_max, size=masses.size))
        st = stats_for(sur)
        for k in sur_stats:
            sur_stats[k].append(st[k])

    row = dict(
        sample=name, n_events=int(masses.size),
        m_min=m_min, m_max=m_max, m_median=float(np.median(masses)),
        cv=real['cv'], mass_lt_0p3=real['mass_lt_0p3'],
        rep_med=real['rep_med'], ks_gue_med=real['ks_gue_med'],
        ks_poisson=real['ks_poisson'],
    )
    for k, vlist in sur_stats.items():
        arr = np.asarray(vlist)
        row[f'sur_{k}_mean'] = float(arr.mean())
        row[f'sur_{k}_std'] = float(arr.std())
        row[f'z_{k}'] = float((real[k] - arr.mean()) /
                              max(arr.std(), 1e-12))
    return row


def main():
    rows = []
    for name, fn in CSV_FILES.items():
        path = DATA / fn
        if not path.exists():
            print(f"[skip] {path} not found", flush=True)
            continue
        df = pd.read_csv(path)
        M = compute_invariant_mass(df)
        print(f"\n=== {name} ===  n_events={len(df)}", flush=True)
        print(f"  Mass range: {M.min():.3f} – {M.max():.3f} GeV  "
              f"(median {np.median(M):.3f})", flush=True)

        r = run_one(name, M)
        if r is None:
            continue
        rows.append(r)
        print(f"  CV       = {r['cv']:.3f}  (sur {r['sur_cv_mean']:.3f}, z={r['z_cv']:+.1f})")
        print(f"  mass<0.3 = {r['mass_lt_0p3']:.3f}  (sur {r['sur_mass_lt_0p3_mean']:.3f}, z={r['z_mass_lt_0p3']:+.1f})")
        print(f"  rep_med  = {r['rep_med']:.3f}  (sur {r['sur_rep_med_mean']:.3f}, z={r['z_rep_med']:+.1f})")
        print(f"  KS_GUE   = {r['ks_gue_med']:.3f}  (sur {r['sur_ks_gue_med_mean']:.3f}, z={r['z_ks_gue_med']:+.1f})")
        print(f"  KS_Poi   = {r['ks_poisson']:.3f}  (sur {r['sur_ks_poisson_mean']:.3f}, z={r['z_ks_poisson']:+.1f})")

    out = pd.DataFrame(rows)
    out.to_parquet(DATA / 'pilot_mass_spectrum_stats.parquet', index=False)
    print(f"\nWrote {DATA}/pilot_mass_spectrum_stats.parquet "
          f"({len(out)} rows)", flush=True)


if __name__ == '__main__':
    main()
