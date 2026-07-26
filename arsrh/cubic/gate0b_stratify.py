"""
GATE 0b — stratify totally real cubics before any arm runs.

Reviewer's correction, taken: Shanks's simplest cubics x^3 - a x^2 - (a+3) x - 1 have their roots
permuted by the Mobius map x -> -1/(x+1), which is UNIMODULAR (det 1) -> Serret-equivalent, shared CF
tail, rho = 1 with no attenuation. So "the derivable mechanism is absent by theorem, both sub-cases"
is FALSE on the cyclic sub-case, and pooling all totally real cubic conjugates mixes a rho=1
subfamily into the target.

TWO CLAIMS TESTED HERE.

[H] Stratum 3 as the reviewer defined it ("cyclic WITHOUT an order-3 element of PGL_2(Q)") is EMPTY.
    Over Qbar a 3-cycle on 3 distinct points determines M uniquely. If sigma generates Gal = C_3 with
    alpha_i -> alpha_{i+1}, then sigma(M) is the unique map sending sigma(alpha_i) -> sigma(alpha_{i+1}),
    i.e. alpha_{i+1} -> alpha_{i+2} -- which is M. So sigma(M) = M, and PGL_2(Qbar)^Gal = PGL_2(Q) by
    Hilbert 90. EVERY cyclic cubic has its 3-cycle realised over Q.

[T] The replacement stratum is the DETERMINANT. For a coprime-integer representative, M^3 = lambda I
    forces (Cayley-Hamilton) Delta = t^2 with t = tr M, and lambda = -t^3. So:
        |t| = 1  ->  M in GL_2(Z)  ->  Serret-equivalent, shared CF tail, rho = 1     (CEILING)
        |t| > 1  ->  M not in GL_2(Z) -> transfer ATTENUATED by g^2/t^2               (GRADED)
    and |Delta| is a GL_2(Z)-conjugation invariant (if d divides every entry of U M U^-1 then it
    divides every entry of M = U^-1 (U M U^-1) U), hence an invariant of the object up to Serret
    equivalence -- not merely of the polynomial.

METHOD. Numerics only PROPOSE the matrix; an exact integer identity DISPOSES:
        (c x + d)^3 f((a x + b)/(c x + d)) == kappa * f(x)      over Z[x]
holds iff M permutes the root set. Nothing is accepted on a numerical tolerance.
"""
from __future__ import annotations
import json, math, os
from fractions import Fraction
from math import gcd
from collections import Counter

import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
mp.mp.dps = 60


# ------------------------------------------------------------------ polynomial helpers (exact, Z[x])
def pmul(u, v):
    w = [0] * (len(u) + len(v) - 1)
    for i, ui in enumerate(u):
        if ui:
            for j, vj in enumerate(v):
                w[i + j] += ui * vj
    return w


def ppow(u, k):
    w = [1]
    for _ in range(k):
        w = pmul(w, u)
    return w


def padd(*ps):
    n = max(len(x) for x in ps)
    w = [0] * n
    for x in ps:
        for i, xi in enumerate(x):
            w[i] += xi
    return w


def permutes_roots(A, B, C, a, b, c, d):
    """EXACT check that x -> (ax+b)/(cx+d) permutes the roots of x^3+Ax^2+Bx+C.
    Returns kappa if it does, else None."""
    num, den = [b, a], [d, c]                      # ax+b and cx+d as [const, x]
    lhs = padd(ppow(num, 3),
               [A * t for t in pmul(ppow(num, 2), den)],
               [B * t for t in pmul(num, ppow(den, 2))],
               [C * t for t in ppow(den, 3)])
    f = [C, B, A, 1]
    lhs += [0] * (4 - len(lhs))
    if lhs[3] == 0 and lhs[2] == 0 and lhs[1] == 0 and lhs[0] == 0:
        return None
    for i in range(4):
        if f[i]:
            k, r = divmod(lhs[i], f[i])
            break
    else:
        return None
    if r or any(lhs[i] != k * f[i] for i in range(4)) or k == 0:
        return None
    return k


def rationalize(x, maxden=10 ** 7, tol=mp.mpf(10) ** -35):
    """continued-fraction rationalisation of an mpf; None if it does not converge cleanly."""
    if not mp.isfinite(x) or abs(x) > mp.mpf(10) ** 12:
        return None
    a0 = mp.floor(x)
    terms = [int(a0)]
    y = x - a0
    for _ in range(40):
        try:
            fr = Fraction(terms[-1])
            for t in reversed(terms[:-1]):
                fr = t + 1 / fr
        except ZeroDivisionError:
            return None
        if abs(mp.mpf(fr.numerator) / fr.denominator - x) < tol and fr.denominator <= maxden:
            return fr
        if y == 0:
            return fr
        y = 1 / y
        a = mp.floor(y)
        terms.append(int(a))
        y -= a
    return None


