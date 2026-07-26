"""
PHASE 8 — the invariant combination, and pre-registration for the lever-arm extension.

[I] WHAT IS ACTUALLY MEASURED. slope and intercept have corr = -0.9991, so neither is believable
    alone; the combination they jointly determine is. For an OLS line the fitted value AT THE
    CENTROID x-bar has variance s^2/n and is UNCORRELATED with the slope. That is the transferable
    quantity: it survives into a 3-parameter fit without re-litigation.

[P] POWER OF THE EXTENSION, before fetching anything. sigma_V at W=1e4 measured directly (not scaled),
    then the covariance of a 3-parameter WLS fit [lnln, 1, 1/lnX] with the far point added -- does `a`
    become determined, and by how much?

[X] PRE-REGISTERED far-point predictions, both models, computed BEFORE the tables are touched:
    a = 0.140 was FITTED from these data to absorb the misfit, so a fitted `a` near 0.140 after the
    extension is NOT confirmation -- the same data would be driving both. The test is whether the far
    point lands where the 2-parameter fit says it will not, by the amount the 3-parameter model says
    it will.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
C = 1.0 / (2 * math.pi ** 2)
K_GOLD = 1.400967852459          # F(=1 under SPCC) + C_0 - Sigma


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def exact_var(g):
    u = exact_N(g); u = u - u[0]
    s = np.arange(1, len(g) + 1, dtype=float) - u
    a, b = s[:-1], s[1:] - 1.0
    U = float((a - b).sum())
    m1 = float(((a ** 2 - b ** 2) / 2).sum()) / U
    m2 = float(((a ** 3 - b ** 3) / 3).sum()) / U
    return m2 - m1 ** 2


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))

# ------------------------------------------------------------------ [I]
p("[I] the invariant combination — what the run actually measured")
W, ANCH = 20000, [40000, 300000, 900000, 1900000]
xs, ys = [], []
for a0 in ANCH:
    for k in range(5):
        s0 = a0 + k * W
        if s0 + W < z.size:
            b = z[s0:s0 + W]
            xs.append(math.log(math.log(float(b[W // 2]) / (2 * math.pi))))
            ys.append(exact_var(b))
x = np.array(xs); y = np.array(ys); n = len(x)
sl, ic = np.polyfit(x, y, 1)
res = y - (sl * x + ic); s = math.sqrt(float(res @ res) / (n - 2))
Sxx = float(((x - x.mean()) ** 2).sum())
p(f"  centroid  lnln = {x.mean():.5f}")
p(f"  V(centroid) = {y.mean():.6f} +/- {s/math.sqrt(n):.6f}   <- var = s^2/n, uncorrelated with slope")
p(f"  slope       = {sl:.6f} +/- {math.sqrt(s*s/Sxx):.6f}")
p(f"  intercept   = {ic:.6f} +/- {math.sqrt(s*s*(1/n + x.mean()**2/Sxx)):.6f}")
p(f"  => the centroid value is {math.sqrt(s*s*(1/n+x.mean()**2/Sxx))/(s/math.sqrt(n)):.0f}x tighter than "
  f"the intercept. THAT is the transferable number.")
p(f"  reference at the centroid: C*lnln + C*K_Goldston = "
  f"{C*x.mean() + C*K_GOLD:.6f}  -> measured is {(y.mean()-(C*x.mean()+C*K_GOLD))/(s/math.sqrt(n)):+.2f} sem")

# ------------------------------------------------------------------ [P]
p("\n[P] far-point precision, MEASURED not scaled")
sig = {}
for Wf in (10000, 20000):
    v = [exact_var(z[1500000 + i * Wf:1500000 + (i + 1) * Wf]) for i in range(12)]
    sig[Wf] = float(np.std(v, ddof=1))
    p(f"  sigma_V at W={Wf:6d}: {sig[Wf]:.6f}   (12 disjoint blocks, same height)")
p(f"  ratio = {sig[10000]/sig[20000]:.2f}  (sqrt(2) = 1.41 if 1/sqrt(W))")

p("\n  3-parameter WLS [lnln, 1, 1/lnX] with the far point(s) added:")
X_near = np.vstack([x, np.ones(n), 1 / np.exp(x)]).T
s_near = np.full(n, s)


def fit_err(far_lnln, far_sig):
    Xf = np.vstack([np.array(far_lnln), np.ones(len(far_lnln)),
                    1 / np.exp(np.array(far_lnln))]).T
    Xa = np.vstack([X_near, Xf])
    sa = np.concatenate([s_near, np.array(far_sig)])
    Wm = np.diag(1 / sa ** 2)
    cov = np.linalg.inv(Xa.T @ Wm @ Xa)
    return math.sqrt(cov[0, 0]), math.sqrt(cov[2, 2]), np.linalg.cond(Xa)


e0 = np.linalg.cond(X_near)
p(f"  near data alone: cond = {e0:.0f}  (rank-deficient in practice)")
for lbl, ll, sg in (("one block at 1e22 (W=1e4)", [3.847], [sig[10000]]),
                    ("both 1e21 and 1e22", [3.797, 3.847], [sig[10000]] * 2)):
    eC, ea, cond = fit_err(ll, sg)
    p(f"  + {lbl:26s}: cond {cond:7.1f}   sigma(C) {eC:.6f}   sigma(a') {ea:.6f}"
      f"   sigma(a) {ea/C:.3f}")

# ------------------------------------------------------------------ [X]
p("\n[X] PRE-REGISTERED far-point predictions (computed BEFORE any table is fetched)")
a_fit = (C - sl) / C * math.exp(x.mean())
p(f"  a fitted from THESE data (absorbs the misfit) = {a_fit:.3f}")
p(f"  {'target':>12s} {'lnln':>7s} {'2-param extrap':>15s} {'3-param (C,K,a)':>17s} {'difference':>12s}")
for lbl, ll in (("gamma=1e21", 3.797), ("gamma=1e22", 3.847)):
    v2 = sl * ll + ic
    v3 = C * ll + C * K_GOLD + C * a_fit / math.exp(ll)
    p(f"  {lbl:>12s} {ll:>7.3f} {v2:>15.6f} {v3:>17.6f} {v3-v2:>12.6f}")
d = (C * 3.847 + C * K_GOLD + C * a_fit / math.exp(3.847)) - (sl * 3.847 + ic)
p(f"\n  separation at 1e22 = {d:.6f}, against a far-point sigma of {sig[10000]:.6f}")
p(f"  => {d/sig[10000]:.2f} sigma with ONE block, {d/(sig[10000]/math.sqrt(2)):.2f} sigma with TWO")
p(f"  {'DISCRIMINATES' if d/sig[10000] > 3 else 'UNDERPOWERED as a two-model discriminator'}")
p("\n  NOTE the asymmetry, pre-registered: a fitted `a` near 0.140 after the extension is NOT")
p("  confirmation -- these same data drove it. The test is the far point's POSITION against the")
p("  2-parameter extrapolation, not the refitted coefficient.")

json.dump({"centroid_lnln": float(x.mean()), "V_centroid": float(y.mean()),
           "V_centroid_sem": float(s / math.sqrt(n)), "slope": float(sl), "intercept": float(ic),
           "sigma_V_W10000": sig[10000], "sigma_V_W20000": sig[20000],
           "a_fitted_from_these_data": float(a_fit),
           "prereg_1e22_2param": float(sl * 3.847 + ic),
           "prereg_1e22_3param": float(C * 3.847 + C * K_GOLD + C * a_fit / math.exp(3.847)),
           "separation": float(d), "sigma_far_one_block": sig[10000]},
          open(os.path.join(HERE, "phase8_invariant_measured.json"), "w"), indent=2)
p("\nwrote phase8_invariant_measured.json")
