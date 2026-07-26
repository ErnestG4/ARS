"""
GATE 0 (BLOCKING) -- is the (cbrt m, cbrt m^2) ladder derivable?

PAPER DERIVATION (verified numerically below).
  alpha = m^(1/3), beta = m^(2/3) = m/alpha.  p/q a convergent of alpha, gcd(p,q)=1.
  Induced approximation to beta:  m q / p.   gcd(mq, p) = gcd(m, p) =: g   (since gcd(q,p)=1),
  so in lowest terms   P/Q = (m q / g) / (p / g),   Q = p/g.

  EXACT:  beta - mq/p = m (p - q alpha) / (alpha p).

  Define the implied partial quotient of ANY fraction P/Q for target x:
      lambda(P/Q) := 1 / ( Q^2 |x - P/Q| ).
  For a convergent of x this equals x_{n+1} + q_{n-1}/q_n  in [a_{n+1}, a_{n+1}+2).

  Then, EXACTLY:
      lambda' = (g^2/m) * lambda * (alpha q / p),      alpha q / p = 1 + O(1/(lambda q^2))
  hence
      ***  lambda' = (g^2 / m) * lambda,  g = gcd(m, p),  relative error O(q^-2)  ***
      ***  log Q   = log q + (1/3) log m - log g       (a DETERMINISTIC translation)  ***

  Involution check (paper): applying the map to P/Q sends g -> m/g, factor (m/g)^2/m = m/g^2,
  and (m/g^2)(g^2/m) = 1.  Self-inverse, as it must be.

  "roughly half" is the m=2, g=1 case: lambda' = lambda/2.  The factor DOES depend on m,
  and it also depends on the gcd -- for m=2, p even gives lambda' = 2*lambda instead.

WHAT THIS SCRIPT CHECKS
  [1] the transfer law, measured against beta's OWN continued fraction (end-to-end, not algebra)
  [2] the location shift, measured
  [3] the gcd branch: distribution of g, and the law separately within each branch
  [4] whether the induced fraction IS a convergent of beta, as a function of lambda'
  [5] the involution, numerically
  [6] "roughly half": the m-dependence, across a family of m
"""
from __future__ import annotations
import json, math, os
from math import gcd
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)


