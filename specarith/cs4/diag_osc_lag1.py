"""Estimator B (twenty-fourth round): the amendment-7 check for the new term. The prediction is
E[v̂_B(b)] = v(b) − Cov(3b)/b, and Cov is computed, like V, from the kept (non-oscillating) long-range part. This checks
that the dropped ℓ-oscillating part's contribution to Cov(3b) averages to ≈ 0 over the file, as for V (lag 0).

Pair (5,5) (the heaviest), at one ℓ of the 64 stratified points of the F2 15.75 file (diag_osc_lavg.dense_nodes()),
Δr = 0.1 on r ∈ [5, 6·10⁴]. For each rung b it stores the osc and non integrals against (1 − χ)·exp(−π(r − R)²/2b²),
two-sided (∫_ℝ, C even), for R = 0 and R = 3b.

  python diag_osc_lag1.py ELL OUT             -> OUT/lag1_L{ELL}.json
  python diag_osc_lag1.py summary OUT         file average over the 64 ℓ (weights ∝ ℓe^ℓ), as fractions of v(b)
"""
import json
import math
import os
import sys

import numpy as np

import gs_unitary as G
import gs_zeta as Z

R_MAX = 60_000.0
I = J = 5


def kern(r, b, R):
    g = lambda x: np.exp(-math.pi * x ** 2 / (2 * b * b))
    return g(r - R) + g(r + R)


def main(ell, out):
    import cs4lr as LR
    lr = LR.LongRangeZeta(Z.tval(ell), pmax=Z.PMAX)
    n = int(round((R_MAX - Z.R_LO) / 0.1)) + 1
    n += n % 2
    r = Z.R_LO + 0.1 * np.arange(n)
    o, nn = lr.connected(Z.DN[I], Z.DN[J], r)
    cl = 1 - G.chi(r)
    res = dict(ell=ell, i=I, j=J)
    for name, f in (("osc", o.real), ("non", nn.real)):
        for b in Z.LADDER:
            for lag, R in ((0, 0.0), (1, 3.0 * b)):
                res[f"{name}_b{b}_lag{lag}"] = float(0.1 * np.sum(cl * kern(r, b, R) * f))
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"lag1_L{ell!r}.json"), "w"), indent=1)
    print(ell, "done", flush=True)


def summary(out):
    import diag_osc_lavg as A
    ells, wts = A.dense_nodes()
    rows = [json.load(open(os.path.join(out, f"lag1_L{ell!r}.json"))) for ell in ells]
    v = json.load(open(os.path.join("results", "gs_zeta", "gs_zeta_L15.7502.json")))["v"]
    w = 4 * (Z.DW[I] * Z.FD[I]) ** 2 / math.sqrt(2)          # pair (5,5)'s weight in v(b) (and in Cov/b)
    res = {}
    for b in Z.LADDER:
        row = {}
        for lag in (0, 1):
            osc = np.array([x[f"osc_b{b}_lag{lag}"] for x in rows])
            avg, se = float(np.dot(wts, osc)), float(osc.std(ddof=1) / math.sqrt(len(osc)))
            row[f"lag{lag}"] = dict(avg_over_v=w * avg / v[str(b)], se_over_v=w * se / v[str(b)],
                                   max_over_v=w * float(np.abs(osc).max()) / v[str(b)])
        # the estimator-B prediction carries V − Cov(3b): the dropped osc part enters as (lag0 − lag1)
        d = np.array([x[f"osc_b{b}_lag0"] - x[f"osc_b{b}_lag1"] for x in rows])
        row["B_term"] = dict(avg_over_v=w * float(np.dot(wts, d)) / v[str(b)],
                             se_over_v=w * float(d.std(ddof=1) / math.sqrt(len(d))) / v[str(b)])
        res[b] = row
        print("b=%5d  lag0 %+.1e ± %.1e (max-ℓ %.1e) | lag1 %+.1e ± %.1e (max-ℓ %.1e) | B term %+.1e ± %.1e   [of v]"
              % (b, row["lag0"]["avg_over_v"], row["lag0"]["se_over_v"], row["lag0"]["max_over_v"],
                 row["lag1"]["avg_over_v"], row["lag1"]["se_over_v"], row["lag1"]["max_over_v"],
                 row["B_term"]["avg_over_v"], row["B_term"]["se_over_v"]))
    json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    summary(sys.argv[2]) if sys.argv[1] == "summary" else main(float(sys.argv[1]), sys.argv[2])
