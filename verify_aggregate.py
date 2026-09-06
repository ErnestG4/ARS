"""Board row for aggregate.py: does the construction-time rule actually refuse?

A guard is worth what it REFUSES, so each check below constructs the defect and
requires the raise. If any of these stops raising, an aggregate can be banked
without its spread again and the Session F failure is reachable.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aggregate import banked, extremum, AggregateWithoutSpread   # noqa: E402

CHECKS = []


def refuses(label, fn, why):
    try:
        fn()
    except AggregateWithoutSpread:
        CHECKS.append((label, True, ""))
    except Exception as e:                                        # noqa: BLE001
        CHECKS.append((label, False, f"raised {type(e).__name__}, not "
                                     f"AggregateWithoutSpread: {e}"))
    else:
        CHECKS.append((label, False, why))


def accepts(label, fn, check=lambda r: True, why=""):
    try:
        r = fn()
    except Exception as e:                                        # noqa: BLE001
        CHECKS.append((label, False, f"refused a legitimate call: {e}"))
    else:
        CHECKS.append((label, bool(check(r)), why))


refuses("a collapsed scalar is refused",
        lambda: banked("genus2_rate_ratio", 0.9583126741064829),
        "banked() accepted a bare float — the Session F defect is reachable again")
refuses("n < 2 is refused",
        lambda: banked("some_mean", [1.0]),
        "an aggregate over one observation was banked as a constant")
refuses("an extremum-named aggregate is refused",
        lambda: banked("worst_misclass_rate", [0.1, 0.2, 0.3]),
        "an extremum was banked as a central tendency, which is the false "
        "positive the census produced 4/4")
refuses("extremum() without `over=` is refused",
        lambda: extremum("best_rho", [0.1, 0.5, 0.7]),
        "a selected maximum was banked without the population it was selected "
        "from — the defect the swing rule was minted for")

accepts("a real sample banks with n, sd, sem and range",
        lambda: banked("rate_ratio", [1.0, 1.2, 0.8, 1.1]),
        lambda r: (r["n"] == 4 and r["sd"] is not None and r["sem"] is not None
                   and r["minimum"] == 0.8 and r["maximum"] == 1.2),
        "a legitimate aggregate did not come back with its dispersion")
accepts("median is available and is not the mean",
        lambda: banked("m", [1.0, 1.0, 10.0], kind="median"),
        lambda r: r["value"] == 1.0, "median returned the wrong value")
accepts("an acknowledged extremum name is allowed through",
        lambda: banked("worst_case_mean", [1.0, 2.0],
                       acknowledge="this really is a central tendency"),
        lambda r: r["acknowledged"] is not None,
        "the acknowledge escape hatch does not work")
accepts("extremum() records the population",
        lambda: extremum("best_rho", [0.1, 0.5, 0.7], over="9 configurations"),
        lambda r: (r["n_candidates"] == 3 and r["over"] and
                   r["selection_margin"] > 0),
        "extremum() lost the selection context")

# Session F's own numbers, banked the way the rule demands.
demo = banked("genus2_rate_ratio",
              [1.05, 0.98, 1.30, 1.86, 0.65, 1.12, 1.21, 0.94, 1.44, 1.02])
print("aggregate.py — construction-time rule\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")
print(f"\n  what Session F's constant looks like under the rule:")
print(f"    value {demo['value']:.4f}  n {demo['n']}  sd {demo['sd']:.3f}  "
      f"sem {demo['sem']:.3f}  range {demo['minimum']:.2f}-{demo['maximum']:.2f}")
print("    — a reader can now tell it is a mean over a wide distribution, "
      "which\n      seventeen significant figures on their own actively hid.")
if bad:
    print("\nVERIFY_AGGREGATE: FAIL")
    sys.exit(1)
print("\nVERIFY_AGGREGATE: PASS — every defect the two failed sweeps chased is "
      "refused at construction, and legitimate aggregates pass through with "
      "their dispersion attached.")
