"""
Task B POST-SEAL DIAGNOSTICS. These are NOT sealed tests. They diagnose two scored outcomes:

  D1. P-B5-saturation FIRED (2*Var[S] = 0.1449 vs plateau 0.2829). Slot-check: the identity
      Sigma^2(L->inf) -> 2 Var[S] is about S(t) sampled UNIFORMLY in t. The sealed run measured
      S AT THE ZEROS (rank_j - rvm_N(gamma_j)), which is the post-jump value of a jump process.
      Did the prediction fire on physics or on my sampling?

  D2. P-B2-slot was FALSIFIED: F(alpha) via a poly-3 unfold recovered the known answer on
      curvature-matched GUE (2.5% median error) where Sigma^2 via the same unfold was 4.51x wrong.
      Proposed mechanism: the fitted-unfold residual is a SMOOTH, LOW-FREQUENCY distortion, so it
      lives at alpha below some alpha_c; Sigma^2 at large L is dominated by exactly that region,
      while F is only read above it. Test: locate alpha_c.
"""
from __future__ import annotations
import json, math, os
import numpy as np
from taskB_falpha import (rvm_N, exact_N, unfold_poly, unfold_const, sigma2, form_factor,
                          curved, gue_analytic, Ls, N, HERE, ROOT, ALPHA_FINE)

p = lambda *a: print(*a, flush=True)
OUT = {"note": "POST-SEAL diagnostics, not sealed tests"}

z6 = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
blk = z6[:N]
rank = np.arange(1, N + 1, dtype=float)

# ------------------------------------------------------------------ D1: sampling of S(t)
p("[D1] Var[S]: sampled AT ZEROS (sealed) vs UNIFORMLY IN t (what the identity is about)")
S_at_zeros = rank - rvm_N(blk)
grid = np.linspace(blk[0], blk[-1], 400_000)
S_uniform = np.searchsorted(blk, grid, side="right").astype(float) - rvm_N(grid)
# drop a burn-in at the very bottom of the block where the asymptotic smooth term is worst
mask = grid > 100.0
v_zeros = float(np.var(S_at_zeros))
v_unif = float(np.var(S_uniform))
v_unif_100 = float(np.var(S_uniform[mask]))
s2_theta = sigma2(rvm_N(blk), Ls)
plateau = float(np.mean(s2_theta[-2:]))
for lbl, v in (("at zeros (sealed)", v_zeros), ("uniform in t", v_unif),
               ("uniform in t, gamma>100", v_unif_100)):
    p(f"  Var[S] {lbl:26s} = {v:.5f}   2*Var[S] = {2*v:.5f}   plateau/2Var = {plateau/(2*v):.3f}")
OUT["D1"] = {"VarS_at_zeros": v_zeros, "VarS_uniform": v_unif, "VarS_uniform_gamma_gt_100": v_unif_100,
             "plateau_L16_32": plateau, "ratio_plateau_over_2VarS_uniform": plateau / (2 * v_unif),
             "sealed_bracket": [0.20, 0.36], "two_VarS_uniform": 2 * v_unif}
p(f"  sealed bracket for 2*Var[S] was [0.20, 0.36]; observed plateau {plateau:.4f}")
p("")

# ------------------------------------------------------------------ D2: where the artifact lives
p("[D2] locating the fitted-unfold artifact in alpha (curvature-matched GUE, B=6)")
a_lo = np.concatenate([np.arange(0.002, 0.100, 0.002), np.arange(0.10, 1.001, 0.01)])
acc_t, acc_p3, acc_p9 = [], [], []
for _ in range(6):
    raw = curved("GUE", N, float(blk[0]))
    acc_t.append(form_factor(rvm_N(raw), a_lo))
    acc_p3.append(form_factor(unfold_poly(raw, 3), a_lo))
    acc_p9.append(form_factor(unfold_poly(raw, 9), a_lo))


def sm(v, w=7):
    v = np.mean(v, 0)
    k = np.ones(w) / w
    return np.convolve(v, k, mode="same")


Kt, Kp3, Kp9 = sm(acc_t), sm(acc_p3), sm(acc_p9)
p(f"  {'alpha':>7s} {'F_theta':>9s} {'F_poly3':>9s} {'F_poly9':>9s} {'GUE ref':>9s}")
for a in (0.004, 0.008, 0.016, 0.03, 0.06, 0.10, 0.20, 0.40, 0.80):
    i = int(np.argmin(np.abs(a_lo - a)))
    p(f"  {a_lo[i]:>7.3f} {Kt[i]:>9.3f} {Kp3[i]:>9.3f} {Kp9[i]:>9.3f} {min(a_lo[i],1.0):>9.3f}")
band = a_lo >= 0.005
excess3 = np.abs(Kp3 - Kt) / np.maximum(Kt, 1e-9)
ac3 = [float(a_lo[i]) for i in range(len(a_lo)) if band[i] and excess3[i] > 0.25]
alpha_c3 = max(ac3) if ac3 else None
p(f"  highest alpha at which poly3 still deviates >25% from theta: {alpha_c3}")
OUT["D2"] = {"alphas": a_lo.tolist(), "F_theta": Kt.tolist(), "F_poly3": Kp3.tolist(),
             "F_poly9": Kp9.tolist(), "alpha_c_poly3_25pct": alpha_c3, "B": 6}
p("")

# ------------------------------------------------------------------ D3: additive-artifact structure
p("[D3] is the fitted-unfold Sigma^2 artifact additive and class-independent?")
rows = {}
for kind, known in (("Poisson", 32.0), ("GUE", float(gue_analytic(Ls)[-1])), ("superrigid", None)):
    a3, at = [], []
    for _ in range(6):
        raw = curved(kind, N, float(blk[0]))
        a3.append(sigma2(unfold_poly(raw, 3), Ls)[-1])
        at.append(sigma2(rvm_N(raw), Ls)[-1])
    m3, mt = float(np.mean(a3)), float(np.mean(at))
    rows[kind] = {"sigma2_32_poly3": m3, "sigma2_32_theta": mt, "excess": m3 - mt,
                  "known": known}
    p(f"  {kind:11s} Sigma^2(32): theta {mt:8.4f}  poly3 {m3:8.4f}  EXCESS {m3-mt:+8.4f}")
z_gen3 = 2.877659645361805       # Phase 3, low_gamma, order-3, L=32 (phase3_sigma2_measured.json)
z_the = 0.28546002689522004      # Phase 3, low_gamma, theta-exact, L=32
p(f"  {'zeta (P3)':11s} Sigma^2(32): theta {z_the:8.4f}  order3 {z_gen3:8.4f}  EXCESS {z_gen3-z_the:+8.4f}")
OUT["D3"] = {"rows": rows, "zeta_phase3_order3_L32": z_gen3, "zeta_phase3_theta_L32": z_the,
             "zeta_excess": z_gen3 - z_the}

json.dump(OUT, open(os.path.join(HERE, "taskB_diagnostics_measured.json"), "w"), indent=2)
p("\nwrote taskB_diagnostics_measured.json")
