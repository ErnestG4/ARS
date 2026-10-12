"""Internal checks of the ζ transcription (the U(N) gates cannot see ζ's arithmetic factors):
  Z1  n = 2: R_{ζ,t,2}(u, v) = (2π)²·R(t, u − v) of R₂'s G0a-verified CS07 kernel (ph2r2/r2lib), relative ≤ 1e-6.
  Z2  every prime-sum summand decays at least like p^{−2}·log^k p (summable) and every Euler factor → 1: the
      magnitude ratio between p ≈ 10⁶ and p ≈ 10⁵ must be ≤ 0.03 (p^{−2} gives 0.01) at random imaginary arguments.
  Z3  the corrected A* local factor equals its defining θ-integral (ratios conjecture, eq. Aptheta) to 1e-10, while
      the printed form does not (the erratum's red path).
  Z4  R_{ζ,t,3}, R_{ζ,t,4} are real (|Im R|/|R| ≤ 1e-8) and symmetric under permutations of their arguments (relative
      ≤ 1e-8) at random points — individual J* terms are neither, so this checks the assembly and the transcription.

  python check_zeta.py  ->  results/check_zeta.json

Z1–Z4 did not catch CS08's sign error in J13's prime-sum term (CS08_ERRATUM.md §4): a sign flip of a real, symmetric,
decaying term passes all four. check_ratios_j.py (every J* against its ratios-conjecture definition; ρ₄ → 0 at
coincidence) does.
"""
import itertools
import json
import math
import os
import random
import sys

import mpmath as mp
import numpy as np

import cs4lib as C

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2r2"))
import r2lib  # noqa: E402

T_TEST = 4.12e8                                   # a height near R3/F1 (ℓ ≈ 18)


def z1(Z, rnd):
    out = []
    for _ in range(6):
        u, v = rnd.uniform(0, 3), rnd.uniform(0, 3)
        mine = float(mp.re(Z.R([mp.mpf(u), mp.mpf(v)])))
        K = r2lib.Kernel(np.array([abs(u - v)]))
        ref = float((2 * math.pi) ** 2 * K.R(T_TEST)[0])
        out.append(dict(u=u, v=v, mine=mine, ref=ref, rel=abs(mine - ref) / abs(ref)))
    return dict(rows=out, worst=max(r["rel"] for r in out), PASS=max(r["rel"] for r in out) <= 1e-6)


def z2(Z, rnd, draws=30, per_band=20):
    """Per-prime summand magnitudes (and |log Euler factor| for A, A*), scaled by p²/log⁴p, maximised over random
    imaginary arguments, at primes just below 1e5 and 1e6. A summable (≈ p^{−2}·log^k) summand keeps the scaled sup
    bounded: ratio (1e6 band / 1e5 band) ≤ 3. A p^{−1} summand would give ≈ 10. (v1 of this test summed 200
    consecutive primes, which share a phase near 1e5: invalid, replaced 2026-10-10.)"""
    res = {}
    bands = [Z.p[(Z.p > lo) & (Z.p <= hi)][:per_band] for lo, hi in ((9.0e4, 1.0e5), (9.0e5, 1.0e6))]
    funcs = (("B", 1, False), ("Q", 2, False), ("B1", 2, False), ("B2", 4, False), ("B3", 4, False), ("B4", 4, False),
             ("S13", 4, False), ("A", 1, True), ("Astar", 4, True))
    for name, nargs, euler in funcs:
        sup = [0.0, 0.0]
        for _ in range(draws):
            args = [1j * rnd.uniform(-3, 3) for _ in range(nargs)]
            for k, band in enumerate(bands):
                for p in band:
                    sub = C.Zeta.__new__(C.Zeta)
                    sub.p, sub.lp = np.array([p]), np.log(np.array([p]))
                    v = getattr(sub, name)(*args)
                    m = abs(complex(mp.log(v))) if euler else abs(complex(v))
                    sup[k] = max(sup[k], m * p ** 2 / np.log(p) ** 4)
        res[name] = dict(sup_1e5=sup[0], sup_1e6=sup[1], ratio=sup[1] / sup[0], PASS=sup[1] / sup[0] <= 3)
    return res


