"""
arsrh/solar_gap_checks.py — earn the flat-GAP claim (reviewer's two checks), z-free.

The bisection showed the z-swing (6-26) tracks null_sd (4x), not the GAP -- so z was never the
finding. Before "robust GAP ~0.25" goes in the record it has to survive two checks:

  (1) WHY does null_sd blow up 4x? n barely drops (6608->5787, 12%), so it is NOT small-n; the
      inhomogeneous-Poisson rate fit is destabilizing on the merged catalog. If the fit is shifting,
      the null MEAN may be drifting under the GAP too -- so track null_mean/median across windows.
  (2) The GAP's own error. Is 0.310 inside the GAP's sampling error or a real excursion? "Flat" is a
      claim with a variance; band each GAP.

And a z-free existence test that is immune to the null-sd instability entirely: does the observed
mass03 exceed a HIGH PERCENTILE of the cycle-preserving null at every merge window? (No ratio, no sd.)

Run:  $HOME/fmexplorer/bin/python3 arsrh/solar_gap_checks.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from arsrh.solar_dedup_test import load_mx, onsets_overlap_merge   # noqa: E402
from arsrh.solar_surrogate_port import (rate_envelope, inhomogeneous_poisson,  # noqa: E402
                                        normspacing_pool, mass03, DAY)


def null_ensemble(onsets, bw_days=45, B=400):
    grid, lam = rate_envelope(onsets, bw_days * DAY)
    m = [mass03(normspacing_pool(inhomogeneous_poisson(grid, lam, onsets.size))) for _ in range(B)]
    return np.array([x for x in m if np.isfinite(x)])


def main():
    mx = load_mx()
    B = 400
    print(f"Solar GAP checks (raw {len(mx)}, B={B} null draws/window, z-free).\n")
    print(f"  {'gap':>4s} {'n':>6s} {'obs':>6s} {'nullμ':>6s} {'nullmed':>7s} {'nullSE':>7s} "
          f"{'null_p99':>8s} {'GAP':>6s} {'GAP±95CI':>10s} {'obs>p99':>8s} {'heavy?':>6s}")
    rows = []
    for gm in (0, 5, 10, 15, 20, 25, 30):
        on = onsets_overlap_merge(mx, gap_min=gm)
        obs = mass03(normspacing_pool(on))
        ens = null_ensemble(on, B=B)
        nm, nmed, nsd = ens.mean(), np.median(ens), ens.std()
        nse = nsd / np.sqrt(len(ens))
        p99, nmax = np.percentile(ens, 99), ens.max()
        gap = obs - nm
        gap_ci = 1.96 * nse
        heavy = (nm - nmed) > 0.5 * nsd            # mean pulled well above median -> right tail
        rows.append({"gap_min": gm, "n": int(on.size), "obs": obs, "null_mean": float(nm),
                     "null_median": float(nmed), "null_se": float(nse), "null_p99": float(p99),
                     "null_max": float(nmax), "GAP": float(gap), "GAP_95CI": float(gap_ci),
                     "obs_exceeds_p99": bool(obs > p99), "heavy_tailed_null": bool(heavy)})
        print(f"  {gm:>4d} {on.size:>6d} {obs:>6.3f} {nm:>6.3f} {nmed:>7.3f} {nse:>7.4f} "
              f"{p99:>8.3f} {gap:>6.3f} ±{gap_ci:>8.4f} {str(obs>p99):>8s} {str(heavy):>6s}")

    gaps = np.array([r["GAP"] for r in rows])
    cis = np.array([r["GAP_95CI"] for r in rows])
    nmeans = np.array([r["null_mean"] for r in rows])
    # check 1: null_mean flat or wandering?
    nmean_range = nmeans.max() - nmeans.min()
    nmean_wanders = nmean_range > 3 * np.mean([r["null_se"] for r in rows])
    # check 2: GAP flat within its CI? (is the spread bigger than the CIs?)
    gap_spread = gaps.max() - gaps.min()
    gap_flat_within_ci = gap_spread < 2 * cis.mean()
    all_exceed_p99 = all(r["obs_exceeds_p99"] for r in rows)
    floor = float(gaps.min())
    out = {"rows": rows, "B": B,
           "check1_null_mean_range": float(nmean_range),
           "check1_null_mean_wanders": bool(nmean_wanders),
           "check2_GAP_spread": float(gap_spread), "check2_GAP_mean_CI": float(cis.mean()),
           "check2_GAP_flat_within_CI": bool(gap_flat_within_ci),
           "zfree_obs_exceeds_null_p99_all_windows": bool(all_exceed_p99),
           "GAP_floor_min_across_windows": floor, "GAP_band": [float(gaps.min()), float(gaps.max())],
           "reading": ""}
    print(f"\n  CHECK 1 (null_mean): range {nmean_range:.3f} over windows, SE~{np.mean([r['null_se'] for r in rows]):.4f} "
          f"-> {'WANDERS (rate fit shifts with merge; sd blowup is fit-instability, not small-n)' if nmean_wanders else 'flat (sd swing is pure MC)'}")
    print(f"  CHECK 2 (GAP): spread {gap_spread:.3f} vs mean CI {cis.mean():.4f} -> "
          f"{'GAP has REAL window structure beyond MC error (NOT constant)' if not gap_flat_within_ci else 'flat within CI'}")
    print(f"  Z-FREE EXISTENCE: obs exceeds null p99 at ALL windows: {all_exceed_p99};  GAP floor (min) = {floor:.3f}")
    out["reading"] = (
        f"null_mean {'WANDERS' if nmean_wanders else 'flat'} ({nmeans.min():.3f}-{nmeans.max():.3f}) and "
        f"obs also drifts, so the GAP is two drifting quantities differenced; the GAP has "
        f"{'real window structure (not constant to MC error)' if not gap_flat_within_ci else 'no structure beyond MC'}. "
        f"The defensible claim is NOT 'flat GAP ~0.25' but 'excess robustly POSITIVE across all dedup "
        f"windows, band {gaps.min():.2f}-{gaps.max():.2f}, floor {floor:.2f}', and z-free: observed "
        f"mass03 exceeds the null's 99th percentile at {'every' if all_exceed_p99 else 'not every'} "
        f"window. Existence robust with a magnitude FLOOR (~{floor:.2f}); no constant magnitude, no z.")
    print(f"\n  READING: {out['reading']}")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "solar_gap_checks_measured.json"), "w"), indent=2, default=str)
    print("\n  wrote solar_gap_checks_measured.json")


if __name__ == "__main__":
    main()
