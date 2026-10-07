"""Phase 6 instrument library (seal PH6_SEAL_6.0.md). One module so a reviewer can read it against the seal.

Sections
  1. configuration and window (seal §3)
  2. LHS statistics: zero sets S(tau), M(tau) (seal §2); Maass sector sums C_eps(tau) (seal §2)
  3. RHS exact identities (seal §5): Dirichlet/zeta (EF §7), Selberg per sector (SB §1.4), picket (Poisson summation)
  4. Layer B readout (seal §6): local grids, joint least squares, arms
  5. nulls (seal §7): GUE (Dumitriu-Edelman beta=2 tridiagonal, as arsrh Phase 1) and Poisson, mapped through N-bar^-1
  6. tolerance bounds (seal §5.1)

Conventions (EF §3b, SB §1.1): g(u) = (1/2pi) int h(r) e^{-iru} dr. Gaussian window w(E) = exp(-(E-T0)^2/(2 sigma^2)).
Nothing here reads data files; callers pass arrays.
"""
from dataclasses import dataclass
import math

import numpy as np
from scipy.special import digamma, loggamma, erfc

SQ2PI = math.sqrt(2 * math.pi)
K_EDGE = 8.5


# ============================================================ 1. configuration and window
@dataclass(frozen=True)
class Config:
    T0: float
    sigma: float
    E_lo: float
    E_hi: float

    @property
    def norm(self):            # line-peak normalisation sigma / sqrt(2 pi)
        return self.sigma / SQ2PI


def rule_config(E_lo, E_hi, k_edge=K_EDGE):
    """Seal §3: T0 = (E_lo + E_hi)/2, sigma = (E_hi - E_lo)/(2 K_edge)."""
    return Config(T0=(E_lo + E_hi) / 2, sigma=(E_hi - E_lo) / (2 * k_edge), E_lo=E_lo, E_hi=E_hi)


def fixed_config(T0, sigma):
    """G0-s windows (seal §8a): fixed (T0, sigma); E_hi = T0 + 8.5 sigma is where the input list must be complete."""
    return Config(T0=T0, sigma=sigma, E_lo=0.0, E_hi=T0 + K_EDGE * sigma)


def w(cfg, E):
    """Gaussian window; E may be complex (analytic continuation)."""
    return np.exp(-((E - cfg.T0) ** 2) / (2 * cfg.sigma ** 2))


def g_zero_line(cfg, taus, u):
    """g_tau(u) for h_tau(r) = w(r) e^{i tau r} (EF §7 step 3): (sigma/sqrt2pi) e^{-sigma^2 (u-tau)^2/2} e^{-i (u-tau) T0}.
    taus: array; u: scalar or array broadcastable."""
    v = u - taus
    return cfg.norm * np.exp(-(cfg.sigma ** 2) * v ** 2 / 2) * np.exp(-1j * v * cfg.T0)


def g_maass(cfg, taus, u):
    """g_tau(u) for h_tau(r) = [w(r) + w(-r)] cos(tau r) (seal §2): real and even in u,
    (sigma/sqrt2pi) * sum_{v = u - tau, u + tau} e^{-sigma^2 v^2/2} cos(v T0)."""
    out = 0.0
    for v in (u - taus, u + taus):
        out = out + np.exp(-(cfg.sigma ** 2) * v ** 2 / 2) * np.cos(v * cfg.T0)
    return cfg.norm * out


def h_maass(cfg, taus, r):
    """h_tau(r) = [w(r) + w(-r)] cos(tau r); r may be complex (h(i/2) for the constant eigenfunction)."""
    return (w(cfg, r) + w(cfg, -r)) * np.cos(np.multiply.outer(taus, r))


# ============================================================ 2. LHS statistics
def _chunks(taus, size=128):
    for i in range(0, len(taus), size):
        yield i, taus[i:i + size]


