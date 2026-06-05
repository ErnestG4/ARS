"""
cross_substrate/longrange_allen_psth_audit.py — re-run the Allen V1 GUE-pole audit +
H1 self-test AFTER the trial-PSTH (external-rate) unfold, which removes the stimulus-
locked rate (orientation tuning + within-trial F1). Decoy-battery-validated first
(trial_psth_unfold.decoy_battery → no false-RIGID).

Decisive questions vs the pre-unfold (smooth-poly) run (all SUPER_POISSON, GUE pole
marginal-only): (a) does the clustering COLLAPSE once stimulus rate is removed (it was
stimulus-driven) or SURVIVE (intrinsic)? (b) does a genuine GUE pole emerge (any cell
RIGID)? (c) does the high-OSI clustering survive (intrinsic to selective cells) or
collapse (it was the tuning rate-steps)?
"""
from __future__ import annotations

import glob
import json
import os
import sys
import numpy as np
import pandas as pd
import h5py
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import longrange_discriminator as LD
from trial_psth_unfold import psth_unfold

NWB_GLOB = os.path.expanduser("~/fmexplorer/allen_cache/session_*/session_*.nwb")
OSI_PARQUET = os.path.join(_ROOT, "data/phase24_results/h1_allen_comparison.parquet")
L = 50.0
REF_N = 1500
N_SEEDS = 12


def unit_presentations(h, row, starts, stops, conds):
    sti = h["units/spike_times_index"]
    lo = 0 if row == 0 else int(sti[row - 1])
    hi = int(sti[row])
    spk = h["units/spike_times"][lo:hi]
    pres, total = [], 0
    for k in np.argsort(starts):
        i0 = np.searchsorted(spk, starts[k], "left")
        i1 = np.searchsorted(spk, stops[k], "left")
        rel = spk[i0:i1] - starts[k]
        total += rel.size
        pres.append((conds[k], float(stops[k] - starts[k]), rel))
    return pres, total


def main():
    osi = pd.read_parquet(OSI_PARQUET).set_index("unit_id")
    targets = set(osi.index)
    rows = []
    for f in sorted(glob.glob(NWB_GLOB)):
        sess = f.split("/")[-1].replace(".nwb", "")
        with h5py.File(f, "r") as h:
            ids = h["units/id"][:]
            present = [(r, int(u)) for r, u in enumerate(ids) if int(u) in targets]
            if not present:
                continue
            g = h["intervals/drifting_gratings_presentations"]
            starts, stops = g["start_time"][:], g["stop_time"][:]
            ori, tf = g["orientation"][:], g["temporal_frequency"][:]
            conds = [(float(o) if np.isfinite(o) else -1.0,
                      float(t) if np.isfinite(t) else 2.0) for o, t in zip(ori, tf)]
            for r, u in present:
                pres, total = unit_presentations(h, r, starts, stops, conds)
                if total < LD.MIN_N_LONGRANGE:
                    continue
                u_unf = psth_unfold(pres)        # stimulus rate removed (external)
                if u_unf.size < LD.MIN_N_LONGRANGE:
                    continue
                v = LD.longrange_verdict(u_unf, L=L, n_seeds=N_SEEDS,
                                         unfold_deg=None, ref_n=REF_N)
                rows.append({"unit_id": u, "n": int(total),
                             "osi": float(osi.loc[u, "osi"]),
                             "longrange_psth": v["verdict"],
                             "sigma2_psth": v["sigma2"]["obs"]})
        print(f"  {sess}: {len(present)} units", flush=True)
    df = pd.DataFrame(rows)

    # join the pre-unfold (smooth-poly) verdicts for the same cells
    pre_path = os.path.join(_HERE, "longrange_allen_cells.parquet")
    if os.path.exists(pre_path):
        pre = pd.read_parquet(pre_path)[["unit_id", "ks_gue", "longrange", "sigma2"]]
        df = df.merge(pre.rename(columns={"longrange": "longrange_poly",
                                          "sigma2": "sigma2_poly"}), on="unit_id", how="left")

    from collections import Counter
    print(f"\n{len(df)} V1 units, trial-PSTH-unfolded (stimulus rate removed).")
    print(f"  long-range mix AFTER PSTH unfold: {dict(Counter(df.longrange_psth))}")
    if "longrange_poly" in df:
        print(f"  (pre, smooth-poly):              {dict(Counter(df.longrange_poly.dropna()))}")
        # transition: where did SUPER_POISSON cells go after stimulus removal?
        sup = df[df.longrange_poly == "SUPER_POISSON"]
        print(f"  of {len(sup)} pre-SUPER_POISSON cells → after PSTH: {dict(Counter(sup.longrange_psth))}")
        med_pre = float(np.nanmedian(df.sigma2_poly)); med_post = float(np.nanmedian(df.sigma2_psth))
        print(f"  median σ²: poly {med_pre:.1f} → PSTH {med_post:.1f}")

    n_rigid = int((df.longrange_psth == "RIGID_GUE").sum())
    n_pois = int((df.longrange_psth == "POISSON_INDEP").sum())
    n_sup = int((df.longrange_psth == "SUPER_POISSON").sum())
    print(f"\n  GENUINE GUE pole emerged? RIGID_GUE cells after PSTH: {n_rigid}/{len(df)}")
    print(f"  POISSON_INDEP: {n_pois}  | SUPER_POISSON (intrinsic clustering): {n_sup}")

    # H1: does high-OSI clustering survive stimulus removal?
    rho, p = stats.spearmanr(df.osi, df.sigma2_psth)
    hi = df[df.osi >= df.osi.quantile(0.66)]
    print(f"\n  H1 after PSTH: Spearman(OSI, σ²_psth) = {rho:+.3f} (p={p:.1e})")
    print(f"  high-OSI tertile (n={len(hi)}) post-PSTH: {dict(Counter(hi.longrange_psth))}")
    hi_sup = int((hi.longrange_psth == "SUPER_POISSON").sum())
    verdict = ("high-OSI clustering SURVIVES stimulus removal (intrinsic)" if hi_sup > len(hi) / 2
               else "high-OSI clustering COLLAPSES after stimulus removal (was stimulus-driven)")
    print(f"  → {verdict}")

    df.to_parquet(os.path.join(_HERE, "longrange_allen_psth_cells.parquet"))
    out = {"n": len(df), "rigid": n_rigid, "poisson_indep": n_pois, "super": n_sup,
           "osi_sigma2_rho_psth": float(rho), "high_osi_super_frac": hi_sup / max(len(hi), 1),
           "h1_verdict": verdict}
    with open(os.path.join(_HERE, "longrange_allen_psth_results.json"), "w") as fo:
        json.dump(out, fo, indent=2)
    print("\nBound: trial-PSTH = EXTERNAL rate (LOO cross-trial condition mean), decoy-"
          "battery-validated (no false-RIGID). Removes stimulus-locked rate; residual "
          "Σ² is structure BEYOND the stimulus. Allen V1 gratings, awake mouse.")


if __name__ == "__main__":
    main()
