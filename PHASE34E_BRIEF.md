# PHASE 34e BRIEF
## SL(2,ℤ) Maass eigenvalue spectrum — methodology validation against the Sarnak anomaly

**Status:** Pre-execution. Brief defines substrate, observables, calibrator zoo, dataset pipeline, asymmetric verdict labels, and forward dependency mapping to 34f-G and 34f-E.

**Field:** ℚ (canonical rational case; methodology calibrator for Q(i) and Q(√−3) at 34f).
**Substrate:** Δ-eigenvalues on SL(2,ℤ)\ℍ² (Maass cusp forms); companion substrate Hecke eigenvalues at primes.
**Right null (BGS-naive prediction):** Wigner-Dyson GOE β=1 bulk NNS for chaotic hyperbolic Δ-spectra.
**Expected empirical outcome (Sarnak anomaly):** Poisson-leaning bulk NNS with level clustering, driven by Hecke-induced geodesic-length-spectrum multiplicities.
**Headline pre-spec verdict:** SARNAK_ANOMALY_REPLICATED_AT_SL2Z if empirical bulk NNS shows the documented deviation from GOE toward Poisson-leaning clustering at literature-consistent magnitude across at least the rigorous-data subset; falsification verdict GOE_AT_SL2Z if bulk matches GOE β=1 cleanly without the documented anomaly (methodology debugging trigger, not a publication result).

---

## §A. Placement in cross-coordinate architecture

Phase 34e is the **SL(2,ℤ) (ℚ-rational) Maass calibrator** for the Bianchi-Maass extensions in Phase 34f. The published Sarnak anomaly — Sarnak 1987; Bolte-Steil-Steiner 1992; Bogomolny-Leyvraz-Schmit 1996; Bogomolny-Georgeot-Giannoni-Schmit 1997 — provides a mature target that the integrated ARS instrument should replicate at the verdict-label level. This is methodology-validation against a published anchor, not scientific discovery. The empirical content is in:

1. Reproducing the published anomaly with the ARS calibrator zoo and asymmetric-verdict-label discipline at the precision of modern rigorous Maass-form datasets.
2. Cross-validating across three independent Maass-form datasets (Seymour-Howell 2022 Zenodo, Booker-Strömbergsson-Venkatesh 2006, Then 2003/2005) which have not previously been jointly cross-checked for spectral-statistics consistency.
3. Characterizing the anomaly shape with the same bootstrap-variance + threshold-crossing methodology (§7.ter.22) developed in 34d.
4. Extending the ARS prime-angle measurement substrate from Z[i]/Z[ω] (Phase 34d Gaussian/Eisenstein) to the Hecke-eigenvalue side of SL(2,ℤ) Maass forms (Sato-Tate substrate) — a parallel methodology calibrator on the companion observable.

34e closure unlocks 34f infrastructure:

- **34f-G:** replicate Then 2003's PSL(2,ℤ[i])\ℍ³ Maass measurement with the validated 34e toolchain (Q(i) Bianchi orbifold; established empirical anchor).
- **34f-E:** extend to PSL(2,ℤ[ω])\ℍ³ Maass measurement on Q(√−3) Bianchi orbifold (first-measurement candidate; no published empirical anchor located via literature search).

The three-coordinate joint statement on Q(√−3) — angles (34d-E), zeros (34c χ₋₃), eigenvalues (34f-E) — depends on 34f-E being signal-bearing, which depends on 34e validating the Maass-spectrum methodology against the canonical case.

If 34e fails to replicate the Sarnak anomaly on SL(2,ℤ), the entire Maass-side architecture is in question — debugging trigger, not a downstream phase.

---

## §B. Substrate, observables, and predictions

### B.1 Spectral substrate

Maass cusp forms on Γ = PSL(2,ℤ) acting on ℍ² are non-holomorphic Hecke eigenfunctions f: Γ\ℍ² → ℂ of the hyperbolic Laplacian Δ = −y²(∂²_x + ∂²_y) satisfying (Δ + λ)f = 0, cuspidal at every cusp, square-integrable in the Petersson inner product. The eigenvalue is parameterized λ = 1/4 + r² for spectral parameter r ≥ 0. The first few rigorous values (Booker-Strömbergsson-Venkatesh 2006, to 100 decimal places):

- r₁ ≈ 9.53369526135355755434...
- r₂ ≈ 12.17300832467967784952...
- r₃ ≈ 13.77975135189073894424...
- r₄ ≈ 14.35850951825981277986...
- r₅ ≈ 16.13807317152103058019...

