"""Cached fast ζ four-point evaluator (speed-up of cs4fast.FastZeta for the long-range quadrature).

In the two-pair geometry every argument is K = c₀ + i(s + c_r·r_t): a real constant c₀ (the "1" in ζ(1+x) etc. is added
inside the blocks, so here c₀ = 0), a scalar offset s fixed by the in-pair offsets (d₁, d₂), and an integer coefficient
c_r of the t-separation r_t. Every primitive block (ζ triplet, A, B, Q, B1–B4, S13, A*) and composite (P1core, P2, P3) is
memoised on (block, keys) for one call of connected(); the (P, M) enumeration reuses them. Pieces with r-oscillating
phase can be skipped (nonosc_only=True) for the long range. Validated against cs4fast (uncached) and the slow evaluator.
"""
import math

import numpy as np

import cs4fast as F
import cs4lib as C


class K:
    __slots__ = ("s", "cr")

    def __init__(self, s, cr):
        self.s, self.cr = float(s), int(cr)

    def __add__(self, o):
        return K(self.s + o.s, self.cr + o.cr)

    def __sub__(self, o):
        return K(self.s - o.s, self.cr - o.cr)

    def __neg__(self):
        return K(-self.s, -self.cr)

    def key(self):
        return (round(self.s, 12), self.cr)


