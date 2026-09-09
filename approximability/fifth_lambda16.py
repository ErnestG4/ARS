#!/usr/bin/env python3
"""FILLING THE LAMBDA GAP: is the 23-step dimension jump lambda-INVARIANT?

COMMITTED GENERATOR of approximability/fifth_lambda16.json.
Predictions sealed here, before any lam=16 output exists.

THE GAP, AND WHY IT IS A DETECTOR
----------------------------------
`fifth_ladder.py` runs LAMBDAS = [8.0, 24.0, 32.0]. Sixteen is missing, and a
gap in a numbered series is one of the few coverage detectors this repo has
found that actually works. It is also the interesting value:
`outside_proven_regime` is `lam <= 20`, so 8 and 16 sit OUTSIDE the Liu-Wen
V>20 regime while 24 and 32 sit inside, and FINDINGS calls the Casdagli-Suto
V>=16 band "genuinely messy point-wise". Sixteen is the messy boundary itself.

WHAT MAKES IT WORTH A RUN RATHER THAN A ROW. Read off the banked artifact
(not the prose -- checked today, they agree):

    lam      dim@q665   dim@q15601   the 23-step jump   estimator disagreement
      8       0.4202      0.4660         +0.0458              0.0956
     24       0.2968      0.3420         +0.0452              0.0597
     32       0.2752      0.3208         +0.0455              0.0347

The dimension LEVEL moves by 0.19 across a 4x range in lambda -- a 70% swing.
The JUMP moves by 0.0006. Whatever the 23-step does to the spectrum, it does
the same thing at every coupling tested, while the coupling strongly sets where
the spectrum sits. Three points is a pattern; a fourth, at a lambda between the
two extremes and inside the unproven regime, is a test.

THE RIVAL THIS SEPARATES, stated so C3 can lose. If the jump were a fixed
FRACTION of the dimension rather than a fixed increment, then at lam=16 (whose
level should land near 0.39) the jump would be about 0.0458 x (0.39/0.4660) =
0.038 -- roughly 0.007 from the banked mean, which C3's bar excludes. So C3
distinguishes "the same increment everywhere" from "scales with the level", and
those are different statements about the operator.

MACHINERY: `periodic_edges`, `floquet_bands`, `bs_dim` and `box_dim` are copied
VERBATIM from the committed `fifth_ladder.py` (which measures at import time and
so cannot be imported), and `potential`/`cf_frac`/`convergents` come from
`task1_pi_depth5` exactly as it imports them. P1 then re-runs lam=8 and demands
the banked numbers back -- the copies are not trusted because they look right.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    re-running lam = 8 reproduces the banked ladder EXACTLY:      ║
║                bands, total_width, dim_bandscaling and dim_boxcount at all   ║
║                9 rungs -- 36 numbers, mismatches <= 0.5. Same machinery or   ║
║                nothing.                                                     ║
║ C1  EXISTENCE  lam = 16 yields a COMPLETE convergent ladder: the layer-zero  ║
║                gate `count_eq_q` (band count equals q) holds at >= 8.5 of 9  ║
║                rungs. A ladder that loses bands is not a fourth point on     ║
║                the same curve, whatever its dimension says.                  ║
║ C2  MECHANISM  the LEVEL is monotone in lambda: dim@q15601 for lam = 16      ║
║                sits strictly inside (0.3420, 0.4660) with at least 0.005 of  ║
║                margin at both ends. If it lands outside, lambda does not     ║
║                order the dimension and the three banked points were not a    ║
║                curve.                                                       ║
║ C3  RESOLUTION THE CELL: the jump is lambda-INVARIANT. |jump(16) − mean of   ║
║                the three banked jumps| <= 0.005. The banked spread is        ║
║                0.0006, so this bar is ~8x the observed scatter and still     ║
║                excludes the proportional-to-level rival by 0.007.            ║
║ C4  RESOLUTION and the box-count estimator still RAILS: its value is         ║
║                identical across q = 41..15601, distinct values <= 1.5.       ║
║                FINDINGS calls box_dim resolution-saturated at every banked   ║
║                lambda; if it stops railing at 16, the estimator-agreement    ║
║                story changes and C3's companion numbers mean something else. ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE: this adds one lambda to a banked ladder. It does not re-open the C
extrapolation, the metallic columns, or any dimension claim quoted elsewhere;
those are lambda->infinity readouts and a single finite lambda does not bear on
them. What it tests is an INVARIANCE across lambda that three points suggested.
"""
import gc
import json
import math
import os
import sys
import time

