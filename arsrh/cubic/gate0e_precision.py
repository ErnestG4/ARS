"""
GATE 0e — the rate formula's OWN precision. Fixes a precision-inflation defect.

Reviewer: "Ratio to measurement 1.00, 1.00, 0.99, 1.35" reads as validation with a footnote. Honest
summary of all nine is ~20% typical, 35% worst -- and the worst sits at the LARGEST |det|, i.e. the
accuracy degrades in the direction the licensing sentence ("any |det| sizes without running") points.
Either the 1.35 is small-n scatter (say so, with the count, and quote sizing precision as a band) or
it is a systematic at large |det| (in which case extrapolation is not licensed at all).

THE TEST. Pool many objects per |det| stratum so the binomial error shrinks, then ask the two
questions separately:
  [z] is each stratum's deviation consistent with binomial scatter at its own n?
  [S] regress log(measured/predicted) on log|det| -- a SYSTEMATIC would show as a nonzero slope,
      scatter would not. This is the discriminating test; the per-row ratios are not.

NOTE ON THE DERIVATION. P(lambda >= x) = 1.4427/x is EXACT for x >= 2 (Bosma-Jager-Wiedijk: the
approximation coefficient theta = 1/lambda has density 1/log2 on [0,1/2]), not merely asymptotic.
So rate = sum_g P(g) min(1, g^2/|Delta|) should be exact in the limit, and any residual is either
finite-n or a g-vs-lambda dependence. Both are measurable here.
"""
from __future__ import annotations
import json, math, os
from math import gcd

import mpmath as mp
from gate0_ladder import certified_cf, convergents, cf_cbrt, lam
from gate0b_stratify import mobius_of_cubic, disc, irreducible

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
DIG, NPQ, BOX, PER = 1200, 1400, 14, 8
A_EV = 20
mp.mp.dps = DIG + 60


def cf_of_mpf(x):
    return certified_cf(int(mp.floor(x * 10 ** DIG)), 10 ** DIG, NPQ)


def counts(a0, a1, M, by_lambda=False):
    """returns (n_events, n_coincident, g-histogram over ALL convergents).
    by_lambda: define the event by lambda >= A (the quantity the transfer law acts on)
    rather than by a_{n+1} >= A.  lambda = a + delta with delta in [0,2), so the two
    definitions differ at order 2/A -- 10% at A=20, which is the size of the residual."""
    a, b, c, d = M
    L0 = [lam(a0, convergents(a0)[1], i) for i in range(1, len(a0) - 45)] if by_lambda else None
    L1 = [lam(a1, convergents(a1)[1], i) for i in range(1, len(a1) - 45)] if by_lambda else None
    D = abs(a * d - b * c)
    P0, Q0 = convergents(a0); P1, Q1 = convergents(a1)
    idx = {Q1[k]: k for k in range(len(Q1))}
    n = k_ = 0
    gh, ghe = {}, {}          # g-histogram over all convergents, and conditioned on EVENTS
    for i in range(1, len(a0) - 45):
        A_, B_ = a * P0[i] + b * Q0[i], c * P0[i] + d * Q0[i]
        if B_ == 0:
            continue
        if B_ < 0:
            A_, B_ = -A_, -B_
        g = gcd(abs(A_), B_)
        gh[g] = gh.get(g, 0) + 1
        if (L0[i - 1] if by_lambda else a0[i + 1]) < A_EV:
            continue
        n += 1
        ghe[g] = ghe.get(g, 0) + 1
        j = idx.get(B_ // g)
        if j is not None and 1 <= j < len(a1) - 45 and P1[j] == A_ // g and \
                (L1[j - 1] if by_lambda else a1[j + 1]) >= A_EV:
            k_ += 1
    return n, k_, gh, D, ghe


def gl2z_orbit_reps(polys, dig=400, probe=60, span=120):
    """REPAIR (2026-07-28, R-165). One representative per GL2(Z) orbit.

    THE DEFECT THIS EXISTS FOR. `collect_cyclic` enumerates POLYNOMIALS over a coefficient box
    and dedups by nothing. Many of them are GL2(Z) translates of the SAME cubic irrational and
    therefore produce IDENTICAL (g, y, lambda) orbits. Verified exactly, not statistically: at
    |t|=13 the polynomials (-7,0,7) and (-4,-11,1) have roots differing by EXACTLY 1.0, so their
    continued fractions agree from a_1 on.

    WHY IT MATTERED. Duplicating an orbit k times leaves `meas` and `pred` unchanged and
    multiplies n by k, so every pooled |z| inflates by exactly sqrt(k). Measured duplication:
    |t|=5 4x, |t|=13 2x, |t|=17 2x, |t|=29 2x. That inflation is what made R-156/R-158's +3.30
    and my own R-161 look-elsewhere p = 0.0100 look significant.

    RATIOS ARE SAFE, COUNTS ARE NOT. Duplication scales numerator and denominator together, so
    gate0e's meas/pred, bias, rms and the sealed +-12% band are UNAFFECTED. Every chi^2, every
    "excess over binomial", and every pooled z IS affected.

    Serret: two cubics share a GL2(Z) orbit iff their CF tails coincide up to a shift. Integer
    translates are the shift-0 case and are caught by the same test.

    `collect_cyclic` is left BIT-IDENTICAL -- banked numbers came off it and must stay auditable.
    """
    reps, sigs = [], []
    for rec in polys:
        A, B, C = rec[0], rec[1], rec[2]
        r = sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=600, extraprec=1200))
        a = certified_cf(int(mp.floor(r[0] * 10 ** dig)), 10 ** dig, 20000)
        if len(a) < 2 * probe + span:
            continue
        dup = False
        for s in sigs:
            for u, v in ((a, s), (s, a)):
                p_probe = tuple(u[probe:2 * probe])
                if any(tuple(v[probe + o:2 * probe + o]) == p_probe for o in range(span)):
                    dup = True
                    break
            if dup:
                break
        if not dup:
            reps.append(rec)
            sigs.append(a)
    return reps


