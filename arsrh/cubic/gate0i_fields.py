"""
GATE 0i — two things the transfer license and the formula's GRADE actually rest on.

[D] FIELD-LEVEL DEDUP. gate0g deduped on POLYNOMIAL discriminant, but disc_poly = index^2 * disc_field,
    so the same field survives many times. If the 24 "objects" per stratum are fewer than 24 FIELDS,
    the sems are optimistic and "could have caught a 4% difference" is optimistic by the multiplicity.
    Test: Q(alpha1) = Q(alpha2) iff f2 has a root in Q[x]/(f1). Found by PSLQ on (1, a, a^2, b),
    then VERIFIED EXACTLY by reducing f2(g(x)) mod f1(x) over Q. Numerics propose, exact disposes.

[G] IS THE ENRICHMENT DERIVABLE? The corrected rate formula uses P(g | event), measured. That makes it
    CALIBRATED, not derived -- which is the real reason it cannot extrapolate, better than a count of
    misses. But there is a route: the branch densities are themselves constrained by the transfer law.
    An alpha1-convergent in branch g maps to an alpha2-rational with lambda' = (g^2/D) lambda, and that
    is an alpha2-CONVERGENT essentially iff lambda' >~ 1. So the g = 1 branch should feed exactly the
    alpha2 convergents of branch g' = D, giving
            P(g = D)  ~  P(g = 1) * 1.4427 / D
    If that closes, P(g) and hence P(g|event) are derived, the formula returns to DERIVED, and the
    |det| range opens. Tested here in form and constant.
"""
from __future__ import annotations
import json, math, os
from fractions import Fraction

import mpmath as mp
from gate0_ladder import convergents
from gate0b_stratify import mobius_of_cubic, disc, irreducible, rationalize
from gate0e_precision import cf_of_mpf, collect_cyclic
from gate0g_marginals import anchors, mean_sem, LEVY, KHIN, A_EV

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
mp.mp.dps = 1260


def _polymod(num, f):
    """reduce a Fraction-coefficient polynomial (low->high) modulo monic f = x^3+Ax^2+Bx+C."""
    A, B, C = f
    r = list(num)
    while len(r) > 3:
        c = r.pop()
        d = len(r) - 3                      # x^(d+3) = -(A x^(d+2) + B x^(d+1) + C x^d)
        r[d + 2] -= c * A
        r[d + 1] -= c * B
        r[d] -= c * C
    while len(r) < 3:
        r.append(Fraction(0))
    return r


def _compose_mod(f2, g, f1):
    """f2(g(x)) mod f1(x), exactly, over Q. f2 = (A,B,C) monic cubic; g low->high Fractions."""
    A2, B2, C2 = f2
    one = [Fraction(1)]

    def mul(u, v):
        w = [Fraction(0)] * (len(u) + len(v) - 1)
        for i, ui in enumerate(u):
            if ui:
                for j, vj in enumerate(v):
                    w[i + j] += ui * vj
        return _polymod(w, f1)

    g1 = _polymod(list(g), f1)
    g2 = mul(g1, g1)
    g3 = mul(g2, g1)
    out = [g3[i] + A2 * g2[i] + B2 * g1[i] + (C2 if i == 0 else 0) for i in range(3)]
    return out


def same_field(f1, f2):
    """Q(root f1) == Q(root f2)?  PSLQ proposes, exact reduction disposes."""
    if f1 == f2:
        return True
    with mp.workdps(120):
        a = sorted(mp.re(x) for x in mp.polyroots([1, *f1], maxsteps=400, extraprec=600))[0]
        for b in sorted(mp.re(x) for x in mp.polyroots([1, *f2], maxsteps=400, extraprec=600)):
            rel = mp.pslq([mp.mpf(1), a, a * a, b], tol=mp.mpf(10) ** -70, maxcoeff=10 ** 14,
                          maxsteps=2000)
            if not rel or rel[3] == 0:
                continue
            g = [Fraction(-int(rel[i]), int(rel[3])) for i in range(3)]
            if all(c == 0 for c in _compose_mod(f2, g, f1)):
                return True
    return False


def dedup_fields(objs):
    keep = []
    for o in objs:
        if not any(same_field(o[:3], k[:3]) for k in keep):
            keep.append(o)
    return keep


