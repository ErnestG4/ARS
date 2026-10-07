"""Phase 2 (item 1) library — ζ consecutive spacings against CUE(N_eff) (seal PH2_SEAL_2.1.md).

Sections
  1. constants Λ, Q, C, η (G0a)                      — BBLM / BFM 2017 definitions
  2. Fredholm machinery (Bornemann; BFM eqs 1.7-1.13, 4.4-4.6): p0, r2 (primary), r2_RZ(ᾱ) (secondary), exact CUE_N
  3. CUE_N Haar draws (G0b, G0d)
  4. model tables and the κ estimator (§4): conditional ML of c = 1/κ² on the window s ≤ S_C (PA1)
  5. moving-block bootstrap (amendment A1)
  6. exact-θ unfolding (§2) and data loaders (Odlyzko text/offset tables; Platt binary)
Nothing here reads data by itself; callers pass arrays or paths.
"""
import math
import struct

import numpy as np
from numpy.polynomial import chebyshev as Cb

# ============================================================ 1. constants
def constants(dps=30):
    """Λ = γ0² + 2γ1 + c0, c0 = Σ_p log²p/(p−1)², Q = Σ_p log³p/(p−1)², C = Q/Λ, η = Q/(Λ√(3Λ)) (BBLM; BFM 2017).
    Prime sums via Σ_p log^k p/(p−1)² = Σ_{r≥2} (r−1) Σ_p log^k p · p^{−r} = Σ_r (r−1)(−1)^k P^{(k)}(r), P = prime zeta."""
    import mpmath as mp
    mp.mp.dps = dps
    g0, g1 = mp.euler, mp.stieltjes(1)
    c0 = mp.mpf(0)
    Q = mp.mpf(0)
    for r in range(2, 200):
        d2 = mp.diff(mp.primezeta, r, 2)
        d3 = mp.diff(mp.primezeta, r, 3)
        t2, t3 = (r - 1) * d2, -(r - 1) * d3
        c0 += t2
        Q += t3
        if abs(t2) < mp.mpf(10) ** (-dps) and abs(t3) < mp.mpf(10) ** (-dps):
            break
    Lam = g0 ** 2 + 2 * g1 + c0
    return dict(Lambda=float(Lam), Q=float(Q), C=float(Q / Lam), eta=float(Q / (Lam * mp.sqrt(3 * Lam))),
                Lambda_str=mp.nstr(Lam, 20), Q_str=mp.nstr(Q, 20))


LAMBDA = 1.5731510713249552        # BFM 2017 (= constants()["Lambda"]; checked in G0a)
Q_CONST = 2.3158463849588033


def n_eff(E, Lam=LAMBDA):
    """N_eff = log(E/2π)/√(12Λ) (BBLM eq. 19)."""
    return np.log(np.asarray(E, dtype=float) / (2 * math.pi)) / math.sqrt(12 * Lam)


def alpha_bar(E, Lam=LAMBDA, Q=Q_CONST):
    """ᾱ = 1 + 2Q/(Λ log(E/2π)) = 2α − 1 (BFM eq. 4.5)."""
    return 1 + 2 * Q / (Lam * np.log(np.asarray(E, dtype=float) / (2 * math.pi)))


# ============================================================ 2. Fredholm machinery
def _gl(m):
    x, w = np.polynomial.legendre.leggauss(m)
    return x, w


def _sine(d):
    return np.sinc(d)                                   # sin(πd)/(πd)


def _kernel_cue(d, N):
    """K^N(x,y) = sin(π d)/(N sin(π d/N)), d = x − y, real N (BFM eq. 1.8); diagonal value 1."""
    out = np.ones_like(d)
    nz = np.abs(d) > 1e-15
    out[nz] = np.sin(np.pi * d[nz]) / (N * np.sin(np.pi * d[nz] / N))
    return out


def _L(d, abar=1.0):
    """L_RZ(x,y) = π d sin(π ᾱ d)/6 (BFM 4.4); ᾱ = 1 gives the CUE_N correction L (BFM 1.10)."""
    return np.pi * d * np.sin(np.pi * abar * d) / 6.0


