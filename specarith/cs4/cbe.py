"""CβE_N eigenphases without a dense eigensolver, for the route (a) GUE calibration (fortieth round: CUE, N ≥ 10³ per block).

Killip–Nenciu (2004, Thm 1): if α_k ~ Θ_{β(N−k−1)+1} independently (k = 0..N−1; Θ_ν has density ∝ (1 − |z|²)^{(ν−3)/2} on
the disc, so |α_k|² ~ Beta(1, (ν − 1)/2) with a uniform phase; Θ_1 = uniform on the circle), the CMV matrix built from
(α_0, …, α_{N−1}) has the CβE_N eigenvalue law. Its eigenvalues are the zeros of the paraorthogonal polynomial Φ_N
(Szegő recursion Φ_{k+1} = zΦ_k − ᾱ_k Φ_k*), i.e. the solutions of b_{N−1}(e^{iθ}) = ᾱ_{N−1} with b_k = zΦ_k/Φ_k*.

On the circle b_{k+1} = z · b_k · conj(w_k)/w_k with w_k = 1 − α_k b_k (Re w_k > 0), so the lifted Prüfer phase
    ψ_0(θ) = θ,   ψ_{k+1}(θ) = θ + ψ_k(θ) − 2·arg(1 − α_k e^{iψ_k(θ)})          (principal arg, continuous in θ)
is continuous and strictly increasing, ψ_{N−1}(θ + 2π) = ψ_{N−1}(θ) + 2πN, with
    dψ_{k+1}/dθ = 1 + (dψ_k/dθ) · (1 − |u_k|²)/|1 − u_k|² > 0,   u_k = α_k e^{iψ_k}.
The N eigenphases in [0, 2π) are the roots of ψ_{N−1}(θ) = c_m, c_m = c_0 + 2πm (m = 0..N−1), c_0 the first value
> ψ_{N−1}(0) congruent to −arg α_{N−1}; each is bracketed in [0, 2π) and found by safeguarded Newton, so the roots come out
sorted and none is missed or doubled (monotone ψ, one root per c_m).

Cost O(N²·iterations) per matrix and one GPU thread per root (CuPy RawKernel), against O(N³) dense: about 1.7 s per
N = 1000 matrix for numpy eigvals on this machine's single core.

  python cbe.py selftest [gpu [OUT]] V1 deterministic (Prüfer roots = dense CMV eigvals), V2 β = 2 against Haar (Mezzadri),
                                   V3 β = 1, 2, 4 nearest-neighbour spacing variance against the sine-process limits
"""
import math
import sys

import numpy as np

TWO_PI = 2 * math.pi


# ---------------------------------------------------------------- the Killip–Nenciu coefficients
def verblunsky(rng, n_mat, N, beta):
    """α (n_mat, N) complex: α_k ~ Θ_{β(N−k−1)+1} for k ≤ N − 2, α_{N−1} uniform on the circle."""
    k = np.arange(N - 1)
    nu = beta * (N - k - 1) + 1.0
    r2 = rng.beta(1.0, (nu - 1) / 2, size=(n_mat, N - 1))
    ph = rng.uniform(0, TWO_PI, size=(n_mat, N))
    a = np.empty((n_mat, N), dtype=complex)
    a[:, :-1] = np.sqrt(r2) * np.exp(1j * ph[:, :-1])
    a[:, -1] = np.exp(1j * ph[:, -1])
    return a


# ---------------------------------------------------------------- references
def cmv_dense(a):
    """The N × N CMV matrix C = L·M (Simon's convention): Θ_j = [[ᾱ_j, ρ_j], [ρ_j, −α_j]], L = Θ_0 ⊕ Θ_2 ⊕ …,
    M = 1 ⊕ Θ_1 ⊕ Θ_3 ⊕ …, with the last (|α_{N−1}| = 1) block the 1 × 1 matrix (ᾱ_{N−1})."""
    N = len(a)
    L = np.zeros((N, N), complex)
    M = np.zeros((N, N), complex)
    M[0, 0] = 1.0
    for j in range(N):
        T = L if j % 2 == 0 else M
        if j == N - 1:
            T[j, j] = np.conj(a[j])
        else:
            r = math.sqrt(max(0.0, 1 - abs(a[j]) ** 2))
            T[j:j + 2, j:j + 2] = [[np.conj(a[j]), r], [r, -a[j]]]
    return L @ M


