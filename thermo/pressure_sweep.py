"""
thermo/pressure_sweep.py — P(s) for the Gauss map, and WHAT DRIVES the phase transition.

Predictions sealed in thermo/PRESSURE_PREREG_SEALED.json BEFORE this was run.

Four measurements:
  P1  golden closed form   -- restricted alphabet {1}: P(s) = -2s log(phi) exactly
  P2  P(s) sweep           -- full alphabet, analytic and strictly decreasing, P(1)=0
  P3  divergence law       -- P(s) + log(2s-1) -> 0 as s -> 1/2+
  P4  ATTRIBUTION          -- is the transition driven by the golden tail or by the
                              large-partial-quotient tail?

P4 is the point. The Gauss map is the induced/accelerated Farey map; the Farey map's
indifferent fixed point at 0 is what makes the pressure non-analytic. The question is
WHICH continued fractions sit near that fixed point. The Farey map decrements a_1 until
it reaches 1 and then drops it, so an orbit with partial quotient a spends exactly a
steps near 0 -- large partial quotients are the slow orbits, and the golden tail
[1,1,1,...] (every a=1) never takes the left branch at all.

The test is decisive and cheap: for any FINITE alphabet {1..A} the operator is a finite
sum, hence entire in s, so P_A is analytic at s=1/2 with a finite value. If the
singularity only appears as A -> infinity, it is manufactured by the large-a tail and
nothing else. The golden subsystem {1} is the control.

Run:  python3 thermo/pressure_sweep.py [--N 28] [--dps 45]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermo.gauss_thermo import GaussOperator          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main(N=28, dps=45, Ne=100):
    mp.mp.dps = dps + 20
    op = GaussOperator(N=N, dps=dps, Ne=Ne)
    out = {"config": {"N": N, "dps": dps, "Ne": Ne}}
    phi = (1 + mp.sqrt(5)) / 2
    print(f"Gauss thermodynamics: N={N}, dps={dps}, Ne={Ne}\n")

    # -- P1 golden closed form ----------------------------------------------------------
    print("P1  golden subsystem A={1}:  P(s) = -2s log(phi) ?")
    rows = []
    worst = mp.inf
    for s in ("0.5", "0.75", "1", "1.5", "2"):
        sv = mp.mpf(s)
        got = op.pressure(sv, alphabet=(1,))
        exact = -2 * sv * mp.log(phi)
        d = float(-mp.log10(abs(got - exact) / abs(exact)))
        worst = min(worst, d)
        rows.append({"s": s, "P": mp.nstr(got, 25), "exact": mp.nstr(exact, 25), "digits": d})
        print(f"     s={s:5s}  P={mp.nstr(got, 22):26s} exact={mp.nstr(exact, 22):26s} {d:5.1f} dig")
    out["P1_golden"] = {"rows": rows, "worst_digits": worst, "PASS": bool(worst > 20)}
    print(f"     -> worst {worst:.1f} digits   {'PASS' if worst > 20 else 'FAIL'}\n")

    # -- P2 pressure sweep, full alphabet ----------------------------------------------
    print("P2  full-alphabet pressure sweep")
    grid = ["0.55", "0.6", "0.7", "0.8", "0.9", "1", "1.1", "1.25", "1.5", "2", "2.5", "3"]
    rows, prev = [], None
    monotone = True
    for s in grid:
        sv = mp.mpf(s)
        t = time.time()
        P = op.pressure(sv)
        if prev is not None and P >= prev:
            monotone = False
        prev = P
        rows.append({"s": s, "P": mp.nstr(P, 25)})
        print(f"     s={s:5s}  P(s) = {mp.nstr(P, 22):26s}  ({time.time() - t:.1f}s)")
    P1val = op.pressure(mp.mpf(1))
    anchor = float(-mp.log10(abs(P1val))) if P1val != 0 else float("inf")
    out["P2_sweep"] = {"rows": rows, "monotone_decreasing": monotone,
                       "P_at_1_digits_of_zero": anchor,
                       "PASS": bool(monotone and anchor > 20)}
    print(f"     -> strictly decreasing: {monotone};  P(1)=0 to {anchor:.1f} digits   "
          f"{'PASS' if monotone and anchor > 20 else 'FAIL'}\n")

    # -- P3 divergence law --------------------------------------------------------------
    print("P3  divergence law:  P(s) + log(2s-1) -> 0  as s -> 1/2+")
    rows = []
    for eps in ("1e-1", "1e-2", "1e-3", "1e-4"):
        e = mp.mpf(eps)
        sv = mp.mpf("0.5") + e
        P = op.pressure(sv)
        resid = P + mp.log(2 * e)
        rows.append({"s_minus_half": eps, "P": mp.nstr(P, 20), "residual": mp.nstr(resid, 20)})
        print(f"     s-1/2={eps:6s}  P={mp.nstr(P, 18):22s}  P+log(2s-1) = {mp.nstr(resid, 15)}")
    final = abs(mp.mpf(rows[-1]["residual"]))
    shrinking = all(abs(mp.mpf(rows[i + 1]["residual"])) < abs(mp.mpf(rows[i]["residual"]))
                    for i in range(len(rows) - 1))
    out["P3_divergence"] = {"rows": rows, "monotone_shrinking": shrinking,
                            "final_abs_residual": mp.nstr(final, 10),
                            "PASS": bool(shrinking and final < mp.mpf("0.05"))}
    print(f"     -> shrinking: {shrinking};  |residual| at 1e-4 = {mp.nstr(final, 6)}   "
          f"{'PASS' if shrinking and final < mp.mpf('0.05') else 'FAIL'}\n")

    # -- P4 ATTRIBUTION -----------------------------------------------------------------
    print("P4  ATTRIBUTION: golden tail, or large-partial-quotient tail?")
    print("    finite alphabet {1..A} is a FINITE sum -> entire in s -> analytic at s=1/2.")
    rows = []
    half = mp.mpf("0.5")
    for A in (1, 2, 3, 5, 10, 20, 40, 80):
        lam, _ = op.leading(half, alphabet=tuple(range(1, A + 1)))
        rows.append({"A": A, "lambda_A_at_half": mp.nstr(lam, 20),
                     "P_A_at_half": mp.nstr(mp.log(lam), 20)})
        print(f"     A={A:3d}  lambda_A(1/2) = {mp.nstr(lam, 16):20s}  "
              f"P_A(1/2) = {mp.nstr(mp.log(lam), 16)}")
    # is lambda_A(1/2) ~ log A + const ?  fit the last few points
    import math
    pts = [(math.log(r["A"]), float(mp.mpf(r["lambda_A_at_half"]))) for r in rows if r["A"] >= 5]
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    slope = sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts)
    inter = my - slope * mx
    all_finite = all(mp.isfinite(mp.mpf(r["lambda_A_at_half"])) for r in rows)
    unbounded = float(mp.mpf(rows[-1]["lambda_A_at_half"])) > float(mp.mpf(rows[0]["lambda_A_at_half"])) + 1
    golden_lam = float(mp.mpf(rows[0]["lambda_A_at_half"]))
    print(f"\n     fit lambda_A(1/2) = {slope:.4f}*log(A) + {inter:.4f}   (predicted slope ~1)")
    print(f"     golden A=1: lambda=({golden_lam:.6f}) finite, P analytic everywhere (P1 closed form)")
    out["P4_attribution"] = {
        "rows": rows, "log_fit_slope": slope, "log_fit_intercept": inter,
        "all_finite_at_half": all_finite, "unbounded_in_A": unbounded,
        "golden_lambda_at_half": golden_lam,
        "VERDICT": ("LARGE_PARTIAL_QUOTIENT_DRIVEN" if (all_finite and unbounded and slope > 0.5)
                    else "INCONCLUSIVE"),
        "PASS": bool(all_finite and unbounded and slope > 0.5)}
    print(f"     -> VERDICT: {out['P4_attribution']['VERDICT']}\n")

    out["ALL_PASS"] = all(out[k]["PASS"] for k in
                          ("P1_golden", "P2_sweep", "P3_divergence", "P4_attribution"))
    print("ALL_PASS:", out["ALL_PASS"])
    p = os.path.join(HERE, "pressure_sweep_measured.json")
    json.dump(out, open(p, "w"), indent=2, default=str)
    print("wrote", p)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=28)
    ap.add_argument("--dps", type=int, default=45)
    ap.add_argument("--Ne", type=int, default=100)
    a = ap.parse_args()
    main(a.N, a.dps, a.Ne)
