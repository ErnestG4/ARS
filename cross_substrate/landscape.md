# ARS Cross-Substrate Landscape

**Status:** v2 consolidation (2026-05-25; v1 2026-05-24; v0 2026-05-22). §0 dashboard = current state; §3/§5 = v0 catalog/matrix retained below.
**Frame:** operator-IS-substrate; cross-substrate landscape-mapping; explorer-shaped, not hypothesis-test-shaped.

---

## §0 — Landscape v2 dashboard (state at a glance, 2026-05-25)

Detailed synthesis: `PROGRESS_REPORT.md` (§1–7); run-by-run: `findings_log.md`. All FLAGGED (verdicts Will's).

**CROSS-SUBSTRATE ARCHITECTURE (the two pillars — what the landscape is finding).** Across substrate
classes the structure separates into a UNIVERSAL part and a SUBSTRATE-KEYED part:
1. **Structural-anchor universality (poles are substrate-general).** The universality-class POLES recur in
   every substrate: a repulsive/GUE pole and a clustered/Poisson pole, with the calibrators (GUE/GOE/Poisson/
   clock) as fixed corners. Neural: corr-eig→GUE and sync-event→Poisson hold in BOTH V1 (Allen) and CA1
   (Buzsáki). Arithmetic/operator: the approximability axis runs GUE↔Poisson across AM/Fib/gaah/ext_harper/
   brocot. The poles are the substrate-invariant skeleton.
2. **H1 / extrinsic-selectivity↔class is substrate-general but substrate-INSTANTIATED.** A per-cell
   EXTRINSIC selectivity property tracks the intrinsic universality class — and the *relevant property is the
   substrate's own selectivity axis*: V1→orientation (OSI), CA1→spatial information (place coding). The
   strong INTRINSIC correlates (burst/ISI) are tautological, not the link ([[intrinsic_vs_extrinsic_predictor]]).
What VARIES across substrates: (a) which biology fills the MIDDLE between the poles — V1: stable intermediate
(avalanche); CA1: behaviour-state-gated avalanche (not a stable intermediate); (b) which selectivity axis is
relevant; (c) which OBSERVABLE is substrate-appropriate (point-process→NNS, Cantor→box-dim, recurrent-network→
population-collective; a feedforward output layer like retina may not support the population observables at all
— [[observable_binding_clarifies]]). **Status of the two pillars: pillar 1 (poles) at high confidence; pillar
2 (H1-substrate-general) at n=2 classes (V1, CA1) — a third class is the open falsification test.**

**MAPPED** (substrates with computed fingerprint coordinates):
- *Operator / arithmetic (18 substrates):* AM (9 Lagrange θ-classes × coupling sweep), Fibonacci/Sturmian
  Hamiltonian (coupling range × Lagrange classes), Sturmian word, ζ / Dirichlet / EC L-zeros (split),
  Mertens, Liouville, Gaussian + Eisenstein primes, Maass, pvc-11 V1, Kuramoto, pulsar (NANOGrav),
  Mackey-Glass / Lorenz / logistic.
- *Neuro depth (Allen):* 8,462 cells × 7 areas (V1/LM/RL/AL/PM/AM/LGN) × 8 stimuli, Family I + Family II.
- *Calibration anchors:* GUE / GOE / GSE / Poisson / clock / uniform-jitter (the landscape corners).
- *Population-level (all 12 sessions):* corr-eig→GUE / avl-onset→intermediate / sync-event→Poisson
  (3 trustable, consistent across sessions) + rate-peak (artifact control).
- *Dynamical (Family V): Mackey-Glass / Lorenz / logistic + Rössler / Chua / Duffing / Hénon (7 systems, bifurcation-sweep trajectories, λ₁/D₂).*
- *Quasi-periodic operators:* maryland / gaah / ext_harper / mosaic × 9 Lagrange classes × coupling
  (D_box; the approximability-family extension test).
- *brocot.fm (FM synthesis):* 4,292 phase3 exemplars × 33 families (partial-frequency NNS + RF per-prime)
  + the 9-Lagrange-class approximability bridge test (depth-sweep at irrational-α targets).
- *Axes populated:* Family I (NNS I.1–I.9), II (Σ²/Δ₃/K), IV (spectral box-dim), V (λ₁/D₂), VI, VII;
  III (RF) where banked.

**PENDING:**
- *Operator:* trace-map thermodynamic-formalism dimension (the deferred quantitative DEGT constant).
- *Neuro:* Tier-2 Buzsáki CA1 framework-port DONE (cycle 1, 8 sessions — see SURPRISES); hippocampus-specific
  cycle-2 (theta-gamma / replay / place fields) IN PROGRESS. spatial population-level (a distinct substrate);
  orthogonal-design Family-VII disambiguation (only if Family VII load-bearing).
- *Third substrate class for the pillar-2 falsification test (QUEUED, acquisition lift):* the turnkey DANDI
  retinal MEA (001677) is phototagging/full-field-flash — NO visual-selectivity axis (DS/contrast/spatial),
  and retina is feedforward (population observables substrate-inappropriate). A proper test needs off-DANDI
  rich-selectivity retina (Marre/Chichilnisky, custom format) or IBL (contrast/choice selectivity, large but
  standardized). Scoped 2026-05-25; deferred pending a proper-selectivity dataset.
- *brocot.fm* (Will's own substrate; audio spectral side — the standing bridge piece).

**SURPRISES / load-bearing findings:**
- **CA1 FRAMEWORK-PORT: the landscape generalises with structured reorganisation (Buzsáki, 8 sessions).**
  Structural POLES are substrate-general — corr-eig stays GUE (0.85), sync-event stays Poisson (0.00), like
  Allen. H1 (extrinsic-selectivity↔per-cell-class) GENERALISES with the substrate's own selectivity axis:
  spatial information (place-coding analogue of OSI) ρ=+0.28 + theta phase-locking ρ=−0.21 (exc), robust at
  n=668 — while the strong burst↔ks_gue ρ=0.52 is INTRINSIC/tautological (not the analogue). But the
  biological MIDDLE reorganises — avalanche is NOT a stable intermediate in CA1; it is behaviour-state-gated
  (Maze-Awake 0.43 ≫ quiet/sleep 0.00, rate-matched sign-consistent ×8; NonREM/REM consolidation effects
  killed by rate-match+power). New cell-type axis: pyramidal more GUE than interneuron (ks_gue 0.69 vs 0.58).
  ⇒ shared cross-substrate = universality-class poles + extrinsic-selectivity principle; what varies = which
  biology fills the middle + which selectivity axis. (buzsaki_port/_selectivity/_ratematch; verdicts Will's.)
- **AM ≡ Fibonacci Hamiltonian up to an approximability-dependent reparametrization** — universal across
  the whole Lagrange spectrum; matching coupling λ* continuous in approximability (not a CF-boundedness
  step); AM-criticality box-dim ≈½ invariant (PROGRESS_REPORT §3 g–k).
- **H1 (OSI↔ks_gue) generalizes across ALL mouse visual areas + LGN** — pathway-independent, not V1-specific.
- **Family VII is monkey-STRONG / mouse-WEAK** (graded ~0.1 vs 0.47, not absent) — reframes to "what makes
  it 4–5× stronger in pvc-11" (4 candidates incl. sampling-geometry).
- **Within-cell stimulus-state is a live axis** — a fixed cell's class shifts with stimulus; Σ² (long-range)
  is the more state-sensitive axis.
- **Per-cell fingerprints COHERE** (visual-cortex cluster, no spatial autocorrelation <1 mm) **but
  POPULATION-level fingerprints FRAGMENT by aggregation** (corr-eig→GUE, sync-event→Poisson, avl→intermediate)
  — no single "population fingerprint"; and **avalanche-criticality is orthogonal to per-cell class** (two
  observables, neither implies the other).
- **Verifying an asymptotic CONSTANT needs the right formalism, not a finer sweep** (the DEGT dimension
  cross-check, §3 k — form confirmed, constant deferred).
- **APPROXIMABILITY STRATIFICATION TRANSCENDS OPERATOR FAMILY (the brocot bridge test).** brocot.fm —
  FM synthesis, mechanistically unlike the AM/Fibonacci Schrödinger operators — shows the SAME
  stratification: Brody q falls with approximability across the 9 Lagrange classes, ρ(rank, q)=−0.91
  (metallic means → GUE/repulsive q≈1, π−3/Liouville → Poisson q=0; FM depth = coupling analogue). A
  third substrate confirms the axis is a substrate-CLASS property. NUANCE: brocot's fine discriminator
  looks like a bounded-vs-unbounded-CF step (e−2 drops with the unbounded group), differing from the
  λ*(class) continuous-in-approximability fine structure — substrates agree gross, differ fine.
  brocot.fm corpus places by spectral DENSITY (sparse-harmonic→repulsive, dense-carpet→clustered).
- **THE AXIS EXTENDS TO 5 OPERATORS (quasi-periodic family).** gaah (ρ=−0.72) and ext_harper (ρ=−0.70)
  join AM/Fibonacci/brocot — D_box falls with approximability at their critical coupling. CONDITIONED on
  a critical/fractal regime: maryland (always-pure-point) is a flat λ-invariant negative control, mosaic
  doesn't stratify — so NOT universal across all quasi-periodic operators. Fine-structure generalizes
  "agree-gross-diverge-fine": the OPERATOR family (AM/Fib/gaah/ext_harper) agrees on fine structure
  (quotient-magnitude/continuous, e-stays-high), and brocot (FM synthesis) is the fine-structure outlier
  (CF-boundedness step).
- **THE GROSS-AGREE/FINE-DIFFER SPLIT NOW HAS A MECHANISM (cf_mechanism.py).** brocot Brody q STEPS on the
  bounded/quadratic-vs-transcendental CF binary (mean 0.982 vs 0.271, Δ=+0.71); operator D_box is
  CONTINUOUS in μ (ρ=−0.63). **e−2 is the discriminator that splits them** (transcendental/unbounded CF,
  but μ=2): brocot q(e)=0.568 drops with the transcendentals; operator D_box(e)=0.782 stays high with
  golden. ⇒ brocot follows the three-distance-theorem / LOCAL / CF-structural step (bounded CF ⇒
  balanced {nα} gaps ⇒ repulsive), operators follow the trace-map-integrated / GLOBAL / continuous-μ —
  confirms the WHY, not just the THAT.
- **THE BROCOT TRIGGER IS BOUNDEDNESS, NOT QUADRATICITY (cf_discriminator.py — confound resolved).** The
  cf_mechanism caveat (boundedness & quadraticity confounded for natural α) is now decomposed by a designed
  second discriminator: hold the CF quotient alphabet fixed at {1,2} and vary ONLY periodicity. Bounded-
  NONquadratic α (Thue–Morse / Fibonacci-word quotients) give brocot q=1.000 — WITH the bounded-quadratic
  anchor (golden/silver/periodic_12 mean 0.969), far from the unbounded anchor (e/liouville 0.284).
  Flipping periodicity left q unchanged ⇒ periodicity is INVISIBLE to brocot; the trigger is boundedness
  of partial quotients (the badly-approximable / Diophantine class), exactly the three-distance prediction
  (quotient MAGNITUDE sets convergent-denominator growth → gap balance). Operator control: all μ=2 bounded
  targets D_box=0.785±0.016 (flat across periodicity) — operators read μ, blind to the split.
- **THE SPLIT IS SUBSTRATE-TYPE-GROUNDED, NOT AN AXIS ARTIFACT (observable-binding clarification).** Tested
  whether cf_mechanism's brocot-step/operator-continuum was an axis-selection confound: the 2×2 has two
  intrinsically-uninformative off-diagonals — brocot box-dim is comb-noise (no fractal in a deterministic FM
  partial set), operator NNS is Cantor-degenerate (q≈0 every class/coupling). Spectral TYPE forces the
  observable (point-process→NNS, Cantor→box-dim); you can't read either substrate on the other's axis. Same
  theme as the dynamical-breadth Family-V finding (substrate CLASS needs observable FAMILY), one layer down
  (spectral TYPE affords specific observable). Honest caveat: boundedness-step & μ-continuum are partly
  observable-bound (boundedness is what NNS sees, μ is what box-dim sees) — strengthens, not weakens, the
  landscape. Banked as clarification (findings_log; 2×2 table the durable artifact).
- **POPULATION-LEVEL FRAGMENTATION IS CONSISTENT ACROSS ALL 12 SESSIONS.** 3 trustable population
  observables span the full axis — corr-eig→GUE (q=0.95±0.05), avl-onset→intermediate (0.66±0.08),
  sync-event→Poisson (0.00±0.00, corroborated by I.5/BRρ) — each a fixed landscape position, aggregation
  (not session) sets the class. rate-peak's Wigner is a confirmed find_peaks artifact (induction-on-noise:
  Poisson surrogate also → q=1). The map gains 3 real population positions + 1 artifact control.
- **STRATIFIED (1,456 cells, 8 stim × 7 area × 12 sess): fragmentation ROBUST, each observable keyed to a
  DIFFERENT factor.** Canonical ordering corr-eig>avl>sync holds in 94% of (area,stim,session) cells ⇒ not
  a pooling artifact. corr-eig is NEAR-INVARIANT (η²≤0.05 on all factors — stable ~GUE everywhere);
  avl-onset is structured by SESSION (η²=0.44) >> AREA (0.19, Kendall W=0.78: V1/lateral low → higher-areas/
  LGN high) >> stimulus; sync-event invariant Poisson. STIMULUS barely structures the population (W≤0.24) —
  contrasts the per-cell within-stimulus-state axis (population is more stimulus-invariant than the cell).
  Population area-structure (carried by avalanche) ≠ per-cell ks_gue area pattern (ρ=−0.14) — reinforces
  population-IS-a-distinct-substrate. (population_strat.py; verdicts Will's.)
- **THE AVALANCHE AREA EFFECT IS RATE-INDEPENDENT (biological) — rate-match de-confound.** Matching every
  area within each (session,block) to common unit-count + total spike-count: avl-onset area Kendall W=0.808
  (raw 0.783 — survives), same ordering V1/lateral low → higher-areas/LGN high. The session dominance
  (η²=0.44) was the rate-sensitive part; the area gradient is the clean matched signal. (population_ratematch.py.)
- **TEMPORAL-STABILITY (early/late half): the 3 observables differ in STRUCTURE-vs-NOISE-vs-INVARIANCE.**
  avl-onset TEMPORALLY STATIONARY (test-retest ρ=0.84, within|Δq|≪between-sd) — fixed reproducible property
  of the condition; the structured+stable+biologically-area-graded observable. corr-eig INVARIANT-BUT-NOISY
  (ρ≈0, ~0.89 everywhere, fluctuations are half-data noise not drift). sync-event invariant Poisson.
  "No single population fingerprint" sharpens: ONE observable carries reproducible biological structure
  (avalanche), two are condition-invariant. (population_temporal.py; verdicts Will's.)

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

> **Substrate-class: Sturmian / Stern-Brocot (number-theoretic frame).** brocot.fm is one
> instance of a broader class. Every infinite Stern-Brocot path (modulo eventually-monotone
> tails) encodes an irrational α via its continued fraction; the **Sturmian word** of slope α
> (mechanical/Beatty sequence) is the canonical event-train — making *parameter-side path ↔
> spectral-side event-train* explicit, the cleanest realization of the operator-IS-substrate
> bet on the parameter side. **Lagrange's theorem** stratifies the class: rationals (terminating
> CF) · quadratic irrationals (eventually-periodic CF — metallic means golden/silver/bronze) ·
> higher-algebraic/transcendental (unbounded partial quotients — Liouville). **Cluster
> prediction — TESTED (2026-05-23, sturmian_run.py):** the symbolic Sturmian-word event-train
> does NOT stratify by Lagrange class — it is 3-distance-rigid (Brody q=ρ=1 for every α), and
> W1δ/I.5q/RF track the FIRST CF quotient (gap ratio), not quadratic-vs-transcendental; rational
> (periodic) is cleanly distinct. ⇒ The CF-class stratification (predicted, and SHOWN by AM's
> θ-class spectral fingerprint, Brody q golden 0.81→Liouville 0.28) is a **spectral/operator
> phenomenon, not a symbolic one** — it needs the operator spectrum (AM / Sturmian Hamiltonian =
> Fibonacci at golden), not the word. **Spectral test DONE + CONFIRMED (sturmian_hamiltonian_run.py):**
> the operator spectrum IS Cantor (D_box<1, q=0) for all irrational α and DOES stratify by CF-class
> — quadratics cluster (D_box≈0.63–0.65), Liouville separates (0.724), rational → AC band (0.805,
> q=0.88). So the prediction holds spectrally. Remaining: (b) **brocot.fm** spectral-side audio
> fingerprint vs parameter-side path. The Sturmian family bridges brocot.fm, AM-θ, Fibonacci, and
> the arithmetic substrates.

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
| Sturmian-word (α-sweep) | ✓ I.5q + matched I/II (8 α) | ✓ III (RF) | ◐ 3-distance rigid (q=1 univ) | ◐ III | — | | — | — | ◐ Σ²/Δ₃ | — | — | Lagrange-class α-sweep | ✓ VI.3 |
| Sturmian-Hamiltonian (α-sweep) | ✓ matched NNS (7 α, Cantor q=0) | | ✓ Cantor; stratifies by CF-class | | — | ✓ IV.2 D_box (0.63 quad→0.72 Liouv) | | — | ◐ Σ²/Δ₃ | — | — | Lagrange-class α-sweep | — |
| Fibonacci Ham. | ✓ (= golden Sturmian-Ham; D_box=0.63) | | ✓ Cantor (DGY class I) | | — | ✓ IV.2 | | — | | — | — | — | — |
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
