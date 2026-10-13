"""Route (a) step 1 (thirtieth round, Will, 2026-10-11): the ζ nearest-neighbour spacing density p(s; E) at the F3 heights
from CS08's n ≤ 4 correlations, and the four checks asked for before the prediction is tagged. No F3 file is decoded.

Spacing density from the correlations (unit mean spacing; translation-invariant ρ_n, even under reflection):
  E(s) = Σ_n ((−1)ⁿ/n!) ∫_{[0,s]ⁿ} ρ_n   ⇒   p(s) = E″(s) = Σ_{n≥2} ((−1)ⁿ/(n−2)!) ∫_{[0,s]^{n−2}} ρ_n(0, s, y) dy,
so p is computed DIRECTLY, term by term (no differentiation of E, unlike route_a_pgate.py):
  T₂(s) = ρ₂(0, s),  T₃(s) = ∫₀ˢ ρ₃(0, y, s) dy,  T₄(s) = ½ ∫∫_{[0,s]²} ρ₄(0, y₁, y₂, s) dy₁ dy₂,
  p₄ = T₂ − T₃ + T₄;  first omitted term T₅ = −(1/3!) ∫_{[0,s]³} ρ₅(0, y, s).
Quadrature: Gauss–Jacobi (weight y²(s − y)², divided out) with a different node count per axis (m, m + 2), so no two
axes share a node and the J* poles at coincident points are never hit; a second run at m + 4 gives the quadrature
error. Small-s rule in `terms` (T₃, T₄ skipped where the determinant's value is < 1e-12).
Uses the corrected sign of J13's prime-sum term (CS08_ERRATUM.md §4), found by this step's coincidence probe.

Correlations: ρ_n(d) = R_n(2πd/L)/Lⁿ, L = N (U(N)) or ℓ = log(t/2π) (ζ), with R_n assembled as in cs4lib (CS08 §5) from
vectorised J* pieces: cs4fast.FastZeta for ζ (prime sums over p ≤ pmax, long-double phases, A*'s resonance by its θ-integral)
and FastRMT below for U(N) (the same assembly, CS08's U(N) pieces as in cs4lib.RMT).

Estimand (thirtieth round (ii)): μ, the amplitude of CS08's arithmetic lower-order part. ρ_n^ζ − ρ_n^sine is that part
(the polar parts of ζ give the sine kernel exactly), and p is linear in the ρ_n, so
  p_μ(s) = p_sine(s) + μ·Δp(s),   Δp = Σ_{n=2..4} ((−1)ⁿ/(n−2)!) ∫ (ρ_n^ζ − ρ_n^sine)   (same nodes for both),
with p_sine the exact sine-kernel density (ph2lib Fredholm). Only Δp is truncated at n = 4.

  python route_a_zeta.py ugate [PROCS]                         U(N) known answer for this integrator → results/route_a_zeta_ugate.json
  python route_a_zeta.py pointcheck T PMAX                       fast vs 30-digit evaluator at the nodes nearest coincidence
  python route_a_zeta.py run CHUNK NCHUNKS OUT [PROCS]           ζ terms at the F3 heights (spot)
  python route_a_zeta.py merge OUT_DIR                           checks (a)–(d) → results/route_a_zeta.json
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
import cs4fast as F  # noqa: E402
import cs4lib as C  # noqa: E402

S_MAX = 1.8                      # sealed window (twenty-first round)
M_NODES = 24                     # Chebyshev–Lobatto nodes on [0, S_MAX] for p(s)
NODES = 0.5 * S_MAX * (1 - np.cos(np.pi * np.arange(M_NODES + 1) / M_NODES))
M_QUAD = 16                      # base Gauss–Legendre order; axes m, m + 2; error run at m + 4
PMAX_MAIN, PMAX_CHECK = 300_000, 1_000_000   # twenty-first round: cutoff ≥ 3·10⁵; convergence at 10⁶

# F3 (ph2r2/FRESH_SETS_F1_F3.md): file → declared height range [t0, t1); heights only, no data
F3 = {"zeros_15146000.dat": (15_146_000, 17_246_000),
      "zeros_25646000.dat": (25_646_000, 27_746_000),
      "zeros_248246000.dat": (248_246_000, 250_346_000),
      "zeros_2373446000.dat": (2_373_446_000, 2_375_546_000),
      "zeros_10639046000.dat": (10_639_046_000, 10_641_146_000)}


def ell_of(t):
    return math.log(t / (2 * math.pi))


def zero_weighted_t(t0, t1, n=4001):
    """The height whose ℓ is the zero-weighted mean of ℓ over [t0, t1) (density ∝ ℓ(t)): ∫ℓ² dt / ∫ℓ dt."""
    t = np.linspace(t0, t1, n)
    ell = np.log(t / (2 * math.pi))
    w = np.full(n, 1.0)
    w[0] = w[-1] = 0.5
    lbar = float(np.sum(w * ell ** 2) / np.sum(w * ell))
    return 2 * math.pi * math.exp(lbar)


def gl(m, s):
    """Gauss–Jacobi on [0, s] with weight y²(s − y)² divided out (α = β = 2): the integrands ρ_n(0, …, y, …, s) vanish as
    y² and (s − y)² at the ends, so nodes sit off the ends (as gs_zeta.gj does for d²; Gauss–Legendre's end nodes lost
    the signal to cancellation between the J* pieces, as in Stage 2's v1)."""
    from scipy.special import roots_jacobi
    x, w = roots_jacobi(m, 2.0, 2.0)                    # weight (1 − x)²(1 + x)² on [−1, 1]
    return 0.5 * s * (x + 1), 0.5 * s * w / ((1 - x) ** 2 * (1 + x) ** 2)


# ---------------------------------------------------------------- U(N), vectorised (CS08 §5, as cs4lib.RMT)
class FastRMT:
    def __init__(self, N):
        self.N = self.ell = N

    @staticmethod
    def z(x):
        return 1 / (1 - np.exp(-x))

    @staticmethod
    def zz(x):
        return -1 / (np.exp(x) - 1)

    @staticmethod
    def dzz(x):
        return np.exp(x) / (np.exp(x) - 1) ** 2

    def J11p(self, a, b):
        x = a.v + b.v
        return [(0 * a.c, self.dzz(x)), (a.c + b.c, self.z(x) * self.z(-x))]

    def J12p(self, a, b1, b2):
        z, zz = self.z, self.zz
        A = a.v
        out = []
        for bi, bj in ((b1, b2), (b2, b1)):
            x = A + bi.v
            out.append((a.c + bi.c, z(x) * z(-x) * (zz(bj.v - bi.v) - zz(bj.v + A))))
        return out

    def J13p(self, a, b1, b2, b3):
        z, zz = self.z, self.zz
        A = a.v
        out = []
        for bi, bj, bk in ((b1, b2, b3), (b2, b1, b3), (b3, b1, b2)):
            x = A + bi.v
            out.append((a.c + bi.c, z(x) * z(-x) * (zz(bj.v - bi.v) - zz(bj.v + A)) * (zz(bk.v - bi.v) - zz(bk.v + A))))
        return out

    def J22p(self, a1, a2, b1, b2):
        z, zz, dzz = self.z, self.zz, self.dzz
        A1, A2, B1, B2 = a1.v, a2.v, b1.v, b2.v
        out = [(0 * a1.c, dzz(A1 + B1) * dzz(A2 + B2) + dzz(A1 + B2) * dzz(A2 + B1))]
        for ai, bj, Ao, Bo in ((a1, b1, A2, B2), (a1, b2, A2, B1), (a2, b1, A1, B2), (a2, b2, A1, B1)):
            Ai, Bj = ai.v, bj.v
            x = Ai + Bj
            out.append((ai.c + bj.c, z(x) * z(-x) * (dzz(Ao + Bo) + (zz(Ao - Ai) - zz(Ao + Bj)) * (zz(Bo - Bj) - zz(Bo + Ai)))))
        num = 1
        for a in (A1, A2):
            for b in (B1, B2):
                num = num * z(a + b) * z(-a - b)
        out.append((a1.c + a2.c + b1.c + b2.c, num / (z(A1 - A2) * z(A2 - A1) * z(B1 - B2) * z(B2 - B1))))
        return out

    def Jp(self, A, B):
        return F.FastZeta.Jp(self, A, B)


# ---------------------------------------------------------------- assembly and the p terms
def R_n(Z, xs):
    """CS08 R_n at n points; xs = list of n real arrays (the raw variable, 2πd/L). Complex array."""
    n = len(xs)
    ell = Z.ell
    tot = np.full(xs[0].shape, float(ell) ** n, complex)
    for P, M in C.index_terms(n):
        A = [F.mk(+1, p, xs[p]) for p in P]
        B = [F.mk(-1, m, xs[m]) for m in M]
        pref = float(ell) ** (n - len(P) - len(M))
        for c, v in Z.Jp(A, B):
            phase = sum(int(c[k]) * xs[k] for k in range(n))
            tot = tot + pref * v * np.exp(-1j * ell * phase)
    return tot


def rho(Z, ds):
    """Unit-spacing ρ_n at points ds (list of n real arrays)."""
    L = float(Z.ell)
    return R_n(Z, [2 * math.pi * d / L for d in ds]) / L ** len(ds)


def sine_rho(ds, N=None):
    """det[K(d_i − d_j)] with the sine kernel (or the exact CUE_N kernel), points as a list of arrays."""
    D = np.stack(ds, -1)
    X = D[..., :, None] - D[..., None, :]
    K = np.ones_like(X)
    nz = np.abs(X) > 1e-15
    if N is None:
        K[nz] = np.sin(np.pi * X[nz]) / (np.pi * X[nz])
    else:
        K[nz] = np.sin(np.pi * X[nz]) / (N * np.sin(np.pi * X[nz] / N))
    return np.linalg.det(K)


def term_points(s, m):
    """Point sets and weights for T₂, T₃, T₄ at gap s (axes m, m + 2 for T₄; m for T₃)."""
    y3, w3 = gl(m, s)
    ya, wa = gl(m, s)
    yb, wb = gl(m + 2, s)
    Y1, Y2 = np.meshgrid(ya, yb, indexing="ij")
    W4 = np.outer(wa, wb).ravel()
    return dict(T2=([np.zeros(1), np.full(1, s)], np.ones(1), 1.0),
                T3=([np.zeros(m), y3, np.full(m, s)], w3, 1.0),
                T4=([np.zeros(Y1.size), Y1.ravel(), Y2.ravel(), np.full(Y1.size, s)], W4, 0.5))


SKIP = 1e-8         # thirty-fourth round (Will): T₃, T₄ of Z are not used where the determinant's value is below this
SKIP_RATIO = 100    # declared: |ρ_n^ζ/ρ_n^sine| ≤ 100 in the skipped region (observed ≤ 1; not proven), so |Δ_n| ≤ 1e-6


def terms(Z, s, m, N_det=None):
    """(T₂, T₃, T₄) from Z (None: from the determinant with kernel N_det; sine kernel if N_det is None).
    Small-s rule (thirty-fourth round): where |T_n| of the determinant (same nodes) is < SKIP = 1e-8, Z's T_n is set to
    that value (so Δ_n = 0) and listed in out["skipped"]. There all n points lie within s and ρ_n ~ s^{n(n−1)} (sine
    kernel: T₃ ~ s⁷, T₄ ~ s¹⁴; skipped: T₃ for s ≤ 0.07, T₄ for s ≤ 0.45 on the sealed nodes), and the J* pieces cancel to
    below double precision (route (a) pointcheck: garbage at s = 0.008). Declared bound: assuming |ρ_n^ζ/ρ_n^sine| ≤ 100
    there (observed ≤ 1, not proven), |Δ_n| ≤ (1 + 100)·SKIP ≈ 1e-6, far below the ~1e-4 bin resolution. The rule is
    applied again at merge (`apply_skip`), so job files written under the earlier SKIP = 1e-12 stay valid."""
    out = {"skipped": []}
    for k, (ds, w, c) in term_points(s, m).items():
        ref = float(c * np.sum(w * sine_rho(ds, N_det)))
        if Z is None:
            out[k] = ref
        elif k != "T2" and abs(ref) < SKIP:
            out[k] = ref
            out["skipped"].append(k)
        else:
            out[k] = float(c * np.sum(w * np.real(rho(Z, ds))))
    return out


def T5_det(s, m, N=None):
    """First omitted term −(1/3!)∫_{[0,s]³} det₅ (axes m, m + 2, m + 4)."""
    axes = [gl(m + 2 * k, s) for k in range(3)]
    Y = np.meshgrid(*[a[0] for a in axes], indexing="ij")
    W = np.einsum("i,j,k->ijk", *[a[1] for a in axes]).ravel()
    ds = [np.zeros(W.size)] + [y.ravel() for y in Y] + [np.full(W.size, s)]
    return float(-np.sum(W * sine_rho(ds, N)) / 6)


def T6_det(s, m=6, N=None):
    """Second omitted term +(1/4!)∫_{[0,s]⁴} det₆ (axes m, m + 2, m + 4, m + 6): the n = 6 term of the n ≤ 5 model
    (thirty-sixth round). Sine kernel at s = 1.8: 1.427e-9 (m = 6 and 8 agree to 4 digits)."""
    axes = [gl(m + 2 * k, s) for k in range(4)]
    Y = np.meshgrid(*[a[0] for a in axes], indexing="ij")
    W = np.einsum("i,j,k,l->ijkl", *[a[1] for a in axes]).ravel()
    ds = [np.zeros(W.size)] + [y.ravel() for y in Y] + [np.full(W.size, s)]
    return float(np.sum(W * sine_rho(ds, N)) / 24)


T5_RANGE_LEVEL = 1e-7      # thirty-sixth round (2): the computed Δ₅ nodes must span the s-range where |T₅^sine| > this
T6_CAP = 100               # thirty-sixth round (3): n = 6 bound = 100·|T₆^sine|
DMU_SYS = 2e-4              # thirty-eighth round: systematic allowance for mean-height vs file-average Δp
TRUNC_MAX = 1e-5           # declared: the truncation bound must stay ≤ 1e-5 on the window (≥ 10× below ~1e-4 bins)


def t5_range_start():
    """Smallest s with |T₅^sine(s)| > T5_RANGE_LEVEL (bisection on [0.9, 1.8])."""
    lo, hi = 0.9, 1.8
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if abs(T5_det(mid, 10)) > T5_RANGE_LEVEL:
            hi = mid
        else:
            lo = mid
    return hi


def p4(T):
    return T["T2"] - T["T3"] + T["T4"]


# ---------------------------------------------------------------- U(N) known-answer gate for this integrator
def _ugate_one(job):
    N, s = job
    if s == 0:
        return dict(N=N, s=0.0, p4=0.0, p4_q=0.0, T5=0.0, pointwise=0.0, skipped=[])
    Z = FastRMT(N)
    T, Tq = terms(Z, s, M_QUAD, N_det=N), terms(Z, s, M_QUAD + 4, N_det=N)
    D = terms(None, s, M_QUAD, N_det=N)
    pw = max(abs(T[k] - D[k]) for k in ("T2", "T3", "T4"))       # transcription vs determinant at the same nodes
    t5 = T5_det(s, 10, N) if N >= 5 else 0.0
    return dict(N=N, s=float(s), p4=p4(Tq), p4_q=abs(p4(Tq) - p4(T)), T5=t5, pointwise=pw, skipped=T["skipped"])


def ugate(procs=8):
    sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
    import ph2lib
    NS = (4, 10, 50)
    with Pool(procs) as pool:
        rows = pool.map(_ugate_one, [(N, s) for N in NS for s in NODES], chunksize=1)
    out = dict(rows={}, nodes=NODES.tolist())
    for N in NS:
        r = [x for x in rows if x["N"] == N]
        pN = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=(), N=N)[0](NODES)
        diff = np.array([x["p4"] for x in r]) - pN
        lim = np.array([(1e-6 if N <= 4 else 1.5 * abs(x["T5"]) + 1e-6) + x["p4_q"] for x in r])
        out["rows"][str(N)] = dict(max_abs_diff=float(np.max(np.abs(diff))), max_ratio=float(np.max(np.abs(diff) / lim)),
                                   max_pointwise=float(max(x["pointwise"] for x in r)),
                                   max_quad=float(max(x["p4_q"] for x in r)),
                                   PASS=bool(np.all(np.abs(diff) <= lim)), diff=diff.tolist())
        v = out["rows"][str(N)]
        print(f"N={N}: max |p4 − p_N| {v['max_abs_diff']:.2e} (ratio to limit {v['max_ratio']:.3f}); transcription vs "
              f"det at the nodes {v['max_pointwise']:.1e}; quadrature {v['max_quad']:.1e}  {'PASS' if v['PASS'] else 'FAIL'}",
              flush=True)
    out["PASS"] = all(v["PASS"] for v in out["rows"].values())
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "route_a_zeta_ugate.json"), "w"), indent=1)
    print("route (a) step-1 integrator, U(N) known answer:", "PASS" if out["PASS"] else "FAIL")
    return out


