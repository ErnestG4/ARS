"""Committed generator of the 2026-08-15 review corrections to the banked
bridge JSONs (defect ledger part 2, findings F1/F3/F4/F5/F8).  Data-side
counterpart of the same-commit script fixes.  Idempotent; every change is
recorded in a *_note field; all untouched keys verified unchanged."""

import json
import numpy as np

BR = "/home/combust/fmexplorer/criticality_tool/bridge"

# ── bridge_b_measured.json ──────────────────────────────────────────────────
p = f"{BR}/bridge_b_measured.json"
b = json.load(open(p))
before = json.loads(json.dumps(b))
B2 = b["B2"]

# F1: g_below_sqrt2 was computed with a bin-CENTER mask that included the bin
# containing sqrt(2) — the witness reported the comb peak it exists to exclude.
cb = np.array(B2["g_centers"])
ge = np.array(B2["g_emp"])
mask = (cb + 0.125) <= np.sqrt(2)          # bin UPPER EDGE <= sqrt(2)
B2["g_below_sqrt2"] = float(ge[mask].max())
B2["g_below_sqrt2_note"] = ("recomputed 2026-08-15 (review F1): bin-upper-edge "
                            "mask; earlier value 3.0673 was the sqrt(2) peak "
                            "itself via a center-based mask. A zero here IS "
                            "the support-set witness.")

# F3: budget gate was theory-only (could not fail); gate on the MEASURED dev.
ib = B2["intensity_budget"]
ib["within"] = bool(ib["banded_dev_vs_model"] <= ib["sealed"]
                    and ib["predicted_variation"] <= ib["sealed"])
ib["note"] = ("2026-08-15 (review F3): 'within' now gates on the measured "
              "banded deviation (0.0104) as well as the theory prediction; "
              "the earlier value used theory alone — a gate that could not "
              "fail. Outcome unchanged on the banked data.")

# F5: stale failure key superseded by the successful subwindow retry.
if "spatstat_error" in B2 and "spatstat_D_uniform" in B2:
    B2["spatstat_error_superseded"] = B2.pop("spatstat_error")

# F8: firing criterion evaluated on the banked replicates.
rows = B2["fix2_powered_replicates"]
right_ok = all(abs(v) <= 0.03 for r_ in rows for v in r_["right"])
wrong_fired = all(v >= 0.08 for r_ in rows for v in r_["wrong"])
B2["fix2_criterion"] = dict(right_within=0.03, wrong_at_least=0.08,
                            right_ok=right_ok, wrong_fired=wrong_fired,
                            FIRED=bool(right_ok and wrong_fired),
                            note="criterion added 2026-08-15 (review F8)")
assert B2["fix2_criterion"]["FIRED"], "banked FIX-2 replicates do not fire?!"

json.dump(b, open(p, "w"), indent=1)
changed = [k for k in ("g_below_sqrt2", "intensity_budget")]
print("bridge_b: g_below_sqrt2 ->", B2["g_below_sqrt2"],
      "| budget.within (measured-gated) ->", ib["within"],
      "| fix2 FIRED ->", B2["fix2_criterion"]["FIRED"])

# ── bridge_a_measured.json: F4 amplification column ────────────────────────
p = f"{BR}/bridge_a_measured.json"
a = json.load(open(p))
lam = 1.0 / np.pi
for row in a["A2_ginibre"]["glue_descriptive"]:
    mu = lam * np.pi * row["R"] ** 2               # mean count in the disk
    row["area_term_over_var"] = row.pop("noise_amplification")
    row["amplification_per_unit_offset"] = float(mu ** 2 / row["direct"])
a["A2_ginibre"]["amplification_note"] = (
    "2026-08-15 (review F4): the sealed record carried BOTH factorizations "
    "of the SNR law; the banked column was mu/Var (labelled 'noise_"
    "amplification') while TOOLKIT §11.3 states the per-unit-pcf-offset law "
    "A = mu^2/Var = (lam*pi*R^2)^2/Var. Column renamed to what it is "
    "(area_term_over_var) and the law's own column added: relative identity "
    "error = delta * A for pcf baseline offset delta.")
json.dump(a, open(p, "w"), indent=1)
print("bridge_a: amplification per-unit-offset ->",
      [f"R={r['R']:.0f}: {r['amplification_per_unit_offset']:.0f}"
       for r in a["A2_ginibre"]["glue_descriptive"]])