def _fsum_rows(phase, weights):
    """Compensated (math.fsum) sum over each row of weights * e^{i phase} (seal §5.1: compensated summation)."""
    out = np.empty(phase.shape[0], dtype=np.complex128)
    for k in range(phase.shape[0]):
        out[k] = complex(math.fsum(weights * np.cos(phase[k])), math.fsum(weights * np.sin(phase[k])))
    return out


def zero_sums(cfg, levels, taus, exact=False):
    """S(tau) = sum_{levels>0} w(E) e^{i tau E};  M(tau) = sum w(-E) e^{-i tau E}  (seal §2, §5).
    Only levels where the window exceeds 1e-300 contribute (exactly zero below that in float64).
    exact=True: compensated summation (math.fsum), as the seal requires for gate statistics (§5.1). exact=False (BLAS)
    is used only for null draws, whose bands are statistical."""
    E = np.asarray(levels, dtype=np.float64)
    E = E[E > 0]
    ws = w(cfg, E)
    keep = ws > 1e-300
    Es, wss = E[keep], ws[keep]
    wm = w(cfg, -E)
    keepm = wm > 1e-300
    Em, wmm = E[keepm], wm[keepm]
    S = np.empty(len(taus), dtype=np.complex128)
    M = np.zeros(len(taus), dtype=np.complex128)
    for i, tc in _chunks(np.asarray(taus, dtype=np.float64), 16 if exact else 128):
        if exact:
            S[i:i + len(tc)] = _fsum_rows(np.multiply.outer(tc, Es), wss)
            if len(Em):
                M[i:i + len(tc)] = _fsum_rows(-np.multiply.outer(tc, Em), wmm)
        else:
            S[i:i + len(tc)] = np.exp(1j * np.multiply.outer(tc, Es)) @ wss
            if len(Em):
                M[i:i + len(tc)] = np.exp(-1j * np.multiply.outer(tc, Em)) @ wmm
    return S, M


def maass_sector_sum(cfg, r_levels, taus, even):
    """C_eps(tau) = sum_j h_tau(r_j), plus h_tau(i/2) for the constant eigenfunction in the even sector (seal §2)."""
    r = np.asarray(r_levels, dtype=np.float64)
    ww = w(cfg, r) + w(cfg, -r)
    out = np.empty(len(taus), dtype=np.float64)
    for i, tc in _chunks(np.asarray(taus, dtype=np.float64)):
        ph = np.multiply.outer(tc, r)
        out[i:i + len(tc)] = [math.fsum(ww * np.cos(ph[k])) for k in range(len(tc))]
    if even:
        out = out + np.real((w(cfg, 0.5j) + w(cfg, -0.5j)) * np.cosh(np.asarray(taus) / 2))
    return out


# ============================================================ 3. RHS identities
def mangoldt_upto(N):
    """Lambda(n) for n = 0..N (float), by sieve."""
    lam = np.zeros(N + 1)
    is_p = np.ones(N + 1, dtype=bool)
    is_p[:2] = False
    for p in range(2, N + 1):
        if not is_p[p]:
            continue
        is_p[p * p::p] = False
        pk = p
        while pk <= N:
            lam[pk] = math.log(p)
            pk *= p
    return lam


def chi4(n):
    n = np.asarray(n)
    return np.where(n % 2 == 0, 0, np.where(n % 4 == 1, 1, -1)).astype(float)


def psi_asymptotic(u):
    """RP15's replacement for Re psi(1/4 + iu/2), pinned (review m1): log(max(|u|, 2)/2), i.e. the leading asymptotic
    log(|u|/2) for |u| >= 2 and 0 inside, so the red path is not singular at u = 0."""
    return np.log(np.maximum(np.abs(u), 2.0) / 2.0)


def trapezoid_integral(f_vals, x):
    dx = x[1] - x[0]
    return dx * (f_vals.sum(axis=-1) - 0.5 * (f_vals[..., 0] + f_vals[..., -1]))


