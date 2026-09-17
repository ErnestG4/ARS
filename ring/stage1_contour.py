"""Stage 1, measure 1 addendum — is collapse a function of eps*T, and what is c?

GENERATOR. Sealed before its output (sealgen.sh). Output: stage1_contour_measured.json.

The first table showed drift ~ linear in eps*T at small eps and a collapse depth
that depends on T. This file tests the sharp form of that claim and fits it:

  CONTOUR CLAIM: the state of the ring after integration depends on eps and T
  only through the product P = eps*T — drift(P) in the linear regime,
  n_distinct(P) in the collapse regime — regardless of how P is split.

Design: a product grid P in {0.02, 0.2, 2, 20, 60, 200}, each realised by
three different (eps, T) splits with T in {200, 600, 2000}. If the contour
claim holds, the three rows at one P agree; if eps enters other than through
P (e.g. large-eps bump deformation), they disagree, and the disagreement is
the finding. TOLERANCES ARE DECLARED HERE, BEFORE THE RUN, so the check in
verify_ring.py can fail:
  LINEAR_P_MAX   = 2.0    products at or below this are 'linear regime'
  DRIFT_AGREE    = 0.20   max relative spread of drift across splits, linear regime
  FIT_RESID      = 0.20   max relative residual of drift = c*P on linear-regime rows
  NDIST_AGREE    = 2      max spread of n_distinct across splits, P >= 20
The fit c is the Stage 6 baseline c(g=1).

Second job: give R4 (spectral vs dynamic standing invariant) more than one
live witness. Long-T rows at eps in {0.01, 0.03, 0.1} with T=8000, and
eps=0.01 at T=20000, are added so more rows above the floor are CONVERGED.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from ring.ringnet import run_dial, BETA                       # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED        # noqa: E402

# pre-declared check tolerances (read by verify_ring.py from the banked seal)
TOL = dict(LINEAR_P_MAX=2.0, DRIFT_AGREE=0.20, FIT_RESID=0.20, NDIST_AGREE=2)

PRODUCTS = [0.02, 0.2, 2.0, 20.0, 60.0, 200.0]
SPLIT_T = [200.0, 600.0, 2000.0]
LONG_ROWS = [(0.01, 8000.0), (0.03, 8000.0), (0.1, 8000.0), (0.01, 20000.0)]

INSTRUMENT = Model("ring_contour_v1", [
    Param("N", DECLARED, value=128, why="as stage1_marginal"),
    Param("J0", DECLARED, value=-2.0, why="as stage1_marginal"),
    Param("J1", DECLARED, value=4.0, why="as stage1_marginal"),
    Param("I0", DECLARED, value=1.0, why="as stage1_marginal"),
    Param("beta", DECLARED, value=BETA, why="as stage1_marginal"),
    Param("dt", DECLARED, value=0.05, why="as stage1_marginal"),
    Param("B", DECLARED, value=16, why="as stage1_marginal"),
    Param("seed", DECLARED, value=1, why="same xi pattern as stage1_marginal so "
                                         "the two tables are the same network"),
    Param("P", TESTED, sweep=PRODUCTS,
          why="the contour coordinate eps*T; the claim under test is that "
              "state depends on eps and T only through it"),
    Param("T_split", TESTED, sweep=SPLIT_T,
          why="how each P is split into (eps, T); agreement across splits IS "
              "the contour test"),
])


def main():
    t0 = time.time()
    P = {p.name: p for p in INSTRUMENT.params}
    kw = dict(N=P["N"].value, J0=P["J0"].value, J1=P["J1"].value, I0=P["I0"].value,
              B=P["B"].value, seed=P["seed"].value, dt=P["dt"].value)
    rows = []
    for prod in PRODUCTS:
        for T in SPLIT_T:
            eps = prod / T
            d = run_dial(eps=eps, T=T, **kw)
            d.update(product=float(prod), kind="split")
            rows.append(d)
            print(f"P={prod:<5g} T={T:<5g} eps={eps:<9.3g} amp={d['bump_amp_median']:.3f} "
                  f"drift={d['drift_median']:.3e} ndist={d['n_distinct']:2d} "
                  f"resid={d['resid_max']:.1e} lam1={d['lam1_median']:+.2e} "
                  f"relax={d['relax_rate_median']:+.2e}")
    for eps, T in LONG_ROWS:
        d = run_dial(eps=eps, T=T, **kw)
        d.update(product=float(eps * T), kind="long")
        rows.append(d)
        print(f"LONG eps={eps:<5g} T={T:<6g} resid={d['resid_max']:.1e} "
              f"lam1={d['lam1_median']:+.2e} relax={d['relax_rate_median']:+.2e} "
              f"ndist={d['n_distinct']:2d}")

    # fit drift = c * P on linear-regime split rows (declared regime, no peeking)
    lin = [r for r in rows if r["kind"] == "split" and r["product"] <= TOL["LINEAR_P_MAX"]]
    x = np.array([r["product"] for r in lin]); y = np.array([r["drift_median"] for r in lin])
    c = float((x * y).sum() / (x * x).sum())                  # through-origin LS
    resid_rel = float(np.max(np.abs(y - c * x) / np.maximum(y, 1e-300)))
    fit = dict(c=c, n_rows=len(lin), max_rel_resid=resid_rel,
               form="drift_median = c * eps * T, through origin, rows with P <= LINEAR_P_MAX")
    print(f"fit: c = {c:.4e} rad/tau per unit eps, max rel resid {resid_rel:.3f} on {len(lin)} rows")

    out = dict(generator=os.path.basename(__file__), instrument=INSTRUMENT.seal(),
               tolerances=TOL, products=PRODUCTS, split_T=SPLIT_T, long_rows=LONG_ROWS,
               rows=rows, fit=fit, wall_s=round(time.time() - t0, 1), numpy=np.__version__)
    path = os.path.join(HERE, "stage1_contour_measured.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {path} ({len(rows)} rows, {out['wall_s']}s)")


if __name__ == "__main__":
    main()
