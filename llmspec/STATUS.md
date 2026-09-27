# llmspec STATUS (brief v1.1) — updated 2026-09-27 08:10 PDT

**Read NOTES.md first**: it is the full state file (mandate, machine rules, code map, results with commits, queue,
lessons). This file is the short version. There is no fixed end time (Will, 09-26 04:50). The alarm cron runs every
30 min. Interrupt: `touch llmspec/STOP`.

## Where things stand
- **Stage 1** (existence): the sealed KDE rule was non-evidence. The licensed dip test finds OLMo Q/K multimodality at
  stage-1 end and none in Pythia. Aim 1 deferred (the OLMo stage-1 trajectory is Will's call).
- **Stage 2** (G7): NOT LICENSED as registered (fails β=2). Raw ⟨r̃⟩ licensed.
- **Stage 3** (Pythia-1.4B): sealed bulk null HOLDS 260/260. G2/G2b: the bulk-shuffle cost is size-dominated.
  Equal-interval ΔW rank rises at constant LR. Change points not licensed.
- **G3 size replication:** 1B and 410M null HOLDS 260/260 each. R2 / R4 / R5 / R6 size-general. R1 fails at 410M;
  R3 fails at 1B and 410M.
- **Seed leg** (410M × 10 runs), COMPLETE (c2c635f):
  - Null holds everywhere (2 cells → DENSITY_ARTIFACT).
  - R2 / R4 / R5 / R6 SEED-ROBUST. R1 (2/10) and R3 (4/10) SEED-DEPENDENT, with spreads.
  - **Frozen drift test (S1/S2): FINDING_CANDIDATE** (q residual −0.0197, t₉ −5.9; ⟨r̃⟩ −0.0021, t₉ −3.8).
  - **Calibrator fidelity (S2): INCONCLUSIVE** as registered (8231e0a). The residual is monotone in mismatch with a
    sign reversal, which looks like an artefact, but the rule can't call it.
  - QK-product discriminator: the drift is present in the invariant product in all 10 runs (so it concerns the
    function, not a symmetry).

## Running (auto)
- **Addendum S4** (18804ca, frozen): known-answer licence of calibrators on realistic truth shapes, then a re-score of
  the 10-run drift. `stage3_calib_v2.py` under checkrun (log: stage3_calib_v2.checkrun.log; progress:
  results/stage3_calib_v2_pools.jsonl, 200 pools; resumable).
- memwatch: host-commit guard (PID 12700).

## Held
- Arm B; OLMo stage-1 trajectory (Will's calls).
