# PH2S Stage 2 — F2 pre-read with estimator B (no F2 zero read)

Asked for: nineteenth round ("GUE baselines …, power, false-positive splits before the F2 seal") and twenty-sixth round
("on to the F2 pre-read with estimator B"). F2 enters only through its pinned height ranges (`ph2r2/FRESH_SETS_F1_F3.md`).
Generator: `s2_preread.py` (subcommands below). Outputs: `results/s2_preread/*.json`. Everything here runs on stored
window sums, so it is light and was run locally.

**Status: the record is complete; the rule choice is Will's (§6).**

## 1. The prediction under test (tag `ph2s-stage2-prediction`)
| F2 file (ℓ) | 15.7502 | 16.4972 | 17.2491 | 19.5003 | 21.75 |
|---|---|---|---|---|---|
| g_B predicted | 0.6703 | 0.6656 | 0.6646 | 0.6829 | 0.7201 |
| shrink g_GUE,B − g_B | 0.289 | 0.293 | 0.295 | 0.276 | 0.239 |
| windows n(100) / n(10⁴) | 17546 / 175 | 18379 / 183 | 19216 / 192 | 21724 / 217 | 24231 / 242 |

- g_GUE,B = 0.9591 (sine kernel).
- The window counts are as `tapered.py` lays out the windows, from N̄ at the pinned ends.
- The measured statistic is ĝ_B = √(v̂_B(10⁴)/v̂_B(100)), with v̂_B from successive differences (`tapered.pooled_diff`).
- Its SE uses the delta method on the two lag-0–2 SEs:
  SE_g = ½·ĝ·√(rSE₁₀₀² + rSE₁₀⁴²).

## 2. Is the lag-0–2 SE right for the zeros? (a risk found and checked)
- **Theory flag (`secorr`).** CS08's predicted window correlations do not decay (open lead L3). Suppose the window sums
  were Gaussian with those correlations. Then the squared differences D_i would stay correlated at every lag, at
  c_k² ≈ 3e-4 to 1.3e-3 per lag at b = 100. Summed over a whole file, the lag-0–2 SE would then be 2.4–4.0× too small
  at b = 100 and 1.4–2.1× at b = 300; at b ≥ 1000 it is ≤ 1.17×.
  - That model is probably wrong for ζ. The arithmetic terms are deterministic oscillations in t with fixed amplitudes,
    not random-amplitude lines, and their time averages converge. The real check is empirical.
- **Measured on F1 (`seemp`; seen data, descriptive).** The lag-0–2 SE agrees with SEs that sum the D autocovariances
  to lag 10, 30 and 100, and with batch means over 5, 10 and 20 contiguous batches. This holds in every file at every
  rung, within the scatter of those estimates.
  - At b = 100, the relative SEs are 0.0109–0.0139 from lags 0–2 and 0.0096–0.0141 summed to lag 10–100. Batch means
    scatter more (0.005–0.017 with 5 batches, 0.009–0.014 with 20) and are not systematically larger.
  - So no long-range inflation is seen. The Gaussian-model extrapolation does not hold for the zeros.
- **GUE (16 independent sequences).** The between-sequence spread of v̂_B, divided by the per-sequence lag-0–2 SE, is
  0.87–1.35 across rungs, which is within what 16 sequences can resolve.

## 3. z calibration on GUE at F2's window counts (`guecal`; the false-positive side)
Each pseudo-file draws n(100) and n(10⁴) windows i.i.d. from the pooled Stage 1 GUE window sums (512 at b = 10⁴; GUE
windows 3b apart are independent to |ρ₁| ≤ 3e-3). It is then scored against the pool's own g, 4000 replicates per file.

| F2 geometry | z mean | z SD | P(\|z\| > 2) | P(\|z\| > 3) | P(z < −2) / P(z > 2) |
|---|---|---|---|---|---|
| 15.75 | +0.01 | 1.08 | 0.060 | 0.0085 | 0.039 / 0.021 |
| 16.50 | +0.01 | 1.08 | 0.061 | 0.0067 | 0.040 / 0.022 |
| 17.25 | +0.02 | 1.08 | 0.061 | 0.0110 | 0.042 / 0.019 |
| 19.50 | +0.02 | 1.05 | 0.056 | 0.0075 | 0.036 / 0.021 |
| 21.75 | +0.02 | 1.04 | 0.054 | 0.0055 | 0.034 / 0.020 |

Nominal values: 0.0455 for |z| > 2 and 0.0027 for |z| > 3.

- The plug-in SE is 4–8% small at n(10⁴) ≈ 175–242.
- The lower tail is heavier: v̂_B(10⁴) is right-skewed, so a low ĝ comes with a small plug-in SE.
- A per-file 3-SE band rejects a true prediction 0.6–1.1% of the time, not 0.27%. A 2-SE band rejects it 5.4–6.1% of
  the time, not 4.6%.

## 4. Operating characteristics of candidate rules (`opchar`)
- **SE model.** rSE(v̂_B(b)) = κ·√(3/(n(b) − 1)), the Gaussian successive-difference value, with v̂ ~ v·χ²_ν/ν and
  plug-in SEs. κ = 1 is the typical F1 ratio (median 0.91, mean 1.0); κ = 1.37 is the worst F1 file (F1a).
