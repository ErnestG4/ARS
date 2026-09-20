"""Stage 3h — the MSD arm's own well: delta sweep of the restoring rate, two-sided.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage3h_well_delta_measured.json.
Pre-registration: RING_BRIEF.md "Stage 3h" (bf1828e). verify_ring.py R18 scores.

Stage 3e explained lambda_eff = 0.19-0.35 x lambda1 on the trapped ring by well
anharmonicity, citing a 0.32 ratio at 0.1 rad that (once banked) turned out to
belong to the eps=0.01 well; the eps=0.1 rows read 1.016. This measures the
sweep on the MSD arm's EXACT trapped state (eps=0.1, gamma=0, start 0.37 rad,
relax 2000 tau) and on the I1c well (eps=0.03, same start, relax 8000 tau).
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
from ring.ringnet import (coupling, heterogeneity, bump_init, gain, dgain, jacobian, top_eigs,   # noqa: E402
                          relaxation_rate, order_parameter, BETA)
from modelparams import Model, Param, TESTED, DECLARED                                          # noqa: E402

INSTRUMENT = Model("ring_well_delta_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("start", DECLARED, value=0.37, why="the MSD arm's and I1c's start angle, rad"),
    Param("fp_rail", DECLARED, value=1e-9, why="fixed-point residual ceiling at the linearisation point"),
    Param("well", TESTED, sweep=["eps0.1_relax2000", "eps0.03_relax8000"], why="the MSD well; the I1c well"),
    Param("delta", TESTED, sweep=[0.005, 0.01, 0.02, 0.05, 0.1, 0.2], why="displacement, rad"),
    Param("T_relax_read", TESTED, sweep=[50.0, 200.0], why="the dynamic read must not depend on it"),
])
P = {p.name: p for p in INSTRUMENT.params}
N, dt = P["N"].value, P["dt"].value
W = coupling(N, P["J0"].value, P["J1"].value)
XI = heterogeneity(N, 1)
I0 = P["I0"].value
WELLS = {"eps0.1_relax2000": (0.1, 2000.0), "eps0.03_relax8000": (0.03, 8000.0)}


def main():
    t0 = time.time()
    rows = []
    for well in P["well"].sweep:
        eps, T_relax = WELLS[well]
        h = eps * XI
        r = bump_init(N, np.array([P["start"].value]))[0]
        for _ in range(int(round(T_relax / dt))):
            r = r + dt * (-r + gain(r @ W.T + I0 + h))
        fp = float(np.abs(-r + gain(W @ r + I0 + h)).max())
        lam = top_eigs(jacobian(r, W, I0, h))
        _, psi = order_parameter(r[None, :])
        row = dict(well=well, eps=eps, T_relax=T_relax, psi=float(psi[0]), fp_resid=fp, rail_ok=fp < P["fp_rail"].value,
                   lam1=float(lam[0]), lam2=float(lam[1]), ratio={})
        for T in P["T_relax_read"].sweep:
            for d in P["delta"].sweep:
                rr = relaxation_rate(r, W, I0, h, delta=d, T=T, dt=dt)
                row["ratio"][f"T{T:g}_d{d:g}"] = float(rr / (-lam[0]))
        rows.append(row)
        print(f"{well}: fp_resid={fp:.1e} psi={psi[0]:.3f} lam1={lam[0]:+.3e} lam2={lam[1]:+.3f}")
        for T in P["T_relax_read"].sweep:
            print(f"   T={T:g}: ratio by delta = " + " ".join(f"{d:g}:{row['ratio'][f'T{T:g}_d{d:g}']:.3f}" for d in P["delta"].sweep))
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), rows=rows,
               msd_lambda_eff_over_lambda1=[0.19, 0.29, 0.35], wall_s=round(time.time() - t0, 1))
    with open(os.path.join(HERE, "stage3h_well_delta_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote stage3h_well_delta_measured.json ({out['wall_s']}s)")


if __name__ == "__main__":
    main()
