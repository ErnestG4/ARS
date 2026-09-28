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

## Amendment B1a-A1 — 2026-09-27, PRE-DATA (no arm has trained a step; the reference band is still computing)
**Source:** Will's 09-27 review of B1b, point 4: "M0-s1 pairs with A0: Pythia step 0, Pythia data order".

1. **Init.** A0, A1, A2 and M0-s1 all START FROM `EleutherAI/pythia-70m` step0 weights (the released fp16-exact values,
   loaded into fp32 masters). This replaces "RNG seed 1234, a new draw" in §1.
   - Every AdamW arm and M0-s1 is then a PAIRED run with the released Pythia-70M trajectory: same init, same data order.
   - A0 − Pythia-70M differs only by precision (bf16 autocast vs fp16 with loss scaling), skipped overflow steps and
     GPU nondeterminism. That difference is reported DESCRIPTIVELY at the shared steps.
   - Caveat: the released step0 is the fp16 rounding of Pythia's fp32 initial masters, so A0's initial masters differ
     from Pythia's by that rounding (≤ 2⁻¹¹ relative).
2. **B-G1 is unchanged.**
   - A0 is now closer to pythia-70m (one member of the n = 10 band) than an independent seed would be. The gate stays
     valid and becomes more conservative.
   - Validation red-path (ii), "HF default init must fail", keeps its purpose: it shows the gate detects a wrong-init
     start.
3. **M0-s2** starts from `EleutherAI/pythia-70m-seed1` step0 with seed 1's data order.
   - The order is rebuilt from the released GPT-NeoX index maps in `EleutherAI/pile-preshuffled-seeds/seed1`
     (doc/sample/shuffle idx over the tokenized Pile).
   - Its AdamW partner is the released `pythia-70m-seed1` trajectory, at the shared steps only.
   - **Known-answer check of the data reconstruction:** the same code on `seed0` (base seed 1234) must reproduce the
     standard preshuffled batches byte for byte, for steps 1–50. If it does not, M0-s2 is BLOCKED (BLOCKED.md) and
     does not run.
4. **Stops.** A1 and A0 run to 5000; A2 to 3000; M0-s1 and M0-s2 to 3000.
   - A1 needs 5000 because the warmup-end model can put its turning point more than 1430 steps after A0's.
   - A2 is REQUIRED, no longer optional: it is the arm that separates the LR-integral model from the other two
     (B1b Q1).

## Amendment B1a-A2 — 2026-09-27 15:20, after band completion, BEFORE any validation result was seen
- **Defect.** §3.5 (iii) scored each run's "step-2t checkpoint" as step t for t ∈ {256, 512, 1000}, but 2 × 512 = 1024 is
  not a released checkpoint (Pythia saves 1000). The frozen scorer raised StopIteration in `validate`.
  - That happened before validate.json was written or anything printed, so NO validation outcome was seen.
  - Cause: `validate` was not dry-run at seal time (the S4 lesson, repeated).
- **Fix (minimal).** Score the NEXT shared checkpoint as step t, i.e. 512 / 1000 / 2000 for t = 256 / 512 / 1000. For
  t = 512 that is a 1.95× step instead of 2×. Nothing else changes.
- **Scorer:** now sha256 e24e570c7f709a3c735024f6b253512ceaaacc6fc5873862be1f8f179334fa4a; the previous sha is 0eb2cdff…
- **Dry run:** every validate branch ran on a fabricated miniature band BEFORE the real validate (this time).
- The band (160 rows, sha256 c51a4d6a…) is unchanged and is reused.

