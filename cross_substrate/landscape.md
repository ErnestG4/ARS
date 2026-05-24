# ARS Cross-Substrate Landscape

**Status:** working artifact, v0 first cut. Populates as substrates are characterized and angles are applied.
**Date:** 2026-05-22
**Frame:** operator-IS-substrate; cross-substrate landscape-mapping; explorer-shaped, not hypothesis-test-shaped.

---

## §1 — Framing

In physical substrates we measure, the operator isn't constructed — it IS the substrate. Each substrate has two faces:

- **Parameter side.** Controllable or observable inputs, often arithmetically organized — Farey/Stern-Brocot ratios, synaptic weight matrices, Dirichlet coefficients, FM operator hierarchies, integer N and quadratic-form coefficients, delay parameters.
- **Spectral side.** Measurable response — partials and sidebands, eigenvalues, spike trains, oscillations, zeros, return-time intervals, scaling exponents. Has universality-class structure.

The "bending" between sides is what the substrate physically does. ARS reads the spectral side; Stern-Brocot/Farey navigation handles the parameter side where it's parameter-controllable.

**Cross-substrate work** charts where each substrate falls in the universality-class landscape on its spectral side. The principal scientific yields:

- **Confluence** — two substrates with no physically-shared mechanism landing in the same fingerprint region. The universality class captures something structural even when the underlying physics is different.
- **Parameter-similar-spectrum-different** — two substrates with structurally similar parameter sides landing in different fingerprint regions. The operator does different work in different settings.
- **Multi-scope movement** — single substrates moving between regions at different scales. The fingerprint isn't substrate-as-point; it can be substrate-as-trajectory.

The work is explorer-shaped: the read isn't testing a hypothesis, it's charting where things are. Hypotheses arise from cluster structure once the landscape populates.

---

## §2 — How to read this document

Four catalogs and a matrix:

- **§3 — Substrate catalog.** For each substrate: parameter side, event-train extraction, current fingerprint status.
- **§4 — Analytical-angle catalog.** For each angle in the ARS toolkit and adjacent methodology: what it measures, what it discriminates, known artifacts.
- **§5 — Substrates × angles matrix.** Cell entries record what has been done at each (substrate, angle) pair.
- **§6 — Methodological notes.** Cross-cutting concerns: extraction artifacts, multi-scope discipline, matched-instrument protocol.

Plus:

- **§7 — Near-term population priorities.**
- **§8 — Open methodological items.**

The document is intended to populate. Empty cells in §5 are explicit targets; new substrates and angles get added to §3 and §4; methodological insights accrete in §6.

---

## §3 — Substrate catalog

### AM (almost-Mathieu operator)

**Parameter side.** λ (coupling strength); θ (frequency, typically golden ratio — Diophantine matters); φ (phase). λ=1 is critical (AC ↔ PP transition). Quasiperiodic with rich Diophantine structure on θ. Class II in the earlier framework.

**Event-train extraction.** Eigenvalues of finite-N AM matrix at fixed (λ, θ, φ); unfolded NNS via `unfold_rotnum` (rotation-number leg, ratio-free) or `unfold_ids_ref` (older IDS-reference leg). L_iter is a load-bearing audited axis (Phase 35 finding).

**Current characterization.** Heavily characterized via Phase 35 instrument-validation work:

- L-iter underconvergence is monotone-N-growing super-linearly on sup side: growth factors 0.93× (N=50k) → 4.99× (N=70k) → 118.5× (N=100k) (rev-5.2).
- Sub-side α is L-range-dependent at N=70k (1.25 → 0.50); N=125k α=1 holds (rev-5.2.1).
- Step-1 verdict math: no-FP retracted at N=70k and N=100k via substrate-correction; N=50k surviving; sensitivity criterion shows polarity inversion (PASS @ N=50k → FAIL @ N=70k → FAIL @ N=100k) opposite to stored claim.
- C1 θ-class structure: sup θ-universal within ~30%; sub θ-pattern-sensitive (3.55× across classes).
- C2 Fibonacci-N resonance: sub-side 89% deviation at F₂₄=46368; sup unchanged.

