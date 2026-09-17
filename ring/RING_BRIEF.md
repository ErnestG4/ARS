# ring/ — Stage 0 + Stage 1 brief (2026-09-16)

Companion to `rotational-dynamics-build-plan.md` (v5). This is the executable
scope for the first arc; the plan is the standing document.

## Superseded claims (read first; grep before citing)

**S1 — RETRACTED 2026-09-16.** *"At ε=0.1, T=2000 the spectral (−λ₁ = 1.49e-2)
and dynamic (1.57e-2) reads agree to 5%"*, cited as the cross-check paying for
itself. Made in: commit message `ff4f786` (immutable — this block is its
pointer), the Standing-invariant paragraph of this brief as of `e572593`, and
the session report of the same round. **Why wrong:** the dynamic read was
taken at a hard-coded, undeclared δ = 0.05 rad (one grid step) in a regime
where the pinning wells are anharmonic below half a step; the 5% was partly
which basin bump 0 sat in — the neighbouring basin at the same ε reads 0.65 at
that δ. The number cited as evidence of the invariant working was produced by
the constant the invariant later caught. **The check was sound; the witness
was not evidence of it.** Replaced by: δ declared and swept, banked read at
δ = 0.005, five converged witnesses within 4% (R4), the δ = 0.05 defect pinned
so it cannot return silently (R4b). Tables re-sealed at v2 (`679fc38`,
`b2b5a04`).

**S2 — CORRECTED 2026-09-16, pre-seal of the coverage test.** The bump width
carried through measure 2 ("w ≈ 0.6 rad") was the *initialisation* width. The
steady-state FWHM at (J0, J1) = (−2, 4) is **2.06 rad** (measured,
`stage1_coverage.fwhm`). Consequences: (i) P1's sealed prediction 30τ was
derived from the wrong w; with the true w, H_motion gives w/ω = 103τ, which
is the measured τ_c(A) = 100. **P1's FAIL score stands (the sealed number was
30) but the interpretation banked with it — "the scale is the period, not
bump-width/ω" — is retracted**: at this width both hypotheses predict 100τ
and only F4 separates them. (ii) The coordinate formula L + w ≥ 2π/B with
w = 2.06 says the B=4 E-clouds (spacing 1.57) are *bridged at any L*, so the
E1/E2 contrast is arc length inside the bridged regime, not the covering
condition; the q-flip result is unaffected (it is a measurement), its "built
at a coordinate" framing is weakened. (iii) F4's pre-registered widths
(−1,3)/(−4,6) span 1.33× — INAPPLICABLE by its own rule — and are swapped
pre-seal for (−6,8)/(−0.5,2.5), span 1.69×. Sealed F4 predictions unchanged:
H_cov → all three on the 100τ rung; H_motion → τ_c ∝ w, extremes on the
70 and 140 rungs.

**S3 — SUPERSEDED 2026-09-16 (coverage test).** Measure 2's P2 reading,
*"τ_c(B) = 300τ vs τ_c(A) = 100τ: the pinned ring's barcode is more
jitter-robust; PH is sensitive to pinning-modulated motion"* (banked
`064890d`, R9 pin retained as the record of what was read). **Not
replicated** on the fine ladder with new seeds: τ_c(A) = τ_c(B) = 140τ and
B's b₁ is 0.8–0.9× A's at every rung (F1). The one-rung gap was realization
noise near threshold. The residence-density mechanism proposed for it is
retired with it (F1 ratio 1.00 against a sealed [1.2, 1.7]).

**S4 — SUPERSEDED 2026-09-16 (coverage test).** Measure 2's P3 reading,
*"jitter at 10–300τ reveals E2's loop: temporal smoothing lifting a slow
arc's SNR."* Wrong mechanism. E2's base b₁ is 3.2; under jitter b₁ is 66–124
at every rung (≥21× base). A bar 20× longer than the base is **constructed,
not lifted**. The E cloud concatenates its four arcs in angular order, so any
temporal mixing across segment boundaries **converts sequence into
topology**; jitter (which wraps modulo t_max) also bridges the 4→1 boundary
and builds a stronger loop than smoothing does (F6b). This is the ladder's
construction side with a named mechanism — order-to-topology conversion —
and it is the "null that manufactures its own signal" flagged on read.

## Frame

