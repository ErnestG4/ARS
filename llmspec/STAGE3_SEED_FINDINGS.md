# Seed-leg findings (STAGE3_SEED_PREREG.md, 2f38b8b) — filled in as seeds complete

## Seed 1 (pythia-410m-seed1; completed 14:57)
- **A. Sealed null: 259 HOLDS / 1 VIOLATED** — per-head Q at step 143000, Δq −0.103 (Δ⟨r̃⟩ −0.0059).
- **Gate-first ladder** (registered order; stage3_ladder.py, committed before running):
  1. G0 for the type: passes.
  2. Density-matched witness: COE(64) mapped through each of the 384 heads' own λ density (G7 mixture fits), identical
     pipeline, R = 10.
     - It gives Δq −0.065 ± 0.011 and Δ⟨r̃⟩ −0.0001.
     - The observed deviation is reproduced within the registered tolerance (|−0.103 − (−0.065)| = 0.038 ≤ 0.10;
       |Δ⟨r̃⟩| 0.006 ≤ 0.010) → label **DENSITY_ARTIFACT**, as registered. Ladder step 3 is not reached.
- **Stated with the label:** the registered tolerance is loose relative to the noise.
  - After the density correction, a residual of −0.038 in q (≈ 3.5 × the density-witness SD) and −0.006 in ⟨r̃⟩ (≈ 3 ×
    the G1 witness SD; ⟨r̃⟩ needs no unfolding and is density-robust per G7) remains.
  - Per-head Q's Δq drifts steadily over training: −0.02 at init, −0.06 by 2000, −0.10 by 143k. Standard 410M shows the
    same drift (to −0.089, just inside tolerance).
  - This small, noise-scaled departure in per-head Q is a CANDIDATE for a pre-registered noise-scaled follow-up. It is
    not a finding, and the sealed verdict stands.
- **B. R1–R6:**
  - R1 DOES NOT REPLICATE on its norm clause (rotary mass 0.486 vs null 0.250; rotary rows 0.285 > 0.27).
  - R2, R3, R4, R5, R6 REPLICATE. R3 ratios: Q 7.7, K 10.7, V 6.3, O 3.1, MLP_IN 19.3, MLP_OUT 3.3. Standard 410M
    failed R3, so R3 already looks seed-sensitive.
- The witness-reuse scale check runs at the end of the seed queue. This seed's null reading is provisional until it
  passes.

## Seed 2 (completed 16:16)
- **A. Sealed null: HOLDS 260/260**, with the worst |Δq| 0.099, just inside tolerance.
  - Per-head Q at 143k: Δq −0.091, Δ⟨r̃⟩ −0.0034. This is the same late-training per-head-Q drift as standard 410M
    (−0.089) and seed 1 (−0.103, ladder → DENSITY_ARTIFACT).
  - G0 passes.
- **B. All six replicate.**
  - R1: rotary mass 0.461; rotary rows 0.2673 ≤ 0.27.
  - R3 ratios: Q 7.6, K 10.2, V 7.5, O 3.4, MLP_IN 21.1, MLP_OUT 3.1 (minimum 3.09).
  - R4 at step 512: OV 0.974, QK 0.021. R5 (512, 1000). R2 and R6 pass.
- **Running pattern (3 of 10 seeds, counting standard 410M):**
  - R1's norm clause straddles its 0.27 ceiling (rows 0.267–0.285), while the concentration (0.46–0.49 vs null 0.25)
    is stable.
  - R3's weakest ratios (O, MLP_OUT) sit near 3.
  - Both look set to be SEED-DEPENDENT on a threshold rather than on the phenomenon. This is noted before the count
    is in, and the verdict will be the registered count.

## Seed 3 (completed 17:34)
- **A. Sealed null: {'HOLDS': 260}.** Worst |Δ⟨r̃⟩| 0.0058, |Δq| 0.089. Per-head Q at 143k: Δq -0.065, Δ⟨r̃⟩ 0.0002. G0 passes: True. No VIOLATED cells.
- **B. All six REPLICATE.** R1: rotary mass 0.391, rows 0.2261. R3 ratios: Q 7.5, K 9.6, V 7.2, O 3.1, MLP_IN 21.5, MLP_OUT 3.1. R4 at 512: OV 0.974, QK 0.029. R5 [512, 1000].

## Per-head-Q drift diagnostics (after review, 17:45–18:20; Addendum S1 committed first, bb7e573)
- **Descriptive flag, applying to every run:** per-head Q's bulk Brody q drifts steadily down over training. This is a
  systematic, directional effect reproduced in 4/4 runs, not noise. The reading-A verdicts above stand as registered;
  the drift is annotated, never relabelled.
  - Δq trajectory (steps 0 / 512 / 2k / 8k / 32k / 96k / 143k): std +0.03 / −0.00 / −0.05 / −0.06 / −0.07 / −0.07 / −0.08;
    s1 −0.02 … −0.10; s2 +0.03 … −0.09; s3 +0.01 … −0.07.
  - Δ⟨r̃⟩ (no unfolding) at 143k: −0.0022 / −0.0059 / −0.0034 / +0.0002. Small and mixed in sign next to the q drift.
- **G7-style calibrator on trained per-head-Q densities** (stage3_ladder.py; COE mapped through each head's own
  end-of-training λ density, identical pipeline, R = 10):
  - It reproduces Δq −0.067 / −0.065 / −0.065 / −0.052, about 73% of the observed −0.081 / −0.103 / −0.091 / −0.065.
  - At step 2000 (std) it predicts −0.053 vs −0.047 observed.
  - **Documented instrument bias (for the calibrator zoo):** kde(4)-unfolded Brody q on trained 410M per-head-Q
    density shapes (64 levels) reads ~0.05–0.07 low for a true β=1 spectrum.
- **Residual after the density correction:** −0.014 / −0.038 / −0.026 / −0.013 (4/4 negative). Interim mean −0.023,
  z = −3.8 (n = 4); Δ⟨r̃⟩ interim z = −2.2.
  - **INTERIM — no verdict.** The pre-registered test (stage3_drift_test.py, frozen before seeds 4–9) issues its verdict
    only at n = 10 and is queued at the end of the seed leg.
- **Noise model.** At step 0 (random weights), per-head-Q Δq already varies across runs by SD ≈ 0.024, about 2.3× the G1
  witness replicate SD (0.0105). Between-run variability exceeds what the witness captures, so the test uses the
  empirical between-run SD.
- **Devices** (unchanged by the queue split): extraction is GPU fp64 (encoded in the extraction estimator_version);
  analysis, ladder and drift test are CPU numpy, as in every earlier run.

## Seed 4 (completed 19:05)
- **A. Sealed null: {'HOLDS': 260} → HOLDS (per-head-Q drift flagged: Δq at 143k = -0.049, Δ⟨r̃⟩ = -0.0016).** Worst |Δ⟨r̃⟩| 0.0057, |Δq| 0.093. G0 passes: True.
- **B.** R1 ✗, R2 ✓, R3 ✗, R4 ✓, R5 ✓, R6 ✓. R1: rotary mass 0.307, rows 0.2467. R3 ratios: Q 7.56, K 10.03, V 5.53, O 2.61, MLP_IN 19.42, MLP_OUT 3.02. R4 at 512: OV 0.979, QK 0.026. R5 [512, 1000].
