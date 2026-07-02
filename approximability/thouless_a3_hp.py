"""(1) a_3 deficit — high-precision (mpmath eigsy, integer matrices, dps=30).
Integer lambda => Hp,Ha are integer matrices => eigenvalues good to ~28 digits.
Total bandwidth W = sum of band widths = alternating readout of sorted(per U antiper) edges.
Report W3/W2 to 20 digits; resolve whether the a_3=1 step is an exact identity or a real deficit.

Nuance (recorded): BIST forbids a preserving TAIL (golden), not a single ISOLATED a=1 step.
So exact preservation at the a_3 step would be an anomaly worth chasing, NOT a BIST violation.
"""
import sys, time, mpmath as mp
mp.mp.dps = 30
sys.path.insert(0, ".")
import numpy as np
from task1_pi_depth5 import potential, cf_frac, convergents

cf = cf_frac(mp.pi, 6); ps, qs = convergents(cf)
LAMS = [8.0, 24.0, 32.0]

def mpmat(V, sign):
    q = len(V); M = mp.zeros(q, q)
    for i in range(q): M[i, i] = mp.mpf(int(round(V[i])))
    for i in range(q - 1): M[i, i + 1] = 1; M[i + 1, i] = 1
    M[0, q - 1] = sign; M[q - 1, 0] = sign
    return M

def total_width_hp(p, q, lam):
    V = potential(p, q, lam)
    Ep, _ = mp.eigsy(mpmat(V, 1))
    Ea, _ = mp.eigsy(mpmat(V, -1))
    e = sorted(list(Ep) + list(Ea))
    W = mp.mpf(0)
    for j in range(q):
        W += e[2 * j + 1] - e[2 * j]
    return W

res = {}
for lam in LAMS:
    t = time.time()
    W2 = total_width_hp(ps[1], qs[1], lam)   # q=106
    W3 = total_width_hp(ps[2], qs[2], lam)   # q=113
    ratio = W3 / W2
    deficit = 1 - ratio
    res[lam] = (W2, W3, ratio, deficit)
    print(f"lam={lam:.0f}  ({time.time()-t:.0f}s)")
    print(f"  W2(q=106) = {mp.nstr(W2,22)}")
    print(f"  W3(q=113) = {mp.nstr(W3,22)}")
    print(f"  W3/W2     = {mp.nstr(ratio,22)}")
    print(f"  deficit 1-W3/W2 = {mp.nstr(deficit,8)}   (sign>0 => W shrank; <0 => grew)")
    sys.stdout.flush()

# scaling probe: is |deficit| ~ (q0/q2)^p * f(lam)?  q0/q2 = 7/113 (older-block fraction)
frac = mp.mpf(7)/113
print(f"\nolder-block fraction q0/q2 = 7/113 = {float(frac):.5f}")
print("if deficit ~ frac^p:  p = log|deficit|/log(frac)")
for lam in LAMS:
    d = abs(res[lam][3])
    if d > 0:
        p = mp.log(d)/mp.log(frac)
        print(f"  lam={lam:.0f}: |deficit|={mp.nstr(d,6)}  -> implied p={mp.nstr(p,5)}")
print("\n(one a=1 step in pi => single deficit per lam; the p-exponent proper comes from golden's many a=1 steps)")
print("HP_DONE")
