"""PH6_SEAL 6.1 §7.1: the Srednicki fixture (J. Phys. A 44 (2011) 305202, arXiv 1104.1850 v3) — a known answer for the
level-pipeline, not a candidate.

Matrix (eq. 27): in the parity-δ oscillator subspace (N = 2K + δ), H_BK is tridiagonal with zero diagonal and
off-diagonal b_k = −(i/2)[(2k + δ)(2k + δ − 1)]^{1/2}, k = 1 … K − 1 (k = 0 … K − 1 basis); unitarily equivalent to the
real symmetric tridiagonal with off-diagonal |b_k|.
Identity (eq. 24): Γ_{∞,N}(½ + iE) = c_N · det_K(E − Ĥ) · Γ_{∞,δ}(½ + iE), with Γ_{∞,N}(s) = 2∫₀^∞ ψ_{∞,N}(x) x^{s−1} dx
(eq. 20), ψ_{∞,N}(x) ∝ H_N(√(2π) x) e^{−πx²} (eq. 21). Computed independently here by the Mellin transform
∫₀^∞ x^{m+s−1} e^{−πx²} dx = ½ π^{−(m+s)/2} Γ((m+s)/2) term by term.
Check: R(E) = Γ_{∞,N}(½+iE) / (Γ_{∞,δ}(½+iE) · det_K(E − Ĥ)) is the same constant at every E (relative spread ≤ 1e-10),
and the matrix eigenvalues are where Γ_{∞,N}(½+iE) vanishes.
"""
import json
import math
import os
import sys

import mpmath as mp
import numpy as np


def hermite_coeffs(N):
    """Physicists' H_N(y) = Σ c_m y^m (exact integers)."""
    if N == 0:
        return [1]
    a, b = [1], [0, 2]
    for n in range(1, N):
        c = [0] * (n + 2)
        for m, v in enumerate(b):
            c[m + 1] += 2 * v
        for m, v in enumerate(a):
            c[m] -= 2 * n * v
        a, b = b, c
    return b


def gamma_inf(N, s):
    c = hermite_coeffs(N)
    tot = mp.mpf(0)
    for m, cm in enumerate(c):
        if cm:
            tot += cm * (2 * mp.pi) ** (mp.mpf(m) / 2) * mp.mpf(1) / 2 * mp.pi ** (-(m + s) / 2) * mp.gamma((m + s) / 2)
    return 2 * tot


def matrix_eigs(N):
    K, d = divmod(N, 2)
    k = np.arange(1, K)
    off = 0.5 * np.sqrt((2 * k + d) * (2 * k + d - 1.0))
    A = np.diag(off, 1) + np.diag(off, -1)
    return np.linalg.eigvalsh(A), A


def check(N, dps=60):
    mp.mp.dps = dps
    ev, A = matrix_eigs(N)
    d = N % 2
    Es = [mp.mpf(x) for x in (0.37, 1.9, 4.4, 7.7, 12.3, 20.1)]
    ratios = []
    for E in Es:
        detK = mp.det(mp.matrix(E * np.eye(len(A)) - A))
        s = mp.mpf(1) / 2 + 1j * E
        ratios.append(gamma_inf(N, s) / (gamma_inf(d, s) * detK))
    r0 = ratios[0]
    spread = max(abs(r / r0 - 1) for r in ratios)
    # the eigenvalues are zeros of Γ_{∞,N}(½ + iE): relative size against its magnitude nearby
    rel = []
    for e in ev[:: max(1, len(ev) // 6)]:
        v0 = abs(gamma_inf(N, mp.mpf(1) / 2 + 1j * mp.mpf(e)))
        v1 = abs(gamma_inf(N, mp.mpf(1) / 2 + 1j * (mp.mpf(e) + mp.mpf("0.05"))))
        rel.append(float(v0 / v1))
    return dict(N=N, K=len(A), eigenvalues_sample=[float(x) for x in ev[:6]], ratio_rel_spread=float(spread),
                gamma_at_eig_over_nearby_max=max(rel), PASS=bool(spread < 1e-10 and max(rel) < 1e-8))


if __name__ == "__main__":
    out = sys.argv[1]
    res = [check(N) for N in (40, 41)]
    for r in res:
        print(json.dumps(r), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "srednicki61.json"), "w"), indent=1)
