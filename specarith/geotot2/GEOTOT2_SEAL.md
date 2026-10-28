# GEO-TOT2 seal — prime powers in (10⁶, 10⁸] against size-matched primes. Nothing above q = 10⁶ counted at sealing

Brief: Will, 2026-10-28 ("GEO-TOT2: seal both"; then "Price (10⁶, 10⁸] … Seal one range only"), both filed verbatim in
`../ph2/PH2_DECISIONS_2026-10-07.md`. Step 0: `../geotot1/GEOTOT1_PP_STEP0.md`. Code: `geotot2.py` (plan / enum / read).
**Sealed plan: `results/PLAN_1e8.json`** (seen range q ≤ 10⁶ and deterministic arithmetic only). `results/PLAN.json` is
the (10⁶, 10⁷] alternative, kept for the record of the range choice (§5).

## 1. Quantities
- v_N(q) = c_N(q)·(q/φ(q)) / q^(2δ_N − 1), N = 3, 4, 5 (GEO-TOT1 conventions: canonical CF, δ_N Pollicott–Vytnova).
- **Matched primes:** the 4 primes nearest q (ties to the smaller). Excess(q) = v_N(q) − mean of v_N over them.
- **Fold count** at a square q = r²: F_N(q) = distinct canonical E_N keys of r² from Niederreiter's folding of the keys
  of r ([b₁…b_s] ↦ [b₁, …, b_{s−1}, b_s + 1, b_s − 1, b_{s−1}, …, b₁]; each asserted to have denominator r² and to be in
  lowest terms). Scaled: f_N(q) = F_N(q)·(q/φ(q)) / q^(2δ_N − 1). Fold counts use only the keys of r < 10⁴ (seen
  range) and are in the plan.

## 2. Sets (10⁶ < q ≤ 10⁸, all fresh)
- **(B) 1,061 prime squares p²,** 1009 ≤ p ≤ 9973. The 26 squares of higher prime powers (p^{2j}, j ≥ 2: 2²⁰ … 2²⁶,
  3¹⁴, 3¹⁶, 5¹⁰, 7⁸, 11⁶, 13⁶, 17⁶, 19⁶, 37⁴ … 97⁴) are reported descriptively (excess and fold), never in a verdict;
  H_seen is built from prime squares only. (The "290" in the 2026-10-28 report for (10⁶, 10⁷] counted every even prime
  power; the prime squares there are 278.)
- **(A) 74 odd prime powers p^k,** k odd ≥ 3, p ≥ 7 (q = p·r² with p > N + 1: no folding for N ≤ 5): 65 cubes
  101³ … 463³, p⁵ for p = 17 … 37 (6), 11⁷, 13⁷, 7⁹. (Odd powers of 2, 3, 5 fold at some N ≤ 5 and are excluded.)
- 5,805 q in all (targets and matched primes). Cost model 12.46 spot core-h (GEO-TOT1 ran at 0.86× this model:
  ≈ 10.7); one process on spot, 20 numba threads, ≈ 40 min wall; cost checks after the first of 20 chunks and at 25 /
  50 / 75% (stop above 1.25×).

## 3. (A) zero excess at the non-foldable odd prime powers
Per N: mean excess over the 74, SE = SD/√74. **UNPOWERED** if SE > fold-size/2, fold-size = the mean f_N over the 1,061
fresh squares (0.0243, 0.0086, 0.0043 for N = 3, 4, 5); else **PASS** if |mean| ≤ 2·SE, **FAIL** otherwise.

| N | predicted SE | fold-size/2 | predicted |
|---|---|---|---|
| 3 | 0.0116 | 0.0122 | powered (borderline) |
| 4 | 0.0029 | 0.0043 | powered |
| 5 | 0.0015 | 0.0022 | powered |

## 4. (B) R_N = mean excess / mean f_N over the 1,061 prime squares
- SEs by a bootstrap over the squares (10,000 resamples, seed 20261029 = 20261028 + 1). Pooled R = inverse-variance-
  weighted mean of R_3, R_4, R_5 with weights from their SEs; its SE from the same bootstrap.
- **H_fold:** R = 1. **H_seen:** R equal to the seen values (103 prime squares, 317 ≤ p ≤ 997, same code):
  R_3 = 0.871 ± 0.291, R_4 = 0.273 ± 0.227, R_5 = 0.707 ± 0.183, pooled 0.601 ± 0.166.
- **Reading** per N and pooled: consistent with H_fold iff |R − 1| ≤ 2·SE; consistent with H_seen iff |R − R_seen| ≤
  2·√(SE² + SE_seen²). "pure folding" = H_fold-consistent and H_seen-inconsistent; "displacement" = the reverse;
  otherwise "unpowered/unexplained".

