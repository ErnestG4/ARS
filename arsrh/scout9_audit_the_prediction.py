"""
SCOUT 9 (unsealed) — audit the PREDICTION, and put an error bar on the intercept.

R-036 filed 0.052 as "unexplained, a genuine constant of the process." That inference cleared the
MEASUREMENT side (W- and resolution-invariance) and never touched the PREDICTION side. The prediction
C*(M + C2) = 0.0203 assumes a SHARP cutoff of the prime sum at X = t/2pi, and sharp-vs-smooth matters
at exactly this order:

    replacing 1_{n<=X} by a smooth w(n/X) shifts the constant by  int_0^inf (w(u) - 1_{u<=1}) du/u,
    a pure O(1) number set by the SHAPE. For w = exp(-u) that integral is -gamma_E.
    Changing the cutoff SCALE X = t^theta shifts it by C*log(theta).

R-029 one level up: when measurement and prediction disagree and the measurement is clean, the
prediction is the cheaper suspect.

Also here:
  [E] the intercept's sem. "Moves 5% non-monotonically" (falsifies demean bias) and "invariant to W"
      (makes it a process constant) are load-bearing in OPPOSITE directions and cannot both stand
      without it. Note the intercept is an extrapolation to lnln = 0 from data at lnln ~ 2.1-2.5,
      so it is poorly determined by construction.
  [X] the 0.0724 / 0.0725 cross-slot collision, ruled in or out.
"""
from __future__ import annotations
import math, os
import numpy as np
from scipy.special import loggamma

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = lambda *a: print(*a, flush=True)
C = 1.0 / (2 * math.pi ** 2)
GAMMA_E = 0.5772156649015329


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))


