"""Checker for the brocot resolution (2026-08-19). Nonzero exit on any failure.

Pins the claims that a reader would act on, and each pin names the input that
would flip it red:

  1. FAITHFUL     -- the banked representatives still reproduce rho = -0.909.
                     Red if the generator drifts from what was originally run.
  2. FAILS-BY-CLASS -- the class-mean CI against mu still INCLUDES ZERO.
                     Red if someone re-establishes a class-level claim without
                     re-running this, which is the specific overclaim retracted.
  3. HOLDS-PER-ALPHA -- rho(D_Q, q) CI is still clear of zero at n>=250.
                     Red if the corroborated form stops holding.
  4. CONFOUNDS    -- the partial correlation controlling for n, and the
                     unbounded-estimator value, are both still clear of zero.
                     Red if either confound reappears.

  5. SATURATION  -- the attenuation toward the rigid end is SUBSTANTIVE: the
                     slope difference CI still excludes zero. Red if the slope
                     stops moving, which would put the range-restriction
                     (instrumental) reading back on the table.
  6. NOT-ONLY-BETWEEN -- the within-class dose-response is still present where a
                     within-class test is well powered. `generic` carries the
                     widest within-class D_Q range, and its slope must stay near
                     the pooled one. Red if the relation collapses to a purely
                     between-class effect.
  8. DEPTH-INVARIANT -- the saturation still holds at EVERY swept depth. Red if
                     it becomes true only at the depth it was discovered at,
                     which would scope the finding to DEPTH = 8.
  7. UNIFIED     -- class position in D_Q still predicts a class's own slope,
                     AFTER controlling for that class's D_Q spread. Red if the
                     association survives only uncontrolled, which would make it
                     a power artifact.

NOT INERT: pin 2 asserts an interval CONTAINS zero and pin 3 asserts one does
NOT, so the two cannot both be satisfied by a degenerate result -- a run that
returned all-zero correlations fails pin 3, and one that returned uniformly
strong correlations fails pin 2. Pins 5-7 extend that: pin 5 needs a slope
DIFFERENCE clear of zero while pin 6 needs a within-class slope CLOSE to the
pooled one, so a degenerate all-flat population fails 6 and a degenerate
all-identical one fails 5.

EXTENDED 2026-08-23 because the claim outgrew the checker: three artifacts were
banked (attenuation, within/between, slope-by-class) that this file did not
mention, and a checker silent about a claim is not evidence for it.
"""
import json, os, sys

H = os.path.dirname(os.path.abspath(__file__))
fail = []


def need(path):
    if not os.path.exists(path):
        fail.append(f"MISSING ARTIFACT {os.path.basename(path)} -- regenerate with its committed generator")
        return None
    return json.load(open(path))


w = need(f"{H}/brocot_within_class.json")
p = need(f"{H}/brocot_perAlpha.json")
c = need(f"{H}/brocot_perAlpha_confounds.json")
att = need(f"{H}/brocot_attenuation.json")
wb = need(f"{H}/brocot_within_between.json")
sbc = need(f"{H}/brocot_slope_by_class.json")
dep = need(f"{H}/brocot_depth_sweep.json")

if w:
    r = w["rho"]["assumed_rank_0_to_8"]["rho_banked_rep"]
    if abs(r - (-0.909)) > 0.02:
        fail.append(f"pin1 FAITHFUL: banked-rep rho on assumed rank = {r:+.3f}, expected -0.909")
    lo, hi = w["rho"]["irrationality_measure_mu"]["ci95"]
    if not (lo <= 0.0 <= hi):
        fail.append(f"pin2 FAILS-BY-CLASS: class-mean CI vs mu [{lo:+.3f},{hi:+.3f}] no longer "
                    "contains zero -- the retracted class-level claim may be back")
    ratio = w["spread"]["ratio_within_over_between"]
    if ratio < 0.5:
        fail.append(f"pin2b: within/between spread ratio {ratio:.2f} < 0.5; the "
                    "'one representative has no error bar' argument rests on this")

if p:
    d = p["corr"]["D_Q (small=resonant)"]
    if p["n"] < 250:
        fail.append(f"pin3 HOLDS-PER-ALPHA: n = {p['n']} < 250")
    if not (d["ci95"][0] > 0.0):
        fail.append(f"pin3 HOLDS-PER-ALPHA: rho(D_Q,q) CI {d['ci95']} touches zero")
    if d["rho"] < 0.5:
        fail.append(f"pin3: rho(D_Q,q) = {d['rho']:+.3f} < 0.5, below the committed prediction")

