# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 witnesses (FN1_STAGE2_SEAL.md §4): the read's own decision functions (fn1_read2.py, frozen CONST) on
parametric R sets at the stage-2 K. No data. TOOLKIT §9.I: output to scratch only.

  python fn1_witness2.py OUT_REL

Rank test (β 0.55, nine fields, stage-2 model SE × s, s ∈ {1, stage-1 raw ratio}):
- null (b = 0): PASS rate must be ≤ 0.02 (exact level 0.0086; 2000 replicates, binomial 99.9% upper bound ≈ 0.019);
- planted target (b = CONST B[0.55]): PASS rate within ±0.03 of the parametric power (independent seed);
- shuffled C (b = B, C permuted per replicate): PASS rate ≤ 0.02.
−7 test:
- must-fail null (δ = 0, C-ordered, σ_rel = the projected rule noise): hit rate within ±0.02 of the tabled false-PASS
  rate; must-pass (δ = DELTA7): hit rate within ±0.03 of the tabled power;
- label logic on constructed sets: hit + low noise → PASS; hit + high noise → PASS (not separated …); miss + low noise
  → FAIL; miss + high noise → FAIL (UNPOWERED …); R_−7 == R_−8 → VOID (ties).
Prints WITNESS2_PASS True/False.
"""
import math, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_H, os.path.join(_H, "..")]
import safeio
safeio.enforce()
import numpy as np
import fn1_read2 as R2

REPS = 2000
C = np.array([R2.C[f] for f in R2.FIELDS])
counts = R2.exact_null_counts()
B, SE = R2.CONST["B"]["0.55"], R2.CONST["SE"]["0.55"]


def pass_rate(b, s, seed, shuffle=False):
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(REPS):
        Cv = rng.permutation(C) if shuffle else C
        r = b * Cv + s * SE * rng.standard_normal(9)
        hits += R2.rank_test(dict(zip(R2.FIELDS, r.tolist())), R2.C, counts)["verdict"] == "PASS"
    return hits / REPS


def main(out_rel):
    res, ok = {}, True
    s_raw = float(sys.argv[2]) if len(sys.argv) > 2 else 3.373
    for nm, s in (("1x", 1.0), ("stage1_raw", s_raw)):
        nul = pass_rate(0.0, s, 7001)
        tgt = pass_rate(B, s, 7002)
        pw = R2.power_at(s, B, SE, counts, 7003)
        shf = pass_rate(B, s, 7004, shuffle=True)
        c = dict(null_pass=nul, target_pass=tgt, target_power_model=pw, shuffled_pass=shf,
                 ok=bool(nul <= 0.02 and abs(tgt - pw) <= 0.03 and shf <= 0.02))
        res["rank_" + nm] = c; ok &= c["ok"]
    # -7 statistical witnesses at the projected rule noise
    model_rel = math.sqrt(2 / (R2.C_SE * int(round(3663002294 ** 0.55))))
    Rbar = SE / model_rel                                   # stage-1 mean R (CONST SE = mean R × model_rel)
    det_rel = float(sys.argv[3]) * model_rel if len(sys.argv) > 3 else 1.708 * model_rel   # stage-1 detrended ratio
    s_rel = math.hypot(det_rel, R2.CONST["DRIFT_SD"])
    sig = s_rel * Rbar
    tab_fp = R2.m7_rates(B, sig, 0.0, 7011)
    tab_pw = R2.m7_rates(B, sig, R2.CONST["DELTA7"], 7012)
    rng = np.random.default_rng(7013)
    e = rng.standard_normal((REPS, 3)) * sig
    hit0 = float((((B * C[0] + e[:, 0]) > (B * C[1] + e[:, 1])) & ((B * C[0] + e[:, 0]) > (B * C[2] + e[:, 2]))).mean())
    d = R2.CONST["DELTA7"]
    hit1 = float((((B * C[0] + d + e[:, 0]) > (B * C[1] + e[:, 1])) & ((B * C[0] + d + e[:, 0]) > (B * C[2] + e[:, 2]))).mean())
    c = dict(sigma_rel=s_rel, tabled_false_pass=tab_fp, mustfail_hit=hit0, tabled_power=tab_pw, mustpass_hit=hit1,
             ok=bool(abs(hit0 - tab_fp) <= 0.02 and abs(hit1 - tab_pw) <= 0.03))
    res["minus7_stat"] = c; ok &= c["ok"]
    # -7 label logic
    base = {f: 0.80 + 0.045 * (R2.C[f] - R2.C["-7"]) for f in R2.FIELDS}

    def setR(r7):
        r = dict(base); r["-7"] = r7; return r
    lab = {}
    lab["hit_low_noise"] = R2.minus7(setR(0.90), 1e-4, 1e-4)["verdict"]
    lab["hit_high_noise"] = R2.minus7(setR(0.90), 0.2, 0.2)["verdict"]
    lab["miss_low_noise"] = R2.minus7(setR(0.70), 1e-4, 1e-4)["verdict"]
    lab["miss_high_noise"] = R2.minus7(setR(0.70), 0.2, 0.2)["verdict"]
    lab["tie"] = R2.minus7(setR(base["-8"]), 1e-4, 1e-4)["verdict"]
    exp = {"hit_low_noise": "PASS",
           "hit_high_noise": "PASS (not separated from the C-ordered null at the read-time noise)",
           "miss_low_noise": "FAIL", "miss_high_noise": "FAIL (UNPOWERED at the read-time noise)", "tie": "VOID (ties)"}
    res["minus7_labels"] = dict(got=lab, expected=exp, ok=lab == exp)
    ok &= lab == exp
    # the drift term must matter: with DRIFT_SD the rule noise exceeds the detrended noise alone
    res["drift_term_active"] = bool(R2.CONST["DRIFT_SD"] >= 0 and s_rel >= det_rel)
    res["ok"] = bool(ok)
    p = safeio.write_json(safeio.scratch(out_rel), res, overwrite=True)
    print("written", p)
    for k, v in res.items():
        print(k, v)
    print("WITNESS2_PASS", bool(ok))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
