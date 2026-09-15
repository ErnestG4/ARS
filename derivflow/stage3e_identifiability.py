#!/usr/bin/env python3
"""STAGE 3e — what F3 actually determines, and what it does not.

COMMITTED GENERATOR of derivflow/stage3e_identifiability.json.

WHY THIS RUNS. Will's second review (2026-09-15) made four points that are each
a measurement: (1) the covariance/bootstrap split is "honest about shape vs
honest about scale, neither about both" -- pick no winner; (2) GLS chi2/dof is a
DISCRIMINATOR between "the error structure was wrong" and "F3 is wrong as a
function"; (3) the degenerate direction is the measurement -- eigendecompose,
quote z along the constrained combination, and read off what the successor
form should be parameterized in; (4) test whether bootstrap-blindness is
structural or under-resampling before stating it as structural.

All five measurements below were run as diagnostics first and are re-run here
under seal so they can be BANKED and the paper's numerals can be READ from an
artifact rather than typed. DISCLOSED PRIOR LOOK on everything except C3's
short-window rows, which had not finished computing when this file was written
and whose bar is therefore a genuine prediction.

NO FLOWS. Everything refits the per-replicate curves Stage 3 banked.

LINEAGE. Shares with 3b/3c/3d the data, fitter and window rule. Shares nothing
on the parameterization or the error-model decomposition, which are the axes
under test. A correction to and extension of those cells, not corroboration.

╔══════════════════════════════════════════════════════════════════════════════╗
║ SEALED PREDICTIONS — every bar strictly inside its stated range.             ║
║                                                                              ║
║ P1  PREMISE     the banked curves reproduce science_dense_grid at n=4096:    ║
║                 mismatches <= 0.5 of 80.                                     ║
║ P2  PREMISE     k* FITTED DIRECTLY in the (lambda, beta, k*) form            ║
║                 reproduces the k* previously DERIVED from (lambda, tau,      ║
║                 beta), to within 1.0 of the direct fit's own standard error, ║
║                 both classes. If the reparameterization does not land on     ║
║                 the sealed k*, it is a different quantity and nothing about  ║
║                 identifiability transfers.                                   ║
║ C1  EXISTENCE   THE OVER-PARAMETERIZATION IS tau: in the (lambda, beta,      ║
║                 k*) form, max |corr(beta, k*)| over both classes at the       ║
║                 sealed window <= 0.80, against 0.98-0.99 for (tau, beta) in  ║
║                 the native form. MET composes                                ║
║                 TAU_IS_THE_OVERPARAMETERIZATION. MISSED means the degeneracy ║
║                 survives reparameterization and is not tau's alone.          ║
║ C2  MECHANISM   F3 IS WRONG AS A FUNCTION FOR iid, NOT MERELY MIS-WEIGHTED:  ║
║                 GLS chi2/dof >= OLS chi2/dof for iid at EVERY shrinkage in   ║
║                 {0.05, 0.1, 0.2, 0.4} (4 of 4). If carrying the correlation  ║
║                 brought chi2/dof toward 1 the misfit was in the error         ║
║                 structure; if it does not, no weighting rescues the form.    ║
║ C3  RESOLUTION  BOOTSTRAP-BLINDNESS AT THE SHORT WINDOW IS STRUCTURAL: the   ║
║                 bootstrap cloud's |corr(tau, beta)| at B=8000 on the         ║
║                 k=5..11 window stays <= 0.95 for both classes, against the   ║
║                 covariance's 0.999. MET means the bootstrap genuinely does   ║
║                 not resolve the flat direction there and the claim is        ║
║                 earned. MISSED means it was under-resampling, a smaller      ║
║                 finding, and the earlier "blind" language is withdrawn.      ║
║                 NOT SEEN before sealing.                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import curve_fit, least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from reachable import Bar                                            # noqa: E402
from verdictlattice import (Arm, compose, PREMISE as PREM_ROLE,      # noqa: E402
                            EXISTENCE as EX_ROLE,
                            MECHANISM as MECH_ROLE, RESOLUTION as RES_ROLE)
from modelparams import Model, Param, TESTED, DECLARED               # noqa: E402
from lineage import Lineage                                          # noqa: E402
from errormodel import degeneracy_of                                 # noqa: E402
from science_rate_question import f3, LN10, KSTAR_LEVEL, FIT_WINDOW_MIN  # noqa: E402

N, R = 4096, 16
SHRINK = [0.05, 0.1, 0.2, 0.4]
B_SWEEP = [400, 2000, 8000]
SYN_RANGES = [11, 16, 64, 256]
SEED = 20260915
L10E = np.log10(np.e)
Y0 = np.log10(KSTAR_LEVEL)

INSTRUMENT = Model("identifiability of F3's shape parameters", [
    Param("parameterization", TESTED, sweep=["(lambda,tau,beta)", "(lambda,beta,kstar)"],
          why="THE axis. Native F3 vs F3 with tau eliminated through the level "
              "crossing, so the (beta, k*) pair can be judged for conditioning "
              "against the (tau, beta) pair"),
    Param("gls_shrinkage", TESTED, sweep=SHRINK,
          why="the sample covariance at R=16 over a 16-point window is "
              "rank-deficient, so a shrinkage is forced; the discriminator must "
              "hold across the sweep or it holds at a choice"),
    Param("bootstrap_B", TESTED, sweep=B_SWEEP,
          why="the structural-vs-under-resampling question IS a question about "
              "B; a single B cannot answer it"),
    Param("synthetic_range", TESTED, sweep=SYN_RANGES,
          why="whether the native degeneracy is a window effect is tested on "
              "exact-F3 data over increasing ranges, up to 22 decades"),
    Param("degeneracy_threshold", DECLARED, value=0.95,
          why="the fork's declared threshold (verify_errormodel); carried "
              "verbatim so this cell and the fork agree on what degenerate means"),
    Param("n", DECLARED, value=N, why="the adjudicated size"),
])


def f3k(k, lam, beta, kstar):
    return lam - (lam - Y0) * (k / kstar) ** beta


def fit_native(mu, sg, ks):
    y, sy = np.log10(mu), sg / (mu * LN10)
    best = None
    for t in (2.0, 5.0, 10.0, 30.0):
        for b in (0.5, 0.75, 1.0):
            try:
                p, cov = curve_fit(f3, ks, y, p0=[y[0], t, b], sigma=sy,
                                   absolute_sigma=True,
                                   bounds=([-np.inf, 1e-3, 0.05], [np.inf, 1e4, 3.0]),
                                   maxfev=20000)
                c2 = float(np.sum(((y - f3(ks, *p)) / sy) ** 2))
                if np.isfinite(c2) and (best is None or c2 < best[0]):
                    best = (c2, p, cov)
            except Exception:
                pass
    return best


def fit_kstar(mu, sg, ks):
    y, sy = np.log10(mu), sg / (mu * LN10)
    best = None
    for b in (0.5, 0.75, 1.0):
        for k0 in (4.0, 8.0, 12.0):
            try:
                p, cov = curve_fit(f3k, ks, y, p0=[y[0], b, k0], sigma=sy,
                                   absolute_sigma=True,
                                   bounds=([-np.inf, 0.05, 0.5], [np.inf, 3.0, 200.0]),
                                   maxfev=20000)
                c2 = float(np.sum(((y - f3k(ks, *p)) / sy) ** 2))
                if np.isfinite(c2) and (best is None or c2 < best[0]):
                    best = (c2, p, cov)
            except Exception:
                pass
    return best


def kstar_from_native(p):
    return p[1] * ((p[0] - Y0) / L10E) ** (1.0 / p[2])


t0 = time.time()
s3 = json.load(open(os.path.join(HERE, "stage3_commensurable_window.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))
KA = np.array(s3["k_grid"], float)
cur = {sc: np.array(s3["per_replicate_curves"][sc]) for sc in ("iid", "gue")}
mu = {sc: cur[sc].mean(axis=0) for sc in cur}
sg = {sc: cur[sc].std(axis=0, ddof=1) / np.sqrt(R) for sc in cur}
W = {sc: mu[sc] > FIT_WINDOW_MIN for sc in cur}
W5 = (KA >= 5) & (KA <= 11)

# ---- P1 ----
p1 = 0
for sc in cur:
    cell = bank["data"][sc][str(N)]
    for j, k in enumerate(s3["k_grid"]):
        for got, want in ((mu[sc][j], cell[str(k)]["mean"]), (sg[sc][j], cell[str(k)]["sigma_mean"])):
            if abs(got - want) > 1e-12 * max(abs(want), 1e-300):
                p1 += 1
P1 = Bar("banked-curve mismatches vs the sealed ensemble (80 numbers)", 0.5,
         floor=0, ceiling=80, direction="le", why="2 x 20 x {mean, sigma}; 0..80")
b1 = P1.score(p1)

# ---- native and reparameterized fits at the sealed window ----
nat = {sc: fit_native(mu[sc][W[sc]], sg[sc][W[sc]], KA[W[sc]]) for sc in cur}
rep = {sc: fit_kstar(mu[sc][W[sc]], sg[sc][W[sc]], KA[W[sc]]) for sc in cur}
nat5 = {sc: fit_native(mu[sc][W5], sg[sc][W5], KA[W5]) for sc in cur}
rep5 = {sc: fit_kstar(mu[sc][W5], sg[sc][W5], KA[W5]) for sc in cur}

# ---- P2: direct k* reproduces derived k* ----
p2_worst = 0.0
for sc in cur:
    k_direct, se_direct = rep[sc][1][2], np.sqrt(rep[sc][2][2, 2])
    k_derived = kstar_from_native(nat[sc][1])
    p2_worst = max(p2_worst, abs(k_direct - k_derived) / max(se_direct, 1e-300))
P2 = Bar("worst |k* direct - k* derived| in units of the direct fit's own sigma",
         1.0, floor=0.0, ceiling=100.0, direction="le",
         why="a discrepancy in the fit's own uncertainty; 100 a practical ceiling. "
             "1.0 sigma is a genuine reproduction bar for two parameterizations "
             "of the same curve at the same window")
b2 = P2.score(float(p2_worst))

# ---- C1: the reparameterization de-degenerates ----
corr_nat = {sc: degeneracy_of(nat[sc][2]) for sc in cur}
corr_rep = {sc: abs(rep[sc][2][1, 2] / np.sqrt(rep[sc][2][1, 1] * rep[sc][2][2, 2])) for sc in cur}
worst_rep = {sc: degeneracy_of(rep[sc][2], (0, 1, 2)) for sc in cur}
C1 = Bar("max over classes of |corr(beta, k*)| at the sealed window", 0.80,
         floor=0.0, ceiling=1.0, direction="le",
         why="a correlation magnitude, [0,1] by construction; 0.80 is well below "
             "the native 0.98-0.99 and well above what noise would give on two "
             "genuinely orthogonal parameters")
c1 = C1.score(float(max(corr_rep.values())))

# ---- eigendecomposition of the class difference (readout) ----
d = np.array([nat["iid"][1][1] - nat["gue"][1][1], nat["iid"][1][2] - nat["gue"][1][2]])
Bsum = nat["iid"][2][1:, 1:] + nat["gue"][2][1:, 1:]
lam_e, V = np.linalg.eigh(Bsum)
eig = {}
for i, lab in ((0, "constrained"), (1, "flat")):
    proj = float(d @ V[:, i])
    eig[lab] = dict(direction=[float(V[0, i]), float(V[1, i])], delta=proj,
                    se=float(np.sqrt(lam_e[i])), z=float(abs(proj) / np.sqrt(lam_e[i])))
eig["mahalanobis_z"] = float(np.sqrt(d @ np.linalg.solve(Bsum, d)))
eig["marginal_z"] = dict(
    tau=float(abs(d[0]) / np.hypot(np.sqrt(nat["iid"][2][1, 1]), np.sqrt(nat["gue"][2][1, 1]))),
    beta=float(abs(d[1]) / np.hypot(np.sqrt(nat["iid"][2][2, 2]), np.sqrt(nat["gue"][2][2, 2]))))
per_class_eig = {}
for sc in cur:
    Bc = nat[sc][2][1:, 1:]
    le, Vc = np.linalg.eigh(Bc)
    per_class_eig[sc] = dict(
        constrained=dict(direction=[float(Vc[0, 0]), float(Vc[1, 0])], sd=float(np.sqrt(le[0]))),
        flat=dict(direction=[float(Vc[0, 1]), float(Vc[1, 1])], sd=float(np.sqrt(le[1]))),
        condition=float(np.sqrt(le[1] / le[0])))

# ---- C2: GLS discriminator ----
gls = {}
for sc in cur:
    w = W[sc]
    ks, m = KA[w], mu[sc][w]
    y = np.log10(m)
    S = np.cov(cur[sc][:, w].T) / R
    D = np.diag(1.0 / (m * LN10))
    C = D @ S @ D
    gls[sc] = {}
    for a in SHRINK:
        Ca = (1 - a) * C + a * np.diag(np.diag(C))
        L = np.linalg.cholesky(Ca)

        def resid(p, _L=L, _ks=ks, _y=y):
            return np.linalg.solve(_L, _y - f3(_ks, *p))
        bestg = None
        for t in (2.0, 5.0, 10.0, 30.0):
            for b in (0.5, 0.75, 1.0):
                try:
                    r = least_squares(resid, [y[0], t, b],
                                      bounds=([-np.inf, 1e-3, 0.05], [np.inf, 1e4, 3.0]))
                    if r.success and (bestg is None or r.cost < bestg.cost):
                        bestg = r
                except Exception:
                    pass
        gls[sc][str(a)] = dict(chi2=float(2 * bestg.cost), dof=int(w.sum() - 3),
                               chi2dof=float(2 * bestg.cost / (w.sum() - 3)))
ols_iid = nat["iid"][0] / (W["iid"].sum() - 3)
n_worse = sum(1 for a in SHRINK if gls["iid"][str(a)]["chi2dof"] >= ols_iid)
C2 = Bar("shrinkages at which GLS chi2/dof >= OLS chi2/dof for iid", 3.5,
         floor=0, ceiling=4, direction="ge",
         why="a count over the 4 shrinkages; 3.5 requires all four. If GLS "
             "brought chi2/dof toward 1 at any shrinkage, the misfit would be "
             "attributable to the error structure")
c2 = C2.score(n_worse)

# ---- synthetic range sweep (readout) ----
rng = np.random.default_rng(SEED)
syn = {}
for kmax in SYN_RANGES:
    ks = np.arange(1, kmax + 1, dtype=float)
    y = f3(ks, -0.15, 1.7, 0.79)
    noise = 0.01 * np.ones_like(y)
    yn = y + noise * rng.standard_normal(len(y))
    _, cov = curve_fit(f3, ks, yn, p0=[y[0], 2.0, 0.75], sigma=noise, absolute_sigma=True,
                       bounds=([-np.inf, 1e-3, 0.05], [np.inf, 1e4, 3.0]), maxfev=20000)
    syn[str(kmax)] = dict(points=int(kmax), decades=float(y[0] - y[-1]),
                          corr=float(degeneracy_of(cov)))

# ---- C3: bootstrap cloud correlation vs B, short window ----
print("bootstrap cloud sweep...", flush=True)
cloud = {}
for sc in cur:
    for lab, w in (("sealed", W[sc]), ("k5_11", W5)):
        rng_b = np.random.default_rng(SEED + 1)
        taus, betas = [], []
        cloud[f"{sc}_{lab}"] = {}
        for B in B_SWEEP:
            while len(taus) < B:
                idx = rng_b.integers(0, R, R)
                cs = cur[sc][idx]
                m2 = cs.mean(axis=0)
                s2 = cs.std(axis=0, ddof=1) / np.sqrt(R)
                g = fit_native(m2[w], s2[w], KA[w])
                if g:
                    taus.append(g[1][1])
                    betas.append(g[1][2])
            cloud[f"{sc}_{lab}"][str(B)] = dict(
                corr=float(np.corrcoef(taus, betas)[0, 1]),
                sd_tau=float(np.std(taus, ddof=1)), sd_beta=float(np.std(betas, ddof=1)))
        print(f"  {sc} {lab} done ({time.time() - t0:.0f}s)", flush=True)
cov_corr_short = {sc: degeneracy_of(nat5[sc][2]) for sc in cur}
cloud_short_max = max(cloud[f"{sc}_k5_11"][str(B_SWEEP[-1])]["corr"] for sc in cur)
C3 = Bar("max over classes of bootstrap-cloud |corr(tau,beta)| at B=8000, k=5..11",
         0.95, floor=0.0, ceiling=1.0, direction="le",
         why="a correlation magnitude, [0,1]. The covariance reads 0.999 there. "
             "MET: the bootstrap does not resolve the flat direction and the "
             "'blind' claim is earned. MISSED: it was under-resampling. Bar set "
             "before these rows were seen")
c3 = C3.score(float(cloud_short_max))

print(INSTRUMENT.report())
print(f"\nP1 {p1}/80   P2 worst {p2_worst:.3f} sigma")
print(f"native corr(tau,beta): iid {corr_nat['iid']:.4f} gue {corr_nat['gue']:.4f}")
print(f"reparam corr(beta,k*): iid {corr_rep['iid']:.4f} gue {corr_rep['gue']:.4f}   "
      f"(worst any pair: iid {worst_rep['iid']:.4f} gue {worst_rep['gue']:.4f})")
print(f"k* direct: iid {rep['iid'][1][2]:.4f} gue {rep['gue'][1][2]:.4f}   "
      f"derived: iid {kstar_from_native(nat['iid'][1]):.4f} gue {kstar_from_native(nat['gue'][1]):.4f}")
print(f"\neigen: constrained z {eig['constrained']['z']:.2f}  flat z {eig['flat']['z']:.2f}  "
      f"mahalanobis {eig['mahalanobis_z']:.2f}  (marginal tau {eig['marginal_z']['tau']:.2f} "
      f"beta {eig['marginal_z']['beta']:.2f})")
print(f"GLS chi2/dof iid: OLS {ols_iid:.3f}  " + "  ".join(f"s{a}:{gls['iid'][str(a)]['chi2dof']:.2f}" for a in SHRINK))
print(f"synthetic corr vs range: " + "  ".join(f"{k}:{v['corr']:.4f}" for k, v in syn.items()))
print("bootstrap cloud corr at B=8000: " + "  ".join(
    f"{k}:{v[str(B_SWEEP[-1])]['corr']:.4f}" for k, v in cloud.items()))
print()
for bb, val, f in ((P1, p1, "{:.0f}"), (P2, p2_worst, "{:.3f}"),
                   (C1, max(corr_rep.values()), "{:.4f}"), (C2, n_worse, "{:.0f}"),
                   (C3, cloud_short_max, "{:.4f}")):
    print("  " + bb.line(val, f))

v = compose(
    [Arm.from_bar(b1, PREM_ROLE, claim="the banked curves ARE the sealed ensemble"),
     Arm.from_bar(b2, PREM_ROLE, claim="and direct k* reproduces derived k*"),
     Arm.from_bar(c1, EX_ROLE, claim="tau is the over-parameterization"),
     Arm.from_bar(c2, MECH_ROLE, claim="and F3 is wrong as a function for iid, not mis-weighted"),
     Arm.from_bar(c3, RES_ROLE, claim="and bootstrap-blindness at the short window is structural")],
    holds="TAU_IS_THE_OVERPARAMETERIZATION",
    fails="THE_DEGENERACY_SURVIVES_REPARAMETERIZATION")
print(f"\nVERDICT: {v['citation']}")

lin = Lineage("stage3e_identifiability", construction="none (refit of banked science)",
              data="science per-replicate curves n=4096 (Stage 3 recovery)",
              protocol="F3 native + F3 in (lambda,beta,k*); GLS; replicate bootstrap")
json.dump(dict(
    n=N, replicates=R, shrink=SHRINK, b_sweep=B_SWEEP, syn_ranges=SYN_RANGES,
    p1_mismatches=p1, p2_worst_sigma=float(p2_worst),
    native={sc: dict(params=list(map(float, nat[sc][1])), corr_tau_beta=corr_nat[sc],
                     chi2dof=float(nat[sc][0] / (W[sc].sum() - 3))) for sc in cur},
    reparam={sc: dict(params=list(map(float, rep[sc][1])), corr_beta_kstar=corr_rep[sc],
                      worst_pair=worst_rep[sc], se_kstar=float(np.sqrt(rep[sc][2][2, 2])),
                      kstar_derived=float(kstar_from_native(nat[sc][1]))) for sc in cur},
    short_window={sc: dict(corr_native=cov_corr_short[sc],
                           corr_reparam_worst=degeneracy_of(rep5[sc][2], (0, 1, 2))) for sc in cur},
    eigen=eig, per_class_eigen=per_class_eig, gls=gls, ols_chi2dof_iid=float(ols_iid),
    synthetic=syn, bootstrap_cloud=cloud,
    lineage=lin.record(),
    bars={s["name"]: s for s in (b1, b2, c1, c2, c3)},
    instrument=INSTRUMENT.seal(),
    scope="RECERT_SCOPE Stage 3e. Identifiability of F3's shape parameters, from "
          "banked data. Runs no flows; re-grades nothing. Disclosed prior look on "
          "all but C3's short-window rows.",
    verdict=v["head"], composed=v, runtime_s=round(time.time() - t0, 1),
), open(os.path.join(HERE, "stage3e_identifiability.json"), "w"), indent=1)
print("\nwrote stage3e_identifiability.json")
