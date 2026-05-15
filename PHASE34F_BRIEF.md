# PHASE 34f BRIEF
## Bianchi Maass eigenvalue spectra — Q(i) replication + Q(√−3) first-measurement + three-coordinate cross-phase closure

**Status:** Pre-execution. Drafted on the 34e methodology calibrator + 34d cross-coordinate scoping. Brief defines substrates, observables, calibrator zoo, dataset pipeline (with infrastructure cost flags for de-novo computation), asymmetric verdict labels per substrate, the substantive cross-coordinate Test 4 (Options A/B) that closes the Q(√−3) three-coordinate joint statement, and the optional spectral-form-factor extension to engage HRR 2023 / Boruch et al. AdS₃-RMT₂ duality.

**Fields:** Q(i) (Picard); Q(√−3) (Bianchi-Z[ω]).
**Substrates:**
- 34f-G-Δ: Δ-eigenvalues on PSL(2, Z[i])\ℍ³ (Picard Maass forms).
- 34f-G-H: Hecke eigenvalues at prime ideals of Z[i] (Picard Sato-Tate).
- 34f-E-Δ: Δ-eigenvalues on PSL(2, Z[ω])\ℍ³ (Bianchi-Z[ω] Maass forms).
- 34f-E-H: Hecke eigenvalues at prime ideals of Z[ω] (Bianchi-Z[ω] Sato-Tate).

**Right null (BGS-naive prediction):** Wigner-Dyson GOE β=1 bulk NNS for both Bianchi substrates (3-D hyperbolic chaotic spectra under BGS conjecture).

**Expected empirical outcome:**
- 34f-G-Δ: Sarnak anomaly extended to Picard. Bulk NNS Poisson-leaning per Then 2003 (companion paper to Then 2005 on SL(2,ℤ)). Replication of published anchor.
- 34f-G-H: Semicircular Sato-Tate. Methodology calibration.
- 34f-E-Δ: Sarnak anomaly extended to Bianchi-Z[ω], **predicted by Hecke-algebra structural argument but not empirically confirmed in literature.** First-measurement.
- 34f-E-H: Semicircular Sato-Tate. Methodology calibration.

**Headline pre-spec verdicts (asymmetric per substrate per 34d/34e discipline):**
- 34f-G-Δ: SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI (replication of Then 2003 with validated 34e toolchain).
- 34f-E-Δ: SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA (first-measurement against structural-extension hypothesis; no published empirical anchor).
- Joint Q(√−3) three-coordinate (if 34f-E-Δ lands signal): SHARED_HECKE_ANOMALY_ACROSS_COORDINATES_ON_Q_SQRT_M3, conditional on cross-coordinate Test 4 (Options A/B in §D.4) showing non-trivial bridge structure.

---

## §A. Placement in cross-coordinate architecture

Phase 34f is the **closer** for the Q(√−3) three-coordinate joint statement scoped at PHASE34D_FINDINGS §D. Phase 34d closed two coordinates of Q(√−3) at null beyond their respective right nulls:

- 34d-E (Eisenstein prime-angle coordinate): NULL beyond Hecke-Poisson, with RW shape confirmed + Chen-2019 finite-X correction at X = 10⁸.
- 34c χ₋₃ (Dirichlet L-zero coordinate): NULL beyond RMT β=4 Sp.

Both nulls; correlation between two nulls is methodologically consistent but substantively empty. The substantive cross-coordinate claim requires the signal-bearing third coordinate. Phase 34f-E supplies it: Bianchi Maass eigenvalues on PSL(2, Z[ω])\ℍ³ are predicted to show the Sarnak anomaly (signal), and the Hecke ring of Z[ω] structurally underlies all three coordinates.

The three-coordinate joint statement closes when:
1. Phase 34e validates the Maass-spectrum methodology on the canonical case (SL(2,ℤ)) — landed as prerequisite.
2. Phase 34f-Δ replicates the Sarnak anomaly on Picard (validates the 3-D Maass methodology against Then 2003) — 34f-G.
3. Phase 34f-Δ on Bianchi-Z[ω] lands the first measurement of the Sarnak anomaly on that substrate — 34f-E.
4. Cross-coordinate Test 4 (§D.4) shows that the 34f-E anomaly structure has bridge to the 34d-E null-residuals or the 34c χ₋₃ null-residuals via the shared Hecke ring of Z[ω].

If 34f-E-Δ does NOT show signal, the Sarnak-anomaly-extension hypothesis is empirically falsified for Bianchi-Z[ω] — that itself is a substantive negative result on the arithmetic structure of Q(√−3).

If 34f-E-Δ shows signal but cross-coordinate Test 4 is null, then 34f-E is a standalone first-measurement of the anomaly on this substrate, and the cross-coordinate convergence claim does not close. The cross-coordinate verdict downgrades to "three substrates measured independently; framework consistency only" rather than "shared Hecke anomaly across coordinates."

---