def dense_phases(a):
    """Eigenphases of the CMV matrix by numpy eigvals, sorted in [0, 2π)."""
    return np.sort(np.mod(np.angle(np.linalg.eigvals(cmv_dense(a))), TWO_PI))


# ---------------------------------------------------------------- Prüfer phase (numpy; reference and CPU fallback)
# ψ_{N−1} = N·θ + φ with φ_0 = 0, φ_{k+1} = φ_k − 2·arg(w_k): only the bounded part φ is accumulated (accumulating ψ,
# which reaches 2πN, cost ~10× in root accuracy). Root equation f(θ) = (N·θ − c_m) + φ(θ) = 0.
# Roots: a grid pass (G = GRID·N points) brackets every c_m between two grid points (ψ monotone), then safeguarded
# Newton from the linear interpolant inside that bracket; stop once a step is < STEP_TOL, after one more polishing step.
# The Newton step is that of the REAL form of the paraorthogonal polynomial, R(θ) ∝ |Φ*_{N−1}(e^{iθ})|·sin((ψ − c_m)/2)
# (Φ_N = Φ*_{N−1}·(b_{N−1} − ᾱ_{N−1}); every zero of R is on the circle, so Newton is well behaved):
#   δθ = −1 / [ (log|Φ*_{N−1}|)′ + (ψ′/2)·cot(f/2) ],   (log|Φ*_{N−1}|)′ = Σ_k ψ_k′·Im(u_k/w_k)   (|Φ*_{k+1}| = |Φ*_k|·|w_k|),
# with δθ = −f/ψ′ once |f| < 1e-8. Plain Newton on ψ needed 12.4 iterations on average (max 31) at N = 1000, mostly
# bisecting across steps where ψ rises by ~2π over a tiny θ range; this form needs 5.4 (max 10), same roots.
GRID = 4
STEP_TOL = 1e-12
ITMAX = 40


def phi_np(a, theta, amp=False):
    """φ(θ) = ψ_{N−1}(θ) − N·θ and dψ_{N−1}/dθ for θ (n_mat, K), a (n_mat, N); vectorised over matrices and θ.
    amp=True also returns (log|Φ*_{N−1}|)′."""
    th = np.asarray(theta, float)
    z = np.exp(1j * th)
    b = z.copy()
    phi = np.zeros_like(th)
    dp = np.ones_like(th)
    La = np.zeros_like(th)
    for k in range(a.shape[1] - 1):
        u = a[:, k:k + 1] * b
        w = 1 - u
        aw = np.abs(w) ** 2
        La = La + dp * np.imag(u / w)
        dp = 1 + dp * (1 - np.abs(u) ** 2) / aw
        phi = phi - 2 * np.angle(w)
        b = z * b * np.conj(w) ** 2 / aw
    return (phi, dp, La) if amp else (phi, dp)


def newton_step(f, dp, La):
    """The step δθ of the real-form Newton (see above); −f/ψ′ near the root."""
    with np.errstate(divide="ignore", invalid="ignore"):
        far = 1.0 / (La + 0.5 * dp / np.tan(0.5 * f))
    return np.where(np.abs(f) < 1e-8, f / dp, far)


def targets(a):
    """c_0 per matrix (the first value > ψ_{N−1}(0) congruent to −arg α_{N−1}) and ψ_{N−1}(0) (= φ(0))."""
    p0, _ = phi_np(a, np.zeros((a.shape[0], 1)))
    p0 = p0[:, 0]
    t = -np.angle(a[:, -1])
    c0 = p0 + np.mod(t - p0, TWO_PI)
    c0 = np.where(c0 <= p0, c0 + TWO_PI, c0)
    return c0, p0


