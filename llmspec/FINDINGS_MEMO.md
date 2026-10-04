# Findings memo — Shapes of LLM weights and transforms over training (CC Brief v1.1)

Branch `llm-spectra` (published: github.com/ErnestG4/ARS), dir `llmspec/`. Compiled 2026-09-27, revised 2026-09-30 (Will's critique #1/#3/#11 + Open leads; Arm B folded in), from the stage documents, which hold the
numbers, tables, commits and caveats: STAGE1_FINDINGS, STAGE2_FINDINGS, STAGE3_FINDINGS (§8–15 supersede §3–7 where they
conflict), STAGE3_REPL_FINDINGS, STAGE3_SEED_FINDINGS. The brief's §6 rule applies: **every claim names its licensing
gate, and nulls are reported as nulls.** Pre-registrations: STAGE3_PREREG.md (0cf53ba), STAGE3_REPL_PREREG.md (8147f53),
STAGE3_SEED_PREREG.md (2f38b8b + S1–S4).

**Status vocabulary.**
- **NULL:** a registered null that held.
- **ESTABLISHED:** passed its registered test and its controls.
- **REPLICATES / SEED-ROBUST / SEED-DEPENDENT:** a G3 verdict.
- **DESCRIPTIVE:** no test; reported as a measurement.
- **NOT LICENSED / NOT RESOLVABLE:** the instrument could not answer.
- **WITHDRAWN / NOT ESTABLISHED:** an earlier reading that did not survive.
- **HELD:** Will's call.

**Data.**
- Pythia-1.4B, 1B and 410M: 26 revisions each.
- PolyPythias 410M: seeds 1–9 plus standard, 26 revisions each.
- OLMo 2 1B: step 0, stage-1 end and `main`.
- All streamed, with exact fp64 SVD. G5-slot long parquets are in results/.

## 1. Headline

| # | Claim | Gate(s) | Status |
|---|---|---|---|
| 1 | Bulk nearest-neighbour statistics (⟨r̃⟩, Brody q) stay at β=1 at every checkpoint: no departure > 0.010 in ⟨r̃⟩ or > 0.10 in q | Sealed null (aim 6); G1 witness; G0; G3 | **NULL** — 260/260 HOLDS in each of 1.4B, 1B and 410M. Across the 10 seed runs, **2 cells were VIOLATED** (per-head Q: seed 1 @143k Δq −0.103; seed 6 @96k Δq −0.106) and the ladder attributed both to DENSITY_ARTIFACT. Per S1, the attribution sits beside the verdict and does not replace it. **Per-head cells are licensed on ⟨r̃⟩ only:** a realistic trained density alone moves raw kde(4) q by ~0.12 under a true β=1 (§3), which is larger than the 0.10 q tolerance. So a per-head q pass or fail is uninformative either way. On ⟨r̃⟩ the per-head cells held, including both VIOLATED cells (Δ⟨r̃⟩ −0.0059 / −0.0046 vs 0.010). At 70M (Arm B) the 0.010 tolerance is not powered: see ARMB_FINDINGS §6, NOT ESTABLISHED. **Context (2026-10-01):** this is what universality predicts for any dense matrix whose bulk is not decoupled (Thamm, Staats & Rosenow 2022, endpoint CNN/MLP; Loftus 2026, an MLP/CNN ⟨r⟩ trajectory): an instrument check, not evidence that the bulk is unlearned. It is the first LLM-trajectory version. The pre-registered LOWER/UPPER-band descriptives were omitted from the reports until 2026-10-01: see STAGE3_FINDINGS §16 Seeds 3/4: cells after 64k / 96k are restarted-run states (10-04); every cell of both HOLDS either way. |
| 2 | A late-training per-head-Q departure from β=1 (q ≈ −0.02 after density matching) | Frozen drift test (S1/S2); fidelity test (S2); known-answer licence (S4) | **NOT ESTABLISHED.** Sealed verdicts stand (FINDING_CANDIDATE / INCONCLUSIVE). S4: the frozen calibrator's own bias under a TRUE β=1 is −0.0207 / −0.0164 (observed −0.0197). The q arm is NOT RESOLVABLE at N=64. ⟨r̃⟩ under the licensed calibrator: −0.00086, t₉ −1.6. S4-sup: the licensed calibrator recovers a planted departure of the claimed size in full, so a real one would have read t ≈ −3.7 (post-hoc power) |
| 3 | Multi-peak (Diffract-style) attention spectra exist | Stage 1 sealed KDE rule; Stage 1b dip test (licensed on nearest confusables); **OLMO_PREMISE (10-03): own-row-norm confusable class** | Sealed rule = non-evidence (tail specks). Dip test: Pythia none (a weak null). **OLMo stage-1 end: NOT LICENSED (row-norm confusable, OLMO_PREMISE_FINDINGS)** — Gaussian blocks with the heads' own row norms read multimodal in 21 % / 8 % of draws (all levels / trimmed) against observed 25 % / 13 %, and the σ-multimodal heads are the row-norm-bimodal heads (Fisher p 1e-16); the gain-folded map is not licensed either (the q_norm gain alone makes 19–64 % of Gaussian heads read multimodal). Descriptive remainder: the trimmed Q rate (13.3 %) still exceeds the row-norm floor (8.2 %), binomial p = 0.0038, short of the 1e-3 bar — not fully explained. Endpoint (ingredient 3) identical to stage-1 end, descriptive. `main` is a different run. |
| 4 | Local statistics on peaked spectra | G7 (Stage 2) | **NOT LICENSED** as registered (kde(4–8) fail β=2). Raw ⟨r̃⟩ LICENSED |
| 5 | Induction heads form between steps 512 and 1000 | Markers; G3 R5 | **REPLICATES** at all 3 sizes; **SEED-ROBUST** (10/10). Consistent with Olsson et al. 2022 and Tigges et al. 2024 (~2B tokens). Dense 70M onset (Arm B): 675 ± 100 steps |
| 6 | The OV circuit leaves its product-Ginibre null before QK does | Circuit null (4000 draws); G3 R4 | **REPLICATES** at all sizes; **SEED-ROBUST** (10/10): OV before QK at Pythia checkpoint resolution (step 512). NOT separable on Arm B's dense grid (512 ± 200 vs 675 ± 200, SIMULTANEOUS as sealed). The two sides use different statistics (copying score vs symmetric fraction), each with its own null width |
| 7 | Heads read common top input directions (cross-head sharing), rather than concentrating in single heads | Input-rotation head null (non-degenerate); G3 R2 | **REPLICATES**; **SEED-ROBUST** (10/10 as registered; reads step 143000, where seeds 3/4 are restarted-run states — n = 8 over valid end-of-training states: 8/8; seeds 3/4 at their last valid checkpoints pass; STAGE3_SEED_FINDINGS correction 10-04). "Head concentration vs 1/16" WITHDRAWN (wrong null) |
| 8 | K's top singular directions concentrate on rotary (position) dims beyond their norm share | Within-head rotation null + norm clause; G3 R1 | Concentration ≥ null + 0.10 in 9/10 seeds as registered — **8/8 over valid end-of-training states** (the one fail, seed 4's 0.307, was a restarted-run state at 143k; seed 4 at 96k reads 0.455) — and at every size, but the registered R1 (with its norm clause) is **SEED-DEPENDENT (2/10)** as registered and fails at 410M; over valid end-of-training states it passes **1/8** (seed 3's pass was its restarted state), the rule's lower band if read proportionally (post hoc, 10-04). The norm share rises late in every run (0.23 at 64k → 0.27–0.30 at 143k), so seeds 3/4 cannot be scored at their earlier valid checkpoints. Concentration exceeds the rotary-row norm share in every run (ratio 1.24–1.76) |
| 9 | Trained spectra leave Marchenko–Pastur by steps 1000–2000 | G1 KS95; G3 R6 | **REPLICATES**; **SEED-ROBUST**. Consequence: "outliers vs the MP edge" is undefined after ~1000 steps, so all outlier counts are WITHDRAWN |
| 10 | Update (ΔW) stable rank rises ≥ 3× from 1k→2k to 15k→16k at constant step count and ~constant LR | Equal-interval ΔW; G3 R3 | Holds on 1.4B for all types. **Not size-general** (V/O fail at 1B/410M), **SEED-DEPENDENT (4/10)**. Q, K and MLP_IN ≥ 3× in 10/10 seeds; the output side (V 8, MLP_OUT 7, O 5 of 10) is what varies |
| 11 | Bulk singular-value ORDERING carries function (Diffract's bulk-permutation witness) | G2 + G2b controls (pre-registered) | **NOT ESTABLISHED.** A same-subspace, size-matched perturbation costs 0.67× the shuffle; local shuffles cost ≈ 0, **but they are tiny**. They move the weights by 0.14% / 0.56% / 2.2% of the bulk shuffle's ‖ΔW‖ (k = 2 / 8 / 32; median 0.07% / 0.28% / 1.1% of ‖W‖ per matrix), and a same-subspace random perturbation of the SAME size also costs ≈ 0 (≤ 0.0004 nats; G2c, a145694). So the k-sweep **neither supports nor contradicts** a "smooth, distributed" reading (the reading declared before G2c ran). Descriptive: at k = 32 the size-matched control costs 4–6× the local shuffle in both seeds (0.00028–0.00039 vs 0.00006–0.00007), all below 1e-3 nats. Registered "Diffract replicates = false" is attributed to scope + size |
| 12 | Compression proceeds as a layer-ordered wave (Liu) | Dense-V run (1.4B); Arm B Q2 wave (70M, sealed exact test) | V at 1.4B: DESCRIPTIVE null (ρ −0.00, 1000-step grid; a post-hoc extension, not a sealed test), consistent with Liu's claim that V/O compress uniformly. **Q/K at 70M (Arm B): OPPOSITE ORDER** as sealed (p_lower 0.0052; the wave family's two-tailed α is 0.10), significant only with layer 0 (p 0.056 without it). Liu's regime (16K tokens per step, 200-step warmup, a statistic that builds in the first layer) is not commensurable with Pythia's |
| 13 | Change points align with events | CP null calibration | **NOT LICENSED** (false-CP rate 0.59–0.98 on smooth curves). No alignment claim is made |
| 14 | The ~2k turning points are anchored by step, warmup end, or LR integral (Arm B Q1) | E4 warp-and-compare, licence v2 (70M) | **NO SIMPLE ANCHOR** (A2), licensed against the curves' own roughness (0.2–0.3%). Warmup length changes the trajectory (STEP is the worst map), and no sealed time map reproduces it within that noise. **NOT RESOLVABLE as sealed (2026-10-01, A0R_PREREG / ARMB_FINDINGS §2b):** an identical-config rerun of A0 (A0r) reads NO_SIMPLE_ANCHOR against A0 on TP_O (fit ratio 13.3 > c_fit 5.4), so the sealed statistic's noise model is too small for paired runs; the paired-divergence floor is 2.36% (O) / 0.48% (MLP_OUT) rel RMS against A2 misfits of 2.42% / 1.69%. Descriptively, the MLP_OUT misfit is 3.5× the floor and stands; the O misfit equals the floor. A1 has no licensed verdict (ARMB_FINDINGS §2) |
| 15 | Early updates are low-rank (Arm B Q3) | ΔW rank ratio type counts (70M) | **INCONCLUSIVE** as sealed. Descriptively Q/K early updates are 5–7× lower-rank; V/O/MLP not |
| 16 | AdamW vs Muon (Arm B Q4) | Two independent pairs, T·s_ref (70M) | 123/368 cells pass (a count, not independent effects). The TIMING and DEPTH of the Q/K stable-rank fall depend on the optimizer (Muon starts it later and leaves it shallower by step 3000); past 3000 at 70M (Q4EXT, ARMB_FINDINGS §9, descriptive) AdamW's Q/K stable rank dips to a minimum near 3000 and recovers to 17/15 by 10000 while Muon stays on its plateau — a dip and recovery under AdamW, not a collapse Muon postpones (Stage 3's 1.4B kept Q/K compressed; possibly a size effect), and Kimi K2 reports σ₁ growth of W_Q/W_K under Muon at scale. Flatter Muon spectra are prior art (Moonlight §3.4); the early delay is the new claim, and it rests on two Muon runs. Pairing caveat: the seed-1 identity check (A9) is INCONCLUSIVE as sealed. The rebuilt data separates from the standard order but a one-step alignment is not resolved (ARMB_FINDINGS §5b) |
| 17 | The trained bulk is the initialisation shrunk by weight decay (reservoir, cheapest form) | Sealed bulk–init overlap (BULK_INIT_OVERLAP_PREREG + A1; continuity gate; two nulls ≈ 0) | **MIXED** as sealed (1.4B and 410M seeds 1–5); **rules out** the shrunk-init reading (E_init 0.5 % / 0.3 % at 143k, ρ_bulk 0.24 / 0.19); α̂ > α_wd (red flag, opposite sign); O lowest (0.06), MLP_IN highest (0.73); the co-adapted calibrator is the only remaining null for H_RES. Seeds 3/4 valid through 64k / 96k only (discontinuous uploads). |
| 18 | Divisor classes of composite periods carry more amplitude than translation symmetry predicts (side brief, divisor/) | Sealed DIVISOR_PREREG (+A1–A4); control gates PASS ×3 models; Holm over 17 tests; A3 log-frequency residualisation; **A4 stratified-permutation frequency null** | Numbers 0–99: **H1 HOLDS d = 2, 4, 5, 10** (pythia-1.4b; REPLICATES 410M, 70M; every layer). **Frequency does not explain it:** A4 (within-frequency-strata permutations, any function of frequency) — d = 2, 5, 10 SURVIVE in all three models (z 11–18), d = 4 SURVIVES at 1.4B/410M and is NOT RESOLVABLE at 70M; A3 (linear/quadratic log-frequency) lowers no z. Periods 2, 5, 10 replicate Zhou et al. 2406.03445 / Kantamneni–Tegmark 2502.00873; **period 4 is new (410M–1.4B)**. Months: NOT RESOLVABLE (12 items resolve only a 40 % excess). Hours: H0 HOLDS d = 3, 4; bets NOT RESOLVABLE; parity positive 3/3, never past Holm. |

