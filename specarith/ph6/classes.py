"""Phase 6 G1-pre (seal §8, §9.2): hyperbolic and glide-reflection classes of PSL(2,Z), three independent ways.

For each trace t <= T_MAX:
  hyperbolic (det +1, discriminant D = t^2 - 4, t >= 3) and glide reflection (det -1, D = t^2 + 4, t >= 1):
  count  = number of Gamma+-conjugacy classes with |trace| = t (primitive or not)
  lsum   = sum over those classes of log N(P0), P0 the primitive root (the Selberg weight numerator)

  (i)   GAUSS: cycles of Gauss-reduced binary quadratic forms of discriminant D, imprimitive forms included
        (count only; Gauss cycles = proper classes, SB §2.2).
  (ii)  CF: Mayer/Efrat continued-fraction necklaces (Ef93 p. 210-212). A primitive necklace (a1..am), a_i >= 1, gives
        M = prod [[a_i,1],[1,0]] with det (-1)^m. Even m: two PSL(2,Z) hyperbolic classes of trace tr M (orbits of
        the even rotations). Odd m: one glide class of trace tr M and one hyperbolic class of trace tr(M^2) = tr(M)^2+2.
        Non-primitive classes = powers (trace recursions t_k = t t_{k-1} -/+ t_{k-2}); log N(P0) = 2 arccosh / arcsinh.
  (iii) PARI: count = sum_{f | l} h+(d f^2), lsum = sum_{f | l} h+(d f^2) * k [r[1]^1 : r[f]^1] * log eps1
        with k = 2 for hyperbolic classes and k = 1 for glide reflections,
        t^2 -/+ 4 = d l^2 with d fundamental (BS07 (2.54), (2.58), Lemma 2.10); h+ = qfbclassno * (2 if the order's
        fundamental unit has norm +1 else 1); eps1 = proper (norm +1) fundamental unit of the maximal order.

G1-pre PASSES iff all three counts agree exactly and lsum(ii) == lsum(iii) to 1e-10 for every t <= T_MAX.
Pure number theory: reads no spectrum.  Usage: python -I classes.py [T_MAX] [OUT.json]
"""
import json
import math
import sys

T_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 30


# ---------- (i) Gauss-reduced cycles ----------
def gauss_cycles(D):
    """Number of proper equivalence classes of all forms (a,b,c), b^2-4ac = D > 0 non-square, via reduced cycles."""
    r = math.isqrt(D)
    assert r * r != D
    sq = math.sqrt(D)
    reduced = set()
    for b in range(1, r + 1):
        if (b - D) % 2:
            continue
        m = (b * b - D) // 4                 # = a*c (negative)
        for a_abs in range(1, abs(m) + 1):
            if abs(m) % a_abs:
                continue
            for a in (a_abs, -a_abs):
                if sq - b < 2 * abs(a) < sq + b:
                    reduced.add((a, b, m // a))

    def rho(f):
        a, b, c = f
        # b' = -b mod 2|c| with sqrt(D) - 2|c| < b' < sqrt(D)
        two_c = 2 * abs(c)
        bp = -b
        k = math.floor((sq - bp) / two_c)
        bp = bp + k * two_c
        if bp >= sq:
            bp -= two_c
        while bp <= sq - two_c:
            bp += two_c
        ap = (bp * bp - D) // (4 * c)
        return (c, bp, ap)

    seen, cycles = set(), 0
    for f in sorted(reduced):
        if f in seen:
            continue
        cycles += 1
        g = f
        while True:
            seen.add(g)
            g = rho(g)
            assert g in reduced, (D, f, g)
            if g == f:
                break
    return cycles


# ---------- (ii) continued-fraction necklaces ----------
def mat_mul(A, B):
    return ((A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]),
            (A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]))


def is_primitive_necklace_rep(w):
    """w is the lexicographically least rotation and has minimal period len(w)."""
    m = len(w)
    rots = [w[i:] + w[:i] for i in range(m)]
    if any(r < w for r in rots[1:]):
        return False
    return all(r != w for r in rots[1:])


def cf_classes(tmax_hyp, tmax_glide):
    """Primitive classes from necklaces: returns {('h'|'g', t): [log N(P0) of each primitive class]}."""
    prim = {}
    bound = max(tmax_hyp, tmax_glide)

    def rec(word, M):
        if word:
            m = len(word)
            tr = M[0][0] + M[1][1]
            if is_primitive_necklace_rep(tuple(word)):
                if m % 2 == 0 and tr <= tmax_hyp:
                    L = 2 * math.acosh(tr / 2)
                    prim.setdefault(("h", tr), []).extend([L, L])
                if m % 2 == 1:
                    if tr <= tmax_glide:
                        prim.setdefault(("g", tr), []).append(2 * math.asinh(tr / 2))
                    t2 = tr * tr + 2
                    if t2 <= tmax_hyp:
                        prim.setdefault(("h", t2), []).append(2 * math.acosh(t2 / 2))
        # extend: entries grow monotonically, prune when the (0,0) entry exceeds the bound
        for a in range(1, bound + 2):
            N = mat_mul(M, ((a, 1), (1, 0)))
            if N[0][0] > bound + 2 and N[1][1] >= 0 and N[0][0] + N[1][1] > bound + 2:
                break
            if len(word) >= 40:
                break
            rec(word + [a], N)

    rec([], ((1, 0), (0, 1)))
    return prim


