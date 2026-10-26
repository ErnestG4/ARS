"""RQ1 read, descriptive figure (seal §5, B1 dropped / D(β) reported): D(β) = R_ℤ[√2] − R_ℤ[i] at matched N with ±2·SE_diff,
one panel per X, with the heuristic's offsets (L = log X and L = log N) from results/HEURISTIC_B_MIRROR.json (round 91:
the one heuristic file) overlaid. Gated cells (β 0.40, 0.45) are filled; the rest are open. No verdict here.

  python rq1_plot_read.py results/read/read1.json results/read/D_beta.png
"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA, HX, HN = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, SURF = "#1f1f1e", "#6b6a64", "#e4e3df", "#fcfcfb"


def main(read_json, out_png):
    r = json.load(open(read_json))
    h = json.load(open("results/HEURISTIC_B_MIRROR.json"))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True, facecolor=SURF)
    for ax, (X, XL, title) in zip(axes, (("10000000000", "1e10", "X = 10¹⁰"), ("100000000000", "1e11", "X = 10¹¹"))):
        rows = r["rows"][X]["rows"]
        hr = {x["beta"]: x["heuristic"] for x in h["rows"][XL]["rows"]}
        b = [x["beta"] for x in rows]
        ax.set_facecolor(SURF)
        ax.axhline(0, color=MUTED, lw=1)
        ax.plot(b, [hr[v]["logX"]["offset"] for v in b], color=HX, lw=2, label="heuristic, L = log X")
        ax.plot(b, [hr[v]["logN"]["offset"] for v in b], color=HN, lw=2, ls="--", label="heuristic, L = log N")
        for x in rows:
            g = x["B2_gated"]
            ax.errorbar(x["beta"], x["D"], yerr=2 * x["SE_diff"], fmt="o", ms=8, color=DATA, mfc=DATA if g else SURF,
                        mew=2, elinewidth=1.5, capsize=0, zorder=3)
        ax.plot([], [], "o", ms=8, color=DATA, mfc=DATA, mew=2, label="data D, gated cell (±2 SE)")
        ax.plot([], [], "o", ms=8, color=DATA, mfc=SURF, mew=2, label="data D, not gated (±2 SE)")
        ax.set_title(f"{title}   (N = {r['rows'][X]['N']:,})", color=INK, fontsize=11, loc="left")
        ax.set_xlabel("β   (K = N^β windows)", color=INK)
        ax.grid(axis="y", color=GRID, lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(MUTED)
        ax.tick_params(colors=MUTED)
    axes[0].set_ylabel("D(β) = R_ℤ[√2] − R_ℤ[i]", color=INK)
    axes[1].legend(frameon=False, fontsize=9, labelcolor=INK, loc="upper right")
    fig.suptitle(f"RQ1 sealed read: B2 {r['B2']} (T = {r['B2_T']:.2f}, t = {r['rule']['t']:.2f}); D(β) descriptive",
                 color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150, facecolor=SURF)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