def brackets(N, c0, psi_grid):
    """Per root m: grid interval j with ψ(θ_j) < c_m ≤ ψ(θ_{j+1}) and the linear-interpolation start (numpy arrays)."""
    G = psi_grid.shape[1] - 1
    tg = TWO_PI * np.arange(G + 1) / G
    c = c0[:, None] + TWO_PI * np.arange(N)[None, :]
    j = np.empty(c.shape, dtype=np.int64)
    for r in range(len(c0)):
        j[r] = np.searchsorted(psi_grid[r], c[r], side="left") - 1
    j = np.clip(j, 0, G - 1)
    p_lo = np.take_along_axis(psi_grid, j, 1)
    p_hi = np.take_along_axis(psi_grid, j + 1, 1)
    lo, hi = tg[j], tg[j + 1]
    start = lo + (hi - lo) * np.clip((c - p_lo) / (p_hi - p_lo), 0, 1)
    return lo, hi, np.clip(start, lo, hi)


def roots_np(a):
    """All N eigenphases per matrix (n_mat, N), sorted. Returns (θ, max iterations)."""
    n_mat, N = a.shape
    c0, _ = targets(a)
    G = GRID * N
    tg = np.broadcast_to(TWO_PI * np.arange(G + 1) / G, (n_mat, G + 1))
    phg, _ = phi_np(a, tg)
    lo, hi, th = brackets(N, c0, N * tg + phg)
    c = c0[:, None] + TWO_PI * np.arange(N)[None, :]
    done = np.zeros((n_mat, N), bool)
    polish = np.zeros((n_mat, N), bool)
    for it in range(ITMAX):
        phi, dp, La = phi_np(a, th, amp=True)
        f = (N * th - c) + phi
        lo = np.where(f < 0, th, lo)
        hi = np.where(f > 0, th, hi)
        new = th - newton_step(f, dp, La)
        new = np.where((new >= lo) & (new <= hi), new, 0.5 * (lo + hi))   # inclusive: a converged step may round onto lo/hi
        small = np.abs(new - th) < STEP_TOL
        th = np.where(done, th, new)
        done |= polish
        polish |= small
        if done.all():
            return th, it + 1
    raise RuntimeError(f"cbe.roots_np: {int((~done).sum())} roots not converged in {ITMAX} iterations")