**Fingerprint status.** AM is in the landscape as a substrate with known L-pathology through `unfold_rotnum`. Where the L-converged values place AM in universality-class terms (Class II AC↔PP) is open — the L-pathology has dominated recent characterization. The Phase 35 findings ARE AM's fingerprint through this instrument; they should be banked as substrate characterization, not only as instrument-validation outcome.

### Fibonacci Hamiltonian

**Parameter side.** Hopping amplitudes and on-site potentials following Fibonacci substitution sequence (quasiperiodic). DGY-controlled Cantor object — only such operator in the framework. Class I.

**Event-train extraction.** Spectral measure of Fibonacci Hamiltonian; DGY-exact multifractal exponents available as known-truth reference. Cut-and-project structure (golden-slope cut-and-project per recent framing).

**Current characterization.** Held under anchor-constructibility gate 745b215 (§5b). Intended as Class I calibrator and known-truth validation target for `unfold_rotnum` (§D campaign).

**Fingerprint status.** Parameter side richly characterized (DGY framework); spectral-side ARS-fingerprint pending §D / 745b215 resolution.

### pvc-11 V1 (Smith lab, CRCNS, monkey natural movie)

**Parameter side.** Cortical V1 connectivity (synaptic weights, network topology); naturalistic-movie stimulus drive. Anesthetized monkey.

**Event-train extraction.** Spike trains from V1 single units; well-characterized population; standard sorting pipeline.

**Current characterization.** Across Phases 22a/22b/24/25/26:
- H1: cross-species OSI ↔ ks_gue_med correlation
- F1/F0: substrate-systematic sign flip
- H2: surviving surrogate battery

**Fingerprint status.** In landscape. Sits in some universality class (H1 correlation suggests GUE-leaning); the specific cluster placement vs other substrates is the cross-substrate question.

### Allen Brain Observatory Neuropixels (mouse V1 awake)

**Parameter side.** Cortical V1 connectivity (mouse); awake state; naturalistic stimulus drive.

**Event-train extraction.** Neuropixels spike trains; same stimulus shape as pvc-11.

**Current characterization.** Phase 28 territory. Designed as species-vs-state disambiguation relative to pvc-11.

**Fingerprint status.** In-progress / planned. Comparison to pvc-11 is the principal informativeness — same analytical pipeline, different species + different state.

### Retinal (Marre lab / Chichilnisky / Field / Goetz — aspirational)

**Parameter side.** Retinal circuit (RGC types, photoreceptor coupling, amacrine and bipolar networks); stimulus drive (naturalistic, white noise, parameter-controlled).

**Event-train extraction.** RGC spike trains from MEA recordings.

**Current characterization.** Aspirational; Phase 27+ target. Marre lab public releases as low-barrier first step (Zenodo, lab page, Vision Institute portal). Chichilnisky email drafted but not sent.

**Fingerprint status.** Not in landscape yet; high-priority next addition. Closer to Will's psych/physio home base than AM substrate work.

### FM / brocot.fm (synth)

**Parameter side.** Stern-Brocot tree path (LR navigation); Farey-organized operator coupling ratios; 3-4 operators (Regime A, classical FM palette) or 6-8 (Regime B, shared path, near-unity ratios, genuinely new timbral territory). 512 preset files across 12 families. Will controls the parameter side directly — methodologically distinct.

**Event-train extraction.** Open question. Candidates: note onsets; partial-mode crossings; amplitude-envelope events; sideband appearances under FM dynamics; rise-time-to-attack events. The "what's the natural event-train for an FM synth" question is itself worth working through.

**Current characterization.** Parameter side richly characterized; spectral side characterized in standard musical/acoustic terms (timbre, partials). ARS-fingerprint characterization is open.

**Fingerprint status.** Not in landscape yet. Distinctive because it supports controlled-parameter-sweep experiments on the spectral side — sweep a path through Stern-Brocot space, watch the fingerprint move. No other substrate in the catalog offers that.

### ζ-zeros (Hilbert-Pólya reference)

