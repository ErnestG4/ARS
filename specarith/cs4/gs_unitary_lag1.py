"""Estimator B (twenty-fourth round), sine-kernel step: the predicted lag-1 window correlation for GUE,
ρ₁ = Cov(S(c), S(c + 3b))/V(b), Cov(R)/b = (1/√2) ∫_ℝ exp(−π(r − R)²/2b²) C(r) dr, from the full sine-kernel connected
function (gs_unitary.C_full; it decays, so no split is needed). Then E[v̂_B] = v(b)(1 − ρ₁) and g_B.
v(b) from gs_unitary.v_direct (as in GS_UNITARY_RESULTS.md).

  python gs_unitary_lag1.py OUT        -> OUT/gs_unitary_lag1.json
"""
import json
import math
import os
import sys

import numpy as np

import gs_unitary as G

DR = 0.2


def cov_over_b(b, R):
    s = b / math.sqrt(math.pi)
    r = np.arange(0.0, R + 6 * s + DR, DR)
    k = np.exp(-math.pi * (r - R) ** 2 / (2 * b * b)) + np.exp(-math.pi * (r + R) ** 2 / (2 * b * b))
    w = k * G.C_full(r)
    return DR * (0.5 * w[0] + np.sum(w[1:])) / math.sqrt(2)


def main(out):
    rows = {}
    for b in G.LADDER:
        v, _ = G.v_direct(b)
        c1 = cov_over_b(b, 3.0 * b)
        rows[b] = dict(v=v, cov1_over_b=c1, rho1=c1 / v, vB=v - c1)
        print("b=%6d  v %.6f  ρ₁ %+.2e  v(1−ρ₁) %.6f" % (b, v, c1 / v, v - c1), flush=True)
    gB = math.sqrt(rows[10_000]["vB"] / rows[100]["vB"])
    g = math.sqrt(rows[10_000]["v"] / rows[100]["v"])
    print("g %.6f   g_B %.6f" % (g, gB))
    os.makedirs(out, exist_ok=True)
    json.dump(dict(rows=rows, g=g, g_B=gB), open(os.path.join(out, "gs_unitary_lag1.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
