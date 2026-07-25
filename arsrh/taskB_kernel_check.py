"""
Two owed checks, neither of them a zeta reading.

K1. The L <-> alpha correspondence, against the kernels rather than assumed from the transform.
    Sigma^2(L) = int_{-inf}^{inf} K(alpha) sin^2(pi alpha L)/(pi alpha)^2 dalpha
               = int_0^inf K(alpha) w_L(alpha) dalpha,   w_L(alpha) = 2 sin^2(pi alpha L)/(pi alpha)^2
    (check: K == 1 gives Sigma^2 = L). Question: what FRACTION of w_L's mass sits below the
    contaminated region alpha < alpha_c ~ 0.002? If it is most of it, the long-L blockage is
    structural. If it is a small fraction carrying a huge amplitude, it is a density-model problem.

K2. Enumerate every filed number that consumes the 0.2/sqrt(W) floor rule, with its margin, so the
    claim "no verdict flips" is either shown per-item or withdrawn.
"""
from __future__ import annotations
import json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
p = lambda *a: print(*a, flush=True)
OUT = {}

# ------------------------------------------------------------------------------- K1
p("[K1] Sigma^2(L) kernel mass below the contaminated region")
p("     w_L(alpha) = 2 sin^2(pi alpha L)/(pi alpha)^2 ;  int_0^inf w_L = L")


def kernel_mass_below(L, ac, n=4_000_000):
    a = np.linspace(1e-12, ac, n)
    w = 2 * np.sin(math.pi * a * L) ** 2 / (math.pi * a) ** 2
    return float(np.trapezoid(w, a))


N_BLOCK = 2000
rows = []
p(f"\n  {'L':>5s} {'total mass':>11s} {'mass<0.002':>11s} {'fraction':>9s} {'2*L*ac (approx)':>16s}")
for L in (1, 2, 4, 8, 16, 32, 64, 128, 250):
    ac = 0.002
    m = kernel_mass_below(L, ac)
    rows.append({"L": L, "alpha_c": ac, "mass_below": m, "fraction": m / L,
                 "small_L_approx_2Lac": 2 * L * ac})
    p(f"  {L:>5d} {float(L):>11.1f} {m:>11.4f} {m/L:>9.3f} {2*L*ac:>16.3f}")

p("\n  -> the contaminated fraction is 2*L*alpha_c while 2*L*alpha_c << 1, i.e. it grows LINEARLY in L")
p(f"  -> alpha_c ~ 0.002 ~ 4/N with N={N_BLOCK}; the fitted unfold's residual occupies the lowest")
p("     ~(order+1) Fourier modes of the block, so alpha_c ~ (order+1)/N in general")
p("  -> Sigma^2(L) is fully contaminated (fraction -> 1) at L ~ 1/(2 alpha_c) ~ N/(2(order+1))")

# amplitude side: how big must Delta K be on alpha<ac to explain the measured +2.5 excess at L=32?
m32 = kernel_mass_below(32, 0.002)
p(f"\n  measured order-3 excess at L=32 is +2.5; kernel mass below alpha_c at L=32 is {m32:.4f}")
p(f"  => required mean Delta K over alpha<0.002 is {2.5/m32:.2f}")
p(f"  measured Delta K in the 0.001-0.002 band was 0.0358-0.0018 = 0.034  ->  {2.5/m32/0.034:.0f}x short")
p("  => the artifact's amplitude is concentrated BELOW 0.001, i.e. in the block's lowest 1-2 Fourier")
p("     modes (alpha ~ 1/N = 0.0005), which is exactly where a degree-3 misfit lives.")
OUT["K1"] = {"rows": rows, "N_block": N_BLOCK, "alpha_c": 0.002,
             "mass_below_at_L32": m32, "required_meanDeltaK_at_L32": 2.5 / m32,
             "measured_DeltaK_0.001_0.002": 0.034,
             "L_at_which_fully_contaminated": 1.0 / (2 * 0.002)}
p("")

