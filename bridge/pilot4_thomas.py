"""Pilot 4 (pre-seal): G-A3 2-D tolerance under the FINAL gate configuration.

Config (sealed if this pilot supports it): direct Σ²(R) from NON-overlapping
grid disks pooled across 6 seeds (observer_b.disk_counts_grid); identity side
from the seed-averaged ĝ; ONE comparison per R per substrate.
Substrates: 2-D Poisson (area term) + Thomas designed instance (integral term).
"""

import json
import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/bridge")
from observer_b import (RectWindow, pcf_2d, sigma2_from_g_2d, disk_counts_grid)

R_LIST = [2.0, 4.0, 6.0]
bins = np.arange(0.0, 12.5 + 1e-9, 0.1)
out = {}

def run_substrate(tag, sampler, seeds, lam_true):
    # TRUE model intensity throughout: lambda-hat jitter is amplified by
    # (lam*pi*R^2)^2/Var in the identity (the FIX-2 twin at gluing level)
    gs, counts = [], {R: [] for R in R_LIST}
    lams = []
    for s in seeds:
        pts, W = sampler(s)
        lam = lam_true
        lams.append(lam)
        c, g = pcf_2d(pts, W, bins, lam=lam)
        gs.append(g)
        for R in R_LIST:
            counts[R].extend(disk_counts_grid(pts, W, R))
        print(f"  {tag} seed {s}: n={len(pts)}", flush=True)
    g_pool = np.mean(gs, axis=0)
    lam_m = float(np.mean(lams))
    rows = []
    for R in R_LIST:
        cnt = np.array(counts[R])
        direct = float(cnt.var(ddof=1))
        ident = float(sigma2_from_g_2d(c, g_pool, R, lam_m))
        rows.append(dict(R=R, direct=direct, identity=ident,
                         n_ind=len(cnt), rel=abs(ident - direct) / direct))
    out[tag] = dict(rows=rows, relSigma=float(max(r["rel"] for r in rows)))
    print(f"{tag}: relSigma={out[tag]['relSigma']:.4f}", flush=True)

def pois(s):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    n = rng.poisson(W.area())
    return rng.uniform(0, 120.0, size=(n, 2)), W

def thomas(s):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    KAPPA, MU, SIG = 0.05, 20, 1.5
    buf = 5 * SIG
    n_par = rng.poisson(KAPPA * (120 + 2 * buf) ** 2)
    par = rng.uniform(-buf, 120 + buf, size=(n_par, 2))
    n_off = rng.poisson(MU, size=n_par)
    pts = np.concatenate([p + SIG * rng.standard_normal((k, 2))
                          for p, k in zip(par, n_off)])
    return pts[W.contains(pts)], W

run_substrate("pois2d", pois, (400, 401, 402, 403, 404, 405), 1.0)
run_substrate("thomas2d", thomas, (300, 301, 302, 303, 304, 305), 1.0)  # kappa*mu = 0.05*20

json.dump(out, open("/home/combust/fmexplorer/criticality_tool/bridge/pilot4_thomas.json", "w"), indent=1)
print("PILOT4 DONE", flush=True)
