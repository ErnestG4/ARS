"""THE SHAPE-z UNDER AN ERROR MODEL THAT CARRIES THE REPLICATE-SHARING COVARIANCE.

COMMITTED GENERATOR of derivflow/zbeta_correlated_error.json.
Predictions sealed here, before any per-replicate data exists in the repo.

WHAT THIS REPAIRS, AND WHY IT IS NOT A TRANSCRIPTION
----------------------------------------------------
ROADMAP backlog item 2026-08-16 (packaging audit). The sealed shape-z treats the
per-k sigma_mean as INDEPENDENT. The conservative convention then rescales each
covariance by max(1, chi2/dof). Recomputed here from the banked artifact rather
than recalled: iid chi2/dof = 3.7587 (rescale x3.759), GUE chi2/dof = 0.0175
(rescale x1.000 -- INERT). So the conservative z(beta) = 5.8411 clears the sealed
5-sigma bar while resting on a GUE sigma the same readout flags as suspect, and
the cheap convention CANNOT touch it: max(1, .) is the identity for chi2 < dof.

The audit filed the diagnosis as UNTESTED: 'shared-replicate correlation' is the
explanation on offer and nothing in the record tests it. This cell tests it, and
the direction is genuinely open -- there is a real argument each way:

  (a) THE AUDIT'S READING: chi2/dof = 0.0175 means the fit sits far closer to the
      means than their error bars allow. Something is wrong with the error model;
      the GUE parameter sigmas are understated; z(beta) is inflated.
  (b) THE COUNTER-ARGUMENT, which is why C2 below predicts the OPPOSITE SIGN: each
      replicate is one deterministic flow measured at successive derivative steps,
      so its curve is smooth and its deviation from the model is largely a COMMON
      MODE across k. A common mode is nearly degenerate with the amplitude
      parameter lambda. The SHAPE parameters (tau, beta) are fixed by DIFFERENCES
      across k, from which the common mode cancels -- so a correlated error model
      should determine beta BETTER than the diagonal one, not worse, and a tiny
      chi2 is the fingerprint of exactly that, not of a broken instrument.

Both cannot be right. C2 is the arm that separates them, and the seal states the
prediction (b) so that a miss is a finding rather than a shrug.

THE INSTRUMENT: TWO INDEPENDENT TREATMENTS, BECAUSE ONE WOULD NOT BE CHECKABLE
------------------------------------------------------------------------------
  PRIMARY -- nonparametric bootstrap over the 16 replicates (B = 2000). Each
  resample re-runs the SEALED reduction verbatim (mean of raw values, then log10,
  then sigma_mean = std/sqrt(16), then the sealed multi-start fit at fixed form
  F3) so every cross-k correlation is carried by construction. No matrix is
  inverted, which matters: with R = 16 replicates the sample covariance over a
  16-point window has rank <= 15 and is SINGULAR, so a naive GLS on this window
  is not merely noisy, it does not exist.

  SECONDARY -- GLS with a shrinkage covariance, swept. C(a) = (1-a)S + a*diag(S).
  The shrinkage intensity is a free parameter and therefore TESTED with its
  sweep, per modelparams: this cell exists because a free parameter rode in
  unlisted once already.

C4 requires the two to agree. They fail differently -- the bootstrap is
distribution-free but noisy at R = 16, the GLS is smooth but needs a
regularisation choice -- so agreement is evidence and disagreement means neither
number should be quoted alone.

DISCLOSURE (prior look, one number): while timing the flow cost before writing
this seal, one iid replicate (child 32, rep 0) was run and its k=1 value seen:
0.3571506082764372. One replicate's single k-point. No covariance, no fit, no
z was computed. It is disclosed because the rule is disclosure, not materiality.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE    the recovered per-replicate ensemble REPRODUCES the banked     ║
║                artifact: mean and sigma_mean at all 20 k, both classes,       ║
║                n = 4096 -- 80 numbers, relative agreement 1e-12.             ║
║                Mismatches <= 0.5 of 80. If this misses, the flows I am        ║
║                analysing are not the flows that were sealed, and every arm    ║
║                below describes a different instrument.                        ║
║ C1  EXISTENCE  the diagnosed MECHANISM is present: median |Pearson r| over    ║
║                fit-window k-pairs, GUE, >= 0.5. If the replicates are         ║
║                near-uncorrelated across k, 'shared-replicate correlation' is  ║
║                an empty explanation and the audit's caveat needs a different  ║
║                one.                                                          ║
║ C2  MECHANISM  AND IT TIGHTENS RATHER THAN LOOSENS (argument (b) above):      ║
║                sigma_boot(beta_GUE) / sigma_indep(beta_GUE) <= 0.95.          ║
║                A miss REFUTES (b) and supports the audit's reading (a);       ║
║                a value in (0.95, 1.0) is directionally consistent and is      ║
║                reported as MISSED, not reinterpreted.                        ║
║ C3  RESOLUTION the headline survives the honest error model:                  ║
║                z_boot(beta) >= 5.0, the sealed bar. This is the decision the  ║
║                cell exists to make. A miss does NOT retract the sealed        ║
║                verdict -- that verdict stands on the sealed rule as executed  ║
║                -- it retracts the claim that beta's margin is comfortable.    ║
║ C4  RESOLUTION and the two treatments agree: max over the shrinkage sweep of  ║
║                |z_gls - z_boot| / z_boot <= 0.25.                            ║
║                                                                              ║
║ C2 IS THE CELL. C3 is what we want to know; C2 is what we would LEARN, and    ║
║ it is the arm where I have a stated position that the data can take away.    ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPE: n = 4096, the adjudicated arm, primary band only. This cell reports an
ERROR MODEL for the sealed point estimates; it does not refit the science, does
not touch the sealed verdict, and does not re-select the functional form (F3 is
fixed from the sealed adjudication; form-selection stability under resampling is
reported as a diagnostic, not as an arm).
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import curve_fit, least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from reachable import Bar                                          # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,     # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED              # noqa: E402
from aggregate import banked                                        # noqa: E402
from science_rate_question import (one_flow, gue_seed, f3, MASTER_SEED,  # noqa: E402
                                   FIT_WINDOW_MIN, LN10)

N = 4096
NI = 2                      # index of n=4096 in N_SCIENCE
R = 16                      # replicates per class, from the seal
B_BOOT = 2000
SHRINK = [0.05, 0.1, 0.2, 0.4]
BOOT_SEED = 20260908
K_DENSE = list(range(1, 17)) + [24, 32, 48, 64]
BANKED = os.path.join(HERE, "science_dense_grid.json")

INSTRUMENT = Model("replicate-sharing error model for the sealed shape-z", [
    Param("bootstrap_B", DECLARED, value=B_BOOT,
          why="resamples of the 16-replicate ensemble; the bootstrap SE's own "
              "relative precision at R=16 is ~1/sqrt(2(R-1)) ~ 18%, which B "
              "cannot improve -- B only removes Monte-Carlo noise on top of it, "
              "and 2000 puts that well below the 18% floor"),
    Param("shrinkage_intensity", TESTED, sweep=SHRINK,
          why="C(a) = (1-a)S + a*diag(S). A free regularisation parameter, and "
              "the reason this Model exists: the sample covariance at R=16 over "
              "a 16-point window is rank-deficient, so SOME choice is forced and "
              "an unlisted one would be the exact defect modelparams was built "
              "for. C4 scores the answer's stability across it"),
    Param("fit_window_rule", TESTED, sweep=["sealed_fixed", "per_resample"],
          why="the sealed window is means > 1e-3 on the FULL ensemble. Holding "
              "it fixed across resamples treats it as a property of the sealed "
              "data; recomputing it per resample lets it fluctuate. Both are "
              "defensible, so neither is assumed"),
    Param("form", DECLARED, value="F3",
          why="fixed from the sealed adjudication. Re-selecting per resample "
              "would be a different question (form stability), reported as a "
              "diagnostic below rather than allowed to move the error bar"),
    Param("n", DECLARED, value=N,
          why="the adjudicated arm; the sealed shape-z is defined at n=4096"),
    Param("band", DECLARED, value="primary",
          why="the sealed primary band (Richardson 2F(eps)-F(2eps)); the eps/2eps "
              "arms exist to test FORM invariance, not to carry the error model"),
])


def _one(args):
    sc, i, child = args
    if sc == "iid":
        seed = np.sort(np.random.default_rng(child).uniform(-1, 1, N))
    else:
        seed = gue_seed(N, np.random.default_rng(child))
    rec = one_flow(seed, N, K_DENSE, f"{sc} n={N} rep={i}")
    return sc, i, {str(k): rec[k]["one_minus_rtilde"] for k in K_DENSE}


def recover():
    """Re-run the sealed flows to recover PER-REPLICATE curves.

    The banked artifact stores only stats() output -- mean and sigma_mean per k.
    The replicate vectors it aggregated were never written, and the covariance
    this cell needs cannot be reconstructed from a mean and a standard error.
    Deterministic under the seal's SeedSequence, so this is a recovery, not a
    new draw -- which is what P1 checks."""
    children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    jobs = ([("iid", i, children[0 + NI * R + i]) for i in range(R)]
            + [("gue", i, children[48 + NI * R + i]) for i in range(R)])
    with Pool(8) as p:
        res = p.map(_one, jobs)
    out = {"iid": [None] * R, "gue": [None] * R}
    for sc, i, rec in res:
        out[sc][i] = rec
    return {sc: np.array([[v[str(k)] for k in K_DENSE] for v in out[sc]])
            for sc in ("iid", "gue")}


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
                                   bounds=([-np.inf, 1e-3, 0.05], [np.inf, 1e4, 3.0]),
                                   maxfev=20000)
                chi2 = float(np.sum(((y - f3(ks, *p)) / sy) ** 2))
                if not np.isfinite(chi2) or not np.all(np.isfinite(cov)):
                    continue
                if best is None or chi2 < best[0]:
                    best = (chi2, p, cov)
            except Exception:
                continue
    return best


def gls_fit(means, S_raw, ks, alpha):
    """GLS at shrinkage `alpha`. S_raw is the covariance OF THE MEAN, raw scale;
    delta-method it into log10 space, shrink, Cholesky-whiten, fit F3."""
    D = np.diag(1.0 / (means * LN10))
    C = D @ S_raw @ D
    C = (1.0 - alpha) * C + alpha * np.diag(np.diag(C))
    L = np.linalg.cholesky(C)
    y = np.log10(means)

    def resid(p):
        return np.linalg.solve(L, y - f3(ks, *p))

    best = None
    for t in (2.0, 5.0, 10.0, 30.0):
        for b in (0.5, 0.75, 1.0):
            try:
                r = least_squares(resid, [y[0], t, b],
                                  bounds=([-np.inf, 1e-3, 0.05], [np.inf, 1e4, 3.0]))
                if not r.success:
                    continue
                if best is None or r.cost < best[0]:
                    best = (r.cost, r)
            except Exception:
                continue
    if best is None:
        return None
    r = best[1]
    J = r.jac
    try:
        cov = np.linalg.inv(J.T @ J)
    except np.linalg.LinAlgError:
        return None
    return r.x, cov


t0 = time.time()
print("recovering per-replicate curves (32 flows at n=4096, 8 workers)...", flush=True)
CURVES = recover()
print(f"  recovered in {time.time() - t0:.0f}s", flush=True)

bank = json.load(open(BANKED))

# ---- P1: does the recovery reproduce the banked artifact? ----
mismatch = 0
for sc in ("iid", "gue"):
    cell = bank["data"][sc][str(N)]
    for j, k in enumerate(K_DENSE):
        col = CURVES[sc][:, j]
        for got, want in ((float(np.mean(col)), cell[str(k)]["mean"]),
                          (float(np.std(col, ddof=1) / np.sqrt(R)),
                           cell[str(k)]["sigma_mean"])):
            if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
                mismatch += 1
P1 = Bar("recovered-vs-banked mismatches (80 numbers)", 0.5, direction="le",
         floor=0, ceiling=80,
         why="20 k-points x 2 classes x {mean, sigma_mean}; a count of "
             "disagreements at 1e-12 relative, 0 to 80")
p1 = P1.score(mismatch)

# ---- the sealed fit window, and the per-class arrays on it ----
WIN, MEANS, SIGS, SRAW, IDX = {}, {}, {}, {}, {}
for sc in ("iid", "gue"):
    cell = bank["data"][sc][str(N)]
    ks = [k for k in K_DENSE if cell[str(k)]["mean"] > FIT_WINDOW_MIN]
    idx = [K_DENSE.index(k) for k in ks]
    WIN[sc], IDX[sc] = np.array(ks, dtype=float), idx
    sub = CURVES[sc][:, idx]
    MEANS[sc] = sub.mean(axis=0)
    SIGS[sc] = sub.std(axis=0, ddof=1) / np.sqrt(R)
    SRAW[sc] = np.cov(sub, rowvar=False) / R

# ---- C1: is the diagnosed correlation there at all? ----
corr = {}
for sc in ("iid", "gue"):
    Cc = np.corrcoef(CURVES[sc][:, IDX[sc]], rowvar=False)
    off = np.abs(Cc[np.triu_indices_from(Cc, k=1)])
    corr[sc] = banked(f"|pearson r| across fit-window k-pairs ({sc})",
                      off.tolist(), kind="median")
med_gue = corr["gue"]["value"]
C1 = Bar("median |pearson r| over fit-window k-pairs, GUE", 0.5,
         floor=0.0, ceiling=1.0,
         why="a median of absolute correlations, 0 to 1, bar strictly inside")
c1 = C1.score(med_gue)

# ---- the diagonal (sealed) reference fits, recomputed from recovered data ----
indep = {}
for sc in ("iid", "gue"):
    chi2, p, cov = sealed_fit(MEANS[sc], SIGS[sc], WIN[sc])
    indep[sc] = dict(p=p, cov=cov, chi2=chi2, dof=len(WIN[sc]) - 3)

# ---- PRIMARY: bootstrap over replicates, both window rules ----
rng = np.random.default_rng(BOOT_SEED)
boot = {}
for rule in ("sealed_fixed", "per_resample"):
    boot[rule] = {}
    for sc in ("iid", "gue"):
        taus, betas, nform = [], [], 0
        for _ in range(B_BOOT):
            pick = rng.integers(0, R, R)
            sub_full = CURVES[sc][pick, :]
            if rule == "sealed_fixed":
                idx = IDX[sc]
            else:
                mfull = sub_full.mean(axis=0)
                idx = [j for j in range(len(K_DENSE)) if mfull[j] > FIT_WINDOW_MIN]
                if len(idx) < 5:
                    continue
            sub = sub_full[:, idx]
            ks = np.array([K_DENSE[j] for j in idx], dtype=float)
            m = sub.mean(axis=0)
            s = sub.std(axis=0, ddof=1) / np.sqrt(R)
            if np.any(m <= 0) or np.any(s <= 0):
                continue
            fit = sealed_fit(m, s, ks)
            if fit is None:
                continue
            nform += 1
            taus.append(fit[1][1])
            betas.append(fit[1][2])
        boot[rule][sc] = dict(
            tau=banked(f"bootstrap tau ({sc}, {rule})", taus, kind="mean"),
            beta=banked(f"bootstrap beta ({sc}, {rule})", betas, kind="mean"),
            se_tau=float(np.std(taus, ddof=1)), se_beta=float(np.std(betas, ddof=1)),
            n_ok=nform)

PR = "sealed_fixed"
ratio_gue = boot[PR]["gue"]["se_beta"] / float(np.sqrt(indep["gue"]["cov"][2][2]))
ratio_iid = boot[PR]["iid"]["se_beta"] / float(np.sqrt(indep["iid"]["cov"][2][2]))
C2 = Bar("sigma_boot(beta_GUE) / sigma_indep(beta_GUE)", 0.95, direction="le",
         floor=0.0, ceiling=100.0,
         why="a ratio of two standard errors of the same parameter: positive, "
             "and 100 is a stated practical ceiling (a 100x error-bar change "
             "would mean the two estimators are not measuring the same thing)")
c2 = C2.score(ratio_gue)

dp = abs(indep["iid"]["p"][2] - indep["gue"]["p"][2])
z_boot = dp / np.sqrt(boot[PR]["iid"]["se_beta"] ** 2 + boot[PR]["gue"]["se_beta"] ** 2)
z_indep = dp / np.sqrt(indep["iid"]["cov"][2][2] + indep["gue"]["cov"][2][2])
C3 = Bar("z_boot(beta)", 5.0, floor=0.0, ceiling=100.0,
         why="the sealed Z_DEPENDENT bar; a z is non-negative and 100 is a "
             "stated practical ceiling")
c3 = C3.score(z_boot)

# ---- SECONDARY: GLS across the shrinkage sweep ----
gls = {}
for a in SHRINK:
    row = {}
    for sc in ("iid", "gue"):
        got = gls_fit(MEANS[sc], SRAW[sc], WIN[sc], a)
        row[sc] = None if got is None else dict(p=got[0].tolist(),
                                                se_beta=float(np.sqrt(got[1][2][2])))
    if row["iid"] and row["gue"]:
        row["z_beta"] = float(dp / np.sqrt(row["iid"]["se_beta"] ** 2
                                           + row["gue"]["se_beta"] ** 2))
    gls[str(a)] = row
zs_gls = [v["z_beta"] for v in gls.values() if "z_beta" in v]
rel = max(abs(z - z_boot) / z_boot for z in zs_gls) if zs_gls else 99.0
C4 = Bar("max |z_gls - z_boot| / z_boot over the shrinkage sweep", 0.25,
         direction="le", floor=0.0, ceiling=100.0,
         why="a relative discrepancy between two error treatments; non-negative, "
             "100 a stated practical ceiling")
c4 = C4.score(rel)

# ---- report ----
print(INSTRUMENT.report())
print(f"\nrecovered {R} replicates x 2 classes at n = {N}; "
      f"P1 mismatches {mismatch} of 80")
print(f"\nfit windows: iid k={[int(k) for k in WIN['iid']]}")
print(f"             gue k={[int(k) for k in WIN['gue']]}")
print("\ncross-k correlation among replicates (the diagnosed mechanism):")
for sc in ("iid", "gue"):
    c = corr[sc]
    print(f"  {sc}: median |r| = {c['value']:.4f}  "
          f"[sd {c['sd']:.4f}, range {c['minimum']:.4f}-{c['maximum']:.4f}, "
          f"n = {c['n']} pairs]")
print(f"\nchi2/dof recomputed: iid {indep['iid']['chi2'] / indep['iid']['dof']:.4f}   "
      f"gue {indep['gue']['chi2'] / indep['gue']['dof']:.4f}")
print(f"\nbeta standard errors  (form F3, window {PR}):")
print(f"  {'':10s} {'sigma_indep':>12s} {'sigma_boot':>12s} {'ratio':>8s}")
for sc, rt in (("iid", ratio_iid), ("gue", ratio_gue)):
    print(f"  {sc:10s} {np.sqrt(indep[sc]['cov'][2][2]):12.6f} "
          f"{boot[PR][sc]['se_beta']:12.6f} {rt:8.3f}")
print(f"\n  z(beta): sealed-recomputed {z_indep:.4f}   bootstrap {z_boot:.4f}   "
      f"conservative(banked convention) 5.8411")
print("  GLS across shrinkage: " + ", ".join(
    f"a={a}: z={gls[str(a)].get('z_beta', float('nan')):.3f}" for a in SHRINK))
print("\n  window-rule sensitivity (bootstrap se_beta):")
for rule in ("sealed_fixed", "per_resample"):
    print(f"    {rule:14s} iid {boot[rule]['iid']['se_beta']:.6f}  "
          f"gue {boot[rule]['gue']['se_beta']:.6f}  "
          f"(resamples fitted: {boot[rule]['iid']['n_ok']}/{boot[rule]['gue']['n_ok']})")
print()
for b, v, f in ((P1, mismatch, "{:.0f}"), (C1, med_gue, "{:.4f}"),
                (C2, ratio_gue, "{:.3f}"), (C3, z_boot, "{:.4f}"),
                (C4, rel, "{:.4f}")):
    print("  " + b.line(v, f))

v = compose([Arm.from_bar(p1, PREM_ROLE,
                          claim="the recovered flows ARE the sealed flows"),
             Arm.from_bar(c1, EX_ROLE,
                          claim="the shared-replicate correlation the audit "
                                "diagnosed is present and strong"),
             Arm.from_bar(c2, MECH_ROLE,
                          claim="and it TIGHTENS the shape parameter rather "
                                "than loosening it -- the common mode is "
                                "degenerate with amplitude, not with shape"),
             Arm.from_bar(c3, RES_ROLE,
                          claim="z(beta) clears the sealed 5-sigma bar under "
                                "the honest error model"),
             Arm.from_bar(c4, RES_ROLE,
                          claim="and two independent error treatments agree")],
            holds="SHAPE_Z_SURVIVES_THE_CORRELATED_ERROR_MODEL",
            fails="SHAPE_Z_NOT_ESTABLISHED_UNDER_CORRELATED_ERROR")
print(f"\nVERDICT: {v['citation']}")

json.dump(dict(
    n=N, replicates=R, B=B_BOOT, boot_seed=BOOT_SEED, shrinkage=SHRINK,
    fit_window={sc: [int(k) for k in WIN[sc]] for sc in ("iid", "gue")},
    p1_mismatches=mismatch,
    correlation=corr,
    chi2_over_dof={sc: indep[sc]["chi2"] / indep[sc]["dof"] for sc in ("iid", "gue")},
    indep={sc: dict(params=indep[sc]["p"].tolist(),
                    se_beta=float(np.sqrt(indep[sc]["cov"][2][2])),
                    se_tau=float(np.sqrt(indep[sc]["cov"][1][1])))
           for sc in ("iid", "gue")},
    bootstrap={rule: {sc: {kk: vv for kk, vv in boot[rule][sc].items()}
                      for sc in ("iid", "gue")} for rule in boot},
    gls=gls,
    z={"sealed_recomputed": z_indep, "bootstrap": z_boot,
       "conservative_convention": 5.8410961226, "gls_sweep": zs_gls},
    ratios={"gue": ratio_gue, "iid": ratio_iid},
    bars={s["name"]: s for s in (p1, c1, c2, c3, c4)},
    instrument=INSTRUMENT.seal(),
    scope="n=4096 primary band, form F3 fixed from the sealed adjudication. An "
          "ERROR MODEL for the sealed point estimates: it does not refit the "
          "science and does not touch the sealed verdict.",
    verdict=v["head"], composed=v,
    runtime_s=round(time.time() - t0, 1)),
    open(os.path.join(HERE, "zbeta_correlated_error.json"), "w"), indent=1)
print("\nwrote zbeta_correlated_error.json")