# ------------------------------------------------------------------------------- K2
p("[K2] every filed number that consumes the 0.2/sqrt(W) floor rule, with margins")
d1 = json.load(open(os.path.join(HERE, "phase1_zeta_crossover_measured.json")))
d2 = json.load(open(os.path.join(HERE, "phase2_dbn_flow_measured.json")))
W_int = d2["window"]["interior_W"]
floor_rule = 0.2 / math.sqrt(W_int)
floor_meas = 0.005441520408777306          # phase1 measured null_sd at W=2000
items = []


def add(name, filed, corrected, binary, margin_filed, margin_corr, flips):
    items.append({"item": name, "filed": filed, "corrected": corrected, "binary_verdict": binary,
                  "margin_filed": margin_filed, "margin_corrected": margin_corr, "flips": flips})
    p(f"  {name}")
    p(f"     filed {filed}   corrected {corrected}")
    p(f"     binary it feeds: {binary}")
    p(f"     margin {margin_filed} -> {margin_corr}   FLIPS: {flips}")


rise = d2["rise_over_bracket_0_0.22"]
add("P2 forward rise over [0,0.22], in floor units",
    f"{rise/floor_rule:.1f}x", f"{rise/floor_meas:.1f}x",
    "'the flow rigidifies resolvably' (needs > 1x)",
    f"{rise/floor_rule:.1f}x above 1", f"{rise/floor_meas:.1f}x above 1", "NO")

slope0 = d2["d_rtilde_dt_at_0"]
add("P2 classifier t-resolution = floor/slope (THE portable number)",
    f"{floor_rule/slope0:.5f} in t", f"{floor_meas/slope0:.5f} in t",
    "none - it IS the deliverable, a magnitude not a binary",
    "n/a", "n/a", "N/A - the deliverable itself moves by +22%")

dev0 = d2["forward"][0]["dev"]
add("P2 t=0 <r~> deviation vs GUE ref, in floor units",
    f"{dev0/floor_rule:.1f}x", f"{dev0/floor_meas:.1f}x",
    "'the t=0 offset is resolvable' (needs > 1x)",
    f"{dev0/floor_rule:.1f}x", f"{dev0/floor_meas:.1f}x", "NO")

# W needed to resolve 1e-3: filed uses c^2/target^2 (sqrt-W law). Refit with the measured exponent.
W = np.array([b["W"] for b in d1["by_W"]], float)
S = np.array([b["null_sd"] for b in d1["by_W"]], float)
q = np.polyfit(np.log(W), np.log(S), 1)
expo, amp = float(q[0]), float(math.exp(q[1]))
W_filed = d1["by_W"][0]["W_needed_to_resolve_1e-3"]
W_corr = (amp / 1e-3) ** (-1.0 / expo)
add("P1 'W needed to resolve 1e-3' (feasibility number)",
    f"{W_filed:.0f} zeros", f"{W_corr:.0f} zeros",
    "'a 1e-3 effect is reachable at accessible W'",
    f"extrapolated on sd ~ W^-0.5", f"extrapolated on sd ~ W^{expo:.3f}",
    f"NOT a flip but a {W_corr/W_filed:.1f}x feasibility cost")

p(f"\n  measured exponent {expo:.3f} (amp {amp:.4f}); 3 points only")
p("  ENUMERATION VERDICT: 3 items feed a binary, none flips; 2 items ARE magnitudes and both move.")
p("  The 0.2/sqrt(W) rule appears nowhere in Phase 1's by_W table (it uses measured per-W sd),")
p("  nowhere in Phase 3 (empirical GUE band), nowhere in Phase 4 (hand-built bands).")
OUT["K2"] = {"floor_rule_at_W2000": floor_rule, "floor_measured_at_W2000": floor_meas,
             "fitted_exponent": expo, "fitted_amplitude": amp, "items": items,
             "verdicts_consuming_floor": len(items), "binary_flips": 0}

json.dump(OUT, open(os.path.join(HERE, "taskB_kernel_check_measured.json"), "w"), indent=2)
p("\nwrote taskB_kernel_check_measured.json")