def mobius_of_cubic(A, B, C):
    """Find the order-3 Mobius map permuting the roots. Returns (a,b,c,d,t,Delta) or None."""
    rts = mp.polyroots([1, A, B, C], maxsteps=300, extraprec=400)
    if any(abs(mp.im(r)) > mp.mpf(10) ** -30 for r in rts):
        return None
    r = sorted(mp.re(x) for x in rts)
    for perm in ((1, 2, 0), (2, 0, 1)):
        for fixed in range(4):                      # set one unknown to 1, solve the rest
            rows, rhs = [], []
            for i in range(3):
                s, t_ = r[i], r[perm[i]]
                co = [s, mp.mpf(1), -t_ * s, -t_]   # a, b, c, d
                rows.append([co[j] for j in range(4) if j != fixed])
                rhs.append(-co[fixed])
            try:
                sol = mp.lu_solve(mp.matrix(rows), mp.matrix(rhs))
            except Exception:
                continue
            v = []
            k = 0
            for j in range(4):
                if j == fixed:
                    v.append(mp.mpf(1))
                else:
                    v.append(sol[k]); k += 1
            fr = [rationalize(x) for x in v]
            if any(x is None for x in fr):
                continue
            den = 1
            for x in fr:
                den = den * x.denominator // gcd(den, x.denominator)
            iv = [int(x * den) for x in fr]
            g = 0
            for x in iv:
                g = gcd(g, abs(x))
            if g == 0:
                continue
            a, b, c, d = (x // g for x in iv)
            if permutes_roots(A, B, C, a, b, c, d) is None:
                continue
            if (a, b, c, d) == (1, 0, 0, 1):        # identity: wrong perm branch
                continue
            return a, b, c, d, a + d, a * d - b * c
    return None


def disc(A, B, C):
    return 18 * A * B * C - 4 * A ** 3 * C + A ** 2 * B ** 2 - 4 * B ** 3 - 27 * C ** 2


def irreducible(A, B, C):
    if C == 0:
        return False
    n = abs(C)
    for k in range(1, n + 1):
        if n % k == 0:
            for s in (k, -k):
                if s ** 3 + A * s ** 2 + B * s + C == 0:
                    return False
    return True


if __name__ == "__main__":
    # ------------------------------------------------------------------ [S] the Shanks check
    p_("=== GATE 0b — stratification of totally real cubics ===\n")
    p_("[S] Shanks's simplest cubics  x^3 - a x^2 - (a+3) x - 1  (reviewer's counterexample)")
    p_(f"  {'a':>4s} {'disc':>10s} {'square?':>8s} {'Mobius (a,b,c,d)':>20s} {'t':>4s} {'|det|':>6s} {'stratum':>10s}")
    shanks = []
    for aa in range(0, 12):
        A, B, C = -aa, -(aa + 3), -1
        if not irreducible(A, B, C):
            continue
        D = disc(A, B, C)
        sq = math.isqrt(D) ** 2 == D if D > 0 else False
        M = mobius_of_cubic(A, B, C)
        if M is None:
            p_(f"  {aa:>4d} {D:>10d} {str(sq):>8s} {'-- none found --':>20s}")
            continue
        a, b, c, d, t, Dl = M
        st = "CEILING" if abs(Dl) == 1 else "GRADED"
        shanks.append((aa, D, t, Dl))
        p_(f"  {aa:>4d} {D:>10d} {str(sq):>8s} {str((a,b,c,d)):>20s} {t:>4d} {abs(Dl):>6d} {st:>10s}")

    # ------------------------------------------------------------------ [H]+[T] the census
    p_("\n[H]+[T] census over x^3 + A x^2 + B x + C, |A|,|B|,|C| <= 12, irreducible, disc > 0")
    N = 12
    n_tr = n_cyc = n_s3 = 0
    found, missing = [], []
    tcount = Counter()
    for A in range(-N, N + 1):
        for B in range(-N, N + 1):
            for C in range(-N, N + 1):
                D = disc(A, B, C)
                if D <= 0 or not irreducible(A, B, C):
                    continue
                n_tr += 1
                if math.isqrt(D) ** 2 != D:
                    n_s3 += 1
                    continue
                n_cyc += 1
                M = mobius_of_cubic(A, B, C)
                if M is None:
                    missing.append((A, B, C, D))
                else:
                    a, b, c, d, t, Dl = M
                    tcount[abs(t)] += 1
                    found.append((A, B, C, D, a, b, c, d, t, Dl))

    p_(f"  totally real irreducible cubics in the box : {n_tr}")
    p_(f"    S3      (disc not a square)              : {n_s3}  ({100*n_s3/n_tr:.2f}%)")
    p_(f"    cyclic  (disc a square)                  : {n_cyc}  ({100*n_cyc/n_tr:.2f}%)")
    p_(f"\n  [H] cyclic cubics with NO rational order-3 Mobius map: {len(missing)}")
    if missing:
        p_(f"      {missing[:5]}   <-- Hilbert-90 argument would be WRONG")
    else:
        p_("      -> stratum 3 as defined (cyclic, no Mobius map) is EMPTY, as the argument predicts.")

    p_(f"\n  [T] |trace| of the coprime-integer representative (Delta = t^2):")
    for t in sorted(tcount):
        lbl = "CEILING  (in GL2(Z): shared CF tail, rho=1)" if t == 1 else \
              f"GRADED   (attenuation g^2/{t*t})"
        p_(f"      |t| = {t}: {tcount[t]:>4d} cubics   |det| = {t*t:<4d}  {lbl}")
    p_(f"      check Delta == t^2 on every one: "
       f"{all(Dl == t*t for *_, t, Dl in found)}")

    p_(f"\n  distinct Mobius maps found (up to sign), by |t|:")
    seen = {}
    for A, B, C, D, a, b, c, d, t, Dl in found:
        seen.setdefault(abs(t), set()).add((a, b, c, d))
    for t in sorted(seen):
        ex = sorted(seen[t])[:4]
        p_(f"      |t|={t}: {len(seen[t])} distinct, e.g. {ex}")

    json.dump({"box": N, "n_totally_real": n_tr, "n_S3": n_s3, "n_cyclic": n_cyc,
               "n_cyclic_without_mobius": len(missing),
               "trace_counts": {str(k): v for k, v in sorted(tcount.items())},
               "shanks": [[a, D, t, Dl] for a, D, t, Dl in shanks],
               "examples": found[:40]},
              open(os.path.join(HERE, "gate0b_stratify_measured.json"), "w"), indent=2)
    p_("\nwrote gate0b_stratify_measured.json")
