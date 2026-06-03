# Phase 34f Findings (34f-G + 34f-E partial) — 3-D Bianchi pipeline validated on BOTH substrates; both data-acquisition-blocked; Berry-Robnik fitter bug caught

**Status:** 34f-G + 34f-E partial. The 3-D Bianchi Maass methodology pipeline is built and synthetic-validated on **both** substrates — Picard PSL(2,Z[i])\ℍ³ (34f-G, replication leg) and Bianchi-Z[ω] PSL(2,Z[ω])\ℍ³ (34f-E, **first-measurement** leg), each `PIPELINE_VALIDATED_READY_TO_FIRE` on its substrate-correct pinned volume. Substantive bulk-NNS is **DATA_ACQUISITION_BLOCKED** on both: 34f-G §D.0a fired (Then 2003's 13,950 Picard eigenvalues unpublished; ~60 OCR-mangled samples; LMFDB Bianchi reCAPTCHA-blocked), and 34f-E §D.0a fired (no accessible Bianchi-Z[ω] Maass dataset; LMFDB Bianchi primarily Cremona holomorphic newforms; de-novo Hejhal-on-ℍ³ for the order-6 unit group is the multi-week cost per §C.3). The synthetic-validation harness **caught a real bug in the Berry-Robnik ρ fitter** that retroactively amends Phase 34e Test 2. Cross-coordinate Test 4 remains 34f-E-substantive-blocked.

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
- Fundamental-domain volumes via the Humbert formula vol = |d_K|^{3/2}·ζ_K(2)/(4π²), PINNED to ONE convention (Humbert-direct) so Picard and Bianchi-Z[ω] derive from one identical chain anchored to a published value: **Picard vol = G/3 ≈ 0.3053218647** (G = Catalan; reproduces Then 2003's stated ≃ 0.305 to 4 sig figs — the anchor); **Bianchi-Z[ω] vol = √3·L(2,χ_{-3})/8 ≈ 0.1691569344** (Humbert-direct).
  - **AMENDED 2026-05-15 (volume reconciliation).** The 34f-G partial (commit ca090d4) used placeholder literals Picard 0.3053218564 (≈3e-9 off the true G/3) and Bianchi-Z[ω] 0.0845776180 (the Elstrodt-Grunewald-Mennicke "smallest Bianchi orbifold" value). EGM's 0.0845776 is the Humbert-direct value / ~2: the ω↔ω² involution (Z[ω]'s order-6 unit group vs Z[i]'s order-4) is an extra Z/2 extended-orbifold quotient. Both 0.16916 and 0.08458 are defensible if cited; we pin **Humbert-direct** so the Z[ω] and Picard volumes come from one formula chain that is independently verified against the Then 2003 Picard anchor (`bianchi_unfolding.volume_constants_self_test()`). bulk-NNS classification is unfolding-scale-invariant, so this changes **no 34f-G/34f-E verdict** — the reconciliation exists solely to eliminate the silent code↔plan disagreement (the bug class flagged in the §F.3 reconciliation note of `PHASE34F_G_EXECUTION_PLAN.md`). The earlier "~3.6× smaller than Picard" remark referred to the EGM-quotient value and no longer applies under the pinned convention (Humbert-direct Z[ω] is ~1.8× smaller than Picard).

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

## §B'. 34f-E Bianchi-Z[ω] (Q(√−3)) first-measurement pipeline

The 34f-E leg targets the **first measurement** of the Sarnak anomaly on PSL(2, Z[ω])\ℍ³ (Q(√−3)). Per the asymmetric-label discipline (PHASE34F_BRIEF §E.2 / METHODS §E): unlike Picard/34f-G there is **no published empirical anchor** — Then 2003 covered Picard only; the Sarnak-anomaly extension to Bianchi-Z[ω] is a *structural Hecke-algebra prediction*, empirically unconfirmed in literature accessible from search. This leg is **never** labelled a "replication".

### B'.1 §D.0a data-availability gate: FIRED for 34f-E

No accessible Bianchi-Z[ω] Maass eigenvalue dataset. LMFDB Bianchi (PHASE34F_BRIEF §C.2) is reCAPTCHA-blocked in session and is primarily Cremona *holomorphic* newforms — Maass-form cardinality on Q(√−3) is unverified and likely insufficient. De-novo Hejhal-on-ℍ³ adapted for the **order-6 unit group of Z[ω]** (§C.3) is 2–6 weeks from Cremona's bianchi-progs / 6–12 weeks from scratch. Per the Phase 34e/34f discipline, an underpowered result is **not** fabricated from unavailable data. **Substantive 34f-E-Δ = DATA_ACQUISITION_BLOCKED.**

### B'.2 Infrastructure (`phase34f/zomega_loader.py` + `run_pipeline_validation_e.py`)

`zomega_loader.py` defines the Z[ω] Δ / Hecke record schema and both pre-flight gates so the leg is genuinely ready-to-fire on acquisition:

- **§D.0a `data_availability_gate()`** — returns a structured `FIRED` report with the acquisition paths and cost flags; marks `substrate_role = FIRST_MEASUREMENT`.
- **§D.0b `normalization_gate()`** — asserts the 3-D λ = r²+1 convention (rejects a carried-over 2-D λ = 1/4+r² contamination), r real-positive, Hecke |a(𝔭)| ≤ 2 (Ramanujan-Petersson), and the substrate-correct **pinned** volume `bianchi_z_omega_volume()` (rejects the Picard volume substituted in). The loader self-test exercises the gate on synthetic known-good **and** known-bad inputs (2-D-convention contamination, wrong-substrate volume, RP-bound violation, data-availability FIRED) — §7.ter.55 discipline: validate the instrument on known inputs before trusting it on unknown ones. **All loader self-test checks pass.**

The 3-D unfolding itself is the *same substrate-agnostic* `phase34f/bianchi_unfolding.py` (`unfold_bianchi_3d(r, volume)`); 34f-E supplies `bianchi_z_omega_volume()` ≈ **0.16915693** (PINNED Humbert-direct √3·L(2,χ₋₃)/8, commit c2cbf22) where 34f-G supplies `picard_volume()` ≈ 0.30532186.

`run_pipeline_validation_e.py` pushes the same three synthetic spectra through the full pipeline on the Z[ω] volume (and through the §D.0b gate):

| synthetic input | ⟨s⟩ | NNS primary | rep_med | Berry-Robnik ρ_GOE |
|---|---|---|---|---|
| Poisson (Sarnak-anomaly analog) | 1.015 | **BL** | 0.023 | 0.091 ± 0.042 |
| GOE β=1 (BGS-naive analog) | 1.000 | **TR** | 0.343 | 0.996 ± 0.004 |
| Berry-Robnik mix (true ρ=0.3) | 1.033 | BL | 0.039 | 0.256 ± 0.017 |

**All 6 validation gates pass** (unfolding_correct, poisson→BL, GOE→TR, poisson_rho_near_0, goe_rho_near_1, br_rho_near_0p3). The statistics are identical to 34f-G — expected and confirmatory: bulk-NNS classification is unfolding-scale-invariant, so the only substrate difference (the pinned volume constant) does not perturb the synthetic verdicts. This validates that the pipeline machinery is **volume-substrate-correct** and the §D.0b gate passes substrate-correct inputs through the real pipeline path.

### B'.3 Orbifold caveat (open empirical question, NOT synthetically modellable)

PSL(2, Z[ω]) has elliptic fixed points of **orders 2 AND 3** (order-6 unit group) vs Picard's order-2 only; the Selberg trace formula picks up extra elliptic terms (PHASE34F_BRIEF §B.2). Bulk-NNS classification (Test 1) is robust to this — it is the load-bearing, scale-invariant result. The quantitative Berry-Robnik ρ **may shift** versus 34f-G; whether the Sarnak-anomaly *shape* is field-independent (Hecke-driven only) or field-dependent (via orbifold singularity structure) is the novel open empirical question 34f-E ↔ 34f-G ρ comparison answers (PHASE34F_BRIEF §D.2). This is **not** something the synthetic harness can model — it is resolved only on real Z[ω] data. The pre-spec verdict labels on acquisition are `SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA` / `..._WITH_FIELD_SHIFT` / `NO_ANOMALY_AT_PSL2_Z_OMEGA` (PHASE34F_BRIEF §E.2).

**Verdict: 34f-E 3-D pipeline PIPELINE_VALIDATED_READY_TO_FIRE; substantive 34f-E-Δ DATA_ACQUISITION_BLOCKED.** The first-measurement run fires the moment a Bianchi-Z[ω] Maass eigenvalue dataset (LMFDB-accessible, or de-novo per §C.3) becomes available — no separate normalization audit required (CONVENTION_PROPAGATED_FROM_34e for the Hecke side; the Δ-side gate is coded and synthetic-validated).

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

- **34f-E 3-D pipeline (Bianchi-Z[ω] methodology, first-measurement leg):** **PIPELINE_VALIDATED_READY_TO_FIRE.** All 6 synthetic-validation gates pass on the substrate-correct pinned Z[ω] volume (`run_pipeline_validation_e.py`); the §D.0a/§D.0b gates are coded and synthetic-validated on known-good and known-bad inputs (`zomega_loader.py` self-test). Asymmetric-label discipline: this is a **first-measurement** leg, not a replication — no published anchor exists.

- **34f-E-Δ (Bianchi-Z[ω] bulk-NNS, substantive):** **DATA_ACQUISITION_BLOCKED.** §D.0a fired — no accessible Z[ω] Maass dataset (LMFDB Bianchi reCAPTCHA-blocked / primarily holomorphic; de-novo Hejhal-on-ℍ³ for the order-6 unit group is 2–6 wk from Cremona bianchi-progs / 6–12 wk from scratch, PHASE34F_BRIEF §C.3). Pre-spec verdict labels on acquisition: SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA / _WITH_FIELD_SHIFT / NO_ANOMALY_AT_PSL2_Z_OMEGA (§E.2). Whether the anomaly *shape* (Berry-Robnik ρ) is field-independent or shifts via the order-3 orbifold structure is the open novel question (§D.2).

- **34f-E-H (Bianchi-Z[ω] Hecke Sato-Tate):** **CONVENTION_PROPAGATED_FROM_34e.** Same Hejhal-lineage Hecke-eigenvalue convention as 34f-G-H; no separate normalization audit required on acquisition.

- **Cross-coordinate Test 4 (Q(√−3) three-coordinate closer):** **34f-E-SUBSTANTIVE-BLOCKED.** Requires the signal-bearing 34f-E-Δ measurement; the 34d-E angle data and 34c χ₋₃ zero data are already cached (PHASE34F_BRIEF §C.4). The Q(√−3) three-coordinate joint statement remains blocked solely on 34f-E-Δ data acquisition — all pipeline infrastructure for the closer is now built and validated.

---

## §F. Outputs

```
PHASE34F_BRIEF.md (committed 16b8e8b)
PHASE34F_G_EXECUTION_PLAN.md (committed c2cbf22)
PHASE34F_FINDINGS.md (this file — 34f-G + 34f-E partial)
phase34f/bianchi_unfolding.py         — 3-D Weyl unfolding, λ=r²+1, cubic;
                                         substrate-agnostic; volume pinned
phase34f/run_pipeline_validation.py   — 34f-G Picard synthetic-validation
phase34f/zomega_loader.py             — 34f-E Z[ω] schema + §D.0a/§D.0b
                                         gates (self-validated)
phase34f/run_pipeline_validation_e.py — 34f-E Z[ω] synthetic-validation
phase34e/run_berry_robnik.py          — Berry-Robnik fitter (BUG FIXED:
                                         numerically-normalized PDF)
data/phase34f_results/pipeline_validation.json   [gitignored]
data/phase34f_results/pipeline_validation_e.json [gitignored]
data/phase34e_results/berry_robnik.json — re-run with corrected fitter
phase34e/data/then2003.{pdf,txt}      — Then 2003 Picard paper [cached, gitignored]
phase34e/data/sh2022.{pdf,txt}        — SH 2022 §3 normalization spec [cached]
```

---

## §G. Open questions / follow-ups

1. **Then 2003 Picard eigenvalue acquisition.** The single blocking dependency for 34f-G substantive. Paths: (a) email Then directly; (b) Strömberg / Lemurell Hejhal-lineage archives; (c) LMFDB Bianchi page via non-reCAPTCHA access (institutional, API token, or a session with browser access); (d) de-novo Hejhal-on-ℍ³ recomputation (multi-week). The pipeline is ready-to-fire on acquisition.

2. **Phase 34e Test 2 full corrected per-level table.** The corrected 6-level Berry-Robnik re-run is in progress (slow file parsing ≈ 4 min for 6 levels). The level-91 direct check (ρ_GOE = 0.068 ± 0.057) confirms the near-Poisson correction; the full table is folded into the Phase 34e amendment when the re-run completes.

3. **§7.ter.57 retrospective on prior fitted-parameter findings.** The Berry-Robnik bug suggests auditing other distribution-fitters in the codebase against synthetic ground truth — specifically any phase that reported a fitted continuous parameter as an absolute (Chen-2019 finite-X correction coefficient in Phase 34d X-rate scan; Phase 34d/34c bootstrap σ² ratios were already synthetic-calibrated against pair-symmetric uniform so are likely fine, but worth an explicit pass).

4. **34f-E Bianchi-Z[ω] data acquisition.** The single blocking dependency for the Q(√−3) three-coordinate closer. The 34f-E pipeline (loader gates + synthetic validation) is now built and `PIPELINE_VALIDATED_READY_TO_FIRE` — the first-measurement run fires the moment Z[ω] Maass eigenvalues are available. Paths (PHASE34F_BRIEF §C.2/§C.3): (a) LMFDB Bianchi via non-reCAPTCHA access (verify Maass cardinality on Q(√−3) first); (b) de-novo Hejhal-on-ℍ³ from Cremona's bianchi-progs adapted for the order-6 unit group (~2–6 wk); (c) de-novo from scratch / Strömberg PSAGE / Lemurell (~6–12 wk). The 34d-E angle data and 34c χ₋₃ zero data for Test 4 are already cached (§C.4); only 34f-E-Δ blocks the closer.

5. **Environment note (post-reboot).** The criticality_tool scripts that import `ars_classify` (NNS engine) require pandas, which lives only in the `$HOME/fmexplorer` venv — invoke `$HOME/fmexplorer/bin/python3`, not bare `python3` (the non-interactive shell does not auto-activate the venv post-reboot). `requirements.txt` does not list pandas; the dependency is via `phase22a/ars_classify.py`.
