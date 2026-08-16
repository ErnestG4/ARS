"""RIGID_GUE arc seal.  COMMITTED GENERATOR of rigidgate/prereg_sealed.json.

Sequence (pilot-informed-seal, declared): brief architected -> provenance
archaeology -> pre-seal pilots (band scan, zeta lens sweep, growth-arm power
measurement) -> KAG battery, including the in-window withdrawal of the
growth arm and the design of the HYPER_RIGID split -> THIS SEAL ->
measurement.  The debugging window closes with the seal (D1 clause).
"""

import hashlib
import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
FREEZE = ["gate_probe.py", "proposed_rule.py", "kag_gate.py", "run_gate.py",
          "kag_measured.json"]


def blob(p):
    d = open(p, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


kag = json.load(open(f"{ROOT}/rigidgate/kag_measured.json"))
assert kag["PASS"], "no seal over a red gate"

seal = dict(
    sealed_utc_date="2026-08-16",
    arc="RIGID_GUE gate characterization (RIGIDGATE_BRIEF.md); discharges "
        "cross_substrate REGISTERED-OPEN / holonomy seal ADD-5.",
    posture="Instrument characterization. NO new science claims. Nothing "
            "under cross_substrate/ is written; NO banked row is "
            "re-verdicted — R4 reports what a rule WOULD do, labeled.",
    debug_freeze="BINDING (D1 clause verbatim): the KAG is the one place "
                 "debugging is legal, and THE DEBUGGING WINDOW CLOSES WHEN "
                 "THE SEAL CLOSES.",
    configs=dict({"C-brocot": [343, 6.86], "C-add5": [1200, 20.0],
                  "C-zeta": [2000, 40.0]}),
    lens_deg=6, band_seeds=24, mult=2.5,
    r1_band_tolerance=0.20,
    r1_note="measured GUE band mean vs Mehta (ln 2piL + gamma + 1)/pi^2, "
            "and renewal decoy mean vs Var(s)*L with Var(s)=3pi/8-1. A band "
            "outside tolerance would mean the LENS is the story.",
    r2_draws=dict(renewal=200, gue=48, poisson=48),
    r2_target="P(false RIGID | renewal) <= 0.01 at every config for the "
              "gate to be called sound against its calibrated family.",
    r3_family=dict(antithetic_f_grid=[0.0, 0.02, 0.05, 0.08, 0.12, 0.2, 0.5,
                                      1.0],
                   bisect_tol=0.005, draws_per_f=12,
                   extras=["clock", "jitter_clock_0.1", "cumulant"]),
    r4_banked_rows=dict(
        brocot_golden=dict(n=343, L=6.86, sigma2=0.635, gue_mean=0.576,
                           z_reported=0.49,
                           sd_reconstructed=(0.635 - 0.576) / 0.49,
                           source="verify/tier2_results.md:46-50"),
        zeta_first_2000=dict(source="RESULTS.md ζ RIGID_GUE claim; measured "
                                    "live from zeros_2000.npy under the "
                                    "banked RvM unfold")),
    r5_battery=["gue", "poisson", "renewal", "antithetic_fstar", "clock",
                "jitter_clock", "zeta", "brocot"],
    proposed_fix="Split the one-sided RIGID branch into RIGID_GUE (|z|<=2.5) "
                 "and HYPER_RIGID (z<-2.5). Same boundary formula, same "
                 "multiplier, no new constant, no statistic added.",
    rejected_designs=list(kag["rejected_designs"].keys()),
    verdicts=["GATE_SOUND", "GATE_BOUNDED", "GATE_DEFECTIVE", "UNDERPOWERED"],
    verdict_rule="GATE_SOUND iff R2 target met AND no tested decoy family "
                 "member crosses the boundary. GATE_BOUNDED iff R2 target "
                 "met but a demonstrated hole exists outside the calibrated "
                 "family. GATE_DEFECTIVE iff a banked verdict is wrong under "
                 "the gate's own stated intent.",
    extension_rule="UNDERPOWERED only: one doubling of r2_draws, fires once.",
    code_freeze_blob_shas={f: blob(f"{ROOT}/rigidgate/{f}") for f in FREEZE},
)
json.dump(seal, open(f"{ROOT}/rigidgate/prereg_sealed.json", "w"), indent=1)
print(f"SEALED: rigidgate/prereg_sealed.json ({len(FREEZE)} files frozen)")
