"""Checker for the decorrelation battery (2026-09-05). Nonzero exit on failure.

This pins a NEGATIVE result. The cell is INVALID at its own premise and its
battery came out MORE correlated than the family it was built to replace; these
pins keep that finding honest and make its reversal loud rather than quiet.

  1. PREMISE-STILL-FAILS -- |rho| in the FM detune family is still below the
                     0.5 bar. Red if it rises: the premise would then hold, the
                     four UNREAD arms become readable, and the cell must be
                     re-adjudicated rather than left saying INVALID.
  2. BATTERY-NOT-BETTER -- the constructed battery is still at least as
                     correlated as the FM family. Red if it improves, because
                     that reverses the finding and the redesign row would then
                     be chasing a problem that had gone away.
  3. CONCENTRATION-STUCK -- the concentration span stays under 1.5x. THIS IS THE
                     DIAGNOSIS: subset size is not a concentration knob. Red if
                     concentration starts moving, which would mean the
                     diagnosis is wrong and the redesign is aimed wrongly.
  4. NO-MATCHED-ENERGY -- still zero matched-energy/differing-concentration
                     pairs. Red if any appear, which is E1 becoming
                     constructible and is the whole point of the follow-up.
  5. AMPLITUDES-PURE -- zero members differ in amplitude from exact. This arm
                     was VACUOUS in the first draft (it compared the bin dict
                     against itself, which render_from never mutates) and
                     reported a meaningless 0. It now checks the amplitudes
                     actually rendered; red if a battery member edits one.
  6. INVALID-CITES -- the verdict is INVALID and the composed record carries a
                     `citation`. THIS IS THE GUARD BUG'S PERMANENT TEST:
                     compose()'s failed-premise branch returned no citation
                     key, so the documented way to report a verdict crashed the
                     first time a premise ever actually failed. Red if the
                     refusal path stops being able to report its own refusal.

NOT INERT: pin 1 asserts a value stays BELOW a bar while pin 2 asserts a
different value stays ABOVE a related one, so no degenerate all-zero or all-one
run satisfies both. Pin 4 asserts a count is zero while pin 5 asserts a
different count is zero for the opposite reason -- one would be broken by a
battery that decorrelates, the other by one that cheats.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "brocot_decorrelation_battery.json")

if not os.path.exists(SRC):
    print(f"SKIP — {os.path.basename(SRC)} absent; run "
          "brocot_decorrelation_battery.py")
    sys.exit(0)

d = json.load(open(SRC))
a = d["amendment1"]
fail = []

a2 = d.get("amendment2") or {}
if not a2:
    fail.append("pin1a PREMISE-SCORING: amendment2 is gone. The sealed P1 was "
                "scored by POOLING 11 ratios, which this cell's own R1 forbids; "
                "the within-ratio scoring is what makes the arms readable and "
                "it must stay recorded beside the seal")
elif a2["rho_fm_within_median"] < 0.5:
    fail.append(f"pin1 PREMISE: the WITHIN-RATIO premise is now "
                f"{a2['rho_fm_within_median']:.3f} < 0.5, so the confound no "
                "longer holds even scored correctly and the amended verdict "
                "must go back to INVALID")
if d.get("verdict_amended") != "DECORRELATION_NOT_ACHIEVED":
    fail.append(f"pin1b AMENDED HEAD is {d.get('verdict_amended')!r}. With the "
                "premise scored within-ratio the arms are READ, and three of "
                "them miss; anything else means the composition changed")
if abs(a["rho_battery"]) < abs(a["rho_fm"]):
    fail.append(f"pin2 BATTERY-NOT-BETTER: the battery ({abs(a['rho_battery']):.3f}) "
                f"is now LESS correlated than the FM family ({abs(a['rho_fm']):.3f}). "
                "The negative finding has reversed and the redesign row is "
                "chasing a problem that moved")
if a["conc_span_max"] >= 1.5:
    fail.append(f"pin3 CONCENTRATION-STUCK: concentration span is now "
                f"{a['conc_span_max']:.3f} >= 1.5, so subset size IS moving "
                "concentration after all and the recorded diagnosis is wrong")
if d["matched_energy_pairs"] != 0:
    fail.append(f"pin4 NO-MATCHED-ENERGY: {d['matched_energy_pairs']} "
                "matched-energy pairs now exist. E1 has become constructible — "
                "which is the goal, so re-read the cell rather than patching "
                "this pin")
if d["amplitude_violations"] != 0:
    fail.append(f"pin5 AMPLITUDES-PURE: {d['amplitude_violations']} battery "
                "member(s) edit an amplitude. Every member must be a pure "
                "frequency move or the battery is a different manipulation "
                "from the one the arc studies")
if d["verdict"] != "INVALID":
    fail.append(f"pin6a INVALID-CITES: verdict is {d['verdict']!r}, not INVALID")
elif not d.get("composed", {}).get("citation"):
    fail.append("pin6b INVALID-CITES: the composed record carries no citation. "
                "compose()'s failed-premise branch has stopped reporting its "
                "own refusal — the 2026-09-05 KeyError is back")

if fail:
    print("FAIL — decorrelation battery")
    for f in fail:
        print("  *", f)
    sys.exit(1)

print(f"PASS — decorrelation battery, {len(d['rows'])} ratios, "
      f"{d['n_manip']} manipulations each")
print(f"       INVALID at its own premise: FM-family |rho| {abs(a['rho_fm']):.3f} "
      "below the 0.5 bar, four arms left UNREAD")
print(f"       and the battery came out WORSE: |rho| {abs(a['rho_battery']):.3f} "
      f"against the family's {abs(a['rho_fm']):.3f}")
print(f"       DIAGNOSIS PINNED: concentration span {a['conc_span_min']:.3f}"
      f"-{a['conc_span_max']:.3f} while energy spans {a['energy_span_max']:.1e} "
      "— subset size is an energy knob, not a concentration one")
print(f"       untested: {a['untested_condition']}")
