"""
arsrh/solar_surrogate_port.py — §3a rate-envelope-preserving surrogate on solar M+X flares.

Prereg: arsrh/SOLAR_PREREG_SEALED.json (sealed before this ran). The sharpest §3a test in the
program: solar M+X flare rate has a ~1000x non-stationary SOLAR-CYCLE envelope (1 event/yr at
minimum, 1865 at maximum), so the flagged clustering (deployed detector: 191/191 BL rows exact-0)
could be ENTIRELY that rate modulation -- a Cox process -- not intrinsic flare clustering.

Construction (load_solar_M_plus, run_phase15_cross_signal.py:131-142): single pooled train of M+X
inter-flare intervals, normalized (diff/diff.mean()), cumsum, subsampled to 2000. NOT per-unit;
neither fungal result transfers.

Surrogate: rate-envelope-preserving INHOMOGENEOUS POISSON. Estimate lambda(t) by kernel-smoothing
the real flare onsets at a bandwidth that captures the cycle (>> mean ISI, << 11 yr); draw
inhomogeneous-Poisson events with that intensity. This preserves the solar cycle and destroys any
INTRINSIC short-range clustering. Sweep the bandwidth (the verdict is bandwidth-sensitive; report
the curve, not one value).

Two deliverables, both re-established from scratch (not transferred from fungal):
  (1) mass03 survival vs the inhomogeneous-Poisson null across the bandwidth sweep -- is the
      clustering intrinsic (beyond the cycle) or rate-envelope-driven?
  (2) where the null lands relative to the near-zero-NEGATIVE clip band (the dormant-bug question).

Run:  $HOME/fmexplorer/bin/python3 arsrh/solar_surrogate_port.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from arithmetic_toolkit import pair_correlation_full   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260724)
N_TARGET = 2000
DAY = 86400.0


def load_solar_onsets():
    p = os.path.join(_ROOT, "data", "solar_flares_plutino_1986_2023.csv")
    df = pd.read_csv(p, low_memory=False)
    df["tstart"] = pd.to_datetime(df["tstart"], errors="coerce")
    df = df.dropna(subset=["tstart"]).sort_values("tstart")
    df = df[df["cat"].isin(["M", "X"])]
    t0 = df["tstart"].iloc[0]
    return np.sort((df["tstart"] - t0).dt.total_seconds().to_numpy())


def normspacing_pool(onsets):
    """Deployed construction: normalized inter-event intervals -> cumsum -> subsample to N_TARGET."""
    diffs = np.diff(onsets)
    diffs = diffs[diffs > 0]
    t = np.cumsum(diffs / diffs.mean())
    if t.size > N_TARGET:
        step = t.size // N_TARGET
        t = t[::step][:N_TARGET]
    return t


def mass03(t):
    sp = np.diff(t)
    sp = sp[sp > 0]
    return float((sp / sp.mean() < 0.3).mean())


def rate_envelope(onsets, bw_sec):
    """lambda(t) by Gaussian-kernel smoothing the onsets, on a daily grid."""
    T = onsets[-1]
    grid = np.arange(0, T + DAY, DAY)
    # histogram then Gaussian smooth (fast KDE)
    counts, edges = np.histogram(onsets, bins=np.arange(0, T + 2 * DAY, DAY))
    from scipy.ndimage import gaussian_filter1d
    lam = gaussian_filter1d(counts.astype(float), bw_sec / DAY) / DAY   # events/sec per day-bin
    lam = np.maximum(lam, 1e-12)
    return grid[:len(lam)], lam


def inhomogeneous_poisson(grid, lam, n_target):
    """Draw events with intensity lambda(t) by thinning a homogeneous Poisson at lam.max()."""
    T = grid[-1]
    lam_max = lam.max()
    m = int(lam_max * T * 1.3) + 100
    cand = np.sort(RNG.uniform(0, T, size=m))
    lam_at = np.interp(cand, grid, lam)
    keep = cand[RNG.uniform(0, lam_max, size=cand.size) < lam_at]
    return np.sort(keep)


def main():
    onsets = load_solar_onsets()
    real_t = normspacing_pool(onsets)
    real_mass = mass03(real_t)
    real_irep = float(pair_correlation_full(real_t).get("repulsion_integral", 0.0))
    span_yr = onsets[-1] / DAY / 365.25
    print(f"Solar M+X: {onsets.size} flares over {span_yr:.1f} yr; deployed pool n={real_t.size}")
    print(f"  observed mass03 = {real_mass:.4f}  (homogeneous-Poisson ref 0.259);  "
          f"I_rep(recon) = {real_irep:+.4f}\n")
    print("Rate-envelope-preserving inhomogeneous-Poisson null, bandwidth sweep:")
    print(f"  {'bw (days)':>10s} {'null mass03 mean±sd':>22s} {'real z':>8s} {'null I_rep':>12s} "
          f"{'verdict':>16s}")

    rows = []
    for bw_days in (15, 30, 45, 60, 90):
        grid, lam = rate_envelope(onsets, bw_days * DAY)
        m_null, ir_null = [], []
        for _ in range(120):
            ev = inhomogeneous_poisson(grid, lam, onsets.size)
            if ev.size < 100:
                continue
            t = normspacing_pool(ev)
            m_null.append(mass03(t))
            ir_null.append(float(pair_correlation_full(t).get("repulsion_integral", 0.0)))
        m_null = np.array(m_null)
        ir_null = np.array(ir_null)
        z = (real_mass - m_null.mean()) / m_null.std() if m_null.std() > 0 else np.inf
        survives = real_mass > m_null.mean() + 3 * m_null.std()
        near_zero_band = bool((np.abs(ir_null).mean() < 0.02) or (ir_null < 0).any())
        rows.append({"bw_days": bw_days, "null_mass03_mean": float(m_null.mean()),
                     "null_mass03_sd": float(m_null.std()), "real_z": float(z),
                     "null_irep_mean": float(ir_null.mean()),
                     "null_irep_min": float(ir_null.min()),
                     "mass03_survives_3sigma": bool(survives),
                     "null_in_near_zero_band": near_zero_band})
        print(f"  {bw_days:>10d} {m_null.mean():>10.4f} ± {m_null.std():.4f}     "
              f"{z:>7.1f} {ir_null.mean():>+12.4f} "
              f"{'INTRINSIC' if survives else 'ENVELOPE-DRIVEN':>16s}")

    # the honest object is the survival-vs-bandwidth curve
    any_survive = any(r["mass03_survives_3sigma"] for r in rows)
    all_survive = all(r["mass03_survives_3sigma"] for r in rows)
    near_zero_any = any(r["null_in_near_zero_band"] for r in rows)
    out = {"observed_mass03": real_mass, "observed_irep_recon": real_irep,
           "homogeneous_poisson_ref": 0.259, "n_flares": int(onsets.size),
           "bandwidth_sweep": rows,
           "mass03_survives_all_bandwidths": all_survive,
           "mass03_survives_some_bandwidths": any_survive,
           "null_enters_near_zero_clip_band": near_zero_any,
           "verdict": ("INTRINSIC clustering beyond the solar cycle (survives the inhomogeneous "
                       "null at all bandwidths)" if all_survive else
                       "ENVELOPE-DRIVEN at some/all bandwidths — the flagged clustering is (partly) "
                       "the solar-cycle rate modulation, a Cox confound; report the curve" if not
                       all_survive else "mixed"),
           "note": "bandwidth-sensitive by construction; the survival-vs-bandwidth curve IS the "
                   "result, not any single point. Deployed-detector confirmation and SOC ground-"
                   "truth cross-check are the next step if the curve is ambiguous."}
    print(f"\n  survives ALL bandwidths: {all_survive};  some: {any_survive};  "
          f"null enters near-zero clip band: {near_zero_any}")
    print(f"  VERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(HERE, "solar_surrogate_port_measured.json"), "w"),
              indent=2, default=str)
    print("\n  (sealed prediction: envelope-driven / weaker-than-fungal survival — check vs above)")
    print("wrote solar_surrogate_port_measured.json")


if __name__ == "__main__":
    main()
