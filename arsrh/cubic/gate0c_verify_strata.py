"""
GATE 0c — verify the transfer law on the CYCLIC strata, against each conjugate's own CF.

General law (derived): for M = (a b; c d) integer, coprime, det Delta, and p/q a convergent of alpha,
    M(p/q) = (ap+bq)/(cp+dq),  g = gcd(ap+bq, cp+dq)   (and g | Delta, since
        Delta*p = d(ap+bq) - b(cp+dq)  and  Delta*q = -c(ap+bq) + a(cp+dq) )
    |M(alpha) - M(p/q)| = |Delta| |alpha - p/q| / (|c*alpha+d| |c*p/q+d|)
    Q = |cp+dq|/g ~ q|c*alpha+d|/g
=>  lambda' = (g^2/|Delta|) * lambda,   the SAME law, with |Delta| in place of m.

STRATA (from gate0b):
  A  S3            no rational Mobius map at all (alpha_2 not in Q(alpha_1))     <- CLEAN TARGET
  B  cyclic |t|=1  |Delta| = 1: in GL2(Z), Serret-equivalent, shared CF tail     <- CEILING
  C  cyclic |t|>1  unique rational M, NOT unimodular: attenuated by g^2/t^2      <- GRADED

Only B and C are touched here. Both are calibrators by construction. No S3 object is read.
"""
from __future__ import annotations
import json, math, os
from math import gcd

import mpmath as mp
from gate0_ladder import certified_cf, convergents, lam, bigratio

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)

DIG, NPQ = 1600, 2000
mp.mp.dps = DIG + 60


def roots_of(A, B, C):
    r = mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800)
    return sorted(mp.re(x) for x in r)


def cf_of(x, digits=DIG, maxn=NPQ):
    scale = 10 ** digits
    num = int(mp.floor(x * scale))
    return certified_cf(num, scale, maxn)


def check(label, A, B, C, M):
    a, b, c, d = M
    Delta = a * d - b * c
    r = roots_of(A, B, C)
    x0 = r[0]
    img = (a * x0 + b) / (c * x0 + d)
    j = min(range(3), key=lambda i: abs(r[i] - img))
    x1 = r[j]
    assert abs(x1 - img) < mp.mpf(10) ** -50, "M does not map root 0 to a root"

    a0 = cf_of(x0); a1 = cf_of(x1)
    P0, Q0 = convergents(a0); P1, Q1 = convergents(a1)
    idx = {Q1[k]: k for k in range(len(Q1))}

    hits, rels, gs = 0, [], {}
    tot = 0
    big_rows = []
    for n in range(1, len(a0) - 45):
        p, q = P0[n], Q0[n]
        A_, B_ = a * p + b * q, c * p + d * q
        if B_ == 0:
            continue
        if B_ < 0:
            A_, B_ = -A_, -B_
        g = gcd(abs(A_), B_)
        Q = B_ // g
        tot += 1
        lm = lam(a0, Q0, n)
        pred = (g * g / abs(Delta)) * lm
        gs[g] = gs.get(g, 0) + 1
        k = idx.get(Q)
        if k is not None and 1 <= k < len(a1) - 45 and P1[k] * g == A_ // 1 * 1 and True:
            # denominator matched; confirm the numerator too
            if P1[k] != A_ // g:
                continue
            meas = lam(a1, Q1, k)
            hits += 1
            rels.append(abs(meas / pred - 1.0))
            if a0[n + 1] >= 50:
                big_rows.append((a0[n + 1], g, pred, meas, a1[k + 1]))
    p_(f"\n  {label}:  x^3{A:+d}x^2{B:+d}x{C:+d}   M = {M}   t = {a+d}   |det| = {abs(Delta)}")
    p_(f"    certified PQs: {len(a0)} / {len(a1)}      g | Delta on every convergent: "
       f"{all(abs(Delta) % g == 0 for g in gs)}")
    p_(f"    g histogram: {dict(sorted(gs.items()))}")
    p_(f"    induced fraction is a convergent of the conjugate: {hits}/{tot} = {100*hits/tot:.1f}%")
    if rels:
        p_(f"    TRANSFER LAW lambda' = (g^2/|det|) lambda:  n = {len(rels)}   "
           f"max |meas/pred - 1| = {max(rels):.2e}   median = {sorted(rels)[len(rels)//2]:.2e}")
    if big_rows:
        p_(f"    exceptional events a >= 50 that land on a conjugate convergent: {len(big_rows)}")
        p_(f"      {'a(alpha1)':>10s} {'g':>4s} {'pred lam':>11s} {'meas lam':>11s} {'a(alpha2)':>10s}")
        for row in big_rows[:5]:
            p_(f"      {row[0]:>10d} {row[1]:>4d} {row[2]:>11.4f} {row[3]:>11.4f} {row[4]:>10d}")
    else:
        p_(f"    exceptional events a >= 50 landing on a conjugate convergent: 0")
    return {"label": label, "poly": [A, B, C], "M": list(M), "t": a + d, "det": abs(Delta),
            "hit_rate": hits / tot, "n_checked": len(rels),
            "max_rel_err": max(rels) if rels else None,
            "g_hist": {str(k): v for k, v in sorted(gs.items())},
            "n_big_transferred": len(big_rows)}


if __name__ == "__main__":
    p_("=== GATE 0c — the transfer law on the cyclic strata ===")
    p_("law: lambda' = (g^2/|det|) lambda, g = gcd(ap+bq, cp+dq), g | det")

    src = json.load(open(os.path.join(HERE, "gate0b_stratify_measured.json")))
    ex = src["examples"]
    picks, want = [], [1, 2, 5, 13]
    for t in want:
        for e in ex:
            A, B, C, D, a, b, c, d, tt, Dl = e
            if abs(tt) == t:
                picks.append((f"stratum {'B' if t == 1 else 'C'} |t|={t}", A, B, C, (a, b, c, d)))
                break

    out = [check(*pk) for pk in picks]

    p_("\n  SUMMARY — attenuation is real and graded, inside the target's own construction")
    p_(f"  {'stratum':>16s} {'|det|':>6s} {'hit rate':>10s} {'a>=50 transferred':>19s}")
    for o in out:
        p_(f"  {o['label']:>16s} {o['det']:>6d} {100*o['hit_rate']:>9.1f}% {o['n_big_transferred']:>19d}")

    json.dump(out, open(os.path.join(HERE, "gate0c_verify_measured.json"), "w"), indent=2)
    p_("\nwrote gate0c_verify_measured.json")
