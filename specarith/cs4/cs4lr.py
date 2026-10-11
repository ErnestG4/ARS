"""Fast CS08 ζ four-point evaluator on a uniform r-grid (Stage 2 long range; G_S_DESIGN.md §6). Same formulas, same
pieces and same caching as cs4fastc.FastZetaCached; only the evaluation of the r-dependent blocks changes:

- Prime blocks (A, B, Q, B1–B4, S13, A*). In the two-pair geometry every argument is i(s + c_r·r_t), so a prime's
  summand depends on r only through u_p = p^{i r_t} = e^{iθ}, θ = r_t·log p, and is a smooth periodic function of θ.
  Sample it at J equispaced θ (J = 128 for p < 1000, 32 above), FFT to its Fourier coefficients c_m(p), and sum
  Σ_p Σ_m c_m(p) e^{i m log p · r_t} over the whole r-grid at once with a type-1 NUFFT (finufft, eps 1e-14).
  Euler products (A, A*): the same on log f_p, with a continuous branch along θ (winding number checked: must be 0).
  Cost per block ~ J × #primes summand evaluations instead of #r × #primes.
  Primes p < 30 are summed pointwise over the grid instead (as cs4fast): for p = 2, 3 some local factors have zeros
  or poles ON |u| = 1 (A's 1 − (1 − u)²/4 at p = 3; B1's 1 − 2/p + u/p at p = 3; the B2/B3 factor 1 − 2v + pv at
  p = 3), which cancel only in the products of blocks, so no per-prime Fourier series exists there.
- ζ(1 + x), ζ′/ζ, (ζ′/ζ)′ at r-dependent x: the Euler–Maclaurin formula of zeta_em with one M ≥ max|Im s| + 64 for
  the grid; the three Dirichlet sums Σ_{n<M} (log n)^k n^{−s} by NUFFT; the M-tail terms pointwise.
- Blocks whose arguments are all r-independent (c_r = 0): evaluated once, as in cs4fast.

Accuracy diagnostics kept per block: the Fourier tail max|c_{±J/2}|/max|c| (aliasing) and any non-zero winding.
Validated against cs4fastc pointwise (cs4lr_check.py).
"""
import math

import finufft
import numpy as np

import cs4fast as F
import cs4fastc as FC
import zeta_em as ZE

EPS = 1e-14
P_DIRECT, P_SPLIT, J_SMALL, J_LARGE = 30, 1000, 128, 32
R_CHUNK = 8192


def nufft_grid(points, strengths, n):
    """Σ_j c_j e^{i k x_j}, k = −n/2 … n/2 − 1."""
    x = np.mod(np.asarray(points, float).ravel() + np.pi, 2 * np.pi) - np.pi
    return finufft.nufft1d1(x, np.ascontiguousarray(np.asarray(strengths, complex).ravel()), n, eps=EPS)