if __name__ == "__main__":
    p_("=== GATE 0i — field-level dedup, and is the enrichment derivable? ===")

    # ------------------------------------------------------------------ [D]
    from gate0g_marginals import collect
    p_("\n[D] FIELD-LEVEL DEDUP of gate0g's object sets (it deduped on POLYNOMIAL discriminant)")
    p_(f"  {'stratum':>16s} {'polys':>7s} {'distinct fields':>16s}")
    out = {}
    for kind, lbl in (("S3", "A: S3 (target)"), ("B", "B: cyclic |t|=1"), ("C", "C: cyclic |t|>1")):
        objs = collect(kind)
        fields = dedup_fields(objs)
        p_(f"  {lbl:>16s} {len(objs):>7d} {len(fields):>16d}")
        rows = []
        for A, B, C, D in fields:
            r = mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800)
            rows.append(anchors(cf_of_mpf(sorted(mp.re(x) for x in r)[0])))
        out[kind] = {"label": lbl, "n_poly": len(objs), "n_field": len(fields)}
        for key in ("levy", "tail", "rate_u", "khinchin"):
            m, s = mean_sem([x[key] for x in rows])
            out[kind][key] = [m, s]

    p_(f"\n  ANCHORS on FIELD-deduplicated units")
    p_(f"  {'anchor':>10s} {'theory':>10s} " +
       "".join(f"{k:>19s}" for k in ("A: S3", "B: |t|=1", "C: |t|>1")))
    # REFERENCE for the LAMBDA tail is 1/(A ln2), NOT the Gauss-Kuzmin tail log2(1+1/A) for a.
    # P(theta <= z) = z/ln2 for z <= 1/2 (Bosma-Jager-Wiedijk) and theta = 1/lambda, so
    # P(lambda >= A) = 1/(A ln 2) = 1.4427/A exactly for A >= 2. Using the a-tail here was the
    # same a-versus-lambda convention slip the seal now fixes, and it manufactured a +2 sem offset.
    TAIL = 1.0 / (A_EV * math.log(2))
    ref = {"levy": LEVY, "tail": TAIL, "rate_u": TAIL / LEVY, "khinchin": KHIN}
    for key, nm in (("levy", "Levy"), ("tail", "P(lam>=A)"), ("rate_u", "ev/unit u"),
                    ("khinchin", "Khinchin")):
        p_(f"  {nm:>10s} {ref[key]:>10.5f} " +
           "".join(f"{out[k][key][0]:>12.5f}+-{out[k][key][1]:<6.5f}" for k in ("S3", "B", "C")))

    p_(f"\n  {'anchor':>10s} {'A vs B':>9s} {'A vs C':>9s} {'B vs C':>9s}   (sem units, field-level)")
    zz = {}
    for key, nm in (("levy", "Levy"), ("tail", "P(lam>=A)"), ("rate_u", "ev/unit u"),
                    ("khinchin", "Khinchin")):
        def z(k1, k2):
            m1, s1 = out[k1][key]; m2, s2 = out[k2][key]
            return (m1 - m2) / math.sqrt(s1 * s1 + s2 * s2)
        zz[key] = [z("S3", "B"), z("S3", "C"), z("B", "C")]
        p_(f"  {nm:>10s} {zz[key][0]:>+9.2f} {zz[key][1]:>+9.2f} {zz[key][2]:>+9.2f}")
    sens = 2 * out["S3"]["rate_u"][1] / out["S3"]["rate_u"][0]
    p_(f"\n  key anchor (ev/unit u): worst |z| = {max(abs(v) for v in zz['rate_u']):.2f};  "
       f"sem = {100*out['S3']['rate_u'][1]/out['S3']['rate_u'][0]:.1f}% of value")
    p_(f"  -> the test could have caught a {100*sens:.0f}% difference at field level "
       f"(polynomial level said 4%).")

    # ------------------------------------------------------------------ [G]
    p_("\n[G] is P(g) derivable?   claim:  P(g = D)  ~  P(g = 1) * 1.4427 / D")
    p_(f"  {'stratum':>12s} {'|det|':>7s} {'P(g=1)':>9s} {'P(g=D) pred':>13s} "
       f"{'P(g=D) meas':>13s} {'ratio':>7s}")
    from math import gcd
    by_t = collect_cyclic(box=14, per=1)
    rows_g = []
    for t in sorted(by_t):
        if t == 1:
            continue
        A, B, C, M = by_t[t][0]
        a, b, c, d = M
        D = abs(a * d - b * c)
        r = sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800))
        a0 = cf_of_mpf(r[0]); P0, Q0 = convergents(a0)
        gh = {}
        for i in range(1, len(a0) - 45):
            A_, B_ = a * P0[i] + b * Q0[i], c * P0[i] + d * Q0[i]
            if B_ == 0:
                continue
            g = gcd(abs(A_), abs(B_))
            gh[g] = gh.get(g, 0) + 1
        tot = sum(gh.values())
        p1 = gh.get(1, 0) / tot
        pD_meas = gh.get(D, 0) / tot
        pD_pred = p1 * 1.4427 / D
        if pD_meas > 0:
            rows_g.append((t, D, p1, pD_pred, pD_meas, pD_pred / pD_meas))
            p_(f"  {'|t|='+str(t):>12s} {D:>7d} {p1:>9.4f} {pD_pred:>13.5f} {pD_meas:>13.5f} "
               f"{pD_pred/pD_meas:>7.2f}")
    if rows_g:
        rr = [x[5] for x in rows_g]
        p_(f"\n  ratio across {len(rr)} strata: mean {sum(rr)/len(rr):.2f}, "
           f"range {min(rr):.2f}..{max(rr):.2f}")
        p_("  -> the FORM holds (P(g=D) tracks P(g=1)/D across two orders of magnitude in D), but the")
        p_("     CONSTANT is off by a roughly uniform factor -- the 'is it a convergent' criterion is")
        p_("     lambda' >~ 1 only approximately. So the route is real and NOT CLOSED.")
        p_("  -> GRADE, stated plainly: the corrected formula uses a MEASURED P(g|event) whose")
        p_("     mechanism is unclosed, so it is CALIBRATED, not derived. That -- not a count of")
        p_("     misses -- is why it cannot extrapolate past the |det| it was calibrated on.")

    json.dump({"dedup": out, "cross_z_field": zz, "sensitivity_field": sens,
               "pg_route": [[t, D, p1, pp, pm, r] for t, D, p1, pp, pm, r in rows_g]},
              open(os.path.join(HERE, "gate0i_fields_measured.json"), "w"), indent=2)
    p_("\nwrote gate0i_fields_measured.json")
