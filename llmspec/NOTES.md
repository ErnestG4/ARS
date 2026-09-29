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
- **HELD (Will's call):** the OLMo stage-1 trajectory for aim 1. (Arm B is RUNNING, not held.)
- **Alarm:** session-only cron, current job 6c2c8221 at `13,43 * * * *` (B4-chain prompt, set 09-29). Earlier alarms
  (0ab464f4, d06bd494) are deleted. Recreate after a restart; see §4.

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

## 4. Running now (09-29 11:00 PDT)
- **TRAINING COMPLETE:** A0, A1, A2, M0s1, M0s2 (queue closed 10:41 on 09-29).
  - A0 passed B-G1 at all 14 steps (worst |z| 1.87).
  - Every checkpoint is on spot with its sha256 .ok marker: A0 161, A1 181, A2 257 (dense), M0s1 161, M0s2 161.
- **B4 CHAIN RUNNING** (`armb/b4_run.sh`, detached; log armb/b4_run.log; sealed code bde3656 + amendments 3 (9a47dd5), 4 (0cebc89) and 5 (3c11ab0: data provenance in every result JSON) (5th-percentile noise row, FAIL-CLOSED seal check -- b4_analyze.py verifies armb/B4_SEAL.json (19 files) before running; any change to a sealed file halts the analysis stage)):
  refs (10 × 14 shared steps + pythia-70m step143000) → 70M witness → arms A0..M0s2 → `b4_analyze.py all`
  (checkrun). ~8 h on the GPU.
  - Resume: re-run armb/b4_run.sh (every stage skips finished outputs).
  - Outputs: cache/armb/<arm>/..., cache/s3/pythia-70m*/..., results/armb_b4_{q1,q2,q3,q4,bulk}.json.
- **Chain stopped 09-29 14:46 and RESUMED 16:29.**
  - spot hung (memory maxed per Will) and was rebooted twice (14:56, 15:54); sshd came back ~16:25.
  - No OOM-killer entry in either earlier boot's kernel log: the cause is not determined (zram thrash or a hard reset
    losing the journal both fit).
  - Our extraction reads measured benign after the resume: spot "used" flat at ~3.1 GB, only reclaimable page cache
    grows, no process pile-up.
  - The retry fix (B4 amendment 6, 960f775) is in place. A2 resumed at step 1425.
- **memwatch** PID 12700. **Alarm** cron replaced 09-29 with a B4-chain prompt.

