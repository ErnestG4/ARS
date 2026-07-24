"""
arsrh/solar_dedup_test.py — the FALSIFYING test for solar's intrinsic-residual claim.

The reviewer's sharp point: solar's sealed prediction failed because the surviving signal lives at
timescales SHORTER than the solar-cycle envelope reaches (burst timescale). Short-timescale residual
is exactly and only where sub-flare catalog double-counting lives. The cycle-preserving null cannot
distinguish "intrinsic burst clustering" from "catalog over-segmentation" -- it preserves the
years-timescale envelope and has no burst structure either way. So the dedup is NOT confirmatory; it
is the falsifying test for the intrinsic half. Recon already showed 44% of short-ISI M+X pairs
OVERLAP in [tstart,tend] and 34% share a multipleID -- a large unexcluded artifact.

Test: rebuild the onset list de-duplicated two ways (the catalog's own multipleID grouping; and an
overlap/gap merge), recompute the DEPLOYED mass03 and the cycle-preserving-null z, and see whether
the clustering survives or collapses.

  survives dedup  -> intrinsic residual is real (confirmed)
  collapses/halves -> the residual was (largely) catalog over-segmentation (the intrinsic HALF falls;
                      survival-over-cycle at raw resolution still stands as a statement about the
                      catalog as given)

Run:  $HOME/fmexplorer/bin/python3 arsrh/solar_dedup_test.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from arsrh.solar_surrogate_port import (rate_envelope, inhomogeneous_poisson,  # noqa: E402
                                        normspacing_pool, mass03, DAY)

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260724)


def load_mx():
    df = pd.read_csv(os.path.join(_ROOT, "data", "solar_flares_plutino_1986_2023.csv"),
                     low_memory=False)
    for c in ("tstart", "tend"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df = df.dropna(subset=["tstart"]).sort_values("tstart").reset_index(drop=True)
    return df[df["cat"].isin(["M", "X"])].sort_values("tstart").reset_index(drop=True)


def onsets_raw(mx):
    t0 = mx["tstart"].iloc[0]
    return np.sort((mx["tstart"] - t0).dt.total_seconds().to_numpy())


def onsets_multipleid(mx):
    """Catalog's own sub-flare grouping: one onset (earliest tstart) per multipleID."""
    g = mx.groupby("multipleID")["tstart"].min().sort_values()
    t0 = g.iloc[0]
    return np.sort((g - t0).dt.total_seconds().to_numpy())


def onsets_overlap_merge(mx, gap_min=0.0):
    """Merge events whose [tstart,tend] overlap (or are within gap_min minutes): one onset each."""
    ts = mx["tstart"].astype("int64").to_numpy() // 10**9
    te = mx["tend"].fillna(mx["tstart"]).astype("int64").to_numpy() // 10**9
    order = np.argsort(ts)
    ts, te = ts[order], te[order]
    merged, cur_start, cur_end = [], ts[0], te[0]
    for i in range(1, len(ts)):
        if ts[i] <= cur_end + gap_min * 60:
            cur_end = max(cur_end, te[i])            # same physical event, extend
        else:
            merged.append(cur_start)
            cur_start, cur_end = ts[i], te[i]
    merged.append(cur_start)
    a = np.array(merged, float)
    return np.sort(a - a[0])


def deployed_mass03(onsets):
    return mass03(normspacing_pool(onsets)), normspacing_pool(onsets).size


def cycle_null_z(onsets, observed_mass, bw_days=45, B=120):
    grid, lam = rate_envelope(onsets, bw_days * DAY)
    m = []
    for _ in range(B):
        ev = inhomogeneous_poisson(grid, lam, onsets.size)
        if ev.size < 100:
            continue
        m.append(mass03(normspacing_pool(ev)))
    m = np.array(m)
    z = (observed_mass - m.mean()) / m.std() if m.std() > 0 else np.inf
    return float(z), float(m.mean()), float(m.std())


def main():
    mx = load_mx()
    variants = {
        "raw": onsets_raw(mx),
        "dedup_multipleID": onsets_multipleid(mx),
        "dedup_overlap_merge": onsets_overlap_merge(mx, gap_min=0.0),
        "dedup_overlap+30min_gap": onsets_overlap_merge(mx, gap_min=30.0),
    }
    print(f"Solar M+X dedup falsifying test. Raw M+X events: {len(mx)}\n")
    print(f"  {'variant':>26s} {'n events':>9s} {'mass03':>8s} {'cycle-null mass03':>18s} {'z':>7s}")
    rows = []
    for name, on in variants.items():
        obs, n_pool = deployed_mass03(on)
        z, nm, ns = cycle_null_z(on, obs)
        rows.append({"variant": name, "n_events": int(on.size), "pool_n": int(n_pool),
                     "observed_mass03": obs, "cycle_null_mass03": nm, "cycle_null_sd": ns, "z": z})
        print(f"  {name:>26s} {on.size:>9d} {obs:>8.3f} {nm:>10.3f} ± {ns:.3f}    {z:>7.1f}")

    raw_z = rows[0]["z"]
    dd_z = rows[1]["z"]                                   # multipleID dedup = the catalog's own call
    collapse = dd_z < 0.5 * raw_z or dd_z < 3
    out = {"raw_M+X": len(mx), "variants": rows,
           "raw_z": raw_z, "multipleID_dedup_z": dd_z,
           "intrinsic_residual_survives_dedup": bool(not collapse),
           "verdict": ("INTRINSIC RESIDUAL SURVIVES dedup — the clustering beyond the cycle is real, "
                       "not catalog over-segmentation" if not collapse else
                       "INTRINSIC RESIDUAL (LARGELY) COLLAPSES under dedup — the short-timescale "
                       "signal the cycle-null could not exclude was substantially catalog "
                       "over-segmentation (shared multipleID / overlapping [tstart,tend]). "
                       "'survives-the-cycle' stands for the catalog as-given; "
                       "'survives-because-intrinsic' does NOT survive de-duplication."),
           "reviewer_point": "confirmed: the falsifying test resolves the identical quantity the "
                             "cycle-null and the over-segmentation mechanism were competing for."}
    print(f"\n  raw z={raw_z:.1f} -> multipleID-dedup z={dd_z:.1f}")
    print(f"  VERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(HERE, "solar_dedup_test_measured.json"), "w"),
              indent=2, default=str)
    print("\n  wrote solar_dedup_test_measured.json")


if __name__ == "__main__":
    main()
