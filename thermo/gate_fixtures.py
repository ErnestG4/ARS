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

# CANONICAL: Keith Briggs 2003, "A precise computation of the Gauss-Kuzmin-Wirsing constant",
# n=800 at 1300 bits, confirmed at n=1000/1600 bits, "probably accurate to 385 decimals".
# Digits extracted from the PDF's own text layer (pdftotext), NOT via a fetch summariser.
GKW_REF = mp.mpf(
    "-0.30366300289873265859744812190155623311087735225365"
    "78951882454814672269952942469109843408119343636368"
    "11098272263710616938474614859745801316065265381818"
    "23787913244613989647642974095044629375949048702977"
)
WIRSING_20 = "-0.30366300289873265859"

# RETRACTED REFERENCE, kept as a live regression test. This string was extracted from
# arXiv 2602.19435 (Nisoli, "Certified spectral approximation of transfer operators and the
# Gauss map") via WebFetch. The PAPER IS REAL and its value is certified -- but the fetch
# summariser DROPPED THE DIGIT '6' AT INDEX 98. The corrupted string is byte-identical to
# Briggs with that one digit deleted, which is why the tail still "looks right": everything
# after the drop is correct but shifted one place left. Anything validated to <=98 digits
# against it was unaffected, which is exactly why it survived.
# Adjudicated independently of that string argument: this operator at N=148/dps=250 agrees with
# Briggs to 112.1 digits, and digit 99 is '6' in both. Briggs is right where the fetch is short.
GKW_CORRUPT_98 = (
    "-0.30366300289873265859744812190155623311087735225365789518824548146722699529"
    "424691098434081193436363811098272263710616938474614859745801316065265381818"
    "237879132446139896476"
)

# Jenkinson-Pollicott, arXiv 1611.09276, "Rigorous effective bounds on the Hausdorff dimension
# of continued fraction Cantor sets: a hundred decimal digits for the dimension of E_2".
# Digits from the PDF's own text layer (pypdf), NOT via a fetch summariser.
DIM_E2_REF = mp.mpf(
    "0.53128050627720514162446864736847178549305910901839"
    "87798883978039275295356438313459181095701811852398"
)

# RETRACTED: the value banked in approximability/thread3_constants.py as JP_PUBLISHED.
# It carries a DIGIT TRANSPOSITION at position 21-22 ("...41624 46 86473" printed as
# "...41624 64 86473"), so it is only correct to 21 digits. thread3_constants.py's
# periodic-orbit convergence table therefore bottomed out against a typo rather than against
# the constant -- its dim E_2 confirmation stands to 21 digits, but its apparent accuracy
# ceiling was artificial. Kept as a regression assert.
DIM_E2_REPO_TRANSPOSED = "0.5312805062772051416246486473684717854930591090"


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

    # cross-check the independent GKW sources before using either
    assert mp.nstr(GKW_REF, 20).startswith(WIRSING_20[:12]), "GKW sources disagree!"
    # regression: the retracted string must still differ from Briggs at exactly digit 99.
    # If this ever stops firing, the reference has been silently swapped back.
    d_corrupt = float(-mp.log10(abs(GKW_REF - mp.mpf(GKW_CORRUPT_98)) / abs(GKW_REF)))
    assert 97 < d_corrupt < 100, f"dropped-digit regression moved: {d_corrupt}"
    d_transp = float(-mp.log10(abs(DIM_E2_REF - mp.mpf(DIM_E2_REPO_TRANSPOSED)) / DIM_E2_REF))
    assert 20 < d_transp < 23, f"transposition regression moved: {d_transp}"
    print(f"  [ref] Briggs(385 dig) vs Wirsing(20 dig): consistent; "
          f"retracted fetch-string diverges at digit {d_corrupt:.0f} (dropped '6')")
    print(f"  [ref] dim E_2 from arXiv 1611.09276 (100 dig); the value banked in "
          f"thread3_constants.py diverges at digit {d_transp:.0f} (transposition)\n")

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
    print(f"      Briggs 2003 (385 dig) / Wirsing    -> {d:5.1f} digits  "
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