import numpy as np
import scipy.linalg as sla
import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from reachable import Bar                                          # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,     # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED              # noqa: E402
from redpath import redpath                                        # noqa: E402
from task1_pi_depth5 import potential, cf_frac, convergents         # noqa: E402

SEED = 20240517
LAM_PREMISE, LAM_NEW = 8.0, 16.0
JUMP_LO, JUMP_HI = "665", "15601"

INSTRUMENT = Model("Sturmian Floquet ladder at alpha=log2(3/2)", [
    Param("lam", TESTED, sweep=[LAM_PREMISE, LAM_NEW],
          why="8 is the PREMISE (it must reproduce the banked ladder); 16 is the "
              "gap in LAMBDAS=[8,24,32] and the only untested value inside the "
              "messy Casdagli-Suto V>=16 / outside-Liu-Wen band"),
    Param("alpha", DECLARED, value="log2(3/2)",
          why="the diatonic value; the banked ladder's only new input, unchanged"),
    Param("q_max", DECLARED, value=15601,
          why="the banked ladder's convergent cutoff; a different cutoff would "
              "make the 23-step jump a different quantity"),
    Param("estimators", DECLARED, value="bs_dim and box_dim, verbatim",
          why="copied from the committed fifth_ladder.py, which measures at "
              "import; P1 is what makes the copies trustworthy"),
    Param("seed", DECLARED, value=SEED, why="the arc's seed, unused by this "
                                            "deterministic path but declared"),
])


# ---- VERBATIM from the committed fifth_ladder.py ----
def periodic_edges(V, corner):
    q = len(V); H = np.zeros((q, q), dtype=np.float64); np.fill_diagonal(H, V)
    idx = np.arange(q - 1); H[idx, idx + 1] = 1.0; H[idx + 1, idx] = 1.0
    H[0, q - 1] = corner; H[q - 1, 0] = corner
    w = sla.eigvalsh(H, overwrite_a=True, driver='evr')
    del H; gc.collect(); return w


def floquet_bands(V):
    ep = periodic_edges(V, +1.0); ea = periodic_edges(V, -1.0)
    return np.sort(np.concatenate([ep, ea]))


def bs_dim(bands, q):
    if not bands: return float("nan")
    mw = sum(hi - lo for lo, hi in bands) / len(bands)
    return math.log(q) / math.log(1.0 / mw) if 0 < mw < 1 else float("nan")


def box_dim(bands, e0, e1, n=12):
    span = e1 - e0; mw = sum(hi - lo for lo, hi in bands) / max(1, len(bands))
    counts, scales, eps = [], [], span
    for _ in range(n):
        s = set()
        for lo, hi in bands:
            for b in range(int((lo - e0) / eps), int((hi - e0) / eps) + 1): s.add(b)
        counts.append(len(s)); scales.append(eps); eps /= 2
        if eps < 2 * mw: break
    if len(counts) < 3: return float("nan")
    return float(np.polyfit(np.log2(1 / np.array(scales)), np.log2(counts), 1)[0])
# ---- end verbatim ----


mp.mp.dps = 80
alpha = mp.log(mp.mpf(3) / mp.mpf(2)) / mp.log(mp.mpf(2))
cf = cf_frac(alpha, 12)
ps, qs = convergents(cf)
LADDER = [(ps[k], qs[k], (cf[k] if k < len(cf) else None))
          for k in range(len(qs)) if qs[k] <= 15601]
print(f"ladder q<=15601: {[q for _, q, _ in LADDER]}", flush=True)


