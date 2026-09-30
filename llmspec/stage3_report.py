"""Stage 3 report: trajectory plots (layer-mean per matrix type vs training step) + event table.
Reads results/stage3_long{TAG}.parquet, stage3_null{TAG}.json, stage3_changepoints{TAG}.json. Writes plots/stage3_*.png and
results/stage3_event_table{TAG}.json. Descriptive only: every verdict lives in stage3_analyze's outputs.
Style (dataviz skill): fixed categorical order, one y-axis per panel, legend for >= 2 series, thin marks,
recessive grid; step 0 sits at the left edge of a symlog axis; the induction-formation interval is shaded.
"""
import json, os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
import mcfg
TAG = mcfg.suffix() + os.environ.get("STAGE3_TAG", "")
MNAME = mcfg.name()
TYPES = ["Q", "K", "V", "O", "MLP_IN", "MLP_OUT"]
COL = dict(zip(TYPES, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]))
INK, MUTED, GRID = "#1f1f1f", "#6b6b66", "#e4e3dc"


def style(ax, title, ylabel):
    ax.set_xscale("symlog", linthresh=1)
    ax.set_title(title, fontsize=9, color=INK, loc="left")
    ax.set_ylabel(ylabel, fontsize=8, color=MUTED)
    ax.tick_params(labelsize=7, colors=MUTED)
    ax.grid(True, color=GRID, lw=0.6)
    for s in ax.spines.values():
        s.set_color(GRID)


def events(ax, ev):
    if ev.get("induction"):
        a, b = ev["induction"]
        ax.axvspan(a, b, color="#9e9e98", alpha=0.18, lw=0)


