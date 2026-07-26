"""
PHASE 7 — delete the sampling step. Exact moments of S, no grid.

Reviewer's move: on (gamma_j, gamma_{j+1}), N(t) = j exactly, so S = j - N_smooth(t) is smooth with
known breakpoints. In the UNFOLDED variable u = N_smooth(t) it is better than smooth -- it is LINEAR:
S(u) = j - u. So with s_j = j - u_j (all O(1), numerically stable):

    interval length      = 1 - s_{j+1} + s_j
    integral of S^k du   = sum_j [ s_j^(k+1) - (s_{j+1} - 1)^(k+1) ] / (k+1)

EXACT, O(W), no grid, no resolution parameter, no aliasing, and no height-dependent effective cutoff.
The mechanism the cutoff gate was built to detect lives entirely in the sampling step; removing the
step removes the mechanism. (And no theta^2 quadrature is needed -- working in u the integrand is a
cubic.)

Third instance this arc of "the right estimator beats a test for the wrong one's failure":
count-deficit over smoothed drift; raw-t coordinate over rescaled; exact integration over sampled.

Also tested: the reviewer's sawtooth model for the kurtosis contamination --
    S = Gaussian + independent bounded sawtooth (var 1/12, kurtosis 1.8)
    kurt(V) = [3*sigG^4 + 6*sigG^2/12 + 1.8/144] / V^2,   sigG^2 = V - 1/12
predicting kurt = 2.712 at V = 0.170 and 2.788 at V = 0.198, i.e. a DRIFT of +0.076 across the arm.
The drift is the test; the point estimate is more agreement than the model has earned.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
C = 1.0 / (2 * math.pi ** 2)


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def exact_moments(g):
    """Exact u-averaged central moments 1..4 of S, with NO sampling grid."""
    u = exact_N(g); u = u - u[0]                           # NORMALISE: else s ~ 1e6 and the
    s = np.arange(1, len(g) + 1, dtype=float) - u          # fifth powers lose all precision
    a = s[:-1]                                             # value at left end of interval j
    b = s[1:] - 1.0                                        # value at right end
    L = a - b                                              # interval length = 1 - s_{j+1} + s_j
    U = float(L.sum())
    raw = [float(((a ** k - b ** k) / k).sum()) / U for k in (2, 3, 4, 5)]  # <S>,<S^2>,<S^3>,<S^4>
    m1, m2, m3, m4 = raw
    v = m2 - m1 ** 2
    c3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3
    c4 = m4 - 4 * m1 * m3 + 6 * m1 ** 2 * m2 - 3 * m1 ** 4
    return v, c3 / v ** 1.5, c4 / v ** 2, U


def sampled_var(g, ps=8):
    """The OLD estimator, for comparison only."""
    u = exact_N(g); u = u - u[0]
    grid = np.linspace(0.0, u[-1], max(16, int(u[-1] * ps)))
    S = np.searchsorted(u, grid, side="right").astype(float) - grid
    return float(np.var(S - S.mean()))


def kurt_model(V):
    sg = V - 1.0 / 12.0
    return (3 * sg ** 2 + 6 * sg / 12.0 + 1.8 / 144.0) / V ** 2


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W, NBLK = 20000, 5
ANCHORS = [40000, 300000, 900000, 1900000]

p("=== PHASE 7 — exact moments, no grid ===\n")
rows = []
for a in ANCHORS:
    for k in range(NBLK):
        s0 = a + k * W
        if s0 + W >= z.size:
            continue
        b = z[s0:s0 + W]
        v, sk, ku, U = exact_moments(b)
        gm = float(b[W // 2]); ll = math.log(math.log(gm / (2 * math.pi)))
        rows.append((ll, v, sk, ku, gm, sampled_var(b)))

x = np.array([r[0] for r in rows]); y = np.array([r[1] for r in rows]); n = len(x)
sl, ic = np.polyfit(x, y, 1)
res = y - (sl * x + ic); s2 = float(res @ res) / (n - 2)
Sxx = float(((x - x.mean()) ** 2).sum())
se_sl = math.sqrt(s2 / Sxx); se_ic = math.sqrt(s2 * (1 / n + x.mean() ** 2 / Sxx))

p("[1] EXACT vs SAMPLED estimator")
d = np.array([r[1] - r[5] for r in rows])
p(f"  Var[S]: exact - sampled, mean {d.mean():+.6f}, sd {d.std(ddof=1):.6f}, max|.| {np.abs(d).max():.6f}")
p(f"  -> the sampling step was biasing Var[S] by {abs(d.mean()):.5f} "
  f"({100*abs(d.mean())/y.mean():.2f}%), constant-ish across height\n")

p(f"[2] THE PROGRAM'S NUMBERS, exact estimator, W={W}, n={n}")
p(f"  slope     = {sl:.6f} +/- {se_sl:.6f}   (Selberg 1/2pi^2 = {C:.6f})")
p(f"  intercept = {ic:.6f} +/- {se_ic:.6f}")
p(f"  slope vs Selberg: {(sl-C)/se_sl:+.2f} sem")
gold = (1 + float(np.euler_gamma) - 0.1762478124) * C
p(f"  intercept vs Goldston {gold:.6f}: {(ic-gold)/se_ic:+.2f} sem")
p(f"  F-integral implied = {(ic - C*(float(np.euler_gamma)-0.1762478124))/C:.4f} "
  f"+/- {se_ic/C:.4f}   (SPCC predicts 1)")

p(f"\n[3] NORMALITY — exact, and against the sawtooth model")
sk = np.array([r[2] for r in rows]); ku = np.array([r[3] for r in rows])
p(f"  skewness: {sk.mean():+.5f} +/- {sk.std(ddof=1)/math.sqrt(n):.5f}   (Selberg: 0)")
p(f"  kurtosis: {ku.mean():+.5f} +/- {ku.std(ddof=1)/math.sqrt(n):.5f}   (Gaussian: 3)")
lo, hi = y.min(), y.max()
p(f"\n  sawtooth model kurt(V) = [3 sigG^4 + 6 sigG^2/12 + 1.8/144]/V^2, sigG^2 = V - 1/12:")
p(f"    at V={lo:.4f} -> {kurt_model(lo):.4f} ;  at V={hi:.4f} -> {kurt_model(hi):.4f}")
p(f"    predicted DRIFT across the arm = {kurt_model(hi)-kurt_model(lo):+.4f}")
sl_k, ic_k = np.polyfit(y, ku, 1)
resk = ku - (sl_k * y + ic_k); s2k = float(resk @ resk) / (n - 2)
Syy = float(((y - y.mean()) ** 2).sum())
se_slk = math.sqrt(s2k / Syy)
meas_drift = sl_k * (hi - lo)
p(f"    MEASURED drift  = {meas_drift:+.4f} +/- {se_slk*(hi-lo):.4f}   "
  f"({meas_drift/(se_slk*(hi-lo)):.1f} sem from zero)")
pred_drift = kurt_model(hi) - kurt_model(lo)
p(f"    measured vs predicted: {(meas_drift-pred_drift)/(se_slk*(hi-lo)):+.2f} sem")
p(f"  point estimate: measured {ku.mean():.4f} vs model at mean V={y.mean():.4f} -> "
  f"{kurt_model(y.mean()):.4f}  ({100*abs(ku.mean()-kurt_model(y.mean()))/kurt_model(y.mean()):.2f}%)")

json.dump({"slope": sl, "slope_sem": se_sl, "intercept": ic, "intercept_sem": se_ic, "n": n,
           "selberg": C, "goldston": gold,
           "F_integral": (ic - C * (float(np.euler_gamma) - 0.1762478124)) / C,
           "F_integral_sem": se_ic / C,
           "skew": float(sk.mean()), "skew_sem": float(sk.std(ddof=1) / math.sqrt(n)),
           "kurt": float(ku.mean()), "kurt_sem": float(ku.std(ddof=1) / math.sqrt(n)),
           "kurt_drift_measured": meas_drift, "kurt_drift_predicted": pred_drift,
           "exact_minus_sampled_var": float(d.mean())},
          open(os.path.join(HERE, "phase7_exact_moments_measured.json"), "w"), indent=2)
p("\nwrote phase7_exact_moments_measured.json")
