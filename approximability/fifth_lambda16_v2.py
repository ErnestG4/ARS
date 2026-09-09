"""FIFTH LAMBDA-16 v2: same seal, premise re-specified to the measured BLAS floor.

COMMITTED GENERATOR of approximability/fifth_lambda16_v2.json.

v1 (fifth_lambda16.py) composed INVALID because P1 demanded BIT-EQUALITY with the
banked lam=8 ladder. That is unachievable for this pipeline and the reason is
measured, not supposed: `sla.eigvalsh` through a threaded LAPACK is
reduction-order dependent, the same q=665 computation returns three different
values at OMP_NUM_THREADS = 1, 2 and 8, and the banked ladder came from an older
numpy/scipy build again. Within one configuration it repeats exactly.

v2 changes EXACTLY TWO THINGS and inherits everything else from v1's seal, which
predates any output:
  1. P1 compares floats to a RELATIVE tolerance of 1e-4 and keeps `bands` (an
     integer count) EXACT. The tolerance is not chosen to pass: the largest
     deviation v1 measured is 1.9e-6 relative, so 1e-4 sits 50x above the
     observed floor -- and it is still ~1000x tighter than the four decimals any
     of these dimensions is quoted to, while a genuine code difference (wrong
     corner sign, wrong band pairing, wrong potential) moves dimensions in the
     third decimal or worse. It admits BLAS noise and nothing else.
  2. The output filename, and the artifact now RECORDS the numerical environment
     -- numpy/scipy versions and the BLAS thread variables -- because an input
     that changes the answer should be pinned, and this one changes it in the
     eighth decimal. That is the same lesson as pinning a graph by hash, one
     layer down.

DISCLOSURE: v2 is sealed after v1's numbers were seen, so C1-C4 are INHERITED
predictions, not fresh ones; their sealing credit belongs to v1's commit, where
they were written before any output existed. P1's bar is the only thing that
moved, and it moved because the quantity it compares is not bit-reproducible.

Read v1's docstring for the question, the banked table and the rival C3 excludes.
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
REL_TOL = 1e-4          # see the docstring: the measured BLAS floor is 1.9e-6
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
        if f == "bands":
            if a != b:                                # an integer count: exact
                mism += 1
            continue
        if abs(a - b) > REL_TOL * max(abs(b), 1e-300):
            mism += 1
P1 = Bar("lam=8 mismatches vs the 36 banked ladder numbers", 0.5, direction="le",
         floor=0, ceiling=36,
         why=f"9 rungs x {{bands (exact), total_width, dim_bandscaling, "
             f"dim_boxcount (relative {REL_TOL:g})}}; a count of disagreements, "
             f"0 to 36. The tolerance is 50x the largest BLAS-noise deviation v1 "
             f"measured and ~1000x tighter than the precision these are quoted "
             f"at, so it admits reduction-order noise and nothing else")
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

import scipy                                                     # noqa: E402
NUMENV = dict(numpy=np.__version__, scipy=scipy.__version__,
              omp=os.environ.get("OMP_NUM_THREADS"),
              openblas=os.environ.get("OPENBLAS_NUM_THREADS"),
              mkl=os.environ.get("MKL_NUM_THREADS"),
              note="eigvalsh is reduction-order dependent; these values change "
                   "the answer in the ~8th decimal and are recorded so a future "
                   "re-run knows what it is matching")
print(f"\nnumerical environment: {NUMENV}")

json.dump(dict(
    alpha="log2(3/2)", seed=SEED, lambdas=[LAM_PREMISE, LAM_NEW],
    numerical_environment=NUMENV, rel_tol=REL_TOL,
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
    open(os.path.join(HERE, "fifth_lambda16_v2.json"), "w"), indent=1)
print("\nwrote fifth_lambda16_v2.json")
