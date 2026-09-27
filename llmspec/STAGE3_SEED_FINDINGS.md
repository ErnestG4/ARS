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

## Step-0 excess variance — diagnosis (review round 4, point 3)
- **Observation:** at step 0 (random init), per-head-Q bulk q varies across the 5 analysed runs with SD 0.021.
- **Pipeline noise floor (synthetic i.i.d.):** 40 pools of 384 heads, 64×1024, N(0, 0.019764²) (small_init
  √(2/(5·1024))), fp16-rounded, identical pipeline → q 1.0056, SD **0.0116**. This matches the G1 witness (0.0105), so
  the witness did not under-sample the instrument's noise.
- **Tensors:** consistent with i.i.d. N(0, σ²) at the config scale (layers 0 / 11 / 23 of standard 410M):
  - entry SD 0.01976–0.01978; kurtosis within ±0.005; KS vs normal ≤ 0.0008;
  - row-norm CV 0.0215–0.0221 (synthetic 0.0220–0.0226);
  - within-head row-correlation SD 0.0310–0.0314 (i.i.d. 0.03125);
  - Q, K and V blocks equally scaled.
  - Fused-QKV slicing cannot matter at init, since every row is identically distributed.
- **No cache or extraction artefact:** a fresh SVD of standard 410M step-0 per-head Q reproduces the banked q exactly
  (1.0363).
- **Where the excess sits:**
  - Random 384-head subsets drawn ACROSS runs (breaking run grouping) give q SD 0.0095, matching the i.i.d. expectation
    of 0.0104. Individual heads are i.i.d.-like; the excess is grouped.
  - Per-layer (16-head) q varies across layers with variance 1.32× the synthetic value (χ² p ≈ 0.013; the earlier
    4-layer sub-pool estimate of 2.2× rested on only 6 sub-pools per run).
  - No layer index is offset consistently across runs (two-way ANOVA F(23, 92) = 0.61, p = 0.91), so there is no
    structural init effect.
- **Conclusion: UNRESOLVED but bounded.** The excess is modest (variance 1.3–3.2× by level, p ≈ 0.01 on few degrees of
  freedom). It is invisible in the tensors' marginal and second-order statistics and not attributable to pipeline,
  cache, slicing or init scale.
- **Consequence for the frozen drift test:** none adverse. Its SE is the empirical between-run SD, which absorbs any
  such excess, so the test is conservative with respect to it. The instrument's own noise floor (0.0116) is now
  documented for the zoo.

## Seed 5 (completed 20:26)
- **A. Sealed null: {'HOLDS': 260} → HOLDS (per-head-Q drift flagged: Δq at 143k = -0.088, Δ⟨r̃⟩ = -0.0020).** Worst |Δ⟨r̃⟩| 0.0074, |Δq| 0.094. G0 passes: True.
- **B.** R1 ✗, R2 ✓, R3 ✓, R4 ✓, R5 ✓, R6 ✓. R1: rotary mass 0.501, rows 0.3011. R3 ratios: Q 6.66, K 9.18, V 5.94, O 3.29, MLP_IN 20.48, MLP_OUT 3.39. R4 at 512: OV 0.974, QK 0.026. R5 [512, 1000].

## Seed 6 (completed 21:46)
- **A. Sealed null: {'HOLDS': 259, 'VIOLATED': 1}.** VIOLATED cells: [['head_Q', 96000, -0.1058, -0.0046]]. Per-head-Q drift flagged: Δq at 143k = -0.093, Δ⟨r̃⟩ = -0.0011. Worst |Δ⟨r̃⟩| 0.0063, |Δq| 0.106. G0 passes: True.
  - Ladder step 2 (automatic, Addendum S1) on head_Q @ 96000: observed Δq -0.106 / Δ⟨r̃⟩ -0.0046; density-matched Δq -0.064 ± 0.011, Δ⟨r̃⟩ 0.0000 → **DENSITY_ARTIFACT** (the known per-head-Q drift, annotated, not relabelled).
- **B.** R1 ✗, R2 ✓, R3 ✗, R4 ✓, R5 ✓, R6 ✓. R1: rotary mass 0.470, rows 0.2706. R3 ratios: Q 7.68, K 9.97, V 3.17, O 2.09, MLP_IN 19.36, MLP_OUT 3.24. R4 at 512: OV 0.982, QK 0.044. R5 [512, 1000].

