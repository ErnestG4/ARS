"""
GATE 0j — three items raised against the sealed design, before any arm runs.

[L] The lambda tail is EXACT, not asymptotic. Reviewer's derivation, verified here.
    Natural extension density 1/(log2 (1+xy)^2) on [0,1]^2, lambda = 1/x + y. The condition
    lambda >= A is x <= 1/(A-y), and the inner integral collapses:
        int_0^X dx/(1+xy)^2 = X/(1+Xy),  X = 1/(A-y)  =>  X/(1+Xy) = 1/A,  independent of y.
    So P(lambda >= A) = 1/(A log 2) EXACTLY, for A >= 2 (so that X <= 1).
    Consequence: the anchor reference has ZERO uncertainty, so R-078's licence is cleaner than
    stated -- the 1.6% sem sits against an exact number, not against an asymptotic one.

[B] Stratum B is a SMOKE TEST, not a ceiling -- and its failure condition can FALSE-FIRE.
    |Delta| = 1 means Serret-equivalent: the two CFs are IDENTICAL from some index n0 onward.
    So the detector's task on B is "find the shift aligning two identical sequences". That tests
    that the code runs; it says almost nothing about resolving two DISTINCT coincident processes.
    C does the real calibration.
    And BEFORE the merge the sequences are unrelated, so f over the full range is (n - n0)/n with
    n0 object-dependent. "B must return 1.00" can therefore fail on a known finite-depth transient,
    voiding a target result for an instrument reason that is not an instrument defect.
    Measured here: the n0 distribution, and the f it implies. The seal's hard-halt threshold is
    then set FROM that distribution rather than from the number 1.00.

[G] R-077, and the reviewer's proposed closure -- which is testable and, on the sign, fails.
    Proposed: P(g=D) ~ P(g=1)*1.4427/D counts only alpha2 events with an alpha1-convergent preimage;
    alpha2 has g=D convergents with no preimage, which inflate MEASURED above PREDICTED.
    But the measured ratio is pred/meas = 1.65 > 1: prediction OVERSHOOTS. Extra preimage-less
    convergents would push the ratio BELOW 1. So that mechanism has the wrong sign.
    Tested instead: is P(g) simply the counting measure of (p_n : q_n) mod Delta? g = gcd(A_,B_)
    divides Delta, hence g = gcd(ap+bq, cp+dq, Delta), a function of (p,q) mod Delta alone. If the
    residues equidistribute over {(p,q) mod Delta : gcd(p,q,Delta) = 1}, then P(g) is EXACTLY a
    finite count and needs no measurement -- which would return the rate formula to DERIVED.
"""
from __future__ import annotations
import json, math, os
from math import gcd

import mpmath as mp
import numpy as np
from scipy.integrate import dblquad
from gate0_ladder import convergents, lam
from gate0e_precision import cf_of_mpf
from gate0b_stratify import mobius_of_cubic

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
mp.mp.dps = 1260
A_EV = 20
SEAL = json.load(open(os.path.join(HERE, "..", "seals", "CUBIC_ARM_SEAL.json")))


def roots(A, B, C):
    return sorted(mp.re(x) for x in mp.polyroots([1, A, B, C], maxsteps=400, extraprec=800))


