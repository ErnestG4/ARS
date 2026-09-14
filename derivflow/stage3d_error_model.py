#!/usr/bin/env python3
"""STAGE 3d — the window swing, computed with an error model that is not known to be wrong.

COMMITTED GENERATOR of derivflow/stage3d_error_model.json.
Predictions sealed here, before any bootstrap z(beta) surface exists.

WHY THIS RUNS. Stages 3b and 3c computed z(beta) from the FIT COVARIANCE with
`absolute_sigma` diagonal errors, and `zbeta_correlated_error` established long
before either that this is the wrong error model for these curves: the 16
replicates are SHARED across k, median |r| 0.875 (iid) and 0.729 (GUE) between
k-pairs. The k* side of 3b/3c is bootstrapped and unaffected. The z(beta) side
is not -- and z(beta) is exactly what the paper's new window-disclosure
paragraph (be1823c) is about.

A four-cell diagnostic at 04:08 (WINDOW_DISCLOSURE_CAVEAT.md) found the
covariance/bootstrap ratio is NOT a constant: 0.87 at the sealed window, 5.89 at
(k_lo=5, k<=11). The covariance model most understates z at SHORT windows, which
is where the swing's denominator lives, so the optimism does not cancel out of a
ratio. Over those four cells the swing was 92x by covariance and 22x by
bootstrap. The paper currently quotes 95.6x / 108.9x / 15.1x.

That diagnostic is 4 cells of 45 at one n. This cell replaces it properly, with
the ERROR MODEL AS A TESTED PARAMETER -- which `verify_declared_params` already
lists as undeclared in both 3b and 3c, so the defect was sitting in a census
written half an hour before the diagnostic found it.

NO FLOWS ARE RUN. Stage 3 banked the n=4096 per-replicate curves and Stage 3c
banked n=1024 and n=2048, so the whole surface is a refit of banked data. That
is the return on having banked them.

LINEAGE. Shares with 3b/3c: the fitter, the window rules, the data. Shares
NOTHING on the error model, which is the axis under test. So this is a
CORRECTION to those cells, not independent corroboration of them, and P2 is
written as a reproduction check against a THIRD cell (`zbeta`) that computed the
sealed bootstrap z(beta) independently.

DISCLOSED PRIOR LOOK: the four diagnostic cells above were seen. The other 41,
the other two n, and every bar are not.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     THE BANKED CURVES ARE THE SEALED ENSEMBLE at every n:         ║
║                 mismatches <= 0.5 of 240 against science_dense_grid.          ║
║ P2  PREMISE     THE SEALED BOOTSTRAP z(beta) REPRODUCES zbeta's INDEPENDENT   ║
║                 VALUE to within 10%. That value is READ from                 ║
║                 zbeta_correlated_error.json, never typed. zbeta computed it   ║
║                 on its own recovery with its own resampler; agreement is a    ║
║                 genuine cross-cell reproduction, and 10% is the bootstrap's   ║
║                 own ~1/sqrt(2(R-1)) ~ 18% precision floor halved.             ║
║ C1  EXISTENCE   THE SWING SURVIVES THE CORRECT ERROR MODEL: under BOOTSTRAP   ║
║                 errors, max/min of z(beta) across the 15 window rules is      ║
║                 >= 3.0 at every n (3 of 3). MISSED means the window           ║
║                 sensitivity was largely an artifact of the optimistic error   ║
║                 model and the paper's paragraph must be withdrawn, not just   ║
║                 renumbered. That is the outcome this cell exists to allow.    ║
║ C2  MECHANISM   AND THE COVARIANCE MODEL INFLATED IT: worst-over-n of         ║
║                 swing_covariance / swing_bootstrap >= 1.5. MISSED means the   ║
║                 two models agree and 3b/3c's numbers stand as published.      ║
║ C3  RESOLUTION  THE SEALED WINDOW IS STILL FAVOURABLY PLACED under bootstrap  ║
║                 errors: minimum over n of its z(beta) percentile > 0.75.      ║
║                 Stated so MET is the uncomfortable answer, as in 3c.          ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE. Refits banked data under two error models. Runs no flows, changes no
instrument, and re-grades nothing. It supplies the numbers the paper's
window-disclosure paragraph should carry.
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
from science_rate_question import f3, LN10, FIT_WINDOW_MIN           # noqa: E402

NS = [1024, 2048, 4096]
R = 16
K_LO = [1, 2, 3, 4, 5]
UPPER = ["sealed_1e-3", "shared_11", "shared_16"]
ERROR_MODELS = ["covariance", "bootstrap"]
B_BOOT = 400
BOOT_SEED = 20260914

INSTRUMENT = Model("window surface under two error models", [
    Param("error_model", TESTED, sweep=ERROR_MODELS,
          why="THE axis, and the one 3b and 3c left undeclared while depending "
              "on it. 'covariance' is absolute_sigma diagonal, which zbeta "
              "showed is wrong for these curves (replicates SHARED across k, "
              "median |r| 0.875 iid / 0.729 GUE). 'bootstrap' resamples whole "
              "replicate curves and carries that correlation automatically"),
    Param("n", TESTED, sweep=NS,
          why="the disclosure is quoted at all three sizes, so the correction "
              "must be too"),
    Param("window_lower_k", TESTED, sweep=K_LO,
          why="the sensitive edge; Stage 3 omitted it entirely and the "
              "significance lives there while the separation does not"),
    Param("window_upper_rule", TESTED, sweep=UPPER,
          why="sealed_1e-3 is the science's own observable-matched rule; the "
              "shared_k rules equalise k and de-equalise the observable"),
    Param("bootstrap_B", DECLARED, value=B_BOOT,
          why="90 cells x 2 classes. The bootstrap SE's own relative precision "
              "at R=16 is ~1/sqrt(2(R-1)) ~ 18%, which B cannot improve; 400 "
              "puts Monte-Carlo noise well under that floor and keeps the "
              "surface affordable"),
    Param("resample_unit", DECLARED, value="replicate (whole curve)",
          why="the correlation under correction is replicate-sharing ACROSS k "
              "within one curve; resampling k-points would destroy it"),
    Param("form", DECLARED, value="F3",
          why="held from the sealed adjudication; AICc-best on all 24 "
              "(class, window, n) cells by margins of 10.3 to 5642"),
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


def mask(mu, ka, lo, rule):
    up = (mu > FIT_WINDOW_MIN) if rule == "sealed_1e-3" else (
        ka <= (11 if rule == "shared_11" else 16))
    return up & (ka >= lo)


t0 = time.time()
s3 = json.load(open(os.path.join(HERE, "stage3_commensurable_window.json")))
s3c = json.load(open(os.path.join(HERE, "stage3c_window_surface_alln.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))
zb = json.load(open(os.path.join(HERE, "zbeta_correlated_error.json")))
ZBETA_REF = float(zb["z"]["bootstrap"])          # READ, never typed
KA = np.array(s3["k_grid"], float)

curves = {4096: {sc: np.array(s3["per_replicate_curves"][sc])
                 for sc in ("iid", "gue")}}
for n in (1024, 2048):
    curves[n] = {sc: np.array(s3c["per_replicate_curves"][str(n)][sc])
                 for sc in ("iid", "gue")}
means = {n: {sc: curves[n][sc].mean(axis=0) for sc in ("iid", "gue")} for n in NS}
sigs = {n: {sc: curves[n][sc].std(axis=0, ddof=1) / np.sqrt(R)
            for sc in ("iid", "gue")} for n in NS}

p1 = 0
for n in NS:
    for sc in ("iid", "gue"):
        cell = bank["data"][sc][str(n)]
        for j, k in enumerate(s3["k_grid"]):
            for got, want in ((means[n][sc][j], cell[str(k)]["mean"]),
                              (sigs[n][sc][j], cell[str(k)]["sigma_mean"])):
                if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
                    p1 += 1
P1 = Bar("banked-curve mismatches across all three n (240 numbers)", 0.5,
         floor=0, ceiling=240, direction="le",
         why="3 n x 2 classes x 20 k x {mean, sigma_mean}; 0 to 240 by construction")
b1 = P1.score(p1)

rng = np.random.default_rng(BOOT_SEED)
surf = {}
for n in NS:
    for lo in K_LO:
        for rule in UPPER:
            fits, ok = {}, True
            for sc in ("iid", "gue"):
                w = mask(means[n][sc], KA, lo, rule)
                if w.sum() < 5:
                    ok = False
                    break
                g = fit_f3(means[n][sc][w], sigs[n][sc][w], KA[w])
                if g is None:
                    ok = False
                    break
                fits[sc] = g
            if not ok:
                continue
            d = abs(fits["iid"][1][2] - fits["gue"][1][2])
            z_cov = d / np.hypot(np.sqrt(fits["iid"][2][2, 2]),
                                 np.sqrt(fits["gue"][2][2, 2]))
            bs = {sc: [] for sc in ("iid", "gue")}
            for _ in range(B_BOOT):
                idx = rng.integers(0, R, R)
                for sc in ("iid", "gue"):
                    c = curves[n][sc][idx]
                    mu = c.mean(axis=0)
                    sg = c.std(axis=0, ddof=1) / np.sqrt(R)
                    w2 = mask(mu, KA, lo, rule)
                    if w2.sum() < 5 or np.any(mu[w2] <= 0):
                        continue
                    g2 = fit_f3(mu[w2], sg[w2], KA[w2])
                    if g2 is not None and np.isfinite(g2[1][2]):
                        bs[sc].append(g2[1][2])
            se = np.hypot(np.std(bs["iid"], ddof=1) if len(bs["iid"]) > 2 else np.inf,
                          np.std(bs["gue"], ddof=1) if len(bs["gue"]) > 2 else np.inf)
            surf[(n, lo, rule)] = dict(
                z_covariance=float(z_cov),
                z_bootstrap=float(d / se) if np.isfinite(se) and se > 0 else float("nan"),
                delta_beta=float(d), n_ok=min(len(bs["iid"]), len(bs["gue"])))
    print(f"  n={n} done ({time.time() - t0:.0f}s)", flush=True)

per_n = {}
for n in NS:
    cells = {k: v for k, v in surf.items() if k[0] == n}
    zc = np.array([v["z_covariance"] for v in cells.values()])
    zbo = np.array([v["z_bootstrap"] for v in cells.values()])
    fin = np.isfinite(zbo)
    per_n[n] = dict(
        swing_cov=float(zc.max() / max(zc.min(), 1e-12)),
        swing_boot=float(zbo[fin].max() / max(zbo[fin].min(), 1e-12)),
        sealed_cov=float(surf[(n, 1, "sealed_1e-3")]["z_covariance"]),
        sealed_boot=float(surf[(n, 1, "sealed_1e-3")]["z_bootstrap"]),
        pct_boot=float(np.mean(zbo[fin] <= surf[(n, 1, "sealed_1e-3")]["z_bootstrap"])),
        zb_min=float(zbo[fin].min()), zb_max=float(zbo[fin].max()))

sealed4096 = per_n[4096]["sealed_boot"]
P2 = Bar("|sealed bootstrap z(beta) - zbeta's independent value| / zbeta's", 0.10,
         floor=0.0, ceiling=10.0, direction="le",
         why="a relative difference between two INDEPENDENT bootstrap "
             "computations of the same quantity, one read from "
             "zbeta_correlated_error.json. Non-negative; 10 a practical ceiling. "
             "0.10 is half the bootstrap's own ~18% precision floor at R=16")
b2 = P2.score(abs(sealed4096 - ZBETA_REF) / max(ZBETA_REF, 1e-12))

n_swing = sum(1 for n in NS if per_n[n]["swing_boot"] >= 3.0)
C1 = Bar("n at which the BOOTSTRAP z(beta) swing reaches 3x", 2.5, floor=0,
         ceiling=3, direction="ge",
         why="a count over the 3 sizes; 2.5 requires all three. MISSED means the "
             "window sensitivity was largely an error-model artifact and the "
             "paper's paragraph must be WITHDRAWN, not renumbered")
c1 = C1.score(n_swing)
infl = max(per_n[n]["swing_cov"] / max(per_n[n]["swing_boot"], 1e-12) for n in NS)
C2 = Bar("worst-over-n swing_covariance / swing_bootstrap", 1.5, floor=0.0,
         ceiling=1000.0, direction="ge",
         why="a ratio of two swings of the same quantity; 1.0 is exact "
             "agreement and 1000 a practical ceiling. MISSED means the two error "
             "models agree and 3b/3c's published numbers stand")
c2 = C2.score(infl)
min_pct = min(per_n[n]["pct_boot"] for n in NS)
C3 = Bar("minimum over n of the sealed window's BOOTSTRAP z(beta) percentile",
         0.75, floor=0.0, ceiling=1.0, direction="ge",
         why="a percentile, [0,1] by construction. Stated so MET is the "
             "uncomfortable answer, as in Stage 3c")
c3 = C3.score(min_pct)

print(INSTRUMENT.report())
print(f"\nP1 banked curves: {p1} of 240 mismatched")
print(f"P2 sealed bootstrap z(beta) {sealed4096:.3f} vs zbeta's {ZBETA_REF:.3f} "
      f"({abs(sealed4096 - ZBETA_REF) / ZBETA_REF:.1%})")
print(f"\n{'n':>6} {'swing cov':>10} {'swing boot':>11} {'inflation':>10} "
      f"{'sealed cov':>11} {'sealed boot':>12} {'pct boot':>9}")
for n in NS:
    v = per_n[n]
    print(f"{n:>6} {v['swing_cov']:>10.1f} {v['swing_boot']:>11.1f} "
          f"{v['swing_cov'] / v['swing_boot']:>10.2f} {v['sealed_cov']:>11.2f} "
          f"{v['sealed_boot']:>12.2f} {v['pct_boot']:>9.2f}")
print()
for bb, val, f in ((P1, p1, "{:.0f}"),
                   (P2, abs(sealed4096 - ZBETA_REF) / ZBETA_REF, "{:.3f}"),
                   (C1, n_swing, "{:.0f}"), (C2, infl, "{:.2f}"),
                   (C3, min_pct, "{:.2f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(b1, PREM_ROLE, claim="the banked curves ARE the sealed ensemble"),
     Arm.from_bar(b2, PREM_ROLE,
                  claim="and the sealed bootstrap reproduces zbeta independently"),
     Arm.from_bar(c1, EX_ROLE,
                  claim="the window swing survives the correct error model"),
     Arm.from_bar(c2, MECH_ROLE, claim="while the covariance model inflated it"),
     Arm.from_bar(c3, RES_ROLE,
                  claim="and the sealed window is still favourably placed")],
    holds="WINDOW_SWING_SURVIVES_THE_CORRECT_ERROR_MODEL",
    fails="THE_WINDOW_SWING_WAS_LARGELY_AN_ERROR_MODEL_ARTIFACT")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    ns=NS, replicates=R, k_lo=K_LO, upper_rules=UPPER,
    error_models=ERROR_MODELS, B=B_BOOT, boot_seed=BOOT_SEED,
    zbeta_reference_read=ZBETA_REF, p1_mismatches=p1,
    surface={f"n{n}_lo{lo}_{rule}": val for (n, lo, rule), val in surf.items()},
    per_n={str(n): per_n[n] for n in NS},
    worst_inflation=infl, n_with_swing=n_swing, min_percentile=min_pct,
    lineage=dict(shares_with_3b3c=["fitter", "window rules", "data"],
                 independent_of_3b3c=["error model"],
                 note="a CORRECTION to 3b/3c, not corroboration of them; P2 is "
                      "a reproduction check against zbeta, a third cell"),
    bars={s["name"]: s for s in (b1, b2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 3d. Refits banked data under two error models; "
          "runs no flows, changes no instrument, re-grades nothing. Supplies "
          "the numbers the paper's window-disclosure paragraph should carry.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "stage3d_error_model.json"), "w"), indent=1)
print("\nwrote stage3d_error_model.json")
