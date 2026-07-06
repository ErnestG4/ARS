# Phase 34c — Brief: ζ zeros + Dirichlet L-zeros + EC L-zeros — RF and p-adic Channels

**Status:** draft, pre-execution.  Pre-pilot audit done at brief-drafting time per the Phase 34a-b consolidation pass (commit 7fca38a).

## Frame

Phases 34a (Mertens sign-changes) and 34b (Liouville sign-changes) closed the orthogonal-channel survey on the two Möbius-family arithmetic objects.  Both returned NULL_IN_ORTHOGONAL_CHANNELS once the substrate-appropriate structural null was applied; the wrong-null (rate-matched Poisson) parallel signal placed them in the same *false-positive equivalence class* with distinct generative-mechanism explanations — squarefree-filter residue density for Mertens (support-restricted family) and random-walk first-passage statistics for Liouville (random-walk-generated family).  The consolidation pass lifted the right-null discipline from execution-time correction to brief-drafting structure: a four-question pre-pilot audit, a structural-null typology with three named families, a two-layer cross-phase enumeration, and within-window stability as a surrogate-independent falsifier.

Phase 34c applies the discipline to the remaining arithmetic objects in the project's instrument-validation portfolio whose NNS-engine bulk verdicts are already settled — ζ zeros (Riemann), Dirichlet L-function zeros, and elliptic curve L-function zeros.  All three belong to the third generative-substrate family in the typology: **spectral-coordinate / unfolding-driven**.  Their bulk statistics are dictated by random-matrix universality (GUE for ζ; symmetry-class-dependent for Dirichlet and EC L per Katz-Sarnak) and the right structural null per the typology is a random-matrix sample at the predicted symmetry class, unfolded via the substrate's mean-spacing law (Riemann-Siegel θ for ζ; conductor-normalised analog for Dirichlet; conductor-and-root-number for EC L).

Phase 34c does not address RH, GRH, BSD, or any random-matrix conjecture itself.

## Structural-null audit (front-loaded, per consolidation pass)

**Generative-substrate family:** spectral-coordinate / unfolding-driven.

**Right structural null per substrate:**

- **ζ zeros (Riemann):** GUE random matrix eigenvalues at matched matrix size N, unfolded to unit mean spacing then re-folded via the Riemann-Siegel θ function to physical-coordinate γ values.

- **Dirichlet L-zeros at conductor q:** symmetry-class random matrix sample per character type — Sp(2N) for real (Legendre-symbol-type) characters, U(N) for complex characters — unfolded via the conductor-normalised analog of Riemann-Siegel θ.

- **EC L-zeros at conductor N_E:** symmetry-class random matrix sample per root number — SO(even) for root number +1, SO(odd) for root number −1 — unfolded via the EC-L-function-appropriate analog.

**Wrong null (the false-positive-equivalence-class trap):** rate-matched Poisson on the unfolded coordinate, parallel to the 34a-b rate-matched Poisson.  Reported in parallel per the two-layer cross-phase enumeration.

**Unfolding methodology per substrate** (specified up front for reproducibility):

- **ζ zeros:** unfolding via the Riemann-Siegel θ function.  γ_n → ñ = θ(γ_n)/π + 1 (Hardy-Littlewood normalisation), so the unfolded sequence has unit mean spacing.  The inverse θ map is required to re-fold RMT surrogates to physical-coordinate γ values.
- **Dirichlet L-zeros at conductor q with character χ:** analytic-conductor unfolding via the per-character expression γ_n → ñ = (γ_n / 2π) · log(q · γ_n / (2π · e)) (Iwaniec-Kowalski Eq. (5.27) for primitive non-principal characters), so per-character unfolded spacings have unit mean.  One unfolding expression per (q, χ) pair; pooled-over-character analyses use the per-character unfolded coordinate before pooling.
- **EC L-zeros at conductor N_E:** curve-conductor unfolding via γ_n → ñ = (γ_n / 2π) · log(N_E · γ_n² / (2π·e)²) (the EC-L analog), so per-curve unfolded spacings have unit mean.  Pooled-across-curves analyses use the per-curve unfolded coordinate before pooling.

**Bulk-vs-edge handling for the RMT surrogate** (Tracy-Widom edge regime applies at N=10⁴):

