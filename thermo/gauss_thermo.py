"""
thermo/gauss_thermo.py — arbitrary-precision thermodynamic formalism of the Gauss map.

Extends the Session-K CP2 operator (`sessionK/coprimary2_transfer_operator.py`, float64
Chebyshev-Lobatto collocation, validated at s=1) to arbitrary precision and arbitrary
complex s. Same operator, new precision path — NOT a new instrument.

    (L_s f)(x) = sum_{n>=1}    (n+x)^{-2s} f(1/(n+x))      full Gauss alphabet
    (L_s f)(x) = sum_{n in A}  (n+x)^{-2s} f(1/(n+x))      restricted alphabet A

Pressure  P(s) = log(leading eigenvalue of L_s).  beta = s is the inverse temperature for
the geometric potential -beta*log|G'|, with G the Gauss map and |G'| = 1/x^2 — so this
family already IS the thermodynamic family; there is no new potential to invent.

Sign convention: P(1) = 0 and the Gauss-map Lyapunov exponent is lambda = -P'(1), so
P is DECREASING at s=1. (Matches CP2's `lyap = -dlog`.)

---------------------------------------------------------------------------------------
METHOD — why this discretization rather than the float64 one
---------------------------------------------------------------------------------------
Collocation on N+1 Chebyshev-Lobatto nodes of [0,1]. The interpolant through those nodes
is EXACTLY a polynomial of degree N, so for each Lagrange basis polynomial
L_i(y) = sum_k c[i,k] y^k the operator's infinite sum has a closed form in Hurwitz zeta:

    sum_{n>Ne} (n+x)^{-2s} L_i(1/(n+x)) = sum_k c[i,k] * zeta(2s+k, Ne+1+x)     EXACT

The tail is therefore neither truncated nor Euler-Maclaurin'd — it is summed in closed
form. (CP2's float64 path uses a one-term `f(0) * nmax^{1-2s}/(2s-1)` tail correction,
which is what caps it near 1e-8.)

The split point Ne is load-bearing, and this is the one subtle part. The monomial
coefficients c[i,k] grow like 4^N — intrinsic to ANY polynomial basis composed with
y = 1/(n+x), which compresses [0,1] into a short interval near 0. Evaluating the whole
sum through them would cancel ~0.6N digits off the answer. Confining them to the n>Ne
tail fixes this twice over: y < 1/Ne kills the 4^k growth term-by-term (no cancellation
within the tail sum), and the tail is itself only an O(Ne^{1-2s}) correction, so the
~0.6N digits of absolute error land on a small correction rather than on the answer.
The first Ne terms are evaluated by (perfectly stable) barycentric interpolation.

Convergence: eigenfunctions are analytic on a neighbourhood of [0,1] (the s=1 eigenfunction
1/(1+x) has its nearest singularity at x=-1), so Chebyshev truncation converges like
rho^{-N} with rho = 3+sqrt(8) = 5.83 — about 0.77 decimal digits per node. Budget
dps >~ 0.77*N + 0.6*N + margin.

Fixtures and the gate live in `thermo/gate_fixtures.py`. Nothing here is trusted until
that gate passes; see also `approximability/thread3_constants.py` for the independent
periodic-orbit determinant route on the restricted alphabet.
"""
from __future__ import annotations

import mpmath as mp


# ---------------------------------------------------------------------------------------
# Chebyshev-Lobatto nodes, barycentric weights, exact Lagrange monomial coefficients
# ---------------------------------------------------------------------------------------
def cheb_lobatto(N):
    """N+1 Chebyshev-Lobatto nodes of [0,1], ascending. Endpoints included."""
    return [(1 - mp.cos(mp.pi * k / N)) / 2 for k in range(N + 1)]


def bary_weights(nodes):
    """True barycentric weights w_i = 1 / prod_{m!=i} (x_i - x_m).

    Computed directly (not from the closed-form Chebyshev pattern) because the monomial
    route below needs the correct SCALE, not just the correct ratios.
    """
    n = len(nodes)
    w = []
    for i in range(n):
        p = mp.mpf(1)
        for m in range(n):
            if m != i:
                p *= nodes[i] - nodes[m]
        w.append(1 / p)
    return w