def main():
    df = pd.read_parquet(ROOT / "results" / f"stage3_long{TAG}.parquet")
    out = ROOT / "plots"; out.mkdir(exist_ok=True)
    mk = df[(df.matrix == "MODEL")].pivot_table(index="step", columns="metric", values="value").sort_index()
    # induction formation interval: last step with max induction < 0.3 -> first step with >= 0.3
    ind = mk["induction_max"]
    ev = {}
    above = ind[ind >= 0.3]
    if len(above):
        first = above.index.min(); prev = ind[ind.index < first].index.max()
        ev["induction"] = [int(prev), int(first)]
    sk = mk["sink_frac"]
    if (sk > 0).any():
        first = sk[sk > 0].index.min(); prev = sk[sk.index < first].index.max()
        ev["first_sink_head"] = [int(prev), int(first)]
    ev["loss_text"] = {int(k): float(v) for k, v in mk["loss_text"].items()}

    def panel(ax, metric, band="all", title=None, ylabel="", matrices=TYPES, agg="mean"):
        d = df[(df.metric == metric) & (df.band == band) & (df.matrix.isin(matrices))]
        for M in matrices:
            g = d[d.matrix == M].groupby("step").value
            g = g.mean() if agg == "mean" else g.median()
            if len(g):
                ax.plot(g.index, g.values, lw=1.5, color=COL.get(M, INK), label=M, marker="o", ms=2.5)
        events(ax, ev); style(ax, title or metric, ylabel)

    figs = [
        ("global", [("stable_rank", "all", "stable rank (layer mean)"), ("spectral_entropy", "all", "spectral entropy"),
                    ("liu_rankslope", "all", "rank-slope (liu_rankslope_v1; NOT an MLE alpha)"),
                    ("mp2_n_upper_outliers", "all", "upper outliers vs MP edge (mp_fit_v2)"),
                    ("mp2_n_lower_departures", "all", "lower-edge departures (mp_fit_v2; rectangular only)"),
                    ("mp2_lower10_ks", "all", "lowest-10% KS vs MP (square; mp_fit_v2 scale)")]),
        ("local", [("rt", "bulk", "bulk <r~> (full matrices)"), ("q_kde", "bulk", "bulk Brody q (kde4)"),
                   ("rt", "lower", "lower-band <r~> (PRECISION_LIMITED for K, V, MLP_IN per G4)"),
                   ("rt", "upper", "upper-band <r~>"), ("sigma2_L10", "bulk", "bulk Sigma^2(10) (kde32; reported)"),
                   ("delta3_L10", "bulk", "bulk Delta_3(10) (reported)")]),
        ("vectors", [("ipr_u_x_dim_median", "upper", "IPR x dim, left vectors, upper band"),
                     ("ipr_u_x_dim_median", "bulk", "IPR x dim, left vectors, bulk"),
                     ("pt_ks_u_median", "upper", "Porter-Thomas KS, upper band"),
                     ("pt_ks_u_median", "bulk", "Porter-Thomas KS, bulk"),
                     ("U_overlap_final", "top8", "top-8 left subspace overlap with step 143000"),
                     ("U_overlap_prev", "top8", "top-8 left subspace overlap with previous revision")]),
        ("motion", [("dW_fro_rel", "all", "||dW|| / ||W||"), ("dW_stable_rank", "all", "stable rank of dW"),
                    ("dW_frac_top32", "all", "fraction of ||dW||^2 in W's top-32 left subspace")]),
    ]
    for name, specs in figs:
        n = len(specs); cols = 3; rows = int(np.ceil(n / cols))
        fig, axs = plt.subplots(rows, cols, figsize=(12, 3.1 * rows), squeeze=False)
        for ax, (met, band, title) in zip(axs.flat, specs):
            panel(ax, met, band, title)
        for ax in list(axs.flat)[n:]:
            ax.axis("off")
        h, l = axs.flat[0].get_legend_handles_labels()
        fig.legend(h, l, loc="upper right", fontsize=8, frameon=False, ncol=6)
        fig.suptitle(f"{MNAME} {name} metrics vs training step (grey band: induction formation)", fontsize=10, x=0.01, ha="left", color=INK)
        fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(out / f"stage3_{name}{TAG}.png", dpi=120); plt.close(fig)
    # per-head types, markers, circuits
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.2))
    for ax, (met, title) in zip(axs[0], [("loss_text", "text-probe loss"), ("loss_rep2", "repeated-sequence 2nd-half loss"),
                                         ("induction_max", "max induction attention")]):
        ax.plot(mk.index, mk[met], lw=1.5, color=INK, marker="o", ms=2.5); events(ax, ev); style(ax, title, "")
    ax = axs[1, 0]; ax.plot(mk.index, mk["sink_mean_all"], lw=1.5, color=INK, marker="o", ms=2.5); events(ax, ev); style(ax, "mean attention to position 0", "")
    for ax, (met, M, title) in zip(axs[1, 1:], [("copy_score_elhage", "OV", "copying score (median head)"),
                                                ("qk_sym_nr", "QK", "QK symmetric-energy fraction, non-rotary (median head)")]):
        d = df[(df.metric == met) & (df.matrix == M)].groupby("step").value
        ax.plot(d.median().index, d.median().values, lw=1.5, color=INK, marker="o", ms=2.5, label="median")
        ax.fill_between(d.quantile(.1).index, d.quantile(.1).values, d.quantile(.9).values, color="#9e9e98", alpha=0.25, lw=0, label="10-90%")
        events(ax, ev); style(ax, title, "")
    fig.suptitle(f"{MNAME} markers and circuits", fontsize=10, x=0.01, ha="left", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(out / f"stage3_markers_circuits{TAG}.png", dpi=120); plt.close(fig)
    cps = json.loads((ROOT / "results" / f"stage3_changepoints{TAG}.json").read_text())
    table = {"events": ev, "changepoints": {k: v for k, v in cps.items() if v}}
    (ROOT / "results" / f"stage3_event_table{TAG}.json").write_text(json.dumps(table, indent=1))
    print("events:", {k: v for k, v in ev.items() if k != "loss_text"}, "| series with change points:", len(table["changepoints"]))


if __name__ == "__main__":
    main()
