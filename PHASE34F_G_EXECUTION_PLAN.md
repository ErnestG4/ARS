# PHASE 34f-G EXECUTION PLAN
## Picard PSL(2,ℤ[i])\ℍ³ Bianchi-Maass — replication of Then 2003 via validated 34e methodology

**Status:** Pre-execution. Operationalizes PHASE34F_BRIEF §B–E for the 34f-G cell specifically, incorporating PHASE34E_FINDINGS closure learnings + 34e amendments (§D.0 gate doubly-vindicated, cross-LEVEL pivot pattern, factor-of-2 unfolding diagnostic, §7.ter.57 synthetic-validated Berry-Robnik fitter discipline with baseline-relative thresholds).

**Predecessor:** PHASE34E_FINDINGS (post-amendments commits 0723183 + ca090d4) — `SARNAK_ANOMALY_REPLICATED_AT_GAMMA0_N_SQUAREFREE`. Δ-side methodology validated on 2-D rigorous Γ₀(N) Maass data with corrected Berry-Robnik fitter; H-side SH normalization closed (a(p) at primes, no rescale, Hejhal-lineage standard per SH 2022 §3).

**Reconciliations applied in this committed revision (2026-05-15):** (i) **§F.2 reframed** to lead with Test-1 cross-dimensional bulk-NNS consistency as the primary novel content; Berry-Robnik Δρ demoted to supplementary/exploratory with the underpowered-fitter caveat explicit; **§C.2 framing line softened** to match; **§G.4** already correctly framed (unchanged). (ii) **§F.3 volume reconciliation:** the Bianchi-Z[ω] fundamental-domain volume is PINNED to the Humbert-direct value √3·L(2,χ_{−3})/8 ≈ 0.16915693 in `phase34f/bianchi_unfolding.py`, superseding the EGM 0.0845776 placeholder used in the 34f-G partial (commit ca090d4); both values are cited; verified by `bianchi_unfolding.volume_constants_self_test()` against the Then 2003 Picard anchor (G/3 ≈ 0.30532186). bulk-NNS classification is unfolding-scale-invariant, so the pin changes no verdict — it only eliminates the silent code↔plan disagreement.

**Scope of this plan:**

- IN: 34f-G-Δ bulk-NNS classification on Picard Bianchi-Maass Δ-eigenvalues (replication of Then 2003).
- IN: 34f-G-Δ Berry-Robnik Δρ characterization with baseline-differenced cross-comparison to 34e Γ₀(N) Δρ ≈ 0.036 ± 0.032 baseline (per §7.ter.57).
- IN: 34f-G-H Sato-Tate execution (unblocked per 34e amendment; convention propagated from 34e closure).
- OUT: 34f-E (PSL(2,ℤ[ω]) first-measurement) — separate execution plan after 34f-G closes.
- OUT: §D.2 field-comparison panel — needs 34f-E Δρ.
- OUT: §D.4 cross-coordinate Test 4 — needs 34f-E signal-bearing finding.

---

## §A. Pre-flight checklist (week 0)

### A.1 Data acquisition — Then 2003 Picard dataset

**Primary action item:** contact H. Then directly. Request:
- Raw Δ-eigenvalue list (Picard PSL(2,ℤ[i])\ℍ³ Maass spectrum).
- Hecke eigenvalue lists at prime ideals of ℤ[i] (for §D.3 unblocked).
- Computational provenance documentation: algorithm version (Hejhal-style 3-D extension specifics), eigenvalue separation criteria, precision tier, parity/sector restrictions if any.

**Affiliation lookup:** Then's published affiliation circa 2003 was Universität Ulm (Steiner group, Theoretische Physik). Current affiliation needs verification via Google Scholar / ORCID / Mathematics Genealogy / DBLP before contact. Expected response window: 1–4 weeks.

**Backup paths if Then unresponsive or dataset unavailable:**

