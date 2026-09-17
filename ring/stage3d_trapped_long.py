"""I1c — eps = 0.03 retention at a long window, cross-checked against Stage 4b's tongue edge.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3d_trapped_long_measured.json.
Pre-registration: RING_BRIEF.md "I1c" (58f20c9). verify_ring.py R13c scores.
Same as stage3c_trapped at eps = 0.03 with T_obs = 3000 tau.
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

INSTRUMENT = Model("ring_trapped_long_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("eps", DECLARED, value=0.03, why="the pinning strength I1b could not resolve at 300 tau"),
    Param("delta_kick", DECLARED, value=0.3, why="as stage3b"),
    Param("T_obs", DECLARED, value=3000.0, why="10x I1b; resolves lambda_eff ~ 1e-3"),
    Param("T_relax", DECLARED, value=8000.0, why="as stage3c"),
    Param("gamma", TESTED, sweep=[0.0, 0.001, 0.003, 0.01, 0.02], why="drive; crossing sealed between 0.001 and 0.003"),
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
    eps = P["eps"].value
    n_obs = int(round(P["T_obs"].value / dt))
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
        rows.append(dict(eps=eps, gamma=g, retention=ret, dpsi_trace=dpsi[::30]))
        print(f"eps={eps} gamma={g:<6} retention={ret:+.3f}")
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               wall_s=round(time.time() - t0, 1))
    with open(os.path.join(HERE, "stage3d_trapped_long_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
