# Q4 extension + third Muon seed — SEALED before any step past 3000 is trained (2026-10-01)

Will's GPU order (10-01): A0r → **Q4 extension past step 3000 + a third Muon seed** → bulk-direction calibrator. This seal
is written by CC under the no-stalling rule (Will can veto any item; nothing here changes a sealed verdict).

## 1. What runs (in this order, GPU, after the A0r scoring run exits; `armb/ext_queue.sh`)
1. **A0 → step 10000**: `train.py A0 --stop 10000`, resuming from `staging/A0/resume.pt` (step 3000; same code path,
   same data order continuing at update 3001; checkpoints every 100 steps past 3000 on the sealed grid
   `q1_licence.grid`, uploaded to spot:`ckpt/A0/` with sha256 .ok markers as before). The B-G1 puller stays on (A0 only);
   all its verdicts are PASS and it only acts on a FAIL.
2. **M0s1 → step 10000**: `train.py M0s1 --stop 10000`, resuming from `staging/M0s1/resume.pt` (Muon hybrid v1, unchanged).
3. **M0s3 → step 3000**: a NEW Muon arm, `INIT = EleutherAI/pythia-70m-seed2` step 0, the STANDARD Pythia batch order,
   W = 1430. It varies the INIT only (like the B-G1 seed band), unlike M0s2 which varies init AND order (seed-1 batches).
   Chosen because a seed-2 batch order would first need the seed-2 index files and a multi-hour materialisation on spot;
   this is disclosed, not hidden. If Will wants the order varied too, M0s4 is the name for that run.
- Stops are chosen so that the runs are useful wherever they are cut: every 100 steps is banked. 10000 ≈ 7% of Pythia's
  schedule (LR still near peak: cosine to 143k). Est. ~16 h each for 1–2, ~7 h for 3. `llmspec/STOP` halts; re-running
  the queue resumes.
- Disk: ~0.29 GB per checkpoint → ~20 GB per extended arm on spot (174 GB free).

## 2. Reading rule (declared now)
- **DESCRIPTIVE ONLY.** No verdict in FINDINGS_MEMO row 16 or ARMB_FINDINGS §5 changes on this data. Q4's "endpoint past
  3000 unknown" stays until a separate sealed test names a statistic, a window and a threshold.
- Banked and plotted per arm, per matrix type, every 100 steps: stable rank, σ₁ (Kimi K2 risk: σ₁(W_Q/W_K) growth under
  Muon), ‖W − W₀‖_F, the LR integral, and the Q/K stable-rank trajectory with the step-3000 values marked.
- M0s3 vs M0s1 at the shared grid ≤ 3000: the Muon-side spread (one pair → ONE draw of spread, not a distribution); it
  is reported beside Q4's "123/368 cells" as the Muon-side analogue of the AdamW seed SD. No cell count is re-read.
- Extraction and plotting through the sealed B4 extractor (b4_extract.run_arm with the arm's stop extended at runtime,
  as a0r_score.py does) and a descriptive script committed before it runs.
