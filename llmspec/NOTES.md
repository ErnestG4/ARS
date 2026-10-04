# llmspec NOTES — compaction-proof state (read this first)

Last full rewrite: 2026-09-26 04:55 PDT. Branch `llm-spectra`, worktree
`/home/combust/fmexplorer/criticality_tool/.claude/worktrees/llm-spectra`; all work is in `llmspec/`. Published 2026-09-30
(github.com/ErnestG4/ARS; Will pushes).

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
- **Disk.** `df /` lies (VHD). The host drive holding the VHD is what fills: **F: (`/mnt/f`) since 2026-10-01** (was C:).
  `remote_st.HOST_DISK` and memwatch guard it. `remote_st.check_stop()` refuses to proceed below
  10 GB free on F:. NEVER bank full checkpoints: stream HF → RAM → GPU.
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
  - OLMo Q/K at stage-1 end: **Q 13.3% excluding dead rows** (24.6% all levels, inflated by the dead-row spike), K 8.6% trimmed (19.9% all levels).
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

## 4. Running now (10-01)
- **LAPSE (10-01, Will):** A0r finished ~04:30 and the spot extraction at 10:06; neither was acted on until Will asked
  at 11:53 (~7 GPU-h + ~2 spot-h idle). Cause: the completion wait expired at 2 h and was not re-armed. Rule now:
  every detached job has a wait RE-ARMED on each expiry, AND an hourly in-session cron alarm (a8edbc70, :23) checks
  jobs, acts on finished ones and launches the next sealed item. (memory: long_jobs_get_rearmed_event_waits)
- **A0r SCORED 10-01 ~14:40: NOT RESOLVABLE as sealed (pipeline mis-reads a known null)** — TP_O identity fit ratio 13.3 >
  c_fit 5.4; paired floor c_pair 2.36% (O) / 0.48% (MLP_OUT) vs A2 misfit 2.42% / 1.69%; MLP_OUT 3.5× the floor
  (descriptive). Written up: ARMB_FINDINGS §2b, memo row 14, README. GPU released to Will.
- **A0r DONE** (step 3000, final loss 3.1254 vs A0 3.1148; 169 ckpts on spot). **A0r scoring DONE** (`armb/a0r_score.py
  all`, committed b3ebf37 before any output was read; log armb/a0r_score.log; pid armb/a0r_score.pid): extract (GPU)
  → calib → licence → q1 → identity; results/armb_a0r_{noise_calibration,q1_warp_licence,q1,identity}.json; verdict per
  A0R_PREREG §2 printed as "identity written; VERDICT: ...".
- **RESUMED 10-01 ~16:20 after the WSL maintenance: ext_queue relaunched (A0 continues 3400 → 10000, then M0s1, M0s3);
  memwatch on F:; hourly alarm 5ca8cfb7 alive. spot access is now the narrow passphrase-less key
  `~/.ssh/id_ed25519_spot_llmspec` (restrict,from=10.0.0.0/24 on spot; no agent socket needed any more).**