if c:
    if c.get("verdict") != "SURVIVES_BOTH":
        fail.append(f"pin4 CONFOUNDS: verdict is {c.get('verdict')}, not SURVIVES_BOTH")
    pr = c["partial_rho_controlling_n"]
    if not (pr[1] > 0.0):
        fail.append(f"pin4a: partial rho controlling n has CI [{pr[1]:+.3f},{pr[2]:+.3f}] touching zero")
    ub = c["C2"]["rho_unbounded"]
    if not (ub[1] > 0.0):
        fail.append(f"pin4b: unbounded-estimator rho CI [{ub[1]:+.3f},{ub[2]:+.3f}] touching zero "
                    "-- the result would then be a Brody-rail artifact")

if att:
    lo, hi = att["slope_diff_ci"]
    if not (hi < 0.0):
        fail.append(f"pin5 SATURATION: slope-difference CI [{lo:+.3f},{hi:+.3f}] no longer "
                    "excludes zero -- the instrumental (range-restriction) reading returns")
    if att["verdict"] != "SUBSTANTIVE":
        fail.append(f"pin5b: attenuation verdict is {att['verdict']}, not SUBSTANTIVE")
    if abs(att["r_pred"] - att["r_obs"]) <= 0.15:
        fail.append("pin5c: observed top-tercile r is now within 0.15 of the "
                    "range-restriction prediction; the drop is explained by X-restriction")

if wb:
    gen = wb["within"].get("generic", {})
    if gen.get("status") != "MEASURED":
        fail.append("pin6 NOT-ONLY-BETWEEN: `generic` is no longer measurable -- it is the "
                    "only class with enough within-class D_Q range to test a dose-response")
    else:
        ratio = gen["slope"] / wb["pooled_slope"]
        if not (0.5 <= ratio <= 2.0):
            fail.append(f"pin6: generic within-class slope {gen['slope']:+.3f} is "
                        f"{ratio:.2f}x the pooled {wb['pooled_slope']:+.3f}; the relation "
                        "no longer reproduces inside the best-powered class")
    if wb["between_share"] > 0.85:
        fail.append(f"pin6b: between-class share {wb['between_share']:.3f} > 0.85 -- the "
                    "relation has become essentially purely between-class")

if sbc:
    if not (sbc["ci_s2"][1] < 0.0):
        fail.append(f"pin7 UNIFIED: partial rho CI {sbc['ci_s2']} no longer excludes zero; "
                    "class position predicts slope only WITHOUT the power control, which "
                    "would make it a power artifact")
    if sbc["verdict"] != "UNIFIED":
        fail.append(f"pin7b: slope-by-class verdict is {sbc['verdict']}, not UNIFIED")

if dep:
    if dep["fails_at"]:
        fail.append(f"pin8 DEPTH-INVARIANT: saturation now fails at depths "
                    f"{dep['fails_at']} -- the finding is scoped to {dep['holds_at']}, "
                    "and BROCOT_SATURATION.md must be narrowed to match")
    if dep["verdict"] != "DEPTH_INVARIANT":
        fail.append(f"pin8b: depth-sweep verdict is {dep['verdict']}, not DEPTH_INVARIANT")
    if len(dep["holds_at"]) < 5:
        fail.append(f"pin8c: only {len(dep['holds_at'])} depths tested clean; the sweep "
                    "must span the knob, not sample it")

if fail:
    print("FAIL — brocot resolution")
    for f in fail:
        print("  *", f)
    sys.exit(1)
print("PASS — brocot: class-level claim retracted (CI contains 0), per-alpha form holds "
      f"(rho={p['corr']['D_Q (small=resonant)']['rho']:+.3f}, n={p['n']}), both confounds ruled out")
print(f"       saturation SUBSTANTIVE (slope diff CI {att['slope_diff_ci'][0]:+.2f}..."
      f"{att['slope_diff_ci'][1]:+.2f}), dose-response survives inside `generic` "
      f"({wb['within']['generic']['slope']:+.2f} vs pooled {wb['pooled_slope']:+.2f}), "
      f"and class position predicts slope after the power control "
      f"(partial rho {sbc['partial_rho_controlling_power']:+.2f})")
print(f"       and it is DEPTH_INVARIANT across {dep['holds_at']} "
      f"(partial count {dep['rows'][0]['median_partials']}..{dep['rows'][-1]['median_partials']})")
