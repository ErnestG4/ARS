"""Thirty-fourth round, item 2 (Will, 2026-10-12): the ζ-side n = 5 term of route (a)'s spacing law, constructed from the
ratios-conjecture DEFINITION (CS08 never writes R₅ for ζ), behind a U(N) gate that uses the same construction.

Construction. For both U(N) (CS08 Theorem "rat", a theorem) and ζ (CS08 Conjecture "ratiozeta"):
  ℛ(A,B;C,D) = Σ_{S⊂A, T⊂B, |S|=|T|} e^{−L(ΣS+ΣT)} Z(S̄+T⁻, T̄+S⁻; C, D) [· 𝒜_ζ(S̄+T⁻, T̄+S⁻; C, D) for ζ],
  Z(A,B;C,D) = Z(A,B)Z(C,D)/(Z(A,D)Z(B,C)),  Z(X,Y) = Π z(1+x+y) [ζ] or Π z(x+y), z(x) = 1/(1 − e^{−x}) [U(N)],
  𝒜_ζ = Π_p Z_p(A,B;C,D) ∫₀¹ 𝒜_{p,θ} dθ  (as in check_ratios_j.py; L = N or ℓ),
and J(A;B) = Π_{α∈A}∂_α Π_{β∈B}∂_β ℛ(A,B;C,D) at C = A, D = B. The mixed first derivative in every variable is taken
EXACTLY with multilinear jets: numbers a = Σ_{S ⊆ vars} a_S ε^S with ε_i² = 0, so J is the top coefficient of ℛ's jet.
Every function is applied to a jet by its Taylor series in the nilpotent part (only orders ≤ #variables present are
non-zero). Poles: the denominators Z(S̄+T⁻, D) and Z(T̄+S⁻, C) contain ζ(1 + 0) at C = A, D = B; they are evaluated as
1/ζ(1+x) (analytic at 0: x − γ₀x² + …), never as ζ.
Each Euler factor of 𝒜_{p,θ} depends on exactly one variable (every variable occurs once in S̄+T⁻ ∪ T̄+S⁻), so the θ
part is built componentwise (no convolutions over the θ × prime grid). θ-integral: trapezoid, 128 points for p < 30 and
48 above (Fourier decay ≤ p^{−k/2}). Primes p ≤ PMAX_T5 (truncated; convergence checked between two cutoffs).

Then R₅ is assembled as cs4lib does for n ≤ 4, now with every split (|P|, |M|) of the 5 points, and
  T₅(s) = −(1/3!) ∫_{[0,s]³} ρ₅(0, y₁, y₂, y₃, s) dy,   ρ₅ = R₅(2πd/L)/L⁵,
on Gauss–Jacobi axes (m, m + 2, m + 4), as route_a_zeta.T5_det.

  python ratios_t5.py selftest             jets vs cs4lib closed forms (U(N) and ζ, n ≤ 4); U(N) R₅ vs det (pointwise)
  python ratios_t5.py ugate [PROCS]        GATE: U(N) T₅ by this construction vs the determinant, at the edge nodes
  python ratios_t5.py zeta CHUNK NCHUNKS OUT    ζ T₅ at the edge nodes of every F3 height (spot)
  python ratios_t5.py merge OUT            → results/ratios_t5.json
"""
import itertools
import json
import math
import os
import sys
from functools import lru_cache

import mpmath as mp
import numpy as np

import cs4lib as C
import route_a_zeta as RA

PMAX_T5, PMAX_T5_CHECK = 1000, 3000
M_T5 = 6                                   # GJ axes 6, 8, 10 (480 points)
EDGE_MIN = 1e-8                            # edge nodes: |T₅^sine| ≥ this; below, the round-34 ratio-100 bound (≤ 1e-6)