def run_lambda(lam):
    e0, e1 = -2.5, lam + 2.5
    out, prev_tw = {}, None
    for (p, q, a) in LADDER:
        td = time.time()
        if q == 1:
            bands = [(lam - 2.0, lam + 2.0)]
        else:
            V = potential(p, q, lam)
            edges = floquet_bands(V)
            bands = [(edges[2 * j], edges[2 * j + 1]) for j in range(q)]
        nb = len(bands); tw = float(sum(hi - lo for lo, hi in bands))
        d_bs = bs_dim(bands, q)
        d_box = box_dim(bands, e0, e1) if q >= 5 else float('nan')
        out[str(q)] = dict(q=q, p=p, bands=nb, count_eq_q=(nb == q),
                           total_width=tw, dim_bandscaling=d_bs, dim_boxcount=d_box,
                           estimator_agreement=(abs(d_bs - d_box)
                                                if np.isfinite(d_box) else None),
                           width_ratio_vs_prev=(tw / prev_tw) if prev_tw else None,
                           outside_proven_regime=(lam <= 20),
                           wall_s=time.time() - td)
        prev_tw = tw
        print(f"  lam={lam:>4} q={q:6d} bands={nb} dim_bs={d_bs:.4f} "
              f"dim_box={d_box:.4f} [{out[str(q)]['wall_s']:.1f}s]", flush=True)
    return out


t0 = time.time()
res = {str(LAM_PREMISE): run_lambda(LAM_PREMISE),
       str(LAM_NEW): run_lambda(LAM_NEW)}
print(f"[{time.time() - t0:.0f}s total]", flush=True)

# ---- P1: does lam=8 reproduce the banked ladder? ----
bank = json.load(open(os.path.join(HERE, "fifth_ladder.json")))["results"]
mine8, bank8 = res[str(LAM_PREMISE)], bank["lam8.0"]
mism = 0
for q, row in bank8.items():
    got = mine8.get(q)
    if got is None:
        mism += 4
        continue
    for f in ("bands", "total_width", "dim_bandscaling", "dim_boxcount"):
        a, b = got[f], row[f]
        if isinstance(a, float) and isinstance(b, float) and a != a and b != b:
            continue                                  # NaN == NaN here
        if a != b:
            mism += 1
P1 = Bar("lam=8 mismatches vs the 36 banked ladder numbers", 0.5, direction="le",
         floor=0, ceiling=36,
         why="9 rungs x {bands, total_width, dim_bandscaling, dim_boxcount}; a "
             "count of disagreements, 0 to 36")
p1 = P1.score(mism)

new = res[str(LAM_NEW)]
n_gate = sum(1 for r in new.values() if r["count_eq_q"])
C1 = Bar("lam=16 rungs passing the count_eq_q gate", 8.5, floor=0, ceiling=9,
         why="a count over the 9 convergent rungs")
c1 = C1.score(n_gate)

lvl16 = new[JUMP_HI]["dim_bandscaling"]
lo_lvl = bank["lam24.0"][JUMP_HI]["dim_bandscaling"]
hi_lvl = bank["lam8.0"][JUMP_HI]["dim_bandscaling"]
margin = min(lvl16 - lo_lvl, hi_lvl - lvl16)
C2 = Bar("margin of dim(lam=16) inside (dim@24, dim@8)", 0.005,
         floor=-1.0, ceiling=1.0,
         why="a signed distance from the nearer endpoint; negative means outside "
             "the interval, and both endpoints are banked dimensions in [0,1]")
c2 = C2.score(margin)

banked_jumps = [bank[k][JUMP_HI]["dim_bandscaling"] - bank[k][JUMP_LO]["dim_bandscaling"]
                for k in ("lam8.0", "lam24.0", "lam32.0")]
mean_jump = sum(banked_jumps) / len(banked_jumps)
jump16 = new[JUMP_HI]["dim_bandscaling"] - new[JUMP_LO]["dim_bandscaling"]
C3 = Bar("|jump(16) - mean of the banked jumps|", 0.005, direction="le",
         floor=0.0, ceiling=2.0,
         why="a difference of two dimension increments, each bounded by 1")
