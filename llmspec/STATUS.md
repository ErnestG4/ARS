# llmspec STATUS (brief v1.1) — updated 2026-09-25 21:26 PDT

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

## Early Stage 3 (two anchors; results/stage3_*_early.*)
- G0 MP passes for all six types.
- Sealed bulk null HOLDS in 20/20 cells (step 0 and step 143000): max |Δ⟨r̃⟩| 0.0026, max |Δq| 0.025.
- Witness: all 10 types read β=1 and are scale-invariant. Sealed G4 flags the lower band as PRECISION_LIMITED for
  K, V and MLP_IN (fp16 effect 0.0024–0.0042 > 0.002). That rule has no sampling allowance, and the replicate
  spread is of similar size; report both.
- Amendment A1 (113089b): mp_fit_v1 collapses on non-MP bulks and is flagged DEGENERATE; mp_fit_v2
  (median-matched) added.

## Running
- All 26 Pythia-1.4B revisions are extracted (21:05).
- Induction forms between step 512 and step 1000: max induction 0.01 → 0.91, rep-loss 12.8 → 3.6. There are no
  checkpoints in between.
- The first sink head appears by step 64000.
- supervise.sh queue5 → queue6: motion pass (~105 s/pair after the Gram σ_max fix, 893b4e0; ETA ~22:05), then
  stage3_analyze, then G2 (~1.5 h). Everything should finish ~01:30.
- **Speed-ups tonight** (all byte-identical or verified):
  - fetch_many streams at ~70 MB/s vs 19 (de19821).
  - Motion σ_max via Gram (893b4e0).
- **Host:** Will added a 64 GB pagefile on a secondary NVMe, so host free commit is now ~71 GB (no reboot needed so
  far). resume.sh = a one-command resume after any reboot.

## Next
0. Chained after queue5: G2 functional witness (stage3_g2.py, pre-registered 0970140): Diffract replication
   (bulk σ-permutation inert, full catastrophic?) with an identity control.
1. When queue4 finishes: stage3_analyze.py, then STAGE3_FINDINGS.md (sealed-null table first; G0/G1/G4; nulls
   reported as nulls).
2. G7 result → STAGE2_FINDINGS.md (licensed or NOT LICENSED for local statistics on peaked spectra).
3. Motion pass (ΔW between consecutive revisions, streamed per layer).
- Held: Arm B (Will). OLMo stage-1 trajectory (Will's call).
