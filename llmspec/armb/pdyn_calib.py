"""Synthetic calibrators for the parametric-dynamics pipeline (pdyn_m2 / pdyn_m3). CPU only; numpy/scipy.

Matrix shapes as a 70M layer: 512x512 (symmetric eigenvalue pipeline, or square W), 2048x512 and 512x2048 (singular
values). Time grid = the real Arm B checkpoint grid by default (grids.arm_grid: every 10 steps 0-500 + Pythia log
steps, every 25 to 3000) or a uniform grid ("uniform:dt:stop").

Families (all stationary Gaussian matrix processes unless stated; every row of the output is a spectrum):
  C1 SMOOTH beta=1   H(t) = sum_a L_ta G_a with G_a independent GOE matrices (off-diagonal variance 1, diagonal 2) and
                     L the Karhunen-Loeve factor of the Gaussian kernel exp(-(t-t')^2 / 2 tau^2) on the grid (components
                     with eigenvalue < kl_tol * max dropped). Locally H(t+d) = H + d Hdot + d^2/2 Hddot with Hdot an
                     independent GOE: the Zakrzewski-Delande / Simons-Altshuler setting (W = Hdot) plus a small
                     Gaussian direct term Hddot_mm (k ~ sqrt(3/2n) ~ 0.05 at n = 512). Rectangular analogue: W(t) with
                     iid real Gaussian entries, same kernel -> singular values. THIS is the positive control for the
                     parametric statistics.
  C1 DBM (literal)   H(t_{i+1}) = H(t_i) + s sqrt(dt) G_i (plain Dyson Brownian motion; optional exact OU step with
                     restoring rate theta), s set so the per-interval displacement is xstep spacings. Increments are
                     independent, so finite-difference velocities are white (C_lag[j >= 1] = 0) and the FD curvature is
                     the difference of two independent Gaussians (sd sqrt(2)/(pi x_step) in k units): a DBM has no
                     ZD/SA statistics at ANY cadence. Kept because the addendum names it;
                     reported as its own known answer (verify (a-dbm)), and it is the process the "DBM-rate" wording
                     refers to. Which of the two the real trajectories resemble at 10-step cadence is a phase-1
                     measurement (C_lag[1] ~ 0 -> DBM-like).
  C2 SMOOTH beta=2   as C1 smooth with GUE increments (complex Hermitian; and complex Gaussian W -> real singular
                     values, the "real singular-value analogue").
  C2 POISSON walk    n independent levels, each a smooth Gaussian process in t (same kernel), positions uniform with
                     unit mean density, amplitude amp spacings: no repulsion; sorted-index tracking sees crossings as
                     kinks.
  C3 shuffle(spectra)  permute checkpoint order (times fixed).
  C5 sign_flips(U, V)  random +-1 per column, joint (u, v together, the real SVD gauge) or independent.
  C4 roundtrip_floor   re-estimate the spectra after rounding the matrix to fp32 (the bank's master precision) and,
                     as a comparison only, to bf16; report the unfolded-level displacement RMS of the round-trip
                     against the per-step displacement RMS: the measurement-noise floor of the velocity.
  PLANTED crossing (M3)  top-K triplets with levels 1, 2 a two-level system sig = s0 +- sqrt((a (t - t0))^2 + c^2)
                     whose vectors rotate by phi(t) = atan2(c, a (t - t0)) / 2 in a fixed 2-plane; K - 2 static
                     levels. Known answers: t_min = t0, g_min = 2c, rotation between t_{k-1} and t_{k+1} =
                     phi(t_{k-1}) - phi(t_{k+1}).
The time scale: tau is set from the requested x_step at the dense cadence (dt = 10 by default) for a GOE bulk,
  x_step = dt * sqrt(2 n) / (pi tau)  (Delta = pi/sqrt(n) at the semicircle centre, <v^2> = 2/tau^2);
  the pipeline reports the MEASURED x_step per window. The same tau is used for every family at that n (the
  rectangular and Poisson families then report their own measured x_step). The rate is an ASSUMPTION about the real
  runs ("DBM-rate assumption"), not a measurement.
"""
import sys, time
from pathlib import Path
import numpy as np
from scipy.linalg import eigh, svd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pdyn_m2 as M2  # noqa: E402

