#!/usr/bin/env python3
"""ROSTER STRETCH ERROR: how seed-sensitive is the stretch exponent, measured?

COMMITTED GENERATOR of derivflow/roster_stretch_error.json.
Predictions sealed here, before any bootstrap of the roster exists.

THE GAP THIS CLOSES
-------------------
seed_roster_beta.json banks a stretch exponent per beta-Hermite arm (0.7172,
0.7030, 0.6837) and NO ERROR ON IT. It banks kstar_err because k* is the cell's
declared comparison statistic; the stretch was carried along as a reported
number. So the roster can say k* orders with repulsion at 122.9 sigma and cannot
say ANYTHING with an error bar about the quantity the paper's open question is
actually about -- the stretch itself.

A 2026-09-09 session note put the stretch's seed-sensitivity at "~3.5 sigma"
by borrowing se_beta = 0.00686 from the sealed n=4096 fits as a proxy error
scale. That is an estimate wearing a measurement's clothes, and it is exactly
the [[unattributed-constant]] shape: a headline sensitivity with no live
derivation. This cell measures it instead.

AND IT MUST BE THE SAME ERROR METHOD ON BOTH SIDES.  Comparing "k* moves 122.9
sigma" against "the stretch moves 3.5 sigma" is a commensurability failure if
the two sigmas come from different estimators -- k*'s from 1000 MVN draws on the
fit covariance, the stretch's from a borrowed independent-sigma standard error.
The comparison is only meaningful if both are read off the SAME resampling
distribution. So every bootstrap resample here refits F3 and records BOTH k* and
the stretch, and the sensitivity ratio is formed from those two bootstrap
spreads. Same replicates, same fits, same resamples, two readouts.

WHY A BOOTSTRAP AND NOT THE FIT COVARIANCE.  zbeta_correlated_error (2026-09-08)
established that the 16 replicates are SHARED across all k in a curve, so the
independent-sigma fit error is the wrong error model: correlation TIGHTENED beta
for GUE (ratio 0.735) and LOOSENED it for iid (1.363). Direction is
class-dependent, so it cannot be signed away in advance for beta-Hermite arms
that have never been tested. Resampling replicates carries the correlation
automatically.

AND THE PER-REPLICATE CURVES GET BANKED THIS TIME.  Both the roster and the
dense-grid science banked only stats() output; recovering the replicate vectors
has now cost two separate re-runs (zbeta 09-08, this cell). The recovered array
is written to the artifact so it costs nobody a third.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     the re-run recovers the ROSTER, not a new draw: refitting     ║
║                 the recovered curves reproduces seed_roster_beta.json's       ║
║                 banked params, kstar and beta_stretch for all three arms.     ║
║                 Mismatches <= 0.5 of 15 (3 arms x {la, tau, stretch, kstar,   ║
║                 chi2}) at 1e-9 relative. If this misses, every number below   ║
║                 describes a different instrument than the banked roster and   ║
║                 nothing here comments on it.                                  ║
║ P2  PREMISE     the beta=2 arm still reproduces the banked GUE arm of         ║
║                 science_dense_grid.json: mean and sigma_mean at all 20 k,     ║
║                 n=4096, primary band. Mismatches <= 0.5 of 40. This is the    ║
║                 roster's own P1, re-run, and it chains this cell to the       ║
║                 sealed science rather than only to the roster.                ║
║ C1  EXISTENCE   the stretch exponent MOVES with repulsion: bootstrap          ║
║                 z(stretch, beta_H=1 vs 4) >= 3.0. This can genuinely miss --  ║
║                 the proxy estimate that motivated the cell put it at ~3.5,    ║
║                 barely above the bar, and the bootstrap sigma is not the      ║
║                 proxy sigma. A miss means the stretch is CONSISTENT WITH      ║
║                 CONSTANT across a 4x change in repulsion, which is a          ║
║                 stronger and more interesting statement than a small          ║
║                 separation; it is reported either way and neither is a        ║
║                 failure of the cell.                                          ║
║ C2  MECHANISM   if it moves, it moves monotonically: adjacent inversions in   ║
║                 the stretch across increasing beta_H <= 0.5 of 2. A           ║
║                 non-monotone stretch would mean repulsion is not the          ║
║                 coordinate even where the numbers differ.                     ║
║ C3  RESOLUTION  the two readouts are differently seed-sensitive, on ONE       ║
║                 error method: z(k*) / z(stretch) >= 3.0, both z's formed      ║
║                 from the same bootstrap resamples of the same replicates.     ║
║                 This is the cell's actual claim. It can miss in both          ║
║                 directions: if the stretch is as seed-sensitive as k* the     ║
║                 ratio lands near 1, and if k*'s bootstrap spread is much      ║
║                 wider than its MVN error the ratio collapses.                 ║
║ C4  RESOLUTION  the correlation correction is REPORTED, not assumed:          ║
║                 sigma_boot(stretch) / sigma_indep(stretch) per arm, and the   ║
║                 bar asks only that it stay inside [0.2, 5.0] -- outside that  ║
║                 the two estimators are not measuring the same parameter and   ║
║                 the bootstrap would need explaining before it is believed.    ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Exploratory, unsealed science, like the roster it corrects. It does not
refit the sealed adjudication, does not touch RATE-SEED-DEPENDENT, and does not
re-select the functional form: F3 is fixed from the sealed adjudication for
every arm, exactly as zbeta_correlated_error fixed it.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from reachable import Bar                                            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,      # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED               # noqa: E402
from science_rate_question import (one_flow, f3, MASTER_SEED,        # noqa: E402
                                   LN10, KSTAR_LEVEL, FIT_WINDOW_MIN)
from scipy.linalg import eigvalsh_tridiagonal                        # noqa: E402


def beta_seed(n, rng, beta):
    """DE beta-Hermite tridiagonal -- seed_roster_beta.beta_seed VERBATIM.

    COPIED, not imported, and the copy is deliberate: seed_roster_beta.py has no
    `if __name__ == "__main__"` guard, so importing anything from it executes the
    roster's own 48-flow Pool at import time -- a two-hour side effect from an
    import statement. P1 is what makes the copy safe: if this function has
    drifted from the roster's by so much as a scaling constant, the recovered
    curves will not reproduce the banked fits and the premise fails closed."""
    diag = rng.normal(0.0, np.sqrt(2.0), n)
    off = np.sqrt(rng.chisquare(beta * np.arange(n - 1, 0, -1)))
    ev = eigvalsh_tridiagonal(diag / np.sqrt(beta), off / np.sqrt(beta))
    return np.sort(ev) / np.sqrt(n)

N = 4096
R = 16
NI = 2
K_DENSE = list(range(1, 17)) + [24, 32, 48, 64]
BETAS = [1.0, 2.0, 4.0]
ROSTER_SEED = 20260908
B_BOOT = 2000
BOOT_SEED = 20260910

INSTRUMENT = Model("bootstrap error model for the roster's stretch exponent", [
    Param("bootstrap_B", DECLARED, value=B_BOOT,
          why="resamples of the 16-replicate ensemble. The bootstrap SE's own "
              "relative precision at R=16 is ~1/sqrt(2(R-1)) ~ 18%, which B "
              "cannot improve; 2000 puts Monte-Carlo noise well under that floor. "
              "Same value as zbeta_correlated_error, deliberately, so the two "
              "error models are comparable"),
    Param("resample_unit", DECLARED, value="replicate (whole curve)",
          why="the correlation this cell exists to carry is replicate-sharing "
              "ACROSS k within one curve. Resampling k-points would destroy the "
              "very structure being propagated"),
    Param("fit_window_rule", DECLARED, value="sealed: mean > 1e-3, held fixed",
          why="held at the FULL-ensemble window per arm rather than recomputed "
              "per resample, treating it as a property of the roster's data. "
              "zbeta swept this and found it immaterial (z moved 9.31 -> 9.31 "
              "at 3 significant figures); an unlisted choice here would be the "
              "defect modelparams exists to catch, so it is listed"),
    Param("form", DECLARED, value="F3",
          why="fixed from the sealed adjudication for every arm. Re-selecting "
              "per resample would be a different question (form stability) and "
              "would let the error bar absorb a model-choice fluctuation"),
    Param("beta_ensemble", TESTED, sweep=BETAS,
          why="the roster's own axis, re-run verbatim so P1 can be a recovery "
              "rather than a comparison"),
    Param("n", DECLARED, value=N,
          why="the roster's size; P1/P2 both compare against n=4096 banked arms"),
])


def sealed_fit(means, sigmas, ks):
    """The sealed multi-start F3 fit, verbatim in structure from fit_ladder."""
    y = np.log10(means)
    sy = sigmas / (means * LN10)
    best = None
    for t in (2.0, 5.0, 10.0, 30.0):
        for b in (0.5, 0.75, 1.0):
            try:
                p, cov = curve_fit(f3, ks, y, p0=[y[0], t, b], sigma=sy,
                                   absolute_sigma=True,
                                   bounds=([-np.inf, 1e-3, 0.05],
                                           [np.inf, 1e4, 3.0]),
                                   maxfev=20000)
                chi2 = float(np.sum(((y - f3(ks, *p)) / sy) ** 2))
                if not np.isfinite(chi2) or not np.all(np.isfinite(cov)):
                    continue
                if best is None or chi2 < best[0]:
                    best = (chi2, p, cov)
            except Exception:
                continue
    return best


def kstar_point(params):
    """k* for F3 from parameters alone -- the level crossing, no error draw.
    Same closed form as science_rate_question.kstar's inner solve()."""
    la, tau, be = params
    y0 = np.log10(KSTAR_LEVEL)
    return tau * ((la - y0) / np.log10(np.e)) ** (1.0 / be)