## §B. Substrate, observables, and predictions

### B.1 Spectral substrate (Picard, 34f-G-Δ)

Maass cusp forms on Γ_K = PSL(2, O_K) for K = Q(i), O_K = Z[i], acting on hyperbolic 3-space ℍ³ = {(x_1, x_2, y) : y > 0} with metric (dx_1² + dx_2² + dy²)/y². Hyperbolic Laplacian:

$$\Delta = -y^2(\partial_{x_1}^2 + \partial_{x_2}^2 + \partial_y^2) + y\partial_y$$

Maass forms satisfy (Δ + λ)f = 0 with λ = r² + 1 (note: **3-D convention**, distinct from 2-D λ = 1/4 + r² in 34e). Spectral parameter r ≥ 0.

Picard fundamental domain Γ_K \ ℍ³ has hyperbolic volume:

$$\text{vol}(\Gamma_{Q(i)} \backslash \mathbb{H}^3) = \frac{|d_K|^{3/2}}{4\pi^2} \zeta_K(2) \approx 0.305...$$

with d_K = -4 the discriminant. Weyl law (3-D Bianchi):

$$N(T) \sim \frac{\text{vol}}{6\pi^2} T^3$$

Unfolding: x_j := vol · r_j³ / (6π²) gives unit-mean spacing.

Then 2003 ("Arithmetic quantum chaos of Maass waveforms," arXiv:math-ph/0305048) is the empirical anchor: Picard Maass eigenvalues computed via Hejhal's algorithm extended to ℍ³, with bulk NNS showing the Sarnak anomaly (Poisson-leaning bulk, deviation from BGS-naive GOE).

### B.2 Spectral substrate (Bianchi-Z[ω], 34f-E-Δ)

Maass cusp forms on Γ_K = PSL(2, O_K) for K = Q(√−3), O_K = Z[ω]. Same ℍ³ action; same eigenvalue equation (Δ + λ)f = 0 with λ = r² + 1.

Bianchi-Z[ω] fundamental domain has volume:

$$\text{vol}(\Gamma_{Q(\sqrt{-3})} \backslash \mathbb{H}^3) = \frac{|d_K|^{3/2}}{4\pi^2} \zeta_K(2) \approx 0.0846...$$

with d_K = -3. **Volume is smaller than Picard by factor ~3.6**; the eigenvalue density is correspondingly higher at fixed T. Statistical power per unit r is higher; total eigenvalue count to fixed T is lower in absolute terms but the unfolded sequence has the same mean spacing 1.

**Orbifold structure differs from Picard:** PSL(2, Z[i]) has elliptic fixed points of order 2 only; PSL(2, Z[ω]) has elliptic fixed points of **orders 2 AND 3** due to the order-6 unit group of Z[ω] (vs order-4 of Z[i]). The Selberg trace formula picks up extra elliptic terms; bulk-NNS classification is robust to this but quantitative shape parameters (Berry-Robnik ρ) may shift.

**Hecke-algebra structural argument for the anomaly extension:** the Sarnak anomaly on PSL(2,ℤ) and PSL(2, Z[i]) is driven by Hecke operator action producing large-multiplicity eigenspaces in the Δ-spectrum. PSL(2, Z[ω]) has an analogous Hecke ring acting on its Maass spectrum; the same multiplicity argument predicts the same anomaly. This is a *structural* prediction without empirical confirmation in literature accessible from search — Then 2003 covered Picard only; subsequent computational work has not surfaced this case.

### B.3 Right null and expected empirical outcome (both Bianchi substrates)

BGS-naive right null: GOE β=1 bulk NNS for both Picard and Bianchi-Z[ω]. Expected empirical outcome: Poisson-leaning bulk NNS per the Sarnak anomaly (replicated on Picard per Then 2003; first-measurement on Bianchi-Z[ω]).

Quantitative parameters:
- Berry-Robnik ρ: expected in the Poisson-dominant regime (0 < ρ < 0.5 per the analogous SL(2,ℤ) literature). 34f-G provides the empirical anchor from Then 2003; 34f-E predicts ρ matched to 34f-G within bootstrap σ, but a discrepancy due to the order-3 elliptic fixed points is an open empirical question.
- Periodic-orbit-family modulations: Bogomolny-Schmit-style subleading P(s) corrections at characteristic length-spectrum scales. Optional shape characterization beyond bulk classification.

### B.4 Companion observables: Hecke eigenvalues at prime ideals (Sato-Tate, 34f-G-H and 34f-E-H)

For each Maass eigenform f on Γ_K, Hecke operators T_𝔭 indexed by prime ideals 𝔭 ⊂ O_K act with eigenvalues λ_𝔭(f). Ramanujan-Petersson normalization: λ_𝔭 ∈ [-2, 2]. Sato-Tate distribution semicircular per the SU(2)-Sato-Tate measure on [-2, 2].

