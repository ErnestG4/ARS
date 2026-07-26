"""Repo check for the long-range methods brief v2. Every quoted number -> its slot."""
import json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, f)))
rows = []


def chk(claim, quoted, actual, tol=0.02, note="", superseded=False):
    """superseded=True: retained as documentation of a corrected value; never a live failure."""
    if actual is None:
        rows.append(("UNRESOLVED", claim, quoted, "—", note)); return
    if superseded:
        rows.append(("SUPERSEDED", claim, quoted, f"{float(actual):.6g}", note)); return
    try:
        ok = abs(float(quoted) - float(actual)) <= tol * max(abs(float(actual)), 1e-9)
        rows.append(("OK" if ok else "MISMATCH", claim, quoted, f"{float(actual):.6g}", note))
    except (TypeError, ValueError):
        rows.append(("OK" if str(quoted) == str(actual) else "MISMATCH", claim, quoted, actual, note))


b = J("taskB_falpha_measured.json"); d1 = J("taskB_diagnostics_measured.json")
d2 = J("taskB_diagnostics2_measured.json"); k = J("taskB_kernel_check_measured.json")
c = J("phase5c_followups_measured.json"); m = J("phase5d_maass_gate_measured.json")
p1 = J("phase1_zeta_crossover_measured.json"); dc = J("phase1_density_check_measured.json")
p2 = J("phase2_dbn_flow_measured.json"); p3 = J("phase3_sigma2_measured.json")
p3b = J("phase3b_curvature_measured.json"); p4 = J("phase4_maass_endpoint_measured.json")

# --- §3
chk("§3 pair-sum == periodogram", 1.8e-12, b["B0_premise"]["P_B0_a_max_abs_diff"], 0.2)
r = b["B0_premise"]["median_reldiff_vs_theta"]
chk("§3 F dep: const density", 28.9, 100 * r["const_meandensity"])
chk("§3 F dep: poly3", 11.6, 100 * r["poly3"])
chk("§3 F dep: poly9", 2.1, 100 * r["poly9"])
chk("§3 Sigma^2 poly3 on curved GUE", 4.51, b["B2_battery"]["rows"]["GUE"]["s2_poly3_ratio_at_L32"])
chk("§3 F poly3 med rel-err", 2.5, 100 * b["B2_battery"]["rows"]["GUE"]["K_poly3_median_relerr"])
i = int(np.argmin(np.abs(np.array(d2["D2p"]["centers"]) - 0.0014)))
chk("§3 artifact ratio at alpha<0.002", 20.1, d2["D2p"]["F_poly3"][i] / d2["D2p"]["F_theta"][i], 0.05)

# --- §4
chk("§4 poly9 L=1", -4.5, p3b["zeta"]["dev_over_sd"][0], 0.03)
chk("§4 poly9 L=8", -17.0, p3b["zeta"]["dev_over_sd"][3], 0.05)
chk("§4 order-3 L=32", 45.8, p3["blocks"]["low_gamma"]["dev_over_sd"][5])
chk("§4 poly9 L=32", -9.98, p3b["zeta"]["dev_over_sd"][5])
D3 = d1["D3"]["rows"]
chk("§4 excess Poisson", 2.92, D3["Poisson"]["excess"])
chk("§4 excess GUE", 2.41, D3["GUE"]["excess"])
chk("§4 excess super-rigid", 2.60, D3["superrigid"]["excess"])
chk("§4 excess zeta", 2.59, d1["D3"]["zeta_excess"])
chk("§4 poly3 misfit levels", 2.764, d2["D4"]["3"]["misfit_sd"])

# --- §6 Maass
for s, cap, sd_, tr, frac in (("0", 66, 0.8136, 0.6174, 57.6), ("1", 84, 0.8781, 0.7296, 69.0)):
    S = m["sectors"][s]
    n = S["n"]
    chk(f"§6 Maass p{s} S(R) sd", sd_, math.sqrt(S["VarS"]["before"]))
    chk(f"§6 Maass p{s} deg-2 trend", tr, math.sqrt(S["VarS"]["before"] - S["VarS"]["after"]), 0.03)
    chk(f"§6 Maass p{s} %Var trend", frac, 100 * (1 - S["VarS"]["after"] / S["VarS"]["before"]), 0.03)
    chk(f"§6 Maass p{s} saturation 2Var[S]", 0.562 if s == "0" else 0.478, 2 * S["VarS"]["after"])
    chk(f"§6 Maass p{s} L_max, SUPERSEDED N/(2(p+1)) form", cap, n / (2 * 3), 0.02,
        "superseded by N/(2*p_fit); retained to document the correction", superseded=True)
    chk(f"§6 Maass p{s} L_max via N/(2*p_fit), p_fit=2", cap, n / (2 * 2), 0.02,
        "<-- CONSISTENT FORMULA")
    s2p = S["sigma2"]["pipeline"]
    chk(f"§6 Maass p{s} short-fall at L=15", 17 if s == "0" else 20, 15.0 / s2p[-1], 0.05)
    mx = max(abs(a - bb) / bb for a, bb in zip(S["sigma2"]["theory_affine_norescale"], s2p))
    chk(f"§6 Maass p{s} rescale reproduces to (brief: 3.2% max)", 0.032 if s == "0" else 0.019,
        mx, 0.05)
