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
