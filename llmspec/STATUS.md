# llmspec STATUS (brief v1.1 + Arm B) — updated 2026-09-30 (merge into main)

**Read NOTES.md first**: it is the full state file (mandate, machine rules, code map, results with commits, queue,
lessons). This file is the short version. There is no fixed end time (Will, 09-26 04:50). No alarm set (B4 cron 6c2c8221 deleted 09-29 22:55,
chain complete). Interrupt: `touch llmspec/STOP`.

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
  - Frozen drift test (S1/S2): FINDING_CANDIDATE as sealed; calibrator fidelity (S2): INCONCLUSIVE as sealed.
  - **Addendum S4 (known-answer calibrator licence): the frozen calibrator manufactures q −0.0207 / −0.0164 under a
    true β = 1 (the observed residual was −0.0197). q arm NOT RESOLVABLE (no calibrator within ±0.005 at N = 64);
    ⟨r̃⟩ arm quiet under the licensed v2_c16 (−0.00086, t₉ −1.6), with power against the claimed size (S4-sup).
    The per-head-Q drift is NOT established.**
  - QK-product "function" reading WITHDRAWN (a realistic density alone moves q by ~0.12 under β = 1).

## Arm B — B4 COMPLETE (09-29 22:29): see armb/ARMB_FINDINGS.md
- All 5 arms trained; A0 PASSED B-G1 at all 14 steps. Seal check OK (19 files). CHECKRUN b4_analyze.py EXIT=0 PASS.
- **Q1:** NO SIMPLE ANCHOR (TP_O and TP_MLPOUT; rests on A2, NSA licensed). The best map (LR_INT) misfits by ~2.3% RMS.
- **Q2:** A0 event pairs SIMULTANEOUS AT THIS RESOLUTION. Wave: OPPOSITE ORDER (p_lower 0.0052), carried by layer 0.
- **Q3:** A0 INCONCLUSIVE (Q/K low-rank early, V/O/MLP not).
- **Q4:** 123/368 cells OPTIMIZER-DIFFERENT. Muon: higher Q/K/MLP stable rank, lower top σ.
- **Bulk:** sealed FINDING_CANDIDATE PRESENT in all 5 arms, status NOT ESTABLISHED. 76/9210 VIOLATED (0.83%) against
  a 1.29% null exceedance rate; the sealed per-cell rule has no multiplicity correction.

## 09-30
- Arm B final form agreed with Will (ARMB_FINDINGS §0).
- FINDINGS_MEMO critique fixes #1, #3 and #11 done, plus Open leads; G2c closed #11 as neither-supports-nor-contradicts.
- Seed-1 identity check (A9): INCONCLUSIVE as sealed (C2 was a dead arm; T separated cleanly from the standard order).
  Q4 stands with the pairing caveat. The alignment follow-up was declined; no A10 exists.
- Zoo seating of the G7 classes: DEFERRED explicitly (FINDINGS_MEMO §5).
- llm-spectra merged into main (--no-ff). Will pushes to the Forgejo + GitHub, with a Zenodo snapshot of the merge commit.
- Nothing running.

## Held
- OLMo stage-1 trajectory (Will's call).