# ---------------------------------------------------------------- the GPU kernels (CuPy): same arithmetic as numpy
_KERNEL = r"""
__device__ void phi_at(const double2* sa, const int N, const double th, double* phi_out, double* dp_out, double* la_out)
{
    double zr, zi;
    sincos(th, &zi, &zr);
    double br = zr, bi = zi, phi = 0.0, dp = 1.0, la = 0.0;
    for (int k = 0; k < N - 1; ++k) {
        const double ar = sa[k].x, ai = sa[k].y;
        const double ur = ar * br - ai * bi, ui = ar * bi + ai * br;
        const double wr = 1.0 - ur, wi = -ui;
        const double aw = wr * wr + wi * wi;
        la += dp * (ui * wr - ur * wi) / aw;                               // ψ_k′ · Im(u/w)
        dp = 1.0 + dp * (1.0 - (ur * ur + ui * ui)) / aw;
        phi -= 2.0 * atan2(wi, wr);
        const double cr = (wr * wr - wi * wi) / aw, ci = (-2.0 * wr * wi) / aw;   // conj(w)^2 / |w|^2
        const double tr = br * cr - bi * ci, ti = br * ci + bi * cr;
        br = zr * tr - zi * ti;
        bi = zr * ti + zi * tr;
    }
    *phi_out = phi;
    *dp_out = dp;
    *la_out = la;
}

extern "C" __global__
void grid_psi(const double2* __restrict__ alpha, const int N, const int n_mat, const int G, double* __restrict__ psi)
{
    extern __shared__ double2 sa[];
    const int mat = blockIdx.y;
    const double2* a = alpha + (size_t)mat * N;
    for (int k = threadIdx.x; k < N - 1; k += blockDim.x) sa[k] = a[k];
    __syncthreads();
    const int g = blockIdx.x * blockDim.x + threadIdx.x;
    if (g > G) return;
    const double th = 6.283185307179586476925286766559 * g / G;
    double phi, dp, la;
    phi_at(sa, N, th, &phi, &dp, &la);
    psi[(size_t)mat * (G + 1) + g] = N * th + phi;
}

extern "C" __global__
void newton(const double2* __restrict__ alpha, const double* __restrict__ c0, const int N, const int n_mat,
            const double step_tol, const int itmax, const double* __restrict__ lo0, const double* __restrict__ hi0,
            double* __restrict__ theta, int* __restrict__ iters)
{
    extern __shared__ double2 sa[];
    const int mat = blockIdx.y;
    const double2* a = alpha + (size_t)mat * N;
    for (int k = threadIdx.x; k < N - 1; k += blockDim.x) sa[k] = a[k];
    __syncthreads();
    const int m = blockIdx.x * blockDim.x + threadIdx.x;
    if (m >= N) return;
    const size_t idx = (size_t)mat * N + m;
    const double c = c0[mat] + 6.283185307179586476925286766559 * m;
    double lo = lo0[idx], hi = hi0[idx], th = theta[idx];
    int it = 0, polish = 0;
    for (; it < itmax; ++it) {
        double phi, dp, la;
        phi_at(sa, N, th, &phi, &dp, &la);
        const double f = (N * th - c) + phi;
        if (f < 0) lo = th; else if (f > 0) hi = th;
        const double step = fabs(f) < 1e-8 ? f / dp : 1.0 / (la + 0.5 * dp / tan(0.5 * f));
        double nw = th - step;
        if (!(nw >= lo && nw <= hi)) nw = 0.5 * (lo + hi);   // inclusive: a converged step may round onto lo/hi
        const int small = fabs(nw - th) < step_tol;
        th = nw;
        if (polish) break;
        if (small) polish = 1;
    }
    theta[idx] = th;
    iters[idx] = it + 1;
}
"""
_mod = None


