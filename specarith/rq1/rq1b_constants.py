"""RQ1-b Step 0 (round 93): Chen et al.'s Conjecture 1.2 constants (arXiv:1901.07386, eqs. 1.12-1.14, 9.25-9.27) for
Φ = 1_(0,1] (Φ̃(s) = 1/s), generalised to a quadratic field F by replacing (i) the conductor term log(π²/4) with
log(4π²) − C_F, (ii) L(s, χ_{−4}) with L(s, χ_F), (iii) the inert primes p ≡ 3 (4) with F's inert primes. Status of the
generalisation: by analogy at each step, not re-derived through the full ratios recipe (UNVERIFIED). No data used.
Integrals on Re β = 0.1 (Chen's Appendix A contour), β = 0.1 + it, composite Simpson on |t| ≤ T (step 0.05),
with the tail beyond T bounded.

  python rq1b_constants.py OUT_JSON [T]
"""
import json
import math
import sys

import mpmath as mp
import numpy as np

mp.mp.dps = 15
EPS = 0.1
T = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0
LOGE = math.log(1 + math.sqrt(2))
FIELDS = {
    "zi": dict(C=math.log(16), chi=[0, 1, 0, -1], inert=lambda p: p % 4 == 3),
    "zs2": dict(C=math.log(8 * math.pi ** 2 / LOGE ** 2), chi=[0, 1, 0, -1, 0, -1, 0, 1], inert=lambda p: p % 8 in (3, 5)),
    "zw": dict(C=math.log(27), chi=[0, 1, -1], inert=lambda p: p % 3 == 2),
}
H = 0.05                                          # t-grid step (composite Simpson on [-T, T]; ≈ 15 points per oscillation at |t| = 200)
TT = np.arange(-T, T + H / 2, H)
WS = np.ones(len(TT)); WS[1:-1:2] = 4; WS[2:-1:2] = 2; WS *= H / 3
BETA = EPS + 1j * TT
PHPH = 1 / ((0.5 + BETA) * (0.5 - BETA))


def line_int(vals):
    """∫_{Re β = EPS} Φ̃(½+β)Φ̃(½−β) g(β) dβ = i ∫ (...) dt, g given on the grid; plus a tail bound for |t| > T
    (|Φ̃Φ̃| ≤ 1/t², |g| taken at the ends)."""
    tail = 2 * max(abs(vals[0]), abs(vals[-1])) / T
    return 1j * np.sum(WS * PHPH * vals), tail


def on_grid(fn):
    return np.array([complex(fn(complex(b))) for b in BETA])


def zlog(s):
    return mp.zeta(s, derivative=1) / mp.zeta(s)


def llog(s, chi):
    return mp.dirichlet(s, chi, derivative=1) / mp.dirichlet(s, chi)


def primes(n):
    s = bytearray([1]) * (n + 1)
    s[:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


PR = primes(100000)
INERT = {k: np.array([p for p in PR if v["inert"](p)], np.float64) for k, v in FIELDS.items()}


def hsum_grid(f):
    p = INERT[f][:, None]
    b = BETA[None, :]
    lp = np.log(p)
    num = (np.exp((2 + 8 * b) * lp) + p ** 2 - 2 * np.exp(4 * b * lp)) * lp
    den = np.exp((2 + 8 * b) * lp) + p ** 2 - np.exp(4 * b * lp) - np.exp((4 + 4 * b) * lp)
    return (num / den).sum(0)


def main(out):
    CPhi = 4 * math.pi ** 2
    Cp = -4 * math.pi ** 2                      # C′_Φ = 4π² ∫₀¹ log x dx
    Ph = 2.0                                    # Φ̃(½)
    res = dict(label="RQ1-b Step 0: Chen et al. Conjecture 1.2 constants for Φ = 1_(0,1]; generalisation UNVERIFIED",
               contour=EPS, T=T, C_Phi=CPhi, Delta_Phi=Cp - math.pi ** 2 * Ph ** 2, fields={})
    v, tail = line_int(on_grid(lambda b: zlog(1 - 2 * b) + zlog(1 + 2 * b)))
    CZ = 2j * math.pi * v
    res["C_Phi_zeta"], res["C_Phi_zeta_imag"], res["C_Phi_zeta_tail_bound"] = CZ.real, CZ.imag, 2 * math.pi * tail
    print("C_Phi_zeta", CZ, "tail", 2 * math.pi * tail, flush=True)
    for f, v in FIELDS.items():
        vl, tl = line_int(on_grid(lambda b: llog(1 + 2 * b, v["chi"]) + llog(1 - 2 * b, v["chi"])))
        va, ta = line_int(hsum_grid(f))
        CL, AP = 2j * math.pi * vl, -4j * math.pi * va
        K = complex(CZ).real - complex(CL).real - complex(AP).real + 2 * math.pi ** 2 * Ph ** 2 + CPhi * (
            math.log(4 * math.pi ** 2) - v["C"] + 2)
        res["fields"][f] = dict(C_F=v["C"], conductor_term=math.log(4 * math.pi ** 2) - v["C"], C_Phi_L=complex(CL).real,
                                C_Phi_L_imag=complex(CL).imag, A_prime=complex(AP).real, A_prime_imag=complex(AP).imag,
                                tail_bounds=dict(C_Phi_L=2 * math.pi * tl, A_prime=4 * math.pi * ta),
                                inert_primes_used=f"p < 1e5 ({len(INERT[f])})", K_Phi=K, K_over_CPhi=K / CPhi)
        print(f, res["fields"][f], flush=True)
    print("C_Phi_zeta", res["C_Phi_zeta"], res["C_Phi_zeta_imag"], "Delta/CPhi", res["Delta_Phi"] / CPhi)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
