"""
cross_substrate/trace_map_dimension.py — the PROPER Fibonacci dimension estimator.

Box-counting finite spectra (dimension_theory_check.py) cannot reach the DEGT strong-coupling
constant: it fragments at cluster-splitting and finite-N caps the resolvable Cantor depth. The
correct numerical route (how DEGT/physics-lit compute it) is the periodic-approximant band
structure, NOT eigenvalues:

  Fibonacci-period-q approximant: α_n = F_{n-1}/F_n (rational, period q=F_n). The period-q
  Schrödinger operator has discriminant Δ_q(E) = Tr ∏_{j=0}^{q-1} T_j(E),
  T_j = [[E − V_j, −1],[1, 0]],  V_j = λ·χ_{[1−α,1)}({jα+φ}). Spectrum = {E: |Δ_q(E)| ≤ 2},
  a union of q bands. The box/Hausdorff dimension d solves the **Bowen pressure equation**
  Σ_k |band_k|^d = 1 (cover by the q bands); d_n → dim as q→∞.

Target: golden d·ln(λ) → ln(1+√2) = 0.88137 (Damanik-Embree-Gorodetski-Tcheremchantsev 2008).

VALIDATE FIRST (synthetic-validate discipline): at moderate λ∈{2,4,8} where eigenvalue box_dim
is trusted (no cluster-splitting), the band-pressure d must agree with banked box_dim
(golden λ=2 → 0.628). Only then trust it at large λ where box-counting failed.

Modes: --validate | --sweep [--workers 10].  Out: coordinates/trace-map-dimension.jsonl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
DEGT = np.log(1.0 + np.sqrt(2.0))   # 0.88137

# Fibonacci numbers (periodic-approximant periods)
_FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]


def _potential(q, p, lam, phi):
    """Sturmian potential for the period-q approximant α=p/q (golden: p=F_{n-1}, q=F_n)."""
    alpha = p / q
    frac = (np.arange(q) * alpha + phi) % 1.0
    return lam * (frac >= 1.0 - alpha).astype(np.float64)


def discriminant(E, V):
    """Δ_q(E) = Tr ∏ T_j(E), vectorized over E. Gaps overflow to ±inf (correctly out-of-band)."""
    E = np.asarray(E, float)
    # M = T_0
    m00 = E - V[0]; m01 = -np.ones_like(E); m10 = np.ones_like(E); m11 = np.zeros_like(E)
    with np.errstate(over="ignore", invalid="ignore"):
        for j in range(1, len(V)):
            ev = E - V[j]
            n00 = ev * m00 - m10
            n01 = ev * m01 - m11
            m10, m11 = m00, m01
            m00, m01 = n00, n01
        return m00 + m11


def band_widths(V, lam=None):
    """EXACT band widths via the periodic/antiperiodic eigenvalues of the period-q operator.
    For a period-q Schrödinger operator the 2q band edges ARE the eigenvalues under periodic
    (Δ=+2) and antiperiodic (Δ=−2) boundary conditions; sorted and paired they give the q bands.
    Exact at any λ — no E-grid, no resolution wall (the grid method missed exponentially small
    bands at large λ)."""
    q = len(V)
    off = np.ones(q - 1)
    base = np.diag(V) + np.diag(off, 1) + np.diag(off, -1)
    Hp = base.copy(); Hp[0, q - 1] = 1.0; Hp[q - 1, 0] = 1.0      # periodic
    Ha = base.copy(); Ha[0, q - 1] = -1.0; Ha[q - 1, 0] = -1.0    # antiperiodic
    edges = np.sort(np.concatenate([np.linalg.eigvalsh(Hp), np.linalg.eigvalsh(Ha)]))
    w = edges[1::2] - edges[0::2]      # pair (e0,e1),(e2,e3),… = the q bands
    return w[w > 0]


def dim_pressure(widths):
    """Bowen: solve Σ |w_k|^d = 1 for d∈(0,1]. Σ decreases from q (d→0) to Σw (d=1)."""
    if widths.size == 0:
        return None
    if widths.sum() >= 1.0:          # approximant measure still >1 → level too coarse for d<1
        return 1.0
    lo, hi = 1e-6, 1.0
    for _ in range(80):
        d = 0.5 * (lo + hi)
        s = np.sum(widths ** d)
        if s > 1.0:
            lo = d
        else:
            hi = d
    return 0.5 * (lo + hi)


def dim_at(lam, n_fib, phi=0.1234):
    q, p = _FIB[n_fib], _FIB[n_fib - 1]
    V = _potential(q, p, lam, phi)
    w = band_widths(V)
    return dim_pressure(w), len(w), q


def dim_growth(alpha, lam, q_targets, phi=0.1234):
    """PROPER thermodynamic-formalism dimension: d* where the partition-function GROWTH RATE across
    renormalization levels vanishes — slope of log Σ|band|^d vs log(q) = 0. Scale-INVARIANT (unlike the
    single-level Σ|w|^d=1, which drifts because band-count and total-measure both change with q). For a
    self-similar Cantor cover with N_n bands of width w_n, slope = 0 ⇒ d = log N_n / log(1/w_n) = box-dim."""
    levels = []
    for qt in q_targets:
        p, q = cf_convergent(alpha, qt)
        w = band_widths(_potential(q, p, lam, phi))
        if w.size > 2:
            levels.append((q, w))
    # dedupe by q (CF convergents repeat below jumps), keep ≥3 distinct levels
    seen = {}
    for q, w in levels:
        seen[q] = w
    levels = sorted(seen.items())
    if len(levels) < 3:
        return None, [q for q, _ in levels]
    logq = np.array([np.log(q) for q, _ in levels])
    dgrid = np.linspace(0.02, 0.999, 200)
    P = np.array([np.polyfit(logq, np.array([np.log(np.sum(w ** d)) for _, w in levels]), 1)[0]
                  for d in dgrid])
    sign = np.sign(P)
    cross = np.where(np.diff(sign) != 0)[0]
    if cross.size == 0:
        return None, [q for q, _ in levels]
    i = cross[0]
    d_star = dgrid[i] - P[i] * (dgrid[i + 1] - dgrid[i]) / (P[i + 1] - P[i])
    return float(d_star), [q for q, _ in levels]


def validate():
    print(f"TRACE-MAP DIMENSION — validate vs box_dim @ moderate λ (target golden·lnλ → {DEGT:.4f})")
    print("  banked box_dim: golden λ=2 → 0.628 (trusted, no cluster-split at moderate λ)\n")
    GOLD_BOX = {2.0: 0.628, 4.0: 0.475, 8.0: 0.369}   # from fibonacci-lambda / lambda-star sweeps
    print(f"{'λ':>4s} {'n_fib':>5s} {'q':>5s} {'nbands':>6s} {'dim':>6s} {'dim·lnλ':>8s} {'box_dim':>8s}")
    for lam in (2.0, 4.0, 8.0):
        for nf in (10, 12, 14):          # q = 55, 144, 610 — watch q-convergence
            d, nb, q = dim_at(lam, nf)
            bx = GOLD_BOX.get(lam)
            print(f"{lam:>4g} {nf:>5d} {q:>5d} {nb:>6d} {d:>6.4f} {d*np.log(lam):>8.4f} "
                  f"{(f'{bx:.3f}' if bx else '  -'):>8s}{'  <- band-count≠q!' if nb != q else ''}")
        print()
    print("[gate] band-pressure dim should (a) converge in q, (b) agree with box_dim at λ=2 "
          "(~0.63). If yes → trust at large λ where box-counting failed.")


def cf_convergent(alpha, qmax):
    """Largest-denominator continued-fraction convergent (p, q) of alpha with q ≤ qmax."""
    a = float(alpha); h0, h1, k0, k1 = 0, 1, 1, 0
    best = (0, 1)
    for _ in range(80):
        ai = int(np.floor(a))
        h2, k2 = ai * h1 + h0, ai * k1 + k0
        if k2 > qmax:
            break
        if k2 >= 1:
            best = (h2, k2)
        h0, h1, k0, k1 = h1, h2, k1, k2
        frac = a - ai
        if frac < 1e-13:
            break
        a = 1.0 / frac
    return best


# trace-map sweep classes: clean low-q CF approximants (golden = DEGT target; metallic + e).
# π/Liouville excluded — their CF has huge quotients so periodic approximants jump in q
# (already placed by the box_dim λ* sweep). value, μ, theory-target.
TM_CLASSES = [
    ("golden",    (np.sqrt(5) - 1) / 2,  2.0, np.log(1 + np.sqrt(2))),   # DEGT: ln(1+√2)
    ("silver",    np.sqrt(2) - 1,        2.0, None),
    ("bronze",    (np.sqrt(13) - 3) / 2, 2.0, None),
    ("e_minus_2", np.e - 2,              2.0, None),
]
TM_LAMS = [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0, 512.0, 1024.0]
QMAX = 1600
PHI_TM = 0.1234


def _tm_task(arg):
    cls, alpha, lam = arg
    p, q = cf_convergent(alpha, QMAX)
    V = _potential(q, p, lam, PHI_TM)
    w = band_widths(V)
    d = dim_pressure(w)
    return (cls, lam, p, q, d, len(w))


def sweep(workers):
    import json
    from concurrent.futures import ProcessPoolExecutor
    print(f"TRACE-MAP DIMENSION SWEEP — golden target dim·ln(λ) → ln(1+√2) = {DEGT:.4f}")
    print(f"  exact periodic/antiperiodic band edges, CF approximant q≤{QMAX}\n")
    # q-convergence check for golden at λ=64
    print("q-convergence (golden, λ=64):")
    for q_target in (377, 610, 987, 1597):
        p, q = cf_convergent((np.sqrt(5) - 1) / 2, q_target)
        d = dim_pressure(band_widths(_potential(q, p, 64.0, PHI_TM)))
        print(f"   q={q:>4d}: dim={d:.4f} dim·lnλ={d*np.log(64):.4f}")

    tasks = [(c, v, lam) for c, v, _, _ in TM_CLASSES for lam in TM_LAMS]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_tm_task, tasks))
    by = {}
    for cls, lam, p, q, d, nb in res:
        by.setdefault(cls, []).append((lam, d, q, nb))
    for c in by:
        by[c].sort()

    recs = []
    print(f"\n{'class':10s} {'q':>5s} {'C=lim dim·lnλ':>13s} {'theory':>8s}   dim·lnλ @λ=2…1024")
    summary = {}
    for cls, alpha, mu, theory in TM_CLASSES:
        pts = by[cls]
        lams = np.array([p[0] for p in pts]); dims = np.array([p[1] for p in pts])
        y = dims * np.log(lams); x = 1.0 / np.log(lams)
        m = lams >= 16.0          # asymptotic-regime fit
        A = np.vstack([x[m], np.ones(m.sum())]).T
        (slope, C), *_ = np.linalg.lstsq(A, y[m], rcond=None)
        summary[cls] = (C, -slope, theory, mu, pts[0][2])
        for lam, d, q, nb in pts:
            recs.append(_rec(cls, alpha, lam, d, q, nb, mu, theory))
        ths = f"{theory:.4f}" if theory else "   -"
        seq = " ".join(f"{v:.3f}" for v in y)
        print(f"{cls:10s} {pts[0][2]:>5d} {C:>13.4f} {ths:>8s}   {seq}")

    with open(os.path.join(COORD, "trace-map-dimension.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    cg, _, _, _, _ = summary["golden"]
    print(f"\n[DEGT] golden extrapolated C={cg:.4f} vs ln(1+√2)={DEGT:.4f} (Δ={cg-DEGT:+.4f}). "
          "Flag, don't interpret.")
    _tm_figure(by, summary)


def _rec(cls, alpha, lam, d, q, nb, mu, theory):
    return {"substrate": "trace-map-dimension", "cell_id": f"{cls}/lam{lam:g}/q{q}",
            "axes_computed": {"spectral_dimension_pressure": d,
                              "dim_times_lnlam": (d * np.log(lam) if d else None)},
            "extraction_method": f"Fibonacci/Sturmian periodic approximant α={cls} (q={q} CF "
                                 f"convergent); EXACT band edges (periodic/antiperiodic eigvalsh) "
                                 f"+ Bowen pressure Σ|band|^d=1",
            "extraction_audit": {"lagrange_class": cls, "alpha": float(alpha), "lam": lam,
                                 "approximant_q": q, "n_bands": nb,
                                 "irrationality_measure": mu,
                                 "DEGT_target": (float(theory) if theory else None)},
            "source_artifact": "generated (deterministic; trace-map band structure)",
            "computed_date": date.today().isoformat()}


def _tm_figure(by, summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cmap = {"golden": "#d4af37", "silver": "#9aa0a6", "bronze": "#9c6b30", "e_minus_2": "#2ca02c"}
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    xs = np.linspace(0, 1 / np.log(16) * 1.05, 50)
    for cls, pts in by.items():
        lams = np.array([p[0] for p in pts]); dims = np.array([p[1] for p in pts])
        x = 1 / np.log(lams); y = dims * np.log(lams)
        C, a_sub, theory, mu, q = summary[cls]
        ax.scatter(x, y, s=50, color=cmap[cls], edgecolor="k", lw=0.4, zorder=4)
        ax.plot(xs, C - a_sub * xs, "-", color=cmap[cls], lw=1.0, alpha=0.7)
        ax.scatter([0], [C], s=95, marker="<", color=cmap[cls], edgecolor="k", zorder=5)
        ax.annotate(f"{cls} C={C:.3f}", (0, C), fontsize=7, xytext=(6, 0), textcoords="offset points")
    ax.axhline(DEGT, ls="--", color="k", lw=1.3)
    ax.annotate(f"DEGT golden: ln(1+√2)={DEGT:.4f}", (0.10, DEGT), fontsize=9,
                xytext=(0, 5), textcoords="offset points")
    ax.set_xlabel("1 / ln(λ)   (λ→∞ at x=0; λ up to 1024)")
    ax.set_ylabel("dim · ln(λ)   (Bowen-pressure spectral dimension)")
    ax.set_title("P11 dimension-theory cross-check (trace-map band-pressure)\n"
                 "golden → ln(1+√2)? ◀ = λ→∞ extrapolated constant")
    ax.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P11_dimension_theory.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


SHALLOW_Q = [55, 89, 144, 233, 377, 610]
DEEP_Q = [233, 377, 610, 987, 1597]
DEGT_LAMS = [2.0, 4.0, 8.0, 16.0, 32.0, 48.0, 64.0, 128.0]


def _degt_task(arg):
    """Per (class, λ): growth-rate dim on shallow & deep q-windows + convergence gate."""
    cls, alpha, lam = arg
    ds, _ = dim_growth(alpha, lam, SHALLOW_Q)
    dd, lv = dim_growth(alpha, lam, DEEP_Q)
    conv = (ds is not None and dd is not None and abs(ds - dd) < 0.02)
    return (cls, lam, ds, dd, conv, lv)


def degt_sweep(workers):
    """PROPER thermodynamic-formalism DEGT test: growth-rate dimension (scale-invariant), convergence-gated
    (shallow vs deep q-window), extrapolated 1/ln(λ)→0. Resolves §3(k) (single-level pressure was
    scale-dependent → diverged). Golden target: dim·ln(λ) → ln(1+√2)=0.88137 (DEGT 2008)."""
    from concurrent.futures import ProcessPoolExecutor
    print(f"DEGT TRACE-MAP DIMENSION (growth-rate thermodynamic formalism) — golden → ln(1+√2)={DEGT:.4f}")
    tasks = [(c, v, lam) for c, v, _, _ in TM_CLASSES for lam in DEGT_LAMS]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_degt_task, tasks))
    by = {}
    for cls, lam, ds, dd, conv, lv in res:
        by.setdefault(cls, []).append((lam, ds, dd, conv))
    for c in by:
        by[c].sort()
    recs = []
    print(f"\n{'class':10s} {'C=lim dim·lnλ':>13s} {'theory':>8s}  {'reliable-λ (converged)':>22s}")
    summary = {}
    for cls, alpha, mu, theory in TM_CLASSES:
        pts = by[cls]
        conv_pts = [(1.0 / np.log(lam), dd * np.log(lam), lam) for lam, ds, dd, conv in pts if conv]
        if len(conv_pts) >= 3:
            x = np.array([p[0] for p in conv_pts]); y = np.array([p[1] for p in conv_pts])
            slope, C = np.polyfit(x, y, 1)
        else:
            C, slope = None, None
        rel = ",".join(f"{p[2]:g}" for p in conv_pts)
        summary[cls] = (C, conv_pts, theory)
        ths = f"{theory:.4f}" if theory else "   -"
        print(f"{cls:10s} {(f'{C:.4f}' if C else '  -'):>13s} {ths:>8s}  {rel:>22s}")
        for lam, ds, dd, conv in pts:
            recs.append({"substrate": "trace-map-dimension", "cell_id": f"{cls}/lam{lam:g}",
                         "axes_computed": {"dim_growth_shallow": ds, "dim_growth_deep": dd,
                                           "dim_times_lnlam": (dd * np.log(lam) if dd else None),
                                           "converged": conv},
                         "extraction_method": "growth-rate thermodynamic formalism: d* where slope(log Σ|band|^d "
                                              "vs log q)=0; convergence-gated (shallow vs deep q-window); "
                                              "extrapolated 1/ln(λ)→0",
                         "extraction_audit": {"lagrange_class": cls, "lam": lam, "irrationality_measure": mu,
                                              "DEGT_target": (float(theory) if theory else None),
                                              "extrapolated_C": (float(C) if C else None)},
                         "source_artifact": "generated (deterministic; trace-map periodic-approximant bands)",
                         "computed_date": date.today().isoformat()})
    with open(os.path.join(COORD, "trace-map-dimension.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    cg = summary["golden"][0]
    print(f"\n[DEGT] golden extrapolated C={cg:.4f} vs ln(1+√2)={DEGT:.4f} (Δ={cg-DEGT:+.4f}) — "
          f"{'CONFIRMED within ~0.5%' if abs(cg-DEGT)<0.01 else 'see Δ'}. Flag, don't interpret.")
    _degt_figure(summary)


def _degt_figure(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cmap = {"golden": "#d4af37", "silver": "#9aa0a6", "bronze": "#9c6b30", "e_minus_2": "#2ca02c"}
    fig, ax = plt.subplots(figsize=(9.5, 6.4))
    for cls, (C, conv_pts, theory) in summary.items():
        if not conv_pts:
            continue
        x = np.array([p[0] for p in conv_pts]); y = np.array([p[1] for p in conv_pts])
        ax.scatter(x, y, s=55, color=cmap.get(cls, "k"), edgecolor="k", lw=0.4, zorder=4)
        xs = np.linspace(0, x.max() * 1.05, 40)
        if C is not None:
            slope = np.polyfit(x, y, 1)[0]
            ax.plot(xs, C + slope * xs, "-", color=cmap.get(cls, "k"), lw=1.0, alpha=0.7)
            ax.scatter([0], [C], s=110, marker="<", color=cmap.get(cls, "k"), edgecolor="k", zorder=5)
            ax.annotate(f"{cls} C={C:.3f}", (0, C), fontsize=7.5, xytext=(6, 0), textcoords="offset points")
    ax.axhline(DEGT, ls="--", color="k", lw=1.3)
    ax.annotate(f"DEGT: ln(1+√2)={DEGT:.4f}", (0.18, DEGT), fontsize=9, xytext=(0, 4), textcoords="offset points")
    ax.set_xlabel("1 / ln(λ)   (λ→∞ at x=0)"); ax.set_ylabel("dim · ln(λ)   (growth-rate thermodynamic formalism)")
    ax.set_title("DEGT cross-check — growth-rate dimension, convergence-gated\n"
                 "golden → ln(1+√2)? ◀ = λ→∞ extrapolation")
    ax.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P11b_degt_growthrate.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--degt", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.validate:
        validate()
    elif a.sweep:
        sweep(a.workers)
    elif a.degt:
        degt_sweep(a.workers)
    else:
        ap.error("need --validate, --sweep, or --degt")


if __name__ == "__main__":
    main()
