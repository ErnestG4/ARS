"""Khinchin Landscape — core engine.

Exact big-integer continued-fraction machinery. Everything numeric in this
project routes through this module; the constants live here once (spec sec 2).

Slot check (read twice):
    alpha = [0; a1, a2, ...]  -- integer part a0 = 0 is EXCLUDED.
    K_n(alpha) = (a1 * a2 * ... * an)^(1/n)   plain geometric mean, no weighting.
Same K as approximability/panel_A_K_reframe.py:47 (Liu-Qu-Wen order parameter).
"""
import math
from fractions import Fraction

# --- named constants, stated once (spec sec 2) -------------------------------
KHINCHIN_K0 = 2.6854520010653064   # Khinchin's constant
LOG2_K0 = math.log2(KHINCHIN_K0)   # ~1.42527 -- diverging-colormap center
LEVY_L = math.exp(math.pi ** 2 / (12 * math.log(2)))  # ~3.275823, precision budget
LOG2_LEVY = math.log2(LEVY_L)      # ~1.71169
GK_RATE_A_GE_2 = 1.0 - math.log2(4.0 / 3.0)  # ~0.5849625, Gauss-Kuzmin a>=2 rate

GUARD_BITS = 64  # G in spec sec 3.3


def gk_moments(kmax=4_000_000):
    """Mean and sd of log2 a under the Gauss-Kuzmin law (the a.e. null)."""
    import numpy as np
    k = np.arange(1, kmax, dtype=np.float64)
    p = np.log2(1.0 + 1.0 / (k * (k + 2.0)))
    l = np.log2(k)
    m1 = float((l * p).sum())
    return m1, math.sqrt(float((l * l * p).sum()) - m1 * m1)


GK_MEAN_LOG2A, GK_SD_LOG2A = gk_moments()   # ~1.42515, ~1.7127


# --- helpers -----------------------------------------------------------------
def ilog2(a):
    """log2 of a positive python int of arbitrary size (math.log2 overflows > 1e308)."""
    bl = a.bit_length()
    if bl <= 52:
        return math.log2(a)
    sh = bl - 52
    return math.log2(a >> sh) + float(sh)


def horizon_limit(B, guard=GUARD_BITS):
    """The trust bound: a quotient is certified only while q_n^2 <= 2^(B-guard)."""
    return 1 << (B - guard)


# --- the engine --------------------------------------------------------------
def cf_quotients(P, Q, D, limit):
    """Partial quotients of P/Q in (0,1) by exact Euclid, stopped at the trust horizon.

    P, Q  : ints with 0 < P < Q.  D: max depth.  limit: 2^(B-G) from horizon_limit().
    Returns (quotients, reason) where reason in {'depth','precision','terminated'}.

    The quotient a_n that first pushes q_n^2 past the limit is NOT emitted: past
    that point the finite-precision P/Q no longer determines the true
    neighbourhood's CF, so the value is not data (spec sec 3.3).
    """
    num, den = Q, P
    q_pp, q_p = 0, 1          # q_{-1}, q_0
    half_bits = (limit.bit_length() - 1) // 2
    out = []
    while len(out) < D:
        if den == 0:
            return out, 'terminated'
        a, r = divmod(num, den)
        q_n = a * q_p + q_pp
        if q_n.bit_length() > half_bits and q_n * q_n > limit:
            return out, 'precision'
        out.append(a)
        q_pp, q_p = q_p, q_n
        num, den = den, r
    return out, 'depth'


DEFAULT_OFFSET = 'pi_m3'


