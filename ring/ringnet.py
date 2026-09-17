"""Ring attractor (Ben-Yishai/Bar-Or/Sompolinsky 1995; Zhang 1996), numpy, float64.

    tau dr/dt = -r + f( W r + I0 + h ),   W_ij = (J0 + J1 cos(th_i - th_j)) / N
    f(u) = beta * softplus(u / beta)      (beta -> 0 recovers [u]_+)

Global inhibition J0 < 0, local excitation J1 > 0, SMOOTH gain. Threshold-linear
was tried first and rejected for the instrument, not the model: its Jacobian at
the fixed point is one-sided at the active-set boundary, and the "marginal"
eigenvalue read +1.7e-3 / -3.4e-3 for constants whose bump did not move in 200
tau (drift 1e-15). A spectral read that disagrees with the dynamics by 12 orders
is a defect of the gain's kink, so the gain is smoothed and the eigenvalue is
cross-checked against a DYNAMIC measurement (`relaxation_rate`) that needs no
linearisation. With
J1 large enough a bump forms without tuned input, and — because W commutes with
rotation — the bump's position is a marginal direction: the Jacobian at the
fixed point has ONE eigenvalue at (numerically) zero and the rest strictly
negative. That marginal mode is the object Stage 1 measures, and the
heterogeneity dial `eps` (fixed per-unit input bias eps * xi_i) is what
destroys it: fixed asymmetries pin the bump, the continuum collapses to a few
discrete attractors, and the zero eigenvalue becomes strictly negative.

Two instrument facts the caller must not forget:
  * The DISCRETE ring already pins, exponentially weakly in N. The eps = 0 row
    is therefore the instrument floor, not "zero"; every threshold downstream
    is set relative to it (see `verify_ring.py`).
  * "Where the collapse happens" depends on how long you integrate: slow drift
    under small eps only shows up at long T. So T is a TESTED parameter with a
    sweep, never a single number.

Leading axis is batch everywhere (B initial bump angles integrated together),
per the plan's hardware note. Dense eigvals are LAPACK; the checker pins BLAS
threads (memory: lapack_reproducibility_depends_on_the_path).
"""
from __future__ import annotations

import numpy as np

# ── LITERATURE (same declaration shape as the root guard modules) ─────────────
LITERATURE = dict(
    status="NAMED",
    note="The model and its marginal mode are textbook; nothing here is ours "
         "except the instrument-floor bookkeeping and the dial.",
    anchors=[
        "Ben-Yishai, Bar-Or & Sompolinsky, PNAS 92:3844 (1995) — ring model, "
        "marginal phase, bump without tuned input.",
        "Zhang, J. Neurosci. 16:2112 (1996) — head-direction ring attractor; "
        "asymmetric coupling shifts the bump (Stage 3).",
        "Renart, Song & Wang, Neuron 38:473 (2003) — heterogeneity pins the "
        "bump and fragments the continuum; the dial's known outcome.",
    ],
    ours="Treating the eps = 0 discretisation pinning as the instrument floor "
         "and sizing every collapse threshold against it.",
)


def coupling(N: int, J0: float, J1: float) -> np.ndarray:
    th = 2.0 * np.pi * np.arange(N) / N
    return (J0 + J1 * np.cos(th[:, None] - th[None, :])) / N


def heterogeneity(N: int, seed: int) -> np.ndarray:
    """Fixed unit-variance per-unit bias pattern xi (one draw per seed)."""
    return np.random.default_rng(seed).standard_normal(N)


def bump_init(N: int, angles: np.ndarray, width: float = 0.6, amp: float = 1.0) -> np.ndarray:
    th = 2.0 * np.pi * np.arange(N) / N
    d = np.angle(np.exp(1j * (th[None, :] - angles[:, None])))
    return amp * np.exp(-0.5 * (d / width) ** 2)


BETA = 0.1   # gain sharpness; DECLARED in verify_ring.py's Model


def gain(u: np.ndarray, beta: float = BETA) -> np.ndarray:
    return beta * np.logaddexp(0.0, u / beta)


def dgain(u: np.ndarray, beta: float = BETA) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-u / beta))


def integrate(r0: np.ndarray, W: np.ndarray, I0: float, h: np.ndarray,
              T: float, dt: float = 0.05, tau: float = 1.0) -> np.ndarray:
    """Forward Euler on the rate equation, batch on axis 0. Returns r(T)."""
    r = np.array(r0, dtype=np.float64, copy=True)
    n_steps = int(round(T / dt))
    a = dt / tau
    for _ in range(n_steps):
        u = r @ W.T + I0 + h
        r += a * (-r + gain(u))
    return r


