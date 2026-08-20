"""Live checker for the holonomy pilot's banked state (witness-must-be-able-
to-fail terminal form).  Nonzero exit on any regression.  Blob-SHA
tamper-evidence against the seal's freeze list; banked verdicts pinned."""

import hashlib
import json
import sys

import numpy as np

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.dirname(_HERE)
HL = _HERE
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

# ADD-7 CLOSURE (2026-08-19): the dial-2.0 residual is an under-ordered
# estimator, not a missing continuum term. Three pins, each naming what flips
# it red -- and note pin (a) asserts a NULL while (b) asserts a NON-null, so no
# degenerate run satisfies both.
fa = json.load(open(f"{HL}/p1_finite_n_arm.json"))
chk(abs(fa["rows"]["0.00"]["z_from_zero"]) < 3.0,
    "the a=0 finite-n arm is no longer inert — if a finite-n response has "
    "appeared, the ADD-7 closure needs re-reading, since it rests on there "
    "being none")
chk(fa["rows"]["0.25"]["residual"] > 0.15,
    "the dial-2.0 residual being explained has itself moved; the closure is "
    "an explanation OF +0.2242 and does not survive that number changing")

dg = json.load(open(f"{HL}/p1_degree_diagnostic.json"))
chk(dg["verdict"].startswith("UNDER_ORDERED_ESTIMATOR"),
    f"ADD-7 mechanism regressed: {dg['verdict'][:70]}")
chk(dg["high_deg_all_consistent_with_zero"],
    "high-degree residuals no longer all within 3 sem of zero — the claim "
    "'deg 5 is the ONLY failing degree' is exactly this")
chk(dg["measured_dynamic_range"] >= 100,
    "the law's validation rests on tracking a measured value across a wide "
    "range; if the sweep no longer spans it, the validation is weaker than stated")
chk(dg["periods_full"] > dg["periods_window"],
    "the mechanism requires the full fit range to span MORE density periods "
    "than the window; if not, the explanation does not apply")

# Straddle localization (2026-08-19): mechanism supported, FORM unresolved.
# Both halves are pinned, so a later run cannot quietly promote the form.
st = json.load(open(f"{HL}/p1_straddle_centroid.json"))
chk(st["cis_disjoint"],
    "straddle centroid CIs overlap — 'the elevation MOVES with degree' is the "
    "whole mechanism claim and this is the measurement of it")
# The form was re-graded DELIBERATELY on 2026-08-19 (SLOPE_RESOLVED,
# OFFSET_UNRESOLVED) after the sealed predictive test, which is what the old
# promotion pin existed to force. Replaced with pins on the new grade: the slope
# half is now asserted, the offset half still pins its own promotion condition.
rb = json.load(open(f"{HL}/ridge_stageB.json"))
ra = json.load(open(f"{HL}/ridge_stageA.json"))
chk(rb["verdict"].startswith("RIDGE_PREDICTIVE"),
    f"the sealed predictive test no longer passes: {rb['verdict'][:80]}")
chk(rb["ci_covers_prediction"] == 2,
    "the held-out centroid CIs no longer both cover their SEALED predictions — "
    "that is the whole predictive claim")
_deg = [5, 7, 9, 11, 13]
_cen = [ra["rows"][str(d)]["centroid"] if str(d) in ra["rows"]
        else rb["rows"][str(d)]["centroid"] for d in _deg]
_slope = float(np.polyfit(_deg, _cen, 1)[0])
chk(abs(_slope - 0.5) < 0.05,
    f"the ridge slope is {_slope:.3f}, no longer 1/2 — SLOPE_RESOLVED rests on "
    "this and on its mechanistic reading periods_full ~ deg")
chk(rb["ci_excludes_baseline"] < 2,
    "the held-out CIs now BOTH exclude the (deg-1)/2 baseline — that would "
    "promote OFFSET_UNRESOLVED to resolved, and COMMUTATOR_TABLE.md still says "
    "unresolved; re-grade deliberately rather than letting a rerun do it")
chk(max(abs(x) for x in st["grid"]["9"]["residuals"]) > 8 * max(st["grid"]["9"]["sems"]),
    "deg-9 straddle bump no longer stands clear of its own noise")
# PIN REMOVED 2026-08-19. It asserted the deviation from (deg-1)/2 was
# signed-and-growing. That "fact" came from a deg-13 centroid computed against an
# ill-conditioned prediction; with the numerics repaired the deviation is FLAT
# (+0.173/+0.182/+0.170). Recorded because the pin worked exactly as designed and
# that was the problem: it defended a wrong number against correction. A pin on a
# measured fact inherits every defect of the measurement, so pinning is not a
# substitute for validating what is pinned.

if fails:
    print("VERIFY_HOLONOMY: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_HOLONOMY: seal, KAG, census, verdicts, registry all green")
