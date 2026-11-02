# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 witnesses, RUN 3 (FN1_STAGE2_SEAL.md §4). Will's rulings, 2026-11-02, after run 2:
- the −7 null is flat (b_null = 0);
- β 0.45, β 0.40 and −7 are declared one-way;
- "Witness run 2 adds the convex null (must be ≤ 0.05) and a flat null (must be ≈ 0.05)".
Run 2 was executed and stays recorded as failed, so this run is numbered 3. Runs 1 and 2 are in results/stage2/.

The read's own decision functions (fn1_read2.py: minus7, verdict_labels, rank_test, power_at; frozen CONST) on
parametric R sets at the stage-2 K. No data. TOOLKIT §9.I: inputs read-only, output to scratch only.

  python fn1_witness2.py OUT_REL READ1.json

Design noise (stated before running): det_d = stage-1 detrended β 0.55 ratio 1.70757 × the stage-2 model relSD
√(2/(c K₂)); σ_rel,d = √(det_d² + DRIFT_SD²); σ_d = σ_rel,d × the stage-1 nine-field mean R (β 0.55, READ1 sha256 pinned).

Rank test (β 0.55, nine fields, σ = SE × s, s ∈ {1, stage-1 raw ratio 3.37269}; bars unchanged from runs 1 and 2):
- null (b = 0): PASS rate ≤ 0.02;
- planted target (b = B): within ±0.03 of power_at (independent seed);
- shuffled C (b = B, C permuted per replicate): PASS rate ≤ 0.02.

−7, statistical. REPS_M7 = 4000 replicates; each simulates all nine R and goes through fn1_read2.minus7 with det = det_d.
- W-flat (Will): flat null, R = 0.80 + σ_d ε. Bar: PASS rate within [0.035, 0.065] (≈ 0.05; ±4.4 binomial SD).
- W-lin: linear C-ordered null, R = 0.80 + B (C − C_−7) + σ_d ε. Bar: PASS rate ≤ 0.05.
- W-convex (Will): the quadratic in C_F fitted by OLS to the stage-1 β 0.55 R over the eight fields other than −7, with
  −7 placed on that curve, + σ_d ε. Bar: PASS rate ≤ 0.05 (point estimate; the Wilson 95% interval is reported).
- W-convex2 (descriptive, no bar): the same curve + q₂ (C − C̄₈)², i.e. the quadratic coefficient doubled. On it
  −7 sits above −8, so the curve is not monotone at −7 and no bar applies.
- W-persist (descriptive, no bar): W-lin plus DELTA7 on −7, beside the tabled power at b_null = 0.

Label reachability, one case per branch:
- −7, through minus7, on base R = 0.80 + B (C − C_−7):
  - large hit (R_−7 = base + 0.10, det_d) → "PASS";
  - miss at low noise (base − 0.03, det 1e−4) → one-way FAIL label;
  - miss at high noise (base − 0.03, det 0.2) → one-way FAIL label;
  - small hit at high noise (R_−11 + 0.01, det 0.2) → one-way FAIL label (the margin absorbs it);
  - tie (R_−7 = R_−8) → "VOID (ties)".
- Verdict lattice, through verdict_labels:
  - primary FAIL with read-time power ≥ 0.80 → "FAIL"; with power < 0.80 → "FAIL (UNPOWERED …)"; PASS → "PASS";
  - β 0.45 and β 0.40: FAIL → one-way FAIL label at any power; PASS → "PASS"; "VOID (ties)" unchanged;
  - placement: True → "PASS", False → "FAIL".

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
    res, ok = {"run": 3, "rule": "flat −7 null; β 0.45, β 0.40, −7 one-way (Will 2026-11-02 rulings)"}, True
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
    w["W_flat"] = m7_rate(np.full(9, 0.80), sig, det_d, 7100)
    w["W_flat"]["ok"] = bool(0.035 <= w["W_flat"]["pass_rate"] <= 0.065)
    w["W_lin"] = m7_rate(lin, sig, det_d, 7101); w["W_lin"]["ok"] = bool(w["W_lin"]["pass_rate"] <= 0.05)
    w["W_convex"] = m7_rate(convex, sig, det_d, 7102); w["W_convex"]["ok"] = bool(w["W_convex"]["pass_rate"] <= 0.05)
    w["W_convex2_descriptive"] = m7_rate(convex2, sig, det_d, 7103)
    lin_p = lin.copy(); lin_p[0] += R2.CONST["DELTA7"]
    w["W_persist_descriptive"] = m7_rate(lin_p, sig, det_d, 7104)
    m0 = R2.m7_margin(0.0, sig)
    w["W_persist_descriptive"]["tabled_power_at_bnull_0"] = R2.m7_power(0.0, sig, m0, R2.CONST["DELTA7"])
    res["minus7_stat"] = w
    ok &= w["W_flat"]["ok"] and w["W_lin"]["ok"] and w["W_convex"]["ok"]
    # label reachability
    base = dict(zip(F, lin.tolist()))

    def setR(r7):
        r = dict(base); r["-7"] = r7; return r
    OW = R2.ONE_WAY_FAIL
    cases = {"PASS_large_hit": (setR(base["-7"] + 0.10), det_d, "PASS"),
             "miss_low_noise": (setR(base["-7"] - 0.03), 1e-4, OW),
             "miss_high_noise": (setR(base["-7"] - 0.03), 0.2, OW),
             "small_hit_high_noise": (setR(base["-11"] + 0.01), 0.2, OW),
             "tie": (setR(base["-8"]), 1e-4, "VOID (ties)")}
    lab = {}
    for nm, (r, det, exp) in cases.items():
        o = R2.minus7(r, det, det)
        lab[nm] = dict(expected=exp, got=o["verdict"], margin=o.get("margin"), T=o.get("T"),
                       power_persist_descriptive=o.get("power_persist_descriptive"), ok=o["verdict"] == exp)
        ok &= lab[nm]["ok"]
    VL = R2.verdict_labels
    lat = {"primary_FAIL_powered": (VL("FAIL", "PASS", "PASS", True, True, "PASS")["primary_beta055"], "FAIL"),
           "primary_FAIL_unpowered": (VL("FAIL", "PASS", "PASS", False, True, "PASS")["primary_beta055"], R2.UNPOWERED),
           "primary_PASS": (VL("PASS", "PASS", "PASS", False, True, "PASS")["primary_beta055"], "PASS"),
           "b045_FAIL": (VL("PASS", "FAIL", "PASS", True, True, "PASS")["secondary_beta045"], OW),
           "b040_FAIL": (VL("PASS", "PASS", "FAIL", True, True, "PASS")["secondary_beta040"], OW),
           "b045_PASS": (VL("PASS", "PASS", "PASS", True, True, "PASS")["secondary_beta045"], "PASS"),
           "b040_PASS": (VL("PASS", "PASS", "PASS", True, True, "PASS")["secondary_beta040"], "PASS"),
           "b045_VOID": (VL("PASS", "VOID (ties)", "PASS", True, True, "PASS")["secondary_beta045"], "VOID (ties)"),
           "zs2_True": (VL("PASS", "PASS", "PASS", True, True, "PASS")["zs2_placement_beta055"], "PASS"),
           "zs2_False": (VL("PASS", "PASS", "PASS", True, False, "PASS")["zs2_placement_beta055"], "FAIL"),
           "m7_passthrough": (VL("PASS", "PASS", "PASS", True, True, OW)["minus7_beta055"], OW)}
    res["lattice_labels"] = {k: dict(got=g, expected=e, ok=g == e) for k, (g, e) in lat.items()}
    ok &= all(g == e for g, e in lat.values())
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
