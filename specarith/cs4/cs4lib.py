"""Conrey–Snaith 2008 (CS08: "Correlations of eigenvalues and Riemann zeros", CNTP 2 (2008) 477; arXiv 0803.2795 v1,
LaTeX source cached at ~/specarith_lit_cache/ph2_next_order/src_0803.2795) §5: the n = 2, 3, 4 correlation functions,
transcribed for U(N) (RMT; a theorem) and for ζ (conjectural, via the ratios conjecture), from one assembly.

Assembly (CS08 §5, R_{N,n} and R_{ζ,t,n} for n = 2, 3, 4): R_n(x_1…x_n) = Σ over disjoint non-empty index sets P, M of
L^{n − |P| − |M|} · J*({i x_p}_{p∈P}; {−i x_m}_{m∈M}), where L = N (RMT) or ℓ = log(t/2π) (ζ), plus L^n. J* is
symmetric under swapping its two arguments (CS08 writes the |P| > |M| terms with the singleton first, e.g.
J*(−iw; iu, iv)), and is needed for set sizes (1,1), (1,2), (1,3), (2,2). Term counts are asserted against the paper's
explicit lists: n = 2: 2; n = 3: 6 + 6; n = 4: 12 + 24 + 8 + 6.

Normalisation (CS08 §5): ∫_{U(N)} Σ* f(θ_{j_1}…θ_{j_n}) dX = (2π)^{−n} ∫_{[0,2π]^n} R_{N,n} f, so R_{N,n} = det[S(x_i − x_j)] with
S(x) = sin(Nx/2)/sin(x/2) and S(0) = N; and Σ_{γ's ≤ T} f = (2π)^{−n} ∫ (1/T)∫ R_{ζ,t,n} dt f + O(T^{1/2+ε}).

Transcription notes:
- B_4's printed denominator has a misplaced parenthesis, "(p^{1+a_2+b_1})−1)"; read as (p^{1+a_2+b_1} − 1), the
  pattern of the other three factors.
- Z_ζ(A,B) = Π ζ(1+α+β); Z†_ζ omits the factors with α + β = 0 (CS08 eq. near line 1519 of the source); in A*,
  Z_p(X,Y) = Π z_p(1+x+y)^{-1}, including z_p(1) factors.
"""
import itertools

import mpmath as mp

mp.mp.dps = 30


# ---------------------------------------------------------------- assembly
def index_terms(n):
    """(P, M) pairs of disjoint non-empty index tuples with |P| + |M| ≤ 4 and J* defined for (min, max) sizes."""
    out = []
    idx = range(n)
    for kp in range(1, n + 1):
        for P in itertools.combinations(idx, kp):
            rest = [i for i in idx if i not in P]
            for km in range(1, len(rest) + 1):
                for M in itertools.combinations(rest, km):
                    if tuple(sorted((len(P), len(M)))) in ((1, 1), (1, 2), (1, 3), (2, 2)):
                        out.append((P, M))
    return out


EXPECTED_COUNTS = {2: {2: 2}, 3: {2: 6, 3: 6}, 4: {2: 12, 3: 24, 4: 14}}     # by |P| + |M|; n = 4, size 4: 8 + 6


def check_counts():
    for n, exp in EXPECTED_COUNTS.items():
        got = {}
        for P, M in index_terms(n):
            got[len(P) + len(M)] = got.get(len(P) + len(M), 0) + 1
        assert got == exp, (n, got, exp)
    n4 = index_terms(4)
    assert sum(1 for P, M in n4 if len(P) == 2 and len(M) == 2) == 6
    assert sum(1 for P, M in n4 if {len(P), len(M)} == {1, 3}) == 8


class Correlations:
    """Common assembly; subclasses provide L and J11, J12, J13, J22."""
    L = None

    def J(self, A, B):
        if len(A) > len(B):
            A, B = B, A
        k = (len(A), len(B))
        if k == (1, 1):
            return self.J11(A[0], B[0])
        if k == (1, 2):
            return self.J12(A[0], B[0], B[1])
        if k == (1, 3):
            return self.J13(A[0], B[0], B[1], B[2])
        if k == (2, 2):
            return self.J22(A[0], A[1], B[0], B[1])
        raise ValueError(k)

    def R(self, xs):
        n = len(xs)
        tot = mp.mpf(self.L) ** n
        for P, M in index_terms(n):
            tot += mp.mpf(self.L) ** (n - len(P) - len(M)) * self.J([1j * xs[p] for p in P], [-1j * xs[m] for m in M])
        return tot


# ---------------------------------------------------------------- U(N) (CS08 §5 "… correlation, RMT")
class RMT(Correlations):
    def __init__(self, N):
        self.N = self.L = N

    def E(self, x):
        return mp.exp(-self.N * x)

    @staticmethod
    def z(x):
        return 1 / (1 - mp.exp(-x))

    @staticmethod
    def zz(x):                                    # z'/z
        return -1 / (mp.exp(x) - 1)

    @staticmethod
    def dzz(x):                                   # (z'/z)'
        return mp.exp(x) / (mp.exp(x) - 1) ** 2

    def J11(self, a, b):
        return self.dzz(a + b) + self.E(a + b) * self.z(a + b) * self.z(-a - b)

    def J12(self, a, b1, b2):
        t = lambda bi, bj: self.E(a + bi) * self.z(a + bi) * self.z(-a - bi) * (self.zz(bj - bi) - self.zz(bj + a))
        return t(b1, b2) + t(b2, b1)

    def J13(self, a, b1, b2, b3):
        def t(bi, bj, bk):
            return (self.E(a + bi) * self.z(a + bi) * self.z(-a - bi)
                    * (self.zz(bj - bi) - self.zz(bj + a)) * (self.zz(bk - bi) - self.zz(bk + a)))
        return t(b1, b2, b3) + t(b2, b1, b3) + t(b3, b1, b2)

    def J22(self, a1, a2, b1, b2):
        zz, dzz, z, E = self.zz, self.dzz, self.z, self.E

        def D(ai, bj, ao, bo):                    # D_{ai,bj}; ao, bo = the other a, b
            return E(ai + bj) * z(ai + bj) * z(-ai - bj) * (
                dzz(ao + bo) + (zz(ao - ai) - zz(ao + bj)) * (zz(bo - bj) - zz(bo + ai)))
        num = 1
        for a in (a1, a2):
            for b in (b1, b2):
                num *= z(a + b) * z(-a - b)
        return (dzz(a1 + b1) * dzz(a2 + b2) + dzz(a1 + b2) * dzz(a2 + b1)
                + D(a1, b1, a2, b2) + D(a1, b2, a2, b1) + D(a2, b1, a1, b2) + D(a2, b2, a1, b1)
                + E(a1 + a2 + b1 + b2) * num / (z(a1 - a2) * z(a2 - a1) * z(b1 - b2) * z(b2 - b1)))


def cue_det(xs, N):
    """Exact CUE_N n-point density in CS08's normalisation: det[S(x_i − x_j)], S(x) = sin(Nx/2)/sin(x/2), S(0) = N."""
    n = len(xs)
    S = lambda x: mp.mpf(N) if x == 0 else mp.sin(N * x / 2) / mp.sin(x / 2)
    return mp.det(mp.matrix([[S(xs[i] - xs[j]) for j in range(n)] for i in range(n)]))
