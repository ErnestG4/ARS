# GEO1 seal: Peter's multiplicity correlations on fresh traces 10⁶ < t ≤ 3·10⁶

Brief: Will, 2026-10-30, option (a), filed verbatim in `ph2/PH2_DECISIONS_2026-10-07.md`. T₂ = 3·10⁶ and D23 on the 4090
were set by Will on 2026-10-31. Code: `geo1_peter_seal.py` and `geo1_peter_d23.py` (committed ec720afd before any run);
the noise-matched D23 variant was added before the seal (fe17838b, labelled there). Parameters:
`results/peter/seal/SEAL_PARAMS.json`. Order: seal → stamp → fresh run on spot → Bitcoin attestation verified on two
explorers → read twice → `cmp`. No statistic, and no class number, from the fresh range has been computed at the time of
sealing.

## 1. The prediction (zero parameters)

Peter, *Correlations of multiplicities in length spectra*, arXiv math/0104234 v1 (2002). The theorem block was read
verbatim (`GEO1_STEP0B_PETER.md`).

- α(n) = g(n) log n / n, where g(n) counts primitive hyperbolic classes of trace n (oriented, as Peter counts them).
- α̃ = α − 1.
- γ(r) = lim_N (1/N) Σ_{2<n≤N} α̃(n) α̃(n + r).
- The theorem (unconditional): γ(r) + 1 = Π_p (1 + Σ_{b≥1} A_r(p^b)).

`geo1_peter.py` evaluates the product over p ≤ 10⁵ and adds a bound on the tail. Each local factor was checked against
counted SL(2, ℤ/q) trace densities, for q = 2⁷, 3⁴, 5³, 7², 11² and r ≤ 24; the largest difference was 2.2·10⁻¹⁶. The
predictions are in `results/peter/PRED.json`. The tail adds at most 6·10⁻⁶ to any statistic's tolerance.

## 2. Fresh range and price

- t = 1,000,001 … 3,000,000, so discriminants d = (t² − 4)/u² ≤ 9·10¹².
- Production route, unchanged from Step 1: PARI `quadclassunit` for h, `quadunitnorm` for N(ε).
- Spot benchmarks per discriminant: 4.0 ms at d = 10¹², 4.6 ms at 10¹³, 4.9 ms at 10^13.5 and 6.2 ms at 10¹⁴. Factoring
  and `quadunitnorm` cost almost nothing.
- Model: 6.0 ms per t, about 3.3 core-hours. On spot that is about 13 minutes with 16 processes.
- The cost checks stop the run above 1.25× the model.

## 3. Statistics

- **Fresh window:** n ∈ [1,000,001, 2,999,880], N = 1,999,880 values. The same n are used for every lag, and n + r ≤ 3·10⁶.
- **Lags:** r = 0–13, 15, 16, 18, 20, 24, 30, 36, 60, 120. This covers small primes, prime powers (4, 8, 9, 16),
  composites and smooth lags (60, 120).
- **Primary statistics (22):** γ̂(r)/γ̂(0) for r ≠ 0.
- **Secondary statistics (23):** γ̂(0) and the raw γ̂(r) for r ≠ 0.
- **Summation:** numpy pairwise sums in float64, with no BLAS. This makes the read bit-reproducible.
- **Descriptive only:** block-jackknife SEs on the fresh window, with blocks of 10⁴.

## 4. Tolerance (fixed numbers, sealed; nothing at read time sets them)

For each statistic j:

tol_j = |trend_j| + Z_B · SE_j + tail_j,  with Z_B = Φ⁻¹(1 − 0.05/90) = 3.261 (Bonferroni over 45 statistics, two-sided).

**trend_j (the convergence trend on the development range).**
- Peter's theorem is a limit statement and gives no rate.
- In `geo1_peter_dev.py` (committed before it ran), the difference from the prediction is computed on the 8 disjoint
  quarter-decade windows 10⁴ … 10⁶.
