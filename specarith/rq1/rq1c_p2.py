"""RQ1-c P2 (round 95): pre-committed D(10¹²) predictions under three scaling laws, with propagated SEs, and the
separability table. Inputs: the sealed read (results/read/read1.json) at 10¹⁰ and 10¹¹; nothing at 10¹² is read.

Laws, each fitted to D(10¹⁰) and D(10¹¹):
  L1: D = A / log X       A by generalised least squares on the two points (with their covariance);
  L2: D = A / log² X      likewise;
  L3: D = c·X^{−δ}        through both points: δ = ln(D₁₀/D₁₁)/ln 10, D₁₂ = D₁₁²/D₁₀ (defined iff D₁₀, D₁₁ > 0).
SE of D at 10¹⁰ and 10¹¹: the read's SE_diff (sealed model). At 10¹²: the same model at the matched N, n₁₂ ≈ 1.880·10¹⁰
split primes (≈ π(10¹²)/2; replaced by the manifest's row count when it exists), R taken at its 10¹¹ value.
Nesting correlation (each X's set contains the smaller X's): ρ = 0.09 between adjacent X and ρ² between 10¹⁰ and 10¹²,
from the 200 nested null replicates of the B2 witness (β 0.40: +0.016, β 0.45: +0.089, each ± 0.07); sensitivity at
ρ = 0.23 (upper 2-SE bound).
Consistency test at 10¹²: |D − pred| ≤ 2·SE_r, SE_r² = Var(D₁₂ − pred) by the delta method with the full covariance.
Separability: laws a, b differ at a cell iff |pred_a − pred_b| ≥ 3·SE_ab, SE_ab² = Var(pred_a − pred_b) + Var(D₁₂)
(the measurement both comparisons share); a cell where any pair of defined laws is not separable is UNPOWERED for P2.

  python rq1c_p2.py OUT_JSON
"""
import json
import math
import sys

import numpy as np

CELLS = [0.40, 0.45, 0.55, 0.60]
C_SE = 0.6271633049515984
N12 = 2 * 1.880e10
LX = {10: math.log(1e10), 11: math.log(1e11), 12: math.log(1e12)}


def preds(d10, d11, cov):
    """Predictions and gradients (∂/∂D₁₀, ∂/∂D₁₁) for the three laws."""
    out = {}
    for name, p in (("1/logX", 1), ("1/log2X", 2)):
        x = np.array([LX[10] ** -p, LX[11] ** -p])
        Ci = np.linalg.inv(cov)
        w = Ci @ x / (x @ Ci @ x)                    # GLS: A = w·D
        A = w @ np.array([d10, d11])
        out[name] = (A * LX[12] ** -p, w * LX[12] ** -p)
    if d10 > 0 and d11 > 0:
        out["X^-delta"] = (d11 ** 2 / d10, np.array([-(d11 / d10) ** 2, 2 * d11 / d10]))
    return out


def main(out, rho=0.09):
    r = json.load(open("results/read/read1.json"))["rows"]
    row = {X: {x["beta"]: x for x in r[str(10 ** X)]["rows"]} for X in (10, 11)}
    res = dict(label="RQ1-c P2 predictions and separability (pre-committed from 1e10 / 1e11)", rho_adjacent=rho, cells={})
    for b in CELLS:
        a10, a11 = row[10][b], row[11][b]
        d10, d11, s10, s11 = a10["D"], a11["D"], a10["SE_diff"], a11["SE_diff"]
        K12 = round(N12 ** b)
        s12 = math.sqrt(2 / (C_SE * K12)) * math.hypot(a11["R_zs2"], a11["R_zi"])
        cov2 = np.array([[s10 ** 2, rho * s10 * s11], [rho * s10 * s11, s11 ** 2]])
        c12 = np.array([rho ** 2 * s10 * s12, rho * s11 * s12])          # Cov(D₁₂, (D₁₀, D₁₁))
        P = preds(d10, d11, cov2)
        laws = {}
        for name, (pv, g) in P.items():
            var_r = s12 ** 2 + g @ cov2 @ g - 2 * g @ c12
            laws[name] = dict(pred=float(pv), SE_pred=float(math.sqrt(g @ cov2 @ g)), SE_resid=float(math.sqrt(var_r)),
                              consistent_window=[float(pv - 2 * math.sqrt(var_r)), float(pv + 2 * math.sqrt(var_r))])
        sep = {}
        names = list(P)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                ga, gb = P[names[i]][1], P[names[j]][1]
                dg = ga - gb
                se = math.sqrt(dg @ cov2 @ dg + s12 ** 2)
                diff = P[names[i]][0] - P[names[j]][0]
                sep[f"{names[i]} vs {names[j]}"] = dict(diff=float(diff), SE=float(se), ratio=float(abs(diff) / se),
                                                         separable=bool(abs(diff) >= 3 * se))
        res["cells"][f"beta={b}"] = dict(D_1e10=d10, SE_1e10=s10, D_1e11=d11, SE_1e11=s11, K_1e12=K12, SE_1e12=s12,
                                          laws=laws, separability=sep,
                                          P2_status="POWERED" if all(v["separable"] for v in sep.values()) else "UNPOWERED")
    json.dump(res, open(out, "w"), indent=1)
    for c, v in res["cells"].items():
        print(c, f"D10 {v['D_1e10']:+.4f}±{v['SE_1e10']:.4f}  D11 {v['D_1e11']:+.4f}±{v['SE_1e11']:.4f}  SE12 {v['SE_1e12']:.4f}",
              v["P2_status"])
        for n, l in v["laws"].items():
            print(f"    {n:9s} pred {l['pred']:+.4f}  SE_pred {l['SE_pred']:.4f}  window ±{2 * l['SE_resid']:.4f}")
        for n, s in v["separability"].items():
            print(f"    {n}: diff {s['diff']:+.4f}, {s['ratio']:.2f} SE, separable {s['separable']}")
    return res


if __name__ == "__main__":
    main(sys.argv[1], *(float(x) for x in sys.argv[2:3]))
