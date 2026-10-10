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
  pattern of the other three factors. arXiv v1 has it in both copies (§5.6 and §5.7). The published CNTP version keeps
  it in §5.6 and fixes it in the §5.7 copy, eq. (5.49), which agrees with this reading.
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


# ---------------------------------------------------------------- ζ (CS08 §5 "… correlation, ζ"; conjectural)
# Erratum found in transcription (2026-10-10): CS08 v1 §5.6 prints A*'s local factor as p^{−Σ}(1 + T₁ + T₂). Evaluating
# its definition, Π_p Z_p(B⁻,A⁻;A,B) ∫₀¹ 𝒜_{p,θ}(B⁻,A⁻;A,B) dθ (ratios conjecture, eq. Aptheta), by residues at
# w = 0, u₁, u₂ gives p^{−Σ}(1 − T₁ − T₂): Res₀ = p^{−Σ} and p^{Σ}·Res_{u_k} = −T_k exactly. The printed form does not
# tend to 1 as p → ∞ (it is not an Euler factor); the corrected one does. Checked numerically in check_zeta.py.
# Journal check (2026-10-10, published CNTP PDF, sha256 decd4a26…; ph2/lit/NEXT_ORDER_LIT.md): the published version
# prints the same "1 +" form in both places, eq. (5.40) in §5.6 and eq. (5.45) in §5.7, with T₁ and T₂ the same fractions
# as here. Under the twentieth-round rule this is recorded as an erratum, not as an arXiv v1 typo corrected in the journal.
import numpy as np  # noqa: E402

_PR = None


def primes_np(pmax=10_000_000):
    global _PR
    if _PR is None or _PR[-1] < pmax * 0.99:
        s = np.ones(pmax + 1, dtype=bool)
        s[:2] = False
        for i in range(2, int(pmax ** 0.5) + 1):
            if s[i]:
                s[i * i::i] = False
        _PR = np.nonzero(s)[0].astype(np.float64)
    return _PR[_PR <= pmax]


