"""
phase36/lanczos_local_measure.py — Track 4 follow-up: O(N) local spectral measure for F1/F2.

Lanczos from |e0> on the AM tridiagonal gives the Jacobi matrix whose spectral measure (w.r.t. e0)
is the local measure dμ0. Its m×m eigendecomposition yields Gauss nodes/weights {θ_k, w_k=|S[0,k]|²}
= dμ0, at O(m·N) (tridiagonal matvec is O(N)), WITHOUT the N×N eigenvector matrix that walled F1 at
N≳5e4. Then φ(t)=⟨e0|e^{-iHt}|e0⟩ = Σ_k w_k e^{-iθ_k t}.

CALIBRATOR GATE (synthetic-validate-fitters discipline — run BEFORE trusting at high N):
finite-precision Lanczos loses orthogonality → ghost (spurious) eigenvalues that could forge a false
floor or smear the metal→floor edge (the structure F1's separation depends on). So at an N where the
EXACT answer is banked (full eigh_tridiagonal), confirm the Lanczos measure reproduces (a) exact φ(t)
[transport signature], (b) the F1 phase-crossing W1δ metal vs insulator. Only if it matches do we push
to high N. Reorthogonalization variants compared: none / full / periodic-partial.
"""
from __future__ import annotations
import os, sys
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.signal import butter, sosfiltfilt, hilbert

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "phase35a")):
    sys.path.insert(0, p)
from unfold_rotnum import am_diag, GOLDEN, W1d              # noqa: E402

METAL, INSUL = 0.5, 1.5


def am_apply(diag, v):
    """(H v)_n = v_{n-1} + v_{n+1} + diag_n v_n  — O(N) matvec for the AM tridiagonal (offdiag=1)."""
    out = diag * v
    out[:-1] += v[1:]
    out[1:] += v[:-1]
    return out


def lanczos_jacobi(diag, m, reorth="periodic", seed_site=0):
    """Lanczos from e_{seed_site}. Returns Gauss nodes θ, weights w (≈ local spectral measure dμ0).
    reorth: 'none' | 'full' | 'periodic' (partial re-orth every few steps)."""
    n = diag.size
    v_prev = np.zeros(n); v = np.zeros(n); v[seed_site] = 1.0
    alpha = np.zeros(m); beta = np.zeros(m)
    V = np.zeros((m, n)) if reorth in ("full", "periodic") else None
    b = 0.0
    for j in range(m):
        if V is not None:
            V[j] = v
        w = am_apply(diag, v)
        a = float(v @ w); alpha[j] = a
        w = w - a * v - b * v_prev
        if reorth == "full" or (reorth == "periodic" and j % 5 == 0):
            # re-orthogonalize against all previous Lanczos vectors (mitigates ghost eigenvalues)
            if V is not None and j > 0:
                w -= V[:j].T @ (V[:j] @ w)
        b = float(np.linalg.norm(w))
        if b < 1e-14:
            alpha = alpha[:j + 1]; beta = beta[:j + 1]; break
        beta[j] = b
        v_prev = v; v = w / b
    # Jacobi matrix J = tridiag(beta[:-1] offdiag, alpha diag). Eigendecompose (small, m×m).
    th, S = eigh_tridiagonal(alpha, beta[:len(alpha) - 1])
    wts = S[0, :] ** 2          # Gauss weights = squared first components (μ0 = <e0|e0> = 1)
    return th, wts


def phi_from_measure(th, wts, t):
    return (wts[None, :] * np.exp(-1j * t[:, None] * th[None, :])).sum(1)


def phi_exact(lam, n, t, phi=0.0):
    d = am_diag(n, lam, GOLDEN, phi); E, Vv = eigh_tridiagonal(d, np.ones(n - 1))
    w = Vv[0, :] ** 2
    return (w[None, :] * np.exp(-1j * t[:, None] * E[None, :])).sum(1)


def f1_W1d(sig_real, dt=0.1, band=(0.05, 0.30)):
    fs = 1.0 / dt
    sos = butter(4, list(band), btype="band", fs=fs, output="sos")
    ph = np.unwrap(np.angle(hilbert(sosfiltfilt(sos, sig_real))))
    t = np.arange(sig_real.size) * dt
    k0 = np.ceil(ph[0] / (2 * np.pi)); k1 = np.floor(ph[-1] / (2 * np.pi))
    if k1 <= k0 + 5:
        return None
    cross = np.interp(2 * np.pi * np.arange(k0, k1 + 1), ph, t)
    iv = np.diff(cross); iv = iv[iv > 0]
    if iv.size < 60:
        return None
    s = iv / iv.mean()
    return round(float(W1d(np.cumsum(np.concatenate([[0.], s])))), 5), int(iv.size)


