"""Assemble and seal bridge/prereg_sealed.json.

Every tolerance is DERIVED (pilot ensembles / banked anchor), never typed:
  * G-A2 tolerance ← bridge/gue_pcf_anchor.json (P3 micro-deliverable).
  * All others ← bridge/pilot_tolerances.json (pilot seeds disjoint from gate
    seeds; rule tol = 2×worst-pilot-deviation with floors, stated per entry).
Runs once; refuses to overwrite an existing seal (a re-seal after seeing gate
data would be the exact post-hoc freedom prereg exists to remove).
"""

import json
import os
import sys

BR = "/home/combust/fmexplorer/criticality_tool/bridge"
OUT = f"{BR}/prereg_sealed.json"
if os.path.exists(OUT):
    sys.exit("SEAL ALREADY EXISTS — refusing to overwrite. Delete manually only "
             "with a filed justification.")

pilot = json.load(open(f"{BR}/pilot_tolerances.json"))
pilot2 = json.load(open(f"{BR}/pilot2_gluing.json"))
pilot3 = json.load(open(f"{BR}/pilot3_gb1.json"))
pilot4 = json.load(open(f"{BR}/pilot4_thomas.json"))
anchor = json.load(open(f"{BR}/gue_pcf_anchor.json"))

seal = {
  "sealed_utc_date": "2026-08-14",
  "author": "Claude Fable 5, sealed BEFORE any gate-seed compute. Pilot seeds "
            "(100-105, 910-915) and anchor seeds (700-723) were run solely to "
            "derive tolerances and are disjoint from gate seeds (1-3, 920-931).",
  "arc": "ARS Bridge Arc — transition functions to the spatial-statistics atlas.",
  "anti_claim": "BINDING (brief §5): no new universality-class claims. "
                "Deliverables are translations, cross-checks, protocol.",
  "step_zero_outcome": "R + spatstat 3.6-2 installed user-space (micromamba) at "
                       "bridge/.rquarantine (gitignored). Observer B is genuine "
                       "spatstat; the pure-Python fallback caveat is NOT needed. "
                       "No-black-box rule (tripwire 5) still applies.",
  "substrates": {
    "1d": ["homogeneous Poisson n=1e5 (gate seeds 1-3)",
           "zeta window: data/odlyzko_zeros1.txt (100k zeros), unfolded by "
           "arsrh/phase1_zeta_crossover.py:61 unfold_zeta (reused by import). "
           "Fallback (pre-registered, P2): large-N CUE via phase34d/circular_sampler.py. "
           "No HKPV sine-kernel sampler is promised."],
    "2d": ["homogeneous Poisson rect 120x120 (gate seeds 1-3)",
           "Ginibre N=2048 UNSCALED (intensity 1/pi), central sub-window 0.8*sqrtN, "
           "gate seeds 920-931; sampler KAG PASSED (bridge/ginibre_kag_measured.json)"]
  },
  "tolerances": {
    "G_A1_1d_K":  max(0.05, 2 * pilot["pois1d"]["devK"]),
    "G_A1_1d_g":  max(0.02, 2 * pilot["pois1d"]["devg"]),
    "G_A3_1d_rel": max(0.05, 2 * pilot["pois1d"]["relSigma"]),
    "G_A1_2d_L":  max(0.05, 2 * pilot["pois2d"]["devL"]),
    "G_A1_2d_g":  max(0.02, 2 * pilot["pois2d"]["devg"]),
    "G_A2_gue_pcf": anchor["TOLERANCE_G_A2"],
    # per-L, scaled from the GUE pilot (n=3686/seed) to the zeta window
    # (n=100000): amplified identity error is bin-noise-dominated and
    # bin noise scales as 1/sqrt(n), so tol(L) = 2*pilot_rel(L)*sqrt(n_ratio)
    "G_A3_1d_gue_rel": {k: max(0.10, 2 * v * (3686.0 / 100000.0) ** 0.5)
                        for k, v in pilot2["gue1d"].items() if float(k) <= 5.0},
    "G_B1_ginibre_pcf_rms": max(0.02, 2 * pilot3["rms_dev"]),
    "G_A3_2d_pois_rel": max(0.10, 2 * pilot4["pois2d"]["rows"][0]["rel"]),
    "G_A3_2d_thomas_rel": max(0.15, 2 * pilot4["thomas2d"]["rows"][0]["rel"]),
    "XCHECK_rel": 0.02,
    "B2_intensity_budget": 0.05
  },
  "G_A3_ginibre_descriptive": "2-D gluing on Ginibre is reported DESCRIPTIVELY, "
      "not gated: for a class-I hyperuniform process Var N(R) is a near-"
      "cancellation (= R/sqrt(pi) exactly, vs area term R^2), so pcf noise eps "
      "is amplified by ~(lam*pi*R^2)/Var — divergent with R. Mechanism derived "
      "pre-seal from the exact g (pilot2_gluing.py header); the limitation is "
      "banked as a TOOLKIT §11 instrument note. The identity ITSELF is gated "
      "with SNR on 2-D Poisson (area term) + Thomas designed instance "
      "(integral term, positive g-1) — decompose-confound-with-designed-"
      "instance discipline.",
  "tolerance_provenance": {
    "rule": "tol = 2 x worst pilot deviation, floored (0.02 abs pcf, 0.05 rel "
            "1d-gluing, 0.10 rel 2d-gluing [400-disk direct-variance noise], "
            "0.05 abs K/L)",
    "G_A2": f"banked anchor bridge/gue_pcf_anchor.json: max|dev|="
            f"{anchor['max_abs_dev']:.4f} over s in {anchor['window']}, "
            f"{anchor['n_levels_pooled']} pooled GUE levels, semicircle-CDF "
            "analytic unfold; analytic-form owner universality.py "
            "pair_correlation (R2_gue)",
    "pilot_raw": pilot
  },
  "gates": {
    "G_A1": "2D Poisson: max|L(r)-r| and max|g-1| within tolerance on r in "
            "[0.25,5]; 1D Poisson: max|K-2r|, max|g-1|, same window.",
    "G_A2": "zeta window empirical g vs 1-(sin pi s/pi s)^2, s in [0.25,5], "
            "max abs dev <= G_A2_gue_pcf.",
    "G_A3": "Sigma^2 via (g-1) integral identity vs direct, rel dev within "
            "tolerance: 1D Poisson at L in {2,5,10,20} (tol G_A3_1d_rel); zeta "
            "GATED at L in {2,5} only (tol G_A3_1d_gue_rel from the GUE gluing "
            "pilot), L in {10,20} descriptive — rigid substrates amplify "
            "identity noise by L^2/Sigma^2(L) (~555x at L=20), the 1-D face "
            "of the same class-I mechanism; 2D GATED at R=2 only, on Poisson + "
            "Thomas designed instance (pooled grid-count direct, pilot-4 "
            "config) — R in {4,6} descriptive: pilot-4 measured the identity "
            "error growing ~(lam*pi*R^2)^2/Var from an irreducible ~4e-3 "
            "pcf baseline offset at these sample sizes (2.7%->48% Poisson, "
            "6%->26% Thomas across R=2->6), with model-lambda vs lambda-hat "
            "both leaving the offset; Ginibre 2-D fully descriptive (see "
            "G_A3_ginibre_descriptive). Disagreement inside gated cells = "
            "transition-function defect, not a finding.",
    "G_B1": "Ginibre pooled pcf (12 gate seeds, central sub-window, border-"
            "corrected, erosion 4.0, bins 0.1 — pilot-3 config) vs exact "
            "g(r)=1-exp(-r^2) [intensity 1/pi units], r in [0.25,4]: RMS dev "
            "<= G_B1_ginibre_pcf_rms (RMS is the sealed metric — noise-robust; "
            "max-abs reported descriptively).",
    "XCHECK": "no-black-box: our border-corrected K vs spatstat Kest border "
              "column, max rel dev <= 2% on r in [1,5]."
  },
  "B1_criteria": {
    "claim_level": "CLASS-LEVEL ONLY (tripwire 6). A repulsive DPP family must "
                   "beat Poisson AND Thomas on the uniform contrast "
                   "D = int_[0.25,4] (g_emp - g_model)^2 dr (upper limit = "
                   "the G-B1 pcf grid reach), and the fitted interaction "
                   "range must cohere with mean spacing.",
    "r_half_ratio": [0.2, 1.0],
    "r_half_derivation": "theory-fixed before compute: exact Ginibre g gives "
                         "r_half = sqrt(ln 2) = 0.8326, mean spacing sqrt(pi) "
                         "= 1.7725, ratio 0.470; repulsive DPPs cross g=0.5 "
                         "below one mean spacing, hence [0.2, 1.0].",
    "family_list_declared": "spatstat: dppGauss, dppCauchy, dppMatern, "
                            "dppPowerExp (verified installed); python: gauss, "
                            "cauchy, powerexp, matern (dpp_python.py). Ginibre "
                            "kernel (complex) in NO family: declared "
                            "approximation, kernel-level ID out of scope."
  },
  "B2_sealed_before_B1": {
    "substrate": "split Gaussian primes, annular wedge r in [3000,3600], "
                 "theta in [0.15,0.35] rad (bridge/gaussian_prime_annulus.py)",
    "intensity_model": "lambda(r) = 2/(pi ln r), theory-supplied (Landau); "
                       "predicted variation across annulus 2.24% <= 5% budget",
    "declared_approximations": [
      "wedge excludes axes -> no inert primes (measure-zero rays)",
      "support set is the checkerboard sublattice {a+b odd} of Z[i], min pair "
      "distance sqrt(2): continuous families cannot express lattice support "
      "(TOOLKIT §9 support-set discipline expected to surface)",
      "residual 2.24% intensity variation treated as stationary for the "
      "DPP fits; K_inhom exercise uses the theory lambda(r)"],
    "park_branch": "ONLY if G_B1 fails (prereg-fixed, not post-B1 preference)."
  },
  "tripwires_carried": "brief §3 items 1-6 verbatim; TOOLKIT.md §11 founded "
                       "this arc (edge correction, intensity estimation).",
  "filing_note_tripwire2_catch": "The draft brief filed Ginibre under "
      "'logarithmic number-variance growth' — a dimension-slot (tripwire-2) "
      "violation caught in CC review before sealing: log growth (Torquato "
      "class II) is 1D sine-kernel/GUE; Ginibre is class I (perimeter law, "
      "S(k)~k^2). Recorded here as an instance of the genus per amended brief."
}

json.dump(seal, open(OUT, "w"), indent=1)
print("SEALED:", json.dumps(seal["tolerances"], indent=1))