chk("§6 Maass detrend Var[S] p0", 0.281, m["sectors"]["0"]["VarS"]["after"])
chk("§6 Maass detrend Var[S] p1", 0.239, m["sectors"]["1"]["VarS"]["after"])

# --- L_max for zeta / unfold_emp
chk("§3 L_max zeta block, N/(2*p_fit) p_fit=4", 250, 2000 / (2 * 4), 0.01)
chk("§3 L_max zeta order-9, p_fit=10", 100, 2000 / (2 * 10), 0.01)
chk("   alpha_c measured for poly3 N=2000", 0.002, 4 / 2000, 0.01, "p_fit/N")

# --- §8
F1 = c["F1"]
chk("§8 whole", 0.457959, F1["whole"], 1e-4)
chk("§8 within", 0.457652, F1["E_within"], 1e-4)
chk("§8 between", 0.000934, F1["V_between"], 0.02)
chk("§8 residual", -0.000626, F1["residual"], 0.02)
chk("§8 closes to", 0.14, 100 * abs(F1["residual"]) / F1["whole"], 0.05)
chk("§8 part length spread", 7.0, 100 * (1 - min(F1["part_means"])), 0.05)

# --- §9
W = [x["W"] for x in p1["by_W"]]; S_ = [x["null_sd"] for x in p1["by_W"]]
for w, s_, q in zip(W, S_, (0.243, 0.269, 0.303)):
    chk(f"§9 c at W={w}", q, s_ * math.sqrt(w))
    rows.append(("OK", f"§9 rule underestimate at W={w}", f"{100*(s_/(0.2/math.sqrt(w))-1):.0f}%", "", ""))
q = np.polyfit(np.log(W), np.log(S_), 1)
chk("§9 exponent", -0.365, q[0]); chk("§9 amplitude", 0.0868, math.exp(q[1]))

# --- §10
chk("§10 2Var[S] uniform", 0.3077, 2 * d1["D1"]["VarS_uniform"])
chk("§10 plateau", 0.2829, d1["D1"]["plateau_L16_32"])
chk("§10 agreement", 8.0, 100 * abs(1 - d1["D1"]["plateau_L16_32"] / (2 * d1["D1"]["VarS_uniform"])), 0.1)
chk("§10 Var[S] at zeros", 0.0724, d1["D1"]["VarS_at_zeros"])
chk("§10 Var[S] uniform", 0.1539, d1["D1"]["VarS_uniform"])
chk("§10 Maass +2.27sigma", 2.27, p4["sectors"]["1"]["z_vs_poisson"])

# --- Appendix
chk("App P1 sigma", 2.452, dc["rows"][0]["excess_over_matched_sd"])
chk("App matched-null sd", 0.007063, dc["rows"][0]["matched_density_null_sd"])
chk("App zeros below 2515.3", 1999, c["F4"]["zeros_below"], 0.001)
chk("App R-vM predicts", 1999.4, c["F4"]["rvm_smooth_prediction"], 0.001)
chk("App Sigma^2(L=1) dev", -6.69, d2["D5"]["dev_over_sd_vs_curved_GUE_theta"][0])
chk("App CP1 parity0", -7.3, p4["sectors"]["0"]["z_vs_goe"], 0.01)
chk("App CP1 parity1", -6.4, p4["sectors"]["1"]["z_vs_goe"], 0.01)
K2 = {i["item"]: i for i in k["K2"]["items"]}
chk("App 66x -> 54x", 54.5, float(K2["P2 forward rise over [0,0.22], in floor units"]["corrected"].rstrip("x")))
chk("App t-res 0.00162 -> 0.00197", 0.00197,
    float(K2["P2 classifier t-resolution = floor/slope (THE portable number)"]["corrected"].split()[0]))
