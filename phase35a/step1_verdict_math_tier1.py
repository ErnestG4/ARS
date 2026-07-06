"""
phase35a/step1_verdict_math_tier1.py — Step-1 verdict math, Tier 1
(Will's explicit authorization 2026-05-20 post slate-3 chain). The
first time across this entire arc that Step-1 verdict math is run;
all prior runs surfaced magnitudes without combining them with the
criterion. Will set the protocol; this implements it.

PROTOCOL (Will's exact words, 2026-05-20).
"Substitute the L-converged sup substrate value (0.382 at N=70k from
Test 2) for Step-1's stored sup_spread@N=70k = 0.0766, and re-run
transition_diagnostic on the no-false-positive verdict at N=70k. If
the verdict survives substitution robustly, the load-bearing case is
cleared and the math at other cells follows the same template. If it
flips, Step-1's no-false-positive at N=70k is retracted and you have
a structural finding to handle."

The "no-false-positive verdict" here = the spread-based criterion
sensitivity_confirm encoded as the validated-non-circular floor:
  PASS iff disjoint AND gap >= max(sub_spread, sup_spread)
where the inputs are stored in `sensitivity_confirm_results.json`.

INPUTS (cited).
- sensitivity_confirm @N=70k:
    sub_spread = 2.7e-05 ; sup_spread = 0.07656 ; gap = 0.177402 ;
    disjoint = True ; stored verdict: PASS (sensitivity validated).
- Test 2 (b0haqgof3 → bo73me0uq) L-converged substrate sup_spread
  at N=70k, δ=0.5, λ=1.5 at L=2.56e7: 0.382 (top_inc 0.95%, converged
  within 5%; apparatus identity bit-deterministic vs b0haqgof3).

SUBSTITUTION (minimal, per Will's exact words).
  sup_spread: 0.07656 → 0.382 (substrate)
  sub_spread: unchanged (2.7e-05; substrate-corrected value not
    directly measured at L-convergence; bh22pfzoa N=70k δ=0.5 L=1.6e6
    mean=0.0107 with α≈1.25 — substrate sub_spread is small, ≲ stored;
    insensitive in the max() because sup dominates by 4+ orders
    of magnitude either way)
  gap: unchanged (0.177402, the stored L=1e5 measurement)
  disjoint: unchanged (True; substrate sub ensemble at ~0.001 vs
    substrate sup ensemble at ~[0.25, 0.64] would still be disjoint
    structurally — verified below as a side check)

RESULT (computed below): the criterion test gap >= max(sub, sup)
under the substitution.

CONFIRMATORY SIDE CHECK (full substrate, beyond Will's minimal
substitution).
  substrate gap = min(test2 sup ensemble at L=2.56e7) − (sub_substrate_max)
  substrate sub_max is extrapolated from bh22pfzoa (α≈1.25 decay) to
  L_top; treated as a coarse upper bound ≤ 0.01.
  Both minimal and full-substrate computations land the same verdict;
  the result is robust to sub-side uncertainty (sup dominates).

θ-CLASS CAVEATS (per Will, C1 result):
  - Sup contamination is θ-class-universal within ~30% (silver/golden
    ratio 1.29) — this verdict at golden θ transfers to other
    Diophantine classes within ~30%.
  - Sub-side is θ-class-sensitive (silver/golden ratio 3.55). Sub
    claims don't transfer as cleanly. But: this verdict-flip is
    dominated by sup_spread (max() of {sub, sup}); the sub-side
    θ-sensitivity does NOT affect the result. NOTED, not gating.

SCOPE. Tier 1 at the load-bearing N=70k cell only. N=50k and N=100k
cells follow the same template per Will, but their substrate
sup_spread values are NOT directly measured (Tier 2 territory) — this
script reports their stored Step-1 verdicts unchanged and does NOT
attempt verdict math at those cells without measured inputs. Step-1
adjudication / N-propagation / what to do next remains Will's call;
this script computes the math, surfaces the result, does not decide.
"""
from __future__ import annotations
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
SENS = os.path.join(HERE, "sensitivity_confirm_results.json")
T2 = os.path.join(HERE, "test2_sup_L_extend_results.json")
BH22_RAW = os.path.join(HERE, "sub_Liter_convergence_rawtable.json")
OUT = os.path.join(HERE, "step1_verdict_math_tier1_results.json")


