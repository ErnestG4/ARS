"""Live checker for the RIGID_GUE arc (witness-must-be-able-to-fail terminal
form).  Nonzero exit on regression; blob-SHA tamper-evidence."""

import hashlib
import json
import sys

RG = "/home/combust/fmexplorer/criticality_tool/rigidgate"
fails = []


def chk(c, m):
    if not c:
        fails.append(m)


seal = json.load(open(f"{RG}/prereg_sealed.json"))
for f, sha in seal["code_freeze_blob_shas"].items():
    d = open(f"{RG}/{f}", "rb").read()
    chk(hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha,
        f"freeze violation: {f}")
chk([a["id"] for a in seal.get("addenda", [])]
    == [f"RG-ADD-{i}" for i in range(1, 9)], "addenda block changed")

kag = json.load(open(f"{RG}/kag_measured.json"))
chk(kag["PASS"], "KAG not PASS")
chk(kag["marginal_exact_identity"]["all_identical"],
    "marginal-exactness identity regressed")
chk(all(v["clock_verdict"] == "HYPER_RIGID"
        for v in kag["hyper_arm"].values()), "HYPER arm stopped firing")
chk(all(v["gue_false_hyper_rate"] <= 0.05
        for v in kag["hyper_arm"].values()), "HYPER arm specificity cost")

g = json.load(open(f"{RG}/gate_measured.json"))
chk(g["R1"]["PASS"], "R1 band validity regressed")
# the two load-bearing findings, pinned
chk(g["R2"]["rows"]["C-brocot"]["false_rigid_rate"] > 0.01,
    "small-n thinness finding vanished (F2)")
chk(g["R2"]["rows"]["C-zeta"]["false_rigid_rate"] <= 0.01,
    "large-n soundness finding vanished (F2)")
chk(g["R3"]["extras"]["clock"]["deployed"] == "RIGID_GUE"
    and g["R3"]["extras"]["clock"]["proposed"] == "HYPER_RIGID",
    "the demonstrated hole (clock earns GUE pole) regressed")
chk(not g["R4"]["zeta_first_2000"]["moves"]
    and not g["R4"]["brocot_golden"]["moves"],
    "banked-row materiality changed — re-report before adopting")
chk(g["verdict"]["hole_demonstrated"], "hole flag cleared")

# the proposed rule must still be two-sided-correct on the battery
sys.path.insert(0, RG)
from proposed_rule import rigid_cell                        # noqa: E402
band = dict(mean=1.0, sd=0.1)
chk(rigid_cell(1.0, band)[0] == "RIGID_GUE", "rule: in-band")
chk(rigid_cell(0.5, band)[0] == "HYPER_RIGID", "rule: below-band")
chk(rigid_cell(2.0, band)[0] is None, "rule: above-band falls through")

if fails:
    print("VERIFY_RIGIDGATE: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_RIGIDGATE: seal, addenda, KAG, findings, and rule all green")
