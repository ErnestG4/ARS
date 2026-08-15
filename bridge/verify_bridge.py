"""Live checker for the bridge arc's banked state (2026-08-15, review F7:
PASS booleans in JSON with no asserting consumer are a permanently-inert
verification artifact).  Exit nonzero if any banked gate/witness regresses.
Run after any edit touching bridge/ or its dependencies."""

import json
import sys

BR = "/home/combust/fmexplorer/criticality_tool/bridge"
fails = []


def chk(cond, msg):
    if not cond:
        fails.append(msg)


a = json.load(open(f"{BR}/bridge_a_measured.json"))
for k in ("G_A1_1d_PASS", "G_A3_1d_pois_PASS", "G_A2_PASS", "G_A3_1d_zeta_PASS",
          "G_A1_2d_PASS", "G_A3_2d_PASS", "G_B1_PASS", "XCHECK_PASS"):
    chk(a.get(k) is True, f"bridge_a gate {k} not True")
for row in a["A2_ginibre"]["glue_descriptive"]:
    chk("amplification_per_unit_offset" in row, "amplification column missing")

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
    data = open(f"/home/combust/fmexplorer/criticality_tool/{f}", "rb").read()
    cur = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    if cur != sha:
        print(f"VERIFY_BRIDGE: FAIL — {f} blob {cur[:12]} != addendum {sha[:12]}")
        sys.exit(1)
print("VERIFY_BRIDGE: blob SHAs match the addendum")
