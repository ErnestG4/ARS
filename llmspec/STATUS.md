# llmspec STATUS (brief v1.1) — updated 2026-09-25 13:20 PDT

Run window: until 09:00 PDT Sat 2026-09-26, alarm every 30 min (cron `7,37 * * * *`, session-only).
GPU in use (Will). Interrupt: `touch llmspec/STOP`. Resume: `./queue.sh <queue file>` (per-layer / per-checkpoint caches).

## Machine limits (read before launching anything)
- Three WSL crashes on 09-25 (10:59, 12:10, 12:32) = **Windows commit exhaustion**. Windows System log,
  Resource-Exhaustion-Detector 2004: vmmemWSL 20.6 GB. The host has 32 GB RAM + a FIXED 18 GB pagefile, giving a
  49.7 GB commit limit, and Windows apps hold ~30 GB of it. Page cache from downloads and GPU allocations both
  count against vmmemWSL. Will may raise the pagefile maximum (admin + reboot); until then, budget ~10 GB for
  all of WSL.
- **Disk:** `df /` lies (1 TB VHD). What fills is C: (`/mnt/c`). remote_st.check_stop() refuses to proceed below
  10 GB free on C:.
- **Rules now in code:**
  - No checkpoints on disk; everything streams HF → RAM → GPU.
  - fp16 GPU storage (exact) with transient fp32 compute, verified bit-identical (verify_fp32_equivalence.py).
  - 6 GB per-process GPU cap.
  - fsync-durable writes (a crash had left zero-length files behind renames).
  - memwatch.sh logs host free commit every 20 s and writes STOP below 5 GB.

## Done
- Stage 1 peak criterion SEALED (34de628); amendment A1 + estimator v2 (ee83e79).
- G7 pre-registration (b1ca2b6); Stage 3 pre-registration SEALED (0cf53ba); memory-safe extractor + probes
  (8ac8db7).
- G4: Pythia F32 checkpoints are fp16 upcasts; OLMo 2 F32 values are fp32 masters. The brief's "OLMo bf16"
  premise does not hold.
- Stage 1 spectra banked for all 5 runs (7 crash-corrupted files found, removed and regenerated).

## Running
- s1_calibrate_v2check (queue3): seal re-derived under estimator v2.
- s1_analyze_v2b: sealed Stage 1 analysis + A1, with plots.

## Next
1. Read the Stage 1 verdict + plots, then write the Stage 1 findings (nulls as nulls; decision per the sealed
   table).
2. Stage 2 G7 with real targets from the selected substrate.
3. Stage 3: stage3_extract.py over the 26-revision schedule (streaming, one at a time), then the G0/G1/G4
   witnesses and the sealed bulk null.
- Arm B: HELD (Will).
