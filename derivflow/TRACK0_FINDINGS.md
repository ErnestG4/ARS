# derivflow Track-0 — FINDINGS

## TL;DR

- **§1 Hermite self-map gate: PASS** (2026-08-10, first run, 480/480 steps, n = 512, s up to
  0.9375). Gate A worst raw-position deviation **1.35×10⁻¹³** of local spacing vs the mpmath
  reference (tolerance 10⁻⁹) — at or below scipy's own reference floor (2.0×10⁻¹³), so the
  iteration is as accurate as the float64 reference it is checked against. Gate B worst unfolded
  bulk-mean-spacing deviation **0.0078** (tolerance 0.02), consistent with O(1/m) finite-size at
  the smallest m = 33. No bracket violation at any step. The harness has earned the other three
  seeds (iid, GUE, picket-fence): **not yet run.**
- **§2 Free-convolution evaluator closed-form gates: PASS** (2026-08-10, first run after one
  API-name fix). Semicircle stability worst density deviation **1.1×10⁻⁷** (tol 10⁻⁴) over
  κ ∈ {1.5…16}; Bernoulli free binomial worst **1.6×10⁻⁶** over κ ∈ {1.2…5}; atom mass at
  κ = 1.5 measured **0.250000** vs 0.25 predicted, absent at κ = 3 (**0.000000**); contraction
  residual certified < 10⁻¹³ everywhere. The evaluator has earned the empirical-measure input
  and the iid seed: **§6.iii not yet run.**
- **§3 iid-seed n-scaling gate (§6.iii): PASS through the strict branch** — all 18 comparisons
  monotone, escalation rule not invoked (2026-08-10, verdict rule pre-committed in scope v1.3
  before the table was read, commit dbb0321). Log-slopes ≈ **−1.0 at every s** (fits −0.91 to
  −1.04) — steeper than the −1/2 fluctuation-dominated signature; no high-s flattening, so the
  ε-adjudication branch was not needed. **Design fact for the seal: the iid seed is already at
  the crystalline ceiling by s = 0.1** (1 − ⟨r̃⟩ ~ 10⁻⁵–10⁻⁷); the rate action lives at small s
  and the science-phase s-grid must be log-spaced there.
