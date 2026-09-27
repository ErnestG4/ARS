# Arm B pre-registration — Part B1a: replica spec, checkpoint grid, anchor gate B-G1

**Status: B1a SEALED 2026-09-27**, before any reference band, gate-validation or A0 result exists. Part B1b (the Q1–Q4
tests) is sealed separately, before A0 starts.

**Frozen with this seal:**
- **Scorer:** `armb/bg1_score.py`, sha256 0eb2cdffa73135e9afbc9d7fc53866538de1ab295a24314f515349aa611bda14. It is copied unedited to spot.
- **Loss probe:** (64, 2049) uint16, sha256 94605108134b8f11003c4412aeae39d9f5ee2d8d40eb632b266ff046cf92a1ea. Indices come from
  seed 20260927 and lie in shards 19–20; no sample straddles a shard boundary.
- **Pre-seal smoke** (spot; NOT a gate evaluation; no band or validation existed): one checkpoint of each file format was
  scored to test the code paths.
  - pythia-70m step1000 (safetensors) and seed1 step1000 / step0 (fp16 .bin).
  - The step-0 values match random-matrix expectations: stable rank 129.7 vs N/4 = 128 for square layers, 229 vs 227.7
    for MLP layers; Frobenius norms 14.31 = 512 × 0.02795 (small_init) and 7.545 = 512 × 0.014731 (wang_init).
