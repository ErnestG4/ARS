# Local crystallization beneath a frozen global measure: sealed measurements of spacing statistics under repeated differentiation

**FULL PROSE DRAFT v1.0 — 2026-08-13. Post-review (internal + literature audits applied).
LaTeX conversion and figures pending. Target submission 2026-08-19.**

---

## Abstract

Let p be a real-rooted polynomial of degree n with roots drawn from a seed ensemble, and let
p^(k) denote its k-th derivative. Recent theorems prove that the *global* empirical root measure
of p^(k) is asymptotically frozen at the seed measure through every k = o(n/log n)
(Angst–Nguyen–Poly 2026, extending Kabluchko, Byun–Lee–Reddy, and Michelen–Vu). We measure what
happens beneath that frozen profile: the *local spacing statistics*, for which, to our
knowledge, no theorem and no prior measurement exists in any regime 1 ≪ k ≤ sn, s < 1
(adversarial literature verification included, dated). Under a pre-registered, seal-adjudicated
protocol — functional-form ladder, selection rule, and decision thresholds committed before the
data existed — we find that local spacing crystallizes within roughly ten derivatives at every
degree measured: a purely local rearrangement invisible to the strongest global theorems.
The relaxation of the gap-ratio distance 1 − ⟨r̃⟩ follows one functional family for every seed
class tested — a stretched exponential in k, AICc-best of the pre-registered ladder on all
three instrument bands at every n from 1024 to 16384 — but with seed-dependent parameters:
iid-uniform seeds relax with (τ, β) = (1.73, 0.79) against GUE-eigenvalue seeds' (0.89, 0.70)
(primary readout, n = 4096), separated at 20σ and 9σ under the sealed rule and at 12σ and 5.8σ
under a conservative covariance rescaling. Same-family universality, refuted one level down.
The crystallization scale k* is flat across the measured 16× range in n: a sealed
two-hypothesis discrimination at n = 16384 returns SCALE-FLAT, excluding proportional-
logarithmic growth at ~10σ_eff. The stretch itself arrives with its most natural explanation
already eliminated — conditioning on initial gap environment fails to decompose it, under
blind-committed binning rules, and rigid, homogeneous GUE seeds stretch too — placing the
mechanism question in the Kohlrausch stretched-exponential literature's own terms, with one of
its standard moves already performed. Verdict grade: SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK.
The full measurement chain — including an instrument artifact found by the protocol's own
regression step, cured under pre-committed amendment rules, and a verdict honestly downgraded
and then resolved at higher resolution — is auditable commit by commit in the public
repository.

## 1. Introduction

Repeated differentiation acts on a real-rooted polynomial as a flow on point configurations:
each application of d/dx replaces the n roots by the n−1 interlacing roots of the derivative.
The global behavior of this flow is by now well understood. Along the proportional regime
k = ⌊sn⌋ the empirical root measure evolves by fractional free convolution (Steinerberger's
nonlocal transport equation; Hoskins–Kabluchko, Exp. Math. 32 (2023) 573–599;
Campbell–O'Rourke–Renfrew, IMRN 2024; Hall–Ho–Jalowy–Kabluchko, Trans. AMS Ser. B 13 (2026)
190–239), and in the small-k regime the newest results make the picture sharp:
Angst–Nguyen–Poly [ANP] prove that for roots drawn i.i.d. from a measure μ that is either
discrete or dimension-nondegenerate — a class that includes our Uniform[−1,1] seed via their
C¹-curve example — the empirical zero measure of p^(k) converges back to μ, almost surely, for
every k = o(n/log n). This extends the k = 1 law of Kabluchko (proving the Pemantle–Rivin
conjecture), the fixed-k results of Byun–Lee–Reddy, and the growing-k theorem of Michelen–Vu.
At the opposite end of the flow, the endpoints are equally settled: at k = n − O(1) the
surviving roots are those of a Hermite polynomial up to a random shift (Hoskins–Steinerberger),
with root-level fluctuation theory around that limit (Arizmendi–Campbell–Fujie — an endpoint-
regime result, ℓ = n − k fixed, explicitly outside the regime studied here); and for entire
functions, repeated differentiation drives zeros to perfect spacing — Cosine Universality,
conjectured by Farmer–Rhoades, proven for even real-rooted entire functions by
Campbell–O'Rourke–Renfrew, with the same phenomenon established for the Selberg Ξ-function by
Gunns–Hughes. The limiting Appell configurations are themselves locally lattice
(Campbell–Jalowy, "Pólya–Schur problems and free probability," Thm 2.7). For a Poisson-zeroed
entire function — the n = ∞ shadow of our iid seed — Pemantle–Subramanian proved that zeros of
f^(k) converge to a uniform random translate of ℤ as k → ∞, with no rate.

