# The Khinchin Landscape — validation report

**Run:** 2026-08-03 · Phase 0 (N=4096, D=512, B=2048) and Phase 1 (N=65536, D=2048, B=8192)
**Box:** local 5900x, 24 threads, 15 GB. Production field: **14.1 s** wall on 22 workers.
The xeon was not needed — the master array is 256 MB and the work is bigint-CPU-bound,
where this box is faster.

---

## 1. Gate outcomes

| Gate | Verdict | Number |
|---|---|---|
| G0a 1/φ: K_n ≡ 1 | **PASS** | max abs dev `0.0` over 2048 depths (exact) |
| G0b √2−1: K_n ≡ 2 | **PASS** | max abs dev `0.0` (exact) |
| G0c √3−1 → √2 at n=2000 | **PASS** | dev `0.0` (exact at even n) |
| G0d e−2 vs (2^m·m!)^{1/3m}, m=500 | **PASS** | rel err `1.6e−15` |
| G0e Liouville-type masks early | **PASS** | engine depth 10 = predicted 10, reason `precision` |
| **G0f engine vs closed form** (added) | **PASS** | all 5 anchors match to their exact horizon |
| G1a median K within 2% of K₀ | **PASS** | `2.684837` vs K₀ `2.685452`, rel err **0.023%** |
| G1b a₁ vs its exact law | **PASS** | χ²=0.019, dof 15, p≈1.0 |
| G1c a₆₄ vs Gauss–Kuzmin | **PASS** | χ²=18.08, dof 15, **p=0.258** |
| G2 nothing past the horizon | **PASS** | 0 finite values past horizon; masked fraction **0.0** |
| G3 a≥2 rate field | **PASS** | φ≡0 exact, √2−1≡1 exact, generic median `0.5849609` vs `0.5849625` (rel err 2.7e−6) |

**G0f is an addition.** As specified, G0a–G0d test only closed-form quotient
sequences and never touch the Euclid engine — they would pass with the engine
entirely broken. G0f runs the engine on a B-bit rational for each anchor and
requires the quotients to match the closed form up to that anchor's predicted
horizon. All five match exactly, and every stop depth equals its predicted budget
(φ 1429, √2−1 780, √3−1 1045, e−2 388, Liouville 8 at B=2048).

---

## 2. Two defects found in the spec

### 2.1 The golden grid offset makes every column a quadratic irrational — CORRECTED

Spec §3.2 offsets the grid by ξ = 1/φ, so α_i = (i + (√5−1)/2)/N. Every such column
satisfies the integer quadratic (2Nα − 2i + 1)² = 5: **every column is a quadratic
irrational in Q(√5)** — eventually-periodic CF, formally the measure-zero exceptional
set, never a generic point. The grid was built out of exactly the material the
landscape exists to contrast against.

It is not benign. `grid_audit.py`, 8192 columns at production parameters (D=2048,
B=8192, lattice N=65536), bootstrap CI on mean S at depth 2048:

| offset | median K @2048 | rel | CI covers log₂K₀? |
|---|---|---|---|
| **golden 1/φ (spec)** | **2.6999** | **+0.54%** | **NO** |
| π−3 | 2.6850 | −0.02% | yes |
| ∛2−1 | 2.6858 | +0.01% | yes |
| ln 2 | 2.6846 | −0.03% | yes |
| stratified jitter | 2.6864 | +0.03% | yes |
| random reals | 2.6844 | −0.04% | yes |

At the Phase-0 scale the bias is worse (+1.35%, ~11σ). The π-offset grid has
*identical lattice geometry*, which isolates the offset itself rather than the
flare structure as the cause.

**Correction applied:** default offset is now **ξ = π − 3** (`kcore.grid_offset`).
π−3 is transcendental, so α_i = (i + ξ)/N is transcendental for every i — no column
is algebraic, let alone quadratic, which removes the defect at theorem level rather
than by hope. Genericity of any one such CF remains conjectural, as it does for
every named real; the audit table is the empirical warrant. The spec-literal
`golden_phi` offset is retained as a selectable option for comparison.

### 2.2 Gate G1's a₁ test names the wrong law — CORRECTED

Spec §4 G1 requires the empirical distribution of a₁ to match Gauss–Kuzmin
P(a₁=k) = log₂(1+1/(k(k+2))). On a Lebesgue-uniform grid that is simply the wrong
law: a₁ = ⌊1/α⌋ for α uniform has the **exact** distribution 1/(k(k+1)) — e.g.
P(a₁=1) = 1/2, not log₂(4/3) = 0.415. Gauss–Kuzmin is the invariant law of the
*Gauss measure*, approached as n→∞ (Kuzmin/Wirsing, rate ≈0.303ⁿ), not the law of
the first quotient.

Tested as written, the gate fails catastrophically: **p = 1.1e−113** on the
production field. Tested against the correct law: **p ≈ 1.0**.

**Correction applied:** split into G1b (a₁ vs its exact law 1/(k(k+1))) and G1c
(a₆₄ vs Gauss–Kuzmin, where the transfer operator has long converged; p = 0.258).
R5's centre panel renders this correction directly.

---

