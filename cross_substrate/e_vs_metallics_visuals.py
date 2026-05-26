"""
cross_substrate/e_vs_metallics_visuals.py — the "e vs the metallic means" visual story.

Four figures, each tied to a program finding, showing how e (μ=2 but UNBOUNDED/transcendental CF) separates
from the metallic means (bounded/quadratic CF) at every level:
  1. SUNFLOWERS — {nα mod 1} phyllotaxis spirals, coloured by three-distance gap class (the mechanism behind
     cf_discriminator: bounded CF → balanced gaps → repulsion).
  2. CF BARCODES — continued-fraction quotient fingerprints (metallic = constant stripes; e = growing pattern).
  3. SPECTRAL CANTOR SETS — Fibonacci/metallic/e Hamiltonian band structures, annotated with DEGT dimension
     (e's spectrum is a fatter fractal, C=1.17 vs golden 0.88).
  4. DIMENSION BREAK-AWAY — dim·ln(λ) extrapolation; metallic cluster vs e flying to 1.17.

Run: --run. Out: figures/V_*.png.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.trace_map_dimension import band_widths, _potential, cf_convergent, DEGT  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
FIG = os.path.join(_HERE, "figures")

# (name, α, colour) — μ=2 metallic means + e (the discriminator) + a couple of higher-μ for contrast
GOLD = (np.sqrt(5) - 1) / 2
CLASSES = [
    ("golden",    GOLD,                  "#d4af37"),
    ("silver",    np.sqrt(2) - 1,        "#9aa0a6"),
    ("bronze",    (np.sqrt(13) - 3) / 2, "#9c6b30"),
    ("metallic5", (np.sqrt(29) - 5) / 2, "#5b8c5a"),
    ("e − 2",     np.e - 2,              "#2ca02c"),
    ("ln 2",      np.log(2),             "#1f77b4"),
]
LIOUVILLE = sum(10.0 ** -k for k in (1, 2, 6, 24, 120))


def cf_digits(alpha, n):
    """Partial quotients a1,a2,… of α∈(0,1) (leading a0=0 dropped)."""
    a = float(alpha); out = []
    for _ in range(n):
        a = 1.0 / a if a > 0 else 0.0
        ai = int(np.floor(a)); out.append(ai)
        a -= ai
        if a < 1e-12:
            break
    return out


def band_intervals(V):
    """Band intervals [(lo,hi),…] of the period-q operator (sorted periodic+antiperiodic eigenvalues, paired)."""
    q = len(V); off = np.ones(q - 1)
    base = np.diag(V) + np.diag(off, 1) + np.diag(off, -1)
    Hp = base.copy(); Hp[0, q - 1] = Hp[q - 1, 0] = 1.0
    Ha = base.copy(); Ha[0, q - 1] = Ha[q - 1, 0] = -1.0
    e = np.sort(np.concatenate([np.linalg.eigvalsh(Hp), np.linalg.eigvalsh(Ha)]))
    return [(e[2 * k], e[2 * k + 1]) for k in range(q)]


# ---- Fig 1: sunflowers --------------------------------------------------------------------------------
def fig_sunflowers():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    N = 1400
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 9))
    for ax, (name, a, col) in zip(axes.ravel(), CLASSES):
        n = np.arange(1, N + 1)
        theta = 2 * np.pi * (n * a)
        r = np.sqrt(n)
        x, y = r * np.cos(theta), r * np.sin(theta)
        # three-distance gap class: gaps of sorted {nα mod 1}
        frac = (n * a) % 1.0
        order = np.argsort(frac)
        sf = frac[order]
        gaps = np.diff(np.concatenate([sf, [sf[0] + 1.0]]))
        gcl = np.zeros(N)
        uniq = np.unique(np.round(gaps, 6))
        gap_of = dict(zip(order, gaps))                      # each n → its forward gap
        gvals = np.array([gap_of[i] for i in range(N)])
        # map to ≤3 discrete colours by gap size rank
        ranks = {v: r for r, v in enumerate(sorted(set(np.round(gvals, 6))))}
        cidx = np.array([ranks[round(v, 6)] for v in gvals])
        sc = ax.scatter(x, y, c=cidx, s=10, cmap="viridis", edgecolor="none")
        ax.set_title(f"{name}   ({len(set(np.round(gvals,6)))} gap sizes)", fontsize=11, color=col, fontweight="bold")
        ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("{nα mod 1} sunflowers, coloured by three-distance gap class\n"
                 "golden = most uniform packing (badly-approximable); e = degenerating gap structure",
                 fontsize=12)
    p = os.path.join(FIG, "V1_sunflowers.png")
    fig.tight_layout(rect=[0, 0, 1, 0.96]); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


# ---- Fig 2: CF barcodes -------------------------------------------------------------------------------
def fig_cf_barcodes():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import mpmath
    mpmath.mp.dps = 140                      # high precision: CF stays EXACT for all rows to D=42
    rows = [("golden", (mpmath.sqrt(5) - 1) / 2), ("silver", mpmath.sqrt(2) - 1),
            ("bronze", (mpmath.sqrt(13) - 3) / 2), ("metallic5", (mpmath.sqrt(29) - 5) / 2),
            ("e − 2", mpmath.e - 2), ("ln 2", mpmath.log(2)),
            ("Liouville", sum(mpmath.mpf(10) ** -k for k in (1, 2, 6, 24, 120)))]

    def cf_hp(a, n):
        out = []
        for _ in range(n):
            if a <= 0:
                break
            a = 1 / a; ai = int(mpmath.floor(a)); out.append(ai); a -= ai
        return out
    D = 42
    M = np.full((len(rows), D), np.nan)
    cfs = {}
    for i, (n, a) in enumerate(rows):
        d = cf_hp(a, D); cfs[i] = d
        M[i, :len(d)] = d
    fig, ax = plt.subplots(figsize=(13, 5))
    im = ax.imshow(np.log10(M + 1), aspect="auto", cmap="magma", vmin=0, vmax=np.log10(13),
                   extent=[0.5, D + 0.5, len(rows) - 0.5, -0.5])   # clip so 1–12 show gradation; Liouville saturates
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=10)
    ax.set_xlabel("continued-fraction quotient index  (a₁, a₂, a₃, …)")
    ax.set_title("CF-quotient fingerprints — metallic means = constant stripes; "
                 "e = the growing [2;1,2,1,1,4,1,1,6,…] staircase; Liouville = sparse giant spikes")
    # annotate the actual digit values for the first several
    for i in range(len(rows)):
        for j, v in enumerate(cfs[i][:14]):
            ax.text(j + 1, i, str(v), ha="center", va="center", fontsize=6.5,
                    color="white" if v < 4 else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.025); cb.set_label("log₁₀(1 + quotient)")
    p = os.path.join(FIG, "V2_cf_barcodes.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


# ---- Fig 3: spectral Cantor sets ----------------------------------------------------------------------
def fig_cantor():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    lam = 2.5; phi = 0.1234                # weak coupling + coarse q → VISIBLE hierarchical Cantor gaps
    sel = [("golden", GOLD, "#d4af37", 0.876), ("silver", np.sqrt(2) - 1, "#9aa0a6", 0.867),
           ("bronze", (np.sqrt(13) - 3) / 2, "#9c6b30", 0.913), ("e − 2", np.e - 2, "#2ca02c", 1.173)]
    fig, ax = plt.subplots(figsize=(13, 5.5))
    for row, (name, a, col, C) in enumerate(sel):
        p, q = cf_convergent(a, 90)
        bands = band_intervals(_potential(q, p, lam, phi))
        segs = [[(lo, row), (hi, row)] for lo, hi in bands]
        ax.add_collection(LineCollection(segs, colors=col, linewidths=7))
        cover = sum(hi - lo for lo, hi in bands)
        ax.text(-0.02, row, f"{name}\nC={C:.3f}", ha="right", va="center", fontsize=9.5,
                color=col, fontweight="bold", transform=ax.get_yaxis_transform())
        ax.text(1.005, row, f"q={q}, Σ|band|={cover:.2f}", ha="left", va="center", fontsize=7.5,
                color="0.4", transform=ax.get_yaxis_transform())
    ax.set_xlim(-2.6, 2.6 + lam); ax.set_ylim(-0.6, len(sel) - 0.4)
    ax.set_yticks([]); ax.set_xlabel("energy E")
    ax.set_title(f"Spectral Cantor sets — Fibonacci/metallic/e Hamiltonians at coupling λ={lam:g}\n"
                 "the hierarchical band/gap structure; e's spectrum has the highest fractal dimension (C=1.17 vs golden 0.88)")
    p2 = os.path.join(FIG, "V3_spectral_cantor.png")
    fig.tight_layout(); fig.savefig(p2, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p2, _HERE))


# ---- Fig 4: dimension break-away ----------------------------------------------------------------------
def fig_breakaway():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path = os.path.join(COORD, "trace-map-dimension.jsonl")
    rows = [json.loads(l) for l in open(path)]
    by = {}
    for r in rows:
        a = r["axes_computed"]; au = r["extraction_audit"]
        if a.get("converged") and isinstance(a.get("dim_times_lnlam"), float):
            by.setdefault(au["lagrange_class"], []).append((au["lam"], a["dim_times_lnlam"]))
    col = {"golden": "#d4af37", "silver": "#9aa0a6", "bronze": "#9c6b30", "e_minus_2": "#2ca02c"}
    fig, ax = plt.subplots(figsize=(10, 6.5))
    for cls, pts in by.items():
        pts.sort()
        x = np.array([1 / np.log(l) for l, _ in pts]); y = np.array([v for _, v in pts])
        ax.scatter(x, y, s=60, color=col.get(cls, "k"), edgecolor="k", lw=0.4, zorder=4, label=cls)
        if len(x) >= 3:
            sl, C = np.polyfit(x, y, 1)
            xs = np.linspace(0, x.max() * 1.05, 30)
            ax.plot(xs, C + sl * xs, "-", color=col.get(cls, "k"), lw=1.1, alpha=0.7)
            ax.scatter([0], [C], s=130, marker="<", color=col.get(cls, "k"), edgecolor="k", zorder=5)
            ax.annotate(f"{cls}: {C:.3f}", (0, C), fontsize=9, xytext=(8, 0), textcoords="offset points",
                        color=col.get(cls, "k"), fontweight="bold")
    ax.axhline(DEGT, ls="--", color="k", lw=1.2)
    ax.annotate(f"DEGT golden: ln(1+√2)={DEGT:.4f}", (0.20, DEGT), fontsize=9, xytext=(0, 4),
                textcoords="offset points")
    ax.set_xlabel("1 / ln(λ)   (λ → ∞ at the left edge)")
    ax.set_ylabel("dim · ln(λ)   (growth-rate thermodynamic-formalism dimension)")
    ax.set_title("The dimension break-away — metallic means cluster at the DEGT line (~0.87–0.91);\n"
                 "e flies off to 1.17 (μ=2 but UNBOUNDED CF) — e separates from the metallics, again")
    ax.legend(fontsize=8, loc="lower right"); ax.grid(alpha=0.2)
    p = os.path.join(FIG, "V4_dimension_breakaway.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if not a.run:
        ap.error("need --run")
    fig_sunflowers()
    fig_cf_barcodes()
    fig_cantor()
    fig_breakaway()
    print("done — 4 figures in figures/V*.png")


if __name__ == "__main__":
    main()