- **B1 — Strömberg MAASS package extension.** Check whether Strömberg's PARI-based MAASS package has 3-D Bianchi extensions; if so, recompute Picard eigenvalues to comparable depth as Then's. Lower implementation cost than B3.
- **B2 — Adjacent Bianchi-computational groups.** Direct contact: Cremona (Warwick), Booker (Bristol), Strömberg (Chalmers), or others identified during the literature pass. Any of them may have computed Picard Maass eigenvalues since 2003 even if not formally published.
- **B3 — Full re-implementation.** Implement Then 2003 algorithm independently. Estimated effort: 4–8 weeks careful work. Worth doing if (a) Then unresponsive AND backups exhausted AND (b) 34f-E will need independent 3-D Bianchi-Maass infrastructure anyway, in which case the re-implementation amortizes across both cells.

### A.2 §D.0 pre-flight normalization gate (Bianchi-specific)

Before any test, verify:

- **Spectral-parameter convention.** Confirm dataset uses LMFDB Bianchi convention λ = r² + 1, or document the variant used. Common alternatives: λ = 1 + r² (equivalent), λ = r² (high-r asymptotic equivalent but shifted near small r), λ = (1/4 + r²) (incorrectly inherited 2-D convention). Convert to LMFDB convention before any downstream processing.
- **Hecke-eigenvalue normalization (§D.3 unblocked per 34e amendment commit 0723183).** SH 2022 §3 confirmed: stores a(p) at primes with no rescale; Hejhal-lineage standard that propagates to Then 2003 as same lineage convention. §D.0 assertion: confirm Then 2003 Hecke values follow Hejhal a(p) convention (no rescale) — working assumption per 34e closure, no separate Then-convention audit required. Verify range plausibility (|a(p)| ≤ 2√p under Ramanujan); document any escape as methodology-error candidate.

§D.0 failure on either axis = highest-priority debug trigger before Test 1 runs.

### A.3 Volume constant numerical verification

Humbert formula for Q(i): Vol(PSL(2,ℤ[i])\ℍ³) = |d_K|^(3/2) · ζ_K(2) / (4π²) with d_K = −4, ζ_K(2) = ζ(2)·L(2, χ_{−4}) = (π²/6)·G:

$$\text{Vol(Picard)} = \frac{4^{3/2}}{4\pi^2} \cdot \frac{\pi^2 G}{6} = \frac{2G}{6} = \frac{G}{3}$$

where G = Catalan's constant ≈ 0.91596559417721901505...

**Numerical values to hardcode (with citation to Humbert + Catalan):**

- Vol(Picard) = G/3 ≈ 0.30532186472574...
- Unfolding constant: Vol/(6π²) = G/(18π²) ≈ 0.005155...

The unfolding constant is ~16× smaller than the 2-D SL(2,ℤ) constant (1/12 ≈ 0.0833). Combined with the cubic-vs-quadratic exponent (x_j = const·r_j³ in 3-D vs x_j = const·r_j² in 2-D), the effect on required raw-eigenvalue count for given statistical power is substantial: reaching unfolded-eigenvalue count N_unfolded = 5000 in Picard requires raw r-range up to roughly (5000/0.00516)^(1/3) ≈ 99, vs (5000·12)^(1/2) ≈ 245 in 2-D SL(2,ℤ). Different scaling laws; verify Then's data reaches sufficient r-range before committing to statistical-power claims.

### A.4 LMFDB Bianchi content scan (light pass)

LMFDB has rational Bianchi *newforms* (holomorphic) for d ∈ {−3, −4, −7, −8, −11} via Cremona's bianchi-progs. **These are not Maass forms.** Scan LMFDB Bianchi pages and recent (2023–2026) update changelogs for any Maass-side content additions since the brief was written. If anything material has appeared, fold into A.1 backup-path planning.

---

## §B. Code adaptation roadmap from 34e

The 34e codebase (phase34e/) supplies most of the toolchain. 34f-G adaptations follow.

### B.1 New substrate-specific files

**phase34f_g/picard_loader.py** ← phase34e/maass_loader.py adapted

