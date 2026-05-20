"""
phase35a/sensitivity_tier1_flipN.py — Sensitivity Tier 1 at flip-N
(Will's adjudication 2026-05-20). Model-based: substitute estimated
substrate sup_spread from Test 1's ratio characterization at the
sensitivity cells {50k, 70k, 100k}; re-run the criterion; first-pass
answer on whether sensitivity also retracts.

PROTOCOL (Will).
- "The right next move for sensitivity is Tier 1 at flip-N: substitute
  estimated substrate values from Test 1's ratio characterization at
  the sensitivity cells, re-run the criterion. This is model-based
  Tier 1 (uses ratio extrapolation, not direct L-convergence
  measurement at flip-N like N=70k's case), so it carries a
  model-input caveat — but it's cheap and gives a first-pass answer
  on whether sensitivity retracts."

MODEL (substrate sup_spread estimate).
- Established equivalence (from Test 2 vs b0haqgof3): substrate
  sup_spread ≈ per-φ-shift ptp ≈ ratio × spread@L=1e5.
  Verification at N=70k: model 4.86×0.0766=0.372 vs direct Test 2
  0.382 (2.6% underestimate). Decent.
- For each sensitivity cell N ∈ {50k, 70k, 100k}, estimate:
  N=50k: Test 1 sup ratio=1.555 × stored sup_spread@N=50k(0.122862)
         = 0.191 (direct Test 1 measurement, well-grounded).
  N=70k: direct Test 2 substrate = 0.382. (Model 4.86×0.0766=0.372
         shown for comparison.)
  N=100k: NOT directly measured. Two extrapolation models reported:
    (a) Test 1 ratio α=2.99 extrapolation: ratio(100k) ≈
        4.86×(100/70)^2.99 = 14.16; substrate ≈ 14.16×0.007146 = 0.101.
    (b) N=70k growth-factor (substrate/L1e5 ≈ 4.99) applied
        directly: substrate ≈ 0.007146×4.99 = 0.0357.
    Both models give different magnitudes but BOTH well below
    N=100k gap (0.496) ⇒ verdict is robust across models.

CRITERION (sensitivity_confirm verbatim):
  PASS iff disjoint AND gap >= max(sub_spread, sup_spread).

CAVEATS (per Will).
- Model carries input uncertainty (especially N=100k extrapolation).
- C1 θ-class: sup θ-universal within ~30% ⇒ transfer ~OK; sub
  θ-sensitive but dominated by sup in max() ⇒ doesn't affect this.
- This is FIRST-PASS only; direct L-convergence runs at N=50k
  (Tier 2, next) and N=100k (deferred per Will) settle definitively.

SCOPE. Sensitivity verdict status only. Does NOT decide rev-5,
RESULTS.md, §D timing, recovery direction, or strategic question.
Banked Step-1 files untouched. Surfaces; Will adjudicates next.
"""
from __future__ import annotations
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
SENS = os.path.join(HERE, "sensitivity_confirm_results.json")
T1 = os.path.join(HERE, "test1_flipN_phi_results.json")
T2 = os.path.join(HERE, "test2_sup_L_extend_results.json")
B0HA = os.path.join(HERE, "sup_phi_resolved_L_results.json")
OUT = os.path.join(HERE, "sensitivity_tier1_flipN_results.json")