- **09-28 morning (Will's three items):**
  - (1) Muon pre-launch check: already sealed and PASSED (A6, 8f51f25).
  - (2) Queue gate made FAIL-CLOSED, 12-case test (99c4e1c). It applies from the next runner launch.
  - (3) **B4 analysis code SEALED (5823b3d)**: armb/b4_extract.py + armb/b4_analyze.py, dry run PASS on a fabricated
    cache. The licence results were banked late, with their checkrun logs (ca0d94b).
  - **Q1 licence v2 (Will's sign-off; sealed 242ae7d, result a64d71f):** HALFWAY retired (it equals the LR_INT map
    post-warmup); midpoint + stretch + overshoot confusers.
    - E4 is now licensed for A2 at ≤ 1% noise with the no-model outcome ("X-driven" wording), and for A1 at 0.5%.
    - A2's grid is dense over 1000–2200 (B1a-A8, 855e007).
  - **B4 RE-SEALED (bde3656)** against licence v2 + arm grids; dry run PASS.
  - B4 run order and status: see §4 (the B4 chain, armb/b4_run.sh).

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
3b. **Seed leg COMPLETE (09-27 ~07:30).** Was split at 13:40 into two supervisors, split at 13:40 into two supervisors:
   - GPU: supervise PID 128268 (DEAD, finished 09-27) → queue_seeds.txt = extract + motion_eq for seeds 1..9, then scalecheck. Rewritten in
     place; same inode; line 1 unchanged.
   - CPU: supervise PID 182787 (DEAD, finished 09-27) → queue_seeds_cpu.txt = per seed, wait for its 10 motion_eq files → analyze
     (LLMSPEC_WITNESS=pythia-410m) → repl.
   - ETA ~13 h total (~88 min GPU per seed). Seed 1 final loss 2.338 (standard 410M 2.33).
   - Seed 1 DONE (14:57): 259 HOLDS / 1 VIOLATED (head_Q @ 143k, dq −0.103). Ladder step 2 (stage3_ladder.py) →
     DENSITY_ARTIFACT (density-matched dq −0.065). A noise-scaled residual (q −0.038, r̃ −0.006, ~3σ) is a CANDIDATE
     only. R1 ✗ (norm clause), R2–R6 ✓. Running record: STAGE3_SEED_FINDINGS.md.
   - For each later seed: run stage3_ladder.py on every VIOLATED cell before recording it (automatic via
     stage3_ladder_all.py).
   - Seeds 2, 3 DONE: HOLDS 260/260 each; all six R replicate.
   - **Addendum S1 (bb7e573):** crossings read mechanically, drift = annotation, a frozen 10-run drift test
     (stage3_drift_test.py, queued last).
   - Interim (n=4): the density calibrator explains ~73% of the per-head-Q q drift; residual z −3.8, ⟨r̃⟩ z −2.2.
     INTERIM, no verdict. Summary lines must say "HOLDS (per-head-Q drift flagged)".
   - **Addendum S2 (248d7b1):** the ⟨r̃⟩ arm is underpowered for the residual; the statistic is a t (df n−1; interim
     t3 −3.8, p ≈ 0.016); calib_fidelity test frozen and queued.
   - Step-0 excess variance: pipeline floor 0.0116 (synthetic, matches witness); tensors i.i.d.-consistent; excess is
     run/layer-grouped, modest, no structural layer effect; UNRESOLVED but bounded; the drift test's empirical SE
     absorbs it.
   - Seed 4 DONE: HOLDS (drift −0.049); R1 ✗ (concentration 0.307), R3 ✗ (O 2.61).
   - Seed 5 DONE: HOLDS (drift −0.088); R1 ✗ (rows 0.301), R2–R6 ✓.
   - Seed 7 DONE: HOLDS (drift −0.071); R1 ✗ (rows 0.288), R3 ✗ (MLP_OUT 2.98). G0 FAIL-as-sealed on V (threshold
     noise; confirmed on the tail with a common threshold).
   - **Seeds 3 and 4 had late loss spikes** (s3 64k–96k, s4 96k–128k; final loss 2.475 / 2.857). Their invariant
     products shrink too, so it is not symmetry drift. Seed 5's Q offset IS QK-symmetry drift. Annotation only.
   - **Addendum S3 (a5cd7bf):** original seeds 3–5 verdicts stay labelled "invalid reused witness"; the re-analysis
     is primary; the frozen tests take re-analysed inputs; stage3_qkprod_drift.py is a labelled descriptive (running).
   - Seed 6 DONE: 259/1 VIOLATED (head_Q @ 96k, dq −0.106) → automatic ladder DENSITY_ARTIFACT; R1 ✗ (rows
     0.2706), R3 ✗ (O 2.09).
   - **HF outage ~21:53 (HTTP 504 on resolve):**
     - It killed seed 7 extract (21/26 done), seed 7 motion, and seed 8 extract + motion. A retry-scope bug meant
       resolve errors were never retried; fixed in f804fce.
     - Stale partial .bin temp files removed. The failed jobs are re-queued at the END of queue_seeds.txt (after
       seed 9), as are seed 9's lines and the scalecheck.
     - The CPU queue waits on seed 7's motion files, so it resumes automatically.
   - **Witness-reuse scale check FAILED** for seeds 3, 4, 5, 9 (final-step rms 0.17–1.37× std 410M; seed 8 pending).
     Their reading A is PROVISIONAL.
     - GPU queue: stage3_seed_witness_gate.py for 9, 8, 3, 4, 5 (own witness if the check fails).
     - CPU queue (rewritten in place): seeds 8/9 wait for a complete witness decision (stage3_wait_witness.py); seeds
       3/4/5 are re-analysed / re-scored / ladder purged and re-run against their own witnesses; then drift_test,
       calib_fidelity.
     - mcfg.witness_suffix(): own witness if present, else LLMSPEC_WITNESS.
3. **Seed leg — PRE-REGISTERED** (STAGE3_SEED_PREREG.md, 2f38b8b). The .bin reader is verified (verify_bin_path, 6ca5be1).
   Queued after G3. When done: STAGE3_SEED_FINDINGS.md.
   - Check results/stage3_seed_scalecheck.json FIRST. Any seed outside ±20% needs its own witness before its null is
     read.
4. ~~Change-point null calibration~~ DONE (§15): NOT LICENSED (false-CP rate 0.59–0.98 on smooth nulls).
5. Zoo seating of the G7 classes (branch-merge session).
6. **FINDINGS_MEMO.md** (brief §6 deliverable: every claim with its gate) written 09-27 (1a4ddd1). S4-sup DONE: all calibrators recover 0.97–1.01 at 1× effect; biases replicate; the ⟨r̃⟩ arm had power (post-hoc t ≈ −3.7 for a departure of the claimed size).
7. **ARM B — spec received 09-27 (brief 'Arm B v0'; operating rules: GPU only, no method/device/precision/scope change
   without Will, BLOCKED.md + conservative default, detached + resumable, NO timers unless Will asks, seal before results).**
   B0 benchmark DONE → armb/B0_REPORT.md. ~~Recommended: 70M compiled, A0→5000 / others→3000, checkpoints on D:~~
   **SUPERSEDED. The decisions actually taken (Will, 09-27/28; recorded in ARMB_PREREG.md A1–A8):**
   - 70M, compiled, all arms.
   - Stops: A0 / A2 / M0s1 / M0s2 → 3000, A1 → 5000. A0 stops at 3000 because the burst check was ABSENT (A3).
   - Storage: raw fp32 checkpoints on spot, not D:.
   - Muon: update RMS matched to AdamW (Moonlight 0.2·√max(m,n)); Q, K, V split from the fused QKV and orthogonalised
     SEPARATELY; NS5 in bf16 (A6 test).
   - Paired design: every AdamW arm and M0s1 starts from Pythia-70M step0; M0s2 from seed1 step0 with seed-1 order (A1).
   - Precision: fp16 + Pythia's DeeperSpeed dynamic loss scaling, with Pythia-matched per-token scale (A4, A5).
   - A2 is required, with a dense grid over 1000–2200 (A8).
   **RULE (Will, 09-27): A1 does not start until A0 passes the anchor gate B-G1.** The server scores B-G1 at the shared
   checkpoints (steps 1–512, 1000, 2000) while A0 keeps training to 5000. PASS through 2000 → A1 queues automatically;
   FAIL → the GPU stops (nothing downstream runs on a bad anchor). To seal in B1: the PolyPythias seed band computed
   BEFORE A0 exists; a family-wise gate calibrated leave-one-seed-out; fail-fast semantics; pull-based signalling.
   - **Scoring server = spot** (Fedora VM, `ssh spot`; see memory cpu_box_128gb; ~/remote-claude-rules.md BINDING). A
     box-operator subagent does all spot work (setup phase 1 launched 09-27 ~13:15: env `llmspec`, ~/llmspec_armb/,
     code rsync, HF inventory of Pythia-70M / PolyPythias-70M revisions, data variant, CPU timing).
   - **B1a DRAFT** armb/ARMB_PREREG.md (d9c5067): replica spec from GPT-NeoX v1.0 source; grid; B-G1 gate
     (164 comparisons, Bonferroni-t T = 5.67 at n = 10; LOSO + 2 red-paths before A0). To fill before sealing: data
     variant (§1a), realised n, probe indices. **B1b (Q1–Q4) still to write**; both are sealed before A0 starts.
   - Source facts: Pythia step1 == step0 bit-identical (update k uses lr(k−1)); step0 std matches small_init;
     NeoX v1.0 files cached in scratchpad/neox.
   - **B1a SEALED 01fc4b5** (scorer bg1_score.py sha 0eb2cdff…, probe sha 94605108…). spot runs band → validate in
     tmux `claude` (started 13:23, ~2h15; log ~/llmspec_armb/bg1_run.log; outputs ~/llmspec_armb/bg1/). Collect
     through the box agent (SendMessage to it; it's idle between phases).
   - **B1b DRAFT** armb/ARMB_PREREG_B1B.md + armb/q1_licence.py (WIP). The Q1 smoke shows minimum-location estimators
     fail known-answer (kink bias, CI undercoverage). Raised with Will: registration-shift estimator for Δt* (A1 vs A0)
     as an alternative. **Waiting on Will** for Q1 method + B0 decisions.
   - Lesson repeated 09-27: `pkill -f <pattern>` killed my own shell AGAIN (pattern in the tool's command line). Use
     explicit PIDs only.
8. **OLMo stage-1 trajectory — DEFERRED behind arm B (Will, 09-27).** The cheapest real lead: the only place
   multimodality survived a licensed test (13.3% of Q heads excluding dead rows at stage-1 end). G7 did not license
   local statistics on peaked spectra, so it can only give peak timing (appear / fade), not internal structure.

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
- Retry scope must cover EVERY network step, including redirects and resolves, not just the data request. The HF
  504 outage (09-26 21:53) raised from _resolve outside the caught exception set and killed four queued jobs.
- **Protocol-template notes collected** (apply forward only):
  1. Rate bars (G0, G4) need allowance for sampling and threshold-estimation noise, set family-wise.
  2. Witness scale matching is unnecessary at the current tolerances (stage3_witness_scale_test: ≤ 0.0024 in ⟨r̃⟩ at
     0.17×).
  3. The nearest-confusable test must precede sealing.
  4. Default-path regression cannot catch default leakage.
  5. Retries must cover every network step.
- **Seed-leg outcome (09-27):**
  - Null holds in all 10 runs (2 cells → DENSITY_ARTIFACT; seed 7 G0 V fail = threshold noise).
  - R2 / R4 / R5 / R6 SEED-ROBUST; R1 2/10 and R3 4/10 SEED-DEPENDENT.
  - Frozen drift test FINDING_CANDIDATE (q t9 −5.9; ⟨r̃⟩ t9 −3.8). **S4: v1 bias −0.0207/−0.0164 under true β=1; q NOT RESOLVABLE; ⟨r̃⟩ quiet (t9 −1.6, v2_c16); drift NOT established.**
  - Calib-fidelity INCONCLUSIVE: the residual is perfectly monotone in mismatch, with a SIGN REVERSAL at the best
    fidelity (Q1 +0.029, Q4 −0.068), i.e. artefact-like. Next: Addendum S4, a higher-fidelity calibrator.
  - QK-product drift is present in all 10 runs (function, not symmetry). **WITHDRAWN by S4** (density alone moves q ~0.12).
- A login prompt paused the session ~01:15–07:15 on 09-27. The detached pipeline kept running and nothing was lost;
  only write-ups were delayed.