**Parameter side.** Dirichlet coefficients of ζ on integers (arithmetic input).

**Event-train extraction.** Imaginary parts of non-trivial zeros on the critical line.

**Current characterization.** Known to be GUE-distributed (Montgomery-Odlyzko). The canonical "random-matrix-like" spacing-statistic reference.

**Fingerprint status.** Theoretical reference point in the landscape. The Hilbert-Pólya conjecture — that ζ-zeros are the spectrum of some Hermitian operator — is the operator-is-substrate bet at the theoretical extreme.

> **Grouping caveat (2026-05-21).** The harvested `L-zeros` coordinate file pools THREE distinct L-function families that do NOT share a universality placement: ζ-zeros are GUE (Brody q=1.00, BR ρ=0.999 — confirmed by the matched leg), but the pooled Dirichlet and EC L-zero panels land near the Poisson corner (q≈0). The substrate is internally bimodal; its pooled median is misleading. **TODO (Will):** split `ζ-zeros` / `Dirichlet-L` / `EC-L` into separate §3 catalog entries and separate coordinate files — read per-panel, never the `L-zeros` pooled median. Per-panel values are preserved in `coordinates/L-zeros.jsonl` (meta.panel) and `findings_log.md`.

### Mackey-Glass system

**Parameter side.** Delay τ; feedback parameters (β, γ, n). Single delay-differential equation; transitions from periodic through quasi-periodic to chaotic as τ increases.

**Event-train extraction.** From the chaotic time series — local extrema, threshold crossings, Poincaré-section return times. Multiple choices; the extraction method matters.

**Current characterization.** Not yet placed in ARS landscape. Canonical chaotic dynamical system; parameter sweep along τ moves cleanly between regimes.

**Fingerprint status.** Not in landscape yet. Valuable as a *known* chaotic substrate with theoretical expectation (chaos can produce Wigner-Dyson-like statistics under appropriate conditions); cheap to simulate; supports controlled-parameter-sweep on τ.

### Sacks spiral / quadratic-form substrate

**Parameter side.** Integer N; quadratic-form coefficients (e.g., x²+x+c family, c=41 candidate).

**Event-train extraction.** Prime-position differences on the Sacks spiral; distance signals between quadratic forms; density depletion measurements.

**Current characterization.** Extended sessions documented earlier. Three claims falsified (π-constant separation; tangent coincidences as coordinate tautology; etc.). Surviving candidate: density depletion near c=41 in x²+x+c family.

**Fingerprint status.** Parameter side characterized in number-theoretic terms; ARS-fingerprint on the spectral side is open.

### [Substrate stubs — for consideration as landscape populates]

- **EEG / neural oscillations.** Different operating regimes (alpha, beta, gamma, theta-gamma coupling); different states (awake, sleep, dissociation, anesthesia). Parameter side is brain-state-resolved.
- **Hippocampal place cells / theta-phase precession.** Spike trains with explicit phase structure on theta cycle.
- **Other chaotic dynamical systems.** Lorenz, Rössler, double-pendulum — canonical chaos references with different attractor topologies.
- **Quantum systems with controlled chaos.** Sinai billiard, quantum kicked rotor — theoretically known universality classes.
- **Cardiac rhythms.** Sinus rhythm, atrial fibrillation, ventricular tachycardia — clinical regimes with different point-process structure.
- **Earthquake catalogs.** Omori-law-following point process with known scaling.
- **Critical statistical-mechanics systems.** Ising at criticality, percolation thresholds — theoretical universality-class references.

---

## §4 — Analytical-angle catalog

### Nearest-neighbor spacings (NNS), pooled

- **Measures.** Distribution of consecutive event-spacings after unfolding to unit mean.
- **Discriminates.** Clock (s=1 rigid) / Poisson (exp(1), W1δ≈0.736) / Wigner-Dyson GOE / GUE / intermediate.
- **Artifacts.** Unfolding-method-dependent (different legs give different residuals); finite-N truncation; L_iter convergence (`unfold_rotnum`).
- **Notes.** ARS primary engine.

