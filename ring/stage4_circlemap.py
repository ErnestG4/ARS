"""Stage 4 — sine circle map: rotation number as a limit, residence (re-indexed), hysteresis with its dead region.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage4_circlemap_measured.json.
Pre-registration: RING_BRIEF.md "Stage 4 — circle map" (6d295e3). verify_ring.py R14 scores.

theta_{n+1} = theta_n + Omega - (K / 2 pi) sin(2 pi theta_n), on the lift, float64,
integer winding w carried separately from the residual phi in [0, 1).
M1 rho_N at N in {1e3, 1e4, 1e5} (Denjoy rail for K < 1: |rho_1e4 - rho_1e5| < 1.1e-4).
M2 residence fraction f within eps_tol of the nearest p/q (q <= Q_max) over L = 100
   sub-windows of a 1e4 window; Farey-coverage rail at K = 0.
M3 0/1 tongue boundary Omega_c = K / 2 pi, exact, on the hysteresis grid.
M4 hysteresis: independent init vs adiabatic up/down sweeps; D(K) must be <= one
   grid step for K < 1; multistability fraction (two inits) must be 0 for K < 1.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import json
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from modelparams import Model, Param, TESTED, DECLARED     # noqa: E402

KS = [0.0, 0.25, 0.5, 0.75, 0.9, 1.0, 1.2, 1.5]
INSTRUMENT = Model("circlemap_v1", [
    Param("n_omega", DECLARED, value=1001, why="Omega grid on [0,1) for M1/M2"),
    Param("n_omega_hyst", DECLARED, value=201, why="Omega grid for the sequential sweeps (M3/M4)"),
    Param("theta0", DECLARED, value=0.37, why="independent init; 0.71 is the second init for multistability"),
    Param("theta0_b", DECLARED, value=0.71, why="second init"),
    Param("N_trans", DECLARED, value=1000, why="transient before measuring"),
    Param("N_meas", DECLARED, value=10000, why="M2 window; M4 measurement per Omega step"),
    Param("N_trans_hyst", DECLARED, value=500, why="transient per Omega step in the adiabatic sweep"),
    Param("N_meas_hyst", DECLARED, value=2000, why="measurement per Omega step in the adiabatic sweep"),
    Param("L_sub", DECLARED, value=100, why="sub-window length for the local rotation estimate"),
    Param("rho_lock_tol", DECLARED, value=1e-3, why="|rho| below this = inside the 0/1 tongue (M3/M4)"),
    Param("Q_staircase", DECLARED, value=50, why="max denominator for the K=1 staircase coverage"),
    Param("K", TESTED, sweep=KS, why="nonlinearity; K<1 invertible (Denjoy), K>1 non-invertible"),
    Param("N_rho", TESTED, sweep=[1000, 10000, 100000], why="rotation-number horizon (B-sup limit)"),
    Param("eps_tol", TESTED, sweep=[1e-3, 1e-2], why="residence tolerance"),
    Param("Q_max", TESTED, sweep=[5, 10], why="max denominator for residence"),
])
P = {p.name: p for p in INSTRUMENT.params}


def step(phi, w, Om, K):
    x = phi + Om - (K / (2 * np.pi)) * np.sin(2 * np.pi * phi)
    fl = np.floor(x)
    return x - fl, w + fl.astype(np.int64)


def iterate(phi, w, Om, K, n):
    for _ in range(n):
        phi, w = step(phi, w, Om, K)
    return phi, w


def farey(Q):
    fr = sorted({Fraction(p, q) for q in range(1, Q + 1) for p in range(0, q + 1)})
    return np.array([float(f) for f in fr])


def nearest_dist(r, fr):
    r = np.asarray(r)
    d = np.abs(r[..., None] - fr[None, ...])
    return d.min(-1)


def euler_phi_sum(Q):
    from math import gcd
    return sum(sum(1 for k in range(1, q + 1) if gcd(k, q) == 1) for q in range(1, Q + 1))


def main():
    t0 = time.time()
    Om = np.linspace(0, 1, P["n_omega"].value, endpoint=False)
    K = np.array(KS)
    OM, KK = np.meshgrid(Om, K)                       # (nK, nOm)
    phi = np.full_like(OM, P["theta0"].value); w = np.zeros(OM.shape, dtype=np.int64)
    phi, w = iterate(phi, w, OM, KK, P["N_trans"].value)
    phi0, w0 = phi.copy(), w.copy()
    # M1: rho_N at three horizons, running from the post-transient state
    rho = {}
    n_done = 0
    L = P["L_sub"].value
    local = []                                        # local rotations over the first N_meas
    for N in P["N_rho"].sweep:
        # advance to N, recording sub-window rotations inside the first N_meas
        while n_done < N:
            chunk = min(L, N - n_done)
            phi_prev, w_prev = phi, w
            phi, w = iterate(phi, w, OM, KK, chunk)
            if n_done + chunk <= P["N_meas"].value and chunk == L:
                local.append(((w - w_prev) + (phi - phi_prev)) / L)
            n_done += chunk
        rho[N] = ((w - w0) + (phi - phi0)) / N
    local = np.stack(local, 0)                        # (n_sub, nK, nOm)
    conv = np.abs(rho[10000] - rho[100000])
    print("M1 max |rho_1e4 - rho_1e5| per K:", {k: float(conv[i].max()) for i, k in enumerate(KS)})
    # M2 residence
    res = {}
    farey_cov = {}
    for Q in P["Q_max"].sweep:
        fr = farey(Q)
        d = nearest_dist(local, fr)                   # (n_sub, nK, nOm)
        for et in P["eps_tol"].sweep:
            f = (d < et).mean(0)                      # (nK, nOm)
            frac1 = (f >= 1.0 - 1e-12).mean(1)        # Omega-fraction with f = 1, per K
            res[f"Q{Q}_eps{et:g}"] = dict(frac_f1_per_K=[float(v) for v in frac1],
                                          mean_f_per_K=[float(v) for v in f.mean(1)])
            farey_cov[f"Q{Q}_eps{et:g}"] = 2 * et * euler_phi_sum(Q)
            print(f"M2 Q={Q} eps={et:g}: Omega-fraction f=1 per K = {[round(v, 3) for v in frac1]}  (Farey cov at K=0: {2*et*euler_phi_sum(Q):.3f})")
    # staircase coverage at K = 1
    fr50 = farey(P["Q_staircase"].value)
    iK1 = KS.index(1.0)
    stair = float((nearest_dist(rho[100000][iK1], fr50) < 1e-3).mean())
    stair_K = {k: float((nearest_dist(rho[100000][i], fr50) < 1e-3).mean()) for i, k in enumerate(KS)}
    print(f"M2 staircase coverage (q<=50, 1e-3) per K: {stair_K}")
    # M3/M4: hysteresis grid, three protocols, plus multistability
    Omh = np.linspace(0, 1, P["n_omega_hyst"].value, endpoint=False)
    dOm = Omh[1] - Omh[0]
    Nt, Nm = P["N_trans_hyst"].value, P["N_meas_hyst"].value

    def measure(phi, w, Omv):
        phi, w = iterate(phi, w, Omv, K, Nt)
        phi0_, w0_ = phi.copy(), w.copy()
        phi, w = iterate(phi, w, Omv, K, Nm)
        return phi, w, ((w - w0_) + (phi - phi0_)) / Nm

    rho_ind = np.zeros((len(KS), len(Omh))); rho_ind_b = np.zeros_like(rho_ind)
    rho_up = np.zeros_like(rho_ind); rho_dn = np.zeros_like(rho_ind)
    for j, Omv in enumerate(Omh):
        p_ = np.full(len(KS), P["theta0"].value); w_ = np.zeros(len(KS), dtype=np.int64)
        _, _, rho_ind[:, j] = measure(p_, w_, Omv)
        p_ = np.full(len(KS), P["theta0_b"].value); w_ = np.zeros(len(KS), dtype=np.int64)
        _, _, rho_ind_b[:, j] = measure(p_, w_, Omv)
    p_ = np.full(len(KS), P["theta0"].value); w_ = np.zeros(len(KS), dtype=np.int64)
    for j, Omv in enumerate(Omh):                     # upward, carrying theta
        p_, w_, rho_up[:, j] = measure(p_, w_, Omv)
    p_ = np.full(len(KS), P["theta0"].value); w_ = np.zeros(len(KS), dtype=np.int64)
    for j in range(len(Omh) - 1, -1, -1):             # downward
        p_, w_, rho_dn[:, j] = measure(p_, w_, Omh[j])

    def omega_c(r):
        """largest Omega, scanning up from 0, with |rho| < tol (the 0/1 tongue's right edge)"""
        out = []
        for i in range(len(KS)):
            inside = np.abs(r[i]) < P["rho_lock_tol"].value
            k = 0
            while k < len(Omh) and inside[k]:
                k += 1
            out.append(float(Omh[k - 1]) if k > 0 else None)
        return out

    oc_ind, oc_up, oc_dn = omega_c(rho_ind), omega_c(rho_up), omega_c(rho_dn)
    D = []
    for i in range(len(KS)):
        vals = [v for v in (oc_ind[i], oc_up[i], oc_dn[i]) if v is not None]
        D.append(float(max(vals) - min(vals)) if len(vals) == 3 else None)
    multi = [float((np.abs(rho_ind[i] - rho_ind_b[i]) > 1e-3).mean()) for i in range(len(KS))]
    exact = [k / (2 * np.pi) for k in KS]
    print("M3 Omega_c (ind/up/dn) vs K/2pi:", [(round(a, 4) if a is not None else None, round(b, 4) if b is not None else None,
                                              round(c, 4) if c is not None else None, round(e, 4)) for a, b, c, e in zip(oc_ind, oc_up, oc_dn, exact)])
    print("M4 D(K):", [round(d, 4) if d is not None else None for d in D], "grid step", round(dOm, 4))
    print("M4 multistability fraction per K:", [round(m, 3) for m in multi])

    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), K=KS,
               M1=dict(max_abs_drho_1e4_1e5_per_K=[float(conv[i].max()) for i in range(len(KS))],
                       max_abs_drho_1e3_1e4_per_K=[float(np.abs(rho[1000] - rho[10000])[i].max()) for i in range(len(KS))]),
               M2=dict(residence=res, farey_coverage_K0=farey_cov, staircase_q50_1e3_per_K=stair_K),
               M3=dict(omega_c_ind=oc_ind, omega_c_up=oc_up, omega_c_dn=oc_dn, exact_K_over_2pi=exact, grid_step=float(dOm)),
               M4=dict(D_per_K=D, multistability_frac_per_K=multi),
               rho_1e5_K1=[float(v) for v in rho[100000][iK1]], omega_grid_n=int(len(Om)),
               wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    with open(os.path.join(HERE, "stage4_circlemap_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote stage4_circlemap_measured.json ({out['wall_s']}s)")


if __name__ == "__main__":
    main()
