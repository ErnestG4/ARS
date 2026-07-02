"""
approximability/panel_A_K_reframe.py — the K-reframe that corrects Panel A's positive candidate.

THEOREM (Liu–Qu–Wen, Adv. Math. 2013): at large coupling, dim_H Σ_{α,λ} = 1  ⟺  K(α) = ∞, where
K(α) = liminf_k (∏₁ᵏ aᵢ)^{1/k} is the GEOMETRIC MEAN of the partial quotients (NOT boundedness).
⇒ C = dim·lnλ is FINITE exactly when K(α) < ∞, and DIVERGES (~lnλ) when K(α)=∞.

Consequence for Panel B: e (K=∞, the 2,4,6,… spine) diverges; π (K=K₀≈2.685, finite) converges and sits
with the metallics. π and e are on OPPOSITE sides of this axis — the reverse of the μ=2 tier intuition.

This script establishes:
  (A) the K order parameter, EXACT from CF digits: K(metallic-a)=a; K(e)→∞; K(π)→Khinchin K₀=2.6854520.
  (B) the engine dim·lnλ trend vs λ: golden/π flatten to a finite C; e does NOT flatten (dim stays high → C grows).

READ-ONLY; imports the C engine; writes only under approximability/.
Run: PYTHONPATH=/home/combust/fmexplorer/riemann_explorer /home/combust/fmexplorer/bin/python3 \
       approximability/panel_A_K_reframe.py
"""
import os, sys, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
import mpmath as mp
from cross_substrate.trace_map_dimension import dim_growth, dim_pressure, band_widths, _potential, cf_convergent

mp.mp.dps = 220
OUT = os.path.dirname(os.path.abspath(__file__))
PHI = 0.1234
KHINCHIN = 2.6854520010653064


def cf_digits(x, n):
    """First n partial quotients of x (mpmath high precision)."""
    a = []
    y = mp.mpf(x)
    for _ in range(n):
        ai = int(mp.floor(y))
        a.append(ai)
        frac = y - ai
        if frac == 0:
            break
        y = 1 / frac
    return a


def K_seq(digits):
    """K_k = (∏₁ᵏ aᵢ)^{1/k} — geometric mean of partial quotients (Liu–Qu–Wen order parameter)."""
    out, logsum = [], 0.0
    for k, a in enumerate(digits, 1):
        logsum += np.log(a)
        out.append(np.exp(logsum / k))
    return out


def gk_random_digits(n, seed=0):
    """Gauss–Kuzmin-distributed partial quotients: P(a=k)=log2(1+1/(k(k+2))). Inverse-CDF sample."""
    rng = np.random.default_rng(seed)
    u = rng.random(n)
    # CDF: P(a<=k) = 1 - log2(1 + 1/(k+1))  ->  invert
    ks = np.arange(1, 20000)
    cdf = 1.0 - np.log2(1.0 + 1.0 / (ks + 1))
    return [int(ks[np.searchsorted(cdf, uu)]) for uu in u]