def order_parameter(r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(|Z|, arg Z) for Z = sum r e^{i th} / sum r, batch on axis 0."""
    N = r.shape[-1]
    th = 2.0 * np.pi * np.arange(N) / N
    z = (r * np.exp(1j * th)).sum(-1) / np.maximum(r.sum(-1), 1e-300)
    return np.abs(z), np.angle(z)


def jacobian(r_star: np.ndarray, W: np.ndarray, I0: float, h: np.ndarray,
             tau: float = 1.0) -> np.ndarray:
    """J = (-I + diag[f'(u)] W)/tau at a fixed point r*."""
    u = W @ r_star + I0 + h
    D = dgain(u)
    return (-np.eye(len(r_star)) + D[:, None] * W) / tau


def top_eigs(J: np.ndarray, k: int = 3) -> np.ndarray:
    """Largest k real parts of the spectrum, descending."""
    lam = np.linalg.eigvals(J).real
    return np.sort(lam)[::-1][:k]


def relaxation_rate(r_star: np.ndarray, W: np.ndarray, I0: float, h: np.ndarray,
                    delta: float, T: float, dt: float = 0.05) -> float:
    """Dynamic read of the marginal mode: displace the converged bump by `delta`
    rad, integrate T, return -log(|displacement(T)| / delta) / T. Zero on a true
    continuum (the displaced bump stays put); positive when pinned (it slides
    back); needs no linearisation, so it is the cross-check on `top_eigs`."""
    N = r_star.shape[-1]
    th = 2.0 * np.pi * np.arange(N) / N
    _, psi0 = order_parameter(r_star[None, :])
    # rotate the bump by delta via periodic resampling on the grid
    src = np.mod(th - delta, 2 * np.pi)
    r_shift = np.interp(src, th, r_star, period=2 * np.pi)
    r_T = integrate(r_shift[None, :], W, I0, h, T, dt)[0]
    _, psi_T = order_parameter(r_T[None, :])
    disp = float(np.abs(np.angle(np.exp(1j * (psi_T[0] - psi0[0])))))
    disp = max(disp, 1e-300)
    return float(-np.log(disp / abs(delta)) / T)


def n_distinct_positions(psi: np.ndarray, tol: float) -> int:
    """Count distinct final bump angles up to circular tolerance `tol`."""
    psi = np.sort(np.mod(psi, 2 * np.pi))
    if psi.size == 0:
        return 0
    gaps = np.diff(np.concatenate([psi, [psi[0] + 2 * np.pi]]))
    return int(max(1, (gaps > tol).sum()))


def run_dial(N: int, J0: float, J1: float, I0: float, eps: float, T: float,
             B: int, seed: int, dt: float = 0.05) -> dict:
    """One dial setting: B bumps at uniform initial angles → fixed points, eigs, positions."""
    W = coupling(N, J0, J1)
    h = eps * heterogeneity(N, seed)
    # OFF-GRID on purpose: angles that are multiples of 2pi/N sit on exact
    # symmetry points of the discrete ring and never see its pinning. The
    # 0.37 offset (in units of the B-spacing) keeps every start off the grid.
    angles0 = 2 * np.pi * (np.arange(B) + 0.37) / B
    r = integrate(bump_init(N, angles0), W, I0, h, T, dt)
    amp, psi = order_parameter(r)
    # residual |dr/dt| at the end: are these fixed points at all?
    resid = np.abs(-r + gain(r @ W.T + I0 + h)).max(-1)
    eigs = np.array([top_eigs(jacobian(r[b], W, I0, h)) for b in range(B)])
    relax = np.array([relaxation_rate(r[b], W, I0, h, delta=0.05, T=50.0, dt=dt)
                      for b in range(min(B, 8))])
    return dict(
        eps=float(eps), T=float(T), B=int(B), N=int(N),
        bump_amp_median=float(np.median(amp)),
        resid_max=float(resid.max()),
        lam1_median=float(np.median(eigs[:, 0])),
        lam1_max=float(eigs[:, 0].max()),
        lam2_median=float(np.median(eigs[:, 1])),
        relax_rate_median=float(np.median(relax)),
        n_distinct=n_distinct_positions(psi, tol=1.5 * 2 * np.pi / N),
        drift_median=float(np.median(np.abs(np.angle(np.exp(1j * (psi - angles0)))))),
    )
