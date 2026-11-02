# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 post-hoc lead (Will 2026-11-02): L'/L(1, chi_D) for the nine class-number-1 imaginary quadratic fields.

L(s,chi) = q^-s sum_a chi(a) zeta(s, a/q); with zeta(s,a) = 1/(s-1) + gamma_0(a) - gamma_1(a)(s-1) + ...
and sum chi = 0:  L(1) = A/q,  L'/L(1) = -log q - B/A,  A = sum chi(a) gamma_0(a/q), B = sum chi(a) gamma_1(a/q).
Checks: L(1) = 2 pi / (w sqrt|D|) (h = 1); L'/L by a second route (Euler product partial sums are too slow; use
central difference of log L on the Hurwitz form at s = 1 +/- 1e-12) to 1e-15; closed form for chi_-4:
L'/L(1) = gamma + 2 log 2 + 3 log pi - 4 log Gamma(1/4) (Lerch/Chowla-Selberg), to 1e-30.
"""
import json, sys
import mpmath as mp
mp.mp.dps = 40

def kron(D, n):
    # Kronecker symbol (D/n) for fundamental D < 0, n >= 1
    if n % 2 == 0:
        if D % 2 == 0:
            return 0
        r8 = D % 8
        s = 1 if r8 in (1, 7) else -1
        return s * kron(D, n // 2)
    # n odd: Jacobi symbol (D/n)
    a, m, t = D % n, n, 1
    if m == 1:
        return 1
    while a:
        while a % 2 == 0:
            a //= 2
            if m % 8 in (3, 5):
                t = -t
        a, m = m, a
        if a % 4 == 3 and m % 4 == 3:
            t = -t
        a %= m
    return t if m == 1 else 0

FIELDS = {"-7": (-7, 2), "-8": (-8, 2), "-11": (-11, 2), "zi": (-4, 4), "-19": (-19, 2), "zw": (-3, 6),
          "-43": (-43, 2), "-67": (-67, 2), "-163": (-163, 2)}

def lval(D):
    q = abs(D)
    chi = [kron(D, a) for a in range(1, q + 1)]
    assert sum(chi) == 0
    A = mp.fsum(c * mp.stieltjes(0, mp.mpf(a) / q) for a, c in zip(range(1, q + 1), chi) if c)
    B = mp.fsum(c * mp.stieltjes(1, mp.mpf(a) / q) for a, c in zip(range(1, q + 1), chi) if c)
    L1 = A / q
    LpL = -mp.log(q) - B / A
    # second route: L(s) via Hurwitz at s = 1 +/- h, central difference of log L
    def L(s):
        return mp.power(q, -s) * mp.fsum(c * mp.zeta(s, mp.mpf(a) / q) for a, c in zip(range(1, q + 1), chi) if c)
    h = mp.mpf("1e-12")
    LpL2 = (mp.log(L(1 + h)) - mp.log(L(1 - h))) / (2 * h)
    return L1, LpL, LpL2, chi


def main(path):
    out = {}
    for k, (D, w) in FIELDS.items():
        L1, LpL, LpL2, chi = lval(D)
        cnf = 2 * mp.pi / (w * mp.sqrt(abs(D)))
        assert abs(L1 / cnf - 1) < mp.mpf("1e-30"), (k, L1, cnf)
        assert abs(LpL - LpL2) < mp.mpf("1e-15"), (k, LpL, LpL2)
        out[k] = {"D": D, "w": w, "L1": float(L1), "L1_classno_check": True, "LpL1": float(LpL),
                  "LpL1_two_routes_absdiff": float(abs(LpL - LpL2)), "chi2": kron(D, 2),
                  "C_F": float(mp.log(abs(D) * (w / 2) ** 2))}
        print(k, "chi(2)=%+d" % kron(D, 2), "L(1)=%.6f" % L1, "L'/L(1)=%+.6f" % LpL, "C_F=%.3f" % out[k]["C_F"])
    zi_cf = mp.euler + 2*mp.log(2) + 3*mp.log(mp.pi) - 4*mp.log(mp.gamma(mp.mpf(1)/4))
    assert abs(lval(-4)[1] - zi_cf) < mp.mpf("1e-30"), zi_cf
    print("zi closed form ok", mp.nstr(zi_cf, 20))
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1])
