# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 witnesses, RUN 2 (FN1_STAGE2_SEAL.md §4; Will 2026-11-02 §2.4 decision: option B, local-slope null).
Run 1 (the drafted −7 rule) stays recorded as failed in results/stage2/FN1_WITNESS2_run1_FAILED.json.
The read's own decision functions (fn1_read2.py, frozen CONST) on parametric R sets at the stage-2 K. No data.
TOOLKIT §9.I: inputs read-only, output to scratch only.

  python fn1_witness2.py OUT_REL READ1.json

Design noise (stated before running): det_d = stage-1 detrended β 0.55 ratio 1.70757 × the stage-2 model relSD
√(2/(c K₂)); σ_rel,d = √(det_d² + DRIFT_SD²); σ_d = σ_rel,d × the stage-1 nine-field mean R (β 0.55, READ1 sha256 pinned).

Rank test (β 0.55, nine fields, σ = SE × s, s ∈ {1, stage-1 raw ratio 3.37269}; bars unchanged from run 1):
- null (b = 0): PASS rate ≤ 0.02; planted target (b = B): within ±0.03 of power_at (independent seed);
  shuffled C (b = B, C permuted per replicate): PASS rate ≤ 0.02.
−7, statistical (REPS_M7 = 4000 replicates; each replicate simulates all nine R and goes through fn1_read2.minus7 with
det = det_d and raw = det_d, so the read-time slopes b_global, b_local and the margin are recomputed per replicate):
- W-lin, linear C-ordered null, no displacement: R = 0.80 + B (C − C_−7) + σ_d ε. Bar: PASS rate ≤ 0.05.
- W-convex (Will's bar), convex-curvature null, no displacement: R = the quadratic in C_F fitted by OLS to the stage-1
  β 0.55 R over the eight fields other than −7, with −7 placed on that curve, + σ_d ε. Bar: PASS rate ≤ 0.05 (point
  estimate; the Wilson 95% interval is reported).
- W-convex2 (descriptive, no bar): the same curve + q₂ (C − C̄₈)², i.e. the quadratic coefficient doubled.
- W-persist (descriptive, no bar): W-lin plus DELTA7 on −7: PASS rate, beside the tabled power at b_null = B.
−7, label reachability (constructed sets through fn1_read2.minus7; base R = 0.80 + B (C − C_−7), so b_global = b_local =
B), one case per branch:
- informative PASS: R_−7 = base + 0.10, det = det_d → "PASS";
- informative FAIL: R_−7 = base − 0.03 (below both neighbours), det = 1e−4 → "FAIL";
- unpowered FAIL: R_−7 = base − 0.03, det = 0.2 → "FAIL (UNPOWERED at the read-time noise)";
- small hit at high noise: R_−7 = R_−11 + 0.01, det = 0.2 → "FAIL (UNPOWERED at the read-time noise)" (the margin
  absorbs a hit that the drafted rule would have counted);
- tie: R_−7 = R_−8 → "VOID (ties)".
- Each case records power_persist_rule and margin.
Prints WITNESS2_PASS True/False; every bar above must hold.
"""
import math, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_H, os.path.join(_H, "..")]
import safeio
safeio.enforce()
import numpy as np
import fn1_read2 as R2

READ1_SHA = "47c19dd26aaf3e892c01928f708c6b7032b61a5a8012dbdce7e3198dcfac4c76"
REPS, REPS_M7 = 2000, 4000
S1_RAW, S1_DET = 3.3726854039071306, 1.7075658694649614
F = R2.FIELDS
C = np.array([R2.C[f] for f in F])
counts = R2.exact_null_counts()
B, SE = R2.CONST["B"]["0.55"], R2.CONST["SE"]["0.55"]
K2 = int(round(3663002294 ** 0.55))


def pass_rate(b, s, seed, shuffle=False):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(REPS):
        Cv = rng.permutation(C) if shuffle else C
        r = b * Cv + s * SE * rng.standard_normal(9)
        hits += R2.rank_test(dict(zip(F, r.tolist())), R2.C, counts)["verdict"] == "PASS"
    return hits / REPS


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]


def m7_rate(mean9, sig, det, seed):
    rng = np.random.default_rng(seed)
    k = 0
    for _ in range(REPS_M7):
        r = mean9 + sig * rng.standard_normal(9)
        k += R2.minus7(dict(zip(F, r.tolist())), det, det)["verdict"] == "PASS"
    return dict(pass_rate=k / REPS_M7, wilson95=wilson(k, REPS_M7), n=REPS_M7)


def main(out_rel, read1):
    rd = safeio.read_json(read1, expect_sha256=READ1_SHA)
    res, ok = {"run": 2, "rule": "option B, local-slope null (Will 2026-11-02)"}, True
    for nm, s in (("1x", 1.0), ("stage1_raw", S1_RAW)):
        nul, tgt = pass_rate(0.0, s, 7001), pass_rate(B, s, 7002)
        pw = R2.power_at(s, B, SE, counts, 7003)
        shf = pass_rate(B, s, 7004, shuffle=True)
        c = dict(null_pass=nul, target_pass=tgt, target_power_model=pw, shuffled_pass=shf,
                 ok=bool(nul <= 0.02 and abs(tgt - pw) <= 0.03 and shf <= 0.02))
        res["rank_" + nm] = c; ok &= c["ok"]
    # design noise
    model_rel = math.sqrt(2 / (R2.C_SE * K2))
    det_d = S1_DET * model_rel
    s_rel = math.hypot(det_d, R2.CONST["DRIFT_SD"])
    R1 = np.array([rd["R"][f]["0.55"] for f in F])
    Rbar = float(R1.mean()); sig = s_rel * Rbar
    res["design_noise"] = dict(model_rel=model_rel, det_rel=det_d, drift_sd=R2.CONST["DRIFT_SD"], sigma_rel=s_rel,
                               Rbar_stage1=Rbar, sigma=sig)
    lin = 0.80 + B * (C - C[0])
    msk = np.array([f != "-7" for f in F])
    q = np.polyfit(C[msk], R1[msk], 2)
    convex = np.polyval(q, C)
    convex2 = convex + q[0] * (C - C[msk].mean()) ** 2          # quadratic coefficient doubled, about the 8-field mean C
    res["convex_fit"] = dict(quad_coef=q.tolist(), curve=dict(zip(F, convex.tolist())),
                             stage1_m7_minus_curve=float(R1[0] - convex[0]),
                             curve_m7_minus_m8=float(convex[0] - convex[1]), curve_m7_minus_m11=float(convex[0] - convex[2]))
    w = {}
    w["W_lin"] = m7_rate(lin, sig, det_d, 7101); w["W_lin"]["ok"] = bool(w["W_lin"]["pass_rate"] <= 0.05)
    w["W_convex"] = m7_rate(convex, sig, det_d, 7102); w["W_convex"]["ok"] = bool(w["W_convex"]["pass_rate"] <= 0.05)
    w["W_convex2_descriptive"] = m7_rate(convex2, sig, det_d, 7103)
    lin_p = lin.copy(); lin_p[0] += R2.CONST["DELTA7"]
    w["W_persist_descriptive"] = m7_rate(lin_p, sig, det_d, 7104)
    mB = R2.m7_margin(B, sig)
    w["W_persist_descriptive"]["tabled_power_at_bnull_B"] = R2.m7_power(B, sig, mB, R2.CONST["DELTA7"])
    res["minus7_stat"] = w
    ok &= w["W_lin"]["ok"] and w["W_convex"]["ok"]
    # label reachability
    base = dict(zip(F, lin.tolist()))

    def setR(r7):
        r = dict(base); r["-7"] = r7; return r
    cases = {"informative_PASS": (setR(base["-7"] + 0.10), det_d, "PASS"),
             "informative_FAIL": (setR(base["-7"] - 0.03), 1e-4, "FAIL"),
             "unpowered_FAIL": (setR(base["-7"] - 0.03), 0.2, "FAIL (UNPOWERED at the read-time noise)"),
             "small_hit_high_noise": (setR(base["-11"] + 0.01), 0.2, "FAIL (UNPOWERED at the read-time noise)"),
             "tie": (setR(base["-8"]), 1e-4, "VOID (ties)")}
    lab = {}
    for nm, (r, det, exp) in cases.items():
        o = R2.minus7(r, det, det)
        lab[nm] = dict(expected=exp, got=o["verdict"], margin=o.get("margin"), power_persist_rule=o.get("power_persist_rule"),
                       T=o.get("T"), b_null=o.get("b_null"), ok=o["verdict"] == exp)
        ok &= lab[nm]["ok"]
    res["minus7_labels"] = lab
    res["ok"] = bool(ok)
    p = safeio.write_json(safeio.scratch(out_rel), res, overwrite=True)
    print("written", p)
    for k, v in res.items():
        print(k, v)
    print("WITNESS2_PASS", bool(ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
