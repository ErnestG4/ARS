#!/usr/bin/env python3
"""STAGE 3b — how much of the paper's quoted significance is a window choice?

COMMITTED GENERATOR of derivflow/stage3b_window_surface.json.
Predictions sealed here, before any window surface exists.

WHY THIS RUNS, AND WHAT IT FIXES IN STAGE 3
-------------------------------------------
Stage 3 (53130cb / 902be48) composed INVALID on a mis-set premise bar, and an
independent design audit found three further defects. This cell is the successor
and each fix is traceable to one of them:

  * STAGE 3 SWEPT ONE EDGE. It declared `window_upper_k` and never declared a
    lower edge, so `modelparams` could not flag the omission -- it cannot know a
    parameter exists. On the same window, moving k_lo from 1 to 5 leaves the k*
    separation flat (4.444 -> 4.544) while z(k*) collapses 82.5 -> 0.1. BOTH
    edges are TESTED here.
  * STAGE 3 MEASURED THE WRONG DISCRIMINANT. It adjudicated on z(k*), a quantity
    that exists only inside that cell. The PAPER quotes z(tau) = 20.4 and
    z(beta) = 9.3. This cell adjudicates on what is published, and carries k*
    alongside precisely to show the two behave differently.
  * STAGE 3'S PREMISE BAR WAS TYPED, NOT DERIVED. It demanded 1e-9 relative
    agreement from an independently written multi-start fit. GUE cleared it at
    1e-11; iid missed at 1e-8, because iid's sealed fit has chi2 = 48.9 on 13
    dof and its optimum is correspondingly shallow. Here the premise is measured
    in units of each parameter's OWN standard error, so a shallow fit is judged
    by its own conditioning ([[lapack-reproducibility-depends-on-the-path]]).
  * "COMMENSURABLE IN k" IS NOT COMMENSURABLE. The sealed `mean > 1e-3` rule is
    OBSERVABLE-matched: it gives both classes ~2.1 decades of decay. Stage 3's
    k<=11 gives 1.62 vs 2.07, which is WORSE matched than the rule it was
    auditing. Decades spanned are recorded per cell here so the trade is visible
    rather than assumed.

THE QUESTION. Across a surface of defensible window choices, does the SEPARATION
move, or only its SIGNIFICANCE? Those have different consequences. A separation
that moves is a finding about the science. A significance that moves while the
separation does not is a finding about what the paper should quote.

NO FLOWS ARE RUN. Stage 3 banked the per-replicate curves (verified here to
reproduce the sealed ensemble at 1e-12), so this is a pure refit of banked data.
That is why the surface can be 15 cells deep.

DISCLOSED PRIOR LOOK. While diagnosing Stage 3 I computed the sealed, k<=11 and
observable-matched shape-z at n=4096 and saw them span 1.45 to 20.49. I have
seen this surface. Grade DECLARED-WITH-PRIOR-LOOK, not SEALED. What is NOT
pre-seen: the bootstrap errors, every cell off those three, n=1024/2048, and
every bar below, all of which are set from reachability arguments rather than
from the values I saw.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     THE BANKED CURVES ARE THE SEALED ENSEMBLE: mean and          ║
║                 sigma_mean at all 20 k for both classes reproduce            ║
║                 science_dense_grid at 1e-12. Mismatches <= 0.5 of 80.        ║
║ P2  PREMISE     THE SEALED ADJUDICATION REPRODUCES, JUDGED BY ITS OWN        ║
║                 CONDITIONING: refitting each class on its own sealed window   ║
║                 returns the banked shape parameters to within 1e-3 of that    ║
║                 parameter's OWN standard error. Stage 3's 1e-9 absolute bar   ║
║                 failed here for a shallow fit; this asks the question the     ║
║                 fit can answer.                                              ║
║ C1  EXISTENCE   THE SEPARATION IS ROBUST: (max - min) / mean of the k*        ║
║                 separation across all window cells <= 0.25. MET composes      ║
║                 SEPARATION_IS_ROBUST_ACROSS_THE_WINDOW_SURFACE. MISSED means  ║
║                 the sealed science's central claim is itself a window         ║
║                 choice, which would be the most serious finding of the arc.   ║
║ C2  MECHANISM   THE SIGNIFICANCE IS NOT: max/min of z(beta) across the same   ║
║                 cells >= 3.0. If C1 METs and C2 METs, the separation is a     ║
║                 result and the quoted sigma is a reporting choice. If C2      ║
║                 MISSES, z(beta) is as stable as the separation and the        ║
║                 paper's number needs no caveat -- a clean negative.           ║
║ C3  RESOLUTION  WHERE THE PUBLISHED NUMBER SITS: the percentile rank of the   ║
║                 SEALED window's z(beta) among all cells. Bar: <= 0.75, i.e.   ║
║                 the published value is NOT in the top quartile of the         ║
║                 window-dependence range. MISSED means the paper quotes a      ║
║                 favourably-placed number and must say so.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Refits banked data on a surface of window rules. Runs no flows, changes no
instrument, and re-grades nothing. It reports what a window choice is worth.
"""
import json
import os
import sys
import time

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
from science_rate_question import f3, LN10, KSTAR_LEVEL, FIT_WINDOW_MIN  # noqa: E402

