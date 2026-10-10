"""Vectorised CS08 ζ four-point pieces over arrays of the pair separation r (fixed in-pair offsets d₁, d₂), mirroring
cs4lib.Zeta / cs4split.Zetap formula by formula. Purpose: the long-range quadrature of G_S_DESIGN.md §3, where the slow
30-digit evaluator (~3 s per point) is too slow. Validated against the slow evaluator pointwise (validate()), which is
Will's sparse direct check (twentieth round (1)).

Points (unit spacing): x₁ = −d₁/2, x₂ = d₁/2, x₃ = r − d₂/2, x₄ = r + d₂/2; ζ variable t-difference = 2πx/ℓ.
Output per r: the connected ρ₄c = (R₄ − R₂(d₁)R₂(d₂))/ℓ⁴ split into r-oscillating and non-oscillating sums (as
cs4split.connected_split). Prime sums over p ≤ pmax (default 1e5; the slow evaluator's R₄ pieces change < 1e-8 from
1e5 to 1e6), chunked over r. A*'s removable resonance (|1 − p^{b₁−b₂}| < 1e-2) is recomputed by its defining
θ-integral (64-point trapezoid; the integrand's poles sit at |u| = p^{−1/2}, so convergence is geometric).
"""
import math

import numpy as np

import cs4lib as C
import zeta_em as ZE

CHUNK = 1024


class Arg:
    """±i·x_k over the r-array: value (complex array) and integer coefficient vector over the 4 points."""
    def __init__(self, v, c):
        self.v, self.c = v, c


def mk(sign, k, x):
    c = np.zeros(4, dtype=int)
    c[k] = sign
    return Arg(sign * 1j * x, c)


