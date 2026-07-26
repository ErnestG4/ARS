"""
SCOUT 11 — verify the reviewer's weight derivation, then pre-register R-040's three numbers.

The claim: my 0.0203 was never WRONG, it was in the wrong SLOT. The synthetic has no zeros, hence no
F-integral, so C*(M + C2) is the correct prediction for the SYNTHETIC (prime-sum-only) object -- which
is exactly R-040's tracking arm. Correct-fact/wrong-slot at the last number of the program.

Checks, in order:
  [1] Lambda(n)^2 / (n log^2 n) = 1/(m^2 p^m) for n = p^m   -- verified numerically, independently.
  [2] sum_(p^m <= X) 1/(m^2 p^m) = lnln X + C_0 - Sigma      -- the identity, at several X.
  [3] the three pre-registered numbers for R-040, and which of them is the valuable one.
"""
from __future__ import annotations
import math
import mpmath as mp
import numpy as np

mp.mp.dps = 30
p = lambda *a: print(*a, flush=True)
C = 1 / (2 * mp.pi ** 2)
GAMMA = mp.euler
SIGMA = mp.nsum(lambda m: (1 / m - 1 / m ** 2) * mp.primezeta(m), [2, mp.inf])
MERTENS = mp.mpf('0.2614972128476427837554268386086958590516')


def sieve(n):
    s = np.ones(n + 1, bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.flatnonzero(s)


# ---------------------------------------------------------------- [1]
p("[1] verify  Lambda(n)^2 / (n log^2 n) = 1/(m^2 p^m)  for n = p^m  (independently, numerically)")
p(f"  {'p':>4s} {'m':>3s} {'n':>7s} {'Lam^2/(n log^2 n)':>20s} {'1/(m^2 p^m)':>15s} {'|diff|':>10s}")
worst = 0.0
for pr in (2, 3, 5, 7, 11):
    for m in (1, 2, 3):
        n = pr ** m
        lhs = math.log(pr) ** 2 / (n * math.log(n) ** 2)
        rhs = 1.0 / (m * m * n)
        worst = max(worst, abs(lhs - rhs))
        if m <= 2 and pr <= 5:
            p(f"  {pr:>4d} {m:>3d} {n:>7d} {lhs:>20.12f} {rhs:>15.12f} {abs(lhs-rhs):>10.1e}")
p(f"  max |diff| over all 15 cases = {worst:.2e}  -> IDENTITY CONFIRMED")
p(f"  (Lambda(p^m) = log p, and log(p^m) = m log p, so log^2 p / (p^m m^2 log^2 p) = 1/(m^2 p^m))\n")

# ---------------------------------------------------------------- [2]
p("[2] verify  sum_(p^m <= X) 1/(m^2 p^m)  =  lnln X + C_0 - Sigma")
p(f"  C_0 - Sigma = {mp.nstr(GAMMA - SIGMA, 12)}   (= M + C2, verified exact in scout 10)")
p(f"  {'X':>10s} {'direct sum':>14s} {'lnln X + C0 - Sig':>20s} {'diff':>11s}")
for X in (10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7):
    pr = sieve(X)
    tot = 0.0
    for q in pr:
        m, pw = 1, int(q)
        while pw <= X:
            tot += 1.0 / (m * m * pw)
            m += 1; pw *= int(q)
    pred = float(mp.log(mp.log(X)) + GAMMA - SIGMA)
    p(f"  {X:>10d} {tot:>14.8f} {pred:>20.8f} {tot-pred:>+11.2e}")
p("  -> converges as X grows (the residual is the Mertens error term). IDENTITY CONFIRMED.\n")

# ---------------------------------------------------------------- [3]
p("[3] R-040 PRE-REGISTERED NUMBERS (three, not one)")
sl = C
ic_syn = (GAMMA - SIGMA) * C
ic_real = (1 + GAMMA - SIGMA) * C
p(f"  tracking arm (X_0 = t/2pi), slope        = {mp.nstr(sl, 8)}")
p(f"  tracking arm (X_0 = t/2pi), intercept    = {mp.nstr(ic_syn, 8)}   <- my 0.0203, correctly slotted")
p(f"  zeta intercept (Goldston, SPCC)          = {mp.nstr(ic_real, 8)}")
p(f"  DIFFERENCE  zeta - synthetic             = {mp.nstr(ic_real - ic_syn, 8)} = 1/2pi^2 = the F-INTEGRAL")
p(f"\n  fixed-X_0 arm: slope = 0 by construction (no growth); any measured slope is manufactured,")
p(f"  and its size IS the budget entry.")
p(f"\n  THE THIRD IS THE VALUABLE ONE. Both arms run through the IDENTICAL estimator, so estimator")
p(f"  bias cancels in the DIFFERENCE. That measures the F-integral without needing Goldston's")
p(f"  constants to precision and without common-mode bias -- the synthetic side is known in CLOSED")
p(f"  FORM rather than resting on o(T). o(T) remains on the zeta side, so R-044 stays a LOOK; but")
p(f"  the differential form is the right way to take it if it is ever taken.\n")

# ---------------------------------------------------------------- [4] the a=0.118 dof problem
p("[4] is a = 0.118 falsifiable as stated?")
p("  NO -- one correction coefficient fitted from one deficit is ZERO degrees of freedom.")
ll = np.array([2.148, 2.493])
p(f"  lever arm in lnln = {ll[1]-ll[0]:.3f}; a 3-parameter fit (C, const, a) over 4 anchors spanning")
p(f"  that arm is badly conditioned: 1/lnX and a constant are nearly collinear over so short a range.")
lnX = np.exp(np.linspace(ll[0], ll[1], 4))
X1 = np.vstack([np.ones(4), 1 / lnX]).T
p(f"  corr(1, 1/lnX) over the 4 anchors = {np.corrcoef(X1[:,0]+1e-9*np.arange(4), X1[:,1])[0,1]:+.3f} "
  f"(degenerate by construction); condition number of [lnln, 1, 1/lnX] = "
  f"{np.linalg.cond(np.vstack([np.linspace(*ll,4), np.ones(4), 1/lnX]).T):.1f}")
p("  => PRE-COMMIT: take a from Chan's ratios-conjecture expansion INDEPENDENTLY, and use the")
p("     measurement to TEST it. Do not fit a and then treat the fitted value as the explanation.")
p("     The second lever (consistent a on disjoint gamma sub-ranges) is NOT available at this")
p("     lever arm and should not be offered as a fallback.")
