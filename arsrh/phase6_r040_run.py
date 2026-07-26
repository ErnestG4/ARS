"""
PHASE 6 — R-040 RUN. Both arms, on the data in hand, against the three numbers pre-registered in
R-046. Normality alongside, as certification only (R-038).

PRE-REGISTERED (scout11, committed 01e0e85, before this run):
    tracking arm (X_0 = t/2pi)  slope     = 0.050660592
    tracking arm (X_0 = t/2pi)  intercept = 0.020313269
    fixed arm    (X_0 const)    slope     = 0            (no growth by construction)
    zeta - synthetic intercept difference = 0.050660592  = 1/2pi^2 = the F-integral

GRADE CAP, recorded here rather than discovered at write-up: the measurement is unconditional
(verified zeros, imaginary parts only, rule 11). The COMPARISON inherits its weakest reference --
leading coefficient 1/2pi^2 is theorem grade; the intercept bracket is RH + SPCC; and if Chan's `a`
is imported for the correction it is CFZ-ratios-conjecture grade, which caps the terminal claim at
CONJECTURE grade. That is a real demotion for a calibration set up as theorem-grade.

Synthetic construction: gamma_j solves N_smooth(t) + S_synth(t) = j - 1/2, with
    S_synth(t) = -(1/pi) sum_{n <= X_0} Lambda(n)/(sqrt(n) log n) sin(t log n)
so that Var[S_synth] = (1/2pi^2) sum_{p^m <= X_0} 1/(m^2 p^m) in closed form. Both arms then run
through the IDENTICAL estimator used on zeta, so estimator bias cancels in the difference.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from scipy.special import loggamma
from scipy.stats import skew, kurtosis

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
C = 1.0 / (2 * math.pi ** 2)
PRE = {"track_slope": 0.050660592, "track_intercept": 0.020313269,
       "fixed_slope": 0.0, "difference": 0.050660592}


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def dexact_N(t):
    return np.log(np.asarray(t, float) / (2 * math.pi)) / (2 * math.pi)


def prime_powers(X):
    """(log n, Lambda(n)) for prime powers n <= X."""
    X = int(X)
    s = np.ones(X + 1, bool); s[:2] = False
    for i in range(2, int(X ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    ln, lam = [], []
    for q in np.flatnonzero(s):
        m, pw = 1, int(q)
        while pw <= X:
            ln.append(math.log(pw)); lam.append(math.log(q))
            m += 1; pw *= int(q)
    return np.array(ln), np.array(lam)


def S_and_dS(t, ln, lam, chunk=400):
    """S_synth and its derivative, chunked over prime powers to bound memory."""
    S = np.zeros_like(t); dS = np.zeros_like(t)
    a = lam / (np.sqrt(np.exp(ln)) * ln)          # Lambda(n)/(sqrt(n) log n)
    b = lam / np.sqrt(np.exp(ln))                 # Lambda(n)/sqrt(n)
    for i in range(0, len(ln), chunk):
        L = ln[i:i + chunk][:, None]
        ph = t[None, :] * L
        S += a[i:i + chunk] @ np.sin(ph)
        dS += b[i:i + chunk] @ np.cos(ph)
    return -S / math.pi, -dS / math.pi


_TG = np.linspace(10.0, 1.4e6, 4_000_000)
_NG = exact_N(_TG)


def synth_block(j0, W, X0):
    """Zeros of the synthetic with prime sum truncated at X0."""
    ln, lam = prime_powers(X0)
    tgt = np.arange(j0, j0 + W, dtype=float) - 0.5
    t = np.interp(tgt, _NG, _TG)
    for _ in range(4):
        S, dS = S_and_dS(t, ln, lam)
        t = t - (exact_N(t) + S - tgt) / (dexact_N(t) + dS)
    var_closed = C * float(np.sum(lam ** 2 / (np.exp(ln) * ln ** 2)))
    return np.sort(t), var_closed, len(ln)


def measure(g, ps=8):
    """THE ESTIMATOR — identical for zeta and both synthetic arms."""
    u = exact_N(g); u = u - u[0]
    grid = np.linspace(0.0, u[-1], max(16, int(u[-1] * ps)))
    S = np.searchsorted(u, grid, side="right").astype(float) - grid
    S = S - S.mean()
    return float(np.var(S)), float(skew(S)), float(kurtosis(S, fisher=False))


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W, NBLK = 5000, 4
ANCHORS = [40000, 300000, 900000, 1900000]
X0_FIXED = 1000

p("=== PHASE 6 — R-040, both arms ===")
p(f"pre-registered: track slope {PRE['track_slope']}, track intercept {PRE['track_intercept']},")
p(f"                fixed slope {PRE['fixed_slope']}, difference {PRE['difference']}\n")

rows = {"zeta": [], "track": [], "fixed": []}
for a in ANCHORS:
    for k in range(NBLK):
        s0 = a + k * W
        if s0 + W >= z.size:
            continue
        b = z[s0:s0 + W]
        gm = float(b[W // 2]); ll = math.log(math.log(gm / (2 * math.pi)))
        v, sk, ku = measure(b)
        rows["zeta"].append((ll, v, sk, ku, gm))
        j0 = int(exact_N(np.array([b[0]]))[0])
        for arm, X0 in (("track", gm / (2 * math.pi)), ("fixed", X0_FIXED)):
            g, vc, npp = synth_block(j0, W, X0)
            vv, _, _ = measure(g)
            rows[arm].append((ll, vv, vc, npp))
    p(f"  anchor gamma~{z[a]:.3g} done")


def fit(xy):
    x = np.array([r[0] for r in xy]); y = np.array([r[1] for r in xy]); n = len(x)
    sl, ic = np.polyfit(x, y, 1)
    res = y - (sl * x + ic); s2 = float(res @ res) / (n - 2)
    Sxx = float(((x - x.mean()) ** 2).sum())
    return sl, math.sqrt(s2 / Sxx), ic, math.sqrt(s2 * (1 / n + x.mean() ** 2 / Sxx)), n


p("\n--- RESULTS ---")
out = {}
for arm in ("zeta", "track", "fixed"):
    sl, ssl, ic, sic, n = fit(rows[arm])
    out[arm] = {"slope": sl, "slope_sem": ssl, "intercept": ic, "intercept_sem": sic, "n": n}
    p(f"  {arm:>6s}: slope {sl:+.6f} +/- {ssl:.6f}   intercept {ic:+.6f} +/- {sic:.6f}   n={n}")

p(f"\n  [ARM 1 — fixed X_0={X0_FIXED}] pre-registered slope = 0")
z_f = out['fixed']['slope'] / out['fixed']['slope_sem']
p(f"    measured {out['fixed']['slope']:+.6f} +/- {out['fixed']['slope_sem']:.6f}  ->  {z_f:+.2f} sem")
p(f"    minimum detectable spurious slope (2 sem) = {2*out['fixed']['slope_sem']:.6f} "
  f"= {100*2*out['fixed']['slope_sem']/C:.1f}% of 1/2pi^2")
p(f"    {'PASS — estimator manufactures no growth' if abs(z_f) < 2 else 'FIRES — estimator manufactures growth'}")

p(f"\n  [ARM 2 — tracking X_0 = t/2pi] pre-registered slope {PRE['track_slope']:.6f}, "
  f"intercept {PRE['track_intercept']:.6f}")
zs = (out['track']['slope'] - PRE['track_slope']) / out['track']['slope_sem']
zi = (out['track']['intercept'] - PRE['track_intercept']) / out['track']['intercept_sem']
p(f"    slope     {out['track']['slope']:+.6f} +/- {out['track']['slope_sem']:.6f}  -> {zs:+.2f} sem")
p(f"    intercept {out['track']['intercept']:+.6f} +/- {out['track']['intercept_sem']:.6f}  -> {zi:+.2f} sem")
cl = np.array([r[2] for r in rows["track"]])
p(f"    closed-form Var[S_synth] check: measured-minus-closed mean "
  f"{np.mean([r[1]-r[2] for r in rows['track']]):+.5f} (sawtooth + estimator, common to both arms)")

d = out['zeta']['intercept'] - out['track']['intercept']
sd = math.hypot(out['zeta']['intercept_sem'], out['track']['intercept_sem'])
p(f"\n  [THE DIFFERENTIAL — the valuable one] pre-registered {PRE['difference']:.6f} = 1/2pi^2")
p(f"    zeta - synthetic intercept = {d:+.6f} +/- {sd:.6f}  ->  "
  f"{(d-PRE['difference'])/sd:+.2f} sem from 1/2pi^2")
p(f"    => F-integral = {d/C:.4f} +/- {sd/C:.4f}   (SPCC predicts 1)")

sk = np.array([r[2] for r in rows["zeta"]]); ku = np.array([r[3] for r in rows["zeta"]])
p(f"\n  [NORMALITY — certification only, NOT the cutoff gate (R-038)]")
p(f"    zeta S: skewness {sk.mean():+.4f} +/- {sk.std(ddof=1)/math.sqrt(len(sk)):.4f} (Selberg: 0)")
p(f"            kurtosis {ku.mean():+.4f} +/- {ku.std(ddof=1)/math.sqrt(len(ku)):.4f} (Selberg: 3)")

out["prereg"] = PRE
out["fixed_arm_min_detectable_slope"] = 2 * out['fixed']['slope_sem']
out["F_integral"] = {"value": d / C, "sem": sd / C}
out["normality"] = {"skew": float(sk.mean()), "kurt": float(ku.mean())}
json.dump(out, open(os.path.join(HERE, "phase6_r040_measured.json"), "w"), indent=2)
p("\nwrote phase6_r040_measured.json")
