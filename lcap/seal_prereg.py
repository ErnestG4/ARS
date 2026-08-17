"""L-policy arc seal.  COMMITTED GENERATOR of lcap/prereg_sealed.json.

Ordering is the ruling (2026-08-16) and is enforced in code: validity map
-> policy derivation -> ZOO GATE (condition 1, must PASS) -> THIS SEAL ->
power cell -> banked rows -> ZETA LAST.  run_lcap.py refuses to evaluate
zeta unless zoo_measured.json records PASS.
"""

import hashlib
import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
FREEZE = ["validity.py", "policy.py", "zoo_validate.py", "run_lcap.py",
          "validity_scales.json", "policy.json", "zoo_measured.json"]


def blob(p):
    d = open(p, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


zoo = json.load(open(f"{ROOT}/lcap/zoo_measured.json"))
assert zoo["PASS"], "condition 1 unmet — no seal over a red zoo gate"
pol = json.load(open(f"{ROOT}/lcap/policy.json"))

seal = dict(
    sealed_utc_date="2026-08-16",
    arc="Substrate-aware L policy (LCAP_BRIEF.md), run under the three "
        "conditions.",
    posture="Instrument arc, propose-only. Nothing under cross_substrate/ is "
            "written; NO banked row is re-verdicted — L1 reports what the "
            "policy WOULD yield.",
    debug_freeze="BINDING (D1 clause): the debugging window closes with this "
                 "seal.",

    condition_1_satisfied=dict(
        ruling="the capped policy must earn its trust on the calibrator zoo "
               "alone, with no reference to zeta; zeta runs last",
        zoo_gate="PASS (lcap/zoo_measured.json), 6 known-class members",
        discovery="the FIRST zoo run FAILED on GOE: at the deployed L=50 a "
                  "genuinely different universality class read RIGID_GUE. "
                  "Across L=3..50 the GUE band's spread grows ~5.7x while "
                  "the GUE-GOE gap grows only ~1.4x, so discrimination "
                  "degrades with L even where the GUE form is perfectly "
                  "valid. This produced a SECOND cap, independent of the "
                  "validity argument and derived entirely from the zoo.",
        policy=pol["rule"], discrimination_L=pol["discrimination_L"],
        Z_SEP=pol["Z_SEP"]),

    condition_2_zeta_direction=dict(
        ruling="pre-commit zeta's direction under the cap; a zero or "
               "positive z is an inconsistency with a banked lens-invariant "
               "measurement and HALTS",
        sealed_prediction="z(zeta) < 0 at L_judge = 5.99",
        halt_condition="z >= 0 -> HALT_INCONSISTENT, no reclassification, "
                       "audit the banked lens-invariance measurement first",
        DISCLOSURE="the stated expectation was 'negative at REDUCED "
                   "significance'. I must disclose that I already hold "
                   "pre-seal data bearing on the magnitude: the rigidgate "
                   "arc measured zeta at L = 2,3,5,8,12,20,40 with z_d6 = "
                   "-3.90,-6.07,-4.40,-4.33,-4.76,-2.89,-2.57. Those imply "
                   "significance INCREASES under the cap (the band sd "
                   "shrinks faster with L than the deficit does), i.e. the "
                   "'reduced significance' half of the expectation is "
                   "expected to be VIOLATED. Registered here in advance "
                   "rather than discovered after. The SIGN half — the halt "
                   "condition — is the load-bearing pre-commitment and is "
                   "not weakened by this disclosure.",
        expectation_magnitude="|z| INCREASES relative to the L=50 value of "
                              "-2.33 (registered counter-expectation; a "
                              "violation is filed, not halted)"),

    condition_3_power_decides=dict(
        ruling="L3's power number decides what a move means; if the capped "
               "statistic cannot resolve an effect of the size already "
               "measured, the verdict is UNDER_RESOLVED, not 'consistent "
               "with GUE'",
        rule="at L_judge compute MDD = k * band_sd; if |measured effect| <= "
             "MDD then any in-band reading is UNDER_RESOLVED",
        k=2.5),

    banked_rows=dict(
        zeta_first_2000=dict(L_deployed=50.0, L_judge=5.99,
                             binding="validity (Berry)", order="LAST"),
        brocot_golden=dict(n=343, L_deployed=6.86,
                           L_judge=pol["policy"]["gue_n343"]["L_judge"],
                           note="6.86 < 8.0 cap -> policy does not move this "
                                "row; reported for completeness"),
        allen_v1=dict(note="0/100 RIGID_GUE — a NEGATIVE result; the policy "
                           "can only tighten the rigid branch, so the "
                           "direction cannot flip these rows. Not re-run.")),

    verdicts=["L_POLICY_FIXED", "L_POLICY_TRADEOFF", "NO_VALIDITY_SCALE",
              "UNDER_RESOLVED", "HALT_INCONSISTENT"],
    presentational_requirement="the note: the zeta row has now moved "
                               "three times (confirmed-at-class-level -> "
                               "superseded -> whatever the cap yields). Its "
                               "OWN HISTORY is banked beside its value in "
                               "RESULTS_LCAP.md — a row that has moved three "
                               "times is trustworthy if the moves are "
                               "visible and merely unstable if they are not.",
    code_freeze_blob_shas={f: blob(f"{ROOT}/lcap/{f}") for f in FREEZE},
)
json.dump(seal, open(f"{ROOT}/lcap/prereg_sealed.json", "w"), indent=1)
print(f"SEALED: lcap/prereg_sealed.json ({len(FREEZE)} files frozen)")