def _job(args):
    beta, i, child = args
    rng = np.random.default_rng(child)
    seed = beta_seed(N, rng, beta)
    rec = one_flow(seed, N, K_DENSE, f"beta={beta} rep={i}")
    return beta, i, [rec[k]["one_minus_rtilde"] for k in K_DENSE]


def recover():
    """Re-run the roster's flows to recover PER-REPLICATE curves.

    Deterministic under the roster's own SeedSequence layout, verbatim: beta=2
    takes the science seal's children 80-95, beta=1 and 4 take
    SeedSequence(ROSTER_SEED). This is a recovery, not a new draw -- which is
    what P1 and P2 check."""
    seal_children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    new_children = np.random.SeedSequence(ROSTER_SEED).spawn(32)
    jobs = [(2.0, i, seal_children[48 + NI * R + i]) for i in range(R)]
    for j, b in enumerate([1.0, 4.0]):
        jobs += [(b, i, new_children[j * R + i]) for i in range(R)]
    with Pool(8) as p:
        res = p.map(_job, jobs)
    out = {b: [None] * R for b in BETAS}
    for b, i, cur in res:
        out[b][i] = cur
    return {b: np.array(v) for b, v in out.items()}


t0 = time.time()
print(f"recovering {3 * R} roster flows at n={N} (8 workers)...", flush=True)
curves = recover()
print(f"  flows done in {time.time() - t0:.0f}s", flush=True)

