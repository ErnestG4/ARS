"""
cross_substrate/allen_fam2_analysis.py — Family II (long-range) cross-reference on Allen depth.

Merges allen-depth-fam2.jsonl (Σ²/Δ₃/K) with allen-depth.jsonl (I.5q + tuning) by cell_id and asks:
  • Does long-range rigidity (Σ², Δ₃) couple to tuning (OSI) — the phase-coupling hook — or is it
    orthogonal to the Family-I H1 axis?
  • Is Family II redundant with Family I (I.5q) or a distinct axis? ρ(Σ², I.5q).
  • Per-area / per-stimulus Family II structure.
Flag-don't-interpret. Run: --run.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
AREAS = ["VISp", "VISl", "VISrl", "VISal", "VISpm", "VISam", "LGd"]
NAME = {"VISp": "V1", "VISl": "LM", "VISrl": "RL", "VISal": "AL", "VISpm": "PM", "VISam": "AM", "LGd": "LGN"}
F2KEYS = ["II.1_sigma2_L", "II.2_delta3_L", "II.3_K_tau1"]


def _load(path, keys, extra=None):
    rows = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        a = r["axes_computed"]
        d = {"cell_id": r["cell_id"]}
        for k in keys:
            d[k] = a.get(k)
        if extra:
            for k in extra:
                d[k] = r.get(k) if k in r else (r.get("tuning", {}) or {}).get(k)
        rows.append(d)
    return pd.DataFrame(rows)


def _sp(df, x, y):
    d = df[[x, y]].dropna()
    if len(d) < 30:
        return None, None, len(d)
    rho, p = stats.spearmanr(d[x], d[y])
    return rho, p, len(d)


def run():
    f2 = _load(os.path.join(COORD, "allen-depth-fam2.jsonl"), F2KEYS)
    d1 = _load(os.path.join(COORD, "allen-depth.jsonl"),
               ["I.5q_ks_gue_med"], extra=["area", "stimulus", "g_osi_dg", "g_dsi_dg"])
    df = f2.merge(d1, on="cell_id")
    dg = df[df["stimulus"] == "drifting_gratings"]
    print(f"ALLEN FAMILY-II CROSS-REF — {len(df)} merged records, {len(dg)} drifting-gratings\n")

    print("(a) Long-range rigidity ↔ tuning (phase-coupling hook) + ↔ Family I, drifting gratings:")
    for k in F2KEYS:
        ro, po, _ = _sp(dg, "g_osi_dg", k)
        rd, pd_, _ = _sp(dg, "g_dsi_dg", k)
        ri, pi, n = _sp(dg, "I.5q_ks_gue_med", k)
        print(f"  {k:15s} ρ(OSI)={_f(ro)} ρ(DSI)={_f(rd)} ρ(I.5q)={_f(ri)}  (n={n})")
    print("  (ρ(OSI)~H1-on-long-range; ρ(I.5q) high ⇒ Family II redundant with Family I, low ⇒ distinct axis)")

    print("\n(b) Per-area median Σ²/Δ₃ (drifting gratings):")
    print(f"  {'area':5s} {'n':>5s} {'med Σ²':>8s} {'med Δ₃':>8s} {'med K':>8s}")
    for a in AREAS:
        sub = dg[dg["area"] == a]
        if len(sub) < 20:
            continue
        print(f"  {NAME[a]:5s} {len(sub):>5d} {_m(sub,'II.1_sigma2_L'):>8s} "
              f"{_m(sub,'II.2_delta3_L'):>8s} {_m(sub,'II.3_K_tau1'):>8s}")

    print("\n(c) Per-stimulus median Σ² (within-cell state on the long-range axis):")
    for s, sub in df.groupby("stimulus"):
        v = sub["II.1_sigma2_L"].dropna()
        if len(v) > 30:
            print(f"  {s:22s} med Σ²={v.median():.3f} (n={len(v)})")


def _f(v):
    return f"{v:+.3f}" if isinstance(v, (int, float)) else "  -  "


def _m(df, k):
    v = df[k].dropna()
    return f"{v.median():.3f}" if len(v) else "  -"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.run:
        run()
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
