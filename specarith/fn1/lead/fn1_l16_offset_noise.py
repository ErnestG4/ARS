# SPDX-License-Identifier: AGPL-3.0-or-later
"""L16 (post hoc, labelled, descriptive only): real noise from the stage-1 and stage-2 offset differences.

Will's brief (2026-11-03): "the offsets from the β 0.55 fitted line reproduce at +0.977 across stages, so the scatter is
field-specific and a second variable is acting. ... Descriptive only: estimate the real noise from the stage-1 and
stage-2 offset differences, scaling for the 8× size, and compare it with the SE model."

Method (committed before running):
- Inputs: the sealed reads, read-only and pinned. Stage 1 is results/read/READ1.json (sha256 47c19dd2…), rows
  [0, n₁) with n₁ = 227,524,967. Stage 2 is results/stage2/read/READ1.json (sha256 440c7f87…), the fresh slice with
  n₂ = 1,831,501,147 (8.05× n₁). The rows are disjoint.
- Offsets, per stage s, at β 0.55 (primary): the OLS residuals of R_F on C_F over the nine fields, in relative
  units, e_s,F = resid_s,F / mean_F R_s. Relative units are used because the R level differs between stages and the
  SE model is relative. Cross-check: corr(e₁, e₂) must reproduce the read's sealed descriptive +0.977.
- Model: e_s,F = μ_F + ε_s,F. μ_F is the field-specific part, common to both stages. ε_s,F is independent noise with
  relSD σ_s.
- d_F = e₂,F − e₁,F. This is the OLS residual of (R₂/R̄₂ − R₁/R̄₁) on C_F, so σ̂_d² = Σ d_F² / 7 (9 − 2 df), and
  E σ̂_d² = σ₁² + σ₂² under the model.
- **Scaling for the 8× size, primary:** the SE model's own. σ_s = r · m_s, with m_s = √(2/(c K_s)), c = 0.627163,
  and K_s the stage's K at β 0.55 (from each read). Then r̂ = σ̂_d / √(m₁² + m₂²): the real-to-model noise ratio
  implied by the offset differences. r̂ = 1 means the SE model is right.
- **Sensitivity (descriptive):**
  (a) 1/√n scaling: σ₂ = σ₁ √(n₁/n₂). This gives r₁ = σ̂_d / (m₁ √(1 + n₁/n₂)) and the implied r₂ = r₁ m₁ √(n₁/n₂)/m₂.
  (b) Absolute units: e in R units against m_s · R̄_s.
  (c) The same computation at β 0.45 and β 0.40 (Will named β 0.55; these rows are extra and descriptive).
- Interval: the χ²₇ 90% interval for σ_d, carried to r̂ (it assumes normal noise and nine fields).
- The common part: σ̂_μ² = Σ e₁,F e₂,F / 7, its share of the offset variance, and r̂ compared with the read-time raw
  and detrended ratios (stage 1: 3.37 / 1.71; stage 2: 4.40 / 2.25).
- Caveat, stated in advance: if μ_F changes between the slices (R drifts along prime order in all nine fields), that
  change lands in d_F and raises r̂. So r̂ bounds the pure noise from above, under this model.
Output to scratch (TOOLKIT §9.I). No verdict.

  python fn1_l16_offset_noise.py OUT_REL
"""
import math, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_H, ".."), os.path.join(_H, "..", "..")]
import safeio
safeio.enforce()
import numpy as np
from scipy import stats

S1 = (os.path.join(_H, "..", "results", "read", "READ1.json"),
      "47c19dd26aaf3e892c01928f708c6b7032b61a5a8012dbdce7e3198dcfac4c76")
S2 = (os.path.join(_H, "..", "results", "stage2", "read", "READ1.json"),
      "440c7f87f341cbe66f35a15f5e3163e864a45ee620192613392cd080eec3c128")
C_SE = 0.6271633049515984
FIELDS = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
CF = {"-7": math.log(7), "-8": math.log(8), "-11": math.log(11), "zi": math.log(16), "-19": math.log(19),
      "zw": math.log(27), "-43": math.log(43), "-67": math.log(67), "-163": math.log(163)}
RAWDET = {"0.55": (3.373, 1.708), "0.45": (1.469, 1.056), "0.4": (1.027, 0.834)}  # stage-1 raw / detrended (seal §3)