# ---------------------------------------------------------------- multilinear jets
class Jets:
    """Arithmetic on arrays of shape (2^n, *batch): component S (bitmask) is the coefficient of Π_{i∈S} ε_i."""

    def __init__(self, n):
        self.n = n
        self.K = 1 << n
        self.pairs = [(S, T) for S in range(self.K) for T in range(self.K) if T & S == T]

    def const(self, v):
        v = np.asarray(v, complex)
        out = np.zeros((self.K,) + v.shape, complex)
        out[0] = v
        return out

    def var(self, v, i, sign=1):
        out = self.const(v)
        out[1 << i] = sign
        return out

    def mul(self, a, b):
        out = np.zeros(np.broadcast_shapes(a.shape, b.shape), complex)
        for S, T in self.pairs:
            out[S] += a[T] * b[S ^ T]
        return out

    def apply(self, x, derivs):
        """f(x) for a jet x, given derivs[k] = f^{(k)}(x₀) (arrays like x₀), k = 0 … n."""
        N = x.copy()
        N[0] = 0
        out = self.const(derivs[0])
        P = self.const(np.ones_like(x[0]))
        for k in range(1, self.n + 1):
            P = self.mul(P, N)
            if not np.any(P):
                break
            out = out + P * (derivs[k] / math.factorial(k))
        return out

    def exp(self, x):
        e = np.exp(x[0])
        return self.apply(x, [e] * (self.n + 1))

    def log(self, x):
        x0 = x[0]
        d = [np.log(x0)] + [(-1) ** (k + 1) * math.factorial(k - 1) / x0 ** k for k in range(1, self.n + 1)]
        return self.apply(x, d)

    def inv(self, x):
        x0 = x[0]
        return self.apply(x, [(-1) ** k * math.factorial(k) / x0 ** (k + 1) for k in range(self.n + 1)])


# ---------------------------------------------------------------- ζ(1+x) and 1/ζ(1+x) derivatives (vectorised)
GAMMA0 = float(mp.euler)


def zeta_derivs2(x0):
    """ζ, ζ′, ζ″ at 1 + x₀ (arrays), from zeta_em's validated triplet (ζ, ζ′/ζ, (ζ′/ζ)′)."""
    import zeta_em as ZE
    x0 = np.asarray(x0, complex)
    z, lz, dlz = ZE.zeta_triplet(x0.ravel())
    z, lz, dlz = z.reshape(x0.shape), lz.reshape(x0.shape), dlz.reshape(x0.shape)
    return [z, z * lz, z * (dlz + lz * lz)]


def invzeta_derivs2(x0):
    """1/ζ(1+x) and its first two derivatives at x₀ (arrays). Exactly at x₀ = 0 (the T⁻/S⁻ factors at C = A, D = B):
    the Laurent series ζ(1+x) = 1/x + γ₀ + … gives 1/ζ(1+x) = x − γ₀x² + …, i.e. (0, 1, −2γ₀)."""
    x0 = np.asarray(x0, complex)
    zero = np.abs(x0) < 1e-13
    safe = np.where(zero, 0.5, x0)
    g0, g1, g2 = zeta_derivs2(safe)
    h0 = 1 / g0
    h1 = -g1 * h0 * h0
    h2 = 2 * g1 * g1 * h0 ** 3 - g2 * h0 * h0
    return [np.where(zero, 0, h0), np.where(zero, 1, h1), np.where(zero, -2 * GAMMA0, h2)]


def support_order(x):
    """Number of variables x depends on (its nilpotent part's support)."""
    bits = 0
    for S in range(1, x.shape[0]):
        if np.any(x[S] != 0):
            bits |= S
    return bin(bits).count("1")