## 2. Descriptive measurements (no test; Pythia-1.4B unless stated; see STAGE3_FINDINGS)
- **Stable rank** collapses for Q/K/O/MLP_OUT between steps 128 and 2000; V collapses later (3k–12k); O and MLP_OUT
  rebound after 2000.
- **Top singular values** grow throughout (Q σ₁ 1.26 → 17.3).
- **Lower-decile departure from MP** in Q/K from ~8k. It is not precision-limited: 44–80× above the fp16 Weyl bound.
- **Circuits:**
  - Copying heads appear with induction.
  - Induction heads leave the QK null band earlier (21% at step 512 vs 2.7% for other heads). Their magnitude
    difference is partly built in by the selection.
- **Update alignment:** Q/K updates put ~9× isotropic mass in W's top-32 left subspace over 1k–3k, decaying to ~2×.
- **Unexplained low-rank update burst in V/O/MLP_OUT at 4k → 5k** (no loss jump). Reported, not interpreted.
- **First sink head:** 48k–64k steps under a strict definition. Not commensurable with the brief's 10–20× (definition,
  probe and BOS token all differ).
- **Seed runs:** seeds 3 and 4 were recorded as having late loss spikes (final loss 2.475 / 2.857 vs ~2.34). **Corrected
  2026-10-03 (BULK_INIT_OVERLAP_FINDINGS §3, polypythias_restart_check.py):** the uploaded trajectory is discontinuous at a
  restart (seed 3 from 96000, seed 4 from 128000: the later checkpoints come from the restarted run, under the original
  step names) — our spike reading measured the discontinuity; whether the original runs spiked is untouched (seed 4's 128k correlates 0.97 with
  its own step 0 and 0.16 with 96k; seed 1 control continues normally). Their final-checkpoint cells are early-training
  states, not end-of-training ones; both seeds are valid through 64000 (3) / 96000 (4) only. PolyPythias names exactly
  these two seeds as outliers.