c3 = C3.score(abs(jump16 - mean_jump))

boxvals = sorted({round(new[q]["dim_boxcount"], 10) for q in ("41", "53", "306", "665", "15601")
                  if new[q]["dim_boxcount"] == new[q]["dim_boxcount"]})
C4 = Bar("distinct box-dim values across q=41..15601 at lam=16", 1.5,
         direction="le", floor=1, ceiling=5,
         why="a count of distinct values over the 5 rungs where box_dim is "
             "defined; 1 means fully railed, as at every banked lambda")
c4 = C4.score(len(boxvals))

# ---- report ----
print()
print(INSTRUMENT.report())
print(f"\nP1: lam=8 vs banked — {mism} of 36 mismatched")
print(f"\n{'lam':>5s} {'dim@665':>9s} {'dim@15601':>10s} {'jump':>9s} {'disagree':>9s}")
for k, lab in (("lam8.0", "8"), (None, "16"), ("lam24.0", "24"), ("lam32.0", "32")):
    r = new if k is None else bank[k]
    a, b = r[JUMP_LO]["dim_bandscaling"], r[JUMP_HI]["dim_bandscaling"]
    ag = r[JUMP_HI]["estimator_agreement"]
    star = "  <- new" if k is None else ""
    print(f"{lab:>5s} {a:9.4f} {b:10.4f} {b - a:+9.4f} {ag:9.4f}{star}")
print(f"\n  banked jumps {[round(j, 4) for j in banked_jumps]}, mean {mean_jump:.5f}")
print(f"  lam=16 jump {jump16:+.5f}, deviation {abs(jump16 - mean_jump):.5f}")
print(f"  box-dim at lam=16 across q=41..15601: {boxvals}")
print()
for b, v, f in ((P1, mism, "{:.0f}"), (C1, n_gate, "{:.0f}"), (C2, margin, "{:.4f}"),
                (C3, abs(jump16 - mean_jump), "{:.5f}"), (C4, len(boxvals), "{:.0f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="the copied machinery IS the banked ladder's"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="lam=16 gives a complete convergent ladder"),
             Arm.from_bar(c2, MECH_ROLE,
                          claim="lambda orders the dimension level, and 16 lands "
                                "between its neighbours"),
             Arm.from_bar(c3, RES_ROLE,
                          claim="the 23-step jump is the same increment at a "
                                "fourth lambda, not a fraction of the level"),
             Arm.from_bar(c4, RES_ROLE,
                          claim="and the box estimator still rails, so the "
                                "companion agreement numbers mean what they did")],
            holds="THE_23_STEP_JUMP_IS_LAMBDA_INVARIANT",
            fails="JUMP_INVARIANCE_NOT_ESTABLISHED_AT_LAMBDA_16")
print(f"\nVERDICT: {v['citation']}")

with redpath("Floquet rungs solved", expect_min=15) as rp:
    rp.observed(sum(len(x) for x in res.values()))

json.dump(dict(
    alpha="log2(3/2)", seed=SEED, lambdas=[LAM_PREMISE, LAM_NEW],
    ladder=[q for _, q, _ in LADDER],
    results=res, p1_mismatches=mism,
    banked_jumps=banked_jumps, mean_banked_jump=mean_jump, jump_lam16=jump16,
    level_lam16=lvl16, level_interval=[lo_lvl, hi_lvl], level_margin=margin,
    box_dim_distinct_values=boxvals,
    bars={s["name"]: s for s in (p1, c1, c2, c3, c4)},
    instrument=INSTRUMENT.seal(),
    scope="adds one lambda to the banked ladder; does NOT bear on the "
          "lambda->infinity C extrapolation or any asymptotic dimension claim",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1)),
    open(os.path.join(HERE, "fifth_lambda16.json"), "w"), indent=1)
print("\nwrote fifth_lambda16.json")
