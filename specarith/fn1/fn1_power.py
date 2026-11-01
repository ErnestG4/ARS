"""FN1 stage 1 (10¹⁰): power and D23 of the sealed rank tests under the sealed SE model and under L13's empirical
fluctuation scales (both methods), as Will required before sealing. Parametric; no new data.

Model: R_F = b·C_F + σ_F·ε_F, with ε i.i.d. N(0, 1).
- b per cell = (R_ℤ[√2] − R_ℤ[i])/(C_ℤ[√2] − C_ℤ[i]) at 10¹⁰ (seen: RQ1 read).
- σ_F = R·√(2/(c K)) × s, with the scale s = 1 (the sealed model) or 1/(model/empirical) from L13 at (10¹⁰, β):
  method A (block arcs) or B (residue subsets), using ℤ[i]'s ratio (the imaginary quadratic one) or ℤ[√2]'s.

The rank test: nine fields, exact one-sided permutation p (9! orderings); PASS iff p < 0.01 and ρ > 0. D23 =
P(PASS | the ordering by C_F exactly true with slope b and noise σ), which is the power at that σ. The secondary
ℤ[√2] prediction: PASS iff R_ℚ(√−67) < R_ℤ[√2] < R_ℚ(√−163) at β 0.55, with ℤ[√2]'s noise scaled by its own L13 ratio.

  python fn1_power.py L13_JSON READ1_JSON CONSTANTS_JSON OUT_JSON
"""
import itertools
import json
import math
import sys

import numpy as np

C_SE = 0.6271633049515984
FIELDS = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
C = dict(zip(FIELDS, [math.log(7), math.log(8), math.log(11), math.log(16), math.log(19), math.log(27),
                      math.log(43), math.log(67), math.log(163)]))
BETAS = [0.55, 0.40, 0.45]
REPS = 100_000
SEED = 20261111


def exact_null(n=9):
    r0 = np.arange(n)
    d2 = np.array([int(((np.array(p) - r0) ** 2).sum()) for p in itertools.permutations(range(n))])
    return np.bincount(d2)


def p_value(d2_obs, counts):
    return counts[: d2_obs + 1].sum() / counts.sum()


def main(l13_json, read1_json, const_json, out):
    L13 = json.load(open(l13_json))
    rd = json.load(open(read1_json))
    cst = json.load(open(const_json))
    C_s2 = C["zi"] + 1.8489                                   # RQ1's ΔC(ℤ[√2], ℤ[i]); Will: C ≈ 4.62
    counts = exact_null()
    d2_crit = max(d for d in range(len(counts)) if p_value(d, counts) < 0.01)
    rho_crit = 1 - 6 * d2_crit / (9 * 80)
    rng = np.random.default_rng(SEED)
    order = np.argsort([C[f] for f in FIELDS])
    assert list(order) == list(range(9))
    res = dict(n_fields=9, exact_null_total=int(counts.sum()), pass_iff=f"sum d^2 <= {d2_crit} (rho >= {rho_crit:.4f}, "
               f"p = {p_value(d2_crit, counts):.5f} < 0.01)", C=C, C_zs2=C_s2, cells={})
    rows = {r["beta"]: r for r in rd["rows"]["10000000000"]["rows"]}
    N = rd["rows"]["10000000000"]["N"]
    for b in BETAS:
        r = rows[b]
        K = r["K"]
        slope = (r["R_zs2"] - r["R_zi"]) / (C_s2 - C["zi"])
        cell = L13["X"]["10000000000"]["fields"]
        sc = {"model": 1.0}
        for f in ("zi", "zs2"):
            c = cell[f][str(b)] if str(b) in cell[f] else cell[f][b]
            Mp = str(c["block_primary_M"])
            sc[f"A_{f}"] = 1 / c["block"][Mp]["ratio_model_over_emp"]
            sc[f"B_{f}"] = 1 / c["subset_pooled"]["ratio_model_over_emp"]
        Rbar = 0.5 * (r["R_zs2"] + r["R_zi"])
        se = Rbar * math.sqrt(2 / (C_SE * K))
        Cv = np.array([C[f] for f in FIELDS])
        out_c = dict(K=K, slope_b=slope, model_SE=se, scales=sc, power={}, zs2_secondary={})
        for name, s in sc.items():
            R = slope * Cv[None, :] + se * s * rng.standard_normal((REPS, 9))
            rk = R.argsort(1).argsort(1)
            d2 = ((rk - np.arange(9)) ** 2).sum(1)
            out_c["power"][name] = float((d2 <= d2_crit).mean())
            if b == 0.55:
                s_zs2 = sc["model"] if name == "model" else sc[name.split("_")[0] + "_zs2"]
                r67 = slope * C["-67"] + se * s * rng.standard_normal(REPS)
                r163 = slope * C["-163"] + se * s * rng.standard_normal(REPS)
                rs2 = slope * C_s2 + se * s_zs2 * rng.standard_normal(REPS)
                out_c["zs2_secondary"][name] = float(((r67 < rs2) & (rs2 < r163)).mean())
        res["cells"][str(b)] = out_c
        print(f"beta {b}: K {K} b {slope:.4f} model SE {se:.4f}; noise scales "
              + ", ".join(f"{k} {v:.1f}x" for k, v in sc.items()))
        print("   power (= D23):", {k: round(v, 3) for k, v in out_c["power"].items()})
        if b == 0.55:
            print("   Z[sqrt2] between -67 and -163:", {k: round(v, 3) for k, v in out_c["zs2_secondary"].items()})
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
