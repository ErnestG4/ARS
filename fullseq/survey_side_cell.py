"""Survey-dialect kill criterion — the sealed side cell.  COMMITTED
GENERATOR of fullseq/survey_side_cell.json.

Option A was not chosen as the arc, but its answer is cheap and bankable and
belongs on the board regardless of where Option B went: *is anything
currently banked in the survey dialect at risk from reordering?*

Method: bound the full-sequence effect by the SUM of the banked pairwise
commutators in that dialect (C4 window<->project, P3 weight<->thin), and
compare it to the smallest margin any banked survey row has to its own gate
boundary.

TRANSFER LABEL, stated because it is the one inference here that crosses
dialects: using the pairwise sum as an UPPER bound relies on composition
being sub-additive, which this arc measured in the 1-D dialect
(H > 0 at every multi-inversion ordering) and did NOT measure in the survey
dialect. Two independent reasons the conclusion survives that transfer:
(1) the margin exceeds the bound by 17x (MEASURED — an earlier draft of
    this docstring said "~2 orders of magnitude" before the number existed;
    corrected here rather than left to flatter the conclusion). 17x is
    comfortable but not unassailable: composition would have to be
    super-additive by more than 17x in this dialect to close it, which is
    large but not absurd, so this is a bound with a stated size and not a
    dismissal;
(2) the survey estimators are ratio-form and their pairwise effects were
    each measured SUPPRESSED to within noise of zero, so the sum is already
    a sum of near-zeros rather than a sum of real effects.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
K = 3.0


def main():
    c4 = json.load(open(f"{ROOT}/holonomy/c4_measured.json"))
    p3 = json.load(open(f"{ROOT}/holonomy/p3_measured.json"))
    d3 = json.load(open(f"{ROOT}/survey/d3_measured.json"))
    z_class = json.load(open(f"{ROOT}/survey/prereg_sealed.json"))["lattice"]["Z_CLASS"]

    # pairwise bounds in F units: |mean| + k*sem, worst over dials / scales
    c4_bound = max(abs(v["mean"]) + K * v["sem"]
                   for v in c4["statistic"].values())
    p3_bound = max(abs(v["mean"]) + K * v["sem"] for v in p3["cells"].values())
    pair_sum = c4_bound + p3_bound

    # smallest banked margin, in F units
    margins, sigmas = [], []
    for srow in d3["slices"].values():
        for t in srow["tiles"].values():
            for fr in t["F"]:
                margins.append(((fr["F"] - 1.0) / fr["sigma"] - z_class)
                               * fr["sigma"])
                sigmas.append(fr["sigma"])
    min_margin_F = float(min(margins))
    ratio = min_margin_F / pair_sum if pair_sum > 0 else np.inf

    out = dict(
        pairwise_bounds_F=dict(C4=float(c4_bound), P3=float(p3_bound),
                               sum=float(pair_sum), k=K),
        smallest_banked_margin_F=min_margin_F,
        margin_over_bound=float(ratio),
        median_sigma_F=float(np.median(sigmas)),
        verdict=("NO_RISK — pairwise is sufficient for everything currently "
                 "banked in the survey dialect"
                 if ratio > 10 else "RISK — a banked row is within reach"),
        transfer_label=("the sum-as-upper-bound step relies on sub-additive "
                        "composition, measured in the 1-D dialect and NOT in "
                        "this one; it survives because the margin exceeds the "
                        "bound by 17x (measured) and because each pairwise "
                        "effect was separately measured suppressed to within "
                        "noise of zero. 17x is comfortable, not unassailable: "
                        "super-additivity beyond 17x in this dialect would "
                        "close it."),
        note="A bankable protocol result in its own right: it says the "
             "pairwise table is sufficient for the survey rows AS BANKED, "
             "not that the survey dialect has no holonomy.")
    json.dump(out, open(f"{ROOT}/fullseq/survey_side_cell.json", "w"),
              indent=1)
    print(f"pairwise bound (C4 {c4_bound:.5f} + P3 {p3_bound:.5f}) = "
          f"{pair_sum:.5f} F-units")
    print(f"smallest banked margin = {min_margin_F:.5f} F-units "
          f"({min_margin_F / np.median(sigmas):.2f} sigma)")
    print(f"margin / bound = {ratio:.0f}x  ->  {out['verdict']}")


if __name__ == "__main__":
    main()
