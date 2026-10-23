"""Stage (b) session 1 diagnostic: in-window Gauss–Legendre quadrature of C(r) = Σ c_a c_b ∫(ρ_{a+b} − ρ_a ρ_b) for CUE_N
(determinants, cheap) against stage (a)'s exact Fredholm C(r), at nq = 6, 8, 10, 12 nodes per coordinate. Run from l6/."""
import itertools, math, sys
import numpy as np
sys.path.insert(0, '.')
import n6a_trace as A
N = 100_000
f1 = A.single_moments(); cp = A.psi_coeffs(f1)          # cp[a] for a = 1..3
def rho(pts):                                              # pts (..., n) -> det of CUE_N kernel
    X = pts[..., :, None] - pts[..., None, :]
    K = np.ones_like(X); nz = np.abs(X) > 1e-15
    K[nz] = np.sin(np.pi * X[nz]) / (N * np.sin(np.pi * X[nz] / N))
    return np.linalg.det(K)
def tuples(nq, a):
    x, w = np.polynomial.legendre.leggauss(nq); x = 2 * (x + 1); w = 2 * w
    T = list(itertools.combinations(range(nq), a))
    return np.array([[x[i] for i in t] for t in T]), np.array([math.factorial(a) * np.prod([w[i] for i in t]) for t in T])
def C_quad(r, nq):
    tot = 0.0
    for a in (1, 2, 3):
        XA, WA = tuples(nq, a)
        for b in (1, 2, 3):
            XB, WB = tuples(nq, b)
            P = np.concatenate([np.repeat(XA, len(XB), 0), np.tile(XB + r, (len(XA), 1))], 1)
            full = rho(P).reshape(len(XA), len(XB))
            prod = np.outer(rho(XA), rho(XB))
            tot += cp[a] * cp[b] * np.sum(WA[:, None] * WB[None, :] * (full - prod))
    return tot
for r in (4.125, 7.3, 20.0, 100.0):
    ex = A.cov_r(r, f1, cp)[0]
    print(r, 'exact', '%.6e' % ex, ' '.join('nq%d %.3e' % (nq, (C_quad(r, nq) - ex) / abs(ex)) for nq in (6, 8, 10, 12)), flush=True)
