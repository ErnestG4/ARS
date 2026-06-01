# Phase 37 — Pre-Bank Verification (2026-06-01, Will's three checks)

Three methodological gates run before the Set-1 wave banks any verdict. All resolved.

## 1. Pass-1 bit-exactness gate (BLOCKING) — PASSED
**Claim to test (not the one calibrator-validation proved):** does adding I.10_cv + I.11_mass03 to shared
`axes.py` leave the OLD axes AND their quadrant assignments bit-exact? (Calibrator-validation proved the NEW
axes are correct; it did NOT prove the edit is non-perturbing to old reads — different claims, and the gap is
where silent drift enters a whole-program re-audit.)

- **Structural:** the Phase-37 commit touched ONLY `cross_substrate/axes.py` (+22 lines) + phase37 scripts;
  `arithmetic_toolkit.py` (home of `joint_q_profile` + `joint_quadrant_diagnostic`) had **0 changes**.
  `joint_quadrant_diagnostic(joint_df, ...)` classifies a `joint_q_profile` DataFrame by fixed thresholds
  (rep_int_low/mid, rf_spike_factor, ks_gue_calibrator); `arithmetic_toolkit` imports NOTHING from `axes`
  (0 matches). ⇒ the quadrant is a function of the event-position profile, NOT the Family-I vector — the
  hypothesized "quadrant = joint function of the axis vector, so inserting dims moves it" coupling does not
  exist in this codebase. compute_family_I is a dict comprehension of independent per-axis fns on one
  spacing array; adding two keys cannot change the other nine.
- **Empirical (end-to-end, deterministic substrate):** old (backup tgz) vs regenerated `ret1-cell` —
  **3250 (cell × old-axis) values across 325 cells, NON-IDENTICAL = 0, max|Δ| = 0.000e+00**; only new keys
  are I.10/I.11 (strict superset). `calibration-anchors` axes also bit-exact.
- **No banked quadrant can move:** no per-cell coordinate file stores a quadrant (they store axis scalars);
  the quadrant is computed downstream from the untouched `joint_q_profile`, and `reaudit_summary` computes
  its two-axis label from CV/mass directly (not `joint_quadrant_diagnostic`).

**VERDICT: wave is CLEAN — it measures the data, not the edit.** The retina flag (ret1 73% clustering-side)
stands on its own (per-cell RGC burstiness at spike-time resolution = real biology, no pooling/grid).

## 2. Set 4 characterization refinement — what the instrument actually measures
Side-assignment holds across gamma/weibull/lognormal/IG/hyperexp (Set 4) ⇒ the axes don't read interval
SHAPE, they read ~one scalar: signed Poisson-distance on the dispersion line. Open question (Will): is FIRING
MAGNITUDE a pure function of CV, or shape-dependent within a side? Matched-CV cross-family comparison (from
set4_calibrator_family_map.jsonl):
- **Repulsion magnitude (rep_med) ≈ PURE function of CV:** cross-family spread at matched CV = **2% (CV 0.55),
  5% (CV 0.70)** on its firing side. The repulsion coordinate LITERALLY IS signed Poisson-distance.
- **Clustering magnitude (mass03) = CV + residual SHAPE:** cross-family spread at matched CV = **15–50%**
  (it's a quantile, frac<0.3 — equal-CV / different-shape distributions give different mass03).

**Characterization:** the REPULSION axis is a clean marginal-CV reader (family-invariant, orthogonal to serial
structure per Arm B); the CLUSTERING axis (mass<τ) is CV-co-monotone but shape-carrying. **Sharpens the
magnitude guardrail one more notch:** cross-substrate `mass<τ` comparison is SHAPE-confounded (not only
N-confounded); only the repulsion magnitude is a clean CV proxy. [[pooled_rhythmic_repulsion_confound]] guardrail.

## 3. Set 3 substrate-vs-readout-quantization discriminator — SUBSTRATE (route A)
The fp16→int4 clustering shift could be (A) genuine surprisal restructuring or (B) surprisal-VALUE coarsening
→ threshold-crossing ties/bunching = the grid artifact on the surprisal axis. Discriminator
(phase37/set3_discriminator.py, structured text):
- int4 surprisals are **CONTINUOUS, not discretized**: tie_frac **0.0000** (fp16 0.0017), unique_frac 1.0,
  min-gap/std ~6e-8 (distinct to float precision) — bnb nf4 is weight-only w/ high-precision compute, so the
  surprisal values the observable sees stay continuous.
- **Dither test:** mass03 shift (int4−fp16) = **+0.0604 plain, +0.0604 dithered** (identical) — survives.

**VERDICT: route A (SUBSTRATE).** int4 genuinely restructures the surprisal sequence toward more clustering;
it is NOT readout-quantization. The Phase-36 parallel is CONCEPTUAL ("both involve quantization") but
mechanistically OPPOSITE (real substrate change vs instrument artifact) — the dither discriminator proves
which, and prevents conflating them.
