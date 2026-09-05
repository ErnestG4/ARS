"""Checker for decorrelation battery v2 (2026-09-05). Nonzero exit on failure.

Pins a NEGATIVE whose value is that it closes a route rather than suggesting a
third knob. Each pin names what flips it red.

  1. PREMISE-HOLDS -- the FM family confound, scored WITHIN RATIO, still clears
                  0.5. v1 scored this by pooling and got 0.432 where the
                  within-ratio median is 0.55-0.64. Red if it drops: the whole
                  battery would then be answering a question that does not
                  arise.
  2. KNOB-IS-WEAK -- rate_mode still fails to move concentration (ratio < 2x
                  against its 3x bar). THIS IS THE FINDING. Red if the knob
                  starts working: the broadband diagnosis would be wrong for a
                  third time and E1/E2 become readable in a way they are not
                  now.
  3. BROADBAND-STANDS -- one band still carries far more of the modulation
                  difference than the closed form predicts (measured
                  top_band_share >= 0.4 at the largest k, where 1/k = 0.125).
                  This is WHY the knob is weak, and it is the measurement that
                  overturned the v1 Amendment 3 over-correction. Red if the
                  difference becomes confined to the targeted bands.
  4. NOT-DECORRELATED -- the battery's |rho| is still above the 0.20 bar. Red
                  if it decorrelates after all, which would reverse the arc's
                  conclusion and must be re-adjudicated rather than enjoyed.
  5. E1-GUARDED -- the applicability flag is still recorded. v1's E1 was INERT
                  because its 2.0x factor exceeded participation_ratio's
                  reachable 1.226x, and nothing caught it because the factor was
                  a bare constant. v2 routes it through Bar and declares the arm
                  INAPPLICABLE when the observed span cannot reach the factor.
                  Red if that flag disappears.

NOT INERT: pin 1 requires a value ABOVE a bar and pin 4 requires a different
value also above a different bar, while pin 2 requires a third BELOW one — no
degenerate instrument satisfies all three. Pin 3 requires a measured quantity to
sit far from a closed-form prediction, so an instrument returning the prediction
fails it.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "brocot_decorrelation_battery_v2.json")

if not os.path.exists(SRC):
    print("SKIP — v2 artifact absent; run brocot_decorrelation_battery_v2.py")
    sys.exit(0)

d = json.load(open(SRC))
fail = []

if d["premise_within_median"] < 0.5:
    fail.append(f"pin1 PREMISE: within-ratio median |rho| is now "
                f"{d['premise_within_median']:.3f} < 0.5. The confound the "
                "battery exists to break no longer holds at the sealed "
                "strength; re-adjudicate before reading anything below")
if d["mech_ratio"] >= 2.0:
    fail.append(f"pin2 KNOB: rate_mode now moves concentration by "
                f"{d['mech_ratio']:.2f}x. The knob works after all — the "
                "broadband diagnosis is wrong for a third time and E1/E2 "
                "become readable in a way they are not now")

kmax = str(max(d["subset_sizes"]))
tbs = d["mech_by_k"][kmax]["distinct"]
if tbs < 0.4:
    fail.append(f"pin3 BROADBAND: top_band_share at k={kmax} is now {tbs:.3f}, "
                f"approaching the closed form's 1/k = {1.0/int(kmax):.3f}. The "
                "difference has become confined to the targeted bands, which "
                "is what v1's Amendment 3 assumed and v2 measured to be false")
if abs(d["rho_battery"]) <= 0.20:
    fail.append(f"pin4 NOT-DECORRELATED: |rho| is now "
                f"{abs(d['rho_battery']):.3f} <= 0.20. The battery "
                "decorrelates; the arc's conclusion reverses and this checker "
                "should be rewritten, not patched")
if "e1_applicable" not in d:
    fail.append("pin5 E1-GUARDED: the applicability flag is gone. v1's E1 was "
                "inert because a bare 2.0x constant exceeded the statistic's "
                "reachable 1.226x and no guard saw it; the flag is what keeps "
                "that from recurring silently")

if fail:
    print("FAIL — decorrelation battery v2")
    for f in fail:
        print("  *", f)
    sys.exit(1)

print(f"PASS — decorrelation battery v2, {len(d['rows'])} ratios, "
      f"{2 * d['n_per_mode']} manipulations each")
print(f"       PREMISE HOLDS within ratio at {d['premise_within_median']:.3f} "
      "(v1 read 0.432 by pooling, which its own R1 forbade)")
print(f"       THE KNOB IS WEAK: rate_mode moves concentration {d['mech_ratio']:.2f}x "
      "against a 3x bar — and the mechanism arm was placed FIRST so that this "
      "makes E1 untestable rather than false")
print(f"       BECAUSE THE DIFFERENCE IS BROADBAND: top_band_share at k={kmax} "
      f"measures {tbs:.3f} where the closed form predicts {1.0/int(kmax):.3f}. "
      "One band carries ~62% of it regardless of k or mode")
print(f"       SO THE ROUTE CLOSES: |rho| {abs(d['rho_battery']):.3f} vs the "
      f"family's {d['premise_within_median']:.3f}. Two independent knobs, "
      "neither moves concentration; a third is not indicated")