KL_TOL = 1e-12


def real_grid(stop=3000):
    import grids
    return np.array(grids.arm_grid("A0", stop), float)


def parse_grid(s):
    if s == "real": return real_grid()
    if s.startswith("real:"): return real_grid(int(s.split(":")[1]))
    if s.startswith("uniform:"):
        _, dt, stop = s.split(":"); return np.arange(0, int(stop) + 1, int(dt), dtype=float)
    raise ValueError(s)


def tau_for_xstep(n, xstep, dt=10.0, beta=1):
    """GOE: <v^2> = Var(Hdot_mm) = 2/tau^2; GUE (diagonal variance 1): 1/tau^2 -> tau scaled by 1/sqrt(2) to match."""
    return dt * np.sqrt(2 * n) / (np.pi * xstep) / (np.sqrt(2) if beta == 2 else 1.0)


def kl_factor(times, tau, tol=KL_TOL):
    t = np.asarray(times, float)
    Kmat = np.exp(-0.5 * ((t[:, None] - t[None, :]) / tau) ** 2)
    w, Q = eigh(Kmat)
    keep = w > tol * w.max()
    return Q[:, keep] * np.sqrt(w[keep])[None, :]          # (T, r): H(t) = sum_a L[t,a] G_a


def goe(n, rng):
    A = rng.standard_normal((n, n)); return (A + A.T) / np.sqrt(2)


def gue(n, rng):
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n)); return (A + A.conj().T) / 2


def _spectra_from_process(gen_component, decompose, L, r_shape, dtype, seed):
    rng = np.random.default_rng(seed)
    T, r = L.shape
    G = np.empty((r,) + r_shape, dtype)
    for a in range(r): G[a] = gen_component(rng)
    Gf = G.reshape(r, -1)
    out = None
    for t in range(T):
        Ht = (L[t] @ Gf).reshape(r_shape)
        s = decompose(Ht)
        if out is None: out = np.empty((T, len(s)))
        out[t] = s
    return out


def smooth_sym(n, times, tau, beta=1, seed=0):
    L = kl_factor(times, tau)
    gen = (lambda rng: goe(n, rng)) if beta == 1 else (lambda rng: gue(n, rng))
    return _spectra_from_process(gen, lambda H: eigh(H, eigvals_only=True), L, (n, n), float if beta == 1 else complex, seed)


def smooth_rect(m, n, times, tau, beta=1, seed=0):
    L = kl_factor(times, tau)
    if beta == 1:
        gen = lambda rng: rng.standard_normal((m, n))
    else:
        gen = lambda rng: (rng.standard_normal((m, n)) + 1j * rng.standard_normal((m, n))) / np.sqrt(2)
    return _spectra_from_process(gen, lambda W: svd(W, compute_uv=False), L, (m, n), float if beta == 1 else complex, seed)


def dbm_sym(n, times, xstep=0.1, seed=0, rect=None, theta=0.0, dt_ref=10.0):
    """Literal DBM: H(0) = GOE (off-diagonal variance 1), H(t+dt) = H(t) + s sqrt(dt) G with G an independent GOE;
    optional OU restoring term theta (exact step). s is set so that the first-order level displacement per dt_ref
    interval is xstep spacings at the semicircle centre: Var(delta H_mm) = 2 s^2 dt = (xstep Delta)^2, Delta = pi/sqrt(n).
    (As first built, s = 1 moved levels > 1 spacing per step and sorted-index tracking read white noise; fixed.)
    rect=(m, n): iid Gaussian increments on W -> singular values."""
    rng = np.random.default_rng(seed)
    t = np.asarray(times, float); T = len(t)
    Delta = np.pi / np.sqrt(n)
    s_inc = xstep * Delta / np.sqrt(2 * dt_ref)
    if rect is None:
        gen = lambda: goe(n, rng); dec = lambda H: eigh(H, eigvals_only=True)
    else:
        gen = lambda: rng.standard_normal(rect); dec = lambda W: svd(W, compute_uv=False)
    H = gen()
    out = [dec(H)]
    for i in range(1, T):
        dt = t[i] - t[i - 1]
        if theta > 0:
            H = H * np.exp(-theta * dt) + s_inc * np.sqrt((1 - np.exp(-2 * theta * dt)) / (2 * theta)) * gen()
        else:
            H = H + s_inc * np.sqrt(dt) * gen()
        out.append(dec(H))
    return np.array(out)