KA = np.array(K_DENSE, dtype=float)
roster = json.load(open(os.path.join(HERE, "seed_roster_beta.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))

# ---------- P1: the re-run reproduces the banked roster ----------
full, p1_mis, p1_detail = {}, 0, {}
for b in BETAS:
    means = curves[b].mean(axis=0)
    sig = curves[b].std(axis=0, ddof=1) / np.sqrt(R)
    win = means > FIT_WINDOW_MIN
    chi2, p, cov = sealed_fit(means[win], sig[win], KA[win])
    full[b] = dict(means=means, sig=sig, win=win, params=p, cov=cov, chi2=chi2)
    a = roster["arms"][f"{b}"]
    got = [p[0], p[1], p[2], kstar_point(p), chi2]
    want = [a["params"][0], a["params"][1], a["params"][2], a["kstar"], a["chi2"]]
    miss = [n for n, g, w in zip(("la", "tau", "stretch", "kstar", "chi2"),
                                 got, want)
            if abs(g - w) > 1e-9 * max(abs(w), 1e-300)]
    p1_detail[str(b)] = miss
    p1_mis += len(miss)
P1 = Bar("roster recovery mismatches (15 numbers)", 0.5, direction="le",
         floor=0, ceiling=15,
         why="3 beta arms x {la, tau, stretch, k*, chi2} refit from the "
             "recovered curves; a count of disagreements at 1e-9 relative, 0 to 15")
p1 = P1.score(p1_mis)

# ---------- P2: beta=2 still reproduces the banked GUE arm ----------
cell = bank["data"]["gue"][str(N)]
p2_mis = 0
for j, k in enumerate(K_DENSE):
    col = curves[2.0][:, j]
    for got, want in ((float(np.mean(col)), cell[str(k)]["mean"]),
                      (float(np.std(col, ddof=1) / np.sqrt(R)),
                       cell[str(k)]["sigma_mean"])):
        if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
            p2_mis += 1
P2 = Bar("beta=2 mismatches vs the 40 banked GUE numbers", 0.5, direction="le",
         floor=0, ceiling=40,
         why="20 k-points x {mean, sigma_mean} at n=4096; the roster's own P1, "
             "re-run, chaining this cell to the sealed science")
p2 = P2.score(p2_mis)

# ---------- the bootstrap: BOTH readouts off the SAME resamples ----------
rng = np.random.default_rng(BOOT_SEED)
boot = {}
for b in BETAS:
    win = full[b]["win"]
    ks_w = KA[win]
    st_s, kst_s, nok = [], [], 0
    for _ in range(B_BOOT):
        idx = rng.integers(0, R, R)
        c = curves[b][idx]
        m = c.mean(axis=0)
        s = c.std(axis=0, ddof=1) / np.sqrt(R)
        if np.any(m[win] <= 0):
            continue
        got = sealed_fit(m[win], s[win], ks_w)
        if got is None:
            continue
        _, p, _ = got
        kk = kstar_point(p)
        if not np.isfinite(kk) or kk <= 0:
            continue
        st_s.append(p[2])
        kst_s.append(kk)
        nok += 1
    st_s, kst_s = np.array(st_s), np.array(kst_s)
    boot[b] = dict(
        n_ok=nok,
        stretch_mean=float(st_s.mean()), se_stretch=float(st_s.std(ddof=1)),
        kstar_mean=float(kst_s.mean()), se_kstar=float(kst_s.std(ddof=1)),
        se_stretch_indep=float(np.sqrt(full[b]["cov"][2, 2])),
        se_kstar_mvn=float(roster["arms"][f"{b}"]["kstar_err"]),
    )
    print(f"  beta_H={b}: stretch {full[b]['params'][2]:.5f} "
          f"+- {boot[b]['se_stretch']:.5f} (boot, {nok}/{B_BOOT} ok);  "
          f"k* {kstar_point(full[b]['params']):.4f} "
          f"+- {boot[b]['se_kstar']:.4f} (boot)", flush=True)

lo, hi = 1.0, 4.0
d_st = abs(full[lo]["params"][2] - full[hi]["params"][2])
z_st = d_st / np.hypot(boot[lo]["se_stretch"], boot[hi]["se_stretch"])
d_ks = abs(kstar_point(full[lo]["params"]) - kstar_point(full[hi]["params"]))
z_ks = d_ks / np.hypot(boot[lo]["se_kstar"], boot[hi]["se_kstar"])

C1 = Bar("bootstrap z(stretch, beta_H=1 vs 4)", 3.0, direction="ge",
         floor=0.0, ceiling=100.0,
         why="a z is non-negative; 100 a stated practical ceiling. The proxy "
             "estimate that motivated this cell put it near 3.5, just above the "
             "bar, so a miss is genuinely reachable and means 'consistent with "
             "constant'")
c1 = C1.score(float(z_st))

st_seq = [full[b]["params"][2] for b in BETAS]
inv = sum(1 for a, c in zip(st_seq, st_seq[1:]) if c > a)
C2 = Bar("adjacent stretch inversions across increasing beta_H", 0.5,
         direction="le", floor=0, ceiling=2,
         why="2 adjacent pairs over the 3 ensembles; the roster found k* "
             "strictly monotone and this asks the same of the stretch")
c2 = C2.score(inv)

ratio = float(z_ks / z_st) if z_st > 0 else float("inf")
C3 = Bar("z(k*) / z(stretch), both from the same bootstrap", 3.0, direction="ge",
         floor=0.0, ceiling=1000.0,
         why="a ratio of two z's formed on the SAME resamples of the SAME "
             "replicates, so the comparison is commensurable; non-negative, "
             "1000 a stated practical ceiling")
c3 = C3.score(ratio)

rat_c = {b: boot[b]["se_stretch"] / boot[b]["se_stretch_indep"] for b in BETAS}
worst = max(rat_c.values(), key=lambda v: abs(np.log(v)))
C4 = Bar("worst |log| sigma_boot(stretch)/sigma_indep(stretch) over the roster",
         5.0, direction="le", floor=1.0, ceiling=100.0,
         why="reported as max(r, 1/r) so either direction of disagreement "
             "counts: correlation may tighten OR loosen, and zbeta measured "
             "both signs on the two seed classes. 1 is exact agreement; "
             "outside 5x the two estimators are not measuring the same "
             "parameter")
c4 = C4.score(float(max(worst, 1.0 / worst)))

v = compose(
    [Arm.from_bar(p1, PREM_ROLE,
                  claim="the re-run IS the banked roster, refit"),
     Arm.from_bar(p2, PREM_ROLE,
                  claim="and beta=2 is still the sealed GUE arm"),
     Arm.from_bar(c1, EX_ROLE,
                  claim="the stretch exponent moves with repulsion at all"),
     Arm.from_bar(c2, MECH_ROLE,
                  claim="and it moves monotonically"),
     Arm.from_bar(c3, RES_ROLE,
                  claim="but far less than the scale does, on one error method"),
     Arm.from_bar(c4, RES_ROLE,
                  claim="with the correlation correction inside a sane range")],
    holds="STRETCH_MOVES_WITH_REPULSION_FAR_LESS_THAN_SCALE",
    fails="STRETCH_IS_CONSISTENT_WITH_CONSTANT_ACROSS_REPULSION")

print(INSTRUMENT.report())
print(f"\nP1: roster recovery — {p1_mis} of 15 mismatched  {p1_detail}")
print(f"P2: beta=2 vs banked GUE — {p2_mis} of 40 mismatched")
for bb, val, f in ((P1, p1_mis, "{:.0f}"), (P2, p2_mis, "{:.0f}"),
                   (C1, z_st, "{:.2f}"), (C2, inv, "{:.0f}"),
                   (C3, ratio, "{:.1f}"),
                   (C4, max(worst, 1.0 / worst), "{:.3f}")):
    print("  " + bb.line(val, f))

print(f"\nstretch across the roster (beta_H 1 -> 4, a 4x change in repulsion):")
for b in BETAS:
    print(f"  beta_H={b}:  stretch {full[b]['params'][2]:.5f} "
          f"+- {boot[b]['se_stretch']:.5f}   "
          f"k* {kstar_point(full[b]['params']):.4f} +- {boot[b]['se_kstar']:.4f}")
print(f"  z(stretch) = {z_st:.2f}   z(k*) = {z_ks:.2f}   ratio = {ratio:.1f}")
print(f"  sigma_boot/sigma_indep on the stretch: "
      + ", ".join(f"beta={b}: {rat_c[b]:.3f}" for b in BETAS))
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, replicates=R, betas=BETAS, k_grid=K_DENSE, B=B_BOOT,
    boot_seed=BOOT_SEED, roster_seed=ROSTER_SEED,
    p1_mismatches=p1_mis, p1_detail=p1_detail, p2_mismatches=p2_mis,
    per_replicate_curves={str(b): curves[b].tolist() for b in BETAS},
    fits={str(b): dict(params=list(map(float, full[b]["params"])),
                       chi2=float(full[b]["chi2"]),
                       dof=int(full[b]["win"].sum() - 3),
                       fit_window_k=[int(k) for k, w
                                     in zip(K_DENSE, full[b]["win"]) if w],
                       kstar=float(kstar_point(full[b]["params"])))
          for b in BETAS},
    bootstrap={str(b): boot[b] for b in BETAS},
    z=dict(stretch=float(z_st), kstar=float(z_ks), ratio=ratio),
    sigma_ratio_stretch={str(b): float(rat_c[b]) for b in BETAS},
    bars={s_["name"]: s_ for s_ in (p1, p2, c1, c2, c3, c4)},
    instrument=INSTRUMENT.seal(),
    scope="exploratory, unsealed science. An ERROR MODEL for the roster's "
          "stretch exponent: it does not refit the sealed adjudication, does "
          "not re-select the form, and does not touch RATE-SEED-DEPENDENT. "
          "Per-replicate curves are BANKED here so no third re-run is needed.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "roster_stretch_error.json"), "w"), indent=1)
print(f"\nwrote roster_stretch_error.json  ({time.time() - t0:.0f}s)")
