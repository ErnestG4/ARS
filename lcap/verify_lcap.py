"""Live checker for the L-policy arc.  Nonzero exit on regression."""

import hashlib
import json
import sys

LC = "/home/combust/fmexplorer/criticality_tool/lcap"
fails = []


def chk(c, m):
    if not c:
        fails.append(m)


seal = json.load(open(f"{LC}/prereg_sealed.json"))
for f, sha in seal["code_freeze_blob_shas"].items():
    d = open(f"{LC}/{f}", "rb").read()
    chk(hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha,
        f"freeze violation: {f}")

# condition 1: the zoo gate, and the GOE discovery that produced the 2nd cap
zoo = json.load(open(f"{LC}/zoo_measured.json"))
chk(zoo["PASS"], "zoo gate not PASS — zeta must not be evaluated")
chk(zoo["members"]["goe"]["verdict"] != "RIGID_GUE",
    "GOE re-admitted to RIGID_GUE — the discrimination cap regressed")
chk(zoo["members"]["clock"]["verdict"] == "HYPER_RIGID", "clock row moved")

pol = json.load(open(f"{LC}/policy.json"))
chk(pol["discrimination_L"] == 40.0, "discrimination cap changed")
chk(pol["discrimination_scan"]["50.0"]["separated"] is False,
    "the L=50 separation failure vanished — that failure is load-bearing")
chk(pol["policy"]["zeta_first_2000"]["L_judge"] < 6.0
    and "validity" in pol["policy"]["zeta_first_2000"]["binding"],
    "zeta's validity cap regressed")

val = json.load(open(f"{LC}/validity_scales.json"))
chk(abs(val["substrates"]["zeta_first_2000"]["validity_L"] - 5.99) < 0.05,
    "Berry scale drifted")
chk(val["substrates"]["poisson"]["basis"] == "NOT_APPLICABLE",
    "empty-cell honesty regressed")

m = json.load(open(f"{LC}/lcap_measured.json"))
z = m["L1_rows"]["zeta_first_2000"]
chk(z["sealed_prediction_sign_held"], "zeta sign pre-commitment broke")
chk(not z["halt"], "HALT condition raised")
chk(z["z"] < -8.0, "zeta significance at the capped L regressed")
chk(z["resolvable"], "zeta effect no longer resolvable above MDD")
chk(z["proposed"] == "HYPER_RIGID", "zeta row verdict changed")
chk(all(v["z"] < -8.0 for v in z["lens_sweep"].values()),
    "zeta lens-invariance regressed")
chk(m["verdict"]["primary"] == "L_POLICY_FIXED", "arc verdict changed")
chk(not m["L1_rows"]["brocot_golden"]["moved_by_policy"],
    "brocot row unexpectedly moved")

if fails:
    print("VERIFY_LCAP: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_LCAP: seal, zoo gate, policy, and zeta row all green")
