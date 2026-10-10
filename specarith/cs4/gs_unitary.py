"""Stage 2 G-s, U(N) step (G_S_DESIGN.md §5.1, §6): the predicted v(b) = V(b)/b of the tapered statistic for the sine
kernel (the N → ∞ U(N) limit), computed directly from the evaluated integrals at every rung of the ladder, two ways:

  direct: the full connected four-point function, determinant of the sine kernel, integrated over all r;
  split:  §3's split (short range, r ≤ 20: full function weighted by χ; long range: the non-oscillating pieces only,
          from the CS08 U(N) transcription in its sine limit, weighted by 1 − χ).

Their difference is the ℓ-oscillating long-range contribution the split drops (G_S_DESIGN §3: claimed negligible).
The predicted v(b) is then compared with the measured long-GUE baseline (ph2s2/results/tapered: 16 × 10⁶ levels).

Assembly (unit spacing; W_b(y) = exp(−πy²/b²); (W⋆W)(r) = (b/√2)exp(−πr²/2b²)):
  v(b) = √2·I₂ + 2√2·I₃(b) + (1/√2)∫ exp(−πr²/2b²) C(r) dr,
  I₂ = ∫ F²ρ₂,   I₃(b) = ∫∫ F(a)F(e) ρ₃(0, a, e) exp(−π(e − a)²/8b²) da de,
  C(r) = ∫∫ F(d₁)F(d₂) [ρ₄(−d₁/2, d₁/2, r − d₂/2, r + d₂/2) − ρ₂(d₁)ρ₂(d₂)] dd₁ dd₂.
(The 3-point weight is the exact midpoint overlap ∫W(x + a/2)W(x + e/2)dx; no local approximation.)

Quadrature. d: Gauss–Legendre on [0, 2.8] (F even, ρ even in each in-pair offset; F(2.8) ~ e^{−29}). Direct r
integral: C(r) is band-limited to |ω| ≤ 4π (a product of four sine kernels in r), so the trapezoid rule with Δr = 0.2
on the even integrand is exact up to the Gaussian tail; r ≤ 4.8b (weight < e^{−36}). Split: Gauss–Legendre panels
(width 0.5 on [0, 20]; geometric beyond, where C_non is smooth and non-oscillating).

  python gs_unitary.py check              pieces: sine-limit transcription = determinant (mp, a few points)
  python gs_unitary.py run OUT [BMAX]     v(b) direct and split on the ladder -> OUT/gs_unitary.json
"""
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

import cs4lib as C
import cs4split as S

U, W, DMAX, ND = 0.5, 0.3, 2.8, 40
LADDER = (100, 300, 1000, 3000, 10_000)
RC = 10.0


def F(d):
    return np.exp(-(d - U) ** 2 / (2 * W * W)) + np.exp(-(d + U) ** 2 / (2 * W * W))


def sinc(x):
    return np.sinc(x)                                   # sin(πx)/(πx)


def chi(r):
    """Smooth partition: 1 for r ≤ RC, 0 for r ≥ 2RC, C∞ in between."""
    t = np.clip((np.asarray(r, float) - RC) / RC, 0.0, 1.0)
    f = lambda s: np.where(s > 0, np.exp(-1.0 / np.where(s > 0, s, 1.0)), 0.0)
    return f(1 - t) / (f(1 - t) + f(t))


class SineLimit(S.RMTp):
    """CS08 U(N) pieces in the N → ∞ limit: points X = 2πu (u in unit spacings), L = 1, z(x) → 1/x, z'/z → −1/x,
    (z'/z)' → 1/x² (each J scales homogeneously in N, so the limit is term by term)."""
    def __init__(self):
        self.N = self.L = 1

    @staticmethod
    def z(x):
        return 1 / x

    @staticmethod
    def zz(x):
        return -1 / x

    @staticmethod
    def dzz(x):
        return 1 / x ** 2


def rho2(d):
    return 1 - sinc(d) ** 2


