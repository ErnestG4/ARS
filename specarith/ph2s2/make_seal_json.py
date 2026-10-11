"""Build seals/PH2S_SEAL_2.0.json (run on Will's go; the seal commit and tag are his call). Refuses unless:
- the dry run read as expected (F1 seen: PASS; GUE stand-in vs ζ: FAIL; vs GUE: PASS; guard witness: NOT RESOLVABLE),
  and the read path reproduced the stored F1 window sums;
- the F2 md5s in s2read.py equal the pins in ph2r2/FRESH_SETS_F1_F3.md;
- the prediction file is the one recorded by tag ph2s-stage2-prediction (sha256 below) and covers all five F2 files;
- the GUE calibration on the Stage 2 baseline exists (24 sequences).
Pins: code (s2read.py, tapered.py and the ph2r2 decode modules), the seal text, the prediction file and its values,
F2 md5s, the rule, the GUE calibration, the operating characteristics, and hashes of the pre-read records.

  python make_seal_json.py [--check]     (--check: run the refusal checks only; writes nothing)
"""
import hashlib
import json
import os
import re

import s2read as R

HERE = R.HERE
sha = R.sha


def pred_blob_at_tag():
    """sha256 of the prediction file as recorded at tag ph2s-stage2-prediction."""
    import subprocess
    rel = os.path.relpath(R.PRED, os.path.join(HERE, "..", ".."))
    blob = subprocess.run(["git", "show", f"ph2s-stage2-prediction:{rel}"], cwd=HERE, capture_output=True, check=True).stdout
    return hashlib.sha256(blob).hexdigest()


def main(check_only=False):
    P = os.path.join(HERE, "results", "s2_preread")
    dry = json.load(open(os.path.join(HERE, "results", "dryrun", "S2_DRYRUN.json")))
    cal = json.load(open(os.path.join(P, "guecal.json")))
    pcal = json.load(open(os.path.join(P, "poolcal.json")))
    op = json.load(open(os.path.join(P, "opchar.json")))
    pins = dict(re.findall(r"\| (zeros_\d+\.dat) \| \[[^|]*\) \| [^|]* \| ([0-9a-f]{32}) \|",
                           open(os.path.join(HERE, "..", "ph2r2", "FRESH_SETS_F1_F3.md")).read()))
    f2_md5 = {f: m for f, _, _, m in R.F2.values()}
    pred = R.predictions()
    checks = dict(dryrun_as_expected=all(dry["as_expected"].values()), F1_sums_reproduce=bool(dry["F1_sums_reproduce"]),
                  f2_md5_match_pins=all(pins.get(f) == m for f, m in f2_md5.items()),
                  prediction_is_tagged=sha(R.PRED) == pred_blob_at_tag(),
                  prediction_covers_F2=sorted(pred) == sorted(R.F2),
                  gue_calibration_stage2=cal["F2"]["n_seq"] == 24)
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: {[k for k, v in checks.items() if not v]}")
    if check_only:
        print("checks (nothing written):", checks)
        return
    adopted = {k: {e: r["adopted_fixedw_pass"] for e, r in v["rules"].items()} for k, v in op["kappa"].items()}
    superseded_A = {k: {e: r["adopted_pass"] for e, r in v["rules"].items()} for k, v in op["kappa"].items()}
    seal = dict(
        seal="PH2S_SEAL_2.0", stage=2, text="PH2S_SEAL_2.0.md", text_sha256=sha(os.path.join(HERE, "PH2S_SEAL_2.0.md")),
        code_sha256={f: sha(os.path.join(HERE, f)) for f in R.CODE},
        prediction=dict(tag="ph2s-stage2-prediction", file=os.path.relpath(R.PRED, HERE), sha256=sha(R.PRED),
                        g_B=pred, g_GUE_B=R.G_GUE_B),
        prediction_sha256=sha(R.PRED),
        f2_md5=f2_md5, f2_files={ell: dict(file=f, t0=t0, t1=t1) for ell, (f, t0, t1, _) in R.F2.items()},
        f2_windows=R.f2_windows(),
        pool_weights=R.pool_weights(R.f2_windows()),
        rule=dict(statistic="g_B = sqrt(vB(1e4)/vB(100)), vB successive differences (tapered.pooled_diff)",
                  se="SE_f = 0.5 g sqrt(rSE_100^2 + rSE_1e4^2), lag-0-2 SEs",
                  pooling="C (round 28): W_f proportional to n_f(1e4) - 1 from the pinned ranges, sum 1; "
                          "d_pool = sum W (g - g_pred); SE_pool = sqrt(sum W^2 SE_f^2); z_pool = d_pool / SE_pool",
                  guard="RESOLVABLE iff 2 SE_pool <= 0.07 (reads SEs and the fixed weights only)",
                  verdict="PASS iff RESOLVABLE and |z_pool| <= 2 (R2) and >= 4 of 5 files |z_f| <= 3 (R1); else FAIL",
                  report="pooled g_B +- 95% CI beside the pooled prediction, regardless of verdict",
                  k_pool=R.K_POOL, k_file=R.K_FILE, min_agree=R.MIN_AGREE, guard_2se_pool=R.GUARD),
        gue_calibration=dict(
            rule_C=dict(stage2_baseline=pcal["F2"]["variants"]["C_fixed_weights"],
                        stage1_replication=pcal["S1"]["variants"]["C_fixed_weights"]),
            per_file=dict(stage2_baseline={k: cal["F2"][k] for k in ("z_sd_per_file", "rate_abs_gt3_per_file")},
                          stage1_replication={k: cal["S1"][k] for k in ("z_sd_per_file", "rate_abs_gt3_per_file")}),
            superseded=dict(note="round-27 '~6-7%' came from the chi-square model; inverse-variance pooling (A) gave "
                                 "a false-FAIL of 0.090 on the Stage 2 GUE baseline (round 28 chose C)",
                            A_stage2=pcal["F2"]["variants"]["A_adopted"], A_stage1=pcal["S1"]["variants"]["A_adopted"])),
        operating_characteristics=dict(alternatives="g = g_pred + eps (g_GUE_B - g_pred); eps = 1 is GUE",
                                       rule_C_pass_by_kappa=adopted, superseded_A_pass_by_kappa=superseded_A,
                                       per_file_se_g={k: v["per_file_se_g"] for k, v in op["kappa"].items()}),
        preread_sha256={os.path.relpath(p, HERE): sha(p) for p in sorted(
            [os.path.join(P, f) for f in os.listdir(P) if f.endswith(".json")]
            + [os.path.join(HERE, "results", "dryrun", "S2_DRYRUN.json")])},
        checks=checks)
    os.makedirs(os.path.join(HERE, "seals"), exist_ok=True)
    json.dump(seal, open(os.path.join(HERE, "seals", "PH2S_SEAL_2.0.json"), "w"), indent=1, default=float)
    print("wrote seals/PH2S_SEAL_2.0.json;", checks)


if __name__ == "__main__":
    import sys
    main(check_only="--check" in sys.argv)
