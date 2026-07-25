"""
ARS-RH Phase 3 — Sigma^2 number variance, the orthogonal long-range witness.
Prereg: PHASE3_PREREG_SEALED.json. §0: instrument-corroboration, NOT about RH.

GENERAL (empirical) unfolding is the estimator whose verdict we trust ONLY after it passes
a known-answer decoy battery. theta-exact R-vM is a zeta-ONLY ground-truth cross-check, never
the general path. The Poisson decoy is the sentinel for over-smoothing false-rigidity.
"""
import json, math, os, sys
import numpy as np
from scipy.linalg import eigh_tridiagonal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RNG = np.random.default_rng(20260725)
EULER = 0.5772156649015329

def sigma2(xi, Ls, step=0.25):
    xi = np.sort(xi); lo, hi = xi[0], xi[-1]; out = []
    for L in Ls:
        starts = np.arange(lo, hi - L, step)
        c = np.searchsorted(xi, starts + L) - np.searchsorted(xi, starts)
        out.append(float(np.var(c)))
    return np.array(out)

def unfold_emp(x, order):
    x = np.sort(x); r = np.arange(1, len(x) + 1)
    c = np.polyfit(x, r, order)
    return np.polyval(c, x)

def gue_levels(N):
    n = 5 * N
    d = math.sqrt(2.0) * RNG.standard_normal(n)
    b = np.sqrt(RNG.chisquare(2 * np.arange(n - 1, 0, -1)))
    ev = np.sort(eigh_tridiagonal(d, b, eigvals_only=True, select="i",
                                  select_range=(2 * N, 3 * N - 1)))
    return ev

def poisson_levels(N):
    return np.sort(RNG.exponential(1.0, N).cumsum())

def superrigid_levels(N, eta=0.3):     # picket fence + jitter: Sigma^2 -> 2 eta^2, << GUE
    return np.sort(np.arange(N) + eta * RNG.standard_normal(N))

def gue_analytic(Ls):
    return np.array([(1.0/math.pi**2)*(math.log(2*math.pi*L)+EULER+1.0) for L in Ls])

N = 2000
Ls = np.array([1,2,4,8,16,32], float)
print("=== ARS-RH Phase 3: Sigma^2 number variance ===", flush=True)
print("Ls =", list(Ls), flush=True)

# ---- calibrate general unfolding order on Poisson + GUE decoys ----
print("\n[decoy battery] calibrate empirical-unfold polynomial order (blocking gate)", flush=True)
print("  GUE analytic Sigma^2:", ["%.3f"%v for v in gue_analytic(Ls)], flush=True)
orders = [3,5,7,9]
B = 12
gate = {}
for order in orders:
    ps=[]; gs=[]; rs=[]
    for _ in range(B):
        ps.append(sigma2(unfold_emp(poisson_levels(N), order), Ls))
        gs.append(sigma2(unfold_emp(gue_levels(N), order), Ls))
        rs.append(sigma2(unfold_emp(superrigid_levels(N), order), Ls))
    ps=np.array(ps).mean(0); gs=np.array(gs).mean(0); rs=np.array(rs).mean(0)
    # Poisson should give ~L; ratio at large L is the over-smoothing sentinel
    pois_ratio = ps[-1]/Ls[-1]
    gue_err = np.abs(gs - gue_analytic(Ls))/gue_analytic(Ls)
    print(f"\n  order {order}:", flush=True)
    print("    Poisson  Sigma^2:", ["%.2f"%v for v in ps], " (want ~L=%.0f at Lmax; ratio %.2f)"%(Ls[-1],pois_ratio), flush=True)
    print("    GUE      Sigma^2:", ["%.3f"%v for v in gs], " (rel-err vs analytic max %.2f)"%gue_err.max(), flush=True)
    print("    super-rig Sigma^2:", ["%.3f"%v for v in rs], " (want << GUE)", flush=True)
    gate[order] = {"poisson_ratio_Lmax": float(pois_ratio), "gue_relerr_max": float(gue_err.max()),
                   "superrigid_below_gue": bool((rs < gs).all())}

