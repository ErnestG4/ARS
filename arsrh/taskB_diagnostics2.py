"""
Task B POST-SEAL DIAGNOSTICS, round 2. NOT sealed tests.

  D4. Mechanism of the additive Sigma^2 artifact: measure the fitted unfold's misfit against the
      exact smooth counting, and check excess ~ 2*Var[misfit] (same saturation logic as D1).
  D5. B.3 completion: the curvature-matched GUE / Poisson BAND through the theta path at low gamma,
      with a realization sd -- the bracket Phase 3's theta-exact column never had.
  D2'. Where the fitted-unfold artifact lives in alpha, with adequate smoothing and reaching below
      alpha = 0.004 (round 1's smoothing was too narrow to read).
"""
from __future__ import annotations
import json, math, os
import numpy as np
from taskB_falpha import (rvm_N, exact_N, unfold_poly, sigma2, form_factor, curved,
                          gue_analytic, Ls, N, HERE, ROOT)

p = lambda *a: print(*a, flush=True)
OUT = {"note": "POST-SEAL diagnostics round 2, not sealed tests"}
z6 = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
blk = z6[:N]

# ---------------------------------------------------------------- D4 misfit -> additive excess
p("[D4] fitted-unfold misfit against the EXACT smooth counting, and the additive excess it predicts")
Nex = exact_N(blk)
rows = {}
for order in (3, 5, 9, 13):
    y = unfold_poly(blk, order)
    mis = y - Nex
    mis = mis - mis.mean()
    v = float(np.var(mis))
    rows[str(order)] = {"misfit_sd": float(np.sqrt(v)), "misfit_var": v, "predicted_excess_2var": 2 * v}
    p(f"  poly{order:<3d} misfit sd = {math.sqrt(v):6.3f} levels   Var = {v:6.3f}   "
      f"predicted Sigma^2 excess ~ 2*Var = {2*v:6.3f}")
p(f"  measured excess at L=32 (D3): Poisson +2.92, GUE +2.41, superrigid +2.60, zeta(P3) +2.59")
OUT["D4"] = rows
p("")

# ---------------------------------------------------------------- D5 curvature-matched bracket
p("[D5] curvature-matched BAND through the theta path at low gamma (B.3 completion)")
B = 20
band = {}
for kind in ("GUE", "Poisson"):
    vals = np.array([sigma2(rvm_N(curved(kind, N, float(blk[0]))), Ls) for _ in range(B)])
    band[kind] = {"mean": vals.mean(0).tolist(), "sd": vals.std(0).tolist()}
    p(f"  {kind:8s} mean " + " ".join("%7.4f" % v for v in vals.mean(0)))
    p(f"  {'':8s} sd   " + " ".join("%7.4f" % v for v in vals.std(0)))
s2_zeta = sigma2(rvm_N(blk), Ls)
gm, gs = np.array(band["GUE"]["mean"]), np.array(band["GUE"]["sd"])
dev = (s2_zeta - gm) / gs
p(f"  zeta_theta   " + " ".join("%7.4f" % v for v in s2_zeta))
p(f"  (zeta-GUE)/sd" + " ".join("%7.2f" % v for v in dev) + "   [neg = MORE rigid]")
p(f"  Ls = {list(Ls)}")
OUT["D5"] = {"B": B, "Ls": Ls.tolist(), "band": band, "sigma2_zeta_theta": s2_zeta.tolist(),
             "dev_over_sd_vs_curved_GUE_theta": dev.tolist(),
             "phase3_flat_band_mean": [0.3456296829538385, 0.41575851391815366, 0.48931144192683884,
                                       0.5622656209411105, 0.6346968597416448, 0.7033050622758842]}
p("")

# ---------------------------------------------------------------- D2' artifact location in alpha
p("[D2'] where does the fitted-unfold artifact live in alpha? (curvature-matched GUE, B=10)")
a = np.concatenate([np.arange(0.0010, 0.0200, 0.0005), np.arange(0.020, 0.201, 0.002),
                    np.arange(0.21, 1.001, 0.01)])
acc = {"theta": [], "poly3": [], "poly9": []}
for _ in range(10):
    raw = curved("GUE", N, float(blk[0]))
    acc["theta"].append(form_factor(rvm_N(raw), a))
    acc["poly3"].append(form_factor(unfold_poly(raw, 3), a))
    acc["poly9"].append(form_factor(unfold_poly(raw, 9), a))
M = {k: np.mean(v, 0) for k, v in acc.items()}


def logbin(a, v, edges):
    return np.array([v[(a >= lo) & (a < hi)].mean() for lo, hi in zip(edges[:-1], edges[1:])])


edges = np.array([0.001, 0.002, 0.004, 0.008, 0.016, 0.032, 0.064, 0.128, 0.256, 0.512, 1.0])
ctr = np.sqrt(edges[:-1] * edges[1:])
bt, b3, b9 = (logbin(a, M[k], edges) for k in ("theta", "poly3", "poly9"))
p(f"  {'alpha band':>16s} {'F_theta':>9s} {'F_poly3':>9s} {'F_poly9':>9s} {'GUE ref':>9s} {'p3/theta':>9s}")
for i in range(len(ctr)):
    p(f"  {edges[i]:7.4f}-{edges[i+1]:<7.4f} {bt[i]:>9.4f} {b3[i]:>9.4f} {b9[i]:>9.4f} "
      f"{min(ctr[i],1.0):>9.4f} {b3[i]/bt[i]:>9.2f}")
OUT["D2p"] = {"edges": edges.tolist(), "centers": ctr.tolist(), "F_theta": bt.tolist(),
              "F_poly3": b3.tolist(), "F_poly9": b9.tolist(), "B": 10}

json.dump(OUT, open(os.path.join(HERE, "taskB_diagnostics2_measured.json"), "w"), indent=2)
p("\nwrote taskB_diagnostics2_measured.json")
