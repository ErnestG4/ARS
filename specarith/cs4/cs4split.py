"""CS08 correlations as pieces, for the short/long split (G_S_DESIGN.md §3).

Every J* is rewritten as Σ (coefficient) · e^{−L·Φ}, with Φ a linear form in the arguments. Arguments are ±i·x_k,
carried as (value, coefficient vector over the points), so each piece knows its phase as an integer vector c with
Φ = i·Σ c_k x_k. R_n = L^n + Σ_{P,M} L^{n−|P|−|M|} Σ_pieces coef · e^{−L·Φ}. Pieces must re-sum to cs4lib's gated
R_n exactly (check_pieces).

For two pairs (x₁, x₂) = (−d₁/2, d₁/2) and (x₃, x₄) = (r − d₂/2, r + d₂/2), a piece oscillates in r (once per mean
spacing, the ℓ- or N-phase) iff c₃ + c₄ ≠ 0. Units: points in angle (U(N)) or raw t (ζ); see to_points().
"""
import math

import mpmath as mp
import numpy as np

import cs4lib as C


def arg(sign, k, x, n):
    c = np.zeros(n, dtype=int)
    c[k] = sign
    return (sign * 1j * x, c)


def phase(*args):
    return sum(a[1] for a in args)


def val(*args):
    return sum(a[0] for a in args)


class PiecesMixin:
    def Jp(self, A, B):
        if len(A) > len(B):
            A, B = B, A
        k = (len(A), len(B))
        if k == (1, 1):
            return self.J11p(A[0], B[0])
        if k == (1, 2):
            return self.J12p(A[0], B[0], B[1])
        if k == (1, 3):
            return self.J13p(A[0], B[0], B[1], B[2])
        if k == (2, 2):
            return self.J22p(A[0], A[1], B[0], B[1])
        raise ValueError(k)

    def R_pieces(self, xs):
        """[(c vector, value)] with R = L^n + Σ value·exp(−L·i·(c·x)) (the L^{n−|P|−|M|} factor folded into value)."""
        n = len(xs)
        out = []
        for P, M in C.index_terms(n):
            A = [arg(+1, p, xs[p], n) for p in P]
            B = [arg(-1, m, xs[m], n) for m in M]
            pref = mp.mpf(self.L) ** (n - len(P) - len(M))
            out += [(c, pref * v) for c, v in self.Jp(A, B)]
        return out

    def R_from_pieces(self, xs):
        tot = mp.mpf(self.L) ** len(xs)
        for c, v in self.R_pieces(xs):
            tot += v * mp.exp(-self.L * 1j * sum(int(ck) * xk for ck, xk in zip(c, xs)))
        return tot


class RMTp(PiecesMixin, C.RMT):
    def J11p(self, a, b):
        x = val(a, b)
        return [(phase(a, b), self.z(x) * self.z(-x)), (0 * phase(a, b), self.dzz(x))]

    def J12p(self, a, b1, b2):
        out = []
        for bi, bj in ((b1, b2), (b2, b1)):
            x = val(a, bi)
            out.append((phase(a, bi), self.z(x) * self.z(-x) * (self.zz(val(bj) - val(bi)) - self.zz(val(bj) + val(a)))))
        return out

    def J13p(self, a, b1, b2, b3):
        out = []
        for bi, bj, bk in ((b1, b2, b3), (b2, b1, b3), (b3, b1, b2)):
            x = val(a, bi)
            out.append((phase(a, bi), self.z(x) * self.z(-x) * (self.zz(val(bj) - val(bi)) - self.zz(val(bj) + val(a)))
                        * (self.zz(val(bk) - val(bi)) - self.zz(val(bk) + val(a)))))
        return out

    def J22p(self, a1, a2, b1, b2):
        z, zz, dzz = self.z, self.zz, self.dzz
        A1, A2, B1, B2 = val(a1), val(a2), val(b1), val(b2)
        zero = 0 * phase(a1, b1)
        out = [(zero, dzz(A1 + B1) * dzz(A2 + B2) + dzz(A1 + B2) * dzz(A2 + B1))]
        for (ai, Ai), (bj, Bj), Ao, Bo in (((a1, A1), (b1, B1), A2, B2), ((a1, A1), (b2, B2), A2, B1),
                                           ((a2, A2), (b1, B1), A1, B2), ((a2, A2), (b2, B2), A1, B1)):
            out.append((phase(ai, bj), z(Ai + Bj) * z(-Ai - Bj) * (dzz(Ao + Bo) + (zz(Ao - Ai) - zz(Ao + Bj)) * (zz(Bo - Bj) - zz(Bo + Ai)))))
        num = 1
        for Ax in (A1, A2):
            for Bx in (B1, B2):
                num *= z(Ax + Bx) * z(-Ax - Bx)
        out.append((phase(a1, a2, b1, b2), num / (z(A1 - A2) * z(A2 - A1) * z(B1 - B2) * z(B2 - B1))))
        return out