def gamma_term(cfg, taus, a, step=None):
    """(1/2pi) int w(u) e^{i tau u} Re psi(1/4 + a/2 + iu/2) du over the real line (EF §7), by the trapezoid rule on
    [T0 - 13 sigma, T0 + 13 sigma]. Returns (value, error estimate from halving the step)."""
    if step is None:
        # trapezoid on an entire-times-analytic integrand: aliasing error ~ |F^(2pi/step - tau)|, negligible for
        # step 0.5 when the window is far from u = 0 (sigma >= 100), else 0.05; halving the step estimates the error
        step = 0.5 if cfg.sigma >= 100 else 0.05
    lo, hi = cfg.T0 - 13 * cfg.sigma, cfg.T0 + 13 * cfg.sigma

    def run(h):
        u = np.arange(lo, hi + h / 2, h)
        f = w(cfg, u) * np.real(digamma(0.25 + a / 2 + 0.5j * u))
        out = np.empty(len(taus), dtype=np.complex128)
        for i, tc in _chunks(np.asarray(taus, dtype=np.float64), 8):
            out[i:i + len(tc)] = trapezoid_integral(np.exp(1j * np.multiply.outer(tc, u)) * f, u)
        # float64 rounding bound (review M4/m11): per term the phase tau*u carries |tau u| 2^-51 (+ evaluation), f a few
        # ulp; summation of N terms adds N 2^-53 of the absolute sum
        absf = np.abs(f) * h
        fb = np.array([np.sum(absf * (np.abs(t * u) * 2 * EPS64 + 8 * EPS64)) for t in taus]) \
            + absf.sum() * len(u) * EPS64 / 2
        return out / (2 * math.pi), fb / (2 * math.pi)

    v1, _ = run(step)
    v2, fb = run(step / 2)
    return v2, np.abs(v2 - v1) + fb


def prime_sum_dirichlet(cfg, taus, chi=None):
    """sum_{n>=2} Lambda(n)/sqrt(n) [chi(n) g_tau(log n) + conj chi(n) g_tau(-log n)] (EF §7; chi real here).
    n_max chosen so every line beyond is > 13 widths from tau <= 4.5; returns (value, tail bound)."""
    sig = cfg.sigma
    n_max = 10000                                                     # seal §5: prime sum to n <= 10^4
    n_tail = max(2 * n_max, min(4_000_000, int(math.ceil(math.exp(4.5 + 25.0 / sig)))))
    lam = mangoldt_upto(n_tail)
    n = np.arange(n_tail + 1)
    c = np.ones(n_tail + 1) if chi is None else chi(n)
    coef = lam / np.sqrt(np.maximum(n, 1)) * c
    sel = np.nonzero(coef[: n_max + 1])[0]
    ln = np.log(sel.astype(float))
    taus = np.asarray(taus, dtype=np.float64)
    val = np.zeros(len(taus), dtype=np.complex128)
    fbound = np.zeros(len(taus))
    for i, tc in _chunks(taus, 64):
        G = g_zero_line(cfg, tc[:, None], ln[None, :]) + g_zero_line(cfg, tc[:, None], -ln[None, :])
        val[i:i + len(tc)] = G @ coef[sel]
        # float64 rounding bound (review M4): log n and tau carry 1 ulp each; the phase (log n - tau) T0 and the Gaussian
        # sigma^2 v^2/2 inherit (T0 + sigma^2 |v|)(log n + tau) 2^-52; the dot product of len(sel) terms adds len 2^-53
        v = np.abs(ln[None, :] - tc[:, None])
        amp = np.abs(coef[sel])[None, :] * np.abs(g_zero_line(cfg, tc[:, None], ln[None, :]))
        fbound[i:i + len(tc)] = np.sum(amp * ((cfg.T0 + sig ** 2 * v) * (ln[None, :] + tc[:, None]) * 2 * EPS64
                                              + (len(sel) + 8) * EPS64), axis=1)
    # tail: n in (n_max, n_tail] summed in absolute value; beyond n_tail a dyadic-block bound
    tsel = np.nonzero(coef[n_max + 1:])[0] + n_max + 1
    lt = np.log(tsel.astype(float))
    tail = np.array([np.sum(np.abs(coef[tsel]) * cfg.norm * np.exp(-(sig ** 2) * (lt - t) ** 2 / 2)) for t in taus])
    beyond = 0.0
    for k in range(60):                     # block [n_tail 2^k, n_tail 2^(k+1)): <= n_tail 2^k terms, each bounded
        lo_n = n_tail * 2.0 ** k
        dist = max(0.0, math.log(lo_n) - float(np.max(taus)))
        beyond += lo_n * math.log(2 * lo_n) / math.sqrt(lo_n) * cfg.norm * math.exp(-(sig ** 2) * dist ** 2 / 2)
    return val, tail + beyond + fbound


