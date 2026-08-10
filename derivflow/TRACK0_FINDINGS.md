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
- Sealed rate question: **still unsealed**, per scope — pending the remaining §6 gates on the iid
  seed (unfolding residual vs the fractional-free-convolution density, jitter floor) and the
  pre-seal adversarial literature pull (2410.06403 v1→v2 diff + 2025–26 citation graph).

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
