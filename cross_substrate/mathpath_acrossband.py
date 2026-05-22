"""
cross_substrate/mathpath_acrossband.py — empirical opener for the math-path.

Will's sharpened math-path conjecture: the OSI-graded inter-leg gap D=I.5q−I.5
arises because the ACROSS-q-BAND ks_gue distribution is skewed in orientation-tuned
cells (a few bands GUE-like, most Poisson-leaning), so the MEDIAN over bands (I.5q)
diverges from what the pooled/plain-NNS distribution (I.5) gives. The derivable
question: what across-band-uniformity assumption does orientation tuning violate?

This script tests the conjecture EMPIRICALLY before any derivation: for each gratings
cell, summarize its banked ks_gue_per_q distribution (dispersion, skew, median−mean)
and ask whether those summaries track OSI and |D|. If yes → the skew mechanism is the
right derivation target; if no → redirect the math-path.

Uses banked ks_gue_per_q (no recompute).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


def load():
    rows = []
    for l in open(os.path.join(_HERE, "coordinates", "pvc-11.jsonl")):
        r = json.loads(l)
        if r["meta"]["subset"] != "gratings":
            continue
        a = r["axes_computed"]
        i5, i5q = a.get("I.5_ks_gue"), a.get("I.5q_ks_gue_med")
        if not (isinstance(i5, float) and isinstance(i5q, float)):
            continue
        rec, uid, _ = r["cell_id"].split("/")
        rows.append({"recording": rec, "unit_id": uid, "i5": i5, "i5q": i5q,
                     "absD": abs(i5q - i5)})
    div = pd.DataFrame(rows)
    fn = pd.read_parquet(os.path.join(_ROOT, "data/phase22a_results/h1_functional.parquet"))
    fn = fn[fn["subset"] == "gratings"][["recording", "unit_id", "osi", "mean_rate"]]
    cls = pd.read_parquet(os.path.join(_ROOT, "data/phase22a_results/h1_classifications.parquet"))
    cls = cls[cls["subset"] == "gratings"][["recording", "unit_id", "ks_gue_per_q"]]
    df = div.merge(fn, on=["recording", "unit_id"]).merge(cls, on=["recording", "unit_id"])
    return df.dropna(subset=["osi"])


def band_stats(v):
    """Across-band summaries of a ks_gue_per_q vector (well-powered bands only:
    drop NaN / nonpositive placeholders)."""
    a = np.asarray(v, float)
    a = a[np.isfinite(a)]
    if a.size < 5:
        return None
    return {"std": float(np.std(a)), "skew": float(stats.skew(a)),
            "med_minus_mean": float(np.median(a) - np.mean(a)),
            "iqr": float(np.percentile(a, 75) - np.percentile(a, 25)),
            "frac_below_0p3": float(np.mean(a < 0.3))}  # GUE-like fraction proxy


def main():
    df = load()
    bs = df["ks_gue_per_q"].apply(band_stats)
    keep = bs.notna()
    df = df[keep].reset_index(drop=True)
    B = pd.DataFrame(list(bs[keep]))
    df = pd.concat([df.reset_index(drop=True), B], axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    print("=" * 74)
    print(f"MATH-PATH OPENER — across-band ks_gue structure vs OSI / |D|  (n={len(df)})")
    print("=" * 74)
    print("Conjecture: tuned cells have skewed/dispersed across-band ks_gue,")
    print("so median-over-bands (I.5q) diverges from pooled (I.5).\n")

    def c(a, b):
        sr, sp = stats.spearmanr(df[a], df[b])
        return sr, sp

    out = {"n": int(len(df)), "correlations": {}}
    print(f"  {'across-band stat':18s} {'~ OSI (ρ,p)':>26s} {'~ |D| (ρ,p)':>26s}")
    for stat in ["std", "skew", "med_minus_mean", "iqr", "frac_below_0p3"]:
        ro, po = c(stat, "osi")
        rd, pd_ = c(stat, "absD")
        out["correlations"][stat] = {"vs_osi": [float(ro), float(po)],
                                     "vs_absD": [float(rd), float(pd_)]}
        print(f"  {stat:18s} {f'{ro:+.3f} (p={po:.1e})':>26s} "
              f"{f'{rd:+.3f} (p={pd_:.1e})':>26s}")

    # does the skew/dispersion mediate? partial |D|~OSI controlling for std+skew
    def pr(x, y, Z):  # Z is a list of control column names
        rx, ry = stats.rankdata(df[x]), stats.rankdata(df[y])
        rZ = np.vstack([stats.rankdata(df[z]) for z in Z] + [np.ones(len(df))]).T
        res = lambda v: v - rZ @ np.linalg.lstsq(rZ, v, rcond=None)[0]
        return stats.pearsonr(res(rx), res(ry))
    r_full, p_full = stats.spearmanr(df["absD"], df["osi"])
    r_med, p_med = pr("absD", "osi", ["std", "skew"])
    print(f"\n  |D|~OSI raw           ρ={r_full:+.3f} (p={p_full:.1e})")
    print(f"  |D|~OSI | std,skew    ρ={r_med:+.3f} (p={p_med:.1e})")
    out["mediation"] = {"absD_osi_raw": [float(r_full), float(p_full)],
                        "absD_osi_given_bandstats": [float(r_med), float(p_med)]}
    drop = (abs(r_med) < 0.6 * abs(r_full))
    out["verdict"] = ("ACROSS_BAND_SKEW_MEDIATES_OSI_GAP" if drop
                      else "SKEW_PRESENT_BUT_NOT_FULL_MEDIATOR")
    print(f"\n  VERDICT: {out['verdict']}")
    print("  (if mediates: math-path should target the across-band-uniformity")
    print("   assumption that orientation tuning violates.)")
    with open(os.path.join(_HERE, "mathpath_acrossband_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n→ wrote mathpath_acrossband_results.json")


if __name__ == "__main__":
    main()
