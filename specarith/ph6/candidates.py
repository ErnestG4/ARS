"""Phase 6.1 candidate construction (PH6_SEAL 6.1 §1–§2). Levels are COMPUTED and stored with hashes; nothing here
applies T1–T4 (that happens only after the 6.1 seal). Definitions: ph6/lit/xp_candidates.md (primary-read).

  python candidates.py c1 VARIANT RES OUT     VARIANT ∈ {a, b} (ϑ₂₀₁₁ = π/4 | 0); RES ∈ {1, 2} (grid ΔE 0.05 | 0.025)
  python candidates.py c4 RES OUT             RES ∈ {1, 2} (root tolerance 1e-10 | 1e-13)

Each run writes OUT/<id>_res<RES>.npy (levels, ascending, E > 0) and OUT/<id>_res<RES>.json (parameters, count, sha256).
"""
import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

N_TARGET = 30_000          # PH6_SEAL_6.0 §3: ≥ 3·10⁴ levels
E_MAX_C1 = 26_600.0        # N̄(26600) ≈ 31,000 > N_TARGET with margin (γ_30000 ≈ 25,755)


def _save(out, ident, res, levels, params):
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, f"{ident}_res{res}.npy")
    np.save(p, levels)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    meta = dict(id=ident, res=res, n=int(len(levels)), E_min=float(levels[0]), E_max=float(levels[-1]), sha256=h,
                params=params)
    json.dump(meta, open(os.path.join(out, f"{ident}_res{res}.json"), "w"), indent=1)
    print(json.dumps(meta), flush=True)


# ---------------------------------------------------------------- C1: Sierra–Rodríguez-Laguna H_I = x(p + ℓ_p²/p)
# S-RL 2011 eq. (14): e^{−iϑ/2} K_{½+iE/2}(h) + e^{iϑ/2} K_{½−iE/2}(h) = 0, ħ = 1, h = 2π. For real E and h the two K's are
# complex conjugates, so the condition is 2 arg K_{½+iE/2}(h) = ϑ + π (mod 2π)  (xp_candidates.md §3, CC check).
def _argK(E, dps=30):
    import mpmath as mp
    with mp.workdps(dps):
        return float(mp.arg(mp.besselk(mp.mpf(1) / 2 + 1j * mp.mpf(E) / 2, 2 * mp.pi)))


def _argK_chunk(Es):
    return [_argK(E) for E in Es]


def c1_levels(theta, dE, procs=12, tol=1e-12):
    grid = np.arange(dE, E_MAX_C1 + dE, dE)
    chunks = np.array_split(grid, procs * 8)
    with Pool(procs) as pool:
        a = np.concatenate([np.array(x) for x in pool.map(_argK_chunk, chunks)])
    phi = np.unwrap(2 * a)                              # continuous 2·arg K on the grid
    target0 = theta + math.pi
    # levels: phi(E) ≡ target0 (mod 2π); find every grid interval where phi crosses target0 + 2πk
    k_lo, k_hi = math.ceil((min(phi) - target0) / (2 * math.pi)), math.floor((max(phi) - target0) / (2 * math.pi))
    levels = []
    sgn = np.sign(phi[-1] - phi[0])
    for k in range(k_lo, k_hi + 1):
        tgt = target0 + 2 * math.pi * k
        idx = np.nonzero((phi[:-1] - tgt) * (phi[1:] - tgt) <= 0)[0]
        for i in idx:
            levels.append(_refine_c1(grid[i], grid[i + 1], tgt, phi[i], tol))
    return np.sort(np.array(levels)), dict(sign_of_phase_drift=float(sgn))


def _refine_c1(e0, e1, tgt, phi0, tol):
    """Secant/bisection on the continuous phase inside one grid cell (the wrap is resolved by the grid value phi0)."""
    def f(E):
        v = 2 * _argK(E)
        v += 2 * math.pi * round((phi0 - v) / (2 * math.pi))     # continue the branch of the cell's left end
        return v - tgt
    a, b = e0, e1
    fa, fb = f(a), f(b)
    for _ in range(200):
        m = 0.5 * (a + b) if fa * fb > 0 else (a * fb - b * fa) / (fb - fa)
        if not (min(a, b) < m < max(a, b)):
            m = 0.5 * (a + b)
        fm = f(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if abs(b - a) < tol:
            break
    return 0.5 * (a + b)


# ---------------------------------------------------------------- C4: Sierra–Townsend LLL (ST08 eq. 22/23)
# Levels: F(E) = (E/2π) log λ + 1 − N̄(E) = integer, λ = L²/(2πℓ²), N̄ = θ/π + 1; F increases for E < 2πλ (= L²/ℓ²,
# the bound). Declared λ = 60,000 (≈ 6·10⁴ levels below the bound; the lowest 3·10⁴+ are read).
LAMBDA_C4 = 60_000


def c4_levels(tol):
    import mpmath as mp
    mp.mp.dps = 30
    lam = LAMBDA_C4
    F = lambda E: E / (2 * mp.pi) * mp.log(lam) + 1 - (mp.siegeltheta(E) / mp.pi + 1)
    Emax = 2 * math.pi * lam
    nmax = int(math.floor(float(F(Emax))))
    levels = []
    E = 1e-6
    for n in range(1, nmax + 1):
        lo = E
        hi = lo + 1.0
        while float(F(hi)) < n and hi < Emax:
            hi = min(hi * 1.5 + 1, Emax)
        a, b = lo, hi
        while b - a > tol * max(1.0, a):
            m = 0.5 * (a + b)
            if float(F(m)) < n:
                a = m
            else:
                b = m
        E = 0.5 * (a + b)
        levels.append(E)
        if len(levels) >= 2 * N_TARGET:
            break
    return np.array(levels), dict(lambda_=lam, bound=Emax, n_below_bound=nmax)


if __name__ == "__main__":
    cmd = sys.argv[1]
    t = time.time()
    if cmd == "c1":
        var, res, out = sys.argv[2], int(sys.argv[3]), sys.argv[4]
        theta = {"a": math.pi / 4, "b": 0.0}[var]
        dE = {1: 0.05, 2: 0.025}[res]
        lev, info = c1_levels(theta, dE, tol={1: 1e-10, 2: 1e-12}[res])
        _save(out, f"C1{var}", res, lev, dict(theta_2011=theta, h="2pi", hbar=1, grid_dE=dE, E_max=E_MAX_C1,
                                              seconds=time.time() - t, **info))
    elif cmd == "c4":
        res, out = int(sys.argv[2]), sys.argv[3]
        lev, info = c4_levels({1: 1e-10, 2: 1e-13}[res])
        _save(out, "C4", res, lev, dict(seconds=time.time() - t, **info))
