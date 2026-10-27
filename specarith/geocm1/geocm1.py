"""GEO-CM1: tongue widths of critical circle maps along metallic paths (GEOCM1_SEAL.md). Desktop CPU.

Map F(x) = x + Ω + A1·sin 2πx + A2·sin 4πx (a lift of degree 1):
  cubic, K:  A1 = −K/2π, A2 = 0  (K = 1 critical: F′ = 1 − cos 2πx);
  quintic:   A1 = −2/(3π), A2 = 1/(12π)  (F′ = (2/3)(1 − cos 2πx)², a zero of order 4: inflection order z = 5).
G(x, Ω) = Fᵠ(x) − x − p. Rotation number ≥ p/q iff max_x G ≥ 0, ≤ p/q iff min_x G ≤ 0; both extremes increase in Ω.
Lower edge Ω₋: max G = 0; upper edge Ω₊: min G = 0. Each level's tongue lies between the tongues of the previous two
convergents (they bracket p_n/q_n), so earlier levels give every bracket; 0/1 and 1/1 = 0/1 + 1 start each path.

Per edge: seed the extremum from a double grid of M = 16q points (numba); CHECK both bracket ends at 30 digits (polished
extremum, sign − at the low end, + at the high end; a wrong sign widens the bracket ×2 about its centre and re-seeds,
at most 5 times; fixes are counted); bisect in Ω to 10⁻¹²·(the previous level's width; 10⁻¹² absolute at the first level) so that
the edge precision is ≤ 10⁻⁶ of the width for |δ| up to 10⁶ (edge_tol_rel is recorded per level) with the extremum tracked by Newton on (Fᵠ)′ = 1 (re-seeded from the grid when Newton fails); independently,
Newton on the saddle-node system G = 0, (Fᵠ)′ = 1 in (x, Ω). Method gate: |bisection − Newton| ≤ 10⁻³ of the width.
Two precisions (30 and 50 digits) per path; widths must agree to ≤ 10⁻⁶ relative.

GATE TOLERANCES (committed before any gate runs): golden (a = 1) and silver (a = 2) pass iff the Aitken estimate (last
three f_n, §3 of the seal) of f and of |δ| = w_n / w_{n+1} is within 3·SE of the literature value AND within 6·10⁻⁴
(f) / 6·10⁻⁴ relative (|δ|) of it (f(1) = 1.0822, |δ| = 2.833612; f(2) = 1.0874, |δ| = 6.79924). Cusp: §4 of the seal.

  python geocm1.py path NAME OUT_JSON      NAME = a1 … a10, cusp, sub05 (K = 0.5, golden, q ≤ 34), quintic (golden)
"""
import json
import math
import os
import platform
import sys
import time

import mpmath as mp
import numba
import numpy as np
from numba import njit, prange

QMAX = 2 * 10 ** 4
DIGITS = (30, 50)
TWO_PI = 2 * math.pi


def params(name):
    if name == "quintic":
        return -2 / (3 * math.pi), 1 / (12 * math.pi)
    if name == "sub05":
        return -0.5 / TWO_PI, 0.0
    return -1 / TWO_PI, 0.0


def convergents(name):
    """(p, q) of the path, in order, starting after 0/1."""
    if name == "cusp":
        return [(1, N) for N in range(2, 201)]              # 1/N lies between 0/1 and 1/(N − 1)
    a = 1 if name in ("quintic", "sub05") else int(name[1:])
    cap = 34 if name == "sub05" else QMAX
    out = [(0, 1), (1, a)]
    while True:
        p = a * out[-1][0] + out[-2][0]
        q = a * out[-1][1] + out[-2][1]
        if q > cap:
            break
        out.append((p, q))
    return out[1:]


@njit(cache=False, parallel=True)
def grid_ext(Om, q, p, A1, A2, M):
    vals = np.empty(M)
    for i in prange(M):
        x0 = i / M
        x = x0
        for _ in range(q):
            x = x + Om + A1 * math.sin(TWO_PI * x) + A2 * math.sin(2 * TWO_PI * x)
        vals[i] = x - x0 - p
    return np.argmax(vals), np.argmin(vals), vals.max(), vals.min()


