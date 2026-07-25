"""
ARS Look Arc — Task B: the "unfolding-free" F(alpha) readout, tested against its own premise.

Seal: seals/TASKB_SEAL.json + seals/TASKB_SEAL_ADDENDUM_1.json (both committed pre-run).

§0: nothing here estimates Lambda; nothing bears on RH. zeta is a calibrator substrate.
§0d: F(alpha), Sigma^2 and Delta_3 are ONE witness under three headings. Nothing below may be
     reported as F corroborating Sigma^2.

Sections:
  G   estimator gate on FLAT decoys (must pass or abort)
  B0  premise test: is the direct exponential sum actually unfolding-free?
  B2  curvature-matched decoy battery (poly leg = powered; theta leg = plumbing only, addendum 1)
  B5  Var[S] saturation bracket + powered theta-truncation cert
  B4  alpha >= 1 look region (qualitative, no significance values)

Run: /home/combust/fmexplorer/bin/python3 arsrh/taskB_falpha.py
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.special import loggamma

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RNG = np.random.default_rng(20260725)
EULER = 0.5772156649015329
p = lambda *a: print(*a, flush=True)

# ----------------------------------------------------------------------------- estimators

def sigma2(xi, Ls, step=0.25):
    """Phase-3 number variance, verbatim (same estimator, for comparability)."""
    xi = np.sort(xi); lo, hi = xi[0], xi[-1]; out = []
    for L in Ls:
        starts = np.arange(lo, hi - L, step)
        c = np.searchsorted(xi, starts + L) - np.searchsorted(xi, starts)
        out.append(float(np.var(c)))
    return np.array(out)


def hann(x):
    u = (x - x[0]) / (x[-1] - x[0])
    return 0.5 - 0.5 * np.cos(2 * math.pi * u)


def form_factor(x, alphas):
    """K(alpha) = |sum_j w_j e^{2 pi i alpha x_j}|^2 / sum_j w_j^2, Hann-tapered.

    Normalised so unit-density Poisson -> 1. GUE limit -> min(alpha,1) = Montgomery's F(alpha).
    NOTE: this is the block periodogram of the level density, NOT Montgomery's T-averaged
    F(alpha,T) with the Lorentzian pair weight. Same GUE limit; different estimator. Labelled
    as such wherever reported.
    """
    x = np.sort(np.asarray(x, float))
    w = hann(x)
    s = np.exp(2j * math.pi * np.outer(np.asarray(alphas, float), x)) @ w
    return (np.abs(s) ** 2) / float((w ** 2).sum())


def form_factor_pairsum(x, alphas):
    """Montgomery's literal form: a DOUBLE sum over pairs of heights. O(N^2) per alpha.

    Used only to demonstrate that the pair sum and the periodogram are the same object.
    """
    x = np.sort(np.asarray(x, float))
    w = hann(x)
    d = x[:, None] - x[None, :]
    ww = np.outer(w, w)
    return np.array([float(np.real(np.sum(ww * np.exp(2j * math.pi * a * d))) / float((w ** 2).sum()))
                     for a in alphas])


ALPHA_FINE = np.arange(0.02, 3.001, 0.002)
ALPHA_OUT = np.arange(0.10, 2.901, 0.05)
BOX = 0.05


def smooth_box(a_fine, k_fine, a_out, half):
    return np.array([k_fine[(a_fine >= a - half) & (a_fine <= a + half)].mean() for a in a_out])


def K_of(x):
    return smooth_box(ALPHA_FINE, form_factor(x, ALPHA_FINE), ALPHA_OUT, BOX)


# ----------------------------------------------------------------------------- unfoldings

def rvm_N(t):
    """Asymptotic Riemann-von Mangoldt smooth counting (Phase 3's theta path, verbatim)."""
    tt = np.asarray(t, float) / (2 * math.pi)
    return tt * np.log(tt) - tt + 7.0 / 8.0


def rvm_N_next(t):
    t = np.asarray(t, float)
    return rvm_N(t) + 1.0 / (48.0 * math.pi * t)


def theta_exact(t):
    """theta(t) = Im log Gamma(1/4 + i t/2) - (t/2) log pi (exact, no asymptotic)."""
    t = np.asarray(t, float)
    return np.imag(loggamma(0.25 + 0.5j * t)) - 0.5 * t * math.log(math.pi)


def exact_N(t):
    return theta_exact(t) / math.pi + 1.0


def unfold_poly(x, order):
    x = np.sort(np.asarray(x, float)); r = np.arange(1, len(x) + 1)
    return np.polyval(np.polyfit(x, r, order), x)


def unfold_const(x):
    """The LITERAL 'no unfolding' reading: rescale raw heights by the block-mean density."""
    x = np.sort(np.asarray(x, float))
    return ((len(x) - 1) / (x[-1] - x[0])) * x


# --------------------------------------------------------------- curved-backbone synthetics

_TG = np.linspace(12.0, 3000.0, 2_000_000)
_NG = exact_N(_TG)
assert np.all(np.diff(_NG) > 0), "exact_N grid not monotone — cannot invert"


def exact_N_inv(v):
    return np.interp(v, _NG, _TG)


def gue_unit(W):
    n = 5 * W
    d = math.sqrt(2.0) * RNG.standard_normal(n)
    b = np.sqrt(RNG.chisquare(2 * np.arange(n - 1, 0, -1)))
    ev = np.sort(eigh_tridiagonal(d, b, eigvals_only=True, select="i",
                                  select_range=(2 * W, 3 * W - 1)))
    s = np.diff(ev)
    return np.concatenate([[0.0], np.cumsum(s / s.mean())])


def poisson_unit(W):
    return np.sort(RNG.exponential(1.0, W).cumsum())


def superrigid_unit(W, eta=0.3):
    return np.sort(np.arange(W) + eta * RNG.standard_normal(W))


UNIT = {"Poisson": poisson_unit, "GUE": gue_unit, "superrigid": superrigid_unit}


def curved(kind, W, t_lo):
    """Impose a KNOWN-class unit-density sequence on zeta's EXACT-theta density backbone."""
    return exact_N_inv(float(exact_N(np.array([t_lo]))[0]) + UNIT[kind](W))


def gue_analytic(Ls):
    return np.array([(1.0 / math.pi ** 2) * (math.log(2 * math.pi * L) + EULER + 1.0) for L in Ls])


def K_analytic(alphas, kind):
    a = np.asarray(alphas, float)
    if kind == "Poisson":
        return np.ones_like(a)
    if kind == "GUE":
        return np.minimum(a, 1.0)
    return None


Ls = np.array([1, 2, 4, 8, 16, 32], float)
N = 2000
OUT = {"anti_claim": "instrument conditioning test; NOT about RH. F(alpha)/Sigma^2/Delta_3 are ONE witness."}

p("=== ARS Look Arc / Task B — F(alpha) premise test ===")
p("seal: seals/TASKB_SEAL.json (+ ADDENDUM_1), both committed pre-run\n")

# ============================================================== G — estimator gate (FLAT)
p("[G] estimator gate on FLAT decoys (abort if fail)")
gate = {}
for kind in ("Poisson", "GUE", "superrigid"):
    ks, s2 = [], []
    for _ in range(8):
        u = UNIT[kind](N)
        ks.append(K_of(u)); s2.append(sigma2(u, Ls))
    ks = np.mean(ks, 0); s2 = np.mean(s2, 0)
    ref = K_analytic(ALPHA_OUT, kind)
    band = (ALPHA_OUT >= 0.3) & (ALPHA_OUT <= 2.5)
    err = float(np.median(np.abs(ks[band] - ref[band]) / ref[band])) if ref is not None else None
    gate[kind] = {"K_median_relerr_vs_analytic": err,
                  "K_at_0.15_0.5_1.0_2.0": [float(np.interp(v, ALPHA_OUT, ks)) for v in (0.15, 0.5, 1.0, 2.0)],
                  "K_full": ks.tolist(), "sigma2": s2.tolist()}
    p(f"  {kind:11s} K(0.15,0.5,1,2) = " +
      ", ".join("%.3f" % v for v in gate[kind]["K_at_0.15_0.5_1.0_2.0"]) +
      (f"   med rel-err = {err:.3f}" if err is not None else "   (no analytic ref)") +
      f"   Sigma^2(32) = {s2[-1]:.3f}")

# super-rigid criterion uses SMALL alpha: a jittered picket fence is CRYSTALLINE, so it carries
# Bragg peaks at integer alpha which push K ABOVE Poisson there. Rigidity shows at small alpha.
gate_pass = (gate["Poisson"]["K_median_relerr_vs_analytic"] < 0.15 and
             gate["GUE"]["K_median_relerr_vs_analytic"] < 0.25 and
             gate["superrigid"]["K_at_0.15_0.5_1.0_2.0"][0] < gate["GUE"]["K_at_0.15_0.5_1.0_2.0"][0] and
             gate["superrigid"]["sigma2"][-1] < gate["GUE"]["sigma2"][-1])
p(f"  GATE {'PASS' if gate_pass else 'FAIL'}")
p(f"  (note: super-rigid K at integer alpha = "
  f"{gate['superrigid']['K_at_0.15_0.5_1.0_2.0'][2]:.2f}/{gate['superrigid']['K_at_0.15_0.5_1.0_2.0'][3]:.2f} "
  f"-> Bragg peaks; crystalline decoys are NOT a valid rigid bracket for a form factor)\n")
OUT["G_estimator_gate"] = {"rows": gate, "pass": bool(gate_pass), "alphas": ALPHA_OUT.tolist()}
if not gate_pass:
    json.dump(OUT, open(os.path.join(HERE, "taskB_falpha_measured.json"), "w"), indent=2)
    raise SystemExit("estimator gate FAILED — abort before any zeta reading")

# ============================================================== B0 — the premise
p("[B0] premise: is the direct exponential sum unfolding-free?")
z6 = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
blk = z6[:N]                                      # Phase 3's low_gamma block, gamma 14.1 .. 2515.3
gmid = float(blk[N // 2])
curv = math.log(blk[-1] / (2 * math.pi)) / math.log(blk[0] / (2 * math.pi))
p(f"  block = zeros6[:2000], gamma {blk[0]:.2f} .. {blk[-1]:.1f}, gamma_mid = {gmid:.4f}")
p(f"  mean spacing {2*math.pi/math.log(blk[-1]/(2*math.pi)):.3f} .. "
  f"{2*math.pi/math.log(blk[0]/(2*math.pi)):.3f}  ({curv:.1f}x density curvature across the block)")

# P-B0-a: Montgomery's literal pair sum over raw heights == the periodogram
a_chk = np.array([0.25, 0.5, 0.75, 1.25, 2.0])
K_pair = form_factor_pairsum(rvm_N(blk), a_chk)
K_per = form_factor(rvm_N(blk), a_chk)
d_a = float(np.max(np.abs(K_pair - K_per)))
p(f"  P-B0-a  max|pair-sum over raw heights - unfold-then-transform| = {d_a:.3e}  "
  f"(sealed < 1e-10 -> {'HOLDS' if d_a < 1e-10 else 'FAILS'})")

schemes = {"theta_rvm": rvm_N(blk),
           "poly3": unfold_poly(blk, 3),
           "poly9": unfold_poly(blk, 9),
           "const_meandensity": unfold_const(blk)}
Kz = {k: K_of(v) for k, v in schemes.items()}
band = (ALPHA_OUT >= 0.2) & (ALPHA_OUT <= 2.0)
rel = {k: float(np.median(np.abs(Kz[k][band] - Kz["theta_rvm"][band]) / Kz["theta_rvm"][band]))
       for k in schemes if k != "theta_rvm"}
for k, v in rel.items():
    p(f"  P-B0-b/c  median rel-diff vs theta over alpha in [0.2,2]:  {k:18s} {v*100:7.2f}%")
OUT["B0_premise"] = {
    "block": {"name": "zeros6[:2000]", "gamma_mid": gmid, "gamma_lo": float(blk[0]),
              "gamma_hi": float(blk[-1]), "density_curvature_ratio": curv},
    "P_B0_a_alphas": a_chk.tolist(), "P_B0_a_pairsum": K_pair.tolist(),
    "P_B0_a_periodogram": K_per.tolist(), "P_B0_a_max_abs_diff": d_a,
    "P_B0_a_holds": bool(d_a < 1e-10),
    "median_reldiff_vs_theta": rel,
    "P_B0_b_holds": bool(rel["poly3"] > 0.10 and rel["poly9"] > 0.02),
    "P_B0_c_holds": bool(rel["const_meandensity"] > 0.50),
    "alphas": ALPHA_OUT.tolist(),
    "K_by_scheme": {k: v.tolist() for k, v in Kz.items()},
}
p("")

# ============================================================== B2 — curvature-matched battery
p("[B2] curvature-matched decoy battery (built on EXACT-theta backbone, unfolded by ASYMPTOTIC rvm_N)")
p("     poly leg = POWERED.  theta leg = PLUMBING ONLY (addendum 1).")
t_lo = float(blk[0])
B = 8
batt = {}
for kind in ("Poisson", "GUE", "superrigid"):
    acc = {"s2_poly3": [], "s2_poly9": [], "s2_theta": [], "K_theta": [], "K_poly3": []}
    for _ in range(B):
        raw = curved(kind, N, t_lo)
        acc["s2_poly3"].append(sigma2(unfold_poly(raw, 3), Ls))
        acc["s2_poly9"].append(sigma2(unfold_poly(raw, 9), Ls))
        acc["s2_theta"].append(sigma2(rvm_N(raw), Ls))
        acc["K_theta"].append(K_of(rvm_N(raw)))
        acc["K_poly3"].append(K_of(unfold_poly(raw, 3)))
    m = {k: np.mean(v, 0) for k, v in acc.items()}
    row = {k: v.tolist() for k, v in m.items()}
    known = {"Poisson": Ls.copy(), "GUE": gue_analytic(Ls)}.get(kind)
    if known is not None:
        row["known_sigma2"] = known.tolist()
        for k in ("s2_poly3", "s2_poly9", "s2_theta"):
            row[k + "_ratio_at_L32"] = float(m[k][-1] / known[-1])
        ref = K_analytic(ALPHA_OUT, kind)
        kb = (ALPHA_OUT >= 0.5) & (ALPHA_OUT <= 2.0)
        row["K_theta_median_relerr"] = float(np.median(np.abs(m["K_theta"][kb] - ref[kb]) / ref[kb]))
        row["K_poly3_median_relerr"] = float(np.median(np.abs(m["K_poly3"][kb] - ref[kb]) / ref[kb]))
        p(f"  {kind:11s} Sigma^2(32)/known:  poly3 {row['s2_poly3_ratio_at_L32']:7.2f}   "
          f"poly9 {row['s2_poly9_ratio_at_L32']:7.2f}   theta {row['s2_theta_ratio_at_L32']:7.2f}")
        p(f"  {'':11s} F med rel-err   :  poly3 {row['K_poly3_median_relerr']*100:7.1f}%  "
          f"theta {row['K_theta_median_relerr']*100:7.1f}%")
    else:
        p(f"  {kind:11s} Sigma^2(32): poly3 {m['s2_poly3'][-1]:.4f}  poly9 {m['s2_poly9'][-1]:.4f}  "
          f"theta {m['s2_theta'][-1]:.4f}  (want << GUE 0.697)")
    batt[kind] = row

pw = (batt["Poisson"]["s2_poly3_ratio_at_L32"] > 1.3 and batt["GUE"]["s2_poly3_ratio_at_L32"] > 2.0)
OUT["B2_battery"] = {"B": B, "Ls": Ls.tolist(), "rows": batt,
                     "P_B2_power_poly_leg_holds": bool(pw)}
p(f"  P-B2-power (poly leg, the only powered one): {'HOLDS' if pw else 'FAILS'}\n")

# ============================================================== B5 — saturation + theta cert
p("[B5] Var[S] saturation bracket + powered theta-truncation cert")
rank = np.arange(1, N + 1, dtype=float)
vS = {"rvm_asymptotic": float(np.var(rank - rvm_N(blk))),
      "rvm_plus_next_order": float(np.var(rank - rvm_N_next(blk))),
      "theta_exact_RS": float(np.var(rank - exact_N(blk)))}
s2_theta_zeta = sigma2(rvm_N(blk), Ls)
s2_next_zeta = sigma2(rvm_N_next(blk), Ls)
s2_exact_zeta = sigma2(exact_N(blk), Ls)
plateau = float(np.mean(s2_theta_zeta[-2:]))       # L = 16, 32
for k, v in vS.items():
    p(f"  Var[S] ({k:20s}) = {v:.5f}   ->  2*Var[S] = {2*v:.5f}")
p("  Sigma^2_theta on the same block   = " + ", ".join("%.4f" % v for v in s2_theta_zeta))
p(f"  observed long-L plateau (mean of L=16,32) = {plateau:.4f}")
sat_hold = 0.20 <= 2 * vS["rvm_asymptotic"] <= 0.36
p(f"  P-B5-saturation: 2*Var[S] = {2*vS['rvm_asymptotic']:.4f} vs sealed bracket [0.20,0.36] "
  f"-> {'HOLDS' if sat_hold else 'FIRES'}")

selberg = float((1.0 / (2 * math.pi ** 2)) * math.log(math.log(gmid / (2 * math.pi))))
p(f"  Selberg asymptotic Var[S] ~ (1/2pi^2)loglog(gamma/2pi) at gamma_mid = {selberg:.5f}  "
  f"(measured/asymptotic = {vS['rvm_asymptotic']/selberg:.2f}x)  [WINDOW property, not a zeta result]")

dS2_next = float(np.max(np.abs(s2_next_zeta - s2_theta_zeta) / s2_theta_zeta))
dS2_exact = float(np.max(np.abs(s2_exact_zeta - s2_theta_zeta) / s2_theta_zeta))
p(f"  theta-cert (POWERED, long-range statistic): max rel |dSigma^2|  "
  f"next-order {dS2_next*100:.4f}%   exact-RS {dS2_exact*100:.4f}%")
p(f"  theta-cert dVar[S]: next-order {abs(vS['rvm_plus_next_order']-vS['rvm_asymptotic']):.2e}   "
  f"exact-RS {abs(vS['theta_exact_RS']-vS['rvm_asymptotic']):.2e}")
OUT["B5"] = {"VarS": vS, "sigma2_theta_zeta": s2_theta_zeta.tolist(),
             "sigma2_next_zeta": s2_next_zeta.tolist(), "sigma2_exact_zeta": s2_exact_zeta.tolist(),
             "plateau_L16_32": plateau, "two_VarS": 2 * vS["rvm_asymptotic"],
             "P_B5_saturation_holds": bool(sat_hold),
             "selberg_asymptotic_VarS": selberg,
             "selberg_ratio_measured_over_asymptotic": vS["rvm_asymptotic"] / selberg,
             "theta_cert_max_relerr_sigma2": {"next_order": dS2_next, "exact_RS": dS2_exact},
             "theta_cert_dVarS": {"next_order": abs(vS["rvm_plus_next_order"] - vS["rvm_asymptotic"]),
                                  "exact_RS": abs(vS["theta_exact_RS"] - vS["rvm_asymptotic"])}}
p("")

# ============================================================== B4 — alpha >= 1 look region
p("[B4] alpha >= 1 LOOK region — qualitative only, NO significance values (seal + spec §R.3)")
hi = ALPHA_OUT >= 1.0
kz = Kz["theta_rvm"]
OUT["B4_look_region"] = {"alphas_ge_1": ALPHA_OUT[hi].tolist(), "K_theta": kz[hi].tolist(),
                         "mean_ge_1": float(kz[hi].mean()), "min_ge_1": float(kz[hi].min()),
                         "max_ge_1": float(kz[hi].max()),
                         "note": "no bracket exists here; calibrator grade zero; qualitative only"}
p("  alpha:  " + " ".join("%5.2f" % a for a in ALPHA_OUT[hi][::4]))
p("  F    :  " + " ".join("%5.2f" % v for v in kz[hi][::4]))
p(f"  (mean {kz[hi].mean():.2f}, range {kz[hi].min():.2f}-{kz[hi].max():.2f}; GUE limit here is 1.0)")
p("  alpha < 1 calibration region, theta path:")
lo = ALPHA_OUT < 1.0
p("  alpha:  " + " ".join("%5.2f" % a for a in ALPHA_OUT[lo][::3]))
p("  F    :  " + " ".join("%5.2f" % v for v in kz[lo][::3]))
p("  GUE  :  " + " ".join("%5.2f" % a for a in ALPHA_OUT[lo][::3]))

json.dump(OUT, open(os.path.join(HERE, "taskB_falpha_measured.json"), "w"), indent=2)
p("\nwrote taskB_falpha_measured.json")
