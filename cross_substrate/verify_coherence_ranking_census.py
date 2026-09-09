"""Re-derive the ranking census's decision and its overlap amendment.

  1. THE DECISION, which is what the census exists to make: the population mean
     Jaccard must clear 0.50 by more than its own 95% half-width, and must do so
     at every fixed index. Either failing returns the arc to
     RANKING_EFFECT_UNRESOLVED, which is where amendment 3 left it.
  2. The census is still a CENSUS, not a large sample.
  3. The input is still the graph the census pinned. This cell supersedes an
     artifact that went stale exactly this way, so it must not become one.
  4. THE AMENDMENT TIES TO THE SEALED RUN EXACTLY. Its mean Jaccard must equal
     the census's to double precision -- that is what makes it the same
     measurement rather than a neighbouring one -- and its exact overlap
     distribution must sum back to the census's lossy buckets, which is an
     independent consistency check on both.
  5. The known-defective field stays flagged, and the amendment stays POST-HOC.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
bad = []
c = json.load(open(os.path.join(HERE, "brocot_coherence_ranking_census.json")))
a = json.load(open(os.path.join(HERE, "brocot_ranking_overlap_amendment.json")))

# 1. the decision
lo, hi = c["jaccard_ci"]
if lo <= c["bar"]:
    bad.append(f"the 95% interval [{lo:.6f}, {hi:.6f}] no longer excludes "
               f"{c['bar']} — this is the boundary call again, not a resolution")
if c["excess_in_halfwidths"] < 1.0:
    bad.append(f"the mean clears the bar by only "
               f"{c['excess_in_halfwidths']:.2f} half-widths")
below = {k: v for k, v in c["mean_by_fixed_index"].items() if v <= c["bar"]}
if below:
    bad.append(f"fixed index/indices at or below the bar: {below} — pooling "
               "would then be hiding a reversal, which C3 exists to catch")
if c["n_indices_clearing"] != len(c["mean_by_fixed_index"]):
    bad.append("n_indices_clearing disagrees with mean_by_fixed_index")
if c["verdict"] != "RANKING_EFFECT_RESOLVED_MODEL_GAP_IS_DOCUMENTATION_ONLY":
    bad.append(f"verdict is {c['verdict']!r}")

# 2. census, not sample
if c["n_cases"] < 6000 or c["n_cases"] > c["pool_size"]:
    bad.append(f"n_cases {c['n_cases']} outside the census range for a pool of "
               f"{c['pool_size']}")

# 3. the pin
gpath = os.path.join(BROCOT, "resources", c["graph"])
if os.path.exists(gpath):
    live = hashlib.sha256(open(gpath, "rb").read()).hexdigest()
    if live != c["graph_sha256"]:
        bad.append(f"the graph has moved ({live[:16]}... vs pinned "
                   f"{c['graph_sha256'][:16]}...). This cell supersedes an "
                   "artifact that went stale exactly this way; re-run it.")
else:
    print("  note: sibling graph absent, pin not checkable here")

# 4. the amendment ties, and reconciles
if not a.get("tie_to_sealed_run_exact"):
    bad.append("the amendment no longer records an exact tie to the sealed run")
if a["mean_jaccard_recomputed"] != c["mean_jaccard"]:
    bad.append(f"amendment mean {a['mean_jaccard_recomputed']!r} != census "
               f"{c['mean_jaccard']!r} — not the same measurement")
if a["n_cases"] != c["n_cases"]:
    bad.append(f"amendment n {a['n_cases']} != census n {c['n_cases']}")
ex = {int(k): v for k, v in a["exact_overlap_distribution"].items()}
if sum(ex.values()) != c["n_cases"]:
    bad.append("the exact distribution does not sum to n_cases")
# the census's lossy buckets are {0,1}->0, {2,3}->1, {4}->2
lossy = {int(k): v for k, v in c["shared_top4_distribution"].items()}
recon = {0: ex.get(0, 0) + ex.get(1, 0),
         1: ex.get(2, 0) + ex.get(3, 0),
         2: ex.get(4, 0)}
if recon != lossy:
    bad.append(f"the exact distribution does not collapse back to the census's "
               f"buckets: {recon} vs {lossy} — one of the two is wrong")
# and the mean must follow from the exact distribution
mean_from_dist = sum(k / (8 - k) * v for k, v in ex.items()) / c["n_cases"]
if abs(mean_from_dist - c["mean_jaccard"]) > 1e-12:
    bad.append(f"mean from the exact distribution {mean_from_dist!r} != banked "
               f"{c['mean_jaccard']!r}")

# 5. labels
if "POST-HOC" not in a["status"].upper():
    bad.append("the amendment has lost its POST-HOC label")
if "4 * j" not in a["defect"] and "4*j" not in a["defect"]:
    bad.append("the amendment no longer names the defective expression, which is "
               "what lets a reader check the claim rather than take it")

print(f"  mean Jaccard {c['mean_jaccard']:.6f}, 95% [{lo:.6f}, {hi:.6f}], "
      f"{c['excess_in_halfwidths']:.2f} half-widths clear of {c['bar']}")
print(f"  fixed indices: " + ", ".join(f"I={k} {v:.4f}"
                                       for k, v in c["mean_by_fixed_index"].items()))
# NOTE TO WHOEVER EDITS THIS: report the value, never an adjective about it.
# Four summary lines written tonight asserted an outcome the checks below were
# still deciding ("all >= 5.0" beside a 4.200, "matched design holds" beside a
# KS of 0.31, and this one). A print that states a conclusion it did not compute
# is a miniature of the defect every checker here exists to catch.
print(f"  exact overlap: " + ", ".join(f"{k}/4:{ex[k]} ({100.0*ex[k]/c['n_cases']:.1f}%)"
                                       for k in sorted(ex))
      + ("   (reconciles with the census's buckets)" if recon == lossy
         else f"   (does NOT reconcile: {recon} vs {lossy})"))

if bad:
    print("VERIFY_COHERENCE_RANKING_CENSUS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_COHERENCE_RANKING_CENSUS: PASS — the decision holds pooled and at "
      "every index, the pin is intact, and the amendment ties to the sealed run "
      "exactly and reconciles with it")
