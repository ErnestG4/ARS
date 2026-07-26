"""
PHASE 10 — the cumulative deficit is an INTEGRATION ARTIFACT with a derivable coefficient.

Reviewer's derivation, verified here:
    int_0^T lnln(t/2pi) dt = T*lnln(T/2pi) - T/L - T/L^2 - 2T/L^3 - ...   (L = ln(T/2pi))
so if the LOCAL bracket is a constant K, the CUMULATIVE bracket is its running average:
    G(T) = K - 1/L - 1/L^2 - ...
Coefficient on 1/L is EXACTLY 1, by integration. The deficit is not non-convergence -- it is what a
converged local statistic looks like when integrated, and I differentiated the wrong way round.

Consequences, both computed here from RAW (the reviewer's b came from my 3-decimal table):
  [b] fit the deficit properly and test the FORM: -b/L vs linear-in-lnln vs 1/L^2.
  [L] invert exactly: if G(T) = K - b/L then
          V_local = C d/dT[ T (lnln X + G) ] = C[ lnln X + K + (1-b)/L + b/L^2 ]
      -- note BOTH correction terms; dropping (1-b)/L is what leaves a residual.
  [S] redo the slope and the invariant against that, and see whether -3.03 sem survives.
  [X] size of the correction at the extension's height.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from scipy.special import loggamma
from scipy.integrate import quad

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
C = 1.0 / (2 * math.pi ** 2)
K = 1.400967852459


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def rho(t):
    return np.log(np.asarray(t, float) / (2 * math.pi)) / (2 * math.pi)


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
u = exact_N(z)
s = np.arange(1, len(z) + 1, dtype=float) - u
a_, b_ = s[:-1], s[1:] - 1.0
I2_t = ((a_ ** 3 - b_ ** 3) / 3.0) / rho(0.5 * (z[:-1] + z[1:]))
stub = quad(lambda t: (exact_N(np.array([t]))[0]) ** 2, 0.0, float(z[0]), limit=200)[0]
cum = np.concatenate([[stub], stub + np.cumsum(I2_t)])

# ---------------------------------------------------------------- [b] the deficit, from raw
p("[b] the cumulative deficit, computed from raw at 40 heights")
idx = np.unique(np.linspace(int(0.03 * len(z)), len(z) - 2, 40).astype(int))
T = z[idx]; L = np.log(T / (2 * math.pi)); ll = np.log(L)
G = cum[idx] / (T * C) - ll
dfc = K - G                                    # positive deficit
p(f"  {'T':>11s} {'L':>7s} {'G(T)':>9s} {'K-G':>9s} {'(K-G)*L':>9s}")
for i in (0, 9, 19, 29, len(idx) - 1):
    p(f"  {T[i]:>11.4g} {L[i]:>7.3f} {G[i]:>9.5f} {dfc[i]:>9.5f} {dfc[i]*L[i]:>9.5f}")
bhat = float(np.mean(dfc * L)); bsd = float(np.std(dfc * L, ddof=1))
p(f"\n  (K-G)*L across all {len(idx)} heights: mean {bhat:.5f}, sd {bsd:.5f}, "
  f"range {np.min(dfc*L):.5f}..{np.max(dfc*L):.5f}")
p(f"  DERIVED coefficient is exactly 1 -> measured b = {bhat:.4f}, {100*(1-bhat):.1f}% below")

p("\n  FORM TEST — which functional form does the deficit follow?")
for lbl, basis in (("b/L         ", 1 / L), ("b/L^2       ", 1 / L ** 2),
                   ("b*lnln (lin)", ll), ("b (constant)", np.ones_like(L))):
    c_ = float(np.sum(dfc * basis) / np.sum(basis * basis))
    r = dfc - c_ * basis
    p(f"    {lbl}: coef {c_:>9.5f}   rms residual {np.sqrt(np.mean(r**2)):.2e}  "
      f"({100*np.sqrt(np.mean(r**2))/np.mean(dfc):.2f}% of the deficit)")
c2 = np.linalg.lstsq(np.vstack([1 / L, 1 / L ** 2]).T, dfc, rcond=None)[0]
p(f"    two-term b/L + c/L^2: b = {c2[0]:.5f}, c = {c2[1]:.5f}")

# ---------------------------------------------------------------- [L] invert, and [S] re-test
p("\n[L]+[S] invert the relation and re-test the local statistic")
p("  V_local = C[ lnln X + K + (1-b)/L + b/L^2 ]   (BOTH terms; dropping (1-b)/L leaves a residual)")
d7 = json.load(open(os.path.join(HERE, "phase7_exact_moments_measured.json")))
d8 = json.load(open(os.path.join(HERE, "phase8_invariant_measured.json")))
xc = d8["centroid_lnln"]; Lc = math.exp(xc)
Vm, Vs = d8["V_centroid"], d8["V_centroid_sem"]
slm, sls = d7["slope"], d7["slope_sem"]


def Vpred(x, b, both=True):
    Lx = math.exp(x)
    corr = b / Lx ** 2 + ((1 - b) / Lx if both else 0.0)
    return C * (x + K + corr)


def slope_pred(x, b, both=True):
    Lx = math.exp(x)
    return C * (1 - 2 * b / Lx ** 2 - ((1 - b) / Lx if both else 0.0))


p(f"\n  INVARIANT at centroid lnln={xc:.5f} (L={Lc:.3f}), measured {Vm:.6f} +/- {Vs:.6f}")
for lbl, v in (("plain C(lnln+K), no correction", C * (xc + K)),
               ("b/L^2 only (reviewer's form)", Vpred(xc, bhat, both=False)),
               ("BOTH terms, derived", Vpred(xc, bhat, both=True))):
    p(f"    {lbl:<32s} {v:.6f}   -> {(Vm-v)/Vs:+6.2f} sem")

p(f"\n  SLOPE, measured {slm:.6f} +/- {sls:.6f}")
for lbl, v in (("plain C", C),
               ("C(1 - 2b/L^2) (reviewer's form)", slope_pred(xc, bhat, both=False)),
               ("BOTH terms, derived", slope_pred(xc, bhat, both=True))):
    p(f"    {lbl:<32s} {v:.6f}   -> {(slm-v)/sls:+6.2f} sem")

# ---------------------------------------------------------------- [X] extension
p("\n[X] the correction at the extension's height")
for lbl, x in (("catalogue top", 2.493), ("gamma=1e21", 3.797), ("gamma=1e22", 3.847)):
    Lx = math.exp(x)
    corr = C * (bhat / Lx ** 2 + (1 - bhat) / Lx)
    p(f"  {lbl:>14s}: L={Lx:6.2f}  correction in V = {corr:.3e}  "
      f"= {corr/2.36e-4:5.2f} far-block sem")
p("  -> at 1e22 the correction is below noise, so the far point measures K DIRECTLY.")
p("     No `a`, no conjecture-grade import, grade cap gone.")

json.dump({"b": bhat, "b_sd": bsd, "b_two_term": c2.tolist(),
           "V_centroid_sem_from_derived": (Vm - Vpred(xc, bhat)) / Vs,
           "slope_sem_from_derived": (slm - slope_pred(xc, bhat)) / sls,
           "slope_sem_from_plainC": (slm - C) / sls},
          open(os.path.join(HERE, "phase10_measured.json"), "w"), indent=2)
p("\nwrote phase10_measured.json")