def poisson_walk(n, times, tau, amp, seed=0):
    rng = np.random.default_rng(seed)
    L = kl_factor(times, tau)
    base = np.sort(rng.uniform(0, n, n))
    Z = rng.standard_normal((L.shape[1], n))
    return base[None, :] + amp * (L @ Z)


def shuffle(spectra, seed=0):
    rng = np.random.default_rng(seed)
    return np.asarray(spectra)[rng.permutation(len(spectra))]


def sign_flips(U, V, seed=0, joint=True):
    rng = np.random.default_rng(seed)
    U2, V2 = [], []
    for u, v in zip(U, V):
        su = rng.choice([-1.0, 1.0], size=u.shape[1])
        sv = su if joint else rng.choice([-1.0, 1.0], size=v.shape[1])
        U2.append(u * su[None, :]); V2.append(v * sv[None, :])
    return U2, V2


def semicircle_cdf(n, sigma=1.0):
    """Oracle CDF for the GOE family (off-diagonal variance sigma^2): radius R = 2 sigma sqrt(n). Applied to the
    stripped spectrum it is a fixed map, so its velocities carry no unfolding noise; the finite-n edge deviation is
    irrelevant inside the band."""
    R = 2 * sigma * np.sqrt(n)
    def cdf(x):
        z = np.clip(np.asarray(x, float) / R, -1, 1)
        return 0.5 + (z * np.sqrt(1 - z ** 2) + np.arcsin(z)) / np.pi
    return cdf


# ---------------------------------------------------------------- C4 round-trip floor
def to_bf16(x):
    """Round-to-nearest-even emulation of bfloat16 on float32 input."""
    b = np.asarray(x, np.float32).view(np.uint32)
    lsb = (b >> 16) & 1
    b = (b + 0x7FFF + lsb) & 0xFFFF0000
    return b.view(np.float32).astype(np.float64)


def roundtrip_floor(m, n, times, tau, top_k, band, kde_c, seed=0, scale=0.02):
    """Smooth beta=1 rect family at matrix scale `scale` (entries ~ N(0, scale^2): a 70M layer's weights are ~ 0.02
    rms); for each checkpoint the spectrum of W, fp32(W), bf16(W). Returns per-level unfolded displacement RMS of
    each round-trip and the per-step displacement RMS, with their ratio."""
    L = kl_factor(times, tau); T, r = L.shape
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((r, m * n)) * scale
    S = {"fp64": [], "fp32": [], "bf16": []}
    for t in range(T):
        W = (L[t] @ G).reshape(m, n)
        S["fp64"].append(svd(W, compute_uv=False))
        S["fp32"].append(svd(W.astype(np.float32).astype(np.float64), compute_uv=False))
        S["bf16"].append(svd(to_bf16(W.astype(np.float32)), compute_uv=False))
    E = {k: M2.unfold_series(np.array(v), top_k, band, kde_c, 1e-3)[0] for k, v in S.items()}
    step_rms = float(np.sqrt(np.mean(np.diff(E["fp64"], axis=0) ** 2)))
    out = dict(step_rms=step_rms)
    for k in ("fp32", "bf16"):
        d = float(np.sqrt(np.mean((E[k] - E["fp64"]) ** 2)))
        raw = float(np.sqrt(np.mean((np.array(S[k]) - np.array(S["fp64"])) ** 2)) / np.mean(np.array(S["fp64"])))
        out[k] = dict(unfolded_rms=d, ratio_to_step=d / step_rms, raw_rel_rms=raw)
    return out