# ------------------------------------------------------------------ exact integer machinery
def inthroot(n: int, k: int) -> int:
    """floor(n ** (1/k)) for ints, exact."""
    if n < 0:
        raise ValueError
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + k - 1) // k + 1)
    while True:
        y = ((k - 1) * x + n // x ** (k - 1)) // k
        if y >= x:
            return x
        x = y


def cf_ratio(num: int, den: int, maxn: int) -> list[int]:
    a = []
    while den and len(a) < maxn:
        qq, r = divmod(num, den)
        a.append(qq)
        num, den = den, r
    return a


def certified_cf(num: int, den: int, maxn: int) -> list[int]:
    """CF terms of any x in [num/den, (num+1)/den]: common prefix of the two endpoints,
    minus the last two terms as margin."""
    a1 = cf_ratio(num, den, maxn + 8)
    a2 = cf_ratio(num + 1, den, maxn + 8)
    k = 0
    while k < min(len(a1), len(a2)) and a1[k] == a2[k]:
        k += 1
    return a1[:max(0, k - 2)][:maxn]


def convergents(a: list[int]):
    """p[i], q[i] for i = 0..len(a)-1."""
    P = [a[0], a[1] * a[0] + 1]
    Q = [1, a[1]]
    for i in range(2, len(a)):
        P.append(a[i] * P[-1] + P[-2])
        Q.append(a[i] * Q[-1] + Q[-2])
    return P, Q


def tail_value(a: list[int], i: int, depth: int = 40) -> float:
    """[a_i; a_{i+1}, ...] as a float."""
    j = min(len(a) - 1, i + depth)
    v = float(a[j])
    while j > i:
        j -= 1
        v = a[j] + 1.0 / v
    return v


def bigratio(x: int, y: int) -> float:
    """x/y as a float for arbitrarily large ints."""
    return (x * (1 << 64) // y) / float(1 << 64)


def lam(a: list[int], Q: list[int], n: int) -> float:
    """implied partial quotient of the n-th convergent: alpha_{n+1} + q_{n-1}/q_n."""
    return tail_value(a, n + 1) + (bigratio(Q[n - 1], Q[n]) if n >= 1 else 0.0)


def cf_cbrt(m: int, power: int, digits: int, maxn: int) -> list[int]:
    """certified CF of m^(power/3), power in {1,2}."""
    scale = 10 ** digits
    num = inthroot(m ** power * scale ** 3, 3)
    return certified_cf(num, scale, maxn)


# ------------------------------------------------------------------ the test
def run(m: int, npq: int, digits: int, A: int = 50, verbose: bool = True):
    a_al = cf_cbrt(m, 1, digits, npq)
    a_be = cf_cbrt(m, 2, digits, npq)
    Pa, Qa = convergents(a_al)
    Pb, Qb = convergents(a_be)
    denom_index = {Qb[k]: k for k in range(len(Qb))}

    rows = []
    for n in range(1, len(a_al) - 45):          # -45: tail_value needs headroom
        p, q = Pa[n], Qa[n]
        g = gcd(m, p)
        Q = p // g
        k = denom_index.get(Q)
        lm = lam(a_al, Qa, n)
        pred = (g * g / m) * lm
        # location
        shift_meas = math.log(Q) - math.log(q)
        shift_pred = math.log(m) / 3.0 - math.log(g)
        if k is not None and 1 <= k < len(a_be) - 45:
            meas = lam(a_be, Qb, k)
            rows.append((n, k, g, lm, pred, meas, shift_meas, shift_pred,
                         a_al[n + 1], a_be[k + 1], math.log(q)))
        else:
            rows.append((n, None, g, lm, pred, None, shift_meas, shift_pred,
                         a_al[n + 1], None, math.log(q)))

    hit = [r for r in rows if r[5] is not None]
    if verbose:
        p_(f"\n===== m = {m}   ({len(a_al)} certified PQs of cbrt(m), {len(a_be)} of cbrt(m^2)) =====")
        p_(f"[4] induced fraction is a convergent of beta: {len(hit)}/{len(rows)} "
           f"= {100*len(hit)/len(rows):.1f}%")
        gc = Counter(r[2] for r in rows)
        p_(f"[3] gcd(m, p) branch counts: {dict(sorted(gc.items()))}")
        rel = [abs(r[5] / r[4] - 1.0) for r in hit]
        p_(f"[1] TRANSFER LAW  lambda' = (g^2/m) lambda, measured against beta's own CF:")
        p_(f"    n = {len(hit)}   max |meas/pred - 1| = {max(rel):.3e}   "
           f"median = {sorted(rel)[len(rel)//2]:.3e}")
        for gval in sorted(gc):
            sub = [r for r in hit if r[2] == gval]
            if sub:
                rr = [abs(r[5] / r[4] - 1.0) for r in sub]
                p_(f"      g = {gval:3d}: n = {len(sub):5d}  factor g^2/m = {gval*gval/m:8.4f}  "
                   f"max rel err = {max(rr):.2e}")
        sh = [abs(r[6] - r[7]) for r in rows]
        p_(f"[2] LOCATION  log Q - log q = (1/3)log m - log g:  max |err| = {max(sh):.3e}")
        big = [r for r in rows if r[8] >= A]
        bighit = [r for r in big if r[5] is not None]
        p_(f"[6] exceptional events a_{{n+1}} >= {A}: {len(big)} in alpha; "
           f"{len(bighit)} land on a beta convergent")
        if bighit:
            p_(f"    {'a_alpha':>9s} {'g':>3s} {'pred lam':>10s} {'meas lam':>10s} {'a_beta':>8s}")
            for r in bighit[:8]:
                p_(f"    {r[8]:>9d} {r[2]:>3d} {r[4]:>10.3f} {r[5]:>10.3f} {r[9]:>8d}")
    return rows, a_al, a_be, Pa, Qa, Pb, Qb


if __name__ == "__main__":
    p_("=== GATE 0 — is the (cbrt m, cbrt m^2) ladder derivable? ===")
    p_("derived on paper:  lambda' = (g^2/m) lambda,  g = gcd(m,p);  "
       "log Q = log q + (1/3)log m - log g")

    NPQ, DIG = 2000, 1400
    out = {}
    for m in (2, 3, 5, 6, 7, 10, 12):
        rows, a_al, a_be, Pa, Qa, Pb, Qb = run(m, NPQ, DIG)
        hit = [r for r in rows if r[5] is not None]
        out[m] = {
            "n_pq_alpha": len(a_al), "n_pq_beta": len(a_be),
            "frac_induced_is_convergent": len(hit) / len(rows),
            "max_rel_err_transfer": max(abs(r[5] / r[4] - 1.0) for r in hit),
            "max_abs_err_location": max(abs(r[6] - r[7]) for r in rows),
            "gcd_counts": {str(k): v for k, v in
                           sorted(Counter(r[2] for r in rows).items())},
        }

    # -------------------------------------------------------------- [5] involution, numerically
    p_("\n[5] INVOLUTION — map alpha->beta then beta->alpha, on m = 6 (g takes both values)")
    m = 6
    a_al = cf_cbrt(m, 1, DIG, NPQ); a_be = cf_cbrt(m, 2, DIG, NPQ)
    Pa, Qa = convergents(a_al); Pb, Qb = convergents(a_be)
    bad = 0; tested = 0
    for n in range(1, 400):
        p, q = Pa[n], Qa[n]
        g = gcd(m, p); Q = p // g; P = m * q // g
        g2 = gcd(m, P); Q2 = P // g2; P2 = m * Q // g2
        tested += 1
        if (P2, Q2) != (p, q):
            bad += 1
    p_(f"    round trip returns the original convergent: {tested-bad}/{tested}")
    p_(f"    factor composition (g^2/m)*((m/g)^2/m) = 1 identically")

    # -------------------------------------------------------------- [6] the m-dependence
    p_("\n[6] 'ROUGHLY HALF' — the factor across m, at g = 1")
    p_(f"    {'m':>4s} {'g=1 factor 1/m':>16s} {'frac of n with g=1':>20s}")
    for m in (2, 3, 5, 6, 7, 10, 12):
        c = out[m]["gcd_counts"]
        tot = sum(c.values())
        p_(f"    {m:>4d} {1.0/m:>16.4f} {c.get('1', 0)/tot:>20.3f}")
    p_("    -> 'roughly half' is the m = 2, g = 1 case ONLY. The factor is g^2/m.")

    json.dump(out, open(os.path.join(HERE, "gate0_ladder_measured.json"), "w"), indent=2)
    p_("\nwrote gate0_ladder_measured.json")