- Read Then 2003 dataset format (specifics TBD pending acquisition; may be tabular ASCII, CSV, custom binary).
- Output schema: `(form_id, r_j)` for Δ-eigenvalues; `(form_id, prime_ideal, hecke_eigenvalue)` for Hecke side conditional on availability.
- Built-in §D.0 normalization gate: assert spectral parameter convention, log convention chosen, abort with diagnostic if values are outside expected range.

**phase34f_g/picard_unfolding.py** ← phase34e/sl2z_unfolding.py adapted

- Cubic in r: `x_j := (Vol / (6 * π²)) * r_j³`
- Vol constant hardcoded as `VOL_PICARD = CATALAN_CONSTANT / 3` with explicit reference to Humbert formula derivation.
- Empirical mean-spacing diagnostic: compute `⟨s⟩` after unfolding; log warning if not within tolerance of 1. **34e finding: empirical ⟨s⟩ ≈ 2.0 across Γ₀(N) levels flagged parity/sector restriction in SH dataset.** Same diagnostic on Picard will surface analogous dataset structure for documentation.

### B.2 Substrate-agnostic files (direct reuse)

- **phase34e/run_nns_classification.py** — NNS engine, calibrator zoo (Poisson, Wigner-Dyson β=1/2/4, COE/CUE/CSE), §7.ter.22 threshold-crossing handling. Operates on unfolded sequence x_j only; no substrate-specific assumptions. **Direct reuse.**
- **phase34e/run_berry_robnik.py** — Berry-Robnik ρ fit with 30-bootstrap σ. **Direct reuse.**

These files passed cross-LEVEL validation across 6 Γ₀(N) levels in 34e; no substrate-specific bugs surfaced. The substrate-agnostic interface is the methodology-validation payoff from 34e.

### B.3 Cross-validation file (modified)

**phase34f_g/run_cross_validation.py** ← phase34e/run_cross_level.py adapted

