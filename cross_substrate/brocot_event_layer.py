"""THE EVENT LAYER: is the residual 70% really beyond closed form?

COMMITTED GENERATOR of cross_substrate/brocot_event_layer.json.
Predictions sealed here, before any output exists.

THE PREMISE UNDER TEST, WHICH IS THIS ARC'S OWN
-------------------------------------------------
Four marker sets have failed on the same residual: v1's coincidence events at
55%, v2's count-changes at 37.7% held out, v3's parent boundaries at 0.0%, and
the horizon-node reference at 30.4%. Every writeup since has said the remainder
are "amplitude-threshold crossings, where a partial crosses the -50 dB floor at
ratios no Farey enumeration knows about", and MAP-FIELD.md ships that sentence.

That sentence is an ATTRIBUTION, not a measurement, and standing obligation 7
says verify the premise before executing on it. Reading what
`predict_partials` actually does:

    threshold_db = -50, RELATIVE to the loudest non-carrier partial
    f_min = 20 Hz, f_max = 20000 Hz
    amplitudes are J_n1(I)*J_n2(I) -- INDEPENDENT of alpha

The last line is the crux. A partial's amplitude does not depend on alpha at
all, so nothing crosses an absolute amplitude floor as alpha sweeps. The count
can only change when:

  DIRECT      two partials merge; amplitudes sum. Farey: max(p,q) <= 2B.
  REFLECTED   two partials meet after folding through DC. Already characterised
              in brocot_theorem_scope: the m != 0 solutions satisfy q <= 2B and
              p <= 2B + 2. ALSO FAREY, and never included in a marker set.
  FLOOR       a partial crosses f_min: |1 + n1 + n2*alpha| = 20/f_c = 1/11.
              Closed form: alpha = (+/-1/11 - 1 - n1)/n2, enumerable exactly.
  REFERENCE   a merge changes the loudest non-carrier partial, moving the -50 dB
              reference and pushing others across it. SECONDARY -- caused by the
              first two, at the same alpha.

f_max never binds: with |n| <= B = 4 and alpha <= 1.4 the largest |nu| is 10.6,
far under 90.9.

So the residual may be fully enumerable, and "no Farey enumeration knows about
them" may simply be false -- an attribution that has been repeated through four
cells and into a shipped document without anyone testing it.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed                                        ║
║                                                                              ║
║ V1  THE UNION COVERS THE RESIDUAL — direct + reflected + floor markers cover  ║
║     at least 60% of large jumps, against the direct set's 30.4%.             ║
║ V2  THE REFLECTED CLASS EARNS ITS PLACE — adding reflected to direct raises   ║
║     coverage by at least 10 points on its own. If it misses, the fold is a    ║
║     real channel that happens not to move this statistic, which is worth      ║
║     knowing and is a different sentence from the one shipped.                ║
║ V3  IT IS NOT CARPET-BOMBING — the union's marker density is at most 4x the   ║
║     direct set's. Coverage bought by marking everything is not a layer.      ║
║ V4  OUT OF SAMPLE — markers derived analytically (no grid anywhere in their   ║
║     construction) score at least 0.8x as well on a 2x finer grid. v2's        ║
║     discipline, and the reason its detected markers were untrustworthy.      ║
║                                                                              ║
║ V1 IS THE ONE THAT DECIDES WHAT THE DOCUMENT SAYS. If it holds, the shipped   ║
║ sentence is wrong and the event layer is completable in closed form. If it    ║
║ misses, the attribution survives a real attempt to break it and becomes a     ║
║ measurement rather than a guess.                                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

AMENDMENT 1 — V4's MISS IS AN ARTIFACT OF THE WINDOW, AND THE WINDOW WAS
INHERITED FROM A FIX FOR ITS MIRROR.

v2 found a commensurability defect -- a FIXED delta of 0.005 spanning 10 coarse
steps but 25 fine ones -- and fixed it by scaling delta with the grid. This cell
inherited that unchanged. But a grid-scaled window SHRINKS when the grid
refines, so if a jump sits at a fixed offset in alpha from its marker, doubling
the grid halves the window and the jump falls out. That is what happened:
coverage went 23/69 to 9/81 while the markers did not move.

Which window is right depends on whether the jump-to-marker offset is a GRID
quantity or a PHYSICAL one, and that is testable rather than arguable. Measured
distances from each large jump to its nearest marker, in alpha:

    grid 3501   p10 0.00030  p25 0.00050  p50 0.00170  p75 0.00350  p90 0.01030
    grid 7001   p10 0.00025  p25 0.00042  p50 0.00118  p75 0.00422  p90 0.01245

Stable across a doubling. The offset is PHYSICAL, so the window must be fixed in
alpha, and under a fixed 0.0006 window coverage is 33.3% coarse and 37.0% fine --
stable, and V4 holds. The sealed V4 is reported MISSED as it fell, with the
corrected measurement beside it, because the arm tested the marker set through
an instrument that was wrong for this quantity.

Both fixes are the same lesson from opposite sides: a window's scaling must match
the scaling of the thing it is windowing. v2 got caught by a fixed window on a
grid-borne quantity; this cell by a grid-scaled window on a physical one.

AMENDMENT 2 — A THRESHOLD STATISTIC WAS HIDING A DISTRIBUTION. Four marker sets
returned coverage 33.3% to the digit, which is not a result but a smell: a
binary near/far count cannot show that the union's extra 16 markers help only
the far tail (p75 0.00343 vs 0.00350, p90 0.00790 vs 0.01030) while leaving the
median untouched. The distance distribution is now the reported quantity and
coverage is a derived summary of it.

V1 AND V2 MISS FOR REAL, and that is the cell's finding. The residual is NOT
closed-form enumerable by direct, reflected and floor markers together: the
median large jump sits 0.0017 in alpha from the nearest one, about eight coarse
grid steps. The shipped attribution survives a genuine attempt to break it, which
is what the seal said a miss would mean -- it is now a measurement rather than a
guess, and MAP-FIELD.md may keep its sentence with a citation instead of a
shrug.
"""
import json
import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                       # noqa: E402
from reachable import Bar                                         # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
A0, A1 = 0.70, 1.40
COARSE, FINE = 3501, 7001
DELTA_STEPS, ABS_JUMP = 3, 0.05          # inherited from v2/v3 unchanged
F_C, F_MIN = 220.0, 20.0


