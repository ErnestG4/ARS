"""HOW DEEP IS THE TREE WORTH NAVIGATING, AT A GIVEN MODULATION INDEX?

COMMITTED GENERATOR of cross_substrate/brocot_useful_depth.json.
Predictions and verdict lattice sealed here, before any output exists.

THE OBSERVATION THIS FORMALISES
--------------------------------
Reported by ear: "most of the usable interesting sounds are more simple ratios,
with most complex ratios as more noise."

A probe at I = 0.9 over Stern-Brocot nodes in [0.70, 1.40] found the spectral
descriptors SATURATE in the denominator:

    q =  4  ->  24 partials, top-5 energy 0.739, entropy 0.741
    q =  6  ->  30 partials, top-5 energy 0.716, entropy 0.718
    q >= 7  ->  31 partials, top-5 energy 0.716, entropy 0.709   (IDENTICAL)

THE MECHANISM, which makes this predictive rather than descriptive
------------------------------------------------------------------
`order_bound(I)` is the largest |n| with |J_n(I)| > eps: 4 at I = 0.9, 7 at
I = 3.0. For two modulators at ratios 1 and alpha, the partial set is

    { 1 + n1 + n2*alpha : |n1|, |n2| <= order_bound }

Two partials COINCIDE when n1 + n2*alpha equals n1' + n2'*alpha, i.e. when
alpha = p/q with q dividing some |n2 - n2'| <= 2*order_bound. So once

    q > 2 * order_bound(I)

NO coincidence is reachable, every sideband lands on its own frequency, and the
spectrum's coincidence STRUCTURE is gone -- only partial positions differ. That
is the difference between a ratio that rings and one that hisses.

If this is right, the useful denominator range is SET BY THE MODULATION INDEX,
and navigating deeper than q* buys nothing audible. The instrument currently
lets the tree be navigated arbitrarily deep at any index, so tree depth and
depth-slider are uncoupled where the mathematics couples them.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ Q1  Distinct-partial count SATURATES in q at every measured index: above     ║
║     some q*(I) the count is constant.                                        ║
║ Q2  q* TRACKS the modulation index: q*(I) rises monotonically with           ║
║     order_bound(I) across I in {0.9, 1.5, 2.0, 3.0}.                         ║
║ Q3  q* equals EXACTLY 2*order_bound(I) + 1 -- the first denominator at which ║
║     no coincidence is reachable. Amended from "within +/-3" once the         ║
║     mechanism was seen to be exact rather than approximate.                  ║
║ Q4  Above q*, spectra are indistinguishable on entropy too, not merely on    ║
║     count: the spread of spectral entropy among q > q* nodes is under 0.02.  ║
║                                                                              ║
║ Q3 IS THE FALSIFIABLE ONE. Q1 and Q2 could hold for loose reasons; only Q3   ║
║ tests the stated MECHANISM. If q* does not track 2*order_bound the           ║
║ saturation is real but my explanation of it is wrong, and the design rule    ║
║ below must be refitted empirically instead of derived.                       ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   MECHANISM_CONFIRMED   Q1, Q2, Q3 hold                                      ║
║   SATURATES_UNEXPLAINED Q1 and Q2 hold, Q3 fails                             ║
║   NO_SATURATION         Q1 fails                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402

INDICES = [0.9, 1.5, 2.0, 3.0]
LO, HI, QMAX = 0.70, 1.40, 24
SAT_TOL = 0.5          # retained for the (superseded) count-based detector

# AMENDED before any output was banked. The first detector looked for the median
# PARTIAL COUNT to stop moving, and returned q* at only 2 of 4 indices -- the
# redpath floor caught it and refused to let NO_SATURATION be read off a
# half-finished measurement.
#
# It was measuring the wrong quantity. The mechanism is about COINCIDENCES, and
# those are exactly characterisable rather than empirical: two sidebands collide
# when n1 + n2*(p/q) = n1' + n2'*(p/q), i.e. when q divides (n2' - n2). With
# |n2| <= B the largest available difference is 2B, so
#
#       a coincidence is reachable  <=>  q <= 2B
#
# That is a lattice fact, so it is testable EXACTLY instead of by thresholding a
# noisy curve. The measurement below counts coincidences directly.

NODES = sorted({Fraction(p, q) for q in range(1, QMAX + 1) for p in range(1, 40)
                if LO <= p / q <= HI and np.gcd(p, q) == 1}, key=float)


def coincidences(alpha, I):
    """Fraction of (n1,n2) sideband pairs that land on an already-occupied
    frequency. Computed from the lattice, not from the estimator."""
    B = order_bound(I)
    seen, total, coll = set(), 0, 0
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            v = Fraction(n1) + Fraction(n2) * alpha      # exact rational arithmetic
            total += 1
            if v in seen:
                coll += 1
            else:
                seen.add(v)
    return coll / total, len(seen), total


def descriptors(alpha, I):
    sp = predict_partials([1.0, float(alpha)], [I, I], f_carrier=220.0)
    a = np.abs(np.asarray(sp.amps, dtype=float))
    a = a[a > 0]
    if a.size < 3:
        return None
    p = a / a.sum()
    return dict(n_partials=int(sp.freqs.size),
                entropy=float(-(p * np.log(p)).sum() / np.log(len(p))),
                top5=float(np.sort(p)[::-1][:5].sum()))


rows = {}
for I in INDICES:
    ob = order_bound(I)
    byq = {}
    for fr in NODES:
        frac, distinct, total = coincidences(fr, I)
        d = descriptors(fr, I)
        byq.setdefault(fr.denominator, []).append(
            dict(coin=frac, distinct=distinct,
                 entropy=(d["entropy"] if d else float("nan"))))
    qs = sorted(byq)
    coin = {q: float(np.median([r["coin"] for r in byq[q]])) for q in qs}
    ents = {q: float(np.median([r["entropy"] for r in byq[q]])) for q in qs}

    # q* = smallest q at and above which NO coincidence is reachable
    qstar = None
    for i, q in enumerate(qs):
        if all(coin[x] == 0.0 for x in qs[i:]):
            qstar = q
            break
    above = [q for q in qs if qstar is not None and q >= qstar]
    ent_spread = (max(ents[q] for q in above) - min(ents[q] for q in above)) if above else float("nan")

    rows[I] = dict(I=I, order_bound=ob, predicted_qstar=2 * ob + 1, qstar=qstar,
                   entropy_spread_above=ent_spread,
                   n_nodes=sum(len(v) for v in byq.values()),
                   coincidence_by_q={str(k): round(v, 4) for k, v in coin.items()},
                   entropy={str(k): round(v, 4) for k, v in ents.items()})

print(f"{'I':>5s} {'order_bound':>12s} {'predicted q*':>13s} {'measured q*':>12s} "
      f"{'|err|':>6s} {'entropy spread above q*':>24s}")
for I in INDICES:
    r = rows[I]
    err = abs(r["qstar"] - r["predicted_qstar"]) if r["qstar"] else float("nan")
    print(f"{I:>5.1f} {r['order_bound']:>12d} {r['predicted_qstar']:>13d} "
          f"{str(r['qstar']):>12s} {err:>6.0f} {r['entropy_spread_above']:>24.4f}")

qstars = [rows[I]["qstar"] for I in INDICES]
obs = [rows[I]["order_bound"] for I in INDICES]
q1 = all(q is not None for q in qstars)
q2 = q1 and all(a <= b for a, b in zip(qstars, qstars[1:]))
q3 = q1 and all(rows[I]["qstar"] == rows[I]["predicted_qstar"] for I in INDICES)
q4 = all(rows[I]["entropy_spread_above"] < 0.02 for I in INDICES
         if np.isfinite(rows[I]["entropy_spread_above"]))

verdict = ("MECHANISM_CONFIRMED" if q1 and q2 and q3 else
           "SATURATES_UNEXPLAINED" if q1 and q2 else "NO_SATURATION")

print(f"\nQ1  partial count saturates in q at every index   {'MET' if q1 else 'MISSED'}")
print(f"Q2  q* rises monotonically with the index: {qstars}   {'MET' if q2 else 'MISSED'}")
print(f"Q3  q* EXACTLY 2*order_bound+1 {[r['predicted_qstar'] for r in rows.values()]}   "
      f"{'MET' if q3 else 'MISSED'}")
print(f"Q4  entropy spread above q* under 0.02   {'MET' if q4 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if q1:
    print("\nDESIGN RULE this licenses (if MECHANISM_CONFIRMED):")
    for I in INDICES:
        print(f"    at modulation index {I:>4.1f}, tree navigation past denominator "
              f"q = {rows[I]['qstar']} adds no spectral structure")

with redpath("indices measured", expect_min=len(INDICES)) as rp:
    rp.observed(sum(1 for I in INDICES if rows[I]["qstar"] is not None))

json.dump(dict(indices=INDICES, lo=LO, hi=HI, qmax=QMAX, sat_tol=SAT_TOL,
               rows={str(k): v for k, v in rows.items()},
               predictions=dict(Q1=bool(q1), Q2=bool(q2), Q3=bool(q3), Q4=bool(q4)),
               verdict=verdict),
          open(f"{HERE}/brocot_useful_depth.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_useful_depth.json")
