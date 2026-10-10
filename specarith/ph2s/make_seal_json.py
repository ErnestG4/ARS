"""Build seals/PH2S_SEAL_1.0.json (run on Will's go; the seal commit is his call). Refuses unless: the dry run read as
expected in both arms sets (seen R: A, C, D PASS; GUE stand-in: A, C, D FAIL), the precision-guard witness fired, the
GUE-vs-GUE specificity check read FAIL for A, C, D, every Stage 1 GUE sequence passed sanity, and 16 baseline sequences
exist per bin. Pins: code (s1lib, s1preread, s1read and the R₂ modules they import), the seal text, F1 md5s, d_ref,
resolvability, per-bin baselines (and a hash of every per-seed baseline record), arm rules and powers.

  python make_seal_json.py
"""
import glob
import hashlib
import json
import math
import os

import s1lib as S

HERE = S.HERE
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
F1_MD5 = {"zeros_10946000.dat": "754495b7e5603d1544d20876909700c9", "zeros_31946000.dat": "1f6f5d94fea2e372fd7ef7e09216fb6a",
          "zeros_319646000.dat": "378eb1cdca224fd2ca4c556ca5a9b62c",
          "zeros_1438946000.dat": "d1d8d60c71f7efcad1d373c4dd8b061f",
          "zeros_13660946000.dat": "fbb8c83b765dff81903e7a22ddaee69d",
          "zeros_24891746000.dat": "662d01b2d2b6923788a1d70602db687b"}


def main():
    P = os.path.join(HERE, "results", "preread")
    pre = json.load(open(os.path.join(P, "preread.json")))
    fpr = json.load(open(os.path.join(P, "fpr.json")))
    fprc = json.load(open(os.path.join(P, "fpr_c.json")))
    dry = json.load(open(os.path.join(HERE, "results", "dryrun", "S1_DRYRUN.json")))
    gue = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(HERE, "results", "gue", "gue_L*.json")))]
    checks = dict(dryrun_seen_R=all(dry["seen_R"]["as_expected"].values()),
                  dryrun_gue_standin=all(dry["gue_standin"]["as_expected"].values()),
                  guard_witness_FIRED=bool(dry["guard_witness"]["FIRED"]),
                  specificity_A_FAIL=pre["specificity"]["A"]["verdict"] == "FAIL",
                  specificity_C_FAIL=dry["gue_standin"]["C"]["verdict"] == "FAIL",
                  specificity_D_FAIL=pre["specificity"]["D"]["verdict"] == "FAIL",
                  gue_sanity=len(gue) == 32 and all(abs(g["mean_spacing"] - 1) < 1e-4 and abs(g["rtilde"] - 0.5996) < 0.005
                                                    for g in gue),
                  baseline_16_seeds_per_bin=all(v == 16 for v in pre["n_gue_seeds"].values()),
                  F1_record_matches=sorted(F1_MD5) == sorted(f for f, _, _ in S.F1.values()),
                  D_resolvable=bool(pre["D_resolvable"]), C_power_ge_080=fprc["power_at_seen"]["3.0"] >= 0.80)
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: {[k for k, v in checks.items() if not v]}")
    pw = pre["power"][str(S.L_PRIMARY)]
    res = pre["resolvable"][str(S.L_PRIMARY)]
    joint_half = math.prod(pw[n]["power"] for n in S.CORE if res[n])
    smallest_seen = min(pre["seen_d"][str(S.L_PRIMARY)].values())
    joint_seen = math.prod(S.Phi((smallest_seen - 3 * pw[n]["se_pred"]) / pw[n]["se_pred"]) for n in S.CORE if res[n])
    code = {f: sha(os.path.join(HERE, f)) for f in ("s1lib.py", "s1preread.py", "s1read.py", "gue_levels.py")}
    code.update({f"../ph2r2/{f}": sha(os.path.join(HERE, "..", "ph2r2", f)) for f in ("g0b.py", "r2prep.py", "r2run.py")})
    seal = dict(seal="PH2S_SEAL_1.0", stage=1, text="PH2S_SEAL_1.0.md", text_sha256=sha(os.path.join(HERE, "PH2S_SEAL_1.0.md")),
                code_sha256=code, f1_md5=F1_MD5, core=list(S.CORE), d_bins=list(S.F1),
                primary=list(S.PRIMARY), L_primary=S.L_PRIMARY, L_secondary=S.L_SECONDARY, boot=dict(short=S.B_SHORT,
                long=S.B_LONG, B=S.BOOT_B), d_ref=pre["d_ref"], resolvable=pre["resolvable"], power=pre["power"],
                arms=dict(A=dict(rule="bin shrinks iff resolvable and d > 3 SE_c; PASS iff >= 4 of 5 core bins shrink "
                                      "(unresolvable counts as not shrinking)",
                                 F1a="NOT RESOLVABLE pre-data", joint_power_half_reference=joint_half,
                                 joint_power_smallest_seen=joint_seen, pooled="descriptive"),
                          B=dict(status="descriptive (unresolvable pre-data in every bin)"),
                          C=dict(rule="Delta_u > 0 for >= 3 of 4 u and mean > 3 SE (unit-resampled)", k_se=3.0,
                                 fpr_empirical=fprc["fpr_by_k"]["3.0"], fpr_2se_empirical=fprc["fpr_by_k"]["2.0"],
                                 power_at_seen=fprc["power_at_seen"]["3.0"]),
                          D=dict(rule="WLS slope of d on L over six F1 bins; PASS iff slope + 2 SE < 0", power=pre["power_D"],
                                 fpr_empirical=fpr["fpr_D"])),
                baseline_sha256={os.path.basename(f): sha(f) for f in sorted(glob.glob(os.path.join(P, "base_*.json")))},
                preread_sha256={os.path.relpath(p, HERE): sha(p) for p in (
                    os.path.join(P, "preread.json"), os.path.join(P, "fpr.json"), os.path.join(P, "fpr_c.json"),
                    os.path.join(HERE, "results", "dryrun", "S1_DRYRUN.json"))},
                checks=checks)
    os.makedirs(os.path.join(HERE, "seals"), exist_ok=True)
    json.dump(seal, open(os.path.join(HERE, "seals", "PH2S_SEAL_1.0.json"), "w"), indent=1, default=float)
    print("wrote seals/PH2S_SEAL_1.0.json; joint power A: %.3f (half reference), %.3f (smallest seen)" % (joint_half, joint_seen))


if __name__ == "__main__":
    main()