class Zetap(PiecesMixin, C.Zeta):
    def P1core(self, x):
        return self.A(x) * self.zeta1(x) * self.zeta1(-x)

    def J11p(self, a, b):
        x = val(a, b)
        return [(phase(a, b), self.P1core(x)), (0 * phase(a, b), self.P2(x))]

    def J12p(self, a, b1, b2):
        A, B1, B2 = val(a), val(b1), val(b2)
        return [(0 * phase(a, b1), self.Q(A + B1, A + B2)),
                (phase(a, b1), -self.P1core(A + B1) * self.P3(A, B1, B2)),
                (phase(a, b2), -self.P1core(A + B2) * self.P3(A, B2, B1))]

    def J13p(self, a, b1, b2, b3):
        A, Bs = val(a), [val(b1), val(b2), val(b3)]
        out = [(0 * phase(a, b1), self.S13(A, *Bs))]
        bb = (b1, b2, b3)
        for i, j, k in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
            out.append((phase(a, bb[i]), self.P1core(A + Bs[i]) * (self.P3(A, Bs[i], Bs[j]) * self.P3(A, Bs[i], Bs[k])
                                                                    - self.B2(A, Bs[i], Bs[j], Bs[k]))))
        return out

    def J22p(self, a1, a2, b1, b2):
        A1, A2, B1, B2 = val(a1), val(a2), val(b1), val(b2)
        zero = 0 * phase(a1, b1)
        out = [(zero, self.P2(A1 + B1) * self.P2(A2 + B2) + self.P2(A1 + B2) * self.P2(A2 + B1) - self.B4(A1, A2, B1, B2))]
        Zz = lambda X, Y, dag: mp.fprod([self.zeta1(x + y) for x in X for y in Y if not (dag and x == -y)])
        AA, BB = (A1, A2), (B1, B2)
        mA, mB = tuple(-x for x in AA), tuple(-x for x in BB)
        out.append((phase(a1, a2, b1, b2), self.Astar(A1, A2, B1, B2) * Zz(AA, BB, False) * Zz(mA, mB, False)
                    / (Zz(AA, mA, True) * Zz(BB, mB, True))))
        for (x1, X1), (y1, Y1), X2, Y2 in (((a1, A1), (b1, B1), A2, B2), ((a1, A1), (b2, B2), A2, B1),
                                           ((a2, A2), (b1, B1), A1, B2), ((a2, A2), (b2, B2), A1, B1)):
            out.append((phase(x1, y1), self.P1core(X1 + Y1) * (self.P2(X2 + Y2) - self.B3(X1, X2, Y1, Y2)
                                                               + self.P3(X1, Y1, Y2) * self.P3(Y1, X1, X2))))
        return out


def two_pairs(d1, d2, r):
    """Unit-spacing points of two pairs: (−d₁/2, d₁/2) and (r − d₂/2, r + d₂/2)."""
    return [-d1 / 2, d1 / 2, r - d2 / 2, r + d2 / 2]


def to_points(model, ds):
    """Unit-spacing coordinates → the model's variable (U(N): angle 2πd/N; ζ: raw t-difference 2πd/ℓ)."""
    return [mp.mpf(2 * math.pi * d / model.L) for d in ds]


def connected_split(model, d1, d2, r):
    """ρ₄c = ρ₄(two pairs) − ρ₂(d₁)ρ₂(d₂) in unit-spacing density (R/L^n), split into r-oscillating and non-oscillating
    sums. Returns (osc, nonosc, total)."""
    xs = to_points(model, two_pairs(d1, d2, r))
    Ln = mp.mpf(model.L)
    osc, non = mp.mpc(0), Ln ** 4
    for c, v in model.R_pieces(xs):
        term = v * mp.exp(-Ln * 1j * sum(int(ck) * xk for ck, xk in zip(c, xs)))
        if int(c[2]) + int(c[3]) != 0:
            osc += term
        else:
            non += term
    r2a = model.R(to_points(model, [0.0, d1]))
    r2b = model.R(to_points(model, [0.0, d2]))
    non -= r2a * r2b
    s = Ln ** 4
    return osc / s, non / s, (osc + non) / s


def check_pieces(n_pts=6, seed=11):
    """Pieces re-sum to the gated R_n (U(N) and ζ), and the RMT connected split re-sums to the determinant's ρ₄c."""
    rng = np.random.default_rng(seed)
    worst = {"rmt": 0.0, "zeta": 0.0, "rmt_conn": 0.0}
    R = RMTp(50)
    Z = Zetap(4.12e8, pmax=100_000)
    for _ in range(n_pts):
        for n in (2, 3, 4):
            xs = [mp.mpf(v) for v in rng.uniform(0, 3, n)]
            a, b = R.R(xs), R.R_from_pieces(xs)
            worst["rmt"] = max(worst["rmt"], float(abs(a - b) / abs(a)))
        xs = [mp.mpf(v) for v in rng.uniform(0, 3, 4)]
        a, b = Z.R(xs), Z.R_from_pieces(xs)
        worst["zeta"] = max(worst["zeta"], float(abs(a - b) / abs(a)))
        d1, d2, r = rng.uniform(0.2, 1.5), rng.uniform(0.2, 1.5), rng.uniform(3, 20)
        osc, non, tot = connected_split(R, d1, d2, r)
        pts = np.array(two_pairs(d1, d2, r))
        K = lambda D: np.where(np.abs(D) > 1e-14, np.sin(np.pi * D) / (50 * np.sin(np.pi * D / 50) + (np.abs(D) <= 1e-14)), 1.0)
        det4 = np.linalg.det(K(pts[:, None] - pts[None, :]))
        det2 = lambda d: 1 - K(np.array(d)) ** 2
        ref = det4 - det2(d1) * det2(d2)
        worst["rmt_conn"] = max(worst["rmt_conn"], float(abs(mp.re(tot) - ref)))
    return worst


if __name__ == "__main__":
    print(check_pieces())
