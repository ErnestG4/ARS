# Local crystallization beneath a frozen global measure: sealed measurements of spacing statistics under repeated differentiation

**DRAFT v0.1 — 2026-08-12. Target submission 2026-08-19 (ROADMAP Step 4 pre-commitment).
Scale-law section ships with whatever state exists on that date (inclusion rule, pinned).**
Venue: short note, math.PR (cross-list math.CA). Repo public at submission.

---

## Abstract (draft)

Let p be a real-rooted polynomial of degree n with roots drawn from a seed ensemble, and let
p^(k) be its k-th derivative. Recent theorems (Angst–Nguyen–Poly 2026; Michelen–Vu 2022) prove
that the *global* empirical root measure of p^(k) is asymptotically frozen at the seed measure
through k = o(n/log n). We measure what happens beneath that frozen profile: the *local spacing
statistics*, for which no theorem exists in any regime 1 ≪ k ≤ sn (adversarial literature
verification included). Under a pre-registered, seal-adjudicated protocol — functional-form
ladder, selection rule, and decision thresholds committed before the data existed — we find that
local spacing fully crystallizes by k ≈ 6–11 at every n ∈ {1024, 2048, 4096}: a purely local
rearrangement invisible to the strongest global theorems. The relaxation follows ONE functional
family for every seed class tested — a stretched exponential in k — but with seed-dependent
parameters: iid-uniform seeds relax with (τ, β) = (1.73, 0.79) against GUE-eigenvalue seeds'
(0.89, 0.70), separated at 20σ and 9σ respectively. Same-family universality, refuted one level
down. The crystallization scale is O(1) in n: a sealed two-hypothesis discrimination at
n = 16384 returns SCALE-FLAT, with k* = 10.828 ± 0.011 landing on the flat prediction (10.827)
to three decimal places and excluding proportional-logarithmic growth at ~10σ — eleven
derivatives crystallize an iid seed at every n across a 16× range. In one sentence: relaxation
form universal, parameters seed-dependent, scale flat in n — universality holds one level up,
breaks one level down, and the whole stack is invisible to every global theorem in the field. The stretch itself is a puzzle with
its most natural explanation already eliminated: conditioning on initial gap environment fails
to decompose it (falsified under blind-committed binning rules), and rigid, homogeneous GUE
seeds stretch too — pointing at flow-generated dynamical heterogeneity in the glass-relaxation
sense. Verdict grade: SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK; the measurement chain — including
an instrument artifact found by the protocol's own regression step, cured under the seal's
pre-committed amendment rules, and a verdict honestly downgraded and then resolved at higher
resolution — is fully auditable, commit by commit, in the public repository.

## 0. Framing prose (Will, 2026-08-13 — near-final register, fold into §§1/4/5)

**What we measured.** Local spacing statistics of real-rooted polynomials under repeated
differentiation, at fixed derivative count k — the regime between the proven global laws and
the proven k → ∞ endpoints. Four sealed or graded results: (1) **Form**: relaxation of
1 − ⟨r̃⟩ toward crystalline follows a stretched exponential for both seed classes, selected by
pre-committed AICc on all three instrument bands, at every n from 1024 to 16384.
(2) **Parameters**: seed-dependent — iid (τ = 1.734, β = 0.788) vs GUE (τ = 0.888, β = 0.703),
separated at 20σ and 9σ. Universality of family, non-universality of rate. (3) **Scale**: k*
is flat in n across a 16× range — ~11 derivatives crystallize a Poisson seed, ~6 a GUE seed,
at any degree — with both flat point-predictions sealed before the runs and landing at 0.09σ
and 0.35σ, excluding proportional-log scaling at 10σ and 18.7σ. (4) **Mechanism constraint**:
conditioning on initial gap environment does not decompose the stretch (4 of 5 quintile bins
remain stretched), falsifying seed-carried heterogeneity as the sole origin of β < 1 under
blind-committed rules.

