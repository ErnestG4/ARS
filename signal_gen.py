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


# ─── β-ensemble (Dumitriu-Edelman) ──────────────────────────────────────────

def make_beta_ensemble_eigenvalues(n_points: int, beta: float,
                                   seed: int = 0,
                                   bulk_frac: float = 0.8) -> np.ndarray:
    """Hermite β-ensemble eigenvalues via the Dumitriu-Edelman tridiagonal.

    Eigenvalue density ∝ |Δ(λ)|^β · exp(-1/4 · Σ λ²) .  The tridiagonal:
        T[i, i]      = √2 · N(0, 1)
        T[i, i+1]    = √(χ²_{(n-1-i)·β})         for i = 0..n-2

    Returns the **sorted, bulk-trimmed, semicircle-unfolded** eigenvalue
    sequence with unit mean spacing.  The semicircle CDF compresses
    edge eigenvalues to near-zero spacing (density vanishes at ±R) —
    we generate at n_internal = n_points / bulk_frac and trim the
    outer (1 - bulk_frac) fraction from each end so that the returned
    sequence has length n_points and clean bulk statistics.
    """
    from scipy.linalg import eigh_tridiagonal
    n_internal = int(np.ceil(n_points / bulk_frac))
    rng = np.random.default_rng(seed)
    diag = np.sqrt(2.0) * rng.standard_normal(n_internal)
    off = np.sqrt(rng.chisquare(
        beta * (n_internal - 1 - np.arange(n_internal - 1))))
    eigs = eigh_tridiagonal(diag, off, eigvals_only=True)
    eigs = np.sort(eigs)
    R = np.sqrt(2.0 * beta * n_internal)
    x = np.clip(eigs / R, -1.0, 1.0)
    cdf = (x * np.sqrt(np.maximum(1 - x*x, 0.0)) + np.arcsin(x)) / np.pi + 0.5
    unfolded = cdf * n_internal
    trim = (n_internal - n_points) // 2
    out = unfolded[trim:trim + n_points]
    sp = np.diff(out)
    if sp.size and sp.mean() > 0:
        out = out / sp.mean()
    return out


# ─── Matérn-II hard-core point process ──────────────────────────────────────

def make_hardcore_process(n_points: int, min_spacing: float,
                          seed: int = 0,
                          density_factor: float = 4.0) -> np.ndarray:
    """Matérn-II hard-core thinning.

    A Poisson candidate process is generated at `density_factor`× target
    density.  Each candidate is given a random mark; a candidate is
    retained iff no other candidate within `min_spacing` has a smaller
    mark.

    `min_spacing` is in units where the post-thinning mean spacing is
    intended to be ≈ 1 (we trim/unfold to enforce this).  Returns a
    sorted point process of length ≤ n_points with unit-mean spacing.
    """
    rng = np.random.default_rng(seed)
    target_span = float(n_points)
    n_cand = int(n_points * density_factor)
    cand_t = np.sort(rng.uniform(0.0, target_span * 1.5, size=n_cand))
    marks = rng.uniform(0.0, 1.0, size=n_cand)
    # Retain by mark order, brute force O(n²) — fine at n_points = 2000.
    keep_t: list[float] = []
    keep_t_arr = np.zeros(0)
    for i in np.argsort(marks):
        t = float(cand_t[i])
        if keep_t_arr.size == 0 or np.min(np.abs(keep_t_arr - t)) >= min_spacing:
            keep_t.append(t)
            keep_t_arr = np.append(keep_t_arr, t)
            if len(keep_t) >= n_points:
                break
    pts = np.sort(np.asarray(keep_t, dtype=np.float64))
    if pts.size < 2:
        return pts
    # Renormalise so mean spacing = 1.
    sp = np.diff(pts)
    return pts / sp.mean() if sp.mean() > 0 else pts


# ─── Ginibre eigenvalue projections ──────────────────────────────────────────

def make_uniform_jitter(n_points: int, jitter: float, seed: int = 0) -> np.ndarray:
    """Uniform spacing with Gaussian jitter: t_n = n + jitter · N(0, 1).

    A regular comb perturbed by independent Gaussian noise.  At
    jitter = 0 this is a perfect lattice; at jitter ≫ 1 it approaches
    Poisson (after sorting and resolving collisions).  This is the
    canonical "near-periodic" calibrator — distinct from any
    Wigner-Dyson β-ensemble.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(1, n_points + 1, dtype=np.float64) + \
        jitter * rng.standard_normal(n_points)
    t = np.sort(t)
    # Enforce strict monotonicity (resolve any collisions from large jitter)
    return np.maximum.accumulate(t + 1e-9 * np.arange(t.size))


def make_ginibre_projected(n_points: int, projection: str = "real_part",
                           seed: int = 0,
                           bulk_frac: float = 0.8) -> np.ndarray:
    """Ginibre ensemble projected to a 1D point process.

    A complex iid Gaussian matrix has eigenvalues uniformly on a unit
    disk in the complex plane (Ginibre's theorem).  Two natural 1D
    projections:

      "real_part":              real parts of the complex eigenvalues
      "symmetric_part_eigvals": eigenvalues of (G + G*) / 2

    Both yield Wigner-semicircle-shaped real-valued distributions for
    unit-normalised Ginibre.  Bulk-trim and semicircle-unfold to unit
    mean spacing.
    """
    n_internal = int(np.ceil(n_points / bulk_frac))
    rng = np.random.default_rng(seed)
    G = (rng.standard_normal((n_internal, n_internal)) +
         1j * rng.standard_normal((n_internal, n_internal))) / np.sqrt(2.0 * n_internal)
    if projection == "real_part":
        eigs = np.sort(np.linalg.eigvals(G).real)
    elif projection == "symmetric_part_eigvals":
        H = (G + G.conj().T) * 0.5
        eigs = np.sort(np.linalg.eigvalsh(H).real)
    else:
        raise ValueError(f"unknown projection: {projection!r}")
    R = max(1.0, float(np.max(np.abs(eigs))) * 1.001)
    x = np.clip(eigs / R, -1.0, 1.0)
    cdf = (x * np.sqrt(np.maximum(1 - x*x, 0.0)) + np.arcsin(x)) / np.pi + 0.5
    unfolded = cdf * n_internal
    trim = (n_internal - n_points) // 2
    out = unfolded[trim:trim + n_points]
    sp = np.diff(out)
    if sp.size and sp.mean() > 0:
        out = out / sp.mean()
    return out
