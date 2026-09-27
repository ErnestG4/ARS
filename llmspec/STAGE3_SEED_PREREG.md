# Seed-leg pre-registration — PolyPythias 410M (brief v1.1 §2 / G3 seeds)

Committed BEFORE any seed statistic. Runs after the G3 size replication (STAGE3_REPL_PREREG.md).

## Substrate
- EleutherAI/pythia-410m-seed1 … seed9 (PolyPythias; each seed changes both initialisation and data order), plus the
  standard EleutherAI/pythia-410m as a 10th seed.
- Same architecture, config and schedule (26 revisions) as 410M.
- Weights exist only as pytorch_model.bin, read via CkptBin. It is verified bit-identical to the safetensors path
  (verify_bin_path.py, 6ca5be1).

## Witness reuse (declared)
- The G1 pooled-null witness depends on the entry scale only through fp16 rounding, and was shown scale-invariant
  (step 0 vs final scales, every type).
- Seeds therefore reuse the pythia-410m witness (LLMSPEC_WITNESS=pythia-410m).
- **Declared check:** each seed's mean entry rms per type at step 0 and step 143000 must lie within ±20% of the
  pythia-410m witness scales. A seed that fails gets its own witness before its null is read.

## Pre-registered readings
- **A. Sealed null per seed:** unchanged (bulk |Δ⟨r̃⟩| ≤ 0.010 and |Δq| ≤ 0.10 in all 260 cells). Prediction: HOLDS for
  every seed. Report the count of seeds with any VIOLATED cell, each with the gate-first ladder.
- **B. R1–R6 per seed:** exact criteria from STAGE3_REPL_PREREG.md. For each R, report "k of 10 seeds REPLICATE".
  - An R is SEED-ROBUST iff ≥ 9/10 replicate.
  - It is SEED-DEPENDENT iff 2–8/10.
  - It is NOT SUPPORTED iff ≤ 1/10.
- **C. Seed spread** of the key numbers (R1 rotary mass, R3 ratios, R5 interval, sealed-null worst deviations): report
  median and range over seeds. No test.

## Cost (for scheduling)
- Per seed: 26 × ~2.5 min extraction, 10 equal-interval pairs, one analysis (~40 min CPU), scoring.
- About 2 h per seed; ~18 h for all nine. They run sequentially, one seed at a time, each resumable.

## ADDENDUM S1 — committed 2026-09-26 ~17:45, BEFORE seed 4's statistics exist (seeds 1–3 and standard 410M are already analysed)
Written because the per-head-Q late-training q drift is now known: Δq at 143k is −0.089 / −0.103 / −0.091 / −0.065
(standard, s1, s2, s3), systematic and directional, and it sits near the sealed 0.10 tolerance that was fixed before it
was known. Nothing below changes a tolerance or a verdict. It fixes in advance how the remaining seeds are READ.
1. **A crossing is a crossing.** A per-head cell with |Δq| > 0.10 is VIOLATED under reading A (the sealed null),
   mechanically, exactly as registered.
   - It then goes through the registered gate-first ladder (stage3_ladder.py runs automatically) and gets that
     ladder's label.
   - Being "the known drift" is a descriptive annotation printed next to the label. It is NEVER a relabel.
2. **Crossings do not touch R1–R6.** The six replication criteria (reading B) are separate readings with their own
   registered rules. A reading-A crossing is not counted as an R-failure.
3. **Descriptive flag, per run:** the per-head-Q drift is reported for every run as Δq and Δ⟨r̃⟩ at 143k and along the
   trajectory, next to the reading-A verdict. The summary line for a run with no VIOLATED cell reads "HOLDS (per-head-Q
   drift flagged: Δq = …)", never a bare "HOLDS".
4. **Pre-registered noise-scaled test of the drift, run once all 10 runs are in** (stage3_drift_test.py, to be
   committed before it is run):
   - For each run, at per-head Q, 143k:
     - residual_q = Δq_obs − Δq_density, where Δq_density comes from the density-matched COE witness (ladder step 2,
       R = 10);
     - Δ⟨r̃⟩_obs, where ⟨r̃⟩ needs no unfolding.
   - The drift is **UNFOLDING-EXPLAINED** iff mean residual_q over the 10 runs is within ±3 SE of 0 AND mean Δ⟨r̃⟩ is
     within ±3 SE of 0.
   - It is a **FINDING_CANDIDATE** (a first crack in the bulk null at the ~0.1-in-q level) iff mean residual_q < 0 at
     ≥ 3 SE, OR mean Δ⟨r̃⟩ < 0 at ≥ 3 SE.
   - SE = SD over runs / √10. Either outcome goes to the calibrator zoo: a documented unfolding bias for trained-Q
     density shapes, or a candidate. The ladder is also run on the three already-analysed runs, so all 10 have
     Δq_density.
5. **R1 / R3 reporting:** verdicts come mechanically from the registered seed counts. The ten-run spread (median,
   range) of both R1 numbers (rotary mass, rotary-row norm share) and of every R3 ratio is reported alongside, because
   both criteria straddle their bars.