## 3. Masking honesty (G2)

**The trust horizon never binds in the production field.** All 65,536 columns reach
the full depth D=2048; masked fraction is exactly 0.0 at every row, and
`stopped by: depth=65536, precision=0`. B=8192 buys a typical depth of
≈(B−G)/(2 log₂ L) ≈ 2374 against D=2048, so the budget is over-provisioned by ~15%
and every column exhausts the depth axis before its precision.

This means **G2 passes trivially** and the masking machinery is *not* exercised by
the field. It is exercised only by the Liouville-type anchor, which masks at depth
10 exactly as predicted (G0e), and by the S1 burn-in region (n<n₀), rendered
achromatic grey in R6. Reported here rather than presented as a hard-won pass.

Headroom, if a deeper run is ever wanted: D could rise to ~2370 at the same B, or B
could drop to ~7100 at the same D, at no cost. The run is 14 s; depth is not the
binding constraint.

---

## 4. What the field measured back

### 4.1 The partial quotients are correlated, and the field recovers the GKW constant

Standardising K_n by the naive i.i.d. Gauss–Kuzmin sd left sd(z) = **0.932 at every
depth** (n = 16…2048) — flat, so not a finite-n artifact. The cause is that the a_k
are not independent: the CLT scale for a Birkhoff sum is
σ_B² = Var(f) + 2Σ_k Cov(f, f∘T^k). Measured from the master array:

| lag | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Cov(log₂a_k, log₂a_{k+lag}) | −0.2586 | +0.0883 | −0.0249 | +0.0086 | −0.0019 | +0.00004 |

The autocovariances **alternate in sign and decay geometrically with ratio ≈ −0.30** —
the Gauss–Kuzmin–Wirsing constant λ = 0.3036300…, the second eigenvalue of the
transfer operator, falling straight out of the landscape. This gives
σ_B = 1.5946 against the marginal 1.7127, predicting sd(z) = 0.9310 vs 0.932
observed. R1z now standardises by σ_B derived live from the field (not a literal),
and |z|>3 lands at **0.2665%** against N(0,1)'s 0.2700%.

**Antibody (binding):** this is the shelf-identity side of the Gauss-map spectral
story that CP2 already owns, independently re-measured from a fluctuation field built
to look at something else. Corroboration of the correlated-quotient picture, **not a
new weld**; no caption may imply the landscape establishes a link it re-measures.

Marginal Var(log₂a) from the field is 2.9247 vs Gauss–Kuzmin theory 2.9334 — an
independent check of the marginal law at second order.

### 4.2 The residual tail deficit is finite-n skewness

Before the σ_B correction the |z|>3 rate was low for a second reason worth
separating: log₂a is heavy-tailed on the right and bounded below by 0, so S_n is
right-skewed at small n and the two tails are wildly asymmetric, converging as the
CLT takes hold:

| n | skew | P(z<−3) | P(z>+3) |
|---|---|---|---|
| 16 | 0.403 | 0.0015% | 0.2762% |
| 64 | 0.191 | 0.0122% | 0.1648% |
| 256 | 0.099 | 0.0397% | 0.1144% |
| 2048 | 0.014 | 0.0534% | 0.0671% |

Mean z → 0 across the same range (−0.026 → +0.0017): the field converges to K₀.

### 4.3 The exceptional set cannot appear in this render — by construction

Spec §1 wants "the measure-zero exceptional set showing as veins that refuse."
A Lebesgue-sampled grid contains no such column, with probability 1. R1z is the
render that can answer this: at constant contrast across all depths a refusing
column would saturate as a vein at every depth, and none does — the standardised
field is N(0,1) noise everywhere. The exceptional set is absent **by construction,
not by failure of resolution or depth**, and no increase in N, D or B will produce
it. It appears in R2/R4 only as the *inserted exact anchor strip*, which is labelled
in-figure as not being grid data.

What the grid *does* show near 1/φ is real and is an absence: badly-approximable
numbers admit no strong rational approximations, so the neighbourhood is comparatively
free of flares — "noble quiet" as a property of the surroundings.

---

## 5. Render notes