def roots_gpu(a, threads=256):
    """roots_np on the GPU: grid kernel (one thread per grid point), brackets on the host, Newton kernel (one thread per
    root); the matrix's α sit in shared memory. Returns (θ, max iterations)."""
    import cupy as cp
    global _mod
    if _mod is None:
        _mod = cp.RawModule(code=_KERNEL)
    n_mat, N = a.shape
    c0, _ = targets(a)
    G = GRID * N
    ag = cp.asarray(np.ascontiguousarray(a))
    psi = cp.empty((n_mat, G + 1), dtype=cp.float64)
    sh = 16 * max(N - 1, 1)
    _mod.get_function("grid_psi")(((G + 1 + threads - 1) // threads, n_mat), (threads,),
                                  (ag, np.int32(N), np.int32(n_mat), np.int32(G), psi), shared_mem=sh)
    lo, hi, th = brackets(N, c0, cp.asnumpy(psi))
    thg = cp.asarray(th)
    its = cp.empty((n_mat, N), dtype=cp.int32)
    _mod.get_function("newton")(((N + threads - 1) // threads, n_mat), (threads,),
                                (ag, cp.asarray(c0), np.int32(N), np.int32(n_mat), np.float64(STEP_TOL), np.int32(ITMAX),
                                 cp.asarray(lo), cp.asarray(hi), thg, its), shared_mem=sh)
    itmax = int(cp.asnumpy(its).max())
    if itmax > ITMAX:                                  # the kernel writes itmax + 1 for a root that never converged
        raise RuntimeError(f"cbe.roots_gpu: {int(cp.asnumpy((its > ITMAX).sum()))} roots not converged in {ITMAX} iterations")
    return cp.asnumpy(thg), itmax


def spacings(theta):
    """Unfolded consecutive spacings N·Δθ/2π including the wrap-around one, (n_mat, N), mean exactly 1 per matrix."""
    N = theta.shape[1]
    d = np.diff(np.concatenate([theta, theta[:, :1] + TWO_PI], axis=1), axis=1)
    return d * N / TWO_PI


def sample(rng, n_mat, N, beta, gpu=False):
    a = verblunsky(rng, n_mat, N, beta)
    th, it = (roots_gpu if gpu else roots_np)(a)
    return th, it


# ---------------------------------------------------------------- self-test
SINE_NN_VAR = {1: 0.286, 2: 0.180, 4: 0.104}   # sine-β nearest-neighbour spacing variance (Mehta), shown beside V3, not tested
V1_TOL = 1e-9   # unfolded units; observed ~1e-10 (rounding of N·θ − c_m where ψ′ is small; dense eig is ~1e-13 there)
Z_MAX = 4.0     # V2/V3: every functional's z-score (independent matrices, SE from their spread) must stay below this
CUTS = (0.5, 1.0, 1.5)


def functionals(sp):
    """Per matrix: fraction of spacings below each cut and the mean of s² (mean s is exactly 1). sp (n_mat, N)."""
    return np.stack([(sp < x).mean(1) for x in CUTS] + [(sp ** 2).mean(1)], axis=1)


def zscore_exact(F, exact):
    m, sd = F.mean(0), F.std(0, ddof=1) / math.sqrt(len(F))
    return (m - exact) / sd


def zscore_two(F, G):
    return (F.mean(0) - G.mean(0)) / np.sqrt(F.var(0, ddof=1) / len(F) + G.var(0, ddof=1) / len(G))


def haar_phases(rng, n_mat, N):
    """Haar U(N) eigenphases (Mezzadri QR with phase correction), sorted."""
    Z = (rng.standard_normal((n_mat, N, N)) + 1j * rng.standard_normal((n_mat, N, N))) / math.sqrt(2)
    Qm, R = np.linalg.qr(Z)
    d = np.diagonal(R, axis1=1, axis2=2)
    Qm = Qm * (d / np.abs(d))[:, None, :]
    return np.sort(np.mod(np.angle(np.linalg.eigvals(Qm)), TWO_PI), axis=1)


def coe_phases(rng, n_mat, N):
    """COE_N: eigenphases of UᵀU, U Haar (Dyson)."""
    Z = (rng.standard_normal((n_mat, N, N)) + 1j * rng.standard_normal((n_mat, N, N))) / math.sqrt(2)
    Qm, R = np.linalg.qr(Z)
    d = np.diagonal(R, axis1=1, axis2=2)
    Qm = Qm * (d / np.abs(d))[:, None, :]
    S = np.transpose(Qm, (0, 2, 1)) @ Qm
    return np.sort(np.mod(np.angle(np.linalg.eigvals(S)), TWO_PI), axis=1)


def cse_phases(rng, n_mat, N):
    """CSE_N: U Haar in U(2N), S = J Uᵀ Jᵀ U (self-dual) has N doubly degenerate eigenphases (Dyson); keep one of each
    pair (sorted, every second)."""
    M2 = 2 * N
    Z = (rng.standard_normal((n_mat, M2, M2)) + 1j * rng.standard_normal((n_mat, M2, M2))) / math.sqrt(2)
    Qm, R = np.linalg.qr(Z)
    d = np.diagonal(R, axis1=1, axis2=2)
    Qm = Qm * (d / np.abs(d))[:, None, :]
    J = np.kron(np.eye(N), np.array([[0.0, 1.0], [-1.0, 0.0]]))
    S = J @ np.transpose(Qm, (0, 2, 1)) @ J.T @ Qm
    ph = np.sort(np.mod(np.angle(np.linalg.eigvals(S)), TWO_PI), axis=1)
    return ph[:, ::2]


def exact_cue_functionals(N):
    """The functionals' exact values for CUE_N from Phase 2's Fredholm tables (ph2lib.spacing_tables with N)."""
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ph2"))
    import ph2lib
    p = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=(), N=N)[0]
    g = np.linspace(0, 6.0, 60001)
    pg = p(g)
    out = [float(np.trapezoid(np.where(g <= x, pg, 0.0), g)) for x in CUTS]
    out.append(float(np.trapezoid(g ** 2 * pg, g)))
    return np.array(out), float(np.trapezoid(pg, g))


def selftest(gpu=False, n_cmv=2000, n_haar=100, n_small=400):
    out = {}
    rng = np.random.default_rng(20261013)
    roots = roots_gpu if gpu else roots_np
    # V1: deterministic — Prüfer roots equal the dense CMV eigenphases (several N, β)
    worst = 0.0
    for N, beta, n in ((5, 2, 20), (64, 2, 8), (200, 2, 4), (200, 1, 2), (200, 4, 2), (1000, 2, 2)):
        a = verblunsky(rng, n, N, beta)
        th, it = roots_np(a)
        ref = np.array([dense_phases(x) for x in a])
        dd = np.angle(np.exp(1j * (th - ref))) * N / TWO_PI          # in unfolded (mean-spacing) units
        worst = max(worst, float(np.abs(dd).max()))
        if gpu:
            tg, _ = roots_gpu(a)
            dg = float(np.abs(np.angle(np.exp(1j * (tg - th)))).max()) * N / TWO_PI
            out[f"V1_gpu_vs_np_N{N}_b{beta}"] = dg
        out[f"V1_iters_N{N}_b{beta}"] = it
    out["V1_max_abs_unfolded_diff"] = worst
    out["V1_PASS"] = worst < V1_TOL and all(v < V1_TOL for k, v in out.items() if k.startswith("V1_gpu"))
    print("V1", {k: v for k, v in out.items() if k.startswith("V1")}, flush=True)
    # V2: β = 2, N = 1000 — CMV sampler and dense Haar each against the exact CUE_N functionals, and against each other
    N = 1000
    exact, mass = exact_cue_functionals(N)
    Fc = functionals(spacings(roots(verblunsky(rng, n_cmv, N, 2.0))[0]))
    Fh = functionals(spacings(haar_phases(rng, n_haar, N)))
    zc, zh, z2 = zscore_exact(Fc, exact), zscore_exact(Fh, exact), zscore_two(Fc, Fh)
    out["V2"] = dict(N=N, n_cmv=n_cmv, n_haar=n_haar, cuts=CUTS, exact=exact.tolist(), exact_mass=mass,
                     cmv_mean=Fc.mean(0).tolist(), haar_mean=Fh.mean(0).tolist(), z_cmv_exact=zc.tolist(),
                     z_haar_exact=zh.tolist(), z_cmv_haar=z2.tolist(),
                     PASS=bool(max(np.abs(zc).max(), np.abs(zh).max(), np.abs(z2).max()) < Z_MAX))
    print("V2", out["V2"], flush=True)
    # V3: β = 1 and 4 against dense COE / CSE at N = 200 (the β dependence of the sampler); the sine-β variance shown
    v3 = {}
    for beta, dense in ((1, coe_phases), (4, cse_phases)):
        Fc = functionals(spacings(roots(verblunsky(rng, n_small * 5, 200, float(beta)))[0]))
        Fd = functionals(spacings(dense(rng, n_small, 200)))
        z = zscore_two(Fc, Fd)
        v3[f"beta{beta}"] = dict(cmv_mean=Fc.mean(0).tolist(), dense_mean=Fd.mean(0).tolist(), z=z.tolist(),
                                 var_cmv=float(Fc[:, -1].mean() - 1), var_sine_beta=SINE_NN_VAR[beta])
    out["V3"] = dict(v3, PASS=bool(all(np.abs(v["z"]).max() < Z_MAX for v in v3.values())))
    print("V3", out["V3"], flush=True)
    out["PASS"] = bool(out["V1_PASS"] and out["V2"]["PASS"] and out["V3"]["PASS"])
    print("SELFTEST", "PASS" if out["PASS"] else "FAIL", flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        import json
        res = selftest(gpu=len(sys.argv) > 2 and sys.argv[2] == "gpu")
        if len(sys.argv) > 3:
            json.dump(res, open(sys.argv[3], "w"), indent=1)
