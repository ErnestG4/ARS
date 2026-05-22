"""
cross_substrate/allen_osi_gap.py — Allen V1 OSI-gap check (scoped-2b).

Tests whether the OSI-graded q-banded↔plain-NNS divergence found in pvc-11
(monkey, anesthetised) recurs in Allen Neuropixels V1 (mouse, awake). If it
does at similar ρ → the finding generalises across cortical V1; if absent/
different → it differentiates state/species.

Self-contained in the main venv: reads cached Allen .nwb directly via h5py
(allensdk's EcephysSession loader version-mismatches these legacy files;
h5py reads the HDF5 regardless). Per-unit OSI is banked
(h1_allen_comparison.parquet, 111 V1 units characterised on drifting gratings).

Per unit: extract drifting-gratings spike train → I.5q (ars_classify q-banded
ks_gue_med) and I.5 (plain unfolded-NNS ks-to-GUE). D = I.5q − I.5. Correlate
|D| with OSI (rate/n-controlled), and the leg decomposition OSI↔I.5q vs OSI↔I.5
(the H1 leg-robustness replication in mouse).

Out: allen_osi_gap_results.json + figures/ALLEN_osi_gap.png
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
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify, unfold_unit_mean        # noqa: E402
from cross_substrate.axes import canonical_spacings, I5_ks_gue, I1_w1_clock  # noqa: E402
from universality import nns_cdf_gue                         # noqa: E402

NWB_GLOB = "/home/combust/fmexplorer/allen_cache/session_*/session_*.nwb"
OSI_PARQUET = os.path.join(_ROOT, "data/phase24_results/h1_allen_comparison.parquet")
FIGDIR = os.path.join(_HERE, "figures")


def gratings_train(h, unit_row, starts, stops):
    """Concatenate a unit's spikes within drifting-gratings presentations,
    gap-removed (contiguous) — matched to the pvc-11 gratings concatenation."""
    sti = h["units/spike_times_index"]
    lo = 0 if unit_row == 0 else int(sti[unit_row - 1])
    hi = int(sti[unit_row])
    spk = h["units/spike_times"][lo:hi]          # per-unit spikes, sorted ascending
    order = np.argsort(starts)
    chunks, off = [], 0.0
    for k in order:
        s0, s1 = starts[k], stops[k]
        i0 = np.searchsorted(spk, s0, "left")    # O(log n) — spk is sorted
        i1 = np.searchsorted(spk, s1, "left")
        chunks.append(spk[i0:i1] - s0 + off)
        off += (s1 - s0)
    return np.sort(np.concatenate(chunks)) if chunks else np.zeros(0)


def collect(limit_sessions=None):
    osi = pd.read_parquet(OSI_PARQUET).set_index("unit_id")
    targets = set(osi.index)
    rows = []
    files = sorted(glob.glob(NWB_GLOB))
    if limit_sessions:
        files = files[:limit_sessions]
    for f in files:
        sess = f.split("/")[-1].replace(".nwb", "")
        with h5py.File(f, "r") as h:
            ids = h["units/id"][:]
            present = [(r, int(u)) for r, u in enumerate(ids) if int(u) in targets]
            if not present:
                continue
            g = h["intervals/drifting_gratings_presentations"]
            starts, stops = g["start_time"][:], g["stop_time"][:]
            for r, u in present:
                train = gratings_train(h, r, starts, stops)
                if train.size < 50:
                    rows.append({"session": sess, "unit_id": u, "n": int(train.size),
                                 "i5q": None, "i5": None, "skip": "few_spikes"})
                    continue
                cl = classify(train)                 # q-banded ks_gue_med
                i5q = cl.get("ks_gue_med")
                pos = unfold_unit_mean(train)
                s = canonical_spacings(pos)
                i5 = I5_ks_gue(s)
                w1 = I1_w1_clock(s)
                rows.append({"session": sess, "unit_id": u, "n": int(train.size),
                             "i5q": None if i5q is None or not np.isfinite(i5q) else float(i5q),
                             "i5": i5, "w1": w1,
                             "osi": float(osi.loc[u, "osi"]),
                             "mean_rate": float(osi.loc[u, "mean_rate"])})
        print(f"  {sess}: {len(present)} target units", flush=True)
    return pd.DataFrame(rows)


def partial(df, x, y, Zcols):
    rx, ry = stats.rankdata(df[x]), stats.rankdata(df[y])
    rZ = np.column_stack([stats.rankdata(df[z]) for z in Zcols] + [np.ones(len(df))])
    res = lambda v: v - rZ @ np.linalg.lstsq(rZ, v, rcond=None)[0]
    return stats.pearsonr(res(rx), res(ry))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-sessions", type=int, default=None)
    a = ap.parse_args()
    print("=" * 72)
    print("ALLEN V1 OSI-GAP CHECK (mouse awake) vs pvc-11 (monkey anesthetised)")
    print("=" * 72)
    df = collect(a.limit_sessions)
    full = df.dropna(subset=["i5", "i5q", "osi"]).copy()
    full["D"] = full["i5q"] - full["i5"]
    full["absD"] = full["D"].abs()
    print(f"\n  units with both legs + OSI: {len(full)} "
          f"(skipped few-spikes: {int((df['i5'].isna()).sum())})")
    out = {"n_units": int(len(full)),
           "n_sessions": int(full["session"].nunique())}

    def c(x, y):
        sr, sp = stats.spearmanr(full[x], full[y])
        return {"rho": float(sr), "p": float(sp)}

    out["absD_vs_osi"] = c("absD", "osi")
    out["signedD_vs_osi"] = c("D", "osi")
    pr_rn, pp_rn = partial(full, "absD", "osi", ["mean_rate", "n"])
    pr_all, pp_all = partial(full, "absD", "osi", ["i5", "mean_rate", "n"])
    out["partial_absD_osi_rate_n"] = {"rho": float(pr_rn), "p": float(pp_rn)}
    out["partial_absD_osi_i5_rate_n"] = {"rho": float(pr_all), "p": float(pp_all)}
    out["leg_osi_vs_i5q"] = c("osi", "i5q")
    out["leg_osi_vs_i5"] = c("osi", "i5")

    print(f"\n  |D| ~ OSI            ρ={out['absD_vs_osi']['rho']:+.3f} (p={out['absD_vs_osi']['p']:.1e})")
    print(f"  |D| ~ OSI | rate,n   ρ={pr_rn:+.3f} (p={pp_rn:.1e})")
    print(f"  |D| ~ OSI | i5,rate,n ρ={pr_all:+.3f} (p={pp_all:.1e})")
    print(f"  OSI ~ I.5q (q-banded) ρ={out['leg_osi_vs_i5q']['rho']:+.3f} (p={out['leg_osi_vs_i5q']['p']:.1e})")
    print(f"  OSI ~ I.5  (plain)    ρ={out['leg_osi_vs_i5']['rho']:+.3f} (p={out['leg_osi_vs_i5']['p']:.1e})")

    osi_gap = (out["absD_vs_osi"]["p"] < 0.05 and out["absD_vs_osi"]["rho"] > 0
               and pp_all < 0.05 and pr_all > 0)
    h1_both = (out["leg_osi_vs_i5q"]["p"] < 0.05 and out["leg_osi_vs_i5"]["p"] < 0.05)
    out["verdict_osi_gap"] = "RECURS_IN_MOUSE_V1" if osi_gap else "ABSENT_OR_DIFFERENT"
    out["verdict_h1_leg_robust_mouse"] = "YES" if h1_both else "NO"
    print(f"\n  OSI-gap verdict: {out['verdict_osi_gap']}")
    print(f"  H1 leg-robust in mouse: {out['verdict_h1_leg_robust_mouse']}")

    _fig(full, out)
    full.to_parquet(os.path.join(_HERE, "allen_osi_gap_cells.parquet"))
    with open(os.path.join(_HERE, "allen_osi_gap_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n→ wrote allen_osi_gap_results.json + cells.parquet + figure")


def _fig(full, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.8))
    a1.scatter(full["osi"], full["absD"], c=full["mean_rate"], cmap="viridis",
               s=36, edgecolor="k", linewidth=0.3)
    a1.set_xlabel("OSI (mouse V1)"); a1.set_ylabel("|D| = |I.5q − I.5|")
    a1.set_title(f"Allen |D| vs OSI  ρ={out['absD_vs_osi']['rho']:+.2f} "
                 f"(partial {out['partial_absD_osi_i5_rate_n']['rho']:+.2f})")
    a1.grid(alpha=0.2)
    a2.scatter(full["osi"], full["i5q"], s=30, label=f"I.5q ρ={out['leg_osi_vs_i5q']['rho']:+.2f}",
               color="#1f77b4", edgecolor="k", linewidth=0.3)
    a2.scatter(full["osi"], full["i5"], s=30, label=f"I.5 ρ={out['leg_osi_vs_i5']['rho']:+.2f}",
               color="#ff7f0e", edgecolor="k", linewidth=0.3)
    a2.set_xlabel("OSI"); a2.set_ylabel("KS-to-GUE"); a2.legend(fontsize=8)
    a2.set_title("H1 leg-robustness in mouse (both legs vs OSI)"); a2.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "ALLEN_osi_gap.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
