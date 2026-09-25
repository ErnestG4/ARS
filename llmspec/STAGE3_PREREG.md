# Stage 3 pre-registration — Pythia-1.4B trajectory (brief v1.1 aims 2–6)

Sealed by commit BEFORE any Stage 3 statistic is computed on real weights. Raw-object extraction
(stage3_extract.py) may run before the seal: it chooses no statistic.

## Substrate and schedule
- Pythia-1.4B (`EleutherAI/pythia-1.4b`), 26 revisions in `pythia_1.4b_schedule.txt`:
  0, 1, 2, 4, …, 512, 1k, 2k, 3k, 4k, 6k, 8k, 12k, 16k, 24k, 32k, 48k, 64k, 96k, 128k, 143k.
- Stored values are fp16 upcasts (G4 audit: 100% on the fp16 grid), so the unit roundoff is u = 2^-11.
- Matrix types, per layer: Q, K, V, O (2048×2048 full); MLP_IN (8192×2048); MLP_OUT (2048×8192).
  Per-head units (128×2048): Q, K, V, O.

## Bands (by RANK, so the definition does not move with a fitted edge)
Levels are sorted ascending, and the rank quantile is q = i/n.
- LOWER = [0.01, 0.10)
- BULK = [0.10, 0.90)
- UPPER = [0.90, 0.99)
- The top and bottom 1% are excluded from local statistics; they are covered by the edge/outlier counts.
- Per-head spectra use the same quantiles on 128 levels.

## Local statistics (per band × matrix type × unit × checkpoint)
- **Pooling rule.** Spacings are formed within each spectrum. The pool is then taken over the 24 layers
  (full unit) or 384 heads (per-head unit). Raw eigenvalues are never pooled across spectra.
- **⟨r̃⟩ (PRIMARY).** Mean of min(r, 1/r) over consecutive spacing ratios of the raw λ = σ² within the band.
  No unfolding.
- **Brody q (SECONDARY).** `cross_substrate.axes.I8_brody_q_unbounded` on unfolded spacings.
  - Unfolding = kde(c=4): a Gaussian-CDF staircase with per-level bandwidth 4 × the local spacing, exactly as in
    stage2_g7.unfold. It passed the unimodal control in the G7 dry run.
  - local(w=5) is reported alongside.
  - A setting with more than 0.1% non-positive spacings is refused.
- **Σ²(L) and Δ₃(L), L ∈ {1, 2, 5, 10}.** Bulk only, averaged per spectrum then over the pool. REPORTED, not
  part of the sealed null.
  - **PRE-DATA AMENDMENT A0 (2026-09-25, before any real Stage 3 statistic):** the long-range unfolding is kde(32),
    not kde(4). kde(4) absorbs fluctuations on scales ≳ 4 spacings: Poisson Σ²(10) read 1.2 instead of 10.
  - kde(32) recovers Wishart Σ² to within 15% of GOE on both shapes. Its known bias: Poisson reads ~27% low at
    L = 10.
  - Δ₃ is unfolding-insensitive and is the more robust long-range reading.
  - Known-answer checks: verify_s3stats.py (red-pathed). All statistics come from ONE module, s3stats.py, used by
    the witnesses and the real data alike.

## G1 pooled-null witness (the reference for every local statistic)
- For each matrix type and unit, generate independent Gaussian matrices of IDENTICAL shape and number.
  Scale them to the real matrix's rms, then round them to the fp16 grid, so G4 is inside the witness.
- Run the IDENTICAL pipeline (bands, unfolding, pooling) with R = 20 replicate pools.
- The witness must read β=1, not Poisson:
  - bulk ⟨r̃⟩ within 0.01 of the fp64 no-rounding witness;
  - bulk ⟨r̃⟩ at least 0.10 above the Poisson value 0.386.
- **Entry-shuffle witness.** Permute each real matrix's entries at steps 0, 1000, 8000, 64000 and 143000, all
  layers. The pipeline must return the same verdict as the Gaussian witness within the tolerances below.

## G0 calibration at step 0
- For every matrix type:
  - MP check: pooled KS distance of σ/s to the MP law with c = min/max shape, at scale s = entry rms. It must be
    ≤ the 95th percentile of the same KS over 200 matched Gaussian draws.
  - β=1 check: the bulk null below HOLDS.
- A G0 failure halts Stage 3 interpretation. The pipeline is suspected first.

## SEALED NULL (aim 6, adopted by Will as a pre-registered instrument check)
- **Criterion.** At every checkpoint, for every matrix type and both units, the BULK band satisfies both:
  - |⟨r̃⟩_real − ⟨r̃⟩_witness| ≤ 0.010;
  - |q_real − q_witness| ≤ 0.10.
  Here "witness" means the replicate mean of the G1 witness for that matrix type, unit and checkpoint scale.