def rhs_dirichlet(cfg, taus, q, chi, a):
    """Seal §5 boxed identity, RHS without the -M term:
        S + M = delta_{q,1}[h(i/2)+h(-i/2)] + g_tau(0) log(q/pi) + Gamma term - prime sum.
    Returns dict of terms (complex arrays) and error estimates. q=1: zeta (chi None, a=0); q=4: chi_-4 (a=1)."""
    taus = np.asarray(taus, dtype=np.float64)
    pole = np.zeros(len(taus), dtype=np.complex128)
    if q == 1:
        pole = w(cfg, 0.5j) * np.exp(-taus / 2) + w(cfg, -0.5j) * np.exp(taus / 2)
    cond = g_zero_line(cfg, taus, 0.0) * math.log(q / math.pi)
    gam, gam_err = gamma_term(cfg, taus, a)
    pr, pr_tail = prime_sum_dirichlet(cfg, taus, chi)
    total = pole + cond + gam - pr
    add_round = 4 * EPS64 * (np.abs(pole) + np.abs(cond) + np.abs(gam) + np.abs(pr))
    return dict(total=total, pole=pole, cond=cond, gamma=gam, prime=pr, smooth=pole + cond + gam,
                err=gam_err + pr_tail + add_round)


def selberg_integrals(cfg, taus, step=None):
    """The integrals of SB §1.4 for h_tau = [w(r)+w(-r)] cos(tau r), all over the real line, by the trapezoid rule
    (h is even, so each is 2 * int_0^inf). Returns dict name -> (value array, error estimate)."""
    if step is None:
        step = min(0.01, cfg.sigma / 100)
    hi = cfg.T0 + 14 * cfg.sigma
    taus = np.asarray(taus, dtype=np.float64)

    def run(hstep):
        r = np.arange(0.0, hi + hstep / 2, hstep)
        H = h_maass(cfg, taus, r)                          # (ntau, nr), real
        k = {
            "ident": r * np.tanh(np.pi * r),
            "E2": 1.0 / np.cosh(np.pi * r),
            "E3": np.cosh(np.pi * r / 3) / np.cosh(np.pi * r),
            "psi_half": np.real(digamma(0.5 + 1j * r)),
            "psi_one": np.real(digamma(1.0 + 1j * r)),
        }
        out = {}
        for name, ker in k.items():
            P = H * ker[None, :]
            val = 2 * trapezoid_integral(P, r)
            # float64 rounding bound: |tau r| 2^-51 phase + 8 ulp evaluation per term, plus N 2^-53 summation
            absP = np.abs(P) * hstep
            fb = 2 * (np.sum(absP * (np.abs(np.multiply.outer(taus, r)) * 2 * EPS64 + 8 * EPS64), axis=1)
                      + absP.sum(axis=1) * len(r) * EPS64 / 2)
            out[name] = (val, fb)
        return out

    v1, v2 = run(step), run(step / 2)
    return {name: (v2[name][0], np.abs(v2[name][0] - v1[name][0]) + v2[name][1]) for name in v1}


