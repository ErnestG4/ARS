# llmspec STATUS (brief v1.1) — updated 2026-09-25 14:25 PDT

Run window: until 09:00 PDT Sat 2026-09-26, alarm every 30 min (cron `7,37 * * * *`, session-only).
GPU in use (Will). Interrupt: `touch llmspec/STOP`. Resume: `./queue.sh <queue file>` (per-layer caches).

## Machine limits (read before launching anything)
- The WSL crashes on 09-25 were **Windows commit exhaustion**: 32 GB RAM + a FIXED 18 GB pagefile, with Windows
  apps holding ~30 GB. Page cache and GPU allocations both count against vmmemWSL.
  - To give the GPU swap headroom, Will would raise the pagefile maximum (admin + reboot).
  - Until then, budget ~10 GB for all of WSL.
- **Disk:** `df /` lies. What fills is C: (`/mnt/c`); jobs refuse to proceed below 10 GB free on C:.
- **Rules in code:**
  - Stream HF → RAM → GPU; no checkpoints on disk.
  - fp16 GPU storage with transient exact fp32 compute (verified bit-identical).
  - 6 GB per-process GPU cap (it fired once as a clean OOM — the design working); batch-1 markers.
  - fsync-durable writes.
  - memwatch.sh writes STOP when host free commit < 5 GB.

## Done (commits)
- **Stage 1** (21c0837, 78c2fad).
  - The sealed KDE rule said PEAKS in both models, but that was UNRESOLVED as evidence: it counted tail specks.
  - Stage 1b, the licensed dip test (post-hoc, calibration committed first, d16caaf):
    - Pythia: 0 multimodal heads in any matrix type.
    - OLMo Q/K: multimodal at stage-1 end (Q 24.6% / 13.3% with the dead-row cluster excluded); sub-floor at
      `main` (8.6%).
  - Decision at the final checkpoint: aim 1 deferred. **The OLMo stage-1 trajectory is Will's call.**
  - G0: FAIL-as-sealed on Pythia W_O (rule had no sampling allowance; attributed); the dip G0 passes everywhere.
  - Seal re-derived under estimator v2: identical (eca356d).
- **Stage 3 prereg SEALED** (0cf53ba). Pre-data amendment A0 (long-range unfolding kde(32), 76052ed). Witness
  generator (82ef74b). Analysis + estimator known answers (44b9f77).

## Running
- **queue4 (GPU):**
  - Extract step143000 + step0 (markers at the final checkpoint: loss 2.10, rep-loss 0.28, max induction 0.97).
  - Then stage3_witness (~40 min).
  - Then the other 24 revisions. ~16 min per revision; ETA ~22:00.
- **G7 (CPU, 4 threads):** stage2_g7.py with real targets = 34 OLMo stage-1-end W_Q heads flagged by the dip test
  → results/g7_olmo_stage1end_Q.json.

## Next
1. When queue4 finishes: stage3_analyze.py, then STAGE3_FINDINGS.md (sealed-null table first; G0/G1/G4; nulls
   reported as nulls).
2. G7 result → STAGE2_FINDINGS.md (licensed or NOT LICENSED for local statistics on peaked spectra).
3. Motion pass (ΔW between consecutive revisions, streamed per layer).
- Held: Arm B (Will). OLMo stage-1 trajectory (Will's call).
