# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 pre-seal power and TOOLKIT §9.J reachability check, RUN 2.
§9.J as clarified by Will (2026-11-02): "every branch a seal claims must be reachable. An arm may be declared one-way
in advance (PASS informative, FAIL not), as long as its PASS branch is shown reachable and its null false-PASS rate
is checked." Declared one-way: β 0.45, β 0.40, −7. Two-way: the primary.
Run 1 (the first §9.J wording, all arms two-way; −7 with option B's local slope) FAILED; it is in
results/stage2/FN1_STAGE2_REACH_FAILED.json.
Design; seen stage-1 data only. TOOLKIT §9.I: inputs read-only and pinned, output to scratch. Uses the read's own
functions (fn1_read2.py, frozen CONST).

  python fn1_stage2_reach.py READ1 OUT_REL

Design noise per arm, as the reading rule projects it (stage-1 ratio × the stage-2 model):
- **Rank arms:** the stage-1 raw ratio at that β × SE[β] (the rule is raw).
  - PASS reachable iff P(PASS | b = B[β], design noise) ≥ 0.01.
  - Null false-PASS = P(PASS | b = 0, design noise); it must be ≤ 0.02 (the rank-null witness bar; exact level
    0.0086).
  - Two-way (primary): the informative FAIL is also reachable iff power ≥ 0.80 at the design noise.
  - Reported too (no verdict): power at 1× and at the stage-1 detrended ratio.
- **ℤ[√2] placement:** plain PASS/FAIL, no power gate.
  - Per-field σ_F = stage-1 raw β 0.55 ratio × R_F(stage-1) × the stage-2 model relSD.
  - P(PASS) with the stage-1 R as means, 200,000 draws. Both branches are reachable iff 0.01 ≤ P(PASS) ≤ 0.99.
- **−7 (one-way, flat null):** σ = √(det_d² + DRIFT_SD²) × mean R (stage-1), with det_d = the stage-1 detrended ratio
  × the model relSD; b_null = 0.
  - PASS reachable iff the power under persistence ≥ 0.01.
  - Null false-PASS: the flat-null rate (independent seed) must lie in [0.035, 0.065]. The convex null is checked in
    the witness.
  - Reported too (no verdict): at det → 0, at the raw DRIFT_SD 0.027302, and under the local and global slopes.
Prints REACH_OK True/False.
"""
import math, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_H, ".."), os.path.join(_H, "..", "..")]
import safeio
safeio.enforce()
import numpy as np
import fn1_read2 as R2

READ1_SHA = "47c19dd26aaf3e892c01928f708c6b7032b61a5a8012dbdce7e3198dcfac4c76"
RAW = {"0.55": 3.3726854039071306, "0.45": 1.4685488047090154, "0.4": 1.0272109880563989}
DET = {"0.55": 1.7075658694649614, "0.45": 1.0557911897410721, "0.4": 0.8338852350434506}
DRIFT_RAW = 0.027302
N2 = 3663002294
F = R2.FIELDS


def main(read1, out_rel):
    rd = safeio.read_json(read1, expect_sha256=READ1_SHA)
    counts = R2.exact_null_counts()
    out, ok = {"label": "FN1 stage-2 pre-seal power and reachability under the design noise (seen stage-1 data)"}, True
    arms = {}
    MODE = {"0.55": "two-way", "0.45": "one-way", "0.4": "one-way"}
    for i, b in enumerate(("0.55", "0.45", "0.4")):
        Bb, SEb = R2.CONST["B"][b], R2.CONST["SE"][b]
        pw = {k: R2.power_at(s, Bb, SEb, counts, 20261150 + 10 * i + j)
              for j, (k, s) in enumerate((("design_raw", RAW[b]), ("1x", 1.0), ("stage1_detrended", DET[b])))}
        fp = R2.power_at(RAW[b], 0.0, SEb, counts, 20261190 + i)
        a = dict(mode=MODE[b], design_ratio=RAW[b], power=pw, null_false_pass=fp, null_ok=bool(fp <= 0.02),
                 pass_reachable=bool(pw["design_raw"] >= 0.01), informative_fail_reachable=bool(pw["design_raw"] >= 0.80))
        a["ok"] = a["pass_reachable"] and a["null_ok"] and (a["informative_fail_reachable"] or MODE[b] == "one-way")
        arms[{"0.55": "primary_beta055", "0.45": "secondary_beta045", "0.4": "secondary_beta040"}[b]] = a
    K = int(round(N2 ** 0.55)); model_rel = math.sqrt(2 / (R2.C_SE * K))
    rng = np.random.default_rng(20261160)
    mu = {f: rd["R"][f]["0.55"] for f in ("-67", "-163")}; mu["zs2"] = rd["R"]["zs2"]["0.55"]
    sim = {f: mu[f] + RAW["0.55"] * mu[f] * model_rel * rng.standard_normal(200_000) for f in mu}
    pz = float(((sim["-67"] < sim["zs2"]) & (sim["zs2"] < sim["-163"])).mean())
    arms["zs2_placement_beta055"] = dict(mode="plain", p_pass_at_stage1_means=pz, ok=bool(0.01 <= pz <= 0.99),
                                         note="no power gate; PASS carries Will's stage-1 caveat")
    R1 = {f: rd["R"][f]["0.55"] for f in F}
    bg, blr, bl, bopt = R2.slopes(R1)
    Rbar = float(np.mean(list(R1.values())))
    det_d = DET["0.55"] * model_rel
    m7 = dict(mode="one-way", b_null=0.0, b_global=bg, b_local_raw=blr, b_local_optionB=bopt, Rbar=Rbar, det_rel_design=det_d)
    for nm, det, drift, slope in (("design", det_d, R2.CONST["DRIFT_SD"], 0.0), ("det_to_0", 0.0, R2.CONST["DRIFT_SD"], 0.0),
                                  ("raw_drift_design", det_d, DRIFT_RAW, 0.0),
                                  ("local_slope_design_descriptive", det_d, R2.CONST["DRIFT_SD"], bopt),
                                  ("global_slope_design_descriptive", det_d, R2.CONST["DRIFT_SD"], bg)):
        sig = math.hypot(det, drift) * Rbar
        mm = R2.m7_margin(slope, sig)
        m7[nm] = dict(sigma_rel=sig / Rbar, slope=slope, margin=mm, power_persist=R2.m7_power(slope, sig, mm, R2.CONST["DELTA7"]),
                      false_pass_check=float((R2.m7_T(slope, sig, 0.0, R2.SEED_M7 + 2) > mm).mean()))
    m7["pass_reachable"] = bool(m7["design"]["power_persist"] >= 0.01)
    m7["null_ok"] = bool(0.035 <= m7["design"]["false_pass_check"] <= 0.065)
    m7["ok"] = m7["pass_reachable"] and m7["null_ok"]
    arms["minus7_beta055"] = m7
    out["arms"] = arms
    ok = all(a["ok"] for a in arms.values())
    out["REACH_OK"] = bool(ok)
    p = safeio.write_json(safeio.scratch(out_rel), out, overwrite=True)
    print("written", p)
    for k, a in arms.items():
        print(k, {kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in a.items() if not isinstance(v, dict)})
        for kk, v in a.items():
            if isinstance(v, dict):
                print("   ", kk, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in v.items()})
    print("REACH_OK", ok)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