- **Verdict per cell:** HOLDS or VIOLATED. The prediction is HOLDS in all 26 × (6 + 4) = 260 cells.
- **On any VIOLATED cell, suspect the gate first, in this order:**
  1. G0 at step 0 for that type.
  2. A density-matched witness: COE mapped onto that cell's own empirical bulk density (stage2_g7 machinery,
     kde(4) unfolding). If it reproduces the deviation within the same tolerance, the cell is labelled
     DENSITY_ARTIFACT, not β≠1.
  3. The precision floor (below).
  Only a violation that survives all three is a FINDING_CANDIDATE.
- The same tolerances are reported for LOWER and UPPER bands, labelled descriptive (not sealed).

## G4 precision (before any small-σ statement)
- For each shape, draw fp64 Gaussian matrices at the real rms (step 0 and step 143000). Compare fp64 against
  fp16-rounded.
- A LOWER-band result is trusted for a type only if rounding changes both of:
  - lower-band ⟨r̃⟩ by < 0.002;
  - the median of the lowest-1% σ by < 1%.
- Otherwise every lower-band statement for that type carries PRECISION_LIMITED.
- Expected problem case: for square matrices the smallest σ are ~rms × 0.02, which is below the fp16 noise
  floor u · rms · (√m + √n) ≈ 0.044 rms.

## Global estimators (G6: an estimator's name is part of the value)
- Stable rank = ‖W‖_F² / σ_max².
- Spectral entropy = −Σ p ln p / ln n, with p = σ²/Σσ².
- **MP fit** (`mp_fit_v1`):
  - Start from s = rms(W). Permuting entries preserves rms, so the shuffled matrix is MP at scale s.
  - E± = s(√m ± √n).
  - τ+ = 99th percentile of σ_max/E+ over 200 matched fp16-rounded Gaussian draws; τ− = 1st percentile of
    σ_min/E− (rectangular only).
  - Outliers: σ > τ+·E+. Rescale s² = (‖W‖_F² − Σ_outliers σ²)/(mn) and iterate to a fixed point.
  - Report: upper outlier count; for rectangular matrices, the lower departure count σ < τ−·E−.
  - For square matrices (E− = 0): report the KS distance of the lowest 10% of σ/s against the matched null.
- **MLE α** (`htsr_mle_v1`, Clauset):
  - Fit on eigenvalues λ = σ². x_min is chosen from the top half of λ by minimum KS distance D, with
    n_tail ≥ 50.
  - α = 1 + n_tail / Σ ln(λ/x_min).
  - Semi-parametric bootstrap p with 100 replicates. α is QUOTED only if p ≥ 0.1; otherwise the output is
    "power-law fit fails" and only D is reported.
- **Rank-slope α** (`liu_rankslope_v1`): OLS slope of log σ_i vs log i over the top 20%. Always labelled as
  such and never compared with the MLE α.

## Vectors, circuits, motion (descriptive; estimators fixed here)
- **Vectors:** per-vector IPR = Σu⁴ and Porter–Thomas KS (√n·u vs N(0,1)), summarised by band. Top-k principal
  angles (k = 1, 4, 8, 16, 32) against the previous schedule checkpoint and against step 143000.
- **Circuits:** as in stage3_extract.py.
  - LayerNorm gains are folded in; centering and biases are ignored (declared).
  - Copying score = Σλ/Σ|λ| over eig(V diag(g1) W_Eᵀ W_U diag(g_f) O) (Elhage), plus the fraction with Re λ > 0.
  - QK: symmetric-energy fraction on the non-rotary dims 32–127. The full-dims version is flagged as
    rotary-contaminated.
  - Null: eigenvalues of the product of two independent real Gaussian matrices of matched shapes; step 0 is the
    empirical null.
- **Motion:** ΔW between consecutive schedule checkpoints. Report the stable rank of ΔW and ‖U32ᵀΔW‖² / ‖ΔW‖².

## Events
- **Probe set** (fixed; its sha256 is recorded at first use):
  - 64 documents from `NeelNanda/pile-10k`, first 512 tokens each. This is a training-distribution proxy and
    may have been seen in training (flagged).
  - One repeated-random-token set: 32 sequences of 2 × 256 tokens, uniform over ids 1000–49999, seed
    20260925.
- **Loss:** mean next-token loss on the text probes.
- **Induction:** per head, the mean attention from second-half position i to position i − 255, and the
  second-half loss on the repeated sequences.
- **Sink:**
  - Per head, the mean attention to position 0 over query positions ≥ 16 on the text probes.
  - Sink fraction = fraction of heads with that value > 0.5.
  - The mean itself is also reported.
- **Change points:** binary segmentation on each metric vs log10(step) for steps ≥ 1, with a piecewise-linear
  model, minimum segment of 3 checkpoints, and a BIC penalty. With 25 points, change points are coarse; the
  output is reported as a checkpoint interval.
