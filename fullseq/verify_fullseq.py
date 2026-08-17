"""Live checker for the full-sequence holonomy arc.  Nonzero exit on
regression."""

import hashlib
import json
import sys

FS = "/home/combust/fmexplorer/criticality_tool/fullseq"
fails = []


def chk(c, m):
    if not c:
        fails.append(m)


seal = json.load(open(f"{FS}/prereg_sealed.json"))
for f, sha in seal["code_freeze_blob_shas"].items():
    d = open(f"{FS}/{f}", "rb").read()
    chk(hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha,
        f"freeze violation: {f}")
chk(seal["kill_criterion"]["recorded_before_S0"], "kill criterion pedigree")
chk(len(seal["kill_criterion"]["targets_named_with_current_margins"]) == 3,
    "named-target list changed")

m = json.load(open(f"{FS}/fullseq_measured.json"))
chk(m["S0_dials_move"], "S0 dial-movement finding regressed — it is what "
                        "makes the mid-stack predictor meaningful")
chk(not m["S3_kill"]["abort_NO_RISK"], "kill criterion now aborts")
chk(m["S3_kill"]["delta_max_sigma"] > 1.0, "Delta_max collapsed")
chk(m["verdict"]["primary"] == "HIGHER_ORDER_MEASURED", "verdict changed")
chk(not m["verdict"]["control_fired"], "rtilde control fired — instrument")

H = m["S1_H"]
rows = m["S2_orderings"]
# single transpositions are the sanity floor: exact by construction
for k, v in H.items():
    if rows[k]["n_inversions"] == 1:
        chk(abs(v["H"]) < 1e-9, f"{k}: single-transposition H no longer exact")
# the finding: H resolvable at multi-inversion orderings, and POSITIVE
multi = [(k, v) for k, v in H.items() if rows[k]["n_inversions"] > 1]
chk(len(multi) >= 3, "multi-inversion sample shrank")
# NOTE: the sealed sample's multi-inversion H are all positive, which is what
# the ORIGINAL headline rested on. That headline was RETRACTED by the
# exhaustive out-of-sample test (subadditivity.json) — this check pins what
# the sealed sample showed, NOT a claim that sub-additivity is general.
chk(all(v["H"] > 0 for _, v in multi),
    "the sealed sample's multi-inversion H changed sign")
chk(max(abs(v["z"]) for _, v in multi) > 3.0,
    "H no longer resolvable at any multi-inversion ordering")
# second-order growth: the 3-inversion H exceeds both 2-inversion H's
h3 = [v["H"] for k, v in multi if rows[k]["n_inversions"] == 3]
h2 = [v["H"] for k, v in multi if rows[k]["n_inversions"] == 2]
chk(h3 and h2 and min(h3) > max(h2),
    "H no longer grows with inversion count")

# the exhaustive out-of-sample test and its RETRACTION of the headline
sub = json.load(open(f"{FS}/subadditivity.json"))
chk(sub["P3"]["holds"], "single-transposition exactness (sanity floor) broke")
chk(sub["P1"]["holds"] is False,
    "the sub-additivity FALSIFICATION vanished — the retraction is "
    "load-bearing and must not be quietly reversed")
chk(sub["P1"]["significant_violations"] >= 5,
    "significant super-additive orderings dropped below the banked count")
chk(sub["n_orderings"] == 59, "exhaustive set is no longer exhaustive")
chk(sub["P2"]["monotone"] is False, "P2 falsification vanished")

if fails:
    print("VERIFY_FULLSEQ: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_FULLSEQ: seal, kill criterion, S0, H-structure all green")