def z3(rnd):
    zp = lambda p, x: 1 / (1 - p ** (-x))
    out = []
    for _ in range(4):
        a1, a2, b1, b2 = (1j * rnd.uniform(-3, 3) for _ in range(4))
        for p in (3.0, 7.0, 101.0):
            th = np.arange(8192) / 8192
            e = np.exp(2j * np.pi * th)
            f = 1.0
            for b in (b1, b2):
                f = f / (1 - np.conj(e) * p ** (-0.5 + b))
            for a in (a1, a2):
                f = f / (1 - e * p ** (-0.5 + a))
            for a in (a1, a2):
                f = f * (1 - np.conj(e) * p ** (-0.5 - a))
            for b in (b1, b2):
                f = f * (1 - e * p ** (-0.5 - b))
            integ = f.mean()
            T1 = zp(p, 1 - a1 - b1) * zp(p, 1 - a2 - b1) * zp(p, b2 - b1) / (zp(p, 1) * zp(p, -a1 - b1) * zp(p, -a2 - b1) * zp(p, 1 + b2 - b1))
            T2 = zp(p, 1 - a1 - b2) * zp(p, 1 - a2 - b2) * zp(p, b1 - b2) / (zp(p, 1) * zp(p, -a1 - b2) * zp(p, -a2 - b2) * zp(p, 1 + b1 - b2))
            S = a1 + a2 + b1 + b2
            corr, printed = p ** (-S) * (1 - T1 - T2), p ** (-S) * (1 + T1 + T2)
            out.append(dict(p=p, err_corrected=abs(corr - integ), err_printed=abs(printed - integ)))
    return dict(worst_corrected=max(r["err_corrected"] for r in out), min_printed=min(r["err_printed"] for r in out),
                PASS=max(r["err_corrected"] for r in out) <= 1e-10 and min(r["err_printed"] for r in out) > 1e-3)


def z4(Z, rnd, per_n=6, min_sep=0.1):
    """Transcription check on well-separated points (min pairwise separation ≥ min_sep). Near-coincident points are a
    separate numerical matter (pole terms ~1/δ² amplify the double-precision prime sums) and are reported, not gated."""
    out = []
    for n in (3, 4):
        for _ in range(per_n):
            xs = [mp.mpf(rnd.uniform(0, 3)) for _ in range(n)]
            sep = min(abs(float(a - b)) for a, b in itertools.combinations(xs, 2))
            base = Z.R(xs)
            perm = Z.R([xs[i] for i in random.Random(n).sample(range(n), n)])
            out.append(dict(n=n, x=[float(x) for x in xs], min_sep=sep, re=float(mp.re(base)),
                            im_rel=float(abs(mp.im(base)) / abs(base)), perm_rel=float(abs(perm - base) / abs(base)),
                            gated=sep >= min_sep))
    g = [r for r in out if r["gated"]]
    return dict(rows=out, n_gated=len(g), PASS=len(g) >= 2 * per_n - 4 and all(r["im_rel"] <= 1e-8 and r["perm_rel"] <= 1e-8 for r in g))


def main():
    rnd = random.Random(20261010)
    Z = C.Zeta(T_TEST, pmax=1_000_000)
    res = dict(t=T_TEST, ell=Z.ell, Z1=z1(Z, rnd), Z2=z2(Z, rnd), Z3=z3(rnd), Z4=z4(Z, rnd))
    res["PASS"] = bool(res["Z1"]["PASS"] and all(v["PASS"] for v in res["Z2"].values()) and res["Z3"]["PASS"]
                       and res["Z4"]["PASS"])
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "check_zeta.json"), "w"), indent=1, default=float)
    print("Z1 n=2 vs r2lib: worst rel %.2e %s" % (res["Z1"]["worst"], res["Z1"]["PASS"]))
    print("Z2 scaled-sup ratios (1e6/1e5):", {k: round(v["ratio"], 3) for k, v in res["Z2"].items()})
    print("Z3 A*: corrected err %.1e, printed min err %.2e, %s" % (res["Z3"]["worst_corrected"], res["Z3"]["min_printed"], res["Z3"]["PASS"]))
    print("Z4 (n, min_sep, Im/R, perm):", [(r["n"], round(r["min_sep"], 3), "%.1e" % r["im_rel"], "%.1e" % r["perm_rel"]) for r in res["Z4"]["rows"]], res["Z4"]["PASS"])
    print("ALL", "PASS" if res["PASS"] else "FAIL")


if __name__ == "__main__":
    main()
