# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 control constants, committed before the seal (FN1H2_SEAL.md §6: "L′/L(1) and Chen's term are controls";
Will, 2026-11-03). Desk arithmetic from D alone; no data.

For each of the 18 h = 2 fields (and, for the record, recomputed for the nine h = 1 fields):
- L(1, χ_D) by Hurwitz/Stieltjes (fn1_lprime.py's construction, copied, not imported: that module writes on import);
  checked against the class-number formula L(1) = 2πh/(w√|D|), h = 2, w = 2;
- L′/L(1, χ_D) two routes (Stieltjes γ₁; central difference of log L on the Hurwitz form at 1 ± 10⁻¹²), agreeing to
  10⁻¹⁵;
- P_L = log(1/L(1)²) + 2 log π, checked = C_F − log 4 (h = 2) and = C_F (h = 1);
- Chen et al.'s L-term in units of 1/log X (fn1_chen_lterm.py's reduction): C_Φ,L/C_Φ = −2·L′/L(2, χ_D), with
  L′/L(2) from mpmath.dirichlet.
TOOLKIT §9.I: safeio.enforce(); output to scratch.

  python fn1h2_controls.py OUT_REL
"""
import math, os, sys

import mpmath as mp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import safeio
safeio.enforce()
mp.mp.dps = 40

H2 = [-15, -20, -24, -35, -40, -51, -52, -88, -91, -115, -123, -148, -187, -232, -235, -267, -403, -427]
H1 = {"-7": (-7, 2), "-8": (-8, 2), "-11": (-11, 2), "zi": (-4, 4), "-19": (-19, 2), "zw": (-3, 6), "-43": (-43, 2),
      "-67": (-67, 2), "-163": (-163, 2)}


def kron(a, n):
    if n == 0:
        return 1 if abs(a) == 1 else 0
    res = 1
    while n % 2 == 0:
        n //= 2
        if a % 2 == 0:
            return 0
        if a % 8 in (3, 5):
            res = -res
    a %= n
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                res = -res
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            res = -res
        a %= n
    return res if n == 1 else 0


def lvals(D):
    q = abs(D)
    chi = [kron(D, a) for a in range(1, q + 1)]
    assert sum(chi) == 0
    A = mp.fsum(c * mp.stieltjes(0, mp.mpf(a) / q) for a, c in zip(range(1, q + 1), chi) if c)
    B = mp.fsum(c * mp.stieltjes(1, mp.mpf(a) / q) for a, c in zip(range(1, q + 1), chi) if c)
    L1, LpL = A / q, -mp.log(q) - B / A

    def L(s):
        return mp.power(q, -s) * mp.fsum(c * mp.zeta(s, mp.mpf(a) / q) for a, c in zip(range(1, q + 1), chi) if c)
    h = mp.mpf("1e-12")
    LpL2 = (mp.log(L(1 + h)) - mp.log(L(1 - h))) / (2 * h)
    chi0 = [0] + [kron(D, a) for a in range(1, q)]
    Lp2 = mp.dirichlet(2, chi0, derivative=1) / mp.dirichlet(2, chi0)
    return L1, LpL, LpL2, Lp2


def one(D, w, h):
    L1, LpL, LpL2, Lp2 = lvals(D)
    cnf = 2 * mp.pi * h / (w * mp.sqrt(abs(D)))
    assert abs(L1 / cnf - 1) < mp.mpf("1e-30"), (D, L1, cnf)
    assert abs(LpL - LpL2) < mp.mpf("1e-15"), (D, LpL, LpL2)
    CF = mp.log(abs(D) * (mp.mpf(w) / 2) ** 2)
    PL = mp.log(1 / L1 ** 2) + 2 * mp.log(mp.pi)
    assert abs(PL - (CF - 2 * mp.log(h))) < mp.mpf("1e-30"), (D, PL, CF)
    return dict(D=D, w=w, h=h, L1=float(L1), LpL1=float(LpL), LpL1_two_routes_absdiff=float(abs(LpL - LpL2)),
                LpL2=float(Lp2.real), chen_Lterm=float(-2 * Lp2.real), C_F=float(CF), P_L=float(PL))


def main(out):
    res = dict(label="FN1-h2 control constants (desk; no data)", h2={}, h1={})
    for D in H2:
        res["h2"][str(D)] = one(D, 2, 2)
        r = res["h2"][str(D)]
        print(D, "L'/L(1) %+.6f  Chen L-term %+.6f  C_F %.4f  P_L %.4f" % (r["LpL1"], r["chen_Lterm"], r["C_F"], r["P_L"]),
              flush=True)
    for k, (D, w) in H1.items():
        res["h1"][k] = one(D, w, 1)
    p = safeio.write_json(safeio.scratch(out), res, overwrite=True)
    print("written", p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
