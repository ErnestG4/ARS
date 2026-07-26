"""
SCOUT 5 (unsealed) — three checks the reviewer's amendments demand.

[P] IS 4% NOISE OR SYSTEMATIC? rho = 1.000 with three adjacent pairs separated by 1.0%, 2.3%, 3.4%
    is ~1-in-8 if 4% is per-point noise. Measure the PER-BLOCK scatter of each ratio and its sem.
    If sem << 4%, the 127-133 spread is SYSTEMATIC and the ranks are secure -- and the spread must
    then be reported as systematic, not as noise.
[8] THE log-8 RATIO WITH ITS ERROR. "0.500 vs 0.500" quotes three digits on a quantity carrying
    percent-level scatter. The prediction is exact by construction (1/8 over 1/4); the MEASUREMENT
    is not. Quote it with its error.
[H] HEIGHT SPAN. Scout 4's 20 blocks were the TOP 20 -- gamma 9.3e5..1.13e6, NOT the full range.
    The Lbar-rescaling makes height-invariance testable, so run a LOW set too and compare. Claiming
    the axis without running it would be the expectation-row failure one more time.
"""
from __future__ import annotations
import math, os
import numpy as np
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


def vm(n):
    for q in range(2, n + 1):
        if n % q == 0:
            m = n
            while m % q == 0:
                m //= q
            return math.log(q) if m == 1 else 0.0
    return 0.0


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W, NB, BPU = 20000, 20, 8
TARGETS = [2, 3, 4, 5, 7, 8, 9, 11, 13]


def build(starts):
    out = []
    for s0 in starts:
        b = z[s0:s0 + W]
        u = exact_N(b); u = u - u[0]
        Lbar = math.log(float(b[W // 2]) / (2 * math.pi))
        nb = int(u[-1] * BPU)
        h, _ = np.histogram(u, bins=nb, range=(0.0, u[-1]))
        psd = (np.abs(np.fft.rfft(h - h.mean())) ** 2) / W
        out.append((np.fft.rfftfreq(nb, d=u[-1] / nb), psd, Lbar, float(b[W // 2])))
    return out


def amps(blocks, n):
    """Integrated peak power per block for target log n."""
    a = []
    for freq, psd, Lbar, _ in blocks:
        i = int(np.argmin(np.abs(freq - math.log(n) / Lbar)))
        j = i - 3 + int(np.argmax(psd[i - 3:i + 4]))
        a.append(float(psd[j - 2:j + 3].sum()))
    return np.array(a)


HI = build([z.size - 1 - (i + 1) * W for i in range(NB)][::-1])
LO = build([40000 + i * W for i in range(NB)])
p(f"HIGH set: gamma {HI[0][3]:.3g} .. {HI[-1][3]:.3g}   Lbar {HI[0][2]:.3f}..{HI[-1][2]:.3f}")
p(f"LOW  set: gamma {LO[0][3]:.3g} .. {LO[-1][3]:.3g}   Lbar {LO[0][2]:.3f}..{LO[-1][2]:.3f}")
p(f"  -> Scout 4 used the HIGH set only. Height-invariance was NOT covered and was not claimed.\n")

# ------------------------------------------------------------------ [P] and [8]
p("[P] per-block scatter: is the 127-133 spread noise or systematic?")
p(f"  {'n':>4s} {'Lam^2/n':>9s} {'ratio mean':>11s} {'per-block sd':>13s} {'sem':>8s} {'sem %':>7s}")
means, sems = {}, {}
for n in TARGETS:
    w = vm(n) ** 2 / n
    r = amps(HI, n) / w
    means[n] = float(r.mean()); sems[n] = float(r.std(ddof=1) / math.sqrt(NB))
    p(f"  {n:>4d} {w:>9.4f} {means[n]:>11.2f} {r.std(ddof=1):>13.2f} {sems[n]:>8.2f} "
      f"{100*sems[n]/means[n]:>6.2f}%")
mv = np.array([means[n] for n in TARGETS])
sv = np.array([sems[n] for n in TARGETS])
spread = 100 * (mv.max() - mv.min()) / mv.mean()
p(f"\n  across-n spread of the means: {spread:.2f}%")
p(f"  typical sem on a single mean : {100*np.mean(sv/mv):.2f}%")
chi2 = float(np.sum((mv - mv.mean()) ** 2 / sv ** 2))
p(f"  chi^2 of the 9 means about a constant = {chi2:.1f} on {len(TARGETS)-1} dof")
p(f"  -> {'SYSTEMATIC (spread >> sem): ranks secure, spread must be reported as systematic' if chi2 > 30 else 'consistent with noise'}")

p("\n[8] log-8 ratio, with its error")
r8 = amps(HI, 8); r4 = amps(HI, 4)
rr = r8 / r4
p(f"  per-block log8/log4: mean {rr.mean():.4f}, sd {rr.std(ddof=1):.4f}, "
  f"sem {rr.std(ddof=1)/math.sqrt(NB):.4f}")
p(f"  quote as {rr.mean():.3f} +/- {rr.std(ddof=1)/math.sqrt(NB):.3f}  against an EXACT prediction of 0.5")
p(f"  (the prediction is exact by construction -- Lambda(8)^2/8 over Lambda(4)^2/4 = (1/8)/(1/4);")
p(f"   the MEASUREMENT is not, and '0.500 vs 0.500' quoted three digits it does not have)")

# ------------------------------------------------------------------ [H]
p("\n[H] height invariance: does the weight law hold at the LOW end too?")
p(f"  {'n':>4s} {'HIGH ratio':>11s} {'LOW ratio':>11s} {'LOW/HIGH':>9s}")
lo_means = {}
for n in TARGETS:
    w = vm(n) ** 2 / n
    lo_means[n] = float(amps(LO, n).mean() / w)
    p(f"  {n:>4d} {means[n]:>11.2f} {lo_means[n]:>11.2f} {lo_means[n]/means[n]:>9.3f}")
lv = np.array([lo_means[n] for n in TARGETS])
p(f"\n  LOW across-n spread {100*(lv.max()-lv.min())/lv.mean():.2f}%  "
  f"(HIGH {spread:.2f}%)")
p(f"  LOW/HIGH overall = {lv.mean()/mv.mean():.3f}")
sl_lo = np.polyfit(np.log(TARGETS), np.log(lv), 1)[0]
sl_hi = np.polyfit(np.log(TARGETS), np.log(mv), 1)[0]
p(f"  fitted exponent deviation: HIGH n^({sl_hi:+.4f})  LOW n^({sl_lo:+.4f})")
p(f"  -> the Lambda(n)^2/n law is {'RECOVERED AT BOTH ENDS' if abs(sl_lo) < 0.05 else 'NOT stable across height'}"
  f"; rank order identical: {sorted(TARGETS, key=lambda n:-lo_means[n]*vm(n)**2/n) == sorted(TARGETS, key=lambda n:-vm(n)**2/n)}")
