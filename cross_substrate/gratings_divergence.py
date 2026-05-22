"""
cross_substrate/gratings_divergence.py — gratings-divergence substrate study.

Tests whether D = I.5q − I.5 (q-banded minus matched plain-NNS KS-to-GUE) across
pvc-11 drifting-gratings units tracks F1/F0 (stimulus-locked rhythmicity), and
whether that survives controlling for firing rate (rate-regime lesson). See
gratings_divergence_brief.md.

Joins:
  coordinates/pvc-11.jsonl          → I.5, I.5q per (recording, unit_id)
  data/phase22a_results/h1_functional.parquet     → f1_f0_pref, osi, dsi, mean_rate
  data/phase22a_results/h1_classifications.parquet → ks_gue_per_q (per-q localization)

Out: gratings_divergence_results.json + figures/GRD_*.png
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
FIGDIR = os.path.join(_HERE, "figures")
TF_HZ = 6.25
GRATING_TRIAL_SEC = 1.0


def load_divergence():
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
                     "D": i5q - i5, "absD": abs(i5q - i5),
                     "n": r["extraction_audit"].get("n_events_used")})
    return pd.DataFrame(rows)


def partial_spearman(x, y, Z):
    """Spearman partial correlation of x,y controlling for one or more Z
    (rank-residual method). Z is an array or list of arrays."""
    Z = [Z] if (np.ndim(Z) == 1) else list(Z)
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    rZ = np.vstack([stats.rankdata(z) for z in Z] + [np.ones_like(rx)]).T
    def resid(a):
        coef, *_ = np.linalg.lstsq(rZ, a, rcond=None)
        return a - rZ @ coef
    r, p = stats.pearsonr(resid(rx), resid(ry))
    return float(r), float(p)


def main():
    div = load_divergence()
    fn = pd.read_parquet(os.path.join(_ROOT, "data/phase22a_results/h1_functional.parquet"))
    fn = fn[fn["subset"] == "gratings"][
        ["recording", "unit_id", "f1_f0_pref", "osi", "dsi", "mean_rate"]]
    df = div.merge(fn, on=["recording", "unit_id"], how="inner")
    df = df.dropna(subset=["f1_f0_pref"])
    print("=" * 76)
    print(f"GRATINGS-DIVERGENCE STUDY — {len(df)} gratings cells (TF={TF_HZ} Hz)")
    print("=" * 76)

    out = {"n_cells": int(len(df)), "TF_hz": TF_HZ}

    def corr(a, b, label):
        sr, sp = stats.spearmanr(df[a], df[b])
        pr, pp = stats.pearsonr(df[a], df[b])
        print(f"  {label:34s} Spearman ρ={sr:+.3f} (p={sp:.2e})  "
              f"Pearson r={pr:+.3f} (p={pp:.2e})")
        return {"spearman_rho": float(sr), "spearman_p": float(sp),
                "pearson_r": float(pr), "pearson_p": float(pp)}

    print("\n[G1] divergence vs F1/F0:")
    out["G1_absD_vs_f1f0"] = corr("absD", "f1_f0_pref", "|D| ~ F1/F0")
    out["G1_signedD_vs_f1f0"] = corr("D", "f1_f0_pref", "signed D ~ F1/F0")

    print("\n[G2] rate control (the load-bearing test):")
    out["G2_absD_vs_rate"] = corr("absD", "mean_rate", "|D| ~ mean_rate")
    out["G2_absD_vs_n"] = corr("absD", "n", "|D| ~ n_events")
    pr_rate, pp_rate = partial_spearman(
        df["absD"].values, df["f1_f0_pref"].values, df["mean_rate"].values)
    print(f"  {'|D|~F1/F0 | controlling rate':34s} partial ρ={pr_rate:+.3f} (p={pp_rate:.2e})")
    out["G2_partial_absD_f1f0_given_rate"] = {"rho": pr_rate, "p": pp_rate}

    print("\n[G3] tuning axes — OSI emerged as the strong predictor:")
    out["G3_absD_vs_osi"] = corr("absD", "osi", "|D| ~ OSI")
    out["G3_absD_vs_dsi"] = corr("absD", "dsi", "|D| ~ DSI")
    out["G3_signedD_vs_osi"] = corr("D", "osi", "signed D ~ OSI")
    out["G3_osi_vs_f1f0"] = corr("osi", "f1_f0_pref", "OSI ~ F1/F0 (are they distinct?)")

    print("\n[G3-control] is the OSI effect rate/n-confounded? (load-bearing)")
    pr_o_r, pp_o_r = partial_spearman(df["absD"].values, df["osi"].values, df["mean_rate"].values)
    pr_o_n, pp_o_n = partial_spearman(df["absD"].values, df["osi"].values, df["n"].values.astype(float))
    pr_o_rn, pp_o_rn = partial_spearman(
        df["absD"].values, df["osi"].values,
        [df["mean_rate"].values, df["n"].values.astype(float)])
    print(f"  |D|~OSI | rate        partial ρ={pr_o_r:+.3f} (p={pp_o_r:.2e})")
    print(f"  |D|~OSI | n           partial ρ={pr_o_n:+.3f} (p={pp_o_n:.2e})")
    print(f"  |D|~OSI | rate AND n  partial ρ={pr_o_rn:+.3f} (p={pp_o_rn:.2e})")
    out["G3_partial_absD_osi_given_rate"] = {"rho": pr_o_r, "p": pp_o_r}
    out["G3_partial_absD_osi_given_n"] = {"rho": pr_o_n, "p": pp_o_n}
    out["G3_partial_absD_osi_given_rate_and_n"] = {"rho": pr_o_rn, "p": pp_o_rn}

    print("\n[G3-leg] which leg carries OSI? (ties to H1: OSI↔ks_gue_med was q-banded)")
    out["leg_osi_vs_i5q"] = corr("osi", "i5q", "OSI ~ I.5q (q-banded)")
    out["leg_osi_vs_i5"] = corr("osi", "i5", "OSI ~ I.5  (object-a, matched)")

    print("\n[G3-value] is |D|~OSI just value-scaling? (control for the GUE-distance value)")
    out["absD_vs_i5"] = corr("absD", "i5", "|D| ~ I.5 (value-scaling check)")
    pr_o_v, pp_o_v = partial_spearman(df["absD"].values, df["osi"].values, df["i5"].values)
    pr_o_all, pp_o_all = partial_spearman(
        df["absD"].values, df["osi"].values,
        [df["i5"].values, df["mean_rate"].values, df["n"].values.astype(float)])
    print(f"  |D|~OSI | I.5              partial ρ={pr_o_v:+.3f} (p={pp_o_v:.2e})")
    print(f"  |D|~OSI | I.5+rate+n       partial ρ={pr_o_all:+.3f} (p={pp_o_all:.2e})")
    out["G3_partial_absD_osi_given_i5"] = {"rho": pr_o_v, "p": pp_o_v}
    out["G3_partial_absD_osi_given_i5_rate_n"] = {"rho": pr_o_all, "p": pp_o_all}

    # verdict (corrected: the substantive axis is OSI, not F1/F0)
    f1f0_supported = (out["G1_absD_vs_f1f0"]["spearman_p"] < 0.05
                      and out["G1_absD_vs_f1f0"]["spearman_rho"] > 0)
    osi_raw = out["G3_absD_vs_osi"]["spearman_p"] < 0.05 and out["G3_absD_vs_osi"]["spearman_rho"] > 0
    osi_robust = (pp_o_rn < 0.05 and pr_o_rn > 0
                  and pp_o_all < 0.05 and pr_o_all > 0)
    leg_specific = (abs(out["leg_osi_vs_i5q"]["spearman_rho"])
                    > 1.5 * abs(out["leg_osi_vs_i5"]["spearman_rho"]))
    out["f1f0_conjecture"] = "REFUTED" if not f1f0_supported else "supported"
    out["verdict"] = (
        "OSI_DIVERGENCE_CONFIRMED" if (osi_raw and osi_robust)
        else "OSI_RATE_CONFOUNDED" if (osi_raw and not osi_robust)
        else "NULL")
    out["leg_specificity"] = ("OSI_SIGNAL_Q_BANDED_SPECIFIC" if leg_specific
                              else "OSI_IN_BOTH_LEGS")
    print(f"\n  F1/F0 conjecture: {out['f1f0_conjecture']}")
    print(f"  VERDICT: {out['verdict']}   (OSI robust to rate+n: {osi_robust})")
    print(f"  leg specificity: {out['leg_specificity']}")

    # G4 per-q localization (exploratory)
    out["G4"] = per_q_localization(df)

    _figs(df, out)
    with open(os.path.join(_HERE, "gratings_divergence_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n→ wrote gratings_divergence_results.json + figures/GRD_*.png")


def per_q_localization(df):
    """Compare mean ks_gue_per_q profile of high-|D| vs low-|D| gratings cells.
    Exploratory; q↔frequency map is non-trivial (flagged)."""
    cls = pd.read_parquet(os.path.join(_ROOT, "data/phase22a_results/h1_classifications.parquet"))
    cls = cls[cls["subset"] == "gratings"][["recording", "unit_id", "ks_gue_per_q"]]
    m = df.merge(cls, on=["recording", "unit_id"], how="inner")
    if m.empty:
        return {"status": "no_join"}
    thr = m["absD"].quantile(0.9)
    hi = m[m["absD"] >= thr]
    lo = m[m["absD"] < m["absD"].median()]

    def meanprof(sub):
        arrs = [np.asarray(v, float) for v in sub["ks_gue_per_q"]
                if v is not None and len(v) == 30]
        return np.nanmean(np.vstack(arrs), axis=0) if arrs else None
    ph, pl = meanprof(hi), meanprof(lo)
    if ph is None or pl is None:
        return {"status": "insufficient"}
    delta = (ph - pl).tolist()
    peak_q = int(np.argmax(np.abs(ph - pl)) + 1)
    return {"status": "ok", "n_hi": int(len(hi)), "n_lo": int(len(lo)),
            "absD_threshold_p90": float(thr),
            "delta_ks_gue_per_q_hi_minus_lo": [round(x, 4) for x in delta],
            "peak_divergence_q": peak_q,
            "note": "q↔frequency map non-trivial; LOCALIZED if delta concentrates "
                    "at few q, DIFFUSE if spread. Exploratory, non-gating."}


def _figs(df, out):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    ax = axes[0]
    sc = ax.scatter(df["osi"], df["absD"], c=df["mean_rate"], s=30,
                    cmap="viridis", edgecolor="k", linewidth=0.3)
    ax.axhline(0.05, color="r", ls=":", lw=1)
    ax.set_xlabel("OSI (orientation selectivity)")
    ax.set_ylabel("|D| = |I.5q − I.5|")
    ax.set_title(f"|D| vs OSI  (ρ={out['G3_absD_vs_osi']['spearman_rho']:+.2f}, "
                 f"partial|rate+n+I.5 ρ={out['G3_partial_absD_osi_given_i5_rate_n']['rho']:+.2f})"
                 f"\nF1/F0 REFUTED (ρ={out['G1_absD_vs_f1f0']['spearman_rho']:+.2f})")
    fig.colorbar(sc, ax=ax, label="mean rate (sp/s)")
    ax.grid(alpha=0.2)

    ax = axes[1]
    ax.scatter(df["mean_rate"], df["absD"], s=30, color="#888", edgecolor="k", linewidth=0.3)
    ax.axhline(0.05, color="r", ls=":", lw=1)
    ax.set_xlabel("mean rate (sp/s)"); ax.set_ylabel("|D|")
    ax.set_title(f"rate control  (ρ={out['G2_absD_vs_rate']['spearman_rho']:+.2f})")
    ax.grid(alpha=0.2)

    ax = axes[2]
    g4 = out.get("G4", {})
    if g4.get("status") == "ok":
        d = g4["delta_ks_gue_per_q_hi_minus_lo"]
        ax.bar(range(1, len(d) + 1), d, color="#9467bd")
        ax.set_xlabel("q-band"); ax.set_ylabel("Δ ks_gue (high-|D| − low-|D|)")
        ax.set_title(f"per-q localization (peak q={g4.get('peak_divergence_q')})")
    else:
        ax.text(0.5, 0.5, "per-q n/a", ha="center")
    ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "GRD_divergence_vs_f1f0.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)


if __name__ == "__main__":
    main()
