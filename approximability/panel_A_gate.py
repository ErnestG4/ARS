"""
approximability/panel_A_gate.py — Panel A GATE (stop-and-look before the full regression).

Sequence (per the reviewer's gate design):
  (1) PIN λ + two-estimator agreement at λ≥16 (box_dim vs band-pressure growth-rate). Confirms C is a
      λ→∞ asymptotic (extrapolated from λ≥16), NOT a λ=2.5 finite proxy.
  (2) PRIMITIVES: from-scratch 𝓛(gold)=log φ=0.4812118, and dim E₂=0.5312805 (transfer operator).
  (3) INDEX-SHIFT TEST: C(metallic-n) vs 𝓛(metallic-n) [same index] and vs 𝓛(metallic-(n+1)) [shift].
      The anchor C(golden)=ln(1+√2)=𝓛(silver) is true BY the DEGT theorem — is the shift CONSISTENT
      across the ladder, or a golden-specific coincidence? Extend to metallic-4/5 to decide.

READ-ONLY: imports the C engine (cross_substrate/trace_map_dimension.py), edits nothing, writes only
under approximability/. Run:
  PYTHONPATH=$HOME/fmexplorer/riemann_explorer $HOME/fmexplorer/bin/python3 \
    approximability/panel_A_gate.py
"""
import os, sys, csv, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
from cross_substrate.trace_map_dimension import (
    cf_convergent, potential, band_widths, dim_growth, dim_pressure,
    DEGT, SHALLOW_Q, DEEP_Q, DEGT_LAMS)

OUT = os.path.dirname(os.path.abspath(__file__))
PHI = 0.1234

# ── Metallic ladder [n̄]: α_n = (√(n²+4)−n)/2, ε_n = (n+√(n²+4))/2, 𝓛 = log ε (period 1). ──
def metallic(n):
    s = np.sqrt(n * n + 4.0)
    return {"n": n, "alpha": (s - n) / 2.0, "eps": (n + s) / 2.0,
            "levy": np.log((n + s) / 2.0), "lagrange": s}   # Λ(metallic-n)=√(n²+4)
METALLICS = [metallic(n) for n in (1, 2, 3, 4, 5)]
NAMES = {1: "golden", 2: "silver", 3: "bronze", 4: "metallic-4", 5: "metallic-5"}


def C_growthrate(alpha):
    """Extrapolated C = lim_{λ→∞} dim(Σ_λ)·ln λ via growth-rate thermodynamic formalism,
    convergence-gated (shallow vs deep q-window), λ→∞ extrapolation over converged λ (same as
    trace_map_dimension.degt_sweep). Returns (C, converged_lams, per-λ points)."""
    conv_pts, allpts = [], []
    for lam in DEGT_LAMS:
        ds, _ = dim_growth(alpha, lam, SHALLOW_Q, PHI)
        dd, lv = dim_growth(alpha, lam, DEEP_Q, PHI)
        conv = (ds is not None and dd is not None and abs(ds - dd) < 0.02)
        allpts.append((lam, ds, dd, conv))
        if conv:
            conv_pts.append((1.0 / np.log(lam), dd * np.log(lam), lam))
    if len(conv_pts) < 3:
        return None, [], allpts
    x = np.array([p[0] for p in conv_pts]); y = np.array([p[1] for p in conv_pts])
    slope, C = np.polyfit(x, y, 1)
    return float(C), [p[2] for p in conv_pts], allpts


