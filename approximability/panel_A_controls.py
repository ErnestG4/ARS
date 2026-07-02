"""
approximability/panel_A_controls.py — close Panel A's control battery with OUT-OF-SAMPLE predictions.

The corrected candidate (C finite ⟺ liminf K<∞; within finite-K, C is a compressed ~0.9 spectral dimension,
NOT a rate/index tracker) was fit on {4 metallics, e, π}. Two shots it did NOT see:
  1. metallic-5 (K=5): PREDICT C in the ~0.9 compressed band, NOT tracking 𝓛(m5)=1.647 or Λ(m5)=√29=5.39.
  2. Λ-cluster (Bugeaud-style words with Λ≈2.95–3.25 fixed, but K and word-structure varying): PREDICT C does
     NOT track the (fixed) Λ; if anything it tracks K. Same-Λ different-word ⇒ if C varies, C is not a function of Λ.

READ-ONLY; imports the C engine; writes only under approximability/.
Run: PYTHONPATH=/home/combust/fmexplorer/riemann_explorer /home/combust/fmexplorer/bin/python3 \
       approximability/panel_A_controls.py
"""
import os, sys, csv, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
from cross_substrate.trace_map_dimension import dim_growth, DEGT_LAMS

PHI = 0.1234


def M(a):
    return np.array([[a, 1.0], [1.0, 0.0]])


def period_matrix(period):
    P = np.eye(2)
    for a in period:
        P = P @ M(a)
    return P


def levy(period):
    """𝓛 = (1/p) log ε, ε = top eigenvalue of the period matrix."""
    ev = np.linalg.eigvals(period_matrix(period))
    return np.log(max(abs(ev))) / len(period)


def pcf(digits, iters=300):
    """Value of [0; overline{digits}] in (0,1) by folding the period from the inside."""
    y = 0.0
    for _ in range(iters):
        for d in reversed(digits):
            y = 1.0 / (d + y)
    return y


def lagrange(period):
    """Λ = max_i ( a_i + [0;overline{a_{i+1},...}] + [0;overline{a_{i-1},a_{i-2},...}] ), cyclic."""
    p = len(period); best = 0.0
    for i in range(p):
        fwd = pcf([period[(i + 1 + k) % p] for k in range(p)])
        bwd = pcf([period[(i - 1 - k) % p] for k in range(p)])
        best = max(best, period[i] + fwd + bwd)
    return best


def Kgeom(period):
    """liminf K = geometric mean of the (periodic) partial quotients = (∏ a_i)^{1/p}."""
    return float(np.prod(period)) ** (1.0 / len(period))


def C_growthrate(alpha, sw, dp, lams=DEGT_LAMS):
    """Extrapolated C = lim_{λ→∞} dim·lnλ, growth-rate, convergence-gated (shallow-vs-deep |Δ|<0.02)."""
    conv = []
    for lam in lams:
        ds, _ = dim_growth(alpha, lam, sw, PHI)
        dd, _ = dim_growth(alpha, lam, dp, PHI)
        if ds is not None and dd is not None and abs(ds - dd) < 0.02:
            conv.append((1.0 / np.log(lam), dd * np.log(lam), lam))
    if len(conv) < 3:
        return None, [c[2] for c in conv]
    x = np.array([c[0] for c in conv]); y = np.array([c[1] for c in conv])
    slope, C = np.polyfit(x, y, 1)
    return float(C), [c[2] for c in conv]


# Fibonacci-tuned windows work for period words whose convergents are dense; metallic-5 needs Pell-5.
SW_FIB = [55, 89, 144, 233, 377, 610]; DP_FIB = [233, 377, 610, 987, 1597]
SW_M5 = [26, 135, 701]; DP_M5 = [135, 701, 3646]           # Pell-5 convergent denominators


