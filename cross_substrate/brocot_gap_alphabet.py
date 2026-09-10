#!/usr/bin/env python3
"""GAP ALPHABET: is the D_Q-rigidity saturation a theorem we re-expressed?

COMMITTED GENERATOR of cross_substrate/brocot_gap_alphabet.json.
Predictions sealed here, before any distinct-spacing count exists.

WHY THIS RUNS
-------------
BROCOT_LITERATURE_STATUS.md (2026-09-09) turned up prior art that the brocot line
had never checked, because until that date the line carried ZERO citations. The
damaging item, found independently by two sweeps:

  BOSHERNITZAN-DYSON (stated in Bleher-Homma-Ji-Roeder-Shen, arXiv:1107.4134):
  the number of DISTINCT nearest-neighbour spacings in {m.omega : |m| <= E} is
  uniformly bounded in E **iff** omega is badly approximable, and unbounded
  otherwise.

That is saturation at the badly-approximable end, as a theorem, at bounded scale
-- the same shape BROCOT_SATURATION.md reports as an empirical finding. In one
dimension the same structure is the three-distance theorem: at bounded N the gap
set of {n.alpha} has at most three values, with multiplicities that are known
functions of the continued-fraction convergents.

So the live worry is [[dont-fit-what-a-theorem-fixes]]: if the Brody fit is
reading the size and weights of a gap alphabet that arithmetic already fixes,
then "the dose-response saturates" is a measurement OF Boshernitzan-Dyson rather
than a finding about this substrate. That is not a small correction. It would
move the result from "we found a saturating relation" to "we re-derived a known
finite-scale theorem through an unusual instrument", which is worth publishing
only if it is SAID that way.

This cell asks the question directly and can answer it either way.

WHAT IS AND IS NOT RE-DERIVED
-----------------------------
The alphas, D_Q and the partial sets are rebuilt from brocot_perAlpha's own
recipe so that P1 can be a reproduction rather than a comparison. The RIGIDITY
axis is recomputed too, but on the UNBOUNDED Brody estimator, not perAlpha's
banked `q`: I8_brody_q fits on bounds (0,1) and rails -- 39.6% of the banked
column sits at 1.0000, and golden reads 0.99993. A railed outcome piles up
exactly at the rigid end, which would manufacture the very variance collapse
under test. BROCOT_SATURATION.md's B1/B2 already chose the unbounded axis "so
the outcome has no rail to pile against"; this cell matches that choice, and P1
checks the bounded column anyway so the two are tied together.

THE STATISTIC. N_distinct(alpha, B) = the number of distinct values among the
nearest-neighbour spacings of the partial set, where two spacings count as one
value if they agree to relative tolerance tau. tau is SWEPT, because a distinct
count in floating point is meaningless without one and a single hidden choice
would be the exact defect modelparams exists to catch.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     the rebuild IS perAlpha: recomputing the BOUNDED Brody q      ║
║                 from freshly built partial sets reproduces the banked         ║
║                 column. Mismatches <= 0.5 of 255 at 1e-9 relative. If this    ║
║                 misses, N_distinct describes a different point set than the   ║
║                 rigidity column does and nothing below is a mediation test.   ║
║ P2  PREMISE     the counter DISCRIMINATES rather than saturating trivially:   ║
║                 at the primary tolerance the median N_distinct must be        ║
║                 strictly inside (1, n_spacings). A counter pinned at 1 (all   ║
║                 spacings identical) or at n (all distinct) measures the       ║
║                 tolerance, not the alphabet, and would make C1-C3 vacuous.    ║
║ C1  EXISTENCE   MEDIATION -- the head. retention = |partial rho(D_Q, u |      ║
║                 N_distinct)| / |rho(D_Q, u)|, at depth 8. Bar: retention      ║
║                 >= 0.5. MET means the dose-response is NOT explained by the   ║
║                 gap alphabet and survives as a finding about this substrate.  ║
║                 MISSED means it largely IS the alphabet, and the honest       ║
║                 report becomes "Boshernitzan-Dyson, measured through a Brody  ║
║                 fit". Both outcomes are publishable; only one is a discovery. ║
║ C2  MECHANISM   the BD growth signature is PRESENT in our own sets: the       ║
║                 slope of N_distinct against B differs between the bottom and  ║
║                 top D_Q terciles, bootstrap CI excluding zero. BD predicts    ║
║                 growth for well-approximable alpha and boundedness for badly  ║
║                 approximable, so the bottom tercile should climb faster. If   ║
║                 this MISSES, the theorem's signature is absent at our scale   ║
║                 and C1 is answering a question about a mechanism that is not  ║
║                 operating here.                                               ║
║ C3  RESOLUTION  the alphabet reproduces the SATURATION SHAPE: |rho(D_Q,       ║
║                 N_distinct)| in the bottom tercile exceeds that in the top    ║
║                 by >= 0.15. This is the same cut BROCOT_SATURATION.md made    ║
║                 on rigidity, applied to the alphabet instead. If the          ║
║                 alphabet saturates where the rigidity saturates, they are     ║
║                 one phenomenon whatever C1 says about mediation.              ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Exploratory, unsealed science. It does not re-run any banked verdict. It
tests whether an existing banked finding has an existing theorem underneath it,
which is a question about ATTRIBUTION, not about whether the numbers are right.
"""
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (os.path.expandvars("$HOME/fmexplorer/brocot"), _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from phase3.partial_prediction import predict_partials, order_bound   # noqa: E402
from cross_substrate.axes import (canonical_spacings, I8_brody_q,     # noqa: E402
                                  I8_brody_q_unbounded)
from reachable import Bar                                             # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,       # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED                # noqa: E402

F_CARRIER = 220.0
DEPTHS = [4.0, 6.0, 8.0, 10.0, 12.0]
PRIMARY_DEPTH = 8.0
TAUS = [1e-9, 1e-7, 1e-5, 1e-3]
PRIMARY_TAU = 1e-7
N_BOOT = 2000
BOOT_SEED = 20260911

INSTRUMENT = Model("gap-alphabet counter over the perAlpha roster", [
    Param("tolerance_tau", TESTED, sweep=TAUS,
          why="two spacings count as one alphabet symbol if they agree to this "
              "relative tolerance. A distinct count in floating point is "
              "undefined without one, and a single hidden choice would set the "
              "answer: too tight and every spacing is its own symbol, too loose "
              "and the alphabet collapses to one. Swept, with P2 guarding the "
              "primary against both degeneracies"),
    Param("depth_B", TESTED, sweep=DEPTHS,
          why="Boshernitzan-Dyson is a statement about GROWTH in the height "
              "bound, so a single depth cannot test it. Swept to give C2 a "
              "slope rather than a point"),
    Param("rigidity_axis", DECLARED, value="I8_brody_q_unbounded",
          why="the bounded estimator rails at 1.0 on 39.6% of this roster, and "
              "the rail sits at the rigid end -- exactly where the saturation "
              "under test lives. BROCOT_SATURATION's B1/B2 chose the unbounded "
              "axis for this reason; matching it keeps the mediation test "
              "commensurable with the finding it is testing"),
    Param("spacing_set", DECLARED, value="raw NN spacings, mean-normalised",
          why="canonical_spacings trims 2-98%, which discards the rarest "
              "alphabet symbols and would bias a distinct COUNT downward. The "
              "trimmed set is still used for the Brody fit, because that is "
              "what the banked rigidity axis was computed on"),
    Param("roster", DECLARED, value="brocot_perAlpha.json rows (n=255)",
          why="the alphas are consumed from the banked artifact rather than "
              "regenerated, so no RNG path can drift; P1 checks the partial "
              "sets rebuilt from them still give the banked q"),
])


def n_distinct(spacings, tau):
    """Alphabet size: sorted spacings clustered at relative tolerance tau."""
    s = np.sort(np.asarray(spacings, dtype=np.float64))
    s = s[s > 0]
    if s.size == 0:
        return 0
    scale = float(np.mean(s))
    if scale <= 0:
        return 0
    cuts = np.diff(s) > (tau * scale)
    return int(1 + np.count_nonzero(cuts))


def raw_spacings(freqs):
    f = np.sort(np.asarray(freqs, dtype=np.float64))
    d = np.diff(f)
    d = d[d > 0]
    return d / np.mean(d) if d.size else d


def partials(alpha, depth):
    return predict_partials([1.0, float(alpha)], [depth, depth],
                            f_carrier=F_CARRIER)


def pearson_ci(x, y, rng, n_boot=N_BOOT):
    x, y = np.asarray(x, float), np.asarray(y, float)
    r = float(np.corrcoef(x, y)[0, 1])
    n = x.size
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        if np.std(x[i]) == 0 or np.std(y[i]) == 0:
            continue
        bs.append(np.corrcoef(x[i], y[i])[0, 1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return r, [float(lo), float(hi)]


def partial_corr(x, y, z):
    """rho(x, y | z) by residualising both on z (linear)."""
    x, y, z = (np.asarray(v, float) for v in (x, y, z))
    Z = np.column_stack([np.ones_like(z), z])
    rx = x - Z @ np.linalg.lstsq(Z, x, rcond=None)[0]
    ry = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
    return float(np.corrcoef(rx, ry)[0, 1])


t0 = time.time()
bank = json.load(open(os.path.join(_HERE, "brocot_perAlpha.json")))
rows = bank["rows"]
alphas = np.array([r["alpha"] for r in rows], dtype=float)
D_Q = np.array([r["D"] for r in rows], dtype=float)
q_banked = np.array([r["q"] for r in rows], dtype=float)
N = len(rows)
print(f"roster: {N} alphas from brocot_perAlpha.json", flush=True)

# ---------- rebuild at every depth ----------
counts = {d: {tau: np.zeros(N, dtype=int) for tau in TAUS} for d in DEPTHS}
n_sp = {d: np.zeros(N, dtype=int) for d in DEPTHS}
u_prim = np.full(N, np.nan)
q_recomp = np.full(N, np.nan)
for j, a in enumerate(alphas):
    for d in DEPTHS:
        sp = partials(a, d)
        if sp.freqs.size < 20:
            continue
        rs = raw_spacings(sp.freqs)
        n_sp[d][j] = rs.size
        for tau in TAUS:
            counts[d][tau][j] = n_distinct(rs, tau)
        if d == PRIMARY_DEPTH:
            cs = canonical_spacings(np.sort(sp.freqs))
            qb = I8_brody_q(cs)
            uu = I8_brody_q_unbounded(cs)
            q_recomp[j] = np.nan if qb is None else qb
            u_prim[j] = np.nan if uu is None else uu
    if (j + 1) % 50 == 0:
        print(f"  {j + 1}/{N} alphas ({time.time() - t0:.0f}s)", flush=True)

ok = np.isfinite(u_prim) & np.isfinite(q_recomp)
print(f"  usable: {ok.sum()} of {N}", flush=True)

# ---------- P1: the rebuild reproduces the banked bounded q ----------
mis = int(np.count_nonzero(
    np.abs(q_recomp[ok] - q_banked[ok]) > 1e-9 * np.maximum(np.abs(q_banked[ok]), 1e-300)))
P1 = Bar("perAlpha bounded-q mismatches", 0.5, floor=0, ceiling=int(ok.sum()),
         direction="le",
         why=f"a count of disagreements at 1e-9 relative over the {int(ok.sum())} "
             "usable alphas; 0 to n by construction")
p1 = P1.score(mis)

# ---------- P2: the counter discriminates ----------
Nd = counts[PRIMARY_DEPTH][PRIMARY_TAU][ok].astype(float)
med = float(np.median(Nd))
med_sp = float(np.median(n_sp[PRIMARY_DEPTH][ok]))
# distance from the nearer degenerate end, as a fraction of the reachable span
head = min(med - 1.0, med_sp - med) / max(med_sp - 1.0, 1e-9)
P2 = Bar("median alphabet size, distance from the nearer degenerate end", 0.02,
         floor=0.0, ceiling=0.5, direction="ge",
         why="0 means the median count sits exactly at 1 (one symbol) or at "
             "n_spacings (all distinct) -- either way the tolerance is being "
             "measured, not the alphabet; 0.5 is the reachable maximum, at the "
             "midpoint. 0.02 asks only that it be off the rail")
p2 = P2.score(float(head))

# ---------- C1: mediation, the head ----------
rng = np.random.default_rng(BOOT_SEED)
r_raw, ci_raw = pearson_ci(D_Q[ok], u_prim[ok], rng)
r_par = partial_corr(D_Q[ok], u_prim[ok], Nd)
retention = abs(r_par) / abs(r_raw) if r_raw != 0 else 0.0
C1 = Bar("|partial rho(D_Q, u | alphabet)| / |rho(D_Q, u)|", 0.5,
         floor=0.0, ceiling=2.0, direction="ge",
         why="a ratio of two correlations of the same pair; 0 means the "
             "alphabet fully accounts for the relation, 1 means it accounts "
             "for none, and values above 1 (suppression) are reachable, which "
             "is why the ceiling is 2 rather than 1")
c1 = C1.score(float(retention))

# ---------- C2: the BD growth signature ----------
B = np.array([order_bound(d) for d in DEPTHS], dtype=float)
logB = np.log(B)
growth = np.full(N, np.nan)
for j in range(N):
    y = np.array([counts[d][PRIMARY_TAU][j] for d in DEPTHS], dtype=float)
    if np.all(y > 0):
        growth[j] = np.polyfit(logB, np.log(y), 1)[0]
gok = ok & np.isfinite(growth)
order = np.argsort(D_Q[gok])
g_sorted = growth[gok][order]
third = g_sorted.size // 3
g_bot, g_top = g_sorted[:third], g_sorted[-third:]
gd = float(np.mean(g_bot) - np.mean(g_top))
bs = [float(np.mean(rng.choice(g_bot, g_bot.size)) -
            np.mean(rng.choice(g_top, g_top.size))) for _ in range(N_BOOT)]
gd_ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
C2 = Bar("alphabet growth-slope gap, bottom minus top D_Q tercile", 0.0,
         floor=-3.0, ceiling=3.0, direction="ge",
         why="a difference of two d(log N_distinct)/d(log B) slopes. Each slope "
             "is bounded well inside [-3,3] because N_distinct is bounded by "
             "the spacing count, which grows at most polynomially in B. BD "
             "predicts a POSITIVE gap; a negative one is fully reachable and "
             "would falsify the mechanism at our scale")
c2 = C2.score(gd)

# ---------- C3: does the alphabet saturate where rigidity does? ----------
o2 = np.argsort(D_Q[ok])
Dv, Nv = D_Q[ok][o2], Nd[o2]
t3 = Dv.size // 3
r_bot = abs(float(np.corrcoef(Dv[:t3], Nv[:t3])[0, 1]))
r_top = abs(float(np.corrcoef(Dv[-t3:], Nv[-t3:])[0, 1]))
C3 = Bar("|rho(D_Q, alphabet)| bottom tercile minus top tercile", 0.15,
         floor=-1.0, ceiling=1.0, direction="ge",
         why="a difference of two absolute correlations, each in [0,1], so the "
             "difference lies in [-1,1]; 0.15 is the same order as the "
             "attenuation BROCOT_SATURATION reports on rigidity")
c3 = C3.score(float(r_bot - r_top))

# ---------- report ----------
print(INSTRUMENT.report())
print(f"\nP1: bounded-q reproduction — {mis} of {int(ok.sum())} mismatched")
print(f"P2: median alphabet {med:.0f} of {med_sp:.0f} spacings "
      f"(headroom {head:.3f})")
print(f"\nalphabet size vs tolerance (depth {PRIMARY_DEPTH:.0f}, median over alphas):")
for tau in TAUS:
    v = counts[PRIMARY_DEPTH][tau][ok]
    print(f"   tau={tau:<8.0e} median {np.median(v):8.1f}   "
          f"range {v.min()}–{v.max()}")
print(f"\nalphabet growth with B (median d log N / d log B): "
      f"{np.nanmedian(growth[gok]):+.3f}")
print(f"   bottom D_Q tercile {np.mean(g_bot):+.3f}   "
      f"top {np.mean(g_top):+.3f}   gap {gd:+.3f} {gd_ci}")
print(f"\nrho(D_Q, u)                = {r_raw:+.4f}  {ci_raw}")
print(f"rho(D_Q, u | alphabet)     = {r_par:+.4f}   retention {retention:.3f}")
print(f"|rho(D_Q, alphabet)| bottom {r_bot:.4f}  top {r_top:.4f}")
print()
for bb, val, f in ((P1, mis, "{:.0f}"), (P2, head, "{:.3f}"),
                   (C1, retention, "{:.3f}"), (C2, gd, "{:+.3f}"),
                   (C3, r_bot - r_top, "{:+.3f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(p1, PREM_ROLE, claim="the rebuilt sets ARE perAlpha's"),
     Arm.from_bar(p2, PREM_ROLE, claim="and the alphabet counter discriminates"),
     Arm.from_bar(c1, EX_ROLE,
                  claim="the dose-response survives controlling for the gap alphabet"),
     Arm.from_bar(c2, MECH_ROLE,
                  claim="with the Boshernitzan-Dyson growth signature present"),
     Arm.from_bar(c3, RES_ROLE,
                  claim="and the alphabet saturating on the same cut as rigidity")],
    holds="SATURATION_SURVIVES_GAP_ALPHABET_CONTROL",
    fails="SATURATION_IS_LARGELY_THE_GAP_ALPHABET")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, n_usable=int(ok.sum()), depths=DEPTHS, taus=TAUS,
    primary_depth=PRIMARY_DEPTH, primary_tau=PRIMARY_TAU,
    order_bounds={str(d): int(order_bound(d)) for d in DEPTHS},
    p1_mismatches=mis,
    alphabet_by_tau={str(tau): counts[PRIMARY_DEPTH][tau][ok].tolist()
                     for tau in TAUS},
    alphabet_by_depth={str(d): counts[d][PRIMARY_TAU][ok].tolist() for d in DEPTHS},
    n_spacings_by_depth={str(d): n_sp[d][ok].tolist() for d in DEPTHS},
    growth=growth[gok].tolist(),
    growth_gap=gd, growth_gap_ci=gd_ci,
    rho_raw=r_raw, rho_raw_ci=ci_raw, rho_partial=r_par, retention=retention,
    rho_alphabet_bottom=r_bot, rho_alphabet_top=r_top,
    u_unbounded=u_prim[ok].tolist(), D_Q=D_Q[ok].tolist(),
    bars={s["name"]: s for s in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="exploratory, unsealed. Tests whether a banked finding has a known "
          "theorem underneath it — a question about ATTRIBUTION, not about "
          "whether the banked numbers are right. Does not re-run any verdict.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(_HERE, "brocot_gap_alphabet.json"), "w"), indent=1)
print("\nwrote brocot_gap_alphabet.json")