## ADDENDUM S2 — committed 2026-09-26 ~19:30, BEFORE seed 5's statistics (review round 4)
1. **The ⟨r̃⟩ arm of the drift test is underpowered for the residual, so read it that way.**
   - Linearising the Brody interpolation, d⟨r̃⟩/dq ≈ (0.531 − 0.386)/1 ≈ 0.145. A q residual of −0.023 predicts
     Δ⟨r̃⟩ ≈ −0.003, inside the observed −0.006 … +0.0002.
   - ⟨r̃⟩ can rule out the FULL q drift (−0.085 → ≈ −0.012) being real, but cannot confirm or exclude the residual.
   - Only the q arm can realistically deliver FINDING_CANDIDATE. A quiet ⟨r̃⟩ is NOT counter-evidence against the
     residual.
2. **The statistic is a t, not a z.** SE comes from the spread over runs, so mean/SE ~ t with n − 1 degrees of freedom.
   - At n = 10 the frozen −3 SE threshold is t₉ = −3, one-sided p ≈ 0.0075. The verdict line prints t, df and p.
   - The interim value at n = 4 was t₃ = −3.8, one-sided p ≈ 0.016, not the "z −3.8" first written.
   - The thresholds are unchanged; only the reporting is corrected.
3. **Calibrator-fidelity test** (stage3_calib_fidelity.py, frozen by this commit, run at n = 10 next to the drift
   test). The residual could be the calibrator matching trained densities imperfectly (smoothing them, so reproducing
   less unfolding bias) rather than a signal.
   - Per head (per-head Q, step 143k, each run): mismatch = KS distance between the head's real λ values and its
     fitted mixture CDF (the calibrator's density).
   - Heads are split into mismatch quartiles within each run. Per quartile, q_obs and q_density are computed on the
     quartile's heads (density-matched COE, R = 10), giving residual(quartile).
   - **CALIBRATOR_SHORTFALL** iff the lowest-mismatch quartile's residual, averaged over runs, is within 1 SE of 0 AND
     the residual grows in magnitude with mismatch (Spearman over the four quartile means ≤ −0.8).
   - **RESIDUAL_NOT_FIDELITY** iff the lowest-mismatch quartile's residual is ≤ −2 SE.
   - Otherwise **INCONCLUSIVE**. SE = SD over runs / √n (a t with n − 1 df, reported as such).
   - The drift test's verdict is reported only together with this one: FINDING_CANDIDATE AND CALIBRATOR_SHORTFALL
     reads as "not established".
4. **Step-0 excess variance** is being diagnosed (review point 3). Its outcome feeds the noise model reported with the
   verdict, but does NOT change the frozen SE (the empirical between-run SD).

## ADDENDUM S3 — committed 2026-09-27 ~01:00, BEFORE any dedicated-witness re-analysis exists (no own-witness file
## for any seed yet; the GPU queue is still on seed 8 extraction)
1. **Which version counts (fixed now).** For every seed that fails the witness-reuse scale check (3, 4, 5, 9; 8 if it
   fails):
   - The ORIGINAL reading-A and R6 results stay in the log, labelled **"computed against invalid reused witness"**.
   - The **dedicated-witness re-analysis is the PRIMARY result.**
   - Seeds that pass the check (1, 2, 6, 7 and standard) keep the reused-witness results as primary.
2. **Inputs to the frozen tests (fixed now).** stage3_drift_test.py and stage3_calib_fidelity.py take every affected
   seed's inputs from the re-analysed version:
   - the ladder entries for those seeds are purged and recomputed against the dedicated witness (already queued:
     stage3_ladder_purge.py → stage3_ladder_all.py);
   - the drift test recomputes any missing head_Q@143k entry on demand;
   - both frozen tests run after every re-analysis in the CPU queue.
3. **Symmetry discriminator for the per-head-Q drift** (a LABELLED DESCRIPTIVE check next to the frozen test, not a
   change to it).
   - Pythia's QK path is invariant under W_Q → A·W_Q, W_K → A⁻ᵀ·W_K for any invertible A on the non-rotary dims. So
     per-head Q spectra need not be invariant between function-identical models; the non-rotary product
     W_Q,nrᵀ·W_K,nr is.
   - The same drift measurement (bulk ⟨r̃⟩ and q through s3stats, vs a product-matched witness built from independent
     Gaussian factors) is run on per-head non-rotary QK-product spectra at step 0 and 143k for all 10 runs.
   - Reading (descriptive): drift present in the product ⇒ it concerns the function; drift only in Q alone ⇒ it
     concerns where training left each seed along the QK symmetry.
4. **Protocol-template notes (forward only; nothing here is applied retroactively to this study):**
   - **G0:** estimate thresholds from enough draws that their own error is small, and set G0's error rate for the
     whole family of tests (e.g. per model), not per test. This is the second false G0 fail from a bare rate bar.
   - **Witness scale matching:** whether anything in the witness depends on absolute scale is tested and recorded
     (stage3_witness_scale_test). The pre-registered ±20% rule still runs as written here.