- **Band descriptives (pre-registered; reported late, STAGE3_FINDINGS §16):** the UPPER-band ⟨r̃⟩ of per-head Q/K
  ends 0.07–0.12 below the witness in every 410M run (10/10), 0.02–0.03 below at 1.4B and ≈ 0 at 1B; whole-matrix
  types stay within ±0.02. Post-hoc reading: the departure orders with head width (64 → 128 → 256), which points at
  the band's upper edge meeting the outlier directions rather than at a change of β.

## 3. Confounds that bound the descriptives
- **LR warmup ends at step 1430.** Every "turning point at ~2k" sits at the first checkpoint after it:
  LR-CONFOUNDED.
  - Arm B (#14) confirms that the schedule matters: changing the warmup changes the trajectory. None of step,
    warmup end or LR integral anchors it as a re-timing.
- **Checkpoint spacing.** Pythia has no equally spaced checkpoints below step 1000. Arm B (own dense checkpoints,
  70M) addressed this: see #12, #14–#16 and armb/ARMB_FINDINGS.md.
  - At 70M's resolution the A0 events (OV/QK null exit, induction, MP exit) are SIMULTANEOUS; the order is not
    resolved.
- **Density shape versus local statistics.** A realistic trained per-head density alone moves kde(4) q by ~0.12 under
  a true β=1 (S4 known-answer pools). A density-matched calibrator must pass a known-answer licence before its
  residual is read.
  - The QK-product "function, not symmetry" reading is WITHDRAWN for this reason.

## 4. Instrument / precision notes (G4, G6, template)
- **Stored precision:** Pythia F32 checkpoints are fp16 upcasts. OLMo 2 F32 are true fp32 masters; the brief's bf16
  premise was wrong. fp16 rounding moves bulk ⟨r̃⟩ by ≤ 0.0017.
- **G6:** HT-SR MLE α (htsr_mle_v1, quoted only where bootstrap p ≥ 0.1) and Liu's rank-slope are kept separate and
  never compared.
- **G0 rate bars:** false-failed twice for lack of a sampling allowance (Stage 1 W_O; seed 7 V). Both are labelled
  FAIL-as-sealed and attributed.
- **Protocol-template notes** (NOTES.md §6 and STAGE3_SEED_FINDINGS S4):
  - rate bars need family-wise noise allowances;
  - witness scale matching is unnecessary at these tolerances;
  - nearest-confusable testing precedes sealing;
  - default-path regression cannot catch default leakage;
  - retries must cover every network step;
  - calibrators need a known-answer licence on realistic shapes;
  - per-head q at N ≈ 64 is calibrator-limited to ~±0.02, so use ⟨r̃⟩;
  - dry-run every refusal branch at seal time.

## 5. Not done
- **DONE:** Arm B (2026-09-29; armb/ARMB_FINDINGS.md).
- **HELD → MOOT (10-03):** the OLMo stage-1 trajectory for aim 1 lost its premise (row 3 NOT LICENSED).
- **Stage 4** (peaked-spectrum local statistics): not reached, because G7 did not license it.
- **Zoo seating: DEFERRED explicitly** (NOT in the published main). DEFERRED explicitly at the 2026-09-30 merge of llm-spectra into main (Will: seat it in the merge or defer it in NOTES; deferred). Not seated because the G7 classes are DATA-DEPENDENT: each class draw (stage2_g7.draw) is mapped through peak mixtures fitted to real OLMo stage-1-end Q heads (fit_mixture on results/g7_targets_olmo_stage1end_Q.npz). Seating them properly is a shared-module design, not a merge-time edit. It needs: (1) a SEPARATE list (e.g. PEAKED_SPECTRUM_CALIBRATORS), NOT EXTENDED_CALIBRATORS, so the 6 existing panel consumers (extractor_distinctness, run_phase20_5_distinctness_revalidation, cross_substrate/rf_decoy_battery, cross_substrate/aq_floor_sweep, comb/verify_comb, phase22a/verify_calibrators) do not change; (2) the targets npz pinned by sha256, failing closed; (3) CALIBRATOR_TIERS entries (construction-defined); (4) _schema_self_check extended to the new list; (5) a regression run of the existing consumers.

## 6. Open leads (for specialists; none of these is running)
Each needs its own pre-registration before it is read as evidence.
1. ~~**OLMo multimodality over training.**~~ **WITHDRAWN 2026-10-03: the premise is NOT LICENSED (row 3; OLMO_PREMISE_FINDINGS).**
   Successor lead: within-head row-norm bimodality (when do rows split into two scales; are they the gain ≈ 0 rows?).
   As originally written: 13.3% of Q heads are multimodal at stage-1 end (dead rows excluded). The
   earlier "sub-floor at `main`, after mid-training" is withdrawn: `main` is a different run (row 3). When do the
   peaks appear, and do they survive the lineage's own stage-2 anneal (ingredient 3; ingredients 1–2 are seed
   replicates of the same anneal — CORRECTED 10-03: the HF card calls ingredients 1–2 exploratory runs)? Stage 2 changes the LR (linear to 0) and the data mix together, so a change there
   cannot be attributed to the schedule alone. G7 did not license local
   statistics on peaked spectra, so a trajectory can time the peaks but not resolve their internal structure.
