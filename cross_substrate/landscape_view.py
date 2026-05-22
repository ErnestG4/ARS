"""
cross_substrate/landscape_view.py — exploratory landscape projections.

Charting, NOT hypothesis-testing (landscape.md §6 anti-hypothesis discipline):
present multiple projections; do not pick a "winning" viewpoint or interpret
clusters. Reads coordinates/*.jsonl, prints summary tables, and writes figures
to cross_substrate/figures/.

Projections:
  P1 (universal, all 10 substrates): I.5q (q-banded ks-to-GUE) × ARS.rep_med.
     The only axes every substrate shares. Pulsar is direct-leg (flagged).
  P2 (matched, 7 substrates): Brody q × Berry-Robnik ρ — Poisson corner (0,0)
     ↔ GUE/Wigner corner (1,1). Object-(a), matched to AM.
  P3 (1D lingua-franca): I.5q strip across all substrates, sorted.
"""
from __future__ import annotations

import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
FIGDIR = os.path.join(_HERE, "figures")
os.makedirs(FIGDIR, exist_ok=True)


def load_all():
    out = {}
    for f in sorted(glob.glob(os.path.join(COORD, "*.jsonl"))):
        sub = os.path.basename(f)[:-6]
        out[sub] = [json.loads(l) for l in open(f)]
    return out


def col(recs, key):
    return np.array([r["axes_computed"].get(key) for r in recs
                     if isinstance(r["axes_computed"].get(key), (int, float))], float)


def msummary(v):
    if v.size == 0:
        return None
    return dict(n=v.size, med=float(np.median(v)),
                p25=float(np.percentile(v, 25)), p75=float(np.percentile(v, 75)))


# ── colours / markers ────────────────────────────────────────────────────────
COLORS = {
    "pvc-11": "#1f77b4", "allen-np": "#17becf", "kuramoto": "#2ca02c",
    "pulsar-nanograv": "#7f7f7f", "L-zeros": "#d62728", "mertens": "#9467bd",
    "liouville": "#8c564b", "maass-gamma0": "#e377c2",
    "gaussian-primes": "#ff7f0e", "eisenstein-primes": "#bcbd22",
}
MATCHED = ["pvc-11", "L-zeros", "mertens", "liouville", "maass-gamma0",
           "gaussian-primes", "eisenstein-primes"]


def text_tables(data):
    print("=" * 78)
    print("LANDSCAPE VIEW — descriptive projections (no interpretation)")
    print("=" * 78)
    print("\n[universal axes — all substrates] median [p25,p75] (n)")
    print(f"  {'substrate':18s} {'I.5q (ks-GUE)':>20s} {'ARS.rep_med':>20s}")
    rows = []
    for sub, recs in data.items():
        a, b = msummary(col(recs, "I.5q_ks_gue_med")), msummary(col(recs, "ARS.rep_med"))
        rows.append((sub, a, b))
    for sub, a, b in sorted(rows, key=lambda r: (r[1]["med"] if r[1] else 9)):
        fa = f"{a['med']:.3f} [{a['p25']:.2f},{a['p75']:.2f}] ({a['n']})" if a else "-"
        fb = f"{b['med']:.3f} [{b['p25']:.2f},{b['p75']:.2f}]" if b else "-"
        flag = "  (direct-leg)" if sub == "pulsar-nanograv" else ""
        print(f"  {sub:18s} {fa:>20s} {fb:>20s}{flag}")

    print("\n[matched object-(a) — 7 substrates] median (n)")
    print(f"  {'substrate':18s} {'W1δ':>8s} {'Brody q':>8s} {'BR ρ':>8s} "
          f"{'ks_GUE':>8s} {'ks_Poiss':>9s}")
    for sub in MATCHED:
        recs = data[sub]
        def m(k):
            s = msummary(col(recs, k))
            return f"{s['med']:.3f}" if s else "-"
        print(f"  {sub:18s} {m('I.1_w1_clock'):>8s} {m('I.8_brody_q'):>8s} "
              f"{m('I.9_berry_robnik_rho'):>8s} {m('I.5_ks_gue'):>8s} "
              f"{m('I.7_ks_poisson'):>9s}")


