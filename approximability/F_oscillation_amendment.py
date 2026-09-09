#!/usr/bin/env python3
r"""AMENDMENT: the genus gap is the oscillating prefactor, and the exponent was never
an empirical quantity.

POST-HOC AND UNSEALED, STATED FIRST. Computed after F_window_exponent's arms were
read. It gets no sealed credit, changes no banked artifact, and converts none of
that cell's four misses into hits. What it does is identify what those misses were
measuring, and the identification is demonstrated arithmetically rather than
argued.

THE CHAIN, and why it kept failing
-----------------------------------
Three cells in a row measured a "genus-dependent decay exponent" and each
excluded one account of it:

    F_reproduce          gap 0.1138 against a 0.05 bar; named estimator bias as
                         a rival and refused to call it a refutation.
    F_genus_exponent     CONFIRMED estimator bias (asymmetry 2.51x, rho -0.500)
                         but bounded it at ~30%; 0.0800 survived Theil-Sen.
    F_window_exponent    EXCLUDED finite window: doubling it left the gap at
                         0.0751, moving 0.0049 against a 0.01 bar.

Each cell replaced one confounded pair with another. The reason is visible only
once the observable is written out.

THE IDENTITY
------------
RH-for-curves gives |alpha_i| = sqrt(p) EXACTLY for every Frobenius eigenvalue --
a theorem, and one this repo's own rh_gate verifies on all 212 curves at vmax=12
with zero failures. Write alpha_i = sqrt(p) * exp(i*theta_i). Then

    s_n = sum_i alpha_i^n = p^(n/2) * sum_i exp(i*n*theta_i)

    log10|residual_n| = log10|1 - s_n| - n*log10(p)
                      = -(n/2)*log10(p) + log10( |1 - s_n| / p^(n/2) )
                        \_____ exponent _____/   \____ oscillation ____/

The first term is FIXED BY THEOREM and is identical for both genera. So the
fitted ratio is not a measurement of the exponent; it is

    ratio = 1 - trend(log10 oscillation) / (0.5*log10 p)

and this cell verifies that identity on the same 212 curves to a maximum error of
2.8e-3 -- the residual being the small-n gap between |1 - s_n| and |s_n|.

WHY IT IS GENUS-DEPENDENT, MEASURED
-----------------------------------
Genus 1 has ONE conjugate eigenvalue pair, so the oscillation is 2*cos(n*theta):
a single frequency, whose finite-window trend is near zero. Genus 2 has TWO
pairs, so 2*cos(n*theta1) + 2*cos(n*theta2): two frequencies that BEAT against
each other, producing deep dips and a real trend across any finite window.
Measured over the battery at vmax = 12:

    genus 1:  mean trend -0.00016,  mean |trend| 0.00608,  mean ratio 1.0009
    genus 2:  mean trend -0.04377,  mean |trend| 0.06530,  mean ratio 1.0760

A factor of 10.7 in trend magnitude, and the ratios follow it. The gap IS the
trend.

WHAT THIS SETTLES
-----------------
* MORNING_F's genus-independence claim is CORRECT about the arithmetic. The
  exponent is 0.5*log10(p) for both genera by RH-for-curves, verified here on
  every curve rather than assumed.
* Every measured "gap" -- F_reproduce's 0.1138, F_genus_exponent's surviving
  0.0800, F_window_exponent's 0.0751 -- is the finite-window trend of a bounded
  almost-periodic function, whose richness grows with the number of eigenvalue
  pairs, i.e. with genus.
* It does not shrink with the window because the oscillation is not noise. No
  robust estimator and no longer window fixes it, which is exactly the pattern
  the three cells observed and could not name from inside.
* THE ESTIMATOR WAS THE WRONG INSTRUMENT FOR THE QUESTION. Fitting a slope to
  estimate a quantity that a theorem already fixes can only measure the
  contamination. F_window_exponent's four misses are all this.

CARRY-FORWARD: do not fit a decay exponent that RH already determines. If a
future cell wants a genus-comparable observable, the candidate is the
oscillation itself -- |1 - s_n|/p^(n/2), bounded by 2g and directly comparable
across genus -- not the slope of its logarithm.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from ff_curve import g1_Nv, g2_Nv, rh_gate, hasse_weil_gate         # noqa: E402

PRIMES = [7, 11, 13, 17, 19, 23, 29]
G1_AB = [(a, b) for a in range(1, 4) for b in range(1, 4)]
G2_C = [(c3, c1, c0) for c3 in range(3) for c1 in range(3) for c0 in range(3)]
VMAX = 12


def squarefree(f, p):
    def trim(a):
        while a and a[-1] % p == 0:
            a = a[:-1]
        return [c % p for c in a]

    def rem(a, b):
        a = a[:]
        db = len(b) - 1
        inv = pow(b[-1], p - 2, p)
        for i in range(len(a) - 1, db - 1, -1):
            c = (a[i] * inv) % p
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % p
        return trim(a)

    a, b = trim(list(f)), trim([(i * c) % p for i, c in enumerate(f)][1:])
    while b:
        a, b = b, rem(a, b)
    return max(len(a) - 1, 0) == 0


def theil_sen(x, y):
    pr = [(y[j] - y[i]) / (x[j] - x[i])
          for i in range(len(x)) for j in range(i + 1, len(x))]
    return float(np.median(pr))


def analyse(res):
    p, g = res["p"], res["genus"]
    n, y, osc = [], [], []
    for v, Nv in enumerate(res["Nv"][:VMAX], start=1):
        r = abs(Nv / float(p ** v) - 1.0)
        if r <= 0:
            continue
        s = res["power_sums"][v - 1]
        n.append(v)
        y.append(np.log10(r))
        osc.append(np.log10(abs(1.0 - s) / p ** (v / 2.0)))
    if len(n) < 3:
        return None
    n = np.array(n, float)
    denom = 0.5 * np.log10(p)
    t_osc = theil_sen(n, np.array(osc))
    ratio = -theil_sen(n, np.array(y)) / denom
    return dict(genus=g, p=p, ratio=ratio, osc_trend=t_osc,
                predicted=1.0 - t_osc / denom,
                rh_ok=bool(rh_gate(res)), hw_ok=bool(hasse_weil_gate(res, VMAX)))


rows = []
for p in PRIMES:
    for (a, b) in G1_AB:
        try:
            r = analyse(g1_Nv(a, b, p, vmax=VMAX))
        except AssertionError:
            continue
        if r:
            rows.append(r)
    for (c3, c1, c0) in G2_C:
        fc = [c0, c1, 0, c3, 0, 1]
        if not squarefree(fc, p):
            continue
        try:
            r = analyse(g2_Nv(fc, p, vmax=VMAX))
        except Exception:
            continue
        if r:
            rows.append(r)

ident_err = max(abs(r["ratio"] - r["predicted"]) for r in rows)
gates_ok = sum(1 for r in rows if r["rh_ok"] and r["hw_ok"])
by_g = {}
for g in (1, 2):
    sub = [r for r in rows if r["genus"] == g]
    by_g[str(g)] = dict(
        n=len(sub),
        mean_ratio=float(np.mean([r["ratio"] for r in sub])),
        mean_osc_trend=float(np.mean([r["osc_trend"] for r in sub])),
        mean_abs_osc_trend=float(np.mean([abs(r["osc_trend"]) for r in sub])))
amp = by_g["2"]["mean_abs_osc_trend"] / by_g["1"]["mean_abs_osc_trend"]

print("POST-HOC AMENDMENT — unsealed. F_window_exponent's four misses stand.\n")
print(f"curves {len(rows)};  RH + Hasse-Weil hold on {gates_ok} of {len(rows)} "
      f"at vmax={VMAX}")
print(f"  => the decay exponent is 0.5*log10(p) BY THEOREM, identically for both "
      f"genera\n")
print(f"identity  ratio == 1 - trend(log10 oscillation)/(0.5*log10 p)")
print(f"  max deviation over all curves: {ident_err:.2e}  "
      f"(residual is the small-n |1-s_n| vs |s_n| gap)\n")
print(f"{'genus':>6s} {'n':>5s} {'mean ratio':>11s} {'mean trend':>11s} "
      f"{'mean |trend|':>13s}")
for g in ("1", "2"):
    d = by_g[g]
    print(f"{g:>6s} {d['n']:>5d} {d['mean_ratio']:>11.4f} "
          f"{d['mean_osc_trend']:>+11.5f} {d['mean_abs_osc_trend']:>13.5f}")
print(f"\n  oscillation-trend amplitude, genus2 / genus1: {amp:.1f}x")
print("  genus 1 is one cosine (no beating); genus 2 is two cosines that beat.")
print("  The gap IS the trend, so no window and no robust estimator removes it.")

json.dump(dict(
    status="POST-HOC, UNSEALED AMENDMENT to F_window_exponent.json",
    amends="F_window_exponent's E1-E4, all four of which MISSED and all four of "
           "which remain missed; this identifies what they were measuring",
    vmax=VMAX, primes=PRIMES, n_curves=len(rows),
    gates_hold=gates_ok,
    theorem="RH-for-curves gives |alpha_i| = sqrt(p) exactly, so "
            "log10|residual_n| = -(n/2)log10(p) + log10(|1-s_n|/p^(n/2)); the "
            "first term is the exponent and is genus-independent by theorem",
    identity="ratio = 1 - trend(log10 oscillation)/(0.5*log10 p)",
    identity_max_error=ident_err,
    by_genus=by_g, oscillation_amplitude_ratio=amp,
    reading="MORNING_F's genus-independence claim is CORRECT about the "
            "arithmetic. Every measured gap (0.1138, 0.0800, 0.0751) is the "
            "finite-window trend of a bounded almost-periodic prefactor whose "
            "richness grows with the number of eigenvalue pairs. It is not "
            "noise, so no robust estimator or longer window removes it.",
    carry_forward="do not fit a decay exponent that RH already determines; if a "
                  "genus-comparable observable is wanted, use the oscillation "
                  "|1-s_n|/p^(n/2) (bounded by 2g) rather than the slope of its "
                  "logarithm."),
    open(os.path.join(HERE, "F_oscillation_amendment.json"), "w"), indent=1)
print("\nwrote F_oscillation_amendment.json")
