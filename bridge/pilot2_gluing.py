"""Amended G-A3 pilot (pre-seal, tolerance derivation only).

Motivation (filed before sealing): the first pilot showed the 2-D gluing
identity on GINIBRE disagreeing with direct Σ² by ~100% rel.  Mechanism, not
bug: for a class-I hyperuniform process Var N(R) is a near-cancellation
(λπR² − λ²∫e^{−r²}γ2πr dr = R/√π for exact Ginibre), so ĝ noise ε is
amplified by ~(λπR²)²/Var N(R) — divergent exactly where hyperuniformity is
strongest.  Same mechanism in 1-D at large L for GUE-class (amplification
~L²/Σ²(L) ≈ L²·π²/ln L).  Consequences:
  * G-A3 is gated on substrates where the identity has SNR: 1-D Poisson,
    1-D GUE-class at moderate L, 2-D Poisson, and a 2-D THOMAS clustered
    designed instance (positive g−1 → no cancellation, integral term
    exercised with signal — decompose-confound-with-designed-instance).
  * Ginibre 2-D gluing is reported DESCRIPTIVELY with the amplification
    factor alongside; the limitation is banked in TOOLKIT §11 as an
    instrument note.  This choice is made pre-seal, from pilot data whose
    declared purpose is tolerance derivation.
"""

import json
import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/bridge")
from observer_b import (RectWindow, pcf_2d, sigma2_from_g_2d, sigma2_disk_direct,
                        pcf_1d, sigma2_from_g_1d, sigma2_direct_1d)
from bank_gue_pcf_anchor import gue_levels, semicircle_unfold, TRIM

out = {}

# ── 2D Thomas designed instance (kappa=0.05, mu=20, sigma=1.5 → lam=1) ───────
KAPPA, MU, SIG = 0.05, 20, 1.5
R_LIST = [2.0, 4.0, 6.0]
bins = np.arange(0.0, 12.5 + 1e-9, 0.1)
rel_th = []
for s in (300, 301, 302, 303, 304, 305):
    rng = np.random.default_rng(s)
    W = RectWindow(120.0, 120.0)
    buf = 5 * SIG
    n_par = rng.poisson(KAPPA * (120 + 2 * buf) ** 2)
    par = rng.uniform(-buf, 120 + buf, size=(n_par, 2))
    n_off = rng.poisson(MU, size=n_par)
    pts = np.concatenate([p + SIG * rng.standard_normal((k, 2))
                          for p, k in zip(par, n_off)])
    pts = pts[W.contains(pts)]
    lam = len(pts) / W.area()
    c, g = pcf_2d(pts, W, bins, lam=lam)
    direct = sigma2_disk_direct(pts, W, R_LIST, n_disks=400, seed=s)
    for R in R_LIST:
        ident = sigma2_from_g_2d(c, g, R, lam)
        rel_th.append(abs(ident - direct[R]["var"]) / direct[R]["var"])
    print(f"  thomas seed {s}: n={len(pts)} lam={lam:.3f}", flush=True)
out["thomas2d"] = dict(relSigma=float(max(rel_th)))
print("2D Thomas gluing pilot:", out["thomas2d"], flush=True)

# ── 1D GUE-class gluing pilot (semicircle-unfolded GUE bulk) ─────────────────
bins1 = np.arange(0.0, 25.0 + 1e-9, 0.05)
L_LIST = [2.0, 5.0, 10.0, 20.0]
rel_g = {L: [] for L in L_LIST}
for s in (800, 801, 802, 803, 804, 805):
    u = np.sort(semicircle_unfold(gue_levels(4096, s), 4096))
    k = int(TRIM * len(u))
    u = u[k:-k]
    c1, g1 = pcf_1d(u, bins1)
    direct = sigma2_direct_1d(u, L_LIST)
    for L, dv in zip(L_LIST, direct):
        ident = sigma2_from_g_1d(c1, g1, L)
        rel_g[L].append(abs(ident - dv) / dv)
    print(f"  gue seed {s} done", flush=True)
out["gue1d"] = {str(L): float(max(v)) for L, v in rel_g.items()}
print("1D GUE gluing pilot (per L):", out["gue1d"], flush=True)

with open("/home/combust/fmexplorer/criticality_tool/bridge/pilot2_gluing.json", "w") as f:
    json.dump(out, f, indent=1)
print("PILOT2 DONE", flush=True)