### B.2 Weyl law and unfolding

The Selberg trace formula yields the asymptotic eigenvalue counting function:

$$N(T) := \#\{r_j \le T\} \sim \frac{\text{Area}}{4\pi} T^2 \text{ as } T \to \infty$$

with Area = π/3 (hyperbolic area of the SL(2,ℤ) fundamental domain). Unfolding maps the raw spectrum r_j → x_j := r_j²/12 so the unfolded sequence has asymptotic mean spacing 1. ARS bulk-NNS measurements operate on the unfolded x_j, not on raw r_j.

Subleading Weyl-law corrections (cusp contribution, identity term, log corrections) are sub-percent at the scales 34e operates and do not affect bulk-NNS classification, but should be retained in the unfolding for any quantitative comparison to RMT prediction shapes. Document which corrections are included in the unfolding pipeline.

### B.3 Right null (BGS-naive prediction)

The Bohigas-Giannoni-Schmit conjecture (BGS 1984: "spectra of generic chaotic Hamiltonians follow random-matrix universality") applied to the hyperbolic Laplacian on Γ\ℍ² for chaotic Γ predicts Wigner-Dyson GOE β=1 NNS:

$$P_{\text{GOE}}(s) = \frac{\pi}{2} s \exp\left(-\frac{\pi s^2}{4}\right)$$

- Linear level repulsion at s → 0.
- Roughly Gaussian decay at large s.
- Mean 1 under correct unfolding.

This is the BGS-naive right null — "what one would predict from generic chaotic dynamics without knowledge of the arithmetic structure."

### B.4 Expected empirical outcome (Sarnak anomaly)

The arithmetic structure of SL(2,ℤ) introduces large-multiplicity degeneracies in the geodesic length spectrum: closed geodesics on Γ\ℍ² correspond to conjugacy classes of hyperbolic elements in Γ, and the Hecke algebra acts on the Δ-spectrum producing high-multiplicity eigenspaces. The Bolte-Steil-Steiner / Bogomolny-Leyvraz-Schmit / Bogomolny-Georgeot-Giannoni-Schmit empirical work shows the bulk NNS shifts away from GOE toward Poisson-leaning level clustering:

$$P_{\text{Poisson}}(s) = e^{-s}$$

- No level repulsion at s → 0 (no factor of s).
- Exponential decay at large s.

The empirical SL(2,ℤ) bulk NNS lies *between* Poisson and GOE — closer to Poisson than to GOE at high statistical significance, with the precise shape captured well by a Berry-Robnik interpolation P_BR(s; ρ) with ρ in the Poisson-dominant regime (prior empirical work suggests ρ in the lower half of [0,1]). Subleading periodic-orbit-family contributions (Bogomolny-Schmit semiclassical analysis) produce specific P(s) modulations at characteristic length-spectrum scales, but the **load-bearing signal is the bulk shape shift, not a small-scale bump**.

This is the "Sarnak anomaly": documented violation of BGS-naive universality by the arithmetic structure of Γ. ARS detects the anomaly by measuring the bulk shift; the anomaly is the *expected* result.

### B.5 Companion observable: Hecke eigenvalues at primes (Sato-Tate)

Each Maass eigenform f has Fourier coefficients a_p(f) at primes p related to Hecke operator eigenvalues by T_p f = λ_p(f) f. Under the Ramanujan-Petersson normalization, λ_p ∈ [−2, 2] (Ramanujan-Petersson is open for Maass forms in general; Kim-Sarnak bounds give |λ_p| ≤ 2 · 7/64 ≈ 0.219 + 2 unconditionally and the conjectured bound holds in all measured cases).

The horizontal Sato-Tate distribution (fixed Maass form f, varying p) is conjectured:

$$d\mu_\infty(x) = \frac{1}{\pi}\sqrt{1 - x^2/4}\, dx \text{ on } [-2, 2]$$

— the semicircular SU(2) Sato-Tate measure. For Maass forms over ℚ this is conjectural; for holomorphic forms over ℚ it is proven (Barnet-Lamb-Geraghty-Harris-Taylor 2011 via potential modularity). Empirical evidence on individual Maass forms is overwhelmingly consistent with semicircular.