## ⚠ Witness-reuse scale check FAILED for seeds 3, 4, 5, 9 (first pass 23:20; seed 8 pending)
- The declared check (STAGE3_SEED_PREREG.md) compares each seed's mean entry rms per type at step 0 and 143k with the
  pythia-410m witness scales (±20%). Step 0 matches everywhere. The FINAL scales differ:
  - seed 3: Q 0.42, O 0.58, MLP_IN 0.77, MLP_OUT 0.51;
  - seed 4: Q 0.38, K 0.77, O 0.17, MLP_IN 0.79, MLP_OUT 0.17;
  - seed 5: Q 1.25;
  - seed 9: Q 1.37.
  - Seeds 1, 2, 6 and 7 are within ±20%.
- **Consequence, as registered:** a failing seed gets its OWN witness before its null is read. The reading-A results
  recorded above for **seeds 3, 4 and 5 are therefore PROVISIONAL** (computed against the reused witness) and are
  superseded by re-analysis against their own witnesses:
  - stage3_seed_witness_gate.py generates the witness;
  - mcfg.witness_suffix() prefers it;
  - analyze, repl and ladder are re-run, with stale ladder entries purged.
  - R1–R5 (reading B) do not depend on the witness. R6 does (via KS95) and is re-scored.
- **Descriptive (reported, not a test):** final weight scales differ strongly across seeds. Seed 4's O and MLP_OUT end
  training at ~0.17× the entry rms of standard 410M; seed 3's Q at ~0.42×. Step-0 scales are identical, so this is
  training-trajectory dependence of final norms.

## Seed 7 (completed 00:31, 27 Sep; scale check passed → reused witness is valid)
- **A. Sealed null: {'HOLDS': 260} → HOLDS (per-head-Q drift flagged: Δq at 143k = -0.071, Δ⟨r̃⟩ = 0.0000).** Worst |Δ⟨r̃⟩| 0.0080, |Δq| 0.097. G0 passes: False. Witness used: stage3_witness_pythia-410m.json.
- **B.** R1 ✗, R2 ✓, R3 ✗, R4 ✓, R5 ✓, R6 ✓. R1: rotary mass 0.497, rows 0.2877. R3 ratios: Q 7.41, K 9.39, V 6.38, O 3.20, MLP_IN 20.00, MLP_OUT 2.98. R4 at 512: OV 0.984, QK 0.042. R5 [512, 1000].
- **G0 FAIL-as-sealed for seed 7, type V** (k = 5/24 step-0 V matrices above the witness KS95, binomial p = 0.006 < 0.01).
  - As registered, seed 7's V is **not interpreted** (G0 halts interpretation for that type). The label stays FAIL.
  - **Attribution** (the pipeline was checked first, as required):
    - Step-0 MP KS distributions of Q, K and V over all 8 × 24 matrices are identical: medians 0.00681 / 0.00681 /
      0.00681; Mann–Whitney V vs Q p = 0.98, V vs K p = 0.94. i.i.d. synthetic matrices at the same shape and scale
      give 0.00679.
    - The per-type witness KS95 thresholds are Monte-Carlo estimates (480 draws each) and differ by noise alone (Q
      0.00767, V 0.00749), which makes V's rule slightly stricter.
    - 8 runs × 6 types = 48 G0 tests at α = 0.01 give P(≥ 1 false fail) ≈ 38%.
    - The fail is therefore attributed to threshold-estimation noise plus multiplicity, not to the V tensors or the
      pipeline. Same defect class as the Stage 1 G0 (a bare rate bar with no allowance for sampling or estimation
      noise).
- **G0 attribution, checked on the TAIL (review 5):**
  - One common KS95 from 1,440 pooled Q/K/V witness-style draws: 0.00759 (bootstrap SE 0.00003).
  - Exceedances over all 8 × 24 step-0 matrices: Q 11, K 9, V 15 (expected ≈ 9.6 each). χ² across types p = 0.43;
    Fisher V vs Q p = 0.54, so there is no V tail anomaly.
  - Seed 7's V: 5/24 above V's own cutoff (0.00749), 2/24 above Q's (0.00767), 3/24 above the common threshold (binomial
    p ≈ 0.12, a pass).
  - The fail is explained by V's Monte-Carlo cutoff landing low. Attribution confirmed on the tail. The label stays
    FAIL-as-sealed and seed 7's V stays uninterpreted.

