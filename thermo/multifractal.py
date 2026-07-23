"""
thermo/multifractal.py — the Lyapunov multifractal spectrum f(alpha) of the Gauss map.

Handoff v3 §3/§9.3. Predictions sealed in thermo/FALPHA_PREREG_SEALED.json before this ran.

L(alpha) = dim_H { x in [0,1] : lambda(x) = alpha },   lambda(x) = lim (1/n) log|(G^n)'(x)|.

This is the canonical Gauss-generated f(alpha): the observable log|G'| IS the geometric
potential that generates the dimension, so the spectrum is a pure readout of the pressure
function P(s) [= pressure of -s log|G'|, my operator convention; P(1)=0] built and gated in
thermo/gauss_thermo.py + gate_fixtures.py. No new operator, no trace-map -- the two-quantization
wall is nowhere near.

PARAMETRIC FORM (the whole method). The equilibrium state mu_s of the potential -s log|G'| has
Lyapunov exponent lambda(mu_s) = -P'(s) and, by the variational principle
P(s) = h(mu_s) - s*lambda(mu_s), entropy h(mu_s) = P(s) - s P'(s). Its dimension is
h/lambda = [P(s) - s P'(s)]/(-P'(s)). So the spectrum is traced out by

    alpha(s) = -P'(s)
    L(alpha(s)) = s - P(s)/P'(s)          for s in (1/2, infinity).

Three landmarks fall out of this single formula, and reproducing all three simultaneously from
one pressure function is the validation:
  * s -> inf : alpha -> 2 log phi (golden edge), L -> 0.       [minimal Lyapunov orbit]
  * s = 1    : alpha = pi^2/(6 ln2), L = 1 EXACTLY.            [a.e. exponent, full dimension]
  * s -> 1/2+: alpha -> inf, L -> 1/2.                          [Good's theorem, dim 1/2]

Run:  python3 thermo/multifractal.py [--N 32] [--dps 48]
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


# Below this s, collocation power iteration gives the true leading eigenvalue (fast, no
# pollution). Above it, the discretization pollutes (a spurious largest-modulus eigenvalue that
# does not converge in N) and the Perron-Frobenius filter (dense eig, sign-definite eigenvector)
# is required. The threshold is conservative: the original non-robust curve was clean through
# s=3, and the pollution first bites near s~4.
POLLUTION_S = mp.mpf("3.5")


def spectrum_point(op, s):
    """(alpha, L) at parameter s, from P(s) and P'(s).

    Hybrid: fast power iteration for s <= POLLUTION_S, Perron-filtered dense eig above it. Both
    return the true leading eigenvalue in their regime; the split is purely for speed (dense eig
    is ~2s vs ~0.2s). Dense eig leaves ~1e-40 imaginary noise, so take real parts.
    """
    with mp.workdps(op.dps):
        s = mp.mpf(s)
        robust = s > POLLUTION_S
        P = mp.re(op.pressure(s, robust=robust))
        Pp = mp.re(op.dpressure(s, robust=robust))
        alpha = -Pp
        L = s - P / Pp
        return alpha, L


def main(N=32, dps=48, Ne=100):
    mp.mp.dps = dps + 20
    op = GaussOperator(N=N, dps=dps, Ne=Ne)
    phi = (1 + mp.sqrt(5)) / 2
    alpha_min = 2 * mp.log(phi)
    alpha_typ = mp.pi ** 2 / (6 * mp.log(2))
    out = {"config": {"N": N, "dps": dps, "Ne": Ne}}
    print(f"Lyapunov multifractal spectrum of the Gauss map (N={N}, dps={dps})\n")

    # ---- the spectrum curve, s from just above 1/2 out to large s -----------------------
    s_grid = ["0.505", "0.51", "0.52", "0.55", "0.6", "0.7", "0.8", "0.9", "1",
              "1.1", "1.25", "1.5", "2", "3", "5", "8", "14", "25"]
    print(f"  {'s':>7s} {'alpha = -P’(s)':>22s} {'L(alpha)':>22s}")
    curve, prev_alpha, mono = [], None, True
    for s in s_grid:
        a, L = spectrum_point(op, s)
        if prev_alpha is not None and a >= prev_alpha:
            mono = False
        prev_alpha = a
        curve.append({"s": s, "alpha": mp.nstr(a, 20), "L": mp.nstr(L, 20)})
        print(f"  {s:>7s} {mp.nstr(a, 18):>22s} {mp.nstr(L, 18):>22s}")
    out["curve"] = curve
    out["alpha_strictly_decreasing_in_s"] = mono

    # ---- landmark 2 (exact, s=1) -------------------------------------------------------
    a1, L1 = spectrum_point(op, mp.mpf(1))
    d_atyp = float(-mp.log10(abs(a1 - alpha_typ) / alpha_typ))
    d_peak = float(-mp.log10(abs(L1 - 1))) if L1 != 1 else float("inf")
    out["L2_peak"] = {"alpha": mp.nstr(a1, 25), "alpha_target": mp.nstr(alpha_typ, 25),
                      "L": mp.nstr(L1, 25), "alpha_digits": d_atyp, "L_digits": d_peak,
                      "PASS": bool(d_atyp > 20 and d_peak > 20)}
    print(f"\n  L2 peak (s=1): alpha = {mp.nstr(a1, 22)}")
    print(f"       pi^2/(6 ln2) = {mp.nstr(alpha_typ, 22)}  -> {d_atyp:.1f} digits")
    print(f"       L = {mp.nstr(L1, 22)}  -> peak=1 to {d_peak:.1f} digits   "
          f"{'PASS' if out['L2_peak']['PASS'] else 'FAIL'}")

    # ---- landmark 1 (golden edge): alpha(s), L(s) as s -> inf --------------------------
    # Perron-filtered, up to the dps-resolution limit: the true leading eigenvalue is phi^{-2s}
    # (~1e-25 at s=17, ~1e-33 at s=22), and beyond that its eigenvector drowns in numerical
    # noise so no sign-definite vector survives and leading_perron falls back to the polluted
    # value. At dps=48 the edge is cleanly resolved to s~25; s=25 already matches 2 log phi to
    # ~7 digits, past the >=6-digit acceptance. (Larger s just needs proportionally higher dps.)
    print("\n  L1 golden edge (s -> inf): alpha -> 2 log phi, L -> 0")
    edge = []
    for s in ("8", "14", "18", "22", "25"):
        a, L = spectrum_point(op, s)
        edge.append({"s": s, "alpha": mp.nstr(a, 18), "L": mp.nstr(L, 12)})
        print(f"     s={s:>4s}: alpha={mp.nstr(a, 16)}  (2 log phi={mp.nstr(alpha_min, 16)})  "
              f"L={mp.nstr(L, 10)}")
    a_edge, L_edge = spectrum_point(op, mp.mpf(25))
    d_edge = float(-mp.log10(abs(a_edge - alpha_min) / alpha_min))
    out["L1_golden_edge"] = {"alpha_at_s25": mp.nstr(a_edge, 18),
                             "alpha_min_target": mp.nstr(alpha_min, 18),
                             "alpha_digits_at_s25": d_edge, "L_at_s25": mp.nstr(L_edge, 8),
                             "dps_resolution_note": "edge resolvable to s~25 at dps=48; "
                             "phi^{-2s} underflows the eigenvector below noise beyond that",
                             "PASS": bool(d_edge > 6 and abs(L_edge) < mp.mpf("1e-4"))}
    print(f"     -> alpha(s=25) matches 2 log phi to {d_edge:.1f} digits, L={mp.nstr(L_edge,6)}   "
          f"{'PASS' if out['L1_golden_edge']['PASS'] else 'FAIL'}")

    # ---- landmark 3 (Good asymptote): L -> 1/2 as s -> 1/2+ -----------------------------
    print("\n  L3 Good asymptote (s -> 1/2+): alpha -> inf, L -> 1/2")
    good = []
    for s in ("0.55", "0.52", "0.51", "0.505", "0.502", "0.501"):
        a, L = spectrum_point(op, s)
        good.append({"s": s, "alpha": mp.nstr(a, 12), "L": mp.nstr(L, 16)})
        print(f"     s={s:>6s}: alpha={mp.nstr(a, 10):>12s}  L={mp.nstr(L, 14)}")
    _, L_good = spectrum_point(op, mp.mpf("0.501"))
    d_good = float(-mp.log10(abs(L_good - mp.mpf("0.5"))))
    out["L3_good_asymptote"] = {"L_at_s0501": mp.nstr(L_good, 16), "target": "0.5",
                                "digits": d_good,
                                "PASS": bool(abs(L_good - mp.mpf("0.5")) < mp.mpf("1e-2"))}
    print(f"     -> L(s=0.501) approaches 1/2 to {d_good:.1f} digits "
          f"(slow: the approach is ~1/|log(2s-1)|)   "
          f"{'PASS' if out['L3_good_asymptote']['PASS'] else 'FAIL'}")

    # ---- unimodality + peak = global max ----------------------------------------------
    Ls = [mp.mpf(c["L"]) for c in curve]
    peak_val = max(Ls)
    unimodal = bool(peak_val <= 1 + mp.mpf("1e-15"))
    out["shape"] = {"alpha_monotone_decreasing_in_s": mono,
                    "max_L_on_grid": mp.nstr(peak_val, 20),
                    "peak_le_1": unimodal}

    out["ALL_PASS"] = bool(out["L2_peak"]["PASS"] and out["L1_golden_edge"]["PASS"]
                           and out["L3_good_asymptote"]["PASS"] and mono and unimodal)
    print(f"\n  alpha(s) strictly decreasing: {mono};  max L on grid = {mp.nstr(peak_val, 18)} "
          f"(<=1: {unimodal})")
    print(f"  ALL_PASS: {out['ALL_PASS']}")
    p = os.path.join(HERE, "multifractal_measured.json")
    json.dump(out, open(p, "w"), indent=2, default=str)
    print("wrote", p)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=32)
    ap.add_argument("--dps", type=int, default=48)
    ap.add_argument("--Ne", type=int, default=100)
    a = ap.parse_args()
    main(a.N, a.dps, a.Ne)