class FastZetaCached(F.FastZeta):
    def _arr(self, k):
        return 1j * (k.s + k.cr * self.rt)

    def _memo(self, name, fn, *ks):
        key = (name,) + tuple(k.key() for k in ks)
        if key not in self.cache:
            self.cache[key] = fn(*[self._arr(k) for k in ks])
        return self.cache[key]

    # primitives (array implementations from FastZeta, memoised on keys)
    def ztripK(self, k):
        key = ("z",) + k.key()
        if key not in self.cache:
            self.cache[key] = F.ZE.zeta_triplet(self._arr(k))
        return self.cache[key]

    def zeta1K(self, k):
        return self.ztripK(k)[0]

    def lzK(self, k):
        return self.ztripK(k)[1]

    def dlzK(self, k):
        return self.ztripK(k)[2]

    def AK(self, x):
        return self._memo("A", super().A, x)

    def BK(self, x):
        return self._memo("B", super().B, x)

    def QK(self, x, y):
        return self._memo("Q", super().Q, x, y)

    def B1K(self, x, y):
        return self._memo("B1", super().B1, x, y)

    def B2K(self, a, b1, b2, b3):
        return self._memo("B2", super().B2, a, b1, b2, b3)

    def B3K(self, a1, a2, b1, b2):
        return self._memo("B3", super().B3, a1, a2, b1, b2)

    def B4K(self, a1, a2, b1, b2):
        return self._memo("B4", super().B4, a1, a2, b1, b2)

    def S13K(self, a, b1, b2, b3):
        return self._memo("S13", super().S13, a, b1, b2, b3)

    def AstarK(self, a1, a2, b1, b2):
        return self._memo("As", super().Astar, a1, a2, b1, b2)

    # composites
    def P1coreK(self, x):
        key = ("P1",) + x.key()
        if key not in self.cache:
            self.cache[key] = self.AK(x) * self.zeta1K(x) * self.zeta1K(-x)
        return self.cache[key]

    def P2K(self, x):
        key = ("P2",) + x.key()
        if key not in self.cache:
            self.cache[key] = self.dlzK(x) - self.BK(x)
        return self.cache[key]

    def P3K(self, a, b, c):
        key = ("P3",) + a.key() + b.key() + c.key()
        if key not in self.cache:
            self.cache[key] = self.B1K(a + b, a + c) + self.lzK(a + c) - self.lzK(c - b)
        return self.cache[key]

    # pieces on (K, coefficient-vector) arguments
    def J11q(self, a, b):
        x = a[0] + b[0]
        return [(a[1] + b[1], lambda: self.P1coreK(x)), (0 * a[1], lambda: self.P2K(x))]

    def J12q(self, a, b1, b2):
        A, B1, B2 = a[0], b1[0], b2[0]
        return [(0 * a[1], lambda: self.QK(A + B1, A + B2)),
                (a[1] + b1[1], lambda: -self.P1coreK(A + B1) * self.P3K(A, B1, B2)),
                (a[1] + b2[1], lambda: -self.P1coreK(A + B2) * self.P3K(A, B2, B1))]

    def J13q(self, a, b1, b2, b3):
        A, Bs, bb = a[0], [b1[0], b2[0], b3[0]], (b1, b2, b3)
        out = [(0 * a[1], lambda: self.S13K(A, *Bs))]
        for i, j, k in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
            out.append((a[1] + bb[i][1], (lambda i=i, j=j, k=k: self.P1coreK(A + Bs[i]) * (
                self.P3K(A, Bs[i], Bs[j]) * self.P3K(A, Bs[i], Bs[k]) - self.B2K(A, Bs[i], Bs[j], Bs[k])))))
        return out

    def J22q(self, a1, a2, b1, b2):
        A1, A2, B1, B2 = a1[0], a2[0], b1[0], b2[0]
        z = self.zeta1K
        out = [(0 * a1[1], lambda: self.P2K(A1 + B1) * self.P2K(A2 + B2) + self.P2K(A1 + B2) * self.P2K(A2 + B1)
                - self.B4K(A1, A2, B1, B2))]
        out.append((a1[1] + a2[1] + b1[1] + b2[1], lambda: self.AstarK(A1, A2, B1, B2)
                    * z(A1 + B1) * z(A1 + B2) * z(A2 + B1) * z(A2 + B2) * z(-A1 - B1) * z(-A1 - B2) * z(-A2 - B1) * z(-A2 - B2)
                    / (z(A1 - A2) * z(A2 - A1) * z(B1 - B2) * z(B2 - B1))))
        for x1, y1, X2, Y2 in ((a1, b1, A2, B2), (a1, b2, A2, B1), (a2, b1, A1, B2), (a2, b2, A1, B1)):
            X1, Y1 = x1[0], y1[0]
            out.append((x1[1] + y1[1], (lambda X1=X1, Y1=Y1, X2=X2, Y2=Y2: self.P1coreK(X1 + Y1) * (
                self.P2K(X2 + Y2) - self.B3K(X1, X2, Y1, Y2) + self.P3K(X1, Y1, Y2) * self.P3K(Y1, X1, X2)))))
        return out

    def Jq(self, A, B):
        if len(A) > len(B):
            A, B = B, A
        return {(1, 1): self.J11q, (1, 2): self.J12q, (1, 3): self.J13q, (2, 2): self.J22q}[(len(A), len(B))](*A, *B)

    def connected(self, d1, d2, r, nonosc_only=False):
        r = np.asarray(r, float)
        sg = 2 * math.pi / self.ell
        self.rt = r * sg
        self.cache = {}
        base = [-d1 / 2 * sg, d1 / 2 * sg, -d2 / 2 * sg, d2 / 2 * sg]
        crs = [0, 0, 1, 1]
        xs_num = [np.full(r.shape, base[0]), np.full(r.shape, base[1]), self.rt + base[2], self.rt + base[3]]
        osc = np.zeros(r.shape, complex)
        non = np.full(r.shape, self.ell ** 4, complex)
        for P, M in C.index_terms(4):
            A = []
            for p in P:
                c = np.zeros(4, dtype=int)
                c[p] = 1
                A.append((K(base[p], crs[p]), c))
            B = []
            for m in M:
                c = np.zeros(4, dtype=int)
                c[m] = -1
                B.append((K(-base[m], -crs[m]), c))
            pref = self.ell ** (4 - len(P) - len(M))
            for c, fn in self.Jq(A, B):
                is_osc = int(c[2]) + int(c[3]) != 0
                if is_osc and nonosc_only:
                    continue
                phase = sum(int(ck) * xk for ck, xk in zip(c, xs_num))
                term = pref * fn() * np.exp(-self.ell * 1j * phase)
                if is_osc:
                    osc += term
                else:
                    non += term
        non -= self.R2(d1) * self.R2(d2) * self.ell ** 4
        return osc / self.ell ** 4, non / self.ell ** 4