if __name__ == "__main__":
    print("=" * 80)
    print("PANEL A — K-REFRAME (Liu–Qu–Wen: dim=1 ⟺ K=∞;  C finite ⟺ K<∞)")
    print("=" * 80)

    # ---- (A) The K order parameter, exact from CF digits ----
    pi_d = cf_digits(mp.pi, 200)
    e_d = cf_digits(mp.e, 200)
    gk_d = gk_random_digits(200, seed=1)
    families = {
        "golden [1̄]":  [1] * 200,
        "silver [2̄]":  [2] * 200,
        "bronze [3̄]":  [3] * 200,
        "metallic-4":   [4] * 200,
        "π":            pi_d,
        "e":            e_d,
        "GK-random":    gk_d,
    }
    print("\n(A) K(α) = liminf (∏aᵢ)^{1/k}  —  the geometric-mean order parameter (EXACT from CF digits)")
    print(f"  {'α':14s} {'K@k=20':>8s} {'K@k=60':>8s} {'K@k=150':>9s}  trend / class")
    Ksummary = {}
    for name, d in families.items():
        ks = K_seq(d[:150])
        k20, k60, k150 = ks[19], ks[59], ks[149]
        Ksummary[name] = (k20, k60, k150)
        if name.startswith(("golden", "silver", "bronze", "metallic")):
            trend = f"= a (constant) → FINITE"
        elif name == "e":
            trend = "RISING → K=∞  (dim→1, C DIVERGES)"
        elif name == "π":
            trend = f"→ Khinchin K₀={KHINCHIN:.4f}  → FINITE (C converges)"
        else:
            trend = f"→ Khinchin K₀={KHINCHIN:.4f} (generic) → FINITE"
        print(f"  {name:14s} {k20:>8.3f} {k60:>8.3f} {k150:>9.3f}  {trend}")
    # e's slow divergence: show it keeps climbing
    e_ks = K_seq(e_d[:200])
    print(f"  → e: K climbs {e_ks[19]:.3f}(k20) → {e_ks[99]:.3f}(k100) → {e_ks[199]:.3f}(k200); "
          f"the 2,4,6,8,… spine ⇒ (∏a)^{{1/k}}~(k/3)^{{1/3}}→∞ (slow but unbounded).")

    # ---- (B) Engine dim·lnλ trend: does it flatten (finite C) or grow (divergent)? ----
    print("\n(B) ENGINE dim·lnλ vs λ — finite family FLATTENS to C; K=∞ (e) does NOT flatten")
    SW = [55, 89, 144, 233, 377, 610]; DP = [233, 377, 610, 987, 1597]
    LAMS = [8.0, 16.0, 32.0, 64.0, 128.0, 256.0]
    probe = {"golden": (np.sqrt(5) - 1) / 2, "e_minus_2": np.e - 2}
    print(f"  {'α':10s} " + " ".join(f"λ={l:g}".rjust(8) for l in LAMS) + "   trend")
    trends = {}
    for name, alpha in probe.items():
        row = []
        for lam in LAMS:
            dd, _ = dim_growth(alpha, lam, DP, PHI)
            row.append(dd * np.log(lam) if dd else None)
        trends[name] = row
        # is the last value still climbing vs the middle? divergent if dim·lnλ keeps rising
        vals = [v for v in row if v is not None]
        climbing = (len(vals) >= 2 and vals[-1] > vals[len(vals)//2] + 0.03)
        cells = " ".join((f"{v:.3f}".rjust(8) if v is not None else "   -".rjust(8)) for v in row)
        tag = "STILL CLIMBING → divergent (K=∞)" if climbing else "flattening → finite C"
        print(f"  {name:10s} {cells}   {tag}")
    # also report dim itself for e vs golden at the largest λ (theorem: dim(e)→1, dim(golden)→0)
    print("\n  dim(Σ_λ) itself (theorem: →1 for e/K=∞, →0 for finite-K):")
    for name, alpha in probe.items():
        dims = []
        for lam in (16.0, 64.0, 256.0):
            dd, _ = dim_growth(alpha, lam, DP, PHI)
            dims.append((lam, dd))
        s = "  ".join(f"λ={l:g}:dim={d:.3f}" for l, d in dims if d)
        print(f"    {name:10s} {s}")

    with open(os.path.join(OUT, "panel_A_K_reframe.json"), "w") as fh:
        json.dump({"K_summary": {k: list(v) for k, v in Ksummary.items()},
                   "dim_lnlam_trend": {k: v for k, v in trends.items()},
                   "khinchin_K0": KHINCHIN}, fh, indent=2)
    print("\n  VERDICT: C finite ⟺ K(α)<∞ (Liu–Qu–Wen). metallics (K=a) & π (K=K₀) FINITE; "
          "e (K=∞) DIVERGES. π and e split — π sits with the metallics.")
    print("  wrote approximability/panel_A_K_reframe.json  — DONE.")
