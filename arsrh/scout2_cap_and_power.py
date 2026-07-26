"""
SCOUT 2 (unsealed, no significance values) — three gating questions, in the order they gate.

A. PIN THE CAP IDENTITY. The scout called 2*Var[S] a "cap". The reviewer notes zeta's Sigma^2(8) at
   the top block (0.435) sits ~10% ABOVE 2*Var[S] (0.395), which a cap forbids. Algebra:
       Sigma^2(L) = Var[S(u+L) - S(u)] = 2*Var[S] - 2*Cov(S(u), S(u+L))
   so 2*Var[S] is the L->infinity LIMIT, and Sigma^2 exceeds it wherever Cov < 0. Verify numerically.

B. POWER FOR THE lnln PROGRAM. Selberg predicts a THEOREM-GRADE COEFFICIENT:
       Var[S] ~ (1/2pi^2) * lnln(T/2pi),   1/2pi^2 = 0.050661
   Measure the per-block sampling scatter of Var[S] at W=20000 so the slope's error bar is known
   BEFORE the program is proposed. Third time this arc a slow-growth law looked testable.

C. SEPARATION. Tabulate the predicted slope against competitors over the available lever arm.
"""
from __future__ import annotations
import math, os
import numpy as np
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
EULER = 0.5772156649015329
C_SELBERG = 1.0 / (2 * math.pi ** 2)


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def S_on_grid(blk, per_spacing=8):
    """S(u) = count(<=u) - u, on a uniform grid in the UNFOLDED coordinate."""
    u = exact_N(blk)
    lo, hi = u[0], u[-1]
    g = np.linspace(lo, hi, int((hi - lo) * per_spacing))
    S = np.searchsorted(u, g, side="right").astype(float) - (g - lo)
    return g, S - S.mean()


def gue(L):
    return (1 / math.pi ** 2) * (math.log(2 * math.pi * L) + EULER + 1.0)


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W = 20000

# ------------------------------------------------------------------ A
p("[A] cap or limit? Sigma^2(L) = 2Var[S] - 2Cov(S(u),S(u+L))")
blk = z[z.size - W - 1:z.size - 1]
g, S = S_on_grid(blk)
step = g[1] - g[0]
vS = float(np.var(S))
p(f"  top block, gamma_mid {blk[W//2]:.4g};  Var[S] = {vS:.5f}, 2Var[S] = {2*vS:.5f}")
p(f"  {'L':>6s} {'Sigma^2 direct':>15s} {'2VarS-2Cov':>12s} {'Cov(L)':>10s} {'vs 2VarS':>10s} {'GUE':>8s}")
for L in (0.5, 1, 2, 4, 8, 16, 32, 64):
    k = int(round(L / step))
    if k >= S.size // 2:
        continue
    cov = float(np.mean(S[:-k] * S[k:]) - S[:-k].mean() * S[k:].mean())
    direct = float(np.var(S[k:] - S[:-k]))
    p(f"  {L:>6.1f} {direct:>15.5f} {2*vS-2*cov:>12.5f} {cov:>10.5f} "
      f"{direct/(2*vS):>10.3f} {gue(L):>8.3f}")
p("  -> if column 2 == column 3 the identity holds; if 'vs 2VarS' crosses 1 in both directions,")
p("     2*Var[S] is a LIMIT that Sigma^2 oscillates about, NOT a cap.\n")

# ------------------------------------------------------------------ B
p("[B] per-block sampling scatter of Var[S] at W=20000, at effectively ONE height")
starts = [z.size - 1 - (i + 1) * W for i in range(20)][::-1]
vs, gm = [], []
for s0 in starts:
    b = z[s0:s0 + W]
    _, Sb = S_on_grid(b, per_spacing=6)
    vs.append(float(np.var(Sb))); gm.append(float(b[W // 2]))
vs = np.array(vs); gm = np.array(gm)
ll = np.log(np.log(gm / (2 * math.pi)))
p(f"  {len(vs)} disjoint blocks, gamma {gm.min():.4g}..{gm.max():.4g}, "
  f"lnln range {ll.min():.4f}..{ll.max():.4f} (span {np.ptp(ll):.4f})")
p(f"  predicted Var[S] change across THAT span: {C_SELBERG*np.ptp(ll):.5f}  (negligible => spread is scatter)")
sd = float(np.std(vs, ddof=1))
p(f"  Var[S]: mean {vs.mean():.5f}, sd {sd:.5f}, min {vs.min():.5f}, max {vs.max():.5f}")
p(f"  => per-block sigma_V = {sd:.5f}\n")

# ------------------------------------------------------------------ C
p("[C] separation over the available lever arm")
lo_i = None
for i in range(0, 200000, W):
    b = z[i:i + W]
    if math.log(b[-1] / (2 * math.pi)) / math.log(b[0] / (2 * math.pi)) < 1.05:
        lo_i = i; break
blo = z[lo_i:lo_i + W]
llo = math.log(math.log(blo[W // 2] / (2 * math.pi)))
lhi = math.log(math.log(gm.max() / (2 * math.pi)))
arm = lhi - llo
p(f"  lowest block with curvature < 1.05: zeros6[{lo_i}:{lo_i+W}], gamma_mid {blo[W//2]:.4g}")
p(f"  lever arm in lnln: {llo:.4f} .. {lhi:.4f}   span {arm:.4f}")
nb = 20
slope_err = sd * math.sqrt(2.0 / nb) / arm
p(f"  with {nb} blocks at each end: slope error ~ sigma_V*sqrt(2/n)/arm = {slope_err:.5f}")
p(f"  {'hypothesis':>28s} {'slope':>9s} {'sigma from Selberg':>20s}")
for lbl, cval in (("Selberg  1/2pi^2", C_SELBERG), ("half     1/4pi^2", 1 / (4 * math.pi ** 2)),
                  ("double   1/pi^2", 1 / math.pi ** 2), ("no growth  0", 0.0)):
    p(f"  {lbl:>28s} {cval:>9.5f} {abs(cval-C_SELBERG)/slope_err:>20.1f}")
p(f"\n  predicted total Var[S] rise across the arm: {C_SELBERG*arm:.5f}")
p(f"  against per-block scatter {sd:.5f} -> single-block contrast {C_SELBERG*arm/sd:.2f} sd,")
p(f"  {nb}-block-averaged contrast {C_SELBERG*arm/(sd*math.sqrt(2.0/nb)):.1f} sd")