def fig_universal(data):
    fig, ax = plt.subplots(figsize=(9, 6.5))
    for sub, recs in data.items():
        x = col(recs, "I.5q_ks_gue_med")
        y = col(recs, "ARS.rep_med")
        n = min(x.size, y.size)
        if n == 0:
            continue
        x, y = x[:n], y[:n]
        c = COLORS.get(sub, "#333")
        if n > 50:                      # cloud + centroid for populous substrates
            idx = np.random.default_rng(0).choice(n, size=min(n, 400), replace=False)
            ax.scatter(x[idx], y[idx], s=8, alpha=0.12, color=c)
        ax.scatter([np.median(x)], [np.median(y)], s=140, color=c,
                   edgecolor="k", zorder=5, label=f"{sub} (n={n})")
        ax.annotate(sub, (np.median(x), np.median(y)), fontsize=7,
                    xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("I.5q  —  q-banded KS distance to GUE  (← more GUE-like)")
    ax.set_ylabel("ARS.rep_med  —  repulsion-integral median")
    ax.set_title("Universal landscape (all 10 substrates) — descriptive, q-banded leg\n"
                 "pulsar = direct-leg (not q-banded); clouds subsampled")
    ax.legend(fontsize=6, loc="best", ncol=2)
    ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P1_universal_I5q_vs_rep.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def fig_matched(data):
    fig, ax = plt.subplots(figsize=(8.5, 7))
    # reference corners FIRST + hollow, so data points render on top of them
    ax.scatter([0], [0], marker="*", s=420, facecolor="none", edgecolor="k",
               linewidth=1.4, zorder=1)
    ax.annotate("Poisson", (0, 0), fontsize=9, xytext=(8, 8), textcoords="offset points")
    ax.scatter([1], [1], marker="*", s=420, facecolor="none", edgecolor="crimson",
               linewidth=1.4, zorder=1)
    ax.annotate("GUE/Wigner", (1, 1), fontsize=9, xytext=(-66, -14),
                textcoords="offset points")
    for sub in MATCHED:
        recs = data[sub]
        x = col(recs, "I.8_brody_q")
        y = col(recs, "I.9_berry_robnik_rho")
        n = min(x.size, y.size)
        if n == 0:
            continue
        ax.scatter(x[:n], y[:n], s=70, alpha=0.75, color=COLORS.get(sub, "#333"),
                   edgecolor="k", linewidth=0.4, zorder=5, label=f"{sub} (n={n})")
    ax.set_xlabel("Brody q  (0 = Poisson, 1 = Wigner)")
    ax.set_ylabel("Berry-Robnik ρ  (0 = Poisson, 1 = GOE/Wigner)")
    ax.set_title("Matched object-(a) repulsion plane — 7 substrates (matched to AM)")
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.05, 1.1)
    ax.legend(fontsize=7, loc="center right"); ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P2_matched_brody_vs_BR.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def fig_strip(data):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    items = []
    for sub, recs in data.items():
        v = col(recs, "I.5q_ks_gue_med")
        if v.size:
            items.append((sub, v))
    items.sort(key=lambda kv: np.median(kv[1]))
    for i, (sub, v) in enumerate(items):
        jitter = (np.random.default_rng(1).random(min(v.size, 300)) - 0.5) * 0.3
        vv = v if v.size <= 300 else v[np.random.default_rng(2).choice(v.size, 300, replace=False)]
        ax.scatter(vv, np.full(vv.size, i) + jitter, s=10, alpha=0.3,
                   color=COLORS.get(sub, "#333"))
        ax.scatter([np.median(v)], [i], s=120, color=COLORS.get(sub, "#333"),
                   edgecolor="k", zorder=5)
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([s for s, _ in items])
    ax.set_xlabel("I.5q — q-banded KS distance to GUE  (← GUE-like ........ far-from-GUE →)")
    ax.set_title("Lingua-franca strip: I.5q across all substrates (sorted by median)")
    ax.grid(alpha=0.2, axis="x")
    p = os.path.join(FIGDIR, "P3_I5q_strip.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def main():
    data = load_all()
    text_tables(data)
    figs = [fig_universal(data), fig_matched(data), fig_strip(data)]
    print("\nfigures written:")
    for p in figs:
        print("  " + os.path.relpath(p, _HERE))


if __name__ == "__main__":
    main()