- **Not scientific parameters** (left open): the checkpoint disk location (Will's decision 4) and the Muon rule
  (M0 only; Will's decision 3).

- **Parent:** CC Brief "Arm B v0" (Will, 2026-09-27); FINDINGS_MEMO.md; B0 report (armb/B0_REPORT.md, c3ea63a).
- **Will's rule (09-27):** A1 does not start until A0 passes B-G1 through step 2000; a FAIL stops the GPU.

## 1. Replica spec (A0) — every item traced to source, not memory
- **Architecture.** `GPTNeoXForCausalLM` with the unmodified `EleutherAI/pythia-70m` config.json: 6 layers, d = 512,
  8 heads, rotary fraction 0.25, parallel residual, untied embeddings, vocab 50304. sdpa attention.
- **Init** (GPT-NeoX v1.0 `megatron/model/init_functions.py`, `transformer.py`, `gpt2_model.py`; pythia-70m.yml
  `init_method: small_init`, `output_layer_init_method: wang_init`):
  - **small_init, N(0, √(2/(5·512)) = 0.027951):** `query_key_value`, `dense_h_to_4h`, `embed_in`, `embed_out`.
  - **wang_init, N(0, 2/(6·√512) = 0.014731):** `attention.dense`, `dense_4h_to_h`.
  - **Constants:** biases 0; LayerNorm weight 1, bias 0.
  - **Check (done):** Pythia-70M step0 layer-0 QKV std is 0.027909, which matches small_init (0.027951) within
    sampling error.
  - **RNG seed:** 1234, the GPT-NeoX default Pythia used. This does not reproduce Pythia's draws (the RNG pipelines
    differ), so A0 is a new seed from the same distribution, and the B-G1 band is a SEED band.
- **Optimizer** (GPT-NeoX v1.0 `training.py`: FusedAdam in AdamW mode; `model/utils.py`
  `get_params_for_weight_decay_optimization`):
  - AdamW, betas (0.9, 0.95), eps 1e-8, weight decay 0.1, decoupled.
  - **No weight decay** on LayerNorm parameters or on any bias. Gradient clipping at global norm 1.0.
- **LR** (GPT-NeoX v1.0 `learning_rates.py` AnnealingLR, reproduced exactly, including its quirk):
  - lr₀ = 1e-3, min_lr = 1e-4, W = 1430 (0.01 × 143000), E = 143000.
  - `lr(n) = lr₀·n/W` for n ≤ W.
  - Otherwise `lr(n) = max(min_lr, lr₀/2·(cos(π·(min(n, E−W) − W)/E) + 1))`. Note the /E, not /(E−W).
  - **Alignment:** optimizer update k (producing checkpoint step k) uses lr(k−1). Verified: Pythia-70M step1 is
    bit-identical to step0 (the first update ran at lr(0) = 0), and step2 − step1 = 9.5e-7 ≈ lr(1) = 7.0e-7 × O(1).
- **Data.**
  - EleutherAI's preshuffled Pile, in the variant fixed in §1a below.
  - Update k reads samples [(k−1)·1024, k·1024) of the concatenated `document-*.bin` (Pythia `utils/batch_viewer.py`:
    iteration i = samples [i·1024, (i+1)·1024)).
  - Each sample is 2049 uint16 tokens: inputs = tokens[:2048], labels = tokens[1:].
  - Read by HTTP range, with retries on every network step (memo §4). A 1024 × 2049 batch = 4,196,352 bytes; its
    sha256 is logged per step.
- **Precision.** fp32 master weights, bf16 autocast forward/backward, fp32 optimizer state. All spectra come from fp32
  masters. No loss scaling.
  - **CAVEAT (recorded):** Pythia trained in fp16 with dynamic loss scaling (initial scale 2¹², window 1000,
    hysteresis 2). Overflow steps are skipped, so a Pythia checkpoint "step t" may contain slightly fewer than t
    applied updates. A0 skips none. The skip count is unknown; it is expected to be a handful by step 5000.
- **Batch.** 1024 × 2048 tokens per update: gradient accumulation of 128 micro-batches of 8, loss averaged over all
  tokens.
- **Engineering, not method:** torch.compile, fused AdamW kernel, sdpa. Each is disclosed; none changes the maths
  beyond floating-point reassociation.

### 1a. Data variant (FILLED 2026-09-27 from the PolyPythias paper)
- **Standard (non-deduplicated) Pile:** `EleutherAI/pile-standard-pythia-preshuffled`.
- Source, arXiv 2503.09543 (https://arxiv.org/html/2503.09543v1): "We use the standard (i.e., non-deduplicated) version
  of the Pile".
- On seeds: "Each training run uses the same hyperparameters, codebase, and data as Biderman et al. (2023b) but varies
  the seeds for parameter initialisation and batch composition". The model card for `EleutherAI/pythia-70m-seed1`
  lists `pythia-{size}m` as the "Original Pythia model (seed 1234)".
- **Consequence for B-G1.** The reference seeds vary init AND batch order together; the 70M suite has no init-only
  variants (those exist only at 160M). A0 varies init only, since it uses Pythia's exact batch order. So the band is
  WIDER than A0's own seed spread: the gate is conservative. Its power is what the §3.5 red-paths measure.

## 2. Checkpoint grid (final)
- **Full fp32 state_dict (282 MB) at:**
  - every 10 steps over 0–500;
  - {1, 2, 4, 8, 16, 32, 64, 128, 256, 512} (Pythia's shared log steps);
  - every 25 steps over 500–3000;
  - every 100 steps over 3000–5000 (A0 only).
  - Totals: 161 checkpoints to 3000, 181 to 5000.
- **AdamW state (exp_avg, exp_avg_sq):** at steps {1, 10, 100, 256, 512, 1000, 1430, 2000, 3000, 5000}.
- **Location:** D: (per-arm directory), with a free-space guard of 10 GB on D: as well as C:. *(Pending Will's
  decision 4.)*
- **Per step, logged:** loss, lr, pre-clip grad norm, update norm ‖ΔW‖ per matrix type, and batch sha256.
- **Resume:** from the latest full checkpoint plus optimizer state. Optimizer state is also saved every 50 steps
  (overwriting one rolling resume slot), so that a resume never loses more than 50 steps.

## 3. Anchor gate B-G1
### 3.1 Reference set
- Pythia-70M (standard Pile, seed 1234) plus PolyPythias `pythia-70m-seed1` … `seed9`: n = 10. All 16 shared
  revisions exist in all 10 repos (spot inventory, ~/llmspec_armb/inventory.json).
- **Precision commensurability.** The references are effectively fp16: the seed repos are fp16 .bin, and pythia-70m's
  fp32 safetensors is an exact fp16 upcast (all 76 tensors equal, checked on spot). So the gate scores A0's checkpoint
  ROUNDED TO fp16. Q1–Q4 (B1b) use A0's fp32 masters, as the brief requires.
- The seed band is computed on spot (the CPU scoring server) from HF-streamed checkpoints, BEFORE A0 exists.
- The same code scores A0 and the references on the same machine (commensurability).

### 3.2 Shared steps
- Gating: {0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000}. A1 is queued on PASS at every one of these.
- Also scored: 3000, plus 4000 and 5000 where references exist.
  - A FAIL at 3000 still stops the GPU.
  - A FAIL there makes the whole arm set uninterpretable (brief §3 B2: "If B-G1 fails, nothing downstream is
    interpreted").
- Steps 0 and 1 test init only (Pythia step1 = step0).

### 3.3 Metrics (per shared step)
- **(a) Loss** on a fixed probe: 64 samples of 2049 tokens.
  - Drawn uniformly (seed 20260927) from preshuffled indices [142,000 × 1024, 143,000 × 1024), i.e. from Pythia's LAST
    1000 steps. The file holds exactly 143,000 × 1024 samples, so every sample is trained on by the end.
  - Unseen by Pythia-70M and A0 through step 5000.
  - PolyPythias seeds use other batch orders, so each probe sample has probability ≈ 5000/143000 = 3.5% of having been
    seen once by a given seed by step 5000 (~2 of 64). Disclosed; expected effect negligible.
  - The probe indices and sha256 are fixed at seal.
- **(b) Layer-mean stable rank ‖W‖_F²/‖W‖₂²** for each of: Q, K, V (split from the fused QKV exactly as Stage 3 does),
  O, MLP_IN, MLP_OUT.
- **(c) Layer-mean Frobenius norm** for the same 6 types.
- Family: 164 comparisons = 5 steps (0, 1, 2, 4, 8) × 12 weight metrics + 8 steps (16 … 2000) × 13.
  - Loss is only compared from step 16 on, because near init every run's loss ≈ ln(50304) ± init noise.

### 3.4 Decision rule
- **Per comparison:** z = (x_A0 − m) / (s·√(1 + 1/n)), with m and s the mean and SD over the n reference runs. Under
  "A0 is exchangeable with the reference seeds" (Gaussian), z ~ t_{n−1}.
- **Family-wise:** PASS iff |z| ≤ T at every comparison. T is the t_{n−1} quantile with two-sided Bonferroni level
  0.05/164: **T = 5.67 for the realised n = 10** (it would be 6.05 at n = 9 if a reference ever fails to load, which
  would be reported).
  - This bounds the false-fail rate at ≤ 5% under the model. The template fix "family-wise allowance" (memo §4)
    applies here: a bare per-step bar would false-fail a correct A0 almost surely.
- **Fail-fast:** the first failing gating step writes FAIL and the GPU stops. PASS needs every gating step through
  2000. Steps not yet scored are PENDING.

### 3.5 Gate validation (run on the reference data BEFORE A0 exists; the gate is used only if all three pass)
- **(i) Leave-one-seed-out specificity.** Each reference run is scored as if it were A0, against the other n − 1.
  - Required: 0 FAILs among the n runs.
  - Also reported: each run's worst |z| and where it occurs.
  - With n ≈ 10 this checks gross mis-specification; it does not estimate a 5% rate precisely, and is reported as
    such.
- **(ii) Red-path: wrong init.** HF's default init (N(0, 0.02) everywhere) at step 0 must FAIL. This is the known
  confound A0 is built to avoid.
- **(iii) Red-path: step misalignment.** Each reference run's step-2t checkpoint, scored as if it were step t (for
  t ∈ {256, 512, 1000}), must FAIL at a majority of those t. This shows the gate resolves one checkpoint-interval of
  timing error.
- **If (ii) or (iii) cannot fail:** the gate is INERT for that confound, and that is reported. If (i) fails, the gate
  is mis-specified. Either way, A0 does not start until Will decides (BLOCKED.md).

### 3.6 Plumbing (pull-based; spot never reaches into Will's desktop)
- **On the GPU host:**
  - A0 writes each shared-step checkpoint to D:.
  - A small uploader rsyncs it to spot:~/llmspec_armb/a0/ (verified by sha256), then deletes nothing locally.
- **On spot:** a scorer in tmux `claude` scores each checkpoint as it arrives and appends to `bg1_verdicts.jsonl`.
- **The GPU-side queue runner pulls that file:**
  - FAIL → writes `llmspec/STOP` with content "B-G1 FAIL step t", and A0 stops at its next step;
  - PASS through 2000 → enqueues A1.
- Every verdict line carries the scorer's git hash and the reference-band file's sha256.