- That difference is fitted by unweighted OLS against log n, and the fit is evaluated at the fresh window's mean log n
  (14.463).
- The same fit is applied to the ratio's difference.
- The fit is dominated by the noisier windows near 10⁴. Its value is therefore an allowance of the size of the
  development-range scatter, not a detected drift. It is used as committed; a weighted fit was not substituted after
  seeing the data.

**SE_j.** SE_j is the larger of two estimates:
- the development range's block-jackknife SE, scaled to the fresh N. This is the maximum of SE·√N over the
  quarter-decade windows k = 21, 22 and 23, divided by √N_F;
- the planted generator's SD over replicates at the fresh N.

**Which estimate binds.**
- The block-jackknife estimate is the larger one for all 45 statistics.
- Real α(n) is dominated by periodic structure from small primes. Primes between 10⁴ and 10⁶ change the block means but
  largely cancel over the whole window.
- That makes block jackknife conservative for the full-window mean. The development range agrees: its z-scores against
  block SE have RMS 0.59.

**tail_j.** The Euler-product truncation bound, propagated through the statistic.

**Resulting tolerances.**

| Statistics | Tolerance range | Statistics where \|trend\| exceeds the Z_B·SE term |
|---|---|---|
| Ratios | 2.2·10⁻⁴ to 1.4·10⁻³ | 15 of 22 |
| γ̂ | 6.0·10⁻⁵ to 7.9·10⁻⁴ | 12 of 23 |

Every tolerance is at most 0.32% of |prediction|. The smallest |prediction| is 0.101 for a ratio and 0.033 for γ(2).

## 5. Witnesses, D23 and power (all before the seal; `results/peter/seal/`)

**Planted generator.**
- Series: α(n) = δ_P(n + s) ξ(n).
- δ_P is the product of SL(2, ℤ/p^B) trace densities for p ≤ 997. B = 7, 4, 3, 2, 2, 2 for p = 2, 3, 5, 7, 11, 13, and
  B = 1 otherwise. That makes 168 tables. The closed form equals the counted densities for p ≤ 47, and every table has
  mean 1.
- Each prime power gets an independent uniform shift s.
- ξ is drawn i.i.d. from the development-range residual α/δ_P on n ∈ [316,228, 10⁶), normalised to mean 1.
- Its correlations are known exactly: γ(r) = Π_q mean(δ_q δ_q(· + r)) − 1 for r ≠ 0, and γ(0) = Π_q mean(δ_q²)·E[ξ²] − 1.

**The as-built generator is smoother than the real data.** Its SD is 0.30–0.84 times the real block-jackknife SE at the
k = 23 window, so a D23 on it alone is optimistic. A noise-matched stress variant was therefore added before the seal and
before it ran:
- ξ′ = 1 + c(ξ − 1), with c = 1.69 = 1/median(ratio);
- this variant's SD is 0.46–1.37 times the real SE (median 0.95).

**Seal gate**, fixed before the stress run: as-built SE-only rates ≥ 0.95, noise-matched full-tolerance rates ≥ 0.95, and
the null's primary FAIL rate ≥ 0.95. All hold.

| R = 2000 each | primary | secondary | joint |
|---|---|---|---|
| planted, as built, SE-only tolerance (vs exact planted) | 1.000 | 0.9995 | 0.9995 |
| planted, noise-matched, full tolerance | 1.000 | 0.999 | 0.999 |
| planted, noise-matched, SE-only (reported) | 0.999 | 0.9615 | 0.961 |
| matched-marginal independent-lag null (vs Peter), FAIL rate | 1.000 | 1.000 | — |
| planted without the 3-adic factor (vs full planted), FAIL rate | 1.000 | 1.000 | — |

**Power per statistic.** A statistic is UNPOWERED if its power is below 0.80.
- For r ≠ 0, ratio and raw: the FAIL rate under the matched-marginal null. This is 1.000 for all 44.
- For γ(0): the matched-marginal null preserves γ(0) by construction (its FAIL rate is 0.16, as designed). Its power is
  instead taken against the Euler product without p = 3, by normal approximation, giving 1.000.
