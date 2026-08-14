"""B2 addenda (updates bridge_b_measured.json in place; each block documented):

(a) COARSE-GRAINED class read.  The fine-bin pcf of the Gaussian-prime wedge is
    a lattice comb (support exactly at checkerboard-Z[i] distances with
    constellation weights); the class-level question needs the comb averaged
    over bins ≥ the lattice pitch.  Bins of width 1.5 to r=15.
(b) POWERED FIX-2 designed instance.  The pre-registered inverted-intensity
    demo came back INERT (right vs wrong identical to 3 digits): at 2.2%
    intensity variation there is nothing for the lens to corrupt.  A falsifier
    that cannot fire certifies nothing, so the demonstration is replaced by a
    powered one: inhomogeneous Poisson on the same wedge with λ(r) ∝ (r/R1)^8
    (4.7× variation).  Correct lens (model λ) must return K ≈ πr²; wrong lens
    (constant λ̂, i.e. ignoring the gradient) must manufacture spurious
    clustering.  The inert original is RETAINED in the record as the
    thin-window-regime observation it actually is.
"""

import json
import sys
import numpy as np

BR = "/home/combust/fmexplorer/criticality_tool/bridge"
sys.path.insert(0, BR)
from observer_b import WedgeWindow, pcf_2d, k_2d
from gaussian_prime_annulus import R1, R2, T1, T2
from observer_b import k_inhom  # the same estimator under test

res = json.load(open(f"{BR}/bridge_b_measured.json"))
pts = np.load(f"{BR}/gp_annulus_points.npy")
W = WedgeWindow(R1, R2, T1, T2)
lam_hat = res["B2"]["lam_hat"]

# (a) coarse-grained class read
cbins = np.arange(0.0, 15.0 + 1e-9, 1.5)
cc, gc = pcf_2d(pts, W, cbins, lam=lam_hat)
res["B2"]["g_coarse_centers"] = cc.tolist()
res["B2"]["g_coarse"] = gc.tolist()
print("coarse g:", [f"{c:.1f}:{v:.3f}" for c, v in zip(cc, gc)], flush=True)

# (b) powered FIX-2 designed instance
rng = np.random.default_rng(20260814)
GAMMA = 8.0
lam_fn = lambda r: (r / R1) ** GAMMA
# normalize to ~30k points: expected n = ∫ lam c dA over wedge
rr = np.linspace(R1, R2, 2000)
base = np.trapezoid(lam_fn(rr) * (T2 - T1) * rr, rr)
c0 = 30000.0 / base
# sample by thinning a uniform Poisson at the max intensity
lam_max = c0 * lam_fn(R2)
area = W.area()
# Thinning theorem: proposal count is Poisson(lam_max*area) EXACTLY. The first
# run drew Poisson(lam_max*area*1.05) — a 5% intensity-model mismatch that
# K_inhom faithfully reported as +5% (caught by fix2_replicates.py; the buggy
# run's numbers are retained in fix2_powered with sampler_bug_note).
n_prop = rng.poisson(lam_max * area)
th = rng.uniform(T1, T2, n_prop)
rad = np.sqrt(rng.uniform(R1**2, R2**2, n_prop))    # uniform-in-area radii
keep = rng.uniform(0, lam_max, n_prop) < c0 * lam_fn(rad)
sp = np.column_stack([rad * np.cos(th), rad * np.sin(th)])[keep]
sp = sp[W.contains(sp)]
lam_sp_hat = len(sp) / area
r_k = np.arange(2.0, 12.01, 2.0)
K_right = k_inhom(sp, W, r_k, lambda r: c0 * lam_fn(r))
K_wrong = k_2d(sp, W, r_k, lam=lam_sp_hat)           # stationary lens = wrong
K_ref = np.pi * r_k**2
res["B2"]["fix2_powered"] = dict(
    gamma=GAMMA, n=len(sp),
    intensity_variation=float(lam_fn(R2) / lam_fn(R1)),
    r_grid=r_k.tolist(), K_poisson_ref=K_ref.tolist(),
    K_inhom_right_lens=K_right.tolist(), K_stationary_wrong_lens=K_wrong.tolist(),
    right_reldev=[float(a / b - 1) for a, b in zip(K_right, K_ref)],
    wrong_reldev=[float(a / b - 1) for a, b in zip(K_wrong, K_ref)],
    note="original inverted-intensity demo retained above as the inert "
         "thin-window observation; this is the powered replacement")
print("FIX-2 powered: right dev", [f"{v:+.1%}" for v in res["B2"]["fix2_powered"]["right_reldev"]],
      " wrong dev", [f"{v:+.1%}" for v in res["B2"]["fix2_powered"]["wrong_reldev"]], flush=True)

json.dump(res, open(f"{BR}/bridge_b_measured.json", "w"), indent=1)
print("B2 ADDENDA DONE", flush=True)
