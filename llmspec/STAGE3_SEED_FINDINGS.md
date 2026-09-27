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

## SEED-LEG RESULT — all 10 runs (standard 410M + seeds 1–9; primary results per Addendum S3)

### A. Sealed null per run

| run | cells | VIOLATED (→ ladder) | per-head-Q drift at 143k: Δq / Δ⟨r̃⟩ | G0 |
|---|---|---|---|---|
| std | {'HOLDS': 260} | — | -0.081 / -0.0022 | pass |
| seed1 | {'HOLDS': 259, 'VIOLATED': 1} | head_Q@143000 → DENSITY_ARTIFACT | -0.103 / -0.0059 | pass |
| seed2 | {'HOLDS': 260} | — | -0.091 / -0.0034 | pass |
| seed3 | {'HOLDS': 260} | — | -0.065 / +0.0002 | pass |
| seed4 | {'HOLDS': 260} | — | -0.049 / -0.0016 | pass |
| seed5 | {'HOLDS': 260} | — | -0.088 / -0.0020 | pass |
| seed6 | {'HOLDS': 259, 'VIOLATED': 1} | head_Q@96000 → DENSITY_ARTIFACT | -0.093 / -0.0011 | pass |
| seed7 | {'HOLDS': 260} | — | -0.071 / +0.0000 | FAIL-as-sealed: V (threshold noise; tail-checked) |
| seed8 | {'HOLDS': 260} | — | -0.088 / -0.0023 | pass |
| seed9 | {'HOLDS': 260} | — | -0.089 / -0.0030 | pass |

### B. R1–R6 seed counts (registered rule: SEED-ROBUST ≥ 9/10, SEED-DEPENDENT 2–8, NOT SUPPORTED ≤ 1)

| R | replicates | verdict |
|---|---|---|
| R1_K_rotary | 2/10 | **SEED-DEPENDENT** |
| R2_cross_head_sharing | 10/10 | **SEED-ROBUST** |
| R3_update_rank_rise | 4/10 | **SEED-DEPENDENT** |
| R4_OV_before_QK | 10/10 | **SEED-ROBUST** |
| R5_induction | 10/10 | **SEED-ROBUST** |
| R6_MP_fit_collapse | 10/10 | **SEED-ROBUST** |

### C. Ten-run spreads (median [min, max]) for the criteria that straddle their bars

- R1 K rotary mass 0.478 [0.307, 0.519] vs null 0.250 [0.249, 0.252]; rotary-row norm share 0.278 [0.226, 0.303]. Concentration ≥ null + 0.10 in 9/10; rows ≤ 0.27 in 3/10. The concentration exceeds the rotary rows' norm share in every run (ratio 1.723 [1.243, 1.760]).
- R3 Q ratio 7.481 [6.664, 7.710] (≥ 3 in 10/10)
- R3 K ratio 9.779 [9.014, 10.716] (≥ 3 in 10/10)
- R3 V ratio 5.734 [1.887, 7.528] (≥ 3 in 8/10)
- R3 O ratio 2.847 [1.343, 3.348] (≥ 3 in 5/10)
- R3 MLP_IN ratio 19.389 [14.477, 21.503] (≥ 3 in 10/10)
- R3 MLP_OUT ratio 3.069 [2.114, 3.392] (≥ 3 in 7/10)
- **Seeds 3 and 4** (late loss spikes) are included in all counts, as registered. Their final-step values (R1 mass
  0.391 / 0.307; R3 O 3.3 / 2.6) are post-instability states.

