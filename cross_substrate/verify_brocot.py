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

NOT INERT: pin 2 asserts an interval CONTAINS zero and pin 3 asserts one does
NOT, so the two cannot both be satisfied by a degenerate result -- a run that
returned all-zero correlations fails pin 3, and one that returned uniformly
strong correlations fails pin 2.
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

if fail:
    print("FAIL — brocot resolution")
    for f in fail:
        print("  *", f)
    sys.exit(1)
print("PASS — brocot: class-level claim retracted (CI contains 0), per-alpha form holds "
      f"(rho={p['corr']['D_Q (small=resonant)']['rho']:+.3f}, n={p['n']}), both confounds ruled out")
