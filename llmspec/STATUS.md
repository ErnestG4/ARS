# llmspec STATUS (brief v1.1) — updated 2026-09-26 23:50 PDT

**Read NOTES.md first**: it is the full state file (mandate, machine rules, code map, results with commits, queue,
lessons). This file is the short version. There is no fixed end time (Will, 09-26 04:50). The alarm cron runs every
30 min. Interrupt: `touch llmspec/STOP`.

## Where things stand
- **Stage 1** (existence): the sealed KDE rule was non-evidence. The licensed dip test finds OLMo Q/K multimodality at
  stage-1 end and none in Pythia. Aim 1 deferred (the OLMo stage-1 trajectory is Will's call).
- **Stage 2** (G7): NOT LICENSED as registered (fails β=2). Raw ⟨r̃⟩ licensed.
- **Stage 3** (Pythia-1.4B): sealed bulk null HOLDS 260/260. Two review rounds hardened or retracted the
  descriptives. G2/G2b: the bulk-shuffle cost is size-dominated. Equal-interval ΔW rank rises at constant LR. Change
  points not licensed.
- **G3 size replication:** 1B and 410M null HOLDS 260/260 each. R2 / R4 / R5 / R6 size-general. R1 fails at 410M
  (norm clause). R3 fails at 1B and 410M (the OV path rises less).
- **Seed leg** (410M × 10 runs):
  - Standard 410M and seeds 1–6 are analysed. Seeds 1 and 6 each have one VIOLATED per-head-Q cell → ladder →
    DENSITY_ARTIFACT (the known drift).
  - The per-head-Q drift is under a frozen 10-run test (Addenda S1 / S2) plus a calibrator-fidelity test.
  - **The witness-reuse scale check failed for seeds 3, 4, 5, 9**, so their reading A is provisional and they are
    re-run against their own witnesses (queued).

## Running (auto)
- **GPU queue** (queue_seeds.txt): seed 7 motion → seed 8 extract + motion → scalecheck → witness gates 9, 8, 3, 4, 5.
- **CPU queue** (queue_seeds_cpu.txt): seed 7 → seeds 8, 9 (after the witness decision) → re-analysis of 3, 4, 5 →
  drift_test → calib_fidelity.
- memwatch: host-commit guard.

## Held
- Arm B; OLMo stage-1 trajectory (Will's calls).