def resid(y):
    x = np.array([CF[f] for f in FIELDS])
    A = np.vstack([np.ones_like(x), x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ coef


def one_beta(r1, r2, b):
    y1 = np.array([r1["R"][f][b] for f in FIELDS]); y2 = np.array([r2["R"][f][b] for f in FIELDS])
    m1b, m2b = y1.mean(), y2.mean()
    K1, K2 = r1["K"][b], r2["K"][b]
    m1, m2 = math.sqrt(2 / (C_SE * K1)), math.sqrt(2 / (C_SE * K2))
    n1, n2 = r1["n"], r2["n"]
    lo, hi = (math.sqrt(7 / stats.chi2.ppf(q, 7)) for q in (0.95, 0.05))
    out = dict(K1=K1, K2=K2, model_rel_1=m1, model_rel_2=m2, n_ratio=n2 / n1)
    for unit, e1, e2, s1, s2 in (("relative", resid(y1) / m1b, resid(y2) / m2b, m1, m2),
                                 ("absolute", resid(y1), resid(y2), m1 * m1b, m2 * m2b)):
        d = e2 - e1
        sd_d = math.sqrt(float((d ** 2).sum()) / 7)
        r_hat = sd_d / math.hypot(s1, s2)
        r1n = sd_d / (s1 * math.sqrt(1 + n1 / n2))
        mu2 = float((e1 * e2).sum()) / 7
        var1, var2 = float((e1 ** 2).sum()) / 7, float((e2 ** 2).sum()) / 7
        out[unit] = dict(
            corr_e1_e2=float(np.corrcoef(e1, e2)[0, 1]),
            sd_e1=math.sqrt(var1), sd_e2=math.sqrt(var2), sd_d=sd_d,
            offsets_1=dict(zip(FIELDS, e1.tolist())), offsets_2=dict(zip(FIELDS, e2.tolist())),
            diffs=dict(zip(FIELDS, d.tolist())),
            r_hat_SEmodel_scaling=r_hat, r_hat_90=[r_hat * lo, r_hat * hi],
            sens_inv_sqrt_n=dict(r1=r1n, r2_implied=r1n * s1 * math.sqrt(n1 / n2) / s2),
            sd_mu=math.sqrt(mu2) if mu2 > 0 else None,
            mu_share_stage1=mu2 / var1, mu_share_stage2=mu2 / var2)
    out["readtime_ratio_stage1_raw_det"] = RAWDET[b]
    out["readtime_ratio_stage2_raw_det"] = [r2["read_time_noise"][b]["noise_ratio_to_sealed_model"],
                                            r2["read_time_noise"][b]["noise_ratio_detrended"]]
    return out


def main(out_rel):
    r1 = safeio.read_json(S1[0], expect_sha256=S1[1])
    r2 = safeio.read_json(S2[0], expect_sha256=S2[1])
    res = {"label": "L16 (post hoc, labelled, descriptive): real noise from the stage-1/stage-2 offset differences",
           "beta": {b: one_beta(r1, r2, b) for b in ("0.55", "0.45", "0.4")}}
    sealed = r2["tests"]["0.55"]["ols_C"]["pearson_with_stage1_resid"]
    got = res["beta"]["0.55"]["absolute"]["corr_e1_e2"]
    res["crosscheck_corr_vs_sealed"] = dict(sealed=sealed, here_absolute=got, ok=bool(abs(sealed - got) < 1e-9))
    p = safeio.write_json(safeio.scratch(out_rel), res, overwrite=True)
    print("written", p)
    print("crosscheck", res["crosscheck_corr_vs_sealed"])
    for b, o in res["beta"].items():
        for u in ("relative", "absolute"):
            q = o[u]
            print(b, u, "corr %.3f sd_d %.5f r_hat %.3f [%.3f, %.3f] inv_sqrt_n r1 %.3f r2 %.3f sd_mu %s share1 %.3f share2 %.3f"
                  % (q["corr_e1_e2"], q["sd_d"], q["r_hat_SEmodel_scaling"], *q["r_hat_90"],
                     q["sens_inv_sqrt_n"]["r1"], q["sens_inv_sqrt_n"]["r2_implied"],
                     None if q["sd_mu"] is None else round(q["sd_mu"], 5), q["mu_share_stage1"], q["mu_share_stage2"]))
        print(b, "K", o["K1"], o["K2"], "model", round(o["model_rel_1"], 5), round(o["model_rel_2"], 5),
              "readtime s1", o["readtime_ratio_stage1_raw_det"], "s2", [round(x, 3) for x in o["readtime_ratio_stage2_raw_det"]])
    return 0 if res["crosscheck_corr_vs_sealed"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
