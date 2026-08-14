"""In-house minimum-contrast DPP / cluster fitting (BRIDGE-B, no-black-box arm).

Families per Lavancier–Møller–Rubak (2015), all with closed-form pcf
g(r) = 1 − c(r)² where c is the kernel correlation (real-kernel DPPs):
  gauss:    c(r) = exp(−(r/α)²)
  cauchy:   c(r) = (1 + (r/α)²)^(−ν−1)
  powerexp: c(r) = exp(−(r/α)^ν), 0 < ν ≤ 2
  matern:   c(r) = (2^(1−ν)/Γ(ν)) (r/α)^ν K_ν(r/α)   (Whittle–Matérn)
Clustered alternative (Thomas):  g(r) = 1 + exp(−r²/(4σ²))/(4πκσ²).
Poisson reference: g ≡ 1.

DIM=2 throughout.  Existence (declared approximation): a real-kernel DPP needs
spectral density λ·ĉ(k) ≤ 1 for all k; we enforce the k=0 bound
λ·2π∫ c(r) r dr ≤ 1 numerically.  The Ginibre kernel is COMPLEX and sits
outside every real family here — the exact reason the B1 claim is sealed
class-level, not kernel-level (brief §1 B1, tripwire 6).

Contrast (sealed): D = ∫_[0.25,5] (ĝ(r) − g_model(r))² dr, trapezoid on the
empirical grid.  Same D evaluated for our fits AND for spatstat's fitted
curves — one uniform criterion, no mixing of internal objectives.
"""

import numpy as np
from scipy.special import kv, gamma as gamma_fn
from scipy.optimize import minimize_scalar


def corr(family, r, alpha, nu):
    r = np.asarray(r, float)
    if family == "gauss":
        return np.exp(-(r / alpha) ** 2)
    if family == "cauchy":
        return (1.0 + (r / alpha) ** 2) ** (-(nu + 1.0))
    if family == "powerexp":
        return np.exp(-(r / alpha) ** nu)
    if family == "matern":
        x = np.maximum(r / alpha, 1e-12)
        return (2.0 ** (1 - nu) / gamma_fn(nu)) * x ** nu * kv(nu, x)
    raise ValueError(family)


def g_dpp(family, r, alpha, nu=1.0):
    return 1.0 - corr(family, r, alpha, nu) ** 2


def g_thomas(r, kappa, sigma):
    return 1.0 + np.exp(-np.asarray(r, float) ** 2 / (4 * sigma ** 2)) / (4 * np.pi * kappa * sigma ** 2)


def alpha_max(family, nu, lam):
    """k=0 existence bound: λ·2π∫c(r;α=1) r dr · α² ≤ 1  (c scales as r/α)."""
    rr = np.linspace(1e-4, 60.0, 40000)
    I1 = 2 * np.pi * np.trapezoid(corr(family, rr, 1.0, nu) * rr, rr)
    return np.sqrt(1.0 / (lam * I1))


def contrast(g_emp_r, g_emp, g_model_vals, lo=0.25, hi=5.0):
    m = (g_emp_r >= lo) & (g_emp_r <= hi)
    return float(np.trapezoid((g_emp[m] - g_model_vals[m]) ** 2, g_emp_r[m]))


def fit_family(family, r, g_emp, lam, lo=0.25, hi=5.0):
    """Min-contrast over α (ν on a grid where the family has a shape param)."""
    nus = {"gauss": [None], "cauchy": [0.5, 1.0, 2.0],
           "powerexp": [0.5, 1.0, 1.5, 2.0], "matern": [0.5, 1.0, 2.0]}[family]
    best = None
    for nu in nus:
        nv = 1.0 if nu is None else nu
        amax = alpha_max(family, nv, lam)
        def D_of(a):
            return contrast(r, g_emp, g_dpp(family, r, a, nv), lo, hi)
        res = minimize_scalar(D_of, bounds=(1e-3, amax), method="bounded")
        cand = dict(family=family, alpha=float(res.x), nu=(None if nu is None else nv),
                    alpha_max=float(amax), at_boundary=bool(res.x > 0.995 * amax),
                    D=float(res.fun))
        if best is None or cand["D"] < best["D"]:
            best = cand
    return best


def fit_thomas(r, g_emp, lam, lo=0.25, hi=5.0):
    best = None
    for sigma in np.geomspace(0.05, 10.0, 60):
        def D_of(k):
            return contrast(r, g_emp, g_thomas(r, k, sigma), lo, hi)
        res = minimize_scalar(D_of, bounds=(1e-4, 100.0), method="bounded")
        cand = dict(family="thomas", kappa=float(res.x), sigma=float(sigma), D=float(res.fun))
        if best is None or cand["D"] < best["D"]:
            best = cand
    return best


def r_half(family, alpha, nu):
    """Interaction range: r where the model g crosses 0.5 (inhibitory families)."""
    rr = np.linspace(1e-3, 30.0, 30000)
    gv = g_dpp(family, rr, alpha, 1.0 if nu is None else nu)
    idx = np.argmax(gv >= 0.5)
    return float(rr[idx])


def fit_all(r, g_emp, lam, lo=0.25, hi=5.0):
    out = {"poisson": dict(family="poisson", D=contrast(r, g_emp, np.ones_like(r), lo, hi))}
    for fam in ("gauss", "cauchy", "powerexp", "matern"):
        out[fam] = fit_family(fam, r, g_emp, lam, lo, hi)
        out[fam]["r_half"] = r_half(fam, out[fam]["alpha"], out[fam]["nu"])
    out["thomas"] = fit_thomas(r, g_emp, lam, lo, hi)
    dpps = {k: v for k, v in out.items() if k in ("gauss", "cauchy", "powerexp", "matern")}
    best = min(dpps.values(), key=lambda v: v["D"])
    out["best_dpp"] = best
    return out
