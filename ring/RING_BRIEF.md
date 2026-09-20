# ring/ — arc brief: Stages 0–4b, 3a–3h, T1–T3 (2026-09-16 → 2026-09-20)

Companion to `rotational-dynamics-build-plan.md` (v5). This is the executable
record of the first arc — pre-registrations, results, and retractions in
order; the plan is the standing document. Board rows R0–R18 in
`verify_ring.py` score it. Stage 5 (spiking ring) is the next unrun stage.

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
δ = 0.005, three distinct converged witnesses within 4% (R4; five rows, two
of them the same fixed point read in both tables), the δ = 0.05 defect pinned
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

**S5 — RETRACTED 2026-09-20 (Stage 3h).** Stage 3e's *"the trapped failures
have one cause … at 0.1 rad the δ-sweep measured a restoring ratio of 0.32.
The anharmonic well, through a third instrument"* (banked `8164091`, R17's
message as of `bf1828e`, plan v5's Stage 3e line). **Why wrong:** the 0.32
was in no table when cited; banked (Stage 1 tables v3, δ = 0.1 column) it
belongs to the **ε = 0.01, T = 20000** rows, a different ε and a different
well. Stage 3h then swept the MSD arm's *own* well (ε = 0.1, start 0.37, the
exact trapped state): ratio **0.99 / 1.01** at δ = 0.1 (T = 50 / 200τ),
1.03 at 0.05, 0.75 only at 0.2 rad — **harmonic** at the 0.1-rad excursion
noise drives. The sealed H_anharm window [0.15, 0.45] is missed by 2×; H_harm
fires. The trapped clauses' common factor λ_eff/λ₁ = 0.19–0.35 has **no
explanation banked**; candidates pre-named in the Stage 3h seal, (a)
disfavoured, (b) noisy-bump effective potential and (c) the 20-segment
crossover estimator open. What survives of Stage 3e: the kind-level
separation (continuum ~1 / trapped saturating / IND_u flat, 9/9 rows), D,
and "not certified at sealed precision". What Stage 3h *does* confirm: the
**I1c well (ε = 0.03)** is anharmonic — ratio 0.22 at 0.1 rad, 0.084 at
0.2 rad — and λ₁ × 0.084 = 3.2·10⁻⁴ reproduces I1c's measured λ_eff =
3.3·10⁻⁴ to 5%. I1c's failed clause is anharmonicity at a 0.3-rad kick,
quantitatively; the *MSD arm's* is not. One mechanism was carried across two
wells; it holds in one.

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
the dynamic read). R4 now has **5 live rows = 3 distinct converged states**
(ε = 0.1, 1.0, 0.01; the ε = 0.1 fixed point appears in both tables and at
two T), all within 4%. R4b pins the
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
curve). `DREiMac 0.3.0` **installed** with Stage 3 (path-lifting, L1–L4b).
Zigzag: **not GUDHI** — the 3.13.0 Python wheel has no zigzag module or
symbol; `Dionysus 2.2.3` **installed** 2026-09-17 (zigzag present; unused so
far — Stage 3a found the lift's ceiling before zigzag was needed).

## Measure 2 — results (v2 table `e789d2c`→banked; v1 `stage1_ph` superseded, see its commit)

**Headline (the marginal-vs-dynamical result everything downstream depends on):**
the static 16-bump cloud **C reads identically to the driven ring A** — r₁₂
60.7 vs 70.7, q-invariant, b₁ 210 vs 250. PH on the population cloud cannot
tell a traversed manifold from a sampled one. The `implies` detector stays
DECLARED, now with a measured reason.

Sealed predictions, scored as declared (R9):
- **P1 FAIL.** τ_c(A) = 100τ rung (30τ predicted, ×3 allowed → ≤90). ~~The
  scale is the rotation period (314τ), not bump-width/ω: jitter must smear
  across the circle, not one bump.~~ *[S2: the 30τ used the initialisation
  width; at the true FWHM 2.06 rad both hypotheses give ~100τ, and only F4
  separates them — H_cov won, H_motion FAIL.]*
- **P2 DIVERGENCE** *[S3 — SUPERSEDED: not replicated on the fine ladder,
  τ_c(A) = τ_c(B) = 140τ (F1); the reading below is the record of what the
  coarse table showed]*. ~~τ_c(B) = 300τ vs τ_c(A) = 100τ. The pinned ring's
  barcode is *more* jitter-robust by one rung — its bump lingers in wells at
  0.6× velocity, so smearing costs it less. PH is sensitive to
  pinning-modulated motion.~~ Stated with its resolution: the ladder step is
  ×3.16 and the gap is exactly one rung, three seeds concordant — which is
  the resolution at which it then failed to replicate.
- **P3 INAPPLICABLE.** E2's base r₁₂ = 2.5 < R_MIN, so there was no detection
  to destroy. Instead the loop *appears* under jitter τ_j = 10–300 (14 → 37 →
  44 → 19) and dies at 1000: ~~jitter acts as temporal smoothing that lifts
  the SNR of a slowly traversed arc (0.0015 rad per bin vs A's 0.01).~~ *[S4:
  wrong mechanism — the loop is CONSTRUCTED (b₁ ≥ 21× base), order-to-topology
  conversion across E's segment boundaries; F6b.]* Pilot observation, not a
  prediction.
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
constructs more than smoothing because it wraps (S4). On A at τ_c(A) = 140τ
the jittered b₁ is **0.91×** the matched b₁ (sealed < 0.5: FAIL, and not
narrowly — the 0.56 first written here was read at the 100 rung the brief
had guessed pre-seal, not at the rung F1 measured; R10 now reads it at
τ_c(A)): destruction is mostly displacement along the trajectory, which
smoothing shares, not misassignment.

**What this changes for the ladder as a null.** A jitter ladder on a cloud
whose time-order encodes the manifold's order is two-sided: below ~2.8/ω it
destroys by displacement; on order-concatenated clouds it constructs by
bridging. The `detector_spec` for any ladder-based claim now needs (i) the
predicted τ_c = 2.8/ω stated before the run, and (ii) a statement of whether
the cloud's time-order carries the manifold's order (a sequence), because
that is the condition under which the null manufactures the signal.

## Stage 2 — non-normality: pre-registration (2026-09-17, before `stage2_nonnormal.py`)

**Premise under test.** The plan's Stage 2 premise is *"dropping symmetry is
what creates non-normality."* Pilot (one row each, disclosed): the symmetric
ring attractor's bump Jacobian J = −I + D·W is already non-normal with **zero
asymmetry** — Henrici 2.09 (18% of ‖J‖_F), numerical abscissa +0.178 against
spectral 0, G_max = 1.36. The source is the gain profile D = diag(f′(u)) across
the bump. The circulant odd coupling is normal at every γ (linear rail:
Henrici 5e-15). So the hypotheses are about **order**, and a 64× span in γ
separates exponent 1 from exponent 2 by a factor of 64 in the relative change:

- **H_plan:** asymmetry creates non-normality — Henrici(γ)/H₀ − 1 ∝ γ¹ and is
  large (≥ 50% at γ = 0.32).
- **H_gain:** non-normality is set by the gain profile; asymmetry enters at
  second order — exponent 2 ± 0.3 over γ ∈ {0.005, 0.02, 0.08, 0.32}, and
  < 10% at γ = 0.32.

**Instrument.** For γ > 0 the bump is a traveling wave, so the lab-frame
instantaneous Jacobian is not a fixed-point linearization (pilot: spectral
abscissa +0.016 at γ = 0.02, ε = 0.1 → G_max 10⁷, meaningless). Stage 2 uses the
**co-moving-frame Jacobian** J_tw = −I + D·W + γ·∂_θ (central-difference
circular derivative), which has an exact translation zero mode r₀′ — asserted
as a rail: ‖J_tw r₀′‖/‖r₀′‖ < 1e-2. Reads per row: Henrici index (strictly
upper part of the Schur form, Frobenius); spectral abscissa α(J); numerical
abscissa ω(J) = λ_max((J+Jᵀ)/2); G_max = sup_t ‖e^{Jt}‖₂ on t ∈ [0.1, 1000]τ
(60 log points); eigenvalue condition number κ of the top eigenvalue;
Kreiss constant K on a grid Re z ∈ [1e-4, 3], Im z ∈ [−1, 1]. Threads pinned.

**Rails (theorem-level; a red rail is an instrument defect, not a finding):**
linear stable circulant (J1 = 1) at every γ: Henrici < 1e-10, ω − α < 1e-10,
G_max = 1 ± 1e-6, K = 1 ± 1e-3. On every row: ω(J) > α(J) ⟺ G_max > 1;
K ≤ G_max ≤ e·N·K (Kreiss); for a marginal row G_max ≥ κ(0).

**Arms and sealed predictions:**
- **S0** symmetric bump (γ = 0, ε = 0): H₀, Δ₀ = ω − α, G₀, κ₀ — banked as
  the *baseline non-normality of a symmetric attractor*. Expected H₀ ≈ 2.1,
  G₀ ≈ 1.36 (pilot). No prediction sealed beyond "Δ₀ > 0" (transient growth
  with zero asymmetry).
- **Sγ** J_tw at γ ∈ {0.005, 0.02, 0.08, 0.32}, ε = 0: exponent of
  Henrici(γ)/H₀ − 1 → H_plan vs H_gain as above. Also G_max(γ)/G₀.
- **Sα** random antisymmetric perturbation of W at ‖ΔW‖_F **matched** to each
  γ (commensurable): exponent of Henrici/H₀ − 1; ratio
  Henrici_rand/Henrici_circ − 1 at the largest matched norm. Sealed
  two-sided: H_struct (< 0.5, structured asymmetry is the gentler source),
  H_comparable (0.5–2), H_inv (> 2). Pilot hints ≈ 0.45; sealed anyway.
- **Sε** heterogeneity at γ = 0, ε ∈ {1e-3, 3e-3, 1e-2, 3e-2, 1e-1} (100×):
  H_pin: G_max(ε) decreases monotonically from κ₀ (pinning turns the
  persistent projector norm into a true transient); H_plan: increases. And
  the exponent of |G_max(ε) − G₀|.

**The discriminating spans:** 64× in γ and matched α (exponent 1 vs 2);
100× in ε (sign and exponent). Single points decide nothing here.

## Stage 2 — results (`stage2_nonnormal_measured.json`, v3 sealed `96a1116`; v1/v2 superseded, red rails)

**Headline: the plan's premise is falsified for this network.** "Dropping
symmetry is what creates non-normality" — no. The **symmetric** ring
attractor's linearisation is already non-normal: Henrici index 2.086 (18% of
‖J‖_F), numerical abscissa 0.178 above the spectral abscissa, G₀ = κ₀ = K₀ =
1.356 (on the marginal row the three coincide exactly — the Kreiss identities
as rails). The source is the gain profile D = diag(f′(u)) of the attractor
state. Then, on every row the rails let us read:
- **circulant asymmetry** (co-moving frame, γ over 16×: 0.005–0.08) moves
  Henrici by ≤ 0.14% — H_plan (first order, ≥ 12% at γ = 0.08) **falsified**
  by ~90×; H_gain's magnitude clause passes; the exponent reads 2.00 on three
  points but none is individually resolved above 3× its declared error bound
  (5.5 × zero-mode residual), so the exponent is **provisional**. γ = 0.32 is
  instrument-limited (zero-mode residual 1.5e-2 at a one-grid-point bump
  edge) and not read.
- **random asymmetry at matched ‖ΔW‖_F** (three read rows, converged to
  |F| < 1e-9 with T up to 182,000τ) moves Henrici by ≤ 0.09%; rand/circ at the
  largest read norm = 0.69 → **H_comparable**. The row matched to γ = 0.32
  did not converge in a 2·10⁵τ budget (G_max 11.8 off a non-fixed-point: the
  garbage the rail exists to catch) — not read.
- **heterogeneity** (100× in ε, all five rows converged): Henrici moves
  ≤ 0.19% and non-monotonically; **G_max decreases monotonically** 1.3542 →
  1.2740 from G₀ = 1.3557, exponent 0.86 in ε — **H_pin PASS, H_plan FAIL**.
  κ rises slightly (1.3558 → 1.3643) while G_max falls: pinning converts the
  marginal mode's *persistent* amplification (G = κ) into a *transient* one
  (G < κ) that shrinks ~linearly in ε.
- The numerical–spectral gap is **0.178 on every read row** (γ, α, ε alike):
  the initial growth rate is a property of the gain profile that no
  perturbation in the sweep touches.

**Instrument record (three rails were red in v1, one in v2; all fixed, none
interpreted around):** (i) G_max and Kreiss read their *grids* on the linear
rail (0.951, 0.864) — t = 0 and Re z → ∞ excluded; (ii) central-difference
∂_θ left a co-moving zero-mode residual ≈ 4γ because the softplus edge is one
grid point wide — spectral derivative cuts it 2500×; (iii) three ε rows were
linearised at non-fixed-points (Stage 1's lesson, re-learned): Newton *and*
Levenberg–Marquardt both fail here because the fixed point is far along the
near-flat ring direction and the landscape is anharmonic below half a grid
step (the δ finding again) — integrate-to-convergence with a budget and an
INSTRUMENT-LIMITED flag is the honest instrument. Every row carries a Henrici
error bound and a `resolved` flag; the Sγ exponent is reported provisional
because of it.

**What Stage 2 gives the plan.** Schur/Henrici/pseudospectra/G_max are all
built and railed; the α sweep the plan asked for is answered with spans
rather than points, and the answer is that the interesting non-normality was
in the symmetric attractor all along. The open question (Clark's
above-capacity slow regions vs SHC saddle-lingering) is untouched; Stage 7
would be where it lives.

## Named rail class: BOUNDARY-SUPPORTED SIGNAL (three instances, one defect)

A statistic taken over a discretized continuum whose signal lives on a
boundary or a measure-zero set. Two forms, one rule:
- **B-sup** — a supremum attained at an edge the grid excludes: G_max at
  t → 0 and the Kreiss constant at Re z → ∞ (Stage 2, read 0.951 / 0.864 on a
  normal matrix); the jitter ladder's τ_c on its top rung; σ censored at 100;
  the smallest readable ρ (Stage 3a); Stage 4's rotation number, a limit
  N → ∞ read at finite N.
- **B-avg** — an average over the continuum whose signal is supported on
  isolated points: per-step continuity on C_perm read 0.998 because the
  signal was 15 jump boundaries in 2000 steps, and the average could not see
  them (Stage 3a).
**Rule:** before banking any sup or average over a continuum, state where the
signal is supported. A sup at an excluded edge is reported **CENSORED**, never
as a value. An average with boundary-supported signal is replaced by a
statistic that counts or measures the boundary events (total variation,
jump count), never by a finer average.

## Two doctrines from Stage 3a, banked as rules

**Topological protection, the sharper form.** The claim was posed as a window
— θ visibly corrupted, n intact. That presupposed graceful degradation, and
the degradation is not graceful. With a cohomological instrument **the
integer never errs; it becomes undefined**: in every readable row |n| was
exact (9/9), and below the censored ρ edge the class is gone, not the count
drifting. That is what "topologically protected" looks like in practice, and
it is the stronger statement of the original claim.

**A library's graceful-degradation path is a null-laundering channel unless
it is opt-in with its own detector spec** (failure mode #16 in *substituted*
form: not a floored estimator, a silently swapped one). DREiMac's
`standard_range=False` reported a different, worse class as if it were a
reading, wrong in 14/15 rows. This is the default design in most scientific
libraries. Rule: every fallback path a library takes on its own is treated as
UNREADABLE unless the fallback has been given its own negative set.

## Stage 3a — path-lifting: pre-registration (2026-09-17, before `stage3_lift.py`)

**What the instrument can and cannot certify — stated first.** Persistent
cohomology → circular coordinate → lift to the universal cover (DREiMac
`CircularCoords`, Yao & Yoon 2025) certifies that the population state
**moves continuously along the manifold with a well-defined winding count**:
a *kinematic* claim. It cannot by itself certify an *attractor*: an
independent-unit construction that follows the same trajectory (di Sarra's
route) lifts just as smoothly. So the detector ladder acquires a third rung —
`consistent_with` (marginal) → **`with_continuous_traversal`** (kinematic,
this stage) → `implies_continuous_attractor` (dynamical) — and the dynamical
rung's candidate instrument is L4 below. `implies` stays DECLARED until L4 is
scored on a declared negative set.

**Invariants under the lift's ambiguity, stated before running.** The
circular coordinate is defined up to orientation, offset, and a monotone
reparametrization of the circle; if the selected cocycle is a k-multiple of
the generator, windings scale by k. Therefore: (i) the **integer |n|** is the
invariant (predicted k = 1 from DREiMac's longest-bar class; k ≠ 1 would show
as |n_est| = k·n_true and is checked); (ii) the orientation sign is *reported,
not predicted*; (iii) θ is compared only after removing a low-order periodic
distortion (Fourier order ≤ 3 in the true angle) — pilot: an affine-only fit
leaves 0.28 rad at ρ = 50 and 0.056 at ρ = 5, which is reparametrization, not
noise; (iv) the offset is arbitrary.

**Reference states.** All Stage 3a clouds are traveling waves or
constructions; no converged fixed point is needed, so the rail-(iii)
pathology does not arise here. Where L4 adds input noise the bump diffuses;
that is the object, not a convergence failure. Budgeted anyway: any arm that
does need a fixed point uses `converge()` with the 2·10⁵τ budget and the
INSTRUMENT-LIMITED flag.

**Arms and sealed predictions** (ρ in spikes/τ per unit rate; bin 0.5τ,
σ_s 1τ unless stated; 3 emission seeds):
- **L1 readout.** A (driven ring, ω = 0.02, 3.18 rotations) at ρ = 50:
  |n_est| = n_true = 3 in 3/3 seeds; θ noise residual < 0.1 rad RMS after the
  order-3 reparametrization fit; k = 1.
- **L2 protection.** ρ ∈ {50, 15, 5, 1.5, 0.5} on A. θ noise residual scales
  as ρ^(−0.5 ± 0.15) over the readable ρ (Poisson counting). |n| exact at
  every readable ρ. The smallest readable ρ is the instrument's edge and is
  reported **censored**. The claim "n survives noise that visibly corrupts θ"
  PASSES if some readable ρ has θ residual > 0.3 rad and |n| exact, FAILS if
  |n| breaks at a ρ where θ residual < 0.3 rad, and is **NOT REACHED** if the
  coordinate becomes unreadable before θ reaches 0.3 rad — the pilot suggests
  the last. A second bin width, 0.1τ, is swept on A to push θ noise up before
  the coordinate fails.
- **L3 the traversal detector across clouds** at ρ = 50: continuity = fraction
  of steps with |Δφ| < π/4, and |n|. A: continuity > 0.95, |n| = 3. **IND**
  (independent Poisson units with the ring's own bump profile as tuning,
  following A's trajectory ψ(t), no recurrence): **the same** — continuity
  > 0.95, |n| = 3: the kinematic ceiling, measured. C_ord (16 static bumps in
  angular order): continuity > 0.95 and **wind_est within 0.15 of 0.94** — it
  *is* a stepwise traversal of 15/16 of the circle and is read as one,
  correctly. *(Amended pre-seal: the first draft said |n| = 1; the 16 bumps
  at (k+0.37)·2π/16 cover 0.94 turns, so |n| = 0 under the floor convention
  by construction. The fractional winding is the honest read.)* C_perm (random
  segment order, 3 permutations):
  continuity < 0.5, and the lift is ill-defined (a majority of steps > π/2).
- **L4 the attractor rung, pilot with a sealed prediction.** Ring A_n with
  declared additive input noise σ_n = 0.05 per unit per step (the bump now
  diffuses along the marginal mode and relaxes transversely at λ₂ = −0.55),
  and IND_n built on **A_n's own noisy trajectory** — kinematics identical by
  construction; the only difference is transverse dynamics. Bin 0.1τ,
  σ_s 0.2τ. Decompose fluctuations about the fitted manifold curve m(φ) into
  transverse residuals; measure their autocorrelation time τ_tr. Prediction:
  τ_tr(A_n) ≈ 1/0.55 ≈ 1.8τ; τ_tr(IND_n) ≈ the smoothing floor (~0.3τ);
  **τ_tr(A_n) > 2 × τ_tr(IND_n)** in 3/3 seeds. If this holds, it is the
  instrument that separates an attractor from an input-driven look-alike; the
  `implies` detector's negative set then gets IND_n as its nearest
  confusable with a number attached.

## Stage 3a — results (`stage3_lift_measured.json`, sealed `9fd594c`)

**The (n, θ) readout works, and its invariants behaved as stated.** L1 PASS:
|n| = 3 = n_true in 9/9 readable seeds across ρ = 50/15/5, k = 0.97–1.00 (the
longest-bar class is the generator), orientation sign random across seeds
(reported, not predicted: −,+,−), θ residual 0.016–0.041 rad after the order-3
reparametrization — an affine-only comparison would have said 0.11–0.31 rad,
which was reparametrization, not noise.

**L2 — the protection claim is NOT REACHED (sealed third option).** There is
no regime in which θ is visibly corrupted and n survives: the instrument fails
*wholesale*. Below the smallest readable ρ (5 at bin 0.5, 15 at bin 0.1 —
**censored edges**, rail class (i)) the standard-range cohomology class is
gone; DREiMac's nonstandard-range fallback still emits coordinates, and its
counts are **wrong in 14/15 rows** (θ 0.9–1.9 rad). A fallback that emits
numbers where the instrument has nothing is a null being laundered; the rule
from here: no standard-range class ⇒ UNREADABLE, never a count. The ρ^(−½)
law also FAILS: θ residual is flat (0.020–0.030 rad) over 10× in ρ,
floor-limited by the reparametrization model, not by counting noise.

**L3 — the kinematic ceiling, measured.** IND (independent tuned Poisson
units on A's own trajectory, no recurrence) reads identically to A: |n| = 3,
continuity 1.000, 3/3. Path-lifting certifies *traversal*, not *attractor*.
C_ord PASS (wind 0.97 vs 0.94). **C_perm's sealed prediction FAILED**:
per-step continuity 0.998, because 15 segment boundaries in 2000 steps
cannot move a per-step fraction and σ_s = 1τ smooths each jump into a fast
sweep. The traversal statistic must see the *jumps*, not the steps: total
variation / net winding of the lifted path is the candidate, to be sealed
before scored. The traversal rung is registered DECLARED
(`ph_topology_with_continuous_traversal`).

**L4 — FAIL, and the ceiling says why.** τ_tr(A_n)/τ_tr(IND_n) = 0.91, 1.12,
1.09 — both at the smoothing floor (0.4τ). A rate-level probe with no spike
noise (not banked; one seed): A_n 1.04τ vs IND_n 1.16τ at bin 0.1, 1.02 vs
1.18 at bin 0.05 — **no separation at the ceiling either**, and IND_n, which
has no transverse fluctuations by construction, reads > 1τ. The 32-bin
manifold estimate leaves within-bin *along*-manifold motion (the bump crosses
a φ-bin in ~10τ) in the "transverse" residual. Instrument, not SNR. **L4b**:
tangent-projected residual (remove the component along dm/dφ), a finer
manifold model, and the rate-level check *first* as the instrument's own
ceiling. The `implies` rung stays DECLARED; IND_n is its nearest confusable
with the kinematics matched by construction, which is what the arm was for.

**What Stage 3a closes and what it doesn't.** The count survives the lift's
ambiguity (integer |n|, k = 1) and reads exactly wherever a coordinate exists;
the gap between marginal and dynamical is now bracketed by two measured
ceilings — PH cannot see traversal (measure 2), the lift cannot see recurrence
(L3) — and the attractor rung's first instrument failed at the rate level,
which is the fact L4b is built on.

## Stage 3b — recurrence: pre-registration (overnight 2026-09-17, before `stage3b_recurrence.py`)

**Why the family changes.** L4 measured deviation from the manifold; IND lies
on the manifold too, so no deviation statistic can separate them. The
discriminating predicate is **recurrence with a restoring force**: an
attractor comes back, an input-driven system is *held* there. That is an
intervention, not an observation.

- **L4b (observational, tangent-projected; run because it is cheap, sealed
  to FAIL).** Manifold model m(φ) as an order-8 Fourier fit of X in the lifted
  coordinate; tangent t̂ = dm/dφ normalized; e_⊥ = (X − m) − ((X − m)·t̂)t̂;
  τ_⊥ from its autocorrelation. Rate level first (A_n vs IND_n on A_n's own
  trajectory, 3 seeds), then spikes at ρ = 50. **Sealed: τ_⊥(A_n)/τ_⊥(IND_n)
  < 2 in ≥ 2/3 seeds at the rate level** — fails to separate, and the reason
  is recorded (predicted: model error is a smooth function of φ(t) and
  dominates the residual in both).
- **I1 along-manifold kick (the live path).** Three systems on the same
  trajectory ψ(t) = ωt (γ = 0.02, no noise): the ring at ε = 0; the pinned
  ring at ε = 0.1 (a *discrete* attractor with a slow restoring force,
  λ₁ = −1.5e-2); and IND_u, independent units with first-order dynamics
  τ_u ṙᵢ = −rᵢ + prof(θᵢ − ψ(t)), τ_u = 1 — units with a state so a kick is
  defined, and no recurrence. At t_k the state is rotated by δ = 0.3 rad along
  the ring; the phase offset Δψ(t) relative to the unkicked run is followed
  for 300τ. **Sealed: retention Δψ(300τ)/δ > 0.9 for the ε = 0 ring; < 0.05
  for IND_u (τ_u = 1); < 0.1 for the pinned ring (e^{−0.015·300} ≈ 0.01).**
  A continuous attractor *retains*; an input-driven system and a discrete
  attractor *restore*. That is the `implies_continuous_attractor` predicate,
  reachable by intervention.
- **I2 transverse kick.** r ← r + η v⊥, v⊥ ⊥ r′, η = 0.2. Both return (the
  ring at its transverse spectrum, IND_u at 1/τ_u); the difference is rate,
  not kind. Sealed: both below 10% at 10τ. Reported so nobody reads a
  transverse return as an attractor signature.
- **T1 traversal statistic re-sealed (B-avg).** On the lifted path: R = total
  variation / |net winding| and J = count of steps with |Δφ| > π/2. Sealed:
  R < 1.5 and J = 0 for A, IND, C_ord; **R > 3 or J ≥ 8 for C_perm** (15
  boundaries; smoothing may merge some). Then
  `ph_topology_with_continuous_traversal` is scored: positives A, IND;
  negatives C_perm, D (unreadable ⇒ silent), unreadable-ρ (silent by rule).

**QUEUED ring→ARS arm (b) — vacuous for this generator, noted 02:35.** The
ring's spikes are inhomogeneous Poisson from the rate envelope, so the
matched-Cox control with the same envelope is *identical in distribution* to
the ring unit's train and the per-cell margin is zero by construction; running
it would score non-evidence as a verdict (#19). A non-vacuous version needs a
spiking ring whose spikes feed back into the dynamics. Not run; for Will.

**Decision queued for Will (not taken overnight):** whether an
intervention-only certification counts for the `implies` rung — i.e. register
`attractor_by_along_manifold_memory` (simulation/experiment) and leave the
observational `implies` DECLARED with "possibly unreachable observationally"
banked as a finding — or fold I1 into `implies` with the intervention
requirement stated in `fires_on`. *[Resolved 2026-09-17, Will: the first —
a separate intervention-class detector (R16); `implies` stays observational
and DECLARED. "Unreachable observationally" was then NOT banked either
(Stage 3e: the MSD growth law is a passive signature that separates in
kind).]*

## Stage 3b — results (`stage3b_recurrence_measured.json`, sealed `ef243e7`)

**The intervention separates in kind.** I1: the ε = 0 ring **retains** an
along-manifold kick exactly — Δψ 0.300 → 0.300 at 300τ, 3/3 — and IND_u
**restores** it completely (0.285 → 0.000 by 10τ, 3/3). That is the
`implies_continuous_attractor` predicate — recurrence with a restoring force
— reached by intervention, as the pre-registration said it would have to be.

**One sealed prediction failed, and it re-poses the discrete-attractor
negative.** The driven pinned ring (ε = 0.1, γ = 0.02) retained **0.88** of
the kick (sealed < 0.1). Under drive ω = 0.02 ≫ c·ε = 2.9e-3 the bump is
not trapped; it sweeps through the wells at a modulated velocity, and on
average there is no restoring force — a driven discrete attractor behaves
like a continuous one for phase memory. The competition ω vs c·ε is the
mode-locking boundary of Stage 4 showing up in Stage 3. I1b (ran; below): the
same kick with the bump *trapped* (γ = 0, or γ below the pinning threshold),
where the restoring force is the well's λ₁ = −0.015 and retention at 300τ
should be ≈ e^{−4.5}.

**L4b failed as sealed, for the predicted reason.** At the rate level IND_n —
zero true transverse fluctuation by construction — reads τ_⊥ = 3.0–3.5τ,
*more* than A_n's 1.1τ: the residual is manifold-model error, a smooth
function of φ(t). At ρ = 50 both sit at the floor (ratio 1.03). **No
deviation-from-manifold statistic reaches the dynamical rung**; on this
substrate the rung is reached by perturbation. Banked.

**I2:** transverse kicks return in the ring (0.001–0.003 remaining at 10τ)
and in IND_u (0) — rate, not kind — and the ring keeps the kick's projection
on its marginal mode (−0.012…−0.019 rad), an observation consistent with I1.
The pinned ring keeps a 7–19% shape residual because the bump's shape is
position-dependent in a heterogeneous landscape.

**T1 — the traversal statistic, re-sealed on the B-avg rail.** R = TV/|net|
reads 1.00 on A and IND (J = 0) and 3.3–5.3 on C_perm (sealed > 3; the J ≥ 8
clause fails — smoothing merges 13 of 15 boundaries). C_ord reads **2.06**,
failing the sealed < 1.5: R − 1 ≈ noise-TV/net, and a stepwise traversal has
a small net. R needs a noise correction before 1.5 is a threshold; that is
pinned as the statistic's false-negative channel. `ph_topology_with_
continuous_traversal` is certified on its *declared* sets (A, IND fire;
C_perm, D-unreadable, unreadable-ρ silent) with the C_ord caveat printed by
the board every run.

## I1b — the trapped negative, and the depinning curve: pre-registration (overnight, before `stage3c_trapped.py`)

The same along-manifold kick (δ = 0.3 rad, T_obs = 300τ) on the pinned ring
at ε ∈ {0.03, 0.1} over drive γ ∈ {0, 0.001, 0.003, 0.01, 0.02}. Retention
R(γ) = Δψ(300τ)/δ. **Sealed:** at γ = 0 the trapped bump restores — R < 0.1
at ε = 0.1 (λ₁ = −0.015 → e^{−4.5}) and R < 0.3 at ε = 0.03 (λ₁ = −0.0038 →
e^{−1.1} = 0.32, so the 300τ window is marginal there and that is stated);
R is monotone non-decreasing in γ at each ε; R(0.02, ε = 0.1) ≈ 0.88 as
banked. The depinning drive γ* (R crossing 0.5) is a **measurement**, expected
between c·ε and 3c·ε (2.9e-3–8.7e-3 at ε = 0.1; 0.9e-3–2.6e-3 at ε = 0.03) —
reported with the grid's resolution (a B-sup rail: a crossing between two
grid points is an interval, not a value). If γ* scales with ε the trapped/
sliding boundary is the ε·T contour's third appearance.

## I1b — results (`stage3c_trapped_measured.json`, sealed `c94351f`)

**The trapped discrete attractor restores; the sliding one retains.** At
ε = 0.1: R(γ = 0) = 0.019 (sealed < 0.1, PASS) and R(γ = 0.02) = 0.72 (PASS).
With I1 this puts all three systems where the predicate says: continuous
attractor 1.00, trapped discrete attractor 0.02, input-driven 0.00, and the
*driven* discrete attractor at 0.72–0.88 because it is sliding. The depinning
crossing at ε = 0.1 lies in **(0.01, 0.02]** — an interval (B-sup), and above
the 3c·ε = 0.0087 guess.

**Two sealed clauses failed, both informative.** (i) R is **not monotone in
γ** at ε = 0.1: 0.019, 0.197, 0.040, 0.334, 0.720. After the drive tilts the
landscape the bump settles in different wells at different γ, and the
effective restoring rate at 300τ is well-dependent (e^{−300λ} = 0.197 needs
λ = 0.0054; 0.040 needs 0.0107 — a 2× spread, larger than Stage 1's per-basin
λ₁ spread of 1.2×, so the tilt is doing work). (ii) ε = 0.03 is INAPPLICABLE
at T_obs = 300τ: R(0) = 0.74 where e^{−1.1} = 0.32 was already called marginal;
the effective λ here is ~1e-3, not the 3.8e-3 median. The window needs
~3000τ. Not re-run overnight; ran as I1c (below).

## Stage 4 — circle map: pre-registration (overnight 2026-09-17, before `stage4_circlemap.py`)

Sine circle map θ_{n+1} = θ_n + Ω − (K/2π) sin(2πθ_n) on the lift, with the
integer winding w carried separately from the residual φ ∈ [0, 1) (the
(n, θ) split, in float64). Ω grid: 1001 points on [0, 1); K ∈ {0, 0.25, 0.5,
0.75, 0.9, 1.0, 1.2, 1.5}; θ₀ = 0.37 (independent init), transient 10³.

**Re-indexed per #20.** No arm asks "is it locked at p/q". The bounded
question is **residence**: over sub-windows of L = 100 iterations inside a
10⁴ window, the fraction f of sub-windows whose local rotation
r_j = (θ_{(j+1)L} − θ_{jL})/L lies within ε_tol of the nearest p/q with
q ≤ Q_max. ε_tol ∈ {10⁻³, 10⁻²} and Q_max ∈ {5, 10} are TESTED.

**Rails (theorem-level; red = instrument):**
- **M1 rotation number as a limit (B-sup).** ρ_N = (θ_N − θ₀)/N at
  N ∈ {10³, 10⁴, 10⁵}. For K < 1 the map is a circle homeomorphism and
  |θ_N − θ₀ − Nρ| < 1 for every N, so **|ρ_{10⁴} − ρ_{10⁵}| < 1.1·10⁻⁴ at
  every Ω for every K < 1**, asserted. For K ≥ 1 the rail does not apply and
  convergence is *reported*, not assumed.
- **M3 the 0/1 tongue boundary is exact:** a fixed point exists iff
  |Ω| ≤ K/2π. The estimator's Ω_c(K) (largest Ω with |ρ| < 10⁻³ scanning up
  from 0) must lie within one grid step (0.005 on the hysteresis grid) of
  K/2π for K ∈ {0.25, 0.5, 0.75, 0.9}.

**Arms and sealed predictions:**
- **M2 residence vs K.** At K = 0 (rigid rotation) the Ω-fraction with f = 1
  is pure number theory: the Farey coverage 2ε_tol·Σ_{q≤Q} φ(q) (Q = 5: 20;
  Q = 10: 64), i.e. 0.020 / 0.064 at ε_tol = 10⁻³ and 0.20 / 0.64 at 10⁻² —
  **measured within ±25% of these** (overlaps neglected; a rail on the
  residence instrument). The Ω-fraction with f = 1 is **monotone
  non-decreasing in K on [0, 1]** at every (ε_tol, Q_max). At K = 1 (complete
  devil's staircase) the fraction of Ω with ρ_{10⁵} within 10⁻³ of some p/q,
  q ≤ 50, is **> 0.85**.
- **M4 hysteresis with its must-be-zero region.** Tongue boundary Ω_c for
  the 0/1 tongue from three protocols on a 201-point Ω grid: independent
  init; adiabatic sweep upward in Ω carrying θ; adiabatic sweep downward.
  Discrepancy D(K) = max pairwise |Ω_c − Ω_c'|. **Sealed: D(K) ≤ one grid
  step for every K < 1 (Denjoy: the rotation number is unique)** — the arm's
  dead region, so "verify it can fire" is: D(K) > one grid step for at least
  one K > 1 is *admissible* and is reported with no prediction on magnitude.
  Multistability at K > 1 is reported as the Ω-fraction where θ₀ = 0.37 and
  θ₀ = 0.71 give |Δρ_{10⁴}| > 10⁻³ (must be 0 for K < 1: a second rail).
- **Connection to I1b (report only):** the depinning interval (0.01, 0.02]
  at ε = 0.1 is the same drive-vs-pinning competition as the 0/1 tongue
  boundary Ω_c = K/2π, with γ playing Ω and the well's c·ε playing K/2π; no
  quantitative mapping is sealed.

**Compute.** numpy, vectorised over (K, Ω); torch is guarded and not
needed at this size (8×1001 trajectories × 10⁵ steps ≈ 5 s).

## Stage 4 — results (`stage4_circlemap_measured.json`, sealed `95be3d1`; 27 s, numpy)

**Rails, all green.** Denjoy: |ρ₁₀⁴ − ρ₁₀⁵| ≤ 4.8·10⁻⁵ at every Ω for every
K < 1 (bound 1.1·10⁻⁴); above 1 it is 6·10⁻⁵ (K = 1), 1.3·10⁻³ (1.2),
2.8·10⁻³ (1.5) — reported. The 0/1 tongue boundary sits within one grid step
of the exact K/2π at every K < 1 in all three protocols. Farey coverage at
K = 0 within +5% / 0% / +11% / −8% of 2ε_tol·Σφ(q). Multistability is
exactly 0 for K ≤ 1 and fires at K > 1 (0.035, 0.144) — the arm can fire.
The hysteresis discrepancy D(K) is 0 at every K, including K > 1 (admissible;
the plan's hysteresis expectation was for *adaptive* oscillators and the
plain map shows none in this protocol, as v5 already said it should not).

**Sealed arms.** Residence Ω-fraction is monotone non-decreasing in K on
[0, 1] at every (ε_tol, Q_max) — PASS; the re-indexed question behaves.

**One sealed test was evidence for neither hypothesis — my own.** The K = 1
staircase coverage (ρ within 10⁻³ of some p/q, q ≤ 50) read 0.978 > 0.85 —
and K = 0, rigid rotation, the rival, read **0.872**. At q ≤ 50 and
tol 10⁻³ the Farey coverage already nearly saturates, so the test cannot
tell a devil's staircase from a rigid rotation. Rival rule, applied to the
arc's own sealed test; recorded INAPPLICABLE AS POSED. The informative read
is the K-dependence, 0.872 → 0.978 → 0.992 (K = 1.2). A discriminating
version needs tol ≪ 1/q_max² (e.g. 10⁻⁵ at q ≤ 50), pre-registered before
re-posing.

**Connection to I1b (not sealed):** the drive-vs-pinning depinning interval
(0.01, 0.02] at ε = 0.1 and the 0/1 tongue boundary Ω_c = K/2π are the same
competition; a quantitative mapping γ ↔ Ω, c·ε ↔ K/2π is a Stage 4b question
for the full ring — ran as Stage 4b (next section).

## Stage 4b — the pinned ring's 0/1 tongue, predicted from a measured quantity: pre-registration (overnight, before `stage4b_ringtongue.py`)

The reduced model for a pinned, driven bump is a phase equation
θ̇ = γ − v_pin(θ), with v_pin the drift-velocity landscape of the heterogeneity
(the object whose median is c·ε, Stage 1). It locks (ρ = 0, trapped) iff
γ < γ* ≡ max_θ v_pin(θ) — the 0/1 tongue edge, exactly as Ω_c = K/2π for the
sine map. **v_pin is measurable at γ = 0**: integrate 64 off-grid bumps briefly
and take the maximal instantaneous drift speed. That is the prediction; the
I1b interval is the test.

- **Sealed:** γ*_pred(ε = 0.1) = max drift speed at γ = 0 lies in the I1b
  interval **(0.01, 0.02]**. γ*_pred(ε = 0.03) = 0.3 × γ*_pred(0.1) within
  ±25% (v_pin ∝ ε in the perturbative regime — Stage 1's contour).
- **Measured tongue:** ρ(γ) = mean bump velocity / γ on a fine γ grid (41
  points, 0 → 0.03) at ε ∈ {0.03, 0.1}, T = 20,000τ after a 2,000τ relax,
  from one start; ρ(γ) = 0 for γ < γ*_meas (first γ with ρ > 10⁻²); **γ*_meas
  within one grid step (7.5·10⁻⁴) of γ*_pred** at each ε. ρ(γ) monotone
  non-decreasing; ρ → 1 as γ/γ* → ∞ (ρ(0.03)/1 > 0.8 at ε = 0.1).
- **Not sealed (report):** the Adler form ρ = √(1 − (γ*/γ)²) fits a
  *sinusoidal* landscape; the heterogeneous landscape's ρ(γ) is compared to
  it and the residual reported, no verdict.
- **Rail:** at ε = 0 the ring's ρ(γ) = 1 for every γ > 0 (ω = γ, Stage 3a
  calibration) within 10⁻³.

## Stage 4b — results (`stage4b_ringtongue_measured.json`, sealed `6d741c2`; 689 s)

**The reduced model predicts the full ring's depinning to within one grid
step.** From the maximal pinning speed measured at γ = 0 (64 starts):
γ*_pred = 7.99·10⁻³ at ε = 0.1 and 1.98·10⁻³ at ε = 0.03. The fine-grid
tongue gives γ*_meas = 8.25·10⁻³ and 2.25·10⁻³ — both within the 7.5·10⁻⁴
step (PASS, PASS). The ε-scaling reads 0.248× (sealed 0.3 ± 25%, PASS): the
pinning landscape is perturbative in ε, the contour's fourth appearance.
ρ(γ) is monotone at both ε and reaches 0.982 at γ = 0.03 (ε = 0.1). The ε = 0
rail holds exactly (ρ = 1.0000 at every γ > 0). Max/median of the landscape
within this table: **3.02** at ε = 0.1, **2.54** at ε = 0.03; against the
Stage 1 contour's c·ε (its median over 16 starts): 2.75 and 2.27 — the *edge*
of the tongue is set by the landscape's maximum, the Stage 1 contour by its
median (R15 prints both).

**One sealed clause failed, on a conflation I made.** γ*_pred(0.1) = 0.0080
is *below* the I1b interval (0.01, 0.02]. I1b's "crossing" was a
retention-at-300τ statistic (R = 0.5), not a tongue edge: just above γ* the
bump slides slowly (ρ = 0.70 one grid step up) and two sliding bumps stay
phase-aligned for a while, so retention crosses 0.5 at a higher γ than ρ
leaves zero. Two observables, one seal; the physics prediction passed and
the conflation failed. Recorded as FAIL, not re-scoped.

**Report only:** ρ rises 0 → 0.70 within one step above γ* at ε = 0.1,
steeper than the Adler √ form (0.40 at γ = 1.09γ*); the heterogeneous
landscape depins more abruptly than a sinusoid. No verdict sealed.

**Instrument note:** the batched einsum integration took 689 s where two
BLAS matmuls would take ~30 s; not re-run (the numbers are the numbers), but
the next ring sweep uses `r @ W_even.T + γ[:, None]·(r @ W_odd.T)`.

## I1c — ε = 0.03 at a long window, cross-checked against Stage 4b: pre-registration (overnight, before `stage3d_trapped_long.py`)

I1b was inapplicable at ε = 0.03 with T_obs = 300τ. Re-run with T_obs = 3000τ
(T_relax 8000τ, δ = 0.3 rad, γ ∈ {0, 0.001, 0.003, 0.01, 0.02}). Stage 4b
measured the tongue edge γ*(0.03) = 2.25·10⁻³, so the retention crossing at a
window long enough to resolve restoring should land between the grid points
that straddle it. **Sealed:** R(γ = 0) < 0.1 (e^{−3000·λ_eff} with λ_eff ≳
10⁻³); R(γ = 0.001) < 0.5 (trapped, below γ*); R(γ = 0.003) > 0.5 (sliding,
above γ*); R(γ ≥ 0.01) > 0.8. If the crossing sits elsewhere, the two
observables (retention at finite T; ρ over 20,000τ) disagree about the edge
and that disagreement is the finding.

## I1c — results (`stage3d_trapped_long_measured.json`, sealed `5c26749`)

**Two observables agree about the edge.** At ε = 0.03, T_obs = 3000τ:
R(γ = 0.001) = 0.001 (trapped, restores completely) and R(γ = 0.003) = 2.0
(sliding) — the retention crossing straddles Stage 4b's tongue edge
γ* = 2.25·10⁻³ as sealed. The intervention's restoring/retaining boundary and
the driven ring's ρ-tongue edge are the same number.

**R(γ = 0) = 0.368 fails the < 0.1 clause** — the well this bump settles in
has λ_eff = 3.3·10⁻⁴, ten times below the Stage 1 median |λ₁| = 3.8·10⁻³ at
ε = 0.03. Well-dependence of the restoring rate is now quantified at 10×,
and 3000τ is still short for the shallowest wells. Any per-well statement
needs the well identified; the median is not the well.

**Retention above threshold exceeds 1** (2.0 at γ = 0.003): a sliding bump's
phase offset is not conserved but *wanders* as the two bumps traverse the
wells at different times. R is a trapped-system statistic; above 0.5 it says
"sliding" and nothing quantitative. Recorded.

## M2b — the staircase test re-posed so the rival fails it: pre-registration (overnight, before `stage4c_staircase.py`)

M2's staircase test (ρ within 10⁻³ of some p/q, q ≤ 50) was passed by rigid
rotation (0.872) because the Farey coverage 2·tol·Σ_{q≤50}φ(q) = 2·tol·774
saturates at tol = 10⁻³. Re-posed with tol ∈ {10⁻³, 10⁻⁴, 10⁻⁵} at
K ∈ {0, 0.5, 1.0}, ρ from N = 10⁵ iterations (Denjoy bound 10⁻⁵ on ρ_N for
K ≤ 1 — at tol = 10⁻⁵ the instrument's own resolution is at the threshold and
that is stated; a K = 1 point counted as unlocked at 10⁻⁵ may be resolution).
**Sealed, at tol = 10⁻⁵:** K = 0 coverage within ±30% of the Farey value
0.0155 (the rival's number, stated first); K = 1 coverage **> 0.5**
(plateaus of the complete staircase with q ≤ 50); **K = 1 minus K = 0 > 0.3**
— the test separates the staircase from its rival by construction or it is
not a test. K = 0.5 lies between them (monotone in K at every tol).

## M2b — results, and M2c pre-registration (overnight)

**M2b (`stage4c_staircase_measured.json`, sealed `330e84b`).** At tol = 10⁻⁵:
K = 1 coverage 0.738 (> 0.5 PASS); K = 0.5 0.201; K = 0 **0.029**;
K = 1 − K = 0 = 0.71 (> 0.3 PASS); monotone in K PASS. The re-posed test
separates the staircase from rigid rotation by construction. **The K = 0
clause FAILS against the Farey value 0.0155 for an exactly identifiable
reason:** `linspace(0, 1, 1001, endpoint=False)` places Ω at j/1001, and
1001 = 7·11·13, so φ(1)+φ(7)+φ(11)+φ(13) = 29 grid points *are* Farey
fractions with q ≤ 50 — 29/1001 = 0.02897, the measured value to the digit.
**A rational Ω grid is itself a Farey object**; at tolerances below the grid
spacing the rival's number measures the grid, not the map. Rail, added to
the boundary-supported-signal class as B-grid: a grid of rationals against a
rational target set has coincidences that are a property of the grid.
**M2c, sealed:** the same three K and three tolerances with Ω drawn
uniformly at random (1001 draws, seed 7); at tol = 10⁻⁵ the K = 0 coverage is
within ±30% of 0.0155 (the Lebesgue estimate now applies) and K = 1 stays
> 0.5 with separation > 0.3.

**M2c (`stage4d_staircase_random_measured.json`, sealed `80311b5`) — PASS.**
Random Ω, tol 10⁻⁵: K = 0 coverage 0.0130 vs Farey 0.0155 (−16%, within
30%); at 10⁻⁴: 0.158 vs 0.155 (+2%). K = 1: 0.736; separation 0.72; monotone.
The rival's number is now the theorem's number, and the staircase test
discriminates. The M2 verdict is superseded: complete-staircase behaviour at
K = 1 is supported against its rival at tol ≤ 10⁻⁴.

## Doctrines banked after the overnight read (2026-09-17, morning)

**Why the along-manifold kick works — a definition, not a proxy.** A
continuous attractor is defined by a marginal direction, and a marginal
direction has no autonomous dynamics: that is what marginal means. A zero
mode does nothing by itself; the only signal it can emit is a response to
displacement — *including the endogenous displacements that noise supplies*,
which is why its passive signature, when noise is present, is the integration
of that noise (Stage 3e: diffusion along the manifold).
Retention of an along-manifold kick is the definition operationalized. This
makes "unreachable observationally" a *structural* claim with L4/L4b as
support, not a generalization from two failed statistics — **but it is not
banked until its passive dual (the MSD arm below) has been run**, because a
structural claim that has not survived the obvious candidate is a claim
about the search.

**Order statistics reconcile the four instruments.** Stage 1's contour used
the *median* pinning velocity (drift averages over many wells: a typical-well
quantity); Stage 4b's tongue edge used the *maximal* (depinning requires
escaping every well: an extreme-value, strongest-barrier quantity). Max/median
of the pinning speed — 3.02 at ε = 0.1 and 2.54 at ε = 0.03 within Stage 4b's
64 starts; 2.75 and 2.27 against the Stage 1 contour's c·ε — is a measurable
property of the disorder, not a nuisance, and the 10× well-dependence that
broke two monotonicity clauses is the same fact seen a third way.

**Presentation correction.** "Predicts the full ring's depinning to 3%" was
the ε = 0.1 number; ε = 0.03 is 12% (1.98e-3 vs 2.25e-3). Both within one grid
step — the honest line is **"3% and 12% at two ε, both within a grid step."**
Reporting the better of two is the winner's-interval shape (#19).

**B-grid generalizes.** On the grid j/n, the count of points that are Farey
fractions with q ≤ Q is Σ_{d | n, d ≤ Q} φ(d): for n = 1001 = 7·11·13 that is
φ(1)+φ(7)+φ(11)+φ(13) = 29. Three small prime factors was maximally bad; a
prime n has essentially no low-denominator hits. Since Arnold-tongue and
devil's-staircase numerics are done on rational grids as a matter of course,
this is a methods note someone should have written; the fix (random draws
or a declared irrational offset) is checkable in advance by the arithmetic.
*Candidate for `~/derivflow_outreach/`, not written here.*

**The QUEUED ring→ARS arm is re-filed: BLOCKED ON A SPIKING RING.** Option
(b) assumed some option was runnable on this generator; identical-in-
distribution kills all three. A spiking ring is a generator change with
consequences for every Stage 1–4 number's applicability — not near-term.

**Drift note, kept visible.** 55 commits in, **Stage 5 — bits per window in
the (n, ψ, r) encoding, the question the plan was written for — is unrun.**
Stage 3a already gives its first two inputs for free: |n| exact wherever
readable (the integer channel's error rate is 0 or undefined, never
intermediate) and θ residual 0.02–0.04 rad (the ψ channel's floor). The arm
is queued *after* the MSD arm and T2 below, and not behind anything else.
*[2026-09-20: the MSD arm, T2, T3 and Stage 3h have run; Stage 5 is now
NEXT — nothing is ahead of it.]*

## Stage 3e — MSD along the manifold: pre-registration (before `stage3e_msd.py`)

Noise is an endogenous kick train, so the three systems should separate by
growth law rather than by response. Input noise σ_n = 0.05 (as L4) on: the
ring at ε = 0, γ = 0.02 (continuum); the ring at ε = 0.1, γ = 0 (trapped in
a well); IND_u (independent first-order units, τ_u = 1, on the noiseless
trajectory ωt, with the same input noise on each unit). Decoded angle =
the order-parameter angle of the rate vector (passive, noise-free decoding;
the spike-level version is a power question to run after, not before).
T = 20,000τ per system, 3 seeds; MSD(Δ) = ⟨(ψ(t+Δ) − ψ(t) − ω_fit Δ)²⟩ over
lags Δ ∈ [1, 2000]τ, log-spaced, after removing the mean drift.

**Sealed:**
- Continuum: log-log slope of MSD vs Δ over Δ ∈ [10, 1000]τ = **1.0 ± 0.15**;
  MSD(1000)/MSD(100) ∈ [7, 13]. D = MSD/(2Δ) is banked (pilot: bump-position
  std 0.031 rad over 1000τ → D ≈ 5·10⁻⁷ rad²/τ).
- Trapped: saturates; slope over [200, 2000]τ < 0.3; **MSD_sat within a
  factor 2 of 2D/|λ₁|** with D from the continuum row and λ₁ = −1.49·10⁻²
  (Stage 1, ε = 0.1, median) — *stated caveat: this well's λ₁ is not the
  median (I1c found 10× spreads), so the factor 2 is generous on purpose*;
  crossover Δ_c (where MSD reaches half its saturation) within a factor 3 of
  1/|λ₁| ≈ 67τ.
- IND_u: saturates by Δ ≈ 3τ_u; MSD(1000)/MSD(10) < 1.5; slope over
  [10, 1000]τ < 0.15.
- Separation in kind: continuum slope − trapped slope > 0.5; IND_u
  saturation lag < trapped crossover / 10.

If all three hold, the `implies` rung is observationally reachable and
`ph_topology_implies_continuous_attractor` gets its instrument (MSD growth
law) and its negative set (trapped ring, IND_u) with numbers. If the
continuum fails its own growth law or the three do not separate, "unreachable
observationally" is banked as structural, having survived the obvious
candidate.

## T2 — traversal statistic re-sealed on MAD jumps + monotone winding (before `stage3f_traversal2.py`)

R = TV/net could not separate stepwise-but-monotone (C_ord) from
smooth-but-noisy. Two clauses, no new scale parameter beyond the
conventional MAD multiplier: J_mad = #{steps with |Δφ| > 5·MAD(|Δφ|)};
M = fraction of steps with sign(Δφ) = sign(net winding) among steps with
|Δφ| > MAD. **Sealed:** A, IND: J_mad ≤ 5 and M ≥ 0.9 (smooth traversal);
C_ord: J_mad ≥ 10 and M ≥ 0.9 (stepwise traversal — a *positive*); C_perm:
J_mad ≥ 10 and M < 0.7 (jumpy, non-monotone — negative); D unreadable.
The traversal detector's positive set gains `stepwise_traversal_C_ord`.

## Detector registered: `attractor_by_along_manifold_memory` (intervention class)

Separate from the observational ladder, because intervention is a different
*access class* and putting it in `fires_on` would conflate statistic-reach
with data-access. Fires when an along-manifold displacement δ is retained
(Δψ(T_obs)/δ > 0.9). Positive: ring ε = 0 (I1: 1.00, 3/3). Negatives: IND_u
(I1: 0.00, 3/3), trapped pinned ring (I1b γ = 0: 0.019). Nearest
confusable: the *driven* pinned ring above depinning (0.72–0.88), which is
sliding and retains — correctly, since above γ* it has no mean restoring
force. Certified on banked data by R16.

## Stage 3e — results (`stage3e_msd_measured.json`, sealed `8164091`)

**In kind, the three growth laws separate in every row.** Continuum: long-lag
slope 0.93–1.09 (sealed 1.0 ± 0.15, PASS 3/3), D = 1.52·10⁻⁵ rad²/τ banked.
IND_u: slope 0.00, MSD(1000)/MSD(10) = 0.98–1.01 (PASS 3/3) — white, no
integration. Trapped: saturating, long-lag slope 0.20–0.40, MSD_sat ≈ 10⁻²
rad². The zero mode *does* emit a passive signature: it integrates noise.

**At sealed precision the rung is not certified, and the trapped failures
have one cause.** *[S5 — the "one cause" attribution below is RETRACTED; the
common factor stands as a measurement, its cause is open.]* MSD_sat is 4–5×
the 2D/|λ₁| prediction (0/3) and the
crossover is 193–346τ against 1/|λ₁| = 67τ (1/3). Both are consistent with a
single effective restoring rate λ_eff = 1/crossover = 2.9–5.2·10⁻³ =
**0.19–0.35 × λ₁**, and 2D/λ_eff matches MSD_sat to 1.0–1.3×. Noise drives
0.1-rad excursions, and at 0.1 rad the δ-sweep measured a restoring ratio of
0.32 *[S5: that 0.32 is the ε = 0.01 well's; the MSD well reads 0.99 at
0.1 rad]*. ~~**The anharmonic well, through a third instrument** — the linear
λ₁ is the wrong constant for a noise-driven bump, as it was for a 0.05-rad
kick.~~ *[S5]*
The continuum's MSD(1000)/MSD(100) clause (2/3) and the separation clause
(2/3, one seed at 0.49 vs 0.5) fail on long-lag statistics: at T = 20,000τ a
lag-1000 MSD has ~20 independent segments (±30%).

**Verdict.** `ph_topology_implies_continuous_attractor` is **not certified**
(sealed clauses missed), and **"unreachable observationally" is not banked**
either — the growth law is a passive signature that separates in kind. The
next seal uses λ_eff from the δ-sweep at the noise-set excursion *[S5: the
δ-sweep of the MSD well gives λ₁, not λ_eff — this prescription is void; see
Stage 3h]*, T ≥ 10⁵τ
or 10 seeds for the long-lag ±30%, and thresholds stated on the long-lag
slope (the post-hoc ordering above is reported, not scored). The rung stays
DECLARED with its instrument named.

## T2 — results (`stage3f_traversal2_measured.json`, sealed `827dc8b`) and T3 pre-registration

**T2 fails as sealed, on the statistic.** J_mad = 300–500 on A and IND
(sealed ≤ 5): MAD of |Δφ| about its own median does not measure noise when
the increments have a nonzero mean — A drifts 0.010 rad/step with MAD
0.0024, so a quarter of ordinary steps exceed 5·MAD. C_ord's M = 0.56 (sealed
≥ 0.9): the monotone clause evaluated on all above-MAD steps is polluted by
noise steps whose signs are random; its 15 real boundaries are a few hundred
steps' worth of noise away from being visible. C_perm passes both clauses
for the wrong reason (noise). B-avg again, one level down: a robust scale
must be taken about the *typical step*, not about zero.

**T3, sealed:** increments centered, c = Δφ − median(Δφ); noise scale
MAD_c = MAD(c); jumps = {|c| > 5·MAD_c}; J = their count; M = fraction of
*jump* steps with sign(Δφ) = sign(net) (undefined → 1 if no jumps). Predictions:
A, IND: J ≤ 10 (noise tails at 3.4σ over 2000 steps) and M ≥ 0.9 or undefined;
C_ord: 10 ≤ J ≤ 40 (15 boundaries, each spread over ≤ 2 bins by σ_s = 1τ) and
M ≥ 0.9; C_perm: 10 ≤ J ≤ 40 and M < 0.7; D unreadable. If C_ord's J lands
outside [10, 40], the smoothing-spread model of a boundary is wrong and that
is reported before the threshold is touched.

**T3 — results (`stage3g_traversal3_measured.json`, sealed `b52fcc8`).** The
monotone clause separates cleanly: C_perm M = 0.57–0.59 (< 0.7 PASS), C_ord
0.99–1.00 (PASS), A/IND 0.78–0.95 (≥ 0.9 in 4/6). J separates smooth (9–44)
from stepwise (121–342). The sealed numbers fail: A/IND J ≤ 10 in 1/6 (the
lifted coordinate's noise is heavier-tailed than Gaussian), and C_ord's J =
121–126 sits at 8× its 15 boundaries because the Gaussian kernel's *support*
is 4σ = 8 bins, not the 2 bins the spread model assumed — a third
boundary-support miscount, reported before the threshold is touched, as
pre-committed. **Three sealed versions of this statistic have each failed
their own numbers while the qualitative separation held; that is the point to
stop iterating.** The ordering is pinned (R13d); the thresholds go to a
negative-set calibration, Will's call, not a fourth seal.

## Stage 3h — the MSD well's own δ-sweep: pre-registration (2026-09-20, before `stage3h_well_delta.py`)

**Why.** Stage 3e attributed the trapped ring's λ_eff = 0.19–0.35 × λ₁ to well
anharmonicity, citing "the δ-sweep measured a restoring ratio of 0.32 at
0.1 rad". The 2026-09-20 review found that number in no table; banking the
sweep (Stage 1 tables v3) shows it belongs to the **ε = 0.01, T = 20000
rows** (0.322), while the **ε = 0.1 converged rows read 1.016** at δ = 0.1 —
harmonic. The MSD arm's trapped run is ε = 0.1 from start 0.37 rad, and the
Stage 1 tables are medians over 16 off-grid starts, so the well the MSD arm
sat in has never had its own sweep. The interpretation borrowed a number
from a different ε and a different well.

**Arm.** The exact trapped state of Stage 3e (ε = 0.1, γ = 0, start 0.37 rad,
relax 2000τ; fixed-point residual asserted < 10⁻⁹) and, for the I1c well,
ε = 0.03 from the same start (relax 8000τ). On each: λ₁ from the Jacobian;
`relaxation_rate` at δ ∈ {0.005, 0.01, 0.02, 0.05, 0.1, 0.2} rad with
T = 50τ and T = 200τ (the read must not depend on T, as the δ probe showed).
**Sealed, two-sided:**
- H_anharm (the Stage 3e interpretation): at δ = 0.1 the ratio
  relax/λ₁ ∈ [0.15, 0.45] for the ε = 0.1 well (matching the MSD-derived
  λ_eff/λ₁ = 0.19–0.35), and the ratio decreases monotonically with δ.
- H_harm (falsifies the interpretation): ratio > 0.8 at δ = 0.1 for that
  well. Then the MSD discrepancy has a different cause, the Stage 3e "one
  cause" paragraph is retracted as S5, and the cause is open — with the
  candidates named in advance: (a) the noise-driven D along the marginal
  mode differs between the driven and trapped rings (checkable from the
  banked trapped MSD at short lags: MSD(10)/20 ≈ 1.4·10⁻⁵ matches the
  continuum's D, so (a) is already disfavoured); (b) the effective potential
  seen by a *noisy* bump differs from the deterministic δ-sweep (shape
  fluctuations couple to position); (c) the crossover/saturation estimator
  itself (the 20-segment long-lag noise).
- The ε = 0.03 well from start 0.37: ratio at δ = 0.1 reported; I1c's
  λ_eff = 3.3·10⁻⁴ vs Jacobian λ₁ is the comparison.

## Stage 3h — results (`stage3h_well_delta_measured.json`, sealed `b175f34`, scored R18)

| well | fp resid | λ₁ | ratio T=50: 0.005 / 0.01 / 0.02 / 0.05 / **0.1** / 0.2 | T=200: 0.1 / 0.2 |
|---|---|---|---|---|
| ε = 0.1, start 0.37 (the MSD arm's) | 1·10⁻¹⁴ | −1.525·10⁻² | 1.009 / 1.014 / 1.022 / 1.031 / **0.992** / 0.751 | 1.014 / 0.944 |
| ε = 0.03, start 0.37 (I1c's) | 1.4·10⁻⁹ | −3.771·10⁻³ | 0.996 / 0.992 / 0.977 / 0.583 / **0.223** / 0.084 | 0.261 / — |

**H_harm fires on the MSD well** (0.99 / 1.01 at 0.1 rad against a sealed
H_anharm window [0.15, 0.45]): Stage 3e's anharmonic cause is retracted
(**S5**). The read is T-independent below 0.1 rad (|Δ| < 0.03); at 0.2 rad
the T = 50 read (0.75) is the ~4-step transient, T = 200 gives 0.94 — the
well is harmonic to within 6% out to 0.2 rad. The MSD arm's noise-driven
excursions are ~0.1 rad; **the linear λ₁ was the right constant for that
well**, and the λ_eff/λ₁ = 0.19–0.35 factor is unexplained. Open, with the
pre-named candidates: (b) the effective potential of a *noisy* bump — shape
fluctuations coupling to position — and (c) the crossover/saturation
estimator at ~20 independent long-lag segments. (a) stays disfavoured.

**H_anharm holds on the I1c well**: 0.22 at 0.1 rad, 0.084 at 0.2 rad, and
λ₁ × ratio(0.2 rad) = 3.18·10⁻⁴ against I1c's measured λ_eff = 3.33·10⁻⁴
(0.95×). The Stage 3b I1c interpretation (a 0.3-rad kick relaxing at the
anharmonic rate) is now quantitative at the well itself. Note λ₁ differs 4×
between the wells (−1.5·10⁻² vs −3.8·10⁻³ at ε 0.1 vs 0.03), consistent
with the pinning gap ∝ ε.

**Doctrine.** A mechanism measured in one well was carried to another by a
number the tables did not contain. The review caught the number; the sweep
of the right well caught the mechanism. *A cause attributed to a well is
measured in that well.*

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
4. **Stage 2 — non-normality.** **Done** (results above).
5. **Stage 3a — path-lifting.** **Done** (results above); L4b done (Stage 3b: sealed-to-fail CONFIRMED, rate-level ratio < 2). `rotational_dynamics_fit`
   stays DECLARED: the ring's asymmetry is a traveling wave, not a rotation in
   a fixed basis; the jPCA-style fit belongs to a Stage-2 substrate with a
   fixed basis (W_sym + αW_rand at α large enough for limit cycles), which
   this sweep did not reach (largest random row unconverged).

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

## Acceptance criteria (board rows R0–R18 in `verify_ring.py`)

*Written for Stage 0/1 (R0–R7); rows R8–R18 carry their own sealed clauses
and pins in the sections above, and every printed verdict is a `chk`
(2026-09-20). A deterministic row is ONE replicate: "3/3" on IND_u or the
trapped ring counts states, not seeds.*

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

*(As written for Stage 0/1.)* Stages 3–7; spikes off the ring into ARS and
the QUEUED ring→ARS instrument bound; any population-level claim. *Since
then: Stages 2, 3a–3h, 4, 4b ran (above); Stage 5 is next; the ARS arm is
BLOCKED on a spiking ring (plan, QUEUED).*

## Deliverables

1. `rotational-dynamics-build-plan.md` v5.
2. `__init__.py` (guarded torch), `ringnet.py`, `detectors.py`, `verify_ring.py`.
3. `stage1_marginal.py` (sealed generator, v2) → `stage1_marginal_measured.json`;
   `stage1_contour.py` (sealed, v2) → `stage1_contour_measured.json`.
4. This brief; RESULTS.md §7.ter row — filed 2026-09-20 (one commit per
   phase convention; deferred from measure 2 through the overnight).

## Open questions carried forward

- QUEUED arm: ~~(b) chosen~~ → **BLOCKED ON A SPIKING RING** (Will,
  2026-09-17; plan QUEUED entry). The rate ring emits no spikes to certify;
  the arm waits for Stage 5's emitter. No option among (a)/(b)/(c) is taken.
- ~~c(ε·T) fit before measure 2~~ — done. ~~Measure 2~~ — done.
- ~~(a) σ_s sweep~~ done (F6; and the "SNR" reading was wrong, S4).
  ~~(b) visits-per-unit~~ done (F5). ~~(c) Stage 2~~ done.
- ~~Stage 3~~ 3a + 3b done. ~~**Overnight queue:** I1b, Stage 4, a
  noise-corrected R for T1~~ — all ran (I1b/I1c, Stage 4/4b/4c/4d, T2/T3;
  results above). ~~**For Will:** whether the intervention-only
  certification counts for the `implies` rung~~ — resolved 2026-09-17: it
  is its own detector (`attractor_by_along_manifold_memory`, intervention
  class), not the observational `implies` rung. **Open (2026-09-20):** the
  MSD arm's λ_eff/λ₁ = 0.19–0.35 has no cause banked (S5); the T3 thresholds
  await a negative-set calibration (Will); Stage 5 is next.
- Per-basin λ₁ spread: at ε=0.1 the three pinned basins have λ₁ = 1.28e-2 /
  1.49e-2 / 1.53e-2; the tables bank the median, min and max. If Stage 6 needs
  per-basin curvature, the column exists.
- Where the QUEUED arm's "which calibrator is each dial setting redundant with"
  column is computed — `extractor_distinctness` machinery or a new panel.