Between these two proven territories lies a gap: the local spacing statistics of p^(k) for
degree-n polynomials at fixed or slowly growing k. No theorem addresses it — ANP's paper, the
strongest global result in the small-k regime, contains no statement finer than weak
convergence of the empirical measure (verified against the full text) — and, to our knowledge,
no measurement existed either (two adversarial literature audits plus a dated submission-day
re-sweep; Appendix B). This paper reports the first measurements in that gap, under a sealed
protocol, and the headline is a two-scale structure: **the global measure is asymptotically
frozen through every k = o(n/log n), while local spacing fully crystallizes by k ≈ 10
underneath it.** Macroscopically invariant, microscopically resolved — a regime no global
theorem can see and no endpoint theorem reaches.

Four results, each sealed or explicitly graded:

1. **Form.** The relaxation of 1 − ⟨r̃⟩ (gap-ratio distance from crystalline) follows a
   stretched exponential in k for both seed classes — AICc-best of a pre-registered three-form
   ladder on all three instrument bands, at every n from 1024 to 16384.
2. **Parameters.** Seed-dependent: iid (τ = 1.734, β = 0.788) versus GUE (0.888, 0.703),
   primary readout at n = 4096, separated at z(τ) = 20.4 and z(β) = 9.3 under the sealed rule
   (12.0 and 5.84 under conservative covariance rescaling). Universality of family,
   non-universality of rate.
3. **Scale.** k* — the fitted curve's crossing of 1 − ⟨r̃⟩ = 10⁻² — is flat across the measured
   16× range: ~11 derivatives crystallize a Poisson seed and ~6 a GUE seed at every n measured,
   with both flat point-predictions sealed before the runs and landing at 0.003σ_eff and
   0.34σ_eff, excluding proportional-log scaling at 9.8σ_eff and 18.6σ_eff.
4. **Mechanism constraint.** Conditioning on initial gap environment does not decompose the
   stretch (4 of 5 quintile bins remain stretched, under binning rules committed blind),
   falsifying seed-carried heterogeneity as the sole origin of β < 1.

## 2. The flow and the instrument

**Flow.** We work in root space. Given the sorted roots of p, the roots of p′ are the solutions
of Σᵢ 1/(x − rᵢ) = 0, one per gap by Rolle interlacing; each is found by bracketed bisection
plus clamped Newton, so no root can be lost or duplicated. The solver is certified against the
Hermite self-map — Hₙ′ = 2n·Hₙ₋₁ moves roots exactly onto Hₙ₋₁'s roots — to 1.35×10⁻¹³ of
local spacing over 480 composed steps. The derivative-root map has a useful exact structure:
its sensitivities ∂x*ᵢ/∂rⱼ = (x*−rⱼ)⁻²/Σₗ(x*−rₗ)⁻² are positive convex weights, so the map is
globally ℓ∞-non-expansive (Lipschitz-1 per step). This is not left as a lemma: measured
transfer ratios run 0.86 at k = 1 down to 0.09 at k = 64 — the flow actively contracts seed
perturbations — and it underwrites the error architecture below.