def main():
    sens = json.load(open(SENS))
    t2 = json.load(open(T2))

    print("=" * 86)
    print("Step-1 VERDICT MATH — Tier 1 (Will's authorization 2026-05-20)")
    print("=" * 86)

    # ── Inputs at N=70k ─────────────────────────────────────────────
    row70k = next(r for r in sens["per_N"] if r["N"] == 70000)
    stored = {
        "N": 70000,
        "sub_spread": float(row70k["sub_spread"]),
        "sup_spread": float(row70k["sup_spread"]),
        "gap": float(row70k["gap"]),
        "disjoint": bool(row70k["disjoint"]),
        "stored_verdict_PASS": bool(row70k["PASS"]),
    }
    # Substrate sup_spread from Test 2 (L=2.56e7 row)
    sup_substrate_spread = float(t2["spreads_by_L"][str(t2["L_top"])])
    sup_substrate_mean = float(t2["means_by_L"][str(t2["L_top"])])
    # Side-check: substrate sup ensemble min (from Test 2 per-φ values)
    sup_phi_top = [float(x) for x in t2["phi_per_L"][str(t2["L_top"])]]
    sup_substrate_min = min(sup_phi_top); sup_substrate_max = max(sup_phi_top)
    # Side-check: substrate sub upper bound at N=70k from bh22pfzoa raw
    # (L=1.6e6 ensemble max, used as a coarse upper bound; substrate is
    # smaller since the trajectory is still decaying with α≈1.25)
    bh22 = json.load(open(BH22_RAW))
    sub_phi_70k_1p6e6 = [w for d, N, L, ph, w in bh22["recs"]
                          if abs(d - 0.5) < 1e-9 and int(N) == 70000
                          and int(L) == 1600000]
    sub_upper_bound = max(sub_phi_70k_1p6e6) if sub_phi_70k_1p6e6 else None

    print(f"\nINPUTS @N=70k:")
    print(f"  Step-1 stored (sensitivity_confirm):")
    print(f"    sub_spread = {stored['sub_spread']:.6g}")
    print(f"    sup_spread = {stored['sup_spread']:.6g}")
    print(f"    gap        = {stored['gap']:.6g}")
    print(f"    disjoint   = {stored['disjoint']}")
    print(f"    stored verdict = "
          f"{'PASS' if stored['stored_verdict_PASS'] else 'FAIL'}")
    print(f"  L-converged substrate (Test 2 @L=2.56e7):")
    print(f"    sup_substrate_spread = {sup_substrate_spread:.6g}")
    print(f"    sup_substrate_mean   = {sup_substrate_mean:.6g}")
    print(f"    sup_substrate range  = [{sup_substrate_min:.6g}, "
          f"{sup_substrate_max:.6g}]")
    print(f"  Substrate sub upper bound (bh22pfzoa @L=1.6e6, "
          f"still decaying ⇒ true substrate ≤ this):")
    print(f"    sub_upper_bound = {sub_upper_bound:.6g}")

    # ── MINIMAL SUBSTITUTION (Will's exact words) ─────────────────
    sub_sub = stored["sub_spread"]       # unchanged
    sup_sub = sup_substrate_spread        # substituted
    gap_sub = stored["gap"]               # unchanged
    max_spread_sub = max(sub_sub, sup_sub)
    crit_min = bool(stored["disjoint"] and gap_sub >= max_spread_sub)
    print(f"\nMINIMAL SUBSTITUTION (Will's exact instruction):")
    print(f"  inputs: gap={gap_sub:.6g}  sub_spread={sub_sub:.6g}  "
          f"sup_spread={sup_sub:.6g}  (sup substituted)")
    print(f"  max(sub_spread, sup_spread) = {max_spread_sub:.6g}")
    print(f"  criterion (disjoint AND gap >= max(spread)): "
          f"{stored['disjoint']} AND {gap_sub:.6g} >= "
          f"{max_spread_sub:.6g} = {gap_sub >= max_spread_sub}")
    print(f"  → verdict under minimal substitution: "
          f"{'PASS' if crit_min else 'FAIL'}")

    # ── CONFIRMATORY SIDE CHECK (full substrate) ──────────────────
    substrate_gap = sup_substrate_min - (sub_upper_bound or 0.0)
    crit_full = bool(substrate_gap > 0 and substrate_gap >= max_spread_sub)
    print(f"\nFULL SUBSTRATE CONFIRMATORY (beyond Will's minimal):")
    print(f"  substrate gap = sup_substrate_min({sup_substrate_min:.6g}) "
          f"− sub_upper_bound({sub_upper_bound:.6g}) = {substrate_gap:.6g}")
    print(f"  max(sub, sup)_substrate = {max_spread_sub:.6g}")
    print(f"  criterion: {substrate_gap > 0} AND "
          f"{substrate_gap:.6g} >= {max_spread_sub:.6g} = "
          f"{substrate_gap >= max_spread_sub}")
    print(f"  → verdict under full substrate: "
          f"{'PASS' if crit_full else 'FAIL'}")

    # ── θ-class transfer caveat ───────────────────────────────────
    print(f"\nθ-CLASS TRANSFER CAVEAT (C1):")
    print(f"  sup contamination θ-class-universal within ~30% (silver/")
    print(f"    golden ratio 1.29) ⇒ this verdict at golden θ transfers")
    print(f"    to other Diophantine classes within ~30%.")
    print(f"  sub-side approximant-pattern-sensitive (3.55×) BUT does not")
    print(f"    affect this verdict (max() is dominated by sup; sup_sub")
    print(f"    is 0.382 vs sub at ~1e-5 to 1e-2 — max is sup either way).")

    # ── Outcome ───────────────────────────────────────────────────
    print(f"\n" + "=" * 86)
    if crit_min:
        outcome = "STEP1_N70K_VERDICT_SURVIVES_SUBSTITUTION"
        msg = ("Sensitivity criterion at N=70k survives substrate "
               "sup_spread substitution. Load-bearing case CLEARED. "
               "Math at other cells follows same template (Will).")
    else:
        outcome = "STEP1_N70K_VERDICT_FLIPS_RETRACTED"
        msg = ("Sensitivity criterion at N=70k FAILS under substrate "
               "sup_spread substitution. **Step-1 no-false-positive at "
               "N=70k is RETRACTED** (per Will's pre-registered framing). "
               "Structural finding to handle.")
    print(f"OUTCOME: {outcome}")
    print(f"  {msg}")
    print("=" * 86)

    # ── Other-N cells: NOT computed (Tier 2 territory) ─────────────
    print(f"\nOTHER CELLS (Tier 2 territory — substrate values NOT measured):")
    for r in sens["per_N"]:
        if r["N"] == 70000: continue
        print(f"  N={r['N']:6d}: stored sub_spread={r['sub_spread']:.6g} "
              f"sup_spread={r['sup_spread']:.6g} gap={r['gap']:.6g} "
              f"stored PASS={r['PASS']}.")
    print("  → Will: 'If Tier 1 at N=70k is decisive, that's enough. If you")
    print("     need substrate values at other cells, Tier 2 = direct L-conv")
    print("     runs at those cells OR N-scaling extrapolation.'")

    rec = {"protocol": "Will's exact words (2026-05-20)",
           "stored_at_N70k": stored,
           "L_converged_substrate": {
               "L_top": t2["L_top"],
               "sup_spread": sup_substrate_spread,
               "sup_mean": sup_substrate_mean,
               "sup_ensemble_min": sup_substrate_min,
               "sup_ensemble_max": sup_substrate_max,
               "sub_upper_bound_from_bh22_L1p6e6":
                   sub_upper_bound},
           "minimal_substitution": {
               "sub_spread": sub_sub, "sup_spread": sup_sub,
               "gap": gap_sub, "max_spread": max_spread_sub,
               "criterion_PASS": bool(crit_min)},
           "full_substrate_confirmatory": {
               "substrate_gap": substrate_gap,
               "max_spread_substrate": max_spread_sub,
               "criterion_PASS": bool(crit_full)},
           "theta_class_caveats": {
               "sup_universal_within_30pct": True,
               "sub_theta_sensitive_3p55x": True,
               "affects_this_verdict": False,
               "reason": "max() dominated by sup; sub θ-sensitivity does "
                         "not flip the maximum."},
           "outcome": outcome,
           "other_N_status": "NOT computed at other N (Tier 2 substrate "
                              "values not measured; Will: decisive at N=70k "
                              "is enough or Tier 2 follows)",
           "scope": "Tier 1 verdict math at the load-bearing N=70k cell. "
                    "Computes; surfaces; does NOT decide Step-1 propagation "
                    "or recovery direction — that is Will's."}
    json.dump(rec, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
