"""
cross_substrate/confluence_view.py — AM-vs-Fibonacci confluence figure.

Two panels (descriptive, flag-don't-interpret):
  P5a  D_box vs λ — the AM golden-θ trajectory through criticality, with the
       Fibonacci-Hamiltonian reference line; finite-N points at λ≈1 overlaid.
  P5b  repulsion plane (Brody q × W1δ) — AM's λ-trajectory sweeping from the
       Wigner corner (sub-AC) to the clustered/Poisson corner (criticality),
       relative to the fixed Fibonacci point and the Sturmian-Ham α-family.

Reads coordinates/am-confluence.jsonl + sturmian-hamiltonian.jsonl. Writes
figures/P5_confluence.png.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
FIGDIR = os.path.join(_HERE, "figures")
FIB_DBOX = 0.6279349210480618

_REGIME_C = {"sub_AC": "#377eb8", "critical": "#e41a1c", "sup_PP": "#4daf4a"}


def _load(name):
    return [json.loads(l) for l in open(os.path.join(COORD, f"{name}.jsonl"))]


def main():
    conf = _load("am-confluence")
    sturm = _load("sturmian-hamiltonian")
    fib = next(r for r in sturm if r["cell_id"].startswith("golden"))
    fib_q = fib["axes_computed"]["I.8_brody_q"]
    fib_w1 = fib["axes_computed"]["I.1_w1_clock"]

    base = sorted([r for r in conf if r["extraction_audit"]["N"] == 50000],
                  key=lambda r: r["extraction_audit"]["lam"])
    conv = sorted([r for r in conf if r["extraction_audit"]["N"] != 50000],
                  key=lambda r: (r["extraction_audit"]["lam"], r["extraction_audit"]["N"]))

    def ax_of(r, k):
        return r["axes_computed"].get(k)

    lam = [r["extraction_audit"]["lam"] for r in base]
    dbox = [ax_of(r, "IV.2_spectral_box_dim") for r in base]
    reg = [r["extraction_audit"]["regime"] for r in base]

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6))

    # ── P5a: D_box vs λ ──────────────────────────────────────────────────────
    axA.plot(lam, dbox, "-", color="0.5", lw=1.2, zorder=1)
    for l, d, rg in zip(lam, dbox, reg):
        axA.scatter([l], [d], s=95, color=_REGIME_C[rg], edgecolor="k", zorder=4)
    # finite-N points at criticality region
    for r in conv:
        l = r["extraction_audit"]["lam"]; n = r["extraction_audit"]["N"]
        axA.scatter([l], [ax_of(r, "IV.2_spectral_box_dim")], s=40, marker="D",
                    color="white", edgecolor=_REGIME_C[r["extraction_audit"]["regime"]],
                    zorder=5)
        axA.annotate(f"N={n//1000}k", (l, ax_of(r, "IV.2_spectral_box_dim")),
                     fontsize=5, xytext=(3, -8), textcoords="offset points")
    axA.axhline(FIB_DBOX, ls="--", color="crimson", lw=1.2)
    axA.annotate(f"Fibonacci Hamiltonian (λ=2): D_box={FIB_DBOX:.3f}",
                 (0.52, FIB_DBOX), fontsize=8, color="crimson",
                 xytext=(0, 5), textcoords="offset points")
    axA.axvline(1.0, ls=":", color="0.4", lw=1)
    axA.annotate("criticality λ=1", (1.0, 0.86), fontsize=8, rotation=90,
                 xytext=(-13, 0), textcoords="offset points", color="0.3")
    axA.set_xlabel("AM coupling λ  (golden θ)")
    axA.set_ylabel("D_box — spectral box-counting dimension (IV.2)")
    axA.set_title("P5a confluence: AM D_box trajectory vs Fibonacci reference\n"
                  "(diamonds = finite-N at λ≈1; circles colored by regime)")
    axA.grid(alpha=0.2)
    from matplotlib.lines import Line2D
    axA.legend(handles=[Line2D([], [], marker="o", ls="", color=c, mec="k", label=k)
                        for k, c in _REGIME_C.items()], fontsize=8, loc="lower left")

    # ── P5b: repulsion plane (Brody q × W1δ) ─────────────────────────────────
    q = [ax_of(r, "I.8_brody_q") for r in base]
    w1 = [ax_of(r, "I.1_w1_clock") for r in base]
    axB.plot(q, w1, "-", color="0.6", lw=1.0, zorder=1)
    for l, qi, wi, rg in zip(lam, q, w1, reg):
        axB.scatter([qi], [wi], s=85, color=_REGIME_C[rg], edgecolor="k", zorder=4)
        axB.annotate(f"λ={l:g}", (qi, wi), fontsize=6, xytext=(4, 2),
                     textcoords="offset points")
    # Sturmian-Ham α-family (the Cantor-spectrum siblings)
    for r in sturm:
        axB.scatter([ax_of(r, "I.8_brody_q")], [ax_of(r, "I.1_w1_clock")],
                    s=45, marker="^", color="0.75", edgecolor="0.3", zorder=2)
    axB.scatter([fib_q], [fib_w1], s=320, marker="*", color="crimson",
                edgecolor="k", zorder=6)
    axB.annotate("Fibonacci\nHamiltonian", (fib_q, fib_w1), fontsize=8, color="crimson",
                 xytext=(8, -18), textcoords="offset points")
    axB.set_xlabel("Brody q  (0 = Poisson/clustered, 1 = Wigner)")
    axB.set_ylabel("W1δ  (→ broader / more clustered)")
    axB.set_title("P5b AM λ-trajectory in the repulsion plane\n"
                  "(grey ▲ = Sturmian-Ham α-family; ★ = Fibonacci)")
    axB.grid(alpha=0.2)

    os.makedirs(FIGDIR, exist_ok=True)
    p = os.path.join(FIGDIR, "P5_confluence.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))

    fig_coupling()


def fig_coupling():
    """P7 — coupling correspondence: AM and Fibonacci D_box(λ) curves on one axis.
    Tests whether the Fibonacci family reaches AM-crit's D_box (it does, at λ≈3.5),
    resolving the §3(g) coupling caveat toward confluence."""
    am = sorted([r for r in _load("am-confluence")
                 if r["extraction_audit"]["N"] == 50000],
                key=lambda r: r["extraction_audit"]["lam"])
    fib = sorted([r for r in _load("fibonacci-lambda")
                  if r["extraction_audit"]["N"] == 50000],
                 key=lambda r: r["extraction_audit"]["lam"])
    AM_CRIT = 0.5136

    def xy(recs):
        return ([r["extraction_audit"]["lam"] for r in recs],
                [r["axes_computed"]["IV.2_spectral_box_dim"] for r in recs])

    fig, ax = plt.subplots(figsize=(9, 6.2))
    lx, ly = xy(am)
    ax.plot(lx, ly, "o-", color="#000000", lw=1.4, ms=7, label="AM (golden θ) — D_box(λ)")
    fx, fy = xy(fib)
    ax.plot(fx, fy, "^-", color="crimson", lw=1.4, ms=7,
            label="Fibonacci/Sturmian-Ham (golden) — D_box(λ)")
    ax.axhline(AM_CRIT, ls="--", color="0.4", lw=1)
    ax.annotate(f"AM-critical D_box={AM_CRIT:.3f} (λ=1)", (5.4, AM_CRIT),
                fontsize=8, color="0.3", xytext=(0, 4), textcoords="offset points")
    # the crossings: AM min at λ=1; Fibonacci reaches it at λ≈3.46
    ax.scatter([1.0], [AM_CRIT], s=160, marker="o", facecolor="none",
               edgecolor="black", lw=1.6, zorder=6)
    ax.scatter([3.46], [AM_CRIT], s=180, marker="*", color="crimson",
               edgecolor="k", zorder=6)
    ax.annotate("Fibonacci reaches\nAM-crit fingerprint\nλ≈3.46", (3.46, AM_CRIT),
                fontsize=8, color="crimson", xytext=(10, -34), textcoords="offset points")
    ax.set_xlabel("operator coupling λ (each in its own normalization)")
    ax.set_ylabel("D_box — spectral box-counting dimension (IV.2)")
    ax.set_title("P7 coupling correspondence — AM-critical D_box is a member of the\n"
                 "Fibonacci coupling family (reached at λ≈3.5, not the reference λ=2)")
    ax.legend(fontsize=9); ax.grid(alpha=0.2)
    p = os.path.join(FIGDIR, "P7_coupling_correspondence.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


if __name__ == "__main__":
    main()
