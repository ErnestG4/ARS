"""I1b — the trapped discrete attractor under the along-manifold kick; retention vs drive.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3c_trapped_measured.json.
Pre-registration: RING_BRIEF.md "I1b" (overnight 2026-09-17). verify_ring.py R13b scores.
Same kick as Stage 3b I1 (delta = 0.3 rad, T_obs = 300 tau), pinned ring at
eps in {0.03, 0.1}, drive gamma in {0, 0.001, 0.003, 0.01, 0.02}. Retention
R(gamma) = dpsi(300)/delta: restoring when trapped, retaining when sliding.
The depinning crossing is reported as an INTERVAL between grid points (B-sup).
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
from ring.ringnet import coupling, heterogeneity, bump_init, order_parameter, BETA        # noqa: E402
from ring.stage3b_recurrence import rotate, step_ring                                    # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                                    # noqa: E402

INSTRUMENT = Model("ring_trapped_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("delta_kick", DECLARED, value=0.3, why="as stage3b"),
    Param("T_obs", DECLARED, value=300.0, why="as stage3b; marginal at eps=0.03 (stated)"),
    Param("T_relax", DECLARED, value=8000.0, why="settle into a well (or onto the sliding orbit) first"),
    Param("gamma", TESTED, sweep=[0.0, 0.001, 0.003, 0.01, 0.02], why="drive; depinning curve"),
    Param("eps", TESTED, sweep=[0.03, 0.1], why="pinning strength"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
TH = 2 * np.pi * np.arange(N) / N
W_EVEN = coupling(N, P["J0"].value, P["J1"].value)
W_ODD = P["J1"].value * np.sin(TH[:, None] - TH[None, :]) / N
XI = heterogeneity(N, 1)


def main():
    t0 = time.time()
    rows = []
    n_obs = int(round(P["T_obs"].value / dt))
    for eps in P["eps"].sweep:
        for g in P["gamma"].sweep:
            W = W_EVEN + g * W_ODD
            h = eps * XI
            r = bump_init(N, np.array([0.37]))[0]
            for _ in range(int(round(P["T_relax"].value / dt))):
                r = step_ring(r, W, h)
            r_ref, r_k = r.copy(), rotate(r, P["delta_kick"].value)
            dpsi = []
            for k in range(n_obs):
                r_ref = step_ring(r_ref, W, h)
                r_k = step_ring(r_k, W, h)
                if k % 20 == 0:
                    _, p1 = order_parameter(r_ref[None, :])
                    _, p2 = order_parameter(r_k[None, :])
                    dpsi.append(float(np.angle(np.exp(1j * (p2[0] - p1[0])))))
            ret = dpsi[-1] / P["delta_kick"].value
            rows.append(dict(eps=eps, gamma=g, retention=ret, dpsi_0=dpsi[0], dpsi_trace=dpsi[::10]))
            print(f"eps={eps:<5} gamma={g:<6} retention={ret:+.3f}")
    cross = {}
    for eps in P["eps"].sweep:
        rr = [(x["gamma"], x["retention"]) for x in rows if x["eps"] == eps]
        below = [gm for gm, rt in rr if rt < 0.5]
        above = [gm for gm, rt in rr if rt >= 0.5]
        cross[str(eps)] = dict(last_below=max(below) if below else None, first_above=min(above) if above else None)
    print("depinning interval per eps:", cross)
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               depinning=cross, wall_s=round(time.time() - t0, 1))
    with open(os.path.join(HERE, "stage3c_trapped_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