1b. **QK-norm row-scale structure (successor to lead 1; OLMO_PREMISE_FINDINGS §4b–5):** heads with multimodal singular
   spectra are the heads whose rows sit at two norm scales, and 98 % of dead rows have q_norm gain ≈ 0. Hypothesis: a
   near-zero gain cuts the row's gradient and weight decay shrinks it (config check pending). Diffract's multi-peak
   attention spectra in OLMo 2 (2608.10850) may be this same effect — a lead for whoever studies QK-norm.
1c. **Top singular directions grew along the initialisation** (BULK_INIT_OVERLAP §2): the top-32 content correlates
   0.86 / 0.79 (1.4B / 410M) with W₀ against nulls of 0.02–0.03, while Q's σ₁ grows 1.26 → 17.3 (Stage 3). Training
   largely amplified particular initial random directions rather than building new ones. Lower for Q (0.69) and O
   (0.55 / 0.36); highest for V and MLP_IN (0.92–0.97). Descriptive.
2. **Dead rows in OLMo Q.** At stage-1 end: a near-zero mode in 170 Q heads, and 8 heads RANK_COLLAPSED (median σ
   below the fp32 floor). At `main` (a different run): 92 heads. What makes them, and do they survive the lineage's
   own anneal? The ~1e-28 depth is unreconciled with what weight decay alone can produce over stage 1 (~1e-22).