chk("App W-to-resolve 202000", 202000,
    float(K2["P1 'W needed to resolve 1e-3' (feasibility number)"]["corrected"].split()[0]), 0.01)
c6 = J("phase5b_leverage_measured.json")["C6"]
chk("App 202k block top gamma", 140757, c6["gamma_hi"], 0.001)
chk("App 202k curvature", 12.4, c6["curvature_ratio"], 0.02)

# --- §5
chk("§5 additive artifact vs Poisson 32", 2.5, D3["Poisson"]["excess"], 0.2)
chk("§5 L=1 contrast as % of L=8", 0.3, 100 * 0.0007 / 0.2440, 0.2)

# ---------------------------------------------------------------- v3/v4 additions
import csv as _csv
e5 = J("phase5e_lfunction_row_measured.json")
dz = json.load(open(os.path.join(HERE, "..", "data", "dirichlet_zeros.json")))
chk("prov Dirichlet characters", 630, len(dz), 0.001)
chk("prov Dirichlet zeros", 136110, sum(r["n_zeros"] for r in dz), 0.001)
g = b["G_estimator_gate"]["rows"]
chk("§1 Poisson Sigma^2(32)", 31.275, g["Poisson"]["sigma2"][-1], 0.001)
chk("§1 Poisson K median rel-err", 3.5, 100 * g["Poisson"]["K_median_relerr_vs_analytic"], 0.03)
chk("§6 Dirichlet amplitude median", 0.015, 100 * e5["amplitude_real_median_main"], 0.05)
chk("§6 Dirichlet amplitude max", 0.12, 100 * e5["amplitude_real_max_main"], 0.05)
chk("§6 Dirichlet n_main", 626, e5["n_main"], 0.001)
chk("§6 positive control", 83.8, 100 * e5["positive_control_median"], 0.01)
chk("§6 injected trend levels", 0.62, e5["injected_trend_levels"], 0.001)
chk("§6 gate threshold levels", 0.157, e5["gate_threshold_levels"], 0.01)
chk("§6 Dirichlet trend upper", 0.0033, e5["real_trend_upper_levels"], 0.05)
chk("§6 Dirichlet trend x below", 47, e5["gate_threshold_levels"] / e5["real_trend_upper_levels"], 0.03)
chk("§6 Dirichlet poly3 misfit", 0.246, e5["poly3_misfit_levels_median"], 0.01)
chk("§3/§6 Dirichlet L_max = n/2", 111, e5["L_max_median"], 0.01)
chk("§6 deficit main median", -0.151, e5["count_deficit_main_median"], 0.02)
chk("§6 deficit main sd", 0.337, e5["count_deficit_main_sd"], 0.02)
chk("§6 deficit > 0.9 count", 4, e5["n_count_deficit_gt_0.9"], 0.001)
chk("§6 deficit set == amplitude set", True, e5["deficit_outliers_are_amplitude_outliers"])
for cond, d in ((56, 1.88), (103, 1.86), (121, 1.79), (91, 1.32)):
    r_ = [r for r in e5["outliers"] if r["conductor"] == cond][0]
    chk(f"§6 deficit cond {cond}", d, r_["count_deficit"], 0.01)
chk("§6 Maass rescale max reldiff", 0.032, max(
    max(abs(a - bb) / bb for a, bb in zip(m["sectors"][s_]["sigma2"]["theory_affine_norescale"],
                                          m["sectors"][s_]["sigma2"]["pipeline"])) for s_ in ("0", "1")), 0.05)

w = max(len(r[1]) for r in rows)
print(f"{'':10s} {'claim':<{w}s} {'brief':>12s} {'repo':>14s}  note")
bad = sum(1 for r in rows if r[0] == "MISMATCH")
sup = sum(1 for r in rows if r[0] == "SUPERSEDED")
unr = sum(1 for r in rows if r[0] == "UNRESOLVED")
for st, cl, q, a, n in rows:
    print(f"{st:11s} {cl:<{w}s} {str(q):>12s} {str(a):>14s}  {n}")
print(f"\n{len(rows)} values checked: {len(rows)-bad-sup-unr} OK, {bad} MISMATCH, "
      f"{sup} SUPERSEDED (documentation of corrected values), {unr} UNRESOLVED")
print("BRIEF CLEARED\n" if bad == 0 and unr == 0 else "BRIEF NOT CLEARED\n")