def selberg_tail_bound(cfg, taus):
    """Seal §5.1 tails for G1 (review m6): classes with t > 30 and prime powers n > 10^4. Uses
    C(t) log eps1 <= sqrt(D) (log D + 1) (class number formula, h log eps = sqrt(D) L(1,chi), L(1,chi) <= log D + 1),
    so each class term is <= (log D + 1) |g(ell_t)|; and 2 Lambda(n)/n |g(2 log n)| for n > 10^4."""
    taus = np.asarray(taus, dtype=np.float64)
    tail = np.zeros(len(taus))
    for kind in (-4, 4):
        for t in range(31, 5000):
            D = t * t + kind
            ell = 2 * math.log((t + math.sqrt(D)) / 2)
            tail += 2 * (math.log(D) + 1) * np.abs(g_maass(cfg, taus, ell))   # x2: hyperbolic and glide both bounded
    lam = mangoldt_upto(200000)
    for n in np.nonzero(lam[10001:])[0] + 10001:
        tail += 2 * lam[n] / n * np.abs(g_maass(cfg, taus, 2 * math.log(n)))
    return tail


def selberg_class_terms(cfg, taus, classdata, kind):
    """Per-sector hyperbolic (kind 'h': H/2) or glide (kind 'g': R/2) sum: sum_t C(t) log eps1 / sqrt(D) g(2 log((t+sqrtD)/2)),
    D = t^2 - 4 or t^2 + 4 (SB §1.4). classdata: {t: C(t) * log eps1} from classes.pari_counts (lsum/2 for 'h', lsum for 'g')."""
    taus = np.asarray(taus, dtype=np.float64)
    out = np.zeros(len(taus))
    for t, clog in classdata.items():
        D = t * t + (-4 if kind == "h" else 4)
        ell = 2 * math.log((t + math.sqrt(D)) / 2)
        out = out + clog / math.sqrt(D) * g_maass(cfg, taus, ell)
    return out


def rhs_selberg(cfg, taus, sector, classdata_h, classdata_g, integrals=None):
    """Seal §5 Maass per-sector identity (SB §1.4, from BS07 (2.39) at N = 1). sector: 'even' or 'odd'.
    The LHS it matches is maass_sector_sum(..., even=(sector=='even')), which includes h(i/2) for 'even'."""
    taus = np.asarray(taus, dtype=np.float64)
    I = integrals if integrals is not None else selberg_integrals(cfg, taus)
    g0 = g_maass(cfg, taus, 0.0)
    ident = I["ident"][0] / 24.0
    ell = 0.5 * (I["E2"][0] / 8.0 + I["E3"][0] / (3 * math.sqrt(3)))
    hyp = selberg_class_terms(cfg, taus, classdata_h, "h")
    gl = selberg_class_terms(cfg, taus, classdata_g, "g")
    err = I["ident"][1] / 24 + 0.5 * (I["E2"][1] / 8 + I["E3"][1] / (3 * math.sqrt(3))) + selberg_tail_bound(cfg, taus)
    if sector == "even":
        lam = mangoldt_upto(10000)
        n = np.nonzero(lam)[0]
        prime = 2 * sum(lam[k] / k * g_maass(cfg, taus, 2 * math.log(k)) for k in n)
        const = g0 / 4 * math.log(math.pi ** 4 / 2)
        psi = -(I["psi_half"][0] + 2 * I["psi_one"][0]) / (4 * math.pi)
        err = err + (I["psi_half"][1] + 2 * I["psi_one"][1]) / (4 * math.pi)
        total = ident + ell + hyp + gl + const + psi + prime
        terms = dict(ident=ident, elliptic=ell, hyperbolic=hyp, glide=gl, g0=const, psi=psi, prime=prime)
    elif sector == "odd":
        const = -g0 / 4 * math.log(8)
        psi = -I["psi_half"][0] / (4 * math.pi)
        err = err + I["psi_half"][1] / (4 * math.pi)
        total = ident + ell + hyp - gl + const + psi
        terms = dict(ident=ident, elliptic=ell, hyperbolic=hyp, glide=-gl, g0=const, psi=psi)
    else:
        raise ValueError(sector)
    return dict(total=total, err=err, **terms)


