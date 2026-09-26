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
