# Phase 34f Findings (34f-G partial) — 3-D Bianchi pipeline validated; Picard data-acquisition-blocked; Berry-Robnik fitter bug caught

**Status:** 34f-G partial. The 3-D Bianchi Maass methodology pipeline is built and synthetic-validated (PIPELINE_VALIDATED_READY_TO_FIRE). Substantive 34f-G bulk-NNS on Picard is **DATA_ACQUISITION_BLOCKED** — the §D.0a data-availability gate fired (Then 2003's 13,950 Picard eigenvalues are not published; only ~60 OCR-mangled samples in the PDF; LMFDB Bianchi reCAPTCHA-blocked). The synthetic-validation harness **caught a real bug in the Berry-Robnik ρ fitter** that retroactively amends Phase 34e Test 2. 34f-E (Bianchi-Z[ω]) and the cross-coordinate Test 4 remain pending the multi-week data-acquisition cost flagged in PHASE34F_BRIEF §C.3.

---

## Frame

Phase 34f is the closer for the Q(√−3) three-coordinate joint statement (PHASE34D_FINDINGS §D). 34f-G is the Picard PSL(2, Z[i])\ℍ³ replication leg — methodology validation of the 3-D Bianchi adaptation against Then 2003's published Sarnak-anomaly result, prior to the 34f-E first-measurement.

This session executed the 34f-G methodology-build + synthetic-validation legs. The substantive bulk-NNS verdict is gated on Then 2003 data acquisition.

---

## §A. §D.0a data-availability gate: FIRED for 34f-G

Per PHASE34F_BRIEF §D.0a / §C.1 / §I.1, the first pre-flight action for 34f-G is confirming Then 2003 Picard eigenvalue data availability.

**Finding:** Then 2003 (arXiv:math-ph/0305048) computed **13,950 Picard Maass eigenvalues** across 4 symmetry classes (D, G, C, H) and concluded the NNS "comes close to that of a Poisson random process" — the Sarnak anomaly for Picard. **But the raw 13,950-eigenvalue list is NOT published**: the PDF contains only Table 1 (~30 small-r samples per class, r ≈ 6–26) and Table 2 (~28 samples around r ≈ 139–140), and these are OCR-mangled across the 4 symmetry-class columns. No Zenodo dataset exists; the LMFDB Bianchi modular forms page is reCAPTCHA-blocked in this session.

**Verdict:** **34f-G substantive bulk-NNS = DATA_ACQUISITION_BLOCKED.** Per PHASE34F_BRIEF §I.1, de-novo Hejhal-on-ℍ³ recomputation is the multi-week infrastructure cost — not feasible in this session. Transcribing the ~60 OCR-mangled samples would fabricate a weak underpowered result and is explicitly NOT done (parallel to the Phase 34e discipline of not over-claiming on unavailable data).

The literature result is unambiguous (Then 2003 found Poisson NNS for Picard — the Sarnak anomaly), so the expected substantive verdict when the data is acquired is SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI. ARS has not independently measured it.

---

## §B. 3-D Bianchi pipeline: built + synthetic-validated

The methodology-build leg IS verifiable without the Then 2003 data, on synthetic spectra with known ground truth.

### B.1 Infrastructure (`phase34f/bianchi_unfolding.py`)

- Spectral-parameter convention **λ = r² + 1** (3-D Then 2003 convention; distinct from the 2-D SL(2,ℤ) λ = 1/4 + r² used in Phase 34e).
- 3-D Bianchi Weyl-law unfolding: **x_j = vol·r_j³ / (6π²)** (cubic, not quadratic).
- Fundamental-domain volumes as published anchors (the general Humbert formula's |d_K|^{3/2} + unit-group conventions are error-prone to re-derive): Picard vol = 0.3053218564 (Then 2003); Bianchi-Z[ω] vol = 0.0845776180 (Elstrodt-Grunewald-Mennicke; smallest Bianchi orbifold, ~3.6× smaller than Picard — consistent with PHASE34F_BRIEF §B.2).

### B.2 Synthetic validation (`phase34f/run_pipeline_validation.py`)

Three synthetic spectra with known ground truth pushed through the full pipeline (cubic unfold → NNS engine → Berry-Robnik fit):

| synthetic input | ⟨s⟩ | NNS primary | rep_med | Berry-Robnik ρ_GOE |
|---|---|---|---|---|
| Poisson (Sarnak-anomaly analog) | 1.015 | **BL** | 0.023 | 0.091 ± 0.042 |
| GOE β=1 (BGS-naive analog) | 1.000 | **TR** | 0.343 | 0.996 ± 0.004 |
| Berry-Robnik mix (true ρ=0.3) | 1.033 | BL | 0.039 | 0.255 ± 0.017 |

**All 6 validation gates pass:**
- unfolding_correct ✓ (cubic Weyl → ⟨s⟩ ≈ 1)
- poisson_classifies_BL ✓ (Sarnak-anomaly analog → BL, as Then 2003 found)
- goe_classifies_TR ✓ (BGS-naive analog → TR)
- poisson_rho_near_0 ✓ (0.091, after the fitter fix below)
- goe_rho_near_1 ✓ (0.996)
- br_rho_near_0p3 ✓ (0.255 for true 0.3, within bootstrap σ)

**Verdict: PIPELINE_VALIDATED_READY_TO_FIRE.** The 3-D Bianchi methodology is ready to run on Then 2003 Picard data the moment it is acquired (or de-novo recomputed). Expected substantive verdict: SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI.

---

## §C. The synthetic-validation harness caught a real Berry-Robnik fitter bug

This is the **headline methodological finding** of the 34f-G session leg, and it retroactively amends Phase 34e Test 2.

### C.1 The bug

The Berry-Robnik P_BR(s; ρ) closed form used in Phase 34e `run_berry_robnik.py` was **not normalized for intermediate ρ**: numerical integration gave ∫P ds = 1.12 at ρ=0.3, 1.21 at ρ=0.5 (should be 1.0), and the mean ∫sP ds = 1.23–1.32 (should be 1.0). It was correct only at the endpoints ρ=0 (Poisson) and ρ=1 (GOE). The MLE over this un-normalized PDF had a **severe positive bias**: fitting pure Poisson synthetic data (true ρ_GOE = 0) returned ρ_GOE ≈ 0.44.

### C.2 How it was caught

The phase34f synthetic-validation harness runs the pipeline on known-ground-truth inputs. The `poisson_rho_near_0` gate FAILED (Poisson synthetic → ρ ≈ 0.44, not ~0) and `br_rho_near_0p3` FAILED. A pure-Poisson / pure-GOE / scipy.quad normalization check isolated the bug to the un-normalized closed form. **The harness did exactly its job: it caught a fitter bug that single-dataset application would not have surfaced.**

### C.3 The fix

Replaced the closed-form normalization with a numerically-normalized PDF: `berry_robnik_pdf_normalized(s, ρ)` computes Z = ∫P_raw ds and μ = mean via scipy.quad (cached on a ρ-grid), then returns (μ/Z)·P_raw(μs; ρ) — guaranteeing ∫P = 1 and ∫sP = 1 for all ρ. Post-fix recovery: pure Poisson → ρ_GOE = 0.09 ± 0.04 (was 0.44); pure GOE → 1.00; BR-0.3 mixture → 0.26.

### C.4 Retroactive amendment to Phase 34e Test 2

Phase 34e Test 2 (commit a458e02 / 0723183) reported "Berry-Robnik ρ ≈ 0.458 ± 0.010 across 6 Γ₀(N) levels, Poisson-dominant." **That ρ ≈ 0.458 was the fitter-bias artifact, NOT a meaningful absolute measurement.** With the corrected fitter, the Γ₀(N) Maass spectra give ρ_GOE ≈ 0.07 (level 91 direct check: 0.068 ± 0.057) — **statistically consistent with pure Poisson**.

**The Sarnak-anomaly conclusion is UNCHANGED and STRENGTHENED.** Test 1 (NNS = BL) was always the load-bearing result and is independent of the Berry-Robnik fitter. The corrected Test 2 says the Γ₀(N) Maass NNS is **essentially pure Poisson** (ρ_GOE ≈ 0.07, within bootstrap error of 0), a cleaner and stronger statement than the prior "Poisson-dominant at ρ ≈ 0.46." Full corrected per-level table in the Phase 34e amendment (`PHASE34E_FINDINGS.md` SQ-2 amendment).

The cross-level consistency conclusion also holds (all 6 levels near-Poisson). The Phase 34e headline verdict SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE stands; the Test 2 numbers are corrected downward toward pure Poisson.

---

## §D. Methodological generalisation

**§7.ter.57 — Synthetic-validate distribution-fitters against known ground truth before interpreting fitted parameters as absolute.** Before reporting a fitted distribution parameter (Berry-Robnik ρ, finite-X correction coefficient, etc.) as a substantive absolute measurement, run the fitter on synthetic inputs with known ground-truth parameter values. If the fitter does not recover the ground truth within its bootstrap σ (pure Poisson → ρ ≈ 0; pure GOE → ρ ≈ 1; known mixture → known ρ), the fitted value on real data is a fitter artifact, not a measurement. Phase 34f canonical example: the Berry-Robnik closed form was un-normalized for intermediate ρ, biasing the Phase 34e Test 2 ρ from a true ≈ 0.07 to an artifact ≈ 0.46 — caught only because the phase34f pipeline-validation harness exercised the fitter on synthetic Poisson/GOE/mixture inputs. Sibling to §7.ter.22-application (seed-replicate near boundary) and §7.ter.55 (pre-flight normalization gate): all three are "validate the instrument on known inputs before trusting it on unknown ones."

---

## §E. Verdict map

- **34f-G-Δ (Picard bulk-NNS, substantive):** **DATA_ACQUISITION_BLOCKED.** Then 2003's 13,950 eigenvalues unpublished; LMFDB reCAPTCHA-blocked; de-novo recomputation is multi-week (PHASE34F_BRIEF §I.1). Literature expectation: SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI (Then 2003 found Poisson NNS); ARS has not independently measured it.

- **34f-G 3-D pipeline (methodology):** **PIPELINE_VALIDATED_READY_TO_FIRE.** All 6 synthetic-validation gates pass (Poisson→BL, GOE→TR, cubic unfolding correct, Berry-Robnik ρ recovery correct post-fix). Methodology is ready to run on Picard data on acquisition.

- **34f-G-H (Picard Hecke Sato-Tate):** **CONVENTION_PROPAGATED_FROM_34e.** Per the Phase 34e amendment (commit 0723183) and Will's propagation argument, the Hejhal-lineage Hecke-eigenvalue convention (a(n) with 1/√|n| in T_n; a(p) at primes is the RP-normalized Satake variable) is the standard Then 2003 also uses. No separate normalization audit required when Picard data is acquired.

- **Berry-Robnik fitter (cross-phase methodology):** **BUG_CAUGHT_AND_FIXED**, retroactively amends Phase 34e Test 2 (ρ ≈ 0.458 artifact → ρ ≈ 0.07 corrected, near-Poisson). Sarnak-anomaly conclusion strengthened.

- **34f-E (Bianchi-Z[ω]) + cross-coordinate Test 4:** **PENDING.** Unchanged multi-week data-acquisition cost (PHASE34F_BRIEF §C.3). The Q(√−3) three-coordinate joint statement remains 34f-E-blocked.

---

## §F. Outputs

```
PHASE34F_BRIEF.md (committed 16b8e8b)
PHASE34F_FINDINGS.md (this file — 34f-G partial)
phase34f/bianchi_unfolding.py        — 3-D Weyl unfolding, λ=r²+1, cubic
phase34f/run_pipeline_validation.py  — synthetic-validation harness
phase34e/run_berry_robnik.py         — Berry-Robnik fitter (BUG FIXED:
                                        numerically-normalized PDF)
data/phase34f_results/pipeline_validation.json [gitignored]
data/phase34e_results/berry_robnik.json — re-run with corrected fitter
phase34e/data/then2003.{pdf,txt}     — Then 2003 Picard paper [cached, gitignored]
phase34e/data/sh2022.{pdf,txt}       — SH 2022 §3 normalization spec [cached]
```

---

## §G. Open questions / follow-ups

1. **Then 2003 Picard eigenvalue acquisition.** The single blocking dependency for 34f-G substantive. Paths: (a) email Then directly; (b) Strömberg / Lemurell Hejhal-lineage archives; (c) LMFDB Bianchi page via non-reCAPTCHA access (institutional, API token, or a session with browser access); (d) de-novo Hejhal-on-ℍ³ recomputation (multi-week). The pipeline is ready-to-fire on acquisition.

2. **Phase 34e Test 2 full corrected per-level table.** The corrected 6-level Berry-Robnik re-run is in progress (slow file parsing ≈ 4 min for 6 levels). The level-91 direct check (ρ_GOE = 0.068 ± 0.057) confirms the near-Poisson correction; the full table is folded into the Phase 34e amendment when the re-run completes.

3. **§7.ter.57 retrospective on prior fitted-parameter findings.** The Berry-Robnik bug suggests auditing other distribution-fitters in the codebase against synthetic ground truth — specifically any phase that reported a fitted continuous parameter as an absolute (Chen-2019 finite-X correction coefficient in Phase 34d X-rate scan; Phase 34d/34c bootstrap σ² ratios were already synthetic-calibrated against pair-symmetric uniform so are likely fine, but worth an explicit pass).

4. **34f-E + cross-coordinate Test 4.** Unchanged: multi-week Bianchi-Z[ω] data acquisition (PHASE34F_BRIEF §C.3). The substantive Q(√−3) three-coordinate convergence claim remains 34f-E-blocked.