N = 4096
R = 16
K_LO = [1, 2, 3, 4, 5]
UPPER = ["sealed_1e-3", "shared_11", "shared_16"]
B_BOOT = 1000
BOOT_SEED = 20260913

INSTRUMENT = Model("sealed science refitted over a window surface", [
    Param("window_lower_k", TESTED, sweep=K_LO,
          why="THE axis Stage 3 omitted. It declared only an upper edge, so "
              "modelparams could not flag the gap -- a parameter that is not "
              "declared cannot be swept and cannot be missed. On the same "
              "window this edge moves z(k*) by three orders of magnitude while "
              "leaving the separation flat"),
    Param("window_upper_rule", TESTED, sweep=UPPER,
          why="sealed_1e-3 is the science's own OBSERVABLE-matched rule (both "
              "classes get ~2.1 decades); shared_11 and shared_16 equalise k "
              "instead, which de-equalises the observable. Carrying all three "
              "makes the trade visible rather than assumed"),
    Param("discriminant", DECLARED, value="z(beta) and z(tau) from the fit covariance",
          why="what the PAPER quotes. Stage 3 adjudicated on z(k*), which "
              "exists only inside that cell and appears in no published claim. "
              "k* is carried alongside precisely to show the two diverge"),
    Param("form", DECLARED, value="F3",
          why="held from the sealed adjudication. An independent audit ran the "
              "full ladder on all 24 (n, class, window) cells and F3 wins every "
              "one by AICc margins of 10.3 to 5642, so holding it is defensible "
              "rather than question-begging"),
    Param("bootstrap_B", DECLARED, value=B_BOOT,
          why="resamples of the 16-replicate ensemble per cell; 15 cells x 2 "
              "classes, and the bootstrap is a diagnostic here rather than the "
              "discriminant, so 1000 suffices"),
    Param("error_model", DECLARED, value="absolute_sigma diagonal, as sealed",
          why="the sealed fit's own error model, kept so the reproduced z "
              "matches the published one. zbeta established it is optimistic "
              "(median |r| 0.875 iid across k-pairs); that is a known and filed "
              "limitation, not one this cell introduces"),
    Param("n", DECLARED, value=N,
          why="the adjudicated size; the published shape-z is defined here"),
])


def fit_f3(mu, sg, ks):
    y, sy = np.log10(mu), sg / (mu * LN10)
    best = None
    for t in (2.0, 5.0, 10.0, 30.0):
        for b in (0.5, 0.75, 1.0):
            try:
                p, cov = curve_fit(f3, ks, y, p0=[y[0], t, b], sigma=sy,
                                   absolute_sigma=True,
                                   bounds=([-np.inf, 1e-3, 0.05],
                                           [np.inf, 1e4, 3.0]), maxfev=20000)
                c2 = float(np.sum(((y - f3(ks, *p)) / sy) ** 2))
                if np.isfinite(c2) and np.all(np.isfinite(cov)) and (
                        best is None or c2 < best[0]):
                    best = (c2, p, cov)
            except Exception:
                continue
    return best


def kstar_of(p):
    return p[1] * ((p[0] - np.log10(KSTAR_LEVEL)) / np.log10(np.e)) ** (1.0 / p[2])


def mask(mu, ka, lo, rule):
    up = (mu > FIT_WINDOW_MIN) if rule == "sealed_1e-3" else (
        ka <= (11 if rule == "shared_11" else 16))
    return up & (ka >= lo)


