# CC Brief — ARS Spectral–Arithmetic Programme v1

**v1 changes:** a pass over the ARS repo (main at 94f32da) found that substantial parts of this programme already exist. The phases are rescoped below so they extend the existing work instead of redoing it. **CC: read every file listed in §0 before sealing anything.**

**Aim.** Extend ARS across the duality between primes and zeros, in both directions:
- arithmetic → spectral: prime correlations predicting zero statistics;
- spectral → arithmetic: zeros predicting prime fluctuations.

Every phase starts from a published known answer before anything new is read.

**Roles of the tools:**
- **Classical random matrix theory** is the expectation engine: it supplies the nulls.
- **The quantum-chaos lens** is the translator between primes and zeros. The trace formula and the explicit formula have the same shape: periodic orbits ↔ primes, energy levels ↔ zeros.
- **Machine learning** is the proposal engine: search and discovery.
- **Exact computation and formal certificates** are the referee. Nothing proposed by search counts until it's certified.

**Standing rules (all carried over from ARS):**
- Seal before reading. Every instrument has a red path, and witnesses must fail.
- Report results as FAIL-as-sealed with an attribution, never as a relabel.
- Every cited fact is fetched from its primary source, or marked UNVERIFIED.
- Check which slot owns each fact separately from checking the fact itself.
- CPU work runs on spot; the GPU is used only where noted.
- Nothing is pushed or published without Will.

---

## §0 — Existing ARS work this builds on (read first)

| Topic | Where | State |
|---|---|---|
| Katz–Sarnak, elliptic curves | RESULTS.md §7.ter.1 and §7.ter.1.bis; `run_lmfdb_family.py`, `run_lmfdb_edge.py` | LMFDB curves with conductor ≤ 99. Bulk statistics don't separate families. The edge statistic (γ₁ by root number) separates SO(even) from SO(odd), KS ≈ 0.94. **No excised-orthogonal model was used**, even though conductor ≤ 99 is exactly the small-conductor regime where excess repulsion matters. |
| Katz–Sarnak, Dirichlet | RESULTS.md §7.ter.3; `run_dirichlet_edge.py` | q ≤ 149: 630 primitive characters (92 real, predicted symplectic; 538 complex, predicted unitary). Bulk can't separate them; the edge γ₁ separation is weaker than for elliptic curves. |
| Family fingerprints, and the audit | RESULTS.md §7.ter.8; audit/04 #1; audit/06 FIX-4 | "All four families fingerprint as one GUE class" in the bulk. The claim that the RF engine's `peak_q` discriminates families is **[not-found]**: it was never wired into any L-function script. The Katz–Sarnak claims were **DOWNGRADED** (the verdict best=GUE doesn't change under the guard). |
| ζ height crossover | arsrh/PHASE1_FINDINGS.md | The sealed prediction was falsified; a real, resolvable crossover to GUE was found above a tridiagonal-GUE noise floor. Bogomolny's finite-height theory is referenced. |
| F(α) / pair correlation | arsrh/LOOK_ARC_TASKB_FINDINGS.md | F(α) is unfolding-dependent. F(α), Σ² and Δ₃ count as one witness, not three. |
| Hardy–Littlewood / comb | comb/RESULTS_COMB.md; COMB_KTUPLE_BRIEF.md | Pair comb weights match the computed ℤ[i] Hardy–Littlewood predictions. The k-tuple arc is drafted but not run. |
| Mertens / Liouville | Phases 34a and 34b; RESULTS.md §7.ter.3 | Mertens: null is Poisson on the squarefree support. Liouville: a constrained ±1 random walk. Sign-change positions measured. |
| Arithmetic quantum chaos | SESSION_K_*; sessionK/ | The Maass spectrum reads arithmetic-Poisson per desymmetrised sector, with GOE excluded at 7–8σ. The transfer-operator (Mayer) route is validated. The non-arithmetic **Hecke n = 5 calibrator is DATA_ACQUISITION_BLOCKED**. |
| Murmurations, Karpenkov, Chowla | none | New. |

**Lessons that bind this programme:**
- **The bulk can't see family symmetry.** The theory says so too: the classical groups give identical bulk variance. All family work therefore uses *edge* statistics: the one-level density near the central point, the first-zero distribution, and γ₁.
- **Any claim about the RF engine must show the wiring before the result.**
- **The desymmetrisation gate from Session K applies to every spectrum with a symmetry.**

---

## Phase 1 — Katz–Sarnak symmetry battery (START HERE): extend, don't redo