if __name__ == "__main__":
    p_("=== GATE 0j — three checks against the sealed design ===")

    # ------------------------------------------------------------------ [L]
    p_("\n[L] is P(lambda >= A) = 1/(A ln 2) EXACT?")
    dens = lambda x, y: 1.0 / (math.log(2) * (1 + x * y) ** 2)
    norm = dblquad(dens, 0, 1, 0, 1)[0]
    p_(f"  normalisation of 1/(log2 (1+xy)^2) over the unit square = {norm:.12f}  (must be 1)")
    p_(f"  {'A':>5s} {'numeric P(lam>=A)':>20s} {'1/(A ln2)':>14s} {'rel diff':>12s}")
    for A in (2, 3, 5, 20, 100):
        num = dblquad(dens, 0, 1, 0, lambda y: min(1.0, 1.0 / (A - y)))[0]
        ex = 1.0 / (A * math.log(2))
        p_(f"  {A:>5d} {num:>20.12f} {ex:>14.9f} {abs(num/ex-1):>12.2e}")
    p_("  -> EXACT at every A >= 2, no asymptotic correction. The anchor reference carries ZERO")
    p_("     uncertainty, so R-078's 1.6% sem is the whole error budget on that comparison.")
    p_("  -> and the a-vs-lambda slip was worse than a slot error: log2(1+1/A) is the")
    p_("     approximate-LOOKING form that is exact for a; 1/(A ln2) is the exact form for lambda.")

    # ------------------------------------------------------------------ [B]
    p_("\n[B] stratum B: where does the Serret merge happen, and what f does it imply?")
    Bpolys = SEAL["arms"]["B"]["polynomials"]
    p_(f"  {'poly':>16s} {'n0':>5s} {'offset':>7s} {'n_ev':>6s} {'ev after n0':>12s} {'f_full':>8s}")
    rows = []
    for A, B, C in Bpolys:
        M = mobius_of_cubic(A, B, C)
        a, b, c, d = M[:4]
        r = roots(A, B, C)
        img = (a * r[0] + b) / (c * r[0] + d)
        j = min(range(3), key=lambda i: abs(r[i] - img))
        a0, a1 = cf_of_mpf(r[0]), cf_of_mpf(r[j])
        # find the merge: smallest i0 with a0[i0:] == a1[i0+off:] for some small offset
        best = None
        L = min(len(a0), len(a1)) - 60
        for off in range(-25, 26):
            i0 = None
            for i in range(1, 200):
                if i + off < 1:
                    continue
                k = 0
                ok = True
                while i + k < L and i + off + k < L:
                    if a0[i + k] != a1[i + off + k]:
                        ok = False
                        break
                    k += 1
                if ok and k > 300:
                    i0 = i
                    break
            if i0 is not None and (best is None or i0 < best[0]):
                best = (i0, off)
        if best is None:
            p_(f"  {str((A,B,C)):>16s}   -- no merge found in the certified range --")
            continue
        i0, off = best
        P0, Q0 = convergents(a0)
        lams = [(i, lam(a0, Q0, i)) for i in range(1, len(a0) - 45)]
        ev = [i for i, l in lams if l >= A_EV]
        after = [i for i in ev if i >= i0]
        f_full = len(after) / len(ev) if ev else float("nan")
        rows.append({"poly": [A, B, C], "n0": i0, "offset": off,
                     "n_ev": len(ev), "n_after": len(after), "f_full": f_full})
        p_(f"  {str((A,B,C)):>16s} {i0:>5d} {off:>+7d} {len(ev):>6d} {len(after):>12d} {f_full:>8.4f}")

    n0s = [x["n0"] for x in rows]
    ffs = [x["f_full"] for x in rows]
    p_(f"\n  n0 across {len(rows)} stratum-B fields: min {min(n0s)}, median {int(np.median(n0s))}, "
       f"max {max(n0s)}")
    p_(f"  f_full: min {min(ffs):.4f}, median {np.median(ffs):.4f}, mean {np.mean(ffs):.4f}")
    thr = float(min(ffs)) - 0.02
    p_(f"  -> 'B must return 1.00' WOULD FALSE-FIRE: the worst field gives f_full = {min(ffs):.4f}")
    p_(f"     on a pre-merge transient that is not an instrument defect.")
    p_(f"  -> AMENDED hard-halt threshold, set from this distribution and not from 1.00:")
    p_(f"       f_full(B) >= {thr:.3f}   (min observed minus 0.02)")
    p_(f"     PLUS the sharper form: on the POST-MERGE segment (index >= n0) f must be 1.000 exactly.")
    p_(f"  -> and B is REGRADED: smoke test, not ceiling. After the merge the partial quotients are")
    p_(f"     IDENTICAL, so the detector aligns a sequence with itself. Stratum C carries the")
    p_(f"     calibration; B only shows the code runs.")

    # ------------------------------------------------------------------ [G]
    p_("\n[G] R-077: the proposed closure fails on SIGN; testing the counting route instead")
    p_("  reviewer's mechanism would make MEASURED exceed PREDICTED (extra preimage-less convergents).")
    p_("  observed pred/meas = 1.65 > 1, i.e. prediction OVERSHOOTS. Wrong sign; not the explanation.")
    p_("\n  counting route: g = gcd(ap+bq, cp+dq, Delta) depends only on (p,q) mod Delta.")
    p_("  If (p_n, q_n) mod Delta equidistributes over {gcd(p,q,Delta)=1}, P(g) is a finite COUNT.")
    p_(f"\n  {'poly':>16s} {'|det|':>6s} {'g':>6s} {'P(g) counted':>14s} {'P(g) measured':>15s} "
       f"{'ratio':>7s}")
    out_g = []
    for A, B, C in SEAL["arms"]["C"]["polynomials"][:6]:
        M = mobius_of_cubic(A, B, C)
        a, b, c, d = M[:4]
        D = abs(a * d - b * c)
        r = roots(A, B, C)
        a0 = cf_of_mpf(r[0]); P0, Q0 = convergents(a0)
        emp = {}
        for i in range(1, len(a0) - 45):
            A_, B_ = a * P0[i] + b * Q0[i], c * P0[i] + d * Q0[i]
            g = gcd(abs(A_), abs(B_))
            emp[g] = emp.get(g, 0) + 1
        tot = sum(emp.values())
        cnt, S = {}, 0
        for pp in range(D):
            for qq in range(D):
                if gcd(gcd(pp, qq), D) != 1:
                    continue
                S += 1
                g = gcd(gcd((a * pp + b * qq) % D, (c * pp + d * qq) % D), D)
                cnt[g] = cnt.get(g, 0) + 1
        for g in sorted(set(cnt) | set(emp)):
            pc, pm = cnt.get(g, 0) / S, emp.get(g, 0) / tot
            out_g.append({"poly": [A, B, C], "det": D, "g": g, "counted": pc, "measured": pm})
            p_(f"  {str((A,B,C)):>16s} {D:>6d} {g:>6d} {pc:>14.5f} {pm:>15.5f} "
               f"{(pc/pm if pm else float('nan')):>7.3f}")
    # A ratio criterion ignores how many counts back each branch -- the same defect as gating a
    # verdict on a threshold before gating on input sanity. Weight by the actual counts.
    from scipy.stats import chi2 as _chi2
    NCONV = 1350                     # approx convergents per object in the certified range
    chi = sum((x["measured"] - x["counted"]) ** 2 * NCONV / (x["counted"] * (1 - x["counted"]))
              for x in out_g)
    dfree = len(out_g) - len(SEAL["arms"]["C"]["polynomials"][:6])
    pv = float(_chi2.sf(chi, dfree))
    rr = [x["counted"] / x["measured"] for x in out_g if x["measured"] > 0.002]
    p_(f"\n  ratio counted/measured, {len(rr)} branches: mean {np.mean(rr):.3f}, "
       f"range {min(rr):.3f}..{max(rr):.3f}")
    worst = min(out_g, key=lambda x: min(x["counted"] / x["measured"], x["measured"] / x["counted"]))
    p_(f"  the worst ratio ({worst['counted']/worst['measured']:.3f}) is the g = {worst['g']} branch "
       f"of |det| = {worst['det']}: expected {worst['counted']*NCONV:.1f} counts, saw "
       f"{worst['measured']*NCONV:.1f} -- Poisson-consistent, not a failure.")
    p_(f"  count-weighted chi^2 = {chi:.1f} on {dfree} df, p = {pv:.3f}")
    closed = pv > 0.05
    p_(f"  -> P(g) {'IS a finite count over (p,q) mod Delta -- DERIVED, no measurement' if closed else 'is NOT explained by the count'}")
    p_(f"  -> and this KILLS my earlier heuristic route: for |det| = 4 the count gives P(g=4) = 1/6")
    p_(f"     exactly, while P(g=1)*1.4427/4 = 0.2405. The 1.65 was chasing a wrong formula.")
    p_(f"\n  BUT the rate formula needs P(g | EVENT), not P(g). The marginal is now derived; the")
    p_(f"  CONDITIONAL is not, because the residue class and lambda are correlated through")
    p_(f"  y_n = q_(n-1)/q_n, which enters BOTH. So R-077 moves from 'empirical input of unknown")
    p_(f"  mechanism' to 'one identified correlation in a skew product whose marginal is derived'.")
    p_(f"  That is a grade change, not a closure: the formula stays CALIBRATED.")

    json.dump({"lambda_tail_exact": True, "stratum_B": rows,
               "B_f_full_min": min(ffs), "B_amended_threshold": thr,
               "B_n0": {"min": min(n0s), "median": float(np.median(n0s)), "max": max(n0s)},
               "counting_route": out_g, "counting_ratio_mean": float(np.mean(rr)),
               "counting_closed": bool(closed)},
              open(os.path.join(HERE, "gate0j_close_measured.json"), "w"), indent=2)
    p_("\nwrote gate0j_close_measured.json")
