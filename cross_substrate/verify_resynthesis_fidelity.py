"""Checker for the resynthesis apparatus (2026-09-04). Nonzero exit on failure.

Pins what a reader would act on. Each pin names the input that flips it red:

  1. FIDELITY-DISCRIMINATES -- the additive render still matches the FM render
                     within 0.10 of the contrast, AND the deliberately truncated
                     B=2 rival still FAILS that same bar. Red either way: if the
                     apparatus drifts, or if the rival starts passing, in which
                     case the bar separates nothing and the arm is inert.
  2. CONTROLS-BOTH-WAYS -- the modulation readout's positive control (FM twin
                     shows the beat) and negative control (additive EXACT does
                     not, its pair being merged) both hold on every ratio. Red
                     if either fails: a readout that fires on the merged
                     stimulus is measuring something other than the beat.
  3. TWIN-CARRIES  -- the additive twin still carries the cue at all but one
                     ratio. Red if carriage drops: the apparatus can be
                     perfectly faithful and still useless, and this is the pin
                     that separates those.
  4. SCOPE-NAMED   -- 5/7 is still the named exception rather than a silent
                     average. Red if it starts passing (re-scope, do not just
                     enjoy it) or if a SECOND ratio fails (the exclusion is then
                     not one odd case but a pattern needing its own account).
  5. ERB-IS-BLIND  -- the phase sweep still moves the ERB contrast by
                     essentially nothing. This pin asserts a NULL on purpose:
                     it is the standing evidence that the static metric cannot
                     see the manipulation, which is WHY the modulation readout
                     exists. Red if phase starts mattering on the ERB metric --
                     that would mean the kernel changed and pins 2-4 need
                     re-deriving, not celebrating.
  6. TRUNCATION    -- the residual is still monotone in the box size B. Red if
                     not, because then pin 1's pass is for some reason other
                     than the truncation it claims to measure.

NOT INERT: pin 1 requires a value BELOW a bar while requiring the rival ABOVE it,
so neither a degenerate all-zero run nor a degenerate all-large one satisfies it.
Pin 2 requires one control to fire and the other NOT to, so an instrument stuck
high fails the negative and one stuck low fails the positive. Pin 5 asserts a
null that pin 3 needs to be true for the cell to make sense at all.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "brocot_resynthesis_fidelity.json")

if not os.path.exists(SRC):
    print(f"SKIP — {os.path.basename(SRC)} absent; run "
          "brocot_resynthesis_fidelity.py")
    sys.exit(0)

d = json.load(open(SRC))
rows, am = d["rows"], d["amendment1"]
n = len(rows)
fail = []

if d["median_fidelity_ratio"] > d["fidelity_ratio_bar"]:
    fail.append(f"pin1 FIDELITY: median error {d['median_fidelity_ratio']:.4f} "
                f"exceeds {d['fidelity_ratio_bar']} of the contrast — the "
                "additive render is no longer the FM render, and every "
                "downstream stimulus is a stimulus about the model")
if d["median_rival_ratio"] <= d["fidelity_ratio_bar"]:
    fail.append(f"pin1b RIVAL: the B={d['rival_B']} truncation now also clears "
                f"the bar at {d['median_rival_ratio']:.4f}. A bar a knowingly "
                "bad apparatus passes is evidence for neither")

if am["positive_control"] != n:
    fail.append(f"pin2 POSITIVE CONTROL: FM twin shows the beat on only "
                f"{am['positive_control']}/{n} — the modulation readout cannot "
                "detect a beat known to be present")
if am["negative_control"] != n:
    fail.append(f"pin2b NEGATIVE CONTROL: the additive EXACT stimulus shows a "
                f"beat on {n - am['negative_control']} ratio(s). Its witness "
                "pair is MERGED, so a beat there means the readout is firing "
                "on something that is not the witness beat")

if am["twin_carries_cue"] < n - 1:
    fail.append(f"pin3 TWIN-CARRIES: only {am['twin_carries_cue']}/{n} additive "
                "twins carry the cue. A faithful apparatus that does not carry "
                "the cue is a faithful apparatus that does nothing")

miss = [r["ratio"] for r in rows if r["snr_add_twin"] < am["snr_db"]]
if miss != ["5/7"]:
    fail.append(f"pin4 SCOPE: the non-carrying set is {miss}, not ['5/7']. If "
                "5/7 now passes, re-scope the claim deliberately; if another "
                "ratio has joined it, the exclusion is a pattern and needs its "
                "own account rather than a named exception")

if d["phase_sweep"]["swing"] > 0.05:
    fail.append(f"pin5 ERB-IS-BLIND: phase now moves the ERB contrast by "
                f"{d['phase_sweep']['swing']:.4f}. That null is the standing "
                "evidence that the static metric cannot see a 2 Hz shift; if it "
                "has changed, the kernel changed and the modulation readout's "
                "necessity must be re-derived")

nonmono = [r["ratio"] for r in rows
           if not all(r["b_sweep"][str(a)] >= r["b_sweep"][str(b)] - 1e-12
                      for a, b in zip(d["b_sweep"], d["b_sweep"][1:]))]
if nonmono:
    fail.append(f"pin6 TRUNCATION: error is not monotone in B at {nonmono}; "
                "pin 1 then passes for a reason other than truncation")

if fail:
    print("FAIL — resynthesis apparatus")
    for f in fail:
        print("  *", f)
    sys.exit(1)

print(f"PASS — resynthesis apparatus, {n} ratios at I={d['I']}")
print(f"       FAITHFUL: median error {d['median_fidelity_ratio']:.4f} of the "
      f"contrast vs a {d['fidelity_ratio_bar']} bar, B={d['rival_B']} rival "
      f"fails it at {d['median_rival_ratio']:.2f} — the arm discriminates")
print(f"       CARRIES THE CUE: {am['twin_carries_cue']}/{n}, positive control "
      f"{am['positive_control']}/{n}, negative control {am['negative_control']}/{n}")
print(f"       SCOPED: 5/7 excluded by name — its witness pair is sub-audible, "
      "and its FM twin's apparent cue was mostly collateral")
print(f"       ERB phase-swing {d['phase_sweep']['swing']:.4f}: the static "
      "metric remains blind to the manipulation, which is why the modulation "
      "readout exists")