def det4(d1, d2, r):
    """ρ₄ of two pairs (−d₁/2, d₁/2), (r − d₂/2, r + d₂/2) for the sine kernel (broadcast arrays)."""
    a, f = sinc(d1), sinc(d2)
    b, c = sinc(r - d2 / 2 + d1 / 2), sinc(r + d2 / 2 + d1 / 2)
    d, e = sinc(r - d2 / 2 - d1 / 2), sinc(r + d2 / 2 - d1 / 2)
    # symmetric, unit diagonal: [[1,a,b,c],[a,1,d,e],[b,d,1,f],[c,e,f,1]]
    return (1 - a * a - b * b - c * c - d * d - e * e - f * f
            + a * a * f * f + b * b * e * e + c * c * d * d
            + 2 * (a * d * b + a * e * c + b * f * c + d * f * e)
            - 2 * (a * d * f * c + a * e * f * b + b * d * e * c))


def nonosc_np(model, d1, d2, r):
    """Non-oscillating connected part (unit-spacing density) from the transcription's pieces, numpy-vectorised."""
    xs = [2 * np.pi * (-d1 / 2), 2 * np.pi * (d1 / 2), 2 * np.pi * (r - d2 / 2), 2 * np.pi * (r + d2 / 2)]
    xs = [np.asarray(x, complex) for x in np.broadcast_arrays(*xs)]
    non, osc = np.ones_like(xs[0]), np.zeros_like(xs[0])
    for P, M in C.index_terms(4):
        A = [S.arg(+1, p, xs[p], 4) for p in P]
        B = [S.arg(-1, m, xs[m], 4) for m in M]
        for c, v in model.Jp(A, B):
            term = v * np.exp(-1j * sum(int(ck) * xk for ck, xk in zip(c, xs)))
            if int(c[2]) + int(c[3]) != 0:
                osc = osc + term
            else:
                non = non + term
    non = non - rho2(d1) * rho2(d2)
    return non, osc


def gl(a, b, n):
    x, w = np.polynomial.legendre.leggauss(n)
    return 0.5 * (b - a) * x + 0.5 * (b + a), 0.5 * (b - a) * w


DN, DW = gl(0.0, DMAX, ND)
FD = F(DN)
WD = 4 * np.outer(DW * FD, DW * FD)                    # d₁, d₂ ≥ 0, ×4 for the signs


def C_full(r):
    r = np.atleast_1d(np.asarray(r, float))
    out = np.empty(len(r))
    D1, D2 = DN[:, None, None], DN[None, :, None]
    base = rho2(D1) * rho2(D2)
    for i in range(0, len(r), 512):
        rr = r[None, None, i:i + 512]
        out[i:i + 512] = np.einsum("ij,ijk->k", WD, det4(D1, D2, rr) - base)
    return out


def C_non(r, model=None):
    model = model or SineLimit()
    r = np.atleast_1d(np.asarray(r, float))
    out = np.empty(len(r))
    D1, D2 = DN[:, None, None], DN[None, :, None]
    for i in range(0, len(r), 64):
        non, _ = nonosc_np(model, D1, D2, r[None, None, i:i + 64])
        out[i:i + 64] = np.einsum("ij,ijk->k", WD, non.real)
    return out


def I2():
    return 2 * float(np.sum(DW * FD ** 2 * rho2(DN)))


def I3(b):
    x, w = gl(-DMAX, DMAX, 2 * ND)
    A, E = x[:, None], x[None, :]
    k = lambda u: sinc(u)
    p, q, s = k(A), k(E), k(E - A)
    rho3 = 1 - p * p - q * q - s * s + 2 * p * q * s
    return float(np.sum(np.outer(w * F(x), w * F(x)) * rho3 * np.exp(-math.pi * (E - A) ** 2 / (8 * b * b))))