The outer ~5–10% of RMT eigenvalues live in the Tracy-Widom edge regime and do not represent bulk statistics.  Standard practice is to **exclude the outer 7.5% on each side** (top 7.5% + bottom 7.5%), retaining the central 85% of eigenvalues as the bulk for the comparison to substrate zero-counts.  This exclusion fraction is applied symmetrically and equally to surrogate and substrate samples so the comparison is apples-to-apples.  The exclusion fraction is a brief-time decision; if the sample-size economy at q=30 binds inside the retained bulk for any panel, the panel falls back to a smaller exclusion (5%) with the fraction reported as a per-panel parameter.

**Pre-pilot adequacy check** (per Phase 34b pre-falsification discipline; runs before sub-3 in each substrate panel):

1. Verify the right null reproduces the bulk NNS-engine verdict on its own surrogates (GUE-unfolded ζ surrogate → TR Wigner-class via joint_q_profile; Sp / U / SO surrogates → matching TR sub-class within tolerance).
2. Verify the wrong null (rate-matched Poisson) on the same coordinate produces BL — diagnostic that the survey reads the right vs wrong null contrast in the orthogonal channels too, not only in the bulk.

**Diagnostic interpretation of pre-pilot failure:** the pre-pilot adequacy check is by construction a *calibrator-zoo sanity check at the relevant sample size*.  If GUE eigenvalues at N=10⁴ do not classify as Wigner GUE under the deployed joint_q_profile pipeline, that is a **calibrator-zoo problem (or sample-size problem) at the relevant sample size, not a substrate problem**.  Failure resolution is calibrator-zoo extension or sample-size adjustment, *not* substrate rejection.  Naming this interpretation up front keeps the diagnostic chain clear when the check fires unexpectedly at execution time.

**RF mode choice for spectral-coordinate substrates** (Phase 34a-b used indicator-mode on integer positions; ζ-zero γ values are real, not integer):

- **Option A (robustness panel):** discretise γ → round(γ × scale) to integer positions; use indicator-mode RF as in 34a-b.  Discretisation introduces an *extractor commitment* via the bin-width parameter (= 1/scale).  Reported with a **bin-width sensitivity check across 3–5 nearby widths** (e.g., 0.5×, 0.7×, 1.0×, 1.4×, 2.0× the base scale).  The bin-width sensitivity panel shows whether any signal mode A reports is binning-stable.
- **Option B (primary):** normalised-mode RF on unit-mean unfolded spacings (the existing `ramanujan_fourier(normalize=True)` path used in Phase 5 / §7.ter.4).  Natural mode for spectral-coordinate substrates; tests "is there period-q structure in spacings?" rather than "in raw discretised positions?"  The two questions are distinct and option B is the substrate-native one.

Plan: option B primary, option A with the bin-width sensitivity panel as a robustness layer.  If A and B disagree (any q with significant survival in one mode and not the other), the disagreement is itself informative — A captures absolute-coordinate periodicity which discretisation may stabilise or destabilise; B captures spacing-coordinate periodicity which is the substrate-native question.  The two modes reporting in parallel bounds the verdict against the mode-choice degree of freedom and against the bin-width-parameter degree of freedom.

## Goals (numbered)

1. Orthogonal-channel survey on **ζ zeros** at two height windows — Odlyzko low-height bulk (first ~2,000 zeros) and 10⁶-height window — per substrate, reporting verdict against rate-matched Poisson (wrong null) and GUE-unfolded (right null).  Within-window stability across 5 non-overlapping height windows reported as the primary surrogate-independent falsifier.

2. Orthogonal-channel survey on **Dirichlet L-zeros**, with the conductor-aggregated pool from §7.ter.3 as the primary dataset; per-character-type panel (real / complex) as the substrate stratification.  Right null: Sp(2N) for real-character pool, U(N) for complex-character pool, conductor-normalised unfolding.

3. Orthogonal-channel survey on **EC L-zeros**, with root-number-stratified panel (+1 / −1) per the §7.ter.4 family-symmetry result.  Right null: SO(even) for root +1, SO(odd) for root −1.

4. **Three-way cross-phase comparison within 34c** (ζ × Dirichlet × EC L) at the surface and deep layers per the two-layer enumeration.  **Bilateral 34a × 34c and 34b × 34c** cross-phase comparisons reported as auxiliary — to test whether the spectral-coordinate family lands in the same wrong-null false-positive equivalence class as the support-restricted / random-walk-generated families.

## Methodology / pipeline

**Carried through from 34a-b session, no changes:**