The plan's v3 carried three defects that the ARS vocabulary names as numbered
failure modes (C1 sign inversion via rival rule; C2 collision with the banked
EC/CA3 bounded-negative; C3 an identity-map null). v4 retracted them; v5
applied six stale items after a second pass. Stage 0 is a **port**, not a
build: the verification layer at the repo root is inherited by placement in
`criticality_tool/ring/`, and the one forcing constraint — `verify_seal_order.py`
is a commit-graph property — is why this is a subdir and not a sibling repo.

Prior state on the ARS side that bounds this arc:
- **phase30** (Kuramoto → ARS): BR_artifact at every K; excluded from the zoo
  on **redundancy** with `periodic_q7` / `uniform_jitter`.
- **EC/CA3 attractor arc** (2026-05-28): attractor topology is not a
  spike-train-fingerprint property; ARS cannot resolve it per-cell by
  construction.
- **NEGATIVE_HALFLINE**: hc3-port Σ²(5)=43.1, allen-hpf 183.5 — super-Poissonian;
  Cox at 45.4 already sits on the hippocampal number.

## Structural-null audit (front-loaded)

Two analysis objects, two generative families, two right nulls:

| object | family | right null | status |
|---|---|---|---|
| per-unit spike trains off the ring | **rate-modulated (Cox)** — a unit under a passing bump is a doubly-stochastic process | matched-envelope Cox: same rate envelope, no attractor | measured at Σ²(5)=45.4; QUEUED arm |
| population-vector cloud → PH | **marginal cloud shape** — PH is order-blind | (a) di Sarra construction: independent oscillation-modulated Poisson on S¹, no recurrence; (b) pinned ring: attractor, no continuum | (a) published + code; (b) built this session at ε=0.1 |

The wrong null for both is rate-matched Poisson; it is not used anywhere in
this arc as the null of record.

## The finding from measure 1, and what it re-indexes (second pass, 2026-09-16)

