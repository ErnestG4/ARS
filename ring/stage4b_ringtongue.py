"""Stage 4b — the pinned ring's 0/1 tongue; depinning threshold predicted from the measured pinning velocity.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage4b_ringtongue_measured.json.
Pre-registration: RING_BRIEF.md "Stage 4b" (419e52b). verify_ring.py R15 scores.

Reduced model: theta' = gamma - v_pin(theta). Locks iff gamma < gamma* = max v_pin.
v_pin is measured at gamma = 0 from 64 off-grid bumps (max instantaneous drift
speed, after a short settle). Then rho(gamma) = mean bump velocity / gamma is
measured on a fine gamma grid at eps in {0.03, 0.1}, batched over gamma.
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
from modelparams import Model, Param, TESTED, DECLARED                                    # noqa: E402

GAMMAS = [float(g) for g in np.linspace(0.0, 0.03, 41)]
INSTRUMENT = Model("ring_tongue_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("B_vpin", DECLARED, value=64, why="off-grid starts for the pinning-velocity landscape"),
    Param("T_settle_vpin", DECLARED, value=20.0, why="let the bump shape relax before reading drift speed"),
    Param("T_vpin", DECLARED, value=200.0, why="window over which max drift speed is taken"),
    Param("T_relax", DECLARED, value=2000.0, why="relax before measuring rho"),
    Param("T_meas", DECLARED, value=20000.0, why="rho window; rho near threshold is small"),
    Param("rho_lock_tol", DECLARED, value=1e-2, why="rho below this = locked"),
    Param("gamma", TESTED, sweep=GAMMAS, why="fine drive grid, step 7.5e-4"),
    Param("eps", TESTED, sweep=[0.0, 0.03, 0.1], why="0 is the omega=gamma rail"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
W_EVEN = coupling(N, P["J0"].value, P["J1"].value)
W_ODD = P["J1"].value * np.sin(TH[:, None] - TH[None, :]) / N
XI = heterogeneity(N, 1)
I0 = P["I0"].value


def integrate_batch(r, W_batch, h, T):
    """r: (B, N); W_batch: (B, N, N) or (N, N); Euler with the softplus gain."""
    n = int(round(T / dt))
    if W_batch.ndim == 2:
        for _ in range(n):
            r = r + dt * (-r + gain(r @ W_batch.T + I0 + h))
    else:
        for _ in range(n):
            u = np.einsum("bij,bj->bi", W_batch, r) + I0 + h
            r = r + dt * (-r + gain(u))
    return r


def main():
    t0 = time.time()
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), vpin={}, tongue={})
    # v_pin landscape at gamma = 0
    B = P["B_vpin"].value
    starts = 2 * np.pi * (np.arange(B) + 0.37) / B
    for eps in (0.03, 0.1):
        h = eps * XI
        r = integrate_batch(bump_init(N, starts), W_EVEN, h, P["T_settle_vpin"].value)
        n = int(round(P["T_vpin"].value / dt))
        _, psi_prev = order_parameter(r)
        vmax = np.zeros(B); vsum = np.zeros(B)
        every = 20
        for k in range(1, n + 1):
            r = r + dt * (-r + gain(r @ W_EVEN.T + I0 + h))
            if k % every == 0:
                _, psi = order_parameter(r)
                v = np.abs(np.angle(np.exp(1j * (psi - psi_prev)))) / (every * dt)
                vmax = np.maximum(vmax, v); vsum += v
                psi_prev = psi
        out["vpin"][str(eps)] = dict(max_speed=float(vmax.max()), median_speed=float(np.median(vsum / (n // every))),
                                     per_start_max=[float(v) for v in vmax])
        print(f"v_pin eps={eps}: max speed {vmax.max():.4e} rad/tau (median of per-start mean {np.median(vsum/(n//every)):.4e}; "
              f"c*eps = {2.9048e-2 * eps:.4e})")
    # tongue: rho(gamma) batched over gamma
    G = np.array(GAMMAS)
    W_batch = W_EVEN[None] + G[:, None, None] * W_ODD[None]
    for eps in P["eps"].sweep:
        h = eps * XI
        r = integrate_batch(bump_init(N, np.full(len(G), 0.37)), W_batch, h, P["T_relax"].value)
        _, psi0 = order_parameter(r)
        n = int(round(P["T_meas"].value / dt)); every = 20
        unwrapped = np.zeros(len(G)); psi_prev = psi0.copy()
        for k in range(1, n + 1):
            u = np.einsum("bij,bj->bi", W_batch, r) + I0 + h
            r = r + dt * (-r + gain(u))
            if k % every == 0:
                _, psi = order_parameter(r)
                unwrapped += np.angle(np.exp(1j * (psi - psi_prev)))
                psi_prev = psi
        omega = unwrapped / P["T_meas"].value
        rho = np.where(G > 0, omega / np.where(G > 0, G, 1.0), 0.0)
        locked = rho < P["rho_lock_tol"].value
        first_unlocked = next((float(g) for g, l in zip(G, locked) if g > 0 and not l), None)
        out["tongue"][str(eps)] = dict(gamma=GAMMAS, omega=[float(v) for v in omega], rho=[float(v) for v in rho],
                                       gamma_star_meas=first_unlocked)
        print(f"tongue eps={eps}: gamma*_meas = {first_unlocked}; rho at gamma=0.03 = {rho[-1]:.3f}; "
              f"rho(gamma) = {[round(float(v), 3) for v in rho[::4]]}")
    out["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "stage4b_ringtongue_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote stage4b_ringtongue_measured.json ({out['wall_s']}s)")


if __name__ == "__main__":
    main()
