# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 pre-seal D2 (a) parametric simulations and the D2 (b) planted witness (Will's go, 2026-11-03).
No h = 2 data. Inputs (pinned by sha256 on the command line): the committed D2 (b) references
(`fn1/results/h2/FN1H2_REFS.json`) and the committed (★) predictions (`fn1/lead/FN1H2_PRED.json`).

**Witness (§9.D) on the h = 1 references, leave-one-out (D1 as accepted: no thinning).** Each h = 1 field j stands in
for an h = 2 field: its reference R_j against the line fitted on the other eight (so the real field-specific scatter
enters). s_j = (R_j − line₋ⱼ(C_j)) / b₋ⱼ; the stand-in gate statistic is mean_j s_j (nine stand-ins).
- Unplanted: must read CONDUCTOR.
- Planted: R_j − [line₋ⱼ(C_j) − line₋ⱼ(C_j − log 4)] (the predicted −log 4 shift, injected): must read L-VALUE.
- Its power: the parametric run below at the measured scatter (σ_LOO), so the single realisation is not the evidence.

**Parametric model (200,000 draws per scenario, seed 20261104 + scenario index).** h = 1: R_i = a + b·C_i + μ_i + e_i,
nine fields at their C. h = 2 primary: R_j = a + b·(C_j + s_true) + μ_j + e_j, nine fields at their C_F = log|D|.
μ ~ N(0, σ_μ²) field-specific; e ~ N(0, (m·R̄)²), m = √(2/(cK_P)) the SE model at K_P = 57,801 (1×; L16 measured 0.69×).
The read's rule applied to each draw: OLS line on the h = 1 values, s = mean(R_h2 − line(C))/b̂, three-way at
−0.5545 / −0.8318; VOID if b̂ ≤ 0. b = 0.04551 (stage-2 B055, committed); a cancels.
Scenarios:
- nominal σ_μ = 0.0213 (L16): s_true = 0 (conductor), −log 4 (L-value), −log 4/2 (INCONCLUSIVE reachability);
- stress σ_μ × 1.5 (D2b: disclosed, cuts not widened);
- the measured scatter σ_LOO from the references (sample SD of the LOO residuals, ddof 1);
- −7 excluded from the reference line (eight h = 1 fields);
- "runs in N" (D1 robustness): s_true = (★)'s committed primary mean s under conductor/N and L-value/N (β 0.55);
- curved truth: the h = 1 truth is the references' own OLS quadratic (K0's form) and h = 2 follows it at C_j + s_true,
  so the line's misfit at the h = 2 C enters as a bias; with the quadratic's residual SD (0.009) as field scatter, and
  (added 2026-11-04, Will's 4(a)) with σ_μ = 0.0213 and 1.5 σ_μ.
**D23 (judged at nominal, Will D2b):** P(CONDUCTOR | s_true = 0) ≥ 0.95 and P(L-VALUE | s_true = −log 4) ≥ 0.95.
§9.J: every branch (CONDUCTOR, L-VALUE, INCONCLUSIVE, VOID) reached in some scenario; VOID's rate reported.
**K0 arm (one-way, α 0.05), the read's form (one-sided t, 6 df, on the h = 2 quadratic coefficient with the sign of
the h = 1 quadratic's):** null (linear truth + σ_μ): false-PASS rate (target 0.05); planted (truth = the references'
quadratic; residual SD = the quadratic fit's residual SD, ddof 3, and separately σ_μ): PASS rate (reachability).
The two rejected Spearman forms are reported too (their null rates exceeded 0.05 in the smoke run). 20,000 draws each.

TOOLKIT §9.I: safeio.enforce(); inputs read with expect_sha256; output to scratch.

  python fn1h2_sim.py REFS_JSON REFS_SHA PRED_JSON PRED_SHA OUT_REL
"""
import math, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import safeio
safeio.enforce()

H1 = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
C1 = np.array([math.log(7), math.log(8), math.log(11), math.log(16), math.log(19), math.log(27), math.log(43),
               math.log(67), math.log(163)])
PRIMARY = [-35, -40, -51, -52, -88, -91, -115, -123, -148]
C2 = np.log(-np.array(PRIMARY, float))
B055 = 0.04550657297146217
SIG_MU = 0.0213
C_SE = 0.6271633049515984
KP = 57801
CUT_C, CUT_L = -0.4 * math.log(4), -0.6 * math.log(4)
NSIM, NK0 = 200_000, 20_000
SEED = 20261104


def ols_batch(x, Y):
    """Row-wise OLS of Y (n_draws × m) on x (m): returns a, b arrays."""
    xm = x.mean(); dx = x - xm
    b = (Y * dx).sum(1) / (dx * dx).sum()
    a = Y.mean(1) - b * xm
    return a, b


def classify(s, b):
    out = np.where(s > CUT_C, 0, np.where(s < CUT_L, 1, 2))
    return np.where(b <= 0, 3, out)                  # 0 CONDUCTOR, 1 L-VALUE, 2 INCONCLUSIVE, 3 VOID


def simulate(seed, s_true, sig_mu, Rbar, h1_mask=None, curve=None):
    rng = np.random.default_rng(seed)
    e_sd = math.sqrt(2 / (C_SE * KP)) * Rbar
    x1 = C1 if h1_mask is None else C1[h1_mask]
    f1 = (lambda c: B055 * c) if curve is None else (lambda c: curve[0] + curve[1] * c + curve[2] * c * c)
    Y1 = f1(x1)[None, :] + rng.normal(0, sig_mu, (NSIM, len(x1))) + rng.normal(0, e_sd, (NSIM, len(x1)))
    Y2 = f1(C2 + s_true)[None, :] + rng.normal(0, sig_mu, (NSIM, 9)) + rng.normal(0, e_sd, (NSIM, 9))
    a, b = ols_batch(x1, Y1)
    s = (Y2 - a[:, None] - b[:, None] * C2[None, :]).mean(1) / b
    cl = classify(s, b)
    return dict(s_true=s_true, sig_mu=sig_mu, median_s=float(np.median(s[b > 0])),
                sd_s_robust=float(np.subtract(*np.percentile(s[b > 0], [75, 25])) / 1.349),
                P_CONDUCTOR=float((cl == 0).mean()), P_LVALUE=float((cl == 1).mean()),
                P_INCONCLUSIVE=float((cl == 2).mean()), P_VOID=float((cl == 3).mean()))


def null_counts():
    import itertools
    r0 = np.arange(9)
    d2 = [int(((np.array(p) - r0) ** 2).sum()) for p in itertools.permutations(range(9))]
    return np.bincount(np.array(d2))


T95_6 = 1.9431802803927816


def k0_t(y1, y2):
    q = np.polyfit(C1, y1, 2)[0]
    A = np.vstack([np.ones(9), C2, C2 * C2]).T
    coef = np.linalg.lstsq(A, y2, rcond=None)[0]
    se = math.sqrt(((y2 - A @ coef) ** 2).sum() / 6 * np.linalg.inv(A.T @ A)[2, 2])
    return np.sign(q) * coef[2] / se


def k0_rates(seed, curve, resid_sd, sig_mu, Rbar, planted, form="t"):
    rng = np.random.default_rng(seed)
    e_sd = math.sqrt(2 / (C_SE * KP)) * Rbar
    hits = 0
    for _ in range(NK0):
        if planted:
            f = lambda c: curve[0] + curve[1] * c + curve[2] * c * c
            y1 = f(C1) + rng.normal(0, resid_sd, 9) + rng.normal(0, e_sd, 9)
            y2 = f(C2) + rng.normal(0, resid_sd, 9) + rng.normal(0, e_sd, 9)
        else:
            y1 = B055 * C1 + rng.normal(0, sig_mu, 9) + rng.normal(0, e_sd, 9)
            y2 = B055 * C2 + rng.normal(0, sig_mu, 9) + rng.normal(0, e_sd, 9)
        if form == "t":
            hits += k0_t(y1, y2) > T95_6
            continue
        A = np.vstack([np.ones(9), C1]).T
        a, b = np.linalg.lstsq(A, y1, rcond=None)[0]
        if b <= 0:
            continue
        q = np.linalg.lstsq(np.vstack([np.ones(9), C1, C1 * C1]).T, y1, rcond=None)[0]
        s = (y2 - a - b * C2).mean() / b
        xs = C2 + s
        pred = q[0] + q[1] * xs + q[2] * xs * xs - (a + b * xs)
        obs = y2 - (a + b * xs)
        if form == "spearman_detrended":
            pred = pred - np.polyval(np.polyfit(C2, pred, 1), C2)
            obs = obs - np.polyval(np.polyfit(C2, obs, 1), C2)
        d2 = int(((np.argsort(np.argsort(pred)) - np.argsort(np.argsort(obs))) ** 2).sum())
        hits += (CDF[d2] < ALPHA) and (1 - 6 * d2 / 720) > 0
    return hits / NK0


ALPHA = 0.05
CDF = None


def main(refs_path, refs_sha, pred_path, pred_sha, out):
    refs = safeio.read_json(refs_path, expect_sha256=refs_sha)["h1_refs"]
    pred = safeio.read_json(pred_path, expect_sha256=pred_sha)
    R1 = np.array([refs[f]["R"]["0.55"] for f in H1])
    Rbar = float(R1.mean())
    res = dict(label="FN1-h2 pre-seal D2 (a) parametric simulations and D2 (b) planted witness (no h = 2 data)",
               inputs=dict(refs_sha256=refs_sha, pred_sha256=pred_sha), constants=dict(
                   B055=B055, sig_mu=SIG_MU, K_P=KP, C_SE=C_SE, cuts=[CUT_C, CUT_L], NSIM=NSIM, NK0=NK0, seed=SEED))
    # witness (LOO)
    sj, sj_pl, resid = [], [], []
    for j in range(9):
        m = np.arange(9) != j
        b, a = np.polyfit(C1[m], R1[m], 1)
        r = R1[j] - (a + b * C1[j])
        resid.append(r)
        sj.append(r / b)
        planted = R1[j] - ((a + b * C1[j]) - (a + b * (C1[j] - math.log(4))))
        sj_pl.append((planted - (a + b * C1[j])) / b)
    s_un, s_pl = float(np.mean(sj)), float(np.mean(sj_pl))
    lab = lambda s: "CONDUCTOR" if s > CUT_C else ("L-VALUE" if s < CUT_L else "INCONCLUSIVE")
    sig_loo = float(np.std(resid, ddof=1))
    res["witness_LOO"] = dict(s_j=dict(zip(H1, sj)), resid_j=dict(zip(H1, resid)), s_unplanted=s_un,
                              s_planted=s_pl, reads_unplanted=lab(s_un), reads_planted=lab(s_pl),
                              gate_ok=lab(s_un) == "CONDUCTOR" and lab(s_pl) == "L-VALUE", sigma_LOO=sig_loo)
    # parametric scenarios
    sN = pred["h2"]["0.55_primary_mean_s"]
    q = np.polyfit(C1, R1, 2)[::-1]                    # a2, b2, c2
    qres = R1 - (q[0] + q[1] * C1 + q[2] * C1 * C1)
    resid_sd_q = float(math.sqrt((qres ** 2).sum() / 6))
    L4 = math.log(4)
    sc = [("nominal conductor", 0.0, SIG_MU, None, None), ("nominal L-value", -L4, SIG_MU, None, None),
          ("nominal midpoint", -L4 / 2, SIG_MU, None, None),
          ("stress x1.5 conductor", 0.0, 1.5 * SIG_MU, None, None), ("stress x1.5 L-value", -L4, 1.5 * SIG_MU, None, None),
          ("measured scatter conductor", 0.0, sig_loo, None, None), ("measured scatter L-value", -L4, sig_loo, None, None),
          ("no -7 conductor", 0.0, SIG_MU, np.arange(9) != 0, None), ("no -7 L-value", -L4, SIG_MU, np.arange(9) != 0, None),
          ("runs in N conductor", sN["conductor_N"], SIG_MU, None, None),
          ("runs in N L-value", sN["Lvalue_N"], SIG_MU, None, None),
          ("curved truth conductor", 0.0, resid_sd_q, None, q), ("curved truth L-value", -L4, resid_sd_q, None, q),
          ("zero slope (VOID reachability)", 0.0, SIG_MU, None, (0.8, 0.0, 0.0)),
          # added 2026-11-04 for Will's 4(a), appended so earlier rows keep their seeds:
          ("curved truth, sigma_mu 0.0213: conductor", 0.0, SIG_MU, None, q),
          ("curved truth, sigma_mu 0.0213: L-value", -L4, SIG_MU, None, q),
          ("curved truth, sigma_mu x1.5: conductor", 0.0, 1.5 * SIG_MU, None, q),
          ("curved truth, sigma_mu x1.5: L-value", -L4, 1.5 * SIG_MU, None, q)]
    res["scenarios"] = {}
    for i, (name, st, sg, mask, curve) in enumerate(sc):
        res["scenarios"][name] = simulate(SEED + i, st, sg, Rbar, mask, curve)
    S = res["scenarios"]
    res["D23_nominal"] = dict(conductor=S["nominal conductor"]["P_CONDUCTOR"], Lvalue=S["nominal L-value"]["P_LVALUE"],
                              meets_095=S["nominal conductor"]["P_CONDUCTOR"] >= 0.95 and S["nominal L-value"]["P_LVALUE"] >= 0.95)
    res["reachable"] = {k: any(v[f"P_{k}"] > 0 for v in S.values()) for k in ("CONDUCTOR", "LVALUE", "INCONCLUSIVE", "VOID")}
    res["references_quadratic"] = dict(coef=[float(v) for v in q], resid_sd=resid_sd_q)
    global CDF
    counts = null_counts()
    CDF = np.cumsum(counts) / counts.sum()
    res["K0"] = dict(form="one-sided t on the h = 2 quadratic coefficient, sign from the h = 1 quadratic (6 df)",
                     null_false_PASS=k0_rates(SEED + 100, None, None, SIG_MU, Rbar, False),
                     planted_PASS=k0_rates(SEED + 101, q, resid_sd_q, SIG_MU, Rbar, True),
                     planted_PASS_at_sig_mu=k0_rates(SEED + 102, q, SIG_MU, SIG_MU, Rbar, True))
    res["K0_rejected_forms"] = {
        "spearman_about_h1_line (draft)": dict(
            null_false_PASS=k0_rates(SEED + 100, None, None, SIG_MU, Rbar, False, "spearman"),
            planted_PASS=k0_rates(SEED + 101, q, resid_sd_q, SIG_MU, Rbar, True, "spearman")),
        "spearman_detrended_within_h2": dict(
            null_false_PASS=k0_rates(SEED + 100, None, None, SIG_MU, Rbar, False, "spearman_detrended"),
            planted_PASS=k0_rates(SEED + 101, q, resid_sd_q, SIG_MU, Rbar, True, "spearman_detrended"))}
    p = safeio.write_json(safeio.scratch(out), res, overwrite=True)
    print("written", p)
    print("witness", res["witness_LOO"]["s_unplanted"], res["witness_LOO"]["reads_unplanted"],
          res["witness_LOO"]["s_planted"], res["witness_LOO"]["reads_planted"], "sigma_LOO", sig_loo)
    for k, v in S.items():
        print("%-34s s_true %+.3f sd_s %.3f  C %.4f  L %.4f  I %.4f  V %.4f" % (
            k, v["s_true"], v["sd_s_robust"], v["P_CONDUCTOR"], v["P_LVALUE"], v["P_INCONCLUSIVE"], v["P_VOID"]))
    print("D23 nominal", res["D23_nominal"], "reachable", res["reachable"], "K0", res["K0"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
