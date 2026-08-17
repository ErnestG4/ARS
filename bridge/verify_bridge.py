"""Live checker for the bridge arc's banked state (2026-08-15, review F7:
PASS booleans in JSON with no asserting consumer are a permanently-inert
verification artifact).  Exit nonzero if any banked gate/witness regresses.
Run after any edit touching bridge/ or its dependencies."""

import json
import sys

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.dirname(_HERE)
BR = _HERE
fails = []


def chk(cond, msg):
    if not cond:
        fails.append(msg)


a = json.load(open(f"{BR}/bridge_a_measured.json"))
for k in ("G_A1_1d_PASS", "G_A3_1d_pois_PASS", "G_A2_PASS", "G_A3_1d_zeta_PASS",
          "G_A1_2d_PASS", "G_A3_2d_PASS", "G_B1_PASS", "XCHECK_PASS"):
    chk(a.get(k) is True, f"bridge_a gate {k} not True")
# The SNR law A = mu^2/Var is TOOLKIT §11.3's headline (14 / 98 / 528 across
# R = 2/4/6). The original check asserted only that the COLUMN EXISTS, which
# could fail solely by the key vanishing — a presence check standing in for a
# value check. Found by red-pathing: busting every amplification value to 1.0
# left this checker green. Values now pinned.
_AMP_BANKED = {2.0: 14.2, 4.0: 98.0, 6.0: 527.9}
for row in a["A2_ginibre"]["glue_descriptive"]:
    chk("amplification_per_unit_offset" in row, "amplification column missing")
    _R = row.get("R")
    if _R in _AMP_BANKED:
        _got = row["amplification_per_unit_offset"]
        chk(abs(_got / _AMP_BANKED[_R] - 1.0) < 0.02,
            f"SNR-law amplification drifted at R={_R}: {_got} vs banked "
            f"{_AMP_BANKED[_R]} (TOOLKIT §11.3)")

b = json.load(open(f"{BR}/bridge_b_measured.json"))
chk(b["B1"]["B1_PASS"] is True, "B1_PASS not True")
chk(b["B2"]["intensity_budget"]["within"] is True, "B2 budget not within (measured-gated)")
chk(b["B2"]["g_below_sqrt2"] == 0.0, "support-set witness g_below_sqrt2 != 0")
chk(b["B2"]["fix2_criterion"]["FIRED"] is True, "powered FIX-2 not FIRED")
chk("spatstat_D_uniform" in b["B2"], "B2 spatstat cross-check missing")
chk("spatstat_error" not in b["B2"], "stale spatstat_error key present")

if fails:
    print("VERIFY_BRIDGE: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_BRIDGE: all banked gates and witnesses green")


# Blob-SHA tamper-evidence (F6 backport): assert the addendum-recorded SHAs
# match the working tree; editing any listed file requires a new dated addendum.
import hashlib
seal = json.load(open(f"{BR}/prereg_sealed.json"))
for f, sha in seal.get("post_seal_addendum_2026_08_15", {}).get("frozen_blob_shas", {}).items():
    data = open(_os.path.join(_REPO, f), "rb").read()
    cur = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    if cur != sha:
        print(f"VERIFY_BRIDGE: FAIL — {f} blob {cur[:12]} != addendum {sha[:12]}")
        sys.exit(1)
print("VERIFY_BRIDGE: blob SHAs match the addendum")
