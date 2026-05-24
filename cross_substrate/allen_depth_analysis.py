"""
cross_substrate/allen_depth_analysis.py — cross-reference analyses on the Allen depth-extension.

Reads coordinates/allen-depth.jsonl (per (cell,stimulus) I.5q/I.5/W1δ + area + tuning) and runs the
four cross-reference hooks (descriptive, flag-don't-interpret):

  (1) H1 ACROSS AREAS — OSI ↔ ks_gue (q-banded I.5q AND matched I.5), per visual area, on the
      drifting-gratings condition. Does H1 (pvc-11 monkey + Allen V1) generalize to LM/RL/AL/PM/AM?
  (2) TUNING-DIM PRIVILEGE — is OSI special, or do DSI / pref_sf / pref_tf / f1_f0 each couple to
      ks_gue? (partial correlations vs mean rate / n).
  (3) FAMILY VII at scale — |I.5q − I.5| vs OSI per area; does the pvc-11-specific OSI-grading stay
      absent in mouse at 12× the Phase-2a sample?
  (4) CROSS-AREA LANDSCAPE — per-area median fingerprint (I.5q, W1δ); do V1/LM/RL/AL/PM/AM cluster
      as "visual cortex" or separate? + within-cell stimulus-state spread (does class shift with stimulus?).

Out: prints tables; writes figures/P_allen_depth.png.
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
AREAS = ["VISp", "VISl", "VISrl", "VISal", "VISpm", "VISam", "LGd"]
NAME = {"VISp": "V1", "VISl": "LM", "VISrl": "RL", "VISal": "AL", "VISpm": "PM",
        "VISam": "AM", "LGd": "LGN"}
TUNING = ["g_osi_dg", "g_dsi_dg", "pref_sf_sg", "pref_tf_dg", "f1_f0_dg", "run_mod_dg"]


def load():
    rows = []
    for line in open(os.path.join(COORD, "allen-depth.jsonl")):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)        # robust to a partial last line while the run appends
        except json.JSONDecodeError:
            continue
        a = r["axes_computed"]
        d = {"session": r["session"], "unit": r["unit_id"], "area": r["area"],
             "stim": r["stimulus"], "n": r["n"],
             "i5q": a["I.5q_ks_gue_med"], "i5": a["I.5_ks_gue"], "w1": a["I.1_w1_clock"]}
        d.update(r.get("tuning", {}))
        rows.append(d)
    return pd.DataFrame(rows)


def _spearman(df, x, y):
    d = df[[x, y]].dropna()
    if len(d) < 30:
        return None, None, len(d)
    rho, p = stats.spearmanr(d[x], d[y])
    return rho, p, len(d)


def h1_across_areas(df):
    print("\n(1) H1 — OSI ↔ ks_gue per area (drifting gratings):")
    print(f"  {'area':5s} {'n':>5s} {'ρ(OSI,I.5q)':>12s} {'p':>8s} {'ρ(OSI,I.5)':>11s} {'p':>8s}")
    dg = df[df["stim"] == "drifting_gratings"]
    for a in AREAS:
        sub = dg[dg["area"] == a]
        rq, pq, nq = _spearman(sub, "g_osi_dg", "i5q")
        ri, pi, ni = _spearman(sub, "g_osi_dg", "i5")
        if rq is None:
            print(f"  {NAME[a]:5s} {len(sub):>5d}  (n<30)")
            continue
        print(f"  {NAME[a]:5s} {nq:>5d} {rq:>12.3f} {pq:>8.1e} {ri:>11.3f} {pi:>8.1e}")


def tuning_privilege(df):
    print("\n(2) Tuning-dim privilege — ρ(tuning, I.5q) pooled over V1+higher visual (drifting gratings):")
    dg = df[(df["stim"] == "drifting_gratings") & (df["area"].isin(AREAS[:6]))]
    for t in TUNING:
        rho, p, n = _spearman(dg, t, "i5q")
        tag = "  <- H1 (OSI)" if t == "g_osi_dg" else ""
        if rho is not None:
            print(f"  {t:12s} ρ={rho:+.3f} p={p:.1e} (n={n}){tag}")


def family_vii(df):
    print("\n(3) Family VII — |I.5q − I.5| vs OSI per area (drifting gratings; pvc-11 had ρ≈0.47, mouse absent):")
    dg = df[df["stim"] == "drifting_gratings"].copy()
    dg["absD"] = (dg["i5q"] - dg["i5"]).abs()
    for a in AREAS:
        sub = dg[dg["area"] == a]
        rho, p, n = _spearman(sub, "g_osi_dg", "absD")
        if rho is not None:
            print(f"  {NAME[a]:5s} ρ(OSI,|D|)={rho:+.3f} p={p:.1e} (n={n})")


def cross_area(df):
    print("\n(4) Cross-area landscape — per-area median fingerprint (drifting gratings):")
    dg = df[df["stim"] == "drifting_gratings"]
    print(f"  {'area':5s} {'n':>5s} {'med I.5q':>9s} {'med I.5':>8s} {'med W1δ':>8s}")
    for a in AREAS:
        sub = dg[dg["area"] == a]
        if len(sub) < 10:
            continue
        print(f"  {NAME[a]:5s} {len(sub):>5d} {sub['i5q'].median():>9.3f} "
              f"{sub['i5'].median():>8.3f} {sub['w1'].median():>8.3f}")
    print("\n  within-cell stimulus-state: median I.5q per stimulus (pooled areas):")
    for s, sub in df.groupby("stim"):
        v = sub["i5q"].dropna()
        if len(v) > 30:
            print(f"    {s:22s} med I.5q={v.median():.3f} (n={len(v)})")
    # per-cell spread across stimuli (does class shift with stimulus within a cell?)
    piv = df.pivot_table(index=["session", "unit"], columns="stim", values="i5q", aggfunc="first")
    spread = (piv.max(axis=1) - piv.min(axis=1)).dropna()
    print(f"\n  within-cell I.5q spread across stimuli: median={spread.median():.3f} "
          f"p90={spread.quantile(0.9):.3f} (n_cells={len(spread)}) "
          f"— large ⇒ universality class is stimulus-state-dependent within a fixed cell")


def figure(df):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dg = df[df["stim"] == "drifting_gratings"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    # cross-area medians in I.5q × W1δ
    for a in AREAS:
        sub = dg[dg["area"] == a]
        if len(sub) < 10:
            continue
        x, y = sub["i5q"].dropna(), sub["w1"].dropna()
        ax[0].scatter([x.median()], [y.median()], s=140, edgecolor="k", zorder=5,
                      label=f"{NAME[a]} (n={len(sub)})")
        ax[0].scatter(x.sample(min(200, len(x))), sub.loc[x.index, "w1"].sample(min(200, len(x))),
                      s=5, alpha=0.08)
    ax[0].set_xlabel("I.5q (q-banded ks-GUE)"); ax[0].set_ylabel("W1δ")
    ax[0].set_title("Allen cross-area fingerprint (drifting gratings)")
    ax[0].legend(fontsize=7); ax[0].grid(alpha=0.2)
    # H1 per area: OSI vs I.5q clouds
    for a in ["VISp", "VISam"]:
        sub = dg[dg["area"] == a][["g_osi_dg", "i5q"]].dropna()
        ax[1].scatter(sub["g_osi_dg"], sub["i5q"], s=7, alpha=0.3, label=NAME[a])
    ax[1].set_xlabel("OSI (g_osi_dg)"); ax[1].set_ylabel("I.5q")
    ax[1].set_title("H1: OSI ↔ ks_gue (V1 vs AM)")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P_allen_depth.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("\nwrote", os.path.relpath(p, _HERE))


def main():
    df = load()
    print(f"ALLEN DEPTH ANALYSIS — {len(df)} (cell,stimulus) records, "
          f"{df.groupby(['session','unit']).ngroups} cells, {df['area'].nunique()} areas")
    h1_across_areas(df)
    tuning_privilege(df)
    family_vii(df)
    cross_area(df)
    figure(df)


if __name__ == "__main__":
    main()