t0 = time.time()
s3 = json.load(open(os.path.join(HERE, "stage3_commensurable_window.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))
KA = np.array(s3["k_grid"], float)
curves = {sc: np.array(s3["per_replicate_curves"][sc]) for sc in ("iid", "gue")}
means = {sc: curves[sc].mean(axis=0) for sc in ("iid", "gue")}
sigs = {sc: curves[sc].std(axis=0, ddof=1) / np.sqrt(R) for sc in ("iid", "gue")}

# ---------- P1 ----------
p1 = 0
for sc in ("iid", "gue"):
    cell = bank["data"][sc][str(N)]
    for j, k in enumerate(s3["k_grid"]):
        for got, want in ((means[sc][j], cell[str(k)]["mean"]),
                          (sigs[sc][j], cell[str(k)]["sigma_mean"])):
            if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
                p1 += 1
P1 = Bar("banked-curve mismatches vs the sealed ensemble (80 numbers)", 0.5,
         floor=0, ceiling=80, direction="le",
         why="2 classes x 20 k x {mean, sigma_mean}; a count of disagreements "
             "at 1e-12 relative, 0 to 80 by construction")
b1 = P1.score(p1)

# ---------- P2: judged in units of the fit's OWN standard error ----------
worst_sig = 0.0
for sc in ("iid", "gue"):
    w = mask(means[sc], KA, 1, "sealed_1e-3")
    _, p, cov = fit_f3(means[sc][w], sigs[sc][w], KA[w])
    for i, want in enumerate(bank["adjudication"]["shape_params"][sc]):
        se = np.sqrt(cov[i, i])
        worst_sig = max(worst_sig, abs(p[i] - want) / max(se, 1e-300))
P2 = Bar("worst |recovered - banked| in units of that parameter's own sigma",
         1e-3, floor=0.0, ceiling=10.0, direction="le",
         why="a discrepancy measured in the fit's OWN uncertainty, so a shallow "
             "optimum is judged by what it can support. 10 sigma is a stated "
             "practical ceiling; 1e-3 sigma is far below any difference that "
             "could matter and far above optimizer noise. Stage 3's 1e-9 "
             "ABSOLUTE bar failed here for exactly this reason")
b2 = P2.score(float(worst_sig))

# ---------- the surface ----------
rng = np.random.default_rng(BOOT_SEED)
surf = {}
for lo in K_LO:
    for rule in UPPER:
        fits, dec, npts = {}, {}, {}
        ok = True
        for sc in ("iid", "gue"):
            w = mask(means[sc], KA, lo, rule)
            if w.sum() < 5:
                ok = False
                break
            got = fit_f3(means[sc][w], sigs[sc][w], KA[w])
            if got is None:
                ok = False
                break
            fits[sc] = got
            npts[sc] = int(w.sum())
            kk = KA[w]
            dec[sc] = float(f3(kk[0], *got[1]) - f3(kk[-1], *got[1]))
        if not ok:
            continue
        z = {}
        for nm, i in (("tau", 1), ("beta", 2)):
            d_ = abs(fits["iid"][1][i] - fits["gue"][1][i])
            se = np.hypot(np.sqrt(fits["iid"][2][i, i]), np.sqrt(fits["gue"][2][i, i]))
            z[nm] = float(d_ / se)
        ks_pt = {sc: kstar_of(fits[sc][1]) for sc in ("iid", "gue")}
        bs = {sc: [] for sc in ("iid", "gue")}
        for _ in range(B_BOOT):
            idx = rng.integers(0, R, R)
            for sc in ("iid", "gue"):
                c = curves[sc][idx]
                mu = c.mean(axis=0)
                sg = c.std(axis=0, ddof=1) / np.sqrt(R)
                w2 = mask(mu, KA, lo, rule)
                if w2.sum() < 5 or np.any(mu[w2] <= 0):
                    continue
                g2 = fit_f3(mu[w2], sg[w2], KA[w2])
                if g2 is None:
                    continue
                kk2 = kstar_of(g2[1])
                if np.isfinite(kk2) and kk2 > 0:
                    bs[sc].append(kk2)
        sep = abs(ks_pt["iid"] - ks_pt["gue"])
        se_k = np.hypot(np.std(bs["iid"], ddof=1) if len(bs["iid"]) > 2 else np.inf,
                        np.std(bs["gue"], ddof=1) if len(bs["gue"]) > 2 else np.inf)
        surf[(lo, rule)] = dict(
            z_tau=z["tau"], z_beta=z["beta"], sep=float(sep),
            z_kstar=float(sep / se_k) if np.isfinite(se_k) and se_k > 0 else float("nan"),
            kstar_iid=float(ks_pt["iid"]), kstar_gue=float(ks_pt["gue"]),
            n_iid=npts["iid"], n_gue=npts["gue"],
            dec_iid=dec["iid"], dec_gue=dec["gue"],
            chi2dof_iid=fits["iid"][0] / max(npts["iid"] - 3, 1),
            chi2dof_gue=fits["gue"][0] / max(npts["gue"] - 3, 1))
    print(f"  k_lo={lo} done ({time.time() - t0:.0f}s)", flush=True)

seps = np.array([v["sep"] for v in surf.values()])
zb = np.array([v["z_beta"] for v in surf.values()])
spread = float((seps.max() - seps.min()) / seps.mean())
swing = float(zb.max() / max(zb.min(), 1e-12))
sealed_zb = surf[(1, "sealed_1e-3")]["z_beta"]
pct = float(np.mean(zb <= sealed_zb))

C1 = Bar("(max - min) / mean of the k* separation across the surface", 0.25,
         floor=0.0, ceiling=2.0, direction="le",
         why="a relative spread of a positive quantity; 0 is perfect "
             "invariance and 2 is the practical ceiling (a spread of twice the "
             "mean would mean the separation changes sign somewhere). 0.25 is "
             "well inside both ends")
c1 = C1.score(spread)
C2 = Bar("max/min of z(beta) across the same surface", 3.0, floor=1.0,
         ceiling=1000.0, direction="ge",
         why="a ratio of a positive quantity to its own minimum, so 1.0 is the "
             "reachable floor (perfect stability) and 1000 a stated practical "
             "ceiling. MISSED is a clean negative: the published sigma needs no "
             "window caveat")
c2 = C2.score(swing)
C3 = Bar("percentile rank of the SEALED window's z(beta) on the surface", 0.75,
         floor=0.0, ceiling=1.0, direction="le",
         why="a percentile, so [0,1] by construction. MISSED means the "
             "published number sits in the top quartile of what a window choice "
             "can produce, which is a disclosure obligation")
c3 = C3.score(pct)

print(INSTRUMENT.report())
print(f"\nP1 banked curves: {p1} of 80 mismatched")
print(f"P2 worst reproduction: {worst_sig:.2e} of a parameter sigma")
print(f"\n{'k_lo':>5} {'upper':>13} {'pts i/g':>9} {'dec i/g':>11} "
      f"{'z(tau)':>7} {'z(beta)':>8} {'sep k*':>8} {'chi2/dof i':>11}")
for (lo, rule), v in sorted(surf.items()):
    mark = "  <-- SEALED" if (lo, rule) == (1, "sealed_1e-3") else ""
    print(f"{lo:>5} {rule:>13} {v['n_iid']:>4}/{v['n_gue']:<4} "
          f"{v['dec_iid']:>5.2f}/{v['dec_gue']:<5.2f} {v['z_tau']:>7.2f} "
          f"{v['z_beta']:>8.2f} {v['sep']:>8.4f} {v['chi2dof_iid']:>11.2f}{mark}")
print(f"\nseparation: {seps.min():.4f} to {seps.max():.4f}  (spread {spread:.1%})")
print(f"z(beta):    {zb.min():.2f} to {zb.max():.2f}  (swing {swing:.1f}x); "
      f"sealed {sealed_zb:.2f} at percentile {pct:.2f}")
print()
for bb, val, f in ((P1, p1, "{:.0f}"), (P2, worst_sig, "{:.2e}"),
                   (C1, spread, "{:.3f}"), (C2, swing, "{:.1f}"),
                   (C3, pct, "{:.2f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(b1, PREM_ROLE, claim="the banked curves ARE the sealed ensemble"),
     Arm.from_bar(b2, PREM_ROLE, claim="and the sealed adjudication reproduces"),
     Arm.from_bar(c1, EX_ROLE, claim="the separation is robust to the window"),
     Arm.from_bar(c2, MECH_ROLE, claim="while its quoted significance is not"),
     Arm.from_bar(c3, RES_ROLE,
                  claim="and the published value is not favourably placed")],
    holds="SEPARATION_IS_ROBUST_ACROSS_THE_WINDOW_SURFACE",
    fails="THE_SEPARATION_ITSELF_IS_WINDOW_DEPENDENT")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, replicates=R, k_grid=s3["k_grid"], k_lo=K_LO, upper_rules=UPPER,
    B=B_BOOT, boot_seed=BOOT_SEED, p1_mismatches=p1,
    p2_worst_in_sigma=float(worst_sig),
    surface={f"lo{lo}_{rule}": val for (lo, rule), val in surf.items()},
    sep_min=float(seps.min()), sep_max=float(seps.max()), sep_spread=spread,
    zbeta_min=float(zb.min()), zbeta_max=float(zb.max()), zbeta_swing=swing,
    sealed_zbeta=float(sealed_zb), sealed_percentile=pct,
    bars={s["name"]: s for s in (b1, b2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 3b. Refits BANKED data over a surface of window "
          "rules; runs no flows, changes no instrument, re-grades nothing. "
          "DECLARED-WITH-PRIOR-LOOK: three cells of this surface were computed "
          "while diagnosing Stage 3.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "stage3b_window_surface.json"), "w"), indent=1)
print("\nwrote stage3b_window_surface.json")
