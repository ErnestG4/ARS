# GEO-TOT2 seal — STATUS: DRAFT for Will (power reported before sealing, as asked). Nothing above q = 10⁶ counted

Brief: Will, 2026-10-28 ("GEO-TOT2: seal both"), filed verbatim in `../ph2/PH2_DECISIONS_2026-10-07.md`. Step 0:
`../geotot1/GEOTOT1_PP_STEP0.md`. Code: `geotot2.py` (plan / enum / read). Plan output: `results/PLAN.json` (seen range
q ≤ 10⁶ and deterministic arithmetic only).

## 1. Quantities
- v_N(q) = c_N(q)·(q/φ(q)) / q^(2δ_N − 1), N = 3, 4, 5 (GEO-TOT1 conventions: canonical CF, δ_N Pollicott–Vytnova).
- **Matched primes:** the 4 primes nearest q (ties to the smaller). Excess(q) = v_N(q) − mean of v_N over them.
- **Fold count** at a square q = r²: F_N(q) = distinct canonical E_N keys of r² from Niederreiter's folding of the keys
  of r ([b₁…b_s] ↦ [b₁, …, b_{s−1}, b_s + 1, b_s − 1, b_{s−1}, …, b₁]; each asserted to have denominator r² and to be
  in lowest terms). Scaled: f_N(q) = F_N(q)·(q/φ(q)) / q^(2δ_N − 1). Fold counts use only the keys of r ≤ 3162 (seen
  range); they are in `results/PLAN.json`.

## 2. Sets (10⁶ < q ≤ 10⁷, all fresh)
- **(B) 278 prime squares p²,** 1009 ≤ p ≤ 3137. *Correction:* the "290" in the 2026-10-28 report counted every even
  prime power; 12 of those are p^{2j}, j ≥ 2 (2²⁰, 11⁶, 37⁴, 41⁴, 43⁴, 2²², 3¹⁴, 13⁶, 47⁴, 7⁸, 53⁴, 5¹⁰). They are
  squares of prime powers, not of primes, and are reported descriptively (excess and fold), never in a verdict. The
  seen squares that set H_seen are prime squares only.
- **(A) 25 odd prime powers p^k,** k odd ≥ 3, p ≥ 7 (q = p·r² with p > N + 1, so no folding for N ≤ 5): 22 cubes
  101³ … 211³ and 17⁵, 19⁵, 23⁵. (2²¹, 2²³, 3¹³, 5⁹ fold at some N ≤ 5 and are excluded.)
- 1,575 q in all (targets and their matched primes). Cost model 0.39 spot core-h (GEO-TOT1 measured 0.86× its model).

## 3. (A) zero excess at the non-foldable odd prime powers
Per N: mean excess over the 25, SE = SD/√25. **UNPOWERED** if SE > fold-size/2, fold-size = the mean f_N over the 278
fresh squares (0.0335, 0.0135, 0.0072 for N = 3, 4, 5); else **PASS** if |mean| ≤ 2·SE, **FAIL** otherwise. Predicted SE
(noise model below): 0.025, 0.0068, 0.0035, so N = 3 and 4 are expected UNPOWERED and N = 5 is borderline (0.0035
against 0.0036).

## 4. (B) R_N = mean excess / mean f_N over the 278 squares
- SEs by a bootstrap over the squares (10,000 resamples, seed 20261028). Pooled R = inverse-variance-weighted mean of
  R_3, R_4, R_5 with weights from their SEs; its SE from the same bootstrap.
- **H_fold:** R = 1. **H_seen:** R equal to the seen values (103 prime squares, 317 ≤ p ≤ 997, same code):
  R_3 = 0.871 ± 0.291, R_4 = 0.273 ± 0.227, R_5 = 0.707 ± 0.183, pooled 0.601 ± 0.166.
- **Reading** per N and pooled: consistent with H_fold iff |R − 1| ≤ 2·SE; consistent with H_seen iff |R − R_seen| ≤
  2·√(SE² + SE_seen²). "pure folding" = H_fold-consistent and H_seen-inconsistent; "displacement" = the reverse;
  otherwise "unpowered/unexplained".

## 5. Power (before sealing)
Noise model: on the seen primes, the SD of v_N(q′) − mean of its 4 nearest other primes, per tenth-decade bin over
10⁴ … 10⁶ (400 primes per bin), fitted as a power law in q and extrapolated to each fresh q (SD ∝ q^−0.16, q^−0.24,
q^−0.26). Fold sizes from the actual fold counts. Normal approximation, 20,000 draws per cell.

| N | predicted SE_R | separation (sd) | P(pure folding \| H_fold) | P(displacement \| H_seen) |
|---|---|---|---|---|
| 3 | 0.218 | 0.36 | 0.00 | 0.08 |
| 4 | 0.147 | 2.69 | 0.87 | 1.00 |
| 5 | 0.139 | 1.27 | 0.09 | 0.55 |
| pooled | 0.118 | 1.96 | 0.45 | 0.91 |

The pooled SE is the independent-N value inflated by 1.30, the seen ratio of the bootstrap pooled SE to the
independent-N value (the three N share their q). **N = 4 is the decisive arm. N = 3 cannot separate the hypotheses**
(H_seen's own SE, 0.29, and R_seen = 0.87 near 1). N = 5 and the pooled reading are weak against H_fold.

## 6. Witness for (B), seen squares only (p ≤ 997) — PASSES
H_fold is made true by construction: each seen square's value is replaced by its 5th-nearest prime's value (real noise,
not one of the 4 matched primes) plus a seeded subset of (1 − x) of its fold keys. The statistic must read R = 1 − x
within 2 SE for x = 0.25 and 0.5 (x = 0 reported):

| x | R_3 | R_4 | R_5 | pooled |
|---|---|---|---|---|
| 0 | 0.968 | 1.000 | 1.047 | 1.009 |
| 0.25 | 0.724 | 0.750 | 0.798 | 0.761 |
| 0.5 | 0.468 | 0.500 | 0.547 | 0.509 |

All within 2 SE (SEs 0.20–0.24 per N, 0.17 pooled). What it shows: the estimator has no bias against a known R (misses −0.03 … +0.05 at every x), and R moves by exactly the removed fraction (the same base noise is used at every x). What it cannot show: resolution — x = 0.25 is only about 1.2 SE from x = 0 at the seen sample size; the power for the fresh read is §5. (Removing x of the fold keys from the real seen counts instead gives R = R_seen − x exactly, by
construction; that version cannot read 1 − x at N = 4, where R_seen = 0.27.)

## 7. Order
Seal (tag `geotot2-seal`) → OpenTimestamps stamp → enumerate the 1,575 q on spot (one process, numba threads; outputs
hashed, nothing displayed) → Bitcoin attestation verified on two explorers → read twice in separate processes, `cmp`
byte-identical. φ(q) of every target checked against q − q/p.

## 8. Pins
To be filled at sealing (`geotot2.py`, `results/PLAN.json`, and the GEO-TOT1 kernel `geotot1.py` bb1d0bad…5474 and
`geotot1_analyze.py` 58a12452…a9f, imported unchanged).
