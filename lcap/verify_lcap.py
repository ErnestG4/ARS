"""Live checker for the L-policy arc.  Nonzero exit on regression."""

import hashlib
import json
import sys

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.dirname(_HERE)
LC = _HERE
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

# LC-ADD-4/5: the bias confirmation and the corrected foundational finding.
# These pin the SELF-CORRECTIONS, so a future edit cannot quietly restore the
# withdrawn table or lose the misclassification measurement.
cr = json.load(open(f"{LC}/cap_rederive.json"))
chk(cr["estimator_bias"]["hardmax_is_downward_biased"],
    "the measured hard-max downward bias vanished")
chk(cr["conclusion_survives"] is False,
    "LC-ADD-2's withdrawal was reversed without a re-derivation")
mc = json.load(open(f"{LC}/misclass_rate.json"))
chk(mc["finding"]["goe_defect_stands"],
    "the foundational GOE defect vanished")
chk(mc["rows"]["50.0"]["misclass_rate"] > 0.4,
    "the deployed-L misclassification rate regressed below its measured value")
chk(mc["rows"]["20.0"]["misclass_rate"] < 0.15,
    "the small-L control regressed — the defect must be L-dependent")

# LC-ADD-1: the n-dependent discrimination cap and the brocot flag
pn = json.load(open(f"{LC}/policy_n.json"))
chk(pn["by_n"]["343"]["discrimination_L"] == 5.0, "n=343 cap drifted")
chk(pn["by_n"]["2000"]["discrimination_L"] == 40.0, "n=2000 cap drifted")
chk(not pn["banked_approximability_rows"]["inside_discrimination_window"],
    "the brocot out-of-window flag vanished — it is load-bearing")

# adoption into the deployed module (the owner's call): both must be live
sys.path.insert(0, _os.path.join(_REPO, "cross_substrate"))
import numpy as np                                            # noqa: E402
from longrange_discriminator import (l_judge, longrange_verdict,   # noqa: E402
                                     DISCRIMINATION_L_BY_N)
chk(l_judge(50, 2000, "zeta_first_2000", accept_provisional=True)[0] == 5.99,
    "zeta L policy not live")
chk(l_judge(6.86, 343, "gue_n343", accept_provisional=True)[0] == 5.0,
    "n=343 L policy not live")
# the provisional cap must NOT be obtainable without acknowledgement
from longrange_discriminator import (discrimination_L,               # noqa: E402
                                     ProvisionalCapError)
try:
    discrimination_L(2000)
    fails.append("provisional cap returned a bare number without caveat")
except ProvisionalCapError:
    pass
chk(DISCRIMINATION_L_BY_N[343] == 5.0, "installed cap table changed")
_clock = longrange_verdict(np.arange(2000, dtype=float), L=40.0, n_seeds=8,
                           ref_n=2000)
chk(_clock["verdict"] == "HYPER_RIGID",
    "the deployed split regressed — a clock earns the GUE pole again")

# The boundary-rate convention is pinned HERE because the 19-row sweep will
# restate rows against it: Clopper-Pearson and Wilson disagree at 4/4
# (0.398 vs 0.510 — uninformative vs result), so a re-run under the other
# convention would flip that row SILENTLY and the board would stay green.
sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
try:
    import boundary_rate as _br
    _br.self_test()
    chk(_br.CONVENTION == "clopper-pearson", "boundary-rate convention changed")
    chk(_br.COIN_FLIP_SPLIT == 0.5, "coin-flip split changed (a CHOSEN convention)")
    chk(_br.classify(4, 4)["treatment"] == "UNINFORMATIVE",
        "the borderline 4/4 row reclassified — the convention decides it")
except AssertionError as _e:
    fails.append(f"boundary_rate self-test failed: {_e}")

if fails:
    print("VERIFY_LCAP: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_LCAP: seal, zoo gate, policy, and zeta row all green")