class LongRangeZeta(FC.FastZetaCached):
    def __init__(self, t, pmax=300_000):
        super().__init__(t, pmax=pmax)
        self.sg = 2 * math.pi / self.ell
        grp = lambda sel, J: dict(p=self.p[sel][None, :], lp=self.lp[sel][None, :], lp_ld=self.lp_ld[sel][None, :], J=J)
        self.direct = grp(self.p < P_DIRECT, None)
        self.groups = [grp((self.p >= P_DIRECT) & (self.p < P_SPLIT), J_SMALL), grp(self.p >= P_SPLIT, J_LARGE)]
        self._grp = None
        self.diag = {}

    # ---- grid
    def set_grid(self, r):
        r = np.asarray(r, float)
        n = len(r)
        assert n % 2 == 0, "grid length must be even"
        dr = (r[-1] - r[0]) / (n - 1)
        assert np.allclose(np.diff(r), dr, rtol=0, atol=1e-9 * max(1.0, abs(r[-1]))), "grid must be uniform"
        self.n, self.dr = n, dr
        self.rc = r[0] + (n // 2) * dr                    # mode k ↔ r = rc + k·dr, k = −n/2 … n/2 − 1
        self.rt = r * self.sg

    # ---- prime sums: in Fourier mode return the raw summand matrix (J × #primes in the group)
    def psum(self, f, *args, prod=False):
        if self._grp is None:
            return super().psum(f, *args, prod=prod)
        g = self._grp
        P = lambda e: F.pexp(e, g["lp"], g["lp_ld"])
        return f(P, g["p"], g["lp"], *args), prod

    def _memo(self, name, fn, *ks):
        key = (name,) + tuple(k.key() for k in ks)
        if key in self.cache:
            return self.cache[key]
        if all(k.cr == 0 for k in ks):
            v = fn(*[np.array([1j * k.s]) for k in ks])[0]
            self.cache[key] = np.full(self.n, v, complex)
            return self.cache[key]
        # direct part (p < P_DIRECT), pointwise over the grid, chunked
        g = self.direct
        dvals = np.empty(self.n, complex)
        for i in range(0, self.n, R_CHUNK):
            sub = [(1j * (k.s + k.cr * self.rt[i:i + R_CHUNK]))[:, None] for k in ks]
            self._grp = g
            try:
                m, prod = fn(*sub)
            finally:
                self._grp = None
            dvals[i:i + R_CHUNK] = np.prod(m, axis=1) if prod else m.sum(1)
        tot, tail = np.zeros(self.n, complex), 0.0
        for g in self.groups:
            J = g["J"]
            th = 2 * np.pi * (np.arange(J) + 0.5) / J            # half-step offset: θ = 0 is an exact removable
            #   singularity of A* (zp(−a − b) at a + b = 0) whenever the in-pair offsets cancel, e.g. d₁ = d₂
            args = [1j * (k.s + k.cr * th[:, None] / g["lp"]) for k in ks]
            self._grp = g
            try:
                m, prod = fn(*args)
            finally:
                self._grp = None
            m = np.broadcast_to(m, (J, g["p"].shape[1]))
            if prod:
                ph = np.unwrap(np.angle(m), axis=0)
                closing = np.angle(m[0] / m[-1])
                wind = np.rint((ph[-1] - ph[0] + closing) / (2 * np.pi))
                if np.any(wind != 0):
                    raise RuntimeError(f"{name}: non-zero winding for {int(np.sum(wind != 0))} primes")
                vals = np.log(np.abs(m)) + 1j * ph
            else:
                vals = m
            mm = np.fft.fftfreq(J, 1.0 / J)[:, None]
            c = np.fft.fft(vals, axis=0) / J * np.exp(-1j * mm * np.pi / J)   # undo the half-step offset
            scale = np.abs(c).max() or 1.0
            tail = max(tail, float(np.abs(c[J // 2]).max() / scale))
            om = mm * g["lp"] * self.sg                      # angular frequency in r
            ph = np.mod(mm * g["lp_ld"] * np.longdouble(self.sg) * np.longdouble(self.rc), F.TWO_PI_LD).astype(float)
            strengths = c * np.exp(1j * ph)
            tot += nufft_grid(om * self.dr, strengths, self.n)
        self.diag[key] = tail
        self.cache[key] = dvals * np.exp(tot) if prod else dvals + tot
        return self.cache[key]

    # ---- ζ triplet on the grid
    def ztripK(self, k):
        key = ("z",) + k.key()
        if key in self.cache:
            return self.cache[key]
        if k.cr == 0:
            z = ZE.zeta_triplet(np.array([1j * k.s]))
            self.cache[key] = tuple(np.full(self.n, v[0], complex) for v in z)
            return self.cache[key]
        y = k.s + k.cr * self.rt                           # s = 1 + iy on the grid
        M = int(math.ceil(np.abs(y).max())) + 64
        n = np.arange(1, M, dtype=float)
        ln_ld = np.log(n.astype(np.longdouble))
        ln = ln_ld.astype(float)
        ph0 = np.mod((np.longdouble(k.s) + np.longdouble(k.cr) * np.longdouble(self.sg) * np.longdouble(self.rc)) * ln_ld,
                     F.TWO_PI_LD).astype(float)
        a = np.exp(-1j * ph0) / n                          # n^{−1−i y(rc)}
        pts = -k.cr * self.sg * ln * self.dr
        z0 = nufft_grid(pts, a, self.n)
        z1 = nufft_grid(pts, -ln * a, self.n)
        z2 = nufft_grid(pts, ln * ln * a, self.n)
        s = 1 + 1j * y
        lM = math.log(M)
        Ms = ZE.cpow_neg(s, np.log(np.array([M], dtype=np.longdouble)))[:, 0]
        g0 = M * Ms / (s - 1)
        g1 = g0 * (-lM - 1 / (s - 1))
        g2 = g0 * ((lM + 1 / (s - 1)) ** 2 + 1 / (s - 1) ** 2)
        z0 = z0 + g0 + Ms / 2
        z1 = z1 + g1 - lM * Ms / 2
        z2 = z2 + g2 + lM * lM * Ms / 2
        for kk in range(1, 11):
            cB = float(ZE.B2K[kk - 1]) / ZE.FACT[kk - 1]
            roots = range(0, 2 * kk - 1)
            R = np.ones(s.shape, complex)
            for j in roots:
                R = R * (s + j)
            S1 = sum(1 / (s + j) for j in roots)
            S2 = sum(1 / (s + j) ** 2 for j in roots)
            h0 = R * Ms * M ** (-2 * kk + 1)
            dlog = S1 - lM
            z0 = z0 + cB * h0
            z1 = z1 + cB * h0 * dlog
            z2 = z2 + cB * h0 * (dlog ** 2 - S2)
        self.cache[key] = (z0, z1 / z0, z2 / z0 - (z1 / z0) ** 2)
        return self.cache[key]

    def connected(self, d1, d2, r, nonosc_only=False):
        self.set_grid(r)
        self.diag = {}
        sg = self.sg
        base = [-d1 / 2 * sg, d1 / 2 * sg, -d2 / 2 * sg, d2 / 2 * sg]
        crs = [0, 0, 1, 1]
        xs_num = [np.full(self.n, base[0]), np.full(self.n, base[1]), self.rt + base[2], self.rt + base[3]]
        self.cache = {}
        osc = np.zeros(self.n, complex)
        non = np.full(self.n, self.ell ** 4, complex)
        for P, M in F.C.index_terms(4):
            A = []
            for p in P:
                c = np.zeros(4, dtype=int)
                c[p] = 1
                A.append((FC.K(base[p], crs[p]), c))
            B = []
            for m in M:
                c = np.zeros(4, dtype=int)
                c[m] = -1
                B.append((FC.K(-base[m], -crs[m]), c))
            pref = self.ell ** (4 - len(P) - len(M))
            for c, fn in self.Jq(A, B):
                is_osc = int(c[2]) + int(c[3]) != 0
                if is_osc and nonosc_only:
                    continue
                phase = sum(int(ck) * xk for ck, xk in zip(c, xs_num))
                term = pref * fn() * np.exp(-self.ell * 1j * phase)
                if is_osc:
                    osc += term
                else:
                    non += term
        non -= self.R2(d1) * self.R2(d2) * self.ell ** 4
        return osc / self.ell ** 4, non / self.ell ** 4
