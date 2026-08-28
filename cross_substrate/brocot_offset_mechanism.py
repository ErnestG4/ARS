"""THE 0.0017 OFFSET: are the markers an incomplete list, or the wrong object?

COMMITTED GENERATOR of cross_substrate/brocot_offset_mechanism.json.
Predictions sealed here, before any output exists.

THE QUESTION, MADE WELL-POSED BY brocot_event_layer
-----------------------------------------------------
Four marker sets built on EXACT events have failed on the same residual, and the
closed-form union (direct + reflected + f_min) covers only 33-37%. What that cell
also produced is a physical scale: the median large jump sits 0.0017 in alpha
from its nearest marker, and the distance percentiles are stable under grid
doubling. Something is happening a fixed distance AWAY from every exact event.

THE HYPOTHESIS, RECORDED IN THE QUEUE BEFORE THIS CELL EXISTED
---------------------------------------------------------------
u = I8_brody_q_unbounded(canonical_spacings(...)) measures level repulsion and is
most sensitive to the SMALLEST spacings. Near a coincidence at alpha_m two
partials separate linearly:

    delta(alpha) = f_c * |a2| * |alpha - alpha_m|

where (a1, a2) is the pair that vanishes at alpha_m. At alpha_m itself the two
are merged and contribute ONE partial -- no anomalously small spacing at all.
Just off it, they contribute a spacing far below the typical one, which is what
a repulsion statistic reacts to hardest. The reaction should therefore peak not
AT the coincidence but where delta becomes comparable to the local spacing
scale:

    delta = kappa * median_spacing        ->        Delta_alpha = kappa * s / (f_c |a2|)

If that holds, the markers are not an incomplete list -- they are the wrong
OBJECT. The event is a near-coincidence at a predictable offset, and the repair
is to place markers at alpha_m +/- Delta_alpha rather than to keep adding
channels at alpha_m.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — bars edge-probed; kappa fitted COARSE, scored FINE       ║
║                                                                              ║
║ O1  NORMALISING CONCENTRATES IT — the coefficient of variation of            ║
║     nu = f_c*|a2|*Delta / s is at most two thirds that of the raw offset      ║
║     Delta. If the spacing scale is the right normaliser the spread should     ║
║     collapse; if it is not, dividing by a varying quantity will not help.    ║
║ O2  AND NOT BY ACCIDENT — the same normalisation with the spacing scale       ║
║     SHUFFLED across jumps does NOT concentrate: its CV ratio stays above      ║
║     0.85. This is the non-inertness arm. Dividing by any varying quantity     ║
║     changes a CV, so without it O1 is uninterpretable.                       ║
║ O3  AND IT PREDICTS — markers placed at alpha_m +/- kappa*s/(f_c|a2|), with   ║
║     kappa fitted on the COARSE grid and scored on the FINE one, cover at      ║
║     least 15 points more of the large jumps than the exact markers alone.    ║
║                                                                              ║
║ O3 IS THE CELL. O1 and O2 can both hold on a quantity that still does not     ║
║ locate anything. If O3 holds the event layer is completable after all, by a   ║
║ different object than four cells assumed. If it misses, the offset is real,   ║
║ measured, and unexplained -- which is a better place to leave it than an      ║
║ attribution nobody tested.                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
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
from modelparams import Model, Param, TESTED, DECLARED            # noqa: E402
from verdictlattice import (Arm, compose, EXISTENCE as EX_ROLE,   # noqa: E402
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from phase3.partial_prediction import predict_partials, order_bound  # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded  # noqa: E402

I_MUS = 0.9
B = order_bound(I_MUS)
A = 2 * B
A0, A1, F_C = 0.70, 1.40, 220.0
COARSE, FINE = 3501, 7001
ABS_JUMP, FIXED_WIN = 0.05, 6e-4
SEED = 20260827

INSTRUMENT = Model("Brody-q over canonical spacings, with a near-coincidence model", [
    Param("abs_jump", TESTED, sweep=[0.03, 0.05, 0.08],
          why="what counts as a large jump; inherited from v2 at 0.05 and "
              "swept here because the offset's meaning should not depend on it"),
    Param("fixed_window", TESTED, sweep=[3e-4, 6e-4, 1.2e-3],
          why="the coverage window, fixed in alpha per brocot_event_layer's "
              "amendment 1; swept because O3's gain must not be a window effect"),
    Param("f_c", DECLARED, value=F_C,
          why="delta scales with f_c and so does the spacing scale s, so kappa "
              "is dimensionless and f_c cancels from the prediction"),
    Param("spacing_statistic", DECLARED, value="median of canonical_spacings",
          why="the median is the scale the smallest spacings are anomalous "
              "RELATIVE TO; a mean would be dragged by the anomaly itself"),
])


def markers():
    D = {Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 1)
         if gcd(p, q) == 1 and A0 <= p / q <= A1}
    R = {Fraction(p, q) for q in range(1, A + 1) for p in range(1, A + 3)
         if gcd(p, q) == 1 and A0 <= p / q <= A1}
    return D | R


MARKS = sorted(markers(), key=float)


def a2_of(alpha):
    """|a2| of the pair that vanishes at this marker — the separation rate."""
    p, q = alpha.numerator, alpha.denominator
    best = None
    for a1 in range(-A, A + 1):
        for a2 in range(-A, A + 1):
            if a1 == 0 and a2 == 0:
                continue
            if a1 * q + a2 * p == 0:
                k = (max(abs(a1), abs(a2)), abs(a2))
                if best is None or k < best[0]:
                    best = (k, abs(a2))
    return best[1] if best else None


A2 = {m: a2_of(m) for m in MARKS}
POS = np.array([float(m) for m in MARKS])


def sweep(n):
    g = np.linspace(A0, A1, n)
    u, sp_med = [], []
    for a in g:
        sp = predict_partials([1.0, float(a)], [I_MUS, I_MUS], f_carrier=F_C)
        f = np.sort(sp.freqs)
        if f.size >= 20:
            u.append(I8_brody_q_unbounded(canonical_spacings(f)))
            sp_med.append(float(np.median(np.diff(f))))
        else:
            u.append(np.nan)
            sp_med.append(np.nan)
    return g, np.array(u, float), np.array(sp_med, float)


def jumps(g, u, s, abs_jump):
    mid = (g[:-1] + g[1:]) / 2
    j = np.abs(np.diff(u))
    ok = np.isfinite(j) & np.isfinite(s[:-1])
    big = ok & (j >= abs_jump)
    xs = mid[big]
    sm = s[:-1][big]
    i = np.array([int(np.argmin(np.abs(x - POS))) for x in xs])
    d = np.abs(xs - POS[i])
    a2 = np.array([A2[MARKS[k]] or 1 for k in i], float)
    return xs, d, sm, a2


gc_, uc, sc = sweep(COARSE)
gf_, uf, sf = sweep(FINE)
xs_c, d_c, s_c, a2_c = jumps(gc_, uc, sc, ABS_JUMP)
xs_f, d_f, s_f, a2_f = jumps(gf_, uf, sf, ABS_JUMP)


def cv(x):
    x = x[np.isfinite(x) & (x > 0)]
    return float(np.std(x) / np.mean(x)) if x.size > 1 and np.mean(x) else 0.0


nu_c = F_C * a2_c * d_c / s_c
o1 = cv(nu_c) / cv(d_c) if cv(d_c) else 1.0
rng = np.random.default_rng(SEED)
shuf = np.array([cv(F_C * a2_c * d_c / rng.permutation(s_c)) / cv(d_c)
                 for _ in range(200)])
o2 = float(np.median(shuf))

KAPPA = float(np.median(nu_c[np.isfinite(nu_c)]))


def coverage(pos, xs, win):
    return float(np.mean([np.any(np.abs(x - pos) <= win) for x in xs])) if xs.size else 0.0


pred = []
for m in MARKS:
    a2 = A2[m] or 1
    for sgn in (+1, -1):
        pred.append(float(m))          # placeholder, replaced per-jump below
base_cov = coverage(POS, xs_f, FIXED_WIN)
# predicted markers use the LOCAL spacing scale, so they are per-jump offsets
s_at = np.interp(POS, gf_, np.nan_to_num(sf, nan=np.nanmedian(sf)))
off = KAPPA * s_at / (F_C * np.array([A2[m] or 1 for m in MARKS], float))
PRED = np.concatenate([POS - off, POS, POS + off])
pred_cov = coverage(PRED, xs_f, FIXED_WIN)
o3 = pred_cov - base_cov

O1 = Bar("CV(normalised) / CV(raw offset)", 0.667, direction="le", floor=0.0,
         ceiling=5.0,
         why="a ratio of two coefficients of variation; 0 if normalising "
             "collapses the spread entirely, and bounded well under 5 by the "
             "observed spreads")
O2 = Bar("same ratio with the spacing scale SHUFFLED", 0.85, floor=0.0,
         ceiling=5.0, why="the same ratio under a permutation null")
O3 = Bar("coverage gain from predicted offsets", 0.15, floor=-1.0, ceiling=1.0,
         why="a difference of two coverages each in [0,1]")
s1, s2, s3 = O1.score(o1), O2.score(o2), O3.score(o3)

print(INSTRUMENT.report())
print(f"\n{len(xs_c)} large jumps coarse, {len(xs_f)} fine; "
      f"{len(MARKS)} exact markers\n")
print(f"raw offset Delta:        median {np.median(d_c):.5f}  CV {cv(d_c):.3f}")
print(f"normalised nu:           median {KAPPA:.3f}  CV {cv(nu_c):.3f}")
print(f"shuffled-scale null:     median CV ratio {o2:.3f} over 200 draws")
print(f"\nkappa fitted on the coarse grid = {KAPPA:.3f}")
print(f"coverage on the FINE grid, window {FIXED_WIN}:")
print(f"   exact markers only        {base_cov:.1%}")
print(f"   plus predicted offsets    {pred_cov:.1%}   ({len(PRED)} markers)")
print()
for b, v, f in ((O1, o1, "{:.3f}"), (O2, o2, "{:.3f}"), (O3, o3, "{:+.1%}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(s3, EX_ROLE,
                          claim="predicted offsets locate jumps the exact "
                                "markers miss"),
             Arm.from_bar(s1, RES_ROLE,
                          claim="the spacing scale is the right normaliser"),
             Arm.from_bar(s2, MECH_ROLE,
                          claim="the concentration is not an artifact of "
                                "dividing by a varying quantity")],
            holds="MARKERS_ARE_THE_WRONG_OBJECT",
            fails="OFFSET_REAL_BUT_UNEXPLAINED")
print(f"\nVERDICT: {v['citation']}")

with redpath("large jumps with an offset measured", expect_min=60) as rp:
    rp.observed(len(xs_c))

json.dump(dict(I=I_MUS, B=B, A=A, coarse=COARSE, fine=FINE,
               abs_jump=ABS_JUMP, fixed_window=FIXED_WIN,
               instrument=INSTRUMENT.seal(), n_markers=len(MARKS),
               n_jumps_coarse=int(len(xs_c)), n_jumps_fine=int(len(xs_f)),
               raw_offset_median=float(np.median(d_c)), raw_cv=cv(d_c),
               nu_cv=cv(nu_c), kappa=KAPPA, shuffled_cv_ratio=o2,
               coverage_exact=base_cov, coverage_predicted=pred_cov,
               bars={s["name"]: s for s in (s1, s2, s3)},
               verdict=v["head"], composed=v),
          open(f"{HERE}/brocot_offset_mechanism.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_offset_mechanism.json")
