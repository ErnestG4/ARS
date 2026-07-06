"""
phase34d/gaussian_primes.py — Gaussian prime ideal angle generator.

Generates angles θ_π ∈ [0, π/2) for prime ideals of Z[i] of norm ≤ X,
per the Rudnick-Waxman 2019 convention:
  - For each rational prime p ≡ 1 mod 4 (split), find the unique
    representation p = a² + b² with a > 0 and b > 0 (the b = 0 case
    only occurs for p = 2 → 1²+1²).
  - Take θ = arctan(b / a) in (0, π/2).
  - One angle per prime IDEAL (the 8 generator representations
    (±a±ib, ±b±ia) collapse to one angle by the unit-orbit reduction;
    the conjugate ideal contributes the same angle).
  - p ≡ 3 mod 4 (inert): no angle (inert primes have no non-trivial
    angle in the unit orbit).
  - p = 2 ramified: 1² + 1² gives θ = π/4 (kept as a single
    representative).

The output is the sorted array of angles, suitable for direct insertion
into ARS pipelines (the angle-sorted sequence is the spectral coordinate;
spacings = np.diff(angles) are the unit-mean-normalised event-time
sequence after unfolding by the Hecke-uniform density 2/π on [0, π/2)).

References:
  - Rudnick, Z. & Waxman, E. (2019). Angles of Gaussian primes. Isr. J.
    Math. 232, 159–199. §1.1.
"""
from __future__ import annotations

import numpy as np


def sieve_primes(limit: int) -> np.ndarray:
    """Sieve of Eratosthenes up to `limit` (inclusive). Returns ascending primes."""
    if limit < 2:
        return np.array([], dtype=np.int64)
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    return np.flatnonzero(sieve).astype(np.int64)