**Readout.** The primary statistic is 1 − ⟨r̃⟩, the mean adjacent-gap ratio's distance from the
crystalline value, computed on unfolded spacings over a fixed central bulk window; Σ²(L) rides
along as a consistency witness. Unfolding is against the theorem-side macroscopic density: the
empirical-seed fractional free convolution μ_s = D_{1−s}(μ^⊞1/(1−s)), evaluated by
Belinschi–Bercovici subordination (a Denjoy–Wolff contraction, convergence certified per call),
integrated per root gap by Gauss quadrature with a single smooth ε_k bandwidth rule, and read
through a Richardson pair-extrapolation that removes the O(ε²) bias the known-answer gates
diagnosed. Two permanent known-answer gates bracket the reference's operating range —
maximally rippled input (a lattice seed, whose true one-step response is ≤ 10⁻⁸, gated at
10⁻⁷) and maximally smooth input (a Hermite seed pushed through the full empirical-reference
path against exact Hₙ₋ₖ truth, gated at 10⁻⁵) — and re-run on any instrument change.

**Error architecture.** Two instruments, never blended: a numerical jitter floor (gated;
replicate spread under seed perturbations at δ down to 10⁻¹² of local spacing sits ~11 orders
below signal) and a realization ensemble (16 fresh seeds per class per n, drawn from an
enumerable SeedSequence protocol) whose spread is the only σ the fits and verdicts consume.

## 3. The sealed protocol

All adjudication rules were committed before the data they judge existed, in a seal bound to
the harness commit: a three-form ladder {power law, exponential, stretched exponential} with
AICc selection over a pre-declared fit window; a 3σ/5σ z-rule on shape parameters (amplitude
excluded) with form disagreement itself constituting a seed-dependence verdict; an ε-band
invariance clause (form selection must agree across the primary and both raw bandwidth arms,
else the verdict is INCONCLUSIVE-ON-INSTRUMENT-GROUNDS); a picket-fence ceiling-invariance
clause; and, for the scale question, two point predictions with acceptance bands constructed
so that no double-positive is possible. The seal carries a disclosure ledger stating exactly
what had been seen when it locked, and a post-change protocol: any instrument modification
triggers re-certification of the known-answer gates before science is recomputed.

That protocol was exercised in earnest. The first verdict (seed-dependent by form
disagreement) was retracted when the protocol's own regression step exposed a reference-grid
aliasing artifact contaminating the fit anchors at 24–38σ_mean; the corrected instrument was
pinned sight-unseen, failed its own lattice gate once (a 1/n²-scaling O(ε²) bias), was amended
under the rules, re-certified, and the re-adjudication returned INCONCLUSIVE-ON-INSTRUMENT-
GROUNDS for an earned reason — the original powers-of-two k-grid could not adjudicate GUE's
fast transition. A grid-density amendment (changing nothing else) resolved it. The verdict
below therefore carries the grade SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK — pre-committed rules
executed faithfully, on a confirmatory-resolution run, with the prior look disclosed — and the
entire chain, hash by hash, is Appendix A.

## 4. Results

**Form.** F3 (stretched exponential, 1 − ⟨r̃⟩ ≈ a·exp(−(k/τ)^β)) is selected for both seed
classes on all three instrument bands at every n — decisively by AICc (margins of 10²–10³
against the exponential and power-law alternatives). Stated with its grade: F3 is AICc-best of
the pre-registered ladder, not a demonstrated law. The selected fits carry residual structure
beyond the ensemble σ — χ²/dof rises 0.76 → 2.29 → 3.76 → 23.4 along n = 1024 → 16384 on the
iid primary arm (raw arms up to ~98; the GUE primary is underdispersed at 0.02–0.22, the
fingerprint of cross-k correlation from shared replicates). This growth is itself a finding:
the instrument's precision improves faster than the three-form family's fidelity, so at
n = 16384 the measurement resolves structure beyond F3. That is the quantitative form of
"best-of-three," and it is the opening datum for any richer-form successor.

**Parameters.** At n = 4096 on the primary readout, iid (τ = 1.734, β = 0.788) versus GUE
(0.888, 0.703): z(τ) = 20.4, z(β) = 9.3 against the sealed 5σ threshold. Under a conservative
treatment — rescaling each covariance by max(1, χ²/dof) — z = 12.0 and 5.84: the verdict
survives, with z(β) near the bar, and both numbers are reported so the reader can weight them.
The quoted parameter values are readout-definition- and n-dependent (the deliberately biased
raw arms give lower (τ, β); iid τ scatters ~0.19 across n); what is robust across every band
and every n is the ordering — iid > GUE in both τ and β, with Δτ = 0.65–0.85 far exceeding
the drift. **Verdict: RATE-SEED-DEPENDENT.**

