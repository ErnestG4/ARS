"""
phase34c/unfolding.py — substrate-specific unfolding to unit mean spacing.

ζ zeros
-------
The non-trivial Riemann zeros γ_n have local mean spacing
2π / log(γ / 2π).  The Riemann-Siegel θ function θ(t) provides the
exact unfolding: the zero-counting function

    N(T) = θ(T)/π + 1 + S(T)         (Riemann-von Mangoldt)

with S(T) the fluctuation term.  Unfolded coordinate ñ_n = θ(γ_n)/π;
unit-mean spacing in ñ by construction.

θ(t) = arg Γ(1/4 + it/2) − (t/2) log π
     ≈ (t/2) log(t/(2π·e)) + π/8           for t ≫ 1   (large-t expansion)

We use the large-t expansion below; for γ ≥ 14 it is accurate to
≪ 10⁻³ of one mean spacing.

Dirichlet L-zeros (per character)
---------------------------------
Per Iwaniec-Kowalski, Eq. 5.27, the analytic-conductor unfolding for a
primitive Dirichlet character χ mod q is

    ñ = (γ / 2π) · log(q · γ / (2π·e))

For complex characters the conductor q enters as is; for real
characters the same formula applies with the appropriate functional
equation.

EC L-zeros (per curve)
----------------------
For an elliptic curve E of conductor N_E, the analytic conductor is
N_E · (γ / 2π)².  The unfolding is

    ñ = (γ / 2π) · log(N_E · (γ / 2π)² / e²)
       = (γ / 2π) · (log(N_E / e²) + 2 log(γ / 2π))

Mean spacing 1 in ñ across the curve's zeros.
"""
from __future__ import annotations

import numpy as np

LOG_TWO_PI = float(np.log(2 * np.pi))


def riemann_siegel_theta(t: np.ndarray) -> np.ndarray:
    """θ(t) via the standard large-t asymptotic.

    θ(t) ≈ (t/2) log(t / (2π)) − t/2 + π/8 + 1/(48·t) − 7/(5760·t³) + …

    Accurate to << 1 mean spacing for t ≥ 14 (which covers all
    non-trivial zeros).  The 1/(48 t) and higher corrections are
    included for precision at small γ.
    """
    t = np.asarray(t, dtype=np.float64)
    safe = np.where(t > 1e-3, t, 1e-3)
    main = (safe / 2.0) * np.log(safe / (2.0 * np.pi)) - safe / 2.0 + np.pi / 8.0
    corr = 1.0 / (48.0 * safe) - 7.0 / (5760.0 * safe ** 3)
    return main + corr


def zeta_unfold(gamma: np.ndarray) -> np.ndarray:
    """Unfold ζ zeros via Riemann-Siegel θ:
        ñ = θ(γ)/π + 1
    so that ⟨Δñ⟩ ≈ 1 over the bulk.
    """
    return riemann_siegel_theta(gamma) / np.pi + 1.0


def zeta_inverse_unfold(n_tilde: np.ndarray,
                          gamma_seed: np.ndarray | None = None,
                          tol: float = 1e-6,
                          max_iter: int = 50) -> np.ndarray:
    """Invert ζ unfolding via Newton's method: find γ such that
    θ(γ)/π + 1 = ñ.

    dθ/dt = (1/2) log(t/(2π))   (leading order)
    """
    n_tilde = np.asarray(n_tilde, dtype=np.float64)
    if gamma_seed is None:
        # Crude seed from leading-order inversion of θ(γ)/π ≈
        # (γ/(2π)) log(γ/(2π·e)) so γ ≈ 2π·ñ / log ñ for ñ ≫ 1
        gamma_seed = 2.0 * np.pi * np.maximum(n_tilde, 1.0) / np.maximum(
            np.log(np.maximum(n_tilde, 2.0)), 1.0)
    gamma = gamma_seed.copy()
    for _ in range(max_iter):
        residual = riemann_siegel_theta(gamma) / np.pi + 1.0 - n_tilde
        deriv = 0.5 * np.log(np.maximum(gamma, 2.0 * np.pi + 0.1)
                                / (2.0 * np.pi)) / np.pi
        deriv = np.where(np.abs(deriv) > 1e-9, deriv, 1e-9)
        gamma = gamma - residual / deriv
        if np.all(np.abs(residual) < tol):
            break
    return gamma