ARS prime-angle measurement on Hecke eigenvalues of SL(2,ℤ) Maass forms is the natural extension of the Phase 34d Gaussian/Eisenstein prime-angle measurement onto a different substrate (Maass-form Hecke eigenvalue instead of Z[i]/Z[ω] prime norm angle). Right null: semicircular Sato-Tate. Expected empirical outcome: semicircular Sato-Tate (no anomaly predicted on the Hecke-eigenvalue side; methodology calibration).

### B.6 Two-substrate ARS measurement on SL(2,ℤ) Maass forms

Phase 34e measures two substrates derived from the same arithmetic object:

- **34e-Δ:** bulk-Δ-eigenvalue NNS. Signal-bearing — Sarnak anomaly is the expected empirical outcome, deviation from BGS-naive right null.
- **34e-H:** prime Hecke-eigenvalue distribution. Null-bearing — Sato-Tate semicircular is both right null and expected empirical outcome; methodology calibrator.

34e-Δ is the substrate that 34f-G and 34f-E extend; 34e-H is the calibrator that 34c/34d ARS toolchain operates on natively.

---

## §C. Data infrastructure

### C.1 Primary dataset: Seymour-Howell 2022 (+ Lowry-Duda 2025 LMFDB database announcement)

- **Seymour-Howell 2022**, "Rigorous computation of Maass cusp forms of squarefree level," Res. Number Theory 8:64. arXiv:2201.08760.
- **Zenodo dataset:** DOI 10.5281/zenodo.7105772 (rigorous Maass forms of squarefree level, including SL(2,ℤ) trivial level).
- **GitHub:** github.com/aseymourhowell/Maass-Form-Trace-Formula-Code.
- **Lowry-Duda 2025**, "A database of rigorous Maass forms," arXiv:2502.01442 (most recent; announces the LMFDB Maass database across Γ₀(N) congruence subgroups, including 2,202 N=1 forms; describes the three rigorous computation methods incl. Seymour-Howell trace formula). [Author: David Lowry-Duda — NOT Seymour-Howell; corrected from initial search-derived attribution.]

This is the workhorse dataset for 34e: several thousand rigorous Maass cusp forms across squarefree levels, with Laplace eigenvalues and Hecke eigenvalues at validated precision. Trivial level N = 1 = SL(2,ℤ) is the canonical case.

### C.2 Cross-validation dataset 1: Booker-Strömbergsson-Venkatesh 2006

- **BSV 2006**, "Effective Computation of Maass Cusp Forms," Int. Math. Res. Notices 2006:71281.
- First rigorous algorithm for SL(2,ℤ) Maass forms.
- Eigenvalues to 100 decimal places.
- Smaller dataset than Seymour-Howell; higher per-form precision.

### C.3 Cross-validation dataset 2: Then 2003/2005

- **Then 2005**, "Maass cusp forms for large eigenvalues," Math. Comput. 74:363–381. arXiv:math-ph/0305047.
- Extends to large r_j (high in the spectrum).
- Hejhal-algorithm-based, heuristic precision (not rigorous in the BSV/SH sense).
- Critical for the statistical power of bulk-NNS classification: more eigenvalues = tighter classification at the cost of rigor.

### C.4 LMFDB

- lmfdb.org Maass form section (modular forms → Maass).
- Aggregated dataset; provenance varies across BSV / Hejhal / Then sources.
- Useful as a sanity check on individual eigenvalues, not as primary dataset.

### C.5 Three-dataset cross-validation strategy

Phase 34e runs the bulk-NNS classification independently on (a), (b), (c) above and tests verdict-label agreement. If all three give SARNAK_ANOMALY_REPLICATED_AT_SL2Z with consistent magnitude, methodology is fully validated. If verdicts diverge, the divergence pattern is itself the investigation — possible sources include:

- Unfolding-methodology differences (which Weyl-law corrections retained).
- Eigenvalue-count differences (statistical power, especially at high r).
- Precision differences (rigorous-but-shallow vs heuristic-but-deep).

This cross-dataset diagnostic is **novel methodological content** — these three datasets have been used separately in the spectral-statistics literature but not jointly cross-checked.

### C.6 Hecke-eigenvalue data

Hecke eigenvalues a_p(f) at primes p ≤ P_max available in all three datasets above. Normalization convention (Ramanujan-Petersson scaling, λ_p ∈ [−2, 2]) should be verified across datasets before pooling. For 34e-H Sato-Tate measurement, Seymour-Howell dataset is sufficient at P_max ~ 10⁴–10⁵ per form across the SL(2,ℤ) trivial-level subset; for cross-dataset Sato-Tate cross-validation, normalization conventions must be aligned explicitly.