# ---------------------------------------------------------------- fast vs 30-digit evaluator at the hardest nodes
def pointcheck(t, pmax, n_pts=6):
    """At the T₄ nodes with the smallest pairwise separation (s = smallest and largest non-zero node), compare the vectorised
    ρ_n with cs4lib.Zeta (30-digit ζ pieces) at the same pmax. Also T₂/T₃ nodes."""
    import mpmath as mp
    Zf = F.FastZeta(t, pmax=pmax)
    Zs = C.Zeta(t, pmax=pmax)
    L = Zf.ell
    rows = []
    for s in (NODES[1], NODES[M_NODES // 2], NODES[-1]):
        for key, (ds, w, c) in term_points(s, M_QUAD).items():
            P = np.stack(ds, -1)
            sep = np.min(np.abs(P[:, :, None] - P[:, None, :]) + np.eye(P.shape[1]) * 9, axis=(1, 2))
            for i in np.argsort(sep)[:n_pts if key == "T4" else 2]:
                fast = complex(rho(Zf, [np.array([d[i]]) for d in ds])[0])
                slow = complex(Zs.R([mp.mpf(2 * math.pi * d[i] / L) for d in ds]) / mp.mpf(L) ** len(ds))
                rows.append(dict(s=float(s), term=key, min_sep=float(sep[i]), fast=fast.real, slow=slow.real,
                                 abs_err=abs(fast - slow)))
                print(rows[-1], flush=True)
    return rows


# ---------------------------------------------------------------- ζ terms at the F3 heights (spot)
def jobs():
    """(file, which-height, pmax, quad order, s) for every evaluation. Heights: the zero-weighted mean for every file at both
    cutoffs; both ends of the lowest file (the file-average check) at the main cutoff; quadrature error at m + 4, main cutoff."""
    J = []
    for f, (t0, t1) in F3.items():
        for pm in (PMAX_MAIN, PMAX_CHECK):
            J += [(f, "mean", pm, M_QUAD, float(s)) for s in NODES[1:]]
        J += [(f, "mean", PMAX_MAIN, M_QUAD + 4, float(s)) for s in NODES[1:]]
    f0 = min(F3, key=lambda k: F3[k][0])
    for which in ("t0", "t1"):
        J += [(f0, which, PMAX_MAIN, M_QUAD, float(s)) for s in NODES[1:]]
    return J


def height(f, which):
    t0, t1 = F3[f]
    return {"mean": zero_weighted_t(t0, t1), "t0": float(t0), "t1": float(t1)}[which]


def _run_one(job):
    f, which, pm, m, s = job
    t = height(f, which)
    Z = F.FastZeta(t, pmax=pm)
    Tz = terms(Z, s, m)
    Ts = terms(None, s, m)
    out = dict(file=f, which=which, t=t, ell=Z.ell, pmax=pm, m=m, s=s, zeta=Tz, sine=Ts)
    if pm == PMAX_MAIN and m == M_QUAD and which == "mean":
        out["T5_sine"] = T5_det(s, 10)
    print(json.dumps(out), flush=True)
    return out


def run(chunk, nchunks, out_dir):
    """Serial over this chunk's jobs (one process per chunk); one JSON line per job, appended, so a restart skips done jobs."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"terms_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        for line in open(path):
            r = json.loads(line)
            done.add((r["file"], r["which"], r["pmax"], r["m"], r["s"]))
    for i, j in enumerate(jobs()):
        if i % nchunks != chunk or j in done:
            continue
        r = _run_one(j)
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")


# ---------------------------------------------------------------- merge: the prediction and checks (a)–(d)
def cheb_interp(vals, s):
    """Barycentric interpolation through the Chebyshev–Lobatto NODES (weights (−1)^k, halved at the ends)."""
    w = (-1.0) ** np.arange(len(NODES))
    w[0] *= 0.5
    w[-1] *= 0.5
    s = np.atleast_1d(np.asarray(s, float))
    D = s[:, None] - NODES[None, :]
    hit = np.isclose(D, 0, atol=1e-14)
    D[hit] = 1.0
    K = w / D
    out = (K @ vals) / K.sum(1)
    r, c = np.nonzero(hit)
    out[r] = np.asarray(vals)[c]
    return out


def apply_skip(r):
    """The small-s rule at merge time: ζ's T₃/T₄ replaced by the sine value where |sine| < SKIP (idempotent)."""
    for k in ("T3", "T4"):
        if abs(r["sine"][k]) < SKIP:
            r["zeta"][k] = r["sine"][k]
            r["zeta"].setdefault("skipped", [])
            if k not in r["zeta"]["skipped"]:
                r["zeta"]["skipped"].append(k)
    return r


def merge(out_dir):
    sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
    import ph2lib
    import r2lib
    rows = []
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("terms_c") and fn.endswith(".jsonl"):
            rows += [json.loads(x) for x in open(os.path.join(out_dir, fn))]
    # one row per job: jobs computed twice in the 2026-10-12 hand-over race are bit-identical (xcheck.duplicate_pairs);
    # keep the first copy so every per-height list has exactly one row per node
    uniq = {}
    for r in rows:
        uniq.setdefault((r["file"], r["which"], r["pmax"], r["m"], r["s"]), r)
    rows = [apply_skip(r) for r in uniq.values()]
    need = len(jobs())
    assert len({(r["file"], r["which"], r["pmax"], r["m"], r["s"]) for r in rows}) == need, (len(rows), need)

    def series(f, which, pm, m, key):
        """Per node s > 0 (s = 0 prepended as 0): Δ = (ζ − sine) and the ζ value of p and of each term."""
        by_s = {r["s"]: r for r in rows if (r["file"], r["which"], r["pmax"], r["m"]) == (f, which, pm, m)}
        out = [0.0]
        for s in NODES[1:]:
            r = by_s[float(s)]
            if key == "dp":
                out.append(p4(r["zeta"]) - p4(r["sine"]))
            elif key == "pz":
                out.append(p4(r["zeta"]))
            else:
                out.append(r["zeta"][key] - r["sine"][key])
        return np.array(out)

    grid = np.linspace(0, S_MAX, 1801)
    p_sine = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=())[0]
    res = dict(window=S_MAX, nodes=NODES.tolist(), pmax=PMAX_MAIN, pmax_check=PMAX_CHECK, m_quad=M_QUAD, files={})
    for f, (t0, t1) in F3.items():
        t = height(f, "mean")
        dp = series(f, "mean", PMAX_MAIN, M_QUAD, "dp")
        dp_hi = series(f, "mean", PMAX_CHECK, M_QUAD, "dp")
        dp_q = series(f, "mean", PMAX_MAIN, M_QUAD + 4, "dp")
        pz = series(f, "mean", PMAX_MAIN, M_QUAD, "pz")
        DP = cheb_interp(dp, grid)
        P1 = p_sine(grid) + DP
        mx = float(np.max(np.abs(DP)))
        proj = lambda e: float(np.sum(cheb_interp(e, grid) * DP) / np.sum(DP * DP))   # δμ of a change e in Δp
        main = [r for r in rows if (r["file"], r["which"], r["pmax"], r["m"]) == (f, "mean", PMAX_MAIN, M_QUAD)]
        main = sorted(main, key=lambda r: r["s"])
        # (a) n = 2 against the R₂ phase's library (CS07 Thm 4.1, independent transcription), same height and cutoff
        K = r2lib.Kernel(2 * math.pi * NODES[1:] / ell_of(t), pmax=PMAX_MAIN)
        r2_ref = K.R(t) / (ell_of(t) / (2 * math.pi)) ** 2
        T2z = np.array([r["zeta"]["T2"] for r in main])
        a_err = float(np.max(np.abs(T2z - r2_ref)))
        # (b) positivity and a valid density on the window, μ = 1 (μ ∈ [0, 1] follows: p_μ is linear in μ, p_sine > 0)
        mass = float(np.trapezoid(P1, grid))
        # (c) THIRTY-SIXTH ROUND: the n ≤ 5 model. Δ₅ = T₅^ζ − T₅^sine, COMPUTED from the ratios-conjecture definition
        # (ratios_t5.py, behind its U(N) gate), is ADDED to Δp at the edge nodes (|T₅^sine| ≥ 1e-8). Conditions:
        #  (1) the T₅ prime-cutoff check (p ≤ 1000 vs 3000) passes (ratios_t5.merge: |change| ≤ 1e-6 at every checked node);
        #  (2) the computed nodes span the s-range where |T₅^sine| > 1e-7 (declared from the determinant, t5_range_start);
        #  (3) truncation: the n = 6 term, bounded by 100·|T₆^sine| (exact, determinant), plus the round-34 bound
        #      100·|T₅^sine| ≤ 1e-6 at the nodes below the edge where Δ₅ is not computed; ≤ TRUNC_MAX on the window.
        t5f = os.path.join(HERE, "results", "ratios_t5.json")
        if not os.path.exists(t5f):
            raise RuntimeError("thirty-sixth round: the n ≤ 5 model needs results/ratios_t5.json (computed Δ₅); none found")
        t5res = json.load(open(t5f))
        computed = t5res["files"][f]["delta5"]
        cutoff_ok = bool(t5res["files"][f]["cutoff_pass"]) if "cutoff_pass" in t5res["files"][f] else None
        T5s = np.array([0.0] + [r["T5_sine"] for r in main])
        d5_signed = np.zeros(len(NODES))
        trunc5 = np.zeros(len(NODES))
        for i, sn in enumerate(NODES):
            key = str(float(sn))
            if key in computed:
                d5_signed[i] = computed[key]
            else:
                trunc5[i] = 100 * abs(T5s[i])
        s0 = t5_range_start()
        edge = sorted(float(k) for k in computed)
        spans = bool(edge and edge[0] <= s0 and abs(edge[-1] - S_MAX) < 1e-12)
        T6 = np.array([0.0] + [abs(T6_det(float(sn))) for sn in NODES[1:]])
        trunc6 = T6_CAP * T6
        trunc = trunc5 + trunc6
        TR = np.abs(cheb_interp(trunc, grid))
        dmu_trunc = float(np.sum(TR * np.abs(DP + cheb_interp(d5_signed, grid))) / np.sum((DP + cheb_interp(d5_signed, grid)) ** 2))
        # the prediction from here on is the n ≤ 5 model
        dp = dp + d5_signed
        dp_hi = dp_hi + d5_signed
        dp_q = dp_q + d5_signed
        DP = cheb_interp(dp, grid)
        P1 = p_sine(grid) + DP
        mx = float(np.max(np.abs(DP)))
        mass = float(np.trapezoid(P1, grid))
        full5 = np.abs(T5s) + np.abs(d5_signed)
        d5 = np.abs(d5_signed)
        src = ["computed" if str(float(sn)) in computed else "bound" for sn in NODES]
        dmu5 = dmu_trunc
        dmu5_signed = proj(d5_signed)
        # (d) prime cutoff at the sealed quantity Δp: 3·10⁵ → 10⁶
        d_change = dp_hi - dp
        # interpolation: the 13-node subset interpolant against the 25-node values at the odd nodes (conservative)
        # file average: the lowest file only (largest ℓ range), Simpson over (t0, mean, t1)
        fav = None
        if f == min(F3, key=lambda k: F3[k][0]):
            e0, e1 = series(f, "t0", PMAX_MAIN, M_QUAD, "dp"), series(f, "t1", PMAX_MAIN, M_QUAD, "dp")
            avg = (e0 + 4 * dp + e1) / 6
            fav = dict(max_abs=float(np.max(np.abs(avg - dp))), dmu=proj(avg - dp), ell_t0=ell_of(t0), ell_t1=ell_of(t1))
        res["files"][f] = dict(
            t_mean=t, ell_mean=ell_of(t), dp_nodes=dp.tolist(), pz_nodes=pz.tolist(), max_abs_dp=mx,
            check_a=dict(max_abs_T2_vs_r2lib=a_err, PASS=a_err <= 1e-9),
            check_b=dict(min_p_mu1=float(P1[1:].min()), min_p_zeta_nodes=float(pz[1:].min()), window_mass_mu1=mass,
                         window_mass_sine=float(np.trapezoid(p_sine(grid), grid)),
                         PASS=bool(P1[1:].min() > 0 and pz[1:].min() > 0 and 0 < mass < 1)),
            check_c=dict(model="n <= 5 (thirty-sixth round)", source=src, delta5_included=d5_signed.tolist(),
                         dmu_of_included_delta5=dmu5_signed, t5_cutoff_pass=cutoff_ok,
                         t5_range_level=T5_RANGE_LEVEL, t5_range_start=s0, computed_nodes=edge, nodes_span_range=spans,
                         T6_sine=T6.tolist(), trunc6_bound=trunc6.tolist(), trunc5_below_edge=trunc5.tolist(),
                         max_trunc=float(trunc.max()), trunc_at_window_edge=float(trunc[-1]), dmu_trunc_worst_sign=dmu5,
                         PASS=bool(cutoff_ok and spans and trunc.max() <= TRUNC_MAX),
                         T5_sine=T5s.tolist()),
            check_d=dict(max_abs_change=float(np.max(np.abs(d_change))), rel_change=float(np.max(np.abs(d_change)) / mx),
                         dmu=proj(d_change)),
            quad=dict(max_abs=float(np.max(np.abs(dp_q - dp))), dmu=proj(dp_q - dp)),
            interp=dict(half_grid_max_abs=float(np.max(np.abs(cheb_interp_sub(dp[::2], NODES[1::2]) - dp[1::2]))),
                        cheb_tail=cheb_tail(dp)),
            file_average=fav,
            prediction=dict(grid_step=S_MAX / 1800, dp=DP.tolist(), p_sine=p_sine(grid).tolist()))
        v = res["files"][f]
        print(f"{f}: ℓ̄ {v['ell_mean']:.4f}  max|Δp| {mx:.3e}  (a) {a_err:.1e}  (b) min p {v['check_b']['min_p_mu1']:.2e} "
              f"mass {mass:.4f}  (c) n≤5: Δ₅ incl. (δμ {v['check_c']['dmu_of_included_delta5']:+.1e}), trunc ≤ {v['check_c']['max_trunc']:.1e} (δμ ≤ {v['check_c']['dmu_trunc_worst_sign']:.1e}), span {v['check_c']['nodes_span_range']}, T5 cutoff {v['check_c']['t5_cutoff_pass']}  "
              f"(d) {v['check_d']['max_abs_change']:.1e} (δμ {v['check_d']['dmu']:+.1e})  quad {v['quad']['max_abs']:.1e}  "
              f"interp tail {v['interp']['cheb_tail']:.1e}" + (f"  file-avg δμ {fav['dmu']:+.1e}" if fav else ""), flush=True)
    # Cross-machine check (Will, 2026-10-12: "keep the split, add the cross-machine check"): the terms come from three
    # CPUs (spot, this machine, char); xcheck.py recomputes spot jobs elsewhere and requires agreement ≤ 1e-12. The
    # prediction is taggable only with that PASS and every per-height check PASS (fail closed if the file is missing).
    xf = os.path.join(HERE, "results", "xcheck.json")
    xc = json.load(open(xf)) if os.path.exists(xf) else None
    res["xcheck"] = None if xc is None else {k: xc[k] for k in ("tol", "n", "worst", "by_host", "PASS") if k in xc}
    per_ok = all(v["check_a"]["PASS"] and v["check_b"]["PASS"] and v["check_c"]["PASS"] for v in res["files"].values())
    res["TAGGABLE"] = bool(per_ok and xc is not None and xc.get("PASS"))
    res["definition"] = ("Delta p at each F3 file's zero-weighted mean height (zero_weighted_t); the read's estimator "
                         "has expectation equal to the zero-weighted file average (thirty-eighth round)")
    res["delta_mu_sys"] = dict(value=DMU_SYS, basis="mean-height vs file-average gap: measured +1.0e-4 at the widest "
                               "file (zeros_15146000, Var l = 1.40e-3), second-order (Var l) scaling for the others "
                               "(<= 4e-5); thirty-eighth round")
    print("per-height checks (a)–(c):", "PASS" if per_ok else "FAIL", "| cross-machine check:",
          "missing" if xc is None else ("PASS" if xc.get("PASS") else "FAIL"), "| TAGGABLE:", res["TAGGABLE"], flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "route_a_zeta.json"), "w"), indent=1)
    return res