def _poly_from_roots(roots):
    """Descending coefficients of prod_m (y - root_m)."""
    desc = [mp.mpf(1)]
    for r in roots:
        new = [mp.mpf(0)] * (len(desc) + 1)
        for k, c in enumerate(desc):
            new[k] += c
            new[k + 1] -= c * r
        desc = new
    return desc


def _poly_deflate(desc, r):
    """Synthetic division: given descending coeffs of P with P(r)=0, return P/(y-r)."""
    out = [desc[0]]
    for c in desc[1:-1]:
        out.append(c + r * out[-1])
    return out


def lagrange_monomial_coeffs(nodes, w):
    """c[i][k] = coefficient of y^k in the i-th Lagrange basis polynomial L_i(y).

    Built by deflating prod_m (y - x_m) by (y - x_i) and scaling by w_i — far better
    conditioned than inverting a Vandermonde matrix.
    """
    full = _poly_from_roots(nodes)
    coeffs = []
    for i, xi in enumerate(nodes):
        q_desc = _poly_deflate(full, xi)          # degree N, descending
        asc = list(reversed(q_desc))
        coeffs.append([w[i] * a for a in asc])
    return coeffs


def bary_row(nodes, w, y):
    """Values [L_0(y), ..., L_N(y)] by the barycentric formula (numerically stable)."""
    diffs = [y - x for x in nodes]
    for i, d in enumerate(diffs):
        if d == 0:
            row = [mp.mpf(0)] * len(nodes)
            row[i] = mp.mpf(1)
            return row
    t = [wi / d for wi, d in zip(w, diffs)]
    tot = mp.fsum(t)
    return [ti / tot for ti in t]