### Re-analysis of seeds 3, 4, 5, 8, 9 (dedicated witnesses; primary per Addendum S3)
- Every one used its own witness (witness_used recorded in its null file).
- The dedicated witnesses reproduce the reused witness's head_Q mean to 4 decimals (1.0045 vs 1.0045). stage3_witness
  uses a fixed RNG seed, so each "own" witness is the same draws re-scaled, and only fp16 rounding changes. The
  re-analysed primary results are therefore identical to the originals (which stay logged, labelled "computed against
  invalid reused witness").
- This is a direct confirmation that absolute scale does not matter here (see the witness scale test).

### Frozen drift test (stage3_drift_test.py; Addendum S1 item 4 / S2) — registered verdict: FINDING_CANDIDATE (pending the joint reading)
> **See ADDENDUM S4 below:** the frozen calibrator's known-answer bias is −0.0207 / −0.0164, the observed residual's
> size and sign; the ⟨r̃⟩ arm is quiet under a licensed calibrator (t₉ −1.6). The drift is NOT established.
- n = 10.
- **q arm:** mean residual (observed Δq − density-matched Δq) = **−0.0197**, SE 0.0033, **t₉ = −5.9, one-sided
  p = 1.1e-4**. It is negative in 10/10 runs (−0.003 … −0.038).
- **⟨r̃⟩ arm:** mean Δ⟨r̃⟩ = −0.0021, SE 0.00056, t₉ = −3.8, p = 0.002.
  - Addendum S2 noted this arm is underpowered: a −0.02 q residual predicts only ≈ −0.003 in ⟨r̃⟩. It reached −3 SE
    anyway.
- By the registered rule (either arm ≤ −3 SE), the verdict is **FINDING_CANDIDATE**.
- **Addendum S2 requires reading it together with the calibrator-fidelity test (running at 07:20).** If that reads
  CALIBRATOR_SHORTFALL, the joint reading is "not established".

### QK-product symmetry discriminator (Addendum S3 item 3; labelled descriptive; stage3_qkprod_drift.py)
> **READING WITHDRAWN (S4):** a realistic density alone moves q by ~−0.12 under a true β = 1, more than this product
> Δq; with no density calibrator for products, "concerns the function" is uninterpretable. Numbers kept as measured.
- The per-head non-rotary product W_Q,nrᵀ·W_K,nr (invariant under the QK symmetry) vs a product witness (q 0.998 ±
  0.012, ⟨r̃⟩ 0.5309 ± 0.0024).
- Δq at step 0: −0.031 … +0.021 across the 10 runs. At 143k: −0.070, −0.078, −0.069, −0.076, −0.074, −0.085, −0.072,
  −0.045, −0.065, −0.078 (std, s1 … s9). Δ⟨r̃⟩ at 143k: −0.006 … +0.005.
- **Descriptive reading (as registered):** the late q drift appears in the symmetry-INVARIANT product in all 10 runs,
  at a similar magnitude to Q alone (−0.045 … −0.085 vs −0.049 … −0.103). So it concerns the function, not where
  training left each seed along the QK symmetry.
- Caveat: no density-matched calibrator was run for the product spectra. Like the Q drift, part of the product drift
  may be the same unfolding bias on non-MP densities. This check separates symmetry from function, not artefact from
  signal.

### Calibrator-fidelity test (stage3_calib_fidelity.py, frozen in Addendum S2) — registered verdict: INCONCLUSIVE
- Residual (observed − density-matched q) by within-run quartile of per-head calibrator mismatch (KS of each head's λ
  against its fitted mixture), mean over 10 runs:
  - **Q1 (best-matched) +0.0294 (SE 0.0046, t₉ = +6.4)**; Q2 −0.0084; Q3 −0.0328; **Q4 (worst) −0.0684**.
  - Spearman(quartile, residual) = −1.0. Every run shows the same ordering (e.g. seed 9: +0.030 / −0.027 / −0.053 /
    −0.051).
- **Registered verdict: INCONCLUSIVE.**
  - CALIBRATOR_SHORTFALL needs |t(Q1)| < 1, i.e. residual ≈ 0 where the calibrator fits best. Here the residual is
    significantly POSITIVE: the calibrator over-predicts the drift for well-fit heads.
  - RESIDUAL_NOT_FIDELITY needs t(Q1) ≤ −2; not met.
- **Registered joint reading (Addendum S2):** drift test FINDING_CANDIDATE with fidelity INCONCLUSIVE. Not relabelled.
- **Descriptive reading (not a test):** the residual depends perfectly monotonically on calibrator mismatch and
  reverses sign at the best fidelity. The negative pooled residual is carried entirely by the heads the Gaussian-
  mixture calibrator fits worst. That is the signature of a calibrator-fidelity artefact rather than a signal in
  per-head Q. The pre-registered rule did not anticipate a sign reversal (it expected Q1 ≈ 0), so it cannot call it.
- **Resolution path:** a higher-fidelity calibrator, pre-registered before it runs (Addendum S4), with the frozen drift
  thresholds re-applied to its residual.

### ADDENDUM S4 — known-answer calibrator licence + re-score (stage3_calib_v2.py; frozen 18804ca, note 746d130, A1 7cfb66e)
Registered verdict: **QUIET ON THE LICENSED ARM ONLY (q arm NOT RESOLVABLE; not UNFOLDING-EXPLAINED).** The S1/S2
verdicts (drift FINDING_CANDIDATE, fidelity INCONCLUSIVE) stand as sealed; S4 is a separately labelled re-score.
CHECKRUN stage3_calib_v2.py EXIT=0 PASS.

**1. Known answer** (R = 100 paired pools × 384 heads per truth family; truths = the real 410M per-head-Q shapes,
smoothed at c = 2).
- **Planted effect:** −0.050 (T_lam) and −0.052 (T_log) in q; −0.0061 / −0.0063 in ⟨r̃⟩ (larger than intended; see
  the S4 note). EVERY calibrator recovers it at 0.99–1.01, so none absorbs a real effect. Their failures are bias.

| calibrator | q bias, T_lam | q bias, T_log | ⟨r̃⟩ bias, T_lam | ⟨r̃⟩ bias, T_log | licensed |
|---|---|---|---|---|---|
| **v1 (frozen mixture)** | **−0.0207 ± 0.0004** | −0.0164 ± 0.0007 (CONDITIONAL: refused 43/100) | −0.00084 | −0.00066 | — |
| v2_c4 (λ-KDE) | +0.0119 | +0.0104 | +0.00057 | +0.00009 | — |
| v2_c8 | +0.0173 | +0.0166 | +0.00024 | −0.00009 | ⟨r̃⟩ |
| v2_c16 | +0.0184 | +0.0180 | +0.00013 | −0.00022 | **⟨r̃⟩ (selected)** |
| v3_c4 (log-λ KDE) | +0.0059 | +0.0056 | +0.00068 | +0.00027 | — |
| v3_c8 | +0.0229 | +0.0224 | +0.00114 | +0.00074 | — |
| v3_c16 | +0.0541 | +0.0546 | +0.00284 | +0.00228 | — |

(bias = the residual the calibrator manufactures when the truth is exactly β = 1; SE ≈ 0.0002 in q, 0.00003 in ⟨r̃⟩.)

- **The frozen calibrator v1 manufactures a q residual of −0.0207 (T_lam) / −0.0164 (T_log) on spectra whose true
  residual is 0.** The observed 10-run residual was −0.0197. As a known-answer measurement, the q-arm
  FINDING_CANDIDATE is v1's own bias.
- **No q calibrator is licensed.** The best, v3_c4, is off by +0.006 (tolerance 0.005). Across the calibrators the bias
  spans −0.02 to +0.05 depending on smoothing. At N = 64 per head, per-head q cannot resolve an effect of about 0.02
  with any calibrator tested, so the q arm is **NOT RESOLVABLE**.

**2. Regression gate:** PASS. v1 through the new code reproduces the frozen per-run residuals within 0.003 on every
run (tolerance 0.012).

**3. Re-score, ⟨r̃⟩ arm (licensed v2_c16):** residual **−0.00086, SE 0.00054, t₉ = −1.6, one-sided p = 0.072**; 0
refused draws.
- The sealed raw Δ⟨r̃⟩ (vs the Gaussian witness) was −0.0021, t₉ = −3.8. Against a licensed density-matched
  calibrator it is quiet.

**4. Descriptive only (no verdict read from these).**
- **Real q residual by calibrator (mean over 10 runs, t₉):**
  - v1: −0.0172 (−5.1).
  - v2_c4 / c8 / c16: +0.0224 (+7.9) / +0.0287 (+9.3) / +0.0334 (+10.4).
  - v3_c4 / c8 / c16: +0.0165 (+6.1) / +0.0346 (+12.4) / +0.0646 (+22.2).
- **The sign of the "drift" is set by the calibrator.**
- **POST-HOC: real residual minus each calibrator's known-answer bias.**
  - v1: +0.0035 (T_lam) / −0.0008 (T_log).
  - Every KDE calibrator: +0.010 to +0.015.
  - No calibrator, bias-corrected, gives a negative residual.
  - The spread of about 0.01 between v1 and the KDE family is a measure of how imperfectly the smoothed truth
    families stand in for the real heads.
- **Consequence for the QK-product discriminator (above):** the known-answer null pools show that a realistic trained
  density alone moves kde(4) q from ~1.00 (the Gaussian witness) to ~0.88 under a TRUE β = 1. That is larger than the
  product Δq (−0.045 … −0.085), which was measured against a Gaussian-product witness with no density calibrator.
  **The product reading "concerns the function" is withdrawn as uninterpretable.** It never separated artefact from
  signal (its own caveat), and S4 shows the artefact is large enough to explain all of it.

**Joint reading (all registered verdicts, none relabelled).**
- S1/S2 drift test: FINDING_CANDIDATE.
- S2 fidelity: INCONCLUSIVE.
- S4: q arm NOT RESOLVABLE, ⟨r̃⟩ arm quiet under a licensed calibrator.
- **Plain statement: a late-training per-head-Q departure from β = 1 is NOT established.** The q-arm evidence was the
  frozen calibrator's own bias, measured by known answer at the observed size and sign. The ⟨r̃⟩ arm is quiet once the
  density is calibrated. The sealed bulk null (HOLDS in all 10 runs) is unaffected.

**Protocol-template notes (forward).**
- (i) Every density-matched calibrator must pass a known-answer licence on realistic shapes BEFORE its residual is read.
  Good fit (KS) is not fidelity, and a Gaussian mixture on a positive variable leaks mass below 0.
- (ii) At N ≈ 64 levels per spectrum, short-range q is calibrator-limited at about ±0.02. Use ⟨r̃⟩ (licensable to
  ±0.0005) for per-head work.
- (iii) Dry-run every refusal branch of a frozen rule at seal time (the A1 crash).
