"""Independent check of the transcribed ζ J* pieces (cs4lib.Zeta.J11, J12, J13, J22) against CS08's own definition:
J_{ζ,t}(A;B) = Π_{α∈A}∂_α Π_{β∈B}∂_β ℛ_{ζ,t}(A,B;C,D) |_{C=A, D=B}   (CS08 Conjecture "ratiozeta" and Theorem "Jzeta";
(ζ′/ζ)(s+α) = ∂_α ζ(s+α)/ζ(s+γ) at γ = α), with
  ℛ_{ζ,t}(A,B;C,D) = Σ_{S⊂A, T⊂B, |S|=|T|} e^{−ℓ(ΣS+ΣT)} Z_ζ(S̄+T⁻, T̄+S⁻; C, D) 𝒜_ζ(S̄+T⁻, T̄+S⁻; C, D),
  Z_ζ(A,B;C,D) = Z(A,B)Z(C,D)/(Z(A,D)Z(B,C)),  Z(X,Y) = Π ζ(1+x+y),
  𝒜_ζ = Π_p Z_p(A,B;C,D) ∫₀¹ 𝒜_{p,θ} dθ,  Z_p(X,Y) = Π z_p(1+x+y)^{−1},  z_p(x) = (1 − p^{−x})^{−1},
  𝒜_{p,θ} = Π_A z_{p,−θ}(½+α) Π_B z_{p,θ}(½+β) / (Π_C z_{p,−θ}(½+γ) Π_D z_{p,θ}(½+δ)),  z_{p,θ}(x) = (1 − e(θ)p^{−x})^{−1}
(X_t replaced by e^{−ℓ(…)}, CS08's remark "chiapprox", as the transcription does).

The identity holds prime by prime, so a short prime list (p ≤ PMAX, default 7) tests every arithmetic factor; ζ is exact
(mpmath) on both sides. Points: Re α, Re β ∈ [0.03, 0.08] (Theorem Jzeta's region, J = J*), imaginary parts in [−0.6, 0.6].
Derivatives: central mixed differences at 60 digits, h = 1e-12 (truncation O(h²); the θ-integral is a 256-point
trapezoid, exact to ~(p^{−1/2})^{256} and analytic in the shifts, so it commutes with the differences).

Pass: every J* within REL_TOL of its definition; the red path (CS08's printed sign of J13's prime-sum term) misses by
≥ RED_MIN; and ρ₄ vanishes at coincidence with the corrected sign but not with the printed one (`coincidence`).
Written 2026-10-11 after route (a)'s coincidence probe found ρ₄^ζ → a negative constant (CS08_ERRATUM.md §4). The
earlier checks Z1–Z4 (check_zeta.py: n = 2 against R₂, summand decay, A*, realness and symmetry) could not see a sign
error in a symmetric, real, decaying term.

  python check_ratios_j.py [PMAX] [NPTS]  →  results/check_ratios_j.json
"""
import itertools
import json
import math
import os
import random
import sys

import mpmath as mp

import cs4lib as C

mp.mp.dps = 60
HERE = os.path.dirname(os.path.abspath(__file__))
T_TEST = 16_190_000.0
NTH = 256


def zp(p, x):
    return 1 / (1 - mp.power(p, -x))


def Zz(X, Y):
    return mp.fprod([mp.zeta(1 + x + y) for x in X for y in Y]) if X and Y else mp.mpf(1)


def Zpp(p, X, Y):
    return mp.fprod([1 / zp(p, 1 + x + y) for x in X for y in Y]) if X and Y else mp.mpf(1)


def A_arith(primes, A, B, Cc, D):
    tot = mp.mpf(1)
    ths = [mp.mpf(k) / NTH for k in range(NTH)]
    for p in primes:
        pref = Zpp(p, A, B) * Zpp(p, Cc, D) / (Zpp(p, A, D) * Zpp(p, B, Cc))
        acc = 0
        for th in ths:
            e = mp.expjpi(2 * th)
            v = mp.mpf(1)
            for a in A:
                v /= (1 - mp.conj(e) * mp.power(p, -(mp.mpf(1) / 2 + a)))
            for b in B:
                v /= (1 - e * mp.power(p, -(mp.mpf(1) / 2 + b)))
            for g in Cc:
                v *= (1 - mp.conj(e) * mp.power(p, -(mp.mpf(1) / 2 + g)))
            for d in D:
                v *= (1 - e * mp.power(p, -(mp.mpf(1) / 2 + d)))
            acc += v
        tot *= pref * acc / NTH
    return tot


def ratios_R(primes, ell, A, B, Cc, D):
    tot = 0
    for k in range(0, min(len(A), len(B)) + 1):
        for S in itertools.combinations(range(len(A)), k):
            for T in itertools.combinations(range(len(B)), k):
                Sv = [A[i] for i in S]
                Tv = [B[j] for j in T]
                Sbar = [A[i] for i in range(len(A)) if i not in S]
                Tbar = [B[j] for j in range(len(B)) if j not in T]
                AA = Sbar + [-x for x in Tv]
                BB = Tbar + [-x for x in Sv]
                Zr = Zz(AA, BB) * Zz(Cc, D) / (Zz(AA, D) * Zz(BB, Cc))
                tot += mp.exp(-ell * (sum(Sv) + sum(Tv))) * Zr * A_arith(primes, AA, BB, Cc, D)
    return tot


