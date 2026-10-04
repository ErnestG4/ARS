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

## Amendment 1 (2026-10-01 22:30): M4 trajectory-Gram hook present but OFF
- `train.py` gained `M4Gram`, a read-only per-step hook (W = 10 Gram of flattened updates per matrix type + their exact
  sum; fp32 buffer ~2.8 GB; any exception disables it; enabled ONLY by `LLMSPEC_M4=1` or the marker `armb/M4_ENABLE`).
  Default OFF; no marker exists; nothing in this queue runs with it.
- Will's three preconditions for turning it on for M0s1's extension were tested (`armb/m4_ab.sh`, `m4_ab_compare.py`,
  `results/armb_m4_ab.json`): (1) memory: peak 10172 MiB with the hook vs ~9300 without — fits; (2) the hook cannot kill
  training: no exception in 100 steps, 100 rows written; (3) A/B from the same resume.pt (step 6000, 100 steps): NOT
  identical — losses equal to printed precision through step 6004, then diverging to median |Δloss| 8.2e-4, max 1.2e-2
  at step 6100; weights median 3.3e-3 relative Frobenius difference, max 2.6e-2 (layer 3 attention.dense). The only
  measured floor (A0 vs A0r: bit-identical for 100 fresh steps) is not met, so the "read-only" claim is NOT confirmed:
  the cause (allocation-dependent kernel selection vs resumed-run nondeterminism) is undetermined; an off/off control
  from the same resume.pt is queued for the pilot phase. **M4 is not enabled for M0s1 or M0s3.** A0 resumed at 6000
  after the A/B (no steps lost); the queue continues unchanged.

## Amendment 2 — SEALED by Will 2026-10-04 as DESCRIPTIVE, with his fixes (written AFTER the descriptive Q4EXT run was
## read, ARMB_FINDINGS §9: every column below is a post-hoc DESCRIPTIVE addition; nothing here is a test)
Source: lit/v2 S §5 / C §104 / A6 items 1, 2, 7 and C §37.
1. **σ₁ ceiling and e-fold marker — MUON ONLY (Will's fix)** (A6 item 1, derivation PARTIAL): the fixed point
   ‖W‖₂* = 0.2·√max(A,B)/wd follows from Muon's update scale (0.2·√max(A,B) × an orthogonal update, Moonlight scaling)
   and applies to the Muon arms only; it is drawn on the Muon σ₁ panels and labelled Muon-specific. **wd from the sealed
   Arm B config: 0.1** (ARMB_PREREG.md:35 "weight decay 0.1, decoupled"; armb/muon.py weight_decay=0.1; the Pythia
   gpt-neox config fetched by lit v2 A2 reads `weight-decay 0.1`) — Will's note said "not 0.1", but the sealed value IS
   0.1, so it is used and this is flagged for him. Ceilings: 512 × 512 (Q, K, V, O): 0.2·√512/0.1 = 45.3; MLP 2048 × 512
   and 512 × 2048: 0.2·√2048/0.1 = 90.5. e-fold (lr·wd)⁻¹ = 1/(1e-3 · 0.1) = 1.0 × 10⁴ steps at the peak lr 1e-3 (the
   schedule is near peak through 10 000). Reading
   (descriptive): does σ₁ bend toward a ceiling of that order by 10 000, or grow linearly? The derivation is CC's, not
   the paper's, and is labelled PARTIAL on the plot.
2. **σ₁ factorised (Muown, A6 item 2):** σ₁ = row-magnitude × row-coherence per matrix, every 100 steps, A0 vs M0s1.
   Muown predicts that under Muon the drift is row-magnitude-driven with coherence flat.
3. **Per-head σ₁(W_Q^h W_K^hᵀ)** (Kimi K2's QK-clip quantity): per head, per layer, every 100 steps, both arms.
4. **Stable rank of W − W₀** (Kang et al. 2602.06385): every 100 steps, per type, A0 vs M0s1 (and M0s3 ≤ 3000).
   Kang's prediction: incremental rank growth under AdamW, none under Muon (uniform spectral growth). The DW0 pass
   banked ‖W−W₀‖_F only; this needs an SVD of W−W₀ per checkpoint, so a re-pass over the 111 + 111 + 41 checkpoints on
   spot (CPU, numpy, ~1 h; the weights are there).
5. **Seed-2 init gate — RUNS FIRST, before any M0s3 spread is quoted (Will's fix)** (C §37, pythia issue #203): Q4EXT item 3 says M0s3 "varies the INIT only" relative to M0s1. That
   holds only if `pythia-70m-seed2` step 0 is a distinct initialisation from `pythia-70m` step 0. Gate: elementwise
   correlation of the two step-0 uploads per matrix (and seed1's, M0s2's init) — DISTINCT iff |corr| < 0.05 on every
   matrix; otherwise the one-draw Muon spread is relabelled "same-init rerun spread" (an order/nondeterminism floor, not an
   init spread). Cheap (three small downloads).
6. **Row 16 at n = 2:** the Q4 statement is re-expressed as a reference-band statement — where do the two Muon runs sit
   relative to the band of the ten AdamW seed runs (pythia-70m-seed1..9 + pythia-70m, banked in B4 refs) at the shared
   steps — beside the existing 123/368 count.
Order: item 5 (gate) → items 2–4 (one pass over the checkpoints, GPU while GPU_STATUS: FREE, as the DW0 pass; the
weights are on spot, streamed sha-verified) → items 1 and 6 (plotting). `armb/q4ext_amend2.py` (committed before it runs).

