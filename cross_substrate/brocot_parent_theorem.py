"""IS THE PARENT A THEOREM? Promoting two empirical 100%s, or bounding them.

COMMITTED GENERATOR of cross_substrate/brocot_parent_theorem.json.

THE HOUSE RULE BEING APPLIED
-----------------------------
An empirical 100% is either a theorem in disguise or a claim with an unstated
denominator, and the two get different sentences. `brocot_above_horizon_parent`
banked two of them over 332 ratios:

    P1  the parent is below the horizon              332/332
    P2  the parent is a Stern-Brocot ancestor        332/332

The disjointness result already got this treatment — measured, then proved, then
asserted in the field generator. These two have not.

P1 IS DEFINITIONAL, NOT EVIDENCE
---------------------------------
The parent is |a1|/|a2| with |a1|,|a2| <= A by the box constraint, so
max(p, q) <= A after reduction, which IS "below the horizon". The 332/332 was
never evidence for anything; it was the constraint restated. (It is still worth
running as a wiring check — it would catch a parent built from the wrong pair —
but it must not be reported as a measured rate.) That is recorded here and the
writeup is corrected.

P2 IS A THEOREM, AND HERE IS THE PROOF
---------------------------------------
Claim. For alpha > 0 and A >= 1, let (a1, a2) minimise |a1 + a2*alpha| over
0 < max(|a1|,|a2|) <= A. Then |a1|/|a2| is a CONVERGENT of alpha, hence a
Stern-Brocot ancestor.

  1. Signs. |a1 + a2*alpha| is invariant under negating both, so take a2 >= 0.
     a2 = 0 forces |a1| >= 1, while q = 1, p = round(alpha) gives error <= 1/2,
     so any minimiser has a2 >= 1. Write q = a2, p = -a1; the objective is
     |q*alpha - p|. If p < 0 the error exceeds q*alpha > alpha, again beaten by
     q = 1, so p >= 0.
  2. The usable q form a PREFIX. For fixed q the best p is round(q*alpha).
     q*alpha increases with q, so round(q*alpha) is non-decreasing, so
     {q : round(q*alpha) <= A} = {1, ..., Q'} for some Q'. For q > Q' the best
     ALLOWED p is A, with error q*alpha - A >= 1/2 (since round(q*alpha) >= A+1),
     which is beaten by q = 1 whenever |alpha - round(alpha)| < 1/2 — true for
     every alpha that is not a half-integer. So the minimiser has q <= Q'.
  3. Lagrange. The minimiser of |q*alpha - p| over 1 <= q <= Q' beats every
     (p', q') with q' <= q, so it is a BEST APPROXIMATION OF THE SECOND KIND,
     and by Lagrange's theorem every such approximation is a convergent of
     alpha.
  4. Convergents are ancestors. Each convergent appears on the Stern-Brocot
     descent to alpha.                                                     [] 

WHERE IT CAN FAIL, WHICH IS THE PART WORTH TESTING
---------------------------------------------------
Step 2 excludes half-integer alpha. Step 3 assumes a STRICT minimum: when two
pairs tie in |q*alpha - p|, the minimiser is not unique and the tie-break
decides, and a tie-break that prefers the SHALLOWER pair can select a
non-convergent. Ties are not exotic — alpha here is rational, so |q*alpha - p|
takes values k/den and collisions are common.

So this cell does not merely confirm the proof on the population it was built
from. It PROBES THE STATED FAILURE MODES:

    (a) a wide population, q <= 200, far beyond the 332 the claim came from
    (b) alpha OUTSIDE brocot's regime, where the box constraint bites hardest
    (c) half-integer alpha, the case step 2 excludes by name
    (d) TIES, counted explicitly, with any non-convergent minimiser reported

A witness that cannot fail is not a witness. If (c) or (d) produce a
non-ancestor, the theorem is true as stated and the SCOPE is what the writeup
must carry — which is a better outcome than a 100% with no denominator.

AMENDMENT 1 — AFTER OUTPUT. The probe fired, twice, and both corrections make
the claim sharper.

(i) THE BOUNDARY IS alpha in (1/A, A), AND IT IS A REAL ONE. Seven ratios
    returned a non-ancestor, every one of them with parent = 0: at alpha = 1/9
    with A = 8, (a1, a2) = (0, 1) gives |alpha| = 1/9, and (-1, 8) gives
    |-1 + 8/9| = 1/9 as well — a TIE, broken toward the shallower pair, which
    has a1 = 0 and therefore names the rational 0/1. Step 1 of the proof ruled
    out a2 = 0 and never considered a1 = 0. It arises exactly when the best p
    is round(q*alpha) = 0, i.e. when alpha sits below 1/(2q) for the winning q,
    and every witness has alpha < 1/A. By the reciprocal symmetry of the box
    (|a1 + a2*alpha| = alpha*|a2 + a1/alpha|, with L and R exchanged in the
    tree) the mirror case is alpha > A.

    This is not a defect to hide — it is interpretable. Outside (1/A, A) there
    is no in-box ringing ratio at all, and the nearest lattice point is the
    CARRIER. "Heard against the carrier, with no ratio partner" is the correct
    reading, and it is a category the display should have.

    brocot's regime is [0.70, 1.40], deep inside (1/8, 8). The theorem covers
    the instrument with three orders of margin.

(ii) THE DENOMINATOR WAS WRONG, AND FIXING IT MADE THE RESULT STRONGER. The
    first pass reported "37101/37108 ancestors, 37023 convergents" and I read
    the 85-case difference as SEMIconvergents selected by the tie-break. It was
    not. Those 85 are ratios whose minimiser has a2 = 0 — it names no rational
    at all — which the loop skipped while the denominator kept counting them.
    A dead arm sitting in an n/m tally, which is this repo's dominant recorded
    error mode, committed here by the person who wrote the module against it.

    With the denominator corrected to what was actually tested: 37023/37023
    minimisers are CONVERGENTS, including all 304 tie cases. The tie-break
    never selected a semiconvergent; there were none to select.

    So Lagrange's step is not merely almost-right. It remains formally proved
    only for a STRICT minimum — a tie could in principle be broken toward a
    semiconvergent — but over 304 exercised ties it never was. That sub-claim
    stays EMPIRICAL with n = 304 attached rather than being absorbed into the
    theorem.

So the honest split, which is what the writeup must carry:

    P1  DEFINITIONAL           the box forces max(p,q) <= A
    P2  THEOREM on (1/A, A)    strict minima: the minimiser is a CONVERGENT,
                               via Lagrange plus the prefix-in-q argument
        EMPIRICAL, n = 304     ties also landed on convergents, unproved
        BOUNDARY, characterised alpha outside (1/A, A) has parent 0: the carrier
        SKIPPED, n = 85        a2 = 0 names no rational; not tested, not passed
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from existence import summarise, EXISTENCE                        # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402


def minimisers(alpha, A):
    """(gap, [all (a1,a2) attaining it], chosen) under the shipped tie-break."""
    p, q = alpha.numerator, alpha.denominator
    best, ties = None, []
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            v = abs(a1 * q + a2 * p)
            if best is None or v < best:
                best, ties = v, [(a1, a2)]
            elif v == best:
                ties.append((a1, a2))
    chosen = min(ties, key=lambda t: (max(abs(t[0]), abs(t[1])), -t[1]))
    return Fraction(best, q), ties, chosen


def convergents(fr):
    a, x = [], fr
    while True:
        i = x.numerator // x.denominator
        a.append(i)
        x -= i
        if x == 0:
            break
        x = 1 / x
    h0, h1, k0, k1, out = 0, 1, 1, 0, []
    for i in a:
        h0, h1 = h1, i * h1 + h0
        k0, k1 = k1, i * k1 + k0
        out.append(Fraction(h1, k1))
    return out


def ancestors(target):
    ln, ld, hn, hd, seen = 0, 1, 1, 0, []
    for _ in range(6000):
        mn, md = ln + hn, ld + hd
        m = Fraction(mn, md)
        if m == target:
            return seen
        seen.append(m)
        if target < m:
            hn, hd = mn, md
        else:
            ln, ld = mn, md
    return seen


def parent(alpha, A):
    _, _, (a1, a2) = minimisers(alpha, A)
    return Fraction(abs(a1), abs(a2)) if a2 else None


IN_SCOPE = lambda f, A: Fraction(1, A) < f < A     # noqa: E731  the theorem's range

POPS = {
    "(a) brocot regime, q <= 200": [
        Fraction(p, q) for q in range(1, 201) for p in range(1, 300)
        if 0.70 <= p / q <= 1.40 and gcd(p, q) == 1],
    "(b) outside the regime, 0.1-8.0": [
        Fraction(p, q) for q in range(1, 41) for p in range(1, 330)
        if 0.10 <= p / q <= 8.0 and gcd(p, q) == 1],
    "(c) half-integers (step 2 excludes these)": [
        Fraction(2 * k + 1, 2) for k in range(0, 40)],
}

results, worst = {}, []
for label, pop in POPS.items():
    for A in (8, 10, 14):
        tested = skipped = below = anc = conv = tied = nonanc = 0
        for f in pop:
            if max(f.numerator, f.denominator) <= A:
                continue                       # below the horizon: gap 0, fuses
            g, ties, ch = minimisers(f, A)
            if g == 0:
                continue
            if ch[1] == 0:
                # a2 = 0: the minimiser names no rational at all. NOT a pass and
                # NOT a fail -- it is untested, and it must be counted as such
                # rather than sitting silently in a denominator.
                skipped += 1
                continue
            tested += 1
            par = Fraction(abs(ch[0]), abs(ch[1]))
            below += max(par.numerator, par.denominator) <= A
            isanc = par in ancestors(f)
            anc += isanc
            conv += par in convergents(f)
            if len(ties) > 2:                  # (a,b) and (-a,-b) always pair
                tied += 1
            if not isanc:
                if IN_SCOPE(f, A):
                    nonanc += 1
                if len(worst) < 8:
                    worst.append(dict(alpha=str(f), A=A, parent=str(par),
                                      gap=float(g), n_ties=len(ties) // 2,
                                      in_scope=bool(IN_SCOPE(f, A)), pop=label))
        results[f"{label} | A={A}"] = dict(
            n=tested, skipped_no_rational=skipped, parent_below=below,
            ancestor=anc, convergent=conv, with_ties=tied,
            non_ancestor_in_scope=nonanc)

print("PARENT THEOREM — probing the proof's own stated failure modes\n")
print(f"{'population | A':>44s} {'tested':>7s} {'skip':>5s} {'below':>7s} "
      f"{'anc':>7s} {'conv':>7s} {'ties':>6s} {'BAD':>4s}")
for k, v in results.items():
    print(f"{k:>44s} {v['n']:>7d} {v['skipped_no_rational']:>5d} "
          f"{v['parent_below']:>7d} {v['ancestor']:>7d} "
          f"{v['convergent']:>7d} {v['with_ties']:>6d} "
          f"{v['non_ancestor_in_scope']:>4d}")

bad = sum(v["non_ancestor_in_scope"] for v in results.values())
skipped_total = sum(v["skipped_no_rational"] for v in results.values())
N = sum(v["n"] for v in results.values())
p1_definitional = all(v["parent_below"] == v["n"] for v in results.values())
p2_holds = bad == 0
ties_seen = sum(v["with_ties"] for v in results.values())

print(f"\nP1  parent below the horizon: {sum(v['parent_below'] for v in results.values())}"
      f"/{N} — and DEFINITIONAL: |a1|,|a2| <= A forces max(p,q) <= A.")
print("    Reported as a wiring check from here on, never as a measured rate.")
print(f"P2  parent is a Stern-Brocot ancestor: {N - bad}/{N} TESTED, across "
      f"{len(POPS)} populations and 3 horizons")
print(f"    {skipped_total} further ratios SKIPPED, not passed: the minimiser "
      f"had a2 = 0 and names no rational.\n    They are excluded from the "
      f"denominator rather than counted as agreement.")
print(f"    convergent (the stronger form): "
      f"{sum(v['convergent'] for v in results.values())}/{N}")
nconv = sum(v["convergent"] for v in results.values())
print(f"    cases with a genuine tie in the argmin: {ties_seen} — the proof's "
      f"named soft spot, exercised")
print(f"    ancestors that are SEMIconvergents (tie-selected): {N - bad - nconv}"
      f" — Lagrange proves the strict case; these stay EMPIRICAL with n stated")
if worst:
    print("\n    NON-ANCESTOR WITNESSES — all OUTSIDE (1/A, A), all parent 0:")
    for w in worst:
        print(f"      alpha={w['alpha']:>9s} A={w['A']:<3d} parent={w['parent']:>7s} "
              f"ties={w['n_ties']:<3d} {w['pop']}")

verdict = ("P2_IS_A_THEOREM_ON_1_OVER_A_TO_A" if p2_holds
           else "P2_HOLDS_ON_A_STATED_POPULATION")
print(f"\nVERDICT: {verdict}")
if p2_holds:
    print("  The 332/332 is confirmation of a proof, not evidence for a rate.")
    print("  Lagrange on best approximations of the second kind, with the box")
    print("  reduced to a prefix in q. Both 100%s leave the table.")
    print("  Outside (1/A, A) the parent degenerates to 0 — no in-box ringing")
    print("  ratio exists and the nearest lattice point is the CARRIER. That is")
    print("  a category, not a counterexample. brocot's [0.70, 1.40] sits deep")
    print("  inside (1/8, 8).")

ex = summarise("n_non_ancestor",
               [v["non_ancestor_in_scope"] for v in results.values()], EXISTENCE)
with redpath("ratios probed outside the originating population", expect_min=2000) as rp:
    rp.observed(N)

json.dump(dict(populations=list(POPS), horizons=[8, 10, 14], n_probed=N,
               results=results, non_ancestor_in_scope_total=bad,
               skipped_no_rational=skipped_total,
               ties_encountered=ties_seen,
               p1_definitional=bool(p1_definitional), p2_holds=bool(p2_holds),
               witnesses=worst, existence=ex, verdict=verdict),
          open(f"{HERE}/brocot_parent_theorem.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_parent_theorem.json")
