"""
SCOUT 4 (unsealed) — fix the peak estimator, then spend the free falsifier.

v3's |delta| <= 0.0002 was NOT a measurement: the output grid step was 0.0004, so 0.0002 is exactly
half a bin. I was reporting "nearest grid point", i.e. agreement finer than the grid can express, and
the native resolution (1/u_max * Lbar = 0.0006) is coarser still. Fixed here:

  LOCATION  — per block, on its OWN NATIVE periodogram, parabolic sub-bin interpolation around the
              local max, then x = f_hat * Lbar. Report mean over 20 blocks +/- sem. That is a
              measured location with a measured error.
  AMPLITUDE — INTEGRATED power over the peak on the native grid, not the interpolated peak VALUE.
              A point sample of a sharp peak is attenuated by random sub-bin phase, which is a
              candidate artifact for the 49-77 drift.

Then three things v3 left on the table:
  [F] log 8 = 2.0794, the unspent falsifier. 9 prime powers sit in the band; v3 reported 8. The
      missing one is 8 = 2^3, predicted WEAKEST at Lambda(8)^2/8 = 0.0601, ~0.5x log 4. Location AND
      relative magnitude, on data already in hand.
  [R] RANK test. Spearman rho between measured amplitude order and Lambda(n)^2/n order needs no
      normalization, so it is a second bracket independent of the unchecked absolute weight.
  [C] Extended controls. Every composite in v3's band (6, 10, 12) is a SUM-frequency of strong peaks,
      so the "must be absent" arm was contaminated by intermodulation. Extend to 3.15 to reach
      primes 17/19/23, prime power 16, and sums 14/15/18/20/21/22.
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


def von_mangoldt(n):
    for q in range(2, n + 1):
        if n % q == 0:
            m = n
            while m % q == 0:
                m //= q
            return math.log(q) if m == 1 else 0.0
    return 0.0


z = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
W, NB, BPU = 20000, 20, 8
starts = [z.size - 1 - (i + 1) * W for i in range(NB)][::-1]

# per-block native periodograms
blocks = []
for s0 in starts:
    b = z[s0:s0 + W]
    u = exact_N(b); u = u - u[0]
    Lbar = math.log(float(b[W // 2]) / (2 * math.pi))
    nb = int(u[-1] * BPU)
    h, _ = np.histogram(u, bins=nb, range=(0.0, u[-1]))
    psd = (np.abs(np.fft.rfft(h - h.mean())) ** 2) / W
    freq = np.fft.rfftfreq(nb, d=u[-1] / nb)
    blocks.append((freq, psd, Lbar, float(u[-1])))
df = blocks[0][0][1] - blocks[0][0][0]
p(f"native frequency resolution: {df:.3e} cycles/unit  ->  {df*blocks[0][2]:.5f} in alpha*Lbar")
p(f"v3 quoted |delta| <= 0.0002 on a 0.0004 grid = HALF A BIN. That was the grid, not a measurement.\n")


def measure(n):
    """Per-block sub-bin location and integrated peak power for target log n."""
    xs, amps = [], []
    for freq, psd, Lbar, ulen in blocks:
        f0 = math.log(n) / Lbar
        i = int(np.argmin(np.abs(freq - f0)))
        j = i - 3 + int(np.argmax(psd[i - 3:i + 4]))
        y0, y1, y2 = psd[j - 1], psd[j], psd[j + 1]
        den = y0 - 2 * y1 + y2
        d = 0.5 * (y0 - y2) / den if den != 0 else 0.0
        d = max(-1.0, min(1.0, d))
        xs.append((freq[j] + d * df) * Lbar)
        amps.append(float(psd[j - 2:j + 3].sum()))          # INTEGRATED power over the peak
    xs = np.array(xs); amps = np.array(amps)
    return xs.mean(), xs.std(ddof=1) / math.sqrt(NB), amps.mean(), amps.std(ddof=1) / math.sqrt(NB)


p("[L]+[F] locations by sub-bin interpolation, and the log 8 falsifier")
p(f"  {'n':>4s} {'log n':>8s} {'measured x':>12s} {'sem':>9s} {'|delta|':>9s} {'d/sem':>7s} "
  f"{'integ.power':>12s} {'Lam^2/n':>9s}")
targets = [2, 3, 4, 5, 7, 8, 9, 11, 13]
res = {}
for n in targets:
    x, sx, a, sa = measure(n)
    w = von_mangoldt(n) ** 2 / n
    res[n] = (x, sx, a, sa, w)
    p(f"  {n:>4d} {math.log(n):>8.5f} {x:>12.5f} {sx:>9.5f} {abs(x-math.log(n)):>9.5f} "
      f"{abs(x-math.log(n))/sx:>7.2f} {a:>12.3f} {w:>9.4f}")

a8, a4 = res[8][2], res[4][2]
p(f"\n  FALSIFIER [F]: log 8 predicted present and WEAKEST, at ~0.5x log 4.")
p(f"    measured log8/log4 = {a8/a4:.3f}   (predicted {0.0601/0.1201:.3f})")
p(f"    log 8 is the smallest of the nine: {a8 == min(res[k][2] for k in targets)}")

p("\n[R] rank test — needs no normalization, so it is independent of the absolute weight")
ns = sorted(targets, key=lambda n: -res[n][2])
pr = sorted(targets, key=lambda n: -res[n][4])
p(f"  measured amplitude order : {ns}")
p(f"  predicted Lambda^2/n order: {pr}")
rm = {n: i for i, n in enumerate(ns)}; rp = {n: i for i, n in enumerate(pr)}
d2 = sum((rm[n] - rp[n]) ** 2 for n in targets); k = len(targets)
rho = 1 - 6 * d2 / (k * (k * k - 1))
tstat = rho * math.sqrt((k - 2) / max(1e-12, 1 - rho ** 2))
p(f"  Spearman rho = {rho:.3f} on n={k}  (t = {tstat:.2f}, df={k-2})")

p("\n[A] amplitude drift: is the 49-77 spread structured in n?")
ns_s = sorted(targets)
rat = np.array([res[n][2] / res[n][4] for n in ns_s])
ln = np.log(np.array(ns_s, float))
sl, ic = np.polyfit(ln, np.log(rat), 1)
p(f"  {'n':>4s} {'integ/(Lam^2/n)':>17s}")
for n, r in zip(ns_s, rat):
    p(f"  {n:>4d} {r:>17.2f}")
p(f"  fit ratio ~ n^({sl:+.3f})  => implied weight Lambda(n)^2 / n^({1-sl:.3f}) rather than /n^1")
p(f"  spread max/min = {rat.max()/rat.min():.2f}")
bin_att = [(math.sin(math.pi * math.log(n) / blocks[0][2] / BPU) /
            (math.pi * math.log(n) / blocks[0][2] / BPU)) ** 2 for n in ns_s]
p(f"  histogram-bin attenuation across the range accounts for only "
  f"{100*(1-bin_att[-1]/bin_att[0]):.2f}% -- not the drift.")

p("\n[C] extended controls: primes and prime powers vs SUM-frequencies (intermodulation)")
p(f"  {'n':>4s} {'class':>16s} {'log n':>8s} {'integ.power':>12s}")
med = np.median([res[n][2] for n in targets])
for n, cls in ((16, "prime power 2^4"), (17, "prime"), (19, "prime"), (23, "prime"),
               (14, "sum 2*7"), (15, "sum 3*5"), (18, "sum 2*3^2"),
               (20, "sum 2^2*5"), (21, "sum 3*7"), (22, "sum 2*11")):
    _, _, a, _ = measure(n)
    p(f"  {n:>4d} {cls:>16s} {math.log(n):>8.5f} {a:>12.4f}")
p(f"\n  (positives above run {min(res[k][2] for k in targets):.2f}-{max(res[k][2] for k in targets):.2f})")