For Picard (Z[i]), prime ideals are either split (norm = p for p ≡ 1 mod 4), inert (norm = p² for p ≡ 3 mod 4), or ramified (the unique prime above 2). For Bianchi-Z[ω], analogous with p mod 3 splitting.

34f-G-H and 34f-E-H provide methodology calibration via Sato-Tate replication — analog of Phase 34e-H but on Bianchi Maass-form Hecke eigenvalues. Expected outcomes: SATO_TATE_REPLICATED with finite-P correction structure consistent with Phase 34d Gaussian/Eisenstein.

### B.5 Two-substrate × two-field measurement matrix

Phase 34f measures four substrates total:

| substrate | field | observable | expected outcome | role |
|---|---|---|---|---|
| 34f-G-Δ | Q(i) | Maass eigenvalues | Sarnak anomaly | Replication (Then 2003) |
| 34f-G-H | Q(i) | Hecke eigenvalues at primes | Semicircular Sato-Tate | Methodology calibration |
| 34f-E-Δ | Q(√−3) | Maass eigenvalues | Sarnak anomaly (predicted) | **First-measurement** |
| 34f-E-H | Q(√−3) | Hecke eigenvalues at primes | Semicircular Sato-Tate | Methodology calibration |

Per the 34d asymmetric-label discipline: Replication substrates and first-measurement substrates get different verdict-label semantics (see §E).

---

## §C. Data infrastructure (with cost flags)

### C.1 Then 2003 Picard data (34f-G primary)

- **Then 2003**, "Arithmetic quantum chaos of Maass waveforms," arXiv:math-ph/0305048. Companion to Then 2005 (SL(2,ℤ)).
- Picard PSL(2, Z[i])\ℍ³ Maass eigenvalues computed via Hejhal's algorithm extended to ℍ³.
- **Data availability uncertainty (flagged in PHASE34E_BRIEF §I.5):** the underlying eigenvalue dataset may not exist as a published downloadable resource. Then's paper reports computed eigenvalues but the raw data is not on a standard archive (Zenodo, LMFDB Bianchi page) as of literature search.
- **Pre-flight action item (§D.0a):** contact Then directly OR check Hejhal lineage repositories (Strömberg, Lemurell) for the dataset. If unavailable, de-novo recomputation from the Hejhal-on-ℍ³ algorithm is required — significant infrastructure cost (multi-week implementation).

### C.2 LMFDB Bianchi modular forms data

- **LMFDB Bianchi modular forms page** (lmfdb.org/ModularForm/GL2/ImaginaryQuadratic). Aggregated dataset across the five imaginary quadratic fields of class number 1 (Q(√−d) for d = 1, 2, 3, 7, 11).
- Includes eigenvalue data for some Bianchi Maass forms, sourced primarily from Cremona's bianchi-progs library and related collaborators.
- **For Picard (Q(i)):** LMFDB has some Maass form data; statistical power may be sufficient for bulk-NNS classification or may require supplementation from Then 2003.
- **For Bianchi-Z[ω] (Q(√−3)):** LMFDB has some Maass form data on Q(√−3); cardinality of the eigenvalue list needs verification at pre-flight. If LMFDB has ~10³ eigenvalues this is sufficient for bulk classification; if much smaller, de-novo computation required.

### C.3 De-novo Bianchi-Z[ω] computation (34f-E infrastructure cost)

If LMFDB data is insufficient: implement Hejhal-on-ℍ³ algorithm adapted for the order-6 unit group of Z[ω] and the resulting fundamental domain. Existing tools:
- Cremona's bianchi-progs library (C, GitHub). Supports class-number-1 imaginary quadratic fields including Q(√−3); designed primarily for Bianchi modular forms (holomorphic side) and L-functions; Maass eigenvalue computation extensions may need direct work.
- Strömberg's PSAGE / Sage-based Hejhal implementations for ℍ³.
- Lemurell's algorithms (Lemurell 2003-2007 on imaginary quadratic Bianchi Maass forms).

**Estimated cost:** 2–6 weeks of implementation effort if starting from Cremona's library; 6–12 weeks if starting from scratch with Hejhal-algorithm reference. Pre-flight estimation required before 34f-E commits.

**Risk mitigation:** if de-novo cost is prohibitive, 34f-E can be staged as a future phase contingent on data acquisition, with 34f-G + cross-coordinate Test 4 on the 34d-E ↔ 34c χ₋₃ ↔ Maass-Picard subset as a partial-progress alternative on Q(i) (not the Q(√−3) closure originally scoped).

### C.4 Cross-coordinate data alignment

Phase 34f cross-coordinate Test 4 (§D.4) requires:
- 34d-E angle data (already cached: data/phase34d_results/, Cornacchia-generated Eisenstein prime angles up to X = 10⁸).
- 34c χ₋₃ zero data (already cached: data/phase34c_results/, Dirichlet real-Sp stratum zeros).
- 34f-E Maass eigenvalue data (this phase, dependent on §C.3).

