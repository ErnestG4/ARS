"""Live checker for the survey arc's banked state (witness-must-be-able-to-
fail terminal form).  Nonzero exit on any regression.  Includes blob-SHA
tamper-evidence against the seal's freeze list."""

import hashlib
import json
import sys

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.dirname(_HERE)
SV = _HERE
fails = []


def chk(cond, msg):
    if not cond:
        fails.append(msg)


seal = json.load(open(f"{SV}/prereg_sealed.json"))
for f, sha in seal["code_freeze_blob_shas"].items():
    d = open(f"{SV}/{f}", "rb").read()
    cur = hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()
    chk(cur == sha, f"freeze violation: {f}")

kag = json.load(open(f"{SV}/mask_kag_measured.json"))
chk(kag["PASS"] is True, "mask KAG not PASS")
chk(kag["red"]["fired"] is True, "red path did not fire")

d2 = json.load(open(f"{SV}/d2_gates_measured.json"))
chk(d2["PASS"] is True, "D2 FIX-2 gate not PASS")
chk(d2["powered_fired"] is True, "powered FIX-2 not fired")

d3 = json.load(open(f"{SV}/d3_measured.json"))
for s, row in d3["slices"].items():
    v = row["verdict"]
    chk(v["primary"] == "CLASS_MEASURED", f"{s}: verdict regressed to {v['primary']}")
    chk(not v["flags"], f"{s}: unexpected flags {v['flags']}")
    chk(abs(row["exponent"]["slope"] - 1.190) < 0.01,
        f"{s}: exponent drifted from banked 1.190")

man = json.load(open(f"{SV}/MANIFEST.json"))
chk(len(man["files"]) == 11, "manifest file count changed")

if fails:
    print("VERIFY_SURVEY: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_SURVEY: seal, gates, verdicts, and freeze all green")
