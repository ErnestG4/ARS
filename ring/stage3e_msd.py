"""Stage 3e — mean-squared displacement along the manifold: the passive dual of the kick.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3e_msd_measured.json.
Pre-registration: RING_BRIEF.md "Stage 3e" (3ad1651). verify_ring.py R17 scores.

Noise is an endogenous kick train. Three systems with the same input noise:
  continuum  ring eps=0,  gamma=0.02  -> zero mode integrates noise: MSD ~ 2 D t
  trapped    ring eps=0.1, gamma=0     -> confined by the well: MSD saturates ~ 2D/|lambda1|
  IND_u      independent first-order units (tau_u=1) on the noiseless trajectory
             omega t, same input noise per unit -> no integration: saturates at readout var
Decoded angle = order-parameter angle of the rate vector (passive, noise-free
decoding; the spike-level version is a power question, after). Mean drift is
removed by a linear fit before MSD.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import json
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import coupling, heterogeneity, bump_init, gain, order_parameter, BETA   # noqa: E402
from ring.stage3b_recurrence import rotate                                                # noqa: E402
from ring import stage3_lift as S3                                                        # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                                    # noqa: E402

INSTRUMENT = Model("ring_msd_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("sigma_n", DECLARED, value=0.05, why="input noise per unit, as L4/L4b"),
    Param("gamma_cont", DECLARED, value=0.02, why="continuum drive (omega = gamma)"),
    Param("eps_trap", DECLARED, value=0.1, why="trapped ring pinning; lambda1 median -1.49e-2 (Stage 1)"),
    Param("tau_u", DECLARED, value=1.0, why="IND_u unit time constant"),
    Param("T_relax", DECLARED, value=2000.0, why="settle before recording"),
    Param("T_rec", DECLARED, value=20000.0, why="recording; lags to 2000 tau need >> that"),
    Param("sample_every", DECLARED, value=1.0, why="angle sample interval, tau"),
    Param("lags", DECLARED, value="logspace(0, log10(2000), 40) tau", why="MSD lag grid"),
    Param("seed", TESTED, sweep=[51, 52, 53], why="noise realisations"),
    Param("system", TESTED, sweep=["continuum", "trapped", "IND_u"], why="the three signatures in kind"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
W_EVEN = coupling(N, P["J0"].value, P["J1"].value)
W_ODD = P["J1"].value * np.sin(TH[:, None] - TH[None, :]) / N
XI = heterogeneity(N, 1)
I0 = P["I0"].value
LAGS = np.unique(np.round(np.logspace(0, np.log10(2000), 40)).astype(int))


def record_ring(eps, gamma, rng):
    W = W_EVEN + gamma * W_ODD
    h = eps * XI
    r = bump_init(N, np.array([0.37]))[0]
    for _ in range(int(round(P["T_relax"].value / dt))):
        r = r + dt * (-r + gain(r @ W.T + I0 + h))
    n = int(round(P["T_rec"].value / dt)); every = int(round(P["sample_every"].value / dt))
    sn = P["sigma_n"].value / np.sqrt(dt)
    psi = []
    for k in range(n):
        r = r + dt * (-r + gain(r @ W.T + I0 + h + sn * rng.standard_normal(N)))
        if k % every == 0:
            psi.append(order_parameter(r[None, :])[1][0])
    return np.unwrap(np.array(psi))


def record_ind(rng, prof, psi0):
    g, tau_u = P["gamma_cont"].value, P["tau_u"].value
    r = rotate(prof, 0.37 - psi0)
    n_relax = int(round(P["T_relax"].value / dt))
    n = int(round(P["T_rec"].value / dt)); every = int(round(P["sample_every"].value / dt))
    sn = P["sigma_n"].value / np.sqrt(dt)
    psi = []
    for k in range(n_relax + n):
        tgt = rotate(prof, 0.37 + g * k * dt - psi0)
        r = r + dt * (-r + tgt + sn * rng.standard_normal(N)) / tau_u
        if k >= n_relax and (k - n_relax) % every == 0:
            psi.append(order_parameter(r[None, :])[1][0])
    return np.unwrap(np.array(psi))


def msd(psi):
    t = np.arange(len(psi)) * P["sample_every"].value
    slope, icpt = np.polyfit(t, psi, 1)
    x = psi - (slope * t + icpt)
    out = []
    for L in LAGS:
        d = x[L:] - x[:-L]
        out.append(float((d ** 2).mean()))
    return np.array(out), float(slope)


def at(m, L):
    """MSD at the grid lag nearest L (the grid is rounded log-spaced)"""
    return float(m[int(np.argmin(np.abs(LAGS - L)))])


def slope_between(lag_lo, lag_hi, m):
    sel = (LAGS >= lag_lo) & (LAGS <= lag_hi)
    return float(np.polyfit(np.log(LAGS[sel]), np.log(np.maximum(m[sel], 1e-300)), 1)[0])


def main():
    t0 = time.time()
    prof, psi0 = S3.bump_profile()
    rows = []
    for seed in P["seed"].sweep:
        for system in P["system"].sweep:
            rng = np.random.default_rng(seed + {"continuum": 0, "trapped": 100, "IND_u": 200}[system])
            if system == "continuum":
                psi = record_ring(0.0, P["gamma_cont"].value, rng)
            elif system == "trapped":
                psi = record_ring(P["eps_trap"].value, 0.0, rng)
            else:
                psi = record_ind(rng, prof, psi0)
            m, drift = msd(psi)
            row = dict(system=system, seed=seed, drift=drift, lags=[int(v) for v in LAGS], msd=[float(v) for v in m],
                       slope_10_1000=slope_between(10, 1000, m), slope_200_2000=slope_between(200, 2000, m),
                       ratio_1000_100=at(m, 1000) / at(m, 100), ratio_1000_10=at(m, 1000) / at(m, 10),
                       msd_2000=float(m[-1]), msd_10=at(m, 10),
                       lag_nearest={"10": int(LAGS[np.argmin(np.abs(LAGS - 10))]), "100": int(LAGS[np.argmin(np.abs(LAGS - 100))]),
                                    "1000": int(LAGS[np.argmin(np.abs(LAGS - 1000))])})
            if system == "continuum":
                sel = (LAGS >= 10) & (LAGS <= 1000)
                row["D"] = float(np.mean(m[sel] / (2 * LAGS[sel])))
            if system == "trapped":
                sat = float(np.mean(m[LAGS >= 1000]))
                half = sat / 2
                idx = int(np.argmax(m >= half))
                row["msd_sat"] = sat; row["crossover_lag"] = int(LAGS[idx])
            rows.append(row)
            print(f"{system:<10} seed={seed}: slope[10,1000]={row['slope_10_1000']:.2f} slope[200,2000]={row['slope_200_2000']:.2f} "
                  f"MSD(10)={row['msd_10']:.2e} MSD(2000)={row['msd_2000']:.2e} r1000/100={row['ratio_1000_100']:.2f} "
                  + (f"D={row['D']:.2e}" if system == "continuum" else "")
                  + (f"sat={row['msd_sat']:.2e} crossover={row['crossover_lag']}" if system == "trapped" else ""))
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               lambda1_ref=-1.49e-2, wall_s=round(time.time() - t0, 1))
    with open(os.path.join(HERE, "stage3e_msd_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote stage3e_msd_measured.json ({out['wall_s']}s)")


if __name__ == "__main__":
    main()
