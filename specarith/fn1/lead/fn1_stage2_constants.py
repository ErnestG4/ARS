# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 constants and pre-seal power table (design; seen stage-1 data only; TOOLKIT §9.I: inputs read-only and
pinned, output to scratch). The values become the frozen CONST block of fn1_read2.py.

  python fn1_stage2_constants.py READ1 CHEN_LTERM SEGNOISE_BETAS OUT_REL

From the sealed stage-1 read (READ1.json, sha256 pinned below):
- B[β]: nine-field OLS slope of R on C_F (stage-1); SE[β] = mean_F R_F(β) × √(2/(c K₂(β))) at the stage-2 K;
- STAGE1_RESID[β], DELTA7 = the −7 residual at β 0.55;
- DRIFT: per-field drift_total_rel = fitted slope of the 8 stage-1 R_seg (β 0.55) × 7 / mean. Two across-field
  spreads: RAW = SD over the nine fields; CORRECTED = √max(0, RAW² − mean_F var(slope estimate)), where the slope
  estimate's variance is from each field's own detrended residuals (OLS, ddof 2). Both are reported; which one is
  committed is stated in the seal (Will's review).
- P_noA, P_full from lead/FN1_CHEN_LTERM.json.
Pre-seal tables (parametric; the stage-2 noise is projected as stage-1 ratio × the stage-2 model SE):
- primary and secondaries: power at 1×, the stage-1 raw ratio and the stage-1 detrended ratio at that β, own slopes;
- −7: false-PASS rate and power under persistence at the projected rule noise (both drift choices), and at raw and
  detrended noise alone.
"""
import math, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_H, ".."), os.path.join(_H, "..", "..")]
import safeio
safeio.enforce()
import numpy as np

READ1_SHA = "47c19dd26aaf3e892c01928f708c6b7032b61a5a8012dbdce7e3198dcfac4c76"
FIELDS = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
C = np.array([math.log(v) for v in (7, 8, 11, 16, 19, 27, 43, 67, 163)])
C_SE = 0.6271633049515984
N2 = 3663002294
BETAS = ("0.55", "0.45", "0.4")
K2 = {b: int(round(N2 ** float(b))) for b in BETAS}
NSIM = 200_000

rd = safeio.read_json(sys.argv[1], expect_sha256=READ1_SHA)
ch = safeio.read_json(sys.argv[2])
sb = safeio.read_json(sys.argv[3])
out = {"label": "FN1 stage-2 constants (from seen stage-1 data) and pre-seal power", "K2": K2}
B, SE, RES = {}, {}, {}
for b in BETAS:
    R = np.array([rd["R"][f][b] for f in FIELDS])
    A = np.vstack([np.ones(9), C]).T
    coef = np.linalg.lstsq(A, R, rcond=None)[0]
    B[b] = float(coef[1]); SE[b] = float(R.mean() * math.sqrt(2 / (C_SE * K2[b])))
    RES[b] = dict(zip(FIELDS, (R - A @ coef).tolist()))
x = np.arange(8); sxx = float(((x - x.mean()) ** 2).sum())
drift, vslope = {}, {}
for f in FIELDS:
    r = np.array(rd["read_time_noise"]["per_field"][f]["R_seg"]); m = r.mean()
    fit = np.polyfit(x, r, 1); res = r - np.polyval(fit, x)
    s2 = float((res ** 2).sum() / (8 - 2))
    drift[f] = float(fit[0] * 7 / m)
    vslope[f] = float(s2 / sxx * 49 / m ** 2)
raw_sd = float(np.std(list(drift.values()), ddof=1))
corr_sd = float(math.sqrt(max(0.0, raw_sd ** 2 - np.mean(list(vslope.values())))))
cross = sb["0.55"]["drift_total_rel_acrossfield_SD"]
out["DRIFT"] = dict(per_field=drift, slope_est_var=vslope, RAW_SD=raw_sd, CORRECTED_SD=corr_sd,
                    crosscheck_SEGNOISE_BETAS_raw_SD=cross, crosscheck_ok=bool(abs(cross - raw_sd) < 1e-12),
                    mean_drift=float(np.mean(list(drift.values()))))
P_noA = {f: ch["fields"][f]["P_noA"] for f in FIELDS}; P_full = {f: ch["fields"][f]["P_full"] for f in FIELDS}
out["CONST"] = dict(B=B, SE=SE, DELTA7=RES["0.55"]["-7"], STAGE1_RESID=RES, P_noA=P_noA, P_full=P_full,
                    DRIFT_SD_raw=raw_sd, DRIFT_SD_corrected=corr_sd)

def rank_power(b, se, s, seed):
    rng = np.random.default_rng(seed)
    sim = b * C[None, :] + s * se * rng.standard_normal((NSIM, 9))
    return float((((sim.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1) <= 26).mean())

pw = {}
for i, b in enumerate(BETAS):
    sc = {"1x": 1.0, "stage1_raw": sb[b]["noise_ratio"], "stage1_detrended": sb[b]["noise_ratio_detrended"]}
    pw[b] = {k: dict(scale=v, power=rank_power(B[b], SE[b], v, 20261130 + i)) for k, v in sc.items()}
out["rank_power"] = pw

def m7(bb, sigma, delta, seed):
    rng = np.random.default_rng(seed); e = rng.standard_normal((NSIM, 3)) * sigma
    return float((((bb * C[0] + delta + e[:, 0]) > (bb * C[1] + e[:, 1])) & ((bb * C[0] + delta + e[:, 0]) > (bb * C[2] + e[:, 2]))).mean())

Rbar = float(np.mean([rd["R"][f]["0.55"] for f in FIELDS]))
model_rel2 = math.sqrt(2 / (C_SE * K2["0.55"]))
det_rel2 = sb["0.55"]["noise_ratio_detrended"] * model_rel2
raw_rel2 = sb["0.55"]["noise_ratio"] * model_rel2
m7tab = {}
for nm, srel in (("rule_drift_raw", math.hypot(det_rel2, raw_sd)), ("rule_drift_corrected", math.hypot(det_rel2, corr_sd)),
                 ("raw_only", raw_rel2), ("detrended_only", det_rel2)):
    m7tab[nm] = dict(sigma_rel=srel, false_pass=m7(B["0.55"], srel * Rbar, 0.0, 20261140),
                     power_persist=m7(B["0.55"], srel * Rbar, RES["0.55"]["-7"], 20261141))
out["minus7_projection"] = dict(Rbar_stage1=Rbar, det_rel_projected=det_rel2, raw_rel_projected=raw_rel2, table=m7tab)
p = safeio.write_json(safeio.scratch(sys.argv[4]), out, overwrite=True)
print("written", p)
print("B", {k: round(v, 5) for k, v in B.items()}, "SE", {k: round(v, 5) for k, v in SE.items()}, "DELTA7 %.4f" % RES["0.55"]["-7"])
print("drift per field", {k: round(v, 3) for k, v in drift.items()})
print("DRIFT_SD raw %.4f corrected %.4f (mean slope-est var %.6f; crosscheck %s)" % (raw_sd, corr_sd, np.mean(list(vslope.values())), out["DRIFT"]["crosscheck_ok"]))
for b in BETAS: print("power", b, {k: (round(v["scale"], 2), round(v["power"], 3)) for k, v in pw[b].items()})
for k, v in m7tab.items(): print("-7", k, "sigma_rel %.4f false_pass %.3f power_persist %.3f" % (v["sigma_rel"], v["false_pass"], v["power_persist"]))
