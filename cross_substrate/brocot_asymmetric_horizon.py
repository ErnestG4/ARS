"""THE ASYMMETRIC HORIZON: the corollary the fusion-density column rests on.

COMMITTED GENERATOR of cross_substrate/brocot_asymmetric_horizon.json.

WHY THIS IS OWED
----------------
`brocot_map_dimension` shipped a graph column on 1.1M pairs, and every one of
those pairs used a form of the horizon that COINCIDENCE-HORIZON.md does not
contain. The published theorem is symmetric in a single index I. A real patch
has per-operator indices, and the column's arithmetic used

    p <= 2*order_bound(I1)   AND   q <= 2*order_bound(I2)

stated inline with a proof sketch and an affordability argument. The symmetric
theorem earned its label at 508/508 against exact enumeration; this has earned
nothing yet. Until it does, a shipped column rests on a corollary the paper
does not contain.

THE COROLLARY
-------------
Two modulators at ratios r1, r2 with indices I1, I2; write B1 = order_bound(I1),
B2 = order_bound(I2). Sidebands sit at f_c*(1 + n1*r1 + n2*r2) with |n1| <= B1
and |n2| <= B2. Scale so r1 = 1 and alpha = r2/r1 = p/q in lowest terms.

  NECESSITY. Two distinct index pairs coincide iff a + b*alpha = 0 with
  a = n1 - n1', b = n2 - n2', so |a| <= 2B1 and |b| <= 2B2. Then a*q + b*p = 0,
  and gcd(p,q) = 1 forces a = m*p, b = -m*q for integer m != 0. The smallest
  admissible |m| is 1, so reachability requires p <= 2B1 AND q <= 2B2.

  SUFFICIENCY, WITNESS RE-DERIVED. The symmetric proof's witness was
  (ceil(p/2), -floor(p/2)) for (n1, n1') and (-floor(q/2), ceil(q/2)) for
  (n2, n2'). It survives, but ONLY because each half is checked against its OWN
  box — and that is the step where "obviously survives" would have been wrong:

      n1  =  ceil(p/2),   n1' = -floor(p/2)   ->  n1 - n1'  =  p    [box 1]
      n2  = -floor(q/2),  n2' =  ceil(q/2)    ->  n2 - n2'  = -q    [box 2]

  p <= 2B1 gives ceil(p/2) <= B1 and floor(p/2) <= B1, so the first pair fits
  box 1; q <= 2B2 gives the second pair box 2. Assigning p's half to B2 or q's
  to B1 fails exactly when the boxes differ, which is the whole asymmetric case.

  INVARIANCE. Relabelling the operators sends alpha -> q/p and swaps B1 <-> B2,
  so the condition becomes q <= 2B2 and p <= 2B1 — the same condition. The
  corollary does not depend on which operator is called first.

  NOT INVARIANT, and this is physical: moving the HIGHER INDEX to the other
  operator, holding the ratios fixed, changes the condition from
  (p <= 2B1, q <= 2B2) to (p <= 2B2, q <= 2B1). Which operator is driven harder
  matters. The symmetric theorem cannot see this at all.

WHAT IS CHECKED HERE, ON THE SAME FOOTING AS THE 508/508
----------------------------------------------------------
  A1  exact ground truth by enumeration over the full (n1, n2) sideband grid,
      in exact rational arithmetic, against the predicate — over a mixed
      (I1, I2) grid including every asymmetric combination
  A2  the sufficiency witness, constructed explicitly and checked in bounds and
      telescoping to zero, at every reachable triple
  A3  relabelling invariance, node by node
  A4  the SHARP BOUNDARY exhibit at the asymmetric line: ratios that are
      reachable at (I1, I2) and unreachable at (I2, I1). If this set is empty
      the asymmetric form is not doing anything the symmetric one does not, and
      the column should have used the symmetric bound.

A4 is the non-inertness arm. Without it, A1 passing would be compatible with
the asymmetric predicate never differing from the symmetric one on this grid.

AMENDMENT 1 — BEFORE ANY VERDICT WAS READ. The planted non-vacuity floor (4000
exact checks) fired: PQ_MAX = 22 reached only 3248. Raised to 22, not lowered to
3248 — the same call as brocot_tie_lemma, and for the same reason: a floor
retuned to what the run happened to produce is a floor that has stopped
policing anything. Nothing else changed.
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

I_GRID = [0.9, 1.5, 2.0, 3.0]
PQ_MAX = 22
RATIOS = sorted({Fraction(p, q) for p in range(1, PQ_MAX + 1)
                 for q in range(1, PQ_MAX + 1) if gcd(p, q) == 1}, key=float)


def truth(alpha, B1, B2):
    """Exact: does any two distinct (n1,n2) give the same partial frequency?"""
    seen = set()
    for n1 in range(-B1, B1 + 1):
        for n2 in range(-B2, B2 + 1):
            v = 1 + n1 + n2 * alpha
            if v in seen:
                return True
            seen.add(v)
    return False


def predicted(alpha, B1, B2):
    return alpha.numerator <= 2 * B1 and alpha.denominator <= 2 * B2


def witness(alpha, B1, B2):
    """The explicit sufficiency pair, each half against its own box."""
    p, q = alpha.numerator, alpha.denominator
    n1, n1p = -(-p // 2), -(p // 2)          # ceil(p/2), -floor(p/2)
    n2, n2p = -(q // 2), -(-q // 2)          # -floor(q/2), ceil(q/2)
    in_box = (abs(n1) <= B1 and abs(n1p) <= B1
              and abs(n2) <= B2 and abs(n2p) <= B2)
    telescopes = ((1 + n1 + n2 * alpha) == (1 + n1p + n2p * alpha))
    return in_box, telescopes, (n1, n1p, n2, n2p)


rows, wit_ok, wit_n, inv_bad, sharp = [], 0, 0, [], []
sharp_seen = set()
for I1 in I_GRID:
    for I2 in I_GRID:
        B1, B2 = order_bound(I1), order_bound(I2)
        agree = n = 0
        for a in RATIOS:
            t, pr = truth(a, B1, B2), predicted(a, B1, B2)
            n += 1
            agree += (t == pr)
            if pr:
                wit_n += 1
                ib, tel, _ = witness(a, B1, B2)
                wit_ok += (ib and tel)
            # A3 relabelling: alpha -> q/p with the boxes swapped
            if predicted(1 / a, B2, B1) != pr:
                inv_bad.append((str(a), I1, I2))
            # A4 the asymmetric line: reachable one way round, not the other
            if I1 != I2 and pr != predicted(a, B2, B1):
                # DE-DUPLICATED 2026-08-25 (adversarial review): each flip was
                # recorded under both (I1,I2) and (I2,I1), so the headline
                # double-counted. Keyed on the UNORDERED index pair now.
                key = (str(a), min(I1, I2), max(I1, I2))
                if key not in sharp_seen:
                    sharp_seen.add(key)
                    sharp.append(dict(alpha=str(a), I1=I1, I2=I2,
                                      at_I1I2=bool(pr),
                                      at_I2I1=bool(predicted(a, B2, B1))))
        rows.append(dict(I1=I1, I2=I2, B1=B1, B2=B2, n=n, agree=agree,
                         accuracy=agree / n))

tot_n = sum(r["n"] for r in rows)
tot_a = sum(r["agree"] for r in rows)
a1 = tot_a == tot_n
a2 = wit_ok == wit_n
a3 = not inv_bad
a4 = len(sharp) > 0

print(f"ratios p/q with p,q <= {PQ_MAX}: {len(RATIOS)}   "
      f"index grid: {I_GRID} x {I_GRID}\n")
print(f"{'I1':>5s} {'I2':>5s} {'B1':>3s} {'B2':>3s} {'n':>5s} "
      f"{'agree':>6s} {'accuracy':>9s}")
for r in rows:
    flag = "" if r["accuracy"] == 1.0 else "   <-- MISMATCH"
    print(f"{r['I1']:>5.1f} {r['I2']:>5.1f} {r['B1']:>3d} {r['B2']:>3d} "
          f"{r['n']:>5d} {r['agree']:>6d} {r['accuracy']:>9.4f}{flag}")

print(f"\nA1  predicate vs exact enumeration: {tot_a}/{tot_n}   "
      f"{'PASS' if a1 else 'FAIL'}")
print(f"A2  sufficiency witness in-box and telescoping: {wit_ok}/{wit_n}   "
      f"{'PASS' if a2 else 'FAIL'}")
print(f"A3  relabelling invariance: {'PASS' if a3 else f'FAIL {inv_bad[:3]}'}")
n_distinct_ratios = len({w["alpha"] for w in sharp})
print(f"A4  asymmetric line non-empty: {len(sharp)} (alpha, index-pair) flips "
      f"across {n_distinct_ratios} distinct ratios   "
      f"{'PASS' if a4 else 'FAIL — INERT'}")
if sharp:
    print("\n    exhibit — same two ratios, same two indices, swapped between ops:")
    for w in sharp[:6]:
        print(f"      alpha={w['alpha']:>6s}  I=({w['I1']}, {w['I2']}) "
              f"{'fuses' if w['at_I1I2'] else 'silent':>6s}   "
              f"I=({w['I2']}, {w['I1']}) {'fuses' if w['at_I2I1'] else 'silent':>6s}")

verdict = ("ASYMMETRIC_COROLLARY_VERIFIED" if (a1 and a2 and a3 and a4)
           else "COROLLARY_NOT_VERIFIED")
print(f"\nVERDICT: {verdict}")
if verdict == "ASYMMETRIC_COROLLARY_VERIFIED":
    print(f"  {tot_n} exact checks across {len(rows)} index pairs, the witness")
    print("  constructed at every reachable triple, relabelling invariance node")
    print("  by node, and the asymmetric line demonstrably non-empty. The")
    print("  fusion-density column now rests on a verified corollary.")

ex = summarise("n_asymmetric_flips", [1] * len(sharp), EXISTENCE)
with redpath("exact predicate checks", expect_min=4000) as rp:
    rp.observed(tot_n)

json.dump(dict(I_grid=I_GRID, pq_max=PQ_MAX, n_ratios=len(RATIOS),
               n_checks=tot_n, n_agree=tot_a, rows=rows,
               witness_checked=wit_n, witness_ok=wit_ok,
               invariance_failures=inv_bad[:20],
               asymmetric_flips=len(sharp),
               asymmetric_flip_distinct_ratios=n_distinct_ratios,
               exhibit=sharp[:12],
               checks=dict(A1=bool(a1), A2=bool(a2), A3=bool(a3), A4=bool(a4)),
               verdict=verdict),
          open(f"{HERE}/brocot_asymmetric_horizon.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_asymmetric_horizon.json")