All three datasets must be aligned to a common Hecke ring of Z[ω] indexing if Option A (structural Hecke-character decomposition) is used. Option B (window-aggregated correlation) uses coarser windowing and is less data-alignment-sensitive.

---

## §D. Tests and verdict labels

### §D.0 Pre-flight gates

#### §D.0a — Data availability gate

Before 34f-G commits: confirm Then 2003 Picard eigenvalue data availability (Then direct contact, Strömberg/Lemurell archives, LMFDB). Document data source, eigenvalue count, precision (rigorous vs heuristic). If data unavailable AND de-novo recomputation cost is high, defer 34f-G to a phase with allocated implementation time.

Before 34f-E commits: confirm Bianchi-Z[ω] eigenvalue data availability on LMFDB; document count and precision. If insufficient, estimate de-novo computation cost (per §C.3) before committing to the first-measurement run.

#### §D.0b — Normalization gate

Mirroring PHASE34E_BRIEF §D.0. Verify:
- Hecke-eigenvalue Ramanujan-Petersson normalization across Then, LMFDB, and any de-novo computed datasets: λ_𝔭 ∈ [-2, 2].
- Spectral-parameter convention λ = r² + 1 (3-D Bianchi) is consistently applied across data sources. **Do not mix with the 2-D convention** λ = 1/4 + r² from 34e.
- Unfolding constant uses the correct field-specific volume (Picard vol ≈ 0.305; Bianchi-Z[ω] vol ≈ 0.0846). Verify both 34f-G and 34f-E use the substrate-correct constant.

Failure of normalization gate is the highest-priority debugging trigger.

### D.1 Test 1 — Bulk-Δ NNS classification (34f-G-Δ and 34f-E-Δ)

**Pipeline** (per substrate):
1. Pull Δ-eigenvalues r_j from the substrate-specific dataset.
2. Unfold via x_j := vol · r_j³ / (6π²) with field-specific volume.
3. Compute s_j := x_{j+1} − x_j; verify ⟨s⟩ ≈ 1.
4. Apply ARS NNS engine with the calibrator zoo (Poisson + Wigner-Dyson + Circular β-equivalents, per 34c/34d/34e).
5. Compute rep_med over 20 random 80%-subsamples (§7.ter.22 threshold-crossing handling).
6. Classify: BL (Poisson-leaning), TR (Wigner-Dyson β=1, GOE-class), or AMBIGUOUS.

**Pre-specified outcomes:**
- 34f-G-Δ: BL with cross-substrate verdict matching the SL(2,ℤ) result from Phase 34e. Replication of Then 2003.
- 34f-E-Δ: BL (predicted by Hecke-algebra structural argument). First-measurement.

### D.2 Test 2 — Anomaly-shape quantification per substrate

Fit empirical P(s) to Berry-Robnik P_BR(s; ρ) per substrate; report fitted ρ with bootstrap σ.

**Pre-specified outcomes:**
- 34f-G-Δ ρ: matches Then 2003 published value within bootstrap σ (specific value depends on Then's reported number; pull at pre-execution and pre-spec to within published error bars per Will's point 4 from PHASE34E_BRIEF review).
- 34f-E-Δ ρ: matches 34f-G-Δ within bootstrap σ if the structural Hecke-algebra argument holds at the quantitative level; substantive deviation (e.g., systematic shift due to order-3 elliptic fixed points) is an open empirical question.

Cross-substrate ρ comparison is itself novel: does the Sarnak anomaly shape depend on the imaginary quadratic field (via orbifold singularity structure) or is it field-independent (driven only by the Hecke algebra)? 34f-G ↔ 34f-E ρ comparison answers this directly.

### D.3 Test 3 — Hecke-eigenvalue Sato-Tate distribution per field (34f-G-H and 34f-E-H)

Per Phase 34d / 34e methodology, with field-specific prime ideal indexing. Pre-specified outcomes: SATO_TATE_REPLICATED with finite-P correction structure consistent with Phase 34d.

### §D.4 Test 4 — Cross-coordinate substantive test on Q(√−3)

This is the **substantive closer** for the three-coordinate joint statement. Two options per the PHASE34D_FINDINGS §D scoping:

#### §D.4 Option A — Structural Hecke-character decomposition

The Hecke ring of Z[ω] indexes Maass-form eigenspaces (34f-E-Δ) and Hecke L-function families L(s, Ξ_k) for Hecke characters Ξ_k (which govern 34d-E angle variance via Rudnick-Waxman + Chen 2019). The decomposition provides a structural bridge:

1. Decompose 34f-E-Δ Maass eigenforms under the Hecke ring of Z[ω]. For each Hecke character Ξ_k, identify the corresponding Maass-form eigenspace (or eigenspace collection).
2. Compute eigenvalue-multiplicity contribution per Hecke character: m_k = (multiplicity-weighted clustering at character k in the bulk NNS).
3. For each Hecke character Ξ_k, compute the contribution to 34d-E angle variance σ²(K, X) at frequency k: σ²_k(K, X) via the explicit-formula decomposition of σ² over zeros of L(s, Ξ_k).
4. Regress m_k against σ²_k residuals (or normalized form): non-trivial regression coefficient = cross-coordinate convergence at the structural level.

