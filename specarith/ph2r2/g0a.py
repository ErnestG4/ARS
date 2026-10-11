"""R₂ pre-read G0a (PH2R2_SEAL 1.0 §4): the CS07 Theorem 4.1 kernel against independent known answers. No zero is read.

1. A-factor identity: the direct Euler factor (1 − p^{−1−η})(1 − 2/p + p^{−1−η})/(1 − 1/p)² equals
   1 − (1 − p^{−η})²/(p − 1)² (per prime, random η = ir).
2. B(0) = Σ_p log²p/(p − 1)² = c₀ = Λ − γ₀² − 2γ₁ (Phase 2's exact constant; BFM/BBLM), with the tail beyond P_MAX
   bounded; A(0) = 1 exactly.
3. Prime-cutoff convergence of A(ir), B(ir): P = 10⁶ vs 10⁷.
4. Large-L limit: R(t, r)/(L/2π)² at fixed s = r L/2π → Montgomery 1 − (sin πs/πs)² as t → ∞.
5. Leading lower-order term: L²·[R/(L/2π)² − (1 − sinc²(πs))] at fixed s → −4Λ sin²(πs)
   (BBLM eq. 16: R₂ = 1 − sinc² − (Λ/(π²ρ̄²)) sin²(πs) + O(ρ̄⁻³), ρ̄ = L/2π). This ties CS07 to the Λ of Phase 2.

  python g0a.py OUT
"""
import json
import math
import os
import sys

import numpy as np

import r2lib as R

LAMBDA = 1.5731510713249552           # BFM 2017 (Phase 2 G0a reproduced it from the prime-zeta series)
EULER_G0 = 0.5772156649015329
STIELTJES_G1 = -0.07281584548367672


def main(out):
    res = {}
    # 1. identity, per prime
    rng = np.random.default_rng(1)
    p = R.primes()[:2000]
    worst = 0.0
    for r in rng.uniform(-50, 50, 20):
        eta = 1j * r
        x = p ** (-1 - eta)
        direct = (1 - x) * (1 - 2 / p + x) / (1 - 1 / p) ** 2
        ident = 1 - (1 - p ** (-eta)) ** 2 / (p - 1) ** 2
        worst = max(worst, float(np.max(np.abs(direct - ident))))
    res["A_identity_max_abs_diff"] = worst

    # 2. B(0) = c0, A(0) = 1
    c0_exact = LAMBDA - EULER_G0 ** 2 - 2 * STIELTJES_G1
    B0 = float(np.real(R.B_ir([0.0])[0]))
    tail_bound = math.log(R.P_MAX) ** 2 / (R.P_MAX * math.log(R.P_MAX)) * 1.1   # Σ_{p>P} log²p/p² ≲ log P / P
    res["B0"] = B0
    res["c0_exact"] = c0_exact
    res["B0_minus_c0"] = B0 - c0_exact
    res["B0_tail_bound"] = tail_bound
    res["A0"] = complex(R.A_ir([0.0])[0]).real

    # 3. prime-cutoff convergence
    rr = np.array([0.05, 0.3, 1.0, 3.0, 10.0])
    a6, a7 = R.A_ir(rr, 10 ** 6), R.A_ir(rr, 10 ** 7)
    b6, b7 = R.B_ir(rr, 10 ** 6), R.B_ir(rr, 10 ** 7)
    res["A_1e6_vs_1e7_max"] = float(np.max(np.abs(a6 - a7)))
    res["B_1e6_vs_1e7_max"] = float(np.max(np.abs(b6 - b7)))

    # 4–5. Montgomery limit and the Λ coefficient at fixed scaled separations s
    s_vals = np.array([0.25, 0.5, 0.75, 1.0, 1.5])
    rows = []
    for L in (14.0, 22.0, 50.0, 100.0, 200.0):
        t = 2 * math.pi * math.exp(L)
        r = 2 * math.pi * s_vals / L
        K = R.Kernel(r)
        dens = K.R(t) / (L / (2 * math.pi)) ** 2
        mont = 1 - (np.sin(np.pi * s_vals) / (np.pi * s_vals)) ** 2
        coeff = L * L * (dens - mont)
        rows.append(dict(L=L, max_abs_dens_minus_montgomery=float(np.max(np.abs(dens - mont))),
                         L2_times_deviation=coeff.tolist(), predicted=(-4 * LAMBDA * np.sin(np.pi * s_vals) ** 2).tolist()))
        print(f"L={L}: max|R/ρ̄² − Montgomery| = {rows[-1]['max_abs_dens_minus_montgomery']:.2e}; "
              f"L²·dev = {np.round(coeff, 4)} vs −4Λ sin² = {np.round(-4 * LAMBDA * np.sin(np.pi * s_vals) ** 2, 4)}",
              flush=True)
    res["montgomery_and_lambda"] = rows
    # error relative to the largest prediction (sin²(πs) vanishes at s = 1, so a pointwise relative error is undefined
    # there); the remainder is O(ρ̄⁻³), so the error must roughly halve from L = 100 to L = 200
    err = {row["L"]: float(np.max(np.abs(np.array(row["L2_times_deviation"]) - np.array(row["predicted"]))))
           for row in rows}
    scale = float(np.max(np.abs(rows[-1]["predicted"])))
    res["lambda_coeff_err_rel_to_max"] = {str(L): e / scale for L, e in err.items()}
    res["lambda_coeff_err_ratio_200_over_100"] = err[200.0] / err[100.0]
    res["lambda_coeff_rel_err_at_L200"] = err[200.0] / scale
    res["PASS"] = bool(worst < 1e-14 and abs(res["A0"] - 1) < 1e-14 and abs(B0 - c0_exact) <= tail_bound
                       and res["A_1e6_vs_1e7_max"] < 1e-5 and res["B_1e6_vs_1e7_max"] < 1e-4
                       and rows[-1]["max_abs_dens_minus_montgomery"] < rows[0]["max_abs_dens_minus_montgomery"]
                       and res["lambda_coeff_rel_err_at_L200"] < 0.05
                       and 0.3 < res["lambda_coeff_err_ratio_200_over_100"] < 0.7)
    print(json.dumps({k: v for k, v in res.items() if k != "montgomery_and_lambda"}, indent=1, default=float))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "g0a.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1])
