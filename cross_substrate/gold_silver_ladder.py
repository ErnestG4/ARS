"""
cross_substrate/gold_silver_ladder.py — what fills the gold↔silver region of the approximability axis?

The metallic means are the constant-CF diagonal (gold [1̄], silver [2̄], …). Between them lies the rich
structure of mixed-digit periodic-CF quadratics + the Markov/Lagrange spectrum. This builds a LADDER of
quadratic irrationals interpolating gold→silver (periodic CFs of 1s and 2s, incl. the Markov-5 number
[2,2,1,1]) and places them — alongside gold/silver/bronze/e — on:
  (A) the IDS staircases (gap structure; how it morphs across the ladder), and
  (B) the dimension-vs-approximability axis (DEGT growth-rate dimension C vs Lagrange constant): does the
      gold→silver bridge interpolate SMOOTHLY or show Markov/Lagrange fine-structure?

Each member: α (high-precision periodic CF), Lagrange constant (the approximability ruler), DEGT dimension
constant C (growth-rate thermodynamic formalism, convergence-gated, extrapolated 1/ln(λ)→0).

Run: --run [--workers 10]. Out: coordinates/gold-silver-ladder.jsonl + figures/V6_*, V7_*.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.trace_map_dimension import dim_growth, cf_convergent, _potential, DEGT  # noqa: E402
from cross_substrate.e_vs_metallics_visuals import band_intervals                            # noqa: E402
COORD = os.path.join(_HERE, "coordinates")
FIG = os.path.join(_HERE, "figures")

# LADDER: periodic-CF quadratics interpolating gold [1] → silver [2], ordered by 2-content.
# [1,1,2,2] / [2,2,1,1] are the Markov-5 number (Lagrange √221/5≈2.973). Plus bronze [3] + e (reference).
LADDER = [
    ("[1] gold",   [1]),
    ("[1,1,1,2]",  [1, 1, 1, 2]),
    ("[1,1,2]",    [1, 1, 2]),
    ("[1,2]",      [1, 2]),
    ("[2,2,1,1]M", [2, 2, 1, 1]),     # Markov-5
    ("[1,2,2]",    [1, 2, 2]),
    ("[1,2,2,2]",  [1, 2, 2, 2]),
    ("[2] silver", [2]),
]
REPS = 80


def cf_value(digits):
    """Value of the finite CF [0; d0, d1, …] by reverse recurrence."""
    x = 0.0
    for d in reversed(digits):
        x = 1.0 / (d + x)
    return x


def periodic_alpha(period):
    return cf_value(period * REPS)


def lagrange_const(period):
    """Lagrange number of a periodic CF: max over the period of [a_i; a_{i+1}, …] + [0; a_{i-1}, a_{i-2}, …]
    (both bi-infinite periodic)."""
    p = len(period); best = 0.0
    ext = period * REPS
    for i in range(p):
        fwd = (period[i:] + period[:i]) * REPS              # a_i, a_{i+1}, …
        f = fwd[0] + cf_value(fwd[1:])
        back = ((period[:i][::-1]) + (period[::-1]) * REPS)  # a_{i-1}, a_{i-2}, …
        b = cf_value(back)
        best = max(best, f + b)
    return best


# ---- DEGT dimension constant per member (growth-rate, convergence-gated, extrapolated) ----
SHALLOW_Q = [55, 89, 144, 233, 377, 610]
DEEP_Q = [233, 377, 610, 987, 1597]
LAMS = [2.0, 4.0, 8.0, 16.0, 32.0]


def _dim_task(arg):
    alpha, lam = arg
    ds, _ = dim_growth(alpha, lam, SHALLOW_Q)
    dd, _ = dim_growth(alpha, lam, DEEP_Q)
    conv = (ds is not None and dd is not None and abs(ds - dd) < 0.02)
    return (lam, dd, conv)


def degt_C(alpha, pool_results):
    pts = [(1 / np.log(lam), dd * np.log(lam)) for lam, dd, conv in pool_results if conv and dd]
    if len(pts) < 3:
        return None
    x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
    return float(np.polyfit(x, y, 1)[1])


def run(workers):
    print("GOLD↔SILVER LADDER — filling the approximability axis between the metallic means")
    # compute α + Lagrange per member
    rows = []
    for name, period in LADDER:
        a = periodic_alpha(period); L = lagrange_const(period)
        rows.append({"name": name, "period": period, "alpha": a, "lagrange": L})
    # dimension C per member (parallel over (member, λ))
    tasks = [(r["alpha"], lam) for r in rows for lam in LAMS]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_dim_task, tasks))
    k = len(LAMS)
    for i, r in enumerate(rows):
        r["C"] = degt_C(r["alpha"], res[i * k:(i + 1) * k])
    print(f"\n{'member':12s} {'α':>8s} {'Lagrange':>9s} {'DEGT C':>7s}")
    for r in rows:
        cstr = f"{r['C']:.4f}" if r["C"] else "  -"
        print(f"{r['name']:12s} {r['alpha']:>8.4f} {r['lagrange']:>9.4f} {cstr:>7s}")
    with open(os.path.join(COORD, "gold-silver-ladder.jsonl"), "w") as fh:
        for r in rows:
            fh.write(json.dumps({**r, "substrate": "gold-silver-ladder",
                                 "computed_date": date.today().isoformat()}) + "\n")
    print("\nLagrange spectrum landmarks: gold √5=2.2361, silver √8=2.8284, Markov-5 √221/5=2.9732 (→3)")
    _fig_staircases(rows)
    _fig_dim_vs_approx(rows)


def _fig_staircases(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lam = 2.5; phi = 0.1234
    order = sorted(rows, key=lambda r: r["lagrange"])     # bottom = least approximable (gold)
    cmap = plt.cm.viridis(np.linspace(0, 1, len(order)))
    fig, ax = plt.subplots(figsize=(13, 8))
    for row_i, (r, col) in enumerate(zip(order, cmap)):
        p, q = cf_convergent(r["alpha"], 90)
        bands = band_intervals(_potential(q, p, lam, phi))
        edges, ids, cum = [], [], 0.0
        for lo, hi in bands:
            edges += [lo, hi]; ids += [cum, cum + 1.0 / q]; cum += 1.0 / q
        # offset each staircase vertically by its ladder rank → a waterfall
        ax.plot(edges, np.array(ids) + row_i, "-", color=col, lw=1.2)
        ax.text(-2.7, row_i + 0.5, f"{r['name']}\nΛ={r['lagrange']:.3f}", ha="right", va="center",
                fontsize=7.5, color=col, fontweight="bold")
        # mark the biggest-gap label {1α} = α (the most-robust gap)
        ax.plot([2.6 + lam], [row_i + (r['alpha'] % 1.0)], ">", color=col, ms=6)
    ax.set_xlim(-2.7, 2.6 + lam + 0.3); ax.set_ylim(-0.3, len(order))
    ax.set_yticks([]); ax.set_xlabel("energy E   (each staircase: IDS 0→1, offset by approximability rank)")
    ax.set_title(f"Gold→silver ladder of IDS staircases (λ={lam:g}), stacked by Lagrange constant Λ (bottom=gold,\n"
                 "least-approximable). ▶ = the {1α} biggest-gap label. Watch the gap structure morph across the bridge.")
    p2 = os.path.join(FIG, "V6_ladder_staircases.png")
    fig.tight_layout(); fig.savefig(p2, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p2, _HERE))


def _fig_dim_vs_approx(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # reference points (banked DEGT): bronze 0.913, e 1.173
    refs = [("bronze", (np.sqrt(13) - 3) / 2, np.sqrt(13), 0.913, "#9c6b30"),
            ("e − 2", np.e - 2, None, 1.173, "#2ca02c")]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    xs = [r["lagrange"] for r in rows if r["C"]]
    ys = [r["C"] for r in rows if r["C"]]
    ax.plot(xs, ys, "-", color="0.6", lw=1, zorder=2)
    for r in rows:
        if r["C"]:
            ax.scatter(r["lagrange"], r["C"], s=70, color="#d4af37" if "gold" in r["name"]
                       else "#9aa0a6" if "silver" in r["name"] else "#4477aa",
                       edgecolor="k", zorder=4)
            ax.annotate(r["name"], (r["lagrange"], r["C"]), fontsize=7, xytext=(4, 4),
                        textcoords="offset points")
    for nm, a, L, C, col in refs:
        if L:
            ax.scatter(L, C, s=80, color=col, edgecolor="k", marker="s", zorder=4)
            ax.annotate(nm, (L, C), fontsize=8, xytext=(4, -10), textcoords="offset points", color=col)
    for xv, lbl in [(np.sqrt(5), "√5 gold"), (np.sqrt(8), "√8 silver"), (np.sqrt(221) / 5, "√221/5 Markov-5"), (3.0, "→3")]:
        ax.axvline(xv, ls=":", color="0.7", lw=0.8)
        ax.text(xv, ax.get_ylim()[0], lbl, rotation=90, fontsize=6.5, va="bottom", ha="right", color="0.5")
    ax.axhline(DEGT, ls="--", color="k", lw=0.9); ax.text(2.3, DEGT, f"DEGT={DEGT:.3f}", fontsize=8)
    ax.set_xlabel("Lagrange constant Λ  (approximability; gold √5 → silver √8 → Markov spectrum → 3)")
    ax.set_ylabel("DEGT dimension constant C  (growth-rate thermodynamic formalism)")
    ax.set_title("Filling the gold→silver bridge — DEGT dimension vs approximability\n"
                 "does C interpolate smoothly, or track Markov/Lagrange structure?")
    ax.grid(alpha=0.2)
    p = os.path.join(FIG, "V7_dim_vs_approximability.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