def fredholm_values(s, m=40, N=None, abars=()):
    """At gap length s: E0 = det(I − K_s) (sine kernel; or the exact CUE_N kernel if N is given), and for each ᾱ the
    first-order term Ω(K_s):L_s = −det(I − K_s) tr((I − K_s)^{-1} L_s) (BFM 1.12)."""
    x, w = _gl(m)
    t = 0.5 * s * (x + 1)
    ws = 0.5 * s * w
    sq = np.sqrt(ws)
    D = t[:, None] - t[None, :]
    K = _sine(D) if N is None else _kernel_cue(D, N)
    A = sq[:, None] * K * sq[None, :]
    I_A = np.eye(m) - A
    det = np.linalg.det(I_A)
    om = []
    for ab in abars:
        B = sq[:, None] * _L(D, ab) * sq[None, :]
        om.append(-det * np.trace(np.linalg.solve(I_A, B)))
    return det, om


def cheb_second_derivative(f_vals, s_nodes, S):
    """Fit a Chebyshev series on [0, S] to values at Chebyshev nodes and return a callable second derivative."""
    deg = len(s_nodes) - 1
    xs = 2 * s_nodes / S - 1
    c = Cb.chebfit(xs, f_vals, deg)
    c2 = Cb.chebder(c, 2) * (2.0 / S) ** 2
    return lambda s: Cb.chebval(2 * np.asarray(s) / S - 1, c2), (lambda s: Cb.chebval(2 * np.asarray(s) / S - 1, c))


def spacing_tables(S=6.0, M=160, m=40, abars=(1.0,), N=None):
    """p0(s) (or the exact CUE_N p_N(s) if N given) and r2(s; ᾱ) for each ᾱ, as callables on [0, S].
    p(s) = d²/ds² E(s) (BFM 1.7); r2 = d²/ds² Ω(K_s):L_s (BFM 1.13)."""
    k = np.arange(M + 1)
    nodes = 0.5 * S * (1 - np.cos(np.pi * k / M))      # Chebyshev–Lobatto on [0, S]
    E = np.empty(M + 1)
    Om = np.empty((len(abars), M + 1))
    for i, s in enumerate(nodes):
        if s == 0:
            E[i] = 1.0
            Om[:, i] = 0.0
            continue
        d, om = fredholm_values(s, m=m, N=N, abars=abars)
        E[i] = d
        Om[:, i] = om
    p, Ef = cheb_second_derivative(E, nodes, S)
    r2 = [cheb_second_derivative(Om[j], nodes, S)[0] for j in range(len(abars))]
    return p, r2, Ef


# ============================================================ 3. CUE_N Haar draws
def haar_unitary_phases(N, n_mat, rng):
    """Eigenphases of n_mat Haar unitaries (Mezzadri QR with phase correction), shape (n_mat, N), in [0, 2π)."""
    Z = (rng.standard_normal((n_mat, N, N)) + 1j * rng.standard_normal((n_mat, N, N))) / math.sqrt(2)
    Qm, R = np.linalg.qr(Z)
    d = np.diagonal(R, axis1=1, axis2=2)
    Qm = Qm * (d / np.abs(d))[:, None, :]
    ev = np.linalg.eigvals(Qm)
    return np.sort(np.mod(np.angle(ev), 2 * math.pi), axis=1)


def cue_spacings(N, n_mat, rng):
    """Consecutive unfolded spacings (mean 1) of CUE_N: N·Δθ/2π including the wrap-around spacing; shape (n_mat, N)."""
    ph = haar_unitary_phases(N, n_mat, rng)
    d = np.diff(np.concatenate([ph, ph[:, :1] + 2 * math.pi], axis=1), axis=1)
    return d * N / (2 * math.pi)