---

## §D. Tests and verdict labels

### §D.0 Pre-flight normalization gate

Before any cross-dataset pooling or substrate analysis, verify Hecke-eigenvalue and spectral-parameter normalization conventions across the three primary datasets:

- Confirm Ramanujan-Petersson rescaling: λ_p ∈ [−2, 2] for the empirical Hecke-eigenvalue data in Seymour-Howell, BSV, and Then.
- Verify Hecke-eigenvalue convention is consistent across datasets: if any uses a different normalization (e.g., un-normalized a_p vs Ramanujan-normalized λ_p, or a different weight-correction factor), rescale before joint analysis.
- Confirm spectral-parameter convention: λ = 1/4 + r² for SL(2,ℤ) Maass forms (2-D hyperbolic). All three datasets follow this convention; flag if any does not (the 3-D convention λ = r² + 1 is used in 34f and must not be mixed).

Failure of the normalization check is the highest-priority debugging trigger before any Test 1–4 result is meaningful. Without this gate, a Sato-Tate "departure" verdict on 34e-H could be a 2× rescaling artifact rather than a substrate finding. (Mirrors PHASE34F_BRIEF §D.0 gate, applied per 2-D SL(2,ℤ) substrate.)

### D.1 Test 1 — Bulk-NNS classification (34e-Δ)

**Pipeline:**

1. Pull Δ-eigenvalues r_j from each dataset (a), (b), (c).
2. Unfold via x_j := r_j²/12 (Weyl-law leading term, SL(2,ℤ)). Document subleading-term inclusion.
3. Compute nearest-neighbor spacings s_j := x_{j+1} − x_j; verify ⟨s⟩ ≈ 1 (sanity check on unfolding).
4. Apply ARS NNS engine with extended calibrator zoo:
   - Poisson (P(s) = e^{−s})
   - GOE β=1 (Wigner surmise)
   - GUE β=2 (Wigner surmise)
   - GSE β=4 (Wigner surmise)
   - COE / CUE / CSE β-equivalents (per 34c/34d Katz monodromy expansion; same β as G-counterparts by Katz-Sarnak bulk equivalence)
5. Compute rep_med over 20 random 80%-subsamples per dataset (§7.ter.22 threshold-crossing handling from 34d).
6. Classify: BL (Poisson-leaning), TR (Wigner-Dyson β=1, GOE-class), or AMBIGUOUS.

**Pre-specified outcome:** rep_med classifies BL with high Welch separation from GOE β=1 across the rigorous datasets, per the published Sarnak anomaly. The expected separation magnitude is large given that prior empirical work distinguishes Poisson-leaning vs GOE cleanly on this substrate.

### D.2 Test 2 — Anomaly-shape quantification

The Sarnak anomaly is not pure Poisson — it interpolates between Poisson and GOE with the Poisson side dominant. Quantitative shape characterization:

1. Fit empirical P(s) to a Berry-Robnik interpolation P_BR(s; ρ) capturing the GOE-fraction; report fitted ρ with bootstrap σ.
2. Compare fitted ρ across the three datasets; expect 0 < ρ < 0.5 (Poisson-dominant) per prior empirical work.
3. Report small-s and large-s asymptotic behavior separately: small-s should show no linear repulsion (Poisson-like, possibly with sub-leading correction); large-s should show approximately exponential decay.

**Methodological add (optional):** Bogomolny-Schmit semiclassical analysis predicts specific subleading P(s) modulations from periodic-orbit-family contributions at characteristic length-spectrum scales. If the empirical P(s) shows these modulations at the predicted scales, that strengthens the replication beyond bulk-shape alone. Specific scale predictions require explicit Bogomolny-Schmit calculation on SL(2,ℤ); optional for 34e core, candidate add-on if 34e wants stronger anomaly characterization than bulk shape alone.

### D.3 Test 3 — Hecke-eigenvalue Sato-Tate distribution (34e-H)

**Pipeline:**

1. Pull Hecke eigenvalues λ_p(f) at primes p ≤ P_max for each Maass form f in the dataset.
2. Pool across forms (horizontal Sato-Tate); also compute per-form distribution (vertical Sato-Tate) as separate sub-test.
3. Apply ARS prime-angle engine with calibrator: semicircular Sato-Tate μ_∞.
4. Test 34d-style finite-X correction: σ²(K, P_max)/(N/K) as a function of P_max ∈ {10³, 10⁴, 10⁵}; check 1/log P_max scaling toward asymptote 1.000 per Chen-2019 NLO.
5. Classify: SATO_TATE_REPLICATED_AT_HECKE_EIGENVALUES, with or without documented finite-P correction.

