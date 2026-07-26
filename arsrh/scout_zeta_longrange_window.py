"""
*** SUPERSEDED FRAMING — see scout2_cap_and_power.py [A]. This file calls 2*Var[S] a "cap".
    It is the L->infinity LIMIT, not a cap: Sigma^2(L) = 2Var[S] - 2Cov(S(u),S(u+L)), and Sigma^2
    EXCEEDS it wherever Cov < 0. Measured on the top block, Sigma^2/2Var[S] crosses 1 in both
    directions (0.70, 0.83, 0.97, 1.08, 1.10, 0.95, 0.86, 1.13 at L=0.5..64). There is no wall at
    L_sat. What is true: GUE grows like log L without bound while zeta oscillates about a finite
    limit, so ABOVE L_sat GUE CEASES TO BE AN ADMISSIBLE BRACKET FOR ZETA -- and the admissible
    bracket becomes Berry, which predicts the oscillation now visible in Cov(L).

SCOUT (not a phase, no seal): is ζ's long-range row actionable, or open-in-principle-only?

The three gates say ζ's long range is OPEN — θ exact, p_fit=0, no reach cap, no amplitude problem.
But every long-range reading in this arc was taken on ONE block: zeros6[:2000], γ ∈ [14, 2515], which
is the entire population at that height and 7.4× heterogeneous. The catalogue holds 2,001,052 zeros to
γ ~ 1.13e6, where blocks can be BOTH large and homogeneous.

Before proposing to point the certified instrument there, ask the feasibility question the arc's own
rule 7 demands: WHERE IS THE RMT WINDOW, as a function of height? Berry saturation bounds Σ² at 2·Var[S];
if that limit sits below GUE's Σ²(L) for all accessible L, there is no window and the row is open only in
the instrument sense.
"""
from __future__ import annotations
import math, os
import numpy as np
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
EULER = 0.5772156649015329


def sigma2(xi, Ls, step=0.25):
    xi = np.sort(xi); lo, hi = xi[0], xi[-1]; out = []
    for L in Ls:
        s = np.arange(lo, hi - L, step)
        out.append(float(np.var(np.searchsorted(xi, s + L) - np.searchsorted(xi, s))))
    return np.array(out)


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def gue(L):
    return (1 / math.pi ** 2) * (math.log(2 * math.pi * L) + EULER + 1.0)


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
Ls = np.array([0.25, 0.5, 1.0, 2.0, 4.0, 8.0])
p(f"catalogue: {z.size} zeros, γ {z[0]:.1f} .. {z[-1]:.1f}\n")
p(f"{'block':>26s} {'γ_mid':>10s} {'curv':>6s} {'Var[S]':>8s} {'2Var[S]':>8s} {'L_sat':>7s}  Σ²_θ vs GUE")

W = 20000
for lo in (0, 200000, 900000, z.size - W - 1):
    blk = z[lo:lo + W]
    gm = float(blk[W // 2])
    curv = math.log(blk[-1] / (2 * math.pi)) / math.log(blk[0] / (2 * math.pi))
    x = exact_N(blk)
    S = np.arange(1, W + 1, dtype=float) - x
    grid = np.linspace(blk[0], blk[-1], 200000)
    Su = np.searchsorted(blk, grid, side="right").astype(float) - exact_N(grid)
    vS = float(np.var(Su))
    s2 = sigma2(x, Ls)
    # L at which the GUE curve reaches the saturation cap 2*Var[S] -> the RMT window edge
    Lsat = math.exp(2 * vS * math.pi ** 2 - EULER - 1.0) / (2 * math.pi)
    p(f"  zeros6[{lo}:{lo+W}] {gm:>10.4g} {curv:>6.3f} {vS:>8.4f} {2*vS:>8.4f} {Lsat:>7.2f}")
    p(f"{'':26s} {'Σ²_θ':>10s} " + " ".join(f"{v:>7.3f}" for v in s2))
    p(f"{'':26s} {'GUE':>10s} " + " ".join(f"{gue(L):>7.3f}" for L in Ls))
    p(f"{'':26s} {'ratio':>10s} " + " ".join(f"{v/gue(L):>7.3f}" for v, L in zip(s2, Ls)))
    p("")

p("READING: L_sat is the L at which GUE's Σ² reaches ζ's saturation cap 2·Var[S].")
p("  Above it, ζ CANNOT track GUE regardless of instrument quality — the cap is physics, not method.")
p("  Var[S] ~ (1/2π²)·lnln(γ/2π) grows like lnln, so L_sat grows like exp(lnln) = ln(γ/2π):")
for g in (1e3, 1e6, 1e12, 1e30):
    v = (1 / (2 * math.pi ** 2)) * math.log(math.log(g / (2 * math.pi)))
    p(f"    γ=1e{int(math.log10(g)):<3d} -> Var[S]~{v:.3f}, cap {2*v:.3f}, "
      f"L_sat ~ {math.exp(2*v*math.pi**2 - EULER - 1.0)/(2*math.pi):.2f}")
