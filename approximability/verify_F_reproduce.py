"""Checker for the Session F independent replication (2026-09-05).

Pins a SPLIT result: one claim corroborated, one not, and one deliberately left
unresolved. Each pin names the input that flips it red.

  1. GATES-REPLICATE -- Hasse-Weil and RH-for-curves both pass 100% of the
                    smooth battery. These are theorems; a single failure means
                    the point-counter is wrong or a singular curve leaked past
                    the squarefree filter. Both happened during construction:
                    y^2 = x^5+x^3 = x^3(x^2+1) got through because ff_curve's
                    g2_Nv checks only degree and leading coefficient.
  2. BATTERY-REAL -- at least 150 smooth cases. 100% of nothing is not
                    method-invariance, and this is the pin that keeps pin 1
                    from going vacuous.
  3. DISPERSION-STANDS -- the genus-2 rate ratio still has sd >= 0.15 across
                    curves. THIS IS THE FINDING: F_results.json banks that
                    quantity to 17 significant figures with no error bar and no
                    n, while it ranges 0.65 to 1.86 curve to curve. Red if the
                    dispersion collapses, because a point constant would then
                    be defensible and this criticism dissolves.
  4. BANKED-NOT-REPRODUCED -- the worst genus delta is still above 0.05. Red if
                    the banked ratios start reproducing: re-adjudicate rather
                    than quietly enjoying it, because that would mean the
                    estimator or the family changed underneath.
  5. CAVEAT-PRESENT -- the estimator caveat is still recorded. M1's miss must
                    NOT be readable as "genus-independence refuted": the log-
                    slope fit is biased up by near-zero dips, which are more
                    frequent at genus 2, so estimator bias and a real
                    genus effect predict the same sign. Red if the caveat is
                    dropped, which is how an UNRESOLVED becomes a claim.

NOT INERT: pin 1 asserts a fraction is exactly 1 while pin 4 asserts a different
quantity is NOT small, so no degenerate run satisfies both -- an empty battery
fails pin 2, and a battery that reproduced everything fails pin 4 loudly rather
than silently.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "F_reproduce.json")

if not os.path.exists(SRC):
    print("SKIP — F_reproduce.json absent; run F_reproduce.py")
    sys.exit(0)

d = json.load(open(SRC))
n = d["n_cases"]
fail = []

if d["hasse_weil_pass"] != n or d["rh_pass"] != n:
    fail.append(f"pin1 GATES: Hasse-Weil {d['hasse_weil_pass']}/{n}, RH "
                f"{d['rh_pass']}/{n}. These are provable; a failure means the "
                "point-counter is wrong or a singular curve leaked past the "
                "squarefree filter (ff_curve.g2_Nv does not check it)")
if n < 150:
    fail.append(f"pin2 BATTERY-REAL: only {n} smooth cases; 100% of a small "
                "battery is not method-invariance and makes pin 1 vacuous")

g2 = d["dispersion"]["2"]
if g2["sd"] < 0.15:
    fail.append(f"pin3 DISPERSION: genus-2 sd is now {g2['sd']:.3f} < 0.15. The "
                "finding was that a 17-significant-figure banked constant sits "
                "on a quantity with large curve-to-curve spread; if the spread "
                "has collapsed, that criticism no longer holds")
if d["worst_delta"] <= d["tol"]:
    fail.append(f"pin4 BANKED-NOT-REPRODUCED: worst delta {d['worst_delta']:.4f} "
                f"is now within {d['tol']}. The banked ratios reproduce — "
                "re-adjudicate the verdict rather than leaving it at "
                "DO_NOT_REPLICATE")
if not d.get("estimator_caveat"):
    fail.append("pin5 CAVEAT: the estimator caveat is gone. Without it M1's "
                "miss reads as 'genus-independence refuted', which this cell "
                "explicitly cannot support — the log-slope fit is biased up by "
                "near-zero dips and those are more frequent at genus 2")

if fail:
    print("FAIL — Session F replication")
    for f in fail:
        print("  *", f)
    sys.exit(1)

print(f"PASS — Session F replication, {n} smooth cases on an independently "
      "declared family")
print(f"       CORROBORATED: Hasse-Weil {d['hasse_weil_pass']}/{n} and "
      f"RH-for-curves {d['rh_pass']}/{n} — method-invariance holds on curves "
      "Session F never used, which is its load-bearing claim")
print(f"       NOT REPRODUCED: rate ratios {d['rate_ratio_g1']:.4f} / "
      f"{d['rate_ratio_g2']:.4f} against banked {d['banked']['g1']:.4f} / "
      f"{d['banked']['g2']:.4f}")
print(f"       AND UNDER-SPECIFIED: genus-2 spread {g2['minimum']:.3f}"
      f"-{g2['maximum']:.3f}, sd {g2['sd']:.3f}, n={g2['n']} — the banked value "
      "carries 17 significant figures, no error bar and no n")
print("       UNRESOLVED BY DESIGN: genus-dependence, because the estimator's "
      "bias and a real effect share a sign (caveat recorded)")