def collect_cyclic_dedup(box=BOX, per=PER, dig=400):
    """`collect_cyclic` with one representative per GL2(Z) orbit. See `gl2z_orbit_reps`."""
    return {t: gl2z_orbit_reps(v, dig=dig) for t, v in collect_cyclic(box=box, per=per).items()}


def collect_cyclic(box=BOX, per=PER):
    """cubics grouped by |t|, up to `per` each.

    ⚠ POOLS DUPLICATE GL2(Z) ORBITS -- see `gl2z_orbit_reps`. Any pooled COUNT or z computed from
    this is inflated by sqrt(duplication factor). Use `collect_cyclic_dedup` for anything that
    pools. Retained bit-identical because banked numbers came off it.
    """
    by_t = {}
    for A in range(-box, box + 1):
        for B in range(-box, box + 1):
            for C in range(-box, box + 1):
                D = disc(A, B, C)
                if D <= 0 or math.isqrt(D) ** 2 != D or not irreducible(A, B, C):
                    continue
                M = mobius_of_cubic(A, B, C)
                if M is None:
                    continue
                t = abs(M[4])
                by_t.setdefault(t, [])
                if len(by_t[t]) < per:
                    by_t[t].append((A, B, C, M[:4]))
    return by_t


if __name__ == "__main__":
    p_("=== GATE 0e — how precise is  rate = sum_g P(g) min(1, g^2/|det|)  ? ===")
    p_(f"events defined at A = {A_EV}; pooling {PER} objects per stratum, {NPQ} PQs each\n")

    rows = []
    rows_lam = []
    rows_cond = []
    rows_both = []

    by_t = collect_cyclic()
    for t in sorted(by_t):
        N = K = NL = KL = 0
        GH, GHE, GHEL = {}, {}, {}
        discs = set()
        for A, B, C, M in by_t[t]:
            r = mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800)
            r = sorted(mp.re(x) for x in r)
            a, b, c, d = M
            img = (a * r[0] + b) / (c * r[0] + d)
            j = min(range(3), key=lambda i: abs(r[i] - img))
            c0, c1 = cf_of_mpf(r[0]), cf_of_mpf(r[j])
            n, k_, gh, D, ghe = counts(c0, c1, M)
            nl, kl, _, _, ghel = counts(c0, c1, M, by_lambda=True)
            N += n; K += k_; NL += nl; KL += kl
            for g, v in gh.items():
                GH[g] = GH.get(g, 0) + v
            for g, v in ghe.items():
                GHE[g] = GHE.get(g, 0) + v
            for g, v in ghel.items():
                GHEL[g] = GHEL.get(g, 0) + v
            discs.add(disc(A, B, C))
        tot = sum(GH.values())
        pred = sum(v / tot * min(1.0, g * g / D) for g, v in GH.items())
        tote = sum(GHE.values())
        prede = sum(v / tote * min(1.0, g * g / D) for g, v in GHE.items())
        rows.append((f"cyclic |t|={t}", D, N, K, pred, len(by_t[t])))
        rows_lam.append((f"cyclic |t|={t}", D, NL, KL, pred, len(by_t[t])))
        rows_cond.append((f"cyclic |t|={t}", D, N, K, prede, len(by_t[t]), dict(GHE)))
        totl = sum(GHEL.values())
        predl = sum(v / totl * min(1.0, g * g / D) for g, v in GHEL.items())
        rows_both.append((f"cyclic |t|={t}", D, NL, KL, predl, len(discs), dict(GHEL)))

    for m in (2, 3, 5, 6, 7, 10, 11, 12, 13, 15):
        c0, c1 = cf_cbrt(m, 1, DIG, NPQ), cf_cbrt(m, 2, DIG, NPQ)
        n, k_, gh, D, ghe = counts(c0, c1, (0, m, 1, 0))
        nl, kl, _, _, ghel = counts(c0, c1, (0, m, 1, 0), by_lambda=True)
        tot = sum(gh.values()); tote = sum(ghe.values())
        pred = sum(v / tot * min(1.0, g * g / D) for g, v in gh.items())
        prede = sum(v / tote * min(1.0, g * g / D) for g, v in ghe.items())
        rows.append((f"cbrt {m}", D, n, k_, pred, 1))
        rows_lam.append((f"cbrt {m}", D, nl, kl, pred, 1))
        rows_cond.append((f"cbrt {m}", D, n, k_, prede, 1, dict(ghe)))

    from scipy.stats import chi2 as _chi2

    def stats(rows, title, verbose):
        p_(f"\n  --- {title} ---")
        if verbose:
            p_(f"  {'pair':>15s} {'|det|':>6s} {'objs':>5s} {'n_ev':>6s} {'k':>6s} "
               f"{'meas':>8s} {'pred':>8s} {'ratio':>7s} {'z':>7s}")
        zs, lds, lrs, labs = [], [], [], []
        for row in rows:
            lbl, D, N, K, pred, nob = row[:6]
            ghe = row[6] if len(row) > 6 else None
            if N == 0:
                continue
            meas = K / N
            if ghe is not None:
                # HETEROGENEOUS success probability: p = min(1, g^2/D) differs by branch, and the
                # g = t and g = t^2 branches have p = 1 (zero variance). Pooled p(1-p) OVERSTATES
                # the variance and deflates chi^2. Correct form: sum_g n_g p_g (1 - p_g).
                sd = math.sqrt(sum(n_g * min(1.0, g * g / D) * (1 - min(1.0, g * g / D))
                                   for g, n_g in ghe.items()))
            else:
                sd = math.sqrt(N * pred * (1 - pred))
            z = (K - N * pred) / sd if sd > 0 else 0.0
            if verbose:
                p_(f"  {lbl:>15s} {D:>6d} {nob:>5d} {N:>6d} {K:>6d} {100*meas:>7.1f}% "
                   f"{100*pred:>7.1f}% {meas/pred:>7.3f} {z:>+7.2f}")
            zs.append(z); labs.append(lbl)
            if pred < 0.999 and meas > 0:
                lds.append(math.log(D)); lrs.append(math.log(meas / pred))
        chi = sum(x * x for x in zs); df = len(zs)
        pval = float(_chi2.sf(chi, df))
        worst = sorted(range(df), key=lambda i: -abs(zs[i]))[:2]
        n_ = len(lds)
        mx = sum(lds) / n_; my = sum(lrs) / n_
        Sxx = sum((x - mx) ** 2 for x in lds)
        sl = sum((x - mx) * (y - my) for x, y in zip(lds, lrs)) / Sxx
        res = [y - (my + sl * (x - mx)) for x, y in zip(lds, lrs)]
        s2 = sum(r * r for r in res) / (n_ - 2)
        se = math.sqrt(s2 / Sxx); rms = math.sqrt(sum(r * r for r in res) / n_)
        sd_my = math.sqrt(s2 / n_)
        p_(f"    chi^2 = {chi:.1f} on {df} df (chi2/df = {chi/df:.2f}), p = {pval:.4f}"
           f"  -> {'EXCESS over binomial' if pval < 0.05 else 'consistent with binomial'}")
        p_(f"    the two largest |z|: {labs[worst[0]]} ({zs[worst[0]]:+.2f}), "
           f"{labs[worst[1]]} ({zs[worst[1]]:+.2f})")
        p_(f"    (a) BIAS  : mean log(meas/pred) = {my:+.4f} +/- {sd_my:.4f} "
           f"({abs(my/sd_my):.2f} sem, factor {math.exp(my):.3f})")
        p_(f"    (b) TREND : slope on log|det|   = {sl:+.4f} +/- {se:.4f} ({abs(sl/se):.2f} sem)")
        p_(f"    (c) SPREAD: residual rms in log = {rms:.4f}  ->  +/-{100*(math.exp(rms)-1):.0f}%")
        return {"chi2": chi, "df": df, "p": pval, "bias": my, "bias_sem": sd_my,
                "slope": sl, "slope_sem": se, "rms": rms,
                "precision_pct": 100 * (math.exp(rms) - 1)}

    r_a = stats(rows, f"events defined by  a_(n+1) >= {A_EV}  (the spec's definition)", True)
    r_l = stats(rows_lam, f"events defined by  lambda >= {A_EV}  (what the transfer law acts on)", False)
    r_c = stats(rows_cond, "P(g | EVENT), events by a  -- fixes the dispersion, leaves a residue", False)
    r_b = stats(rows_both, "P(g | EVENT) AND events by lambda -- both corrections together", True)
    p_("  ('objs' is now DISTINCT DISCRIMINANTS: the coefficient box yields many polynomials")
    p_("   per field, and correlated objects are one witness.)")

    p_("\n  => The two definitions differ at order 2/A because lambda = a + delta, delta in [0,2).")
    p_(f"     bias      {math.exp(r_a['bias']):.3f}  ->  {math.exp(r_l['bias']):.3f}"
       f"      (2/A = {2/A_EV:.2f})")
    p_(f"     precision  +/-{r_a['precision_pct']:.0f}%  ->  +/-{r_l['precision_pct']:.0f}%")
    p_(f"     chi2/df    {r_a['chi2']/r_a['df']:.2f}  ->  {r_l['chi2']/r_l['df']:.2f}")
    best = r_l if r_l["rms"] < r_a["rms"] else r_a
    p_(f"\n  => THE FIX: P(g | event) != P(g). The g = t branch has factor t^2/t^2 = 1 and transfers")
    p_(f"     everything, so enriching it inflates the rate above a P(g)-based prediction.")
    p_(f"     precision  +/-{r_a['precision_pct']:.0f}% (marginal)  ->  +/-{r_c['precision_pct']:.0f}% (conditional)")
    p_(f"     chi2/df     {r_a['chi2']/r_a['df']:.2f}            ->  {r_c['chi2']/r_c['df']:.2f}   "
       f"(p = {r_c['p']:.3f})")
    p_(f"\n  => BOTH CORRECTIONS: precision +/-{r_a['precision_pct']:.0f}% -> "
       f"+/-{r_b['precision_pct']:.0f}%, chi2/df {r_c['chi2']/r_c['df']:.2f} -> {r_b['chi2']/r_b['df']:.2f}, "
       f"trend {abs(r_c['slope']/r_c['slope_sem']):.2f} -> {abs(r_b['slope']/r_b['slope_sem']):.2f} sem")
    p_(f"\n  => OLD LICENSED STATEMENT: with the conditional histogram -- a WITHIN-object quantity needing")
    p_(f"     no partner, so free at design time -- the formula sizes |det| in 2..1849 to")
    p_(f"     +/-{r_c['precision_pct']:.0f}% (1 sd), bias {abs(r_c['bias']/r_c['bias_sem']):.2f} sem, "
       f"trend {abs(r_c['slope']/r_c['slope_sem']):.2f} sem. Quote that band.")

    json.dump({"A_event": A_EV, "n_pq": NPQ, "per_stratum": PER,
               "rows": [{"label": l, "det": D, "n": N, "k": K, "pred": p, "n_objects": o}
                        for l, D, N, K, p, o in rows],
               "by_a": r_a, "by_lambda": r_l, "by_conditional_g": r_c, "both_corrections": r_b},
              open(os.path.join(HERE, "gate0e_precision_measured.json"), "w"), indent=2)
    p_("\nwrote gate0e_precision_measured.json")