**Rescope (v1).** The existing edge tests are the baseline; reproduce them first as known answers. The new parts are:
1. **The symplectic family done properly:** quadratic characters χ_d over a wide range of fundamental discriminants, not just the 92 real characters with q ≤ 149.
2. **The excised-orthogonal model for small-conductor elliptic curves:** re-read the conductor ≤ 99 edge result against the excised model as well as the plain SO(even)/SO(odd) predictions.
3. **One-level density with a declared test function,** in addition to γ₁.
4. **Conductor-range convergence:** how the classification sharpens as the conductor grows.
5. **Wiring the RF engine into the family scripts.** This closes audit/04 #1 honestly: wire it first, seal a prediction, then read the result, whichever way it comes out.

Bulk statistics are reported descriptively only; they aren't a family test.

**Question.** Can ARS classify whole *families* of L-functions by symmetry type from the statistics of their low-lying zeros, the way it classifies single spectra?

**Known answers.** Katz–Sarnak one-level densities, with zeros scaled by (log conductor)/2π. **Verify each formula against the primary source before sealing.**

| Family | Symmetry | One-level density W(x) |
|---|---|---|
| Primitive Dirichlet L(s,χ), χ mod q | Unitary | 1 |
| Quadratic Dirichlet L(s,χ_d) | Symplectic | 1 − sin(2πx)/(2πx) |
| Elliptic curves, root number +1 | SO(even) | 1 + sin(2πx)/(2πx) |
| Elliptic curves, root number −1 | SO(odd) | 1 − sin(2πx)/(2πx) + δ₀(x) |
| Elliptic curves, both | O | 1 + ½δ₀(x) |

**Also compute the first-zero distribution per family.** It discriminates symmetry types more sharply than the density does.

