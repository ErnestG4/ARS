"""C3a: Bolte–Egger–Keppeler lattice (J. Phys. A 50 (2017) 105201, arXiv 1610.06472 v2), op_N(h) in the form of their
eq. (B.11) with g_{m,0} from (B.8) and g_{0,0} from (B.9); ħ = 1, ℓ_x = ℓ_ξ = √(2πN) (their §5 numerics).

  op_N(h)_{k,l} = (g_00 − ½(k ℓ_x/N)²) δ_{k,l} + Σ_{m=1}^{N−1} g_{m,0} δ_{k+m,l}   (indices mod N)
  g_{m,0} = ℓ_ξ² (−1)^m / (4 N² sin²(πm/N)) · {1 (N even) | cos(πm/N) (N odd)},
  g_{0,0} = ℓ_ξ² / (24 N²) · {N² + 2 (N even) | N² − 1 (N odd)}.

The diagonal index k is taken in the symmetric range (−N/2, N/2]: the x-part of eq. (2.15),
−(ℓ_x²/4π²) Σ_n (−1)ⁿ/n² (T^{0,n} + T^{0,−n}), equals −½(k ℓ_x/N)² exactly for that representative
(Σ_n (−1)ⁿ cos(nθ)/n² = θ²/4 − π²/12, |θ| ≤ π). Known answer: Lemma 1 — the spectrum is symmetric about 0 when
ℓ_x = ℓ_ξ.

  python c3_bek.py N OUT          eigenvalues of the dense real symmetric matrix (LAPACK eigvalsh) -> OUT/C3a_N<N>.npy
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np


def matrix(N):
    ell2 = 2 * math.pi * N                                   # ℓ_x² = ℓ_ξ² = 2πN
    m = np.arange(1, N)
    s2 = np.sin(np.pi * m / N) ** 2
    g = ell2 * (-1.0) ** m / (4.0 * N * N * s2)
    if N % 2 == 1:
        g *= np.cos(np.pi * m / N)
    g00 = ell2 / (24.0 * N * N) * ((N * N + 2) if N % 2 == 0 else (N * N - 1))
    col = np.concatenate([[g00], g])                        # first row of the circulant: A[0, l] = g_{l}
    idx = (np.arange(N)[None, :] - np.arange(N)[:, None]) % N
    A = col[idx]
    k = np.arange(N)
    ks = np.where(k <= N // 2, k, k - N)
    A[np.arange(N), np.arange(N)] -= 0.5 * (ks * math.sqrt(ell2) / N) ** 2
    return A


def eigenvalues(N):
    A = matrix(N)
    assert np.allclose(A, A.T), "op_N(h) not symmetric"
    return np.linalg.eigvalsh(A)


if __name__ == "__main__":
    N, out = int(sys.argv[1]), sys.argv[2]
    t = time.time()
    ev = eigenvalues(N)
    sym = float(np.max(np.abs(np.sort(ev) + np.sort(ev)[::-1])))     # Lemma 1: E ↦ −E
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, f"C3a_N{N}.npy")
    np.save(p, ev)
    meta = dict(id="C3a", N=N, n=int(len(ev)), n_positive=int((ev > 0).sum()), E_min=float(ev[0]), E_max=float(ev[-1]),
                lemma1_max_asymmetry=sym, sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(),
                params=dict(hbar=1, ell_x="sqrt(2 pi N)", ell_xi="sqrt(2 pi N)", seconds=time.time() - t))
    json.dump(meta, open(os.path.join(out, f"C3a_N{N}.json"), "w"), indent=1)
    print(json.dumps(meta), flush=True)