## Amendment B1a-A3 — 2026-09-27 16:15, stop step and storage (applying Will's rules; pre-data)
1. **A0 stop = 3000.**
   - Will's rule: A0 goes to 5000 only if Pythia-70M's released checkpoints show the 4k→5k update burst.
   - `armb/burst_check_70m.py` (criterion frozen at dc8c20a before running): **ABSENT in Pythia-70M and in all 9
     PolyPythias seeds** (10/10). V/O/MLP_OUT 4k→5k ratios are 0.86–1.06, against ≤ 0.5 for a burst.
   - A1 still runs to 5000 (Q1's warmup-end model); A2, M0-s1 and M0-s2 to 3000. The §2 grid is truncated
     accordingly.
2. **Storage** (Will's decision): raw fp32 checkpoints are banked on spot (~/llmspec_armb/ckpt/<arm>/), not on D:.
   - spot has 553 GB free after Will's expansion.
   - The plan needs ≈ 231 GB of weights (A0 45, A1 51, A2 45, M0 × 2 90) plus ≈ 28 GB of optimizer state.
   - A 10 GB free-space guard applies on spot.
   - Checkpoints transit C: only until their sha256-verified copy on spot exists; C:'s 10 GB guard stays.
3. **Muon rule** (Will's decision): Q, K and V are orthogonalised as SEPARATE matrices (split from the fused QKV).
   The LR rule is RMS-matched to AdamW (the brief's default), pending the text of Will's decision block.

## Amendment B1a-A4 — 2026-09-27 ~17:10: precision fp16 + loss scaling (Will's decision); A0 restarted
1. **What happened.** Will's decision block chose fp16 to match Pythia, but it never reached CC. B1a had sealed the
   brief's text ("bf16 autocast, fp32 masters").
   - A0 was launched in bf16 at 16:25 and stopped at step 164 when Will's review raised it.
   - **Disclosed:** the B-G1 daemon had scored that bf16 run at steps 0–128, all PASS (e.g. step 128 worst sr_MLP_IN
     z = −1.32).
   - Those verdicts are ARCHIVED (spot `bg1/_aborted_A0_bf16_verdicts.jsonl`, `ckpt/_aborted_A0_bf16`; local
     `armb/staging/_aborted_A0_bf16/`). They are NOT the anchor.
2. **New precision (all arms)** — every item below is traced to source, not memory.
   - fp32 master weights, fp16 autocast (torch.autocast float16).
   - **Dynamic loss scaling:** a line-for-line port of DeeperSpeed@eb7f5cf (the commit GPT-NeoX v1.0 pins)
     `deepspeed/runtime/fp16/loss_scaler.py` `DynamicLossScaler.update_scale`, with pythia-70m.yml's fp16 block:
     initial_scale_power 12, loss_scale_window 1000, hysteresis 2, min_loss_scale 1.
   - **Overflow** (any non-finite gradient): the update is SKIPPED and the LR scheduler is NOT advanced, but the step
     counter and the data pointer advance. This follows DeeperSpeed `engine._take_model_step`: "if overflow:
     self.skipped_steps += 1 else: lr_scheduler.step()", then "global_steps += 1".
   - So the n-th APPLIED update uses lr(n−1), and a skipped step consumes its batch, as in Pythia.
   - Unscale and clip (1.0) happen after the overflow check. The per-step log records loss_scale, overflow and the
     applied/skipped counts.
   - **Residual difference (disclosed):** DeepSpeed fp16 runs a pure-half model with an fp32 master copy; torch autocast
     keeps LayerNorm/softmax/CE in fp32. A0's skip COUNT may therefore differ from Pythia's (unknown). The B-G1 gate
     and the descriptive A0 − Pythia-70M comparison measure the net effect.
3. **Engineering (no change to the maths).** Forward + CE now run inside ONE compiled graph, with one GPU sync per step.
   The bf16 run had the CE outside the graph and a sync per micro-batch: 11.9 s/step vs the benchmark's ~8.5 s. Every
   arm uses the same compiled setting.
4. **Muon (M0-s1, M0-s2), confirmed by Will 09-27.**
   - Moonlight update-RMS matching: each orthogonalised update is scaled by 0.2·√max(m, n) of its matrix's shape.
   - Same LR, schedule and weight decay as the paired AdamW arm.
   - **Muon params:** 2-D hidden matrices only: Q, K, V (split from the fused QKV, each 512 × 512, orthogonalised
     separately, each scaled by its own shape), attention O, MLP in, MLP out.
   - **AdamW params:** embeddings, unembedding, LayerNorms, all biases.
   - **Reference implementation:** Nesterov momentum 0.95, 5 Newton–Schulz steps. The exact implementation commit goes
     into each arm's version string.

## Amendment B1a-A5 — 2026-09-27 ~18:40: B-G1 FAIL on the fp16 A0; the precision decision rule is committed BEFORE the gradient test
1. **What happened.** The fp16 A0 FAILED B-G1 at step 128 on probe loss.
   - A0 7.5394 vs band 7.3575 ± 0.0081 (Pythia-70M 7.3643); z = 21.37 against T = 5.67. Step 64 had z = 2.89 (a
     pass). All weight metrics passed.
   - The GPU stopped at step 138, as designed.
   - The failed run is ARCHIVED with its verdicts (spot `ckpt/_failed_A0_fp16_v1`, `bg1/_failed_A0_fp16_v1_verdicts.jsonl`;
     local `armb/staging/_failed_A0_fp16_v1/`).
   - The aborted bf16 run had probe loss 7.3631 at step 128 on identical batches.
2. **Hypothesis:** fp16 gradient underflow from my loss-scale arithmetic under gradient accumulation.
   - Per-token gradient factor, Pythia: cur_scale / (32 seq × 2048) = 4096/65536 = 0.0625. (DeepSpeed per GPU:
     mean-over-micro-batch loss × cur_scale; gas = 1; 32 GPUs × 32 sequences.)
   - Current code: cur_scale × 8/1024 / (8 × 2048) = 32/16384 = 0.00195, i.e. 32× smaller.
   - Proposed: micro-batch loss × cur_scale × MICRO/32, then divide the accumulated gradient by cur_scale × BATCH/32. The
     per-token factor becomes 0.0625, and the update maths is unchanged.
   - These are DERIVED values; the test below MEASURES them.
3. **Gradient test** (`armb/grad_underflow_test.py`, frozen by this commit; no training).
   - Weights: pythia-70m step128 (released). Data: 64 sequences of batch 129 (update 129's samples). Gradient of the mean
     token CE:
     - G_ref: fp32, no autocast;
     - G_cur: fp16 autocast with the current per-micro scale;
     - G_fix: fp16 autocast with the Pythia-matched per-micro scale;
     - G_bf16: bf16 autocast, unscaled.
   - Each variant accumulates over 8 micro-batches of 8, and the scaled variants go through the same unscale step.
   - **Reported:**
     - rel_err = ‖G − G_ref‖/‖G_ref‖;
     - cosine(G, G_ref);
     - the fraction of parameter entries with G = 0 where G_ref ≠ 0;
     - the MEASURED per-token gradient scale in the fp16 graph: the mean |∂(scaled loss)/∂logits| per element, via a
       hook, for G_cur and G_fix, and their ratio.
   - **CONFIRMED** iff rel_err(G_cur) > 2 × rel_err(G_fix) AND rel_err(G_fix) ≤ 2 × rel_err(G_bf16). That is, the
     current scaling loses accuracy that Pythia-matched scaling recovers, to bf16-comparable accuracy. Otherwise NOT
     CONFIRMED.
4. **Precision decision (committed now, before the test runs; no gate-shopping).**
   - **CONFIRMED:** fix fp16 with the Pythia-matched per-micro scale. The full dynamic scaler is already a line-for-line
     port (window 1000, hysteresis 2, min 1; no LR advance on a skip), so no further patching is needed. Restart A0
     from step 0 in fp16.
   - **NOT CONFIRMED:** switch to bf16 autocast (the brief's original text), recording "Pythia fp16 vs A0 bf16" as a
     caveat, and restart A0 from step 0 in bf16.
   - **Either way:** that choice is FINAL for all arms. The restarted A0 is judged by B-G1 from step 0. If it FAILS again,
     CC does NOT switch precision or retry. It writes BLOCKED.md with the diagnosis, and Will decides.
5. **Result (A5 test, `results/armb_grad_underflow.json`, CHECKRUN EXIT=0 PASS): CONFIRMED.**

   | scaling | rel_err vs fp32 | cosine | logit gradients flushed to 0 | per-token factor, measured |
   |---|---|---|---|---|
   | failed A0 | 1.21 | 0.63 | 81% | 0.00173 |
   | Pythia-matched | 0.00065 | 1.0000 | 0.009% | **0.0625** (= Pythia's derived 0.0625) |
   | bf16 | 0.012 | 0.9999 | — | — |

   - The measured per-token factor ratio (fix / current) is 36.2. The derived value is 32; underflow also shrinks the
     current path's measured value.
   - **Decision per the rule committed above: fp16 with the Pythia-matched per-micro scale, FINAL for all arms.**
   - `train.py` now backpropagates micro-loss × cur_scale × MICRO/32 and unscales the accumulated gradient by
     cur_scale × BATCH/32.
   - A0 restarts from step 0, judged by B-G1 from step 0. If it FAILS: BLOCKED.md, no retry.

## Amendment B1a-A6 — 2026-09-28: Muon implementation and its SEALED pre-launch update test (criterion committed before the test exists)
1. **Implementation:** `armb/muon.py`, MUON_VERSION "muon-hybrid-v1".
   - NS5 is taken from KellerJordan/Muon@f98f1ca. Momentum, Nesterov, weight decay and the 0.2·√max(A, B) LR rule are
     taken from MoonshotAI/Moonlight@c2ad5b2 examples/toy_train.py.
   - Q, K and V are split from the fused QKV and orthogonalised separately. Momentum buffers are fp32.
   - The trainer unscales, overflow-checks (skip logic) and clips (1.0) BEFORE the Muon step, exactly as for the AdamW
     arms.
2. **Update test** (`armb/muon_update_test.py`, written after this commit; no training).
   - **Setup:** pythia-70m step128 weights. TWO consecutive optimizer steps (to exercise momentum) on the first 64
     sequences of update 129's and update 130's batches, with lr 1e-3 and wd 0.1. The loss scale is 4096 at the first
     step and 8192 at the second, to exercise unscale consistency.
   - **Compared quantity:** the parameter change after step 2, per matrix type (Q, K, V, O, MLP_IN, MLP_OUT, aggregated
     over layers), as rel_err and cosine against REF.
   - **Variants:**
     - REF: fp32 gradients, fp32 NS.
     - PATH: the trainer's real path (fp16 autocast, Pythia-matched loss scale, overflow check, unscale, clip), fp32
       momentum, bf16 NS.
     - PATH_ns32: PATH with fp32 NS.
     - REF_ns16: REF gradients with bf16 NS.
     - RED: PATH with the fused QKV orthogonalised as ONE 1536 × 512 matrix (the spec error the test guards against).
   - **Criteria:**
     - (i) plumbing: PATH_ns32 vs REF has rel_err ≤ 0.01 and cosine ≥ 0.9999 for every type.
     - (ii) bf16 NS: PATH vs REF has cosine ≥ 0.995 and rel_err ≤ 0.1 for every type, AND
       |rel_err(PATH) − rel_err(REF_ns16)| ≤ 0.01 (the fp16 gradient path adds nothing beyond the bf16-NS error).
     - (iii) the witness can fire: RED vs REF has rel_err > 0.1 for Q, K and V.
   - **Decision:**
     - (i) ∧ (ii) ∧ (iii) → PASS, NS in bf16 (reference practice).
     - (i) ∧ (iii) but not (ii) → PASS with NS in fp32 (Will's allowed alternative), recorded.
     - Otherwise → BLOCKED.md; M0 does not launch.
3. **Result (`results/armb_muon_update_test.json`, CHECKRUN EXIT=0 PASS): PASS, NS in bf16.**
   - (i) PATH_ns32 vs REF: rel_err ≤ 0.0069, cosine ≥ 0.99997.
   - (ii) PATH vs REF: rel_err 0.038–0.079, cosine ≥ 0.9969. This is identical to REF_ns16 within 0.0003, so the bf16-NS
     rounding is the whole error and the fp16 gradient path adds nothing.
   - (iii) RED (fused QKV): rel_err 0.64–0.66 on Q/K/V; O and the MLPs are unaffected.
   - **Disclosed:** micro-batch 4 instead of 8, because of the VRAM cap while A0 trained. The per-token scale factor is
     identical, and it is a harder underflow condition.
   - **M0 uses MuonHybrid with bf16 NS** (MUON_VERSION "muon-hybrid-v1").

## Amendment B1a-A7 — 2026-09-28 ~02:00: the M0-s2 data reconstruction passes its known-answer check
1. **Code:** `armb/seed_order.py` (sha256 84c8a368…), which follows EleutherAI/pile-preshuffled-seeds `dataset.py`
   (MMapIndexedDataset.Index L88–125, get L203–214, GPT2Dataset.__getitem__ L259–282, read_dataset L285–303).
   - The index maps address the UNSHUFFLED tokenized Pile, 664,230,651,068 bytes, available on HF as
     `EleutherAI/pythia_pile_idxmaps` (133 × 5 GB shards; same .idx sha256). It is read only by HTTP range.
2. **Known-answer check (sealed in A1):** seed0 maps (base seed 1234), steps 1–50, compared with the preshuffled standard
   batches. **51,200/51,200 samples byte-exact; no offsets tuned.** M0-s2 is therefore NOT blocked.
3. **Seed-1 batches** for steps 1–3000 are being materialised on spot (`~/llmspec_armb/data/seed1_batches/`, per-step
   sha256 in steps.jsonl; MANIFEST.json at the end), ETA ~12–14 h.
4. **Unverified (disclosed):** that `seed1/` IS PolyPythias seed 1. That rests on the dataset README and the `_1s_`
   filenames. The known-answer check validates the METHOD (the seed0 files).
   - Queued (non-blocking, descriptive): train 16 steps of AdamW from pythia-70m-seed1 step0 on the reconstructed seed-1
     batches, and compare the weight change with the released seed-1 step16. The control is the same run on the
     standard-order batches. Criteria to be sealed before it runs.

## Amendment B1a-A8 — 2026-09-28 ~14:05, PRE-DATA for A2 (A2 has not started; A1 is at step ~4880)
- **Change (Will):** A2's checkpoint grid adds every 10 steps over 1000–2200: 257 checkpoints instead of 161,
  ≈ +27 GB on spot. "No-regret; disk only": the model, the data and the schedule are unchanged.
- **One definition:** `armb/grids.py` `arm_grid(arm)`. The trainer uses it from A2 on (A0 and A1 are unaffected: same
  grid as before). B4 extraction and analysis are switched to it by the B4 amendment that follows the licence re-run.
- **Reason:** the sealed licences allow a Q1 model verdict only through E4 on A2 at ≤ 0.5% noise. Will asked for the A2
  warp licence to be re-run on the denser grid (on spot, synthetic only) before B4 reads any arm.