class Zeta(Correlations):
    """ζ correlations at height t (ℓ = log(t/2π)). Prime sums/products over p ≤ pmax in complex double (numpy); ζ, ζ′/ζ,
    (ζ′/ζ)′ at 1 + x in mpmath. Arguments are complex scalars (in use: ±i·x with real x)."""

    def __init__(self, t, pmax=1_000_000):
        self.t = t
        self.L = self.ell = float(mp.log(mp.mpf(t) / (2 * mp.pi)))
        self.p = primes_np(pmax)
        self.lp = np.log(self.p)

    # -- ζ pieces (mpmath)
    @staticmethod
    def zeta1(x):
        return mp.zeta(1 + x)

    @staticmethod
    def lz(x):                                   # ζ′/ζ(1+x)
        s = 1 + x
        return mp.zeta(s, derivative=1) / mp.zeta(s)

    @staticmethod
    def dlz(x):                                  # (ζ′/ζ)′(1+x)
        s = 1 + x
        z0, z1, z2 = mp.zeta(s), mp.zeta(s, derivative=1), mp.zeta(s, derivative=2)
        return z2 / z0 - (z1 / z0) ** 2

    # -- prime sums/products (numpy complex), p^{−x} = exp(−x log p)
    def pw(self, x):
        return np.exp(-complex(x) * self.lp)

    def A(self, x):
        return mp.mpc(np.exp(np.sum(np.log1p(-((1 - self.pw(x)) ** 2) / (self.p - 1) ** 2))))

    def B(self, x):
        return mp.mpc(np.sum((self.lp / (self.p * np.exp(complex(x) * self.lp) - 1)) ** 2))

    def Q(self, x, y):
        p, lp = self.p, self.lp
        return mp.mpc(-np.sum(lp ** 3 * self.pw(2 + x + y) / ((1 - self.pw(1 + x)) * (1 - self.pw(1 + y)))))

    def B1(self, x, y):
        p, lp = self.p, self.lp
        px, py = self.pw(x), self.pw(y)
        num = (1 - px) * (1 - px - py + self.pw(1 + y)) * lp
        den = (1 - self.pw(1 - x + y)) * (1 - self.pw(1 + y)) * (1 - 2 / p + self.pw(1 + x)) * np.exp((2 - complex(x) + complex(y)) * lp)
        return mp.mpc(np.sum(num / den))

    def B2(self, a, b1, b2, b3):
        p, lp = self.p, self.lp
        P = lambda e: np.exp(complex(e) * lp)    # p^{e}
        num = (p - 1) * P(2 * b1) * (P(a + b1) - 1) * (P(a + b1) - p) * lp ** 2
        den = (-2 * P(a + b1) + P(a + b1 + 1) + 1) ** 2 * (P(b1) - P(b2 + 1)) * (P(b1) - P(b3 + 1))
        return mp.mpc(np.sum(num / den))

    def B3(self, a1, a2, b1, b2):
        p, lp = self.p, self.lp
        P = lambda e: np.exp(complex(e) * lp)
        C = (-P(a1 + b1) + 2 * P(a1 + b1 + 1) - P(a2 + b1 + 2) - P(2 * a1 + 2 * b1 + 1) + P(a1 + a2 + 2 * b1 + 1)
             - P(a1 + b2 + 2) + P(a2 + b2 + 2) + P(2 * a1 + b1 + b2 + 1) - 2 * P(a1 + a2 + b1 + b2 + 2)
             + P(a1 + a2 + b1 + b2 + 3))
        k = -2 * P(a1 + b1) + P(a1 + b1 + 1) + 1
        t1 = (p - 1) ** 2 * (P(a1 + b1) - 1) ** 2 * P(a1 + b1) / ((P(a1) - P(a2 + 1)) * k ** 2 * (P(b1) - P(b2 + 1)))
        t2 = C / ((P(a1) - P(a2 + 1)) * k * (P(b2 + 1) - P(b1)) * (P(a2 + b2 + 1) - 1))
        t3 = 1 / (P(a2 + b2 + 1) - 1)
        return mp.mpc(np.sum(lp ** 2 * (t1 + t2 + t3)))

    def B4(self, a1, a2, b1, b2):
        p, lp = self.p, self.lp
        P = lambda e: np.exp(complex(e) * lp)
        num = (3 - P(1 + a1 + b1) - P(1 + a2 + b1) - P(1 + a1 + b2) - P(1 + a2 + b2) + P(2 + a1 + a2 + b1 + b2)) * lp ** 4
        den = (P(1 + a1 + b1) - 1) * (P(1 + a2 + b1) - 1) * (P(1 + a1 + b2) - 1) * (P(1 + a2 + b2) - 1)   # erratum-free reading
        return mp.mpc(np.sum(num / den))

    def S13(self, a, b1, b2, b3):               # −Σ_p z_p(1+a+b1)z_p(1+a+b2)z_p(1+a+b3) log⁴p / p^{3+3a+b1+b2+b3}
        lp = self.lp
        zp = lambda x: 1 / (1 - self.pw(x))
        return mp.mpc(-np.sum(zp(1 + a + b1) * zp(1 + a + b2) * zp(1 + a + b3) * lp ** 4 * self.pw(3 + 3 * a + b1 + b2 + b3)))

    def Astar(self, a1, a2, b1, b2):
        """Corrected local factor (see erratum above): Z_p-prefactor × p^{−Σ}(1 − T₁ − T₂)."""
        zp = lambda x: 1 / (1 - self.pw(x))
        Zp = lambda X, Y: np.prod([1 / zp(1 + x + y) for x in X for y in Y], axis=0)
        A_, B_ = (a1, a2), (b1, b2)
        mA, mB = tuple(-x for x in A_), tuple(-x for x in B_)
        pref = Zp(A_, B_) * Zp(mA, mB) / (Zp(A_, mA) * Zp(B_, mB))
        z1 = zp(1)
        T1 = zp(1 - a1 - b1) * zp(1 - a2 - b1) * zp(b2 - b1) / (z1 * zp(-a1 - b1) * zp(-a2 - b1) * zp(1 + b2 - b1))
        T2 = zp(1 - a1 - b2) * zp(1 - a2 - b2) * zp(b1 - b2) / (z1 * zp(-a1 - b2) * zp(-a2 - b2) * zp(1 + b1 - b2))
        fac = pref * self.pw(a1 + a2 + b1 + b2) * (1 - T1 - T2)
        # T₁, T₂ each carry 1/(1 − q), q = p^{b₁−b₂} (|q| = 1 on the imaginary axis): a removable pole. Near q = 1 they
        # cancel catastrophically in double precision, so primes with |1 − q| < 1e-2 are recomputed in mpmath (40 digits).
        q = np.exp(complex(b1 - b2) * self.lp)
        bad = np.nonzero(np.abs(1 - q) < 1e-2)[0]
        if len(bad):
            with mp.workdps(40):
                for i in bad:
                    p = mp.mpf(int(round(self.p[i])))
                    zpm = lambda x: 1 / (1 - p ** (-mp.mpc(x)))
                    Zpm = lambda X, Y: mp.fprod([1 / zpm(1 + x + y) for x in X for y in Y])
                    prefm = Zpm(A_, B_) * Zpm(mA, mB) / (Zpm(A_, mA) * Zpm(B_, mB))
                    t1 = zpm(1 - a1 - b1) * zpm(1 - a2 - b1) * zpm(b2 - b1) / (zpm(1) * zpm(-a1 - b1) * zpm(-a2 - b1) * zpm(1 + b2 - b1))
                    t2 = zpm(1 - a1 - b2) * zpm(1 - a2 - b2) * zpm(b1 - b2) / (zpm(1) * zpm(-a1 - b2) * zpm(-a2 - b2) * zpm(1 + b1 - b2))
                    fac[i] = complex(prefm * p ** (-mp.mpc(a1 + a2 + b1 + b2)) * (1 - t1 - t2))
        return mp.mpc(np.exp(np.sum(np.log(fac))))

    # -- CS08 §5 building blocks
    def P1(self, x):
        return mp.exp(-self.ell * x) * self.A(x) * self.zeta1(x) * self.zeta1(-x)

    def P2(self, x):
        return self.dlz(x) - self.B(x)

    def P3(self, a, b, c):
        return self.B1(a + b, a + c) + self.lz(a + c) - self.lz(c - b)

    def J11(self, a, b):
        return self.P1(a + b) + self.P2(a + b)

    def J12(self, a, b1, b2):
        return self.Q(a + b1, a + b2) - self.P1(a + b1) * self.P3(a, b1, b2) - self.P1(a + b2) * self.P3(a, b2, b1)

    def J13(self, a, b1, b2, b3):
        W1 = lambda bi, bj, bk: self.P1(a + bi) * (self.P3(a, bi, bj) * self.P3(a, bi, bk) - self.B2(a, bi, bj, bk))
        return self.S13(a, b1, b2, b3) + W1(b1, b2, b3) + W1(b2, b1, b3) + W1(b3, b1, b2)

    def J22(self, a1, a2, b1, b2):
        def W(x1, y1, x2, y2):
            return self.P1(x1 + y1) * (self.P2(x2 + y2) - self.B3(x1, x2, y1, y2)
                                      + self.P3(x1, y1, y2) * self.P3(y1, x1, x2))
        Zz = lambda X, Y, dag: mp.fprod([self.zeta1(x + y) for x in X for y in Y if not (dag and x == -y)])
        A_, B_ = (a1, a2), (b1, b2)
        mA, mB = tuple(-x for x in A_), tuple(-x for x in B_)
        big = (mp.exp(-self.ell * (a1 + a2 + b1 + b2)) * self.Astar(a1, a2, b1, b2) * Zz(A_, B_, False) * Zz(mA, mB, False)
               / (Zz(A_, mA, True) * Zz(B_, mB, True)))
        return (self.P2(a1 + b1) * self.P2(a2 + b2) + self.P2(a1 + b2) * self.P2(a2 + b1) - self.B4(a1, a2, b1, b2) + big
                + W(a1, b1, a2, b2) + W(a1, b2, a2, b1) + W(a2, b1, a1, b2) + W(a2, b2, a1, b1))