**Where this sits.** The field has proven results bracketing our regime on both sides, none
inside it. Global side: the free-convolution law governs the density along the flow
(Steinerberger; Hoskins–Kabluchko; Campbell–O'Rourke–Renfrew IMRN), and Angst–Nguyen–Poly
(Jan 2026) make the small-k picture sharp — the empirical zero distribution of the k-th
derivative converges back to the seed measure for all k = o(n/log n), extending the Kabluchko
k = 1 / Byun–Lee–Reddy fixed-k / Michelen–Vu growing-k lineage. Endpoint side:
Hoskins–Steinerberger's Hermite behavior at k = n − ℓ, and Campbell–O'Rourke–Renfrew's Cosine
Universality with Hermite and Laguerre universality as finite free limit theorems — a program
grown out of the Marcus–Spielman–Srivastava interlacing-families work behind Ramanujan graphs
and Kadison–Singer. Our contribution threads the needle these leave open: the global measure
is provably frozen at the k's we study, while local spacing fully crystallizes by k ≈ 10
underneath it. Two-scale structure — macroscopically invariant, microscopically resolved —
that no global theorem can see and no endpoint theorem reaches.

## 1. Introduction — the two-scale contrast

- Frame: the derivative flow k ↦ roots(p^(k)) as a one-parameter flow on point configurations.
- The global rail (theorem): ANP 2601.01212 Thm 1.3 — empirical measure → μ, a.s., all
  k = o(n/log n), for dimension-nondegenerate μ; Uniform[−1,1] is their example (3) (C¹-curve,
  local dimension 1). Lineage: Kabluchko k=1 (1206.6692), Byun–Lee–Reddy fixed k, Michelen–Vu
  k ≲ log n (2212.11867), a.s. sequel 2307.06788.
- The endpoint rails: Cosine Universality at k → ∞ for entire functions (Campbell–O'Rourke–
  Renfrew 2410.06403, conj. Farmer–Rhoades math/0310252); Hermite endpoint at k = n − O(1)
  (Hoskins–Steinerberger 2005.09809); the flow's Appell targets are locally lattice
  (Campbell–Jalowy 2605.31356 Thm 2.7). n = ∞ Poisson anchor: zeros of f^(k) → random
  ℤ-translate, NO rate (Pemantle–Subramanian 1409.7956).
- The gap (verified open, twice, adversarially — §Appendix B): local spacing statistics of
  p^(k) for degree-n real-rooted polynomials, ANY regime 1 ≪ k ≤ sn. ANP verified SILENT on
  local statistics (full-text check).
- Our contribution: the first measurements in that gap, under a sealed protocol; the two-scale
  statement — crystallization completes at k = O(10) while the global measure provably cannot
  move until k ~ n/log n.

## 2. Instrument

- Flow: exact root-space differentiation (electrostatic interlacing solve; certified against
  the Hermite self-map H_n' = 2n·H_{n−1} to 1.35×10⁻¹³ of local spacing; the map is globally
  ℓ∞-non-expansive — convex-weight lemma — measured transfer ratios 0.86 → 0.09).
- Unfolding reference: empirical-seed fractional free convolution μ_s = D_{1−s}(μ^⊞1/(1−s))
  via Belinschi–Bercovici subordination (contraction-certified), per-gap Gauss quadrature,
  smooth ε_k rule, Richardson primary. Two permanent known-answer gates bracket the operating
  range (lattice ≤ 10⁻⁷ rippled worst case; Hermite-through-reference ≤ 10⁻⁵ smooth case).
- Machinery citations: Marcus–Spielman–Srivastava finite free convolution; Steinerberger PDE;
  Hoskins–Kabluchko; Arizmendi–Campbell–Fujie 2506.08910 (finite free cumulants, critical
  points); Campbell–O'Rourke–Renfrew 2307.11935.
- Error architecture: numerical jitter floor (gated, ~11 orders below signal) vs realization
  ensemble σ (16 replicates, SeedSequence-enumerable) — two instruments, never blended.
- Readout: 1 − ⟨r̃⟩ on the central bulk window (log-space; ceiling compression), Σ²(L) as
  consistency witness.

## 3. Sealed protocol

- The seal (RATE_QUESTION_SEAL, commit 95e1ad3): disclosure ledger, form ladder
  {power, exponential, stretched exponential}, AICc selection, fit-window rule, 3σ/5σ z-rule
  on shape parameters (amplitude excluded), form-disagreement clause, ε/2ε triple-band
  invariance clause, picket-fence ceiling-invariance clause, harness commit binding with
  gate-rerun protocol.
- Pre-registration ordering: ladder committed before any k-resolved data existed; seal written
  before the error-bar ensemble ran (the fitted iid data is entirely post-seal).
- The amendment mechanism as a feature: v1.5/v1.5.1 (instrument correction under the seal's
  post-change protocol), v1.6 (dense grid with second disclosure ledger and grade label).

## 4. Results

- **Crystallization**: 1 − ⟨r̃⟩ falls from O(0.3) to the 10⁻⁴ ceiling within k ≲ 32 at every n;
  k*(iid) = 10.95 ± 0.07 / 10.59 ± 0.05 / 10.89 ± 0.03, k*(GUE) = 6.23 / 6.26 / 6.16 (± ≤ 0.02)
  at n = 1024/2048/4096. [Figure: relaxation curves, both seeds, three n, with σ bands.]
- **One family**: F3 (stretched exponential) selected for BOTH seed classes on ALL THREE
  instrument-band arms (triple-band invariant), all n.
- **Seed-dependent parameters**: (τ, β) = (1.734, 0.788) iid vs (0.888, 0.703) GUE at n = 4096;
  z(τ) = 20.4, z(β) = 9.3 against the sealed 5σ threshold. VERDICT: RATE-SEED-DEPENDENT
  [SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK].
- **Scale in n — sealed verdict SCALE-FLAT**: two point predictions committed before the run
  (H_flat = 10.827 from precision-weighted anchors with σ_sys = 0.192 absorbing the anchors'
  non-monotone scatter, χ²_flat = 27.9/2 filed openly; H_log = 12.704, proportional growth
  anchored at n = 4096; affine log rejected as non-identifiable on near-flat anchors);
  measured k*(16384) = 10.828 ± 0.011 — d_flat = 0.001, d_log = 1.876 ≈ 10σ_eff. F3 holds on
  all three bands at n = 16384.
- **What the three-decimal agreement certifies** (the sentence, per Will): a post-hoc analysis
  hitting three decimals would invite suspicion of tuning; the commit ordering makes tuning
  impossible, so the agreement converts entirely into evidence that the instrument's error
  model is honest — the ±0.011 means what it says. The prediction's precision certifies the
  error bars, not just the hypothesis, and every error-barred number in this section comes from
  the same certified pipeline.
- **GUE arm (landed under the pinned rule, its one sentence):** the GUE arm, run
  unsealed-confirmatory per the seal's if-time clause, read k*(16384) = 6.220 ± 0.004 against
  its flat prediction 6.202 (0.35σ_eff; proportional-log excluded at 18.7σ_eff) — both seed
  classes crystallize on an O(1) clock, and both landed on their pre-committed predictions
  within a small fraction of σ.
- **Ceiling and floor**: Hermite arm measured crystalline at every s (1 − ⟨r̃⟩ 10⁻⁷–10⁻⁵);
  picket-fence ceiling-invariant under the flow (≤ 10⁻³ every k, every n, corrected
  instrument); interlacing floor at k = O(1) (program-derived — labeled as such; complex
  pairing theorems exclude real support by hypothesis).

## 5. Discussion

- The two-scale statement, formal: ANP freeze the macroscopic profile; we measure completion of
  local crystallization at k* = O(10), n-independent across our range. The local regime is open
  AND provably invisible to the strongest global theorems.
- **The stretch as the open mechanism question — now with its citation spine (Will,
  2026-08-13).** The form is Kohlrausch–Williams–Watts, and its origin is one of the core
  questions of the glass transition: the dominant explanation holds β < 1 reflects an average
  over a spatially heterogeneous distribution of local relaxation times (dynamical
  heterogeneity, observed in simulation and colloid experiment), against an alternate line in
  which dynamics are locally nonexponential — intrinsic nonexponentiality. Our β-composition
  is a clean datum for exactly that debate, from a system with none of glass physics'
  confounds: Step 2 falsified the initial-configuration version of the heterogeneous scenario
  under blind-committed rules (conditioning on seed environment leaves the stretch intact —
  4/5 quintile bins), and both seed classes — including rigid, homogeneous GUE — stretch
  anyway. In glass language: the stretching is not quenched-disorder-carried, so it is either
  dynamically generated heterogeneity or intrinsic local nonexponentiality — and the field's
  own instrument for separating those, the ISOCONFIGURATIONAL ENSEMBLE, is structurally the
  experiment this harness already performs (fixed seed, ensemble over dynamics-adjacent
  perturbation). The backlogged mid-flow re-conditioning probe is precisely the
  isoconfigurational move translated to root flows. Specimen sentence: a deterministic,
  exactly-specified interacting system — convex-weight root dynamics with a proven Lipschitz
  structure — exhibiting measured KWW relaxation with a certified error model is a genuinely
  unusual object for that literature: simpler than any glass-former, richer than any solvable
  toy. Filed texture any mechanism must face: exactly one environment quintile (largest
  cone-gap) relaxes as a clean exponential, 3× slower than the stretched rest.
- Complex/rotationally-invariant flow: excluded here, live boundary (Galligo–Najnudel–Vu
  2506.06263, 2607.05054). Heat flow: the published half-bridge (Hall–Ho–Jalowy–Kabluchko,
  Indiana/EJP/LMP 2025) and the queued cross-flow comparison (dBN connection).
- **Why the clock is O(1) — one graded paragraph, anchored to the paper's own lemma.** The
  derivative-root map's sensitivities ∂x*ᵢ/∂rⱼ = (x*−rⱼ)⁻² / Σₗ(x*−rₗ)⁻² are positive convex
  weights decaying quadratically in distance: each new root is overwhelmingly determined by its
  near neighbors (measured transfer ratios 0.86 → 0.09, §2). Relaxation is therefore a local
  process whose interaction range is measured in spacings, not fractions of the support — and a
  local process has no way to know n. This is interpretation, not theorem, but interpretation
  anchored to a lemma the paper proves — and it dovetails with, rather than competes against,
  the open mechanism question: locality explains why the clock is O(1); it conspicuously fails
  to explain why the clock is STRETCHED, which is exactly what the β-composition poses.
- Watch item, updated 2026-08-13 (a dated re-sweep datum): JKM Part I AND Part II now posted —
  Part II is a catalog of exactly-characterized seed families (Touchard, Fubini, Eulerian,
  Narayana, hypergeometric incl. Hermite/Laguerre/Jacobi), a ready-made extension of the seed
  roster if the parameter-dependence question wants a third and fourth class. Part III
  (fluctuations/functional limit theorems — the one that would touch these σ-resolved curves)
  remains in preparation and absent from both authors' publication lists: fixed-k local
  spacing stays unclaimed; these verdicts remain the only measurements in the regime.
- Boundary hardening: the complex/rotationally-invariant flow (Galligo–Najnudel–Vu and
  successors) and the heat-flow program (Hall–Ho–Jalowy–Kabluchko: Indiana, EJP, LMP) are both
  producing steadily; neither touches real-rooted fixed-k local statistics; both cited as LIVE
  adjacent tracks. The heat-flow set is Step 5's opening citation spine.

## Appendix A — Honesty chain (the feature, not the confession)

Verdict history with commit hashes: RATE-SEED-DEPENDENT via form clause (v1 instrument,
4f29d70) → instrument artifact found by the roadmap's own Step-1 regression (c235861) →
fit-window contamination measured at 24–38 σ_mean (be7f2b9) → corrected reference defined
sight-unseen, failed its own gate, amended v1.5.1 with the gate-forced Richardson fix
(78ce01a, c7275d3) → all gates re-certified; verdict honestly downgraded to
INCONCLUSIVE-ON-INSTRUMENT-GROUNDS, earned not technical (d6a7cff) → dense-grid amendment with
second disclosure ledger and grade label (c986573) → RATE-SEED-DEPENDENT via the parameter
clause, triple-band invariant (6cc2562). Seal JSONs and the commit-ordering table reproduced.
A hostile referee looking for the weakness should find we published it first.

## Appendix B — Literature verification protocol

Adversarial pulls (agent-executed, four targets, ~30 sources) 2026-08-11; post-pull sweep
2026-08-12 (ANP verified: hypothesis class covers Uniform[−1,1] via C¹-curve example; full-text
silent on local statistics). GAP STANDS under both the fixed-s and small-k parameterizations.
Writing-time re-sweep, DATED here so the paper's own OPEN claims carry their verification date:
Jalowy–Kabluchko–Marynych Part III by name, the 2410.06403/ANP citation graphs, and the
Galligo–Najnudel–Vu line. [Date stamp at execution.]

## Appendix C — Reproducibility and cost

Wall-clock economics for replicators: the n = 16384 arm ran 16 replicates on a Ryzen 5900X
under 5-way replicate-level multiprocessing and netted ~1.5–2× over serial — these kernels are
streaming-dominated (~3 flops/byte), so the memory-bandwidth wall binds well below the core
count; budget accordingly. Solver temporaries are candidate-axis-chunked (bitwise-identical;
known-answer gates re-certified after the change, per the seal's post-change protocol). All
RNG derives from a single committed SeedSequence master; every replicate is enumerable in
advance and every run is exactly reproducible, including across the two OS reboots this
campaign absorbed mid-flight.

## TODO (drafting)

- [ ] Figures: (1) relaxation curves both seeds × three n with σ bands + fitted F3;
      (2) k*(n) with sealed predictions; (3) per-bin Step-2 decomposition; (4) two-scale
      schematic (frozen measure / crystallizing spacings).
- [ ] Full prose for §§1–5 (skeleton → text).
- [ ] LaTeX conversion + arXiv packaging; repo tag.
- [ ] Writing-time re-sweep: 2410.06403 citation graph; JKM-III status check (named).
- [ ] Step-3 verdict slot per inclusion rule on 2026-08-19.
