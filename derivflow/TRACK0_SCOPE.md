# derivflow Track-0 — SCOPE

**Status: SCOPED 2026-08-11 (v1.4 — v1.2 added Will's free-convolution-evaluator design to §4 and
the compact-support pin to §5a after the Hermite gate PASS; v1.3 pre-committed the §6.iii gate rule
and slope-interpretation frame while the n-sweep was in flight, table unseen; v1.4, after §6.iii
PASS and its ceiling finding: k-parameterization of the science grid, the interlacing floor
bracket, the pre-registered functional-form ladder, the §6.iv-a/-b split, and the widened
adversarial-pull target).** Drafted, cut down by Will same day (Hermite gate swapped in
for the mis-specified picket-fence gate; order-of-limits split added to §9; v2/citation-graph rider
added to the pre-seal pull), DRAFT label removed on his call. Nothing here is sealed. Per TOOLKIT
§10 discipline, the sealed prediction is written only AFTER the Track-0 harness validation and null
runs below come back green. Register thread starts at R-188 when work begins.

## 0. Anti-claim header

Nothing in this arc estimates Λ, bears on RH, or claims anything about ζ until the (queued,
untouched) ζ′/Speiser track opens with its own brief. The flow parameter here is d/dx, not dBN
heat time; the dBN comparison is a post-verdict, unsealed, exploratory question (§8).

## 1. Frame

Critical points of f are zeros of f′, so the "overlaying waveforms → critical-point clustering"
program begins with the derivative hierarchy. Repeated differentiation is a one-parameter flow on
point sets with a theorem-side prediction for how the distribution evolves — the same structural
shape as Phase 2's dBN flow, so the Phase 2 harness is reused with one real modification (§4).
Track-0 validates the harness and measures the estimator floor. The science question (§7) is
sealed only after Track-0 passes.

## 2. Substrate decision (binding for this track)

**Real-rooted only.** The theorem rails — Steinerberger's nonlocal transport PDE, the
Hoskins–Kabluchko fractional-free-convolution identification, and finite free probability
(differentiation = finite free convolution) — live in the real-rooted case. Complex-root flows
are a different, less-paved literature: **explicitly out of scope, future track.** Nothing is
lost: the natural seeds (ζ ordinates as a real sequence, GUE eigenvalues) are real point sets.

## 3. Structural-null audit (front-loaded)

Generative family: **deterministic flow on a point set** — given the seed, differentiation has no
randomness; all randomness enters through the seed ensemble. Two nulls, each excluding exactly one
confound:

- **Matched-density flow null.** For any local-structure claim at flow time s, the null is the
  SAME flow run on seeds with matched global density but scrambled local structure (iid draws
  from the seed's empirical measure). Excludes: "the flow's density evolution manufactured the
  spacing signal."
- **Respect-the-unfolding null.** All spacing statistics at flow time s are computed against the
  theorem-side density at that s (§4), never against the seed density or a pooled fit. Excludes:
  unfolding-mismatch artifacts — the Phase 1 matched-density-null discipline, per flow step.

Per-step unfolding is the tripwire to install BEFORE anything runs: unlike dBN at Phase 2's
resolution, the density here evolves strongly along the flow (support shrinks as
√(1−s)-rescaled free-convolution powers), so a static unfold silently violates Phase 1 discipline.

## 4. Flow parameterization and harness modification

Clock: **s = k/n**, fraction of derivatives taken — the scaling in which the free-convolution
results are stated: after ⌊sn⌋ differentiations the empirical root measure is the fractional free
convolution power μ^⊞ 1/(1−s) of the seed measure, rescaled (Hoskins–Kabluchko; Steinerberger PDE).

**Science-grid parameterization (v1.4, forced by §6.iii's ceiling finding):** the crystallization
action lives at **small integer derivative count k, not at order-one s** — the iid seed is at the
crystalline ceiling by s = 0.1 already (findings §3). The science grid is therefore parameterized
in **k ∈ {1, 2, 4, 8, …} up to ~n/10**, with s = k/n derived, not the reverse. Theorem-side floor
at the small end: real-rootedness Rolle-interlaces every derivative — exactly one new root per
gap — so k = 1 is a near-deterministic local map on the gap sequence and a Poisson-gapped seed
CANNOT be crystalline after one step; its spacing distribution is a smoothed transform of the
seed's, not the ceiling. (Exact real-rooted statements to pin via the §9 pull — the
Pemantle–Rivin / Kabluchko critical-points-pairing line is the complex-coefficient cousin; shape
confident, citations not.) The transition Poisson → crystal is thus BRACKETED: seed-like at
k = O(1) by interlacing, Hermite-ceiling by k = n/10 by measurement.

Harness modification (the one real change vs Phase 2): at each sampled s, recompute the unfolding
against the predicted push-forward density before evaluating any spacing statistic. Validation of
this step is itself a Track-0 gate (§6).

**Free-convolution evaluator (v1.2, Will's design):** Belinschi–Bercovici subordination, NOT the
R-transform power series (which degrades exactly at large κ = 1/(1−s) near s_max). The
subordinator solves ω(z) = z/κ + (1 − 1/κ)·F_μ(ω(z)) by fixed-point iteration — an honest
contraction on C⁺ (Denjoy–Wolff), so convergence is certified, and the harness logs the
contraction residual per z-point. Density by Stieltjes inversion at x + iε with ε tied to local
mean spacing; an ε-doubling stability check is folded into the §6.iii residual so bandwidth
sensitivity cannot masquerade as density mismatch. **The reference is derived from the EMPIRICAL
seed measure** (G_emp(z) = (1/n)Σ 1/(z − rᵢ), exact and free), not the population law — the seed
is a draw, already O(n^(−1/2)) off the population law before the flow acts, and a population-law
gate would spend tolerance budget on sampling noise the flow didn't cause. The population-law
comparison rides along as a logged diagnostic, never a gate. Atom threshold, hard-coded not
discovered: an atom of mass a in μ survives in μ^⊞κ iff a > 1 − 1/κ = s, so the seed's
1/n-atoms are gone for any s > 1/n and the reference is a.c. essentially immediately; the s-grid's
first point sits safely above 1/n. **The evaluator has its own known-answer gates and gates
nothing until both are green:** semicircle (free-convolution-stable, sc(σ)^⊞κ = sc(σ√κ), exact at
every κ — smooth input) and symmetric Bernoulli ½(δ₋₁ + δ₊₁) (free binomial, closed form, atoms
of mass ½ surviving exactly until s = ½ then dissolving — atomic input, exercising the threshold
at a predictable-to-the-digit point). Flow-time reference: μ_s = D_(1−s)(μ^⊞ 1/(1−s)) — dilation
by (1 − s), verified against the Hermite/semicircle family where it is exact.

Numerics: root-space iteration, never coefficient space (catastrophic cancellation). Roots of p′
interlace roots of p, so each step is n−1 bracketed 1-D solves of Σᵢ 1/(x−rᵢ) = 0 — guaranteed
brackets, no root can be lost silently. Interlacing is asserted per step (a violated bracket is a
harness FAIL, not a warning). Precision escalates to mpmath where gaps crowd. Seed size n chosen
so that (1−s_max)·n stays above the Phase 1/3 minimum-window power threshold at the largest s
sampled; the per-s zero count is logged so no readout is silently underpowered.

## 5. Calibrator seeds (battery of four)

- **(a) iid seed** (Poisson local structure at matched density): does the flow rigidify from
  maximal disorder, and at what rate. **Population law: Uniform[−1, 1] — compactly supported,
  pinned** (v1.2): Hoskins–Kabluchko is stated for compactly supported measures, so this keeps
  §6.iii's reference inside the theorem's hypotheses; Gaussian-rooted seeds would lean on an
  extension the doc does not cite.
- **(b) GUE-eigenvalue seed** (already rigid): does the flow preserve, sharpen, or overshoot RMT
  spacing toward the crystalline limit. **Bonus property:** the semicircle family is stable under
  fractional free convolution, so this seed's global density is form-invariant along the flow up
  to scaling — the one seed where density drift cannot confound the local readout.
- **(c) Hermite seed** — **known-answer calibrator (theorem-exact).** Hₙ′ = 2n·Hₙ₋₁ exactly, so
  seeding with Hermite roots makes every single flow step land on exactly computable values —
  the roots of Hₙ₋ₖ, rescaled — at every finite n. One gate certifies bracket integrity,
  root-loss FAIL behavior, and the unfolding residual simultaneously, at every sampled s, not
  just at a fixed point. This is the calibrator-zoo-first gate, and the finite free avatar of
  semicircle free-convolution stability.
- **(d) Picket-fence seed** — **measurement, NOT a gate.** Demoted from the drafted known-answer
  role (Will's catch, owned as his proposal error two turns prior, recorded here per
  gate-certifies-half discipline): the uniform root measure is NOT a fixed point of fractional
  free convolution, so a finite-n picket-fence seed's global density drifts BY THEOREM, and the
  drafted "flow-invariant else broken" gate would have failed a correct harness. Its unfolded
  local spacing under the flow is an open question and stays in the battery as one.

Readouts: **⟨r̃⟩ and Σ²(L) along s** — the Phase 1/3 battery unchanged, so numbers are directly
comparable across arcs. Per-s, per-axis series captured in full (capture-full-sweep rule); 20-seed
replicates near any class boundary, distributions reported, not just means.

## 6. Track-0 acceptance criteria (harness, not science)

- **PASS:** (i) **Hermite exactness** — measured roots at every sampled s match the roots of
  Hₙ₋ₖ (rescaled) to stated numerical tolerance, across the full s range; (ii) interlacing
  bracket-verified at every step on all four seeds; (iii) per-step unfolding residual vs the
  fractional-free-convolution prediction within tolerance on the iid seed, and exact on the
  Hermite seed (this doubles as a live derivation of the theorem-side density — no unattributed
  constants); (iv) estimator jitter floor per §6.iv-a below, the Hermite seed supplying the
  **finite-n ceiling arm** (order-of-limits: §9).

**§6.iv split (v1.4, Will's design): two perturbation models, two INSTRUMENTS, never blended.**

- **§6.iv-a — numerical jitter floor. A GATE.** iid position jitter at δ ∈ {10⁻¹², 10⁻¹⁰, 10⁻⁸}
  × local spacing on the seed, replicated flows (R = 6 per δ), spread of unfolded readouts per k
  on the k-grid. Certifies the rate fits aren't reading solver noise. Measured in the small-k
  action window — which is also the cheap window (κ = 1 + k/(n−k) ≈ 1, so §6.iii's 14,792-iter
  corner at s = 0.9 is irrelevant to where the science lives). Downstream extension is
  theorem-side, not assumed: the derivative-root map is **globally ℓ∞ non-expansive**
  (∂x*ᵢ/∂rⱼ = (x*−rⱼ)⁻² / Σₗ(x*−rₗ)⁻² are positive convex weights along any segment of sorted
  root vectors ⇒ Lipschitz-1 per step), so the floor measured at small k upper-bounds every
  later k. Declared gates: (i) **position transfer ratio** ‖Δx(k)‖∞ / ‖Δx(0)‖∞ ≤ 1.02 at every
  k for δ ∈ {10⁻¹⁰, 10⁻⁸} (theorem-exact ≤ 1; slack is solver noise; at δ = 10⁻¹² the ratio is
  logged only — solver accuracy 1.35×10⁻¹³ is a nontrivial fraction of δ there); (ii) **readout
  floor-vs-signal**: at δ = 10⁻¹², for every k with unperturbed 1 − ⟨r̃⟩ > 10⁻³ (the window the
  fits consume), replicate spread < 1% of signal; at-ceiling k rows require spread < 10⁻⁷
  absolute and are labeled as such; (iii) **no super-linear amplification**: log-log slope of
  spread vs δ over the top two decades ≤ 1.3.
- **§6.iv-b — realization ensemble. NOT a gate: the error bar.** Fresh Uniform[−1, 1] draws
  (8–16 replicates), same pipeline. The σ consumed by the functional-form fits and the
  universality verdict comes from -b and only -b; -a has to sit decades below it. Named and
  separate in the artifact, to block the specific failure where a tight numerical floor gets
  quoted as the statistical uncertainty on the rate.
- **FAIL (harness):** a Hermite step misses its known answer, a bracket fails, or unfolding
  residual exceeds tolerance. No science claims are made from a FAIL run; fix and rerun.

**§6.iii gate rule — PRE-COMMITTED 2026-08-10 before the n-scaling table was read** (v1.3; the
n ∈ {1024, 2048, 4096} sweep was in flight, its output unseen, when this was filed and committed):

- **PASS bar: strict monotonicity on all 18 comparisons** (9 sampled s × 2 adjacent-n pairs) of
  the KS residual vs the empirical-seed free-convolution reference.
- **Escalation, not tolerance:** if EXACTLY ONE pair fails, AND it is a 2048→4096 pair, AND it is
  at s ≥ 0.7 (the fluctuation-plausible corner), the verdict is **INCONCLUSIVE-PENDING-REPLICATION**
  — resolved by a pre-declared 10-seed replicate at that s for both n, gate then requiring the
  MEDIAN residual to be monotone. This is escalation to more power (seed-replicate-near-boundary
  rule), not a noise waiver: no reference to the §6.iv jitter floor, which does not exist yet and
  would make the gate unevaluable.
- **Outright FAIL:** more than one failed pair, any failed 1024→2048 pair, or any failed pair at
  s < 0.7.
- **Slope is recorded separately from the verdict** (Will's interpretation frame, fixed before
  the table): fluctuation-dominated residual ⇒ log-slope ≈ −1/2 in n at low-to-mid s is the
  healthy signature. At s = 0.8–0.9 the slope may legitimately flatten from two NUMERICAL causes
  — windowed count shrinking as (1−s)·n, and the ε/inversion floor — so a high-s flattening is
  checked against the per-s ε trace before being read as a gate concern. Monotone-in-n can
  survive a flattened slope; the artifact records both so they cannot be conflated. If a seal is
  later written on top of a PASS obtained through the escalation branch, the seal must say so.
- Only after PASS is the §7 question sealed.

## 7. The question to seal (draft wording — sealed only after Track-0 PASS)

**(Re-cast v1.4, k-parameterized, after §6.iii bracketed the transition.)** The transition
Poisson → crystal is bracketed: seed-like at k = O(1) by Rolle interlacing (theorem), at the
Hermite ceiling by k = n/10 (measurement, findings §3). **The sealed question is the transition's
scale and shape, and whether they are seed-class-independent:** does crystallization complete at
k ~ log n, k ~ n^α, or within O(1) decades of k — and is the answer, and the fitted form's
parameters, the same across seed classes? Readouts: 1 − ⟨r̃⟩ (log space — ceiling compression)
and the Σ²(L) slope, along the k-grid, with σ from §6.iv-b.

**Functional-form ladder — PRE-REGISTERED HERE, before any transition curve has been seen**
(fitting an unknown decay with post-hoc form selection is exactly the freedom the seal exists to
remove): candidate forms for 1 − ⟨r̃⟩ vs k are **(F1) power law** a·k^(−b), **(F2) exponential**
a·exp(−k/τ), **(F3) stretched exponential** a·exp(−(k/τ)^β). Selection rule: **AICc on the
pre-declared k-grid points** (deterministic; a held-out split would itself require a choice the
seal would have to defend). RATE-UNIVERSAL vs RATE-SEED-DEPENDENT is adjudicated on the selected
form's parameters per seed, against §6.iv-b's σ; **form disagreement across seeds itself
constitutes RATE-SEED-DEPENDENT.** Either verdict is publishable-grade for the arc. Verdicts:
RATE-UNIVERSAL / RATE-SEED-DEPENDENT / INCONCLUSIVE (with the power statement that would make it
a clean FAIL of the design instead).

## 8. Explicitly out of scope

Complex-root flows (§2). ζ′/Speiser: queued, untouched until Track-0 verdicts land. The dBN
cross-flow comparison (same functional form as Phase 2's harness output or not): post-verdict,
unsealed, exploratory. The Kac–Rice waveform program and FM-index sweep: separate briefs.
The meta-process (clusters-of-clusters): blocked until this arc produces a substrate for it.

## 9. Literature status (pulled 2026-08-10, live search — not conversation recall)

Filed with exact conditionality per the row-c-suspect rule:

- **THEOREM (bulk flow, global law):** Steinerberger's nonlocal transport PDE for root density
  under differentiation, proven for compactly supported real-rooted case by **Hoskins–Kabluchko**
  ("Dynamics of zeroes under repeated differentiation," Exp. Math. 2021) — identification with
  **fractional free convolution** μ^⊞ 1/(1−s). Extensions: Hall–Ho–Jalowy–Kabluchko
  (arXiv:2312.14883, fractional differential operators z^a(d/dz)^b);
  Campbell–O'Rourke–Renfrew (IMRN 2024, arXiv:2307.11935, R-diagonal / independent-coefficient
  random polynomials, incl. CLT-type behavior as s → 1).
- **THEOREM (iid complex roots, slow-k regime):** Kabluchko–Michelen-line result
  (arXiv:2212.11867): for k ≤ log n/(5 log log n), zeros of the k-th derivative redistribute to
  the SAME seed measure μ. Global law only; regime disjoint from our s = k/n clock. Companion
  a.s. results: arXiv:2307.06788.
- **THEOREM, endpoint regime, restricted class (the strongest local-statistics statement found):**
  **"Cosine Universality"** — roots become perfectly spaced under repeated differentiation —
  conjectured by Farmer–Rhoades 2005 (arXiv:math/0310252, proven there for real entire functions
  of order 1, zeros on a line, with zero-spacing regularity hypotheses), refined by Farmer 2022,
  and **proven by Campbell–O'Rourke–Renfrew (arXiv:2410.06403, Oct 2024; v2 dated 2026-05-21)
  for even entire functions with only real roots, real on the real line** (plus Farmer's Hermite
  Universality conjecture and finite free analogs of the LLN, CLT, and Poisson limit theorem for
  deterministic polynomials under repeated differentiation — abstract verified against arXiv by
  Will 2026-08-10). This is a k → ∞ statement for entire functions — the ENDPOINT of our flow,
  not fixed s.
- **ORDER-OF-LIMITS SPLIT (the ceiling arm carries two endpoints; do not conflate the slots):**
  the s → 1 endpoint depends on which limit goes first. **Finite-n polynomial seed (Track-0's
  regime): the repeated-differentiation attractor is HERMITE** — the finite free CLT in
  2410.06403 — locally regular, globally semicircle. **n = ∞ first (entire function): the
  attractor is cosine** — perfectly spaced, globally flat. "Ceiling arm = cosine" is correct only
  in the n→∞-first regime; Track-0 lives at finite n, where **the ceiling arm is Hermite via the
  CLT** (§6.iv). The sealed rate question is unaffected — both endpoints are locally rigid, and
  the rate at which seeds approach local rigidity is exactly the open territory bracketed below.
- **OPEN AS SEARCHED (the gap our measurement sits in):** local SPACING statistics at fixed
  s ∈ (0,1) for degree-n polynomials, n → ∞. Fluctuation results exist at the linear-statistics
  level (finite free CLT line), but no gap/spacing universality theorem at fixed s was found in
  this pull. **Consequence for the seal: at fixed s there is no theorem to "confirm" — the rate
  question (§7) is genuine measurement territory, with the theorem rails at the two ends
  (global density at every s; crystalline local limit at the endpoint) serving as the floor and
  ceiling arms.** A deeper adversarial pull (someone trying to find the theorem that DOES cover
  fixed-s local statistics) is a mandatory pre-seal step — this section records a search, and a
  search is not a proof of absence. **The pull's concrete targets (Will's rider):** diff
  2410.06403 v1 → v2 (v2 is 2026-05-21, seven months of possible strengthening), and sweep the
  2025–26 papers citing it — if anyone has closed fixed-s local spacing, it will be in that
  citation graph. **Widened v1.4 (after the k-re-parameterization):** hunt specifically for
  local statistics after **o(n) derivatives** of real-rooted polynomials — transition-scale
  results, if they exist, live under that description, not under fixed-s language, which is
  presumably why the fixed-s-scoped pull did not surface them. OPEN-AS-SEARCHED must be
  re-verified against the re-parameterized question, not just the original. Also pin exact
  real-rooted statements for the k = O(1) interlacing floor (the Pemantle–Rivin / Kabluchko
  critical-points-pairing line is the complex cousin; the real-rooted citations are unpinned).

## 10. Methodological commitments carried through

Calibrator zoo first (§5c known-answer); §9 floor+ceiling guards live in the acceptance criteria
(§6.iv); null-before-prereg (TOOLKIT §10) is the document's own structure; commensurability check
before any cross-s or cross-seed comparison (same estimator, same window policy, same unfolding
convention — instrumented, not assumed); no unattributed constants (the theorem-side density is
derived live in §6.iii, never hardcoded); seed-replicate near boundaries; full per-axis sweep
capture; premise-before-mechanism (Track-0 establishes THAT the harness reads the flow before any
WHY about rates).

## 11. Deliverables

1. `derivflow/track0_harness.py` — root-space differentiation flow + per-step unfolding.
2. `derivflow/TRACK0_FINDINGS.md` — harness verdicts (§6), estimator floor per s.
3. Pre-seal literature verification note (the §9 adversarial pull), filed with exact
   conditionality.
4. `derivflow/seals/RATE_QUESTION_SEAL.json` — written only after 1–3 are green.