### Ramanujan-Fourier indicator-mode amplitudes (RF)

- **Measures.** Amplitudes of Ramanujan-Fourier basis modes on the event-train indicator function.
- **Discriminates.** Number-theoretic structure in event spacings; p-adic enrichment patterns; arithmetic vs analytic spectral character.
- **Artifacts.** Basis-truncation; stationarity requirements; sensitivity to extraction artifacts at low-mode end.
- **Notes.** ARS primary engine. p=7 enrichment as new finding category from earlier work.

### W1δ — 1-Wasserstein distance from clock

- **Measures.** Scalar distance from unfolded NNS to clock distribution.
- **Range.** 0 (perfect clock) to ~0.736 (Poisson, 2/e).
- **Discriminates.** Regime via magnitude; clock-like → integrable/AC; intermediate → Wigner-Dyson; Poisson-like → PP/localized.
- **Artifacts.** Inherits all NNS extraction artifacts; L_iter dependence (Phase 35).

### Universality-class identification

- **Measures.** Which canonical class the spectral-side fingerprint falls into.
- **Classes.** Clock; Poisson; Wigner-Dyson GOE; Wigner-Dyson GUE; Picket Fence / Bessel-structured (FM-style); intermediate classes between these.
- **Artifacts.** Class boundaries are sometimes fuzzy; finite-size effects can move substrates between classes at different scales (multi-scope reads matter).

### p-adic analysis

- **Measures.** p-adic-valued structure on event indices or arithmetic structure on the parameter side.
- **Discriminates.** p-specific resonances; arithmetic vs analytic class structure; Diophantine vs Liouvillian properties of parameters.
- **Artifacts.** Choice of p; alignment of event indices to arithmetic scaffold; interaction with extraction methods.
- **Notes.** p=7 enrichment is the canonical example from prior ARS work.

### Mackey-Glass / chaos diagnostics

- **Measures.** Delay-embedding reconstruction; Lyapunov exponents; correlation dimension / Grassberger-Procaccia; recurrence quantification.
- **Discriminates.** Chaotic vs non-chaotic; characterizes attractor topology and dimensionality.
- **Artifacts.** Embedding-parameter choices; finite-data effects; transient vs asymptotic behavior.

### Multifractal exponents (DGY-style)

- **Measures.** Scaling of spectral measure moments; multifractal spectrum f(α).
- **Discriminates.** Singular-continuous vs absolutely-continuous vs pure-point spectral character; Cantor-set structure.
- **Artifacts.** Finite-scale truncation; box-counting convergence.
- **Notes.** Fibonacci Hamiltonian has DGY-exact known-truth values; valuable for instrument validation.

### Spectral / Fourier analysis

- **Measures.** Power spectrum; time-frequency content; partial / harmonic / subharmonic structure.
- **Discriminates.** Integrable / periodic / quasiperiodic / chaotic / mixed regimes.
- **Artifacts.** Window-choice (see §6 windowing/stationarization).

### Cross-frequency coupling

- **Measures.** Phase-amplitude coupling, phase-phase coupling across frequency bands.
- **Discriminates.** Nonlinear interaction between scales; relevant for neural / chaotic substrates.
- **Artifacts.** Surrogate-test dependence; band-edge effects.

### Higher-order spectral statistics (beyond NNS)

- **2-point correlation function R₂(s).** Captures level-pair correlations beyond nearest-neighbor.
- **Number variance Σ²(L) / spectral rigidity Δ₃(L).** Long-range correlations; distinguishes integrable / chaotic at large scales.
- **Spectral form factor K(τ).** Fourier transform of R₂; sensitive probe for universality class.
- **Discriminates.** Fine-grained universality-class structure beyond NNS.
- **Artifacts.** Need cleaner statistics at larger ranges; sensitive to deunfolding choices.

### Cross-species / cross-state metrics (H1-flavored)

- **Measures.** Correlation of universality-class fingerprint with substrate-side properties (e.g., OSI ↔ ks_gue_med across cells).
- **Discriminates.** Which substrate-side properties predict fingerprint variation across cells, units, or conditions.
- **Artifacts.** Requires multiple substrates / conditions; correlation ≠ mechanism.