- **Colour:** `berlin` (Crameri, perceptually uniform diverging), centred on
  log₂K₀, cool below Khinchin / warm above, neutral-dark at K₀, achromatic grey
  for masked. Rate field: `cividis` (perceptually uniform, CVD-safe sequential).
  The two-series categorical pair (#3987e5 / #d95926) passes all six checks of the
  palette validator on the dark surface (worst adjacent CVD ΔE 26.8).
- **Spec §5 states the diverging centre as log₂K₀ ≈ 1.4253.** The correct value is
  **1.4251655**; 1.4253 corresponds to K = 2.6859. Minor, but it is the colour centre.
- **Display reduction is by stride, not averaging.** Averaging f adjacent columns
  divides the per-column spread by √f — which is the entire signal — and it silently
  rendered the standardised field as a dead N(0,1/16) image before this was caught.
  Every displayed pixel column is now one real column; the cost is that a flare in a
  skipped column is not shown, which the native-resolution zooms cover.
- **The zooms use a log depth axis plus a raw-quotient panel.** On a linear axis
  ~95% of pixels sit at n>100, by which point a rational flare — one enormous
  quotient at n≈2 — has washed out of the running mean entirely. R3 on the original
  linear-K layout showed literally nothing at α=1/2. The flare is a shallow, raw-quotient
  phenomenon and is now rendered as one.
- **16-bit masters** are true single-channel PNGs at native resolution
  (65536×2048) with a sidecar JSON giving the exact inverse scaling; pixel value 0
  is reserved for masked.

## 6. S1 burn-in sensitivity (mandatory, spec §5b)

| n₀ | median shadow K | mean shadow K |
|---|---|---|
| 16 | 2.2552 | 2.2012 |
| 64 | 2.4550 | 2.4226 |

The burn-in dependence is large — 9% between the two — which is the point: S1 is a
**downward-biased** estimate of liminf K, the running min from n₀ converging to the
tail-inf (≤ liminf), with transient dips biasing it low. It is captioned in R6 as
"running-min shadow of K (n₀ = 64)" and nowhere as liminf K. Disagreement set
(K within 5% of K₀ but shadow below 0.75·K₀): **2.26%** of columns, rendered as the
R6 rug, illustration only.

## 7. Deviations from spec, in one place

1. Grid offset ξ = π−3, not 1/φ (§2.1 above). **Load-bearing.**
2. G1's a₁ law corrected and split into G1b/G1c (§2.2). **Load-bearing.**
3. G0f added — the engine was otherwise untested by G0 (§1).
4. R1z added: depth-standardised companion. The spec-literal absolute render is
   a near-black rectangle below n≈300 because the spread falls as 1/√n; R1z is the
   view in which the theorem's content, and the absence of exceptional veins, is legible.
5. Zoom layout: log depth + raw-quotient panel (§5).
6. Display reduction by stride, not column-mean (§5).
7. Anchors are evaluated at depth 2048 regardless of the phase's field depth D,
   since closed-form quotients cost nothing and G0c/G0d require n=2000/1500.
8. **R7 added — constructed exceptional atlas.** §1's "veins that refuse" cannot be
   sampled (measure zero at any resolution), so R7 exhibits them instead: bounded-type
   F_m (quotients ≤ m, the Hensley / Jenkinson–Pollicott Cantor sets), metallic
   columns, noble tails, arithmetic-growth e-type classes and a Liouville escapee,
   beside a panel of sampled grid columns. Constructed sequences have exact CFs at
   every depth, so no trust horizon applies; the grey tail on the Liouville column is
   the generator cap (k≤24), not a precision mask. Every panel is labelled
   sampled-vs-constructed and the two are never mixed on one axis. §1 is amended
   accordingly in EPISTEMIC_STATE.md.
9. Phase 3 sonification not attempted — separate go/no-go per spec §8.

## 8. The recalled −1.6%: chased and resolved

`chase_preview_number.py`, at the exact preview configuration (N=4096, D=512, B=2048),
settles it three ways.

**It is a depth, not a defect.** Median K crosses −1.6% at depth **n ≈ 20** on both
grids — golden −1.55%, corrected π−3 −1.81% at n=20. A clean grid shows the same
number, so it is not the offset.

**The mechanism is median-vs-mean skew, not slow convergence.** E[log₂K_n] = log₂K₀
*exactly* at every n; the centre never converges slowly. But log₂a is heavy-tailed on
the right and bounded below by 0, so S_n is right-skewed and its median sits below its
mean, closing as the skew decays (0.403 at n=16 → 0.014 at n=2048, §4.2). Median K is
therefore below K₀ at shallow depth on any grid and rises through it.

**Sign alone acquits it.** Every reading that carries the defect's fingerprint is
*positive*, because quadratic irrationals of large discriminant carry a larger
period-average log a than Khinchin:

| statistic (preview config) | golden | π−3 (clean) | contamination signature? |
|---|---|---|---|
| median K at depth 20 | −1.55% | −1.81% | **no — clean grid shows it too** |
| median K at deepest depth | +1.35% | +0.06% | yes |
| median of per-column time-averaged K | +1.63% | +0.35% | yes |
| pooled median over all (n, column) | +0.97% | −0.11% | yes |

The near-miss is the third row: +1.63% has the same magnitude as −1.6% with opposite
sign, and it *is* a contamination signature. But the sign is not a detail — the defect
can only push K up.

**The operational lesson.** At n≈20 the defect is not detectable at any sample size
worth having: golden-vs-clean separation is −0.50σ at n=16 and +0.26σ at n=32, first
exceeding 3σ at n=64 and saturating at 6–7σ for n≥128. A preview evaluated shallower
than n≈64 **cannot** catch this defect. The number was not waved through; it was
unobservable.

**One hypothesis raised and refuted.** That the preview read at a shallow depth because
G1a evaluates at the "deepest *common* unmasked depth" — a min over columns, which one
unlucky column could drag down. Tested: the per-column horizon distribution is tight
(at B=1000, min 243 against median 271 over 4096 columns), so a correct horizon rule
never lands the gate near depth 20. The min-over-columns design is still fragile in
principle and worth watching, but it is not what happened.
