# Arm B addendum — parametric spectral dynamics (AdamW vs Muon): plan integration (2026-10-01)

Source: Will's addendum, https://claude.ai/code/artifact/33c76b0f-c2cc-4965-9bec-a5e7ebfb497a (doc 7Pr3SrJVDs8MyGayyBc2tq,
rev 10, read 2026-10-01 21:40). The addendum's measurements M1–M6, predictions P1–P6, calibrators C1–C8 and run design are
adopted as written; this file maps them onto what exists, orders the work, and records CC's review notes. Nothing here is
sealed; the pre-registration (P1–P6 + C1–C8) is a separate file to be sealed before the first pilot step is trained.

## 1. What already exists (no new training needed)
- **Dense Arm B bank** (`cache/armb/<arm>/step*/L*.npz`, sealed B4 extraction from fp32 masters): A0 161, A1 181, A2 257,
  M0s1 161, M0s2 161 checkpoints; per layer per matrix: all singular values fp64 (`sig_M`), per-head σ (`sighead_M`),
  top-32 left/right vectors fp32 (`U32_M`, `V32_M`), rms, Frobenius-derivable. Cadence: every 10 steps over 0–500 (+ the
  log steps), every 25 over 500–3000, A2 every 10 over 1000–2200 (B1a-A8), every 100 past 3000 (extension running).
  → **M1, M5, M6 run on this bank at once, on CPU.** M3's event list and M2's curvature from the bank are **PROVISIONAL**
  until the per-step pilot exists: C6 needs a dense reference to downsample, and until then the only aliasing estimate
  is synthetic (it assumes DBM-like rates, which is what is under test). Velocity on the bank is reasonable; curvature
  (a second difference whose tails come from near-crossings a 10–25-step grid can skip) and edge crossings are not.
  The grid changes cadence at step 500 and 0–500 is warmup (the least stationary window): analyse [0, 500) and
  [500, 3000] separately, never pooled.
- **A0r** (identical-config rerun, 161 checkpoints) = the measured floor for BETWEEN-RUN comparisons (AdamW vs Muon):
  dynamical divergence of two trajectories from GPU nondeterminism, growing over training. It is NOT the velocity floor
  along one trajectory; that is C4, measurement noise, which for this bank (fp32 masters) must be an **fp32 round-trip**,
  not the addendum's bf16 version (which would overstate it).
- **Q4 extension** (running: A0 → 10000, then M0s1 → 10000, M0s3 → 3000; every 100 steps) extends the time axis at
  near-constant lr (quasi-stationary windows the addendum asks for).
- Snapshot results that P1/P3 lean on: bulk ⟨r̃⟩/q at β = 1 (Stage 3, seeds), Muon higher stable rank and delayed Q/K
  collapse (Q4), the 70M bulk NOT ESTABLISHED at 0.010 (ARMB_FINDINGS §6).
- CPU box spot (56 cores, 117 GB) for all fp64 SVD work (`stage3_extract_mf.py` pattern); `cache/mf`-style banking.