- Calibrator zoo gate (8/8 PASS on STATIONARY_CALIBRATORS) at session start, covers 34c per Phase 34b's session-spanning gate convention.
- p-adic v4 synthetic re-validation (≥5/6 single-prime detections, period-13 narrow miss as documented).
- Joint_q_profile NNS reproduction at Q_MAX=30, JPF_CAP=1500.
- Surrogate ensemble at ≥1000 seeds per null.

**New per 34c:**

- Right-null surrogate generator at the random-matrix family appropriate to each substrate (`phase34c/right_null.py`).  **Primary implementation: Dumitriu–Edelman β-tridiagonal Hermite sampling** for the Wigner classes (β=1/2/4 → GOE/GUE/GSE) and the **Edelman–Sutton analogs** for Sp and SO; direct `scipy.linalg.eigh` only as a small-N spot-check.  Re-folding via inverse θ for ζ, conductor-normalised analog for L-functions.  Bulk-eigenvalue retention: central 85% (7.5% exclusion each side), as specified in the structural-null audit.
- Within-window stability as a **primary** check on the survey schedule (per consolidation pass: surrogate-independent falsifier — runs before the null-based tests in each sub-3 panel).  5 non-overlapping windows; CV(|a_q|) reported at the top-3 q.
- Per-substrate pre-pilot adequacy: verify the right null reproduces the substrate's bulk NNS-engine verdict on its own surrogates.  Failure → calibrator-zoo / sample-size diagnostic, per the audit-section note above.

**Substrate-specific windowing** (specified up front, not left to runtime):

- **ζ zeros:** height bands **[10^k, 10^(k+1)]** for k spanning the available Odlyzko table heights.  Mean local density changes by orders of magnitude across decades of height, so log-spaced height bands are the natural unit-density windowing scheme.  Within-window stability is per-decade.
- **Dirichlet L-zeros:** per-character-family windowing — separate real-character (Sp-class) and complex-character (U-class) pools, with within-pool conductor banding [10^k, 10^(k+1)] for log-spaced conductors.  Symmetry class shifts by character type, so pooling across character types before per-character right-null testing would mask the family-symmetry contrast.
- **EC L-zeros:** per-curve-conductor windowing [10^k, 10^(k+1)], with **per-rank stratification** as a secondary panel if sample size allows (rank-0 / rank-1 curves segregated, per the analytic-rank-vs-functional-equation literature).  Within-rank stratification is a finer-grained substrate panel; reported as a robustness layer if sample size at the rank-stratified level clears the Phase 34b 132-event floor at q=30.

**Pipeline order per substrate:**

1. Load published-product table (Odlyzko for ζ; existing project caches for Dirichlet / EC L).
2. Stationarity check (phase30 module, 10 windows; restrict to stationary sub-window if flagged).
3. NNS-engine reproduction (expected: Wigner-class TR for all three; reconciles with §7.ter.4 / §7.ter.7).
4. Pre-pilot adequacy: right-null self-test (does GUE/Sp/U/SO unfolded surrogate produce the expected bulk verdict?).
5. Within-window stability (surrogate-independent; runs as primary falsifier before null-based survey).
6. RF + p-adic v4 survey against two nulls (wrong: rate-matched Poisson; right: substrate-family RMT-unfolded).
7. Multi-order falsification: second-source cross-tabulation (LMFDB vs Odlyzko for ζ; LMFDB vs §7.ter.3 cache for Dirichlet).

## Acceptance criteria

**Per substrate** (ζ, Dirichlet, EC L) — verdict against the right (RMT-unfolded) null:

- **NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_RMT**: no RF spike or p-adic concentration above the right null at p < 0.001; within-window stability CV ≤ 0.30 at top-flagged q across ≥4 of 5 windows.  ⇒ The substrate is featureless under RF / p-adic v4 beyond what the bulk random-matrix universality already explains.

- **RF_SPIKE_AT_q={q}_BEYOND_RMT**: a specific q's |a_q| survives p < 0.001 against the right null AND within-window stability CV ≤ 0.30 at that q across ≥4 of 5 windows AND second-source cross-tabulation matches.  ⇒ Genuine integer-period structure beyond RMT in this substrate.

- **P_ADIC_CONCENTRATION_p={p}_BEYOND_RMT**: dominant_prime_per_q concentrates on a specific prime above the right-null distribution AND within-window-stable AND second-source-confirmed.

- **AMBIGUOUS_AT_BOUNDARY**: signal at marginal significance against the right null but fails one of stability / cross-source.  Bounded as suggestive, not asserted.

- **NON_STATIONARY**: phase30 10-window check flags non-stationary; analysis restricted to stationary sub-window per 34a-b precedent.

