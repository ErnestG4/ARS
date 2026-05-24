"""
cross_substrate/landscape_view.py — exploratory landscape projections (14 substrates).

Charting, NOT hypothesis-testing (landscape §6): present multiple projections; do not
pick a "winning" viewpoint or interpret clusters. Reads coordinates/*.jsonl (auto-
discovers all substrates), prints summary tables, writes figures to figures/.

No single axis spans all 14 substrates (q-banded I.5q ⊃ ARS-classified; matched W1δ ⊃
object-(a) substrates; Family V ⊃ time-series substrates). Each projection includes
whichever substrates carry its axes; the rest are absent by construction, not omitted.

Projections:
  P1 universal q-banded: I.5q × ARS.rep_med (ARS-classified substrates).
  P2 matched repulsion plane: Brody q × BR ρ (object-(a): AM, pvc-11, arithmetic, dynamical).
  P3 I.5q strip (sorted), ARS-classified.
  P4 Family V (dynamical): D₂ × W1δ, the chaos-ordered MG/Lorenz/logistic trajectories.
"""
from __future__ import annotations

import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
FIGDIR = os.path.join(_HERE, "figures")
os.makedirs(FIGDIR, exist_ok=True)

_PALETTE = {
    "pvc-11": "#1f77b4", "allen-np": "#17becf", "kuramoto": "#2ca02c",
    "pulsar-nanograv": "#7f7f7f", "L-zeros": "#d62728", "mertens": "#9467bd",
    "liouville": "#8c564b", "maass-gamma0": "#e377c2", "gaussian-primes": "#ff7f0e",
    "eisenstein-primes": "#bcbd22", "am": "#000000", "mackey-glass": "#e41a1c",
    "lorenz": "#377eb8", "logistic": "#4daf4a",
}
DYNAMICAL = ["mackey-glass", "lorenz", "logistic"]


def load_all():
    out = {}
    for f in sorted(glob.glob(os.path.join(COORD, "*.jsonl"))):
        out[os.path.basename(f)[:-6]] = [json.loads(l) for l in open(f)]
    return out


def col(recs, key):
    return np.array([r["axes_computed"].get(key) for r in recs
                     if isinstance(r["axes_computed"].get(key), (int, float))], float)


def color(sub, i=0):
    return _PALETTE.get(sub, cm.tab20(i % 20))


def msummary(v):
    if v.size == 0:
        return None
    return dict(n=v.size, med=float(np.median(v)),
                p25=float(np.percentile(v, 25)), p75=float(np.percentile(v, 75)))


def has(recs, key):
    return col(recs, key).size > 0


def text_tables(data):
    print("=" * 84)
    print(f"LANDSCAPE VIEW — {len(data)} substrates (descriptive, no interpretation)")
    print("=" * 84)
    print("\n[q-banded] I.5q (ks-GUE) × ARS.rep_med — ARS-classified substrates")
    for sub, recs in sorted(data.items(),
                            key=lambda kv: (msummary(col(kv[1], "I.5q_ks_gue_med")) or {"med": 9})["med"]):
        a = msummary(col(recs, "I.5q_ks_gue_med"))
        if not a:
            continue
        b = msummary(col(recs, "ARS.rep_med"))
        flag = "  (direct-leg)" if sub == "pulsar-nanograv" else ""
        print(f"  {sub:18s} I.5q={a['med']:.3f} [{a['p25']:.2f},{a['p75']:.2f}] (n={a['n']})"
              f"  rep={b['med']:.3f}{flag}" if b else "")

    print("\n[matched object-(a)] W1δ / Brody q / BR ρ / ks_GUE — substrates with plain-NNS")
    for sub, recs in data.items():
        if not has(recs, "I.1_w1_clock"):
            continue
        def m(k):
            s = msummary(col(recs, k))
            return f"{s['med']:.3f}" if s else "  -  "
        print(f"  {sub:18s} W1δ={m('I.1_w1_clock')} q={m('I.8_brody_q')} "
              f"ρ={m('I.9_berry_robnik_rho')} ks_GUE={m('I.5_ks_gue')} (n={len(recs)})")

    print("\n[Family V — dynamical] D₂ / λ₁ — time-series substrates")
    for sub in DYNAMICAL:
        recs = data.get(sub, [])
        for r in recs:
            a = r["axes_computed"]
            d2, lam = a.get("V.2_correlation_dim"), a.get("V.1_lyapunov")
            print(f"  {sub:14s} {r['cell_id'][:22]:22s} "
                  f"D₂={d2:.2f}" if isinstance(d2, float) else f"  {sub} {r['cell_id']} D₂=NA",
                  f"λ₁={lam:+.3f}" if isinstance(lam, float) else "λ₁=NA")


