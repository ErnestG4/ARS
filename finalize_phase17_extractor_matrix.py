"""
Finalise the Phase 17 σ̂ × extractor × architecture matrix:
  - load the parquet (4 archs × 7 extractors)
  - cleanly separate valid vs flagged/underpowered cells
  - compute per-extractor spread on valid cells only
  - render the heatmap with three families colour-coded
"""
from __future__ import annotations
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATA = "data"
PLOTS = "plots"

EXTRACTOR_PANEL = [
    ("residual_norm_peaks",                "find_peaks"),
    ("attention_entropy_peaks",            "find_peaks"),
    ("layer_kl_divergence_events",         "threshold_crossing"),
    ("attention_target_jumps",             "by_construction"),
    ("attention_sink_events",              "by_construction"),
    ("attention_argmax_sink",              "by_construction"),
    ("attention_multi_head_sink_consensus","by_construction"),
]


def main():
    df = pd.read_parquet(f"{DATA}/phase17_extractor_arch_sigma.parquet")
    arc = df[df["extractor_family"] != "synthetic_control"].copy()
    archs = ["Qwen2.5-3B", "Phi-3-mini-4k-instruct", "TinyLlama-1.1B-Chat",
             "Mistral-7B-v0.1"]
    extractors = [e for e, _ in EXTRACTOR_PANEL]
    families = {e: f for e, f in EXTRACTOR_PANEL}

    # Build matrix; mark flagged or NaN as masked.
    M_sigma = np.full((len(archs), len(extractors)), np.nan)
    M_n = np.zeros((len(archs), len(extractors)), dtype=int)
    M_rep = np.full((len(archs), len(extractors)), np.nan)
    M_flag = np.zeros((len(archs), len(extractors)), dtype=bool)
    for i, a in enumerate(archs):
        for k, e in enumerate(extractors):
            row = arc[(arc["arch"] == a) & (arc["extractor"] == e)]
            if len(row):
                r = row.iloc[0]
                if pd.notna(r["sigma_hat"]):
                    M_sigma[i, k] = float(r["sigma_hat"])
                    M_n[i, k] = int(r["n"])
                    M_rep[i, k] = float(r["rep_int_q_median"])
                    M_flag[i, k] = bool(r["flagged"])

    # Print full table
    print("=" * 110)
    print("σ̂ × extractor × architecture matrix")
    print("=" * 110)
    print(f"{'extractor':<40}  {'family':<22}  " +
          "  ".join(f"{a[:13]:<13}" for a in archs))
    for k, e in enumerate(extractors):
        row_strs = []
        for i in range(len(archs)):
            v = M_sigma[i, k]
            if np.isnan(v):
                row_strs.append("    --       ")
            elif M_flag[i, k]:
                row_strs.append(f" *{v:.3f}*({M_n[i,k]:>3}) ")
            else:
                row_strs.append(f"  {v:.3f}({M_n[i,k]:>3})  ")
        print(f"{e:<40}  {families[e]:<22}  " + " ".join(row_strs))
    print()
    print("  '*X*' = flagged (out-of-domain calibrator boundary)")
    print("  '--'  = underpowered (n_events < 50) or extraction failed")
    print()

    # Per-extractor spread on VALID cells only (non-flagged, non-NaN)
    print("=" * 110)
    print("Per-extractor σ̂ spread across architectures (valid cells only)")
    print("=" * 110)
    print(f"  {'extractor':<40}  {'family':<22}  {'n_valid':>7}  "
          f"{'spread':>10}  verdict")
    rows = []
    for k, e in enumerate(extractors):
        valid_idx = ~np.isnan(M_sigma[:, k]) & ~M_flag[:, k]
        n_valid = int(valid_idx.sum())
        if n_valid < 2:
            verdict = "insufficient_valid_cells"
            spread = np.nan
        else:
            vals = M_sigma[valid_idx, k]
            spread = float(vals.max() - vals.min())
            if spread <= 0.02:
                verdict = "saturated  (≤ 0.02)"
            elif spread <= 0.05:
                verdict = "intermediate"
            else:
                verdict = "discriminative (> 0.05)"
        spread_str = f"{spread:.4f}" if not np.isnan(spread) else "      —"
        print(f"  {e:<40}  {families[e]:<22}  {n_valid:>7}  "
              f"{spread_str:>10}  {verdict}")
        rows.append(dict(extractor=e, family=families[e], n_valid=n_valid,
                         spread=spread, verdict=verdict))

    # Family-level summary on valid cells
    print()
    print("=" * 110)
    print("Family-level σ̂ spread (valid cells only)")
    print("=" * 110)
    s = pd.DataFrame(rows).dropna(subset=["spread"])
    by = s.groupby("family")["spread"].agg(["mean", "max", "count"])
    print(by)

    # ─── Render heatmap ───────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(15, 5),
                             gridspec_kw={"width_ratios": [3, 1]})

    # Mask flagged cells in the heatmap by overlaying hatching
    M_disp = np.ma.array(M_sigma, mask=M_flag | np.isnan(M_sigma))
    ax = axes[0]
    im = ax.imshow(M_disp, aspect="auto", cmap="viridis",
                   vmin=0.0, vmax=0.20)
    # Draw flagged / nan cells with hatching
    for i in range(len(archs)):
        for k in range(len(extractors)):
            if np.isnan(M_sigma[i, k]):
                ax.add_patch(plt.Rectangle((k - 0.5, i - 0.5), 1, 1,
                             fill=True, color="#444"))
                ax.text(k, i, "—", ha="center", va="center",
                        fontsize=11, color="white")
            elif M_flag[i, k]:
                ax.add_patch(plt.Rectangle((k - 0.5, i - 0.5), 1, 1,
                             fill=False, hatch="///", edgecolor="black"))
                ax.text(k, i, f"*{M_sigma[i,k]:.3f}*\n n={M_n[i,k]}",
                        ha="center", va="center", fontsize=8, color="black")
            else:
                v = M_sigma[i, k]
                color = "white" if v < 0.10 else "black"
                ax.text(k, i, f"{v:.3f}\nn={M_n[i,k]}",
                        ha="center", va="center", fontsize=8, color=color)

    ax.set_xticks(range(len(extractors)))
    ax.set_xticklabels(extractors, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(archs)))
    ax.set_yticklabels(archs, fontsize=10)

    # Colour the x-tick labels by family
    fam_color = {"find_peaks": "#1f77b4",
                 "threshold_crossing": "#9467bd",
                 "by_construction": "#d62728"}
    for k, e in enumerate(extractors):
        ax.get_xticklabels()[k].set_color(fam_color[families[e]])

    ax.set_title("σ̂ per (architecture × extractor)\n"
                 "*X* hatched = flagged out-of-domain;  — = underpowered")
    fig.colorbar(im, ax=ax, label="σ̂  (calibrator-relative)")

    # Per-extractor spread on valid cells
    ax2 = axes[1]
    spreads = [r["spread"] for r in rows]
    spreads_plot = [s if not np.isnan(s) else 0 for s in spreads]
    colors = [fam_color[r["family"]] for r in rows]
    bars = ax2.barh(range(len(extractors)), spreads_plot, color=colors,
                    alpha=0.85)
    for i, r in enumerate(rows):
        if np.isnan(r["spread"]):
            bars[i].set_hatch("///")
            ax2.text(0.005, i, f"  insufficient", va="center", fontsize=7,
                     color="black")
    ax2.set_yticks(range(len(extractors)))
    ax2.set_yticklabels(extractors, fontsize=8)
    ax2.set_xlabel("σ̂ spread across archs (valid cells)")
    ax2.axvline(0.02, color="gray", ls=":", lw=1)
    ax2.axvline(0.05, color="gray", ls="-", lw=1)
    ax2.text(0.022, len(extractors) - 0.5, "0.02  saturated", fontsize=7,
             color="gray", rotation=90, va="bottom")
    ax2.text(0.055, len(extractors) - 0.5, "0.05  discriminative", fontsize=7,
             color="gray", rotation=90, va="bottom")
    handles = [Patch(facecolor=c, label=f) for f, c in fam_color.items()]
    ax2.legend(handles=handles, loc="lower right", fontsize=7)
    ax2.set_title("σ̂ spread per extractor")
    ax2.set_xlim(0, max(0.10, max(s for s in spreads if not np.isnan(s)) * 1.1))

    fig.tight_layout()
    out = f"{PLOTS}/49d_phase17_extractor_arch_heatmap.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"\n  → {out}")


if __name__ == "__main__":
    main()
