# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2: (★)'s predictions, committed before any χ′-control or h = 2 compute (Will, 2026-11-03, D5: "Before computing,
commit (★)'s prediction for each h = 1 field under "runs in X" and under "runs in N"."). Desk arithmetic; no data.

(★) (lead/FN1H2_R_DERIVATION.md §2): E[R](C; L, K) = Σ_{k≠0} w_K(k) · min(1, (C + 2 log|k|)/L),
w_K(k) = K sin²(πk/K)/(πk)² (Σ_{k≠0} w_K = 1 − 1/K). Evaluated exactly: for |k| ≥ k_sat = ⌈e^{(L−C)/2}⌉ the min is 1
and that part is (1 − 1/K) − Σ_{|k|<k_sat} w_K(k).

The two variables (the §4 robustness table, made explicit per field):
- **runs in X:** L = log X, X = the prime-norm cutoff. Every set here has X = X* = 2·10¹⁰.
- **runs in N:** L = log X_N(N), X_N(N) = li⁻¹(N): the cutoff at which an h = 1 set (split fraction ½, mirrored) has N
  points, since then N ≈ π(X) ≈ li(X). The h = 1 reference at X* has N ≈ li(X*), so X_N = X* for it by construction.
  A set with half the points (the χ′-thinned control, or an h = 2 principal set) has X_N = li⁻¹(li(X*)/2).

K: the fixed K_P of the draft as revised (stage 1's K at β 0.55 / 0.45 / 0.40: 57,801 / 7,873 / 2,906).

Predictions written (per β):
1. **D5, the χ′-thinned h = 1 control (D′ = 5, keep p with (5/p) = +1), per h = 1 field:**
   - reference R★(C; log X*);
   - thinned, runs in X: ½[R★(C; log X*) + R★(C + 2 log 5; log X*)];
   - thinned, runs in N: ½[R★(C; log X_N) + R★(C + 2 log 5; log X_N)], X_N = li⁻¹(li(X*)/2);
   - ΔR = thinned − reference under each, the quantity the control measures (the field-specific offsets of L16 cancel
     in it to first order; the absolute level of (★) misfits our statistic, RQ1-b).
2. **The h = 2 fields (primary and descriptive), per field:** R★ under conductor/X (C_F at log X*), conductor/N (C_F at
   log X_N), L-value/X (C_F − log 4 at log X*), L-value/N; and the displacement s each implies against the h = 1 (★)
   curve at log X* (s solves R★(C + s; log X*) = R; bisection).

TOOLKIT §9.I: safeio.enforce(); output to scratch, copied into the repo by a separate cp + git add.

  python fn1h2_pred.py OUT_REL
"""
import math, os, sys

import numpy as np
from scipy.special import expi
from scipy.optimize import brentq

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import safeio
safeio.enforce()

XSTAR = 2 * 10 ** 10
KP = {"0.55": 57801, "0.45": 7873, "0.4": 2906}
DP = 5
H1 = {"-7": math.log(7), "-8": math.log(8), "-11": math.log(11), "zi": math.log(16), "-19": math.log(19),
      "zw": math.log(27), "-43": math.log(43), "-67": math.log(67), "-163": math.log(163)}
H2 = [-15, -20, -24, -35, -40, -51, -52, -88, -91, -115, -123, -148, -187, -232, -235, -267, -403, -427]
PRIMARY = [-35, -40, -51, -52, -88, -91, -115, -123, -148]


def li(x):
    return float(expi(math.log(x)))


def li_inv(y):
    return brentq(lambda x: li(x) - y, 2.0, 1e14, xtol=1e-6, rtol=1e-15)


def rstar(C, L, K):
    ksat = max(1, math.ceil(math.exp((L - C) / 2)))
    k = np.arange(1, ksat, dtype=np.float64)
    w = 2 * K * np.sin(np.pi * k / K) ** 2 / (np.pi * k) ** 2         # ±k together
    part = float((w * np.minimum(1.0, (C + 2 * np.log(k)) / L)).sum())
    return part + (1 - 1 / K) - float(w.sum())


def main(out):
    LX = math.log(XSTAR)
    XN_half = li_inv(li(XSTAR) / 2)
    LN = math.log(XN_half)
    res = dict(label="FN1-h2 (★) predictions, committed before computing (D5; desk, no data)",
               X_star=XSTAR, log_X_star=LX, li_X_star=li(XSTAR), X_N_half=XN_half, log_X_N_half=LN, K_P=KP,
               D_prime=DP, h1={}, h2={})
    for b, K in KP.items():
        h1 = {}
        for f, C in H1.items():
            ref = rstar(C, LX, K)
            tx = 0.5 * (rstar(C, LX, K) + rstar(C + 2 * math.log(DP), LX, K))
            tn = 0.5 * (rstar(C, LN, K) + rstar(C + 2 * math.log(DP), LN, K))
            h1[f] = dict(C=C, ref=ref, thin_runs_in_X=tx, thin_runs_in_N=tn, dR_runs_in_X=tx - ref,
                         dR_runs_in_N=tn - ref)
        res["h1"][b] = h1
        h2 = {}
        for D in H2:
            C = math.log(-D)
            vals = dict(conductor_X=rstar(C, LX, K), conductor_N=rstar(C, LN, K),
                        Lvalue_X=rstar(C - math.log(4), LX, K), Lvalue_N=rstar(C - math.log(4), LN, K))
            sv = {}
            for name, R in vals.items():
                sv[name] = brentq(lambda s: rstar(C + s, LX, K) - R, -8.0, 8.0, xtol=1e-10)
            h2[str(D)] = dict(C=C, primary=D in PRIMARY, R=vals, s_against_h1_curve_at_X_star=sv)
        res["h2"][b] = h2
        prim = [h2[str(D)]["s_against_h1_curve_at_X_star"] for D in PRIMARY]
        res["h2"][b + "_primary_mean_s"] = {k: float(np.mean([p[k] for p in prim])) for k in prim[0]}
    p = safeio.write_json(safeio.scratch(out), res, overwrite=True)
    print("written", p)
    print("X_N(li(X*)/2) = %.6g, log %.4f vs log X* %.4f" % (XN_half, LN, LX))
    for b in KP:
        print("beta", b, "h1 dR (X / N):", {f: "%.4f / %.4f" % (v["dR_runs_in_X"], v["dR_runs_in_N"])
                                            for f, v in res["h1"][b].items()})
        print("beta", b, "primary mean s:", {k: round(v, 3) for k, v in res["h2"][b + "_primary_mean_s"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