class FastZeta:
    def __init__(self, t, pmax=100_000):
        self.t = t
        self.ell = math.log(t / (2 * math.pi))
        self.p = C.primes_np(pmax)
        self.lp = np.log(self.p)

    # ---- ζ pieces (arrays)
    def ztrip(self, x):
        return ZE.zeta_triplet(x)

    def zeta1(self, x):
        return self.ztrip(x)[0]

    def lz(self, x):
        return self.ztrip(x)[1]

    def dlz(self, x):
        return self.ztrip(x)[2]

    # ---- prime sums: f(P, args...) -> summand matrix (rows = r, cols = primes); summed over primes, chunked over r
    def psum(self, f, *args, prod=False):
        args = [np.broadcast_to(np.asarray(a, complex), np.broadcast(*[np.asarray(b) for b in args]).shape) for a in args]
        n = args[0].shape[0]
        out = np.empty(n, complex)
        p, lp = self.p[None, :], self.lp[None, :]
        for i in range(0, n, CHUNK):
            sub = [a[i:i + CHUNK, None] for a in args]
            P = lambda e: np.exp(e * lp)                     # p^{e}
            m = f(P, p, lp, *sub)
            out[i:i + CHUNK] = np.exp(np.log(m).sum(1)) if prod else m.sum(1)
        return out

    def A(self, x):
        return self.psum(lambda P, p, lp, x: np.exp(np.log1p(-((1 - P(-x)) ** 2) / (p - 1) ** 2)), x, prod=True)

    def B(self, x):
        return self.psum(lambda P, p, lp, x: (lp / (P(1 + x) - 1)) ** 2, x)

    def Q(self, x, y):
        return self.psum(lambda P, p, lp, x, y: -lp ** 3 * P(-(2 + x + y)) / ((1 - P(-(1 + x))) * (1 - P(-(1 + y)))), x, y)

    def B1(self, x, y):
        def f(P, p, lp, x, y):
            px, py = P(-x), P(-y)
            num = (1 - px) * (1 - px - py + P(-(1 + y))) * lp
            den = (1 - P(-(1 - x + y))) * (1 - P(-(1 + y))) * (1 - 2 / p + P(-(1 + x))) * P(2 - x + y)
            return num / den
        return self.psum(f, x, y)

    def B2(self, a, b1, b2, b3):
        def f(P, p, lp, a, b1, b2, b3):
            num = (p - 1) * P(2 * b1) * (P(a + b1) - 1) * (P(a + b1) - p) * lp ** 2
            den = (-2 * P(a + b1) + P(a + b1 + 1) + 1) ** 2 * (P(b1) - P(b2 + 1)) * (P(b1) - P(b3 + 1))
            return num / den
        return self.psum(f, a, b1, b2, b3)

    def B3(self, a1, a2, b1, b2):
        def f(P, p, lp, a1, a2, b1, b2):
            Cc = (-P(a1 + b1) + 2 * P(a1 + b1 + 1) - P(a2 + b1 + 2) - P(2 * a1 + 2 * b1 + 1) + P(a1 + a2 + 2 * b1 + 1)
                  - P(a1 + b2 + 2) + P(a2 + b2 + 2) + P(2 * a1 + b1 + b2 + 1) - 2 * P(a1 + a2 + b1 + b2 + 2)
                  + P(a1 + a2 + b1 + b2 + 3))
            k = -2 * P(a1 + b1) + P(a1 + b1 + 1) + 1
            t1 = (p - 1) ** 2 * (P(a1 + b1) - 1) ** 2 * P(a1 + b1) / ((P(a1) - P(a2 + 1)) * k ** 2 * (P(b1) - P(b2 + 1)))
            t2 = Cc / ((P(a1) - P(a2 + 1)) * k * (P(b2 + 1) - P(b1)) * (P(a2 + b2 + 1) - 1))
            t3 = 1 / (P(a2 + b2 + 1) - 1)
            return lp ** 2 * (t1 + t2 + t3)
        return self.psum(f, a1, a2, b1, b2)

    def B4(self, a1, a2, b1, b2):
        def f(P, p, lp, a1, a2, b1, b2):
            num = (3 - P(1 + a1 + b1) - P(1 + a2 + b1) - P(1 + a1 + b2) - P(1 + a2 + b2) + P(2 + a1 + a2 + b1 + b2)) * lp ** 4
            den = (P(1 + a1 + b1) - 1) * (P(1 + a2 + b1) - 1) * (P(1 + a1 + b2) - 1) * (P(1 + a2 + b2) - 1)
            return num / den
        return self.psum(f, a1, a2, b1, b2)

    def S13(self, a, b1, b2, b3):
        def f(P, p, lp, a, b1, b2, b3):
            zp = lambda x: 1 / (1 - P(-x))
            return -(zp(1 + a + b1) * zp(1 + a + b2) * zp(1 + a + b3) * lp ** 4 * P(-(3 + 3 * a + b1 + b2 + b3)))
        return self.psum(f, a, b1, b2, b3)

    def Astar(self, a1, a2, b1, b2):
        def f(P, p, lp, a1, a2, b1, b2):
            zp = lambda x: 1 / (1 - P(-x))
            Zp = lambda X, Y: np.prod([1 / zp(1 + x + y) for x in X for y in Y], axis=0)
            A_, B_ = (a1, a2), (b1, b2)
            mA, mB = tuple(-x for x in A_), tuple(-x for x in B_)
            pref = Zp(A_, B_) * Zp(mA, mB) / (Zp(A_, mA) * Zp(B_, mB))
            T1 = zp(1 - a1 - b1) * zp(1 - a2 - b1) * zp(b2 - b1) / (zp(1) * zp(-a1 - b1) * zp(-a2 - b1) * zp(1 + b2 - b1))
            T2 = zp(1 - a1 - b2) * zp(1 - a2 - b2) * zp(b1 - b2) / (zp(1) * zp(-a1 - b2) * zp(-a2 - b2) * zp(1 + b1 - b2))
            fac = pref * P(-(a1 + a2 + b1 + b2)) * (1 - T1 - T2)
            q = P(b1 - b2)
            bad = np.abs(1 - q) < 1e-2
            if bad.any():
                rows, cols = np.nonzero(bad)
                pp = np.broadcast_to(p, bad.shape)[rows, cols]
                A1, A2 = np.broadcast_to(a1, bad.shape)[rows, cols], np.broadcast_to(a2, bad.shape)[rows, cols]
                Bb1, Bb2 = np.broadcast_to(b1, bad.shape)[rows, cols], np.broadcast_to(b2, bad.shape)[rows, cols]
                th = np.arange(64) / 64
                e = np.exp(2j * np.pi * th)[None, :]
                pw = lambda ex: np.exp(ex[:, None] * np.log(pp)[:, None])
                g = 1.0
                for b in (Bb1, Bb2):
                    g = g / (1 - np.conj(e) * pw(-0.5 + b))
                for a in (A1, A2):
                    g = g / (1 - e * pw(-0.5 + a))
                for a in (A1, A2):
                    g = g * (1 - np.conj(e) * pw(-0.5 - a))
                for b in (Bb1, Bb2):
                    g = g * (1 - e * pw(-0.5 - b))
                integ = g.mean(1)
                fac[rows, cols] = pref[rows, cols] * integ if np.ndim(pref) else pref * integ
            return fac
        return self.psum(f, a1, a2, b1, b2, prod=True)

    # ---- CS08 §5 building blocks
    def P1core(self, x):
        z0p = self.zeta1(x)
        z0m = self.zeta1(-x)
        return self.A(x) * z0p * z0m

    def P2(self, x):
        return self.dlz(x) - self.B(x)

    def P3(self, a, b, c):
        return self.B1(a + b, a + c) + self.lz(a + c) - self.lz(c - b)

    def J11p(self, a, b):
        x = a.v + b.v
        return [(a.c + b.c, self.P1core(x)), (0 * a.c, self.P2(x))]

    def J12p(self, a, b1, b2):
        A, B1, B2 = a.v, b1.v, b2.v
        return [(0 * a.c, self.Q(A + B1, A + B2)),
                (a.c + b1.c, -self.P1core(A + B1) * self.P3(A, B1, B2)),
                (a.c + b2.c, -self.P1core(A + B2) * self.P3(A, B2, B1))]

    def J13p(self, a, b1, b2, b3):
        A, Bs, bb = a.v, [b1.v, b2.v, b3.v], (b1, b2, b3)
        out = [(0 * a.c, self.S13(A, *Bs))]
        for i, j, k in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
            out.append((a.c + bb[i].c, self.P1core(A + Bs[i]) * (self.P3(A, Bs[i], Bs[j]) * self.P3(A, Bs[i], Bs[k])
                                                                  - self.B2(A, Bs[i], Bs[j], Bs[k]))))
        return out

    def J22p(self, a1, a2, b1, b2):
        A1, A2, B1, B2 = a1.v, a2.v, b1.v, b2.v
        out = [(0 * a1.c, self.P2(A1 + B1) * self.P2(A2 + B2) + self.P2(A1 + B2) * self.P2(A2 + B1) - self.B4(A1, A2, B1, B2))]
        z = self.zeta1
        num = z(A1 + B1) * z(A1 + B2) * z(A2 + B1) * z(A2 + B2) * z(-A1 - B1) * z(-A1 - B2) * z(-A2 - B1) * z(-A2 - B2)
        den = z(A1 - A2) * z(A2 - A1) * z(B1 - B2) * z(B2 - B1)          # Z† drops the α + β = 0 factors
        out.append((a1.c + a2.c + b1.c + b2.c, self.Astar(A1, A2, B1, B2) * num / den))
        for x1, y1, X2, Y2 in ((a1, b1, A2, B2), (a1, b2, A2, B1), (a2, b1, A1, B2), (a2, b2, A1, B1)):
            X1, Y1 = x1.v, y1.v
            out.append((x1.c + y1.c, self.P1core(X1 + Y1) * (self.P2(X2 + Y2) - self.B3(X1, X2, Y1, Y2)
                                                           + self.P3(X1, Y1, Y2) * self.P3(Y1, X1, X2))))
        return out

    def Jp(self, A, B):
        if len(A) > len(B):
            A, B = B, A
        k = (len(A), len(B))
        return {(1, 1): lambda: self.J11p(*A, *B), (1, 2): lambda: self.J12p(*A, *B),
                (1, 3): lambda: self.J13p(*A, *B), (2, 2): lambda: self.J22p(*A, *B)}[k]()

    def R2(self, d):
        """ρ₂ at unit-spacing separation d (scalar), as R₂/ℓ²."""
        x = 2 * math.pi * d / self.ell
        a, b = Arg(np.array([1j * x]), np.array([1, -1, 0, 0])), None
        J = self.J11p(Arg(np.array([1j * x]), np.array([1, 0, 0, 0])), Arg(np.array([0j]), np.array([0, -1, 0, 0])))
        J2 = self.J11p(Arg(np.array([0j]), np.array([0, 1, 0, 0])), Arg(np.array([-1j * x]), np.array([-1, 0, 0, 0])))
        tot = self.ell ** 2
        for c, v in J + J2:
            ph = 1j * x * (c[0])                               # points (x, 0): Φ = i(c₀·x + c₁·0)
            tot = tot + v[0] * np.exp(-self.ell * ph)
        return tot / self.ell ** 2

    def connected(self, d1, d2, r):
        """r: real array (unit spacing). Returns (osc, nonosc) arrays of ρ₄c in unit-spacing density."""
        r = np.asarray(r, float)
        s = 2 * math.pi / self.ell
        xs = [np.full(r.shape, -d1 / 2 * s), np.full(r.shape, d1 / 2 * s), (r - d2 / 2) * s, (r + d2 / 2) * s]
        osc = np.zeros(r.shape, complex)
        non = np.full(r.shape, self.ell ** 4, complex)
        for P, M in C.index_terms(4):
            A = [mk(+1, p, xs[p]) for p in P]
            B = [mk(-1, m, xs[m]) for m in M]
            pref = self.ell ** (4 - len(P) - len(M))
            for c, v in self.Jp(A, B):
                phase = sum(int(ck) * xk for ck, xk in zip(c, xs))
                term = pref * v * np.exp(-self.ell * 1j * phase)
                if int(c[2]) + int(c[3]) != 0:
                    osc += term
                else:
                    non += term
        r2 = self.R2(d1) * self.R2(d2) * self.ell ** 4
        non -= r2
        return osc / self.ell ** 4, non / self.ell ** 4


def validate(t=4.12e8, d1=0.5, d2=0.5, rs=(2.0, 5.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0)):
    import mpmath as mp
    import cs4split as S
    F = FastZeta(t)
    osc, non = F.connected(d1, d2, np.array(rs))
    Z = S.Zetap(t, pmax=100_000)
    rows = []
    for k, r in enumerate(rs):
        o, n_, _ = S.connected_split(Z, d1, d2, r)
        rows.append(dict(r=r, fast_non=non[k].real, slow_non=float(mp.re(n_)), fast_osc=osc[k].real, slow_osc=float(mp.re(o)),
                         err_non=abs(non[k] - complex(n_)), err_osc=abs(osc[k] - complex(o))))
    return rows


if __name__ == "__main__":
    for row in validate():
        print({k: (round(v, 10) if isinstance(v, float) else v) for k, v in row.items()})
