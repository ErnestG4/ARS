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