## Seed weight-scale divergence — symmetry vs instability (review 5; descriptive)
- **Four checks** (step 143k, relative to standard 410M; per-head products from per-head Frobenius norms):

  | run | text loss | EMB | UNEMB | Q | K | O | MLP_OUT | ‖Q_h‖·‖K_h‖ | ‖V_h‖·‖O_h‖ |
  |---|---|---|---|---|---|---|---|---|---|
  | std | 2.329 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
  | s1, s2, s6, s7 | 2.338–2.359 | 1.00 | 1.00–1.03 | 1.09–1.14 | 1.00–1.01 | 0.98–1.02 | 1.00–1.01 | 0.97–1.03 | 1.02–1.06 |
  | s5 | 2.349 | 1.00 | 1.03 | **1.245** | 1.02 | 0.97 | 1.00 | **1.055** | 0.98 |
  | **s3** | **2.475** | 0.78 | 1.27 | 0.42 | 0.83 | 0.58 | 0.51 | **0.62** | **0.47** |
  | **s4** | **2.857** | 0.77 | 1.33 | 0.38 | 0.77 | 0.17 | 0.17 | **0.50** | **0.15** |

  - Configs are identical to standard (hidden 1024, 24 L, 16 H, rotary 0.25, init range 0.02). Downloads are sha256-
    verified, and the .bin path is bit-verified against safetensors. Not a loading mistake.
- **Seed 5 fits QK-symmetry drift.** Q alone is 1.245×, but the invariant QK product is 1.055× and the loss is normal.
- **Seeds 3 and 4 are NOT symmetry drift: they had late-training loss spikes.**
  - Text loss tracks all other runs within ~0.01 nats up to 64k.
  - Seed 3 jumps 2.415 → 2.603 between 64k and 96k, then partly recovers (2.475 at 143k).
  - Seed 4 jumps 2.358 → 3.315 between 96k and 128k and ends at 2.857.
  - Their invariant products shrink along with the individual norms, and their losses differ, so these are genuinely
    different, post-instability models. Induction survives (max 0.94).
- **Consequences:**
  - Their final-step results (reading A, R1, R3, the per-head-Q drift inputs) describe post-spike states. For example,
    seed 4's weak R1 concentration (0.307) and seed 3's (0.391) are both final-step measurements.
  - Every frozen test still includes all 10 runs, as registered. The spikes are an annotation, never a reason to
    exclude.
  - The witness-reuse failures for seeds 3 and 4 are downstream of these instabilities. For seeds 5 and 9 (Q 1.25 /
    1.37×), symmetry drift in Q is the likely cause; seed 9 is checked the same way once it is analysed.

## Witness absolute-scale test (protocol-template note; stage3_witness_scale_test.py)
- The same witness construction at the standard 410M scale vs 0.17× (seed 4's extreme). Full O at 1024² and per-head Q
  at 64 × 1024, fp16, R = 12 pools each, all bands.
  - Every difference is ≤ 0.0024 in ⟨r̃⟩ and ≤ 0.034 in q (upper band; bulk ≤ 0.0095), with mixed signs.
  - The largest relative one is per-head-Q bulk ⟨r̃⟩: −0.0024 ± 0.0008. Across 12 comparisons that is plausible, and it
    is ≤ ¼ of the sealed 0.010 tolerance in any case.
  - fp16 subnormal fraction at 0.17×: 1.4% (O) and 0.6% (per-head Q) of entries.
- **For the protocol template:** scale matching of the witness protects only against effects far below the null's
  tolerance, since spacing statistics are scale-free and fp16 rounding is relative. Future arcs can drop the ±20%
  reuse rule unless weights approach the subnormal range (or tolerances tighten by ~4×).
  - In THIS study the rule still runs as written: dedicated witnesses for the failing seeds, re-analysis primary per
    Addendum S3.
