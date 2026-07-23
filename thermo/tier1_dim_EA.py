"""
thermo/tier1_dim_EA.py — TIER-1 SEALED PAYOFF (v3 handoff §6/§9.2).

The apparatus has so far only REPRODUCED constants it was pointed at. This is the first time it
must PREDICT numbers it has not seen. Until this clears, the machine is validated but not
load-bearing.

Object: dim_H E_A, the Hausdorff dimension of the set of reals whose continued-fraction digits
all lie in a finite alphabet A. This is a "dim E_2-type" exponent, explicitly endorsed as a
Tier-1 target, and it is unambiguously GAUSS-generated (the restricted Gauss operator IS its
generator -- no trace-map, no almost-Mathieu; the two-quantization wall is not approached).

dim E_A = the s* where the pressure of the alphabet-restricted operator vanishes:
    P_A(s*) = log(leading eigenvalue of L_s restricted to A) = 0.

PROTOCOL (order matters, and is enforced by committing this file's output before step 3):
  1. Predict dim E_A for several A with the collocation operator.
  2. Cross-check EVERY prediction with a second, numerically independent route -- the
     periodic-orbit cycle expansion (Ruelle/Fredholm dynamical determinant via Newton
     identities over the alphabet's words). Different discretization, different failure modes.
     dim E_2 is carried along as the CONTROL: it is the one value already gated, so if the two
     routes agree on the controls but disagree elsewhere, the disagreement is real.
  3. ONLY THEN look up published values and compare.

Steps 1-2 are sealed to thermo/TIER1_PREREG_SEALED.json and committed before step 3 runs. No
literature value for any alphabet other than {1,2} has been consulted at authoring time.

Run:  python3 thermo/tier1_dim_EA.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from itertools import product

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermo.gauss_thermo import GaussOperator          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

ALPHABETS = [(1, 2), (1, 2, 3), (1, 2, 3, 4), (1, 2, 3, 4, 5), (1, 3), (2, 3)]


# ---------------------------------------------------------------------------------------
# Route 2 -- periodic-orbit cycle expansion (independent of the collocation matrix)
# ---------------------------------------------------------------------------------------
def word_multiplier(word):
    """Multiplier rho_w of the inverse-branch composition for a CF word (attracting branch)."""
    M = mp.matrix([[1, 0], [0, 1]])
    for a in word:
        M = M * mp.matrix([[0, 1], [1, a]])
    p, q, r, s = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    disc = mp.sqrt((s - p) ** 2 + 4 * r * q)
    rhos = []
    for x in ((-(s - p) + disc) / (2 * r), (-(s - p) - disc) / (2 * r)):
        rhos.append((p * s - q * r) / (r * x + s) ** 2)
    return min(rhos, key=lambda z: abs(z))


def build_multipliers(alphabet, nmax):
    return {n: [word_multiplier(w) for w in product(alphabet, repeat=n)]
            for n in range(1, nmax + 1)}


def fredholm_det(s, rho_by_n, nmax):
    """det(1 - L_s) from traces via Newton identities. Zero at s = dim E_A."""
    t = [mp.fsum(mp.power(abs(r), s) / (1 - r) for r in rho_by_n[n])
         for n in range(1, nmax + 1)]
    c = [mp.mpf(1)]
    for n in range(1, nmax + 1):
        cn = mp.fsum(c[n - k] * t[k - 1] for k in range(1, n + 1))
        c.append(-cn / n)
    return mp.fsum(c)


def dim_cycle_expansion(alphabet, nmax, dps=40):
    with mp.workdps(dps):
        rho = build_multipliers(alphabet, nmax)
        f = lambda s: fredholm_det(s, rho, nmax)
        lo, hi = mp.mpf("0.05"), mp.mpf("0.999")
        flo = f(lo)
        for _ in range(200):
            mid = (lo + hi) / 2
            if flo * f(mid) <= 0:
                hi = mid
            else:
                lo, flo = mid, f(mid)
            if hi - lo < mp.mpf(10) ** (-(dps - 6)):
                break
        return (lo + hi) / 2


# ---------------------------------------------------------------------------------------
# Route 1 -- collocation operator (bracket by coarse scan, then secant)
# ---------------------------------------------------------------------------------------
def dim_collocation(op, alphabet):
    with mp.workdps(op.dps):
        f = lambda s: op.pressure(s, alphabet=alphabet)
        lo = None
        prev_s = mp.mpf("0.05")
        prev = f(prev_s)
        for k in range(1, 20):
            s = mp.mpf("0.05") + k * mp.mpf("0.05")
            v = f(s)
            if prev * v <= 0:
                lo = prev_s
                break
            prev_s, prev = s, v
        start = (lo + mp.mpf("0.05")) if lo is not None else mp.mpf("0.5")
        return mp.findroot(f, start, tol=mp.mpf(10) ** (-int(0.7 * op.dps)))


def main():
    mp.mp.dps = 80
    N, dps, Ne = 40, 60, 100
    op = GaussOperator(N=N, dps=dps, Ne=Ne)
    nmax_for = {2: 14, 3: 10, 4: 8, 5: 7}

    print("TIER-1 SEALED PREDICTION -- dim E_A, two independent routes")
    print(f"route 1: Chebyshev collocation, N={N}, dps={dps}")
    print("route 2: periodic-orbit cycle expansion (Fredholm det via Newton identities)\n")
    print(f"  {'alphabet':>14s} {'route 1 (collocation)':>34s} {'route 2 (cycles)':>26s} {'agree':>7s}")

    rows = []
    for A in ALPHABETS:
        t = time.time()
        d1 = dim_collocation(op, A)
        d2 = dim_cycle_expansion(A, nmax_for[len(A)])
        agree = float(-mp.log10(abs(d1 - d2) / abs(d1)))
        rows.append({"alphabet": list(A), "route1_collocation": mp.nstr(d1, 30),
                     "route2_cycle_expansion": mp.nstr(d2, 25),
                     "routes_agree_digits": agree, "secs": round(time.time() - t, 1)})
        print(f"  {str(A):>14s} {mp.nstr(d1, 28):>34s} {mp.nstr(d2, 20):>26s} {agree:6.1f}")

    control = rows[0]
    out = {
        "sealed_utc_date": "2026-07-22",
        "what": "Tier-1 sealed prediction of dim_H E_A from the Gauss operator, BEFORE any "
                "literature lookup for alphabets other than {1,2}.",
        "instrument": "thermo/gauss_thermo.py (gate: thermo/gate_fixtures.py, GATE_PASS)",
        "config": {"N": N, "dps": dps, "Ne": Ne, "cycle_nmax_by_alphabet_size": nmax_for},
        "control": "alphabet {1,2} = dim E_2, the ONLY value already gated "
                   "(Jenkinson-Pollicott arXiv 1611.09276). Its agreement calibrates the rest.",
        "predictions": rows,
        "acceptance": "each alphabet: the two independent routes agree to >= 15 digits; and the "
                      "{1,2} control reproduces the gated dim E_2.",
        "not_yet_done": "comparison against published dim E_A for A != {1,2} -- deliberately "
                        "not consulted before this file was committed.",
        "wall": "Gauss door only. No trace-map / almost-Mathieu quantity appears here.",
    }
    worst = min(r["routes_agree_digits"] for r in rows)
    out["min_route_agreement_digits"] = worst
    out["SEAL_VALID"] = bool(worst >= 15)
    print(f"\n  control {{1,2}} routes agree to {control['routes_agree_digits']:.1f} digits")
    print(f"  worst cross-route agreement: {worst:.1f} digits")
    print(f"  SEAL_VALID: {out['SEAL_VALID']}")

    p = os.path.join(HERE, "TIER1_PREREG_SEALED.json")
    json.dump(out, open(p, "w"), indent=2, default=str)
    print("wrote", p)
    print("\nSEALED. Do not look up published dim E_A until this file is committed.")


if __name__ == "__main__":
    main()
