# Phase 6 near-miss check: the fixed-point hit rule (round 67; POST HOC, DESCRIPTIVE; committed before computing)

**Status:** committed before any quantity below is computed. Nothing here is a verdict. A true-prime percentile above 95
on any spectrum is **flagged for a pre-registered follow-up**; it is not reported as a finding. Decisions: the Phase 6
near-miss check and round 67 (`../ph2/PH2_DECISIONS_2026-10-07.md`). The inventory is in the session report of
2026-10-19.

## 1. Inputs
- **Spectra:** the converged 6.1 candidates, read at their res2 level lists exactly as the 6.1 read used them (A4).

  | candidate | levels | sha256 | read top E_hi |
  |---|---|---|---|
  | C1a | `results/candidates/C1a_res2.npy` | pinned in its `.json` | 26599.92 |
  | C1b | `results/candidates/C1b_res2.npy` | pinned in its `.json` | 26599.83 |
  | C2 | `results/candidates/C2_res2.npy` | pinned in its `.json` | 26605.86 |
  | C4 | `results/candidates/C4_res2.npy` | pinned in its `.json` | 376221.85 |

  Each one's sha256 is checked against its committed `.json` before use. C3a (not converged), C3b, BBM and the Sierra
  mirror (INAPPLICABLE, no levels) are out of scope.
- **Configuration:** the sealed `ph6lib.rule_config(0, E_hi)` with E_hi as in `results/read61/<id>.json` (K_edge 8.5),
  so T₀ and σ are as read.
- **No 6.2 deformation scan exists,** so there are no deformation paths and no rank correlations along them.

## 2. The quantity
- r(τ) = (S(τ) + M(τ) − S_smooth(τ)) / (σ/√2π), the sealed 6.0 readout quantity (`tests61.t3`'s r: `ph6lib.zero_sums`
  with compensated summation, minus `ph6lib.rhs_dirichlet(cfg, τ, 1, None, 0)["smooth"]`).
- r is complex. The hit uses its modulus **|r(τ)|**, the envelope. Near a line r carries the phase e^{−i(τ−log n)T₀},
  which turns about T₀/σ ≈ 8.5 rad across one line width, so only the modulus is a stable amplitude off the exact
  point.
- "S(τ₀), interpolated" (round 67) is computed **exactly at τ₀**: the sealed sum is evaluated at τ₀ itself, which is
  the limit of any interpolation. No grid enters the test point's value.

## 3. The hit rule (round 67)
- **Resolution width:** w = 1/σ, the sealed line width (6.0 seal, §3 table). It is 6.4·10⁻⁴ for C1a, C1b and C2,
  and 4.5·10⁻⁵ for C4.
- **Test points:**
  - true set: τ₀ = log n for the 34 prime powers n ≤ 90 (the 6.0 bound; `ph6lib.LINE_NS`, `is_prime_power`);
  - fake sets: τ₀ = log m for the 55 non-prime-powers m in [2, 90].
- **Reference band:** [τ₀ − 10w, τ₀ + 10w] (B = 10 resolution widths), sampled on the 6.0 fine grid step 0.2/σ
  (6.0 seal line 97), so 101 points.
  - Excluded: every band point within ±1w of **any** log n, n = 2…90. That is every true point and every point any fake
    set can contain; the 200 fake sets are drawn from these 55.
- **Hit at τ₀** iff |r(τ₀)| > the 99th percentile (numpy linear interpolation) of |r| over the band points that remain.
- **Rates:** true rate = hits / 34. Each fake set is 34 distinct m drawn without replacement from the 55
  non-prime-powers, matched in count and range (seed [20261020, 67, j], j = 0…199; the same 200 sets for every
  spectrum). Its rate is computed with the identical rule. A point's hit status does not depend on which set it is in,
  because the exclusion is the same for all.
- **Percentile:** the mid-rank percentile of the true rate among the 200 fake rates, 100·(#{fake < true} +
  ½·#{fake = true})/200. #{fake < true} and #{fake ≤ true} are also reported.
- **Amplitude correlation:**
  - **Primary:** the Pearson correlation, with its sign, between Re r(log n) and Λ(n)/√n (= log p/p^{k/2}; log p/√p for
    primes) over all 34 prime powers. The fixed-point amplitude exists at every test point.
  - Also reported: the Spearman correlation, and both correlations over the hits only.
  - For ζ the explicit formula gives Re r(log n) ≈ −Λ(n)/√n, so its sign is negative.

## 4. Controls (descriptive; showing the rule can fire and can stay quiet)
- **Positive control:** the ζ zeros, the first 3·10⁴ of `data/odlyzko_zeros6.txt`, sha-checked by `tests61.zeros_in`.
  This is 6.1's known-answer list, at its configuration rule_config(0, γ_30000).
- **Negative control:** one GUE null-level draw (`ph6lib.null_levels("gue", nbar_zeta, E_hi, rng)`) at the same
  configuration. The seed is CALIB_SEEDS["gue"] + 150, from the held-out range the calibration never used.
- Both use the identical rule and the same 200 fake sets. Their percentiles are reported beside the candidates'.
- **A positive control that does not reach a high percentile** means the rule cannot see a true arithmetic spectrum at
  this size. Then the candidates' numbers are reported with that caveat.

## 5. Reporting
- **Per spectrum:** the true rate, the fake-rate distribution (mean, 5–95% range), the percentile, the Pearson and
  Spearman correlations with signs, and the per-n hit table.
- **Flag:** any candidate with a percentile above 95 is flagged for a pre-registered follow-up, and is not reported as a
  finding.
- All of it is labelled post hoc and descriptive.
- **Machine:** spot (CPU), under `nice`.
- **Outputs:** `results/nearmiss/` (JSON per spectrum and a summary). The code is `nearmiss.py`, committed before it
  runs.

## 6. Result and closure (round 68): a null
**Result (aa494a9b, `results/nearmiss/`).**
- C1a: 2/34 true-prime hits (n = 16, 25), percentile 100.
- C1b: 1/34 (n = 8), percentile 100.
- C2: 1/34, percentile 7.2.
- C4: 2/34, percentile 80.5.
- Controls: the ζ zeros hit 34/34 (percentile 100, Pearson −1.000); the GUE draw hit 2/34 (percentile 15.5).

**The C1a and C1b flags are a defect in the flag rule (Will, round 68), not near-misses.**
- The percentile is ill-posed when the fake sets' hit counts are near zero. C1b has no non-prime-power hit, so every fake
  rate is 0 and one true hit reaches the 100th percentile; C1a has one.
- **Exact count tails at the theoretical 1% chance rate** (0.34 expected hits per 34 points), before correcting across
  the 4 candidates:
  - C1a's 2 hits: Poisson p = 0.046 (exact binomial(34, 0.01): 0.045);
  - C1b's 1 hit: p = 0.288 (0.289).

  Corrected ×4 they are 0.18 and 1.
- **No amplitude correlation:** |r| ≤ 0.29 for every candidate, against −1.000 for the zeros.

**Conclusion (descriptive):** no prime-line structure in the xp candidates, consistent with the expectation for 1D
integrable systems. No follow-up.

**Rule amendment (round 68):** future near-miss checks use exact count tails at the chance-rate floor (the binomial or
Poisson tail at the rule's nominal per-point rate), not percentiles among sparse fake sets. Fake sets may still be
reported, as a description of the rule's empirical rate.