**Pre-specified outcome:** Semicircular Sato-Tate replicated with σ²/(N/K) → 1 with finite-P correction structure consistent with Phase 34d. This is methodology validation — same toolchain that landed Phase 34d on Gaussian/Eisenstein primes should land here on Maass-form Hecke eigenvalues. Substantive deviation from Sato-Tate would be a methodology error to debug, not a discovery.

### D.4 Test 4 — Cross-dataset reproducibility

Compare verdict labels from Tests 1–3 across the three independent Maass-form datasets. Acceptance criterion: same verdict label on all three, with bootstrap-σ overlap on the quantitative parameters (Berry-Robnik ρ for Test 2; finite-P correction coefficient for Test 3).

**Disagreement-pattern catalog:**

- Seymour-Howell vs BSV diverge → precision/methodology difference (BSV more precise but smaller dataset).
- Seymour-Howell vs Then diverge → rigor/heuristic difference (Then heuristic but reaches higher eigenvalues).
- All three diverge → fundamental methodology issue.

This is the novel methodological content of 34e — first joint cross-validation of these three datasets at the spectral-statistics level.

### §D.5 (forward-deferred) — Spectral form factor on SL(2,ℤ) Maass

Forward-looking note, not in 34e core scope. Haehl-Reeves-Rozali 2023 (JHEP 12:161, arXiv:2309.00611) reformulates arithmetic chaos via the spectral form factor:

$$\text{SFF}(t) := \left| \sum_j e^{i x_j t} \right|^2$$

(sum over unfolded eigenvalues). The SFF picks up a "linear ramp" at intermediate t from universal eigenvalue repulsion; arithmetic anomaly appears as theory-dependent subleading corrections. SL(2,ℤ) SFF computation on Seymour-Howell + Then datasets would be the canonical-case validation underpinning the Bianchi-side SFF flagged at PHASE34F_BRIEF §D.5. Flag here so the 2-D baseline is in place if 34f or a subsequent phase wants to engage AdS₃-RMT₂ duality framing (Boruch-Di Ubaldo-Haehl-Perlmutter-Rozali 2024–2025). Otherwise deferred.

---

## §E. Pre-specified verdict labels (asymmetric)

Following the 34d asymmetric-verdict-label discipline:

### E.1 34e-Δ (bulk NNS)

- **SARNAK_ANOMALY_REPLICATED_AT_SL2Z:** rep_med classifies BL across all three datasets; high Welch separation from GOE β=1; Berry-Robnik ρ in the Poisson-dominant regime with cross-dataset consistency. Headline pre-spec verdict.
- **SARNAK_ANOMALY_REPLICATED_AT_SL2Z_PARTIAL:** Replicated on Seymour-Howell + BSV but not Then (or some 2-of-3 subset). Methodology validated against the rigorous-data subset; Then's heuristic precision flagged as potentially insufficient at high r. Acceptable forward-progress verdict.
- **METHODOLOGY_INCONSISTENT_ACROSS_DATASETS:** Different datasets give different verdicts beyond the partial-replication pattern. Debugging required before downstream phases proceed.
- **GOE_AT_SL2Z (counter-anomaly):** rep_med classifies TR (GOE-like) on all datasets, contradicting the published Sarnak anomaly. Almost certainly a methodology error (likely in unfolding or NNS computation). Investigate; do not propagate.
- **AMBIGUOUS:** rep_med crosses BL/TR boundary; threshold-crossing investigation per §7.ter.22.

### E.2 34e-H (Hecke prime-angle Sato-Tate)

- **SATO_TATE_REPLICATED_AT_HECKE_EIGENVALUES:** Semicircular distribution reproduced to 1σ at P_max = 10⁵; finite-P deficit closes with Chen-2019-NLO-consistent 1/log P scaling. Methodology calibration successful.
- **SATO_TATE_REPLICATED_AT_FINITE_P_WITH_CORRECTION:** Same as above but with explicit documentation of finite-P correction in the saturation regime — direct analog of the Phase 34d Gaussian-side verdict shape.
- **SATO_TATE_DEPARTURE_AT_HECKE_EIGENVALUES:** Significant deviation from semicircular distribution beyond finite-P correction. Highly unlikely given established literature; flag for methodology debugging.

### E.3 Cross-verdict (joint Δ + H)

