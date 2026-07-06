"""
phase34d/circular_sampler.py — Haar-distributed sampling from the classical
compact groups U(N), O(N), Sp(2N) and the associated Circular ensembles
CUE / COE / CSE.

Implementation follows Mezzadri 2007 (Notices AMS 54:5, 592–604, "How to
generate random matrices from the classical compact groups"). The
QR-with-phase-normalization recipe is the load-bearing trick: naive QR
of a complex Ginibre matrix gives Q with a non-Haar phase distribution
on the eigenphases, and the D = diag(R)/|diag(R)| correction restores
Haar invariance.

For Phase 34d-G the CUE sampler is the natural right-null calibrator for
prime-angle substrates — Rudnick-Waxman Proposition 5.3 shows that
U(N), USp(2N), SO(2N) all give the same min(n, N) bulk variance, so the
three Circular ensembles are *bulk-indistinguishable* on NNS / RF Mode B /
p-adic v4. The global moment σ²(K, X) is what discriminates at family level.

References:
  - Mezzadri, F. (2007). How to generate random matrices from the classical
    compact groups. Notices Amer. Math. Soc. 54:5, 592–604.
  - Rudnick, Z. & Waxman, E. (2019). Angles of Gaussian primes. Isr. J. Math.
    232, 159–199. Proposition 5.3.
"""
from __future__ import annotations

import numpy as np


def sample_cue(N: int, rng: np.random.Generator) -> np.ndarray:
    """Sample one Haar-distributed unitary matrix U ∈ U(N).

    Implements Mezzadri 2007 recipe: complex Ginibre → QR → phase-normalize.

    Returns
    -------
    U : (N, N) complex array, with U U^* = I exactly (up to FP).
    """
    A = (rng.standard_normal((N, N))
         + 1j * rng.standard_normal((N, N))) / np.sqrt(2.0)
    Q, R = np.linalg.qr(A)
    # Mezzadri 2007 eq. (38): phase-normalize columns so Q is Haar-distributed
    # on U(N). Naive QR returns Q with a phase that is NOT Haar.
    d = np.diag(R)
    ph = d / np.abs(d)
    return Q * ph[np.newaxis, :]


def sample_cue_eigenphases(N: int, rng: np.random.Generator) -> np.ndarray:
    """Sample eigenphases of one Haar-distributed U(N) matrix, sorted on [0, 2π).

    Returns
    -------
    phases : (N,) float array, sorted, in [0, 2π).
    """
    U = sample_cue(N, rng)
    ev = np.linalg.eigvals(U)
    ph = np.angle(ev) % (2 * np.pi)
    return np.sort(ph)


def sample_coe(N: int, rng: np.random.Generator) -> np.ndarray:
    """Sample one matrix from the Circular Orthogonal Ensemble COE = U(N)/O(N).

    COE is the distribution of U · U^T for U Haar on U(N). The eigenphases of
    a COE element are distributed as Dyson β=1 on the unit circle (orthogonal
    symmetry — invariant under U ↦ O^T U O for O ∈ O(N)).
    """
    U = sample_cue(N, rng)
    return U @ U.T


def sample_coe_eigenphases(N: int, rng: np.random.Generator) -> np.ndarray:
    """Sample eigenphases of one COE matrix, sorted on [0, 2π)."""
    M = sample_coe(N, rng)
    ev = np.linalg.eigvals(M)
    ph = np.angle(ev) % (2 * np.pi)
    return np.sort(ph)


def sample_cse_eigenphases(N: int, rng: np.random.Generator) -> np.ndarray:
    """Sample CSE eigenphases (size 2N, returned as N doubly-degenerate values).

    CSE = U(2N) / Sp(2N). The standard construction: take U Haar on U(2N),
    form M = U · J · U^T · J^{-1} with J the 2N×2N symplectic form
    J = ([0, I_N], [-I_N, 0]); M is then quaternionic-self-dual and its
    eigenvalues come in Kramers pairs (each value appears twice).

    Returns
    -------
    phases : (N,) float array of the N distinct eigenphases (each occurs
             with multiplicity 2 in the spectrum of the full 2N×2N matrix).
    """
    twoN = 2 * N
    U = sample_cue(twoN, rng)
    J = np.zeros((twoN, twoN), dtype=complex)
    J[:N, N:] = np.eye(N)
    J[N:, :N] = -np.eye(N)
    M = U @ J @ U.T @ np.linalg.inv(J)
    ev = np.linalg.eigvals(M)
    ph = np.angle(ev) % (2 * np.pi)
    ph_sorted = np.sort(ph)
    # Collapse Kramers pairs: take every other entry after sort.
    return ph_sorted[::2]


def circular_unit_mean_spacings(N: int, kind: str,
                                rng: np.random.Generator) -> np.ndarray:
    """Sample one Circular-ensemble realisation and return unit-mean spacings.

    Parameters
    ----------
    N    : matrix size (number of eigenphases on [0, 2π)).
    kind : one of {'CUE', 'COE', 'CSE'}.
    rng  : numpy random generator.

    Returns
    -------
    spacings : (N - 1,) float array of unit-mean nearest-neighbour spacings.
               Mean of returned array is 1.0 (up to FP noise of sampling).
    """
    if kind == 'CUE':
        ph = sample_cue_eigenphases(N, rng)
    elif kind == 'COE':
        ph = sample_coe_eigenphases(N, rng)
    elif kind == 'CSE':
        ph = sample_cse_eigenphases(N, rng)
    else:
        raise ValueError(f"unknown circular ensemble: {kind!r}")
    raw = np.diff(ph)
    # Unit-mean normalisation. For Haar U(N), mean phase spacing is 2π/N.
    return raw / np.mean(raw)


__all__ = [
    'sample_cue',
    'sample_cue_eigenphases',
    'sample_coe',
    'sample_coe_eigenphases',
    'sample_cse_eigenphases',
    'circular_unit_mean_spacings',
]