**A known finite-conductor deviation, part of the known answer.** At small conductor, elliptic-curve low zeros show *excess repulsion* from the central point (Miller's observation). It is modelled by the excised orthogonal ensemble of Dueñez–Huynh–Keating–Miller–Snaith. The battery must expect this deviation, not flag it as a failure. Fetch and file both sources.

**Data.**
- Compute low-lying zeros with PARI/GP (`lfunzeros`) on spot:
   - Dirichlet characters for prime q up to the declared range;
   - fundamental discriminants d for the quadratic family;
   - elliptic curves from the LMFDB by conductor bands.
- Cross-check a random 5% of the computed zeros against LMFDB-stored zeros where they exist.
- Pin the PARI version.

**Calibration (red path), before any real family is read.**
1. **Random-matrix draws** from CUE, USp(2N), SO(2N) and SO(2N+1), with N matched to each family's effective size. The classifier must recover the right type at a sealed rate.
2. **Witnesses that must fail:**
   - a mixture of two types at a declared ratio must be flagged as mixed;
   - a family with relabelled root numbers must be flagged as inconsistent.
3. **Seal:** the scaling, the statistic set (one-level density, first-zero distribution, ARS nearest-neighbour spacing of the low zeros), the thresholds, and the multiplicity rule.

**Gates.**
- G0: the classifier recovers every pure random-matrix type at the sealed rate.
- G1: each real family is classified to its Katz–Sarnak type, or to the excised-orthogonal model for small-conductor elliptic curves.
- G2: the cross-check against LMFDB zeros matches to the declared tolerance.

**Output.** PH1_FINDINGS.md: a per-family classification table plus a convergence plot showing how the classification sharpens as the conductor range grows. This becomes a new zoo tier: the *family-level* universality classifier.

---

## Phase 2 — Bogomolny–Keating corrections in zeta zeros (both directions at once)

**Rescope (v1).** arsrh Phase 1 already resolves the crossover to GUE with height.
- **First,** check whether that crossover was compared quantitatively to the effective-size law CUE(N_eff). If not, do that as the known answer.
- **The new part** is the arithmetic leg: whether the singular-series terms, computed with the comb arc's Hardy–Littlewood machinery, explain what's left over.
- **Respect Look arc Task B:** F(α), Σ² and Δ₃ count as one witness, not three.

**Question.** Does the RF engine's singular-series (CRT) prediction explain the measured departures of zeta zeros from GUE?

**Known answers. Verify both before sealing.**
- **Bogomolny–Keating (1995–96)** derived zero correlations, *including* the lower-order corrections, from the Hardy–Littlewood prime-pair conjecture.
- **Bogomolny–Bohigas–Leboeuf–Monastra (2006)** found that the spacing distribution of zeros at height E matches CUE with an *effective* matrix size N_eff = log(E/2π)/√(12Λ), with Λ ≈ 1.5731. **Verify the formula and constant.**

**Data.** Odlyzko's public tables of zeta zeros at several heights (around 10¹², 10²¹, 10²², 10²³). Fetch them and hash every file.

**Pipeline.**
- **The RF engine** computes the arithmetic correction terms (the singular-series prediction) at each height.
- **NNS** measures the actual deviation from asymptotic GUE.
- **Compare** with a residual test against the CUE(N_eff) null.

**Gates.**
- G0: CUE(N_eff) draws reproduce the published finite-size curves.
- G1: the measured zeta-zero deviation matches the CUE(N_eff) prediction within sealed tolerance at each height.
- G2 (the new part): the RF-predicted arithmetic terms account for the residual left after G1.

---

## Phase 3 — Mertens phase alignment (spectral → arithmetic)

**Rescope (v1).** Phases 34a and 34b supply the right nulls (Poisson on the squarefree support; a constrained Liouville walk), and RESULTS.md §7.ter.3 has sign-change positions. The Odlyzko–te Riele LLL reproduction is new.

**Known answer to reproduce first.** Odlyzko–te Riele (1985) disproved the Mertens conjecture. They used the explicit formula to write M(x)/√x as a sum of oscillations, one per zeta zero, and lattice reduction (LLL) to find x where the first ~2000 zeros' phases align.

**Later bounds. Verify each from its primary source:**
- Kotnik–te Riele (2006);
- Hurst (2018): limsup M(x)/√x > 1.826 and liminf < −1.837.

**Pipeline.**
1. Take high-precision zeros (Odlyzko's low-height table or mpmath).
2. Use fpylll for LLL.
3. Reproduce the 1985 bounds as the known answer.
4. **Then search:** an LLL + ML hybrid looks for larger predicted excursions.
5. **Certify every candidate:**
   - exactly, wherever x is computationally reachable;
   - otherwise through the explicit-formula bound with rigorous error terms.

**Gate.** Phase 3 search results are reported only if Phase 3 reproduction passed.

---

## Phase 4 — Murmuration-style discovery (ML proposes, exact computation decides)

**Known answer to replicate.** He–Lee–Oliver–Pozdnyakov (2022) found oscillations in averaged elliptic-curve prime coefficients a_p, sorted by rank, using data analysis and ML on LMFDB curves. Zubrilina (2023) proved the corresponding result for modular forms. **Verify both.**

**Pipeline.**
1. Replicate the murmuration plots from LMFDB data.
2. **Discovery mode:** unsupervised analysis (PCA, clustering, small models) across L-function families.
3. **Every candidate pattern** is written as a sealed hypothesis and tested on held-out conductor ranges with exact recomputation.
4. Nothing found in an exploration slice counts until it is tested on held-out data.

The GPU can be used here for model training.

---

## Phase 5 — Arithmetic vs. generic quantum chaos: replaced in v1

**Rescope (v1).** Session K already did the arithmetic side: Maass Poisson per sector, GOE excluded at 7–8σ, desymmetrisation gated. The only open item is the **non-arithmetic calibrator, Hecke n = 5**, which is DATA_ACQUISITION_BLOCKED. Phase 5 is now just unblocking it:
- obtain the Bogomolny–Schmit levels (~6000), or generate them;
- or use the area-preserving-perturbation crossover route noted in the Session K brief, R1.

The original v0 text follows, for reference.

**Question.** Can ARS tell *why* a chaotic system fails to be GOE?

**Known answer.** Laplacian eigenvalues of arithmetic hyperbolic surfaces (e.g. the modular surface) show Poisson-like statistics despite classical chaos, because arithmetic forces many periodic orbits to have the same length (Bogomolny–Georgeot–Giannoni–Schmit; Hejhal). Non-arithmetic surfaces show GOE.

**v0 scope only.**
- Locate eigenvalue datasets: Maass-form eigenvalues for SL(2,ℤ) in the LMFDB and in Then's large computations; non-arithmetic comparison spectra, such as Hecke triangle groups or billiards.
- Estimate the compute cost if spectra must be generated.
- Report back before building anything.

---

## Order for today and after

1. **Phase 1:**
   - read §0;
   - reproduce the existing edge results as known answers;
   - calibrate on random-matrix draws;
   - then the new parts: symplectic χ_d, the excised re-read, the one-level density, conductor convergence, the RF wiring.
2. **Phase 2:** fetch and hash the Odlyzko tables, then reproduce the CUE(N_eff) known answer.
3. **Phase 3:** reproduce Odlyzko–te Riele.
4. **Phase 4:** replicate the murmurations.
5. **Phase 5:** scoping report.

**Citations to fetch and file before their phase is sealed:**
- Katz–Sarnak;
- Miller (excess repulsion);
- Dueñez–Huynh–Keating–Miller–Snaith;
- Bogomolny–Keating;
- Bogomolny–Bohigas–Leboeuf–Monastra;
- Odlyzko–te Riele;
- Kotnik–te Riele;
- Hurst;
- He–Lee–Oliver–Pozdnyakov;
- Zubrilina;
- Bogomolny–Georgeot–Giannoni–Schmit.