def dirichlet_unfold(gamma: np.ndarray, conductor: int) -> np.ndarray:
    """Per-character analytic-conductor unfolding (Iwaniec-Kowalski 5.27).

    ñ = (γ / 2π) · log(q · γ / (2π·e))
    """
    gamma = np.asarray(gamma, dtype=np.float64)
    return (gamma / (2 * np.pi)) * (np.log(conductor * gamma / (2 * np.pi))
                                       - 1.0)


def ec_unfold(gamma: np.ndarray, conductor: int) -> np.ndarray:
    """Per-curve conductor unfolding for elliptic curve L-functions.

    ñ = (γ / 2π) · (log(N_E / e²) + 2 log(γ / 2π))
    """
    gamma = np.asarray(gamma, dtype=np.float64)
    log_2pi = LOG_TWO_PI
    return (gamma / (2 * np.pi)) * (np.log(conductor) - 2.0
                                       + 2.0 * (np.log(gamma) - log_2pi))


def unfold_substrate_zeros(substrate: str,
                             zeros: np.ndarray,
                             conductor: int | None = None) -> np.ndarray:
    """Dispatch to substrate-appropriate unfolding."""
    if substrate == 'zeta':
        return zeta_unfold(zeros)
    if substrate == 'dirichlet':
        if conductor is None:
            raise ValueError("Dirichlet unfolding requires conductor")
        return dirichlet_unfold(zeros, conductor)
    if substrate == 'ec':
        if conductor is None:
            raise ValueError("EC unfolding requires conductor")
        return ec_unfold(zeros, conductor)
    raise ValueError(f"unknown substrate: {substrate}")


def pool_unfolded(per_object_zeros: list[tuple[int, np.ndarray]],
                    substrate: str) -> np.ndarray:
    """Pool unfolded zeros across multiple objects (characters / curves).

    per_object_zeros : list of (conductor, γ-array) tuples.
    Each object's zeros are unfolded with its own conductor, then
    concatenated.

    Filters γ ≤ 1e-6 per object before unfolding (EC L curves with
    analytic rank > 0 have a γ=0 functional-equation zero which
    would NaN-poison the unfolding via log(γ)).
    """
    if substrate == 'zeta':
        raise ValueError("ζ is a single object; no pooling needed")
    parts = []
    for cond, gz in per_object_zeros:
        gz_arr = np.asarray(gz)
        gz_arr = gz_arr[gz_arr > 1e-6]
        if gz_arr.size == 0:
            continue
        nz = unfold_substrate_zeros(substrate, gz_arr, conductor=cond)
        parts.append(nz)
    return np.sort(np.concatenate(parts))


# ─── Sanity ─────────────────────────────────────────────────────────────────

def _sanity():
    """Quick check: mean spacing of unfolded ζ zeros ≈ 1."""
    import os
    sys_path_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from zeros_loaders import load_zeta_zeros, load_dirichlet, load_ec_curves
    print("=" * 60)
    print("Unfolding sanity check")
    print("=" * 60)

    z = load_zeta_zeros('odlyzko_zeros1.txt')[:5000]
    nt = zeta_unfold(z)
    sp = np.diff(nt)
    print(f"ζ first 5K zeros — unfolded spacing mean: {sp.mean():.4f}, "
          f"std: {sp.std():.4f}")
    # Expected: mean ≈ 1.000, std ≈ 1 (Wigner)

    d = load_dirichlet()
    e = d[0]
    nt = dirichlet_unfold(np.asarray(e['zeros']), e['conductor'])
    sp = np.diff(nt)
    print(f"Dirichlet q={e['q']} (real char) — unfolded spacing mean: "
          f"{sp.mean():.4f}, std: {sp.std():.4f}")

    ec = load_ec_curves()
    c = ec[0]
    nt = ec_unfold(np.asarray(c['zeros']), c['conductor'])
    sp = np.diff(nt)
    print(f"EC L curve {c['label']} (cond {c['conductor']}) — unfolded "
          f"spacing mean: {sp.mean():.4f}, std: {sp.std():.4f}")


if __name__ == '__main__':
    _sanity()
