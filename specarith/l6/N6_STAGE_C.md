# n = 6, stage (c): results as they come (method: `N6_STAGE_C_BOUND.md`)

## Steps 1–2: the n = 6 construction and its U(N) pointwise gate (`cs4/ratios_t6.py`; spot)
- The construction is `ratios_t5.Model` at n = 6. It is general in n, so no new transcription was needed.
- **Gate result: FAIL** (`cs4/results/n6c/UGATE6.json`), with tolerance 10⁻¹² + 10⁻⁶·|det|, pointwise:

  | N | configurations (8 each) | max relative difference | max absolute difference | result |
  |---|---|---|---|---|
  | 10 | spread over [0, 6) | 1.0·10⁻⁷ | 1.4·10⁻¹² | pass |
  | 10 | one pair 10⁻³ apart | 9.6 | 6.5·10⁻¹⁰ | **fail** |
  | 50 | spread over [0, 6) | 3.3·10⁻⁷ | 2.5·10⁻¹² | pass |
  | 50 | one pair 10⁻³ apart | 1.7·10⁹ | 3.4·10⁻⁸ | **fail** |
  | 50 | 3 + 3 at r = 5 | 1.9·10⁻⁷ | 3.1·10⁻¹² | pass |
  | 50 | 3 + 3 at r = 9 | 2.1·10⁻⁸ | 2.0·10⁻¹⁴ | pass |

- **The failure is near coincidence.** With a pair 10⁻³ apart, ρ₆ falls to 10⁻⁶–10⁻¹⁸, which is ∝ d², and the
  construction carries an absolute error of up to 3·10⁻⁸ there. That comes from cancellation between z-factors
  1/(1 − e^{−x}) at x ~ 10⁻³. Away from coincidence, the relative accuracy is 2·10⁻⁸–3·10⁻⁷.
- **By the committed rule, no ζ value is read** (no bound, no G-b3) until Will rules.
- **Relevance (for that ruling, not a ruling):** the quadratures that would use the construction never come near
  coincidence. Distinct Gauss–Legendre nodes, 6 per 4-unit window, are at least 0.54 apart, and the clusters are
  ≥ 20 apart in G-b1 and G-b3. An amended gate would test near-coincidence at the quadrature's minimum separation, or
  evaluate near-coincident configurations in mpmath. **That is Will's call.**

## Large-N diagnostic (not a gate; `cs4/results/n6c/LARGEN.json`)
The construction against the determinant in the 3 + 3 geometry (4 configurations each), max relative difference:

| N | r = 20 | r = 100 | r = 1000 |
|---|---|---|---|
| 10³ | 8.8·10⁻¹¹ | 7.4·10⁻¹⁴ | (r > N/2) |
| 10⁴ | 7.9·10⁻⁸ | 1.6·10⁻¹⁰ | 2.3·10⁻³ (a configuration with det 2.8·10⁻⁸) |
| 10⁵ | 1.8·10⁻¹¹ | 2.3·10⁻¹² | 7.1·10⁻¹² |

**At N = 10⁵ the construction is accurate to about 10⁻¹¹ out to r = 1000,** so G-b1 can use stage (a)'s N directly.