# ---------------------------------------------------------------- planted crossing (M3)
def planted_crossing(times, K=16, d_out=512, d_in=512, t0=1500.0, slope=1e-3, coupling=0.05, s0=5.0, seed=0,
                     static_gap=0.5, noise=0.0):
    """Returns sig (T, K), U, V lists (d, K), and the known answers."""
    rng = np.random.default_rng(seed)
    t = np.asarray(times, float); T = len(t)
    Qu = np.linalg.qr(rng.standard_normal((d_out, K)))[0]; Qv = np.linalg.qr(rng.standard_normal((d_in, K)))[0]
    base = s0 - static_gap * np.arange(2, K) - 1.0          # K-2 static levels below the pair
    sig = np.empty((T, K)); U = []; V = []
    phi = 0.5 * np.arctan2(coupling, slope * (t - t0))
    for k in range(T):
        e = np.sqrt((slope * (t[k] - t0)) ** 2 + coupling ** 2)
        s = np.concatenate([[s0 + e, s0 - e], base])
        c, s_ = np.cos(phi[k]), np.sin(phi[k])
        u = Qu.copy(); v = Qv.copy()
        u[:, 0] = c * Qu[:, 0] + s_ * Qu[:, 1]; u[:, 1] = -s_ * Qu[:, 0] + c * Qu[:, 1]
        v[:, 0] = c * Qv[:, 0] + s_ * Qv[:, 1]; v[:, 1] = -s_ * Qv[:, 0] + c * Qv[:, 1]
        if noise > 0:
            s = s + noise * rng.standard_normal(K)
        order = np.argsort(-s)
        sig[k] = s[order]; U.append(u[:, order]); V.append(v[:, order])
    truth = dict(t_min=t0, g_min=2 * coupling, phi=phi, times=t)
    return sig, U, V, truth


def expected_rotation(truth, k):
    """Rotation of the level-1 vector between checkpoints k-1 and k+1 (degrees)."""
    return float(np.degrees(abs(truth["phi"][k - 1] - truth["phi"][k + 1])))


# ---------------------------------------------------------------- CLI
FAMILIES = ("c1_sym", "c1_rect", "c1_dbm", "c1_ou", "c2_sym", "c2_rect", "c2_poisson")


def make(family, n, m, times, xstep, seed, amp=None, dt_ref=10.0):
    tau = tau_for_xstep(n, xstep, dt_ref); tau2 = tau_for_xstep(n, xstep, dt_ref, beta=2)
    if family == "c1_sym": return smooth_sym(n, times, tau, 1, seed)
    if family == "c2_sym": return smooth_sym(n, times, tau2, 2, seed)
    if family == "c1_rect": return smooth_rect(m, n, times, tau, 1, seed)
    if family == "c2_rect": return smooth_rect(m, n, times, tau2, 2, seed)
    if family == "c1_dbm": return dbm_sym(n, times, xstep, seed, dt_ref=dt_ref)
    if family == "c1_ou": return dbm_sym(n, times, xstep, seed, theta=1.0 / tau, dt_ref=dt_ref)
    if family == "c2_poisson":
        # amplitude so that the walk's x_step matches the GOE family's: v_rms = amp/tau spacings per step
        a = amp if amp is not None else xstep * tau / dt_ref
        return poisson_walk(n, times, tau, a, seed)
    raise ValueError(family)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("family", choices=FAMILIES); ap.add_argument("out")
    ap.add_argument("--n", type=int, default=512); ap.add_argument("--m", type=int, default=2048)
    ap.add_argument("--grid", default="real"); ap.add_argument("--xstep", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--analyse", action="store_true")
    ap.add_argument("--dt-ref", type=float, default=10.0, help="cadence (steps) at which --xstep is defined")
    a = ap.parse_args()
    t0 = time.time(); times = parse_grid(a.grid)
    S = make(a.family, a.n, a.m, times, a.xstep, a.seed, dt_ref=a.dt_ref)
    np.savez_compressed(a.out, spectra=S, times=times, family=a.family, xstep=a.xstep, seed=a.seed, dt_ref=a.dt_ref)
    print(f"{a.family}: spectra {S.shape} tau={tau_for_xstep(a.n, a.xstep, a.dt_ref):.1f} -> {a.out} ({time.time() - t0:.1f}s)")
    if a.analyse:
        res = M2.analyse(S, times); print("\n".join(M2.summary_lines(res)))