def _scatter_medians(ax, data, kx, ky, subs=None):
    for i, (sub, recs) in enumerate(data.items()):
        if subs and sub not in subs:
            continue
        x, y = col(recs, kx), col(recs, ky)
        n = min(x.size, y.size)
        if n == 0:
            continue
        x, y = x[:n], y[:n]
        c = color(sub, i)
        if n > 40:
            idx = np.random.default_rng(0).choice(n, min(n, 300), replace=False)
            ax.scatter(x[idx], y[idx], s=7, alpha=0.10, color=c)
        ax.scatter([np.median(x)], [np.median(y)], s=130, color=c, edgecolor="k",
                   zorder=5, label=f"{sub} (n={n})")
        ax.annotate(sub, (np.median(x), np.median(y)), fontsize=6,
                    xytext=(4, 4), textcoords="offset points")


def fig_universal(data):
    fig, ax = plt.subplots(figsize=(9.5, 6.8))
    _scatter_medians(ax, data, "I.5q_ks_gue_med", "ARS.rep_med")
    ax.set_xlabel("I.5q — q-banded KS to GUE (← GUE-like)")
    ax.set_ylabel("ARS.rep_med")
    ax.set_title("P1 universal (q-banded, ARS-classified substrates)")
    ax.legend(fontsize=6, ncol=2); ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P1_universal_I5q_vs_rep.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def fig_matched(data):
    fig, ax = plt.subplots(figsize=(8.5, 7))
    ax.scatter([0], [0], marker="*", s=420, facecolor="none", edgecolor="k", lw=1.4, zorder=1)
    ax.annotate("Poisson", (0, 0), fontsize=9, xytext=(8, 8), textcoords="offset points")
    ax.scatter([1], [1], marker="*", s=420, facecolor="none", edgecolor="crimson", lw=1.4, zorder=1)
    ax.annotate("GUE/Wigner", (1, 1), fontsize=9, xytext=(-66, -14), textcoords="offset points")
    matched = [s for s, r in data.items() if has(r, "I.8_brody_q")]
    _scatter_medians(ax, data, "I.8_brody_q", "I.9_berry_robnik_rho", subs=matched)
    ax.set_xlabel("Brody q (0=Poisson, 1=Wigner)")
    ax.set_ylabel("Berry-Robnik ρ")
    ax.set_title("P2 matched repulsion plane (object-(a): AM, pvc-11, arithmetic, dynamical)")
    ax.set_xlim(-0.05, 1.15); ax.set_ylim(-0.05, 1.15)
    ax.legend(fontsize=6, ncol=2); ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P2_matched_brody_vs_BR.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def fig_strip(data):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    items = [(s, col(r, "I.5q_ks_gue_med")) for s, r in data.items()
             if col(r, "I.5q_ks_gue_med").size]
    items.sort(key=lambda kv: np.median(kv[1]))
    for i, (sub, v) in enumerate(items):
        vv = v if v.size <= 300 else v[np.random.default_rng(2).choice(v.size, 300, replace=False)]
        jit = (np.random.default_rng(1).random(vv.size) - 0.5) * 0.3
        ax.scatter(vv, np.full(vv.size, i) + jit, s=9, alpha=0.3, color=color(sub, i))
        ax.scatter([np.median(v)], [i], s=110, color=color(sub, i), edgecolor="k", zorder=5)
    ax.set_yticks(range(len(items))); ax.set_yticklabels([s for s, _ in items])
    ax.set_xlabel("I.5q — q-banded KS to GUE (← GUE-like ...... far →)")
    ax.set_title("P3 lingua-franca strip: I.5q (sorted)"); ax.grid(alpha=0.2, axis="x")
    p = os.path.join(FIGDIR, "P3_I5q_strip.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def fig_familyV(data):
    """Dynamical sub-landscape: D₂ × W1δ, per-cell, chaos-ordered trajectories."""
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for i, sub in enumerate(DYNAMICAL):
        recs = data.get(sub, [])
        pts = [(r["axes_computed"].get("V.2_correlation_dim"),
                r["axes_computed"].get("I.1_w1_clock"), r["cell_id"])
               for r in recs]
        pts = [(d, w, c) for d, w, c in pts if isinstance(d, (int, float))]
        if not pts:
            continue
        d2 = [p[0] for p in pts]
        w1 = [p[1] if isinstance(p[1], (int, float)) else 0.0 for p in pts]
        ax.plot(d2, w1, "-", color=color(sub, i), alpha=0.4, zorder=1)
        ax.scatter(d2, w1, s=80, color=color(sub, i), edgecolor="k", lw=0.4,
                   zorder=3, label=sub)
        for d, w, c in pts:
            ax.annotate(c.split("_", 1)[-1][:10], (d, w if isinstance(w, (int, float)) else 0),
                        fontsize=5, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("V.2 correlation dimension D₂ (→ higher-D chaos)")
    ax.set_ylabel("W1δ (peak/event-interval NNS, → broader)")
    ax.set_title("P4 Family V — dynamical sub-landscape (chaos-ordered trajectories)")
    ax.legend(fontsize=8); ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P4_familyV_dynamical.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    return p


def main():
    data = load_all()
    text_tables(data)
    figs = [fig_universal(data), fig_matched(data), fig_strip(data), fig_familyV(data)]
    print("\nfigures:")
    for p in figs:
        print("  " + os.path.relpath(p, _HERE))


if __name__ == "__main__":
    main()
