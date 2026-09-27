# Arm B — Stage B0 benchmark report (2026-09-27)

Generator: `armb/b0_bench.py`; raw numbers: `results/armb_b0_bench.json`.

**Setup.**
- Device: NVIDIA GeForce RTX 4090 (CUDA hard-asserted); torch 2.11.0+cu130; transformers 5.8.0.
- fp32 master weights, bf16 autocast, sdpa attention.
- Unmodified HF GPTNeoX configs, which match Pythia's released yml files.
- Per-process VRAM cap 80%, because the desktop holds ~3.3 GB.

**Per this stage's rule: report and stop.** Will picks the model size, stop step and arm set (§6 of the brief).

## 1. Throughput (effective batch 1024 × 2048 by gradient accumulation)

| size | params | best micro-batch | eager tok/s | full AdamW step (eager) | peak VRAM (full step) | Muon NS5 overhead / step |
|---|---|---|---|---|---|---|
| 31M | 30.5M | 8 | 242k | **8.1 s** | 10.5 GiB | 0.02 s |
| 70M | 70.4M | 8 | 197k | **12.7 s** | 12.0 GiB | 0.02 s |
| 160M | 162.3M | 4 | 87k | **25.0 s** | 9.7 GiB | 0.04 s |

- **torch.compile (70M):** 267k tok/s, **1.36× eager**, giving about **9 s per step**. Engineering only: the maths is
  unchanged. I'd use it unless you object.
- **Memory is logits-bound.** At micro-batch 8, the fp32 logits are 8 × 2048 × 50,304 × 4 B = 3.3 GB, which is why
  micro-batch 16 runs out of memory even with activation checkpointing. A chunked cross-entropy would free memory,
  but not buy speed. Not needed.
- **Noise:** two benchmark passes differed by ~10% (the desktop shares the GPU). Treat the projections as ±15%.
- **Muon overhead is negligible** (≤ 0.5% of a step) at every size.

## 2. Wall-clock per run (GPU time; checkpoint saves add < 2 min per run)

| size | to step 3000 | to step 5000 |
|---|---|---|
| 31M (eager) | 6.7 h | 11.2 h |
| 70M (eager) | 10.6 h | 17.6 h |
| **70M (compiled)** | **~7.5 h** | **~12.5 h** |
| 160M (eager) | 20.8 h | 34.7 h |

**Arm-set totals, 70M compiled:**

| arm set | runs | to step 3000 | to step 5000 |
|---|---|---|---|
| A0 + A1 + M0 × 2 | 4 | ~30 h | ~50 h |
| + A2 | 5 | ~38 h | ~63 h |

Scheduling: if the runs only get the GPU overnight, that's one run per night at step 3000, and one per night only just
fits at step 5000.

## 3. Disk (full fp32 checkpoints = raw-object banking)
- **Grid as specified, plus Pythia's log-spaced steps,** which B-G1 needs:
  - 0–500 every 10: 51 checkpoints.
  - Plus {1, 2, 4, 8, 16, 32, 64, 128, 256, 512}: 10.
  - 500–3000 every 25: 100.
  - 3000–5000 every 100: 20.
  - Total: 161 checkpoints to step 3000, 181 to step 5000.

| size | fp32 checkpoint | per run to 3000 | per run to 5000 | + Adam state at 10 points |
|---|---|---|---|---|
| 31M | 122 MB | 19.6 GB | 22.1 GB | +2.4 GB |
| 70M | 282 MB | 45.4 GB | 51.0 GB | +5.6 GB |
| 160M | 649 MB | 104.5 GB | 117.5 GB | +13.0 GB |

- **70M, 4 runs:** 182 GB (all to step 3000) / 204 GB (all to step 5000), plus 22 GB of Adam state. **5 runs:**
  227 / 255 GB plus 28 GB.
- **The recommended mix** (A0 to step 5000, the rest to step 3000): 4 runs = 187 GB + 22 GB; with A2, 232 GB + 28 GB.
- **C: cannot hold this.** It has 61 GB free with a 10 GB reserve, so at most one 70M run.
- **D: has 507 GB free** and holds any of these arm sets. It is your drive, so this is your call (decision 4).
  - Not tested: D:'s write speed from WSL (drvfs). Nothing was written to D:.
  - Saves to ext4 take 0.4 s for 70M; drvfs will be slower, but it's a small cost against a 9 s step.
- **Fallback if D: is not approved:** compute the Stage 3 spectra inside the training loop at every grid step, and
  bank fp32 weights only on a sparse subset (e.g. Pythia's shared steps plus every 100). That departs from
  raw-object banking, so it would need your sign-off.

## 4. Data
- EleutherAI's preshuffled Pile (standard and deduped) is 20 × 30 GB shards; each step is 1024 consecutive
  2049-token samples = 4.2 MB.
- Step 5000 ends inside shard 0 (~21 GB of 30), so batches stream by HTTP range: 6.1 MB/s measured vs ~0.5 MB/s
  needed. Nothing is banked on C:.
- Batch boundaries are to be verified against `document.idx` in B1.

## 5. Found while reading the configs (for B1 / B2; no action taken)
1. **Init.** Pythia uses `small_init` (std √(2/(5d))) and `wang_init` for output layers (std 2/(L·√d)). HF's
   `GPTNeoXForCausalLM` initialises everything at N(0, 0.02). A0 must reimplement Pythia's init or B-G1 will fail at
   step 0 for a known reason. I'll implement it from the GPT-NeoX source, not from memory.
2. **Optimizer details** to take from the GPT-NeoX source before sealing: the yml says "Adam" with weight-decay 0.1
   (NeoX FusedAdam, adam_w_mode); which parameter groups are exempt from decay (biases / LayerNorm); the exact
   warmup and cosine formulas (min_lr = 0.1 × lr for 70M/160M).
3. **Data variant.** 31M's released config trains on deduped; 70M/160M exist in both. B-G1's seed band comes from
   PolyPythias, so A0 must use whichever variant PolyPythias used at that size. To verify in B1.
4. **Muon on fused QKV.** GPTNeoX stores Q, K and V as one (3d × d) matrix. Orthogonalising it whole or per Q/K/V
   gives different updates. This belongs with decision 3 (the Muon rule).
5. **Precision caveat:** Pythia trained in fp16 with dynamic loss scaling; Arm B uses bf16 autocast (brief §2).
   Recorded.

## 6. Recommendation (the decisions are yours)
- **Size: 70M.** It is the default, the compiled runs fit ~7.5 h at step 3000, and PolyPythias has 70M seeds for the
  B-G1 band.
  - 31M saves ~30% of the time but has fewer layers for the wave test and deduped-only data.
  - 160M doubles the time and disk for questions that don't need large N.
- **Stop step: 3000 for A1 / A2 / M0; 5000 for A0 only** (+5 h). That brings the 4k→5k update burst into the anchor
  run, where it can be compared with Pythia-70M.
- **Arms: A0 + A1 + M0 × 2, with A2 queued last if the calendar allows.** Q1's dose-response needs A2, but A0/A1
  alone can already separate "slope ≈ 1" from "slope ≈ 0".
- **Disk: D:,** with a per-arm directory and a free-space guard (the same 10 GB-reserve logic applied to /mnt/d).
