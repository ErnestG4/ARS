"""RIGID_GUE arc addenda RG-ADD-6..8 (Will's review round, 2026-08-16).
Run once.  COMMITTED GENERATOR of the seal's addenda extension."""

import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
P = f"{ROOT}/rigidgate/prereg_sealed.json"

seal = json.load(open(P))
ids = [a["id"] for a in seal["addenda"]]
assert "RG-ADD-6" not in ids, "run-once guard"

seal["addenda"] += [
    dict(
        id="RG-ADD-6", date="2026-08-16",
        title="The ADD-5 correction is luck, not vindication — recorded as "
              "such at Will's instruction",
        detail="ADD-5's '~1.1 sigma' originated with CC and was repeated in "
               "Will's audit; NEITHER of us checked the standard deviation "
               "the figure was built on (8 draws, sd 1.5 against a "
               "200-draw value of 0.72, and a min compared to a boundary "
               "rather than a band). The concern re-vindicating at n=343 "
               "(1.5 sigma, false-RIGID 0.035) is a COINCIDENCE of "
               "configuration, not evidence that the original estimate was "
               "sound: the estimate was made at n=1200, where the true "
               "margin is 3.6 sigma and the false-RIGID rate is 0.000. "
               "Banked this way deliberately — an audit item that turns "
               "out to have been mis-measured is itself a finding "
               "(brief tripwire 5), and recording the near-miss is worth "
               "more than the number having happened to hold.",
        lesson="a sigma quoted from a small draw count is a sample "
               "statistic, not a property of the gate; check the "
               "denominator before an audit item inherits it.",
    ),
    dict(
        id="RG-ADD-7", date="2026-08-16",
        title="Delta_3 arm reclassified: PROMOTABLE, not rejected",
        detail="The arc filed the Delta_3 growth arm under rejected "
               "designs because it flags the banked zeta row at z=-9.5. "
               "Will's correction, adopted: that is a mismatch between the "
               "GATE'S L POLICY and the SUBSTRATE'S validity window, not a "
               "defect in Delta_3. The arm rejects every spoof at ~12:1 "
               "power and fails only on a substrate being judged 8.3x past "
               "its own Berry saturation scale (measured at the banked "
               "config: L=50 vs ln(T/2pi)=5.99). A Delta_3 variant with a "
               "SUBSTRATE-AWARE L cap may therefore dominate the deployed "
               "gate on BOTH axes (rejects hyper-rigid spoofs AND keeps "
               "genuine low-height arithmetic rows). Moved to "
               "registered-open as a promotable variant; the measured "
               "power numbers (GUE increment 0.1053 +/- 0.0086) carry over "
               "as its starting calibration.",
    ),
    dict(
        id="RG-ADD-8", date="2026-08-16",
        title="Single-L census run; F4 promoted from scope note to "
              "registered-open",
        detail="Census of every long-range gate call site at head: 6 gate "
               "sites, ALL single-L, NONE sweeps L; multi-L sites = zero. "
               "Delta_3 is computed at every site and discarded as "
               "secondary, so the gate is single-L AND effectively "
               "single-statistic. Highest exposure: "
               "cross_substrate/longrange_audit.py:36 uses a FIXED "
               "AUDIT_L=50.0 across heterogeneous arithmetic substrates — "
               "the banked zeta row was judged at 8.3x its own saturation "
               "scale (z=-2.33 measured at that exact configuration). "
               "Full table and priority-ordered hardening in "
               "rigidgate/SINGLE_L_CENSUS.md. Scope statement stands: the "
               "spoof is adversarial, no natural substrate does this, and "
               "nothing here shows a banked row to be wrong — what is "
               "established is that every RIGID_GUE row certifies "
               "rigidity AT ONE SCALE, not class.",
    ),
]
json.dump(seal, open(P, "w"), indent=1)
print(f"addenda now: {[a['id'] for a in seal['addenda']]}")