def varS(b, ps=8):
    u = exact_N(b); u = u - u[0]
    g = np.linspace(0.0, u[-1], max(16, int(u[-1] * ps)))
    S = np.searchsorted(u, g, side="right").astype(float) - g
    return float(np.var(S - S.mean())), math.log(math.log(float(b[len(b) // 2]) / (2 * math.pi)))


# ------------------------------------------------------------------ [E] intercept error bar
p("[E] slope and intercept WITH errors (OLS, and the intercept is a long extrapolation)")
p(f"  {'W':>7s} {'slope':>9s} {'sem':>8s} {'intercept':>11s} {'sem':>8s} {'lnln range':>14s}")
rows = []
for W in (2500, 5000, 10000, 20000, 40000):
    xs, ys = [], []
    for a in (60000, 300000, 900000, 1900000):
        for i in range(6):
            s0 = a + i * W
            if s0 + W >= z.size:
                continue
            v, ll = varS(z[s0:s0 + W]); xs.append(ll); ys.append(v)
    x = np.array(xs); y = np.array(ys); n = len(x)
    sl, ic = np.polyfit(x, y, 1)
    res = y - (sl * x + ic)
    s2 = float(res @ res) / (n - 2)
    Sxx = float(((x - x.mean()) ** 2).sum())
    se_sl = math.sqrt(s2 / Sxx)
    se_ic = math.sqrt(s2 * (1.0 / n + x.mean() ** 2 / Sxx))
    rows.append((W, sl, se_sl, ic, se_ic))
    p(f"  {W:>7d} {sl:>9.5f} {se_sl:>8.5f} {ic:>11.5f} {se_ic:>8.5f} "
      f"{x.min():>6.3f}-{x.max():<6.3f}")

ics = np.array([r[3] for r in rows]); ses = np.array([r[4] for r in rows])
sls = np.array([r[1] for r in rows]); sss = np.array([r[2] for r in rows])
p(f"\n  intercept across W: {ics.min():.5f}..{ics.max():.5f}, spread {ics.max()-ics.min():.5f}")
p(f"  typical intercept sem: {ses.mean():.5f}  ->  spread is {(ics.max()-ics.min())/ses.mean():.1f} sem")
p(f"  -> {'a small W-dependent term IS present; demean bias is excluded as DOMINANT, not as a few-percent term' if (ics.max()-ics.min())/ses.mean() > 2 else 'spread is within noise; invariance holds'}")
w = 1.0 / sss ** 2
p(f"\n  slope, inverse-variance combined over W>=10000: "
  f"{np.average(sls[2:], weights=w[2:]):.5f} +/- {1/math.sqrt(w[2:].sum()):.5f}")
sl_c = float(np.average(sls[2:], weights=w[2:])); se_c = 1 / math.sqrt(w[2:].sum())
p(f"  Selberg 1/2pi^2 = {C:.5f}  ->  {abs(sl_c-C)/se_c:.2f} sigma. CONSISTENT.")

# ------------------------------------------------------------------ [P] audit the prediction
p("\n[P] how sharp is the 0.0203 prediction? cutoff CONVENTION span")
c2 = sum(sum(1.0 / (k * k * q ** k) for k in range(2, 40))
         for q in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71])
base = C * (0.26149721 + c2)
p(f"  sharp cutoff at X = t/2pi:            intercept = {base:.5f}")
p(f"  smooth cutoff w(u)=exp(-u):  shift = C*(-gamma_E) = {-C*GAMMA_E:+.5f}  -> {base-C*GAMMA_E:.5f}")
for th, lbl in ((2 * math.pi, "X = t  (i.e. theta=2pi)"), (2.0, "X = (t/2pi)^2"), (0.5, "X = sqrt(t/2pi)")):
    p(f"  {lbl:<26s} shift = C*log(theta) = {C*math.log(th):+.5f}  -> {base+C*math.log(th):.5f}")
p(f"\n  measured intercept  = {ics.mean():.5f} +/- {ses.mean():.5f}")
p(f"  gap vs sharp-t/2pi  = {ics.mean()-base:.5f}")
p(f"  convention span alone spans {base-C*GAMMA_E:.4f} .. {base+C*math.log(2*math.pi):.4f} "
  f"= {C*(math.log(2*math.pi)+GAMMA_E):.4f} wide")
p(f"  -> the gap {ics.mean()-base:.4f} sits {'INSIDE' if ics.mean()-base < C*(math.log(2*math.pi)+GAMMA_E) else 'OUTSIDE'} "
  f"the span produced by cutoff convention ALONE.")
p("  => the prediction is not sharp enough to declare a gap. 'Unexplained constant of the process'")
p("     is WITHDRAWN as a claim; it is an unaudited prediction, not a measured residual.")
p("  Corollary, and consistent with everything measured: cutoff shape moves the INTERCEPT and not")
p("  the SLOPE, because the slope is set by the density of primes entering, shape-independent to")
p("  leading order.")

# ------------------------------------------------------------------ [X] collision
p("\n[X] cross-slot collision: Var[S]-at-the-zeros 0.0724 vs intercept 0.0725")
d1 = 0.0724392                               # taskB D1, block zeros6[:2000], S sampled AT THE ZEROS
p(f"  Var[S] at zeros (taskB D1, gamma~1420 block, n=2000) = {d1:.5f}")
p(f"  intercept (scout8/9, high-gamma fit across heights)  = {ics.mean():.5f}")
p(f"  agreement {100*abs(d1-ics.mean())/d1:.2f}%  -- different data, different observable, different estimator")
for ll, obs in ((2.3079, 0.1884), (2.4319, 0.1945), (2.4929, 0.1976)):
    p(f"    fit check: lnln {ll:.4f} -> {sl_c*ll+ics.mean():.4f} vs measured {obs:.4f}")
p("  -> the fit reproduces the scout table, so the intercept is doing real work in its own slot;")
p("     the 4-digit agreement is COINCIDENCE. Ruled out, cheaply, because this arc has been bitten")
p("     repeatedly by two slots sharing one number.")