- **METHODOLOGY_CONSISTENCY_ACROSS_MAASS_SUBSTRATES_AT_SL2Z:** Both 34e-Δ and 34e-H land their expected verdicts with consistent error structure across the rigorous datasets. Full methodology validation; 34f infrastructure planning unlocked.

---

## §F. Forward dependency mapping to 34f

### F.1 34f-G (Picard, Q(i))

If 34e closes successfully, 34f-G runs the validated toolchain on Then 2003's PSL(2,ℤ[i])\ℍ³ Maass spectrum. Key parameter changes:

- Spectral parameter convention: λ = r² + 1 in hyperbolic 3-space (LMFDB Bianchi convention) vs λ = 1/4 + r² in 2-D.
- Unfolding constant changes: volume of Picard fundamental domain ≠ π/3; specific value per Then 2003 / standard reference.
- Calibrator zoo unchanged (Poisson + Wigner-Dyson family).

**34f-G expected verdict:** SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI per Then 2003. Replication of a published empirical result with the validated 34e methodology.

### F.2 34f-E (PSL(2,ℤ[ω]), Q(√−3))

34f-E extends to PSL(2,ℤ[ω])\ℍ³ Maass spectrum. No published empirical anchor located via literature search (Then 2003 covered Picard only; PSL(2,ℤ[ω])\ℍ³ Maass-form spectral statistics not surfaced).

34f-E is therefore a **first-measurement candidate**. The Sarnak anomaly *should* extend to PSL(2,ℤ[ω]) by the same Hecke-algebra structural argument, but empirical confirmation has not previously been attempted (or has not surfaced in literature accessible from search). The order-6 unit group of ℤ[ω] (vs. order-4 of ℤ[i]) introduces extra orbifold singularity structure; whether this affects the anomaly shape quantitatively is an open empirical question.

**34f-E expected verdict:** SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA per asymmetric label discipline.

**Infrastructure cost flag (forward dependency for 34f, not 34e):** PSL(2,ℤ[ω])\ℍ³ Maass eigenvalues do not appear to exist as a published dataset. De novo computation required. Existing tools (Then 2003 algorithm, Strömberg algorithms) extend in principle but require non-trivial implementation work for the order-6 unit group. Pre-flight estimation of compute cost and implementation effort needed before 34f-E commits.

### F.3 Cross-coordinate joint statement on Q(√−3)

If 34f-E lands SARNAK_ANOMALY_FIRST_MEASUREMENT, the three-coordinate joint statement on Q(√−3) closes:

- 34d-E (angle coordinate): null at right-null (RW shape + Chen-2019 finite-X correction)
- 34c χ₋₃ (zero coordinate): null at right-null (Katz-Sarnak Sp-class)
- 34f-E (Maass eigenvalue coordinate): signal per Sarnak anomaly

Structural unity: the Hecke ring of ℤ[ω] acts consistently across all three observables. The **substantive** claim — SHARED_HECKE_ANOMALY_ACROSS_COORDINATES_ON_Q_SQRT_M3 — requires the cross-coordinate Test 4 specified in PHASE34F_BRIEF §D.4 (Option A structural Hecke-character decomposition or Option B window-aggregated coarser correlation, depending on whether the bridge function can be derived in advance). Phase 34e does not test this directly but provides the methodology validation that 34f-E will use to land its half of the joint statement.

---

## §G. Candidate METHODS.md updates upon 34e closure

The following methodology entries are candidates for METHODS.md upon successful 34e closure. Numbering provisional; merge into existing §7.ter ladder at Will's discretion.

**G.1 Maass-spectrum substrate handling.** Eigenvalue parameterization conventions (2-D: λ = 1/4 + r²; 3-D: λ = r² + 1). Weyl-law unfolding with leading + subleading term selection. Calibrator zoo specialization for Δ-eigenvalue substrates (Wigner-Dyson β=1 right null for non-arithmetic chaotic; Poisson-leaning expected for arithmetic case).

**G.2 Cross-dataset reproducibility discipline.** When multiple independent datasets exist for the same substrate, run the classifier independently on each, report verdict consistency, and characterize divergence patterns. Bootstrap-σ overlap is the consistency criterion. Disagreement catalog: precision vs rigor vs eigenvalue-count tradeoffs.

**G.3 Sarnak-anomaly canon entry.** Published prediction shapes (Poisson-leaning Berry-Robnik); periodic-orbit-family modulation locations (Bogomolny-Schmit); expected magnitudes from prior empirical work; bridge to Hecke-eigenvalue Sato-Tate substrate as a separate observable on the same arithmetic object.

