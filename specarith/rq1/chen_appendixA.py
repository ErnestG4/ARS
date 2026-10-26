"""Line-by-line Python transcription of Chen et al. (arXiv:1901.07386) Appendix A, run on our ℤ[i] angle set
(rq1_angles' sieve, Tonelli–Shanks and Cornacchia). Round 86 post-hoc cross-check; tolerances in CHEN_XCHECK.md.

Mathematica → here:
  primes1 = primes ≡ 1 mod 4 in [1, X]; primes3 = primes ≡ 3 mod 4 in [√1, √X]
  gauss2 = ArcTan[b/a] (a < b), gauss3 = ArcTan[a/b]: both ideals above each p ∈ primes1
  allAngles = trivial (0 for each primes3) ∪ gauss2 ∪ gauss3; weights 2 log p (primes3), log p, log p
  HistogramList[anglesWeights, {0, π/2, π/(2 Round[X^j])}] → K = Round[X^j] bin weight sums on [0, π/2)
  Variance (denominator K − 1) / (X^{1−j} Log[X]), for j = 0.1, 0.125, …, 0.7

  python chen_appendixA.py X OUT_JSON
"""
import json
import math
import sys

import numpy as np

import rq1_angles as R


def angles_weights(X):
    ps = R.primes_in(2, X + 1)
    p1 = ps[ps % 4 == 1]
    ang = np.empty(2 * len(p1))
    for i, p in enumerate(p1.tolist()):
        s = R.sqrt_mod(p - 1, p)
        a, b = p, s
        r = math.isqrt(p)
        while b > r:
            a, b = b, a % b
        c = math.isqrt(p - b * b)
        lo, hi = min(b, c), max(b, c)
        ang[2 * i] = math.atan(hi / lo)                          # gauss2: ArcTan[b/a], a < b
        ang[2 * i + 1] = math.atan(lo / hi)                      # gauss3: ArcTan[a/b]
    w = np.repeat(np.log(p1.astype(np.float64)), 2)
    p3 = R.primes_in(2, math.isqrt(X) + 1)
    p3 = p3[p3 % 4 == 3]
    ang = np.concatenate([np.zeros(len(p3)), ang])
    w = np.concatenate([2 * np.log(p3.astype(np.float64)), w])
    return ang, w


def main(X, out):
    ang, w = angles_weights(X)
    rows = []
    for j in np.round(np.arange(0.1, 0.7001, 0.025), 3):
        K = int(round(X ** float(j)))
        idx = np.minimum((ang / (math.pi / 2) * K).astype(np.int64), K - 1)
        sums = np.bincount(idx, weights=w, minlength=K)
        v = sums.var(ddof=1) / (X ** (1 - float(j)) * math.log(X))
        rows.append(dict(lam=float(j), K=K, value=float(v)))
        print(f"{j:.3f} {K} {v:.5f}", flush=True)
    json.dump(dict(X=X, n_angles=int(len(ang)), rows=rows), open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(int(float(sys.argv[1])), sys.argv[2]))