# ---------------------------------------------------------------- the ratio expression as a jet
class Model:
    """kind 'U' (L = N) or 'zeta' (L = ℓ, primes p ≤ pmax)."""

    def __init__(self, kind, L, pmax=None):
        self.kind, self.L = kind, float(L)
        if kind == "zeta":
            p = C.primes_np(pmax)
            p = p[p <= pmax]
            self.groups = []
            for sel, nth in ((p < 30, 128), (p >= 30, 48)):
                if np.any(sel):
                    pp = p[sel]
                    th = np.arange(nth) / nth
                    self.groups.append((pp, np.log(pp), np.exp(2j * np.pi * th)))

    # z-factors of Z(X,Y): numerator (inverse=False) or denominator (inverse=True), argument jet x (x₀ may be 0 only if
    # inverse)
    def zfac(self, J, x, inverse):
        if self.kind == "U":
            one_minus = self.zero_safe_1mexp(J, x)               # 1 − e^{−x} = 1/z(x)
            return one_minus if inverse else J.inv(one_minus)
        K = support_order(x)
        if K > 2:
            raise ValueError("a ζ factor with more than two variables (never occurs in the ratio formula)")
        d = invzeta_derivs2(x[0]) if inverse else zeta_derivs2(x[0])
        if not inverse and np.any(np.abs(x[0]) < 1e-13):
            raise ValueError("ζ(1 + 0) in a numerator")
        return J.apply(x, d + [0 * d[0]] * (J.n + 1 - len(d)))

    @staticmethod
    def zero_safe_1mexp(J, x):
        """1 − e^{−x} as a jet; analytic at x₀ = 0 (derivatives −(−1)^k e^{−x₀} for k ≥ 1)."""
        x0 = x[0]
        e = np.exp(-x0)
        return J.apply(x, [1 - e] + [-((-1) ** k) * e for k in range(1, J.n + 1)])

    def arith(self, J, AA, BB, Cc, D):
        """log 𝒜_ζ(AA, BB; Cc, D) as a jet. AA/BB: lists of (value, var index, sign) (sign ±1: the element is ±variable);
        Cc/D: constant values."""
        bshape = np.shape(np.asarray(AA[0][0]))
        tot = J.const(np.zeros(bshape, complex))
        for pp, lp, e in self.groups:
            # Z_p factors: log(1 − p^{−1−x−y}) summed with signs
            def zp_log(xjet):
                y = xjet.copy()
                y[0] = y[0] + 1
                u = J.exp(-y[..., None] * lp)                                           # p^{−1−x}, (K, *batch, P)
                v = -u
                v[0] = v[0] + 1
                return J.log(v)

            def jet_of(el):
                v, i, sg = el
                return J.var(v, i, sg) if i is not None else J.const(v)

            Aj = [jet_of(a) for a in AA]
            Bj = [jet_of(b) for b in BB]
            Cj = [J.const(c) for c in Cc]
            Dj = [J.const(d) for d in D]
            lz = np.zeros((J.K,) + bshape + (len(pp),), complex)
            for X, Y, sg in ((Aj, Bj, 1), (Cj, Dj, 1), (Aj, Dj, -1), (Bj, Cj, -1)):
                for x in X:
                    for y in Y:
                        lz = lz + sg * zp_log(x + y)
            # θ part: Π over single-variable factors, built componentwise on (P, θ)
            const = np.ones(bshape + (len(pp), len(e)), complex)
            comps = {0: const}
            # constants C (with e(−θ)) and D (with e(θ)) multiply; AA (e(−θ)), BB (e(θ)) divide
            for c in Cc:
                comps[0] = comps[0] * (1 - np.conj(e) * np.exp(-np.multiply.outer(0.5 + np.asarray(c, complex), lp))[..., None])
            for d in D:
                comps[0] = comps[0] * (1 - e * np.exp(-np.multiply.outer(0.5 + np.asarray(d, complex), lp))[..., None])
            for (v, i, sg), ph in [(a, np.conj(e)) for a in AA] + [(b, e) for b in BB]:
                qv = ph * np.exp(-np.multiply.outer(0.5 + np.asarray(v, complex), lp))[..., None]   # e(∓θ)p^{−½−x₀}
                f = 1 / (1 - qv)
                if i is None:
                    for S in comps:
                        comps[S] = comps[S] * f
                    continue
                df = -qv * lp[:, None] / (1 - qv) ** 2 * sg                         # d/dε of f, x = x₀ + sg·ε
                new = {}
                for S, c in comps.items():
                    new[S] = c * f
                    new[S | (1 << i)] = c * df
                comps = new
            mean = np.zeros((J.K,) + bshape + (len(pp),), complex)
            for S, c in comps.items():
                mean[S] = c.mean(axis=-1)
            lth = J.log(mean)
            tot = tot + (lz + lth).sum(axis=-1)
        return tot

    def ratio_jet(self, J, A, B):
        """ℛ(A,B;C=A,D=B) as a jet in the variables (A then B). A, B: lists of complex values."""
        nA = len(A)
        Cc, D = list(A), list(B)
        zero = np.zeros(np.shape(np.asarray(A[0])), complex)
        out = J.const(zero)
        for k in range(0, min(len(A), len(B)) + 1):
            for S in itertools.combinations(range(nA), k):
                for T in itertools.combinations(range(len(B)), k):
                    # elements as (value, var index, sign)
                    Sbar = [(A[i], i, 1) for i in range(nA) if i not in S]
                    Tm = [(-B[j], nA + j, -1) for j in T]
                    Tbar = [(B[j], nA + j, 1) for j in range(len(B)) if j not in T]
                    Sm = [(-A[i], i, -1) for i in S]
                    AA, BB = Sbar + Tm, Tbar + Sm
                    jet = lambda el: J.var(el[0], el[1], el[2])
                    # e^{−L(ΣS + ΣT)}
                    lin = J.const(zero)
                    for i in S:
                        lin = lin + J.var(A[i], i, 1)
                    for j in T:
                        lin = lin + J.var(B[j], nA + j, 1)
                    term = J.exp(-self.L * lin)
                    for a in AA:
                        for b in BB:
                            term = J.mul(term, self.zfac(J, jet(a) + jet(b), False))
                    for c in Cc:
                        for d in D:
                            term = J.mul(term, self.zfac(J, J.const(c + d), False))
                    for a in AA:
                        for d in D:
                            term = J.mul(term, self.zfac(J, jet(a) + J.const(d), True))
                    for b in BB:
                        for c in Cc:
                            term = J.mul(term, self.zfac(J, jet(b) + J.const(c), True))
                    if self.kind == "zeta":
                        term = J.mul(term, J.exp(self.arith(J, AA, BB, Cc, D)))
                    out = out + term
        return out

    def J(self, A, B):
        J = Jets(len(A) + len(B))
        return self.ratio_jet(J, list(A), list(B))[J.K - 1]

    def R(self, xs):
        """R_n at real points xs (raw variable): L^n + Σ_{P,M} L^{n−|P|−|M|} J({i x_p}; {−i x_m})."""
        n = len(xs)
        tot = self.L ** n
        idx = range(n)
        for kp in range(1, n + 1):
            for P in itertools.combinations(idx, kp):
                rest = [i for i in idx if i not in P]
                for km in range(1, len(rest) + 1):
                    for M in itertools.combinations(rest, km):
                        tot += self.L ** (n - kp - km) * self.J([1j * xs[p] for p in P], [-1j * xs[m] for m in M])
        return tot

    def rho(self, ds):
        return self.R([2 * math.pi * d / self.L for d in ds]) / self.L ** len(ds)


