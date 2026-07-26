"""
SCOUT 3 v2 (unsealed, no significance values). Two fixes to v1, both mine:

  - CURVATURE BUDGET was the wrong statistic. I reported the within-block RANGE of Var[S]. The bias
    from averaging a LINEAR function over a block is zero at the mean abscissa; what matters is
    mean_over_block[lnln] - lnln(gamma_mid), a second-order quantity. And I only measured the TOP
    blocks, where curvature is smallest -- the concern was about the BOTTOM of the lever arm.
  - CONTROL LOCATION was misplaced. I used alpha*Lbar = 2.20 as a "non-prime" control; e^2.20 = 9.03,
    and 9 = 3^2 IS a prime power, so it is a positive location, not a control. Controls must be
    non-prime-POWERS: log 6, log 10, log 12, plus non-integer locations.

  - And the location test is redone by PEAK-FINDING rather than by sampling at predicted spots, so
    the peaks have to land on log p^k rather than being looked for there. v1's ratios were also
    computed on a subsampled periodogram (grid 0.0015 vs native 0.0006) so their magnitudes were
    not trustworthy; locations were. Locations are the test.
"""
from __future__ import annotations
import math, os
import numpy as np
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
p = lambda *a: print(*a, flush=True)
C_SEL = 1.0 / (2 * math.pi ** 2)


def exact_N(t):
    t = np.asarray(t, float)
    return (np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)) / math.pi + 1.0


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W = 20000

# ------------------------------------------------------------------ [2] curvature bias, BOTH ends
p("[2] curvature bias, computed correctly, at BOTH ends of the lever arm")
p("    bias = C * ( mean_over_block[lnln(gamma/2pi)] - lnln(gamma_mid/2pi) )")
p(f"  {'block':>22s} {'gamma_mid':>11s} {'curv':>7s} {'lnln bias':>11s} {'Var[S] bias':>12s} {'vs sigma_V':>11s}")
for lbl, s0 in (("low end  [40000:60000]", 40000), ("top      [1981051:...]", z.size - W - 1)):
    b = z[s0:s0 + W]
    gm = float(b[W // 2])
    curv = math.log(b[-1] / (2 * math.pi)) / math.log(b[0] / (2 * math.pi))
    ll_all = np.log(np.log(b / (2 * math.pi)))
    bias_ll = float(ll_all.mean() - math.log(math.log(gm / (2 * math.pi))))
    p(f"  {lbl:>22s} {gm:>11.4g} {curv:>7.4f} {bias_ll:>+11.6f} {C_SEL*bias_ll:>+12.6f} "
      f"{abs(C_SEL*bias_ll)/0.00037:>10.2f}x")
p("  -> the LINEAR part of the height dependence cancels at the block's mean abscissa; only the")
p("     second-order term survives. Use mean_over_block[lnln], NOT lnln(gamma_mid), and the")
p("     curvature systematic is controlled by construction rather than budgeted.\n")

# ------------------------------------------------------------------ [3] peak-finding
p("[3] prime peaks by PEAK-FINDING (peaks must land on log p^k; not sampled at predicted spots)")
NB = 20
starts = [z.size - 1 - (i + 1) * W for i in range(NB)][::-1]
BPU = 8
xg = np.arange(0.30, 2.60, 0.0004)           # finer than native resolution (12.1/20000 = 0.0006)
acc = np.zeros_like(xg)
for s0 in starts:
    b = z[s0:s0 + W]
    u = exact_N(b); u = u - u[0]
    Lbar = math.log(float(b[W // 2]) / (2 * math.pi))
    nb = int(u[-1] * BPU)
    h, _ = np.histogram(u, bins=nb, range=(0.0, u[-1]))
    F = np.fft.rfft(h - h.mean())
    freq = np.fft.rfftfreq(nb, d=u[-1] / nb)
    acc += np.interp(xg, freq * Lbar, (np.abs(F) ** 2) / W)
acc /= NB

# find local maxima above a high quantile
thr = float(np.quantile(acc, 0.995))
loc = [i for i in range(2, len(acc) - 2)
       if acc[i] > thr and acc[i] == acc[max(0, i - 6):i + 7].max()]
peaks = sorted(((float(acc[i]), float(xg[i])) for i in loc), reverse=True)[:10]
p(f"  {NB} blocks averaged; top 10 local maxima in alpha*Lbar in [0.30, 2.60]:")
p(f"  {'power':>10s} {'alpha*Lbar':>11s} {'exp(.)':>9s} {'nearest int':>12s} {'|delta|':>9s} {'prime power?':>13s}")
for amp, x in peaks:
    n = round(math.exp(x))
    ispp = n > 1 and len({q for q in range(2, n + 1) if n % q == 0 and
                          all(q % r for r in range(2, int(q ** 0.5) + 1))}) == 1
    p(f"  {amp:>10.3f} {x:>11.4f} {math.exp(x):>9.4f} {n:>12d} {abs(x-math.log(n)):>9.4f} "
      f"{('YES' if ispp else 'no'):>13s}")

p(f"\n  NEGATIVE CONTROLS — non-prime-power integers and non-integer locations:")
p(f"  {'target':>14s} {'alpha*Lbar':>11s} {'PSD':>10s} {'vs median':>10s}")
med = float(np.median(acc))
for lbl, val in (("log 6", math.log(6)), ("log 10", math.log(10)), ("log 12", math.log(12)),
                 ("non-int 1.25", 1.25), ("non-int 0.85", 0.85),
                 ("log 2 (POS)", math.log(2)), ("log 9 (POS)", math.log(9))):
    i = int(np.argmin(np.abs(xg - val)))
    v = float(acc[max(0, i - 3):i + 4].max())
    p(f"  {lbl:>14s} {val:>11.4f} {v:>10.4f} {v/med:>9.1f}x")
p(f"\n  median PSD over the band = {med:.5f}")
p("  A prime-power attribution is earned only if the POS rows tower over the control rows.")
