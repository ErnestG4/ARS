"""50-digit reference for the ζ connected two-pair function (Will, 2026-10-10: the known answer for the phase-precision
fix). cs4lib.Zeta (the "slow" evaluator) computes ζ-values in mpmath but its prime sums/products in numpy complex
double, so it shares the large-phase precision limit it was used to check. Here every prime sum and Euler product (A, B,
Q, B1, B2, B3, B4, S13, A*) is an mpmath loop over p ≤ pmax at mp.dps = 50, same formulas as cs4lib.Zeta (summands
transcribed again from CS08 §5.7 and cs4lib; any transcription slip would show as an O(1) disagreement, not a
1e-9 one); ζ, ζ′/ζ, (ζ′/ζ)′ are mpmath at 50 digits (inherited). Memoised per argument tuple.

  python cs4ref.py CHUNK NCHUNKS OUT     points: the 4 failing + 4 passing points of the sparse check (L = 16.5)
  python cs4ref.py compare OUT          reference vs slow (cs4split) vs fast (cs4fast, fixed) at those points
"""
import functools
import glob
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

import cs4split as S

mp.mp.dps = 50
POINTS = [(16.5, 0.3, 0.8, 12558.2), (16.5, 0.3, 0.8, 20000.0), (16.5, 0.3, 0.8, 14665.4), (16.5, 0.3, 0.8, 17126.2),
          (16.5, 0.5, 0.5, 10.0), (16.5, 0.5, 0.5, 300.0), (16.5, 0.3, 0.8, 1000.0), (16.5, 1.0, 0.4, 5000.0)]


class ZetaRef(S.Zetap):
    def __init__(self, t, pmax=100_000):
        super().__init__(t, pmax=pmax)
        self.ell = self.L = mp.log(mp.mpf(t) / (2 * mp.pi))
        self.mpp = [mp.mpf(int(round(p))) for p in self.p]
        self.mlp = [mp.log(p) for p in self.mpp]

    def _P(self, i, e):                                 # p^{e}
        return mp.exp(e * self.mlp[i])

    @functools.lru_cache(maxsize=None)
    def A(self, x):
        s = mp.mpf(0)
        for i, p in enumerate(self.mpp):
            s += mp.log(1 - (1 - self._P(i, -x)) ** 2 / (p - 1) ** 2)
        return mp.exp(s)

    @functools.lru_cache(maxsize=None)
    def B(self, x):
        return mp.fsum((self.mlp[i] / (self._P(i, 1 + x) - 1)) ** 2 for i in range(len(self.mpp)))

    @functools.lru_cache(maxsize=None)
    def Q(self, x, y):
        return -mp.fsum(self.mlp[i] ** 3 * self._P(i, -(2 + x + y)) / ((1 - self._P(i, -(1 + x))) * (1 - self._P(i, -(1 + y))))
                        for i in range(len(self.mpp)))

    @functools.lru_cache(maxsize=None)
    def B1(self, x, y):
        out = []
        for i, p in enumerate(self.mpp):
            px, py = self._P(i, -x), self._P(i, -y)
            num = (1 - px) * (1 - px - py + self._P(i, -(1 + y))) * self.mlp[i]
            den = (1 - self._P(i, -(1 - x + y))) * (1 - self._P(i, -(1 + y))) * (1 - 2 / p + self._P(i, -(1 + x))) * self._P(i, 2 - x + y)
            out.append(num / den)
        return mp.fsum(out)

    @functools.lru_cache(maxsize=None)
    def B2(self, a, b1, b2, b3):
        out = []
        for i, p in enumerate(self.mpp):
            P = lambda e: self._P(i, e)
            num = (p - 1) * P(2 * b1) * (P(a + b1) - 1) * (P(a + b1) - p) * self.mlp[i] ** 2
            den = (-2 * P(a + b1) + P(a + b1 + 1) + 1) ** 2 * (P(b1) - P(b2 + 1)) * (P(b1) - P(b3 + 1))
            out.append(num / den)
        return mp.fsum(out)

    @functools.lru_cache(maxsize=None)
    def B3(self, a1, a2, b1, b2):
        out = []
        for i, p in enumerate(self.mpp):
            P = lambda e: self._P(i, e)
            Cc = (-P(a1 + b1) + 2 * P(a1 + b1 + 1) - P(a2 + b1 + 2) - P(2 * a1 + 2 * b1 + 1) + P(a1 + a2 + 2 * b1 + 1)
                  - P(a1 + b2 + 2) + P(a2 + b2 + 2) + P(2 * a1 + b1 + b2 + 1) - 2 * P(a1 + a2 + b1 + b2 + 2)
                  + P(a1 + a2 + b1 + b2 + 3))
            k = -2 * P(a1 + b1) + P(a1 + b1 + 1) + 1
            t1 = (p - 1) ** 2 * (P(a1 + b1) - 1) ** 2 * P(a1 + b1) / ((P(a1) - P(a2 + 1)) * k ** 2 * (P(b1) - P(b2 + 1)))
            t2 = Cc / ((P(a1) - P(a2 + 1)) * k * (P(b2 + 1) - P(b1)) * (P(a2 + b2 + 1) - 1))
            t3 = 1 / (P(a2 + b2 + 1) - 1)
            out.append(self.mlp[i] ** 2 * (t1 + t2 + t3))
        return mp.fsum(out)

    @functools.lru_cache(maxsize=None)
    def B4(self, a1, a2, b1, b2):
        out = []
        for i, p in enumerate(self.mpp):
            P = lambda e: self._P(i, e)
            num = (3 - P(1 + a1 + b1) - P(1 + a2 + b1) - P(1 + a1 + b2) - P(1 + a2 + b2) + P(2 + a1 + a2 + b1 + b2)) * self.mlp[i] ** 4
            den = (P(1 + a1 + b1) - 1) * (P(1 + a2 + b1) - 1) * (P(1 + a1 + b2) - 1) * (P(1 + a2 + b2) - 1)
            out.append(num / den)
        return mp.fsum(out)

    @functools.lru_cache(maxsize=None)
    def S13(self, a, b1, b2, b3):
        out = []
        for i in range(len(self.mpp)):
            zp = lambda x: 1 / (1 - self._P(i, -x))
            out.append(zp(1 + a + b1) * zp(1 + a + b2) * zp(1 + a + b3) * self.mlp[i] ** 4 * self._P(i, -(3 + 3 * a + b1 + b2 + b3)))
        return -mp.fsum(out)

    @functools.lru_cache(maxsize=None)
    def Astar(self, a1, a2, b1, b2):
        s = mp.mpf(0)
        for i in range(len(self.mpp)):
            zp = lambda x: 1 / (1 - self._P(i, -x))
            Zp = lambda X, Y: mp.fprod([1 / zp(1 + x + y) for x in X for y in Y])
            A_, B_ = (a1, a2), (b1, b2)
            mA, mB = tuple(-x for x in A_), tuple(-x for x in B_)
            pref = Zp(A_, B_) * Zp(mA, mB) / (Zp(A_, mA) * Zp(B_, mB))
            T1 = zp(1 - a1 - b1) * zp(1 - a2 - b1) * zp(b2 - b1) / (zp(1) * zp(-a1 - b1) * zp(-a2 - b1) * zp(1 + b2 - b1))
            T2 = zp(1 - a1 - b2) * zp(1 - a2 - b2) * zp(b1 - b2) / (zp(1) * zp(-a1 - b2) * zp(-a2 - b2) * zp(1 + b1 - b2))
            s += mp.log(pref * self._P(i, -(a1 + a2 + b1 + b2)) * (1 - T1 - T2))
        return mp.exp(s)