Option A advantages: structurally explicit; if non-trivial coefficient found, mechanism (Hecke ring) is identified.

Option A risks: requires deriving the bridge function (eigenspace decomposition + explicit formula application) in advance; if the bridge derivation is intractable for Z[ω] specifically, Option A falls through to Option B.

#### §D.4 Option B — Window-aggregated coarser correlation

Define a common windowing parameter T (Hecke-ring conductor norm threshold) and aggregate:

- 34d-E: σ²(K, X) variance residuals from RW asymptote, aggregated by primes with norm contributing to Hecke characters in window T.
- 34c χ₋₃: zero-statistic residuals from Sp β=4 right null, aggregated by L-function family contributions in window T.
- 34f-E-Δ: Maass-form eigenvalue clustering aggregated by Hecke-ring conductor in window T.

Compute pairwise correlations between the three window-aggregated time series. Non-trivial correlation matrix = cross-coordinate convergence at the window level.

Option B advantages: doesn't require bridge derivation; computes correlations on observable quantities directly. Coarser but tractable.

Option B risks: coarser windowing may wash out signal that exists at structural level; null result on Option B does not necessarily falsify Option A.

#### §D.4 Option choice gate

At pre-execution: attempt Option A bridge derivation. If derivation succeeds and yields tractable explicit bridge function, run Option A. If derivation fails or is intractable, fall back to Option B. Document the bridge-derivation outcome regardless of which option is run.

**Pre-specified outcomes:**

- **SHARED_HECKE_ANOMALY_ACROSS_COORDINATES_ON_Q_SQRT_M3:** Option A (or Option B as fallback) shows non-trivial regression coefficient / correlation matrix at significance threshold. Substantive cross-coordinate convergence claim closes.
- **THREE_COORDINATE_INDEPENDENCE_ON_Q_SQRT_M3:** All three coordinates measured but cross-coordinate Test 4 returns null. Three substrates with consistent ARS readouts via the framework; no substantive shared anomaly. Methodological-consistency-only verdict (analog of the Phase 34d cross-phase outcome but with three coordinates instead of two).
- **TEST_4_BRIDGE_FUNCTION_INTRACTABLE:** Option A derivation fails; Option B is run as fallback; if Option B is null, the verdict is TEST_4_NEGATIVE_BUT_OPTION_A_UNTESTED (substantive cross-coordinate claim neither confirmed nor falsified; structural test deferred to future work).

### §D.5 Test 5 (optional) — Spectral form factor on Bianchi Maass spectra

Following the forward-deferred note from PHASE34E_BRIEF §D.5: if 34e established the SFF tooling on SL(2,ℤ), extend here to Picard and Bianchi-Z[ω].

Compute SFF(t) = |Σ_j e^{i x_j t}|² on unfolded Maass eigenvalues per substrate. Check for:
- Linear ramp at intermediate t per universal eigenvalue repulsion (Wigner-Dyson universality).
- Subleading arithmetic corrections per HRR 2023 / Boruch et al. 2024-25 framework.
- Cross-substrate ramp comparison: does the linear ramp coefficient match across SL(2,ℤ), Picard, Bianchi-Z[ω]? Universal or field-specific?

Test 5 is critical-path only if 34f wants to engage AdS₃-RMT₂ duality framing per HRR / Boruch et al. The brief includes Test 5 in §D structure as deferred-but-defined; promotion to critical path is a separate decision.

**Pre-specified outcomes for Test 5:**
- SFF_RAMP_REPLICATED_AT_BIANCHI: universal linear ramp at intermediate t on both Picard and Bianchi-Z[ω], consistent with the SL(2,ℤ) baseline from 34e §D.5.
- SFF_ARITHMETIC_CORRECTION_DETECTED: subleading correction structure per HRR 2023 detected at the Bianchi substrate; cross-substrate corrections compared.

### D.6 Test 6 — Cross-dataset reproducibility (per substrate)

Where multiple data sources exist for the same substrate, mirror the Phase 34e Test 4 cross-dataset reproducibility discipline. For Picard: Then 2003 (if available) vs LMFDB Bianchi page (if has Picard data). For Bianchi-Z[ω]: LMFDB (if has Z[ω] data) vs de-novo computed (if produced).

If only one data source per substrate, Test 6 is skipped with a documented note. Cross-substrate ρ consistency (Test 2) becomes the methodology consistency check in that case.

---

## §E. Pre-specified verdict labels (asymmetric per substrate)

Per the 34d/34e asymmetric-verdict-label discipline:

### E.1 34f-G-Δ (Picard Δ-eigenvalues, replication)