# ---------------------------------------------------------------- T₅ on the GJ grid
def t5_points(s, m=M_T5):
    axes = [RA.gl(m + 2 * k, s) for k in range(3)]
    pts = []
    for (i, y1), (j, y2), (k, y3) in itertools.product(*[list(enumerate(a[0])) for a in axes]):
        pts.append(((0.0, y1, y2, y3, s), axes[0][1][i] * axes[1][1][j] * axes[2][1][k]))
    return pts


def T5_model(model, s, m=M_T5, batch=24):
    pts = t5_points(s, m)
    tot = 0.0
    for i in range(0, len(pts), batch):
        chunk = pts[i:i + batch]
        ds = [np.array([p[0][k] for p in chunk]) for k in range(5)]
        w = np.array([p[1] for p in chunk])
        tot += float(np.sum(w * model.rho(ds).real))
    return -tot / 6


def edge_nodes():
    return [float(s) for s in RA.NODES[1:] if abs(RA.T5_det(s, 10)) >= EDGE_MIN]


# ---------------------------------------------------------------- checks
def selftest():
    rnd = np.random.default_rng(3)
    out = {}
    # (1) jets vs closed forms, U(N) and ζ (same primes), sizes (1,1) … (2,2), generic imaginary points
    for kind in ("U", "zeta"):
        if kind == "U":
            M, ref = Model("U", 10), C.RMT(10)
        else:
            M, ref = Model("zeta", math.log(1.619e7 / (2 * math.pi)), pmax=PMAX_T5), C.Zeta(1.619e7, pmax=PMAX_T5)
        worst = 0.0
        for na, nb in ((1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2)):
            A = list(1j * rnd.uniform(-0.6, 0.6, na))
            B = list(-1j * rnd.uniform(-0.6, 0.6, nb))
            mine = M.J(A, B)
            closed = complex(ref.J([mp.mpc(a) for a in A], [mp.mpc(b) for b in B]))
            worst = max(worst, abs(mine - closed) / abs(closed))
        out[f"J_vs_closed_{kind}"] = worst
        print(f"{kind}: jets vs closed-form J*, n ≤ 4 sizes: worst rel {worst:.2e}", flush=True)
    # (2) U(N): R₅ by the construction vs det, pointwise
    for N in (10, 50):
        M = Model("U", N)
        diffs, dets = [], []
        for _ in range(8):
            d = np.sort(rnd.uniform(0, 1.8, 5))
            mine = M.rho(list(d)).real
            det = RA.sine_rho([np.array([x]) for x in d], N)[0]
            diffs.append(abs(mine - det))
            dets.append(abs(det))
        # absolute: ρ₅ ranges over many decades on random points, so a relative test at a tiny ρ₅ measures rounding
        out[f"R5_vs_det_N{N}"] = dict(max_abs=max(diffs), max_det=max(dets))
        print(f"U({N}): ρ₅ construction vs det, pointwise max |diff| {max(diffs):.1e} (max ρ₅ {max(dets):.1e})", flush=True)
    return out