def run(chunk, nchunks, out):
    rows = []
    for k, (L, d1, d2, r) in enumerate(POINTS):
        if k % nchunks != chunk:
            continue
        Z = ZetaRef(2 * mp.pi * mp.exp(L))
        o, n_, _ = S.connected_split(Z, d1, d2, r)
        rows.append(dict(L=L, d1=d1, d2=d2, r=r, ref_non=str(n_), ref_osc=str(o)))
        print(k, r, mp.nstr(n_, 20), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(rows, open(os.path.join(out, f"ref_{chunk:02d}.json"), "w"), indent=1)


def compare(out):
    import cs4fast as F
    rows = [r for f in sorted(glob.glob(os.path.join(out, "ref_*.json"))) for r in json.load(open(f))]
    res = []
    for r in sorted(rows, key=lambda r: (r["d1"], r["r"])):
        t = 2 * math.pi * math.exp(r["L"])
        ref_n, ref_o = mp.mpc(r["ref_non"]), mp.mpc(r["ref_osc"])
        so, sn, _ = S.connected_split(S.Zetap(t, pmax=100_000), r["d1"], r["d2"], r["r"])
        fo, fn = F.FastZeta(t, pmax=100_000).connected(r["d1"], r["d2"], np.array([r["r"]]))
        res.append(dict(r, slow_err_non=float(abs(sn - ref_n)), fast_err_non=float(abs(complex(fn[0]) - ref_n)),
                        slow_err_osc=float(abs(so - ref_o)), fast_err_osc=float(abs(complex(fo[0]) - ref_o))))
        print("d=(%.1f,%.1f) r=%8.1f  |ref_non| %.2e   slow err %.2e   fast err %.2e" % (
            r["d1"], r["d2"], r["r"], float(abs(ref_n)), res[-1]["slow_err_non"], res[-1]["fast_err_non"]), flush=True)
    json.dump(res, open(os.path.join(out, "ref_compare.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "compare":
        compare(sys.argv[2])
    else:
        run(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