### Surrogate batteries (H2-flavored)

- **Measures.** Whether the substrate's fingerprint survives randomization of various proposed structural features.
- **Discriminates.** Which structural features of the spike train carry the universality-class signature.
- **Surrogate types.** Inter-spike-interval shuffles; conditional rate-matched surrogates; phase-randomized; ISI-distribution-preserved.
- **Artifacts.** Surrogate-test dependence; null-model choice carries implicit assumptions.

### Substrate-systematic differences (F1/F0-flavored)

- **Measures.** Systematic differences in fingerprint between similar substrates (monkey vs mouse V1; sub vs sup in AM; etc.).
- **Discriminates.** Substrate-specific structural differences within a class.
- **Artifacts.** Cross-substrate comparison requires matched-instrument protocol.

### Windowing / stationarization

- **Measures (methodologically).** How time-series are pre-processed before NNS / RF extraction.
- **Operations.** Two sequential, asymmetric: windowing (localizes; sets resolution; NOT scale-invariant — window-size sweep IS the measurement) + unfolding (rescales; bulk-NNS-invariant per §17).
- **Artifacts.** Window-choice dominates resolution-dependent reads; per §7.ter.5/.22/.21-C of earlier work.
- **Notes.** Long-pending documentation thread; named here as first-class methodology.

---

## §5 — Substrates × angles matrix

Cell entries: ✓ done; ◐ partial / in-progress; ○ planned; — not applicable; (blank) not done.
NNS marker `I.5q` = q-banded ks-to-GUE harvested into coordinates (Phase 2a); full matched object-(a) NNS axes (W1δ, Brody, Σ²/Δ₃) pending Phase 2b recompute. See `coordinates/*.jsonl`.

| Substrate | NNS / W1δ | RF | Universality class | p-adic | Mackey-Glass | Multifractal | Spectral | Cross-freq | 2pt / Σ² / K(τ) | H1-style | H2-style | F-style | Windowing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AM | ✓ matched I/II/VI (11 cells: 6 core + 5 θ-class) | — (no RF) | ✓ sub→clock, sup→intermediate(N-drift); θ-struct sup-side (Brody), sub θ-invariant | ◐ θ-class (golden/silver/bronze/Liouville) | — | | — | — | ◐ Σ²/Δ₃ | — | — | sub↔sup | ✓ VI.1 α + VI.2 β |
| Fibonacci | ○ | ○ | ○ | | — | DGY known-truth | — | — | | — | — | — | — |
| pvc-11 V1 | ✓ I.5q + matched W1δ/I/II (2b) | ✓ III (2a) | ✓ GUE-leaning | ◐ III | | | ✓ | ◐ | | ✓ OSI | ✓ | ✓ F1/F0 | ✓ |
| Allen NP | ◐ I.5q (2a, 544 cells) | ✓ III (2a) | ◐ | ◐ III | | | ○ | ○ | | ○ planned | ◐ surrogate | ○ planned | ○ |
| Retinal | aspirational | aspirational | aspirational | | | | aspirational | aspirational | | aspirational | aspirational | aspirational | — |
| FM/brocot.fm | event-train TBD | event-train TBD | event-train TBD | | — | | partials ✓ | ○ | | — | — | — | — |
| ζ / Dirichlet / EC L-zeros | ✓ I.5q + matched I/II (2b); q→1 ρ→1 | | ✓ GUE canonical | | — | | — | — | ✓ | — | — | — | — |
| Kuramoto | ◐ I.5q (2a, 6361 cells) | ◐ III (2a) | ◐ K-sweep | ◐ III | | | | ◐ | | — | — | — | ◐ |
| Pulsar (NANOGrav) | ◐ I.5q direct-leg (2a, 33a) | | ◐ cross-domain bounded | | — | | — | — | | — | ◐ surrogate-z | — | — |
| Mertens | ✓ I.5q + matched I/II (2b); BL | | ◐ BL (far-from-GUE) | ◐ | — | | — | — | | — | — | — | — |
| Liouville | ✓ I.5q + matched I/II (2b); BL | | ◐ BL (far-from-GUE) | ◐ | — | | — | — | | — | — | — | — |
| Maass Γ₀(N) | ✓ I.5q + matched I/II (2b); Sarnak | | ◐ Sarnak-anomaly | | — | | — | — | | — | — | — | — |
| Gaussian / Eisenstein primes | ✓ I.5q + matched I/II (2b); near-GUE | | ◐ near-GUE | ◐ | — | | — | — | | — | — | — | — |
| Mackey-Glass | ✓ peak-NNS (τ-sweep 5 cells) | — | ✓ τ-trajectory stable→chaotic | — | ✓ V.2 D₂ + V.1 λ (Benettin) | | — | — | ◐ Σ²/Δ₃ | — | — | τ-sweep | ✓ VI.3 cross-extract |
| Lorenz | ✓ lobe-NNS (ρ-sweep 4 cells) | — | ✓ ρ-trajectory stable→chaotic | — | ✓ V.2 D₂=2.2 + V.1 λ=0.909 (Benettin) | | — | — | ◐ Σ²/Δ₃ | — | — | ρ-sweep | — |
| Logistic | ✓ IEI-NNS (r-sweep 5 cells) | — | ✓ period-doubling route | — | ✓ V.1 λ ANALYTIC (exact) + V.2 D₂ | | — | — | ◐ Σ²/Δ₃ | — | — | r-sweep | ✓ VI.3 |
| Sacks/quadratic | | | | p=7 candidate | — | | | — | | — | — | — | — |