**Scale.** Two point predictions were sealed before the n = 16384 run from the three smaller
anchors: H_flat = 10.827 (precision-weighted mean, with σ_sys = 0.192 absorbing the anchors'
real scatter — they are mutually inconsistent as an exact constant, χ² = 27.9/2 iid and
44.0/2 GUE, both filed) and H_log = 12.704 (proportional growth anchored at n = 4096; an
affine log fit is non-identifiable on near-flat anchors and was rejected in the seal itself).
Measured: k*(iid, 16384) = 10.828 ± 0.011 — 0.003σ_eff from H_flat, 9.8σ_eff from H_log.
**Verdict: SCALE-FLAT.** The GUE arm, run unsealed-confirmatory, read 6.220 ± 0.004 against
its flat prediction 6.202 (0.34σ_eff; log excluded at 18.6σ_eff). What these landings certify
is the discrimination — flat accepted, proportional-log excluded, tuning impossible by commit
order. The three-decimal iid coincidence itself is luck under our own error model (σ_eff is
anchor-scatter-dominated; a 0.001 landing has ~0.4% probability) and is claimed as nothing
more; the fit errors σ_m are optimistic (see Form), which is why the sealed adjudication runs
on σ_eff throughout — the GUE landing sits at 4.2σ_m and is accepted precisely because the
seal's error model anticipated that σ_sys dominates.

**Ceiling, floor, and controls.** The Hermite seed's bulk is measured crystalline at every
flow time (1 − ⟨r̃⟩ at 10⁻⁷–10⁻⁵ — the finite-n ceiling arm); the picket fence is
ceiling-invariant through the full corrected pipeline at every k and n (the sealed clause
that once fired on the artifact now holds); and the k = O(1) floor — a Poisson-gapped seed
cannot be crystalline after one Rolle-interlacing step — is stated as program-derived: the
literature's zero–critical-point pairing theorems require planar densities and exclude real
support by hypothesis.

## 5. Discussion

**The two-scale statement.** ANP freeze the macroscopic profile — asymptotically, almost
surely, for every k = o(n/log n), for exactly our seed class — while the local spacing
completes its crystallization by k* ≈ 6–11, n-independent across the measured range. The
mechanistic grounding is the paper's own lemma, offered as interpretation and graded as such:
convex-weight sensitivities decaying quadratically make each root's update a near-neighbor
affair, so relaxation is a local process whose interaction range is measured in spacings, not
fractions of the support — and a local process has no way to know n. Locality explains why
the clock is O(1). It conspicuously fails to explain why the clock is stretched.

