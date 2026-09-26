# llmspec NOTES — compaction-proof state (read this first)

Last full rewrite: 2026-09-26 04:55 PDT. Branch `llm-spectra`, worktree
`/home/combust/fmexplorer/criticality_tool/.claude/worktrees/llm-spectra`; all work is in `llmspec/`. Commits are local
and NOT pushed.

## 0. Mandate
- **Brief:** CC Brief v1.1, "Shapes of LLM weights and transforms over training" (Will, 2026-09-25). Staged plan:
  - Stage 1: existence check.
  - Stage 2: G7 multi-peak calibrator.
  - Stage 3: Pythia trajectories + pre-registered bulk null.
  - Stage 4: peaked-spectrum trajectory, only if G7 licenses local statistics.
  - Stage 5: arm B, AdamW vs Muon.
- **Will's §8 answers:**
  1. Peak criterion = MP-calibrated KDE.
  2. Arm B = HOLD.
  3. Bulk NNS/⟨r̃⟩ β=1 null = ADOPTED as a pre-registered instrument check.
  - Download budget: no cap.
- **Standing instructions:**
  - USE THE GPU.
  - Runs must be interruptible (`llmspec/STOP`) and resumable.
  - Do everything properly; never degrade an experiment for convenience or to make up for a mistake.
  - Autonomous: don't stall on questions; pick and proceed.
  - No fixed end time (04:50, 2026-09-26).
  - Keep notes for compaction.