## 2. Phases (order; GPU only where marked)
0. **Calibrators + pipeline first (CPU, now).** Build M2 (unfolding to unit spacing; time rescaling by RMS level
   velocity; velocity distribution, Simons–Altshuler C(x), Zakrzewski–Delande P(k)) and M3 (sign alignment, Hungarian
   overlap matching, Davis–Kahan gap rule, ambiguous-match flags) and run them on C1 (synthetic β = 1 DBM, same shapes and
   sampling), C2 (β = 2 and Poisson walks: witness-must-fail), C3 (shuffled order), C5 (sign flips). Verify the
   Zakrzewski–Delande normalisation against Fyodorov's open-access review (arXiv 1108.0950), which restates it (the 1993
   paper may be paywalled), not memory (addendum's own flag). `verify_*.py` with `--redpath`.
1. **Re-analysis of the banked arms (CPU, exploratory):** M1/M3/M5/M6 on A0/A1/A2/M0s1/M0s2 (+ A0r as the floor pair);
   M2 velocities at the existing cadence, per window ([0,500) warmup at 10 steps; [500,3000] at 25); curvature and the
   M3 event list tagged PROVISIONAL (see §1); a first, aliasing-exposed estimate of the RMS level velocity and mean
   edge-crossing time, superseded by the pilot's. Impressions, no verdicts.
2. **Pilots (GPU, after the Q4 extension; or the lean box with the micro-batch caveat):** one AdamW (A0 config) and one
   Muon (M0s1 config) run of 2000 steps with (a) per-step fp64 σ + top-16 vectors banked by a CPU side-worker (the
   trainer copies weights to host memory each step; 36 SVDs of ≤ 2048×512 fp64 ≈ 2 s on the 5900x vs 7.5 s per training
   step, so it keeps up; full weights only every 100 steps) and (b) the **M4 hook**: per step, the Gram matrix of the last
   W = 10 flattened updates per matrix type and whole-model (10 dot products per step, on-GPU) → k* and gap ratio offline.
   Both are read-only instrumentation added to `train.py` under a sealed amendment. The pilot ALSO validates M3 (whether
   the 10/25-step grid resolves edge crossings is unknown until per-step data exist). ≈ 4.2 h GPU each at 70M.
   **M4 preconditions (Will):** measured peak memory + buffer fits with margin (else bf16 or pinned CPU buffer); the hook
   cannot kill training (any exception disables it and training continues); an A/B from the same checkpoint with and
   without the hook gives identical weights (or within the nondeterminism floor). All three verified, or the hook is off.
3. **Production (Will's budget call):** 3 seeds × 2 optimizers + one lr-matched control pair = 8 runs, unless an existing
   arm serves as half the pair (A0 is AdamW at Pythia's lr, M0s1 Muon at its RMS-matched lr; neither is lr-matched to the
   other, so the pair is 2 new runs unless Will declares one of them the anchor). At 70M ≈ 6.8 h per 3000 steps →
   ~55 GPU-hours for 8; the lean box can take the extraction and, with the micro-batch change disclosed, some training.
- **Timely option (Will's call):** the M4 hook could be sealed before M0s1's extension starts (~05:00 10-02 after A0
  reaches 10000) so the Muon extension logs the trajectory Gram at no GPU cost; A0's AdamW counterpart would then come
  from the AdamW pilot. CC will not modify the running trainer without Will's word (method-change rule).

## 3. CC's review notes on the addendum (for Will; none blocks phase 0–1)
- **M2's unfolding is the whole game** (strip outliers BEFORE unfolding). Singular values of W are not a stationary spectrum: the Frobenius norm, the
  spike, and the lower-decile shape all drift (STAGE3 §8, lead 4). Unfold per checkpoint against the matrix's own
  smoothed density (the stage2_g7 kde(4) machinery already does this for q) and report velocities of the UNFOLDED
  levels; otherwise the collective drift reads as velocity (the addendum's warning 11, made concrete).
- **Paired divergence is the velocity floor.** A0 vs A0r showed paired runs diverge by ~2% in relative curve terms over
  3000 steps; per-level eigenvalue trajectories will diverge too. C4 (bf16 round-trip) is a lower floor than the real
  one; use A0 vs A0r as the measured same-configuration floor for M2/M3 (one draw, as always).
- **Edge crossings in a 70M model are few.** Six layers × 6 matrices × top-16 at 10–25-step cadence: the event count
  for P5/P6 may be tens, not thousands; the ARS classification needs its n stated before any class word.
- **P2 is the open question, as the addendum says.** CC's prior: the bulk velocities WILL look β = 1, so the informative
  outcome is a failure — but the logic runs both ways (Will): heavy unfolding can MANUFACTURE a pass. So C2's β = 2 and
  Poisson witnesses go through the identical unfolding and must fail visibly, or a P2 pass means nothing; and a failure
  must not be an unfolding or cadence artefact (C1 at the real cadence, C6 once the pilot exists).
- **P3 is partly known** (Q4; Moonlight): state it as a replication at this scale.
- **The bottom of the MLP spectrum** (MF_EXPLORE_IMPRESSIONS §3: neuron-side localisation late in training, lost after
  loss spikes) is outside "bulk eigenvalue-only" statistics but is exactly a dynamics question; keep it as an M6-style
  descriptive beside the edge events.
- Scope stays ≤ 125M and excludes OLMo, as the addendum says; the OLMo premise check (OLMO_PREMISE_PREREG.md) is a
  separate CPU item.

## 4. Deliverables and where they go
- `armb/pdyn_*.py` (pipeline + verifiers), `armb/PDYN_PREREG.md` (P1–P6, C1–C8, cadence rule, sealed before phase 2),
  `armb/PDYN_FINDINGS.md`; results under `results/armb_pdyn_*`; FINDINGS_MEMO rows added only through the sealed file.
