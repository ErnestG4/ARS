"""RIGID_GUE seal addendum RG-ADD-9 (2026-08-17): the Delta_3 promotion is
re-confirmed against CURRENTLY banked evidence, and the re-check finds a gap.
Run once."""
import json
ROOT = "/home/combust/fmexplorer/criticality_tool"
P = f"{ROOT}/rigidgate/prereg_sealed.json"
seal = json.load(open(P))
ids = [a["id"] for a in seal["addenda"]]
assert "RG-ADD-9" not in ids, "run-once guard"
seal["addenda"].append(dict(
    id="RG-ADD-9", date="2026-08-17",
    title="Delta_3 promotion RE-CONFIRMED against current evidence — and "
          "downgraded to PROMOTABLE-PENDING-POWER-INSIDE-WINDOW",
    why_rechecked="RG-ADD-7 reclassified the Delta_3 growth arm from "
                  "'rejected' to PROMOTABLE on the reasoning that its zeta "
                  "failure was an L-POLICY mismatch rather than a defect. "
                  "That diagnosis has since been through three corrections "
                  "(LC-ADD-1 the cap is n-dependent; LC-ADD-4/5 the caps "
                  "were withdrawn as biased AND measuring the wrong "
                  "estimand; LC-ADD-6/8 re-derived at the correct estimand). "
                  "A promotion resting on superseded reasoning is exactly "
                  "the kind of thing that survives by not being re-read.",
    what_survives="The QUALITATIVE claim survives and is strengthened: the "
                  "Delta_3 arm rejected every spoof and failed only on a "
                  "substrate judged far outside its own validity window, and "
                  "the current evidence puts that window at L <= 5.99 for "
                  "zeta (Berry) against a deployed L of 50 — a larger "
                  "mismatch than the original diagnosis assumed.",
    the_gap="But the POWER FIGURE that made it 'promotable' (GUE increment "
            "0.1053 +/- 0.0086, ~12:1) was measured across a lever of "
            "L = 5 -> 40. Under the CURRENT banked policy the only "
            "admissible cell at n=2000 is L = 5, and nothing is admissible "
            "at n=1200 or n=343. A growth arm needs TWO L values, so inside "
            "a window capped near 6 the available lever is at best L in "
            "[2, 6] — roughly 3x, against the 8x lever the 12:1 figure was "
            "measured on. POWER INSIDE THE DEPLOYABLE WINDOW WAS NEVER "
            "MEASURED, and a growth statistic's power falls with the lever.",
    status="PROMOTABLE-PENDING-POWER-INSIDE-WINDOW. The brief for the "
           "Delta_3 variant must OPEN by measuring the arm's increment and "
           "its variance over L in [2, 6] at the deployed n. If the 12:1 "
           "does not survive the shorter lever, the variant is not a "
           "candidate instrument and the n=343 problem needs more data "
           "rather than a different statistic.",
))
json.dump(seal, open(P, "w"), indent=1)
print(f"addenda now: {[a['id'] for a in seal['addenda']]}")
