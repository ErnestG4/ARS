"""RQ1 POST-HOC collapse figure (round 92; descriptive, no verdict): per X, (top) D(β) with ±2 SE against the conductor-
shift prediction R_ℤ[i](aK) − R_ℤ[i](K) and its first-order form R′_ℤ[i]·log a / log N; (bottom) the collapse
residual R_ℤ[√2](K) − R_ℤ[i](aK) in units of its model SE. Gated B2 cells (β 0.40, 0.45) shaded.

  python rq1_plot_collapse.py results/collapse/COLLAPSE.json results/collapse/collapse.png
"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA, SHIFT, FIRST = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, SURF, BAND = "#1f1f1e", "#6b6a64", "#e4e3df", "#fcfcfb", "#efeeea"


def main(path, out):
    c = json.load(open(path))
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharex=True, facecolor=SURF, gridspec_kw=dict(height_ratios=[3, 2]))
    for j, (X, title) in enumerate((("10000000000", "X = 10¹⁰"), ("100000000000", "X = 10¹¹"))):
        rows = c["rows"][X]["rows"]
        b = [x["beta"] for x in rows]
        top, bot = axes[0][j], axes[1][j]
        for ax in (top, bot):
            ax.set_facecolor(SURF)
            ax.axvspan(0.395, 0.455, color=BAND, zorder=0)
            ax.grid(axis="y", color=GRID, lw=0.8)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color(MUTED)
            ax.tick_params(colors=MUTED)
        top.axhline(0, color=MUTED, lw=1)
        top.fill_between(b, [x["D"] - 2 * x["SE_D"] for x in rows], [x["D"] + 2 * x["SE_D"] for x in rows],
                         color=DATA, alpha=0.15, lw=0)
        top.plot(b, [x["D"] for x in rows], color=DATA, lw=2, label="data D(β) = R_ℤ[√2](K) − R_ℤ[i](K), ±2 SE")
        top.plot(b, [x["D_pred_shift"] for x in rows], color=SHIFT, lw=2, label="shift: R_ℤ[i](aK) − R_ℤ[i](K)")
        top.plot(b, [x["D_pred_first_order"] for x in rows], color=FIRST, lw=2, ls="--",
                 label="first order: R′_ℤ[i]·log a / log N")
        top.set_title(f"{title}   (post hoc)", color=INK, fontsize=11, loc="left")
        bot.axhline(0, color=MUTED, lw=1)
        for y in (-2, 2):
            bot.axhline(y, color=MUTED, lw=0.8, ls=":")
        bot.plot(b, [x["residual_over_SE"] for x in rows], "o-", color=DATA, lw=2, ms=4)
        bot.set_xlabel("β   (K = N^β)", color=INK)
    axes[0][0].set_ylabel("D(β)", color=INK)
    axes[1][0].set_ylabel("[R_ℤ[√2](K) − R_ℤ[i](aK)] / SE", color=INK)
    axes[0][1].legend(frameon=False, fontsize=8.5, labelcolor=INK, loc="upper left")
    fig.suptitle(f"RQ1 post-hoc conductor-scaling collapse, a = {c['a']:.4f} (shaded: the gated B2 cells)", color=INK,
                 fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, facecolor=SURF)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