- **Per-file SE(ĝ_B):** 0.040–0.044 (κ = 1) or 0.055–0.060 (κ = 1.37).
- **Pooled (inverse-variance) SE:** 0.019 (κ = 1) or 0.026 (κ = 1.37), against a predicted shrink of 0.24–0.30.
- **Alternatives:** g = g_pred + ε·(g_GUE,B − g_pred), so ε is the fractional error in the predicted shrink (ε = 1 is
  GUE).
- **Candidate rules:**
  - **R1:** ≥ 4 of 5 files with |z_f| ≤ k.
  - **R2:** pooled |z_pool| ≤ k.

P(PASS), κ = 1 (κ = 1.37 in brackets):

| ε | R1, k = 2 | R2, k = 2 | R1, k = 3 | R2, k = 3 |
|---|---|---|---|---|
| −0.3 | 0.08 (0.33) | 0.001 (0.03) | 0.56 (0.83) | 0.015 (0.16) |
| −0.2 | 0.48 (0.69) | 0.08 (0.24) | 0.92 (0.97) | 0.31 (0.57) |
| −0.1 | 0.87 (0.91) | 0.56 (0.66) | 0.99 (0.99) | 0.85 (0.90) |
| **0 (true)** | **0.98 (0.98)** | **0.94 (0.92)** | **1.00 (1.00)** | **0.99 (0.99)** |
| +0.1 | 0.96 (0.98) | 0.81 (0.91) | 1.00 (1.00) | 0.98 (0.99) |
| +0.2 | 0.77 (0.93) | 0.32 (0.65) | 1.00 (1.00) | 0.72 (0.93) |
| +0.3 | 0.37 (0.76) | 0.04 (0.29) | 0.96 (1.00) | 0.23 (0.70) |
| +0.5 | 0.007 (0.21) | 0.000 (0.012) | 0.40 (0.93) | 0.001 (0.11) |
| 1 (GUE) | 0.000 (0.000) | 0.000 (0.000) | 0.000 (0.03) | 0.000 (0.000) |

- **Every rule rejects GUE** with near certainty (the arm can fire). For R1 at k = 3, κ = 1.37, the rejection rate is
  0.97.
- **The test's sharpness lives in R2.** R2 at k = 2 detects a 20% error in the predicted shrink with probability
  0.92/0.68 (low/high side) at κ = 1, and 0.76/0.35 at κ = 1.37. At k = 3 these fall to 0.69/0.28 (κ = 1).
- **High-side errors are harder to detect** (ĝ above the prediction, towards GUE). This is the same skew as in §3.
- **Size (false FAIL with the prediction true):** about 6% for R2 at k = 2, or about 7–8% for R1 ∧ R2. For R2 at k = 3
  it is about 1%. §3's calibration suggests the real rates are slightly higher than these model values.

## 5. Dry run (`dryrun`)
- **F1 (seen data; prediction interpolated in ℓ and held at the end values outside 15.75–21.75; descriptive only):**

  | file | ℓ | ĝ_B | g_pred | z |
  |---|---|---|---|---|
  | F1a | 14.46 | 0.663 ± 0.063 | 0.670 | −0.12 |
  | F1b | 15.47 | 0.669 ± 0.038 | 0.670 | −0.04 |
  | F1c | 17.75 | 0.714 ± 0.052 | 0.669 | +0.87 |
  | F1d | 19.25 | 0.682 ± 0.037 | 0.681 | +0.02 |
  | F1e | 21.50 | 0.685 ± 0.034 | 0.716 | −0.92 |
  | F1x | 22.10 | 0.752 ± 0.038 | 0.720 | +0.83 |

  - Core five: z_pool = −0.24, so R1 and R2 pass at k = 2 and k = 3. The F1 heights are not F2's, and F1 is seen;
    this is a pipeline check, not evidence.
- **GUE stand-in at F2 geometry:**
  - Against the ζ prediction: z = +3.7 to +7.5 per file, z_pool = +10.6, so R1 and R2 FAIL at k = 2 and 3.
  - Against the GUE prediction: z = −0.3 to +2.4, z_pool = +1.7, so both PASS.

## 6. For Will: the arm-P rule
Options (both are precision-only guards; neither reads ĝ):
- **(a) Recommended: PASS iff R2 at k = 2 and R1 at k = 3.**
  - R2 is the sharp test: a pooled band of about ±0.037, which is 13% of the predicted shrink.
  - R1 is a per-file consistency check, so one aberrant file cannot hide in the pool.
  - Size is about 6–7% (false FAIL). Power against a 20% error in the shrink is 0.92/0.68 (κ = 1).
  - RESOLVABLE (achieved) iff the achieved pooled 2·SE_pool ≤ 0.25 × the mean predicted shrink, about 0.070. That
    holds for κ ≤ about 1.9 (the worst F1 file has κ = 1.37).
- **(b) Conservative: R2 at k = 3 with R1 at k = 3.** Size is about 1%, but power against a 20% error is only
  0.69/0.28.
- **Either way:**
  - Record the §3 calibration: plug-in SE about 5% small, heavier lower tail.
  - Record the asymmetric power, so a PASS is read as "consistent within about ±20% of the shrink, less tightly on the
    high side".
  - The GUE comparison, ĝ_B < g_GUE,B, is implied by the band and needs no separate arm (Stage 1 established the
    direction).
- **Not yet built:** the seal JSON and a read script with md5 verification of the F2 files, in the shape of Stage 1's
  `s1read.py`. They follow the rule choice.