def direct_markers():
    """max(p,q) <= 2B — v1's set, the below-horizon nodes."""
    return {Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
            if gcd(p, q) == 1 and A0 <= p / q <= A1}


def reflected_markers():
    """The fold's m != 0 class: q <= 2B and p <= 2B + 2."""
    return {Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 3)
            if gcd(p, q) == 1 and A0 <= p / q <= A1}


def floor_markers():
    """alpha where a partial crosses f_min: |1 + n1 + n2*alpha| = f_min/f_c."""
    t = Fraction(int(F_MIN), int(F_C))
    out = set()
    for n1 in range(-B, B + 1):
        for n2 in range(-B, B + 1):
            if n2 == 0:
                continue
            for s in (t, -t):
                a = Fraction(s - 1 - n1, n2)
                if A0 <= a <= A1:
                    out.add(a)
    return out


DIRECT, REFL, FLOOR = direct_markers(), reflected_markers(), floor_markers()
UNION = DIRECT | REFL | FLOOR


def sweep(n):
    g = np.linspace(A0, A1, n)
    u = []
    for a in g:
        sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=F_C)
        u.append(I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
                 if sp.freqs.size >= 20 else np.nan)
    return g, np.array(u, float)


FIXED_WIN = 6e-4          # amendment 1: fixed in alpha, not in grid steps


def distances(marks, g, u):
    """Distance in alpha from each large jump to its nearest marker."""
    mid = (g[:-1] + g[1:]) / 2
    j = np.abs(np.diff(u))
    ok = np.isfinite(j)
    big = ok & (j >= ABS_JUMP)
    pos = np.array(sorted(float(m) for m in marks))
    xs = mid[big]
    d = np.array([np.min(np.abs(x - pos)) for x in xs]) if xs.size else np.array([])
    return d, int(big.sum())


def score(marks, g, u):
    mid = (g[:-1] + g[1:]) / 2
    j = np.abs(np.diff(u))
    ok = np.isfinite(j)
    d = (A1 - A0) / (len(g) - 1)
    pos = np.array(sorted(float(m) for m in marks))
    near = np.array([np.any(np.abs(x - pos) <= DELTA_STEPS * d) for x in mid])
    big = ok & (j >= ABS_JUMP)
    cov = float(near[big].mean()) if big.any() else 0.0
    m_near = float(np.median(j[ok & near])) if (ok & near).any() else 0.0
    m_far = float(np.median(j[ok & ~near])) if (ok & ~near).any() else 0.0
    dd, nb = distances(marks, g, u)
    fixed = float(np.mean(dd <= FIXED_WIN)) if dd.size else 0.0
    pct = (np.percentile(dd, [10, 25, 50, 75, 90]).tolist() if dd.size
           else [0.0] * 5)
    return dict(coverage=cov, coverage_fixed_window=fixed, n_big=int(big.sum()),
                dist_pctiles=pct,
                contrast=(m_near / m_far if m_far > 0 else float("inf")))


gc_, uc = sweep(COARSE)
gf_, uf = sweep(FINE)
S = {name: score(m, gc_, uc) for name, m in
     (("direct", DIRECT), ("direct+refl", DIRECT | REFL),
      ("direct+floor", DIRECT | FLOOR), ("union", UNION))}
Sf = {name: score(m, gf_, uf) for name, m in
      (("direct", DIRECT), ("union", UNION))}