def cheb_tail(vals):
    """max |c_k| over the last three Chebyshev coefficients of the interpolant through NODES (DCT-I): the interpolation
    error estimate on the window (the 13-node half-grid comparison above is a conservative upper check)."""
    M = len(NODES) - 1
    f = np.asarray(vals, float)
    j = np.arange(M + 1)
    w = np.ones(M + 1)
    w[0] = w[-1] = 0.5
    c = np.array([(2.0 / M) * np.sum(w * f * np.cos(np.pi * j * k / M)) for k in range(M + 1)])
    c[0] *= 0.5
    c[-1] *= 0.5
    return float(np.max(np.abs(c[-3:])))


def cheb_interp_sub(vals, s):
    """Barycentric interpolation through the even-index subset of NODES (itself Chebyshev–Lobatto, M/2 intervals)."""
    nodes = NODES[::2]
    w = (-1.0) ** np.arange(len(nodes))
    w[0] *= 0.5
    w[-1] *= 0.5
    D = np.atleast_1d(s)[:, None] - nodes[None, :]
    K = w / D
    return (K @ vals) / K.sum(1)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "ugate":
        ugate(int(a[1]) if len(a) > 1 else 8)
    elif a[0] == "pointcheck":
        pointcheck(float(a[1]), int(a[2]))
    elif a[0] == "run":
        run(int(a[1]), int(a[2]), a[3])
    elif a[0] == "merge":
        merge(a[1])
    else:
        raise SystemExit(__doc__)
