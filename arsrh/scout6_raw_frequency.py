"""
SCOUT 6 (unsealed) — the height test failed, and the failure is MY coordinate choice, not physics.

Scout 5 [H]: the Lambda(n)^2/n law held at high gamma (exponent n^-0.014) and collapsed at low gamma
(n^-0.632). Diagnosis before blaming zeta:

  I computed the periodogram in the UNFOLDED coordinate u and rescaled frequency by a SINGLE Lbar per
  block. But Lbar varies WITHIN a block, so the term for n sits at alpha = log n / Lbar(t), which
  DRIFTS across the block by  d_alpha ~ log n * dLbar / Lbar^2.  The smear is proportional to log n,
  so high-n peaks lose more power through a fixed integration window -- manufacturing exactly a
  monotone n^-something falloff. Magnitude: LOW set dLbar ~ 0.35, Lbar ~ 8.75 -> d_alpha ~ log n *
  0.0046 = up to 234 NATIVE BINS of smear at n=13. HIGH set dLbar ~ 0.005 -> under one bin.

  This is the curvature systematic I declared "controlled by construction" after budgeting it for
  Var[S] ONLY, where it is second order. For the SPECTRAL readout it is first order in log n. The
  budget did not propagate to the second observable.

THE FIX IS A COORDINATE, NOT A CORRECTION. In RAW t the explicit formula's terms sit at FIXED
frequency log n -- no Lbar anywhere. So take the exponential sum over raw gamma:
    P(omega) = |sum_j exp(i omega gamma_j)|^2,  peaks at omega = log n exactly, at every height.
No rescaling, no drift, nothing to smear. Redo LOW vs HIGH there.
"""
from __future__ import annotations
import math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
TARGETS = [2, 3, 4, 5, 7, 8, 9, 11, 13]


def vm(n):
    for q in range(2, n + 1):
        if n % q == 0:
            m = n
            while m % q == 0:
                m //= q
            return math.log(q) if m == 1 else 0.0
    return 0.0


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W, NB, DT = 20000, 20, 0.25


def block_psd(b):
    """Periodogram of the raw zero point-process in t. Peaks at f = log n / 2pi."""
    span = b[-1] - b[0]
    nb = int(span / DT)
    h, _ = np.histogram(b, bins=nb, range=(b[0], b[-1]))
    psd = (np.abs(np.fft.rfft(h - h.mean())) ** 2) / len(b)
    return np.fft.rfftfreq(nb, d=span / nb), psd


def amps(starts, n):
    out = []
    for s0 in starts:
        f, psd = block_psd(z[s0:s0 + W])
        i = int(np.argmin(np.abs(f - math.log(n) / (2 * math.pi))))
        j = i - 4 + int(np.argmax(psd[i - 4:i + 5]))
        out.append(float(psd[j - 3:j + 4].sum()))
    return np.array(out)


HI = [z.size - 1 - (i + 1) * W for i in range(NB)][::-1]
LO = [40000 + i * W for i in range(NB)]
p(f"HIGH gamma {z[HI[0]]:.3g}..{z[HI[-1]+W]:.3g}   LOW gamma {z[LO[0]]:.3g}..{z[LO[-1]+W]:.3g}")
p("peaks now sought at omega = log n in RAW t; no Lbar, no rescaling, no drift.\n")

p(f"  {'n':>4s} {'Lam^2/n':>9s} {'HIGH ratio':>12s} {'sem':>7s} {'LOW ratio':>11s} {'sem':>7s} {'LOW/HIGH':>9s}")
mh, ml = {}, {}
for n in TARGETS:
    w = vm(n) ** 2 / n
    ah, al = amps(HI, n) / w, amps(LO, n) / w
    mh[n], ml[n] = float(ah.mean()), float(al.mean())
    p(f"  {n:>4d} {w:>9.4f} {mh[n]:>12.2f} {ah.std(ddof=1)/math.sqrt(NB):>7.2f} "
      f"{ml[n]:>11.2f} {al.std(ddof=1)/math.sqrt(NB):>7.2f} {ml[n]/mh[n]:>9.3f}")

hv = np.array([mh[n] for n in TARGETS]); lv = np.array([ml[n] for n in TARGETS])
ln = np.log(np.array(TARGETS, float))
sh = np.polyfit(ln, np.log(hv), 1)[0]; sl = np.polyfit(ln, np.log(lv), 1)[0]
p(f"\n  fitted exponent deviation:  HIGH n^({sh:+.4f})   LOW n^({sl:+.4f})")
p(f"  across-n spread:            HIGH {100*(hv.max()-hv.min())/hv.mean():.2f}%   "
  f"LOW {100*(lv.max()-lv.min())/lv.mean():.2f}%")
p(f"  (unfolded-coordinate version gave HIGH -0.014, LOW -0.632)")
ok = abs(sl) < 0.06 and abs(sh) < 0.06
p(f"\n  -> {'LAW HOLDS AT BOTH HEIGHTS once the coordinate is right: the Scout-5 collapse was the' if ok else 'still not stable -- coordinate was NOT the whole story'}")
if ok:
    p("     within-block Lbar drift, i.e. MY curvature systematic reaching a second observable,")
    p("     not a height dependence of the weight law.")
ro_h = sorted(TARGETS, key=lambda n: -mh[n] * vm(n) ** 2 / n)
ro_l = sorted(TARGETS, key=lambda n: -ml[n] * vm(n) ** 2 / n)
ro_p = sorted(TARGETS, key=lambda n: -vm(n) ** 2 / n)
p(f"  rank order  HIGH: {ro_h}\n              LOW : {ro_l}\n              pred: {ro_p}")