def all_classes_from_primitive(prim, tmax_hyp, tmax_glide):
    """Add powers: hyperbolic t_k = t t_{k-1} - t_{k-2}; glide odd powers are glides, even powers hyperbolic."""
    count, lsum = {}, {}

    def add(kind, t, L0):
        count[(kind, t)] = count.get((kind, t), 0) + 1
        lsum[(kind, t)] = lsum.get((kind, t), 0.0) + L0

    for (kind, t), Ls in prim.items():
        for L0 in Ls:
            if kind == "h":
                tk_2, tk_1 = 2, t           # traces of P^0, P^1 (det +1)
                while tk_1 <= tmax_hyp:
                    add("h", tk_1, L0)
                    tk_2, tk_1 = tk_1, t * tk_1 - tk_2
            else:
                # glide P (det -1): traces of P^k satisfy t_k = t t_{k-1} + t_{k-2}; odd k glide, even k hyperbolic
                # (the even powers are already counted as the hyperbolic class from tr(M^2) and its powers)
                tk_2, tk_1, k = 2, t, 1
                while True:
                    if k % 2 == 1:
                        if tk_1 > tmax_glide:
                            break
                        add("g", tk_1, L0)
                    tk_2, tk_1, k = tk_1, t * tk_1 + tk_2, k + 1
                    if k > 60:
                        break
    return count, lsum


# ---------- (iii) PARI ----------
def pari_counts(tmax_hyp, tmax_glide):
    import cypari2
    pari = cypari2.Pari()
    pari.set_real_precision(38)
    count, lsum = {}, {}
    for kind, ts, sgn in (("h", range(3, tmax_hyp + 1), -4), ("g", range(1, tmax_glide + 1), 4)):
        for t in ts:
            D = t * t + sgn
            d = int(pari(f"coredisc({D})"))
            l = math.isqrt(D // d)
            assert d * l * l == D
            log_eps1 = _log_proper_unit(pari, d)          # eps1: proper fundamental unit, maximal order
            c, s = 0, 0.0
            for f in range(1, l + 1):
                if l % f:
                    continue
                Df = d * f * f
                h = int(pari(f"qfbclassno({Df})"))
                hplus = h * (2 if int(pari(f"quadunitnorm({Df})")) == 1 else 1)
                idx = round(_log_proper_unit(pari, Df) / log_eps1)
                assert abs(idx * log_eps1 - _log_proper_unit(pari, Df)) < 1e-9 * idx * log_eps1, (D, f)
                c += hplus
                # sum of log N(P0) over the classes: hyperbolic 2 [index] log eps1 per class (BS07 Lemma 2.10);
                # glide (det -1) [index] log eps1 per class, since N(T0) = ((t + sqrt(t^2+4))/2)^2 (BS07 (2.50)):
                # t = 1 gives log N = 2 log phi = log eps1. (The first G1-pre run on 2026-10-07 used the factor 2 for
                # both kinds; the glide sums then came out exactly half the CF sums at every t. The RHS uses
                # C(t) log eps1 from BS07 (2.39)/(2.40) directly and was never affected.)
                s += hplus * (2 if kind == "h" else 1) * idx * log_eps1
            count[(kind, t)] = c
            lsum[(kind, t)] = s
    return count, lsum


def _log_proper_unit(pari, D):
    """log of the smallest unit > 1 of norm +1 in the order of discriminant D."""
    # u = x + y*w with w = quadgen(D) = (D mod 2 + sqrt(D))/2; t_QUAD components are [pol, x, y]
    x = int(pari(f"component(quadunit({D}), 2)"))
    y = int(pari(f"component(quadunit({D}), 3)"))
    w = ((D % 2) + math.sqrt(D)) / 2
    eps = abs(x + y * w)
    if eps < 1:
        eps = 1 / eps
    nrm = int(pari(f"quadunitnorm({D})"))
    return math.log(eps) * (2 if nrm == -1 else 1)


def main():
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    prim = cf_classes(T_MAX, T_MAX)
    cf_count, cf_lsum = all_classes_from_primitive(prim, T_MAX, T_MAX)
    pa_count, pa_lsum = pari_counts(T_MAX, T_MAX)
    rows, ok = [], True
    for kind, ts, sgn in (("h", range(3, T_MAX + 1), -4), ("g", range(1, T_MAX + 1), 4)):
        for t in ts:
            D = t * t + sgn
            g = gauss_cycles(D)
            c2, c3 = cf_count.get((kind, t), 0), pa_count[(kind, t)]
            l2, l3 = cf_lsum.get((kind, t), 0.0), pa_lsum[(kind, t)]
            agree = (g == c2 == c3) and abs(l2 - l3) <= 1e-10 * max(1.0, l3)
            ok &= agree
            rows.append(dict(kind=kind, t=t, D=D, gauss=g, cf=c2, pari=c3, lsum_cf=l2, lsum_pari=l3, agree=agree))
    for r in rows:
        if r["t"] <= 8 or not r["agree"]:
            print(r)
    print("G1-pre", "PASS" if ok else "FAIL", f"(t <= {T_MAX}, {len(rows)} rows)")
    if out_path:
        with open(out_path, "w") as f:
            json.dump(dict(t_max=T_MAX, verdict="PASS" if ok else "FAIL", rows=rows), f, indent=1)


if __name__ == "__main__":
    main()