def picket_levels(cfg, lam, theta=0.0, span=40.0):
    """Interval-dilation spectrum E_n = (theta + 2 pi n)/lam (seal §5; Endres-Steiner eq. 150), all n with
    |E_n - T0| <= span * sigma."""
    n_lo = math.floor(((cfg.T0 - span * cfg.sigma) * lam - theta) / (2 * math.pi))
    n_hi = math.ceil(((cfg.T0 + span * cfg.sigma) * lam - theta) / (2 * math.pi))
    n = np.arange(n_lo, n_hi + 1)
    return (theta + 2 * math.pi * n) / lam


def picket_sum(cfg, levels, taus):
    """Two-sided sum over the picket (all n, including E <= 0): sum_n w(E_n) e^{i tau E_n}."""
    E = np.asarray(levels, dtype=np.float64)
    ws = w(cfg, E)
    keep = ws > 1e-300
    out = np.empty(len(taus), dtype=np.complex128)
    for i, tc in _chunks(np.asarray(taus, dtype=np.float64)):
        out[i:i + len(tc)] = np.exp(1j * np.multiply.outer(tc, E[keep])) @ ws[keep]
    return out


def rhs_picket(cfg, taus, lam, theta=0.0):
    """Poisson summation (seal §5): (lam/2pi) sum_k e^{ik theta} W(tau - k lam), W(nu) = sigma sqrt(2pi) e^{-sigma^2 nu^2/2} e^{i nu T0}.
    Returns (total, smooth k=0 term)."""
    taus = np.asarray(taus, dtype=np.float64)
    kmax = int(math.ceil((taus.max() + 40 / cfg.sigma) / lam)) + 1
    total = np.zeros(len(taus), dtype=np.complex128)
    smooth = None
    for k in range(-kmax, kmax + 1):
        nu = taus - k * lam
        term = (lam / (2 * math.pi)) * np.exp(1j * k * theta) * cfg.sigma * SQ2PI \
            * np.exp(-(cfg.sigma ** 2) * nu ** 2 / 2) * np.exp(1j * nu * cfg.T0)
        total = total + term
        if k == 0:
            smooth = term
    return total, smooth


# ============================================================ 4. Layer B readout
LINE_NS = np.arange(2, 91)


def local_grid(cfg, ns=LINE_NS):
    """Seal §4: tau = log n + (j/2)/sigma, j = -6..6, for every n (concatenated, sorted, with the owning n)."""
    js = np.arange(-6, 7) / 2.0
    taus = (np.log(ns)[:, None] + js[None, :] / cfg.sigma).ravel()
    return taus


def readout(cfg, taus, r_vals, ns=LINE_NS):
    """Seal §6.1: joint least squares r(tau) = sum_n c_n e^{-sigma^2 (tau - log n)^2/2} e^{i (tau - log n) T0}."""
    ln = np.log(ns.astype(float))
    d = taus[:, None] - ln[None, :]
    A = np.exp(-(cfg.sigma ** 2) * d ** 2 / 2) * np.exp(1j * d * cfg.T0)
    c, *_ = np.linalg.lstsq(A, r_vals, rcond=None)
    return c


def weights(kind, ns=LINE_NS):
    """a_n of seal §6.1: 'zeta' -Lambda(n)/sqrt n; 'chi4' -chi(n)Lambda(n)/sqrt n; 'zero' 0."""
    lam = mangoldt_upto(int(ns.max()))[ns]
    if kind == "zeta":
        return -lam / np.sqrt(ns)
    if kind == "chi4":
        return -chi4(ns) * lam / np.sqrt(ns)
    if kind == "zero":
        return np.zeros(len(ns))
    raise ValueError(kind)


def is_prime_power(ns=LINE_NS):
    return mangoldt_upto(int(ns.max()))[ns] > 0