def grid_offset(B, kind=DEFAULT_OFFSET):
    """Integer offset xi_B = floor(2^B * xi) for the column grid.

    NOT 1/phi. The spec (sec 3.2) offsets by xi = 1/phi, but then every column
    alpha_i = (i + (sqrt5-1)/2)/N satisfies the integer quadratic
    (2*N*alpha - 2i + 1)^2 = 5 -- every column is a quadratic irrational in
    Q(sqrt5), i.e. the measure-zero exceptional set, never a generic point.
    grid_audit.py measures the cost: median K at depth 2048 lands +0.54% off K0
    with a bootstrap CI excluding it, while pi-3, cbrt2-1, ln2, stratified jitter
    and true random reals all land within +-0.04% and cover it.

    Default xi = pi - 3 is transcendental, so alpha_i = (i + xi)/N is transcendental
    for every i (else pi = 3 + N*alpha_i - i would be algebraic) -- no column is
    algebraic, let alone quadratic. Genericity of any one such CF stays conjectural,
    as it does for every named real; the audit is the empirical warrant.
    """
    if kind == 'golden_phi':                       # spec-literal, kept for comparison
        return (math.isqrt(5 << (2 * B)) - (1 << B)) // 2
    import mpmath
    mpmath.mp.dps = int(B * 0.302) + 40
    two_B = mpmath.mpf(2) ** B
    if kind == 'pi_m3':
        return int(mpmath.floor((mpmath.pi - 3) * two_B))
    if kind == 'ln2':
        return int(mpmath.floor(mpmath.log(2) * two_B))
    if kind == 'cbrt2_m1':
        return int(mpmath.floor((mpmath.cbrt(2) - 1) * two_B))
    raise KeyError(kind)


def grid_numerators(N, B, kind=DEFAULT_OFFSET):
    """Column sample grid: alpha_i = (i + xi)/N in exact integers.

    Returns (xi_B, Q) with numerator P_i = (i << B) + xi_B and common Q = N << B.
    The offset keeps every column off the exact simple rationals; see grid_offset()
    for why it is not 1/phi.
    """
    return grid_offset(B, kind), N << B


# --- anchors (spec sec 4) ----------------------------------------------------
# Closed-form quotient generators. These bypass Euclid entirely, so they are the
# reference the engine is checked AGAINST (gate G0f), not a product of it.
def anchor_phi(n):
    """1/phi = [0; 1,1,1,...]"""
    return 1


def anchor_sqrt2m1(n):
    """sqrt(2)-1 = [0; 2,2,2,...]"""
    return 2


def anchor_sqrt3m1(n):
    """sqrt(3)-1 = [0; 1,2,1,2,...]"""
    return 1 if n % 2 == 1 else 2


