"""Stage 2 — non-normality of the ring attractor's linearisation, with its rails.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage2_nonnormal_measured.json.
Pre-registration: RING_BRIEF.md "Stage 2 — non-normality" (aacad2f): H_plan vs
H_gain on EXPONENTS over a 64x span in gamma, matched-norm random asymmetry,
100x span in eps, theorem rails on a linear circulant. verify_ring.py R11 scores.

Per row: Henrici index (strictly-upper Schur part, Frobenius), spectral
abscissa alpha, numerical abscissa omega, G_max = sup_t ||e^{Jt}||_2, the top
eigenvalue's condition number kappa, the Kreiss constant K on a declared grid.
For gamma > 0 the bump travels; the linearisation is taken in the co-moving
frame, J_tw = -I + D W + gamma * d/dtheta, whose translation zero mode r0' is
asserted as a rail (the instrument can be wrong; the rail is how it says so).

V2 (2026-09-17). v1's rails were red three ways, all instrument, all fixed here:
  * G_max and Kreiss read their GRIDS, not the matrix (0.951 and 0.864 on a
    normal rail): the t-grid excluded t -> 0 and the z-grid stopped at Re z = 3.
    v2 includes t = 0 (||e^0|| = 1) and extends Re z to 1e3.
  * The central-difference d/dtheta left a zero-mode residual ~ 4*gamma: the
    softplus gain (beta = 0.1) makes the bump edge one grid point wide. v2 uses
    the spectral (FFT) derivative: residual 8.8e-6 / 1.3e-4 / 1.7e-3 / 1.5e-2 at
    gamma = 0.005 / 0.02 / 0.08 / 0.32. The rail (< 1e-2) still fails at 0.32;
    that row is banked INSTRUMENT-LIMITED and not read.
  * Three S-eps rows were linearised at non-fixed-points (T = 2000 where
    eps = 0.01 needs 20000 -- Stage 1's own lesson). v2 Newton-polishes every
    fixed point to |F| < 1e-11 and asserts it.
  * Every row carries an ERROR BOUND on its Henrici change: a relative
    perturbation rho of J moves Henrici by <= rho*||J||_F, i.e. ~5.5*rho of H0.
    A change is RESOLVED only if it exceeds 3x its bound; otherwise the row
    says "unresolved", which is the honest reading of v1's S-gamma column.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np
from scipy.linalg import schur, expm, svdvals

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import coupling, heterogeneity, bump_init, integrate, dgain, BETA   # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                              # noqa: E402

ZERO_MODE_RAIL = 1e-2     # relative residual of J_tw r0'; rows above it are INSTRUMENT-LIMITED
FP_RAIL = 1e-11           # max |F| after Newton polish
RESOLVE = 3.0             # a change counts only if > RESOLVE x its error bound
GAMMAS = [0.005, 0.02, 0.08, 0.32]
EPSS = [1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
INSTRUMENT = Model("ring_nonnormal_v2", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("J1_rail", DECLARED, value=1.0, why="linear circulant rail: below the bump "
                                             "threshold so -I + W is stable (abscissa -0.5)"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("T_relax", DECLARED, value=2000.0, why="converge the bump before linearising"),
    Param("seed_xi", DECLARED, value=1, why="same heterogeneity pattern"),
    Param("seed_R", DECLARED, value=5, why="the random antisymmetric perturbation pattern"),
    Param("t_grid", DECLARED, value="{0} + logspace(-3,3,80)",
          why="G_max search grid, tau; includes t=0 so a normal stable matrix reads exactly 1"),
    Param("kreiss_grid", DECLARED, value="Re logspace(-4,3,40) x Im linspace(-1,1,41)",
          why="declared so the sup is over a stated region; Re z to 1e3 so a normal "
              "matrix reads 1 within 1e-3"),
    Param("derivative", DECLARED, value="spectral (FFT)",
          why="central differences left a zero-mode residual ~4*gamma at a one-grid-point bump edge"),
    Param("zero_mode_rail", DECLARED, value=ZERO_MODE_RAIL, why="J_tw r0' relative residual ceiling"),
    Param("fp_rail", DECLARED, value=FP_RAIL, why="Newton-polished fixed-point residual ceiling"),
    Param("resolve", DECLARED, value=RESOLVE, why="a Henrici change is read only above this "
                                                 "multiple of its error bound 5.5*rho"),
    Param("gamma", TESTED, sweep=GAMMAS, why="circulant asymmetry, 64x span"),
    Param("eps", TESTED, sweep=EPSS, why="heterogeneity, 100x span"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
XI = heterogeneity(N, P["seed_xi"].value)
T_GRID = np.concatenate([[0.0], np.logspace(-3, 3, 80)])
K_RE, K_IM = np.logspace(-4, 3, 40), np.linspace(-1, 1, 41)
# spectral (FFT) derivative d/dtheta on the periodic grid
_k = np.fft.fftfreq(N, d=1.0 / N)
DTH = np.real(np.fft.ifft(1j * _k[:, None] * np.fft.fft(np.eye(N), axis=0), axis=0))


def w_odd(J1):
    return J1 * np.sin(TH[:, None] - TH[None, :]) / N


def reads(J, marginal_hint=False):
    T, _ = schur(J, output="complex")
    hen = float(np.linalg.norm(np.triu(T, 1), "fro"))
    lam, V = np.linalg.eig(J)
    i = int(np.argmax(lam.real))
    alpha = float(lam.real.max())
    omega = float(np.linalg.eigvalsh((J + J.T) / 2).max())
    # eigenvalue condition number of the top eigenvalue: 1/|<left,right>|
    Vinv = np.linalg.inv(V)
    kappa = float(np.linalg.norm(V[:, i]) * np.linalg.norm(Vinv[i, :]))
    gm = float(max(np.linalg.norm(expm(J * t), 2) for t in T_GRID))
    # Kreiss constant on the declared grid: sup Re z * ||(zI - J)^-1||
    K = 0.0
    I = np.eye(N)
    for re in K_RE:
        for im in K_IM:
            z = re + 1j * im
            smin = svdvals(z * I - J)[-1]
            K = max(K, re / max(smin, 1e-300))
    return dict(henrici=hen, frob=float(np.linalg.norm(J, "fro")), alpha=alpha, omega=omega,
                gap=omega - alpha, gmax=gm, kappa=kappa, kreiss=float(K),
                im_top=float(np.sort(np.abs(lam.imag))[-1]))


from ring.ringnet import gain as _gain                                    # noqa: E402


def newton_polish(r, W, h, max_iter=40):
    """Damped Newton on F(r) = -r + f(W r + I0 + h) from the integrated state."""
    I0 = P["I0"].value
    for _ in range(max_iter):
        u = W @ r + I0 + h
        F = -r + _gain(u)
        if np.abs(F).max() < FP_RAIL:
            break
        J = -np.eye(N) + dgain(u)[:, None] * W
        step = np.linalg.solve(J, F)
        lam = 1.0
        while lam > 1e-4:                     # backtracking on |F|
            rn = r - lam * step
            if np.abs(-rn + _gain(W @ rn + I0 + h)).max() < np.abs(F).max():
                break
            lam *= 0.5
        r = rn
    return r, float(np.abs(-r + _gain(W @ r + I0 + h)).max())


def bump_state(J0, J1, gamma, eps, polish=True):
    W = coupling(N, J0, J1) + gamma * w_odd(J1)
    h = eps * XI
    r = integrate(bump_init(N, np.array([0.37])), W, P["I0"].value, h, P["T_relax"].value, dt)[0]
    fp = None
    if polish:
        r, fp = newton_polish(r, W, h)
    D = dgain(W @ r + P["I0"].value + h)
    return W, r, D, fp


def main():
    t0 = time.time()
    rows = []
    J0, J1 = P["J0"].value, P["J1"].value

    # rails: linear stable circulant at every gamma (and gamma = 0)
    for g in [0.0] + GAMMAS:
        A = -np.eye(N) + coupling(N, J0, P["J1_rail"].value) + g * w_odd(P["J1_rail"].value)
        rows.append(dict(arm="rail", gamma=g, eps=0.0, **reads(A)))
        print(f"rail  gamma={g:<6} henrici={rows[-1]['henrici']:.1e} gap={rows[-1]['gap']:+.1e} "
              f"gmax={rows[-1]['gmax']:.6f} K={rows[-1]['kreiss']:.4f}")

    # S0: symmetric bump
    W, r, D, fp = bump_state(J0, J1, 0.0, 0.0)
    Jsym = -np.eye(N) + D[:, None] * W
    rows.append(dict(arm="S0", gamma=0.0, eps=0.0, fixed_point_resid=fp, rail_ok=fp < FP_RAIL,
                     **reads(Jsym)))
    H0, G0 = rows[-1]["henrici"], rows[-1]["gmax"]
    print(f"S0    henrici={H0:.4f} gap={rows[-1]['gap']:+.4f} gmax={G0:.4f} kappa={rows[-1]['kappa']:.4f} "
          f"K={rows[-1]['kreiss']:.4f}")

    # S-gamma: co-moving-frame Jacobian of the traveling bump
    for g in GAMMAS:
        W, r, D, _ = bump_state(J0, J1, g, 0.0, polish=False)   # traveling wave: no fixed point
        Jtw = -np.eye(N) + D[:, None] * W + g * DTH
        r0p = DTH @ r
        zres = float(np.linalg.norm(Jtw @ r0p) / np.linalg.norm(r0p))
        x = reads(Jtw)
        bound = 5.5 * zres                       # relative Henrici error bound
        rel = x["henrici"] / H0 - 1
        rows.append(dict(arm="Sgamma", gamma=g, eps=0.0, zero_mode_resid=zres, rail_ok=zres < ZERO_MODE_RAIL,
                         henrici_rel=rel, henrici_rel_bound=bound,
                         resolved=abs(rel) > RESOLVE * bound, **x))
        print(f"Sg    gamma={g:<6} henrici={x['henrici']:.4f} (rel {rel:+.2e}, bound {bound:.1e}, "
              f"{'RESOLVED' if abs(rel) > RESOLVE * bound else 'unresolved'}) gap={x['gap']:+.4f} "
              f"gmax={x['gmax']:.4f} zero-mode resid={zres:.1e} {'RAIL OK' if zres < ZERO_MODE_RAIL else 'INSTRUMENT-LIMITED'}")

    # S-alpha: random antisymmetric perturbation at matched ||dW||_F
    rng = np.random.default_rng(P["seed_R"].value)
    R = rng.standard_normal((N, N)); R = (R - R.T); R /= np.linalg.norm(R, "fro")
    for g in GAMMAS:
        a = float(np.linalg.norm(g * w_odd(J1), "fro"))
        W = coupling(N, J0, J1) + a * R
        r = integrate(bump_init(N, np.array([0.37])), W, P["I0"].value, 0 * XI, P["T_relax"].value, dt)[0]
        r, fp = newton_polish(r, W, 0 * XI)
        D = dgain(W @ r + P["I0"].value)
        Jr = -np.eye(N) + D[:, None] * W
        x = reads(Jr)
        rel = x["henrici"] / H0 - 1; bound = 5.5 * fp
        rows.append(dict(arm="Salpha", gamma=g, eps=0.0, dW_frob=a, fixed_point_resid=fp, rail_ok=fp < FP_RAIL,
                         henrici_rel=rel, henrici_rel_bound=bound, resolved=abs(rel) > RESOLVE * bound, **x))
        print(f"Sa    matched gamma={g:<6} |dW|={a:.4f} henrici={x['henrici']:.4f} (rel {rel:+.2e}) "
              f"gap={x['gap']:+.4f} gmax={x['gmax']:.4f} fp_resid={fp:.1e}")

    # S-eps: heterogeneity at gamma = 0
    for e in EPSS:
        W, r, D, fp = bump_state(J0, J1, 0.0, e)
        Je = -np.eye(N) + D[:, None] * W
        x = reads(Je)
        rel = x["henrici"] / H0 - 1; bound = 5.5 * fp
        rows.append(dict(arm="Seps", gamma=0.0, eps=e, fixed_point_resid=fp, rail_ok=fp < FP_RAIL,
                         henrici_rel=rel, henrici_rel_bound=bound, resolved=abs(rel) > RESOLVE * bound, **x))
        x = rows[-1]
        print(f"Se    eps={e:<6} henrici={x['henrici']:.4f} (rel {x['henrici']/H0-1:+.2e}) alpha={x['alpha']:+.2e} "
              f"gap={x['gap']:+.4f} gmax={x['gmax']:.4f} (G0 {G0:.4f}) kappa={x['kappa']:.4f} fp_resid={fp:.1e}")

    def loglog_slope(xs, ys):
        xs, ys = np.log(np.asarray(xs)), np.log(np.asarray(ys))
        return float(np.polyfit(xs, ys, 1)[0])

    sg = [x for x in rows if x["arm"] == "Sgamma" and x["rail_ok"]]
    sa = [x for x in rows if x["arm"] == "Salpha" and x["rail_ok"]]
    se = [x for x in rows if x["arm"] == "Seps" and x["rail_ok"]]
    hg = [x["henrici_rel"] for x in sg]; ha = [x["henrici_rel"] for x in sa]
    ge = [abs(x["gmax"] - G0) for x in se]
    fits = dict(
        gammas_read=[x["gamma"] for x in sg],
        exp_henrici_gamma=(loglog_slope([x["gamma"] for x in sg], np.abs(hg))
                           if len(sg) >= 2 and min(np.abs(hg)) > 0 else None),
        n_resolved_gamma=sum(x["resolved"] for x in sg),
        exp_henrici_alpha=(loglog_slope([x["gamma"] for x in sa], np.abs(ha))
                           if len(sa) >= 2 and min(np.abs(ha)) > 0 else None),
        n_resolved_alpha=sum(x["resolved"] for x in sa),
        exp_gmax_eps=loglog_slope([x["eps"] for x in se], ge) if len(se) >= 2 and min(ge) > 0 else None,
        gmax_eps=[x["gmax"] for x in se], eps_read=[x["eps"] for x in se],
        rel_henrici_gamma=hg, rel_henrici_alpha=ha,
        ratio_rand_over_circ_largest_read=((ha[len(hg) - 1] / hg[-1]) if hg and hg[-1] != 0 else None),
    )
    print("fits:", json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in fits.items()}))
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               fits=fits, H0=H0, G0=G0, wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    path = os.path.join(HERE, "stage2_nonnormal_measured.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path} ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
