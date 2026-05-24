"""
cross_substrate/dimension_theory_check.py — Fibonacci D_box(λ) vs DEGT large-coupling theory.

Theory (Damanik-Embree-Gorodetski-Tcheremchantsev, CMP 2008, arXiv:0705.0338): for the
GOLDEN Fibonacci Hamiltonian, dim(Σ_λ)·ln(λ) → ln(1+√2) ≈ 0.88137 as λ→∞. Same coupling
convention as sturmian_eigs (diagonal λ·χ_{[1−α,1)}, off-diag 1).

Two instrument hazards at large λ, both must be handled before comparing to 0.8814:
  (1) SATURATION: at fine box sizes every eigenvalue is alone → counts plateau at N, so the
      naive box_dim (counts>1, all sizes) under-slopes. Fix: fit the slope only in the
      UNSATURATED scaling window (counts ≫ a few, counts ≪ N).
  (2) FINITE-N: the spectrum is more fractal at large λ, so N=50k under-resolves worse —
      box_dim·ln(λ) drifts DOWN with λ (banked: golden 0.767@λ8 → 0.738@λ16, away from
      0.8814). Must N-converge before trusting any large-λ value.

--probe: golden at λ∈{16,32} × N∈{50k,100k,200k}, naive vs windowed box_dim, + raw box-count
         log-log dump — decide whether the instrument can reach the asymptotic regime at our N.
Out (probe): prints only (decision gate before the full sweep).
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase35a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from cross_substrate.sturmian_hamiltonian_run import sturmian_eigs  # noqa: E402

GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0
N_PHI = 8
PHIS = (np.arange(N_PHI) + 0.5) / N_PHI
DEGT = np.log(1.0 + np.sqrt(2.0))   # 0.88137, the golden target for D_box·ln(λ)


def box_counts(eigs, n_sizes=18):
    e = np.sort(np.asarray(eigs, float))
    span = float(e[-1] - e[0])
    sizes = span / (2.0 ** np.arange(1, n_sizes + 1))
    counts = np.array([np.unique(np.floor((e - e[0]) / s)).size for s in sizes], float)
    return sizes, counts


def box_dim_naive(eigs, n_sizes=18):
    sizes, counts = box_counts(eigs, n_sizes)
    m = counts > 1
    if m.sum() < 4:
        return None
    return float(-np.polyfit(np.log(sizes[m]), np.log(counts[m]), 1)[0])


def box_dim_windowed(eigs, n_sizes=18, lo=8, hi_frac=0.5):
    """Slope in the UNSATURATED window: counts ≥ lo (above coarse few-box regime) and
    counts ≤ hi_frac·N (below fine-scale one-eigenvalue-per-box saturation)."""
    sizes, counts = box_counts(eigs, n_sizes)
    N = len(eigs)
    m = (counts >= lo) & (counts <= hi_frac * N)
    if m.sum() < 4:
        return None, m.sum()
    return float(-np.polyfit(np.log(sizes[m]), np.log(counts[m]), 1)[0]), int(m.sum())


def _fp(lam, n, which):
    """Return (naive D_box, windowed D_box, n_window) pooled over φ (mean)."""
    nv, wv, nw = [], [], []
    for phi in PHIS:
        ev = sturmian_eigs(GOLDEN, float(phi), lam=lam, n=n)
        d = box_dim_naive(ev)
        if d is not None:
            nv.append(d)
        w, k = box_dim_windowed(ev)
        if w is not None:
            wv.append(w); nw.append(k)
    return (float(np.mean(nv)) if nv else None,
            float(np.mean(wv)) if wv else None,
            int(np.mean(nw)) if nw else 0)


def _task(arg):
    lam, n = arg
    t0 = time.perf_counter()
    naive, win, nw = _fp(lam, n, "golden")
    return (lam, n, naive, win, nw, time.perf_counter() - t0)


def probe(workers):
    print(f"DIMENSION-THEORY PROBE (golden Fibonacci) — target D_box·ln(λ) → ln(1+√2) = {DEGT:.4f}")
    print("  naive vs windowed box_dim; N-convergence at large λ\n")
    tasks = [(lam, n) for lam in (16.0, 32.0) for n in (50_000, 100_000, 200_000)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = [fu.result() for fu in [ex.submit(_task, t) for t in tasks]]
    res.sort(key=lambda r: (r[0], r[1]))
    print(f"{'λ':>4s} {'N':>7s} {'naive':>7s} {'·lnλ':>6s} {'windowed':>8s} {'·lnλ':>6s} {'nwin':>5s} {'(s)':>5s}")
    for lam, n, naive, win, nw, dt in res:
        print(f"{lam:>4g} {n:>7d} {naive:>7.3f} {naive*np.log(lam):>6.3f} "
              f"{win:>8.3f} {win*np.log(lam):>6.3f} {nw:>5d} {dt:>5.0f}")
    # raw log-log dump at λ=32, N=200k for scaling-window inspection
    print("\nraw box-count log-log @ λ=32, N=200k (one φ) — is there a clean scaling window?")
    ev = sturmian_eigs(GOLDEN, float(PHIS[0]), lam=32.0, n=200_000)
    sizes, counts = box_counts(ev, 18)
    print(f"  {'ln(1/size)':>11s} {'ln(count)':>10s} {'local-slope':>11s}")
    ls, lc = np.log(1 / sizes), np.log(counts)
    for i in range(len(sizes)):
        sl = (lc[i] - lc[i - 1]) / (ls[i] - ls[i - 1]) if i else float('nan')
        sat = "  <- saturating" if counts[i] > 0.5 * len(ev) else ""
        print(f"  {ls[i]:>11.2f} {lc[i]:>10.2f} {sl:>11.3f}{sat}")
    print(f"\n[gate] does windowed box_dim·ln(λ) approach {DEGT:.4f} and stabilize in N? "
          "If yes → run full large-λ sweep; if finite-N still dominates at 200k → report bounded.")


# ── full large-λ sweep across classes (gate passed: N=50k converged, windowed box_dim) ──
import json                                                          # noqa: E402
from datetime import date                                           # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
LAM_BIG = [16.0, 32.0, 64.0, 128.0, 256.0, 512.0]
SWEEP_CLASSES = [
    ("golden",    (np.sqrt(5) - 1) / 2,  True,  2.0,  np.log(1 + np.sqrt(2))),  # DEGT target
    ("silver",    np.sqrt(2) - 1,        True,  2.0,  None),
    ("bronze",    (np.sqrt(13) - 3) / 2, True,  2.0,  None),
    ("e_minus_2", np.e - 2,              False, 2.0,  None),
    ("pi_minus_3", np.pi - 3,            False, 7.10, None),
    ("liouville", sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), False, 1e9, None),
]
N_SWEEP = 50_000
NSIZES_BIG = 26   # more box scales so the unsaturated within-cluster window stays populated at large λ


def _fp_class(alpha, lam, n, nsizes=NSIZES_BIG):
    wv, nw = [], []
    for phi in PHIS:
        ev = sturmian_eigs(alpha, float(phi), lam=lam, n=n)
        w, k = box_dim_windowed(ev, n_sizes=nsizes)
        if w is not None:
            wv.append(w); nw.append(k)
    return (float(np.mean(wv)) if wv else None, int(np.mean(nw)) if nw else 0)


def _sweep_task(arg):
    cls, alpha, lam, n = arg
    w, nw = _fp_class(alpha, lam, n)
    return (cls, lam, n, w, nw)


def sweep(workers):
    tasks = [(c, v, lam, N_SWEEP) for c, v, *_ in SWEEP_CLASSES for lam in LAM_BIG]
    tasks.append(("golden", (np.sqrt(5) - 1) / 2, 512.0, 100_000))   # N-spot-check at max λ
    print(f"DIMENSION-THEORY SWEEP — {len(tasks)} cells, {workers} workers, N={N_SWEEP} "
          f"(+1 N=100k spot), windowed box_dim, λ∈{LAM_BIG}")
    print(f"  golden target: D_box·ln(λ) → ln(1+√2) = {DEGT:.4f}")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = [fu.result() for fu in [ex.submit(_sweep_task, t) for t in tasks]]

    spot = [r for r in res if r[2] == 100_000]
    res = [r for r in res if r[2] == N_SWEEP]
    by = {}
    for cls, lam, n, w, nw in res:
        by.setdefault(cls, []).append((lam, w, nw))
    for c in by:
        by[c].sort()

    recs = []
    print(f"\n{'class':11s} {'C=lim D·lnλ':>11s} {'theory':>7s} {'a(subl)':>7s} {'D·lnλ@512':>10s}")
    summary = {}
    for cls, alpha, bounded, mu, theory in SWEEP_CLASSES:
        pts = by[cls]
        lams = np.array([p[0] for p in pts]); dbox = np.array([p[1] for p in pts])
        x = 1.0 / np.log(lams); y = dbox * np.log(lams)        # D·lnλ = C − a·x
        A = np.vstack([x, np.ones_like(x)]).T
        (slope, C), *_ = np.linalg.lstsq(A, y, rcond=None)
        a_sub = -slope
        summary[cls] = (C, a_sub, mu, theory, bounded)
        for lam, w, nw in pts:
            recs.append(_rec(cls, alpha, lam, N_SWEEP, w, nw, mu, bounded))
        ths = f"{theory:.4f}" if theory else "  -"
        print(f"{cls:11s} {C:>11.4f} {ths:>7s} {a_sub:>7.3f} {y[-1]:>10.4f}")
    if spot:
        c, lam, n, w, nw = spot[0]
        gd = dict((p[0], p[1]) for p in by["golden"]).get(lam)
        if gd is not None:
            print(f"\nN-spot golden λ={lam:g}: D_box(50k)={gd:.4f} vs (100k)={w:.4f}  "
                  f"(Δ={w-gd:+.4f} → N-{'stable' if abs(w-gd)<0.01 else 'DRIFT'})")
        recs.append(_rec("golden", (np.sqrt(5) - 1) / 2, lam, 100_000, w, nw, 2.0, True))

    with open(os.path.join(COORD, "dimension-theory.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    cg = summary["golden"][0]
    print(f"\n[DEGT cross-check] golden extrapolated C={cg:.4f} vs theory {DEGT:.4f} "
          f"(Δ={cg-DEGT:+.4f}). Cross-class C ordered by approximability? Flag, don't interpret.")
    _sweep_figure(by, summary)


def _rec(cls, alpha, lam, n, w, nw, mu, bounded):
    return {"substrate": "dimension-theory", "cell_id": f"{cls}/lam{lam:g}/N{n}",
            "axes_computed": {"IV.2_spectral_box_dim_windowed": w,
                              "D_box_times_lnlam": (w * np.log(lam) if w else None)},
            "extraction_method": f"Fibonacci α={cls}, λ={lam:g}; windowed box_dim (unsaturated "
                                 f"scaling window, n_sizes={NSIZES_BIG}), {N_PHI}φ, N={n}",
            "extraction_audit": {"lagrange_class": cls, "theta_or_alpha": float(alpha),
                                 "lam": lam, "N": n, "n_phi": N_PHI, "n_window": nw,
                                 "irrationality_measure": mu, "cf_bounded": bounded,
                                 "DEGT_target_golden": float(DEGT)},
            "source_artifact": "generated (deterministic eigensolve)",
            "computed_date": date.today().isoformat()}


def _sweep_figure(by, summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cmap = {"golden": "#d4af37", "silver": "#9aa0a6", "bronze": "#9c6b30",
            "e_minus_2": "#2ca02c", "pi_minus_3": "#1f77b4", "liouville": "#d62728"}
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    xs = np.linspace(0, 1 / np.log(16) * 1.05, 50)
    for cls, pts in by.items():
        lams = np.array([p[0] for p in pts]); dbox = np.array([p[1] for p in pts])
        x = 1 / np.log(lams); y = dbox * np.log(lams)
        C, a_sub, mu, theory, bounded = summary[cls]
        ax.scatter(x, y, s=55, color=cmap[cls], edgecolor="k", lw=0.4, zorder=4,
                   marker=("o" if bounded else "^"))
        ax.plot(xs, C - a_sub * xs, "-", color=cmap[cls], lw=1.0, alpha=0.7)
        ax.scatter([0], [C], s=90, marker="<", color=cmap[cls], edgecolor="k", zorder=5)
        ax.annotate(f"{cls} C={C:.3f}", (0, C), fontsize=7, xytext=(6, 0),
                    textcoords="offset points")
    ax.axhline(DEGT, ls="--", color="k", lw=1.2)
    ax.annotate(f"DEGT golden target ln(1+√2)={DEGT:.4f}", (0.18, DEGT), fontsize=8,
                xytext=(0, 4), textcoords="offset points")
    ax.set_xlabel("1 / ln(λ)   (λ→∞ at x=0)")
    ax.set_ylabel("D_box · ln(λ)")
    ax.set_title("P11 dimension-theory cross-check — D_box·ln(λ) extrapolation vs DEGT\n"
                 "(◀ = λ→∞ extrapolated C; golden should hit ln(1+√2); ● bounded-CF ▲ unbounded)")
    ax.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P11_dimension_theory.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.probe:
        probe(a.workers)
    elif a.sweep:
        sweep(a.workers)
    else:
        ap.error("need --probe or --sweep")


if __name__ == "__main__":
    main()