- **§4 Adversarial literature pull: GAP STANDS under both parameterizations** (2026-08-11,
  agent, four targets). 2410.06403 v2 is presentational; seven citing papers all global-scale
  (near-miss 2605.31356 proves the flow's TARGETS are locally lattice, not the flow); no theorem
  on local spacing of p^(k) for 1 ≪ k ≤ sn; the n = ∞ Poisson anchor (Pemantle–Subramanian
  1409.7956: crystallization theorem, NO rate) and the k = n − O(1) Hermite/Appell endpoint are
  now cited; the k = O(1) interlacing floor is program-derived (complex pairing theorems exclude
  real support by hypothesis). Full verdicts in scope §9.
- **§5 Numerical jitter floor (§6.iv-a): PASS, all three declared gates** (2026-08-11). Transfer
  ratios 0.86 → 0.09 across k = 1…64 (theorem bound ≤ 1, measured strictly contractive and
  tightening with k); floor-vs-signal ratio ~10⁻¹³ in the fit window (gate: 10⁻²); amplification
  slopes 0.46–1.17 (gate: ≤ 1.3). The rate fits cannot be reading solver noise by ~11 orders.
- **SEALED 2026-08-11** (`seals/RATE_QUESTION_SEAL.json`, commit 95e1ad3, bound to harness commit
  90a1787): disclosure ledger, 16-replicate ensemble under SeedSequence(20260811), form ladder +
  AICc + 3σ/5σ z-rule on shape parameters, picket-fence ceiling-invariance clause, k*(n)
  descriptive table. Seal written BEFORE §6.iv-b ran, so the fitted iid data is entirely
  post-seal.
- **§6 Realization ensemble (§6.iv-b): banked** (2026-08-11, 48 flows, 94 min,
  `track0_ensemble.json`). Relative σ 2.5–25% across the fit window; 5 fit-window points at every
  n; the §6.iv-a numerical floor sits ~11 orders below this σ — the -a/-b separation the scope
  demanded, confirmed. No verdict field by design: this is the error bar.
- **TRACK-0 COMPLETE.** Every gate green, error bar banked, seal locked. The science phase (GUE
  ensemble from seal children 48–95, picket-fence, fits, z-adjudication) executes a fully
  pre-committed procedure.

## 5. Numerical jitter floor (scope §6.iv-a, gates declared v1.4 before the run)

Runner: `track0_jitter_floor.py`. Artifact: `track0_jitter_floor.json`. n = 4096,
k ∈ {1, 2, 4, 8, 16, 32, 64}, δ ∈ {10⁻¹², 10⁻¹⁰, 10⁻⁸} × local spacing, R = 6, 19 flows,
runtime 81 min.

| k | 1−⟨r̃⟩ (unpert.) | spread @δ=10⁻¹² | transfer max | amp slope | window |
|---|---|---|---|---|---|
| 1 | 3.29×10⁻¹ | 4.7×10⁻¹⁴ | 0.858 | 1.03 | FIT |
| 4 | 8.61×10⁻² | 1.1×10⁻¹⁴ | 0.621 | 0.94 | FIT |
| 16 | 3.27×10⁻³ | 6.6×10⁻¹⁵ | 0.348 | 1.17 | FIT |
| 64 | 1.43×10⁻⁴ | 3.5×10⁻¹⁵ | 0.090 | 0.46 | ceiling |

- **Gate (i), transfer:** every ratio strictly below 1 at every k and gated δ — the ℓ∞
  non-expansivity lemma is not just satisfied but strengthens with k (0.86 at k = 1 down to
  0.09 at k = 64): the flow actively contracts seed perturbations, so the small-k floor
  upper-bounds downstream by a widening margin.
- **Gate (ii), floor-vs-signal:** in the fit window the replicate spread at δ = 10⁻¹² sits
  ~11 orders below the signal (ratio ~10⁻¹³ vs the 1% gate). Ceiling rows: spreads
  3.5–8.7×10⁻¹⁵ vs the 10⁻⁷ bound.
- **Gate (iii), amplification:** log-log slopes 0.46–1.17, all ≤ 1.3 — linear-or-below transfer,
  no chaotic amplification anywhere on the grid.
- **Pre-registration ordering, for the record:** the functional-form ladder was committed
  (v1.4, 87437a7) BEFORE any k-resolved transition data existed (§6.iii saw only the s ≥ 0.1
  ceiling plateau; the n = 256 smoke's two points and this run's 7-point unperturbed curve came
  after the ladder was filed). The iid transition curve incidentally visible in this artifact's
  unperturbed column is banked, unfitted, and uncompared — no form has been selected and no
  second seed class has been run; the sealed adjudication is untouched.

## 1. Hermite self-map gate (scope §5c / §6)

Harness: `track0_harness.py`. Artifact: `track0_hermite_gate.json` (all declared constants,
per-step records, checkpoint records, verdict). Runtime 13 s single-core.

**Design as run** (Will's three harness notes, folded in before first execution):
- Two independent comparisons, both green across the full s range. Gate A (raw positions, no
  rescaling — the identity Hₙ′ = 2n·Hₙ₋₁ moves roots onto Hₙ₋₁'s roots literally): authoritative
  reference is mpmath at dps 40, Newton-refined through the recurrence, at 8 checkpoints; the
  per-step scipy comparison is advisory. Gate B (unfolding layer, where rescaling lives): unfolded
  bulk mean spacing vs 1 against the per-step semicircle radius √(2m), every step. Physicists'
  convention pinned in the header comment (probabilists' = √2 dilation).
- Checkpoint deviations **decrease** along the flow: 1.35 → 0.09 ×10⁻¹³ from k = 1 to k = 479.
  Consistent with the map's sensitivity structure: ∂x*/∂rᵢ are convex weights (they sum to 1), so
  per-step solve error does not amplify downstream — the flow is error-contractive in practice.
- Bulk window `BULK_FRACTION = 0.20` (central), inherited from the Phase 1/3 GUE-arm convention
  (central W of a size-5W spectrum, `arsrh/phase1_zeta_crossover.py:48`), applied identically at
  every s. Readout power floor `MIN_WINDOWED_SPACINGS = 64` checked against POST-window count.
- The rate statistic is logged as **1 − ⟨r̃⟩** (ceiling-compression fix): ⟨r̃⟩ approaches 1 from
  below, so the fit runs in log-distance space, not against the saturating raw value.

**Ceiling arm, measured** (banked as measurement, not gate): the Hermite bulk is essentially
crystalline at every s — 1 − ⟨r̃⟩ runs 2.4×10⁻⁷ (s ≈ 0) → 4.2×10⁻⁵ (s = 0.94, m = 33), Σ²(L=8)
0.005 → 0.022. This is the finite-n ceiling arm of scope §6.iv/§9 with numbers attached: the
rate fits for the science seeds will be read against this floor-of-the-ceiling, which is itself
O(1/m)-limited, not zero.

**Powered-readout consequence for the science runs:** with the 20% window at n = 512, the
post-window count crosses below 64 spacings at s ≈ 0.37. The gate itself is valid at all s
(exactness does not need readout power), but the science runs need
0.2·(1 − s_max)·n ≥ 64 ⇒ **n ≥ 3250 for s_max = 0.9; use n = 4096.** This lands exactly as
scope §4 anticipated — the floor binds on post-window count, per Will's note 3.

**Solver change 2026-08-10 (same day):** `diff_step` moved from 60-bisection+3-Newton to
25-bisection+5-clamped-Newton for the n = 4096 science runs; the gate was re-run before anything
consumed the new solver and **re-PASSED with bit-identical worst deviation (1.35×10⁻¹³)**.
Caveat, so this doesn't sound stronger than what it certifies: bit-identical means both solvers
converge to the same float64 fixed points at the checked points — which is exactly what
bracket-clamped iterations should do — not that the solvers are equivalent in general. The
gate's authority is unchanged either way.

**Verdict: PASS.** Gates §6.i (Hermite exactness) and §6.ii-on-Hermite (interlacing) are green.
Remaining before the seal: §6.iii (unfolding residual vs fractional-free-convolution density,
iid seed), §6.iv (jitter floor per s, iid seed), and the §9 adversarial literature pull.

## 2. Free-convolution evaluator — closed-form gates (scope §4 v1.2)

Evaluator: `free_conv.py` (Belinschi–Bercovici subordination per Will's design — route, empirical
-measure reference, atom threshold, and the two known-answer gates all pinned in scope §4 BEFORE
the code existed). Artifact: `freeconv_gates.json`. Build order held: subordination core → the
two closed-form gates → (checkpoint reported here) → empirical input → §6.iii.

- **Gate S (semicircle, smooth input):** sc(1)^⊞κ vs sc(√κ) closed form, κ ∈ {1.5, 2, 4, 8, 16},
  interior grid |x| ≤ 0.95·edge. Worst density deviation 1.06×10⁻⁷ (tol 10⁻⁴), worst same-grid
  mass deviation 4.9×10⁻⁷, worst ε-doubling deviation 1.1×10⁻⁷.
- **Gate B (Bernoulli, atomic input):** closed form derived via R-transform before coding
  (a.c. density κ√(4(κ−1)−x²)/(2π(κ²−x²)); κ = 2 collapses to the arcsine law — internal
  consistency for free). κ ∈ {1.2, 1.5, 1.9, 2, 3, 5}: worst density deviation 1.63×10⁻⁶, worst
  mass deviation 4.8×10⁻⁷.
- **Atom threshold, predicted to the digit (scope §4):** pole-mass probe ε·|Im G(κ+iε)| at the
  atom location: κ = 1.5 → 0.250000 measured vs 1 − κ/2 = 0.25 predicted; κ = 3 → 0.000000.
  The mass-½ atoms survive below s = ½ and are gone above it, as the threshold formula requires.
- **Contraction certification:** worst subordination residual 9.99×10⁻¹⁴ (target 10⁻¹³) across
  every gate point; iteration count peaks at 2082 (κ = 16 near the real axis — the Denjoy–Wolff
  factor approaching 1 exactly where the scope said the R-transform route would have died).

**Verdict: PASS.** The evaluator has earned the empirical-measure input and the iid seed.

## 3. iid-seed unfolding residual, n-scaling gate (scope §6.iii, rule pre-committed v1.3)

Runner: `track0_iid_scaling.py`. Artifact: `track0_iid_scaling.json` (raw per-(s,n) records;
`derived_slopes_computed_at_read_time` added post hoc from the banked KS values, raw data
unchanged). Seed Uniform[−1, 1], RNG seed 0, n ∈ {1024, 2048, 4096}, s ∈ {0.1 … 0.9}.
Runtime 4 h 32 m single-core, dominated by the n = 4096 flow + high-s subordination.

**Verdict: PASS through the strict branch.** All 18 adjacent-n comparisons of the KS residual
vs the empirical-seed free-convolution reference are strictly monotone decreasing. The
escalation branch (INCONCLUSIVE-PENDING-REPLICATION) was not invoked; the 0.05 sanity ceiling
was never approached (worst KS at n = 4096: 0.00175, at s = 0.9).

| s | KS 1024 → 2048 → 4096 | slope (LS fit) | pop-ref diag @4096 | iters @4096 |
|---|---|---|---|---|
| 0.1 | 0.00111 → 0.00062 → 0.00031 | −0.91 | 0.0068 | 241 |
| 0.3 | 0.00125 → 0.00065 → 0.00034 | −0.95 | 0.0057 | 744 |
| 0.5 | 0.00162 → 0.00084 → 0.00042 | −0.97 | 0.0053 | 1670 |
| 0.7 | 0.00256 → 0.00132 → 0.00064 | −1.00 | 0.0056 | 3906 |
| 0.9 | 0.00739 → 0.00349 → 0.00175 | −1.04 | 0.0087 | 14792 |

(Full 9-row table in the artifact.)

- **Slope, recorded separately from the verdict per the pre-commitment:** ≈ −1.0 in n at every
  s, uniformly steeper than the −1/2 fluctuation-dominated signature the frame named as healthy.
  **Filed (2026-08-11, Will's read, adopted) as a SECOND WITNESS for the ceiling fact below, not
  an anomaly:** KS ~ 1/m is the CDF-discrepancy scaling of a rigid process, n^(−1/2) of an
  independent-increments one; the −1/2 pre-frame assumed the flowed set would still be
  fluctuation-dominated at the measured s, and the ceiling fact says it isn't, anywhere on the
  grid. Two mechanically independent readouts, one conclusion: everything from s = 0.1 up is
  already crystal. The pre-frame was wrong for a coherent reason. No high-s flattening
  appeared, so the ε-trace adjudication was not needed (ε-doubling deviations 0.8–2.9×10⁻²
  in density units; CDF-level KS sits 1–2 orders below, as expected from integration).
- **Empirical-reference design vindicated at scale:** the population-law diagnostic runs 5–20×
  above the empirical-reference residual at matched (s, n) — that gap is the seed-sampling
  offset the gate would otherwise have spent its budget on. Worst mass defect 9.1×10⁻⁴, logged
  not hidden.
- **Subordination cost, measured for §6.iv to inherit:** iteration counts grow steeply in s on
  the empirical measure — 241 (s = 0.1) → 14,792 (s = 0.9) at n = 4096, vs ≤ 2,082 for the
  smooth closed-form gates even at κ = 16. Converged and certified everywhere (residual
  < 10⁻¹³), but the jitter-floor run's cost model must use these counts, not the gate-run's.
- **★ Design fact for the sealed phase (instrument property, not a science claim):** the iid
  seed's bulk is already at the crystalline ceiling at the FIRST grid point — 1 − ⟨r̃⟩ ranges
  10⁻⁵ (n = 1024, s = 0.1) down to 10⁻⁷, i.e. Hermite-ceiling level, at every sampled s, with
  Σ²(L=8) at 0.00–0.04. Crystallization of this seed is essentially complete before s = 0.1 at
  these n. **Consequence: the sealed rate question's action lives at small s, and the science
  s-grid must be log-spaced down to s ~ O(1/n).** Filed as an s-grid design output of Track-0.
  Deliberately NOT done here, to keep the seal honest: no rate was fitted, and no second seed
  class was run or compared — the rate-universality question remains fully open.
