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
