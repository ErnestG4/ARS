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
        below = anc = conv = tied = nonanc = 0
        for f in pop:
            if max(f.numerator, f.denominator) <= A:
                continue
            g, ties, ch = minimisers(f, A)
            if g == 0:
                continue
            par = Fraction(abs(ch[0]), abs(ch[1])) if ch[1] else None
            if par is None:
                continue
            below += max(par.numerator, par.denominator) <= A
            isanc = par in ancestors(f)
            anc += isanc
            conv += par in convergents(f)
            if len(ties) > 2:                     # (a,b) and (-a,-b) always pair
                tied += 1
            if not isanc:
                nonanc += 1
                if len(worst) < 6:
                    worst.append(dict(alpha=str(f), A=A, parent=str(par),
                                      gap=float(g), n_ties=len(ties) // 2,
                                      pop=label))
            n = below  # placeholder to keep names honest below
        tot = sum(1 for f in pop
                  if max(f.numerator, f.denominator) > A
                  and minimisers(f, A)[0] != 0)
        results[f"{label} | A={A}"] = dict(
            n=tot, parent_below=below, ancestor=anc, convergent=conv,
            with_ties=tied, non_ancestor=nonanc)

print("PARENT THEOREM — probing the proof's own stated failure modes\n")
print(f"{'population | A':>44s} {'n':>6s} {'below':>7s} {'anc':>7s} "
      f"{'conv':>7s} {'ties':>6s} {'BAD':>4s}")
for k, v in results.items():
    print(f"{k:>44s} {v['n']:>6d} {v['parent_below']:>7d} {v['ancestor']:>7d} "
          f"{v['convergent']:>7d} {v['with_ties']:>6d} {v['non_ancestor']:>4d}")

bad = sum(v["non_ancestor"] for v in results.values())
N = sum(v["n"] for v in results.values())
p1_definitional = all(v["parent_below"] == v["n"] for v in results.values())
p2_holds = bad == 0
ties_seen = sum(v["with_ties"] for v in results.values())

print(f"\nP1  parent below the horizon: {sum(v['parent_below'] for v in results.values())}"
      f"/{N} — and DEFINITIONAL: |a1|,|a2| <= A forces max(p,q) <= A.")
print("    Reported as a wiring check from here on, never as a measured rate.")
print(f"P2  parent is a Stern-Brocot ancestor: {N - bad}/{N} across "
      f"{len(POPS)} populations and 3 horizons")
print(f"    convergent (the stronger form): "
      f"{sum(v['convergent'] for v in results.values())}/{N}")
print(f"    cases with a genuine tie in the argmin: {ties_seen} — the proof's "
      f"named soft spot, exercised")
if worst:
    print("\n    NON-ANCESTOR WITNESSES (the theorem's scope boundary):")
    for w in worst:
        print(f"      alpha={w['alpha']:>9s} A={w['A']:<3d} parent={w['parent']:>7s} "
              f"ties={w['n_ties']:<3d} {w['pop']}")

verdict = ("P2_IS_A_THEOREM" if p2_holds else "P2_HOLDS_ON_A_STATED_POPULATION")
print(f"\nVERDICT: {verdict}")
if p2_holds:
    print("  The 332/332 is confirmation of a proof, not evidence for a rate.")
    print("  Lagrange's theorem on best approximations of the second kind, with")
    print("  the box reduced to a prefix in q. Both 100%s leave the table.")

ex = summarise("n_non_ancestor", [v["non_ancestor"] for v in results.values()],
               EXISTENCE)
with redpath("ratios probed outside the originating population", expect_min=2000) as rp:
    rp.observed(N)

json.dump(dict(populations=list(POPS), horizons=[8, 10, 14], n_probed=N,
               results=results, non_ancestor_total=bad,
               ties_encountered=ties_seen,
               p1_definitional=bool(p1_definitional), p2_holds=bool(p2_holds),
               witnesses=worst, existence=ex, verdict=verdict),
          open(f"{HERE}/brocot_parent_theorem.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_parent_theorem.json")