- **SAMPLE_SIZE_BOUNDED_AT_q≥Q**: sub-q-band sample size cap binds at some q < 30.  Per-substrate projection: ζ never binds (10⁶ zeros), Dirichlet never binds (4.05M pooled spacings from §7.ter.3), EC L binds at q ≥ ~15 in the root-number-stratified sub-panels (50 curves × ~100 zeros ≈ 5K per stratum; q=30 leaves ~170 events per residue class — marginal but feasible).  **EC L panel protocol per Q2 amendment:** primary at q_max=30 with SAMPLE_SIZE_BOUNDED flag (30% margin above the Phase 34b 132-event floor); **robustness panel at q_max=20** (≥255 events per residue class, well clear of the floor); cross-tabulate.  If the q=30 and q=20 verdicts disagree, the disagreement is itself informative about the resolution-limited findings boundary.

**Cross-phase within 34c (three-way ζ × Dirichlet × EC L), two-layer per consolidation pass:**

- **Surface layer (vs rate-matched Poisson):** {parallel_null, parallel_signal, divergent} across the three substrates.  Pearson r between RF |a_q| spectra at matched n reported per pair.
- **Deep layer (vs each substrate's right RMT-unfolded null):** {parallel_null, parallel_signal, divergent}.
- **False-positive-equivalence-class diagnostic:** if the surface verdict is parallel signal at the same q or same prime, name the wrong-null-induced equivalence class explicitly (the RMT-unfolding-destroying rate-matched Poisson is the wrong null for all three).  Without this, the parallel reads as a substrate-shared spectral-coordinate fingerprint — the trap the right-null layer prevents.

**Cross-phase bilateral 34a/b × 34c (auxiliary):**

- Surface layer: do all five substrates (Mertens, Liouville, ζ, Dirichlet, EC L) land in the same rate-matched-Poisson false-positive equivalence class?  The support-restricted (Mertens) and random-walk-generated (Liouville) families both showed identical wrong-null signatures (p=2 dominance, q=2 spike) against rate-matched Poisson despite structurally distinct underlying priors.  Spectral-coordinate substrates' structural prior is in unfolded mean density and has **no small-prime modular flavor**, so the **brief-time prediction is DIVERGENT at the surface layer**: 34a/b carries the p=2 / q=2 wrong-null artefact and 34c does not.  DIVERGENT-at-surface is the false-positive-equivalence-class diagnostic *working as intended* — it shows the wrong-null artefact is family-specific, not substrate-independent.
- Deep layer: each substrate against its family-specific right null.  **Brief-time prediction is PARALLEL_NULL at the deep layer**: all five substrates survive their own right nulls (orthogonal channels uniformly featureless beyond family-specific structural floors).
- **Surprise outcome (worth flagging in advance):** if all five substrates land at the *same* p=2 / q=2 wrong-null signature against Poisson, the wrong-null artefact is substrate-independent in a way the support-filter / random-walk explanations do not predict, and the result needs further analysis before the Phase 34a-b right-null story holds.  Reporting this outcome explicitly if it lands prevents it from being read as "everything is parallel; no information" — it is the unexpected outcome, not the default.

**EC L stratification stability sub-comparison:**

The bilateral cross-phase comparison is done **both with EC L strata combined and per-stratum** (root number +1 / −1 separately).  If the combined-sample equivalence-class behaviour differs from the stratified, that is a **stratification-sensitivity finding** worth recording — the surface signal (or its absence) at the root-number-mixed level may not survive at the root-number-pure level, or vice versa.  This is the EC-L-specific analog of the per-character stratification in Dirichlet.

## Out of scope

- Claims about RH, GRH, BSD, or any random-matrix conjecture itself.
- Mechanism claims about substrate physics underneath any orthogonal-channel signal found.
- Computation of new ζ zero heights / L-function zeros beyond published tables.
- The deeper Katz-Sarnak family-symmetry theory; we use it as the substrate-family null specification, not as a research question.
- Extending the calibrator zoo to add a "spectral-coordinate with arithmetic structure" class.  If such a class is needed (no current calibrator covers it), that becomes Phase 34d.

## Methodological commitments carried through

- Calibrator zoo first (one pass at session start covers 34c per 34a-b session-spanning convention).
- Multi-order falsification on any surviving signal (within-window stability, second-source cross-tabulation, right-null re-test).
- Surrogate adequacy: right-null pre-pilot verification per Phase 34b discipline (verify the surrogate reproduces the substrate's bulk verdict on its own samples before using it as the survey null).
- §7.ter.19 not applicable (zeros are point-process by construction at the mathematical level).
- **Within-window stability as surrogate-independent falsifier** per consolidation pass (runs as primary check on the survey schedule, not only as a sub-4 falsification step).
- **Two-layer cross-phase enumeration** per consolidation pass.
- **False-positive equivalence class** named explicitly when the surface (wrong-null) verdict is parallel across substrates.

## Deliverables

1. `phase34c/` directory with the analysis pipeline:
   - `zeta_zeros.py` — loader for Odlyzko tables (data/odlyzko_zeros1.txt, odlyzko_zeros6.txt).
   - `dirichlet_zeros.py` — loader for the §7.ter.3 conductor-aggregated pool (data/dirichlet_zeros.json).
   - `ec_zeros.py` — loader for LMFDB EC L-zeros (data/lmfdb_zeros.json, lmfdb_zeros_h1000.json), root-number-stratified.
   - `unfold.py` — Riemann-Siegel θ + L-function analogs.
   - `right_null.py` — GUE / Sp(2N) / U(N) / SO(even) / SO(odd) random-matrix eigenvalue generators + re-folding to physical coordinates.
   - `run_zeta_survey.py`, `run_dirichlet_survey.py`, `run_ec_survey.py` — per-substrate orchestrators.
   - `run_cross_phase.py` — three-way cross-comparison + bilateral 34a/b × 34c.
2. `data/phase34c_results/` with per-substrate stationarity, NNS, RF+p-adic survey, within-window stability, cross-phase outputs.
3. RESULTS.md §7.ter.49 entry (chronological) + §8 validated-output bullet.
4. One commit per consolidation-pass commit convention.

## Open questions (resolved at brief-amendment time, not at runtime)

1. **RF mode choice (option A vs B) — RESOLVED:** option B (normalised-mode RF on unit-mean unfolded spacings) primary, option A (discretised indicator-mode) as a robustness panel.  Mode A introduces an extractor commitment via the bin-width parameter, so the indicator-mode reporting includes a **bin-width sensitivity panel across 3-5 nearby widths**.  If A and B disagree, the disagreement is itself informative; the bin-width sensitivity panel shows whether mode A's signal is binning-stable.  See *RF mode choice* below.

2. **EC L sample size at root-number split — RESOLVED:** primary at q_max=30 with SAMPLE_SIZE_BOUNDED-flagged status (per-stratum ~170 events per residue class, 30% margin above the Phase 34b 132-event floor).  **Parallel q_max=20 panel as the robustness layer** (≥255 events per residue class — clear of the floor).  Primary at q=30, robustness at q=20, cross-tabulate.  If the q=30 verdict and q=20 verdict disagree, the disagreement is itself informative about resolution-limited findings.

3. **Right-null implementation efficiency — RESOLVED:** primary method is **Dumitriu–Edelman β-tridiagonal Hermite sampling** for the Wigner classes (β=1/2/4 → GOE/GUE/GSE), O(N²) compute and O(N) memory per ensemble.  SO and Sp use the analogous **Edelman–Sutton tridiagonal constructions**.  Direct diagonalization (`scipy.linalg.eigh`) only as a small-N spot-check.  **Selberg-trace-formula approximation as third-line fallback for ζ specifically** if Dumitriu–Edelman somehow blocks, with approximation-quality check (truncation order, deviation from theoretical RMT bulk distribution) documented in the methods.

4. **Bulk-vs-cluster framing for ζ at 10⁶ height:** Odlyzko 10⁶-height tables give ~10⁴ zeros at heights γ ~ 10⁶.  Sample size adequate.  The two-window setup (low-height bulk + 10⁶-height window) tests whether the orthogonal-channel verdict is height-dependent — an open question the brief leaves to the data.

## What this brief is not

Not a contribution to the ζ / L-function / EC literature.  Not a Katz-Sarnak family-symmetry analysis.  Not a claim that any of the three substrates carries hidden arithmetic structure.  The brief is the orthogonal-channel survey on three load-bearing RH-adjacent arithmetic objects with the Phase 34a-b discipline pre-installed at brief-drafting time, not bolted on at runtime.  Either outcome — uniform PARALLEL_NULL across the five-substrate (34a + 34b + 34c) portfolio at the deep layer, or DIVERGENT at the deep layer on one of the three — is informative, and the verdict will be reported with that framing.
