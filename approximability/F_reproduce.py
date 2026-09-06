"""INDEPENDENT REPLICATION of Session F's genus>0 calibrator claims.

COMMITTED GENERATOR of approximability/F_reproduce.json.
Predictions sealed here, before any output exists.

WHY THIS EXISTS, AND WHAT IT IS NOT
-----------------------------------
Session F banked four numbers in F_results.json:

    smooth_battery      "77/77 Weil+RH pass"
    genus1_rate_ratio   0.9747993542043758
    genus2_rate_ratio   0.9583126741064829
    rh_rate             "0.5*log10(q) genus-independent exponent"

and its commit contains no driver. `ff_curve.py` is a pure module -- eight
functions, no __main__, no prints -- so the code that produced those four
numbers is on no branch. That is the committed-generator rule failing.

THIS IS NOT A RECOVERY OF THAT RUN. MORNING_F states the protocol (77 smooth
curve x base-field x genus cases, p up to 29, four genus-1 and four genus-2
families, singular curves filtered by a squarefree check) but does NOT state
which families. Reconstructing an enumeration until it returns 77 would be
tuning to a target, and a reconstruction is a hypothesis about what was run, not
the run. So this cell declares its OWN enumeration, in advance, and reports what
that enumeration gives.

WHICH MAKES IT A STRONGER TEST THAN A RECONSTRUCTION WOULD BE. Session F's
load-bearing claim is METHOD-INVARIANCE: Hasse-Weil and RH-for-curves are
PROVABLE gates, so they must pass on every smooth curve, not merely on the 77
that were tried. An independent family that also passes 100% corroborates the
claim; one that fails refutes it and the count 77 becomes irrelevant. Likewise
the rate exponent is asserted to be genus-INDEPENDENT, which is a claim about
all curves rather than about a sample.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                           ║
║                                                                              ║
║ P1  PREMISE — the enumeration is non-trivial and actually reaches smooth     ║
║     curves in both genera: at least 20 smooth cases per genus survive the    ║
║     singularity filter. A battery that filtered everything out would pass    ║
║     the gates vacuously.                                                     ║
║                                                                              ║
║ E1  METHOD-INVARIANCE REPLICATES — Hasse-Weil passes on 100% of smooth       ║
║     cases. These are provable bounds; a single failure is a bug in the       ║
║     point-counter, which is exactly how Session F found its own Newton-      ║
║     identity error (Hasse-Weil is loose, so it passed some buggy curves and  ║
║     failed others at p=11).                                                  ║
║                                                                              ║
║ E2  AND RH-FOR-CURVES PASSES on 100% of smooth cases, same reasoning. Both   ║
║     arms are needed: RH held while N_v was wrong in Session F's bug, so RH   ║
║     alone would have missed it, and Hasse-Weil alone is too loose.           ║
║                                                                              ║
║ E3  THE RATE RATIO REPLICATES — the measured decay exponent of              ║
║     |N_n/p^n - 1| against 0.5*log10(p), averaged over smooth curves, lands   ║
║     within 0.05 of Session F's banked value in BOTH genera (0.9748, 0.9583). ║
║     This is the arm that can embarrass the banked numbers, and it is scored  ║
║     against them as recorded, with no tuning.                                ║
║                                                                              ║
║ M1  MECHANISM — genus-independence. The two genus-wise mean ratios differ    ║
║     by less than 0.05, which is what "the exponent is genus-independent,     ║
║     genus enters only the 2g prefactor" predicts.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

MY DECLARED ENUMERATION, fixed before running: genus-1 curves y^2 = x^3 + ax + b
over a = 1..3, b = 1..3; genus-2 curves y^2 = x^5 + c3 x^3 + c1 x + c0 over
c3, c1, c0 in {0,1,2}; primes p in {7, 11, 13, 17, 19, 23, 29}. Singular cases
are dropped by the module's own asserts, and the count that survives is reported
rather than aimed at. p >= 7 because the genus-2 discriminant machinery and the
Legendre symbol both degrade at very small p, and 29 is Session F's stated top.

AMENDMENT 1 — MY SCOPE SAID "SMOOTH" AND MY CODE DID NOT ENFORCE IT, AND THE
REASON IS A GAP IN THE BANKED MODULE.

The first run reported 2 failures out of 246 on gates that are THEOREMS. Both
were the same curve, y^2 = x^5 + x^3 = x^3(x^2 + 1) -- a triple root at 0, so f
is not squarefree and the curve is SINGULAR. It is not a genus-2 curve at all,
and the Weil gates were right to reject it.

The sealed text above says "singular cases are dropped by the module's own
asserts". THAT SENTENCE IS FALSE, and I wrote it without checking. `g2_Nv`
asserts only `len(fc)==6 and fc[5]%p!=0` -- degree five, leading coefficient
nonzero. It performs NO squarefree test. MORNING_F describes singular curves
being "filtered by a squarefree-f check", so Session F did that filtering in the
driver that was never committed, and the check left the repo with it.

SO THE MODULE SHIPS WITHOUT A SINGULARITY GUARD. Anyone importing
ff_curve.g2_Nv on an unfiltered family gets confidently wrong N_v, and will
notice only when a Weil gate happens to catch it -- which, Hasse-Weil being a
loose bound, is sometimes. That is precisely the shape of Session F's own
recorded bug, where the loose gate passed some buggy curves and failed others.
Recorded here; guarding the module is a change to another arc's banked artifact
and is registered rather than made in passing.

FIXED BY IMPLEMENTING MY OWN STATED SCOPE, not by changing it: an explicit
squarefree test over F_p (deg gcd(f, f') == 0) now filters genus-2 candidates,
and the genus-1 case keeps the module's discriminant assert, which IS the right
test there. No prediction is altered and no bar moves -- the sealed text always
said the battery was smooth; only the code failed to be.

AMENDMENT 2 — WHAT REPLICATES, WHAT DOES NOT, AND WHAT I AM NOT ENTITLED TO
CONCLUDE FROM THE DIFFERENCE.

REPLICATES, CLEANLY. Hasse-Weil 212/212 and RH-for-curves 212/212 on a family
Session F never used. Its load-bearing claim was never the count 77 -- it was
METHOD-INVARIANCE on provable gates, and that is exactly what an independent
family can corroborate. It does.

DOES NOT REPLICATE. The banked rate ratios:

    genus 1   mine 1.0008 +/- 0.0108 sem (sd 0.081, n=57)    banked 0.9748
    genus 2   mine 1.1147 +/- 0.0238 sem (sd 0.296, n=155)   banked 0.9583

That is -2.4 sem at genus 1 and -6.6 sem at genus 2.

THE REAL POINT IS NOT THE DISAGREEMENT, IT IS THE DISPERSION. The genus-2 ratio
ranges from 0.650 to 1.862 across individual curves, a factor of 2.9, with a
standard deviation of 0.296. F_results.json banks it as

    "genus2_rate_ratio": 0.9583126741064829

-- seventeen significant figures on a quantity whose curve-to-curve spread is
0.3. Whatever that number is, it is a property of the family that was averaged,
and it was banked with no error bar and no n. A reader meeting it has no way to
know it is a mean over a wide distribution rather than a constant. That is the
unattributed-constant failure, and it is the substantive finding here.

AND WHAT I AM NOT ENTITLED TO SAY. M1 misses -- my genus means differ by 0.114
against a 0.05 bar -- but I will NOT report "genus-independence is refuted",
because my own estimator is suspect in exactly the direction of that miss. It
fits log10|N_n/p^n - 1| against n; when that quantity dips near zero at some n
the log dives, steepening the fitted slope and biasing the ratio UP. Genus 2 has
four Frobenius eigenvalues rather than two, so cancellation near zero is far more
frequent there -- which is also why its sd is 3.6x the genus-1 sd. A
genus-dependent BIAS IN MY ESTIMATOR and a genus-dependent EXPONENT predict the
same sign of miss, and this cell does not separate them.

So the honest reading of E3 and M1 is: the banked constants do not reproduce
under a natural estimator on an independent family, and they are quoted with a
precision the quantity does not support. Whether the exponent itself is
genus-dependent is UNRESOLVED and needs an estimator that is robust to
near-zero dips -- median-of-slopes, or a fit on the bound-normalised quantity
|N_n - (p^n+1)|/(2g p^(n/2)) instead.

WHAT THIS CELL DOES NOT CLAIM. It does not recover Session F's run, does not
establish that 77 was the right count, and says nothing about the beta question
MORNING_F explicitly banked as a genus-0 matter.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from aggregate import banked                                      # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PRE_ROLE,    # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE)
from ff_curve import g1_Nv, g2_Nv, hasse_weil_gate, rh_gate       # noqa: E402

def poly_gcd_deg(f, p):
    """Degree of gcd(f, f') over F_p; 0 means f is squarefree. Written here
    because the module it complements does not test this and the battery's
    stated scope requires it."""
    def trim(a):
        while a and a[-1] % p == 0:
            a = a[:-1]
        return [c % p for c in a]

    def divmod_(a, b):
        a = a[:]
        db = len(b) - 1
        inv = pow(b[-1], p - 2, p)
        q = [0] * max(0, len(a) - db)
        for i in range(len(a) - 1, db - 1, -1):
            c = (a[i] * inv) % p
            q[i - db] = c
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % p
        return trim(a)

    fp = trim([(i * c) % p for i, c in enumerate(f)][1:])
    a, b = trim(f[:]), fp
    while b:
        a, b = b, divmod_(a, b)
    return max(len(a) - 1, 0)


PRIMES = [7, 11, 13, 17, 19, 23, 29]
G1_AB = [(a, b) for a in range(1, 4) for b in range(1, 4)]
G2_C = [(c3, c1, c0) for c3 in range(3) for c1 in range(3) for c0 in range(3)]
VMAX = 6
BANKED = {"g1": 0.9747993542043758, "g2": 0.9583126741064829}
TOL = 0.05
MIN_PER_GENUS = 20

INSTRUMENT = Model("provable Weil gates on an independently declared curve "
                   "battery", [
    Param("primes", TESTED, sweep=PRIMES,
          why="the base fields; Session F states p up to 29 and the gates are "
              "provable at every one, so a sweep is the test rather than a "
              "robustness garnish"),
    Param("vmax", DECLARED, value=VMAX,
          why="extension degrees 1..6, the module's own default and the range "
              "over which the Newton-identity bug showed itself (v >= 3)"),
    Param("banked_tolerance", DECLARED, value=TOL,
          why="how close my ratio must land to Session F's banked one. The "
              "enumerations differ deliberately, so exact agreement is not "
              "expected and would be suspicious; 0.05 is about 5% of a "
              "quantity that sits near 1"),
    Param("min_smooth_per_genus", DECLARED, value=MIN_PER_GENUS,
          why="the non-vacuity floor: gates cannot pass 100% meaningfully on an "
              "empty or near-empty battery"),
])


def rate_ratio(res):
    """Decay exponent of |N_n/p^n - 1| against the predicted 0.5*log10(p).

    RH for curves gives |N_n - (p^n+1)| <= 2g p^(n/2), so |N_n/p^n - 1| decays
    like p^(-n/2): slope of log10 against n is -0.5*log10(p). The ratio of the
    MEASURED slope to that is the reported number, and it is 1 when the bound
    is saturated."""
    p = res["p"]
    y, n = [], []
    for v, Nv in enumerate(res["Nv"][:VMAX], start=1):
        r = abs(Nv / float(p ** v) - 1.0)
        if r > 0:
            y.append(np.log10(r))
            n.append(v)
    if len(n) < 3:
        return None
    slope = float(np.polyfit(n, y, 1)[0])
    return -slope / (0.5 * np.log10(p))


rows = []
for p in PRIMES:
    for (a, b) in G1_AB:
        try:
            res = g1_Nv(a, b, p, vmax=VMAX)
        except AssertionError:
            continue                      # singular, dropped by the module
        rows.append(dict(genus=1, p=p, curve=f"y^2=x^3+{a}x+{b}",
                         hw=bool(hasse_weil_gate(res, VMAX)),
                         rh=bool(rh_gate(res)), ratio=rate_ratio(res)))
    for (c3, c1, c0) in G2_C:
        fc = [c0, c1, 0, c3, 0, 1]        # low->high, deg 5 monic
        if poly_gcd_deg(fc, p) != 0:
            continue                      # SINGULAR: the module does not check
        try:
            res = g2_Nv(fc, p, vmax=VMAX)
        except Exception:
            continue                      # singular / miscount asserts
        rows.append(dict(genus=2, p=p, curve=f"y^2=x^5+{c3}x^3+{c1}x+{c0}",
                         hw=bool(hasse_weil_gate(res, VMAX)),
                         rh=bool(rh_gate(res)), ratio=rate_ratio(res)))

g1 = [r for r in rows if r["genus"] == 1]
g2 = [r for r in rows if r["genus"] == 2]
n_hw = sum(1 for r in rows if r["hw"])
n_rh = sum(1 for r in rows if r["rh"])
rat = {g: float(np.mean([r["ratio"] for r in (g1 if g == 1 else g2)
                         if r["ratio"] is not None])) for g in (1, 2)}

print(INSTRUMENT.report())
print(f"\nindependently declared battery: {len(rows)} smooth cases "
      f"({len(g1)} genus-1, {len(g2)} genus-2) over p in {PRIMES}")
print(f"Session F banked 77 cases from families it did not state; this is a "
      f"DIFFERENT enumeration, so the counts are not expected to match.\n")
print(f"  Hasse-Weil pass : {n_hw}/{len(rows)}")
print(f"  RH-for-curves   : {n_rh}/{len(rows)}")
print(f"  rate ratio g=1  : {rat[1]:.6f}   banked {BANKED['g1']:.6f}   "
      f"delta {abs(rat[1] - BANKED['g1']):.6f}")
print(f"  rate ratio g=2  : {rat[2]:.6f}   banked {BANKED['g2']:.6f}   "
      f"delta {abs(rat[2] - BANKED['g2']):.6f}")
print(f"  genus gap       : {abs(rat[1] - rat[2]):.6f}")

nmin = min(len(g1), len(g2))
P1 = Bar("smallest smooth-case count in either genus", MIN_PER_GENUS,
         floor=0, ceiling=len(PRIMES) * max(len(G1_AB), len(G2_C)),
         why="a count; 0 is attainable if the singularity filter removes "
             "everything and the ceiling is the full declared grid")
E1 = Bar("Hasse-Weil pass fraction", 1.0, floor=0.0, ceiling=1.0,
         why="a fraction over the smooth battery; the gate is PROVABLE so "
             "anything below 1 is a defect in the counter, and both ends are "
             "attainable")
E2 = Bar("RH-for-curves pass fraction", 1.0, floor=0.0, ceiling=1.0,
         why="same, and needed alongside Hasse-Weil because Session F's bug "
             "left RH passing while N_v was wrong")
E3 = Bar("worst |replicated - banked| rate ratio across the two genera", TOL,
         direction="le", floor=0.0, ceiling=2.0,
         why="an absolute difference between two quantities near 1; 0 is "
             "attainable and a wholly different exponent would give O(1)")
M1 = Bar("|genus-1 minus genus-2| mean rate ratio", TOL, direction="le",
         floor=0.0, ceiling=2.0,
         why="the genus-independence claim, on the same scale as E3")

worst = max(abs(rat[1] - BANKED["g1"]), abs(rat[2] - BANKED["g2"]))
gap = abs(rat[1] - rat[2])
sP = P1.score(nmin)
s1 = E1.score(n_hw / max(len(rows), 1))
s2 = E2.score(n_rh / max(len(rows), 1))
s3, sM = E3.score(worst), M1.score(gap)

print()
for b, val, f in ((P1, nmin, "{:.0f}"), (E1, n_hw / max(len(rows), 1), "{:.4f}"),
                  (E2, n_rh / max(len(rows), 1), "{:.4f}"),
                  (E3, worst, "{:.4f}"), (M1, gap, "{:.4f}")):
    print("  " + b.line(val, f))

arms = [Arm.from_bar(sP, PRE_ROLE, claim="the battery is non-vacuous"),
        Arm.from_bar(s1, EX_ROLE, claim="Hasse-Weil holds on an independent "
                                        "family"),
        Arm.from_bar(s2, EX_ROLE, claim="and so does RH-for-curves"),
        Arm.from_bar(s3, EX_ROLE, claim="the banked rate ratios replicate"),
        Arm.from_bar(sM, MECH_ROLE, claim="because the exponent is "
                                          "genus-independent")]
v = compose(arms, holds="SESSION_F_CLAIMS_REPLICATE",
            fails="SESSION_F_CLAIMS_DO_NOT_REPLICATE")
print(f"\nVERDICT: {v['citation']}")

with redpath("smooth curve cases", expect_min=40) as rp:
    rp.observed(len(rows))

json.dump(dict(primes=PRIMES, vmax=VMAX, banked=BANKED, tol=TOL,
               instrument=INSTRUMENT.seal(),
               n_cases=len(rows), n_g1=len(g1), n_g2=len(g2),
               hasse_weil_pass=n_hw, rh_pass=n_rh,
               rate_ratio_g1=rat[1], rate_ratio_g2=rat[2],
               worst_delta=worst, genus_gap=gap, rows=rows,
               # ROUTED THROUGH aggregate.banked(), 2026-09-05. This cell is
               # the one that found Session F's constant banked to seventeen
               # figures with no n; its own dispersion block was written by
               # hand and was therefore compliant by memory rather than by
               # construction. banked() cannot return a bare scalar, so the
               # spread now travels with the value whether or not anyone
               # remembers to attach it.
               dispersion={str(g): dict(
                   **{k: v for k, v in banked(f"rate_ratio_genus{g}",
                                              vv).items() if k != "name"},
                   banked_z=float((BANKED["g" + str(g)] - float(np.mean(vv)))
                                  / (float(np.std(vv, ddof=1))
                                     / np.sqrt(len(vv)))))
                   for g, vv in ((g, [r["ratio"] for r in rows
                                      if r["genus"] == g
                                      and r["ratio"] is not None])
                                 for g in (1, 2))},
               estimator_caveat="the log-slope fit is biased UP when "
                                "|N_n/p^n - 1| dips near zero, which happens "
                                "more often at genus 2 (four eigenvalues, more "
                                "cancellation). A genus-dependent estimator "
                                "bias and a genus-dependent exponent predict "
                                "the same sign of miss; this cell does not "
                                "separate them, so M1's miss is NOT read as "
                                "refuting genus-independence",
               bars={s["name"]: s for s in (sP, s1, s2, s3, sM)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/F_reproduce.json", "w"), indent=1)
print("\nwritten -> approximability/F_reproduce.json")
