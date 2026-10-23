"""High-precision path of the ratios construction (round 76; post-hoc construction change, l6/N6_STAGE_C.md).

ratios_t5.Model evaluates in complex double. Near coincident points the z-factors 1/(1 − e^{−x}) (U(N)) or ζ(1 + x)
(ζ) are ~1/x and the (S, T) terms cancel; at a pair 10⁻³ apart the double result carries ~3·10⁻⁸ absolute error where
ρ₆ is 10⁻⁶–10⁻¹⁸ (stage (c) U(N) gate, f73f3895). This module is the same construction, term for term, in mpmath
(mp.dps = 40), one configuration at a time, with the same (S, T) enumeration, the same phase filter option, the same
θ grids and prime groups for 𝒜_ζ.

Dispatch (ratios_t6.rho_auto): a configuration whose smallest pairwise separation (unfolded units) is below DELTA_TH
is evaluated here; at or above it, by ratios_t5.Model in double. ratios_t6.guard refuses below-threshold evaluation in
double (raises). DELTA_TH is declared before any run: 0.1 unit spacings.
"""
import itertools
import math

import mpmath as mp

DPS = 40
DELTA_TH = 0.1


class JetsMP:
    """Multilinear jets as Python lists of mp numbers; component S (bitmask) = coefficient of Π_{i∈S} ε_i."""

    def __init__(self, n):
        self.n = n
        self.K = 1 << n
        self.pairs = [(S, T) for S in range(self.K) for T in range(self.K) if T & S == T]

    def const(self, v):
        out = [mp.mpc(0)] * self.K
        out[0] = mp.mpc(v)
        return out

    def var(self, v, i, sign=1):
        out = self.const(v)
        out[1 << i] = mp.mpc(sign)
        return out

    @staticmethod
    def add(a, b):
        return [x + y for x, y in zip(a, b)]

    @staticmethod
    def scale(a, c):
        return [x * c for x in a]

    def mul(self, a, b):
        out = [mp.mpc(0)] * self.K
        for S, T in self.pairs:
            at = a[T]
            if at:
                bt = b[S ^ T]
                if bt:
                    out[S] += at * bt
        return out

    def apply(self, x, derivs):
        N = list(x)
        N[0] = mp.mpc(0)
        out = self.const(derivs[0])
        P = self.const(1)
        for k in range(1, self.n + 1):
            P = self.mul(P, N)
            if not any(P):
                break
            if k < len(derivs) and derivs[k] != 0:
                out = self.add(out, self.scale(P, derivs[k] / math.factorial(k)))
        return out

    def exp(self, x):
        e = mp.exp(x[0])
        return self.apply(x, [e] * (self.n + 1))

    def log(self, x):
        x0 = x[0]
        d = [mp.log(x0)] + [(-1) ** (k + 1) * math.factorial(k - 1) / x0 ** k for k in range(1, self.n + 1)]
        return self.apply(x, d)

    def inv(self, x):
        x0 = x[0]
        return self.apply(x, [(-1) ** k * math.factorial(k) / x0 ** (k + 1) for k in range(self.n + 1)])


def _support(x):
    bits = 0
    for S in range(1, len(x)):
        if x[S]:
            bits |= S
    return bin(bits).count("1")


def zeta_d2(x0):
    s = 1 + x0
    return [mp.zeta(s), mp.zeta(s, 1, 1), mp.zeta(s, 1, 2)]


def invzeta_d2(x0):
    if abs(x0) < mp.mpf(10) ** (-(DPS - 5)):
        return [mp.mpc(0), mp.mpc(1), -2 * mp.euler]
    g0, g1, g2 = zeta_d2(x0)
    h0 = 1 / g0
    return [h0, -g1 * h0 * h0, 2 * g1 * g1 * h0 ** 3 - g2 * h0 * h0]