def band(c_calib, alpha=0.01, ns=LINE_NS):
    """Seal §6.2: s_n^2 = mean |c_n|^2 over calibration draws (rows); B_n = s_n sqrt(ln(89/alpha))."""
    s = np.sqrt(np.mean(np.abs(c_calib) ** 2, axis=0))
    return s * math.sqrt(math.log(len(ns) / alpha)), s


T3_MIN_SET = (2, 3, 4, 5, 7)


def t3_verdict(c, a, B, applicable=True, ns=LINE_NS):
    """Seal §6.3. Returns (verdict, details). a = expected weights; B = band at this configuration."""
    if not applicable:
        return "INAPPLICABLE", {}
    pp = is_prime_power(ns)
    expected_nonzero = a != 0
    R = pp & expected_nonzero & (np.abs(a) >= 2 * B)
    Rset = set(ns[R].tolist())
    # PROPOSED AMENDMENT A3 (review B1; pending Will): the minimum set is taken over the weight vector's support,
    # M_w = M ∩ {n : a_n != 0} ({3, 5, 7} under chi_-4). The sealed text applies M = {2,3,4,5,7} to every weight vector,
    # which makes every chi_-4 reading NOT RESOLVABLE, the exact truth included.
    M_w = {m for m in T3_MIN_SET if a[list(ns).index(m)] != 0}
    if not M_w <= Rset and np.any(a != 0):
        return "NOT RESOLVABLE", dict(R=sorted(Rset), M_w=sorted(M_w))
    pos = R & ~(np.abs(c) > B)
    wgt = R & ~(np.abs(c - a) <= B)
    sgn = R & ~(np.real(c) * a > 0)
    silent_set = ~expected_nonzero            # non-prime-powers and any n with a_n = 0 (e.g. powers of 2 under chi4)
    sil = silent_set & (np.abs(c) > B)
    failed = {k: ns[v].tolist() for k, v in (("POSITION", pos), ("WEIGHT", wgt), ("SIGN", sgn), ("SILENCE", sil)) if v.any()}
    verdict = "PASS" if not failed else "FAIL"
    return verdict, dict(R=sorted(Rset), failed_arms=failed)


# ============================================================ 5. nulls
def theta_rs(t):
    """Riemann-Siegel theta: Im log Gamma(1/4 + i t/2) - (t/2) log pi (EF §5)."""
    t = np.asarray(t, dtype=np.float64)
    return np.imag(loggamma(0.25 + 0.5j * t)) - t / 2 * math.log(math.pi)


def nbar_zeta(t):
    """Smooth zero count theta(t)/pi + 1 (MV Thm 14.1; EF §5)."""
    return theta_rs(t) / math.pi + 1.0


def nbar_chi(t, q=4, kappa=1):
    """MV Thm 14.5 smooth part for primitive chi mod q: arg Gamma(1/4 + kappa/2 + iT/2)/pi + (T/2pi) log(q/pi)."""
    t = np.asarray(t, dtype=np.float64)
    return np.imag(loggamma(0.25 + kappa / 2 + 0.5j * t)) / math.pi + t / (2 * math.pi) * math.log(q / math.pi)


def dnbar(nbar, t, h=1e-4):
    return (nbar(t + h) - nbar(t - h)) / (2 * h)


def invert_nbar(nbar, x, t_min, t_max):
    """Solve nbar(t) = x for t in [t_min, t_max] (nbar increasing there) by bisection + Newton, vectorised."""
    x = np.asarray(x, dtype=np.float64)
    lo = np.full_like(x, t_min)
    hi = np.full_like(x, t_max)
    for _ in range(60):
        mid = (lo + hi) / 2
        f = nbar(mid) - x
        lo = np.where(f < 0, mid, lo)
        hi = np.where(f < 0, hi, mid)
    t = (lo + hi) / 2
    for _ in range(3):
        t = t - (nbar(t) - x) / dnbar(nbar, t)
    return t


