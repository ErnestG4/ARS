"""Live checker for the comb arc's banked state (bridge review F7 applied to
the sibling arc in the same stroke).  Exit nonzero on regression."""

import json
import sys

CT = "/home/combust/fmexplorer/criticality_tool"
fails = []


def chk(cond, msg):
    if not cond:
        fails.append(msg)


for f, tag in (("exact_offsets_kag_measured.json", "band1"),
               ("exact_offsets_kag_band2_measured.json", "band2")):
    k = json.load(open(f"{CT}/comb/{f}"))
    chk(k["PASS"] is True, f"estimator KAG {tag} not PASS")

m = json.load(open(f"{CT}/comb/comb_measured.json"))
chk(m["VERDICT"].startswith("PASS"), f"comb verdict regressed: {m['VERDICT']}")
chk(m["measured_power_ok"] is True, "measured power criterion not met")
chk(m["discriminator"]["resolved"] is True, "N50 discriminator unresolved")
# The 53.9 sigma IS the headline; the resolved flag alone could stay True with
# the separation collapsed. Found by red-pathing (busting sigma left this
# green). Value pinned.
chk(abs(m["discriminator"]["z"] - 53.94) < 0.5,
    f"N50 discriminator z drifted from the banked 53.94: "
    f"{m['discriminator']['z']}")
chk(m["level_all_mandatory_within_k"] is True, "level test regressed")

s = json.load(open(f"{CT}/comb/prereg_sealed.json"))
chk("post_seal_addendum_2026_08_15" in s, "seal addendum missing")
chk(abs(s["prediction_first"]["C_prime_G"] - 0.83829544) < 1e-8,
    "C'_G drifted from sealed value")

sys.path.insert(0, CT)
import calibrator_panel as cp                     # import runs _schema_self_check
chk("gp_comb" in dict(cp.CALIBRATORS_2D), "gp_comb not seated")
chk(cp.CALIBRATOR_TIERS.get("gp_comb") == cp.TIER_CONJECTURE, "gp_comb tier wrong")

if fails:
    print("VERIFY_COMB: FAIL")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("VERIFY_COMB: all banked gates, seal, and seating green")
