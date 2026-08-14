"""Pilot ensemble runs whose ONLY purpose is tolerance derivation for the
prereg seal (G-A1, G-A3, G-B1).  Declared openly: these seeds (100-105,
910-915) are pilot seeds and are DISJOINT from the gate seeds (1-3, 920-931)
used after sealing — the gate never re-reads pilot data.

Tolerance rule throughout: tol = 2 × (worst pilot deviation), with floors
(0.02 absolute on pcf curves, 0.05 relative on Σ² gluing) so a lucky pilot
cannot under-cover.  G-A2's tolerance comes from the banked GUE anchor
(bridge/gue_pcf_anchor.json), not from here.
"""

import json
import numpy as np
import sys

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/bridge")
from observer_b import (k_1d, pcf_1d, sigma2_from_g_1d, sigma2_direct_1d,
                        RectWindow, DiskWindow,
                        k_2d, pcf_2d, sigma2_from_g_2d, sigma2_disk_direct)
from ginibre_sampler import sample_ginibre, central_points

out = {}

# ── 1D Poisson pilot ─────────────────────────────────────────────────────────
r1 = np.arange(0.25, 5.01, 0.25)
bins1 = np.arange(0.0, 25.0 + 1e-9, 0.05)
L_LIST = [2.0, 5.0, 10.0, 20.0]
devK, devg, relS = [], [], []
for s in (100, 101, 102):
    rng = np.random.default_rng(s)
    e = np.sort(rng.uniform(0, 100_000, 100_000))
    K = k_1d(e, r1, lam=1.0)
    devK.append(np.abs(K - 2 * r1).max())
    c, g = pcf_1d(e, bins1, lam=1.0)
    m = c >= 0.25
    devg.append(np.abs(g[m] - 1.0).max())
    # gluing: identity vs direct sliding-window variance (home semantics,
    # fast implementation — exact-equality-verified against universality.py)
    direct = sigma2_direct_1d(e, L_LIST)
    for L, dv in zip(L_LIST, direct):
        ident = sigma2_from_g_1d(c, g, L, lam=1.0)
        relS.append(abs(ident - dv) / max(dv, 1e-9))
out["pois1d"] = dict(devK=max(devK), devg=max(devg), relSigma=max(relS))
print("1D Poisson pilot:", out["pois1d"], flush=True)

# ── 2D Poisson pilot ─────────────────────────────────────────────────────────
r2 = np.arange(0.25, 5.01, 0.25)
bins2 = np.arange(0.0, 5.0 + 1e-9, 0.1)
devL, devg2 = [], []
for s in (100, 101, 102, 103, 104, 105):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    n = rng.poisson(W.area())
    pts = rng.uniform(0, 120.0, size=(n, 2))
    K = k_2d(pts, W, r2, lam=1.0)
    L = np.sqrt(K / np.pi)
    devL.append(np.abs(L - r2).max())
    c2, g2 = pcf_2d(pts, W, bins2, lam=1.0)
    m = c2 >= 0.25
    devg2.append(np.abs(g2[m] - 1.0).max())
out["pois2d"] = dict(devL=max(devL), devg=max(devg2))
print("2D Poisson pilot:", out["pois2d"], flush=True)

# ── Ginibre pilot (pooled pcf; per-seed Σ² gluing) ───────────────────────────
N = 2048
gbins = np.arange(0.0, 12.5 + 1e-9, 0.05)
R_LIST = [2.0, 4.0, 6.0]
gs, relSg = [], []
for s in (910, 911, 912, 913, 914, 915):
    ev = sample_ginibre(N, s)
    pts, R = central_points(ev, N)
    W = DiskWindow(R)
    lam = 1.0 / np.pi
    cg, g = pcf_2d(pts, W, gbins, lam=lam)
    gs.append(g)
    direct = sigma2_disk_direct(pts, W, R_LIST, n_disks=400, seed=s)
    for Rd in R_LIST:
        ident = sigma2_from_g_2d(cg, g, Rd, lam)
        relSg.append(abs(ident - direct[Rd]["var"]) / max(direct[Rd]["var"], 1e-9))
    print(f"  ginibre pilot seed {s} done", flush=True)
g_pool = np.mean(gs, axis=0)
m = (cg >= 0.25) & (cg <= 4.0)
g_ana = 1.0 - np.exp(-cg[m]**2)
out["ginibre"] = dict(dev_pcf=float(np.abs(g_pool[m] - g_ana).max()),
                      relSigma=max(relSg))
print("Ginibre pilot:", out["ginibre"], flush=True)

with open("/home/combust/fmexplorer/criticality_tool/bridge/pilot_tolerances.json", "w") as f:
    json.dump(out, f, indent=1)
print("PILOT DONE", flush=True)