def gue_unfolded(n_levels, rng):
    """Unit-density GUE levels: central 80% of a Dumitriu-Edelman beta=2 Hermite tridiagonal of size n_mat, with
    diag ~ sqrt(2) N(0,1), off-diag_k ~ sqrt(chi^2_{2(n-k)}) (arsrh Phase 1 normalisation), unfolded by the semicircle
    of radius sqrt(8 n_mat). Returns n_levels consecutive unfolded levels starting at 0."""
    from scipy.linalg import eigh_tridiagonal
    n_mat = int(math.ceil(n_levels / 0.8)) + 10
    d = math.sqrt(2.0) * rng.standard_normal(n_mat)
    b = np.sqrt(rng.chisquare(2 * np.arange(n_mat - 1, 0, -1)))
    ev = eigh_tridiagonal(d, b, eigvals_only=True)
    R = math.sqrt(8.0 * n_mat)
    x = np.clip(ev / R, -1, 1)
    F = n_mat * (0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / math.pi)
    i0 = (n_mat - n_levels) // 2
    u = np.sort(F)[i0:i0 + n_levels]
    return u - u[0]


def poisson_unfolded(n_levels, rng):
    """Unit-density Poisson levels: n_levels sorted uniforms on [0, n_levels)."""
    return np.sort(rng.uniform(0, n_levels, n_levels))


def null_levels(kind, nbar, E_hi, rng, t_min=7.0):
    """Seal §7: unfolded GUE or Poisson levels mapped onto the target's smooth count by nbar^-1, covering
    [t_min, E_hi + margin] (window at t_min is ~e^-36 or smaller for every configuration used)."""
    x0 = float(nbar(np.array([t_min]))[0])
    x1 = float(nbar(np.array([E_hi * 1.02 + 50]))[0])
    n = int(math.ceil(x1 - x0))
    u = gue_unfolded(n, rng) if kind == "gue" else poisson_unfolded(n, rng)
    u = u[u < x1 - x0]
    return invert_nbar(nbar, x0 + u, t_min, E_hi * 1.05 + 100)


# ============================================================ 6. tolerance bounds (seal §5.1)
EPS64 = 2.0 ** -52


def eps_data_zero(cfg, levels, taus, delta):
    """delta * sum_k (tau w(E_k) + |w'(E_k)|) over the levels and their mirrors (worst-case input inaccuracy)."""
    E = np.asarray(levels, dtype=np.float64)
    E = E[E > 0]
    d_eff = delta + 2.0 ** -53 * float(np.max(E))       # float64 representation of the levels (review m7)
    out = np.zeros(len(taus))
    for X in (E, -E):
        ws = w(cfg, X)
        wp = np.abs(X - cfg.T0) / cfg.sigma ** 2 * ws
        out = out + d_eff * (np.asarray(taus) * ws.sum() + wp.sum())
    return out


def eps_float_zero(cfg, levels, taus):
    """Seal §5.1: sum_k w(E_k)(|tau E_k| + 1) 2^-51 (per-term phase and evaluation rounding), plus the compensated-
    summation term: math.fsum is correctly rounded, <= 2^-53 |sum| per real/imag part, bounded by 2 * 2^-53 sum w."""
    E = np.asarray(levels, dtype=np.float64)
    E = E[E > 0]
    ws = w(cfg, E) + w(cfg, -E)
    taus = np.asarray(taus)
    return 2.0 ** -51 * (taus * (ws * E).sum() + ws.sum()) + 2 * 2.0 ** -53 * ws.sum()


def eps_trunc(cfg, density_at_edge):
    """Levels above E_hi are not in the list: sum over them of |h| <= 2 * rho_max * int_{E_hi}^inf w dE."""
    z = (cfg.E_hi - cfg.T0) / cfg.sigma
    return 2.0 * density_at_edge * cfg.sigma * math.sqrt(math.pi / 2) * erfc(z / math.sqrt(2))


def tolerance(*parts):
    """Seal §5.1: eps(tau) = 2 x (eps_data + eps_float + eps_trunc + eps_rhs)."""
    return 2.0 * sum(parts)