- (superseded) **HALTED 10-01 14:52 at step 3400 for Will's WSL maintenance (STOP file; resume.pt = 3400 exactly). GPU quiet.**
  Resume (same session after maintenance, Will's call): `rm llmspec/STOP`; `cd llmspec/armb && setsid nohup ./ext_queue.sh >
  ext_queue.log 2>&1 &` (its A0 stage resumes train.py from 3400 to 10000, then M0s1, M0s3); restart `bash memwatch.sh`;
  re-arm the waits; the hourly alarm (5ca8cfb7) survives only if the session does.
- (superseded) **PAUSE AFTER A0 (Will 10-01 14:40): WSL maintenance.** The queue shell was killed; only `train.py A0 --stop 10000`
  runs (pid armb/trainer_A0_ext.pid; ETA ~05:20 10-02). M0s1/M0s3 NOT started. After maintenance (a WSL restart kills
  this session and its cron alarm): check `armb/train_A0_ext.log` reached step 10000 (else re-run `train.py A0 --stop
  10000`, it resumes), then `cd llmspec/armb && setsid nohup ./ext_queue.sh > ext_queue.log 2>&1 &`, re-arm waits, re-create
  the hourly alarm. memwatch (pid 2700200) also dies with WSL: restart `bash memwatch.sh`.
- **GPU_STATUS: FREE** (10-01 13:59 PDT, Will: "we've lost more time" while he sets up the lean box). Will reclaims the
  card by saying so: then `touch llmspec/STOP` (halts the queue within a minute, resumable) and set this line to
  `GPU_STATUS: HELD_FOR_WILL`. ext_queue LAUNCHED (A0 → 10000 first).
  The A0r scoring extraction finishes on its own (~14:30) and then the GPU is Will's.
- **ext_queue HELD, NOT STARTED** (`armb/ext_queue.sh`; re-launch with `setsid nohup ./ext_queue.sh > ext_queue.log 2>&1 &` when GPU_STATUS: FREE; it was:
  Q4EXT_PREREG.md (3e52ea3): A0 → 10000, M0s1 → 10000, M0s3 (Muon, seed-2 init, standard order) → 3000; logs
  armb/train_<arm>_ext.log; DESCRIPTIVE only. ~16 h + 16 h + 7 h. STOP halts; re-run the script to resume.
- **arm-B EXPLORATORY look DONE 10-01 (MF_EXPLORE_IMPRESSIONS.md; results/mf_explore/):** bulk octaves Porter–Thomas-like
  (supports neither hypothesis, as declared); the DEEPEST octave of MLP_IN/MLP_OUT on the NEURON side localises late in
  training (log T/N +8.9 / +7.4 at 1.4B; +5.5 ± 3.2 / +4.2 ± 2.5 at 410M), q = 4 only (q = 2 +0.1), null at Haar; seeds 3/4
  LOSE it after their loss spikes; no head-scale structure in bulk vectors beyond the norm profile. Design notes for arm A in §6.
- **spot arm-B re-extraction DONE 10:06** (40 GB in spot:~/llmspec_mf/cache/mf, 1.4B + seeds 1–5). Exploratory
  analysis script (mf_explore.py) being written by an agent; it will RUN ON SPOT (C: has 38 GB free) and only summaries
  come back. Impressions only, no verdicts.
- **spot: arm-B re-extraction RUNNING** (launched 10-01 03:53 PDT in tmux `claude` on spot; `~/llmspec_mf/run_mf.sh`;
  log `~/llmspec_mf/mf_run.log`; output `~/llmspec_mf/cache/mf/<model>/<rev>/L*.npz`; code `~/llmspec_armb/code/llmspec`
  = dbcf7f8 + cdad297). Order: pythia-1.4b (26 revs) → pythia-410m-seed1..5. 6 workers × 8 threads, nice 10. Resumable
  (re-run the script); STOP = `touch ~/llmspec_armb/code/llmspec/STOP` on spot. Sealed extractor: stage3_extract_mf.py
  (what it banks is in its docstring); verifier verify_mf_extract.py PASS locally and on spot (red path fires).
  **Held-out runs (seeds 6–9, 410M-std, 1B, 70M, Arm B) are NOT in the queue.** Pull results to
  cache/mf/ locally when done (≈ 14 GB per 1.4B, ≈ 6 GB per seed — check C: first).
- **Q4EXT descriptive DONE 10-03 10:59 (ARMB_FINDINGS §9; results/armb_q4ext_descriptive.json):** AdamW Q/K stable rank
  bottoms near 3000 and rises to 17/15 by 10000; Muon plateau 38/35; Muon σ₁ grows but stays below AdamW's Q/K σ₁ at 10000;
  M0s3-vs-M0s1 spread one draw: median 2.4 %, 17 % of cells > 10 %. No verdict change. GPU: no job of mine running.
- **OLMO_PREMISE SEALED + RUNNING 10-03 ~18:00 (jobs/olmo_premise.log; results/olmo_premise.json):** A1 (lit v2 + HF card:
  ingredients 1–2 exploratory, T4 on ingredient 3; dip conservative; ACR unavailable) + A2 (folded branch NOT LICENSED by its
  own known answer: gain-folded Gaussian reads multimodal 64 %; raw branch primary; gain column descriptive). CPU, ~10 min.
- **Divisor A4 v2 (stratified permutation, CONFIRMATION RUN) SEALED + RUNNING (jobs/divisor_strat.log):** fixed observed
  baseline; real counts: no f(count) feature can create the comb (verifier). Will's order: lit v2 read ✓ → push (Will) →
  OLMO_PREMISE ✓ → A4 ✓ → arm A last.
- **Divisor A3 DONE 11:20 (DIVISOR_FINDINGS §7):** can-fire read 0.097 vs the sealed 0.10 → INAPPLICABLE by the letter (the
  log-frequency profile is mostly magnitude decay); residualisation reported descriptively: SURVIVES ×4 classes ×3 models, z
  unchanged/higher, linear log-frequency explains 16–18 % of the matrix. **A4 DRAFTED for Will** (detrended comb covariate).
- **Divisor Harmonics v0 PRIMARY READ DONE 10-03 09:30 (divisor/DIVISOR_FINDINGS.md):** gates PASS ×3 models; numbers H1 HOLDS
  d=2,4,5,10 (z 28/12/41/9 at 1.4B; replicates 410M, 70M); months NOT RESOLVABLE (power: ≥40 % excess needed); hours H0 HOLDS
  d=3,4, bets NOT RESOLVABLE, parity d=2 positive 3/3 (not rejected). A0 trajectory: period 5 first (step 256), 10 & 2 by 1500,
  4 by 6000; hour parity rejected from 3000. PENDING on spot: first-token + per-layer descriptive passes (A2 fix), wait armed.
- **Q4EXT descriptive extraction LAUNCHED 10-03 ~08:50 (armb/q4ext_run.sh → q4ext_run.log):** q4ext_extract.py (sealed B4
  extractor with stops extended at runtime, as a0r_score.py; A0/M0s1 70 new ckpts each, M0s3 161; then DW0 pass: ‖W_t−W_0‖_F,
  ‖W_t‖_F, σ₁ per layer/type at the 100-step cadence) then q4ext_descriptive.py (results/armb_q4ext_descriptive.json,
  plots/armb_q4ext_*.png; M0s3-vs-M0s1 spread = ONE draw). Hours of GPU; STOP halts; re-run the script to resume.
- **ext_queue DONE 10-03 08:23 (Q4EXT: A0 → 10000, M0s1 → 10000, M0s3 → 3000 all exited 0; M0s3 169 ckpts .ok on spot).** GPU is
  FREE per the flag; next main-arc GPU item = the Q4EXT descriptive extraction (b4_extract on the extension checkpoints,
  Q4EXT_PREREG.md) — not launched yet. Divisor extraction (minutes) runs first: chain_extract.sh relaunched 08:3x after its
  first attempt self-matched `pgrep -f 'python3 train.py'` against the launching shell's command line (pattern now anchored
  to the venv binary; the pgrep self-match lesson again).
- **Divisor Harmonics v0 (Will's side-project brief, briefs/DIVISOR_HARMONICS_V0.md) SEALED 10-03** — divisor/DIVISOR_PREREG.md +
  templates.py (frozen) + divisor_extract.py / divisor_spectrum.py / verify_divisor.py (PASS, red paths fire); tokenisation audit
  (hours: 3 tokens, shared final '00' — sealed primary = last token, first token = declared secondary; Will may amend before
  extraction). Weights fetched (step143000 ×3), 23 A0 ckpts at ~/llmspec_div/A0. divisor/chain_extract.sh ARMED: runs after
  ext_queue exits, only if GPU_STATUS: FREE and no train.py; minutes of GPU. Then: rsync acts → spot ~/llmspec_div, run
  divisor_spectrum.py (numpy; nulls B=4000, shuffles 10k) in tmux claude; DIVISOR_FINDINGS.md.
- **PolyPythias seeds 3/4 PROVENANCE SETTLED 10-03 03:40 (polypythias_restart_check.py): post-spike checkpoints are RESTARTS**
  (seed 4 @128k ≈ its own step 0–512, corr 0.97; seed 3 @96k ≈ a partially trained restart; seed 1 control continues). Lead 6
  WITHDRAWN; memo §2, MF §3, README corrected; seeds valid through 64k (3) / 96k (4) only.
- **BULK_INIT_OVERLAP DONE 10-03 02:13 → verdict MIXED for both rows (BULK_INIT_OVERLAP_FINDINGS.md):** normal runs leave
  the init smoothly (ρ_bulk 0.24 / 0.19 at 143k; E_init 0.5 % / 0.3 %; α̂ > α_wd — red flag fired the other way); by type O
  lowest (0.06; MP-shape ≠ init memory), MLP_IN highest (0.73); init memory falls with depth into the spectrum. **Seeds 3/4:
  late checkpoints re-correlate with the init (seed 4 at 128k: ρ 0.99, α̂ 0.97) = early-training signature → PROVENANCE
  ANOMALY; polypythias_restart_check.py RUNNING on spot (log ~/llmspec_bio/restart_check.log) to settle restart/mislabel.**
  Lead 6 and the MF §3 'lose it after the spike' remark are suspended pending that check.
- (done) **BULK_INIT_OVERLAP real run RAN on spot (10-02 22:53, tmux claude, ~/llmspec_bio/run_bio.sh; log bio_run.log;
  results ~/llmspec_bio/results; 1.4B then seeds 1–5, 26 revs + step1; ~1–1.5 h):** prereg 91e1308 + A1 b42d2c3; code sealed
  063b6d6. After: pull results → bulk_init_overlap_verdict.py → BULK_INIT_OVERLAP_FINDINGS.md (words INIT-DOMINATED /
  LEARNED / MIXED per row; continuity gate first).
- **LIT REVIEW v2 (Will 10-02):** A1–A9 + V in llmspec/lit/v2/ (committed; the v1 report and critique were LOST with the
  reboot — scratchpad is volatile); C (critic) running; S (synthesis) next. Pre-read amendments already applied:
  BULK_INIT_OVERLAP A1.
- **A0 EXTENSION DONE 10-02 10:12 (step 10000; 70 checkpoints every 100 past 3000 on spot:ckpt/A0, sha-verified).
  M0s1 extension RUNNING since 10:12 (resumed 3000 → 10000; M4 off as sealed); M0s3 follows. NEXT GPU ITEM after the
  queue: Q4EXT descriptive extraction (b4_extract.run_arm with stops extended at runtime, as a0r_score.py does) for
  A0/M0s1/M0s3 + a descriptive plotting script committed before it runs (Q4EXT_PREREG §2). Local staging/A0 bank for
  the extension does not exist yet (cache/armb/A0 ends at 3000).**
- **pdyn attribution controls DONE 10-02 ~08:10 (PDYN_FINDINGS §6; results/armb_pdyn_c9):** density drift (C9) does NOT
  reproduce the C(x) departure (43/48 stay at C1; a 50× planted drift does fill the dip); a β=1 process with SHORT velocity
  memory (OU τ_v 5–10 steps) REPRODUCES C(x) and curvature (44–45/48). P2 word stays FAILS-as-sealed; attribution = wrong
  C1 time structure, not drift, not (needed) non-generic motion. Amendment A1 (driver-matched C1 with τ_v fixed from the
  optimiser's momentum before the re-read) proposed for Will's seal.
- **pdyn PHASE 1 DONE 10-02 07:05 (armb/PDYN_FINDINGS.md):** P2 FAILS on W2 for A0 AND M0s1 (36/36; velocity Gaussian
  HOLDS, C(x) FAILS everywhere with a shallower-than-β=1 dip, curvature mixed/PROVISIONAL); reproducible on A0r to 3 digits.
  P3 HOLDS (Muon higher effective rank, weaker top-16 mass; replication). P5 FAILS PROVISIONAL (~2k events/window at
  x_step≈0.5 — aliased). ATTRIBUTION OPEN: next CPU controls C9 (C1 + slow density drift) and a driver-matched C1 before any
  interpretation. Results in results/armb_pdyn_phase1 (parts/ not committed).
- (done) **pdyn PHASE 1 RAN (10-02 05:45, this box CPU, nice, 8 workers, ~1 h):** `armb/pdyn_phase1.py` on the banked arms
  A0 A1 A2 M0s1 M0s2 A0r → results/armb_pdyn_phase1/ (run.log; summary.json at the end). Prereg PDYN_PREREG.md (4405874);
  runner committed before the run. Resumable (re-run the same command).
- **Parametric-dynamics phase 0 SEALED 10-02 ~05:00:** armb/pdyn_m2.py (unfold → velocities, C(x), ZD curvature; kde(32),
  local ⟨v²⟩, windows split at 500), pdyn_m3.py (Hungarian matching, Davis–Kahan gap rule, crossings), pdyn_calib.py
  (C1 smooth β=1 + literal DBM, C2 β=2 + Poisson, C3, C4 fp32, C5, planted crossing), verify_pdyn.py (PASS; red path
  fires), PDYN_PIPELINE_NOTES.md (ZD normalisation CONFIRMED via Fyodorov 1108.0950; discrimination sample sizes; cadence
  tail loss). Phase 1 (re-analysis of the banked arms) may start on spot CPU: NEXT CPU ITEM once Will OKs the PDYN prereg
  wording (P1–P6 as in the addendum; curvature/M3 PROVISIONAL at bank cadence).
- **CRASH 10-02 ~00:03 (WSL/host; Will: another build job shares the box 03:15–~04:15, CPU only).** A0 extension died at
  ~step 6800; RELAUNCHED 03:15 from resume.pt 6750 (ext_queue.sh, pid armb/ext_queue.pid); queue → M0s1 → M0s3 unchanged.
  Hourly alarm 5ca8cfb7 survived; waits re-armed; memwatch up. pdyn verifier: normal PASS (CHECKRUN 10-01 23:5x);
  red path re-running alone after two 30-min background kills under CPU contention.
- **M4 hook A/B (10-01 22:20): NOT within the floor** (same resume.pt, 100 steps: weights median 3e-3 rel diff, loss
  diverging from the last bit); hook kept in train.py, OFF (no armb/M4_ENABLE); not enabled for M0s1/M0s3; off/off control
  queued for the pilot phase. results/armb_m4_ab.json; Q4EXT_PREREG Amendment 1.
- **Arm B ADDENDUM (Will 10-01 21:40): parametric spectral dynamics** — armb/PARAMETRIC_DYNAMICS_PLAN.md. Phase 0 (CPU,
  spot): M2/M3 pipeline + calibrators C1–C5 with red paths; phase 1 (CPU): M1/M3/M5/M6 on the banked dense arms + A0r as
  the floor pair; phase 2 (GPU, after the Q4 ext): AdamW + Muon pilots, 2000 steps, per-step σ side-worker + M4 Gram hook
  (sealed amendment); phase 3 production = Will's budget call. Timely option: seal the M4 hook before M0s1's extension
  starts (~05:00 10-02) — needs Will's word.
- **OLMo plan (1) step 0: OLMO_PREMISE_PREREG.md DRAFTED (needs Will's seal = commit on his word):** gain-folded dip tests
  (raw vs diag(g)·W_Q), a row-norm confusable licence class, per-head predictor table, the three ingredient finals as the
  endpoint (seed replicates), dead-row depth vs the weight-decay bound; verdict vocabulary declared. CPU/lean-box work.
- **Arm A:** prediction figure + prereg SKELETON committed (e224e29) BEFORE any arm-A code; Will to fill `[TBD]`s and seal.
- **A0r RUNNING** (launched 2026-10-01; PID in armb/A0r.pid; log armb/train_A0r.log; memwatch PID 2700200, log
  logs/memwatch_a0r.log): identical-config rerun of A0, SEALED in armb/A0R_PREREG.md (94d18ae) as the paired-run
  divergence floor for Q1 (Will 10-01). ~6.8 h. Checkpoints → spot:~/llmspec_armb/ckpt/A0r/. Resume: re-run
  `train.py A0r` (resume.pt in armb/staging/A0r). When done: wrapper that scores A0r through the SEALED Q1 pipeline
  (substituting only the arm name), committed BEFORE any A0r data is read; verdict table in A0R_PREREG §2.
- **10-01 review round** (two agents: critic + lit review; reports in the session scratchpad, not the repo):
  - 9230df4 headers no longer "unpushed"; 2a4262c corrections commit; 94d18ae A0r seal.
  - **OLMo `main` is a DIFFERENT RUN** from the checkpoint lineage (olmo_main_provenance.py, DIFFERENT_RUN): the
    "fade by main" is withdrawn; stage-1-end stands; aim-1 deferral re-opened; the lineage endpoint is
    stage2-ingredient3-step23852-tokens51B (ingredients 1–2 = seed replicates of the same anneal; stage 2 changes LR
    and data mix together).
  - Pre-registered LOWER/UPPER-band ⟨r̃⟩ reported late (STAGE3_FINDINGS §16; stage3_band_report.py): per-head Q/K
    upper band −0.07…−0.12 in all 10 410M runs; orders with d_head; interpretation post hoc.
  - Wording fixes per the critique (README, FINDINGS_MEMO rows 1/3/5/6/11/12/14/16, STAGE3 §3/§8/§11).
  - **Bulk-band singular-vector statistics (pt_ks_*/ipr_* band=bulk, all runs; Arm B cache) remain UNREAD by anyone.**
    Will's draft hypothesis (unconfirmed): "the noise-like bulk carries smooth, distributed function that spectral
    statistics can't see" — vector statistics can only refute it (localisation); the first test must be FUNCTIONAL
    (critique_v2 §(iii) plan 2: pure rotations vs value reorders at matched ‖δW·X‖, antithetic ± pairs, a
    co-adapted-random-bulk calibrator, a planted red path).
  - **Bulk-vector arm SCOPED by Will 10-01** (briefs/README.md, verbatim): A = SEALED spectral-scale self-similarity
    of bulk function (k-sweep, ‖δW·X‖-matched, antithetic, LR power/broken/cutoff, red-path plants, min-decades rule);
    B = EXPLORATORY multifractality of bulk singular vectors on 1.4B + seeds 1–5 ONLY (seeds 6–9 and other sizes
    stay UNREAD); shared co-adapted random-bulk calibrator.
  - **Will's GPU order (10-01):** (1) A0r [running]; (2) Q4 extension past 3000 + a third Muon seed; (3) the
    bulk-direction calibrator last. OLMo premise check (gain-folded dip on stage-1 end + the three ingredient finals,
    row-norm confusable, dead-row depth) to be SEALED before any of it is read.

## 4-old. Running now (09-30)
- The B4 chain is COMPLETE (22:29). Results: results/armb_b4_{q1,q2,q3,q4,bulk}.json.
  Memo: armb/ARMB_FINDINGS.md (committed with the CHECKRUN line). B4 cron 6c2c8221 deleted.
  - Bulk: the sealed per-arm verdict is FINDING_CANDIDATE PRESENT, status NOT ESTABLISHED. The VIOLATED rate (0.83%)
    is below the null's 1.29% exceedance at |d| > MDD, and the sealed rule has no multiplicity correction.
    Any re-read needs a new pre-registration (memo open lead 8).
- **09-30:** Will reviewed ARMB_FINDINGS. The final form is agreed (§0, d728603). Revisions 712d1c4 (descriptive,
  armb/b4_post_descriptive.py). Open lead 9 (A1 at the 0.5% row) stays OPEN by Will's call: if it is ever run, it
  goes post hoc in its own section, never the verdict table.
- **09-30 FINDINGS_MEMO critique fixes (2f7dd6b):**
  - #1: 2 VIOLATED seed cells shown; per-head cells licensed on ⟨r̃⟩ only.
  - #3: lead with 13.3%, floors stated.
  - Arm B folded in (#12, #14–#16); §6 Open leads added.
  - **#11 DONE (6f64e3d):** G2c ran 09-30 00:5x–01:53, checkrun PASS, all 6 local conditions reproduced G2b.
    - The local shuffles are tiny (0.14 / 0.56 / 2.2% of the bulk shuffle's ||dW||), and a same-size same-subspace
      control also costs ~0. So the k-sweep neither supports nor contradicts the smooth, distributed reading.
    - STAGE3 §11's "functionally inert" reading is withdrawn with a dated note.
- **09-30 seed-1 identity check DONE: INCONCLUSIVE as sealed** (ARMB_FINDINGS §5b).
  - T is right-like and C1 (standard order) wrong-like, cleanly.
  - C2 (+1 shift) was a DEAD ARM: 127/128 batches are shared with T, so it could not read wrong. Its separability was
    not checked on the known-answer system before sealing.
  - Per A9, Q4 stands with the pairing caveat. The alignment follow-up was DECLINED by Will (09-30); no A10 exists.
  - armb/_seed1_cache deleted 09-30 (Will approved; the hashes stay in spot's steps.jsonl).
- **09-30 MERGED into main** (--no-ff; the first merge 458a697 was superseded by a second merge after the README and
  licensing, before anything was pushed). The Zenodo snapshot commit is the merge commit tagged
  `llmspec-2026-09-30`. Record its hash in the Zenodo metadata. Will pushes main to the Forgejo and GitHub.
- Licensing: code AGPL-3.0-or-later (repo LICENSE); llmspec results and write-ups CC-BY-4.0 (llmspec/LICENSE-RESULTS.md).
  Internal details (paths, hostnames) are LEFT as-is by Will's decision (09-30).
- Nothing running.
- Will's order after it: publish (Will pushes the Forgejo + GitHub; Zenodo snapshot at the same commit), then the
  Arm B open leads.
- **Next (Will's call):**
  - ARMB open leads 1–8.
  - Seed-1 identity check (queued; criteria to be sealed before it runs).
  - Hosting: Will's local Forgejo (Combust/ARS); all 13 branches pushed by Will 09-30. Will pushes manually; I never push. Zenodo on Will's go.
  - Narrow-scope spot key.
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
- **09-29 18:55 extraction COMPLETE; ANALYSIS RUNNING** (`b4_analyze.py all` under checkrun, PID 780406): `seal check OK (19 files)`;
  q1–q4 written 18:55–18:56; bulk stage at 221/921 checkpoints at 19:49 (~4/min, ETA ~22:30). Stdout goes to checkrun's tmp file.
  - `armb/ARMB_FINDINGS.md` DRAFTED from q1–q4 (bulk section PENDING; uncommitted until the bulk JSON + CHECKRUN line exist).
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
5. Zoo seating of the G7 classes: DEFERRED explicitly at the 2026-09-30 merge of llm-spectra into main (Will: seat it in the merge or defer it in NOTES; deferred). Not seated because the G7 classes are DATA-DEPENDENT: each class draw (stage2_g7.draw) is mapped through peak mixtures fitted to real OLMo stage-1-end Q heads (fit_mixture on results/g7_targets_olmo_stage1end_Q.npz). Seating them properly is a shared-module design, not a merge-time edit. It needs: (1) a SEPARATE list (e.g. PEAKED_SPECTRUM_CALIBRATORS), NOT EXTENDED_CALIBRATORS, so the 6 existing panel consumers (extractor_distinctness, run_phase20_5_distinctness_revalidation, cross_substrate/rf_decoy_battery, cross_substrate/aq_floor_sweep, comb/verify_comb, phase22a/verify_calibrators) do not change; (2) the targets npz pinned by sha256, failing closed; (3) CALIBRATOR_TIERS entries (construction-defined); (4) _schema_self_check extended to the new list; (5) a regression run of the existing consumers.
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