def anchor_e_m2(n):
    """e-2 = [0; 1,2,1,1,4,1,1,6,...]; a_{3m-1} = 2m, else 1."""
    return 2 * ((n + 1) // 3) if n % 3 == 2 else 1


def anchor_liouville(n):
    """Constructed Liouville-type: a_k = 2^(2^k). Precision death by design."""
    return 1 << (1 << n)


ANCHORS = {
    'phi':       dict(label='1/phi',      gen=anchor_phi,      approx=0.6180339887498949, cap=None),
    'sqrt2m1':   dict(label='sqrt2 - 1',  gen=anchor_sqrt2m1,  approx=0.4142135623730951, cap=None),
    'sqrt3m1':   dict(label='sqrt3 - 1',  gen=anchor_sqrt3m1,  approx=0.7320508075688772, cap=None),
    'e_m2':      dict(label='e - 2',      gen=anchor_e_m2,     approx=0.7182818284590452, cap=None),
    # cap=24: a_25 = 2^(2^25) is a 4 MB integer and a_4096 would exhaust the box.
    # The Liouville horizon lands near depth 11 at B=8192, so 24 is far past useful.
    'liouville': dict(label='Liouville-type', gen=anchor_liouville, approx=None, cap=24),
}


def anchor_sequence(key, D):
    """Exact closed-form quotients a_1..a_D for a named anchor (clamped by 'cap')."""
    spec = ANCHORS[key]
    if spec['cap'] is not None:
        D = min(D, spec['cap'])
    gen = spec['gen']
    return [gen(n) for n in range(1, D + 1)]


def anchor_rational(key, B):
    """High-precision rational P/Q ~ anchor, Q = 2^B, for feeding the Euclid engine.

    This is the "a real number known to B bits" object; running cf_quotients on it
    and comparing against anchor_sequence() is what actually tests the engine.
    """
    one = 1 << B
    if key == 'phi':
        return (math.isqrt(5 << (2 * B)) - one) // 2, one
    if key == 'sqrt2m1':
        return math.isqrt(2 << (2 * B)) - one, one
    if key == 'sqrt3m1':
        return math.isqrt(3 << (2 * B)) - one, one
    if key == 'e_m2':
        # exact rational partial sum of sum 1/k!, truncated well past B bits
        term, tot, k = Fraction(1), Fraction(0), 0
        while True:
            tot += term
            if k > 2 and term < Fraction(1, 1 << (B + 16)):
                break
            k += 1
            term /= k
        frac = tot - 2
        return (frac.numerator << B) // frac.denominator, one
    if key == 'liouville':
        # build the exact convergent of [0; 4, 16, 256, ...] deep enough that its
        # own CF is still the true one well past the horizon, then truncate to B bits
        depth = 4
        while 2 * ((1 << (depth + 1)) - 2) < B + 64:
            depth += 1
        depth += 1
        p_pp, p_p, q_pp, q_p = 1, 0, 0, 1
        for n in range(1, depth + 1):
            a = anchor_liouville(n)
            p_pp, p_p = p_p, a * p_p + p_pp
            q_pp, q_p = q_p, a * q_p + q_pp
        return (p_p << B) // q_p, one
    raise KeyError(key)


def predicted_horizon(quots, B, guard=GUARD_BITS):
    """Depth at which an exactly-known quotient sequence exhausts a B-bit budget."""
    limit = horizon_limit(B, guard)
    q_pp, q_p = 0, 1
    for n, a in enumerate(quots, start=1):
        q_n = a * q_p + q_pp
        if q_n * q_n > limit:
            return n - 1
        q_pp, q_p = q_p, q_n
    return len(quots)


def running_K(quots):
    """K_n for n = 1..len(quots) as floats (via log2 accumulation)."""
    out, s = [], 0.0
    for n, a in enumerate(quots, start=1):
        s += ilog2(a)
        out.append(2.0 ** (s / n))
    return out


# --- constructed exceptional columns (R7 atlas) ------------------------------
# The theorem forbids SAMPLING these: a Lebesgue grid meets the exceptional set
# with probability zero. Nothing forbids EXHIBITING them. Every sequence below is
# built, not measured, so its CF is exact at any depth and the trust horizon does
# not apply -- unlike a grid column, which is a real known to B bits.
def _gk_conditioned(rng, m, n):
    """i.i.d. draws from Gauss-Kuzmin conditioned on a <= m (bounded type F_m)."""
    import numpy as np
    k = np.arange(1, m + 1)
    p = np.log2(1.0 + 1.0 / (k * (k + 2.0)))
    return [int(v) for v in rng.choice(k, size=n, p=p / p.sum())]   # py int: ilog2 needs bit_length


def constructed_columns(D, seed=20260803):
    """The exceptional atlas: (label, class, quotients) for R7."""
    import numpy as np
    rng = np.random.default_rng(seed)
    out = []
    for m in (2, 3, 5, 10):
        out.append((f'F_{m}', 'bounded type  (a ≤ m)', _gk_conditioned(rng, m, D)))
    for m, nm in ((1, 'φ'), (2, '√2−1'), (5, '[5;5,5,…]')):
        out.append((f'all a={m}  {nm}', 'metallic  (K ≡ m exactly)', [m] * D))
    for pre in (16, 64, 256):
        out.append((f'noble tail @{pre}', 'noble tail  (K → 1)',
                    _gk_conditioned(rng, 12, pre) + [1] * (D - pre)))
    out.append(('e−2', 'arithmetic growth  (K → ∞)', anchor_sequence('e_m2', D)))
    out.append(('a_k = k', 'arithmetic growth  (K → ∞)', list(range(1, D + 1))))
    out.append(('a_k = 2^k', 'arithmetic growth  (K → ∞)', [1 << k for k in range(1, D + 1)]))
    # NB the grey tail on this column is the generator cap (k<=24), NOT a precision
    # mask: constructed columns have exact CFs and no trust horizon.
    out.append(('Liouville a_k=2^(2^k)\n(generator-capped k≤24)', 'escapee  (K → ∞ fast)',
                anchor_sequence('liouville', D)))
    out.append(('Gauss–Kuzmin draw', 'generic reference  (K → K₀)',
                _gk_conditioned(rng, 4_000_000, D)))
    return out


def running_log2K(quots):
    """log2 K_n for n = 1..len(quots). Use this, not running_K, when the class can
    diverge: K_n for a_k = 2^(2^k) overflows a float long before depth 24."""
    out, s = [], 0.0
    for n, a in enumerate(quots, start=1):
        s += ilog2(a)
        out.append(s / n)
    return out
