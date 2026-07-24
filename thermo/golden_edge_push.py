"""
thermo/golden_edge_push.py — is the 7.2-digit golden edge a LIMIT gap or a NUMERICAL floor?

Reviewer: "7.2 digits at the golden edge conflates two things -- (i) how far the true s=25 value
sits from its own s->inf limit (math), and (ii) how accurately you computed s=25 (numerics).
Push to s=50: if agreement improves at the rate the zero-temperature asymptotics predict, the
7.2 was (i). If it stalls or degrades, it's (ii)."

Zero-temperature asymptotics: as s->inf the equilibrium measure concentrates on the golden fixed
point (multiplier |rho_1| = phi^-2 = 0.382); the leading correction comes from the next periodic
orbit (|rho_2| = (sqrt2-1)^2 = 0.1716), so

    alpha(s) - 2 log phi  ~  C * (|rho_2|/|rho_1|)^s  =  C * 0.449^s      (decay ~ e^{-0.80 s})

If alpha - alpha_min keeps decaying at ~0.449/step out to s=50, the s=25 gap was (i), the limit
not yet reached -- the apparatus is fine. A stall would be (ii), conditioning: (n+x)^{-2s} spans
~10 orders of magnitude between n=1 and n=2 at s=25 alone, so this is a live possibility.

dps is raised so phi^{-2s} (~1e-21 at s=50) stays well above the eigenvector noise floor.

Run:  python3 thermo/golden_edge_push.py
"""
from __future__ import annotations

import json
import math
import os
import sys

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermo.gauss_thermo import GaussOperator          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    mp.mp.dps = 110
    phi = (1 + mp.sqrt(5)) / 2
    alpha_min = 2 * mp.log(phi)
    op = GaussOperator(N=44, dps=95, Ne=130)
    rho2_over_rho1 = (mp.sqrt(2) - 1) ** 2 / phi ** (-2)     # 0.449...
    predicted_rate = float(-mp.log10(rho2_over_rho1))         # digits gained per unit s
    print(f"golden edge push (N=44, dps=95). alpha_min = 2 log phi = {mp.nstr(alpha_min, 20)}")
    print(f"predicted zero-T decay: (|rho2|/|rho1|)^s = {float(rho2_over_rho1):.4f}^s "
          f"= {predicted_rate:.3f} digits/unit-s\n")
    print(f"  {'s':>4s} {'alpha - alpha_min':>26s} {'digits':>8s} {'d(digits)/ds':>13s}")
    rows, prev = [], None
    for s in (10, 20, 30, 40, 50):
        P = mp.re(op.pressure(mp.mpf(s), robust=True))
        Pp = mp.re(op.dpressure(mp.mpf(s), robust=True))
        alpha = -Pp
        gap = abs(alpha - alpha_min)
        dig = float(-mp.log10(gap))
        rate = "" if prev is None else f"{(dig - prev[1]) / (s - prev[0]):.3f}"
        rows.append({"s": s, "alpha_minus_min": mp.nstr(gap, 6), "digits": round(dig, 2),
                     "rate_since_prev": None if prev is None else round((dig - prev[1]) / (s - prev[0]), 3)})
        print(f"  {s:>4d} {mp.nstr(gap, 6):>26s} {dig:8.2f} {rate:>13s}")
        prev = (s, dig)

    rates = [r["rate_since_prev"] for r in rows if r["rate_since_prev"] is not None]
    mean_rate = sum(rates) / len(rates)
    # (i) limit-gap: rate stays near the predicted zero-T rate, no stall
    # (ii) numerical floor: rate collapses toward 0 (digits stop improving)
    stalled = rates[-1] < 0.3 * predicted_rate
    verdict = ("NUMERICAL_FLOOR" if stalled else
               "LIMIT_GAP" if abs(mean_rate - predicted_rate) < 0.35 * predicted_rate else
               "DECAYS_BUT_OFF_PREDICTED_RATE")
    out = {"alpha_min": mp.nstr(alpha_min, 25), "predicted_rate_digits_per_s": predicted_rate,
           "rows": rows, "mean_measured_rate": mean_rate, "final_step_rate": rates[-1],
           "VERDICT": verdict,
           "reading": ("alpha - alpha_min keeps shrinking at ~the predicted zero-temperature rate "
                       "out to s=50, so the s=25 gap was the LIMIT not yet reached (math), not a "
                       "numerical floor -- the apparatus is sound at the edge") if verdict == "LIMIT_GAP"
                      else ("digit gain stalled -> a numerical floor (conditioning), the thing to "
                            "diagnose") if verdict == "NUMERICAL_FLOOR" else
                      "decays without stalling but off the predicted rate; edge sound, rate model rough"}
    print(f"\n  predicted rate {predicted_rate:.3f} dig/s;  measured mean {mean_rate:.3f}, "
          f"final step {rates[-1]:.3f}")
    print(f"  VERDICT: {verdict}")
    json.dump(out, open(os.path.join(HERE, "golden_edge_push_measured.json"), "w"),
              indent=2, default=str)
    print("wrote golden_edge_push_measured.json")


if __name__ == "__main__":
    main()
