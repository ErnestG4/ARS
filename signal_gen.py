"""
Signal generators for the criticality tool.

Re-uses scanner.make_zeta_signal / make_white_noise / etc. from the
sibling riemann_explorer/, and adds null-hypothesis generators specific
to criticality work — most notably make_poisson_zeta_like, which has
the same chirp envelope as the ζ signal but Poisson-spaced "frequencies"
instead of GUE-spaced ones.
"""
from __future__ import annotations

import os, sys
import numpy as np

# Re-use the scanner's generators (zeta, primes, mobius, noise, pure_fm).
sys.path.insert(0, '/home/combust/fmexplorer/riemann_explorer')
import scanner   # noqa: E402

ZETA_ZEROS = scanner.ZETA_ZEROS

make_zeta_signal     = scanner.make_zeta_signal
make_prime_gap_signal = scanner.make_prime_gap_signal
make_mobius_signal   = scanner.make_mobius_signal
make_white_noise     = scanner.make_white_noise
make_pure_tone       = scanner.make_pure_tone
make_pure_fm         = scanner.make_pure_fm


def make_poisson_zeta_like(
    sr:       float = 44100.0,
    duration: float = 4.0,
    n_points: int   = 50,
    seed:     int   = 0,
    height_min: float | None = None,
    height_max: float | None = None,
) -> np.ndarray:
    """
    Null hypothesis for the ζ signal.  Same form,
        f(t) = (1/n) Σ_k cos(t_k · log(t+1)) / √t_k,
    but `t_k` are independent Uniform(t_min, t_max) draws (sorted) instead
    of the actual Riemann zero heights.  Result: same chirp envelope, same
    density of "frequencies", but Poisson level statistics in the t_k.

    If the F ≈ 12 super-Poisson clustering we see on the real ζ signal is
    induced by chirp dynamics rather than ζ-zero structure, this signal
    will reproduce it.  If the clustering is intrinsic to the GUE-spaced
    zero heights, this null will show different (Poisson-like) F.
    """
    rng = np.random.default_rng(seed)
    if height_min is None:
        height_min = float(ZETA_ZEROS[0])
    if height_max is None:
        height_max = float(ZETA_ZEROS[min(n_points, len(ZETA_ZEROS)) - 1])
    heights = np.sort(rng.uniform(height_min, height_max, n_points))

    N = int(sr * duration)
    t = np.arange(1, N + 1, dtype=np.float64) / sr
    log_t = np.log(t + 1.0)
    sig = np.zeros(N, dtype=np.float64)
    for tn in heights:
        sig += np.cos(tn * log_t) / np.sqrt(tn)
    return (sig / n_points).astype(np.float32)


def _semicircle_cdf_unit(x):
    """CDF of Wigner semicircle ρ(x) = (2/π)√(1−x²) on [-1, 1]."""
    x = np.clip(x, -1.0, 1.0)
    return 0.5 + (x * np.sqrt(1.0 - x * x) + np.arcsin(x)) / np.pi


def make_gue_eigenvalue_signal(
    sr:       float = 44100.0,
    duration: float = 4.0,
    n_points: int   = 100,
    seed:     int   = 42,
    rescale_to_zeta_range: bool = True,
    semicircle_R: float = 2.0,
) -> np.ndarray:
    """
    Synthetic GUE FM-style calibration signal: same chirp form as ζ, but
    `t_k` are eigenvalues of a GUE random matrix unfolded by the Wigner
    semicircle CDF — so their spacing distribution follows the Wigner
    surmise (verified KS ≈ 0.04 at N=500, ≈ 0.06 at N=100).

    Matrix normalisation is H = (A + A†)/√(2N) with A_ij ~ CN(0, 1) →
    bulk semicircle on [-2, 2], so the semicircle CDF is applied at
    R = 2 (eigs/R lives in [-1, 1]).

    By default the unfolded eigenvalues are then rescaled linearly to
    span the first n_points ζ zeros' range, which preserves the
    normalised-spacing distribution while matching ζ's spectral content.
    """
    rng = np.random.default_rng(seed)
    N = n_points
    A = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    eig = np.sort(np.linalg.eigvalsh(H).real)

    # Wigner-semicircle unfolding with proper R.
    eig_unfolded = _semicircle_cdf_unit(eig / semicircle_R) * N

    if rescale_to_zeta_range:
        z_min = float(ZETA_ZEROS[0])
        z_max = float(ZETA_ZEROS[min(N, len(ZETA_ZEROS)) - 1])
        eig_unfolded = z_min + (eig_unfolded - eig_unfolded[0]) * (z_max - z_min) / (
            eig_unfolded[-1] - eig_unfolded[0])

    t = np.arange(1, int(sr * duration) + 1, dtype=np.float64) / sr
    log_t = np.log(t + 1.0)
    sig = np.zeros(t.size, dtype=np.float64)
    for lam in eig_unfolded:
        sig += np.cos(lam * log_t) / np.sqrt(abs(lam) + 1.0)
    return (sig / N).astype(np.float32)