def J_ratio(primes, ell, A, B, h=mp.mpf("1e-12")):
    """Mixed first derivative in every element of A and B, at C = A, D = B (held fixed)."""
    n = len(A) + len(B)
    tot = 0
    for signs in itertools.product((1, -1), repeat=n):
        Ah = [a + s * h for a, s in zip(A, signs[:len(A)])]
        Bh = [b + s * h for b, s in zip(B, signs[len(A):])]
        tot += math.prod(signs) * ratios_R(primes, ell, Ah, Bh, A, B)
    return tot / (2 * h) ** n


REL_TOL = 1e-10          # J* against its definition (double-precision prime sums in cs4lib)
RED_MIN = 1e-3           # the printed J13 sign must miss by at least this (red path)


def coincidence(printed=False):
    """ρ₄^ζ(0, y, a, b)/ρ₄^sine as y → 0 (cs4fast, pmax 3·10⁵). A density of distinct zeros vanishes at coincidence, so the
    ratio must settle; PASS iff |r(3e-3) − r(1e-2)| ≤ 0.05·|r(1e-2)| + 0.02 for every configuration and height. y below
    ~1e-3 is not used: there double-precision cancellation between the J* pieces dominates."""
    import numpy as np

    import cs4fast as F
    import route_a_zeta as RA
    orig = F.FastZeta.S13
    if printed:
        F.FastZeta.S13 = lambda self, *a: -orig(self, *a)
    rows = []
    try:
        for t in (16_190_000.0, 1e10):
            Z = F.FastZeta(t, pmax=300_000)
            for a, b in ((0.45, 0.9), (1.0, 1.2), (0.3, 1.5)):
                ys = np.array([1e-2, 3e-3])
                ds = [0 * ys, ys, 0 * ys + a, 0 * ys + b]
                r = np.real(RA.rho(Z, ds)) / RA.sine_rho(ds)
                ok = bool(abs(r[1] - r[0]) <= 0.05 * abs(r[0]) + 0.02)
                rows.append(dict(t=t, a=a, b=b, ratio_y1e2=float(r[0]), ratio_y3e3=float(r[1]), settles=ok))
    finally:
        F.FastZeta.S13 = orig
    return dict(rows=rows, PASS=all(x["settles"] for x in rows))


def main(pmax=7, npts=3, seed=11):
    rnd = random.Random(seed)
    Z = C.Zeta(T_TEST, pmax=pmax)
    primes = [int(p) for p in Z.p]
    ell = mp.mpf(Z.ell)
    pt = lambda: mp.mpc(rnd.uniform(0.03, 0.08), rnd.uniform(-0.6, 0.6))
    rows = []
    for name, na, nb, fn in (("J11", 1, 1, lambda A, B: Z.J11(A[0], B[0])),
                             ("J12", 1, 2, lambda A, B: Z.J12(A[0], B[0], B[1])),
                             ("J13", 1, 3, lambda A, B: Z.J13(A[0], B[0], B[1], B[2])),
                             ("J22", 2, 2, lambda A, B: Z.J22(A[0], A[1], B[0], B[1]))):
        for _ in range(npts):
            A = [pt() for _ in range(na)]
            B = [pt() for _ in range(nb)]
            ref = J_ratio(primes, ell, A, B)
            mine = fn(A, B)
            row = dict(J=name, A=[str(a) for a in A], B=[str(b) for b in B], ratio_def=str(ref), transcribed=str(mine),
                       rel=float(abs(ref - mine) / abs(ref)))
            if name == "J13":                    # red path: the sign CS08 prints
                printed = mine - 2 * Z.S13(A[0], B[0], B[1], B[2])
                row["rel_printed_sign"] = float(abs(ref - printed) / abs(ref))
            rows.append(row)
            print(name, "rel %.2e" % row["rel"], ("  printed sign: rel %.2e" % row["rel_printed_sign"]) if "rel_printed_sign" in row
                  else "", flush=True)
    co, co_red = coincidence(False), coincidence(True)
    for lab, c in (("corrected", co), ("printed (red path)", co_red)):
        print("coincidence,", lab, [(x["a"], x["b"], round(x["ratio_y1e2"], 4), round(x["ratio_y3e3"], 4)) for x in c["rows"]],
              "settles" if c["PASS"] else "does not settle", flush=True)
    out = dict(pmax=pmax, primes=primes, t=T_TEST, rel_tol=REL_TOL, red_min=RED_MIN, rows=rows,
               coincidence=co, coincidence_printed=co_red)
    out["PASS_definition"] = all(r["rel"] <= REL_TOL for r in rows)
    out["PASS_red_definition"] = all(r["rel_printed_sign"] >= RED_MIN for r in rows if r["J"] == "J13")
    out["PASS"] = bool(out["PASS_definition"] and out["PASS_red_definition"] and co["PASS"] and not co_red["PASS"])
    print("definition", out["PASS_definition"], "| red path fails as it must", out["PASS_red_definition"],
          "| coincidence", co["PASS"], "| printed sign fails coincidence", not co_red["PASS"], "=>",
          "PASS" if out["PASS"] else "FAIL", flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "check_ratios_j.json"), "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(int(a[0]) if a else 7, int(a[1]) if len(a) > 1 else 3)
