"""Phase 2 R₂ library (PH2R2_SEAL 1.0): the Conrey–Snaith pair correlation with all arithmetic lower-order terms.

Source (R1): Conrey & Snaith, Proc. LMS 94 (2007) 594, Theorem 4.1 (arXiv math/0509480 v2, LaTeX lines 1226–1250),
assuming the ratios conjecture:
  Σ_{γ,γ′≤T} f(γ − γ′) = (1/4π²) ∫₀^T [ 2π f(0) log(t/2π)
        + ∫ f(r) ( log²(t/2π) + 2( (ζ′/ζ)′(1+ir) + (t/2π)^{−ir} ζ(1−ir)ζ(1+ir) A(ir) − B(ir) ) ) dr ] dt + O(T^{1/2+ε}),
  A(η) = Π_p (1 − p^{−1−η})(1 − 2/p + p^{−1−η}) / (1 − 1/p)²,   B(η) = Σ_p ( log p / (p^{1+η} − 1) )².
The f(0) term is the diagonal γ = γ′; the off-diagonal pair density at height t and raw separation r is therefore
  R(t, r) = (1/4π²) [ log²(t/2π) + 2 Re( (ζ′/ζ)′(1+ir) + (t/2π)^{−ir} ζ(1−ir)ζ(1+ir) A(ir) − B(ir) ) ]   (f even).
Identity used for A (algebra, checked numerically in G0a): with x = p^{−1−η}, the factor equals
  1 − (1 − p^{−η})² / (p − 1)²,
so log A(η) = Σ_p log(1 − (1 − p^{−η})²/(p − 1)²), whose tail beyond P is O(4/(P log P)).
Split used by the estimand μ (seal §2): R = RMT + LOT with
  RMT(t, r) = (1/4π²) [ L_t² − 2/r² + 2 cos(r L_t)/r² ] = (L_t/2π)² (1 − sinc²),   L_t = log(t/2π),
  LOT = R − RMT (everything arithmetic: the regular parts of (ζ′/ζ)′, of ζζ, A − 1 and B).
"""
import math

import numpy as np

P_MAX = 10_000_000


def primes_upto(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


_PRIMES = None


def primes():
    global _PRIMES
    if _PRIMES is None:
        _PRIMES = primes_upto(P_MAX).astype(np.float64)
    return _PRIMES


def A_ir(r, pmax=P_MAX, chunk=200_000):
    """A(ir) for an array of real r (complex result), via log A = Σ_p log(1 − (1 − p^{−ir})²/(p − 1)²)."""
    p = primes()
    p = p[p <= pmax]
    r = np.atleast_1d(np.asarray(r, dtype=float))
    out = np.zeros(len(r), dtype=complex)
    lp = np.log(p)
    for i in range(0, len(p), chunk):
        pp, ll = p[i:i + chunk], lp[i:i + chunk]
        ph = np.exp(-1j * np.outer(r, ll))                 # p^{−ir}
        out += np.log1p(-((1 - ph) ** 2) / (pp - 1) ** 2).sum(axis=1)
    return np.exp(out)


def B_ir(r, pmax=P_MAX, chunk=200_000):
    """B(ir) = Σ_p (log p / (p^{1+ir} − 1))² for an array of real r."""
    p = primes()
    p = p[p <= pmax]
    r = np.atleast_1d(np.asarray(r, dtype=float))
    out = np.zeros(len(r), dtype=complex)
    lp = np.log(p)
    for i in range(0, len(p), chunk):
        pp, ll = p[i:i + chunk], lp[i:i + chunk]
        ps = pp * np.exp(1j * np.outer(r, ll))               # p^{1+ir}
        out += ((ll / (ps - 1)) ** 2).sum(axis=1)
    return out


def zeta_terms(r, dps=30):
    """(ζ′/ζ)′(1+ir) and ζ(1−ir)ζ(1+ir) for an array of real r ≠ 0 (mpmath)."""
    import mpmath as mp
    d1 = np.empty(len(r), dtype=complex)
    zz = np.empty(len(r), dtype=complex)
    with mp.workdps(dps):
        for k, x in enumerate(np.atleast_1d(r)):
            s = mp.mpc(1, x)
            z0, z1, z2 = mp.zeta(s), mp.zeta(s, derivative=1), mp.zeta(s, derivative=2)
            d1[k] = complex(z2 / z0 - (z1 / z0) ** 2)
            zz[k] = complex(mp.zeta(mp.mpc(1, -x)) * z0)
    return d1, zz


class Kernel:
    """Precomputed r-dependence of the CS07 pair density on a grid of r > 0 (even in r)."""

    def __init__(self, r_grid, pmax=P_MAX):
        self.r = np.asarray(r_grid, dtype=float)
        self.d1, self.zz = zeta_terms(self.r)
        self.A = A_ir(self.r, pmax)
        self.B = B_ir(self.r, pmax)

    def R(self, t):
        """CS07 off-diagonal pair density at height t on the r grid."""
        L = math.log(t / (2 * math.pi))
        g = self.d1 + np.exp(-1j * self.r * L) * self.zz * self.A - self.B
        return (L * L + 2 * np.real(g)) / (4 * math.pi ** 2)

    def RMT(self, t):
        L = math.log(t / (2 * math.pi))
        r = self.r
        return (L * L - 2 / r ** 2 + 2 * np.cos(r * L) / r ** 2) / (4 * math.pi ** 2)

    def LOT(self, t):
        return self.R(t) - self.RMT(t)