# ── dim E₂ (digits ∈ {1,2}) via transfer operator L_s f(x)=Σ_{a=1,2}(a+x)^{-2s} f(1/(a+x)). ──
# dim = s* where leading eigenvalue ρ(s*)=1. Chebyshev–Nyström collocation on [0,1] (analytic → spectral acc.).
def dim_E2(M=40):
    j = np.arange(M)
    x = 0.5 * (1 - np.cos(np.pi * j / (M - 1)))            # Chebyshev nodes on [0,1]
    # barycentric weights for Chebyshev-Lobatto
    w = np.ones(M); w[1::2] = -1; w[0] *= 0.5; w[-1] *= 0.5
    def interp_matrix(xt):                                  # rows: eval points; cols: nodal basis
        xt = np.asarray(xt)[:, None]
        diff = xt - x[None, :]
        exact = np.isclose(diff, 0.0)
        with np.errstate(divide="ignore", invalid="ignore"):
            W = w[None, :] / diff
        W[exact.any(axis=1)] = 0.0
        rows_exact = np.where(exact.any(axis=1))[0]
        B = W / W.sum(axis=1, keepdims=True)
        for r in rows_exact:
            B[r] = exact[r].astype(float)
        return B
    def rho(s):
        A = np.zeros((M, M))
        for a in (1, 2):
            g = 1.0 / (a + x)                               # branch image of each node
            A += (1.0 / (a + x))[:, None] ** (2 * s) * interp_matrix(g)
        # A acts as (L_s f)(x_i) = Σ_a (a+x_i)^{-2s} f(g_i); f(g_i)=interp -> B @ f_nodes
        # careful: kernel weight uses (a+x_i)^{-2s}, image node g_i=1/(a+x_i)
        return np.max(np.abs(np.linalg.eigvals(A)))
    lo, hi = 0.4, 0.7
    for _ in range(60):
        s = 0.5 * (lo + hi)
        if rho(s) > 1.0: lo = s
        else: hi = s
    return 0.5 * (lo + hi)


def box_dim_from_eigs(eigs, n_sizes=14):
    """Box-counting dimension of a 1-D spectrum (log N(ε) vs log(1/ε), robust window)."""
    e = np.sort(np.asarray(eigs, float)); span = e[-1] - e[0]
    if span <= 0: return None
    e = (e - e[0]) / span
    sizes = np.logspace(-3.5, -0.7, n_sizes)
    N = np.array([len(np.unique(np.floor(e / s))) for s in sizes])
    lx, ly = np.log(1 / sizes), np.log(N)
    return float(np.polyfit(lx, ly, 1)[0])