- **HELD (Will's call):** arm B; the OLMo stage-1 trajectory for aim 1.
- **Alarm:** cron job every 30 min at `7,37 * * * *` (session-only; recreate after a restart). Its prompt says: read
  NOTES.md, check liveness, advance the queue.

## 1. Machine rules (each learned from an incident on 09-25)
- **Host commit.** WSL crashes = Windows commit exhaustion (vmmemWSL counts RAM + page cache + GPU allocations).
  Will added a 64 GB pagefile on a secondary NVMe, so host free commit is now ~60–70 GB. WSL RAM is still capped at
  12 GB (`.wslconfig`).
- **Disk.** `df /` lies (1 TB VHD). C: (`/mnt/c`) is what fills. `remote_st.check_stop()` refuses to proceed below
  10 GB free on C:. NEVER bank full checkpoints: stream HF → RAM → GPU.
- **GPU.**
  - 6 GB per-process cap in stage3_extract (an overrun raises OOM instead of crashing the VM).
  - Weights are stored on the GPU as fp16. This is exact for Pythia (F32 checkpoints are fp16 upcasts; asserted per
    tensor).
  - Compute runs in fp32/fp64 via transient per-module upcast; bit-identical to plain fp32 (verify_fp32_equivalence.py).
- **Durability.** `remote_st.durable_save` = tmp → fsync → rename → fsync dir, plus a posix_fadvise DONTNEED page-cache
  eviction. (A crash had left zero-length files behind renames.)
- **Streaming.** `remote_st.fetch_many`: keep-alive sessions, CDN URL resolved once per file, 4 tensors in flight;
  ~70 MB/s, byte-identical to `fetch` (verify_fetch.py).
- **Watchdog.** `memwatch.sh` logs RAM/cache/GPU/C:/host commit every 20 s and writes `STOP` with content "memwatch"
  if host commit < 5 GB.
  - `supervise.sh q1 q2 …` runs queue files and auto-resumes after a memwatch STOP. A manual STOP (any other content)
    ends it.
  - `chain2.sh <pid> q…` starts `supervise` after a PID exits.
  - `resume.sh` restarts watchdog + supervise after a reboot. It references queue4–6, which are all done; edit it for
    the current queue first.
- **NEVER `pkill -f <pattern>`** in the Bash tool: the pattern is in the tool's own command line, so it kills the
  shell (done twice). Use explicit PIDs.
- **Commit hook.** A commit message that claims an outcome needs a `CHECKRUN <checker> EXIT=n PASS` line produced by
  `../checkrun.sh <checker>`; paste it, never type it. checkrun.sh writes to `.checkrun_log`.
- **Plots** are git-ignored. They regenerate from the scripts (stage1_analyze.py, stage3_report.py).

## 2. Code map (llmspec/)
- **I/O:**
  - `remote_st.py`: HTTP-range safetensors reader, fetch/fetch_many, STOP + disk guard, durable_save.
  - `specs.py`: model layouts, per-head blocks, G4 grid audit.
- **Stage 1:**
  - `peaks.py`: SVD, KDE, modes.
  - `stage1_calibrate.py`: seal.
  - `stage1_spectra.py`, `stage1_analyze.py` (sealed rule + amendment A1).
  - `stage1b_dip.py`: Hartigan dip test (licensed).
  - `verify_kde_sparse.py`.
- **Stage 2:** `stage2_g7.py` (G7 calibrator; prereg in its docstring).
- **Stage 3:**
  - `stage3_extract.py`: streaming per-checkpoint extraction + markers.
  - `stage3_probes.py` → `results/probes.npz` (sha256 in probes.sha256).
  - `s3stats.py`: THE local-statistics module.
  - `stage3_witness.py`: G1/G4/margins.
  - `stage3_analyze.py`: sealed null, G0, globals, vectors, circuits, markers, change points, motion ingestion.
    `STAGE3_TAG` env var gives partial-run outputs.
  - `stage3_mp2_patch.py`, `stage3_report.py` (plots + event table).
  - `stage3_motion.py`: consecutive ΔW. `stage3_motion_eq.py`: equal 1000-step ΔW.
  - `stage3_g2.py`: G2 functional witness. `stage3_g2b.py`: G2 controls.
  - `stage3_confounds.py`, `stage3_confounds2.py`, `stage3_headnull.py`, `stage3_circuit_null.py`: review checks.
  - `stage3_wave.py`: per-layer compression timing over all revisions.
- **Verifiers** (all red-pathed with `--redpath`): verify_kde_sparse, verify_fp32_equivalence, verify_s3stats,
  verify_stage3_estimators, verify_fetch, verify_motion_sigma.
- **Docs:** STAGE3_PREREG.md (+ amendments A0 and A1), STAGE1_FINDINGS.md, STAGE2_FINDINGS.md, STAGE3_FINDINGS.md
  (§1–12; §8–12 supersede earlier sections where they conflict), STATUS.md.

## 3. Results (status labels exactly as in the findings docs)
### Stage 1 — existence (21c0837, 78c2fad, d16caaf, eca356d)
- **Sealed KDE rule:** PEAKS in both OLMo-2-1B `main` and Pythia-1.4B, so the decision table says "BOTH". But this is
  UNRESOLVED as evidence: the rule was never tested against its nearest confusable (unimodal heavy tails), and the
  counted modes were tail specks.
- **G0 FAIL-as-sealed on Pythia W_O** (6/384). Attributed: the bar had no sampling allowance, giving an 18%
  false-fail rate.
- **Stage 1b, Hartigan dip test** (post-hoc; licensed, 0/2000 false positives on every confusable; weak power):
  - Pythia: 0 multimodal heads in any type.
  - OLMo Q/K at stage-1 end: Q 24.6% (13.3% excluding dead rows), K 19.9%.
  - OLMo `main`: Q 8.6%, below the 10% floor.
  - **Decision: aim 1 deferred.** OLMo stage-1 trajectory = Will's call.
- **G4:** Pythia F32 = fp16 upcasts. OLMo-2 F32 = fp32 masters (the brief's "bf16" premise was wrong). OLMo Q/K
  have dead rows (norm ~1e-28).

### Stage 2 — G7 on real OLMo stage-1-end W_Q targets (55de694)
- **NOT LICENSED as registered.** kde(6)/kde(8) pass Poisson, β=1 and clustered on both families but fail β=2
  (Δq ≈ −0.2).
- Raw-x ⟨r̃⟩ LICENSED.
- Post-hoc: dropping the optional β=2 class would license "clustering vs β=1 vs Poisson". Reported, NOT adopted
  (Will's call).

### Stage 3 — Pythia-1.4B, 26 schedule revisions (prereg 0cf53ba; findings 4ff09ee … 463ea03)
- **SEALED NULL HOLDS 260/260 cells.** Precisely: no bulk departure > 0.010 in ⟨r̃⟩ or > 0.10 in q (loose) at any
  checkpoint in any type. Worst |Δ⟨r̃⟩| 0.004, |Δq| 0.034.
  - G0 passes. The witness reads β=1. The instrument fires on Poisson (⟨r̃⟩ 0.39).
- **LR confound.** Warmup ends at 1430 (config: Adam lr 2e-4, warmup 0.01, cosine to 2e-5). Every "turning point at
  ~2k" = LR-CONFOUNDED.
- **MP fit invalid for trained matrices** (KS > witness 95th percentile in 96–100% of layers from ~512–2000). All
  outlier-vs-MP-edge counts after that point are WITHDRAWN. Report top-k σ only (Q σ₁ 1.26 → 17.3).
- **"Outlier peak then decline":** RETRACTED (edge artefact).
- **Localisation:**
  - K's top singular directions concentrate on rotary dims (0.48 vs 0.25 null; rotary rows carry only 0.227 of the
    norm). SURVIVES.
  - Head concentration is NOT norm-driven: the input-rotation null gives more concentration (Q 0.59 vs observed
    0.24). The real structure is cross-head sharing of input directions.
  - Not LN/massive-activation (0 shared heavy residual coordinates raw or folded; late-layer Q meets LN-gain
    coordinates with small mass).
- **Circuits:**
  - Product-Ginibre null: OV departs by step 512 (98.7% of heads), QK at 1000–2000.
  - The 14 induction heads leave the QK band earlier (21% at 512, 100% at 1000 vs 2.7% / 49%). Magnitude is partly
    selection-built. "OV before induction" is at the resolution limit.
- **Events:** induction 512–1000 (no checkpoints between). First sink head >0.5 at 48k–64k. Sink comparison with the
  brief's 10–20× is NOT COMMENSURABLE: the paper's own Pythia-1B gap is ~50×, and definition, probe and BOS all
  differ.
- **Liu wave:** not resolved (schedule too coarse; only arm B can resolve 512–2000). Dense-V extension running.
- **Square lower-edge rise:** NOT precision-limited (Weyl bound: ≤ 0.01 possible vs 0.19 observed).
- **Change points:** uncalibrated → descriptive only.
- **G2:** identity 0.000; bulk +2.67; full +9.4; upper +0.10; lower inert. "Diffract replicates" = false as sealed.
- **G2b** (29d8f63):
  - Same-subspace size-matched control +1.80 vs +2.67, so SIZE explains ≥ half and "bulk ordering carries function"
    is NOT established.
  - Local shuffles (k = 2/8/32) inert.
  - One matrix +0.005; one layer +0.035–0.08; all at once +2.67 (superadditive).
  - MP-bulk ill-defined for trained spectra (+8 nats).
- **Equal-interval ΔW** (463ea03):
  - Update stable rank rises 5–15× over 1k–31k at constant LR: dynamics, not spacing. Late decline LR-confounded.
  - Per-LR relative update shrinks 2–10×.
  - Q/K updates ~9× isotropic in W's top-32 early, ~2× later.
  - Unexplained low-rank burst in V/O/MLP_OUT at 4k–5k.
  - Sub-1000 "low-rank early" → arm B.

## 4. Running now (check with `ps -eo pid,args | grep -E "[c]hain2|[s]upervise|[q]ueue.sh|[s]tage3_|[m]emwatch"`)
- queue7 (dense V + wave): DONE. queue_r14 (1.4B scorer consistency): DONE, passes.
- **PID 120469:** supervise(queue_r14 ✓ → queue_pythia-1b [running since 05:27] → queue_pythia-410m).
  - queue_r14: stage3_repl.py on 1.4B. Consistency check: it must reproduce R1 0.484 vs 0.25 / rows 0.227; R2 Q
    0.243 < 0.588, K 0.133 < 0.496; R3 ratios ≥ 4.2; R4 at step 512: OV 0.987, QK 0.034; R5 (512, 1000); R6 Q/K
    ~1.0 by 1000.
  - queue_pythia-{1b,410m}: extract 26 revisions → witness → motion_eq → analyze → report → repl. Rough ETA: 1B
    ~5–6 h, 410M ~2–3 h.
- **PID 128268:** chain2 → supervise(queue_seeds), starting when 120469 exits.
  - queue_seeds: PolyPythias 410M seeds 1–9, each = extract (CkptBin, .bin path) → motion_eq → analyze
    (LLMSPEC_WITNESS=pythia-410m) → repl; then stage3_seed_scalecheck. ~2 h per seed.
- **memwatch:** PID 12700.
- **Alarm cron:** job 0ab464f4, `7,37 * * * *`.

## 5. Next (in order; mark each done here with its commit)
1. ~~Dense-V + wave~~ DONE → STAGE3_FINDINGS §13: V shows NO layer ordering at 1000-step resolution (ρ −0.00). Scorer
   consistency on 1.4B → §14 (all R1–R6 reproduce).
2. **G3 replication** — PRE-REGISTERED (STAGE3_REPL_PREREG.md, 8147f53).
   - Model-general refactor, regression-gated: extraction bit-identical (verify_refactor_regression) and analysis
     16769 rows identical (verify_analyze_regression, 2990ef5).
   - Scorer: stage3_repl.py (215e989).
   - When done: STAGE3_REPL_FINDINGS.md (sealed null per model first; then R1–R6 REPLICATES / DOES NOT; nulls as
     nulls).
   - **1B DONE (09:52):** null HOLDS 260/260. R1, R2, R4, R5, R6 REPLICATE. **R3 DOES NOT** (V 2.98, O 1.80 < 3).
   - **410M DONE (12:54):** null HOLDS 260/260. R2, R4, R5, R6 REPLICATE. **R1 DOES NOT** (norm clause: rows 0.2704 >
     0.27). **R3 DOES NOT** (V 1.89, O 1.43, MLP_OUT 2.11). Cross-size table in STAGE3_REPL_FINDINGS.md.
3b. Seed leg RUNNING since 12:54, split at 13:40 into two supervisors:
   - GPU: supervise PID 128268 → queue_seeds.txt = extract + motion_eq for seeds 1..9, then scalecheck. Rewritten in
     place; same inode; line 1 unchanged.
   - CPU: supervise PID 182787 → queue_seeds_cpu.txt = per seed, wait for its 10 motion_eq files → analyze
     (LLMSPEC_WITNESS=pythia-410m) → repl.
   - ETA ~13 h total (~88 min GPU per seed). Seed 1 final loss 2.338 (standard 410M 2.33).
   - Seed 1 DONE (14:57): 259 HOLDS / 1 VIOLATED (head_Q @ 143k, dq −0.103). Ladder step 2 (stage3_ladder.py) →
     DENSITY_ARTIFACT (density-matched dq −0.065). A noise-scaled residual (q −0.038, r̃ −0.006, ~3σ) is a CANDIDATE
     only. R1 ✗ (norm clause), R2–R6 ✓. Running record: STAGE3_SEED_FINDINGS.md.
   - For each later seed: run stage3_ladder.py on every VIOLATED cell before recording it.
3. **Seed leg — PRE-REGISTERED** (STAGE3_SEED_PREREG.md, 2f38b8b). The .bin reader is verified (verify_bin_path, 6ca5be1).
   Queued after G3. When done: STAGE3_SEED_FINDINGS.md.
   - Check results/stage3_seed_scalecheck.json FIRST. Any seed outside ±20% needs its own witness before its null is
     read.
4. ~~Change-point null calibration~~ DONE (§15): NOT LICENSED (false-CP rate 0.59–0.98 on smooth nulls).
5. Zoo seating of the G7 classes (branch-merge session).
- HELD: arm B; OLMo stage-1 trajectory.

## 6. Lessons from this run (to carry into memory at handoff)
- A sealed criterion must be tested against its NEAREST CONFUSABLE, not only its easy null. The KDE rule saw MP but
  never heavy-tailed unimodal.
- Pass/fail bars on rates need a sampling allowance (sealed G0 and G4 both lacked one).
- Iterated estimators can collapse (mp_fit_v1); synthetic validation must include the regime the data will be in.
- Nulls can be degenerate (within-head output rotation leaves per-head mass exactly invariant). Check that a null can
  differ from the observed before reading "observed = null".
- Timing claims need the training schedule (LR warmup/decay) and the checkpoint grid beside them.
- A count against a fitted edge is only meaningful while the fit holds. Track goodness of fit.
- A regression gate on the DEFAULT path cannot catch a default leaking into a new configuration. The model-general
  refactor passed bit-identical 1.4B regressions while stage3_motion_eq still hard-coded 1.4B's LR peak (caught at
  12:10 on 09-26, before any use; fixed in ba7839b). When generalising, grep for every numeric constant tied to the
  old configuration, not just shapes.
