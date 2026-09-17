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

GAMMAS = [0.005, 0.02, 0.08, 0.32]
EPSS = [1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
INSTRUMENT = Model("ring_nonnormal_v1", [
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
    Param("t_grid", DECLARED, value="logspace(-1,3,60)", why="G_max search grid, tau"),
    Param("kreiss_grid", DECLARED, value="Re logspace(-4,0.5,30) x Im linspace(-1,1,41)",
          why="declared so the sup is over a stated region"),
    Param("gamma", TESTED, sweep=GAMMAS, why="circulant asymmetry, 64x span"),
    Param("eps", TESTED, sweep=EPSS, why="heterogeneity, 100x span"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
XI = heterogeneity(N, P["seed_xi"].value)
T_GRID = np.logspace(-1, 3, 60)
K_RE, K_IM = np.logspace(-4, 0.5, 30), np.linspace(-1, 1, 41)
# circular central-difference derivative d/dtheta
DTH = (np.roll(np.eye(N), -1, 1) - np.roll(np.eye(N), 1, 1)) / (2 * 2 * np.pi / N)


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


def bump_state(J0, J1, gamma, eps):
    W = coupling(N, J0, J1) + gamma * w_odd(J1)
    h = eps * XI
    r = integrate(bump_init(N, np.array([0.37])), W, P["I0"].value, h, P["T_relax"].value, dt)[0]
    D = dgain(W @ r + P["I0"].value + h)
    return W, r, D


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
    W, r, D = bump_state(J0, J1, 0.0, 0.0)
    Jsym = -np.eye(N) + D[:, None] * W
    rows.append(dict(arm="S0", gamma=0.0, eps=0.0, zero_mode_resid=None, **reads(Jsym)))
    H0, G0 = rows[-1]["henrici"], rows[-1]["gmax"]
    print(f"S0    henrici={H0:.4f} gap={rows[-1]['gap']:+.4f} gmax={G0:.4f} kappa={rows[-1]['kappa']:.4f} "
          f"K={rows[-1]['kreiss']:.4f}")

    # S-gamma: co-moving-frame Jacobian of the traveling bump
    for g in GAMMAS:
        W, r, D = bump_state(J0, J1, g, 0.0)
        Jtw = -np.eye(N) + D[:, None] * W + g * DTH
        r0p = DTH @ r
        zres = float(np.linalg.norm(Jtw @ r0p) / np.linalg.norm(r0p))
        rows.append(dict(arm="Sgamma", gamma=g, eps=0.0, zero_mode_resid=zres, **reads(Jtw)))
        x = rows[-1]
        print(f"Sg    gamma={g:<6} henrici={x['henrici']:.4f} (rel {x['henrici']/H0-1:+.2e}) gap={x['gap']:+.4f} "
              f"gmax={x['gmax']:.4f} zero-mode resid={zres:.1e} |Im|top={x['im_top']:.4f}")

    # S-alpha: random antisymmetric perturbation at matched ||dW||_F
    rng = np.random.default_rng(P["seed_R"].value)
    R = rng.standard_normal((N, N)); R = (R - R.T); R /= np.linalg.norm(R, "fro")
    for g in GAMMAS:
        a = float(np.linalg.norm(g * w_odd(J1), "fro"))
        W = coupling(N, J0, J1) + a * R
        r = integrate(bump_init(N, np.array([0.37])), W, P["I0"].value, 0 * XI, P["T_relax"].value, dt)[0]
        D = dgain(W @ r + P["I0"].value)
        Jr = -np.eye(N) + D[:, None] * W
        from ring.ringnet import gain as _gain
        fp = float(np.abs(-r + _gain(W @ r + P["I0"].value)).max())
        rows.append(dict(arm="Salpha", gamma=g, eps=0.0, dW_frob=a, fixed_point_resid=fp, **reads(Jr)))
        x = rows[-1]
        print(f"Sa    matched gamma={g:<6} |dW|={a:.4f} henrici={x['henrici']:.4f} (rel {x['henrici']/H0-1:+.2e}) "
              f"gap={x['gap']:+.4f} gmax={x['gmax']:.4f} fp_resid={fp:.1e}")

    # S-eps: heterogeneity at gamma = 0
    for e in EPSS:
        W, r, D = bump_state(J0, J1, 0.0, e)
        Je = -np.eye(N) + D[:, None] * W
        from ring.ringnet import gain as _gain
        fp = float(np.abs(-r + _gain(W @ r + P["I0"].value + e * XI)).max())
        rows.append(dict(arm="Seps", gamma=0.0, eps=e, fixed_point_resid=fp, **reads(Je)))
        x = rows[-1]
        print(f"Se    eps={e:<6} henrici={x['henrici']:.4f} (rel {x['henrici']/H0-1:+.2e}) alpha={x['alpha']:+.2e} "
              f"gap={x['gap']:+.4f} gmax={x['gmax']:.4f} (G0 {G0:.4f}) kappa={x['kappa']:.4f} fp_resid={fp:.1e}")

    def loglog_slope(xs, ys):
        xs, ys = np.log(np.asarray(xs)), np.log(np.asarray(ys))
        return float(np.polyfit(xs, ys, 1)[0])

    hg = [x["henrici"] / H0 - 1 for x in rows if x["arm"] == "Sgamma"]
    ha = [x["henrici"] / H0 - 1 for x in rows if x["arm"] == "Salpha"]
    ge = [abs(x["gmax"] - G0) for x in rows if x["arm"] == "Seps"]
    fits = dict(
        exp_henrici_gamma=loglog_slope(GAMMAS, np.abs(hg)) if min(np.abs(hg)) > 0 else None,
        exp_henrici_alpha=loglog_slope(GAMMAS, np.abs(ha)) if min(np.abs(ha)) > 0 else None,
        exp_gmax_eps=loglog_slope(EPSS, ge) if min(ge) > 0 else None,
        rel_henrici_gamma=hg, rel_henrici_alpha=ha,
        ratio_rand_over_circ_largest=(ha[-1] / hg[-1]) if hg[-1] != 0 else None,
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
