"""CERTIFY the D2 COMPUTED-UNUSED detector against its NEAREST CONFUSABLE.

The confusable is not constructed. It is already in the repo, and it is as near as
a negative case can get: the token `p_two` appears at five sites, computed by the
same `_ks_pvalue(ks_two, ...)` idiom every time.

  run_decisive.py:247       if ks_two > 0.10 and p_two < 0.05        -> COMPARED
  run_controls.py:287       if ks_two < 0.10 and p_two > 0.05        -> COMPARED
  run_calibration.py:318    (ks_two > 0.10 and p_two < 0.05)         -> COMPARED
  run_analytical_nns.py:266 print(f"... p={p_two:.4f}")              -> PRINTED ONLY

Same name, same idiom, same computation, one file apart. A detector that fires on
"a p-value exists here" fires on all four; the one that is correct fires on one.
That is what makes this the nearest confusable rather than a far-away negative
with a specificity number and no information.

IT ALSO CARRIES A FINDING. The comparison is present in three siblings and absent
in the fourth: the rejection region was in the ancestor and was SHED BY A COPY.
So the C3 COMPARE-DIRECTIVE (Ruling 3, brief clause 8) is not a policy preference
imposed on the variants -- it restores a comparison the population demonstrably
used to have. Consolidation is the fix for the mechanism that lost it.

The detector under test is the SHIPPED predicate, imported, not a mirror of it.
"""
import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from detector_spec import DetectorSpec                      # noqa: E402
from c3_inline_inventory import computed_unused_names        # noqa: E402  (SHIPPED predicate)

CASES = {
    "p_two@run_analytical_nns": ("run_analytical_nns.py", True),   # printed only -> MUST FIRE
    "p_two@run_controls":       ("run_controls.py", False),        # compared     -> MUST BE SILENT
    "p_two@run_decisive":       ("run_decisive.py", False),        # compared     -> MUST BE SILENT
    "p_two@run_calibration":    ("run_calibration.py", False),     # compared     -> MUST BE SILENT
}

spec = DetectorSpec(
    name="D2 computed-unused (module-wide)",
    fires_on="a quality quantity assigned in scope and never appearing in a Compare",
    positive_set={k: v for k, v in CASES.items() if v[1]},
    negative_set={k: v for k, v in CASES.items() if not v[1]},
    nearest_confusable=(
        "the SAME token `p_two`, produced by the SAME _ks_pvalue idiom, in three "
        "sibling files where it IS compared against 0.05 -- distinguishable from the "
        "positive only by whether a Compare node consumes it, never by name, "
        "provenance, or the presence of a p-value"),
    negative_rationale=(
        "run_decisive:247, run_controls:287 and run_calibration:318 each gate on "
        "p_two against 0.05, so these are genuine rejection regions and firing on "
        "them would be a false positive -- the detector would be reporting the "
        "absence of a comparison that is on the line"),
)

print(f"{'case':30s} {'expect':>7s} {'observed':>9s}  verdict")
tp = fp = tn = fn = 0
for case, (path, must_fire) in CASES.items():
    src = open(os.path.join(ROOT, path), errors="replace").read()
    fired = "p_two" in computed_unused_names(ast.parse(src))
    spec.record(case, fired=fired)
    ok = (fired == must_fire)
    tp += (fired and must_fire); fn += ((not fired) and must_fire)
    fp += (fired and not must_fire); tn += ((not fired) and (not must_fire))
    print(f"{case:30s} {str(must_fire):>7s} {str(fired):>9s}  {'ok' if ok else 'WRONG'}")

spec.certify()

print(f"\nsensitivity {tp}/{tp + fn}    specificity {tn}/{tn + fp}"
      f"    (negatives are the nearest confusable, not far-away cases)")
print("\nD2_CERTIFIED — the detector separates printed-only from compared on the "
      "identical token, so COMPUTED_UNUSED at the newly visible sites is a "
      "measurement and not an artifact of the extractor's reach.")
print("\nFINDING carried by the negative set: three siblings compare p_two, one "
      "prints it. The rejection region was SHED BY A COPY, which is the mechanism "
      "clause 8's COMPARE-DIRECTIVE reverses.")
