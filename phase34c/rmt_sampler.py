"""
phase34c/rmt_sampler.py — Dumitriu–Edelman β-tridiagonal Hermite
ensemble sampling for the random-matrix-theory right null surrogates.

The β-Hermite tridiagonal of Dumitriu–Edelman (2002), "Matrix Models
for Beta Ensembles," produces eigenvalues distributed as the β-Hermite
ensemble (GOE for β=1, GUE for β=2, GSE for β=4) with O(N²) compute
and O(N) memory per ensemble — far cheaper than dense diagonalization
of N×N matrices for N ≥ 10⁴.

For the symmetry classes we need:
  - ζ → GUE → β=2
  - Dirichlet real-character → Sp(2N) bulk → β=4 (the Sp bulk
    statistics are Wigner-Dyson β=4; the Edelman–Sutton tridiagonal
    forms for the compact-group ensembles match this for bulk eigen-
    values, with edge corrections only at the outer few %)
  - Dirichlet complex-character → U(N) → β=2
  - EC L root +1 → SO(even) bulk → β=1
  - EC L root −1 → SO(odd)  bulk → β=1
The 7.5% Tracy–Widom-edge exclusion specified in the brief is
applied at this layer so the bulk-vs-bulk comparison to substrate
zeros is apples-to-apples.

Eigenvalue ranges for β-Hermite at matrix size N: bulk lives in
[-2√N, +2√N] (Wigner semicircle).  After Wigner-semicircle unfolding
the eigenvalues have unit mean spacing.

Reference: Dumitriu & Edelman, J. Math. Phys. 43, 5830 (2002).
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh_tridiagonal


def sample_beta_hermite_eigenvalues(N: int, beta: float,
                                      rng: np.random.Generator) -> np.ndarray:
    """Sample one β-Hermite ensemble of size N; return sorted eigenvalues.

    Constructs the tridiagonal:
        d[i]   = (1/√β) · Z_i              (i = 0..N-1, Z_i ~ N(0, 1))
        e[i]   = (1/√(2β)) · χ_{β·(N-i-1)} (i = 0..N-2)
    so that eigenvalues distribute as the β-Hermite ensemble
    (Hermite weight, with the standard √(2·β) normalisation).

    Output: sorted eigenvalues, shape (N,).
    """
    if beta <= 0:
        raise ValueError(f"beta must be positive, got {beta}")
    # Dumitriu–Edelman (2002) canonical β-Hermite tridiagonal:
    #   a_i ~ N(0, √(2/β))                    diagonal
    #   b_i ~ χ_{β·(n-i)} / √β                 off-diagonal
    # Eigenvalues live in [-2√n, +2√n] for any β (Wigner semicircle
    # radius R = 2√n in this normalisation).
    diag = rng.standard_normal(N) * np.sqrt(2.0 / beta)
    df = beta * (N - 1 - np.arange(N - 1))     # shape param k for χ_k
    # χ_k = √(gamma(k/2, scale=2)); handles fractional df for β=4.
    chi_samples = np.sqrt(rng.gamma(df / 2.0, 2.0))
    offdiag = chi_samples / np.sqrt(beta)
    # Eigenvalues of symmetric tridiagonal matrix
    eig = eigh_tridiagonal(diag, offdiag, eigvals_only=True)
    return np.sort(eig)


def wigner_unfold(eigenvalues: np.ndarray, N: int) -> np.ndarray:
    """Wigner-semicircle unfolding for β-Hermite eigenvalues.

    Mean density at eigenvalue λ in the bulk:
        ρ(λ) = (1/π) · √(2N − λ²/2)        (the Wigner semicircle
                                              for the standard β-Hermite
                                              normalisation, support
                                              [-2√N, +2√N])

    Unfolded coordinate: cumulative density at each eigenvalue, which
    is the analytic integral
        F(λ) = ∫_{-2√N}^{λ} ρ(s) ds
             = (1/π) · [λ √(2N − λ²/2) / 2 + 2N · arcsin(λ / (2√N))] + N/2

    Eigenvalues outside the bulk are returned as NaN.
    """
    R = 2.0 * np.sqrt(N)        # semicircle radius for the chosen scale
    lam = np.asarray(eigenvalues, dtype=np.float64)
    inside = np.abs(lam) <= R
    safe_lam = np.clip(lam, -R + 1e-12, R - 1e-12)
    # Use the semicircle distribution scaled so mean density is 1 after
    # unfolding.  N(λ) = (N/π) · [λ √(R² − λ²) / R² + arcsin(λ/R) + π/2]
    n_unfold = (N / np.pi) * (safe_lam * np.sqrt(R ** 2 - safe_lam ** 2)
                                  / R ** 2
                                + np.arcsin(safe_lam / R) + np.pi / 2.0)
    n_unfold = np.where(inside, n_unfold, np.nan)
    return n_unfold


def sample_rmt_unfolded(N: int, beta: float,
                          edge_exclude_frac: float = 0.075,
                          rng: np.random.Generator | None = None
                          ) -> np.ndarray:
    """Sample a β-Hermite ensemble of size N, unfold via Wigner
    semicircle, and return the central bulk eigenvalues after Tracy–
    Widom-edge exclusion.

    edge_exclude_frac: fraction of eigenvalues to exclude on EACH side
        (default 0.075 → retain central 85% per the brief's bulk-vs-
        edge handling specification).  Exclusion is applied on the
        sorted eigenvalue list before unfolding so the Tracy–Widom
        edge regime is dropped consistently.
    """
    if rng is None:
        rng = np.random.default_rng()
    eig = sample_beta_hermite_eigenvalues(N, beta, rng)
    n_excl = int(N * edge_exclude_frac)
    if n_excl > 0:
        eig = eig[n_excl:N - n_excl]
    return wigner_unfold(eig, N)


def beta_for_symmetry_class(symmetry_class: str) -> float:
    """Map Katz–Sarnak symmetry class → β-Hermite parameter for the bulk.

    Bulk eigenvalue spacing for compact-group ensembles agrees with
    Wigner-Dyson β at the bulk:
        U(N), GUE      → β=2
        Sp(2N), GSE    → β=4
        SO(even/odd), GOE → β=1
    Tracy–Widom edge regimes differ between classical and compact
    ensembles; the 7.5% edge exclusion brings them into agreement in
    the retained bulk for our purposes.
    """
    s = symmetry_class.upper()
    if s in ('GUE', 'U', 'UN'):
        return 2.0
    if s in ('GSE', 'SP', 'SP2N'):
        return 4.0
    if s in ('GOE', 'SO', 'SO_EVEN', 'SO_ODD'):
        return 1.0
    raise ValueError(f"unknown symmetry class: {symmetry_class}")


def sample_for_substrate(substrate: str, *, N: int, n_seeds: int,
                            extra_label: str = '',
                            edge_exclude_frac: float = 0.075,
                            base_seed: int = 0
                            ) -> list[np.ndarray]:
    """Sample n_seeds independent RMT surrogates for the given substrate
    and stratum.  Returns a list of unfolded-eigenvalue arrays.

    substrate / extra_label combinations:
        ('zeta', '')              → β=2 (GUE bulk)
        ('dirichlet', 'real')     → β=4 (Sp(2N) bulk)
        ('dirichlet', 'complex')  → β=2 (U(N) bulk)
        ('ec', 'root_plus')       → β=1 (SO(even) bulk)
        ('ec', 'root_minus')      → β=1 (SO(odd)  bulk)
    """
    key = f"{substrate}:{extra_label}".lower()
    if key == 'zeta:':
        beta = 2.0
    elif key == 'dirichlet:real':
        beta = 4.0
    elif key == 'dirichlet:complex':
        beta = 2.0
    elif key.startswith('ec:root'):
        beta = 1.0
    else:
        raise ValueError(f"unknown (substrate, extra_label) = ({substrate!r}, "
                         f"{extra_label!r})")
    out = []
    for s in range(n_seeds):
        rng = np.random.default_rng(base_seed + s)
        out.append(sample_rmt_unfolded(N, beta,
                                         edge_exclude_frac=edge_exclude_frac,
                                         rng=rng))
    return out


# ─── Self-tests ─────────────────────────────────────────────────────────────

def _verify_bulk_statistics():
    """Confirm Wigner-Dyson nearest-neighbour spacing statistics on
    Dumitriu–Edelman samples."""
    print("=" * 60)
    print("Dumitriu–Edelman bulk-spacing sanity check")
    print("=" * 60)
    for beta, label, expected_var in [
        (1.0, 'GOE', None),
        (2.0, 'GUE', None),
        (4.0, 'GSE', None),
    ]:
        rng = np.random.default_rng(42)
        nt = sample_rmt_unfolded(2000, beta, rng=rng)
        sp = np.diff(nt)
        sp = sp[~np.isnan(sp)]
        print(f"  β={beta:.0f} {label}: N=2000, "
              f"mean spacing = {sp.mean():.4f}, std = {sp.std():.4f}")
    # Wigner-Dyson predicted std at unit mean spacing:
    #   GOE (β=1):   ≈ √(4/π − 1) ≈ 0.521
    #   GUE (β=2):   ≈ √(3π/8 − 1) ≈ 0.421
    #   GSE (β=4):   ≈ smaller still ≈ 0.310
    print("  expected: GOE std ≈ 0.52, GUE std ≈ 0.42, GSE std ≈ 0.31")


if __name__ == '__main__':
    _verify_bulk_statistics()