v1v = S["union"]["coverage"]
v2v = S["direct+refl"]["coverage"] - S["direct"]["coverage"]
v3v = len(UNION) / len(DIRECT)
v4v = Sf["union"]["coverage"] / S["union"]["coverage"] if S["union"]["coverage"] else 0.0
# amendment 1: the same arm through a window fixed in alpha rather than in steps
v4_fixed = (Sf["union"]["coverage_fixed_window"] / S["union"]["coverage_fixed_window"]
            if S["union"]["coverage_fixed_window"] else 0.0)

V1 = Bar("union coverage of large jumps", 0.60, floor=0.0, ceiling=1.0,
         why="a fraction of large-jump steps: 0 to 1")
V2 = Bar("coverage gain from the reflected class", 0.10, floor=-1.0,
         ceiling=1.0, why="a difference of two coverages each in [0,1]")
V3 = Bar("union markers / direct markers", 4.0, direction="le", floor=1.0,
         ceiling=float(len(UNION)),
         why="the union contains the direct set, so the ratio is at least 1 "
             f"and at most |union| = {len(UNION)} when direct has one member")
V4 = Bar("fine-grid coverage / coarse-grid coverage", 0.80, floor=0.0,
         ceiling=2.0,
         why="a ratio of two coverages each in [0,1]; bounded by 2 in practice "
             "since a doubled grid cannot double a fraction already near 1")
s1, s2, s3, s4 = V1.score(v1v), V2.score(v2v), V3.score(v3v), V4.score(v4v)

print(f"I = {I_MUS}, B = {B}, 2B = {A}, alpha in [{A0}, {A1}]")
print(f"marker classes:  direct {len(DIRECT)}   reflected {len(REFL)}   "
      f"floor {len(FLOOR)}   union {len(UNION)}\n")
print(f"{'marker set':>14s} {'markers':>8s} {'coverage':>9s} {'contrast':>9s}")
for name, m in (("direct", DIRECT), ("direct+refl", DIRECT | REFL),
                ("direct+floor", DIRECT | FLOOR), ("union", UNION)):
    print(f"{name:>14s} {len(m):>8d} {S[name]['coverage']:>8.1%} "
          f"{S[name]['contrast']:>9.2f}")
print(f"\ndistance from each large jump to its nearest marker (alpha):")
print(f"{'set':>14s} {'grid':>6s} {'p10':>8s} {'p25':>8s} {'p50':>8s} "
      f"{'p75':>8s} {'p90':>8s}")
for lab, T in (("direct", S), ("union", S)):
    q = T[lab]["dist_pctiles"]
    print(f"{lab:>14s} {COARSE:>6d} " + "".join(f"{x:>8.5f}" for x in q))
for lab in ("direct", "union"):
    q = Sf[lab]["dist_pctiles"]
    print(f"{lab:>14s} {FINE:>6d} " + "".join(f"{x:>8.5f}" for x in q))
print(f"\nlarge jumps on the coarse grid: {S['direct']['n_big']}")
print(f"out of sample, GRID-SCALED window (as sealed): "
      f"union {S['union']['coverage']:.1%} -> {Sf['union']['coverage']:.1%}  "
      f"ratio {v4v:.2f}")
print(f"out of sample, FIXED {FIXED_WIN} window (amendment 1): "
      f"union {S['union']['coverage_fixed_window']:.1%} -> "
      f"{Sf['union']['coverage_fixed_window']:.1%}  ratio {v4_fixed:.2f}")
print(f"\nfloor markers (|1 + n1 + n2a| = {F_MIN:.0f}/{F_C:.0f}): "
      f"{sorted(str(x) for x in FLOOR)[:6]} ...")
print()
for b, v, f in ((V1, v1v, "{:.1%}"), (V2, v2v, "{:+.1%}"),
                (V3, v3v, "{:.2f}"), (V4, v4v, "{:.2f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s1, EX_ROLE,
                          claim="the residual IS closed-form enumerable, so "
                                "the shipped attribution is wrong"),
             Arm.from_bar(s2, MECH_ROLE,
                          claim="the reflected channel is what was missing"),
             Arm.from_bar(s3, RES_ROLE, claim="not bought by marking everything"),
             Arm.from_bar(s4, RES_ROLE, claim="holds out of sample")],
            holds="EVENT_LAYER_IS_CLOSED_FORM",
            fails="RESIDUAL_SURVIVES_CLOSED_FORM")
print(f"\nVERDICT: {v['citation']}")

with redpath("large jumps scored", expect_min=50) as rp:
    rp.observed(S["direct"]["n_big"])

json.dump(dict(I=I_MUS, B=B, A=A, a0=A0, a1=A1, coarse=COARSE, fine=FINE,
               delta_steps=DELTA_STEPS, abs_jump=ABS_JUMP,
               n_direct=len(DIRECT), n_reflected=len(REFL), n_floor=len(FLOOR),
               n_union=len(UNION),
               coarse_scores=S, fine_scores=Sf,
               fixed_window=FIXED_WIN, v4_fixed_window_ratio=v4_fixed,
               floor_markers=sorted(str(x) for x in FLOOR),
               bars={s["name"]: s for s in (s1, s2, s3, s4)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_event_layer.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_event_layer.json")