class ModelMP:
    """kind 'U' (L = N) or 'zeta' (L = ℓ, primes p ≤ pmax), as ratios_t5.Model, in mpmath."""

    def __init__(self, kind, L, pmax=None):
        mp.mp.dps = DPS
        self.kind, self.L = kind, mp.mpf(L)
        if kind == "zeta":
            p = [q for q in range(2, pmax + 1) if all(q % d for d in range(2, int(q ** 0.5) + 1))]
            self.groups = []
            for sel, nth in ((lambda q: q < 30, 128), (lambda q: q >= 30, 48)):
                pp = [q for q in p if sel(q)]
                if pp:
                    self.groups.append(([mp.mpf(q) for q in pp], [mp.log(q) for q in pp],
                                        [mp.expjpi(2 * mp.mpf(k) / nth) for k in range(nth)]))

    def zfac(self, J, x, inverse):
        if self.kind == "U":
            e = mp.exp(-x[0])
            one_minus = J.apply(x, [1 - e] + [-((-1) ** k) * e for k in range(1, J.n + 1)])
            return one_minus if inverse else J.inv(one_minus)
        if _support(x) > 2:
            raise ValueError("a ζ factor with more than two variables")
        if not inverse and abs(x[0]) < mp.mpf(10) ** (-(DPS - 5)):
            raise ValueError("ζ(1 + 0) in a numerator")
        return J.apply(x, invzeta_d2(x[0]) if inverse else zeta_d2(x[0]))

    def arith(self, J, AA, BB, Cc, D):
        tot = J.const(0)
        jet_of = lambda el: J.var(el[0], el[1], el[2]) if el[1] is not None else J.const(el[0])   # noqa: E731
        Aj, Bj = [jet_of(a) for a in AA], [jet_of(b) for b in BB]
        Cj, Dj = [J.const(c) for c in Cc], [J.const(d) for d in D]
        for pp, lp, e in self.groups:
            for p, l in zip(pp, lp):
                # Z_p factors: Σ ± log(1 − p^{−1−x−y})
                lz = J.const(0)
                for X, Y, sg in ((Aj, Bj, 1), (Cj, Dj, 1), (Aj, Dj, -1), (Bj, Cj, -1)):
                    for x in X:
                        for y in Y:
                            xy = J.add(x, y)
                            u = mp.exp(-(1 + xy[0]) * l)
                            f = J.apply(xy, [mp.log(1 - u), l * u / (1 - u), -l * l * u / (1 - u) ** 2])
                            lz = J.add(lz, J.scale(f, sg))
                # θ part: mean over θ of Π factors, built componentwise
                nth = len(e)
                comps = {0: [mp.mpc(1)] * nth}
                for c in Cc:
                    q = mp.exp(-(mp.mpf(0.5) + c) * l)
                    comps[0] = [v * (1 - mp.conj(t) * q) for v, t in zip(comps[0], e)]
                for d in D:
                    q = mp.exp(-(mp.mpf(0.5) + d) * l)
                    comps[0] = [v * (1 - t * q) for v, t in zip(comps[0], e)]
                for (v, i, sg), conj_ph in [(a, True) for a in AA] + [(b, False) for b in BB]:
                    base = mp.exp(-(mp.mpf(0.5) + v) * l)
                    qv = [(mp.conj(t) if conj_ph else t) * base for t in e]
                    f = [1 / (1 - q) for q in qv]
                    if i is None:
                        comps = {S: [a * b for a, b in zip(c, f)] for S, c in comps.items()}
                        continue
                    df = [-q * l / (1 - q) ** 2 * sg for q in qv]
                    new = {}
                    for S, c in comps.items():
                        new[S] = [a * b for a, b in zip(c, f)]
                        new[S | (1 << i)] = [a * b for a, b in zip(c, df)]
                    comps = new
                mean = [mp.mpc(0)] * J.K
                for S, c in comps.items():
                    mean[S] = mp.fsum(c) / nth
                tot = J.add(tot, J.add(lz, J.log(mean)))
        return tot

    def ratio_jet(self, J, A, B, Aidx=None, Bidx=None, clusterB=None, keep=None):
        nA = len(A)
        Cc, D = list(A), list(B)
        out = J.const(0)
        for k in range(0, min(len(A), len(B)) + 1):
            for S in itertools.combinations(range(nA), k):
                for T in itertools.combinations(range(len(B)), k):
                    if keep is not None:
                        cB = sum(1 for i in S if Aidx[i] in clusterB) - sum(1 for j in T if Bidx[j] in clusterB)
                        if not keep(cB):
                            continue
                    Sbar = [(A[i], i, 1) for i in range(nA) if i not in S]
                    Tm = [(-B[j], nA + j, -1) for j in T]
                    Tbar = [(B[j], nA + j, 1) for j in range(len(B)) if j not in T]
                    Sm = [(-A[i], i, -1) for i in S]
                    AA, BB = Sbar + Tm, Tbar + Sm
                    jet = lambda el: J.var(el[0], el[1], el[2])               # noqa: E731
                    lin = J.const(0)
                    for i in S:
                        lin = J.add(lin, J.var(A[i], i, 1))
                    for j in T:
                        lin = J.add(lin, J.var(B[j], nA + j, 1))
                    term = J.exp(J.scale(lin, -self.L))
                    for a in AA:
                        for b in BB:
                            term = J.mul(term, self.zfac(J, J.add(jet(a), jet(b)), False))
                    for c in Cc:
                        for d in D:
                            term = J.mul(term, self.zfac(J, J.const(c + d), False))
                    for a in AA:
                        for d in D:
                            term = J.mul(term, self.zfac(J, J.add(jet(a), J.const(d)), True))
                    for b in BB:
                        for c in Cc:
                            term = J.mul(term, self.zfac(J, J.add(jet(b), J.const(c)), True))
                    if self.kind == "zeta":
                        term = J.mul(term, J.exp(self.arith(J, AA, BB, Cc, D)))
                    out = J.add(out, term)
        return out

    def R(self, xs, clusterB=None, keep=None):
        n = len(xs)
        tot = self.L ** n
        idx = range(n)
        for kp in range(1, n + 1):
            for P in itertools.combinations(idx, kp):
                rest = [i for i in idx if i not in P]
                for km in range(1, len(rest) + 1):
                    for M in itertools.combinations(rest, km):
                        J = JetsMP(kp + km)
                        v = self.ratio_jet(J, [1j * xs[p] for p in P], [-1j * xs[m] for m in M], list(P), list(M),
                                           clusterB, keep)[J.K - 1]
                        tot += self.L ** (n - kp - km) * v
        return tot

    def rho(self, ds, clusterB=None, keep=None):
        """ds: one configuration (sequence of floats, unfolded units)."""
        xs = [2 * mp.pi * mp.mpf(d) / self.L for d in ds]
        return self.R(xs, clusterB, keep) / self.L ** len(ds)