def orbit(x0, Om, q, A1, A2):
    """Fᵠ(x0) and its derivatives: d1 = ∂x, d2 = ∂xx, dO = ∂Ω, dxO = ∂x∂Ω (chain rule), at the current mp precision."""
    x, d1, d2, dO, dxO = x0, mp.mpf(1), mp.mpf(0), mp.mpf(0), mp.mpf(0)
    tp = 2 * mp.pi
    a1, a2 = mp.mpf(A1), mp.mpf(A2)
    for _ in range(q):
        s, c = mp.sinpi(2 * x), mp.cospi(2 * x)
        s2, c2 = 2 * s * c, 2 * c * c - 1
        g1 = 1 + tp * a1 * c + 2 * tp * a2 * c2
        g2 = -tp * tp * a1 * s - 4 * tp * tp * a2 * s2
        d2, dxO = g2 * d1 * d1 + g1 * d2, g2 * d1 * dO + g1 * dxO
        d1, dO = g1 * d1, g1 * dO + 1
        x = x + Om + a1 * s + a2 * s2
    return x, d1, d2, dO, dxO


def extremum(x, Om, q, p, A1, A2, kind, its=40):
    """Newton on (Fᵠ)′ = 1 from x; returns (x*, G) or None if it does not converge to the right kind."""
    tol = mp.mpf(10) ** (-mp.mp.dps + 8)
    for _ in range(its):
        xq, d1, d2, _, _ = orbit(x, Om, q, A1, A2)
        if d2 == 0:
            return None
        step = (d1 - 1) / d2
        x = x - step
        if abs(step) < tol:
            xq, d1, d2, _, _ = orbit(x, Om, q, A1, A2)
            if (kind == "max" and d2 < 0) or (kind == "min" and d2 > 0):
                return x, xq - x - p
            return None
    return None


def ext_value(Om, q, p, A1, A2, kind, x_prev=None):
    """Extremum value of G at Ω: track from x_prev by Newton, else seed from the double grid."""
    if x_prev is not None:
        r = extremum(x_prev, Om, q, p, A1, A2, kind)
        if r is not None:
            return r, False
    M = 16 * q
    imax, imin, _, _ = grid_ext(float(Om), q, p, A1, A2, M)
    i = imax if kind == "max" else imin
    r = extremum(mp.mpf(int(i)) / M, Om, q, p, A1, A2, kind)
    if r is None:                       # derivative-free fallback: golden-section on ±2 grid points, then polish
        r = golden_ext(mp.mpf(int(i) - 2) / M, mp.mpf(int(i) + 2) / M, Om, q, p, A1, A2, kind)
        pol = extremum(r[0], Om, q, p, A1, A2, kind)
        if pol is not None and abs(pol[0] - r[0]) < mp.mpf(4) / M:
            r = pol
    return r, True


