# Arm A — spectral-scale self-similarity of bulk function: pre-registration SKELETON

**Status: SKELETON (2026-10-01), not sealed.** Written with the prediction figure `seals/armA_predictions.png`
(`armA_predictions.py`) before any arm-A code exists. Will seals; every `[TBD]` is filled before sealing, never after a
number is seen. Scope and corrections: `briefs/README.md` (Will, 2026-10-01, both notes).

## 0. Hypotheses (declared)
- **H_SS (Will):** the noise-like bulk carries smooth, distributed function that is self-similar across spectral scale
  ("fractal through media").
- **H_RES (nearest confusable):** the bulk is a load-bearing but unlearned reservoir: random directions that downstream
  layers co-adapted to. Operationalised by the shared **co-adapted random-bulk calibrator** (§4).
- **H_KNEE (CC):** function in the bulk has a characteristic scale imposed by the architecture (d_head on the
  head-nested side); the residual (input) side is the only place a data-imprinted exponent could survive.
- Predictions per panel are drawn in the figure; the verdict table (§6) is read off those regions and nothing else.
- **Per-type priors (added 2026-10-04 from BULK_INIT_OVERLAP, Will; DRAFT, part of the seal):** the trained bulk is not the
  initialisation shrunk by weight decay in any type (E_init ≤ 1 %), but how much init content the bulk keeps differs
  sharply by type (ρ_bulk at 143k, 1.4B / 410M-s1): **MLP_IN 0.73 / 0.73**, V 0.41 / 0.34, K 0.27 / 0.16, Q 0.21 / 0.14,
  MLP_OUT 0.17 / 0.19, **O 0.06 / 0.06**. Declared predictions, read per type and never pooled into one verdict:
  - **MLP_IN = the reservoir candidate.** A mostly-random input layer with a learned readout is the classic
    random-features picture: H_RES predicts RESERVOIR for MLP_IN with the smallest calibrator gap of any type.
  - **O, Q, K = the learned-function candidates.** If the bulk carries learned function anywhere, H_SS (or H_KNEE) is
    predicted to show here first; O, whose bulk has left its initialisation the most while staying MP-shaped (Staats),
    is the single most informative type.
  - V and MLP_OUT intermediate; reported, no directional prediction.
  - The co-adapted calibrator (§4) is now the ONLY deciding null for H_RES: the initialisation cannot explain the bulk,
    and SGD noise alone can build a random-looking one.
  - The prediction figure gains one panel row per type group (MLP_IN / O·Q·K / V·MLP_OUT) before sealing.

## 1. Substrate and objects
- Models: `[TBD]` — Pythia-70m (own infrastructure; needed for the calibrator fine-tunes) and one released size for
  the perturbation arm only. The split-sample rule applies: seeds 6–9, 410M-std, 1B are UNREAD for arm B and may serve
  arm A only if named here.
- Matrices: per layer, Q, K, V, O, MLP_IN, MLP_OUT; sides: head-nested (rows of Q/K/V, cols of O) and residual.
- Probe set X: `[TBD]` fixed token batch, hashed; activations at each matrix's input (LN folded, declared as in Stage 3).
- Checkpoint(s): `[TBD]` final + one mid-training; step 0 as a sanity (trained = random there).

## 2. Scale axis and perturbation families
- **Octave bands** by singular-value index from the spike edge s₀ = `[TBD, 32 at d = 2048]`: B_j = [s₀2ʲ, s₀2ʲ⁺¹),
  j = 0 … ⌊log₂(r/s₀)⌋ − 1. (d = 2048 → 6 octaves = 1.8 decades; d = 1024 → 5.)
- Per band, three perturbation families, each at doses `[TBD: 4–5, geometric]`:
  - **R_j** pure rotation within the band's subspace: W + U_j (exp(εA) − I) Σ_j V_jᵀ with A skew (left and right
    versions);
  - **V_j** value perturbation U_j diag(δσ) V_jᵀ (values only, directions fixed);
  - **G_j** generic additive U_j X V_jᵀ.
