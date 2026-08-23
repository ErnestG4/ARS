"""IS THE SATURATION A PROPERTY OF THE SIGNAL, OR OF DEPTH = 8?

COMMITTED GENERATOR of cross_substrate/brocot_depth_sweep.json.
Predictions and verdict lattice sealed here, before any output exists.

WHY THIS RUNS AT ALL
--------------------
Every brocot result in this arc — B1's ordering, B2's attenuation, and the three
measurements that closed B2's open question — was computed at `DEPTH = 8`, taken
unexamined from `brocot_perAlpha.json`. Nobody chose 8 for this analysis; it was
inherited.

The house rule is explicit: a new front-end's gate must sweep its own knob. Depth
sets how many partials the predictor emits (129 at depth 4, 790 at depth 14), and
the outcome is a spacing statistic over exactly those partials — so depth is not a
cosmetic parameter, it is the sample size of every single measurement. A
saturation that exists only at depth 8 is a fact about depth 8.

The PREDICTOR (D_Q) is depth-independent — it is a property of the number. Only
the outcome u moves. So this sweep varies exactly one thing.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS                                                            ║
║                                                                              ║
║ D1  The saturation HOLDS at every swept depth: the slope-difference CI        ║
║     excludes zero at all of {4, 6, 8, 10, 12, 14}.                           ║
║ D2  Its MAGNITUDE moves a lot — max |slope difference| across depths is more  ║
║     than 2x the min. Depth changes the partial count 6-fold, and a spacing    ║
║     statistic over 129 points is not the same instrument as one over 790.    ║
║ D3  The class-level result (partial rho of class position against            ║
║     within-class slope, controlling for spread) stays NEGATIVE at every       ║
║     depth.                                                                   ║
║                                                                              ║
║ D1 is the one that would hurt. If the saturation appears only at some depths, ║
║ the finding is SCOPED to those and the BROCOT_SATURATION.md wording must be   ║
║ narrowed — stated here so the narrowing cannot be a post-hoc rescue.         ║
║                                                                              ║
║ VERDICT LATTICE                                                              ║
║   DEPTH_INVARIANT    D1 holds at every depth                                 ║
║   DEPTH_SCOPED       D1 holds at some depths and not others; the finding is   ║
║                      scoped to the depths where it holds, and they are named  ║
║   DEPTH_ABSENT       D1 fails at depth 8 itself, which would mean the         ║
║                      original result does not reproduce                       ║
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
ATT = json.load(open(f"{HERE}/brocot_attenuation.json"))
DEPTHS = [4, 6, 8, 10, 12, 14]
SEED, BOOT = 20260823, 2000


def partial_rho(x, y, z):
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return float(stats.pearsonr(ex, ey)[0])


def measure(depth):
    D, U, C, npart = [], [], [], []
    for r in SRC["rows"]:
        if r.get("D") is None:
            continue
        sp = predict_partials([1.0, r["alpha"]], [depth, depth], f_carrier=220.0)
        if sp.freqs.size < 20:
            continue
        u = I8_brody_q_unbounded(canonical_spacings(np.sort(sp.freqs)))
        if u is None:
            continue
        D.append(float(r["D"])); U.append(float(u)); C.append(r["cls"])
        npart.append(int(sp.freqs.size))
    D, U, C = np.array(D), np.array(U), np.array(C)
    n = D.size
    slope_full = float(np.polyfit(D, U, 1)[0])
    cut = np.percentile(D, 200 / 3)
    top = D >= cut
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

    classes = sorted(set(C))
    mD, sl, sD = [], [], []
    for c in classes:
        m = C == c
        if m.sum() < 8 or np.ptp(D[m]) == 0:
            continue
        mD.append(D[m].mean()); sl.append(float(np.polyfit(D[m], U[m], 1)[0]))
        sD.append(float(D[m].std(ddof=1)))
    prho = partial_rho(np.array(mD), np.array(sl), np.array(sD)) if len(mD) >= 5 else float("nan")

    return dict(depth=depth, n=n, median_partials=int(np.median(npart)),
                rho_full=float(stats.spearmanr(D, U)[0]),
                slope_full=slope_full, slope_top=slope_top,
                slope_diff=slope_top - slope_full, ci=[float(lo), float(hi)],
                holds=bool(hi < 0), n_classes=len(mD), partial_rho_class=prho)


res = [measure(d) for d in DEPTHS]

# the depth-8 row must reproduce the banked attenuation run
r8 = next(r for r in res if r["depth"] == 8)
assert abs(r8["slope_full"] - ATT["full"]["slope"]) < 1e-9, (
    f"depth-8 slope {r8['slope_full']} != banked {ATT['full']['slope']}")

print(f"{'depth':>5s} {'n':>4s} {'partials':>9s} {'rho_full':>9s} {'slope_full':>11s} "
      f"{'slope_top':>10s} {'diff':>9s} {'95% CI':>20s} {'holds':>6s} {'pRho':>7s}")
for r in res:
    ci = f"[{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}]"
    print(f"  {r['depth']:>3d} {r['n']:>4d} {r['median_partials']:>9d} "
          f"{r['rho_full']:>9.3f} {r['slope_full']:>11.3f} {r['slope_top']:>10.3f} "
          f"{r['slope_diff']:>9.3f} {ci:>20s} {str(r['holds']):>6s} "
          f"{r['partial_rho_class']:>7.3f}")

holds = [r["depth"] for r in res if r["holds"]]
fails = [r["depth"] for r in res if not r["holds"]]
mags = [abs(r["slope_diff"]) for r in res]
d1 = not fails
d2 = (max(mags) / min(mags)) > 2.0 if min(mags) > 0 else True
d3 = all(r["partial_rho_class"] < 0 for r in res if np.isfinite(r["partial_rho_class"]))

verdict = ("DEPTH_INVARIANT" if d1 else
           "DEPTH_ABSENT" if 8 in fails else "DEPTH_SCOPED")

print(f"\nD1  saturation holds at: {holds}   fails at: {fails or 'none'}   "
      f"{'MET' if d1 else 'MISSED'}")
print(f"D2  |slope diff| ranges {min(mags):.3f}..{max(mags):.3f} "
      f"({max(mags) / min(mags):.1f}x)   {'MET' if d2 else 'MISSED'}")
print(f"D3  class-level partial rho negative at every depth: "
      f"{[round(r['partial_rho_class'], 3) for r in res]}   {'MET' if d3 else 'MISSED'}")
print(f"\nVERDICT: {verdict}")
if verdict == "DEPTH_SCOPED":
    print(f"  BROCOT_SATURATION.md must be narrowed to depths {holds}, per the sealed clause.")

with redpath("depths measured", expect_min=len(DEPTHS)) as rp:
    rp.observed(len(res))

json.dump(dict(depths=DEPTHS, rows=res, holds_at=holds, fails_at=fails,
               predictions=dict(D1=bool(d1), D2=bool(d2), D3=bool(d3)),
               verdict=verdict, seed=SEED, n_boot=BOOT),
          open(f"{HERE}/brocot_depth_sweep.json", "w"), indent=1)
print("\nwritten -> cross_substrate/brocot_depth_sweep.json")
