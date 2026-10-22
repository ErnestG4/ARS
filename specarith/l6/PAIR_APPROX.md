# Pair-connected approximation for the block variance (round 72; EXPLORATORY; committed before computing)

**Status:** exploratory theory. It is validated against the long CUE baseline first, and is **not applied to ζ**
until that validates (round 72). The n = 6 extension waits on this result.

## The approximation
Write each per-file estimator to leading order as μ̂ − μ = (1/n)·Σ_i φ_i, with φ_i the influence of level i, and let
W(G) = SE_boot(G)²·n be the moving-block bootstrap variance at block length G in unit-count form, the quantity L6
measured (`_var_table`). Split φ_i = k·δ_i + η_i, where:
- δ_i is the local relative density deviation, which varies slowly;
- k is the estimator's linear response to density;
- η_i is the remainder, correlated only at short range.

Keeping only covariance between distant parts that passes through the pair function (one "bond" through R₂ᶜ), a block
of G levels contributes Σ_block δ_i ≈ G − ℓ_G, where ℓ_G is the block's length. That has variance Σ²(G), the number
variance. So

  **W(G) ≈ A + k²·Σ²(G)/G**,

where A collects the short-range (η) part and does not depend on G. Everything arithmetic would enter through Σ²(G).
For ζ that is the pair statistic's Σ², which is not used here.

## Ingredients
- **k, the response, per (statistic, file geometry):**
  - Dilate a CUE sequence so the density rises by δ: positions x → x/(1 + δ), spacings s → s/(1 + δ). Run the
    identical estimator with no bootstrap.
  - k = (μ̂(+δ) − μ̂(−δ))/(2δ), at δ = 10⁻³ and 2·10⁻³ (a linearity check). Averaged over the 50 long CUE sequences,
    with SE from their spread.
  - For corrected (B), μ̂ = (k̄₃ − κ₃^sine)/Δκ₃, taken from `b2_est.zeros_stats`'s k̄₃, as in `b2_read.fit`.
- **Σ²(G):** the exact CUE_N number variance at N = 10⁵ (`l6_base.sigma2_exact`, gate 1's formula), at G = 300, 1,000,
  3,000 and 10,000. Route (a) and (A) block G spacings; corrected (B) blocks G unfolded units. At unit density both use
  Σ²(G).
- **Measured W(G):** per sequence se(G)²·n from `results/base/stats/stats_cue_*.json`. Mean and SE over the 50
  sequences, per file.

## Validation against the long CUE baseline (declared)
- **Parameter-free test:** the fall from G = 300 to 10⁴.
  - Measured: Δ_meas = W(300) − W(10⁴), averaged over sequences, with SE from the per-sequence differences.
  - Predicted: Δ_pred = k²·(Σ²(300)/300 − Σ²(10⁴)/10⁴), with SE from k's.
  - z = (Δ_meas − Δ_pred)/combined SE.
- **One-constant fit:** A per file by weighted least squares over the four G with k fixed, then the residual z at each
  G.
- **Validates, per statistic:** |z_fall| ≤ 3 for every file, and every residual |z| ≤ 3.
- **Power, reported with the result (TOOLKIT §9.D):** if the predicted fall is below 2 SE of the measured fall, the
  test cannot fail. Then the result is reported as **uninformative**, not as validated.
- **Also reported:** the pair share k²Σ²(300)/300 / W(300). That is the fraction of CUE's block variance this term
  carries at G = 300. It is a CUE quantity only.

Code: `round72.py resp` / `pair_summary` → `results/r72/resp_*.json`, `results/r72/PAIR_SUMMARY.json`.

## Result (`results/r72/PAIR_SUMMARY.json`; CUE only)
**Response k** (dμ̂/dδ, mean over 50 sequences, δ = 2·10⁻³):

| statistic | k | linearity (k at δ = 10⁻³ / k at 2·10⁻³) |
|---|---|---|
| route (a) | −13 to −39, rising in magnitude with height | 0.99 |
| (A) | −13 to −19 | 0.98 |
| corrected (B) | −1.2 to −1.4 ± 0.7–0.8 | −0.09 |

For corrected (B), the two step sizes disagree, so its k is noise-dominated and consistent with about 0: this κ₃
estimator barely responds to a uniform density change.

**The pair-connected term is negligible.** k²Σ²(300)/300 is 0.1–0.2% of CUE's W(300) for route (a) and (A), and about
0.001% for (B). Over 300 → 10⁴ the predicted fall is 0.05–0.15% of W(300), against measured falls of 7–17% ± 5%.

**Declared reading:**
- route (a): **uninformative**. The measured fall's SE swamps nothing the model predicts, and z_fall ≤ 2.4.
- (A) and corrected (B): **do not validate** (z_fall up to 3.6 and 3.4).

**Not applied to ζ.**

**Diagnosis (descriptive):**
1. **The validation target is contaminated.** CUE's measured fall at n = 10⁵ is mostly the moving-block bootstrap's
   G/n bias. The concatenation variant (n = 5·10⁶) sits 4–24% above the per-sequence W at G = 10⁴ (§13), about the
   size of the "fall". So the long CUE baseline's real G-dependence for these statistics is small, and the
   approximation's near-zero prediction is not contradicted by it. Equally, the approximation was never able to fail
   in the direction that matters.
2. **What is robust needs no ζ input.** The pair-connected channel carries ≤ 0.2% of CUE's block variance. Within this
   approximation, any Σ²(G) ≥ 0, ζ's included, can change W by at most that much.
   - So the zeros' deficits (zeros/long 0.18–0.77) cannot come through the density, or pair-connected, channel.
   - They must sit in the short-range part A, or in the cross-connections the approximation drops: correlation between
     the *shapes* of distant local configurations, not their densities.
   - This is a statement about the approximation's reach, computed on CUE. It is not a ζ prediction.
3. **Consequence for the n = 6 extension** (which waits on this result): the pair channel is ruled out as the carrier.
   An exact corrected-(B) block variance at n = 6 would include the higher cross-connections that this approximation
   drops. Whether to pursue it is Will's call.