# pick order: Poisson ratio in [0.8,1.2] AND GUE rel-err < 0.25 AND super-rigid < GUE
ok = [o for o in orders if 0.8 <= gate[o]["poisson_ratio_Lmax"] <= 1.2
      and gate[o]["gue_relerr_max"] < 0.25 and gate[o]["superrigid_below_gue"]]
print("\n  orders passing gate:", ok, flush=True)
if not ok:
    print("  GATE FAILED — no order recovers Poisson=L AND GUE=analytic AND sees super-rigidity. ABORT before zeta.", flush=True)
    json.dump({"gate": gate, "passed": []}, open(os.path.join(HERE,"phase3_sigma2_measured.json"),"w"), indent=2)
    sys.exit(0)
ORDER = min(ok)   # lowest passing order = least flexible = least over-smoothing risk
print(f"  -> locked general-unfold order = {ORDER} (lowest passing = least over-smoothing)", flush=True)

# ---- zeta, general unfolding (decoy-gated) + theta-exact ground-truth cross-check ----
def rvm_N(t):
    tt = t/(2*math.pi); return tt*np.log(tt) - tt + 7.0/8.0

z6 = np.sort(np.loadtxt(os.path.join(ROOT,"data","odlyzko_zeros6.txt")))
W = N
blocks = {"low_gamma": z6[:W], "high_gamma": z6[z6.size-W-1:z6.size-1]}
# GUE ensemble band through the SAME estimator (order ORDER)
gue_band = np.array([sigma2(unfold_emp(gue_levels(W), ORDER), Ls) for _ in range(30)])
gb_m, gb_s = gue_band.mean(0), gue_band.std(0)

print("\n[zeta] Sigma^2 vs GUE-ensemble band (same estimator), general unfold order %d"%ORDER, flush=True)
res = {"order": ORDER, "Ls": list(Ls), "gate": gate, "passed_orders": ok,
       "gue_band_mean": gb_m.tolist(), "gue_band_sd": gb_s.tolist(),
       "gue_analytic": gue_analytic(Ls).tolist(), "blocks": {}}
for name, blk in blocks.items():
    gmid = float(blk[len(blk)//2])
    s_gen = sigma2(unfold_emp(blk, ORDER), Ls)
    s_the = sigma2(rvm_N(blk), Ls)                    # zeta-only ground truth
    dev = (s_gen - gb_m)/gb_s
    print(f"\n  {name} (gamma_mid={gmid:.4g}):", flush=True)
    print("    zeta Sigma^2 (general):", ["%.3f"%v for v in s_gen], flush=True)
    print("    zeta Sigma^2 (theta-ex):", ["%.3f"%v for v in s_the], "  <- ground-truth xcheck", flush=True)
    print("    GUE band mean         :", ["%.3f"%v for v in gb_m], flush=True)
    print("    (zeta_gen - GUE)/sd   :", ["%+.2f"%v for v in dev], "  (neg = MORE rigid than GUE)", flush=True)
    gen_the_agree = float(np.max(np.abs(s_gen - s_the)/np.maximum(s_the,1e-9)))
    res["blocks"][name] = {"gamma_mid": gmid, "sigma2_general": s_gen.tolist(),
                           "sigma2_theta_exact": s_the.tolist(), "dev_over_sd": dev.tolist(),
                           "general_vs_theta_max_relerr": gen_the_agree}
    print("    general-vs-theta max rel-err: %.3f %s"%(gen_the_agree,
          "(paths agree)" if gen_the_agree < 0.2 else "(DISAGREE -> unfolding is the story)"), flush=True)

json.dump(res, open(os.path.join(HERE,"phase3_sigma2_measured.json"),"w"), indent=2)
print("\nDONE", flush=True)
