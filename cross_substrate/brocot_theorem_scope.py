"""THEOREM SCOPE: the fold convention, and how much of the ladder is epsilon.

COMMITTED GENERATOR of cross_substrate/brocot_theorem_scope.json.
Predictions sealed here, before any output exists.

WHY THIS RUNS
-------------
Review of COINCIDENCE-HORIZON.md raised two scope gaps that the 508/508
verification cannot see, because the verification and the proof share the same
convention and would agree with each other whether or not it matched the synth.

(A) THE FOLD. `predict_partials` reflects negative frequencies onto the positive
    axis — "Negative absolute frequencies reflect to their positive counterparts
    and amplitudes sum at the reflected bin (Web Audio behaviour)",
    partial_prediction.py:20-21 and :117-123. My coincidence checker compared
    UNFOLDED lattice values. So the theorem is about the unfolded lattice, and
    the folded lattice has a SECOND coincidence channel the proof never handled:

        1 + n1 + n2*a = -(1 + n1' + n2'*a)
        =>  2 + (n1+n1') + (n2+n2')*a = 0

    With a = p/q this needs q | (n2+n2'), so n2+n2' = k*q and n1+n1' = -k*p - 2.
    The k = 0 branch is the alarming one: n1 = n1' = -1 and n2 = -n2' = m gives
    +m*a and -m*a, which reflect onto each other for ANY a whatsoever — rational
    or irrational. If that branch dominates, the folded lattice has coincidences
    everywhere and the horizon would be vacuous for the instrument as shipped.

    This run measures the two channels separately at every node.

(B) EPSILON. The theorem is exact GIVEN B, but B = order_bound(I) is defined by
    |J_n(I)| > eps with eps defaulting to 1e-3. Every "rings from I >= ..." rung
    in the ladder is therefore eps-relative. The 4/3 rung is the tell: it needs
    B >= 2, and J_2(0.1) ~ 0.00125 — barely over the default. A constant doing
    classification work has to be written down and its influence measured.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ T1  The DIRECT channel reproduces the horizon exactly: direct coincidence     ║
║     <=> max(p,q) <= 2B, at every node. (Re-verification under the split.)     ║
║ T2  The k=0 REFLECTED branch fires at EVERY node, above and below the         ║
║     horizon alike — so it carries no ratio-dependent information.             ║
║ T3  Because of T2, the FOLDED lattice has coincidences everywhere, and a      ║
║     predicate stated over folded values would be vacuous. The horizon is      ║
║     therefore a statement about the DIRECT channel and must say so.           ║
║ T4  The ladder's ORDERING is eps-invariant across eps in {1e-2, 1e-3, 1e-4}   ║
║     while its absolute I-thresholds are not: at least one rung moves.         ║
║                                                                              ║
║ IF T2 FAILS the fold is harmless and one scope sentence suffices. IF T2       ║
║ HOLDS the document must say which lattice the theorem is about, because a     ║
║ reader who assumes standard FM folding would otherwise find the proof         ║
║ incomplete — and would be right.                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy.special import jv

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import order_bound                 # noqa: E402

INDICES = [0.9, 1.5, 2.0, 3.0]
EPSILONS = [1e-2, 1e-3, 1e-4]
LO, HI, QMAX = 0.70, 1.40, 24
SPEC_LADDER = [Fraction(4, 3), Fraction(9, 7), Fraction(14, 11), Fraction(43, 34)]

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 40)
                if LO <= p / q <= HI and np.gcd(p, q) == 1}, key=float)


def channels(alpha, B):
    """Count coincidences in the DIRECT and REFLECTED channels separately.

    A partial sits at 1 + n1 + n2*alpha (carrier units). DIRECT: two partials
    share that value. REFLECTED: two partials have values summing to zero, so
    folding maps one onto the other.
    """
    vals = {}
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            vals[(n1, n2)] = Fraction(1) + Fraction(n1) + Fraction(n2) * alpha
    seen, direct = set(), 0
    for v in vals.values():
        if v in seen:
            direct += 1
        else:
            seen.add(v)
    refl_k0 = refl_other = 0
    keys = list(vals)
    for i, k1 in enumerate(keys):
        v1 = vals[k1]
        if v1 <= 0:
            continue
        for k2 in keys[i + 1:]:
            if vals[k2] != -v1:
                continue
            if k1[0] + k2[0] == -2 and k1[1] + k2[1] == 0:
                refl_k0 += 1
            else:
                refl_other += 1
    return direct, refl_k0, refl_other


rows = {}
for I in INDICES:
    B = order_bound(I)
    hor = 2 * B
    per = []
    for fr in NODES:
        d, r0, ro = channels(fr, B)
        per.append(dict(node=str(fr), maxpq=max(fr.numerator, fr.denominator),
                        below=max(fr.numerator, fr.denominator) <= hor,
                        direct=d, refl_k0=r0, refl_other=ro))
    t1 = all((r["direct"] > 0) == r["below"] for r in per)
    k0_everywhere = all(r["refl_k0"] > 0 for r in per)
    k0_above = sum(1 for r in per if not r["below"] and r["refl_k0"] > 0)
    n_above = sum(1 for r in per if not r["below"])
    folded_any = all((r["direct"] + r["refl_k0"] + r["refl_other"]) > 0 for r in per)
    rows[I] = dict(I=I, B=B, horizon=hor, n_nodes=len(per),
                   direct_matches_horizon=bool(t1),
                   k0_fires_everywhere=bool(k0_everywhere),
                   k0_above_horizon=f"{k0_above}/{n_above}",
                   folded_coincidence_at_every_node=bool(folded_any),
                   median_refl_k0=float(np.median([r["refl_k0"] for r in per])),
                   median_refl_other=float(np.median([r["refl_other"] for r in per])))

print("(A) CHANNEL SPLIT — direct vs reflected\n")
print(f"{'I':>5s} {'B':>3s} {'horizon':>8s} {'direct==horizon':>16s} "
      f"{'k0 everywhere':>14s} {'k0 above horizon':>17s} {'folded: any coinc':>18s}")
for I in INDICES:
    r = rows[I]
    print(f"{I:>5.1f} {r['B']:>3d} {r['horizon']:>8d} "
          f"{str(r['direct_matches_horizon']):>16s} {str(r['k0_fires_everywhere']):>14s} "
          f"{r['k0_above_horizon']:>17s} {str(r['folded_coincidence_at_every_node']):>18s}")

t1 = all(rows[I]["direct_matches_horizon"] for I in INDICES)
t2 = all(rows[I]["k0_fires_everywhere"] for I in INDICES)
t3 = all(rows[I]["folded_coincidence_at_every_node"] for I in INDICES)

# ── (B) epsilon sensitivity of the ladder ──────────────────────────────────
def ob(I, eps):
    n = 0
    while n <= 50 and abs(jv(n + 1, I)) > eps:
        n += 1
    return n


def rings_from(fr, eps):
    need = int(np.ceil(max(fr.numerator, fr.denominator) / 2))
    for I in np.arange(0.05, 12.001, 0.01):
        if ob(float(I), eps) >= need:
            return round(float(I), 2)
    return None


print("\n(B) EPSILON SENSITIVITY of the spec ladder\n")
print(f"{'ratio':>7s} {'max(p,q)':>9s} " + " ".join(f"{'eps='+str(e):>12s}" for e in EPSILONS))
ladder = {}
for fr in SPEC_LADDER:
    vals = [rings_from(fr, e) for e in EPSILONS]
    ladder[str(fr)] = {str(e): v for e, v in zip(EPSILONS, vals)}
    print(f"{str(fr):>7s} {max(fr.numerator, fr.denominator):>9d} "
          + " ".join(f"{(str(v) if v else '>12'):>12s}" for v in vals))

orders = []
for e in EPSILONS:
    seq = [rings_from(fr, e) or 999 for fr in SPEC_LADDER]
    orders.append(all(a <= b for a, b in zip(seq, seq[1:])))
moved = any(len({ladder[str(fr)][str(e)] for e in EPSILONS}) > 1 for fr in SPEC_LADDER)
t4 = all(orders) and moved

print(f"\nT1  direct channel reproduces the horizon exactly   {'MET' if t1 else 'MISSED'}")
print(f"T2  k=0 reflected branch fires at EVERY node   {'MET' if t2 else 'MISSED'}")
print(f"T3  folded lattice has a coincidence at every node (predicate vacuous)   "
      f"{'MET' if t3 else 'MISSED'}")
print(f"T4  ladder ORDER eps-invariant ({all(orders)}) while thresholds MOVE ({moved})   "
      f"{'MET' if t4 else 'MISSED'}")

verdict = ("SCOPE_IS_DIRECT_CHANNEL" if (t2 and t3) else "FOLD_HARMLESS")
print(f"\nVERDICT: {verdict}")
if verdict == "SCOPE_IS_DIRECT_CHANNEL":
    print("  The theorem is about the DIRECT (unfolded) coincidence channel and the")
    print("  document must say so. The reflected k=0 branch fires for EVERY alpha,")
    print("  rational or not, so a predicate over folded values would be vacuous --")
    print("  it carries no ratio-dependent information and cannot distinguish ratios.")

with redpath("index cells with both channels measured", expect_min=len(INDICES)) as rp:
    rp.observed(len(rows))

json.dump(dict(indices=INDICES, epsilons=EPSILONS, qmax=QMAX,
               channel_rows={str(k): v for k, v in rows.items()},
               ladder_by_epsilon=ladder, ladder_order_preserved=orders,
               ladder_thresholds_moved=bool(moved),
               predictions=dict(T1=bool(t1), T2=bool(t2), T3=bool(t3), T4=bool(t4)),
               verdict=verdict),
          open(f"{HERE}/brocot_theorem_scope.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_theorem_scope.json")