def calibrate(n=1200, dt=0.1, T=2000.0):
    """GATE: does the Lanczos local measure reproduce exact φ(t) + the F1 metal/insulator W1δ at an N
    where exact diag is banked?"""
    t = np.arange(0, T, dt)
    print(f"CALIBRATION at N={n} (exact diag banked) — Lanczos vs exact")
    print(f"{'regime':9s} {'reorth':9s} {'m':>5s} {'maxΔφ':>9s} {'|φ|late/early exact→lanc':>26s} {'F1 W1δ exact→lanc':>22s}")
    results = {}
    for lam, name in ((METAL, "metal"), (INSUL, "insul")):
        d = am_diag(n, lam, GOLDEN, 0.0)
        pe = phi_exact(lam, n, t)
        ratio_e = np.abs(pe)[t > 0.8 * T].mean() / np.abs(pe)[t < 5].mean()
        w1_e = f1_W1d(np.real(pe), dt)
        for reorth in ("none", "periodic", "full"):
            for m in (n // 2, n):
                th, wts = lanczos_jacobi(d, m, reorth=reorth)
                pl = phi_from_measure(th, wts, t)
                maxd = float(np.max(np.abs(pl - pe)))
                ratio_l = np.abs(pl)[t > 0.8 * T].mean() / np.abs(pl)[t < 5].mean()
                w1_l = f1_W1d(np.real(pl), dt)
                print(f"{name:9s} {reorth:9s} {m:5d} {maxd:9.2e} "
                      f"{ratio_e:11.3f}→{ratio_l:<8.3f} "
                      f"{str(w1_e[0] if w1_e else None):>10s}→{str(w1_l[0] if w1_l else None):<10s}")
                results[(name, reorth, m)] = dict(maxd=maxd, ratio_e=float(ratio_e), ratio_l=float(ratio_l),
                                                  w1_e=w1_e[0] if w1_e else None, w1_l=w1_l[0] if w1_l else None)
    return results


def convergence_ladder(n=8000, ms=(1500, 2500, 3500, 4500, 6000), dt=0.1, T=2000.0):
    """Does a SUB-N moment count m≪N converge φ(t)/F1-W1δ to the exact answer (incl. the floor)?
    φ(t) on horizon T needs the measure resolved to ~1/T ⇒ m ~ (spectral width)·T/π, independent of N.
    Confirms the high-N push (m≪N, O(N) memory, small-J eigenvectors) is faithful BEFORE we go where
    we can't diagonalize. Exact is banked at this N (full eigh)."""
    t = np.arange(0, T, dt)
    print(f"\nCONVERGENCE LADDER at N={n} (exact banked) — sub-N moment count m vs exact F1 W1δ")
    for lam, name in ((METAL, "metal"), (INSUL, "insul")):
        d = am_diag(n, lam, GOLDEN, 0.0)
        pe = phi_exact(lam, n, t); w1_e = f1_W1d(np.real(pe), dt)
        print(f"  {name} (exact F1 W1δ={w1_e[0] if w1_e else None}):")
        for m in ms:
            th, wts = lanczos_jacobi(d, m, reorth="periodic")
            w1_l = f1_W1d(np.real(phi_from_measure(th, wts, t)), dt)
            print(f"     m={m:5d} ({m/n:.2f}·N): F1 W1δ={w1_l[0] if w1_l else None}")


def high_n_alpha_resolution(n=50000, m=4500, dt=0.1, T=2000.0, alphas=(0.0, 0.13, 0.27, 0.41)):
    """THE payoff: with the O(N)-memory Lanczos measure (m≪N, no N×N eigenvectors), push φ(t) to high N
    and re-run the F1 α-sweep. If the α-confound (separation collapsing at α=0.13/0.27 at N=2584)
    DISAPPEARS at high N, the instability was the substrate's phase-noise (collapses with N), NOT an F1
    defect ⇒ F1's blocker resolved. 'none' reorth keeps memory O(N)."""
    t = np.arange(0, T, dt)
    # GUARD: confirm the 'none'-reorth config we'll USE at high N reproduces exact at a checkable N
    print(f"\nGUARD — 'none'-reorth (the high-N config), m={m}, at N=8000 (exact banked):")
    for lam, name in ((METAL, "metal"), (INSUL, "insul")):
        d8 = am_diag(8000, lam, GOLDEN, 0.0)
        we = f1_W1d(np.real(phi_exact(lam, 8000, t)), dt)
        th, wts = lanczos_jacobi(d8, m, reorth="none")
        wl = f1_W1d(np.real(phi_from_measure(th, wts, t)), dt)
        print(f"   {name}: exact F1 W1δ={we[0] if we else None} vs none-reorth m={m}={wl[0] if wl else None}")
    print(f"\nHIGH-N α-RESOLUTION at N={n}, m={m} (O(N) memory; the regime walled off by eigenvectors)")
    print(f"{'α':>6s} {'metal W1δ':>10s} {'insul W1δ':>10s} {'sep':>9s}")
    seps = []
    for a in alphas:
        out = {}
        for lam, name in ((METAL, "metal"), (INSUL, "insul")):
            d = am_diag(n, lam, GOLDEN, a)
            th, wts = lanczos_jacobi(d, m, reorth="none")
            r = f1_W1d(np.real(phi_from_measure(th, wts, t)), dt)
            out[name] = r[0] if r else None
        sep = (out['insul'] - out['metal']) if (out['metal'] is not None and out['insul'] is not None) else None
        if sep is not None:
            seps.append(sep)
        print(f"{a:6.2f} {str(out['metal']):>10s} {str(out['insul']):>10s} {str(round(sep,5) if sep is not None else None):>9s}")
    if seps:
        same_sign = all(s > 0 for s in seps) or all(s < 0 for s in seps)
        spread = max(seps) - min(seps)
        print(f"\n  α-sweep separations: {[round(s,4) for s in seps]}")
        print(f"  same-sign across α = {same_sign}; spread = {spread:.4f}")
        print(f"  >>> α-CONFOUND {'RESOLVED (separation α-stable at high N)' if same_sign and spread < 0.05 else 'PERSISTS (still α-contingent)'}")


if __name__ == "__main__":
    import sys as _s
    mode = _s.argv[1] if len(_s.argv) > 1 else "calibrate"
    if mode == "calibrate":
        calibrate()
    elif mode == "converge":
        convergence_ladder()
    elif mode == "highn":
        n = int(_s.argv[2]) if len(_s.argv) > 2 else 50000
        m = int(_s.argv[3]) if len(_s.argv) > 3 else 4500
        high_n_alpha_resolution(n=n, m=m)