# ---------------------------------------------------------------------------------------
# The operator
# ---------------------------------------------------------------------------------------
class GaussOperator:
    """Discretized L_s. Reusable across s: nodes/weights/coefficients are built once."""

    def __init__(self, N=40, dps=60, Ne=100):
        self.N, self.dps, self.Ne = N, dps, Ne
        with mp.workdps(dps):
            self.nodes = cheb_lobatto(N)
            self.w = bary_weights(self.nodes)
            self.coeffs = lagrange_monomial_coeffs(self.nodes, self.w)
            # barycentric rows for the explicit head n=1..Ne, cached per node
            self.head_rows = [
                [bary_row(self.nodes, self.w, 1 / (n + xj)) for n in range(1, Ne + 1)]
                for xj in self.nodes
            ]

    def matrix(self, s, alphabet=None):
        """L_s as a (N+1)x(N+1) mpmath matrix acting on node values.

        alphabet=None -> full Gauss map (infinite sum, exact Hurwitz-zeta tail).
        alphabet=iterable of ints -> restricted subsystem (finite sum, no tail).
        """
        N, Ne = self.N, self.Ne
        with mp.workdps(self.dps):
            s = mp.mpmathify(s)
            two_s = 2 * s
            M = mp.matrix(N + 1, N + 1)

            if alphabet is not None:
                for j, xj in enumerate(self.nodes):
                    for n in alphabet:
                        y = 1 / (n + xj)
                        wgt = (n + xj) ** (-two_s)
                        row = bary_row(self.nodes, self.w, y)
                        for i in range(N + 1):
                            M[j, i] += wgt * row[i]
                return M

            # full alphabet: explicit head + closed-form tail
            for j, xj in enumerate(self.nodes):
                for n in range(1, Ne + 1):
                    wgt = (n + xj) ** (-two_s)
                    row = self.head_rows[j][n - 1]
                    for i in range(N + 1):
                        M[j, i] += wgt * row[i]
                # EXACT tail: sum_{n>Ne} (n+x)^{-2s} L_i(1/(n+x)) = sum_k c[i,k] zeta(2s+k, Ne+1+x)
                a = Ne + 1 + xj
                Z = [mp.zeta(two_s + k, a) for k in range(N + 1)]
                for i in range(N + 1):
                    ci = self.coeffs[i]
                    M[j, i] += mp.fsum(ci[k] * Z[k] for k in range(N + 1))
            return M

    # -- spectrum -----------------------------------------------------------------------
    def leading(self, s, alphabet=None, iters=None, matrix=None):
        """Leading eigenvalue and right eigenvector by power iteration.

        Convergence rate is |lambda_1/lambda_0| ~ 0.30 at s=1, so ~0.52 digits/iteration.
        """
        M = self.matrix(s, alphabet) if matrix is None else matrix
        n = M.rows
        if iters is None:
            iters = int(self.dps / 0.52) + 40
        with mp.workdps(self.dps):
            v = mp.matrix([mp.mpf(1)] * n)
            lam = mp.mpf(0)
            for _ in range(iters):
                u = M * v
                m = max(range(n), key=lambda i: abs(u[i]))
                lam = u[m] / v[m]
                nrm = u[m]
                v = mp.matrix([ui / nrm for ui in u])
            return lam, v

    def subleading(self, s, alphabet=None, matrix=None):
        """Second eigenvalue by Wielandt deflation (needs left+right leading vectors).

        At s=1 with the full alphabet this is the Gauss-Kuzmin-Wirsing constant.
        """
        M = self.matrix(s, alphabet) if matrix is None else matrix
        lam0, v0 = self.leading(s, alphabet, matrix=M)
        MT = M.T
        _, u0 = self.leading(s, alphabet, matrix=MT)   # left eigenvector of M
        n = M.rows
        with mp.workdps(self.dps):
            denom = mp.fsum(u0[i] * v0[i] for i in range(n))
            D = mp.matrix(n, n)
            for i in range(n):
                for j in range(n):
                    D[i, j] = M[i, j] - lam0 * v0[i] * u0[j] / denom
            lam1, _ = self.leading(s, alphabet, matrix=D)
            return lam1

    # -- thermodynamics -----------------------------------------------------------------
    def pressure(self, s, alphabet=None):
        """P(s) = log(leading eigenvalue of L_s). Anchor: P(1) = 0 on the full alphabet."""
        lam, _ = self.leading(s, alphabet)
        with mp.workdps(self.dps):
            return mp.log(lam)

    def dpressure(self, s, alphabet=None, h=None):
        """P'(s) by a 4th-order central difference.

        `mp.diff` is NOT usable here: it chooses a step from the ambient precision, but
        `pressure` pins its own working precision at self.dps, so mp.diff's step falls
        below the resolution of the function it is differentiating and the result
        collapses to exactly 0. The step is therefore set explicitly.

        h = 10^(-dps/5) balances the two error sources. The N-truncation error is a
        SMOOTH function of s (same discretization at every s), so it largely cancels in
        the difference rather than being amplified by 1/h; the derivative is accurate to
        roughly the pressure's own accuracy, not to accuracy/h.
        """
        with mp.workdps(self.dps):
            if h is None:
                h = mp.mpf(10) ** (-self.dps // 5)
            f = lambda t: self.pressure(t, alphabet)
            return (-f(s + 2 * h) + 8 * f(s + h) - 8 * f(s - h) + f(s - 2 * h)) / (12 * h)

    def lyapunov(self, alphabet=None):
        """Gauss-map Lyapunov exponent lambda = -P'(1). Closed form pi^2/(6 ln 2).

        The Levy / denominator-growth constant is lambda/2 = pi^2/(12 ln 2).
        """
        return -self.dpressure(mp.mpf(1), alphabet)

    def dimension(self, alphabet, start="0.53"):
        """Hausdorff dimension of the CF subsystem on `alphabet`: the s* with P(s*)=0.

        For alphabet={1,2} this is dim E_2 (Jenkinson-Pollicott). Secant, not bisection:
        P is smooth and monotone here, so secant needs ~8 matrix builds where bisection
        would need one per bit. Tolerance is set from the operator's OWN accuracy
        (~0.86 digits per node), not from the ambient mpmath precision.
        """
        with mp.workdps(self.dps):
            f = lambda t: self.pressure(t, alphabet)
            tol = mp.mpf(10) ** (-int(0.7 * self.dps))
            return mp.findroot(f, mp.mpf(start), tol=tol)