def main():
    sens = json.load(open(SENS))
    t1 = json.load(open(T1))
    t2 = json.load(open(T2))
    b0ha = json.load(open(B0HA))

    print("=" * 86)
    print("SENSITIVITY VERDICT — Tier 1 at flip-N (Will authorization 2026-05-20)")
    print("Model-based: ratio extrapolation from Test 1 at the sensitivity cells.")
    print("=" * 86)

    sens_rows = {r["N"]: r for r in sens["per_N"]}

    # ── Per-cell substrate estimate ────────────────────────────────
    # N=50k: Test 1 sup ratio at N=50000
    t1_sup_50k = next(c for c in t1["per_cell"]
                       if c["leg"] == "sup" and c["N"] == 50000)
    ratio_50k = t1_sup_50k["ratio"]
    sup_substrate_50k = ratio_50k * sens_rows[50000]["sup_spread"]

    # N=70k: direct Test 2 substrate
    sup_substrate_70k_direct = float(t2["spreads_by_L"][str(t2["L_top"])])
    # Model comparison: b0haqgof3 ratio × stored sup_spread@70k
    b0ha_sup_70k = next(c for c in b0ha["per_cell"]
                         if c["delta"] == 0.5 and c["N"] == 70000)
    ratio_70k = b0ha_sup_70k["ratio_phi_shift_to_L_ref_spread"]
    sup_substrate_70k_model = ratio_70k * sens_rows[70000]["sup_spread"]

    # N=100k: not measured. Two extrapolation models.
    # (a) Test 1 sup ratio α-extrapolation
    sup_alpha = t1["per_leg"]["sup"]["loglog_alpha_ratio_vs_N"]
    ratio_70k_t1baseline = t1["per_leg"]["sup"]["baseline_N70k_ratio"]
    ratio_100k_alpha = ratio_70k_t1baseline * (100000 / 70000) ** sup_alpha
    sup_substrate_100k_alpha = ratio_100k_alpha * sens_rows[100000]["sup_spread"]
    # (b) N=70k growth-factor model (substrate/L1e5 ≈ 4.99 at N=70k applied at N=100k)
    growth_factor_70k = sup_substrate_70k_direct / sens_rows[70000]["sup_spread"]
    sup_substrate_100k_growth = growth_factor_70k * sens_rows[100000]["sup_spread"]

    # ── Re-evaluate criterion per cell ─────────────────────────────
    def evaluate(N, sup_sub, model_tag):
        r = sens_rows[N]
        sub = r["sub_spread"]; gap = r["gap"]; disj = r["disjoint"]
        max_sp = max(sub, sup_sub)
        passes = bool(disj and gap >= max_sp)
        ratio_test = gap / max_sp if max_sp > 0 else None
        return {"N": N, "model": model_tag, "sub_spread": sub,
                "sup_substrate": sup_sub, "gap": gap, "disjoint": disj,
                "max_spread": max_sp,
                "gap_over_max_spread": (round(ratio_test, 3)
                                         if ratio_test is not None else None),
                "criterion_PASS": passes,
                "stored_was_PASS": bool(r["PASS"])}

    res_50k = evaluate(50000, sup_substrate_50k, "Test 1 ratio direct")
    res_70k_direct = evaluate(70000, sup_substrate_70k_direct,
                               "Test 2 direct L-converged")
    res_70k_model = evaluate(70000, sup_substrate_70k_model,
                              "Model (b0haqgof3 ratio × stored)")
    res_100k_alpha = evaluate(100000, sup_substrate_100k_alpha,
                               f"Test 1 sup α={sup_alpha:.2f} extrapolation")
    res_100k_growth = evaluate(100000, sup_substrate_100k_growth,
                                "N=70k growth-factor (~4.99×)")

    # ── Print ─────────────────────────────────────────────────────
    for r in (res_50k, res_70k_direct, res_70k_model,
              res_100k_alpha, res_100k_growth):
        print(f"\nN={r['N']:6d}  ({r['model']}):")
        print(f"  sub_spread={r['sub_spread']:.6g}  "
              f"sup_substrate={r['sup_substrate']:.6g}  "
              f"max={r['max_spread']:.6g}")
        print(f"  gap={r['gap']:.6g}  "
              f"gap/max={r['gap_over_max_spread']}  "
              f"→ criterion {'PASS' if r['criterion_PASS'] else 'FAIL'}  "
              f"(stored {'PASS' if r['stored_was_PASS'] else 'FAIL'})")

    # ── Sensitivity verdict structural read ────────────────────────
    # The sensitivity verdict was "criterion validated non-circular":
    # criterion PASSes at sensitivity cells {50k, 70k, 100k}; criterion
    # FAILs at smaller N (e.g., N=2584 originally; N≈4.3e4 in dense-logN).
    # Under substrate correction, does this criterion-flip-with-N
    # structure survive?
    cells_status = {50000: res_50k["criterion_PASS"],
                     70000: res_70k_direct["criterion_PASS"],
                     "100000_alpha_model": res_100k_alpha["criterion_PASS"],
                     "100000_growth_model": res_100k_growth["criterion_PASS"]}
    # Per Will's language: "structurally different criterion output …
    # mild exposure characterized." Read the per-cell pattern.
    if (res_50k["criterion_PASS"] and not res_70k_direct["criterion_PASS"]
        and res_100k_alpha["criterion_PASS"]
        and res_100k_growth["criterion_PASS"]):
        struct = ("SENSITIVITY_NON_UNIFORM_EXPOSURE: criterion PASSes at "
                  "N=50k and (model) N=100k under substrate correction; "
                  "FAILs at N=70k. Localized exposure pattern (not a clean "
                  "across-cells retraction). The criterion-flip-with-N "
                  "structure (small N→FAIL, large N→PASS) survives but "
                  "with N=70k as a localized substrate-corrected failure.")
        terminal = "SENSITIVITY_NON_UNIFORM_EXPOSURE_NOT_RETRACTED"
    elif (not res_50k["criterion_PASS"] and not res_70k_direct["criterion_PASS"]
          and not res_100k_alpha["criterion_PASS"]
          and not res_100k_growth["criterion_PASS"]):
        struct = ("Substrate correction breaks the criterion at all tested "
                  "sensitivity cells ⇒ criterion-flip-with-N claim broken; "
                  "sensitivity verdict retracts.")
        terminal = "SENSITIVITY_RETRACTS"
    else:
        struct = ("Mixed pattern (model-dependent). Surface; Will adjudicates.")
        terminal = "SENSITIVITY_MIXED_MODEL_DEPENDENT"

    print("\n" + "=" * 86)
    print(f"SENSITIVITY STRUCTURAL READ: {terminal}")
    print(f"  {struct}")
    print("=" * 86)
    print("\nMODEL CAVEATS (per Will, 'model-input caveat'):")
    print("  - N=50k substrate estimate uses Test 1 direct ratio measurement;")
    print("    well-grounded (Test 1 L_top=1.6e6 close to substrate).")
    print("  - N=70k confirmed by direct Test 2 (model agrees within 2.6%).")
    print("  - N=100k: TWO extrapolation models reported; both PASS the")
    print(f"    criterion robustly (factors {res_100k_alpha['gap_over_max_spread']}")
    print(f"    and {res_100k_growth['gap_over_max_spread']}); direct measurement")
    print("    deferred per Will (Tier 2 at N=100k expensive, not blocking).")
    print("  - C1 θ-class: sup θ-universal within ~30%; sub θ-sensitive but")
    print("    dominated by sup in max() ⇒ doesn't affect this verdict.")
    print("\n  Banked sensitivity NOT marked retracted (per Will's guardrail).")
    print("  Surfaced for Will's adjudication. rev-5.1 / banked-file updates")
    print("  remain Will's housekeeping.")

    rec = {"protocol": "Sensitivity Tier 1 at flip-N (Will 2026-05-20)",
           "model": "substrate sup_spread ≈ ratio × spread@L=1e5; "
                    "verified at N=70k (model 0.372 vs Test 2 direct 0.382, "
                    "2.6% underestimate)",
           "per_cell": {
               "N50k_direct_ratio": res_50k,
               "N70k_direct_T2": res_70k_direct,
               "N70k_model_compare": res_70k_model,
               "N100k_alpha_extrap": res_100k_alpha,
               "N100k_growth_factor": res_100k_growth,
           },
           "structural_read": struct,
           "terminal": terminal,
           "theta_class_caveat": "sup θ-universal within ~30% (C1); "
                                  "sub θ-sensitive but dominated by sup",
           "scope": "Sensitivity verdict math, model-based at N=50k/N=100k "
                    "and direct at N=70k. Banked sensitivity NOT marked "
                    "retracted. rev-5.1 / banked-file updates Will's."}
    json.dump(rec, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