# ============================================================ 4. model tables and the κ estimator
class Model:
    """p(s; u, ᾱ) = p0(s) + u_k · r2(s; ᾱ_k) with u_k = 1/(κ² N_eff,k²). PRIMARY: ᾱ = 1 (r2 = BFM 1.13);
    SECONDARY: ᾱ_k = ᾱ(E_k) (BFM 4.4–4.6), r2_RZ tabulated on an ᾱ grid and interpolated linearly."""

    def __init__(self, S=6.0, M=160, m=40, abar_grid=None):
        self.S = S
        self.abar_grid = np.array([1.0]) if abar_grid is None else np.asarray(abar_grid)
        p0, r2s, _ = spacing_tables(S, M, m, tuple(self.abar_grid))
        self.p0, self.r2s = p0, r2s

    def eval(self, s, abar=None):
        s = np.clip(np.asarray(s, dtype=float), 0.0, self.S)
        p0 = self.p0(s)
        if abar is None or len(self.abar_grid) == 1:
            return p0, self.r2s[0](s)
        g = self.abar_grid
        ab = np.clip(np.asarray(abar, dtype=float), g[0], g[-1])
        j = np.clip(np.searchsorted(g, ab) - 1, 0, len(g) - 2)
        f = (ab - g[j]) / (g[j + 1] - g[j])
        R = np.stack([r(s) for r in self.r2s])
        idx = np.arange(len(s))
        return p0, (1 - f) * R[j, idx] + f * R[j + 1, idx]


S_C = 2.0          # fit window s ≤ S_C (proposed amendment PA1): the first-order family p0 + c·r2/N² is a density there
S_BRACKET = 0.05   # positivity is checked on [S_BRACKET, S_C]; below it r2/p0 → −1/N²-type finite limits (no constraint
                   # tighter than c < N²) and the Chebyshev tables' absolute noise (~1e-12) would dominate the ratio


def _window_grid(sc, n=20001):
    s = np.linspace(0.0, sc, n)
    w = np.full(n, sc / (n - 1)); w[0] *= 0.5; w[-1] *= 0.5     # trapezoid
    return s, w