The matrix is intentionally sparse — most cells are open. The empty space IS the population target. Phase 2a populated the NNS `I.5q` (q-banded) and RF (III) columns for 10 substrates from already-banked artifacts; new substrate rows (Kuramoto, Pulsar, Mertens, Liouville, Maass, Gaussian/Eisenstein primes) added here pending full §3 catalog entries.

---

## §6 — Methodological notes

### Event-train extraction artifacts

Any spectral-side measurement depends on the extraction step (how a clean point process is derived from the substrate). Extraction itself introduces artifacts that can dominate fingerprints at coarse scales. Discipline:

- For each new substrate, characterize extraction artifacts before extracting structural claims about the substrate.
- Cross-extraction reads (different event-extraction methods on the same substrate) can separate substrate signal from extraction artifact.
- The Phase 35 L_iter pathology is an extraction-artifact instance at the unfolding step — substrate-blind, deterministic, L-decaying.

### Multi-scope reads

Substrates can produce different fingerprints at different scales (short-N vs large-N; short-time vs long-time windows). The landscape doesn't require a single placement per substrate — substrates can move across regions at different scopes, and that movement is itself informative.

### Cross-substrate confluence

Two substrates landing in the same fingerprint region with no physically-shared mechanism is the operationalized confluence — the signal that the universality class captures something structural that the substrates have in common even when the underlying physics differs. This is the principal scientific yield of the landscape.

### Parameter-side / spectral-side asymmetry across substrates

Substrates differ in how much of the parameter side is controllable:

- **Experimenter-controlled.** FM / brocot.fm; simulated systems (Mackey-Glass).
- **Observable but not controllable.** V1, retinal, EEG — connectivity / cell-types / states can be measured but not directly set.
- **Theoretical / definitional.** ζ (Dirichlet coefficients given by definition); Fibonacci (substitution sequence given).
- **Empirical-physical.** AM — implementation parameter λ can be set in simulation; the physical AM realization has fixed parameters.

The landscape benefits from substrates spanning this range. Experimenter-controlled substrates support parameter-sweep experiments; observable substrates support correlation analyses; theoretical substrates support calibration.

### Anti-hypothesis-test discipline

Landscape work is exploratory / charting, not hypothesis-test-shaped. Hypotheses arise from cluster structure once enough substrates are plotted. Resist pre-loading hypotheses; resist forcing substrates into expected categories; let isolated points and unexpected clusters be informative.

