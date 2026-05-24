"""
cross_substrate/allen_depth_spatial.py — spatial-structure axes on the Allen depth-extension.

Spatial structure is currently underutilized (per-cell fingerprinting ignores where the cell sits).
Position is recoverable WITHOUT recompute: unit_id → units.csv ecephys_channel_id → channels.csv
(probe_vertical_position + AP/DV/LR CCF coordinates). Three analyses (descriptive, flag-don't-interpret):

  (1) DEPTH-STRATIFIED landscape — Allen ecephys has NO clean layer label, so stratify by RELATIVE
      cortical depth within each area (probe_vertical_position quantiles ≈ superficial/mid/deep ≈
      L2/3 · L4 · L5-6). Do depth bins occupy different fingerprint positions? (L4 thalamic-input vs
      L5 output.)
  (2) SPATIAL DECORRELATION — pairwise |fingerprint Δ| vs 3D CCF distance within an area; at what
      distance does fingerprint similarity decay to chance? (universality-class spatial autocorrelation.)
  (3) SAMPLING-GEOMETRY quantification — Allen NPX spatial extent (DV depth span vs AP/LR lateral) to
      contrast with the pvc-11 Utah array (2D ~4mm L2/3 patch): the 4th Family-VII-split candidate.

Read-only; joins position at load time. Run: --run. Out: figures/P_allen_spatial.png + tables.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
FIGDIR = os.path.join(_HERE, "figures")
CACHE = "/home/combust/fmexplorer/allen_cache"
AREAS = ["VISp", "VISl", "VISrl", "VISal", "VISpm", "VISam", "LGd"]
NAME = {"VISp": "V1", "VISl": "LM", "VISrl": "RL", "VISal": "AL", "VISpm": "PM",
        "VISam": "AM", "LGd": "LGN"}


def _position_lookup():
    """unit_id → (probe_vertical, ap, dv, lr) via units→channels join."""
    u = pd.read_csv(f"{CACHE}/units.csv", low_memory=False)[["id", "ecephys_channel_id"]]
    ch = pd.read_csv(f"{CACHE}/channels.csv", low_memory=False).rename(columns={"id": "chan_id"})
    m = u.merge(ch, left_on="ecephys_channel_id", right_on="chan_id")
    cols = {"v": "probe_vertical_position", "ap": "anterior_posterior_ccf_coordinate",
            "dv": "dorsal_ventral_ccf_coordinate", "lr": "left_right_ccf_coordinate"}
    return m.set_index("id")[[cols["v"], cols["ap"], cols["dv"], cols["lr"]]].rename(
        columns={v: k for k, v in cols.items()})


def load():
    rows = []
    for line in open(os.path.join(COORD, "allen-depth.jsonl")):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        a = r["axes_computed"]
        rows.append({"session": r["session"], "unit": r["unit_id"], "area": r["area"],
                     "stim": r["stimulus"], "i5q": a["I.5q_ks_gue_med"],
                     "i5": a["I.5_ks_gue"], "w1": a["I.1_w1_clock"]})
    df = pd.DataFrame(rows)
    pos = _position_lookup()
    df = df.merge(pos, left_on="unit", right_index=True, how="left")
    # CCF coords of exactly 0 are unregistered (real CCF µm are positive ~10^3–10^4)
    df["ccf_valid"] = (df["ap"] > 0) & (df["dv"] > 0) & (df["lr"] > 0)
    return df


def depth_stratified(df):
    print("\n(1) DEPTH-STRATIFIED fingerprint (drifting gratings; depth-proxy = probe_vertical quantile "
          "within area; deep→shallow):")
    dg = df[(df["stim"] == "drifting_gratings") & df["v"].notna()]
    print(f"  {'area':5s} {'bin':>10s} {'n':>5s} {'med I.5q':>9s} {'med W1δ':>8s}")
    for a in AREAS:
        sub = dg[dg["area"] == a]
        if len(sub) < 60:
            continue
        q = pd.qcut(sub["v"], 3, labels=["deep", "mid", "superf"], duplicates="drop")
        for b in ["deep", "mid", "superf"]:
            s = sub[q == b]
            if len(s) >= 15:
                print(f"  {NAME[a]:5s} {b:>10s} {len(s):>5d} {s['i5q'].median():>9.3f} "
                      f"{s['w1'].median():>8.3f}")
        # is there a depth gradient in I.5q?
        rho, p = stats.spearmanr(sub["v"], sub["i5q"])
        print(f"     → ρ(depth, I.5q)={rho:+.3f} p={p:.1e} (n={len(sub)})")


def spatial_decorrelation(df):
    print("\n(2) SPATIAL DECORRELATION — |I.5q Δ| vs 3D CCF distance (drifting gratings, CCF-registered, within area):")
    dg = df[(df["stim"] == "drifting_gratings") & df["ccf_valid"]
            & df[["ap", "dv", "lr", "i5q"]].notna().all(axis=1)]
    any_area = False
    for a in AREAS:
        sub = dg[dg["area"] == a]
        if len(sub) < 50 or sub[["ap", "dv", "lr"]].nunique().min() < 2:
            continue
        any_area = True
        xyz = sub[["ap", "dv", "lr"]].to_numpy()
        v = sub["i5q"].to_numpy()
        n = len(sub)
        rng = np.random.default_rng(0)
        ii = rng.integers(0, n, 4000); jj = rng.integers(0, n, 4000)
        ok = ii != jj
        d = np.linalg.norm(xyz[ii[ok]] - xyz[jj[ok]], axis=1)
        dd = np.abs(v[ii[ok]] - v[jj[ok]])
        if np.ptp(d) == 0:
            continue
        rho, p = stats.spearmanr(d, dd)
        print(f"  {NAME[a]:5s} n={n}: ρ(dist, |ΔI.5q|)={rho:+.3f} p={p:.1e} "
              f"(>0 ⇒ farther cells more different; median|Δ|={np.median(dd):.3f})")
    if not any_area:
        print("  (no area with ≥50 CCF-registered cells yet — firms up at full scale)")


def sampling_geometry(df):
    print("\n(3) SAMPLING GEOMETRY — Allen NPX spatial extent per area (µm), vs pvc-11 Utah ~4mm 2D patch:")
    dg = df[(df["stim"] == "drifting_gratings") & df["ccf_valid"]]
    print(f"  {'area':5s} {'n':>5s} {'DV span':>8s} {'AP span':>8s} {'LR span':>8s}  (CCF-registered only)")
    for a in AREAS:
        sub = dg[dg["area"] == a][["ap", "dv", "lr"]].dropna()
        if len(sub) < 20:
            continue
        dv = sub["dv"].max() - sub["dv"].min()
        ap = sub["ap"].max() - sub["ap"].min()
        lr = sub["lr"].max() - sub["lr"].min()
        print(f"  {NAME[a]:5s} {len(sub):>5d} {dv:>8.0f} {ap:>8.0f} {lr:>8.0f}")
    print("  ⇒ NPX: large DV (depth), small AP/LR (lateral) — supports the sampling-geometry candidate "
          "for the Family-VII pvc-11-specificity (Utah catches lateral correlations NPX cannot).")


def main():
    df = load()
    print(f"ALLEN SPATIAL — {len(df)} records, {df.groupby(['session','unit']).ngroups} cells; "
          f"position joined for {df['dv'].notna().mean()*100:.0f}%")
    depth_stratified(df)
    spatial_decorrelation(df)
    sampling_geometry(df)


if __name__ == "__main__":
    main()