class WindowFit:
    """Conditional maximum likelihood of c = 1/κ² on the window s ≤ sc (PA1):
        ℓ(c) = Σ_k [log(p0(s_k) + c a_k(s_k)) − log(F0 + c Fa_k)],  a_k = r2(s; ᾱ_k)/N_eff,k²,  Fa_k = ∫₀^sc a_k,
    over spacings with s_k ≤ sc only; the window's own probability is conditioned out, so the out-of-window tail (where
    the first-order family turns negative at small N) carries no information and cannot cap ĉ.
    The c-range is the one where the model density is positive on the whole window for every spacing's N_eff (a
    property of the model, not of the data)."""

    def __init__(self, model, sc=S_C):
        self.model, self.sc = model, sc
        g, w = _window_grid(sc)
        self.F0 = float(np.sum(w * model.p0(g)))
        self.Fr = np.array([float(np.sum(w * r(g))) for r in model.r2s])       # per ᾱ-grid node
        b = g >= S_BRACKET
        self._gb, self._p0b = g[b], model.p0(g[b])
        self._r2b = np.stack([r(g[b]) for r in model.r2s])

    def _Fr_at(self, abar):
        if len(self.model.abar_grid) == 1 or abar is None:
            return np.full(np.shape(abar) if abar is not None else (), self.Fr[0])
        return np.interp(abar, self.model.abar_grid, self.Fr)

    def c_range(self, Neff_min, abars=None):
        """(lo, hi): c-range where p0 + c r2(ᾱ)/N² > 0 on [S_BRACKET, sc] for N ≥ Neff_min and every ᾱ node in use."""
        rows = range(len(self.model.abar_grid)) if abars is not None and len(self.model.abar_grid) > 1 else [0]
        hi, lo = math.inf, -math.inf
        for j in rows:
            rho = self._r2b[j] / self._p0b              # a/p0 = rho/N²; positivity: 1 + c·rho/N² > 0
            if (rho < 0).any():
                hi = min(hi, float(np.min(-1 / rho[rho < 0])))
            if (rho > 0).any():
                lo = max(lo, float(np.max(-1 / rho[rho > 0])))
        n2 = float(Neff_min) ** 2
        return lo * n2 * (1 - 1e-9), hi * n2 * (1 - 1e-9)

    def prepare(self, s, Neff, abar=None):
        """Per-spacing arrays for spacings s (all of them; the window mask is applied here and kept, so a bootstrap
        resamples the full sequence and the in-window count is random as it should be)."""
        s = np.asarray(s, dtype=float)
        Neff = np.broadcast_to(np.asarray(Neff, dtype=float), s.shape)
        inw = s <= self.sc
        p0, r2 = self.model.eval(s[inw], None if abar is None else np.broadcast_to(abar, s.shape)[inw])
        n2 = Neff[inw] ** 2
        Fr = self._Fr_at(None if abar is None else np.broadcast_to(abar, s.shape)[inw])
        rho = r2 / n2 / p0                        # a_k/p0_k
        phi = Fr / n2 / self.F0                   # Fa_k/F0
        out = dict(inw=inw, rho=np.zeros(s.shape), phi=np.zeros(s.shape), Nmin=float(np.min(Neff)))
        out["rho"][inw] = rho
        out["phi"][inw] = phi
        return out

    def fit(self, prep, idx=None, lo=None, hi=None):
        """ĉ by bisection on the score Σ_k [ρ_k/(1 + cρ_k) − φ_k/(1 + cφ_k)] (ρ = a/p0, φ = Fa/F0) inside the
        positivity range. Returns (ĉ, flag) with flag ∈ {'interior', 'at_lo', 'at_hi'}."""
        inw, rho, phi = prep["inw"], prep["rho"], prep["phi"]
        if idx is not None:
            inw, rho, phi = inw[idx], rho[idx], phi[idx]
        rho, phi = rho[inw], phi[inw]
        if lo is None or hi is None:
            l0, h0 = self.c_range(prep["Nmin"], abars=None)
            lo = l0 if lo is None else lo
            hi = h0 if hi is None else hi
        # the model range is computed on a grid; a spacing between grid nodes can sit a hair outside it
        if (rho > 0).any():
            lo = max(lo, float(np.max(-1 / rho[rho > 0])) * (1 - 1e-9))
        if (rho < 0).any():
            hi = min(hi, float(np.min(-1 / rho[rho < 0])) * (1 - 1e-9))
        score = lambda c: float(np.sum(rho / (1 + c * rho)) - np.sum(phi / (1 + c * phi)))
        if score(lo) <= 0:
            return lo, "at_lo"
        if score(hi) >= 0:
            return hi, "at_hi"
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if score(mid) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi), "interior"

    def loglik(self, prep, c):
        inw, rho, phi = prep["inw"], prep["rho"], prep["phi"]
        return float(np.sum(np.log1p(c * rho[inw])) - np.sum(np.log1p(c * phi[inw])))

    def expected_c(self, p_true, Neff, abar=None, n=40001):
        """Deterministic 'infinite-sample' ĉ against a known spacing law p_true (§6 truncation allowance, G0c): the
        maximiser of ∫₀^sc p_true(s) [log(p0 + c a) − log(F0 + c Fa)] ds, one N_eff (and ᾱ)."""
        g, w = _window_grid(self.sc, n)
        g, w = g[1:], w[1:]
        wt = np.maximum(p_true(g), 0) * w
        p0, r2 = self.model.eval(g, None if abar is None else np.full(g.shape, abar))
        rho = r2 / Neff ** 2 / p0
        phi = float(self._Fr_at(abar)) / Neff ** 2 / self.F0
        lo, hi = self.c_range(Neff, abars=None if abar is None else [abar])
        ok = g >= S_BRACKET
        score = lambda c: float(np.sum(wt[ok] * rho[ok] / (1 + c * rho[ok])) + np.sum(wt[~ok] * rho[~ok] / (1 + c * rho[~ok]))
                                - np.sum(wt) * phi / (1 + c * phi))
        if score(lo) <= 0:
            return lo
        if score(hi) >= 0:
            return hi
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if score(mid) > 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)