3. **The low-rank update burst in V/O/MLP_OUT at 4k → 5k** (1.4B, no loss jump). Unexplained. In the released Pythia-70M
   runs (standard + seeds 1–9) the frozen burst check reads ABSENT 10/10 (armb/burst_check_70m.py), so it may be
   size-specific.
4. **Q/K lower-decile departure from MP from ~8k**, 44–80× above the fp16 Weyl bound. It is not precision.
5. **K's concentration on rotary dims** (#8): ≥ null + 0.10 in 9/10 seeds and at every size, but R1 with its norm
   clause is SEED-DEPENDENT.
6. ~~Seed 4's late loss spike as a natural experiment~~ **WITHDRAWN 2026-10-03:** the uploaded trajectory is discontinuous
   at a restart (BULK_INIT_OVERLAP_FINDINGS §3); there is no continuous spike trajectory to read.
7. **Bulk singular VECTORS.** G2/G2b tested only the ordering of bulk singular values, and nothing tested puts
   function there (#11). Whether function lives in the bulk's singular vectors was never tested.
   - A hint pointing there (G2c, descriptive, under 0.001 nats): at k = 32, a same-size random perturbation confined
     to the bulk subspace costs 4–6× the local shuffle, in both seeds.
   - The shuffle only reorders singular VALUES and leaves the vectors alone; the random perturbation also rotates the
     DIRECTIONS. So at equal size, disturbing the directions hurt more than reordering the values.
8. **Arm B leads** (70M): see armb/ARMB_FINDINGS.md §8 (Q1 misfit shape, the wave without layer 0, the Q3 reference
   phase, the Muon ΔW rank, the bulk count test with a measured null rate, and more).

