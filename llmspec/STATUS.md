# llmspec STATUS (brief v1.1) — updated 2026-09-25 23:47 PDT

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

## Stage 3 done → STAGE3_FINDINGS.md (4ff09ee, da8d0bc, 9367aee)
- **Sealed bulk null HOLDS in 260/260 cells** (worst |Δ⟨r̃⟩| 0.004, |Δq| 0.034). G0 passes. The witness reads β=1.
- **Descriptive:**
  - O/MLP_OUT outliers detach first (peak ~2k steps); Q/K later; V last.
  - O/MLP_OUT stable rank rebounds after 2k.
  - Q/K/V upper vectors localise from 2k–8k.
  - ΔW is low-rank early and high-rank late.
  - The OV departure from product-Ginibre (by 512) precedes QK (1000–2000).
  - Induction forms at 512–1000; first sink head at 48k–64k.
- **Not resolved:** Liu's wave (schedule too coarse). The square lower-edge rise is NOT precision-limited (Weyl bound).

## Running
- **G2** (stage3_g2.py): the identity control passes (Δloss +0.0000). **bulk:1 gave Δloss +2.66 nats**, NOT
  Diffract's "bulk permutation harmless". Our bulk = ranks 10–90%, permuted in all 144 matrices at once; Diffract's
  definition and scope may differ, so check commensurability before calling it a non-replication. ETA ~01:05.
- **Then queue7** (post-hoc, declared): dense-V extraction (5k–15k, 8 revisions) + stage3_wave.py.

## Next
0. Chained after queue5: G2 functional witness (stage3_g2.py, pre-registered 0970140): Diffract replication
   (bulk σ-permutation inert, full catastrophic?) with an identity control.
1. When queue4 finishes: stage3_analyze.py, then STAGE3_FINDINGS.md (sealed-null table first; G0/G1/G4; nulls
   reported as nulls).
2. G7 result → STAGE2_FINDINGS.md (licensed or NOT LICENSED for local statistics on peaked spectra).
3. Motion pass (ΔW between consecutive revisions, streamed per layer).
- Held: Arm B (Will). OLMo stage-1 trajectory (Will's call).