**The stretch.** The relaxation form is Kohlrausch–Williams–Watts, and the origin of KWW
stretching is a fifty-year question in the glass literature, standardly framed as a dichotomy
(Ediger, Annu. Rev. Phys. Chem. 51 (2000) 99; Richert, J. Phys.: Condens. Matter 14 (2002)
R703; Sillescu, J. Non-Cryst. Solids 243 (1999) 81): dynamical heterogeneity — β < 1 as an
average over spatially varying exponential rates — versus intrinsically nonexponential local
dynamics. Our measurements contribute a datum from a system with none of glass physics'
confounds. The initial-configuration version of the heterogeneous scenario is falsified here
under blind-committed rules: binning roots by seed gap environment leaves 4 of 5 quintiles
stretched, and the rigid, homogeneous GUE seed stretches too — so the stretching is not
quenched-disorder-carried. In the field's terms, what remains is dynamically generated
heterogeneity or intrinsic nonexponentiality, and the field's own instrument for separating
them — the isoconfigurational ensemble (Widmer-Cooper–Harrowell–Fynewever, PRL 93 (2004)
135701; applied to KWW origins in arXiv:2011.00579) — is structurally the experiment this
harness performs, with one precision owed: in molecular dynamics the resampled quantity is
momenta, bona fide dynamical degrees of freedom; the derivative flow is deterministic and has
no momentum-like variable, so our ensemble resamples seed-adjacent perturbation at fixed
conditioning. The structural match — condition on configuration, ensemble over realization —
is claimed with that limit conceded. We performed that probe: re-conditioning mid-flow (bin
on environment at k = 2 rather than k = 0, rules pinned blind) ALSO fails to decompose the
stretch — 3 of 5 quintiles remain stretched (β = 0.70/0.55/0.49). Neither the initial nor the
instantaneous configuration's local gap environment carries the rate distribution: within the
dichotomy's terms, and under the pinned caveat that the environment variable may be too crude,
the evidence now leans toward intrinsic local nonexponentiality. Three textures constrain any
candidate mechanism: a STABLE slow subpopulation — the largest-gap quintile selects a pure
exponential at both conditioning times with nearly unchanged rate (τ = 3.07 at k = 0,
3.18 at k = 2); an emergent fast power-law tail (the smallest-gap quintile at k = 2 selects
F1, χ²/dof 1.2); and the fact that the per-bin fits at k = 2 conditioning are mostly GOOD
(χ²/dof 0.5–1.2 for the middle quintiles) while the aggregate misfits — the residual
structure lives in the mixture, not the components. Rates DO order monotonically by
environment (τ = 3.18 → 0.30 across quintiles); what environment fails to explain is the
stretch WITHIN each bin. A deterministic,
exactly-specified interacting system with a proven Lipschitz structure exhibiting measured
KWW relaxation under a certified error model is, we believe, an unusual specimen for this
literature: simpler than any glass-former, richer than any solvable toy.

**Adjacent tracks.** The complex/rotationally-invariant flow (Galligo–Najnudel–Vu; Najnudel–Vu)
and the heat flow (Hall–Ho–Jalowy–Kabluchko, Indiana Univ. Math. J. 74 (2025); EJP 30 (2025);
Hall–Ho, Lett. Math. Phys. 115 (2025)) are both active; neither touches real-rooted fixed-k
local statistics. The nearest theorem-shaped object to our σ-resolved curves is the announced
Part III (fluctuations and functional limit theorems) of the Jalowy–Kabluchko–Marynych
program, unposted as of this writing; Part II's catalog of exactly-characterized seed families
is a ready-made extension of the seed roster for mapping the (τ, β) dependence beyond two
classes.

## Appendix A — The measurement chain

[Verdict-history table with commit hashes, seal JSONs reproduced, and the commit-ordering
table: v1 form-clause verdict (4f29d70) → instrument artifact found by the roadmap's own
regression step (c235861) → contamination measured at 24–38σ_mean (be7f2b9) → corrected
reference pinned sight-unseen (78ce01a), gate-forced Richardson amendment (c7275d3) → gates
re-certified, verdict downgraded to INCONCLUSIVE-ON-INSTRUMENT-GROUNDS (d6a7cff) → dense-grid
amendment with second disclosure ledger (c986573) → RATE-SEED-DEPENDENT via the z-clause
(6cc2562) → SCALE-FLAT sealed (d629f6f; 889f472 seal) → post-review disclosure pass
(505931c). A hostile referee looking for the weakness should find we published it first.]

## Appendix B — Literature verification protocol

Two adversarial audits (2026-08-11, four targets, ~30 sources; 2026-08-13, ~55 sources,
including full-text silence checks on ANP and citation-graph sweeps of both rail papers), and
a submission-day re-sweep to be executed and dated at submission. Process fact filed openly:
the 08-13 audit found a paper our earlier sweeps had missed for eleven months (JKM Part II,
posted 2025-09) — global-only, gap intact — which is why the re-sweep re-runs the searches
rather than citing prior audits. The open-regime claim is therefore always "as of [date],
verified by [protocol]," never a standing fact.

## Appendix C — Reproducibility and cost

[As drafted in NOTE.md: SeedSequence enumeration, wall-clock economics and the bandwidth
wall, bitwise-identical solver chunking with gate re-certification, per-replicate banking
gap disclosed, σ_sys framing caveats.]

---

*Figures (4): relaxation curves both seeds × four n with σ bands and fitted F3; k*(n) with
sealed predictions and acceptance bands; Step-2 per-bin decomposition; two-scale schematic.*
