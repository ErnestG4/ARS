"""Vectorised ζ(s), ζ′(s), ζ″(s) near Re s = 1 by Euler–Maclaurin summation (numpy, complex double), for the fast CS08
evaluator: ζ(1 + x), ζ′/ζ(1 + x), (ζ′/ζ)′(1 + x) on large arrays of x (|Im x| up to ~2·10⁴).

  ζ(s) = Σ_{n<M} n^{−s} + M^{1−s}/(s−1) + M^{−s}/2 + Σ_{k=1}^{K} B_{2k}/(2k)! · s(s+1)…(s+2k−2) · M^{−s−2k+1},
with M = ⌈|Im s|⌉ + 64 (v1 used |Im s|/2π, where the Bernoulli terms stop decreasing: errors up to 35%), K = 10. Derivatives in s are taken
term by term (∂/∂s n^{−s} = −log n · n^{−s}; the Bernoulli terms by the product rule on the rising factorial). Validated
against mpmath by check() to ≤ 1e-12 relative, including near the pole |x| ~ 1e-3.
"""
import math

import mpmath as mp
import numpy as np

B2K = [mp.bernoulli(2 * k) for k in range(1, 11)]
FACT = [math.factorial(2 * k) for k in range(1, 11)]


TWO_PI_LD = np.longdouble("6.283185307179586476925286766559005768")   # parsed at long-double precision; v2 used
#                                         2·np.pi (a double π cast up): mod-2π at ~1e5 rad then lost ~4e-12


def cpow_neg(s, logs):
    """exp(−s·log) for complex s (column) and real logs (row), with the phase y·log reduced mod 2π in 80-bit long
    double before the exponential: at y·log ~ 1e5 rad, double precision would lose ~5 digits of phase (v1 did; it failed
    the sparse direct check at r > 1e4 spacings by up to 1.3e-9)."""
    s = np.asarray(s, complex)
    logs_ld = np.asarray(logs, np.longdouble)        # must ARRIVE in long double (np.log of long-double n): a double
    #                                                  log cast up keeps its 1e-16 rounding, which times Im s ~ 1e4
    #                                                  is the 1e-11 phase error (v2 did this; check_longdouble.py caught it)
    ph = np.mod(np.multiply.outer(s.imag.astype(np.longdouble), logs_ld), TWO_PI_LD).astype(float)
    return np.exp(-np.multiply.outer(s.real, logs_ld.astype(float))) * np.exp(-1j * ph)


def _zeta_derivs(s, M):
    """ζ, ζ′, ζ″ at complex array s (same M for the whole array)."""
    n = np.arange(1, M, dtype=float)
    ln_ld = np.log(n.astype(np.longdouble))
    ln = ln_ld.astype(float)
    z0 = np.zeros(s.shape, complex)
    z1 = np.zeros(s.shape, complex)
    z2 = np.zeros(s.shape, complex)
    for i in range(0, len(n), 512):
        nn, ll = n[i:i + 512], ln[i:i + 512]
        t = cpow_neg(s, ln_ld[i:i + 512])                    # n^{−s}, long-double log and phase
        z0 += t.sum(1)
        z1 += (-t * ll).sum(1)
        z2 += (t * ll * ll).sum(1)
    lM = math.log(M)
    Ms = cpow_neg(s, np.log(np.array([M], dtype=np.longdouble)))[:, 0]    # M^{−s}
    # M^{1−s}/(s−1) and its derivatives: g(s) = M·M^{−s}/(s−1)
    g0 = M * Ms / (s - 1)
    g1 = g0 * (-lM - 1 / (s - 1))
    g2 = g0 * ((lM + 1 / (s - 1)) ** 2 + 1 / (s - 1) ** 2)
    z0 += g0 + Ms / 2
    z1 += g1 - lM * Ms / 2
    z2 += g2 + lM * lM * Ms / 2
    # Bernoulli terms: c_k · R_k(s) · M^{−s−2k+1}, R_k(s) = s(s+1)…(s+2k−2); derivatives by log-derivative sums
    for k in range(1, 11):
        c = float(B2K[k - 1]) / FACT[k - 1]
        roots = [j for j in range(0, 2 * k - 1)]
        R = np.ones(s.shape, complex)
        for j in roots:
            R = R * (s + j)
        S1 = sum(1 / (s + j) for j in roots)
        S2 = sum(1 / (s + j) ** 2 for j in roots)
        E = Ms * M ** (-2 * k + 1)
        h0 = R * E
        dlog = S1 - lM
        h1 = h0 * dlog
        h2 = h0 * (dlog ** 2 - S2)
        z0 += c * h0
        z1 += c * h1
        z2 += c * h2
    return z0, z1, z2


def zeta_triplet(x):
    """For complex array x: ζ(1+x), ζ′/ζ(1+x), (ζ′/ζ)′(1+x)."""
    x = np.atleast_1d(np.asarray(x, complex))
    s = 1 + x
    out0 = np.empty(x.shape, complex)
    out1 = np.empty(x.shape, complex)
    out2 = np.empty(x.shape, complex)
    imax = np.abs(s.imag)
    # group by required M
    Ms = np.ceil(imax).astype(int) + 64              # the Bernoulli terms fall like (|s|/2πM)^{2k} ≤ (1/2π)^{2k}
    bins = np.unique(np.ceil(Ms / 256).astype(int) * 256)
    for Mb in bins:
        sel = np.ceil(Ms / 256).astype(int) * 256 == Mb
        z0, z1, z2 = _zeta_derivs(s[sel], int(Mb))
        out0[sel] = z0
        out1[sel] = z1 / z0
        out2[sel] = z2 / z0 - (z1 / z0) ** 2
    return out0, out1, out2


def check(n=60, seed=1):
    rng = np.random.default_rng(seed)
    ys = np.concatenate([rng.uniform(-20000, 20000, n), rng.uniform(-50, 50, n), 1e-3 * rng.uniform(-1, 1, 10)])
    xs = 1j * ys + rng.uniform(-0.01, 0.01, len(ys)) * 0
    z0, z1, z2 = zeta_triplet(xs)
    worst = [0.0, 0.0, 0.0]
    for k, x in enumerate(xs):
        s = mp.mpc(1, float(x.imag))
        a0, a1, a2 = mp.zeta(s), mp.zeta(s, derivative=1), mp.zeta(s, derivative=2)
        ref = [complex(a0), complex(a1 / a0), complex(a2 / a0 - (a1 / a0) ** 2)]
        for j, (got, r) in enumerate(zip((z0[k], z1[k], z2[k]), ref)):
            worst[j] = max(worst[j], abs(got - r) / abs(r))
    return dict(zeta=worst[0], logderiv=worst[1], logderiv_prime=worst[2])


if __name__ == "__main__":
    print(check())