- 34e ran across 6 Γ₀(N) levels for cross-LEVEL reproducibility.
- 34f-G runs cross-PARTITION reproducibility within Picard dataset (if Then's data has multiple computational seeds, precision tiers, or sub-spectrum partitions) OR against backup-path recomputation (B1/B2/B3).
- Single-source degenerate case: if only one Picard dataset is available, cross-validation collapses to partial-replication labeling per 34e §7.ter.54 discipline.

### B.4 Hecke-side files (unblocked per 34e amendment)

**phase34f_g/run_sato_tate.py** ← phase34e/run_sato_tate.py (post-amendment) adapted

Convention is `CONVENTION_PROPAGATED_FROM_34e`: SH stores a(p) at primes, no rescale, Hejhal-lineage standard per SH 2022 §3 (closed in commit 0723183). Propagates to Then 2003 as same-lineage convention; no separate Then-data audit required.

Steps:

- Load Picard Hecke eigenvalues via picard_loader with assertion: values stored as a(𝔭) with no rescale; convention matches Hejhal lineage.
- Apply standard Sato-Tate analysis with finite-P correction (Chen-2019 NLO structure per Phase 34d).
- Verdict labels per PHASE34F_BRIEF §E.4.

---

## §C. Test execution order

Sequential gating per PHASE34F_BRIEF §F.2 go/no-go discipline.

### C.1 Test 1 — Bulk-NNS classification on Picard Δ-eigenvalues

**Steps:**

1. Load Picard Δ-eigenvalues via picard_loader (§B.1) with §D.0 gate.
2. Apply picard_unfolding (§B.1); log empirical mean-spacing diagnostic.
3. Run substrate-agnostic NNS classifier (§B.2) with 20-seed 80%-subsample bootstrap.
4. Output: rep_med ± σ, ks_gue_med ± σ, full-N and 20-seed primary classifications.

**Expected outcome:** BL (Poisson-leaning) per Then 2003. rep_med ≪ 0.10 (TR/BL boundary), 20/20 seeds classifying BL.

**Failure mode (REPLICATION_FAILED_AT_PSL2_ZI):** rep_med > 0.10, TR classification on multiple seeds. Most likely causes (in priority order):

1. Wrong Vol constant in unfolding (factor of 4π² or 6π² missing/doubled).
2. Spectral parameter convention mis-conversion at §D.0.
3. Cubic exponent miscoded as quadratic (carried-over 2-D bug).
4. Parity / Atkin-Lehner-sector contamination causing pseudo-spectrum that classifies TR.

Stop on failure; debug systematically before proceeding.

### C.2 Test 2 — Berry-Robnik ρ fit and cross-dimensional comparison (baseline-differenced)

**Discipline:** apply §7.ter.57 (synthetic-validated fitter + baseline-relative thresholds, added per 34e amendment commit 0723183). The 34e phase34f synthetic-validation harness caught Berry-Robnik fitter bias: the corrected fitter's pure-Poisson baseline is ≈ 0.09, not 0. Absolute ρ values are fitter-implementation-dependent; only baseline-differenced Δρ is meaningful for cross-comparison.

**Steps:**

1. Apply synthetic-validated Berry-Robnik fitter to unfolded Picard NNS.
2. 30-bootstrap σ on the fit.
3. Establish 3-D fitter pure-Poisson baseline: run the fitter on synthetic 3-D Weyl-unfolded Poisson sequences (the pipeline-validation harness already exercises cubic unfolding on synthetic 3-D Weyl spectra per Point 3 confirmation). Output: ρ_Poisson-baseline(3D).
4. Compute baseline-differenced statistic: Δρ_34f-G := ρ_GOE(Picard) − ρ_Poisson-baseline(3D).

**Cross-dimensional comparison — baseline-differenced framing (secondary / exploratory):**

The *primary* substantive result of 34f-G is Test 1: robust bulk-NNS BL classification of the unfolded Picard Δ-spectrum (the Sarnak anomaly proper — scale-invariant, fitter-independent). The Berry-Robnik Δρ comparison below is a *secondary, exploratory* characterization, not the headline finding, and must not be reported as one (see the §F.2 reframe and §G.4). It is in particular *not* the absolute-scale question "does Picard's ρ match Γ₀(N)'s ρ" (fitter-dependent, invalidated). At most, limited by fitter precision, it asks as an exploratory check:

> *(exploratory, underpowered)* Is Δρ_34f-G (3-D Picard, baseline-differenced) consistent with Δρ_34e (2-D Γ₀(N) squarefree, baseline-differenced)?

| Substrate | ρ_GOE ± σ | ρ_Poisson-baseline | Δρ (baseline-differenced) |
|---|---|---|---|
| Γ₀(N) squarefree, 2-prime-divisor (34e, corrected) | 0.126 ± 0.032 | ≈ 0.09 (2-D fitter) | ≈ 0.036 ± 0.032 |
| Picard PSL(2,ℤ[i])\ℍ³ (34f-G, target) | TBD | TBD (3-D fitter; synthetic-Poisson-calibrated) | TBD |

Note: the corrected Γ₀(N) Δρ ≈ 0.036 ± 0.032 is barely distinguishable from zero at 1σ. The "Sarnak anomaly" is captured robustly by Test 1 NNS classification (rep_med ≪ 0.10 → BL); the Berry-Robnik ρ shows only a marginal quantitative anomaly-shape signal at this resolution. The cross-dimensional question is therefore whether Picard shows a similarly marginal Δρ, a substantially larger Δρ, or near-zero Δρ — interpreted only as exploratory supporting detail.

**Three interpretive cases (baseline-differenced):**

- **Δρ_34f-G ≈ Δρ_34e within bootstrap σ (both ≈ marginal):** cross-dimensional consistency of the marginal Berry-Robnik signal. Anomaly shape parameter behaves similarly in 2-D Γ₀(N) and 3-D Picard at the imaginary-quadratic / class-number-1 level after baseline correction.
- **Δρ_34f-G substantially larger than Δρ_34e:** Picard shows stronger GOE-fraction signal than Γ₀(N) squarefree, baseline-corrected. Could indicate higher Hecke degeneracy at 3-D Bianchi level-1 vs composite 2-D Γ₀(N) level decoration — or dimensional structural difference.
- **Δρ_34f-G substantially smaller than Δρ_34e or near zero:** Picard shows Poisson-like NNS clustering even more cleanly than Γ₀(N) — stronger arithmetic anomaly. Worth investigating for orbifold-specific Hecke multiplicity attribution.

**Literature comparison caveat (per Point 1 sync):** Published ρ ∈ [0.3, 0.5] values (Bogomolny-Schmit / Sarnak) use a properly-normalized Berry-Robnik that is **not directly comparable to our fitter's raw output**. Two paths:

- **(preferred) Calibrate** our fitter against a literature-reproduced case — recover a published ρ value on a published spectrum and back out the baseline shift to map our scale onto the literature scale.
- **(fallback) Internal-scale only** — report Δρ throughout, decline absolute-ρ-vs-literature comparison, document the limitation.

Then 2003's own reported ρ should also be cross-referenced but only after the same baseline-differencing discipline is applied; if Then's fitter has different bias than ours, compare via the corresponding Δρ.

### C.3 Test 3 — Sato-Tate (unblocked per 34e amendment)

Convention propagated from Phase 34e: SH a(p)-at-primes-no-rescale = Hejhal-lineage standard = applicable to Then 2003 data. Test 3 runs in standard execution sequence — no deferral.

Steps:

1. Load Picard Hecke eigenvalues via picard_loader with §D.0 convention assertion.
2. Apply Sato-Tate measurement with finite-P scan per 34d Chen-2019 NLO structure (P_max ∈ {10³, 10⁴, 10⁵} as data depth allows).
3. Pre-spec verdict per PHASE34F_BRIEF §E.4: `SATO_TATE_REPLICATED_AT_HECKE_EIGENVALUES_PER_CELL` with finite-P correction documented if present.

**Ramanujan-conditional caveat (carried from PHASE34F_BRIEF §B.4):** Sato-Tate verdict assumes empirical |a(𝔭)| stays within Ramanujan bound. Document any escape from the range as a methodology-error flag, not as Ramanujan falsification.

### C.4 Test 4 — Cross-validation within Picard

Compare verdicts across Picard dataset partitions (different seeds, precision tiers, or sub-spectrum splits) if available. If only single-source Picard data: cross-validation degenerates to partial-replication per 34e §7.ter.54.

---

## §D. Decision gates

### D.1 Data-acquisition gate (week 1–4)

After A.1 / A.2 / A.4 close:

- **Then's data acquired:** proceed to §B/§C standard path.
- **Backup B1/B2 yields data:** proceed with documented backup-source provenance noted in final FINDINGS.
- **Only B3 (full re-implementation) remains:** re-assess timeline (~4–8 weeks added). Decide whether (a) defer 34f-G to focus on a more cost-effective acquisition path, or (b) commit to B3 with the rationale that 34f-E will need independent 3-D infrastructure anyway and B3 amortizes.

### D.2 §D.0 normalization gate (immediately before Test 1)

Standard gate per 34e methodology vindication. Halt if fails; do not propagate.

### D.3 Test 1 outcome gate

- **REPLICATED:** proceed to Test 2.
- **PARTIAL:** investigate dataset-provenance / unfolding-constant / convention; partial-replication is acceptable forward-progress with documentation.
- **FAILED:** stop; do not proceed to Test 2/3/4 or 34f-E until 3-D methodology is debugged.

### D.4 Test 2 outcome gate

- **Δρ_34f-G in expected baseline-differenced range (consistent with 34e Δρ ≈ 0.036 ± 0.032 or interpretable as one of the three cases in §C.2):** forward to §F closure.
- **Δρ_34f-G in unexpected baseline-differenced range:** investigate (could be 3-D structural difference vs 2-D; could be methodology bug; could be substantively novel); document either way as observation worth dedicated FINDINGS section.

---

## §E. Expected timeline

**Scenario A — Then's data available, week 1 response:**

| Week | Activity |
|---|---|
| 1 | Data acquisition + §D.0 gate |
| 2 | Code adaptation (§B) + Test 1 |
| 3 | Tests 2 and 4 |
| 4 | FINDINGS writeup + METHODS.md updates |

Total: ~4 weeks to closure.

**Scenario B — Backup B1/B2 dataset, week 2–4:**

| Week | Activity |
|---|---|
| 1–4 | Data acquisition via backup path (contact + dataset transfer / extraction) |
| 4–5 | Code adaptation + Test 1 |
| 6 | Tests 2 and 4 |
| 7 | FINDINGS writeup |

Total: ~6–7 weeks to closure.

**Scenario C — Re-implementation B3:**

| Week | Activity |
|---|---|
| 1–8 | Re-implementation of Then 2003 algorithm + validation |
| 8–9 | Code adaptation + Test 1 |
| 10 | Tests 2 and 4 |
| 11 | FINDINGS writeup |

Total: ~10–11 weeks to closure. Worth committing to only if 34f-E independent infrastructure is also part of the budget.

**Test 3 (Sato-Tate) timeline:** runs in standard sequence alongside Tests 2/4 per CONVENTION_PROPAGATED_FROM_34e; no longer deferral-dependent. Folds into the same week as Tests 2/4 in each scenario above.

---

## §F. Expected outputs and closure

### F.1 Verdict targets per PHASE34F_BRIEF §E.1

- Primary Δ-side: `SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI` per Then 2003.
- Primary H-side: `SATO_TATE_REPLICATED_AT_HECKE_EIGENVALUES_AT_PSL2_ZI` (now standard execution with convention propagated from 34e).
- Joint closure: `METHODOLOGY_CONSISTENCY_ACROSS_BIANCHI_SUBSTRATES_AT_PSL2_ZI` if both substrates land their expected verdicts.
- Possible qualifier: `_PARTIAL` if Test 4 single-source (only one Picard dataset partition available).

### F.2 Cross-comparison findings (novel content beyond pure replication)

**Primary novel content — Test-1 cross-dimensional bulk-NNS consistency.**

- **Picard bulk-NNS verdict (3-D) vs Γ₀(N) squarefree bulk-NNS verdict (2-D; 34e: all 6 levels BL, 20/20 subsample seeds, rep_med 0.02–0.07):** the substantive cross-dimensional statement is whether the Sarnak anomaly's *NNS-level* signature — robust BL classification of the unfolded Δ-spectrum — reproduces across the 2-D Γ₀(N) and 3-D Picard arithmetic settings (both class-number-1 imaginary-quadratic; Γ₀(N) squarefree level vs Bianchi level-1). This is the scale-invariant, fitter-independent result and is **the headline novel content of 34f-G beyond the pure Then-2003 replication.** Pre-spec: rep_med ≪ 0.10 with 20/20 seeds BL on Picard, *jointly* with the 34e Γ₀(N) BL result → `METHODOLOGY_CONSISTENCY_ACROSS_BIANCHI_SUBSTRATES` at the NNS-level Sarnak signature. Asymmetric-label discipline (§7.ter.49 / METHODS): a joint BL is methodology-consistency across two settings, **not** a discovery — the Sarnak anomaly is 30+ years lit-confirmed.

**Supplementary / exploratory (underpowered — do NOT headline).**

- **Δρ_34f-G (baseline-differenced) vs Δρ_34e (Γ₀(N) squarefree, baseline-differenced ≈ 0.036 ± 0.032):** exploratory only. The corrected 34e Δρ is barely ~1σ from zero (§C.2, §G.4) and the Berry-Robnik fitter is underpowered at this resolution per §7.ter.57; report Δρ *with the explicit underpowered-fitter caveat* and do not present it as a primary cross-dimensional finding. Internal-scale-only unless the fitter is calibrated against a literature-reproduced case (§C.2 path A).
- **ρ_34f-G vs literature (Bogomolny-Schmit / Sarnak ρ ∈ [0.3, 0.5] on properly-normalized fitter):** supplementary; only if fitter baseline-calibrated against literature scale; otherwise defer to internal-scale Δρ comparison.
- **Unfolding mean-spacing (⟨s⟩) diagnostic on Picard:** does the empirical ⟨s⟩ structure match 34e's ⟨s⟩ ≈ 2.0 parity/sector signature, or differ? Documents Picard dataset structure (parity, Atkin-Lehner analog at Bianchi level, newforms-only restriction, etc.). Supporting detail, not a primary finding. (NB: this is the *empirical-spacing* diagnostic — distinct from the *fundamental-domain-volume* factor-2 reconciled in §F.3; kept terminologically separate to avoid the collision.)

### F.3 Forward enablement for 34f-E

After 34f-G closes:

- 3-D Bianchi-Maass methodology validated against published anchor (Then 2003).
- Code framework (picard_loader, picard_unfolding) is template for `phase34f_e/psl2zomega_loader.py` and `phase34f_e/psl2zomega_unfolding.py`.
- Vol(PSL(2,ℤ[ω])\ℍ³) numerical value ready: from Humbert with d_K = −3 and L(2, χ_{−3}):
  - Vol = 3^(3/2) · ζ_Q(√−3)(2) / (4π²)
  - = (3√3/(4π²)) · (π²/6) · L(2, χ_{−3})
  - = (√3/8) · L(2, χ_{−3})
  - = 0.21650635 · 0.78130241 ≈ **0.16915693** (Humbert-direct).

  **§F.3 VOLUME RECONCILIATION (2026-05-15 — code↔plan pin).** This
  Humbert-direct value **0.16915693** is now PINNED in
  `phase34f/bianchi_unfolding.py` (`BIANCHI_Z_OMEGA_VOLUME`,
  `bianchi_z_omega_volume()`), derived from the *same* Humbert formula
  chain as the Picard anchor Vol(Picard) = G/3 ≈ 0.30532186 (§A.3) —
  this plan and the code now agree on exactly this value. It
  **SUPERSEDES** the placeholder 0.0845776180 (the
  Elstrodt-Grunewald-Mennicke "smallest Bianchi orbifold" value) that
  was used in the 34f-G partial — recorded in RESULTS.md §7.ter (frozen
  chronological entry, commit ca090d4, left intact per the RESULTS.md
  §7.ter convention) and in the PHASE34F_FINDINGS §B.1 bullet (now
  AMENDED 2026-05-15 with this reconciliation). EGM's 0.0845776 is the
  Humbert-direct value / ~2: the ω↔ω² involution (Z[ω]'s order-6 unit
  group vs Z[i]'s order-4) is an extra Z/2 *extended-orbifold* quotient.
  Both 0.16916 (Humbert-direct, **chosen**) and 0.08458 (EGM
  extended-orbifold-quotient) are defensible *if cited*; we pin
  Humbert-direct so Picard and Z[ω] derive from one identical,
  anchor-verified formula chain. The pin is enforced by
  `bianchi_unfolding.volume_constants_self_test()`: it asserts the chain
  reproduces Then 2003's Picard 0.305 to 4 sig figs (independent of the
  d_K=−3 choice) and that the module literal equals the pinned closed
  form (anti-drift). bulk-NNS classification is unfolding-scale-invariant
  (§G.5), so this pin changes **no 34f-G or 34f-E verdict** — its sole
  purpose is to eliminate the silent code↔plan disagreement (the bug
  class flagged here).
- Hecke-side Sato-Tate path inherited from 34e + 34f-G with convention propagated (no separate normalization investigation required for 34f-E).

### F.4 Field-comparison panel (deferred to 34f-E closure)

34f-G Δρ provides one of two values for §D.2 field-comparison panel; 34f-E Δρ provides the other (each baseline-differenced against its own 3-D fitter's pure-Poisson baseline per §C.2 discipline). Panel closes after 34f-E. Pre-staging: report 34f-G Δρ with explicit pre-spec for the comparison test.

### F.5 Cross-coordinate Test 4 (deferred to 34f-E closure)

Substantive joint statement on Q(√−3) requires 34f-E signal + Test 4 bridge function or window-aggregated correlation per PHASE34F_BRIEF §D.4. Deferred until 34f-E closure.

---

## §G. Open items and risks

### G.1 Then's response timeline
Primary driver of Scenario A vs B vs C. Contact within week 1; escalate to backup paths if no response within 4 weeks.

### G.2 §D.0 conversion errors as common bug source
3-D vs 2-D spectral parameter conventions (λ = r² + 1 vs λ = 1/4 + r²), Vol-constant entries (G/3 = 0.3053 not 1/12), unfolding exponent (cubic vs quadratic). Validate against Then's own reported eigenvalue spacings (cross-check empirical spacing distribution against published before running Test 1).

### G.3 SH normalization closure — RESOLVED
Phase 34e amendment commit 0723183 closed the SH Hecke-normalization investigation: a(p) at primes with no rescale, Hejhal-lineage standard per SH 2022 §3. Convention propagates to Then 2003 as Hejhal-lineage. 34f-G-H is unblocked; no Then-convention audit required separately. Tracked here as a resolved item, not an open risk.

### G.4 Cross-dimensional Δρ interpretation
If 34f-G Δρ (baseline-differenced) differs significantly from 34e Δρ ≈ 0.036 ± 0.032, deciding "2-D vs 3-D structural difference" vs "Picard-specific vs Γ₀(N)-specific" requires more data — at minimum 34f-E Δρ for cross-orbifold disambiguation within 3-D. Don't over-interpret 34f-G Δρ alone in a writeup. (Note: corrected 34e Δρ ≈ 0.036 is barely 1σ from zero — interpretive resolution on cross-dimensional Berry-Robnik comparison is fundamentally limited at this fitter precision; consider this when scoping FINDINGS claims.)

### G.5 Bianchi-specific subtleties potentially absent from 2-D toolchain
- Atkin-Lehner involutions don't have a direct Bianchi analog at level 1 (Picard is level-1 over Q(i)).
- Cusps in 3-D differ in structure from 2-D (1-cusp PSL(2,ℤ[i])\ℍ³ vs 1-cusp SL(2,ℤ)\ℍ²; both topologically simple but geometrically distinct).
- Volume-formula precision worth getting right for the unfolding sanity-check, but **not load-bearing for 34f-G's two primary tests**. Test 1 (NNS) is scale-invariant (34e ⟨s⟩ ≈ 2.0 did not perturb the BL verdict); Test 2 (Berry-Robnik fit) explicitly renormalizes s = s/mean(s) before fitting. Volume precision becomes load-bearing only for global-moment statistics (σ²(K,X)-type), which are not in 34f-G scope. Get right as good practice; don't over-weight in execution priority. (This is exactly why the §F.3 Humbert-vs-EGM volume reconciliation changes no verdict — it is a code↔plan hygiene fix, not a result-affecting correction.)

Document any 3-D-specific empirical quirks for METHODS.md candidate entries beyond the 34e §7.ter.53–57 set.

### G.6 Re-implementation cost ↔ 34f-E amortization decision
Scenario C (full B3 re-implementation) is justifiable on cost-amortization grounds *if* 34f-E will eventually require independent 3-D Bianchi-Maass infrastructure anyway. Decision should be made at the §D.1 gate with explicit 34f-E forward-budget consideration.

---

## §H. Bibliographic note — RESOLVED

Lowry-Duda 2025 (arXiv:2502.01442) attribution corrected in PHASE34E_BRIEF §H.2 per commit ca090d4 (residual §C.1 header tidied). No remaining citation drift; no batch fix needed.

---

End of execution plan.
