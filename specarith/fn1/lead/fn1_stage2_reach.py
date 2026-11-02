# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 pre-seal power and TOOLKIT reachability check (Will 2026-11-02: "before sealing, every arm's informative
PASS and FAIL branches must be shown reachable under the design noise"). Design; seen stage-1 data only. TOOLKIT §9.I:
inputs read-only and pinned, output to scratch. The read's own functions (fn1_read2.py, frozen CONST).

  python fn1_stage2_reach.py READ1 OUT_REL

Design noise, per arm, as the seal's reading rule projects it (stage-1 ratio × the stage-2 model):
- rank arms (primary β 0.55; secondaries β 0.45, 0.40): the rule is raw, so the design noise is the stage-1 raw ratio
  at that β × SE[β]. Informative PASS reachable iff P(PASS | b = B[β], design noise) ≥ 0.01 (a PASS is informative
  at any power). Informative FAIL reachable iff power at the design noise ≥ 0.80 (otherwise every FAIL is labelled
  UNPOWERED). Also reported (no verdict): power at 1× and at the stage-1 detrended ratio.
- ℤ[√2] placement (no power gate): per-field σ_F = stage-1 raw β 0.55 ratio × R_F(stage-1) × the stage-2 model relSD;
  P(PASS) with the stage-1 R as means, 200,000 draws. Both branches reachable iff 0.01 ≤ P(PASS) ≤ 0.99.
- −7 (option B): σ = √(det_d² + DRIFT_SD²) × mean R (stage-1), det_d = stage-1 detrended ratio × model relSD; b_null =
  min(b_global, max(0, b_local)) from the stage-1 R. Informative PASS reachable iff the power under persistence
  ≥ 0.01; informative FAIL reachable iff that power ≥ 0.80. Also reported (no verdict): at det → 0, at the raw
  DRIFT_SD 0.027302 (Will: record that the arm would be weak), under the global slope, and the projected margin.
Prints REACH_OK True/False (all arms both branches).
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
    for i, b in enumerate(("0.55", "0.45", "0.4")):
        Bb, SEb = R2.CONST["B"][b], R2.CONST["SE"][b]
        pw = {k: R2.power_at(s, Bb, SEb, counts, 20261150 + 10 * i + j)
              for j, (k, s) in enumerate((("design_raw", RAW[b]), ("1x", 1.0), ("stage1_detrended", DET[b])))}
        a = dict(design_ratio=RAW[b], power=pw, pass_reachable=bool(pw["design_raw"] >= 0.01),
                 informative_fail_reachable=bool(pw["design_raw"] >= 0.80))
        a["both_reachable"] = a["pass_reachable"] and a["informative_fail_reachable"]
        arms[{"0.55": "primary_beta055", "0.45": "secondary_beta045", "0.4": "secondary_beta040"}[b]] = a
    K = int(round(N2 ** 0.55)); model_rel = math.sqrt(2 / (R2.C_SE * K))
    rng = np.random.default_rng(20261160)
    mu = {f: rd["R"][f]["0.55"] for f in ("-67", "-163")}; mu["zs2"] = rd["R"]["zs2"]["0.55"]
    sim = {f: mu[f] + RAW["0.55"] * mu[f] * model_rel * rng.standard_normal(200_000) for f in mu}
    pz = float(((sim["-67"] < sim["zs2"]) & (sim["zs2"] < sim["-163"])).mean())
    arms["zs2_placement_beta055"] = dict(p_pass_at_stage1_means=pz, both_reachable=bool(0.01 <= pz <= 0.99),
                                         note="no power gate; PASS carries Will's stage-1 caveat")
    R1 = {f: rd["R"][f]["0.55"] for f in F}
    bg, blr, bl, bn = R2.slopes(R1)
    Rbar = float(np.mean(list(R1.values())))
    det_d = DET["0.55"] * model_rel
    m7 = dict(b_global=bg, b_local_raw=blr, b_local=bl, b_null=bn, Rbar=Rbar, det_rel_design=det_d)
    for nm, det, drift, slope in (("design", det_d, R2.CONST["DRIFT_SD"], bn), ("det_to_0", 0.0, R2.CONST["DRIFT_SD"], bn),
                                  ("raw_drift_design", det_d, DRIFT_RAW, bn), ("raw_drift_det_to_0", 0.0, DRIFT_RAW, bn),
                                  ("global_slope_design", det_d, R2.CONST["DRIFT_SD"], bg)):
        sig = math.hypot(det, drift) * Rbar
        mm = R2.m7_margin(slope, sig)
        m7[nm] = dict(sigma_rel=sig / Rbar, slope=slope, margin=mm, power_persist=R2.m7_power(slope, sig, mm, R2.CONST["DELTA7"]),
                      false_pass_check=float((R2.m7_T(slope, sig, 0.0, R2.SEED_M7 + 2) > mm).mean()))
    m7["pass_reachable"] = bool(m7["design"]["power_persist"] >= 0.01)
    m7["informative_fail_reachable"] = bool(m7["design"]["power_persist"] >= 0.80)
    m7["both_reachable"] = m7["pass_reachable"] and m7["informative_fail_reachable"]
    arms["minus7_beta055"] = m7
    out["arms"] = arms
    ok = all(a["both_reachable"] for a in arms.values())
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
