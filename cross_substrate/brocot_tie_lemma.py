"""THE TIE LEMMA: closing the last empirical 100% in the parent theorem.

COMMITTED GENERATOR of cross_substrate/brocot_tie_lemma.json.

WHY THIS EXISTS
---------------
`brocot_parent_theorem` proved that the parent is a convergent of alpha where the
argmin is STRICT, and left the tie case as "empirical, n = 304". By the rule that
cell itself minted, that is not a resting place: an empirical 100% is either a
theorem in disguise or a claim with an unstated denominator, and a residue
labelled correctly is still a residue.

THE LEMMA
---------
Claim. Let alpha > 0, A >= 1, and let the argmin of |a1 + a2*alpha| over the box
be attained by several pairs. The shipped tie-break — smallest max(|a1|,|a2|),
then a2 > 0 — selects a CONVERGENT of alpha.

  1. Normalise as in the parent theorem: a2 = q > 0, p = -a1, objective
     |q*alpha - p|, and q ranges over a prefix {1..Q'}. A minimiser must use the
     optimal p for its own q, namely p = round(q*alpha).
  2. max(p, q) IS STRICTLY INCREASING IN q over that prefix. For alpha <= 1,
     p = round(q*alpha) <= q so max = q, strictly increasing. For alpha > 1,
     q*alpha gains more than 1 per step so p = round(q*alpha) is strictly
     increasing and max = p. Either way the order by max(p,q) IS the order by q.
  3. Therefore "smallest max" selects the minimiser with the smallest q. Call it
     (p, q). Every q' < q fails to be a minimiser — by minimality of q — so
     |q'*alpha - p'| > |q*alpha - p| STRICTLY for all q' < q.
  4. That is exactly the definition of a best approximation of the second kind,
     so by Lagrange's theorem (p, q) is a convergent of alpha.               []

The lemma is unconditional in alpha > 0. What still needs (1/A, A) is the step
from convergent to Stern-Brocot ANCESTOR: at alpha < 1/A the selected p can be 0,
and 0/1 is the tree's boundary rather than a node on the descent.

WHAT MAKES THIS A TEST AND NOT A RESTATEMENT
---------------------------------------------
Step 2 is where the lemma lives, and step 3 is where the TIE-BREAK becomes
load-bearing: the proof works for "smallest max" and for no other rule. So this
cell does three things, and the third is the one that can fail:

  (a) verify the monotonicity of step 2 directly, per alpha, over the prefix
  (b) verify on a large tie population that the selected pair is a convergent
  (c) DECOY — re-run the same populations under WRONG tie-breaks (largest max,
      largest a2, lexicographic) and confirm they DO select non-convergents.
      If every rule passes, the lemma is not saying anything about the shipped
      one, and (b) is measuring the population rather than the rule.

(c) is the non-inertness argument. A witness that cannot fail is not a witness.
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

RULES = {
    "shipped: smallest max(|a1|,|a2|)": lambda t: (max(abs(t[0]), abs(t[1])), -t[1]),
    "decoy: largest max":               lambda t: (-max(abs(t[0]), abs(t[1])), -t[1]),
    "decoy: largest |a2|":              lambda t: (-abs(t[1]), abs(t[0])),
    "decoy: lexicographic on (a1,a2)":  lambda t: (t[0], t[1]),
}


def all_minimisers(alpha, A):
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
    return best, ties


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
    return set(out)


def prefix_monotone(alpha, A):
    """Step 2, checked directly: max(round(q*alpha), q) strictly increases."""
    prev = None
    for q in range(1, A + 1):
        p = int(alpha * q + Fraction(1, 2))          # round-half-up, exact
        if p > A:
            break
        m = max(p, q)
        if prev is not None and m <= prev:
            return False
        prev = m
    return True


POP = [Fraction(p, q) for q in range(1, 121) for p in range(1, 200)
       if Fraction(1, 8) < Fraction(p, q) < 8 and gcd(p, q) == 1]
HORIZONS = (8, 10, 14)

mono_fail, tie_cases = [], 0
per_rule = {k: dict(selected=0, convergent=0, nonconv_witness=None) for k in RULES}

for A in HORIZONS:
    for f in POP:
        if max(f.numerator, f.denominator) <= A:
            continue
        if not prefix_monotone(f, A):
            mono_fail.append((str(f), A))
        m, ties = all_minimisers(f, A)
        if m == 0 or len(ties) <= 2:                 # (a,b) and (-a,-b) pair up
            continue
        tie_cases += 1
        cv = convergents(f)
        for name, key in RULES.items():
            a1, a2 = min(ties, key=key)
            if a2 == 0:
                continue                              # names no rational
            par = Fraction(abs(a1), abs(a2))
            per_rule[name]["selected"] += 1
            if par in cv:
                per_rule[name]["convergent"] += 1
            elif per_rule[name]["nonconv_witness"] is None:
                per_rule[name]["nonconv_witness"] = dict(
                    alpha=str(f), A=A, chose=str(par), n_ties=len(ties) // 2)

print(f"population: {len(POP)} ratios in (1/8, 8), horizons {HORIZONS}")
print(f"step 2 — max(p,q) strictly increasing over the prefix: "
      f"{'HOLDS everywhere' if not mono_fail else f'FAILS at {mono_fail[:3]}'}")
print(f"genuine ties in the argmin: {tie_cases}   "
      f"(the parent theorem exercised 304)\n")
print(f"{'tie-break rule':>34s} {'selected':>9s} {'convergent':>11s} "
      f"{'rate':>7s}   first non-convergent")
for name, v in per_rule.items():
    w = v["nonconv_witness"]
    rate = v["convergent"] / v["selected"] if v["selected"] else 0.0
    wit = (f"alpha={w['alpha']} A={w['A']} -> {w['chose']}" if w else "— none —")
    print(f"{name:>34s} {v['selected']:>9d} {v['convergent']:>11d} "
          f"{rate:>6.1%}   {wit}")

shipped = per_rule["shipped: smallest max(|a1|,|a2|)"]
lemma_holds = (not mono_fail) and shipped["selected"] == shipped["convergent"]
decoys = {k: v for k, v in per_rule.items() if k.startswith("decoy")}
decoys_fire = sum(1 for v in decoys.values()
                  if v["nonconv_witness"] is not None)

print(f"\nnon-inertness: {decoys_fire}/{len(decoys)} decoy tie-breaks DO select "
      f"a non-convergent")
verdict = ("TIE_CASE_IS_A_THEOREM" if (lemma_holds and decoys_fire)
           else "LEMMA_HOLDS_BUT_TEST_IS_INERT" if lemma_holds
           else "LEMMA_FALSIFIED")
print(f"\nVERDICT: {verdict}")
if verdict == "TIE_CASE_IS_A_THEOREM":
    print("  Ordering by max(p,q) IS ordering by q, so the shipped tie-break")
    print("  selects the smallest-denominator minimiser, which strictly beats")
    print("  every smaller denominator and is therefore a convergent by")
    print("  Lagrange. The parent theorem's last empirical residue closes, and")
    print("  the decoys show the rule is load-bearing rather than the")
    print("  population being forgiving.")
elif verdict == "LEMMA_HOLDS_BUT_TEST_IS_INERT":
    print("  Every tie-break passes, so this measures the population and not")
    print("  the rule. The 100% stays EMPIRICAL and the claim is not earned.")

ex = summarise("n_nonconvergent_shipped",
               [shipped["selected"] - shipped["convergent"]], EXISTENCE)
with redpath("genuine tie cases exercised", expect_min=300) as rp:
    rp.observed(tie_cases)

json.dump(dict(n_population=len(POP), horizons=list(HORIZONS),
               tie_cases=tie_cases, monotonicity_failures=mono_fail[:20],
               rules={k: dict(selected=v["selected"], convergent=v["convergent"],
                              nonconv_witness=v["nonconv_witness"])
                      for k, v in per_rule.items()},
               decoys_that_fire=decoys_fire, lemma_holds=bool(lemma_holds),
               existence=ex, verdict=verdict),
          open(f"{HERE}/brocot_tie_lemma.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_tie_lemma.json")
