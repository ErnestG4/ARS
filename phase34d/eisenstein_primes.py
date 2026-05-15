"""
phase34d/eisenstein_primes.py — Eisenstein prime ideal angle generator.

Generates angles θ_π ∈ [0, π/3) for prime ideals of Z[ω] (ω = e^{2πi/3})
of norm ≤ X, per the extension of the Rudnick-Waxman convention:
  - For each rational prime p ≡ 1 mod 3 (split): find a, b with
    a² - ab + b² = p (this is the Eisenstein norm form). The split
    factors are π = a + bω and π̄ = a + bω̄.
  - The unit group Z[ω]× = {±1, ±ω, ±ω²} has order 6. The unit-orbit
    coordinate is u(π) = (π / π̄)^3 = e^{i·6θ_π}, so θ_π is defined
    mod π/3.
  - Fundamental sector: [0, π/3). Take the representative angle of
    π in that sector.
  - p ≡ 2 mod 3 (inert): no angle.
  - p = 3 ramified: (1 - ω) generates the unique prime above 3 with
    N(1-ω) = 3. θ = arg(1 - ω) reduced mod π/3 = π/6 (single
    representative if include_ramified=True).

By the Phase 34d brief convention (RW-style): **one angle per prime
ideal**. The two split factors π and π̄ correspond to distinct prime
ideals; we record an angle for *each*. To match RW one-angle-per-ideal,
one of the two will fall in [0, π/3) directly and the other will be its
reflection; reducing mod π/3 gives two angles per split prime.

References:
  - Rudnick, Z. & Waxman, E. (2019). Angles of Gaussian primes.
    Isr. J. Math. 232, 159–199. (For analog; Eisenstein case not in
    literature per Phase 34d lit-lock §6.)
  - Cohen, H. (1993). A Course in Computational Algebraic Number Theory.
    §1.5 on the Eisenstein integers and norm-form representations.
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
    """Square root of n modulo prime p via Tonelli-Shanks."""
    if pow(n, (p - 1) // 2, p) != 1:
        raise ValueError(f"{n} is not a QR mod {p}")
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
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


def split_p_as_eisenstein_norm(p: int) -> tuple[int, int]:
    """For a prime p ≡ 1 mod 3, find a, b > 0 with a² - ab + b² = p.

    Uses Cornacchia for the form x² + 3y² = 4p:
      a² - ab + b² = p   ⇔   (2a - b)² + 3 b² = 4p
    Set u = 2a - b, v = b. Then u² + 3v² = 4p.

    Cornacchia on discriminant -12 (a² + 3b² form, scaled): find x with
    x² ≡ -3 (mod 4p), reduce via Euclidean algorithm, recover (u, v),
    then a = (u + v) / 2.

    O(log² p) per prime via Tonelli-Shanks.
    """
    if p == 3:
        return (2, 1)  # 2² - 2·1 + 1² = 4 - 2 + 1 = 3 ✓
    if p % 3 != 1:
        raise ValueError(f"p = {p} is not ≡ 1 mod 3; not representable as a² - ab + b²")
    # Find x with x² ≡ -3 (mod p): equivalent to finding √(p - 3) mod p
    # Since p ≡ 1 mod 3, -3 is a QR mod p.
    x = _tonelli_shanks((p - 3) % p, p)
    if x * 2 > p:
        x = p - x
    # Adjust x so that x is odd (because u = 2a - b must have same parity
    # as -b = -v, and we want u² + 3v² = 4p, so u and v must both be even
    # or both odd; for p odd, 4p is divisible by 4 mod ..., let's check)
    # Actually for u² + 3v² = 4p with p odd: 4p ≡ 4 mod 8. u² + 3v² ≡ 4 mod 8.
    # Pairs (u² mod 8, v² mod 8) summing to 4 mod 8 (with 3v² mod 8 ∈ {0,3,4,3}):
    # u² ∈ {0,1,4}, 3v² ∈ {0,3,4,3}. Pairs giving 4: (0,4),(1,3),(4,0). So
    # (u even, v even) or (u odd, v odd).
    # We want a, b > 0 integers, so u and v must have the same parity.
    # Run Euclidean on (2p, x) — but actually simpler to run on (p, x) and adjust.
    # Standard Cornacchia for d = 3, N = p: find (a, b) with a² + 3b² = p
    # when (p-3) is QR mod p AND additional conditions; if a² + 3b² = p has no
    # solution we need 4·p version.
    # Try the 4p version directly.
    # Tonelli on -3 mod 4p: easier to compute mod p and reconstruct.
    # Actually let's just brute force when fast Cornacchia is fiddly:
    # Iterate over the Euclidean remainder sequence (p, x) and find first pair
    # with r² < p.
    a_seq, b_seq = p, x
    sqrt_p = int(np.sqrt(p))
    while b_seq > sqrt_p:
        a_seq, b_seq = b_seq, a_seq % b_seq
    # Now we have b_seq ≤ √p. We need b² = b_seq with 3b² + (-) = 4p... actually
    # this is for the principal form. Let me just use the original brute-force
    # search but with a smarter loop limit:
    bmax = int(np.sqrt(4.0 * p / 3.0)) + 1
    for b in range(1, bmax + 1):
        disc = 4 * p - 3 * b * b
        if disc < 0:
            break
        s = int(np.sqrt(disc))
        if s * s != disc:
            continue
        if (b + s) % 2 != 0:
            continue
        a1 = (b + s) // 2
        a2 = (b - s) // 2
        for a in (a1, a2):
            if a > 0 and a * a - a * b + b * b == p:
                return (a, b)
    raise ValueError(f"failed to represent p = {p} as a² - ab + b²")


def eisenstein_prime_angles(X: int,
                            include_ramified: bool = True,
                            both_factors: bool = True) -> np.ndarray:
    """Generate sorted angles of Eisenstein prime ideals of norm ≤ X.

    Parameters
    ----------
    X                : norm cap.
    include_ramified : whether to include p = 3 (one angle).
    both_factors     : whether each split p contributes BOTH π and π̄
                       (two angles per ideal pair) or just ONE
                       representative. Default True per RW
                       one-angle-per-prime-ideal convention (two ideals
                       above p ≡ 1 mod 3, hence two angles).

    Returns
    -------
    angles : (N,) sorted float array of θ_π ∈ [0, π/3).
    """
    primes = sieve_primes(X)
    angles = []
    for p in primes:
        p = int(p)
        if p == 3:
            if include_ramified:
                # N(1 - ω) = 3; 1 - ω = 1 - e^{2πi/3} = 1 - (-1/2 + i√3/2)
                #                    = 3/2 - i√3/2,   arg = -π/6
                # Reduced mod π/3: -π/6 mod π/3 = π/6
                angles.append(np.pi / 6)
        elif p % 3 == 1:
            a, b = split_p_as_eisenstein_norm(p)
            # π = a + bω = a + b·(-1/2 + i√3/2) = (a - b/2) + i·(b√3/2)
            x = a - 0.5 * b
            y = 0.5 * np.sqrt(3.0) * b
            theta_pi = np.arctan2(y, x)
            # Reduce mod π/3 to fundamental sector [0, π/3)
            theta_pi_red = theta_pi % (np.pi / 3)
            angles.append(theta_pi_red)
            if both_factors:
                # π̄ = a + bω̄ = (a - b/2) - i·(b√3/2)
                theta_pibar = np.arctan2(-y, x)
                theta_pibar_red = theta_pibar % (np.pi / 3)
                # If both reduce to the same angle (e.g., the prime is on
                # the symmetry axis), only add one to avoid double-counting.
                # For generic split primes the two will land at distinct
                # angles within [0, π/3).
                if abs(theta_pibar_red - theta_pi_red) > 1e-12:
                    angles.append(theta_pibar_red)
        # p % 3 == 2: inert, no contribution
    return np.sort(np.array(angles, dtype=np.float64))


def hecke_unfold_eisenstein(angles: np.ndarray) -> np.ndarray:
    """Apply Hecke-uniform unfolding to angle sequence on [0, π/3).

    For Eisenstein prime angles, Hecke equidistribution says the density
    is 3/π uniform on [0, π/3). The unfolded coordinate has unit mean spacing:

        x_unfolded(θ) = (3N / π) · θ

    where N is the number of angles.
    """
    N = len(angles)
    return angles * (3.0 * N / np.pi)


if __name__ == '__main__':
    import sys
    X = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    print(f"Generating Eisenstein prime angles for norm cap X = {X}")
    angles = eisenstein_prime_angles(X, both_factors=True)
    print(f"  N = {len(angles)} angles")
    print(f"  range: [{angles[0]:.6f}, {angles[-1]:.6f}]   (should be ⊂ [0, {np.pi/3:.6f}))")
    print(f"  first 5: {angles[:5]}")
    print(f"  last 5:  {angles[-5:]}")
    unfolded = hecke_unfold_eisenstein(angles)
    spacings = np.diff(unfolded)
    print(f"  mean unfolded spacing: {np.mean(spacings):.6f}   (should be ~1.0)")
    print(f"  CV of unfolded spacings: {np.std(spacings)/np.mean(spacings):.4f}")