- **SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI:** bulk NNS classifies BL across Then 2003 data + any LMFDB cross-check; Berry-Robnik ρ matches Then's published value within bootstrap σ. Headline pre-spec verdict.
- **SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI_PARTIAL:** replicated on the rigorous-data subset only (if Then's data is heuristic and cross-validation diverges). Acceptable forward-progress verdict.
- **METHODOLOGY_INCONSISTENT_WITH_THEN_2003:** verdict differs from Then 2003 published result. Debugging required; possible sources include unfolding-constant errors, eigenvalue-data-quality issues, or methodology divergence from Hejhal-on-ℍ³ original. Do not propagate to 34f-E until resolved.
- **AMBIGUOUS / GOE_AT_PSL2_ZI:** threshold-crossing or counter-anomaly verdicts trigger §7.ter.22 / methodology investigation as in 34e.

### E.2 34f-E-Δ (Bianchi-Z[ω] Δ-eigenvalues, first-measurement)

- **SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA:** bulk NNS classifies BL; Berry-Robnik ρ consistent with 34f-G-Δ within bootstrap σ (or with a documented structural-difference flag if ρ differs significantly due to orbifold structure). **Novel content per asymmetric-label discipline: not "replication" since no published anchor exists.**
- **SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA_WITH_FIELD_SHIFT:** bulk anomaly present but Berry-Robnik ρ shifts significantly from 34f-G-Δ value. Substantive content: the anomaly shape depends on the imaginary quadratic field beyond constant-level, plausibly through orbifold singularity structure. Open novel result.
- **NO_ANOMALY_AT_PSL2_Z_OMEGA:** bulk NNS classifies TR (GOE-class), contradicting the structural-extension hypothesis. **Substantive falsification of the Sarnak-anomaly-extension argument for Bianchi-Z[ω].** Real result if it lands; investigate methodology errors but do not assume artifact without exhaustive cross-check.
- **AMBIGUOUS:** threshold-crossing verdict per §7.ter.22.

### E.3 34f-G-H and 34f-E-H (Sato-Tate, methodology calibration)

Per Phase 34d/34e Sato-Tate verdict labels:
- **SATO_TATE_REPLICATED_AT_BIANCHI_HECKE_EIGENVALUES_(K)** for K ∈ {Q(i), Q(√−3)}.
- **SATO_TATE_REPLICATED_AT_FINITE_P_WITH_CORRECTION_(K):** Chen-2019 NLO finite-P correction structure documented per substrate.

### E.4 Cross-coordinate joint verdict on Q(√−3) (the headline)

Conditional on:
1. 34f-E-Δ landing SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA, AND
2. Cross-coordinate Test 4 (Option A or B) returning non-trivial bridge structure.

Joint verdict labels:

- **SHARED_HECKE_ANOMALY_ACROSS_COORDINATES_ON_Q_SQRT_M3:** Substantive three-coordinate convergence on Q(√−3); the Hecke ring of Z[ω] structurally underlies the angle null (34d-E), zero null (34c χ₋₃), and Maass-eigenvalue signal (34f-E-Δ) coordinates. Joint statement closes per PHASE34D_FINDINGS §D scoping.
- **SHARED_ANOMALY_VIA_OPTION_B_ONLY:** Option B window-aggregated correlation positive, Option A structural bridge untested or failed. Weaker form of the shared-anomaly claim; mechanism not fully identified at structural level.
- **THREE_COORDINATE_INDEPENDENCE_ON_Q_SQRT_M3:** Three coordinates measured independently per ARS framework; no substantive shared anomaly detected at Test 4. Methodological-consistency-only verdict.
- **PARTIAL_CLOSURE_ON_PICARD_PROXY:** 34f-E infrastructure cost prohibitive; 34f-G + cross-coordinate Test 4 on the 34d-E ↔ 34c χ₋₃ ↔ Maass-Picard subset on Q(i) as partial-progress alternative. Does not close the Q(√−3) joint statement; provides methodology validation for the Q(i) cross-coordinate parallel.

---

## §F. Forward dependency / phase termination

Phase 34f is the scoped **closer** for the spectral-coordinate orthogonal-channel survey on Q(√−3). Successful closure of 34f-E plus Test 4 returns the framework to the open frontier (cross-domain extensions, finer arithmetic Q substrates, or modern-physics framing engagement at 34g+).

### F.1 If 34f closes substantively (SHARED_HECKE_ANOMALY_ACROSS_COORDINATES)

The orthogonal-channel survey on Q(√−3) is complete. Forward directions:
- 34g candidate: extend the three-coordinate structure to higher class-number imaginary quadratics (Q(√−d) for d = 7, 11, 19, ...) — substrate-systematics check.
- 34g candidate: extend to real quadratic fields (Q(√d) for d > 0) — does the cross-coordinate convergence pattern survive at real quadratic? Open empirical question.
- 34g candidate: engage AdS₃-RMT₂ duality framing if §D.5 SFF tests landed cleanly.

### F.2 If 34f closes partially (THREE_COORDINATE_INDEPENDENCE)

Three coordinates measured with consistent framework verdicts but no substantive cross-coordinate convergence. This is the Phase 34d outcome extended to three coordinates — methodological-consistency-only.

Forward directions:
- 34g: investigate why cross-coordinate convergence does not appear despite shared Hecke-ring structural argument. Possible reasons: bridge function structure is more subtle (not captured by Options A/B); Hecke-ring acts on each coordinate through different functorial paths; null residuals at 34d-E and 34c χ₋₃ are intrinsically uncorrelated even with shared Hecke structure.
- 34g: revisit cross-coordinate test design with finer bridge function or richer signal-bearing substrate.

### F.3 If 34f-E fails to land signal (NO_ANOMALY_AT_PSL2_Z_OMEGA)

Substantive falsification of the Sarnak-anomaly-extension argument for Bianchi-Z[ω]. **Open novel negative result on the Hecke-algebra structural hypothesis.**

Forward directions:
- 34g: investigate whether the Hecke-algebra argument fails specifically for Bianchi-Z[ω] (e.g., the order-3 elliptic fixed points modify the multiplicity structure non-trivially) or has a more general failure mode.
- 34g: re-examine the Sarnak anomaly on PSL(2, Z[i]) to confirm it isn't specific to Q(i); cross-substrate field-dependence becomes the substantive question.

---

## §G. Candidate METHODS.md updates upon 34f closure

Provisional; merge into existing §7.ter ladder at Will's discretion.

**G.1 Bianchi Maass-spectrum substrate handling.** 3-D hyperbolic Weyl law N(T) ~ vol·T³/(6π²); field-specific fundamental-domain volumes; spectral-parameter convention λ = r² + 1 (vs 2-D 1/4 + r² at 34e). Calibrator zoo unchanged.

**G.2 Orbifold-structure-aware unfolding.** Elliptic fixed points modify the Selberg trace formula's subleading terms; for substrates with order > 2 isotropy (e.g., Z[ω] order-3 fixed points), document the trace-formula-correction terms retained in unfolding.

**G.3 Three-coordinate joint-statement structure.** When three or more substrates of one arithmetic object are available with at least one signal-bearing coordinate, cross-coordinate Test 4 (structural Hecke-character decomposition Option A or window-aggregated correlation Option B) is the substantive convergence test. Phase 34f canonical example: Q(√−3) via angle (34d-E) + zero (34c χ₋₃) + Maass eigenvalue (34f-E) coordinates.

**G.4 First-measurement-vs-replication asymmetric-label discipline on Maass-spectrum substrates.** Extension of the Phase 34d asymmetric-label methodology to the Maass-spectrum case: replication substrates (Picard, with Then 2003 anchor) get SARNAK_ANOMALY_REPLICATED labels; first-measurement substrates (Bianchi-Z[ω], no published anchor) get FIRST_MEASUREMENT labels. Treating symmetrically would leak unearned replication claim.

---

## §H. References

(In addition to PHASE34E_BRIEF §H references, which all apply here.)

### H.1 Bianchi Maass forms — computational

- Then, H. (2005). "Arithmetic quantum chaos of Maass waveforms." arXiv:math-ph/0305048. (Picard PSL(2, Z[i])\ℍ³ Maass eigenvalues; companion to Then 2005 on SL(2,ℤ).)
- Lemurell, S. (2003-2007). Series of papers on Maass forms over imaginary quadratic fields; check for Bianchi-Z[ω] coverage.
- Strömberg, F. (work on PSAGE / Sage Hejhal implementations for ℍ³).
- Cremona, J.E. (1984 + ongoing). *bianchi-progs*. https://github.com/JohnCremona/bianchi-progs

### H.2 Bianchi modular forms — analytic theory

- Cremona, J.E. (1984). "Modular symbols for Γ₁(N) and elliptic curves with everywhere good reduction." Math. Proc. Camb. Philos. Soc. 95:265-275.
- Cremona, J.E. (1981). "Modular symbols." PhD thesis, Oxford.
- Friedberg, S. (1985). "On Maass wave forms and the imaginary quadratic Doi-Naganuma lifting." Math. Ann. 271:333–349.
- Elstrodt, J., Grunewald, F., Mennicke, J. (1998). *Groups Acting on Hyperbolic Space: Harmonic Analysis and Number Theory*. Springer Monographs.

### H.3 Spectral form factor and arithmetic chaos (modern reframing)

- Haehl, F.M., Reeves, W., Rozali, M. (2023). JHEP 12:161. arXiv:2309.00611.
- Boruch, J., Di Ubaldo, G., Haehl, F.M., Perlmutter, E., Rozali, M. (2024-2025). Series on modular-invariant RMT + AdS₃ wormholes.

### H.4 Hecke ring structure on imaginary quadratic fields

- Bump, D. (1997). *Automorphic Forms and Representations*. Cambridge.
- Gelbart, S., Jacquet, H. (1979). "Forms on GL(2) from the analytic point of view." Proc. Symp. Pure Math. 33.

---

## §I. Open questions, dependencies, and risks

### I.1 Then 2003 data availability

Single highest-risk dependency. If Then's Picard eigenvalue data is unavailable AND de-novo recomputation is required, 34f-G timeline shifts substantially. Pre-flight Then-contact + Strömberg/Lemurell archive check is the first action upon phase-launch. Mitigation: 34f-G has fallback verdict SARNAK_ANOMALY_REPLICATED_PARTIAL on cross-validation against LMFDB; 34f-E proceeds independently of 34f-G data acquisition.

### I.2 Bianchi-Z[ω] de-novo computation cost

LMFDB cardinality + precision for Q(√−3) Bianchi Maass forms needs verification. If insufficient, 6-12 weeks of Hejhal-on-ℍ³ adaptation for Z[ω] order-6 unit group. Mitigation: stage 34f-E as conditional on data acquisition; 34f-G + Q(i) cross-coordinate partial closure as fallback.

### I.3 Test 4 bridge function tractability

Option A (structural Hecke-character decomposition) bridge derivation may not be tractable for Bianchi-Z[ω] specifically. Option B fallback exists but is coarser. Pre-execution: attempt bridge derivation early; commit to Option B explicitly if Option A is intractable. Document the derivation attempt regardless of outcome.

### I.4 Cross-substrate Berry-Robnik ρ consistency vs field-dependence

Open empirical question: does the Sarnak anomaly shape depend on the imaginary quadratic field (Picard ρ vs Bianchi-Z[ω] ρ) beyond bootstrap σ? If yes, the orbifold structure matters quantitatively — novel substantive finding. If no, the anomaly is field-independent within the Bianchi class. 34f-G ↔ 34f-E ρ comparison answers this directly.

### I.5 SFF / AdS₃-RMT₂ engagement scope decision

Test 5 promotion to critical path is the major scope-expansion decision for 34f. Without engagement, 34f is a number-theory phase; with engagement, 34f connects to AdS₃ wormholes / random-matrix-modular-invariant theory at a more substantive level. Decision should be made at 34f pre-execution with explicit scope statement.

### I.6 Order-3 elliptic fixed point handling

PSL(2, Z[ω]) has order-3 elliptic fixed points in addition to order-2. Hejhal-style algorithm and trace-formula unfolding must handle the order-3 case correctly. Documentation: which subleading Weyl-law terms are retained; verify mean-spacing 1 after unfolding on synthetic-test or matched-Picard data before running on Bianchi-Z[ω] real data.

### I.7 Three-coordinate joint statement scope risk

Even with all three coordinates measured and Test 4 returning a non-trivial bridge, the SHARED_HECKE_ANOMALY_ACROSS_COORDINATES claim is a strong assertion. Substantiating it for publication requires careful methodology around the bridge derivation (Option A) or correlation interpretation (Option B). Pre-publication: peer review on the bridge function design; consider seeking pre-submission review from Sarnak / Rudnick / Waxman / Boruch on the cross-coordinate methodology.

---

## §J. Success criteria

**Primary headline (full closure):**
- 34f-G-Δ: SARNAK_ANOMALY_REPLICATED_AT_PSL2_ZI (Then 2003 replication).
- 34f-E-Δ: SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA (novel content).
- Cross-coordinate Test 4: SHARED_HECKE_ANOMALY_ACROSS_COORDINATES_ON_Q_SQRT_M3 (substantive three-coordinate closure on Q(√−3)).
- Sato-Tate methodology calibration on both fields.

**Acceptable partial closure (PSL(2, Z[ω]) infrastructure cost prohibitive):**
- 34f-G + Q(i) cross-coordinate analog (Maass-Picard ↔ 34c χ₋₃ on Q(i) via Z[i] Hecke ring) closes a partial three-coordinate statement on Q(i) instead of Q(√−3). Reduced scope but completes methodology validation.

**Substantive negative result (Sarnak anomaly extension falsified on Z[ω]):**
- 34f-E-Δ NO_ANOMALY_AT_PSL2_Z_OMEGA verdict if it lands cleanly. Substantively novel; open arithmetic question about the Hecke-algebra structural argument's field-dependence.

**Failure-mode response policy:**
- Then 2003 data unavailable + de-novo cost prohibitive → defer 34f-G; proceed 34f-E + Test 4 on 34d-E ↔ 34c χ₋₃ ↔ Bianchi-Z[ω] subset (skip Picard cross-validation).
- 34f-G replication fails methodology check → halt; debug 3-D Maass methodology before 34f-E.
- 34f-E null with Picard signal → substantive Sarnak-anomaly-extension falsification on Q(√−3); document and propagate.
- Test 4 null → partial three-coordinate verdict THREE_COORDINATE_INDEPENDENCE; methodological-consistency-only closure.

---

End of brief.
