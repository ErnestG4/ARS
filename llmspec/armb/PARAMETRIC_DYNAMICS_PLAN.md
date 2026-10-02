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
  → **M1, M3 (top-16 ⊂ top-32), M5, M6 run on this bank at once, on CPU**, with the cadence caveat (C6) stated.
- **A0r** (identical-config rerun, 161 checkpoints) = a free same-configuration pair for the estimator floor beyond C4:
  two runs differing only by GPU nondeterminism bound how much eigenvalue "motion" is run-to-run divergence.
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
   Zakrzewski–Delande normalisation against the paper, not memory (addendum's own flag). `verify_*.py` with `--redpath`.
1. **Re-analysis of the banked arms (CPU, exploratory):** M1/M3/M5/M6 on A0/A1/A2/M0s1/M0s2 (+ A0r as the floor pair);
   M2 at the 10-step cadence with C6 (downsampling) quantifying what the grid loses; first estimate of the RMS level
   velocity and the mean edge-crossing time → the production cadence rule ("< 0.1 expected crossings per interval").
   Impressions, no verdicts; this is what the addendum's pilot would measure, at coarser cadence.
2. **Pilots (GPU, after the Q4 extension; or the lean box with the micro-batch caveat):** one AdamW (A0 config) and one
   Muon (M0s1 config) run of 2000 steps with (a) per-step fp64 σ + top-16 vectors banked by a CPU side-worker (the
   trainer copies weights to host memory each step; 36 SVDs of ≤ 2048×512 fp64 ≈ 2 s on the 5900x vs 7.5 s per training
   step, so it keeps up; full weights only every 100 steps) and (b) the **M4 hook**: per step, the Gram matrix of the last
   W = 10 flattened updates per matrix type (10 dot products of the update vectors, on-GPU, negligible) → k* and gap ratio.
   Both are read-only instrumentation added to `train.py` under a sealed amendment; they do not change the numerics.
   ≈ 4.2 h GPU each at 70M.
3. **Production (Will's budget call):** ≥ 3 seeds per optimizer + one lr-matched pair, cadence from the pilot, dense early.
   At 70M ≈ 6.8 h per 3000 steps → ~50 GPU-hours for 7 runs; the lean box can take the extraction and, with the
   micro-batch change disclosed, some training.
- **Timely option (Will's call):** the M4 hook could be sealed before M0s1's extension starts (~05:00 10-02 after A0
  reaches 10000) so the Muon extension logs the trajectory Gram at no GPU cost; A0's AdamW counterpart would then come
  from the AdamW pilot. CC will not modify the running trainer without Will's word (method-change rule).

## 3. CC's review notes on the addendum (for Will; none blocks phase 0–1)
- **M2's unfolding is the whole game.** Singular values of W are not a stationary spectrum: the Frobenius norm, the
  spike, and the lower-decile shape all drift (STAGE3 §8, lead 4). Unfold per checkpoint against the matrix's own
  smoothed density (the stage2_g7 kde(4) machinery already does this for q) and report velocities of the UNFOLDED
  levels; otherwise the collective drift reads as velocity (the addendum's warning 11, made concrete).
- **Paired divergence is the velocity floor.** A0 vs A0r showed paired runs diverge by ~2% in relative curve terms over
  3000 steps; per-level eigenvalue trajectories will diverge too. C4 (bf16 round-trip) is a lower floor than the real
  one; use A0 vs A0r as the measured same-configuration floor for M2/M3 (one draw, as always).
- **Edge crossings in a 70M model are few.** Six layers × 6 matrices × top-16 at 10–25-step cadence: the event count
  for P5/P6 may be tens, not thousands; the ARS classification needs its n stated before any class word.
- **P2 is the open question, as the addendum says.** CC's prior: the bulk velocities WILL look β = 1 (universality of
  motion follows from the same perturbation structure that gives static β = 1), so the informative outcome is a
  failure; design the calibrators so a failure cannot be an unfolding or cadence artefact (C1 at the real cadence, C6).
- **P3 is partly known** (Q4; Moonlight): state it as a replication at this scale.
- **The bottom of the MLP spectrum** (MF_EXPLORE_IMPRESSIONS §3: neuron-side localisation late in training, lost after
  loss spikes) is outside "bulk eigenvalue-only" statistics but is exactly a dynamics question; keep it as an M6-style
  descriptive beside the edge events.
- Scope stays ≤ 125M and excludes OLMo, as the addendum says; the OLMo premise check (OLMO_PREMISE_PREREG.md) is a
  separate CPU item.

## 4. Deliverables and where they go
- `armb/pdyn_*.py` (pipeline + verifiers), `armb/PDYN_PREREG.md` (P1–P6, C1–C8, cadence rule, sealed before phase 2),
  `armb/PDYN_FINDINGS.md`; results under `results/armb_pdyn_*`; FINDINGS_MEMO rows added only through the sealed file.