def _ugate_one(job):
    N, s = job
    return dict(N=N, s=s, T5_construct=T5_model(Model("U", N), s), T5_det=RA.T5_det(s, M_T5, N))


def ugate(procs=8):
    from multiprocessing import Pool
    nodes = edge_nodes()
    with Pool(procs) as pool:
        rows = pool.map(_ugate_one, [(N, s) for N in (10, 50) for s in nodes], chunksize=1)
    for r in rows:
        r["abs_diff"] = abs(r["T5_construct"] - r["T5_det"])
        r["PASS"] = r["abs_diff"] <= 1e-9 + 1e-6 * abs(r["T5_det"])
        print(r, flush=True)
    out = dict(nodes=nodes, rows=rows, PASS=all(r["PASS"] for r in rows))
    os.makedirs(os.path.join(RA.HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(RA.HERE, "results", "ratios_t5_ugate.json"), "w"), indent=1)
    print("U(N) gate for the ratios-definition T₅:", "PASS" if out["PASS"] else "FAIL")
    return out


# ---------------------------------------------------------------- ζ T₅ at the F3 heights (spot)
def zeta_jobs():
    """(file, s, pmax): every edge node at every F3 height at PMAX_T5; the prime-cutoff check at PMAX_T5_CHECK for the
    lowest and highest heights at the outermost node and one inner edge node."""
    nodes = edge_nodes()
    files = list(RA.F3)
    J = [(f, s, PMAX_T5) for f in files for s in nodes]
    for f in (files[0], files[-1]):
        for s in (nodes[-1], nodes[len(nodes) // 2]):
            J.append((f, s, PMAX_T5_CHECK))
    return J


def zeta_run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"t5_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["file"], r["s"], r["pmax"]) for r in map(json.loads, open(path))}
    for i, (f, s, pm) in enumerate(zeta_jobs()):
        if i % nchunks != chunk or (f, s, pm) in done:
            continue
        t = RA.height(f, "mean")
        M = Model("zeta", RA.ell_of(t), pmax=pm)
        row = dict(file=f, s=s, pmax=pm, t=t, ell=RA.ell_of(t), T5_zeta=T5_model(M, s), T5_sine=RA.T5_det(s, M_T5),
                   T5_sine_ref=RA.T5_det(s, 10))
        with open(path, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(row, flush=True)


def merge(out_dir):
    rows = [json.loads(x) for fn in sorted(os.listdir(out_dir)) if fn.startswith("t5_c") for x in open(os.path.join(out_dir, fn))]
    assert len({(r["file"], r["s"], r["pmax"]) for r in rows}) == len(zeta_jobs()), (len(rows), len(zeta_jobs()))
    res = dict(edge_min=EDGE_MIN, nodes=edge_nodes(), pmax=PMAX_T5, pmax_check=PMAX_T5_CHECK, m=M_T5, files={})
    for f in RA.F3:
        main = sorted([r for r in rows if r["file"] == f and r["pmax"] == PMAX_T5], key=lambda r: r["s"])
        d5 = {r["s"]: r["T5_zeta"] - r["T5_sine"] for r in main}
        chk = [r for r in rows if r["file"] == f and r["pmax"] == PMAX_T5_CHECK]
        conv = {r["s"]: abs((r["T5_zeta"] - r["T5_sine"]) - d5[r["s"]]) for r in chk}
        quad = max(abs(r["T5_sine"] - r["T5_sine_ref"]) for r in main)
        res["files"][f] = dict(ell=main[0]["ell"], delta5=d5, max_abs_delta5=max(abs(v) for v in d5.values()),
                               ratio=max(abs(d5[r["s"]]) / abs(r["T5_sine"]) for r in main),
                               cutoff_change=conv, quad_sine=quad)
        print(f, {k: v for k, v in res["files"][f].items() if k != "delta5"}, flush=True)
    json.dump(res, open(os.path.join(RA.HERE, "results", "ratios_t5.json"), "w"), indent=1)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "selftest":
        print(selftest())
    elif a[0] == "ugate":
        ugate(int(a[1]) if len(a) > 1 else 8)
    elif a[0] == "zeta":
        zeta_run(int(a[1]), int(a[2]), a[3])
    elif a[0] == "merge":
        merge(a[1])
    else:
        raise SystemExit(__doc__)
