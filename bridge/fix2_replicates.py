"""Committed generator of B2's fix2_powered_replicates (3 seeds, exact
thinning-theorem sampler).  This is the run that CAUGHT the 1.05x proposal-
count bug in patch_b2_addenda.py's first execution: the estimator's +5%
readback was systematic across seeds and r, which is a model-mismatch
signature, not noise (seed_replicate_near_boundary discipline).
Exposure audit for that bug: see RESULTS_BRIDGE.md 'Defect ledger'."""

import json
import sys
import numpy as np

BR = "/home/combust/fmexplorer/criticality_tool/bridge"
sys.path.insert(0, BR)
from observer_b import WedgeWindow, k_2d, k_inhom
from gaussian_prime_annulus import R1, R2, T1, T2

W = WedgeWindow(R1, R2, T1, T2)
GAMMA = 8.0
lam_fn = lambda r: (r / R1) ** GAMMA
rr = np.linspace(R1, R2, 2000)
c0 = 30000.0 / np.trapezoid(lam_fn(rr) * (T2 - T1) * rr, rr)
lam_max = c0 * lam_fn(R2)
r_k = np.arange(2.0, 12.01, 2.0)
K_ref = np.pi * r_k**2

rows = []
for seed in (11, 12, 13):
    rng = np.random.default_rng(seed)
    n_prop = rng.poisson(lam_max * W.area())      # exact thinning count
    th = rng.uniform(T1, T2, n_prop)
    rad = np.sqrt(rng.uniform(R1**2, R2**2, n_prop))
    keep = rng.uniform(0, lam_max, n_prop) < c0 * lam_fn(rad)
    sp = np.column_stack([rad * np.cos(th), rad * np.sin(th)])[keep]
    sp = sp[W.contains(sp)]
    Kr = k_inhom(sp, W, r_k, lambda r: c0 * lam_fn(r))
    Kw = k_2d(sp, W, r_k, lam=len(sp) / W.area())
    rows.append(dict(seed=seed, n=len(sp),
                     right=[float(a / b - 1) for a, b in zip(Kr, K_ref)],
                     wrong=[float(a / b - 1) for a, b in zip(Kw, K_ref)]))
    print(seed, "right", [f"{v:+.1%}" for v in rows[-1]["right"]],
          "wrong", [f"{v:+.1%}" for v in rows[-1]["wrong"]], flush=True)

res = json.load(open(f"{BR}/bridge_b_measured.json"))
res["B2"]["fix2_powered_replicates"] = rows
json.dump(res, open(f"{BR}/bridge_b_measured.json", "w"), indent=1)
print("REPLICATES SAVED")