**G.4 Two-substrate measurement discipline.** When the same arithmetic object admits two distinct ARS substrates (e.g., Δ-eigenvalues + Hecke eigenvalues for Maass forms), pre-specify right-null + expected empirical outcome per substrate; report cross-substrate verdict matrix as a consistency check.

---

## §H. References

### H.1 Arithmetic anomaly canon

- Sarnak, P. (1987). "Statistical properties of eigenvalues of the Hecke operators." In *Analytic Number Theory and Diophantine Problems* (Stillwater, OK, 1984), Prog. Math. 70, Birkhäuser Boston, pp. 321–331.
- Bolte, J., Steil, G., Steiner, F. (1992). "Arithmetical chaos and violation of universality in energy level statistics." Phys. Rev. Lett. 69:2188–2191.
- Bogomolny, E., Leyvraz, F., Schmit, C. (1996). "Distribution of eigenvalues for the modular group." Comm. Math. Phys. 176:577–617.
- Bogomolny, E., Georgeot, B., Giannoni, M.J., Schmit, C. (1997). "Arithmetical chaos." Phys. Rep. 291:219–324.
- Sarnak, P. (1993). "Arithmetic Quantum Chaos." Schur lectures (Tel Aviv 1992), Israel Math. Conf. Proc. 8. Available: web.math.princeton.edu/sarnak/ArithmeticQuantumChaos.pdf
- Rudnick, Z., Sarnak, P. (1994). "The behavior of eigenstates of arithmetic hyperbolic manifolds." Comm. Math. Phys. 161:195–213.

### H.2 Computational infrastructure

- Hejhal, D.A. (1991). "Eigenvalues of the Laplacian for PSL(2,ℤ): Some new results and computational techniques." International Symposium in Memory of Hua Loo-Keng, vol. 1, Springer, pp. 59–102.
- Hejhal, D.A., Rackner, B.N. (1992). "On the Topography of Maass Waveforms for PSL(2,ℤ)." Exp. Math. 1:275–305.
- Booker, A.R., Strömbergsson, A., Venkatesh, A. (2006). "Effective computation of Maass cusp forms." Int. Math. Res. Notices 2006:71281.
- Then, H. (2005). "Maass cusp forms for large eigenvalues." Math. Comput. 74:363–381. (arXiv:math-ph/0305047)
- Then, H. (2005). "Arithmetic quantum chaos of Maass waveforms." (arXiv:math-ph/0305048) — companion paper, Picard group PSL(2,ℤ[i]).
- Seymour-Howell, A. (2022). "Rigorous computation of Maass cusp forms of squarefree level." Res. Number Theory 8:64. (arXiv:2201.08760)
- Seymour-Howell, A. (2022). Zenodo dataset of Maass forms of squarefree level. DOI:10.5281/zenodo.7105772
- Lowry-Duda, D. (2025). "A database of rigorous Maass forms." arXiv:2502.01442. [Corrected attribution: author is David Lowry-Duda, not Seymour-Howell. The paper announces the LMFDB Maass database and describes three rigorous computation methods including the Seymour-Howell trace-formula method.]

### H.3 Modern reframing

- Haehl, F.M., Reeves, W., Rozali, M. (2023). "Symmetries and spectral statistics in chaotic conformal field theories II: Maass cusp forms and arithmetic chaos." JHEP 12:161. (arXiv:2309.00611)
- Boruch, J., Di Ubaldo, G., Haehl, F.M., Perlmutter, E., Rozali, M. (2024–2025). "Modular-Invariant Random Matrix Theory and AdS₃ Wormholes" (and follow-ups).

### H.4 Hecke eigenvalue / Sato-Tate

- Sarnak, P. (1995). "Spectra of hyperbolic surfaces." Bull. AMS 40:441–478.
- Barnet-Lamb, T., Geraghty, D., Harris, M., Taylor, R. (2011). "A family of Calabi-Yau varieties and potential automorphy II." Publ. Res. Inst. Math. Sci. 47:29–98. (Sato-Tate for holomorphic forms over ℚ.)
- Serre, J.-P. (1997). "Répartition asymptotique des valeurs propres de l'opérateur de Hecke T_p." J. Amer. Math. Soc. 10:75–102.

### H.5 Foundational