- **Random-subspace sweep (smoothness):** for k ∈ {8, …, 1024} geometric, N_k = `[TBD]` random k-subspaces of the whole
  bulk, generic perturbations at one fixed size; the statistic is the DISPERSION (CV²) of cost across draws, not its
  mean (Will's correction: the mean is flat under every hypothesis).
- **Antithetic pairs:** every cost is [L(+δ) + L(−δ)]/2 − L₀; [L(+δ) − L(−δ)]/2 is banked separately (first-order term).
- **Regime checks (sealed):** linearity of cost in dose² at every band (ratio of successive doses within `[TBD]`);
  the fp16 re-storage floor measured per matrix (G2c lesson); a band is INAPPLICABLE if either fails.

## 3. The three per-band reports (Will's decomposition)
1. **Input-projection profile** P_j = mean_{k∈B_j} ‖vₖᵀX‖² / (its calibrator value).
2. **Output-matched cost** C^out_j: cost at doses matched on ‖δW·X‖_F, / calibrator.
3. **Raw size-matched cost** C^raw_j: cost at matched ‖δW‖_F, / calibrator (= 1 × 2 up to the regime).
Each as log₁₀ of trained/calibrator, per band, with the replicate spread of the calibrator (§4) as the noise.
Caution recorded: activation covariances already have power-law spectra; a power law in P_j is new ONLY relative to
the calibrator's P_j.

## 4. Calibrator (shared with arm B): co-adapted random bulk
- Take the trained model; in every matrix replace the bulk (indices ≥ s₀) by a Haar rotation within its own subspace,
  keeping σ and the top s₀ directions; freeze the bulk AND the top-s₀ directions; fine-tune everything else until the
  probe loss recovers to within ε_rec = `[TBD]` of the original. Fine-tune control: the original model with the same
  budget and the same frozen set.
- Report the loss gap at recovery as a covariate; `[TBD]` replicates (≥ 3) give the band noise.
- A calibrator whose loss does not recover within the budget → arm A is INAPPLICABLE at that budget (declared outcome).

## 5. Red path (must classify correctly BEFORE sealing)
Three planted models from the calibrator, each fine-tuned on a held-out synthetic task with updates projected into the
bulk subspace:
- **uniform** (every band equally); **self-similar** (band weights ∝ 2^(−αj), α = `[TBD]`); **characteristic-scale**
  (one band only, j* = the d_head band).
The full pipeline (§2–§3, §6) must return SELF-SIMILAR / FLAT / KNEE respectively, on the task loss, at the declared
doses, with arm B's PT-KS/IPR on the planted vectors staying null (the plant is distributed). Any misclassification
blocks the seal.

## 6. Statistics and verdicts (per side, per report)
- Fit log₁₀ ratio vs j by (a) constant, (b) power law, (c) broken power law with the break free, (d) power law with
  exponential cutoff; compare by likelihood ratio with the calibrator spread as the error model; pooled across layers
  with per-layer offsets (hierarchical), because single matrices have < 2 decades.
- **Minimum-octaves rule:** a power-law call needs ≥ `[TBD, 4]` octaves inside the applicable range; otherwise the
  outcome is NOT RESOLVABLE on that side, whatever the fit says.
- **Verdict table (read from the figure's regions):**
  - A and B flat (within ε = `[TBD]`) → **RESERVOIR** (H_SS not supported);
  - A or B power law over ≥ min octaves, exponent ≠ calibrator's beyond its spread, no preferred break → **SELF-SIMILAR
    on that side**;
  - broken power law with the break at the declared d_head band on the head-nested side → **CHARACTERISTIC SCALE**;
  - break elsewhere → **CHARACTERISTIC SCALE (undeclared location)**, reported, not interpreted;
  - D: CV² slope −1 ± `[TBD]` → SMOOTH; shallower and lumpy → CONCENTRATED. (Both H_SS and H_RES predict SMOOTH; D
    cannot separate them and is reported as a property.)
- Every verdict carries the side, the report (1/2/3), the octave range used and the calibrator's recovery gap.

## 7. What would NOT be evidence
- Any ratio read without the calibrator (trained-only curves inherit the spectrum's own power law).
- A power law in P_j alone (known activation statistics).
- Bands that failed the regime checks; fewer octaves than the rule; G2c's 4–6× (two draws, < 1e-3 nats).

## 8. Order of work (Will's GPU order)
A0r (done 10-01) → Q4 extension + third Muon seed (done 10-03) → calibrator + red-path plants → arm A proper
(next, after Will seals the `[TBD]`s, the per-type priors above, and the lit-v2 design changes, lit/v2/S.md §5). Arm B's exploratory
extraction runs on spot's CPUs meanwhile (1.4B + seeds 1–5 only).
