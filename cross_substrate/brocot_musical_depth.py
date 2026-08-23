"""DOES THE SATURATION HOLD IN THE REGIME THE SYNTHESIZER ACTUALLY INHABITS?

COMMITTED GENERATOR of cross_substrate/brocot_musical_depth.json.
Predictions and verdict lattice sealed here, before any output exists.

THE CORRECTION THIS RUN EXISTS FOR
-----------------------------------
`predict_partials(ratios, depths, ...)` takes MODULATION INDICES, one per
modulator — `depths` is not a tree depth. Every brocot ARS measurement in this
programme passed `[8.0, 8.0]`, inherited from `brocot_perAlpha.json`, and last
night's "depth sweep" swept {4, 6, 8, 10, 12, 14} around it and reported
DEPTH_INVARIANT.

BROCOT-SPEC.md §1, on the instrument's defining regime:

    "Modulation indices are LOW — around half the first Bessel peak, so I ~ 0.9
     typically, with the meaningful range being 0.1 to 3.0 rather than the DX7's
     0.5 to 8.0."
    "the depth slider's perceptually useful range is 0 to ~3, not 0 to 8"

So EVERY point swept last night sits at or above the top of the instrument's
useful range, and the lowest (4) is above it. The sweep spanned a knob; it did
not span the knob's musical interval. It was anchored on the inherited value
instead of on the range the instrument operates in — which is the same
inherited-knob defect the sweep was written to cure, one level out.

DEPTH_INVARIANT across I = 4..14 remains true as measured. What it does not
license is any statement about I ~ 0.9, and that is the only regime a Brocot
patch actually occupies.

MEASURABILITY IS PART OF THE ANSWER
------------------------------------
Measured before sealing this: the analysis needs >= 20 partials for the spacing
statistic, and

    I = 0.1  ->  median 10 partials,   0 of 255 alpha qualify
    I = 0.5  ->  median 20 partials, 200 of 255 qualify
    I = 0.9  ->  median 31 partials, 255 of 255
    I = 3.0  ->  median 92 partials, 255 of 255

I = 0.1 is therefore NOT MEASURABLE by this instrument, and I = 0.5 admits a
55-alpha SELECTION EFFECT — the alphas that drop out are not a random 55. Both
are recorded as such rather than run and quietly reported.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ M1  The saturation HOLDS at the musical indices {0.9, 1.5, 2.0, 3.0}:        ║
║     the slope-difference CI excludes zero at each.                           ║
║ M2  It is WEAKER there than at I = 8: |slope difference| at I = 0.9 is       ║
║     smaller than at I = 8. Thirty-one partials is a noisier spacing sample   ║
║     than three hundred and forty-four.                                       ║
║ M3  The class-level partial rho stays NEGATIVE at every musical index.       ║
║ M4  I = 0.5 is reported SELECTION_BIASED and I = 0.1 NOT_MEASURABLE, never   ║
║     as results.                                                              ║
║                                                                              ║
║ M1 IS THE ONE THAT DECIDES WHETHER ANY OF THIS REACHES THE INSTRUMENT.       ║
║ If the saturation is absent at musical indices, the finding is REAL and      ║
║ SCOPED TO A REGIME BROCOT DOES NOT USE — which is a legitimate result and    ║
║ must be said plainly rather than softened into "holds broadly". Stated here  ║
║ so that outcome cannot be reframed after the fact.                           ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   HOLDS_IN_MUSICAL_REGIME    M1 holds at all four musical indices            ║
║   PARTIAL                    holds at some, named                            ║
║   ABSENT_IN_MUSICAL_REGIME   fails at all four: the finding does not reach   ║
║                              the instrument                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.expandvars("$HOME/fmexplorer/brocot"))
from redpath import redpath                                                 # noqa: E402
from phase3.partial_prediction import predict_partials                      # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q_unbounded   # noqa: E402

SRC = json.load(open(f"{HERE}/brocot_perAlpha.json"))
MUSICAL = [0.9, 1.5, 2.0, 3.0]
DIAGNOSTIC = [0.1, 0.5]
REFERENCE = [8.0]
MIN_PARTIALS, SEED, BOOT = 20, 20260823, 2000


def partial_rho(x, y, z):
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return float(stats.pearsonr(ex, ey)[0])


def measure(I):
    D, U, C, npart, dropped = [], [], [], [], 0
    for r in SRC["rows"]:
        if r.get("D") is None:
            continue
        sp = predict_partials([1.0, r["alpha"]], [I, I], f_carrier=220.0)
        if sp.freqs.size < MIN_PARTIALS:
            dropped += 1
            continue
        u = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
        if u is None:
            dropped += 1
            continue
        D.append(float(r["D"])); U.append(float(u)); C.append(r["cls"])
        npart.append(int(sp.freqs.size))
    n = len(D)
    total = sum(1 for r in SRC["rows"] if r.get("D") is not None)
    if n < 30:
        return dict(I=I, n=n, dropped=dropped, of=total,
                    status="NOT_MEASURABLE",
                    why=f"only {n} of {total} alpha reach {MIN_PARTIALS} partials; "
                        "the spacing statistic has nothing to fit")
    D, U, C = np.array(D), np.array(U), np.array(C)
    status = "MEASURED" if dropped == 0 else "SELECTION_BIASED"

    slope_full = float(np.polyfit(D, U, 1)[0])
    top = D >= np.percentile(D, 200 / 3)
    slope_top = float(np.polyfit(D[top], U[top], 1)[0])

    rng = np.random.default_rng(SEED)
    diffs = []
    for _ in range(BOOT):
        idx = rng.integers(0, n, n)
        d, uu = D[idx], U[idx]
        t = d >= np.percentile(d, 200 / 3)
        if t.sum() < 10 or np.ptp(d[t]) == 0:
            continue
        diffs.append(float(np.polyfit(d[t], uu[t], 1)[0]) - float(np.polyfit(d, uu, 1)[0]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])

    mD, sl, sD = [], [], []
    for c in sorted(set(C)):
        m = C == c
        if m.sum() >= 8 and np.ptp(D[m]) > 0:
            mD.append(D[m].mean()); sl.append(float(np.polyfit(D[m], U[m], 1)[0]))
            sD.append(float(D[m].std(ddof=1)))
    prho = partial_rho(np.array(mD), np.array(sl), np.array(sD)) if len(mD) >= 5 else float("nan")

    return dict(I=I, n=n, dropped=dropped, of=total, status=status,
                median_partials=int(np.median(npart)),
                rho_full=float(stats.spearmanr(D, U)[0]),
                slope_full=slope_full, slope_top=slope_top,
                slope_diff=slope_top - slope_full, ci=[float(lo), float(hi)],
                holds=bool(hi < 0), partial_rho_class=prho, n_classes=len(mD))


rows = [measure(I) for I in DIAGNOSTIC + MUSICAL + REFERENCE]
musical = [r for r in rows if r["I"] in MUSICAL]

print(f"{'I':>5s} {'status':>17s} {'n':>4s} {'drop':>5s} {'parts':>6s} {'rho':>7s} "
      f"{'slope_full':>11s} {'slope_top':>10s} {'diff':>8s} {'95% CI':>18s} {'holds':>6s} {'pRho':>7s}")
for r in rows:
    tag = " (musical)" if r["I"] in MUSICAL else " (ref)" if r["I"] in REFERENCE else " (diag)"
    if r["status"] == "NOT_MEASURABLE":
        print(f"{r['I']:>5.1f} {r['status']:>17s} {r['n']:>4d} {r['dropped']:>5d} "
              f"{'—':>6s} {'—':>7s} {'—':>11s} {'—':>10s} {'—':>8s} {'—':>18s} {'—':>6s} {'—':>7s}{tag}")
        continue
    ci = f"[{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}]"
    print(f"{r['I']:>5.1f} {r['status']:>17s} {r['n']:>4d} {r['dropped']:>5d} "
          f"{r['median_partials']:>6d} {r['rho_full']:>7.3f} {r['slope_full']:>11.3f} "
          f"{r['slope_top']:>10.3f} {r['slope_diff']:>8.3f} {ci:>18s} "
          f"{str(r['holds']):>6s} {r['partial_rho_class']:>7.3f}{tag}")

held = [r["I"] for r in musical if r["holds"]]
failed = [r["I"] for r in musical if not r["holds"]]
ref8 = next(r for r in rows if r["I"] == 8.0)
m09 = next(r for r in musical if r["I"] == 0.9)

m1 = not failed
m2 = abs(m09["slope_diff"]) < abs(ref8["slope_diff"])
m3 = all(r["partial_rho_class"] < 0 for r in musical if np.isfinite(r["partial_rho_class"]))
m4 = (next(r for r in rows if r["I"] == 0.1)["status"] == "NOT_MEASURABLE"
      and next(r for r in rows if r["I"] == 0.5)["status"] == "SELECTION_BIASED")

verdict = ("HOLDS_IN_MUSICAL_REGIME" if m1 else
           "ABSENT_IN_MUSICAL_REGIME" if not held else "PARTIAL")

print(f"\nM1  saturation holds at musical indices {held}; fails at {failed or 'none'}   "
      f"{'MET' if m1 else 'MISSED'}")
print(f"M2  |slope diff| at I=0.9 is {abs(m09['slope_diff']):.3f} vs {abs(ref8['slope_diff']):.3f} "
      f"at I=8   {'MET' if m2 else 'MISSED'}")
print(f"M3  class-level partial rho negative at every musical index: "
      f"{[round(r['partial_rho_class'], 3) for r in musical]}   {'MET' if m3 else 'MISSED'}")
print(f"M4  I=0.1 NOT_MEASURABLE and I=0.5 SELECTION_BIASED, not reported as results   "
      f"{'MET' if m4 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")

with redpath("musical indices measured", expect_min=len(MUSICAL)) as rp:
    rp.observed(sum(1 for r in musical if r["status"] != "NOT_MEASURABLE"))

json.dump(dict(musical_indices=MUSICAL, diagnostic=DIAGNOSTIC, reference=REFERENCE,
               min_partials=MIN_PARTIALS, rows=rows, holds_at=held, fails_at=failed,
               predictions=dict(M1=bool(m1), M2=bool(m2), M3=bool(m3), M4=bool(m4)),
               verdict=verdict, seed=SEED, n_boot=BOOT),
          open(f"{HERE}/brocot_musical_depth.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_musical_depth.json")