def kappa_from_c(c):
    """κ = 1/√c for c > 0; κ = ∞ for c ≤ 0 (no finite-N correction)."""
    return 1 / math.sqrt(c) if c > 0 else math.inf


# ============================================================ 5. moving-block bootstrap (A1)
def block_bootstrap_c(fitter, prep, block_len, n_boot, rng):
    """Moving-block bootstrap of ĉ (A1): resample overlapping blocks of consecutive spacings (the full sequence, window
    mask carried along) to the original length; returns the ĉ replicates."""
    n = len(prep["inw"])
    nb = int(math.ceil(n / block_len))
    out = np.empty(n_boot)
    for b in range(n_boot):
        st = rng.integers(0, n - block_len + 1, nb)
        idx = (st[:, None] + np.arange(block_len)[None, :]).ravel()[:n]
        out[b] = fitter.fit(prep, idx)[0]
    return out


# ============================================================ 6. unfolding and data loaders
def nbar_exact(gammas_mp):
    """N̄(γ) = θ(γ)/π + 1 with the exact Riemann–Siegel θ (mpmath; inputs are mpf at the caller's precision)."""
    import mpmath as mp
    return [mp.siegeltheta(g) / mp.pi + 1 for g in gammas_mp]


def unfolded_spacings(gammas_mp, dps=40):
    """Consecutive spacings of N̄(γ_k) computed in extended precision, returned as float64 (§2)."""
    import mpmath as mp
    with mp.workdps(dps):
        x = nbar_exact(gammas_mp)
        return np.array([float(x[i + 1] - x[i]) for i in range(len(x) - 1)])


def read_platt_file(path, t_lo=None, t_hi=None):
    """Decode an LMFDB Platt zeros file (format of lmfdb/zeros/zeta/platt_zeros.py, J. Bober): uint64 block count; per
    block a 'ddQQ' header (t0, t1, N(t0), N(t1)) then N(t1) − N(t0) records 'QIB' (13 bytes) of cumulative integer
    deltas, γ = t0 + Z·2^-101. Returns (list of (t0_int_or_float, Z_int) pairs as exact rationals via mpf later, N(t0) of
    the first zero). Zeros are returned as Python Fractions-free tuples (t0, Z) to keep full precision."""
    out = []
    first_index = None
    with open(path, "rb") as f:
        nblocks = struct.unpack("<Q", f.read(8))[0]
        for _ in range(nblocks):
            t0, t1, Nt0, Nt1 = struct.unpack("<ddQQ", f.read(32))
            n = Nt1 - Nt0
            raw = f.read(13 * n)
            if (t_hi is not None and t0 > t_hi) or (t_lo is not None and t1 < t_lo):
                continue
            if first_index is None:
                first_index = Nt0 + 1
            Z = 0
            for k in range(n):
                z1, z2, z3 = struct.unpack_from("<QIB", raw, 13 * k)
                Z += (z3 << 96) + (z2 << 64) + z1
                out.append((t0, Z))
    return out, first_index


def platt_to_mpf(pairs, dps=45):
    import mpmath as mp
    with mp.workdps(dps):
        eps = mp.mpf(2) ** (-101)
        return [mp.mpf(t0) + Z * eps for t0, Z in pairs]


def read_odlyzko_offset_table(path, dps=45):
    """Odlyzko zeros3/4/5: a text header giving the base ('Values of gamma - BASE'), then one offset per line.
    Returns the zeros as mpf (base + offset) at dps digits."""
    import mpmath as mp
    import re
    txt = open(path).read()
    base = int(re.search(r"Values of gamma\s*-\s*(\d+)", txt).group(1))
    lines = [ln.strip() for ln in txt.splitlines()]
    vals = [ln for ln in lines if re.fullmatch(r"-?\d+\.\d+", ln)]
    with mp.workdps(dps):
        return [mp.mpf(base) + mp.mpf(v) for v in vals]