def v_direct(b, dr=0.2):
    r = np.arange(0.0, 4.8 * b + dr, dr)
    c = C_full(r)
    wt = np.exp(-math.pi * r ** 2 / (2 * b * b)) * c
    I4 = dr * (wt[0] + 2 * np.sum(wt[1:]))
    return math.sqrt(2) * I2() + 2 * math.sqrt(2) * I3(b) + I4 / math.sqrt(2), I4 / math.sqrt(2)


def panels_split(b):
    """GL nodes: width-0.5 panels on [0, 2RC] (full function × χ there), geometric panels on [RC, 4.8b] for the
    non-oscillating part × (1 − χ)."""
    sh = [gl(a, a + 0.5, 12) for a in np.arange(0, 2 * RC, 0.5)]
    rs, ws = np.concatenate([p[0] for p in sh]), np.concatenate([p[1] for p in sh])
    edges = [RC, 1.5 * RC, 2 * RC]
    while edges[-1] < 4.8 * b:
        edges.append(edges[-1] * 1.25)
    lg = [gl(a, c, 16) for a, c in zip(edges[:-1], edges[1:])]
    rl, wl = np.concatenate([p[0] for p in lg]), np.concatenate([p[1] for p in lg])
    return rs, ws, rl, wl


def v_split(b, cache):
    rs, ws, rl, wl = panels_split(b)
    key = ("s",)
    if key not in cache:
        cache[key] = C_full(rs)
    cs = cache[key]
    cl = C_non(rl)
    g = lambda r: np.exp(-math.pi * r ** 2 / (2 * b * b))
    I4 = 2 * (np.sum(ws * g(rs) * chi(rs) * cs) + np.sum(wl * g(rl) * (1 - chi(rl)) * cl))
    return math.sqrt(2) * I2() + 2 * math.sqrt(2) * I3(b) + I4 / math.sqrt(2), I4 / math.sqrt(2)


def check(npts=4, seed=3):
    """Sine-limit pieces re-sum to the determinant; the numpy pieces equal the mp pieces."""
    rng = np.random.default_rng(seed)
    mp.mp.dps = 30
    m = SineLimit()
    worst = 0.0
    for _ in range(npts):
        d1, d2, r = rng.uniform(0.2, 2.0), rng.uniform(0.2, 2.0), rng.uniform(10, 40)
        o, n_, tot = S.connected_split(m, d1, d2, r)
        ref = det4(d1, d2, r) - rho2(d1) * rho2(d2)
        non, osc = nonosc_np(m, np.array(d1), np.array(d2), np.array(r))
        worst = max(worst, abs(float(mp.re(tot)) - ref), abs(complex(non) - complex(n_)), abs(complex(osc) - complex(o)),
                    abs((non + osc).real - ref))
        print("d=(%.3f,%.3f) r=%.2f  det %.3e  mp-total err %.1e  np non err %.1e  np osc err %.1e"
              % (d1, d2, r, ref, abs(float(mp.re(tot)) - ref), abs(complex(non) - complex(n_)), abs(complex(osc) - complex(o))))
    print("worst", worst)
    return worst


def run(out, bmax=10_000):
    cache, res = {}, []
    for b in [b for b in LADDER if b <= bmax]:
        vd, i4d = v_direct(b)
        vs, i4s = v_split(b, cache)
        res.append(dict(b=b, v_direct=vd, v_split=vs, diff=vs - vd, I4_direct=i4d, I4_split=i4s))
        print("b=%6d  v_direct %.8f  v_split %.8f  diff %.2e" % (b, vd, vs, vs - vd), flush=True)
    g = math.sqrt(res[-1]["v_direct"] / res[0]["v_direct"]) if res[-1]["b"] == 10_000 else None
    os.makedirs(out, exist_ok=True)
    json.dump(dict(I2=I2(), rows=res, g_direct=g), open(os.path.join(out, "gs_unitary.json"), "w"), indent=1)
    print("I2 %.8f  g(direct) %s" % (I2(), g))


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check()
    else:
        run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10_000)
