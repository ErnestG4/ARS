"""Survey arc seal generator (committed).  Refuses overwrite.  Written after
D0+D1 and the declared pre-seal audits, BEFORE any science measurement.
Code-freeze blob SHAs are stamped by the runner-side check against the values
recorded here at seal commit time."""

import json
import os
import subprocess
import sys

SV = "/home/combust/fmexplorer/criticality_tool/survey"
OUT = f"{SV}/prereg_sealed.json"
if os.path.exists(OUT):
    sys.exit("SEAL EXISTS — refusing to overwrite.")

audit = json.load(open(f"{SV}/preseal_audit.json"))
FROZEN = ["survey_io.py", "tiling.py", "estimators.py", "mask_kag.py",
          "verdict_lattice.py", "run_mask_kag.py", "run_d2_gates.py",
          "run_d3_measure.py", "seal_prereg.py", "acquire.py"]
shas = {f: subprocess.run(["git", "hash-object", f"{SV}/{f}"],
                          capture_output=True, text=True).stdout.strip()
        for f in FROZEN if os.path.exists(f"{SV}/{f}")}

seal = {
  "sealed_utc_date": "2026-08-15",
  "arc": "Survey arc (SURVEY_ARC_BRIEF.md, approved 2026-08-15).",
  "anti_claim": "Brief §0 verbatim: no cosmology, no 3D-field statements, no "
                "hyperuniformity-of-the-universe claims in either direction; "
                "claims attach to the projected process, per sealed slice.",
  "expectation_registration": "Brief §0.1: super-Poissonian at all sealed "
      "scales. Sub-Poissonian anywhere -> INSTRUMENT_HOLD, audit first.",
  "slices": {"primary": [0.6, 0.8], "comparison": [0.4, 0.6]},
  "windows_and_tiles": {
      "tiling": "10x10 deg gnomonic, MIN_EFF_FRACTION 0.60, corner "
                "distortion 1.54% <= 2% budget; 28 accepted tiles (D1)",
      "randoms": "8-file subset, disjoint halves (even=KAG, odd=null), "
                 "MANIFEST.json SHAs"},
  "scale_ranges": {
      "pcf_bins_deg": [0.05, 1.0, 0.05],
      "sigma2_L_deg": [0.1, 0.2, 0.5],
      "watch_item_adjudication": "L = 1.0 deg EXCLUDED from the sealed range "
          "per the D1 watch item: F(1 deg) leaned low (~0.93) with the bias "
          "pointing sub-Poissonian — the direction of the §0.1 surprise "
          "clause; a tile-edge artifact must not be allowed to fire "
          "INSTRUMENT_HOLD. Class power is >= 70 sigma at the retained "
          "scales, so the cap costs nothing. L=1.0 re-enters, if wanted, "
          "through the numeric extension rule with its own dry-run — not "
          "through the front door.",
      "r_min_deg": 0.05,
      "r_min_provenance": "DESI positioner patrol scale (arXiv:2404.03006, "
          "2406.04804, 2411.12025); nothing quoted below it, even "
          "descriptively (tripwire 4)."},
  "null_model_freeze": "BINDING: the estimator null model — the randoms-"
      "shot-noise term (W_D/W_R)*w2bar_R*Ebar in the cell-expectation "
      "variance, the weighted-pair effective-count z calibration, and the "
      "small-mean 4th-moment sigma_F — is load-bearing measurement code "
      "inside the blob-SHA freeze. NO null-model term changes after this "
      "seal, KAG-derived or otherwise. The KAG is the one place debugging "
      "is legal, and THE DEBUGGING WINDOW CLOSES WHEN THE SEAL CLOSES. Any "
      "post-seal change requires a dated addendum and re-derivation of "
      "every affected number.",
  "budgets": {
      "tile_weight_budget": "|tile mean w / global - 1| <= 0.05 (pre-seal "
          "audit observed max 0.0235; preseal_audit.json); tiles beyond "
          "budget excluded by rule (tripwire 3)",
      "cell_floor": "E_c >= 0.2 * median (estimators.CELL_FLOOR)"},
  "extension_rule_numeric": "Fires ONCE, only on UNDERPOWERED: "
      "MIN_EFF_FRACTION 0.60 -> 0.50 (dry-run EXECUTED pre-seal: 28 -> 31 "
      "tiles, preseal_audit.json). No other extension exists.",
  "power_criterion": ">= 20 accepted tiles per slice AND >= 500 pooled "
      "accepted cells at every sealed L AND class separation |z| capability "
      ">= 5 at every sealed L (analytic: >= 70 sigma at retained scales).",
  "lattice": {
      "module": "verdict_lattice.py (rulings-as-code; includes the "
                "implementation-time completion CLASS_INCONSISTENT_ACROSS_"
                "TILES — the brief's §4 had no cell for tile disagreement)",
      "Z_CLASS": 5.0, "CONSISTENCY_FRAC": 0.9, "DRIFT_CHI2": 9.0},
  "instrument_hold_checklist_numeric": [
      "H1 offending tile re-passes the weight budget (<= 0.05)",
      "H2 offending tile eff-fraction within 3 sigma of the accepted-tile "
      "population",
      "H3 per-tile mask KAG re-run on the offending tile: green under the "
      "D1 arms",
      "H4 F recomputed with the KAG randoms half swapped in as "
      "expectations: consistent within 3 sigma of the null-half value"],
  "instrument_hold_exit": "All four pass -> bank with audit attached; any "
      "fail -> defect filed, tile excluded by rule, measurement re-run. No "
      "other analyst action in hold.",
  "obstruction_envelope": "Sigma2-from-pcf row is DESCRIPTIVE (A = mu^2/Var "
      "is 1e4-1e8 at survey mu). OBSTRUCTION_BANKED requires: class calls "
      "differ AND |F_cells - F_pcf| > 3*sqrt(sigma_F^2 + sigma_pcf_int^2) "
      "where sigma_pcf_int propagates the per-bin pcf noise floor through "
      "the same cell integral.",
  "adjacency_statement": "At the sealed L <= 0.5 deg (<= tile/20) with "
      "per-tile expectation normalization (tile-mean density absorbed by "
      "the per-tile W_D/W_R scale), super-tile mode sharing enters at "
      "second order; sealed effective-N statement: tile scatter treated as "
      "independent at the sealed scales. Non-adjacent subsets NOT required "
      "at this range (they would be at L approaching the tile scale — "
      "which is excluded).",
  "d2_fix2_gates": {
      "right_lens": "weighted expectations (null half, released WEIGHT): "
          "thinned-KAG F within the D1 arms",
      "wrong_lens_real": "unweighted expectations at real DESI weight "
          "amplitude — REGISTERED EXPECTATION: near-inert (weights are "
          "mild, mean 1.005; the B2 thin-window observation's analog); "
          "filed as the amplitude observation either way",
      "wrong_lens_powered": "synthetic weight gradient injected into the "
          "thinned-KAG data (w <- w * (1 + G*(x/5deg)), G = 0.5): wrong "
          "lens (ignore injected weights in expectations) must push F "
          "above right-lens by >= 5 sigma at some sealed L in every test "
          "tile (in-code FIRED bool); right lens (injected weights in both "
          "slots) must stay within arms. A falsifier that cannot fire "
          "certifies nothing.",
      "double_weighting_tripwire": "weights enter expectations exactly "
          "once (tripwire 1): data weights in W_D and N_c; randoms weights "
          "in RR/E_c; no second application anywhere"},
  "pilot_informed_pedigree": "Windows/tiles/arms from D0+D1 (mask KAG, "
      "declared estimator-null fix pre-seal); weight budget from the "
      "declared pre-seal audit (selection-model territory, no clustering "
      "statistic touched); extension dry-run executed. Sequence: D0+D1 + "
      "audits -> seal -> D2 gates -> D3 measurement.",
  "code_freeze_blob_shas": shas,
}
json.dump(seal, open(OUT, "w"), indent=1)
print("SEALED.", len(shas), "files frozen:")
for f, s in shas.items():
    print(" ", f, s[:12])
