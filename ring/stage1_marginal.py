"""Stage 1, measure 1 — marginal stability along the ring, and where the dial kills it.

GENERATOR. Sealed before its output per sealgen.sh: this file is committed
alone, then run, and `stage1_marginal_measured.json` is committed afterwards.

What it measures, per (T, eps) cell, B off-grid bumps in a batch:
  lam1, lam2      — top two real parts of the fixed-point Jacobian spectrum
  relax_rate      — dynamic read of the same mode (displace, integrate, log-ratio)
  n_distinct      — distinct final bump positions (continuum → discrete count)
  drift_median    — how far the bumps slid from where they were put
  resid_max       — is it a fixed point at all (the eigenvalues are only
                    meaningful where this is small)

Two instrument facts this file exists to make visible rather than assume:
  1. The eps = 0 row is the FLOOR, not "zero". Every detector threshold is set
     against it (verify_ring.py), and the nearest confusable is the weakly
     pinned ring one dial step up, not a far-away negative.
  2. "Where the collapse happens" depends on T. So T is swept, both rows are
     banked, and the checker asserts they DIFFER — a checker that only saw
     the long row would have banked a collapse threshold that is a property
     of the integration time.

Also banks a no-bump control (J1 below the bump threshold): a detector for
"marginal mode present" must not fire where there is no bump to be marginal.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")       # LAPACK path-dependence:
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")  # pin BEFORE numpy import
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import run_dial, BETA, RELAX_DELTAS         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED        # noqa: E402

INSTRUMENT = Model("ring_marginal_mode_v2", [   # v2: relax_delta declared + swept
    Param("N", DECLARED, value=128,
          why="ring size; discretisation pinning is exponentially small in N "
              "with a cosine kernel and the eps=0 row measures it directly"),
    Param("J0", DECLARED, value=-2.0, why="global inhibition (Ben-Yishai 1995)"),
    Param("J1", DECLARED, value=4.0,
          why="local excitation above the bump threshold; the no-bump control "
              "sets it to 1.0 to show the detector goes silent"),
    Param("I0", DECLARED, value=1.0, why="uniform drive; untuned by construction"),
    Param("beta", DECLARED, value=BETA,
          why="gain smoothness; threshold-linear was rejected because its "
              "Jacobian is one-sided at the active-set edge (ringnet docstring)"),
    Param("dt", DECLARED, value=0.05, why="Euler step in tau; resid_max is banked "
                                          "so a bad step shows as a non-fixed-point"),
    Param("B", DECLARED, value=16, why="bumps per batch, off-grid starts"),
    Param("seed", DECLARED, value=1, why="the fixed heterogeneity pattern xi"),
    Param("relax_delta", DECLARED, value=RELAX_DELTAS[0],
          why="displacement for the dynamic read; the banked value is the "
              "smallest of the sweep because the read converges to lam1 as "
              "delta -> 0 (ratio 0.965 at 0.005 vs 0.61 at 0.05, the original "
              "hard-coded value, which was one grid step)"),
    Param("relax_delta_sweep", TESTED, sweep=list(RELAX_DELTAS),
          why="the dynamic read's own instrument constant; swept so its "
              "anharmonic bias is visible in every banked row"),
    Param("eps", TESTED, sweep=[0.0, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1],
          why="the dial: per-unit fixed input bias eps*xi_i"),
    Param("T", TESTED, sweep=[200.0, 2000.0],
          why="integration time; collapse depth is T-dependent and both rows "
              "are banked so the checker can assert that"),
])


def main():
    t0 = time.time()
    P = {p.name: p for p in INSTRUMENT.params}
    rows = []
    for T in P["T"].sweep:
        for eps in P["eps"].sweep:
            d = run_dial(N=P["N"].value, J0=P["J0"].value, J1=P["J1"].value,
                         I0=P["I0"].value, eps=eps, T=T, B=P["B"].value,
                         seed=P["seed"].value, dt=P["dt"].value)
            d["control"] = "bump"
            rows.append(d)
            print(f"T={T:<6g} eps={eps:<6g} amp={d['bump_amp_median']:.3f} "
                  f"resid={d['resid_max']:.1e} lam1={d['lam1_median']:+.2e} "
                  f"relax={d['relax_rate_median']:+.2e} ndist={d['n_distinct']:2d}")
    # no-bump control: J1 below threshold, eps = 0
    for T in P["T"].sweep:
        d = run_dial(N=P["N"].value, J0=P["J0"].value, J1=1.0, I0=P["I0"].value,
                     eps=0.0, T=T, B=P["B"].value, seed=P["seed"].value,
                     dt=P["dt"].value)
        d["control"] = "no_bump_J1=1.0"
        rows.append(d)
        print(f"T={T:<6g} NO-BUMP amp={d['bump_amp_median']:.3f} "
              f"lam1={d['lam1_median']:+.2e}")

    out = dict(
        generator=os.path.basename(__file__),
        instrument=INSTRUMENT.seal(),
        rows=rows,
        wall_s=round(time.time() - t0, 1),
        numpy=np.__version__,
    )
    path = os.path.join(HERE, "stage1_marginal_measured.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path} ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