def golden_ext(a, b, Om, q, p, A1, A2, kind):
    """Golden-section search for the max (or min) of G on [a, b], x to ~10^(−dps/2) (G then to ~10^(−dps))."""
    sgn = 1 if kind == "max" else -1
    Gv = lambda x: sgn * (orbit(x, Om, q, A1, A2)[0] - x - p)
    g = (mp.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = Gv(c), Gv(d)
    tol = mp.mpf(10) ** (-(mp.mp.dps // 2) - 2)
    while b - a > tol:
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = Gv(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = Gv(d)
    x = (a + b) / 2
    return x, sgn * Gv(x)


def edge(lo, hi, q, p, A1, A2, kind, tol):
    """Bisection for the Ω where the extremum of G crosses 0 (− at lo, + at hi), with 30-digit bracket checks."""
    fixes = 0
    with mp.workdps(30):
        for _ in range(6):
            rl, _ = ext_value(lo, q, p, A1, A2, kind)
            rh, _ = ext_value(hi, q, p, A1, A2, kind)
            if rl is not None and rh is not None and rl[1] < 0 < rh[1]:
                break
            fixes += 1
            c, h = (lo + hi) / 2, (hi - lo)
            lo, hi = c - h, c + h
        else:
            raise RuntimeError(("bracket", p, q, kind))
    x = None
    while hi - lo > tol:
        mid = (lo + hi) / 2
        r, _ = ext_value(mid, q, p, A1, A2, kind, x)
        if r is None:
            raise RuntimeError(("extremum", p, q, kind, float(mid)))
        x = r[0]
        if r[1] < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2, x, fixes


def newton_sn(x, Om, q, p, A1, A2, its=60):
    """Saddle-node Newton in (x, Ω): G = 0, (Fᵠ)′ = 1."""
    tol = mp.mpf(10) ** (-mp.mp.dps + 8)
    for _ in range(its):
        xq, d1, d2, dO, dxO = orbit(x, Om, q, A1, A2)
        f1, f2 = xq - x - p, d1 - 1
        J = mp.matrix([[d1 - 1, dO], [d2, dxO]])
        dx, dOm = mp.lu_solve(J, mp.matrix([f1, f2]))
        x, Om = x - dx, Om - dOm
        if abs(dOm) < tol and abs(dx) < tol:
            return Om
    return None


def tongue(p, q, lo, hi, A1, A2, wprev):
    tol = (wprev if wprev else mp.mpf(1)) * mp.mpf(10) ** -12
    om_lo, x_lo, f1 = edge(lo, hi, q, p, A1, A2, "max", tol)        # lower edge
    om_hi, x_hi, f2 = edge(lo, hi, q, p, A1, A2, "min", tol)        # upper edge
    n_lo = newton_sn(x_lo, om_lo, q, p, A1, A2)
    n_hi = newton_sn(x_hi, om_hi, q, p, A1, A2)
    w = om_hi - om_lo
    agree = None if n_lo is None or n_hi is None else float(max(abs(n_lo - om_lo), abs(n_hi - om_hi)) / w)
    return dict(p=p, q=q, lo=om_lo, hi=om_hi, w=w, fixes=f1 + f2, newton_agree_rel=agree, edge_tol_rel=float(tol / w))


def run_path(name, dps):
    A1, A2 = params(name)
    mp.mp.dps = dps
    levels = []
    t0 = time.time()
    # 0/1 tongue: bracket [−1, 0] for the lower edge and [0, 1] for the upper edge
    z_lo, _, _ = edge(mp.mpf(-1), mp.mpf(0), 1, 0, A1, A2, "max", mp.mpf(10) ** -25)
    z_hi, _, _ = edge(mp.mpf(0), mp.mpf(1), 1, 0, A1, A2, "min", mp.mpf(10) ** -25)
    known = {(0, 1): (z_lo, z_hi), (1, 1): (z_lo + 1, z_hi + 1)}
    chain = [(0, 1)]                    # convergents already available, in path order
    convs = convergents(name)
    wprev = None
    for (p, q) in convs:
        if name == "cusp":
            b2, b1 = (0, 1), ((1, q - 1) if q > 2 else (1, 1))
        elif len(chain) >= 2:
            b2, b1 = chain[-2], chain[-1]
        else:
            b2, b1 = (0, 1), (1, 1)
        if (p, q) in known:             # 1/1 on the golden path
            chain.append((p, q))
            continue
        a_, b_ = known[b2], known[b1]
        lo, hi = (a_[1], b_[0]) if b2[0] / b2[1] < b1[0] / b1[1] else (b_[1], a_[0])
        lv = tongue(p, q, lo, hi, A1, A2, wprev)
        known[(p, q)] = (lv["lo"], lv["hi"])
        wprev = lv["w"]
        levels.append({k: (mp.nstr(v, dps) if isinstance(v, mp.mpf) else v) for k, v in lv.items()})
        print(name, dps, p, q, mp.nstr(lv["w"], 12), lv["fixes"], lv["newton_agree_rel"], round(time.time() - t0), flush=True)
        if name != "cusp":
            chain.append((p, q))
    return levels


def main(name, out):
    res = dict(path=name, params=params(name), digits=DIGITS, qmax=QMAX,
               env=dict(python=platform.python_version(), numpy=np.__version__, numba=numba.__version__,
                        mpmath=mp.__version__, kernel=platform.release()), runs={})
    for d in ((50,) if name == "sub05" else DIGITS):
        res["runs"][str(d)] = run_path(name, d)
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[2], sys.argv[3]))