def _tonelli_shanks(n: int, p: int) -> int:
    """Return x with x² ≡ n (mod p), p odd prime, n a quadratic residue mod p.

    Tonelli-Shanks algorithm. Returns one of the two square roots; the other
    is p - x.
    """
    # Trivial case
    if pow(n, (p - 1) // 2, p) != 1:
        raise ValueError(f"{n} is not a QR mod {p}")
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    # Find Q, S with p - 1 = Q · 2^S, Q odd
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Find a quadratic non-residue z
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
        # Find least i with t^(2^i) = 1
        i = 0
        temp = t
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


def split_p_as_sum_of_two_squares(p: int) -> tuple[int, int]:
    """For a prime p ≡ 1 mod 4, find a, b > 0 with a² + b² = p.

    Cornacchia's algorithm via Tonelli-Shanks for x² ≡ -1 mod p, then
    Euclidean reduction. O(log² p) per prime — much faster than the
    O(√p) brute-force search at large p.

    Returns (a, b) with a ≥ b > 0 (canonical orientation).

    Raises
    ------
    ValueError if p is not ≡ 1 mod 4 (and not p=2).
    """
    if p == 2:
        return (1, 1)
    if p % 4 != 1:
        raise ValueError(f"p = {p} is not ≡ 1 mod 4; cannot represent as sum of two squares")
    # Find x with x² ≡ -1 (mod p)
    x = _tonelli_shanks(p - 1, p)
    if x * 2 > p:
        x = p - x
    # Euclidean reduction: r_0 = p, r_1 = x, ...; first r_i below √p is one component
    a, b = p, x
    sqrt_p = int(np.sqrt(p))
    while b > sqrt_p:
        a, b = b, a % b
    # Now b ≤ √p; the other component is √(p - b²)
    other_sq = p - b * b
    other = int(np.sqrt(other_sq))
    # Adjust for rounding
    if other * other != other_sq:
        for d in (-1, +1, -2, +2):
            if (other + d) * (other + d) == other_sq:
                other = other + d
                break
        else:
            raise ValueError(f"Cornacchia failed for p={p}: b={b}, other²={other_sq}")
    a_, b_ = max(other, b), min(other, b)
    if a_ * a_ + b_ * b_ != p:
        raise ValueError(f"verification failed: {a_}² + {b_}² = {a_*a_+b_*b_} ≠ {p}")
    return (a_, b_)


def gaussian_prime_angles(X: int,
                          include_ramified: bool = True,
                          both_ideals: bool = True) -> np.ndarray:
    """Generate sorted angles of Gaussian prime ideals of norm ≤ X.

    A rational prime p ≡ 1 mod 4 splits as p = π · π̄ in Z[i] with
    π = a + ib (a > 0, b > 0), giving TWO distinct prime ideals (π) and
    (π̄) of norm p. The canonical representatives (with a > 0, b > 0) are:
        (π)  → α = a + ib (with a ≥ b convention), θ = arctan(b/a) ∈ (0, π/4]
        (π̄) → α = b + ia (the unit-conjugate),   θ = π/2 - arctan(b/a) ∈ [π/4, π/2)
    Both angles are recorded so the output has one angle per prime ideal,
    matching the Rudnick-Waxman 2019 convention (N = π(X) = #{p prime in
    Z[i] : Norm p ≤ X}).

    Parameters
    ----------
    X                : norm cap. Each rational split prime p ≡ 1 mod 4 with
                       p ≤ X contributes 2 angles; p = 2 ramified contributes
                       1; inert p ≡ 3 mod 4 with p² ≤ X are at θ = 0
                       (the trivial axis) and excluded by default.
    include_ramified : whether to include p = 2 (one angle at π/4).
    both_ideals      : whether each split p contributes BOTH ideals (two
                       angles, default True) or just one (legacy convention).

    Returns
    -------
    angles : (N,) sorted float array of θ_π ∈ [0, π/2).
    """
    primes = sieve_primes(X)
    angles = []
    for p in primes:
        p = int(p)
        if p == 2:
            if include_ramified:
                angles.append(np.pi / 4)
        elif p % 4 == 1:
            a, b = split_p_as_sum_of_two_squares(p)
            # (π) = (a + ib), θ = arctan(b/a) ∈ (0, π/4]
            theta_pi = np.arctan2(b, a)
            angles.append(theta_pi)
            if both_ideals:
                # (π̄) = (a - ib); canonical rep with a > 0, b > 0 is b + ia,
                # θ = arctan(a/b) = π/2 - arctan(b/a) ∈ [π/4, π/2)
                theta_pibar = np.pi / 2 - theta_pi
                # Avoid double-counting when a == b (on the symmetry axis π/4)
                if abs(theta_pibar - theta_pi) > 1e-12:
                    angles.append(theta_pibar)
        # p % 4 == 3: inert (norm p²); RW convention θ = 0, skip
    return np.sort(np.array(angles, dtype=np.float64))


def hecke_unfold_gaussian(angles: np.ndarray) -> np.ndarray:
    """Apply Hecke-uniform unfolding to angle sequence on [0, π/2).

    For Gaussian prime angles, Hecke 1918 equidistribution says the density
    is 2/π uniform on [0, π/2). The unfolded coordinate has unit mean spacing:

        x_unfolded(θ) = (2N / π) · θ

    where N is the number of angles. After unfolding,
    np.diff(x_unfolded) has mean 1.0 exactly.
    """
    N = len(angles)
    return angles * (2.0 * N / np.pi)


if __name__ == '__main__':
    import sys
    X = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    print(f"Generating Gaussian prime angles for norm cap X = {X}")
    angles = gaussian_prime_angles(X)
    print(f"  N = {len(angles)} angles")
    print(f"  range: [{angles[0]:.6f}, {angles[-1]:.6f}]   (should be ⊂ [0, {np.pi/2:.6f}))")
    print(f"  first 5: {angles[:5]}")
    print(f"  last 5:  {angles[-5:]}")
    unfolded = hecke_unfold_gaussian(angles)
    spacings = np.diff(unfolded)
    print(f"  mean unfolded spacing: {np.mean(spacings):.6f}   (should be ~1.0)")
    print(f"  CV of unfolded spacings: {np.std(spacings)/np.mean(spacings):.4f}")
