"""M2b — the staircase test re-posed at tolerances where the rival (rigid rotation) fails it.

GENERATOR. Sealed before its output (sealgen.sh). Output: stage4c_staircase_measured.json.
Pre-registration: RING_BRIEF.md "M2b" (56f6856). verify_ring.py R14b scores.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import json
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.stage4_circlemap import iterate, farey, nearest_dist, euler_phi_sum     # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED                            # noqa: E402

INSTRUMENT = Model("circlemap_staircase_v1", [
    Param("n_omega", DECLARED, value=1001, why="as stage4"),
    Param("theta0", DECLARED, value=0.37, why="as stage4"),
    Param("N_trans", DECLARED, value=1000, why="as stage4"),
    Param("N_rho", DECLARED, value=100000, why="rho horizon; Denjoy bound 1e-5 on rho_N for K<=1"),
    Param("Q", DECLARED, value=50, why="max denominator"),
    Param("K", TESTED, sweep=[0.0, 0.5, 1.0], why="rival (rigid rotation), intermediate, complete staircase"),
    Param("tol", TESTED, sweep=[1e-3, 1e-4, 1e-5], why="the tolerance that made M2 non-discriminating"),
])
P = {p.name: p for p in INSTRUMENT.params}


def main():
    t0 = time.time()
    Om = np.linspace(0, 1, P["n_omega"].value, endpoint=False)
    K = np.array(P["K"].sweep)
    OM, KK = np.meshgrid(Om, K)
    phi = np.full_like(OM, P["theta0"].value); w = np.zeros(OM.shape, dtype=np.int64)
    phi, w = iterate(phi, w, OM, KK, P["N_trans"].value)
    phi0, w0 = phi.copy(), w.copy()
    phi, w = iterate(phi, w, OM, KK, P["N_rho"].value)
    rho = ((w - w0) + (phi - phi0)) / P["N_rho"].value
    fr = farey(P["Q"].value)
    d = nearest_dist(rho, fr)                                   # (nK, nOm)
    cov = {}
    for tol in P["tol"].sweep:
        cov[f"{tol:g}"] = {f"{k:g}": float((d[i] < tol).mean()) for i, k in enumerate(P["K"].sweep)}
        far = 2 * tol * euler_phi_sum(P["Q"].value)
        cov[f"{tol:g}"]["farey_K0"] = min(1.0, far)
        print(f"tol={tol:g}: coverage per K = {cov[f'{tol:g}']}")
    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(), coverage=cov,
               wall_s=round(time.time() - t0, 1))
    with open(os.path.join(HERE, "stage4c_staircase_measured.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote stage4c_staircase_measured.json ({out['wall_s']}s)")


if __name__ == "__main__":
    main()
