# Findings memo — Shapes of LLM weights and transforms over training (CC Brief v1.1)

Branch `llm-spectra` (local, unpushed), dir `llmspec/`. Compiled 2026-09-27 from the stage documents, which hold the
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
| 1 | Bulk nearest-neighbour statistics (⟨r̃⟩, Brody q) stay at β=1 at every checkpoint: no departure > 0.010 in ⟨r̃⟩ or > 0.10 in q | Sealed null (aim 6); G1 witness; G0; G3 | **NULL** — 260/260 cells in each of 1.4B, 1B and 410M, and in all 10 seed runs (2 cells → DENSITY_ARTIFACT by the ladder; its 0.10 tolerance is 5× the v1 calibrator's measured 0.02 bias, so the labels stand) |
| 2 | A late-training per-head-Q departure from β=1 (q ≈ −0.02 after density matching) | Frozen drift test (S1/S2); fidelity test (S2); known-answer licence (S4) | **NOT ESTABLISHED.** Sealed verdicts stand (FINDING_CANDIDATE / INCONCLUSIVE). S4: the frozen calibrator's own bias under a TRUE β=1 is −0.0207 / −0.0164 (observed −0.0197). The q arm is NOT RESOLVABLE at N=64. ⟨r̃⟩ under the licensed calibrator: −0.00086, t₉ −1.6. S4-sup: the licensed calibrator recovers a planted departure of the claimed size in full, so a real one would have read t ≈ −3.7 (post-hoc power) |
| 3 | Multi-peak (Diffract-style) attention spectra exist | Stage 1 sealed KDE rule; Stage 1b dip test (licensed on nearest confusables) | Sealed rule = non-evidence (tail specks). Dip test: **Pythia 0 heads multimodal** (NULL, and a weak one: the test misses minority or broad peaks, e.g. ~0% power for a 20% peak at sd 0.1); **OLMo Q/K multimodal at stage-1 end** (Q 24.6%, 13.3% excluding dead rows), sub-floor at `main` (8.6%). Aim 1 deferred |
| 4 | Local statistics on peaked spectra | G7 (Stage 2) | **NOT LICENSED** as registered (kde(4–8) fail β=2). Raw ⟨r̃⟩ LICENSED |
| 5 | Induction heads form between steps 512 and 1000 | Markers; G3 R5 | **REPLICATES** at all 3 sizes; **SEED-ROBUST** (10/10) |
| 6 | The OV circuit leaves its product-Ginibre null before QK does | Circuit null (4000 draws); G3 R4 | **REPLICATES** at all sizes; **SEED-ROBUST** (10/10). At the resolution limit (step 512) |
| 7 | Heads read common top input directions (cross-head sharing), rather than concentrating in single heads | Input-rotation head null (non-degenerate); G3 R2 | **REPLICATES**; **SEED-ROBUST** (10/10). "Head concentration vs 1/16" WITHDRAWN (wrong null) |
| 8 | K's top singular directions concentrate on rotary (position) dims beyond their norm share | Within-head rotation null + norm clause; G3 R1 | Concentration ≥ null + 0.10 in 9/10 seeds and at every size, but the registered R1 (with its norm clause) is **SEED-DEPENDENT (2/10)** and fails at 410M. Concentration exceeds the rotary-row norm share in every run (ratio 1.24–1.76) |
| 9 | Trained spectra leave Marchenko–Pastur by steps 1000–2000 | G1 KS95; G3 R6 | **REPLICATES**; **SEED-ROBUST**. Consequence: "outliers vs the MP edge" is undefined after ~1000 steps, so all outlier counts are WITHDRAWN |
| 10 | Update (ΔW) stable rank rises ≥ 3× from 1k→2k to 15k→16k at constant step count and ~constant LR | Equal-interval ΔW; G3 R3 | Holds on 1.4B for all types. **Not size-general** (V/O fail at 1B/410M), **SEED-DEPENDENT (4/10)**. Q, K and MLP_IN ≥ 3× in 10/10 seeds; the output side (V 8, MLP_OUT 7, O 5 of 10) is what varies |
| 11 | Bulk singular-value ORDERING carries function (Diffract's bulk-permutation witness) | G2 + G2b controls (pre-registered) | **NOT ESTABLISHED.** A same-subspace, size-matched perturbation costs 0.67× the shuffle; local shuffles cost ≈ 0. Registered "Diffract replicates = false" is attributed to scope + size |
| 12 | V's compression proceeds as a layer-ordered wave (Liu) | Dense-V run, 1000-step grid | **NULL for V** (ρ −0.00). Q/K/O/MLP UNRESOLVED (they compress within 256–2000 steps; only 512/1000/2000 exist). Needs arm B |
| 13 | Change points align with events | CP null calibration | **NOT LICENSED** (false-CP rate 0.59–0.98 on smooth curves). No alignment claim is made |

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
- **Seed runs:** seeds 3 and 4 have late loss spikes (final loss 2.475 / 2.857 vs ~2.34). Their final states are
  post-instability.

## 3. Confounds that bound the descriptives
- **LR warmup ends at step 1430.** Every "turning point at ~2k" sits at the first checkpoint after it:
  LR-CONFOUNDED.
- **Checkpoint spacing.** Pythia has no equally spaced checkpoints below step 1000. "Low-rank early" updates, event
  ordering within 256–2000, and non-V compression waves all need arm B (own dense checkpoints). **HELD.**
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
- **HELD (Will's call):** arm B (AdamW vs Muon; own dense checkpoints), and the OLMo stage-1 trajectory for aim 1.
- **Stage 4** (peaked-spectrum local statistics): not reached, because G7 did not license it.
- **Zoo seating:** the G7 classes still need seating in calibrator_panel.py (a shared-module edit, left for the
  branch-merge session).