**There is no ε\*.** Drift is ≈ linear in ε·T at small ε, so in the long-T
limit any ε > 0 collapses the continuum, and "the heterogeneity at which the
ring goes discrete" is a property of the network **and the observation window
jointly**. Two banked rows at the same ε=0.03 say it: 16 distinct attractors
at T=200, 4 at T=2000. The index is an **ε·T contour** (#20 on first contact).

Three upstream consequences, all applied to the plan on the branch:
1. **Stage 1's gotcha is now a measured law** citing those two rows.
2. **Stage 6 is re-posed**: gain modulates the drift coefficient; fit c(g) and
   report the surface, not "the g at which it stiffens".
3. **Stage 5 / QUEUED acquire a structural confound.** The certifier needs
   n=2000 events at rate r ⇒ T = 2000/r ⇒ contour position 2000·ε/r, fixed by
   the certifier. Window length and attractor state cannot be chosen
   independently. The QUEUED arm is **confounded by construction, not
   underpowered**; it does not leave the queue until one of the three options
   in the plan's QUEUED entry is chosen.

**Detector naming.** `ph_topology_implies_continuous_attractor` asserted the
inference Stage 1's own framing denies. Measure 2 now scores
`ph_topology_consistent_with_continuous_attractor` (marginal claim; negative
set = converged pinned-ring cloud, jittered cloud above τ_c, within-cell
scrambled cloud; nearest confusable = the pinned ring's *transient* cloud,
which traces the ring before collapse). The `implies` form stays DECLARED
through all of Stage 1 by design (`STAGE1_CANNOT_CERTIFY`); it needs Stage 3
path-lifting or zigzag. `rotational_dynamics_fit` has a real certification
path (skew_frac vs TME) and is unchanged.

**Rates carry intervals.** Sensitivity 2/2 → CP95 ≥ 0.158, specificity 3/3 →
CP95 ≥ 0.292, both UNINFORMATIVE per `boundary_rate`. The number doing the
work is the **256× margin** on λ₁ between the ε=0 floor and the nearest
confusable; the board leads with it.

**Standing invariant, and what it caught the moment it had a second witness.**
R4 runs on every row of both tables: converged rows must agree within 20%;
non-converged rows are flagged and attributed; ≥3 live witnesses required.
The contour table added long-T rows, and on the first new converged witness
(ε=0.01, T=20000) the reads were **39% apart**. A δ sweep showed the dynamic
read converging to λ₁ as δ→0 (ratio 0.965 at 0.005, 0.61 at 0.05, 0.32 at
0.1; same at T=50/200; at both ε): the pinning wells are anharmonic below
half a grid step, and δ=0.05 — one grid step — was a **hard-coded, undeclared
instrument constant**. The 5% agreement banked earlier at ε=0.1 was partly
the luck of bump 0's basin (the next basin reads 0.65 at δ=0.05). Fix: δ
declared and swept (`relax_delta_sweep`), banked read at δ=0.005, both
generators re-sealed at v2 (λ₁/drift/n_distinct bit-identical — δ enters only
the dynamic read). R4 now has **5 live witnesses**, all within 4%. R4b pins the
δ=0.05 defect (ratio must stay < 0.8 on that row) so a refactor cannot
silently restore the constant. The dynamic read's own floor is measured on the
ε=0 rows (≈6e-6 at δ=0.005; it scales ~1/δ) under a declared ceiling of 1e-4.

**c(ε·T) fitted, contour domain found (R8).** c = 2.905e-2 rad/τ per unit ε,
max residual 2.3% on 9 linear-regime rows; splits at equal P agree to 0.1–3%
(drift) and within 1 (n_distinct) at P=20, 60. **At P=200 the pre-declared
check fails (1/4/3)** because the ε=1 split deforms the bump (amp 0.710) —
the contour is perturbative, valid while the bump is undeformed. R8 asserts
that failure remains, as the domain boundary.

**Venv, declared as three capabilities** (checked against packaged wheels):
`ripser 0.6.15` + `persim 0.3.8` **installed** (barcodes with
`do_cocycles=True` from the first pass; diagram distances for the jitter
curve). `DREiMac 0.3.0` declared, install with Stage 3. Zigzag: **not GUDHI**
— the 3.13.0 Python wheel has no zigzag module or symbol; `Dionysus 2.2.3`
ships a cp312 `manylinux_2_39` wheel and host glibc is 2.39, so it installs
as a wheel when reached.

## Measure 2 — results (v2 table `e789d2c`→banked; v1 `stage1_ph` superseded, see its commit)

**Headline (the marginal-vs-dynamical result everything downstream depends on):**
the static 16-bump cloud **C reads identically to the driven ring A** — r₁₂
60.7 vs 70.7, q-invariant, b₁ 210 vs 250. PH on the population cloud cannot
tell a traversed manifold from a sampled one. The `implies` detector stays
DECLARED, now with a measured reason.

Sealed predictions, scored as declared (R9):
- **P1 FAIL.** τ_c(A) = 100τ rung (30τ predicted, ×3 allowed → ≤90). The
  scale is the rotation period (314τ), not bump-width/ω: jitter must smear
  across the circle, not one bump.
- **P2 DIVERGENCE.** τ_c(B) = 300τ vs τ_c(A) = 100τ. The pinned ring's barcode
  is *more* jitter-robust by one rung — its bump lingers in wells at 0.6×
  velocity, so smearing costs it less. PH is sensitive to pinning-modulated
  motion. Stated with its resolution: the ladder step is ×3.16 and the gap is
  exactly one rung, three seeds concordant.
- **P3 INAPPLICABLE.** E2's base r₁₂ = 2.5 < R_MIN, so there was no detection
  to destroy. Instead the loop *appears* under jitter τ_j = 10–300 (14 → 37 →
  44 → 19) and dies at 1000: jitter acts as temporal smoothing that lifts the
  SNR of a slowly traversed arc (0.0015 rad per bin vs A's 0.01). Pilot
  observation, not a prediction.
- **P4 PASS on A/B/E2** (scramble → 1.4 / 1.3 / 1.3). **C: FAIL as
  predicted** — "no-op" was wrong because the concatenated static bumps are a
  *sequence*; C dropped 60.7 → 7.7 but **kept a loop in 2/3 seeds** (b₁ 12–37%
  of base). Two surrogate defects found here and fixed in v2 (first-spike
  anchoring; edge clipping), and one **structural blind spot** that survives
  v2: a single-block unit is ISI-shuffle invariant, so the scramble only
  destroys sequence expressed as revisits. Recorded in the detector spec.
- **P5:** D = 1.09 PASS; E1 < E2 (1.06 < 2.51) PASS; **E2 ≥ R_MIN FAIL.**

**Subsetting bites exactly at the confusable.** A/B/C are q-invariant (r₁₂ >
40 at every q). E1 reads **1.06 at q=0.5 and 18.3 at q=1.0**; E2 2.5 / 18.9 /
1.2 across q=0.5/1.0/0.25. di Sarra's load-bearing preprocessing step,
reproduced with ground truth, and it flips the verdict only where the cloud is
marginal. Pinned (R9).

**Detector certified on its declared sets:** A fires (r₁₂ = 71, 24× R_MIN);
D, A-jittered-above-τ_c, A-scrambled silent. Sensitivity 1/1 (CP95 ≥ 0.025),
specificity 3/3 (CP95 ≥ 0.292) — both UNINFORMATIVE as tallies; the 24× margin
and the three silent negatives at ~1 are the numbers.

**Instrument facts:** r₁₂ = b₁/b₂ inflates when b₂ is tiny (a ratio of two
noise bars); the v1 r₁₂ = 751 was b₁ = 1230 from clip pile-up. Absolute b₁
against the base cloud is carried in every row and should gate any future
threshold alongside r₁₂.

## Coverage test + construction boundary — pre-registration (2026-09-16, before `stage1_coverage.py`)

**Claim under test (H_cov).** PH's temporal sensitivity comes entirely from
*coverage* — the residence-time density of the trajectory on the manifold —
not from motion per se. One mechanism for P1 (τ_c(A) at the period scale: the
smear must cover the circle) and P2 (the pinned ring's wells raise residence
density, so smearing costs it less). Rival H_motion: τ_c ∝ bump width / ω.

**Second question.** The jitter ladder is two-sided (P3: jitter *constructed*
E2's loop). Gaussian jitter of spike times is, in expectation, **smoothing at
τ_j plus random misassignment**. So a **smoothing-matched baseline** — the
unjittered spikes smoothed at σ = √(σ_s² + τ_j²) — separates what the ladder
constructs from what it destroys. Reported at every rung from here on.

**Arms and sealed predictions** (R_MIN = 3, r₁₂ rule as before; fine ladder
τ_j ∈ {30, 50, 70, 100, 140, 200, 300}τ; 2 emission seeds unless stated):
- **F1 fine ladder, A and B.** τ_c(A) ∈ [70, 140]; D* ≡ ω·τ_c(A) ≈ 2.0 rad.
  Under H_cov (residence density), τ_c(B)/τ_c(A) ∈ [1.2, 1.7] (B's well
  velocity is 0.6×ω̄). A ratio at ≥ 2.5 falsifies the residence account.
- **F2 speed at fixed coverage.** γ ∈ {0.01, 0.02, 0.04}, T = 3 periods each.
  H_cov: ω·τ_c = D* within ±30% (τ_c ≈ 200, 100, 50).
- **F3 coverage multiplicity at fixed speed.** γ = 0.02, rotations ∈ {1, 3, 10}.
  H_cov: τ_c unchanged within one fine rung (×1.4).
- **F4 bump width at fixed speed** — the discriminating arm. (J0, J1) ∈
  {(−2, 4), (−6, 8), (−0.5, 2.5)} at γ = 0.02 (swapped pre-seal, see S2);
  FWHM 2.06 / 1.57 / 2.65 rad. H_cov: τ_c independent of w within ×1.4 (all on
  the 100 rung); H_motion: τ_c ∝ w (extremes on the 70 and 140 rungs).
  INAPPLICABLE if the achieved widths span < 1.5× (they span 1.69×).
- **F5 the C residual as a coverage statement.** C1 (one sweep, one block per
  unit) vs C3 (three sweeps, three blocks per unit), scrambled, 3 seeds.
  H_cov: C1 keeps a loop in ≥1 seed (as banked); C3's median r₁₂ < R_MIN.
  This is item (b) — the scramble's power as visits-per-unit — measured.
- **F6 construction boundary.** σ_s ∈ {0.5, 1, 2, 5, 10, 20, 50, 100}τ, no
  jitter, on A and E2. E2 crosses R_MIN somewhere in [5, 50]τ (the
  construction regime exists and has a lower edge); A stays above R_MIN until
  σ_c(A) ∈ [70, 200]τ. **F6b smoothing-matched ladder** on A, B, E2: on E2 the
  jittered r₁₂ at τ_j = 30–100 is within ×2 of the smoothing-matched base
  (what jitter constructed is smoothing); on A at τ_j ≥ τ_c the jittered b₁ is
  < 0.5× the matched b₁ (destruction beyond smoothing).

## Coverage test — results (`stage1_coverage_measured.json`, sealed `1fb6d07`)

**H_cov confirmed; H_motion falsified (F4, the discriminating arm).** Bump
widths 1.57 / 2.06 / 2.65 rad (1.69× span) all give τ_c = 140τ, and the
destruction *fraction* b₁/b₁(base) is the same at every rung across widths
(0.27 / 0.30 / 0.32 at 70τ). H_motion predicted the extremes on the 70 and
140 rungs; they landed on the same rung. **F2:** ω·τ_c = 3.0 / 2.8 / 2.8 rad
across a 4× speed range (sealed ±30%; measured ±7%). **F3:** rotations
1 / 3 / 10 give identical b₁ curves (188 / 204 / 208 at 30τ; 18.5 / 18.9 /
19.0 at 100τ). **The single claim:** PH's jitter sensitivity is set by
**angular displacement over τ_j alone** — ω·τ_c ≈ 2.8 rad (0.45 of the
circle), b₁ half-life at ω·τ ≈ 1.1 rad — independent of bump width,
coverage multiplicity, and pinning. It accounts for P1 (with the true w both
hypotheses gave 100τ; F4 breaks the tie for coverage) and for the *absence*
of P2 (S3). The τ ladder now has a predicted scale: τ_c ≈ 2.8/ω.

**F1:** τ_c(A) = 140τ PASS [70, 140] (edge); ratio τ_c(B)/τ_c(A) = 1.00 FAIL
[1.2, 1.7] → S3. **F5 PASS:** C1 (one block per unit) keeps a loop under
scramble in 3/3 seeds (r₁₂ 6.7–9.2, b₁ 43–55); C3 (three blocks) dies
(median 1.22, b₁ 15–19). **The scramble's power is visits-per-unit, measured.**

**F6 / F6b — the construction boundary, and the statistic that couldn't see it.**
On E2 the smoothing-only loop crosses R_MIN at σ = 2–5τ (sealed lower edge
[5, 50]: FAIL at the low end) and r₁₂ is valid only to σ ≈ 10 — beyond that
b₂ → 0 and the ratio reads 0 or 10¹²–10¹⁴. **r₁₂ = b₁/b₂ is scale-free:**
smoothing shrinks b₁ and b₂ together, so A's r₁₂ *rises* with σ (69 → 175)
while its b₁ falls 255 → 34. r₁₂ is retired for any smoothed or matched
cloud; the **b₁ half-life** is the estimator that survives. On b₁: E2's
jittered loop (66–124) exceeds the smoothing-matched one (0–55) — jitter
constructs more than smoothing because it wraps (S4). On A at τ_c the
jittered b₁ is 0.56× the matched b₁ (sealed < 0.5: FAIL, narrowly):
destruction is mostly displacement along the trajectory, which smoothing
shares, not misassignment.

**What this changes for the ladder as a null.** A jitter ladder on a cloud
whose time-order encodes the manifold's order is two-sided: below ~2.8/ω it
destroys by displacement; on order-concatenated clouds it constructs by
bridging. The `detector_spec` for any ladder-based claim now needs (i) the
predicted τ_c = 2.8/ω stated before the run, and (ii) a statement of whether
the cloud's time-order carries the manifold's order (a sequence), because
that is the condition under which the null manufactures the signal.

## Goals

1. **Stage 0 port.** Every detector the arc will report is declared in
   `detectors.py` with its negative set and nearest confusable before it is
   built; the board (`verify_ring.py`) refuses a declared-only detector that
   reads as certified. Torch is guarded and the guard is tested.
2. **Stage 1, measure 1 — marginal stability along the ring, and where the
   heterogeneity dial destroys it.** Banked table over ε × T with the ε=0 row as
   the instrument floor.
3. **Stage 1, measure 2 — PH H₁ rank 1 on the population cloud**, through the
   jitter ladder, the within-cell ISI-order scramble, and the subsetting sweep.
   Scores `ph_topology_consistent_with_continuous_attractor` only. **Done**
   (results above).

## Measure 2 — pre-registration (2026-09-16, before `stage1_ph.py` runs)

**Traversal.** A stationary ε=0 ring has no dynamics along the ring, so a
jitter ladder on it is inert (every arm must be able to fire). The positive
cloud therefore uses Zhang's odd coupling, `W += γ·J1·sin(Δθ)/N`, which
rotates the bump at **ω = γ rad/τ** exactly (calibrated: 2.000e-2 at γ=0.02,
ε=0; 4.9997e-2 at 0.05). At ε=0.1 the drive beats pinning (c·ε = 2.9e-3 ≪ ω)
with instantaneous velocity modulated to 0.6× in the wells.

**Clouds (2×2 plus the coordinate):** A intact driven (ε=0, γ=0.02) —
positive; B pinned driven (ε=0.1, γ=0.02) — attractor with wells, still
traces the ring; C intact undriven (ε=0, γ=0) — 16 static bumps, topology
from sampling not dynamics; D pinned undriven converged (ε=0.1, γ=0,
pre-relaxed 2000τ) — the declared negative, 3 clusters; **E pinned undriven
transient at a chosen contour distance:** ε=0.1, relax 100τ, then sample a
window W. With c known, 16 arcs of length L = c·ε·W cover the circle when
L ≥ 2π/16 = 0.39 rad, i.e. **W ≥ 135τ**. E1 samples W=50τ (L = 0.15, gaps
predicted → H₁ weak); E2 samples W=200τ (L = 0.58, covered → H₁ rank 1).
The confusable is now built at a coordinate, not sampled and hoped over.

**Pipeline.** Poisson spikes at ρ=50 spikes/τ per unit rate; bins Δ=0.5τ;
Gaussian smoothing σ_s=1τ; subsetting by top-q population activity, q ∈
{1.0, 0.5, 0.25}; ≤600 points to ripser (H₁, cocycles on); statistic
**r₁₂ = longest H₁ bar / second longest**; detector fires at r₁₂ > R_MIN = 3.
Bottleneck distance to the unperturbed diagram (persim) along the ladder.
3 emission seeds; median and range reported.

**Jitter ladder** τ_j ∈ {0.1, 0.3, 1, 3, 10, 30, 100}τ; τ_c = first rung with
median r₁₂ < R_MIN. **Within-cell ISI-order scramble** on A, B, C, E2.

**Predictions, sealed:**
- P1 τ_c(A) ≈ bump width / ω ≈ 0.6/0.02 = **30τ** (within a factor 3, i.e. the
  30τ rung or a neighbour).
- P2 **ladder scale vs contour scale.** For B the drift timescale is 1/(c·ε) =
  345τ and the traversal timescale w/ω = 30τ — a factor 10 apart. τ_c(B) on
  the same rung as τ_c(A) ⇒ PH reads the traversal; τ_c(B) ≥ the 100τ rung ⇒
  PH reads the drift. Either is informative.
- P3 For E2 the only motion is drift: τ_c(E2) ≈ w/(c·ε) ≈ **200τ** (≥ the
  100τ rung).
- P4 Scramble kills A, B, E2 (r₁₂ → ~1); on C it is a **no-op in
  distribution** (stationary rates) — that arm is INAPPLICABLE on C and is
  reported so, never as a pass.
- P5 D: r₁₂ ≈ 1 (H₁ absent). E1 < E2 on r₁₂.

**Pre-seal pilot amendment (one seed, A/D/E; disclosed before sealing).**
(i) τ_c(A) under the R_MIN=3 rule was censored at the top rung (r₁₂ = 5.1 at
τ_j = 100): the ladder range is extended to {…, 300, 1000}τ; **P1 is kept as
sealed (30τ) and scored as written** — the pilot suggests the true scale is
~period/2 ≈ 157τ (jitter must smear across the whole circle, not one bump
width), which is a pilot observation, not a prediction. (ii) **The first form of
the coordinate was wrong**: E1 read 28.8 > E2 23.6. The covering condition is
**L + w ≥ 2π/B** with w the bump width as the Rips metric resolution, not
L ≥ 2π/B; at B=16 the 0.39-rad spacing is under the 0.6-rad width and gaps are
bridged at any L. E is rebuilt with **B_E = 4** (spacing 1.57 rad), W ∈ {100,
400}τ: L = 0.29 rad leaves a 0.68-rad gap (E1, H₁ predicted absent); L = 1.16
rad covers (E2, H₁ rank 1). **P5 is re-sealed against this design.** The
coordinate survives; its formula acquired the term the pilot showed it was
missing. (iii) P3's τ_c(E2) is now against the B=4 cloud; prediction unchanged
in form (w/(c·ε) ≈ 200τ).

**Detector scoring** (`ph_topology_consistent_with_continuous_attractor`):
positive `intact_ring_cloud` = A at q=0.5; negatives `pinned_ring_cloud_converged`
= D, `jittered_cloud_above_tau_c` = A at τ_j=100, `within_cell_scrambled_cloud`
= A scrambled. E is not in either set — it is expected to FIRE, which is what
"consistent with" means and why the `implies` detector stays DECLARED.

## Methodology

- Model: Ben-Yishai ring, N=128, `W = (J0 + J1 cos Δθ)/N`, J0=−2, J1=4, I0=1,
  smooth gain `β·softplus(u/β)`, β=0.1. **Threshold-linear was rejected for the
  instrument**: its fixed-point Jacobian is one-sided at the active-set edge
  and read λ₁ = ±1.7e-3 for a bump that did not move in 200τ (drift 1e-15).
- Dial: fixed per-unit input bias `ε·ξᵢ`, ξ ~ N(0,1) seed 1;
  ε ∈ {0, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1}; T ∈ {200, 2000}τ; B=16 bumps
  per batch at **off-grid** starting angles (on-grid starts sit on exact
  symmetry points and never see pinning).
- Reads: λ₁, λ₂ (Jacobian spectrum); `relax_rate` (displace the bump 0.05 rad,
  integrate 50τ, log-ratio — no linearisation); `n_distinct` final positions;
  `drift_median`; `resid_max` (is it a fixed point).
- Instrument sealed via `modelparams.Model` in each generator (v2): 3 TESTED
  (ε or P, T, `relax_delta_sweep`), 9 DECLARED.
- Generator-before-output via `sealgen.sh`; outcome claims only with CHECKRUN lines.

## Acceptance criteria (board rows R0–R7 in `verify_ring.py`)

- **PASS**: all eight rows green — guard real; specs construct; floor at
  |λ₁|<1e-12, drift<1e-9; λ₁ strictly decreasing with ε; ε=0.1 row converged
  (resid<1e-8) and collapsed (n_distinct ≤ B/2); spectral/dynamic agree within
  20% on **every** converged row above the floor at the smallest declared δ,
  ≥3 such witnesses (R4; was "the converged row", singular — see S1);
  n_distinct differs across T at some ε; built
  detector two-sided-correct with the nearest confusable silent by >10×.
- **SOFT PASS**: R5 (T-dependence) is the only red — the sweep is too short to
  show it; extend T, do not lower the bar.
- **FAIL**: R6 red — the detector fires on the weakly pinned ring, or the
  confusable is silent only via the convergence gate and not via λ₁. That is a
  one-sided calibration and the threshold is redrawn against the table, never
  the other way.

## Out of scope this session

Stage 2+; spikes off the ring into ARS and the QUEUED ring→ARS
instrument bound; any population-level claim.

## Deliverables

1. `rotational-dynamics-build-plan.md` v5.
2. `__init__.py` (guarded torch), `ringnet.py`, `detectors.py`, `verify_ring.py`.
3. `stage1_marginal.py` (sealed generator, v2) → `stage1_marginal_measured.json`;
   `stage1_contour.py` (sealed, v2) → `stage1_contour_measured.json`.
4. This brief; RESULTS.md §7.ter row deferred until measure 2 lands (one
   commit per phase convention).

## Open questions carried forward

- QUEUED arm: **(b) chosen** — long-range certification dropped, matched-Cox +
  `wigner_renewal` kept, deliverable re-sealed as the per-cell detection
  margin vs the dial; bank where the margin crosses the floor. (Plan, QUEUED.)
- ~~c(ε·T) fit before measure 2~~ — done. ~~Measure 2~~ — done.
- **Next:** (a) the E-cloud SNR question — smoothing σ_s vs traversal speed is
  an undeclared coupling (jitter at 10–300τ revealed E2's loop); sweep σ_s as
  a TESTED param before any E verdict is read; (b) the scramble's power as a
  visits-per-unit statement, computed per cloud; (c) Stage 2.
- Per-basin λ₁ spread: at ε=0.1 the three pinned basins have λ₁ = 1.28e-2 /
  1.49e-2 / 1.53e-2; the tables bank the median, min and max. If Stage 6 needs
  per-basin curvature, the column exists.
- Where the QUEUED arm's "which calibrator is each dial setting redundant with"
  column is computed — `extractor_distinctness` machinery or a new panel.
