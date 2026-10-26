"""RQ1 (round 85): prime-ideal angles in ℤ[√2] (and ℤ[i] for the gate), and the exact sector-variance estimator.

ℤ[√2]: for a split prime p (p ≡ ±1 mod 8), π = gcd(p, s + √2) in ℤ[√2] with s² ≡ 2 (mod p) (norm-Euclidean gcd,
exact integers); assert |N(π)| = p; reduce by units to the fundamental domain 1 ≤ |π/π′| < ε² (ε = 1 + √2), sign
a > 0, then of {π, π′} keep the one with θ ≤ ½, θ(π) = log|π/π′| / (2 log ε) ∈ [0, 1). The archive stores that
generator (a, b) as int32; the two ideals above p sit at θ and 1 − θ. 2 and the inert primes are excluded.

Estimator (RW eq. 1.2, θ ∈ [0, 1), window width w = 1/K, centre averaged over the circle), computed exactly: N(c) is
piecewise constant with breakpoints θ_i ± w/2, so Var = Σ_segments len·N² − (N w)²; no grid.

  python rq1_angles.py gen LO HI OUT_NPY        one segment of p ∈ [LO, HI) → int32 (a, b) rows, sorted by p
"""
import math
import sys

import numpy as np

EPS = 1.0 + math.sqrt(2.0)
LOG_EPS2 = 2.0 * math.log(EPS)


