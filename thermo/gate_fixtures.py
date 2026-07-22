"""
thermo/gate_fixtures.py — calibrator gate for the arbitrary-precision Gauss operator.

Every fixture is a GATE: if one fails, stop and fix the primitive before anything
downstream. Nothing in thermo/ is trusted until this passes.

| fixture                     | authoritative source                                      |
|-----------------------------|-----------------------------------------------------------|
| leading eigenvalue at s=1   | definitional (= 1 exactly)                                |
| GKW constant (2nd eig, s=1) | Wirsing (20 dig) + arXiv 2602.19435 Thm 1.1 (certified 90+)|
| Gauss Lyapunov -P'(1)       | closed form pi^2/(6 ln 2)                                 |
| dim E_2 (partial quots <=2) | Jenkinson-Pollicott, as banked in thread3_constants.py    |

PROVENANCE / precision hygiene. Reference digits are pulled from sources, never from
memory. The two GKW sources are independent (Wirsing 1974 analytic; arXiv 2602.19435
certified interval arithmetic) and agree on their common 20 digits, so the long string
is cross-checked rather than taken on one authority.

    Snag worth recording: an early run of this comparison "saturated" at 18.3 digits
    regardless of N or dps, which looks exactly like a corrupted reference string. It
    was not — the reference literal was being parsed at the ambient dps (15) before
    precision was raised. Parse references at full precision BEFORE comparing.

FILING. Same operator at different s, and the operator on a restricted alphabet, are
DIFFERENT OBJECTS. dim E_2 is the restricted-alphabet subsystem {1,2}; the GKW constant
and the Lyapunov exponent are the full alphabet. They are reported separately.

Run:  python3 thermo/gate_fixtures.py [--N 32] [--dps 55]
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

# --- reference constants, parsed at high precision BEFORE any comparison ---------------
mp.mp.dps = 220

# arXiv 2602.19435 Thm 1.1 (certified, |err| < 1e-175); first 20 digits agree with Wirsing.
GKW_REF = mp.mpf(
    "-0.30366300289873265859744812190155623311087735225365789518824548146722699529"
    "424691098434081193436363811098272263710616938474614859745801316065265381818"
    "237879132446139896476"
)
WIRSING_20 = "-0.30366300289873265859"

# Jenkinson-Pollicott, as banked in approximability/thread3_constants.py
DIM_E2_REF = mp.mpf("0.5312805062772051416246486473684717854930591090")


def digits_agree(a, b):
    """Number of leading decimal digits two values share (inf if bit-identical)."""
    d = abs(a - b)
    if d == 0:
        return float("inf")
    return float(-mp.log10(d / max(abs(a), abs(b), mp.mpf(1))))


def run(N=32, dps=55, Ne=100):
    op = GaussOperator(N=N, dps=dps, Ne=Ne)
    res = {"config": {"N": N, "dps": dps, "Ne": Ne}, "fixtures": {}}
    print(f"Gauss operator: N={N} Chebyshev-Lobatto nodes, dps={dps}, head split Ne={Ne}")
    print(f"(expected ~{0.86 * N:.0f} digits: convergence is ~0.86 decimal digits/node)\n")

    # cross-check the two independent GKW sources before using either
    assert mp.nstr(GKW_REF, 20).startswith(WIRSING_20[:12]), "GKW sources disagree!"

    # -- 1. leading eigenvalue at s=1 = 1 exactly --------------------------------------
    t = time.time()
    lam0, _ = op.leading(1)
    d = digits_agree(lam0, mp.mpf(1))
    res["fixtures"]["lambda0_s1"] = {"value": mp.nstr(lam0, 30), "target": "1",
                                     "digits": d, "pass": bool(d > 0.5 * N)}
    print(f"  [1] lambda_0(s=1)      = {mp.nstr(lam0, 28)}")
    print(f"      target 1 (definitional)            -> {d:5.1f} digits  "
          f"{'PASS' if d > 0.5 * N else 'FAIL'}   ({time.time() - t:.1f}s)")

    # -- 2. GKW constant ----------------------------------------------------------------
    t = time.time()
    lam1 = op.subleading(1)
    d = digits_agree(lam1, GKW_REF)
    res["fixtures"]["gkw_constant"] = {"value": mp.nstr(lam1, 45),
                                       "target": mp.nstr(GKW_REF, 45),
                                       "digits": d, "pass": bool(d > 0.5 * N)}
    print(f"  [2] lambda_1(s=1)      = {mp.nstr(lam1, 28)}")
    print(f"      Wirsing / arXiv 2602.19435         -> {d:5.1f} digits  "
          f"{'PASS' if d > 0.5 * N else 'FAIL'}   ({time.time() - t:.1f}s)")

    # -- 3. Lyapunov exponent -----------------------------------------------------------
    t = time.time()
    lyap = op.lyapunov()
    exact = mp.pi ** 2 / (6 * mp.log(2))
    d = digits_agree(lyap, exact)
    res["fixtures"]["lyapunov"] = {"value": mp.nstr(lyap, 30), "target": mp.nstr(exact, 30),
                                   "digits": d, "pass": bool(d > 0.4 * N),
                                   "levy_exponent": mp.nstr(lyap / 2, 30)}
    print(f"  [3] -P'(1)             = {mp.nstr(lyap, 28)}")
    print(f"      pi^2/(6 ln 2)                      -> {d:5.1f} digits  "
          f"{'PASS' if d > 0.4 * N else 'FAIL'}   ({time.time() - t:.1f}s)")
    print(f"      Levy exponent -P'(1)/2 = {mp.nstr(lyap / 2, 24)}  "
          f"[pi^2/(12 ln 2) = {mp.nstr(exact / 2, 24)}]")

    # -- 4. dim E_2 (RESTRICTED alphabet -- a different object) -------------------------
    t = time.time()
    dim = op.dimension((1, 2))
    d = digits_agree(dim, DIM_E2_REF)
    res["fixtures"]["dim_E2"] = {"value": mp.nstr(dim, 30), "target": mp.nstr(DIM_E2_REF, 30),
                                 "digits": d, "pass": bool(d > 0.3 * N),
                                 "note": "restricted alphabet {1,2} -- NOT the full Gauss operator"}
    print(f"  [4] dim E_2 (alphabet {{1,2}}) = {mp.nstr(dim, 28)}")
    print(f"      Jenkinson-Pollicott                -> {d:5.1f} digits  "
          f"{'PASS' if d > 0.3 * N else 'FAIL'}   ({time.time() - t:.1f}s)")

    res["GATE_PASS"] = all(f["pass"] for f in res["fixtures"].values())
    print(f"\nGATE_PASS: {res['GATE_PASS']}")

    out = os.path.join(HERE, "gate_fixtures_measured.json")
    json.dump(res, open(out, "w"), indent=2, default=str)
    print("wrote", out)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=32)
    ap.add_argument("--dps", type=int, default=55)
    ap.add_argument("--Ne", type=int, default=100)
    a = ap.parse_args()
    r = run(a.N, a.dps, a.Ne)
    sys.exit(0 if r["GATE_PASS"] else 1)