## 5. Power, and the range choice (Will: seal the extended range iff it lifts N = 5 or the pooled reading to ≥ 2 sd)
Noise model: on the seen primes, the SD of v_N(q′) − mean of its 4 nearest other primes, per tenth-decade bin over
10⁴ … 10⁶ (400 primes per bin), fitted as a power law in q (SD ∝ q^−0.16, q^−0.24, q^−0.26) and extrapolated to each
fresh q. Fold sizes from the actual fold counts. Normal approximation; separation = |1 − R_seen| / √(SE_R² + SE_seen²).

| | (10⁶, 10⁷]: SE_R | separation | (10⁶, 10⁸]: SE_R | separation | P(pure folding \| H_fold) | P(displacement \| H_seen) |
|---|---|---|---|---|---|---|
| N = 3 | 0.218 | 0.36 | 0.120 | 0.41 | 0.00 | 0.18 |
| N = 4 | 0.147 | 2.69 | 0.084 | 3.01 | 0.95 | 1.00 |
| N = 5 | 0.139 | 1.27 | 0.083 | 1.46 | 0.07 | 0.94 |
| pooled | 0.118 | 1.96 | 0.068 | **2.23** | 0.70 | 1.00 |

(The probability columns are for (10⁶, 10⁸]; for (10⁶, 10⁷] they were 0.00 / 0.08, 0.87 / 1.00, 0.09 / 0.55,
0.45 / 0.91.) The pooled SE is the independent-N value × 1.30, the seen ratio of the bootstrap pooled SE to the
independent-N value.

**Choice: (10⁶, 10⁸].** Basis: the pooled separation rises from 1.96 to 2.23 sd (≥ 2); N = 5 rises only to 1.46. N = 4
is the decisive arm in either range. Limits stated now: H_seen's own SE caps the separation even with unlimited fresh
data (N = 3: 0.44 sd, N = 4: 3.21, N = 5: 1.60), so N = 3 cannot separate the hypotheses in any range; and the noise
model is extrapolated up to two decades beyond its fit range (10⁴ … 10⁶).

## 6. Witness for (B), seen squares only (p ≤ 997) — passes; it shows no bias, not resolution
H_fold is made true by construction: each seen square's value is replaced by its 5th-nearest prime's value (real noise,
not one of the 4 matched primes) plus a seeded subset of (1 − x) of its fold keys. The statistic must read R = 1 − x
within 2 SE for x = 0.25 and 0.5 (x = 0 reported):

| x | R_3 | R_4 | R_5 | pooled |
|---|---|---|---|---|
| 0 | 0.968 | 1.000 | 1.047 | 1.009 |
| 0.25 | 0.724 | 0.750 | 0.798 | 0.761 |
| 0.5 | 0.468 | 0.500 | 0.547 | 0.509 |

All within 2 SE (SEs 0.20–0.24 per N, 0.17 pooled). **Recorded (Will): the witness shows the estimator is unbiased
(misses −0.03 … +0.05 at every x, and R moves by exactly the removed fraction, since the same base noise is used at every
x); it does not show that x = 0.25 can be resolved at the seen sample size (x = 0.25 is about 1.2 SE from x = 0).** The
fresh read's resolving power is §5. (Removing x of the fold keys from the real seen counts gives R = R_seen − x by
construction, which cannot read 1 − x at N = 4 where R_seen = 0.27.)

## 7. Checks run before sealing (seen data only)
- The chunked enumeration reproduces GEO-TOT1's φ and counts exactly on q = 1000 … 1399.
- `read` on the seen squares (and seen cubes 47³ … 97³ in the (A) slot) returns H_seen's R exactly (0.8707, 0.2729,
  0.7071).

## 8. Order
Seal (tag `geotot2-seal`) → OpenTimestamps stamp → enumerate the 5,805 q on spot (outputs hashed, nothing displayed) →
Bitcoin attestation verified on two explorers → read twice in separate processes, `cmp` byte-identical. φ(q) of every
target checked against q − q/p. Pushes stay with Will.

## 9. Pins
Listed with their committed sha256 in the stamp manifest (`timestamps/`): `GEOTOT2_SEAL.md`, `geotot2.py`,
`results/PLAN_1e8.json`, `results/PLAN.json`, `run_geotot2_spot.sh`, and the GEO-TOT1 files it imports unchanged
(`../geotot1/geotot1.py` bb1d0bad…5474, `../geotot1/geotot1_analyze.py` 58a12452…a9f) and `../geotot1/GEOTOT1_PP_STEP0.md`.
Spot environment as GEO-TOT1 (ph6c: Python 3.12.15, numpy 2.5.3, numba 0.68.0).
