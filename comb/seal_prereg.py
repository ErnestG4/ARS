"""Assemble and seal comb/prereg_sealed.json (committed generator).
Refuses overwrite.  Written and sealed BEFORE any fresh-wedge sieve exists;
every §4.5 item of the brief is embedded here, not promised."""

import json
import os
import sys
import numpy as np

CT = "/home/combust/fmexplorer/criticality_tool"
OUT = f"{CT}/comb/prereg_sealed.json"
if os.path.exists(OUT):
    sys.exit("SEAL ALREADY EXISTS — refusing to overwrite.")

CODE_FREEZE_COMMIT = "9eb285a8d426a4210d5586d0050053746c687e1d"

ss = json.load(open(f"{CT}/comb/singular_series_banked.json"))
kagm = json.load(open(f"{CT}/comb/exact_offsets_kag_measured.json"))
assert kagm["PASS"], "estimator KAG must be green before sealing"

# ── windows (fresh; B2 wedge [0.15,0.35] excluded) ──────────────────────────
T1, T2 = 0.45, 0.65
BAND1 = (9_000_000, 12_960_000)      # radii 3000-3600 (B2 norms, DISJOINT wedge)
BAND2 = (36_000_000, 51_840_000)     # radii 6000-7200 (fully new; ~4x norm)

# ── power seal (analytic, pre-sieve): per-class sigma from lambda_model ─────
def band_power(norm_lo, norm_hi):
    r1, r2 = np.sqrt(norm_lo), np.sqrt(norm_hi)
    area = 0.5 * (T2 - T1) * (norm_hi - norm_lo)
    lam = 2.0 / (np.pi * np.log(0.5 * (r1 + r2)))
    n = lam * area
    return n, 2.0 * lam            # (expected points, occupancy rho)

power = {}
ok_power = True
for cid, cl in ss["classes"].items():
    if not cl["mandatory"]:
        continue
    sig2_inv = 0.0
    for lo, hi in (BAND1, BAND2):
        n, rho = band_power(lo, hi)
        E = (cl["n_offsets"] / 2) * n * rho          # canonical half-set
        sig = np.sqrt(E * cl["S_prime_pred"]) / E    # Poisson
        sig2_inv += 1.0 / sig**2
    sp = float(1.0 / np.sqrt(sig2_inv))
    power[cid] = dict(sigma_pooled_pred=sp, ok=bool(sp <= 0.02))
    ok_power = ok_power and sp <= 0.02
assert ok_power, "POWER SEAL FAIL — adjust window geometry BEFORE sealing"

seal = {
  "sealed_utc_date": "2026-08-14",
  "author": "Claude Fable 5. Sealed before any fresh-wedge data exists. "
            "The B2 window (theta [0.15,0.35]) is the DISCLOSED PILOT GLIMPSE "
            "(brief §0.5) and gates nothing here.",
  "arc": "Comb calibrator micro-arc (COMB_CALIBRATOR_BRIEF.md, approved with "
         "amendments 2026-08-14).",
  "epistemic_tier": "CONJECTURE-BACKED-COMPUTABLE (binding on every artifact): "
                    "HL constellation weights unproven; singular series "
                    "computable to arbitrary precision.",
  "anti_claim": "No universality-class claims; no promotion of the B2/B3 "
                "scale-qualified filing.",
  "code_freeze": {
    "commit": CODE_FREEZE_COMMIT,
    "files": ["comb/singular_series.py", "comb/exact_offsets.py",
              "comb/run_kag.py"],
    "rule": "No analysis-code change after fresh data exists; a post-freeze "
            "defect fix requires a dated seal addendum and re-derivation of "
            "every affected number.",
    "estimator_kag": "PASS (comb/exact_offsets_kag_measured.json: worst |z| "
                     "3.07 over 152 tests, grand mean z +0.015)"
  },
  "prediction_first": {
    "C_prime_G": ss["C_prime_G"],
    "tail_bound_rel": ss["tail_bound_rel"],
    "anchor": ss["anchor"],
    "classes": {cid: dict(S_prime_pred=cl["S_prime_pred"],
                          n_offsets=cl["n_offsets"],
                          mandatory=cl["mandatory"])
                for cid, cl in ss["classes"].items()}
  },
  "windows": {
    "wedge_theta": [T1, T2],
    "band1_norm": list(BAND1),
    "band2_norm": list(BAND2),
    "fresh_declaration": "band1 shares B2's norms with a DISJOINT wedge; "
                         "band2 is fully new (4x norm). B2 wedge excluded."
  },
  "power_seal": power,
  "power_criterion": "predicted sigma_pooled <= 0.02 for every mandatory "
                     "class (all pass; worst listed above)",
  "extension_rule_numeric": "Fires ONCE, only on UNDERPOWERED: widen wedge to "
                            "theta [0.45, 0.85] (double the angular width), "
                            "same two norm bands, same estimator, same seal.",
  "acceptance_2x2": {
    "k": 3,
    "level_test": "PER CLASS: inverse-variance pooled S'_hat across the two "
                  "bands; |pooled - S_prime_pred| <= 3*sigma_pooled for ALL "
                  "mandatory classes -> pooled match.",
    "drift_test": "sign-coherence form (per-class z's are positively "
                  "correlated within a band — independence pooling is wrong "
                  "in principle, estimator-KAG lesson): drift z_d = "
                  "(S'_b2 - S'_b1)/sqrt(s1^2+s2^2) per mandatory class; "
                  "COHERENT DRIFT := (>= 2/3 of mandatory classes share "
                  "drift sign) AND (>= 3 classes with |z_d| >= 2).",
    "discriminator": "N50_q5m2 minus N50_q5m1 must be positive with >= 3 "
                     "sigma on the difference (predicted separation 4/3), "
                     "required for PASS.",
    "cells": {
      "pooled match x no drift": "PASS (WEIGHTS_MATCH_SINGULAR_SERIES)",
      "pooled match x coherent drift": "SOFT PASS (MATCH_WITH_BOUNDED_DRIFT) "
          "— seated BOUNDED-AT-SCALE; drift law filed with SIGN and FITTED "
          "COEFFICIENT vs 1/ln(norm); registry entry carries validated norm "
          "range",
      "pooled deviation (any class)": "FAIL substantive "
          "(DEVIATION_BEYOND_ERRORS) — drift does not rescue",
      "insufficient counts": "UNDERPOWERED -> numeric extension once"
    },
    "secondary_shells": "N in {34, 36, 64, 80, 90, 100} DESCRIPTIVE — "
                        "reported with the same statistics, gate nothing"
  },
  "pilot_informed_pedigree": "Windows, shell list, estimator config and this "
      "seal's thresholds were informed by: the disclosed B2 glimpse (brief "
      "§0.5), the estimator-KAG pilots (601-608), and the analytic power "
      "computation above. Sequence: theory + pilots -> seal -> fresh sieve. "
      "No fresh-wedge datum existed when this file was written."
}

json.dump(seal, open(OUT, "w"), indent=1)
print("SEALED. Worst predicted sigma_pooled:",
      max(v["sigma_pooled_pred"] for v in power.values()))
