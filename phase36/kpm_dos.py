"""
phase36/kpm_dos.py — Track 4 F2 floor recovery via KPM global DOS (Phase 36 follow-up).

F2 (spectral→IDS-unfold) lost the banked metal→floor when the DOS was estimated by Gaussian KDE
(smoothing artifact). The principled fix: estimate the global DOS by the KERNEL POLYNOMIAL METHOD —
Chebyshev moments μ_n = (1/N)Tr T_n(H̃) via STOCHASTIC TRACE (O(M·R·N) matvecs, no diagonalization),
Jackson kernel to damp Gibbs ringing. The floor then comes from MOMENT CONVERGENCE (M), not a smoothing
bandwidth. Unfold the eigenvalues through the KPM-IDS → W1δ.

GATES (calibrator discipline + a free ergodicity check):
  (1) moment-convergence ladder at N=1200 vs the BANKED exact metal floor (~0.005) — does W1δ converge
      DOWN to the floor as M grows? (vs KDE which railed at 0.5-1.0).
  (2) α-INVARIANCE of the recovered floor — the IDS is a TRACE ⇒ ergodic/self-averaging ⇒ a.s.
      α-independent. If the KPM floor comes out α-independent, the estimator is reading the IDS as the
      ergodic theorem requires; if α-dependent, the estimator is broken (the IDS cannot be) — caught
      before trust. Recovering the floor AGAINST A THEOREM.
"""
from __future__ import annotations
import os, sys
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "phase35a")):
    sys.path.insert(0, p)
from unfold_rotnum import am_diag, GOLDEN, W1d        # noqa: E402

METAL, INSUL = 0.5, 1.5


def am_apply_scaled(diag, v, a):
    """H̃ v = (H v)/a, H tridiagonal (offdiag 1). O(N)."""
    out = diag * v
    out[:-1] += v[1:]; out[1:] += v[:-1]
    return out / a


def jackson_kernel(M):
    n = np.arange(M)
    return ((M - n + 1) * np.cos(np.pi * n / (M + 1)) +
            np.sin(np.pi * n / (M + 1)) / np.tan(np.pi / (M + 1))) / (M + 1)


def kpm_moments(diag, M, R, a, rng):
    """Chebyshev moments μ_n = (1/N)Tr T_n(H̃) via stochastic trace over R ±1 probe vectors. O(M·R·N)."""
    n = diag.size
    mu = np.zeros(M)
    for _ in range(R):
        xi = rng.choice([-1.0, 1.0], size=n)
        t0 = xi.copy()
        t1 = am_apply_scaled(diag, t0, a)
        mu[0] += t0 @ t0
        mu[1] += t0 @ t1
        for k in range(2, M):
            t2 = 2.0 * am_apply_scaled(diag, t1, a) - t0
            mu[k] += t0 @ t2
            t0, t1 = t1, t2
    return mu / (R * n)


def kpm_ids(mu, a, n_grid=20000):
    """Reconstruct DOS on x∈(-1,1) with Jackson damping, integrate → IDS(E) on a grid. Returns (E, IDS)."""
    M = mu.size
    g = jackson_kernel(M)
    x = np.linspace(-1, 1, n_grid + 2)[1:-1]
    # ρ(x) = 1/(π√(1-x²)) [g0 μ0 + 2 Σ_{n≥1} g_n μ_n T_n(x)]
    Tn_prev = np.ones_like(x); Tn = x.copy()
    s = g[0] * mu[0] + 2.0 * g[1] * mu[1] * Tn
    for k in range(2, M):
        Tn_next = 2.0 * x * Tn - Tn_prev
        s += 2.0 * g[k] * mu[k] * Tn_next
        Tn_prev, Tn = Tn, Tn_next
    rho_x = s / (np.pi * np.sqrt(1 - x * x))
    rho_x = np.clip(rho_x, 0, None)
    E = x * a
    cdf = np.cumsum(rho_x); cdf /= cdf[-1]
    return E, cdf


def f2_kpm_W1d(lam, n, alpha, M, R, rng):
    pad = 0.05
    a = (2.0 + 2.0 * lam) * (1.0 + pad)          # H̃ = H/a, spectrum ⊂ (-1,1)
    diag = am_diag(n, lam, GOLDEN, alpha)
    mu = kpm_moments(diag, M, R, a, rng)
    Egrid, ids = kpm_ids(mu, a)
    ev = np.sort(eigvalsh_tridiagonal(diag, np.ones(n - 1)))   # eigenvalue points (O(N) mem)
    unf = np.interp(ev, Egrid, ids) * n
    return round(float(W1d(unf)), 5)


def gate(n=1200):
    rng = np.random.default_rng(0)
    print(f"KPM F2 GATE at N={n}")
    print(f"(1) moment-convergence ladder — metal W1δ should converge DOWN to the banked exact floor ~0.005")
    print(f"    (KDE-DOS railed at 0.48-1.0; the floor needs an accurate DOS)")
    for M in (256, 512, 1024, 2048, 4096):
        w = f2_kpm_W1d(METAL, n, 0.0, M, 24, np.random.default_rng(0))
        print(f"      M={M:5d} R=24: metal W1δ={w}")
    print(f"\n(2) α-invariance of the recovered floor (M=2048) — IDS is a trace ⇒ should be α-INDEPENDENT")
    ws = []
    for alpha in (0.0, 0.13, 0.27, 0.41):
        w = f2_kpm_W1d(METAL, n, alpha, 2048, 24, np.random.default_rng(0))
        ws.append(w); print(f"      α={alpha}: metal W1δ={w}")
    spread = max(ws) - min(ws)
    print(f"    spread across α = {spread:.4f}  (F2-exact metal spread was 0.0022; F1 local was 0.146)")
    print(f"    >>> floor {'α-INVARIANT (IDS behaving as ergodic theorem requires)' if spread < 0.02 else 'α-DEPENDENT (estimator broken — IDS cannot be)'}")
    # also confirm separation: insulator should read higher
    wi = f2_kpm_W1d(INSUL, n, 0.0, 2048, 24, np.random.default_rng(0))
    print(f"\n  separation check (M=2048, α=0): metal W1δ={ws[0]} vs insul W1δ={wi}  sep={round(wi-ws[0],4)}")


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1 and _s.argv[1] == "gate":
        gate(int(_s.argv[2]) if len(_s.argv) > 2 else 1200)
    else:
        gate()