if __name__ == "__main__":
    print("=" * 78)
    print("PANEL A GATE — identify C (DEGT spectral dimension) before the regression")
    print("=" * 78)

    # ---- (2) PRIMITIVES ----
    L_gold = np.log((1 + np.sqrt(5)) / 2)
    e2 = dim_E2()
    print("\n(2) PRIMITIVE GATES")
    print(f"  𝓛(golden) = log φ         = {L_gold:.7f}   target 0.4812118   "
          f"{'PASS' if abs(L_gold-0.4812118)<1e-6 else 'FAIL'}")
    print(f"  dim E₂ (transfer operator) = {e2:.7f}   target 0.5312805   "
          f"{'PASS' if abs(e2-0.5312805)<1e-4 else 'FAIL'}")

    # ---- (1) TWO-ESTIMATOR AGREEMENT AT λ≥16 (golden) ----
    print("\n(1) TWO-ESTIMATOR AGREEMENT (golden) — box_dim vs band-pressure growth-rate")
    try:
        from cross_substrate.sturmian_hamiltonian_run import sturmian_eigs
        have_eigs = True
    except Exception as ex:
        have_eigs = False; print(f"    (sturmian_eigs unavailable: {ex})")
    ag = (np.sqrt(5) - 1) / 2
    print(f"  {'λ':>5s} {'box_dim·lnλ':>12s} {'pressure·lnλ (growth)':>22s} {'Δ':>8s}")
    for lam in (8.0, 16.0, 32.0):
        dd, _ = dim_growth(ag, lam, DEEP_Q, PHI)
        pr = dd * np.log(lam) if dd else None
        bx = None
        if have_eigs:
            try:
                ev = sturmian_eigs(ag, PHI, lam=lam, n=4000)
                bd = box_dim_from_eigs(ev)
                bx = bd * np.log(lam) if bd else None
            except Exception:
                bx = None
        bxs = f"{bx:.4f}" if bx else "   -"
        prs = f"{pr:.4f}" if pr else "   -"
        d = f"{pr-bx:+.4f}" if (bx and pr) else "   -"
        print(f"  {lam:>5g} {bxs:>12s} {prs:>22s} {d:>8s}")
    print(f"  → C is extrapolated from the λ≥16 growth-rate points to λ→∞ (x=1/lnλ→0); "
          f"λ=2.5 is band-plot legibility only, not a C value.")

    # ---- (3) INDEX-SHIFT TEST ----
    print("\n(3) INDEX-SHIFT TEST — C(metallic-n) vs 𝓛(metallic-n) and 𝓛(metallic-(n+1))")
    rows = []
    for m in METALLICS:
        C, clams, _ = C_growthrate(m["alpha"])
        rows.append({**m, "name": NAMES[m["n"]], "C": C, "conv_lams": clams})
    # attach 𝓛(n+1)
    levy_by_n = {m["n"]: m["levy"] for m in METALLICS}
    print(f"\n  {'class':11s} {'C':>7s} {'𝓛(n)':>7s} {'𝓛(n+1)':>8s}  {'C−𝓛(n)':>8s} {'C−𝓛(n+1)':>9s}")
    for r in rows:
        Ln, Ln1 = r["levy"], levy_by_n.get(r["n"] + 1)
        C = r["C"]
        s_same = f"{C-Ln:+.3f}" if C else "   -"
        s_shift = f"{C-Ln1:+.3f}" if (C and Ln1) else "   -"
        Cs = f"{C:.4f}" if C else "  -"
        L1s = f"{Ln1:.4f}" if Ln1 else "   -"
        print(f"  {r['name']:11s} {Cs:>7s} {Ln:>7.4f} {L1s:>8s}  {s_same:>8s} {s_shift:>9s}")

    # regressions (over metallics with a C and a defined 𝓛(n+1))
    def r2(xs, ys):
        xs, ys = np.asarray(xs), np.asarray(ys)
        sl, ic = np.polyfit(xs, ys, 1); pred = sl * xs + ic
        ss_res = np.sum((ys - pred) ** 2); ss_tot = np.sum((ys - ys.mean()) ** 2)
        return (1 - ss_res / ss_tot if ss_tot > 0 else float('nan')), sl, ic
    have = [r for r in rows if r["C"] is not None]
    Cvals = [r["C"] for r in have]
    Lsame = [r["levy"] for r in have]
    shift = [(r, levy_by_n.get(r["n"] + 1)) for r in have]
    shift = [(r, l1) for r, l1 in shift if l1 is not None]
    print("\n  REGRESSIONS:")
    R2s, sl_s, _ = r2(Lsame, Cvals)
    print(f"   C ~ 𝓛(same index) : R²={R2s:.3f}  slope={sl_s:+.3f}  "
          f"(index-shift H1 predicts C≈𝓛(n+1), so same-index slope≈0 if plateau)")
    if len(shift) >= 3:
        R2sh, sl_sh, ic_sh = r2([l1 for _, l1 in shift], [r["C"] for r, _ in shift])
        print(f"   C ~ 𝓛(n+1 shift)  : R²={R2sh:.3f}  slope={sl_sh:+.3f} intercept={ic_sh:+.3f}  "
              f"(consistent shift ⇒ R²≈1, slope≈1, intercept≈0)")
    # plateau test: is C ~ constant across bounded metallics?
    print(f"   C spread across bounded metallics: mean={np.mean(Cvals):.4f} "
          f"sd={np.std(Cvals):.4f} range=[{min(Cvals):.4f},{max(Cvals):.4f}]")
    print(f"   𝓛 spread (same set):               mean={np.mean(Lsame):.4f} "
          f"sd={np.std(Lsame):.4f} range=[{min(Lsame):.4f},{max(Lsame):.4f}]")

    # CSV
    with open(os.path.join(OUT, "panel_A_C_levy.csv"), "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["n", "name", "alpha", "eps", "C_degt", "levy_L", "lagrange_Lambda",
                     "levy_n_plus_1", "conv_lams"])
        for r in rows:
            wr.writerow([r["n"], r["name"], f"{r['alpha']:.6f}", f"{r['eps']:.6f}",
                         (f"{r['C']:.5f}" if r["C"] else ""), f"{r['levy']:.5f}",
                         f"{r['lagrange']:.5f}", (f"{levy_by_n.get(r['n']+1):.5f}" if levy_by_n.get(r['n']+1) else ""),
                         "|".join(f"{l:g}" for l in r["conv_lams"])])
    print(f"\n  wrote {os.path.relpath(os.path.join(OUT,'panel_A_C_levy.csv'), _ROOT)}")
    # save numeric summary json for the figure/report
    with open(os.path.join(OUT, "panel_A_gate.json"), "w") as fh:
        json.dump({"primitives": {"levy_gold": L_gold, "dim_E2": e2},
                   "metallics": [{"n": r["n"], "name": r["name"], "C": r["C"],
                                  "levy": r["levy"], "lagrange": r["lagrange"]} for r in rows]},
                  fh, indent=2)
    print("  DONE.")