def primes_in(lo, hi):
    """Primes in [lo, hi) by a segmented sieve (numpy)."""
    lo = max(lo, 2)
    if hi <= lo:
        return np.zeros(0, np.int64)
    r = int(math.isqrt(hi - 1)) + 1
    base = np.ones(r + 1, bool)
    base[:2] = False
    for i in range(2, int(math.isqrt(r)) + 1):
        if base[i]:
            base[i * i::i] = False
    seg = np.ones(hi - lo, bool)
    for q in np.nonzero(base)[0]:
        q = int(q)
        s = max(q * q, ((lo + q - 1) // q) * q)
        seg[s - lo::q] = False
    if lo < 2:
        seg[:2 - lo] = False
    return lo + np.nonzero(seg)[0].astype(np.int64)


def sqrt_mod(n, p):
    """Tonelli–Shanks: x with x² ≡ n (mod p), p an odd prime, n a QR."""
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


def _divround(x, d):
    """round(x/d) for integers, d > 0."""
    return (2 * x + d) // (2 * d)


def gcd_zs2(a1, b1, a2, b2):
    """gcd in ℤ[√2] (norm-Euclidean) of a1 + b1√2 and a2 + b2√2, exact integers."""
    while a2 or b2:
        n = a2 * a2 - 2 * b2 * b2
        x, y = a1 * a2 - 2 * b1 * b2, b1 * a2 - a1 * b2          # (a1 + b1√2)(a2 − b2√2)
        if n < 0:
            x, y, n = -x, -y, -n
        qa, qb = _divround(x, n), _divround(y, n)
        ra, rb = a1 - (qa * a2 + 2 * qb * b2), b1 - (qa * b2 + qb * a2)
        a1, b1, a2, b2 = a2, b2, ra, rb
    return a1, b1


def theta_ab(a, b, p):
    """θ for a reduced generator (a, b ≥ 0 after reduction): log|π/π′| = 2 log(a + b√2) − log p."""
    return (2.0 * math.log(a + b * math.sqrt(2.0)) - math.log(p)) / LOG_EPS2


def reduce_zs2(a, b, p):
    """Multiply by ±ε^n so that 1 ≤ |π/π′| < ε² and a > 0; return (a, b) with θ ∈ [0, 1), then pick θ ≤ ½."""
    # log|π| without cancellation: the same-sign combination of a and b√2 is the larger of |π|, |π′|
    big = abs(a) + abs(b) * math.sqrt(2.0)
    lg_big = math.log(big)
    same = (a >= 0) == (b >= 0)                                  # then |π| = big, else |π′| = big
    lpi = lg_big if same else math.log(p) - lg_big
    t = (2.0 * lpi - math.log(p)) / LOG_EPS2
    n = math.floor(t)
    # π·ε^{−n}: ε^{−1} = −1 + √2 (times sign; signs are fixed afterwards)
    ua, ub = (1, 1) if n < 0 else (-1, 1)
    for _ in range(abs(n)):
        a, b = a * ua + 2 * b * ub, a * ub + b * ua
    for _ in range(2):                                            # float edge: fix up by one step either way
        th = _theta_exact_sign(a, b, p)
        if th < 0:
            a, b = a * 1 + 2 * b * 1, a * 1 + b * 1               # × ε
        elif th >= 1:
            a, b = -a + 2 * b, a - b                              # × (−1 + √2) = ε⁻¹
    if a < 0:
        a, b = -a, -b
    if b < 0:                                                     # |π| < |π′| cannot happen in the domain; guard
        raise ArithmeticError((a, b, p))
    th = theta_ab(a, b, p)
    if th > 0.5:                                                  # take the conjugate ideal: π′ ε (θ → 1 − θ)
        a, b = a - 2 * b, a - b                                   # π′·ε = (a − b√2)(1 + √2)
        if a < 0:
            a, b = -a, -b
    if b < 0 or not 0.0 <= theta_ab(a, b, p) <= 0.5 + 1e-12:
        raise ArithmeticError(("domain", a, b, p))
    return a, b


def _theta_exact_sign(a, b, p):
    same = (a >= 0) == (b >= 0)
    big = abs(a) + abs(b) * math.sqrt(2.0)
    lpi = math.log(big) if same else math.log(p) - math.log(big)
    return (2.0 * lpi - math.log(p)) / LOG_EPS2


def gen_segment(lo, hi):
    ps = primes_in(lo, hi)
    out = np.empty((len(ps), 2), np.int32)
    n = 0
    for p in ps.tolist():
        if p % 8 not in (1, 7):
            continue
        s = sqrt_mod(2, p)
        a, b = gcd_zs2(p, 0, s, 1)
        if abs(a * a - 2 * b * b) != p:
            raise ArithmeticError(("norm", p, a, b))
        a, b = reduce_zs2(a, b, p)
        if abs(a * a - 2 * b * b) != p:                           # N(π) = ±p, asserted for every prime
            raise ArithmeticError(("norm after reduction", p, a, b))
        out[n] = a, b
        n += 1
    return out[:n]


def thetas_from_ab(ab):
    """θ ∈ [0, ½] per stored generator (float64), and p = |a² − 2b²| (int64), exactly from the int32 pair."""
    a, b = ab[:, 0].astype(np.int64), ab[:, 1].astype(np.int64)
    p = np.abs(a * a - 2 * b * b)
    th = (2.0 * np.log(a + b * math.sqrt(2.0)) - np.log(p.astype(np.float64))) / LOG_EPS2
    return th, p


def both_ideals(th):
    """The two prime ideals above each split p: θ and 1 − θ (mod 1)."""
    return np.concatenate([th, np.mod(1.0 - th, 1.0)])


def gen_segment_zi(lo, hi):
    """ℤ[i] archive rows: for each p ≡ 1 mod 4 in [lo, hi), the Cornacchia pair (u, v), 0 < u < v, u² + v² = p
    (asserted); the two ideals sit at θ = atan(u/v)/(π/2) and 1 − θ. Inert primes and (1 + i) are excluded (the
    ℤ[√2] archive's convention: N = prime ideals above split primes)."""
    ps = primes_in(lo, hi)
    ps = ps[ps % 4 == 1]
    out = np.empty((len(ps), 2), np.int32)
    for i, p in enumerate(ps.tolist()):
        s = sqrt_mod(p - 1, p)
        a, b = p, s
        r = math.isqrt(p)
        while b > r:
            a, b = b, a % b
        c = math.isqrt(p - b * b)
        if b * b + c * c != p:
            raise ArithmeticError(("cornacchia", p))
        out[i] = min(b, c), max(b, c)
    return out


# ---------- ℤ[i] (gate 3), RW's convention: all prime ideals of norm ≤ x, θ = arg/(π/2) ∈ [0, 1) ----------
def gaussian_thetas(x):
    ps = primes_in(2, x + 1)
    th = []
    for p in ps.tolist():
        if p % 4 == 1:
            s = sqrt_mod(p - 1, p)                                # √−1
            a, b = p, s                                          # Cornacchia
            r = math.isqrt(p)
            while b > r:
                a, b = b, a % b
            c = math.isqrt(p - b * b)
            assert b * b + c * c == p, p
            t = math.atan2(c, b) / (math.pi / 2)
            th += [t, 1.0 - t]                                    # (b + ci) and its conjugate, rotated into [0, π/2)
    th = np.mod(np.array(th), 1.0)
    inert = [p for p in ps.tolist() if p % 4 == 3 and p * p <= x]
    extra = [0.0] * len(inert) + ([0.5] if 2 <= x else [])        # inert at θ = 0, (1 + i) at arg π/4
    return np.concatenate([th, np.array(extra)])


# ---------- the exact sliding-window variance on the circle [0, 1) ----------
def var_exact(th, K):
    th = np.mod(np.asarray(th, np.float64), 1.0)
    N, w = len(th), 1.0 / K
    pos = np.concatenate([np.mod(th - w / 2, 1.0), np.mod(th + w / 2, 1.0)])
    inc = np.concatenate([np.ones(N, np.int64), -np.ones(N, np.int64)])
    o = np.argsort(pos, kind="stable")
    pos, inc = pos[o], inc[o]
    d = np.abs(th - 0.0)
    c0 = int(np.sum(np.minimum(d, 1.0 - d) < w / 2))              # windows covering c = 0
    cnt = c0 + np.cumsum(inc)
    lens = np.diff(np.concatenate([pos, [1.0]]))
    first = pos[0] if len(pos) else 1.0
    I2 = first * c0 * c0 + float(np.sum(lens * cnt.astype(np.float64) ** 2))
    return I2 - (N * w) ** 2


def var_pairs(th, K):
    """Brute check of var_exact: ∫N² = Σ_{i,j} max(0, w − d_ij) (small N only)."""
    th = np.mod(np.asarray(th, np.float64), 1.0)
    w = 1.0 / K
    d = np.abs(th[:, None] - th[None, :])
    d = np.minimum(d, 1.0 - d)
    return float(np.sum(np.maximum(0.0, w - d))) - (len(th) * w) ** 2


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        np.save(sys.argv[4], gen_segment(int(sys.argv[2]), int(sys.argv[3])))
        sys.exit(0)