### Matched-instrument protocol for cross-substrate comparison

Comparing fingerprints across substrates requires matched preprocessing — same unfolding leg, same window choice, same surrogate generation method. Cross-substrate matched-instrument is what makes confluence claims credible. The §A apparatus-invariance first-law from the slicing brief generalizes here: apparatus matched across compared slices, or varied as a declared axis. Same discipline cross-substrate.

### The L_iter / L-axis lesson (Phase 35 generalizes)

Any iteration-budget parameter in an extraction pipeline is potentially load-bearing in a way that can be unaudited and substrate-blind. The Phase 35 finding generalizes: when adding a new substrate, audit the iteration-budget axes of every preprocessing step before interpreting structural claims about the substrate.

---

## §7 — Near-term population priorities

In priority order for landscape-population:

1. **AM-as-substrate re-placement.** The Phase 35 L-pathology characterization IS AM's fingerprint through `unfold_rotnum`. Place AM explicitly in the landscape with this characterization banked, rather than treating Phase 35 only as instrument-validation outcome. Reorganizes ~12 months of work as substrate characterization.

2. **Retinal acquisition.** Marre lab public release as low-barrier first step (Zenodo / Vision Institute portal). High cross-substrate information value (alternative cortical-adjacent substrate to V1). Methodologically closer to Will's psych/physio home base than AM.

3. **FM / brocot.fm event-train derivation.** Will's own substrate; supports controlled-parameter-sweep experiments — sweep a Stern-Brocot path, watch the fingerprint move. The event-train extraction question (note onsets vs partial crossings vs envelope events) is itself worth working through; choosing the extraction is partly a methodological exercise.

4. **Mackey-Glass.** Known chaotic substrate; canonical reference; cheap to simulate; supports controlled τ-sweep across periodic → chaotic transition.

5. **Allen Neuropixels (Phase 28).** Already planned; species-vs-state comparison with pvc-11.

6. **Fibonacci Hamiltonian.** Held under 745b215; valuable as known-truth calibrator and Class I parameter-side reference.

7. **Sacks spiral / quadratic-form substrate.** Existing characterization; placement gives a number-theoretic anchor in the landscape distinct from ζ.

Substrate stubs (§3) become candidates as the matrix populates and gaps become visible.

---

## §8 — Open methodological items

- **Windowing / stationarization methods section.** Long-pending live thread from the handoff document. Documentation, not a verdict gate, but referenced repeatedly across substrates.
- **Event-train extraction discipline document.** Separately writable as substrates accumulate; the cross-substrate matched-instrument protocol needs documentation of extraction choices per substrate.
- **Cross-substrate matched-instrument protocol.** Concrete spec for fair comparison across substrates with different extraction characteristics.
- **Landscape visualization.** What are the axes of the 2D coordinate space? Candidate: W1δ × multifractal exponent. Candidate: NNS-class × RF-mode-structure. Open design question; figure naturally emerges as more substrates are characterized.
- **Iteration-budget audit protocol.** Generalize the L_iter discipline (Phase 35) to any preprocessing iteration in any pipeline applied to any substrate.

---

## §9 — Versioning and updates

This document is a working artifact. Substrates get added to §3 as they become candidates; angles get added to §4 as new methodology enters the toolkit; cells in §5 fill as work is done; methodological notes accrete in §6.

Updates are not "revisions" in the strict sense (no rev-numbering); the document is the operative landscape and edits land in-place. Significant additions or structural reorganizations get noted in a changelog if needed.

**v0 — 2026-05-22.** First cut. Substrate catalog covers AM, Fibonacci, pvc-11 V1, Allen NP, retinal, FM/brocot.fm, ζ-zeros, Mackey-Glass, Sacks/quadratic; substrate stubs listed for consideration. Angle catalog covers NNS, RF, W1δ, universality-class ID, p-adic, Mackey-Glass diagnostics, multifractal, spectral/Fourier, cross-frequency, higher-order spectral, H1/H2/F-style metrics, windowing/stationarization. Matrix sparse; population priorities listed.
