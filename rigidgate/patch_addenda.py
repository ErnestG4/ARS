"""Dated addenda to the RIGID_GUE arc seal (run once, 2026-08-16).
COMMITTED GENERATOR of the seal's `addenda` block.  gate_measured.json is
NOT edited — the generator's output stays the raw record; interpretation
lives here and in RESULTS_RIGIDGATE.md."""

import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
P = f"{ROOT}/rigidgate/prereg_sealed.json"

seal = json.load(open(P))
assert "addenda" not in seal, "run-once guard"

seal["addenda"] = [
    dict(
        id="RG-ADD-1", date="2026-08-16",
        title="Sealed lattice has no cell for the outcome that occurred",
        three_event=[
            "seal defined GATE_SOUND / GATE_BOUNDED (both requiring the R2 "
            "target met) and GATE_DEFECTIVE (defined by a banked verdict "
            "being WRONG)",
            "measurement produced: R2 target met at 2 of 3 configs, missed "
            "at C-brocot (false-RIGID 0.035 > 0.01), with NO banked verdict "
            "shown wrong (brocot sits at z=+0.49, comfortably inside the "
            "band; the 3.5% is a rate over hypothetical renewal draws, not "
            "evidence about that row)",
            "run_gate.py's else-branch assigned GATE_DEFECTIVE, which the "
            "sealed PROSE does not authorise for this outcome — recorded "
            "here as a lattice hole of THIS arc's design, not silently "
            "retitled"],
        substantive_verdict="GATE_CONFIG_DEPENDENT (the missing cell): the "
                            "gate is sound against its calibrated decoy "
                            "family at n>=1200 (margin 3.6-3.8 sigma, "
                            "false-RIGID 0.000) and thin at small n "
                            "(n=343: margin 1.5 sigma, false-RIGID 0.035); "
                            "and it is BOUNDED in the brief's sense — a "
                            "demonstrated hole exists outside the "
                            "calibrated family (hyper-rigid processes earn "
                            "the GUE pole).",
        proposed_cell="Future runs of this arc adopt GATE_CONFIG_DEPENDENT "
                      "with the per-config error-rate table as its payload; "
                      "the banked JSON keeps the code's raw output so the "
                      "hole stays visible in the record.",
    ),
    dict(
        id="RG-ADD-2", date="2026-08-16",
        title="ADD-5's thinness figure corrected — and re-vindicated at a "
              "different configuration",
        detail="The holonomy seal's ADD-5 quoted ~1.1 sigma from an 8-draw "
               "renewal sample compared min-to-boundary; that is a "
               "small-sample artifact (the sd was over-estimated at 1.5 vs "
               "a 200-draw value of 0.72, and a min is not a band). "
               "Properly measured the margin at that configuration "
               "(n=1200, L=20) is 3.6 sigma with false-RIGID 0.000. "
               "HOWEVER the concern is re-vindicated at the SMALL-n "
               "configuration the banked approximability rows actually use "
               "(n=343, L=6.86): margin 1.5 sigma, false-RIGID 0.035. The "
               "thinness is real and CONFIGURATION-DEPENDENT, concentrated "
               "where small-n rows live — which is why a per-verdict "
               "margin re-derivation (the ADD-5 trigger's own proposal) is "
               "the right instrument.",
    ),
    dict(
        id="RG-ADD-3", date="2026-08-16",
        title="R5 battery tested the adversarial family at the wrong member",
        three_event=[
            "R5 was sealed to test 'antithetic_fstar'",
            "f* is by construction the BOUNDARY-CROSSING member, so testing "
            "the rule there tests it exactly at the boundary, where any "
            "band rule passes by definition — the battery's "
            "rejects_hyper_spoofs flag therefore came back False for a "
            "reason that carries no information about the fix",
            "corrected reading recorded here: the proposed fix rejects "
            "every HYPER-rigid member (clock z=-5.09, jitter-clock -4.22, "
            "antithetic f<=0.02) and correctly does NOT reject a member "
            "tuned to sit inside the band — see RG-ADD-4, which is a limit, "
            "not a defect"],
    ),
    dict(
        id="RG-ADD-4", date="2026-08-16",
        title="Fundamental limit, stated as scope",
        detail="A marginal-EXACT construction tuned to f* ~ 0.056 has GUE "
               "NNS by permutation identity AND Sigma^2 inside the GUE band "
               "at the tested L (z=+0.67). No rule built on Sigma^2 at a "
               "single L can exclude it, because it matches on both "
               "measured quantities. The gate's claim is therefore bounded "
               "to NON-ADVERSARIAL substrates — the same shape as the "
               "module's founding lesson one level up: NNS certifies the "
               "marginal, not the class; Sigma^2 at one L certifies "
               "rigidity AT THAT SCALE, not the class.",
    ),
    dict(
        id="RG-ADD-5", date="2026-08-16",
        title="Marginal-exactness is an identity pre-cumsum, 3e-4 post",
        detail="KAG cell D verifies the antithetic construction and the "
               "renewal decoy share a bit-identical sorted spacing multiset "
               "(18/18). The R3 KS comparison runs after a cumsum "
               "round-trip, where floating-point non-associativity "
               "perturbs the recovered spacings in the last ulps: KS "
               "0.011845 vs 0.012202. The construction is exact; the "
               "reported KS equality is not, and the run's "
               "'identical=False' means round-trip, not construction.",
    ),
]
json.dump(seal, open(P, "w"), indent=1)
print(f"addenda applied: {[a['id'] for a in seal['addenda']]}")