- **No statistic is UNPOWERED.**

**Structure resolution (descriptive).** Power to tell Peter's product from the product without the prime p:
- 1.00 for p = 2, 3 and 5 at every statistic;
- 1.00 for p = 7 and 11 at every statistic except these raw γ, where the local factor is within the tolerance of 1:
  - p = 7: γ(4);
  - p = 11: γ(4), γ(7) and γ(18) (power ≤ 0.01), and γ(15) (power 0.37).
- Every ratio resolves all five primes.

**Witnesses at read** (same statistic code, fresh-window length):
- shuffled t (a seeded permutation of the fresh α̃): must FAIL;
- one matched-marginal null series: must FAIL;
- one planted series, compared with its exact values under the full tolerance: must PASS.

If any witness does otherwise, the read is VOID (witness).

## 6. Inputs (GRH)

**Production values are GRH-conditional.** h(d) from `quadclassunit` (Buchmann–McCurley) is conditional on GRH, and PARI
does not certify it. Every multiplicity g(t), and so every statistic here, is therefore GRH-conditional in its input. The
prediction itself (Peter's theorem) is unconditional.

**Independent check.**
- A seeded sample of 200 (t, u) from the fresh range, 44 of them with u > 1, is in `results/peter/seal/HSAMPLE.json`
  (seed 20261107). It was chosen from t alone.
- For each sample, the class number is recomputed by a different algorithm: PARI `qfbclassno`, the analytic class number
  formula in O(√d), which is also uncertified for d > 0.
- The unit norm is recomputed from the parity of the continued-fraction period of ω = (b + √d)/2, in pure Python. This
  agreed with `quadunitnorm` on all 10,067 discriminants checked (`CFCHECK.json`).
- The read compares (h, N(ε)) with the production rows by program and records only counts.
- If anything is missing or mismatched, the read is VOID (inputs). VOID (inputs) also applies to a coverage gap in the
  fresh t, a mismatched development-data hash (c72380f9…3258), or a mismatched pool-source hash.

## 7. Verdict lattice (`geo1_peter_seal.py read`)

| Condition | Verdict |
|---|---|
| Inputs fail | VOID (inputs) |
| Inputs pass; a witness misbehaves | VOID (witness) |
| Otherwise | Primary is PASS if every powered ratio is within tolerance, FAIL if any is outside. Secondary is decided the same way. The overall verdict is the primary one. |

UNPOWERED statistics are listed separately (there are none).

## 8. §9.F rehearsal (done before sealing; `results/peter/seal/dryrun/`)

**Dry double read.**
- Input: the development data split at t = 3·10⁵. The "fresh" part is (3·10⁵, 10⁶], with 10 seeded independent class
  numbers.
- Two reads in separate processes are byte-identical (`cmp` status 0). Timings are kept in `.timing` sidecars, outside
  the compared JSON.
- The dry-run verdict means nothing, because that data was seen.

**Red paths.**

| Corruption | Verdict |
|---|---|
| One independent h changed | VOID (inputs) |
| One fresh t removed | VOID (inputs) |
| Tolerances × 10⁴ | VOID (witness) |

**Fix found by the rehearsal.** A coverage gap first ended the read with an assertion. It now writes VOID (inputs); see
the commit that carries this document.

**Fresh run** (`run_peter_fresh_spot.sh`):
- PARI on 200 chunks with cost checks, then the 200 independent class numbers, then merge and sha256.
- It computes no statistic. Its outputs stay unread until the attestation is verified.

## 9. Attribution

- Prediction: Y. Peter (2002), arXiv math/0104234, unconditional.
- Multiplicities: PARI/GP 2.17.2 `quadclassunit` / `quadunitnorm`, GRH-conditional, not certified.
- Input check: PARI `qfbclassno` plus a continued-fraction unit-norm parity.
