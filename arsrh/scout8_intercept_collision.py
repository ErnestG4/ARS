"""
SCOUT 8 (unsealed) — the intercept has been attributed to two different single causes and both
attributions are mine. 0.0738 was filed as (a) the finite-block DEMEAN BIAS, which justified sealing
on the coefficient, and later as (b) the n<=16 PRIME CONTRIBUTION at 101.5%. They sum to ~0.15
against a measured 0.0738, so at most one can hold and possibly neither.

THE DISCRIMINATOR IS FREE AND SEPARATES THEM BY SCALING:
    demean bias      -> depends on BLOCK LENGTH W       (longer block removes less)
    prime constant   -> invariant to W and to sampling
    sawtooth of S    -> depends on SAMPLING RESOLUTION  (S falls linearly then jumps by 1)

So: sweep W at fixed resolution, and sweep resolution at fixed W, fitting Var[S] vs lnln at four
heights in each cell. Whatever moves the INTERCEPT identifies it. And whatever the intercept is,
the load-bearing question for the program is whether the SLOPE is stable, since that is what the
coefficient seal rests on.
"""
from __future__ import annotations
import math, os
import numpy as np
from scipy.special import loggamma

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = lambda *a: print(*a, flush=True)
C_SEL = 1.0 / (2 * math.pi ** 2)


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))


def varS(b, per_spacing):
    u = exact_N(b); u = u - u[0]
    g = np.linspace(0.0, u[-1], max(16, int(u[-1] * per_spacing)))
    S = np.searchsorted(u, g, side="right").astype(float) - g
    return float(np.var(S - S.mean())), math.log(math.log(float(b[len(b) // 2]) / (2 * math.pi)))


ANCHORS = [60000, 300000, 900000, 1900000]     # start indices spanning the lever arm
NBLK = 6


def cell(W, ps):
    lls, vs = [], []
    for a in ANCHORS:
        for i in range(NBLK):
            s0 = a + i * W
            if s0 + W >= z.size:
                continue
            v, ll = varS(z[s0:s0 + W], ps)
            vs.append(v); lls.append(ll)
    sl, ic = np.polyfit(lls, vs, 1)
    return sl, ic, len(vs)


p("[A] BLOCK-LENGTH sweep at fixed sampling (8 pts / mean spacing)")
p(f"  {'W':>7s} {'slope':>9s} {'intercept':>11s} {'n':>4s}   demean bias would scale WITH W")
prev = None
for W in (2500, 5000, 10000, 20000, 40000):
    sl, ic, n = cell(W, 8)
    p(f"  {W:>7d} {sl:>9.5f} {ic:>11.5f} {n:>4d}" + ("" if prev is None else f"   d_ic = {ic-prev:+.5f}"))
    prev = ic
p(f"  Selberg slope for reference: {C_SEL:.5f}\n")

p("[B] SAMPLING-RESOLUTION sweep at fixed W=20000")
p(f"  {'pts/spacing':>12s} {'slope':>9s} {'intercept':>11s}   sawtooth would scale WITH resolution")
for ps in (1, 2, 4, 8, 16, 32):
    sl, ic, n = cell(20000, ps)
    p(f"  {ps:>12d} {sl:>9.5f} {ic:>11.5f}")

p("\n[C] verdict")
sl_w = [cell(W, 8)[0] for W in (2500, 5000, 10000, 20000, 40000)]
ic_w = [cell(W, 8)[1] for W in (2500, 5000, 10000, 20000, 40000)]
sl_r = [cell(20000, ps)[0] for ps in (1, 2, 4, 8, 16, 32)]
ic_r = [cell(20000, ps)[1] for ps in (1, 2, 4, 8, 16, 32)]
p(f"  slope     across W  : {min(sl_w):.5f} .. {max(sl_w):.5f}  (spread {100*(max(sl_w)-min(sl_w))/np.mean(sl_w):.1f}%)")
p(f"  slope     across res: {min(sl_r):.5f} .. {max(sl_r):.5f}  (spread {100*(max(sl_r)-min(sl_r))/np.mean(sl_r):.1f}%)")
p(f"  intercept across W  : {min(ic_w):.5f} .. {max(ic_w):.5f}")
p(f"  intercept across res: {min(ic_r):.5f} .. {max(ic_r):.5f}")
p(f"\n  theory: C*(Mertens + sum_p sum_(k>=2) 1/(k^2 p^k)) is the ONLY intercept the prime sum allows.")
c2 = 0.0
for q in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    c2 += sum(1.0 / (k * k * q ** k) for k in range(2, 40))
p(f"    Mertens M = 0.26150, C2 = {c2:.5f} -> predicted intercept = {C_SEL*(0.26150+c2):.5f}")
p(f"    uniform-sawtooth variance 1/12 = {1/12:.5f} (a SAMPLING term, not a prime term)")