- Bohigas, O., Giannoni, M.J., Schmit, C. (1984). "Characterization of chaotic quantum spectra and universality of level fluctuation laws." Phys. Rev. Lett. 52:1–4. (BGS conjecture.)
- Berry, M.V., Tabor, M. (1977). "Level clustering in the regular spectrum." Proc. R. Soc. London A 356:375–394. (Poisson for integrable.)
- Iwaniec, H. (2002). *Spectral methods of automorphic forms*. 2nd ed. Grad. Studies Math. 53. AMS.
- Katz, N., Sarnak, P. (1999). *Random matrices, Frobenius eigenvalues, and monodromy*. AMS Coll. Pub. 45.

---

## §I. Open questions, dependencies, and risks

### I.1 Statistical power

Bulk-NNS classification with high Welch separation from GOE β=1 requires ~10³–10⁴ unfolded eigenvalues per dataset. Rigorous SL(2,ℤ) trivial-level eigenvalue counts are modest (rigorous datasets Seymour-Howell + BSV combined: low to mid-10³ at present); combining with non-rigorous-but-deep Then dataset (10⁴+ eigenvalues) gives sufficient joint power but at the cost of including heuristic data. If 34e wants rigorous-only verdict at full strength, additional Maass eigenvalue computation may be needed (Seymour-Howell code is the natural extension path).

### I.2 Unfolding methodology

Leading Weyl-law constant (Area/4π = 1/12 for SL(2,ℤ)) is well-known; subleading corrections from cusps, identity term, small-eigenvalue contributions can shift unfolded mean-spacing by ~1–3%. ARS NNS engine should be robust to this (calibrator and substrate unfolded consistently), but worth documenting which corrections are included.

### I.3 Hecke-eigenvalue normalization

Seymour-Howell 2022 reports under Ramanujan-Petersson normalization (λ_p ∈ [−2, 2]); LMFDB consistent. Then 2003 normalization should be verified before pooling — if different conventions are used, λ_p values must be rescaled before joint analysis.

### I.4 Cross-dataset reproducibility risk

If Test 4 shows substantive divergence beyond the partial-replication pattern, 34e closure becomes conditional on diagnosing the divergence — potentially a multi-week debugging task. Mitigation: run Seymour-Howell as the primary dataset and report BSV/Then as secondary cross-checks; partial replication on rigorous-only datasets sufficient for primary verdict (SARNAK_ANOMALY_REPLICATED_AT_SL2Z_PARTIAL is an acceptable forward-progress label).

### I.5 Forward dependency: 34f-G infrastructure

Then 2003 Picard PSL(2,ℤ[i]) Maass eigenvalues may not exist as a published, downloadable dataset. If 34f-G requires reproducing Then's computation: Hejhal-style algorithm on hyperbolic 3-space is real infrastructure cost. Contact Then directly is simpler path; recomputation from published algorithm is backup. Worth a pre-34f data-availability check.

### I.6 Forward dependency: 34f-E infrastructure

PSL(2,ℤ[ω])\ℍ³ Maass eigenvalues do not appear as published dataset. De novo computation required. Existing tools extend in principle but order-6 unit group of ℤ[ω] implementation is non-trivial. Pre-flight: estimate compute cost and implementation effort before committing to 34f-E.

### I.7 Modern framing forward planning

If 34f wants to engage modern physics-side framing (spectral form factor + AdS₃ wormholes), Test 5 from §D.5 becomes part of 34f's structural target. Optional for 34e; flag here so 34f planning can incorporate.

---

## §J. Success criteria

**Primary headline:** SARNAK_ANOMALY_REPLICATED_AT_SL2Z on at least the Seymour-Howell + BSV consistent subset (rigorous-data verdict).

**Methodology validation:** 34e-H Sato-Tate verdict matches Phase 34d Gaussian/Eisenstein methodology shape (toolchain works on Maass-form Hecke side at the same finite-P correction structure).

**Forward enablement:** 34f infrastructure planning unblocked; PHASE34F_BRIEF drafting can proceed with methodology calibrated against the canonical case.

**Failure-mode response policy:**

- GOE_AT_SL2Z verdict: stop; debug unfolding and NNS computation; do not proceed to 34f until resolved.
- METHODOLOGY_INCONSISTENT_ACROSS_DATASETS: diagnose divergence pattern; partial-replication on rigorous-only subset may suffice; document divergence as known limitation.
- SATO_TATE_DEPARTURE: investigate methodology error in prime-angle measurement; do not propagate to 34f until resolved.

---

End of brief.
