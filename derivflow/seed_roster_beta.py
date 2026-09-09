#!/usr/bin/env python3
"""SEED ROSTER: is the (tau, beta) seed-dependence a function of LOCAL REPULSION,
with the global measure held fixed?

COMMITTED GENERATOR of derivflow/seed_roster_beta.json.
Predictions sealed here, before any beta != 2 flow exists.

THE BACKLOG ITEM, AND A DELIBERATE DEPARTURE FROM ITS WORDING
--------------------------------------------------------------
ROADMAP backlog 2026-08-13 proposed the JKM Part II catalogue (Touchard, Fubini,
Eulerian, Narayana, hypergeometric) as "the ready-made third and fourth seed
classes if the (tau, beta) parameter-dependence question graduates from a
two-point comparison to a parameter-surface measurement." This cell graduates the
question but changes the roster, for two stated reasons:

  1. FEASIBILITY. Those families are catalogued by their GLOBAL root
     distributions. Getting their ROOTS at n = 4096 means finding the zeros of a
     degree-4096 integer polynomial whose coefficients overflow double precision
     by hundreds of orders of magnitude; the root-finding is ill-conditioned
     exactly where we would need it to be exact.
  2. THE AXIS IS WRONG FOR THE QUESTION. Those families differ in their global
     shape. This arc's whole finding is a TWO-SCALE structure -- global frozen,
     local crystallising underneath -- so a roster that varies the global shape
     confounds the two scales in the very measurement meant to separate them.

The beta-Hermite ensembles fix both. The existing GUE seed is already the
Dumitriu-Edelman beta = 2 tridiagonal (science_rate_question.gue_seed), so the
family generalises by ONE parameter, and:

  * every beta-Hermite ensemble has the SAME semicircle global law after
    scaling, so the global measure is held FIXED by construction while local
    repulsion is swept -- the matched-pair design this repo's own rule asks for,
    hold one property and flip the other;
  * beta IS the repulsion strength (eigenvalue interaction |x_i - x_j|^beta), so
    the sweep is along the axis that governs local statistics, which is the axis
    the relaxation curve lives on;
  * beta = 2 reproduces the banked GUE arm EXACTLY, which turns the existing
    science run into this cell's premise instead of a neighbouring result.

iid (Uniform[-1,1]) stays in the comparison as the non-repulsive reference, read
from the banked artifact rather than re-run.

TAU IS NOT THE COMPARISON QUANTITY. Today's lesson from the isoconfig amendment:
tau in F3 is degenerate with the stretch exponent and is not commensurable across
fits that may select different forms. Every cross-seed comparison below is made
at k*, the level crossing, using the arc's own sealed kstar() with its MVN
parameter-draw error bar.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    the beta = 2 arm reproduces the banked GUE arm of              ║
║                science_dense_grid.json: mean and sigma_mean at all 20 k,      ║
║                n = 4096, primary band. Mismatches <= 0.5 of 40. This is the   ║
║                whole reason to build the roster on this family; if it         ║
║                misses, the new arms are a different instrument and nothing    ║
║                below compares to anything banked.                            ║
║ P2  PREMISE    the design is actually matched: the three classes' seed root   ║
║                distributions agree, max pairwise two-sample KS <= 0.05        ║
║                (a same-law KS at n = 4096 sits near 0.03). If the global      ║
║                laws differ, a k* difference is not attributable to local      ║
║                repulsion and the cell's question is unanswerable.             ║
║ C1  EXISTENCE  the stretched form is not a property of beta = 2: all three    ║
║                beta arms select F3 under the sealed ladder, counted >= 2.5    ║
║                of 3.                                                         ║
║ C2  MECHANISM  and the relaxation scale ORDERS with repulsion: k* strictly    ║
║                decreasing across beta = 1, 2, 4 -- adjacent inversions <=     ║
║                0.5 of 2. Predicted decreasing because a more strongly         ║
║                repelling seed starts nearer the crystalline configuration     ║
║                the flow is heading to (banked: GUE k* ~ 6 against iid ~ 11).  ║
║ C3  RESOLUTION the axis actually moves the scale rather than jittering it:    ║
║                |k*(1) - k*(4)| / sqrt(err1^2 + err4^2) >= 3.0.                ║
║                                                                              ║
║ C2 IS THE CELL. C1 can hold trivially if every seed stretches; C3 can hold    ║
║ on a large but unordered spread. C2 is the claim that repulsion is the        ║
║ VARIABLE the two-point iid/GUE contrast was sampling, and a miss says the     ║
║ contrast was reading something else that happens to differ between them.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE: exploratory and unsealed as science -- it does not touch the sealed
RATE-SEED-DEPENDENT verdict. What is sealed is this cell's prediction set.
Seeds for beta = 1 and beta = 4 come from a fresh SeedSequence(20260908); the
beta = 2 arm deliberately reuses the science seal's own children so that P1 is a
reproduction and not a resampling.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.linalg import eigvalsh_tridiagonal
from scipy.stats import ks_2samp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from reachable import Bar                                            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,       # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED                # noqa: E402
from aggregate import banked                                          # noqa: E402
from science_rate_question import (one_flow, fit_ladder, kstar,        # noqa: E402
                                   gue_seed, MASTER_SEED, FIT_WINDOW_MIN)

N = 4096
R = 16
NI = 2                                   # n=4096 index in the seal's N_SCIENCE
K_DENSE = list(range(1, 17)) + [24, 32, 48, 64]
BETAS = [1.0, 2.0, 4.0]
ROSTER_SEED = 20260908

INSTRUMENT = Model("beta-Hermite seed roster (Dumitriu-Edelman tridiagonal)", [
    Param("beta_ensemble", TESTED, sweep=BETAS,
          why="the repulsion exponent in |x_i - x_j|^beta. THE axis of this "
              "cell: it varies local statistics while leaving the semicircle "
              "global law unchanged, which P2 verifies rather than assumes"),
    Param("n", DECLARED, value=N,
          why="the adjudicated size of the arc; P1 compares against the banked "
              "n=4096 arm"),
    Param("replicates", DECLARED, value=R,
          why="the seal's own ensemble size, so per-k sigma_mean is computed the "
              "same way as in the banked artifact"),
    Param("k_grid", DECLARED, value="dense {1..16} u {24,32,48,64}",
          why="the v1.6 dense grid verbatim; any other grid would make P1 "
              "incomparable to the banked numbers"),
    Param("seed_streams", DECLARED,
          value=f"beta=2 reuses the science seal's children 80-95; beta=1 and 4 "
                f"from SeedSequence({ROSTER_SEED})",
          why="beta=2 must REPRODUCE, so it takes the seal's own stream; the new "
              "arms take an independent stream because they are new draws and "
              "reusing a stream across ensembles would correlate them"),
    Param("comparison_statistic", DECLARED, value="k* (level crossing)",
          why="tau in F3 is degenerate with the stretch exponent and is not "
              "commensurable across fits that may select different forms "
              "(gue_isoconfig_kstar_amendment, 2026-09-08). Every cross-seed "
              "comparison here is at k*"),
])


def beta_seed(n, rng, beta):
    """DE beta-Hermite tridiagonal, full spectrum, scaled to the semicircle.

    beta = 2 is science_rate_question.gue_seed VERBATIM in structure; the only
    generalisation is the chi-square degrees of freedom and the matching 1/sqrt
    scaling. P1 tests that this reduces exactly."""
    diag = rng.normal(0.0, np.sqrt(2.0), n)
    off = np.sqrt(rng.chisquare(beta * np.arange(n - 1, 0, -1)))
    ev = eigvalsh_tridiagonal(diag / np.sqrt(beta), off / np.sqrt(beta))
    return np.sort(ev) / np.sqrt(n)


def _job(args):
    beta, i, child = args
    rng = np.random.default_rng(child)
    seed = beta_seed(N, rng, beta)
    rec = one_flow(seed, N, K_DENSE, f"beta={beta} rep={i}")
    return beta, i, {str(k): rec[k]["one_minus_rtilde"] for k in K_DENSE}, seed


t0 = time.time()
seal_children = np.random.SeedSequence(MASTER_SEED).spawn(96)
new_children = np.random.SeedSequence(ROSTER_SEED).spawn(32)
jobs = []
for i in range(R):
    jobs.append((2.0, i, seal_children[48 + NI * R + i]))
for j, b in enumerate([1.0, 4.0]):
    for i in range(R):
        jobs.append((b, i, new_children[j * R + i]))

print(f"running {len(jobs)} flows at n={N} over beta in {BETAS} (8 workers)...",
      flush=True)
with Pool(8) as p:
    res = p.map(_job, jobs)
print(f"  flows done in {time.time() - t0:.0f}s", flush=True)

curves = {b: [None] * R for b in BETAS}
seeds = {b: [None] * R for b in BETAS}
for b, i, rec, sd in res:
    curves[b][i] = [rec[str(k)] for k in K_DENSE]
    seeds[b][i] = sd
curves = {b: np.array(v) for b, v in curves.items()}

# ---- P1: does beta=2 reproduce the banked GUE arm? ----
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))
cell = bank["data"]["gue"][str(N)]
mismatch = 0
for j, k in enumerate(K_DENSE):
    col = curves[2.0][:, j]
    for got, want in ((float(np.mean(col)), cell[str(k)]["mean"]),
                      (float(np.std(col, ddof=1) / np.sqrt(R)),
                       cell[str(k)]["sigma_mean"])):
        if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
            mismatch += 1
P1 = Bar("beta=2 mismatches vs the 40 banked GUE numbers", 0.5, direction="le",
         floor=0, ceiling=40,
         why="20 k-points x {mean, sigma_mean} at n=4096; a count of "
             "disagreements at 1e-12 relative, 0 to 40")
p1 = P1.score(mismatch)

# ---- P2: is the global law actually held fixed? ----
ks_pairs = {}
for a in range(len(BETAS)):
    for b in range(a + 1, len(BETAS)):
        ba, bb = BETAS[a], BETAS[b]
        d = float(np.median([ks_2samp(seeds[ba][i], seeds[bb][i]).statistic
                             for i in range(R)]))
        ks_pairs[f"{ba}v{bb}"] = d
worst_ks = max(ks_pairs.values())
P2 = Bar("max pairwise seed-law KS across beta", 0.05, direction="le",
         floor=0.0, ceiling=1.0,
         why="a two-sample KS statistic lies in [0,1]; a same-law KS at "
             "n=4096 sits near 0.03, so 0.05 admits sampling noise and "
             "excludes a real difference in the global law")
p2 = P2.score(worst_ks)

# ---- fits and k* per beta ----
rng_ci = np.random.default_rng(4242)
arms = {}
for b in BETAS:
    means = curves[b].mean(axis=0)
    sig = curves[b].std(axis=0, ddof=1) / np.sqrt(R)
    ks_in = [k for j, k in enumerate(K_DENSE) if means[j] > FIT_WINDOW_MIN]
    idx = [K_DENSE.index(k) for k in ks_in]
    sel, fits = fit_ladder(np.array(ks_in, dtype=float), means[idx], sig[idx])
    k0, kerr = (None, None)
    if "params" in fits[sel]:
        k0, kerr = kstar(sel, np.array(fits[sel]["params"]),
                         np.array(fits[sel]["cov"]), rng_ci)
    p = fits[sel].get("params")
    arms[b] = dict(selected=sel, fit_window_k=ks_in, params=p,
                   kstar=k0, kstar_err=kerr,
                   tau=(p[1] if sel in ("F2", "F3") and p else None),
                   beta_stretch=(p[2] if sel == "F3" and p else None),
                   chi2=fits[sel].get("chi2"), dof=fits[sel].get("dof"))

C1 = Bar("beta arms selecting F3", 2.5, floor=0, ceiling=3,
         why="a count over the 3 beta-ensembles")
c1 = C1.score(sum(1 for b in BETAS if arms[b]["selected"] == "F3"))

kstars = [arms[b]["kstar"] for b in BETAS]
inv = (99 if any(x is None for x in kstars)
       else sum(1 for a, b in zip(kstars, kstars[1:]) if b >= a))
C2 = Bar("adjacent k* inversions across increasing beta", 0.5, direction="le",
         floor=0, ceiling=2, why="2 adjacent pairs over the 3 ensembles")
c2 = C2.score(inv)

if arms[1.0]["kstar"] is not None and arms[4.0]["kstar"] is not None:
    sep = (abs(arms[1.0]["kstar"] - arms[4.0]["kstar"])
           / np.sqrt(arms[1.0]["kstar_err"] ** 2 + arms[4.0]["kstar_err"] ** 2))
else:
    sep = 0.0
C3 = Bar("|k*(beta=1) - k*(beta=4)| in combined sigma", 3.0,
         floor=0.0, ceiling=1000.0,
         why="a separation in units of the combined MVN k* error; non-negative, "
             "1000 a stated practical ceiling")
c3 = C3.score(sep)

# ---- report ----
print(INSTRUMENT.report())
print(f"\nP1: beta=2 vs banked GUE — {mismatch} of 40 mismatched")
print(f"P2: pairwise seed-law KS — " +
      ", ".join(f"{k} {v:.4f}" for k, v in ks_pairs.items()))
print(f"\n{'beta':>6s} {'form':>5s} {'window':>7s} {'k*':>9s} {'err':>7s} "
      f"{'tau':>8s} {'stretch':>8s} {'chi2/dof':>9s}")
for b in BETAS:
    a = arms[b]
    print(f"{b:>6.0f} {a['selected']:>5s} {len(a['fit_window_k']):>7d} "
          f"{a['kstar']:>9.4f} {a['kstar_err']:>7.4f} "
          f"{(a['tau'] if a['tau'] else float('nan')):>8.4f} "
          f"{(a['beta_stretch'] if a['beta_stretch'] else float('nan')):>8.4f} "
          f"{a['chi2'] / a['dof']:>9.4f}")
bi = bank["kstar_table"]["iid"][str(N)]
bg = bank["kstar_table"]["gue"][str(N)]
print(f"\n  banked reference: iid k* {bi['kstar']:.4f} +- {bi['err']:.4f} "
      f"({bi['form']}), gue k* {bg['kstar']:.4f} +- {bg['err']:.4f} ({bg['form']})")
print(f"  k* trend across repulsion: " +
      " > ".join(f"{arms[b]['kstar']:.3f}" for b in BETAS)
      + ("  (monotone decreasing)" if inv == 0 else f"  ({inv} inversion(s))"))
print()
for bb, v, f in ((P1, mismatch, "{:.0f}"), (P2, worst_ks, "{:.4f}"),
                 (C1, sum(1 for b in BETAS if arms[b]["selected"] == "F3"), "{:.0f}"),
                 (C2, inv, "{:.0f}"), (C3, sep, "{:.2f}")):
    print("  " + bb.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="beta=2 IS the banked GUE arm"),
             Arm.from_bar(p2, PREM_ROLE,
                          claim="the global law is held fixed across the roster"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="the stretched form is not special to beta=2"),
             Arm.from_bar(c2, MECH_ROLE,
                          claim="and the relaxation scale orders with repulsion"),
             Arm.from_bar(c3, RES_ROLE,
                          claim="the repulsion axis moves the scale well beyond "
                                "its own error")],
            holds="RELAXATION_SCALE_ORDERS_WITH_SEED_REPULSION",
            fails="REPULSION_ORDERING_NOT_ESTABLISHED")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, replicates=R, betas=BETAS, k_grid=K_DENSE, roster_seed=ROSTER_SEED,
    p1_mismatches=mismatch, seed_law_ks=ks_pairs,
    arms={str(b): arms[b] for b in BETAS},
    banked_reference={"iid": bi, "gue": bg},
    kstar_by_beta={str(b): dict(kstar=arms[b]["kstar"], err=arms[b]["kstar_err"])
                   for b in BETAS},
    bars={s["name"]: s for s in (p1, p2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="exploratory, unsealed science. Does not touch the sealed "
          "RATE-SEED-DEPENDENT verdict. Global law held fixed BY CONSTRUCTION "
          "and verified by P2, so k* differences are attributable to local "
          "repulsion.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1)),
    open(os.path.join(HERE, "seed_roster_beta.json"), "w"), indent=1)
print("\nwrote seed_roster_beta.json")