if __name__ == "__main__":
    print("=" * 82)
    print("PANEL A CONTROL BATTERY — out-of-sample: metallic-5 (K=5) + Λ-cluster (fix Λ, vary word)")
    print("=" * 82)

    # ---- primitive validation of Λ and 𝓛 against the metallic identities ----
    print("\n[validate] Λ(metallic-n)=√(n²+4), 𝓛(metallic-n)=log((n+√(n²+4))/2):")
    for n in (1, 2, 3):
        Lam = lagrange([n]); Lv = levy([n])
        tL = np.sqrt(n * n + 4); tv = np.log((n + np.sqrt(n * n + 4)) / 2)
        print(f"   [{n}̄]: Λ={Lam:.5f} (target {tL:.5f} {'✓' if abs(Lam-tL)<1e-4 else 'FAIL'})  "
              f"𝓛={Lv:.5f} (target {tv:.5f} {'✓' if abs(Lv-tv)<1e-6 else 'FAIL'})")

    # ---- (1) metallic-5 OUT-OF-SAMPLE ----
    print("\n(1) metallic-5 [5̄] — OUT-OF-SAMPLE prediction: C in ~0.9 band, NOT 𝓛=1.647 / Λ=5.385")
    a5 = pcf([5]); C5, lams5 = C_growthrate(a5, SW_M5, DP_M5, lams=[2.0, 4.0, 8.0, 16.0, 32.0])
    print(f"   K=5  𝓛={levy([5]):.4f}  Λ={lagrange([5]):.4f}  →  C(measured)={('%.4f'%C5) if C5 else 'None'}  "
          f"(converged λ: {lams5})")
    if C5:
        band = 0.85 <= C5 <= 1.10
        print(f"   VERDICT: C={C5:.3f} {'IN the ~0.9 compressed band ✓ (prediction held)' if band else 'OUTSIDE band ✗'}; "
              f"C−𝓛={C5-levy([5]):+.3f} (huge ⇒ not a 𝓛-tracker), C/Λ={C5/lagrange([5]):.3f}")

    # ---- (2) Λ-cluster: fix Λ≈3, vary word ----
    print("\n(2) Λ-CLUSTER — words with Λ≈2.95–3.25 (fixed), K & structure varying:")
    CLUSTER = [[1, 2], [1, 1, 2], [1, 2, 2], [1, 1, 1, 2], [1, 2, 2, 2], [2, 2, 1, 1]]
    print(f"   {'word':14s} {'p':>2s} {'Λ':>7s} {'𝓛':>7s} {'K':>6s} {'C':>7s}   C−𝓛")
    rows = []
    for w in CLUSTER:
        a = pcf(w); Lam = lagrange(w); Lv = levy(w); K = Kgeom(w)
        C, lams = C_growthrate(a, SW_FIB, DP_FIB)
        rows.append({"word": w, "p": len(w), "alpha": a, "Lambda": Lam, "levy": Lv, "K": K, "C": C})
        Cs = f"{C:.4f}" if C else "  None"
        cm = f"{C-Lv:+.3f}" if C else "   -"
        print(f"   {str(w):14s} {len(w):>2d} {Lam:>7.4f} {Lv:>7.4f} {K:>6.3f} {Cs:>7s}   {cm}")
    good = [r for r in rows if r["C"] is not None]
    if len(good) >= 3:
        Cs = np.array([r["C"] for r in good]); Ks = np.array([r["K"] for r in good])
        Ls = np.array([r["Lambda"] for r in good]); Lv = np.array([r["levy"] for r in good])
        def R2(x, y):
            if np.std(x) < 1e-9: return float('nan')
            sl, ic = np.polyfit(x, y, 1); p = sl*x+ic
            return 1 - np.sum((y-p)**2)/np.sum((y-y.mean())**2)
        print(f"\n   within cluster: C spread sd={Cs.std():.3f} range=[{Cs.min():.3f},{Cs.max():.3f}]; "
              f"Λ spread sd={Ls.std():.3f} (fixed by design)")
        print(f"   C~Λ  R²={R2(Ls,Cs):.3f}  (fixed Λ ⇒ can't track it)   "
              f"C~K R²={R2(Ks,Cs):.3f}   C~𝓛 R²={R2(Lv,Cs):.3f}")
        print(f"   → if C varies across same-Λ words, C is NOT a function of Λ alone; "
              f"does the variation follow K (Liu–Wen order parameter)?")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "panel_A_controls.csv"), "w", newline="") as fh:
        wr = csv.writer(fh); wr.writerow(["word", "p", "Lambda", "levy", "K", "C"])
        wr.writerow(["[5̄]", 1, f"{lagrange([5]):.5f}", f"{levy([5]):.5f}", 5.0, (f"{C5:.5f}" if C5 else "")])
        for r in rows:
            wr.writerow(["".join(map(str, r["word"])), r["p"], f"{r['Lambda']:.5f}",
                         f"{r['levy']:.5f}", f"{r['K']:.5f}", (f"{r['C']:.5f}" if r["C"] else "")])
    print("\n   wrote approximability/panel_A_controls.csv — DONE.")
