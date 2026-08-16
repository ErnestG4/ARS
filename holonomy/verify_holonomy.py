"""Live checker for the holonomy pilot's banked state (witness-must-be-able-
to-fail terminal form).  Nonzero exit on any regression.  Blob-SHA
tamper-evidence against the seal's freeze list; banked verdicts pinned."""

import hashlib
import json
import sys

HL = "/home/combust/fmexplorer/criticality_tool/holonomy"
fails = []


def chk(cond, msg):
    if not cond:
        fails.append(msg)


seal = json.load(open(f"{HL}/prereg_sealed.json"))
for f, sha in seal["code_freeze_blob_shas"].items():
    d = open(f"{HL}/{f}", "rb").read()
    cur = hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()
    chk(cur == sha, f"freeze violation: {f}")

kag = json.load(open(f"{HL}/kag_measured.json"))
chk(kag["PASS"] is True, "KAG not PASS")
chk(kag["fp_headroom"]["within"], "fp headroom regressed")
chk(kag["p3"]["equivalence_thin"]["bit_identical"],
    "thin_pre equivalence regressed")

own = json.load(open(f"{HL}/ownership_map.json"))
chk(own["coverage"] >= 0.9, "census coverage below sealed floor")

v = json.load(open(f"{HL}/arc_verdicts.json"))
BANKED = {"P1": ("ORDER_RULING_REQUIRED", "NONCOMMUTING_UNPREDICTED"),
          "P2": ("COMMUTATOR_MEASURED", "COMMUTATOR_MEASURED"),
          "P3": ("POINT_CHECK_CLEAN", "POINT_CHECK_CLEAN")}
for pair, (prim, meas) in BANKED.items():
    chk(v[pair]["verdict"]["primary"] == prim,
        f"{pair} primary regressed to {v[pair]['verdict']['primary']}")
    chk(v[pair]["verdict"]["measurement"] == meas,
        f"{pair} measurement regressed")
chk("HALT_PLUMBING_SIGN" not in v["P3"]["verdict"]["flags"],
    "P3 A3 sign flag raised")

p3 = json.load(open(f"{HL}/p3_measured.json"))
chk(abs(p3["dcount"]["mean"] + 10003) < 300, "P3 dcount drifted")
chk(p3["dcount"]["sign_ok_all_draws"], "P3 sign consistency regressed")

opt = json.load(open(f"{HL}/opt_measured.json"))
chk(opt["trigger_fired"] is True, "optional trigger record changed")
chk(opt["op2"]["law_agrees"], "OP2 sealed formula regressed")

# seal addenda (ADD-1..5, Will's post-banking audit) + their artifacts
chk([a["id"] for a in seal.get("addenda", [])]
    == [f"ADD-{i}" for i in range(1, 8)], "seal addenda block changed")
m1 = json.load(open(f"{HL}/op1_materiality.json"))
chk(m1["clean"] is False and abs(m1["margin_over_delta"] - 1.4) < 0.3,
    "OP1 materiality banked result drifted")
c1 = json.load(open(f"{HL}/op1_correctness.json"))
chk(c1["ruled_correct_matched_lens"] is False
    and c1["z_mixed"] < c1["z_matched"] <= 0.05
    and "first_run" in c1,
    "OP1 correctness banked result drifted")

# canonical registry importable and self-consistent with banked orders
sys.path.insert(0, HL)
from canonical import CANONICAL, assert_canonical      # noqa: E402
chk(assert_canonical("unfold_window_1d", "window_then_unfold"),
    "canonical P1 order")
chk(assert_canonical("reweight_edge_2d", "edge_then_reweight"),
    "canonical P2 order")
chk(assert_canonical("surrogate_unfold_1d", "matched_lens"),
    "canonical OP1 invariant (ADD-3 revision)")
chk(CANONICAL["surrogate_unfold_1d"].get("separation_status")
    == "UNDER_RESOLVED",
    "OP1 UNDER_RESOLVED marker missing (Will's audit round 2)")
try:
    assert_canonical("unfold_window_1d", "unfold_then_window")
    fails.append("assert_canonical failed to reject a wrong order")
except AssertionError:
    pass
chk(len(CANONICAL) == 6, "registry row count changed")
chk(assert_canonical("window_project_survey", "matched"),
    "canonical C4 invariant (ADD-6)")
chk(CANONICAL["window_project_survey"].get("separation_status")
    == "NO_TRUTH_BY_CONSTRUCTION", "C4 truth-absence marker missing")

# C4 cell (ADD-6): law confirmed at 10/20/30, mechanism real, statistic clean
c4 = json.load(open(f"{HL}/c4_measured.json"))
chk(c4["kag"]["PASS"] and c4["kag"]["red_fired"], "C4 KAG regressed")
chk(abs(c4["law"]["rows"]["tile10"]["z"]) <= 3.0
    and abs(c4["law"]["rows"]["tile30"]["z"]) <= 3.0,
    "C4 membership law regressed at the converged tiles")
chk(c4["statistic_clean"], "C4 statistic-level suppression regressed")
chk(c4["materiality"]["clean"], "C4 materiality regressed")

# P1 absorption upgrade (ADD-7): honest mixed result, pinned as such
ab = json.load(open(f"{HL}/p1_absorption_test.json"))
chk(ab["verdict"]["term_sign_confirmed"], "absorption sign prediction lost")
chk(ab["verdict"]["dial_independent"] is False,
    "T2 falsification vanished — the attribution refutation is load-bearing")
chk(ab["T3"]["n_pass_trend_only"] == ab["T3"]["n_cells"],
    "P1 out-of-sample confirmation regressed")

if fails:
    print("VERIFY_HOLONOMY: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_HOLONOMY: seal, KAG, census, verdicts, registry all green")
