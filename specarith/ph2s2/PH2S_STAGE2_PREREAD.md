# PH2S Stage 2 — F2 pre-read with estimator B (no F2 zero read)

Asked for: nineteenth round ("GUE baselines …, power, false-positive splits before the F2 seal") and twenty-sixth round
("on to the F2 pre-read with estimator B"). F2 enters only through its pinned height ranges (`ph2r2/FRESH_SETS_F1_F3.md`).
Generator: `s2_preread.py` (subcommands below). Outputs: `results/s2_preread/*.json`. Everything here runs on stored
window sums, so it is light and was run locally.

**Status:**
- v1: e7fbf200.
- Revised in the twenty-seventh round: §3 (Stage 2 GUE baseline; corrected reference value; pooling bias) and §4–§6.
- Rule adopted: option (a). **Open for Will: the pooling construction (§6).**

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
- **GUE.** The between-sequence spread of v̂_B, divided by the per-sequence lag-0–2 SE, is within what the sequence
  counts can resolve:
  - Stage 2 baseline (24 sequences): 1.04–1.27 across rungs;
  - Stage 1 sequences (16): 0.87–1.35.

## 3. z calibration on GUE at F2's window counts (`guecal`, `poolcal`; the false-positive side) — REVISED
**Revised in the twenty-seventh round.** v1 (e7fbf200) had two defects:
- **(i) Wrong GUE set.** It used the Stage 1 sequences. The dedicated Stage 2 baseline is 24 × 10⁶ fresh sequences
  (`f2_gue_levels.py`, seed base 20261012, generated 10-10). It is now primary; Stage 1's 16 are a replication.
- **(ii) Wrong reference value.** It scored pseudo-files against the within-sequence successive-difference mean, but
  i.i.d. draws have the pool's variance as their expectation. That gave a fixed offset of about ±0.3 SE_pool per set.

Method: 4000 replicate F2 reads. Each pseudo-file draws n(100) and n(10⁴) windows i.i.d. from the set's pooled window
sums (768 at b = 10⁴ for the Stage 2 set; GUE windows 3b apart are independent to |ρ₁| ≤ 3e-3).

| | Stage 2 baseline (24) | Stage 1 (16) |
|---|---|---|
| per-file z SD | 1.05–1.09 | 1.07–1.09 |
| per-file P(\|z\| > 3) (nominal 0.0027) | 0.006–0.009 | 0.008–0.011 |
| **pooled z (inverse-variance weights, as adopted): mean / SD** | **−0.35 / 1.12** | **−0.32 / 1.11** |
| P(z_pool < −2) / P(z_pool > 2) | 0.077 / 0.014 | 0.070 / 0.014 |
| R1 fails (< 4 files within 3 SE) | 0.0005 | 0.0005 |
| **false-FAIL of the adopted rule** | **0.090** | **0.090** (0.085 in `poolcal`'s independent draw) |

- **Per file:** the plug-in SE is 5–9% small, and the lower tail is heavier. v̂_B(10⁴) is right-skewed, so a low ĝ comes
  with a small plug-in SE.
- **Pooled, the same skew becomes a bias.** Inverse-variance weights 1/SE_f² ∝ 1/ĝ_f² give more weight to low draws.
  The pooled deviation is pulled down (mean d_pool −0.008, about 0.35 SE_pool). The adopted rule therefore fails a
  true prediction about 9% of the time, not the 6–7% from the χ² model in §4 (which understates the skew).
- **Two constructions that avoid it** (`poolcal`; false-FAIL with the same R1 ∧ |z_pool| ≤ 2):

  | construction | z_pool mean / SD (Stage 2; Stage 1) | false-FAIL (Stage 2; Stage 1) |
  |---|---|---|
  | A — adopted: SE_f = ½ĝ_f·rSE_f, weights 1/SE_f² | −0.35 / 1.12; −0.32 / 1.11 | 0.090; 0.085 |
  | B — SE_f evaluated at the prediction: ½·g_pred,f·rSE_f | −0.10 / 1.09; −0.07 / 1.08 | 0.068; 0.066 |
  | **C — weights fixed pre-data ∝ n_f(10⁴) − 1; SE_pool from the measured SE_f** | **−0.10 / 1.04; −0.06 / 1.03** | **0.055; 0.057** |

  C's weights come from the window counts alone, so they cannot read ĝ. Its SE_pool = √(Σ W_f² SE_f²) still uses the
  measured SEs. §4 gives its power.

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
- **The adopted rule (R2, k = 2, with R1, k = 3), under both pooling constructions of §3.** The model's size is below
  GUE's measured rate; §3 is the record for size.

  | ε | −0.3 | −0.2 | −0.1 | 0 | +0.1 | +0.2 | +0.3 | GUE |
  |---|---|---|---|---|---|---|---|---|
  | A (inverse-variance), κ = 1 | 0.001 | 0.076 | 0.56 | 0.937 | 0.81 | 0.32 | 0.039 | 0.000 |
  | **C (fixed weights), κ = 1** | 0.002 | 0.12 | 0.65 | 0.953 | 0.75 | 0.24 | 0.023 | 0.000 |
  | A, κ = 1.37 | 0.027 | 0.24 | 0.66 | 0.921 | 0.91 | 0.65 | 0.29 | 0.000 |
  | **C, κ = 1.37** | 0.053 | 0.35 | 0.77 | 0.951 | 0.87 | 0.55 | 0.20 | 0.000 |

  - **Power against a 20% shrink error:**
    - A: 0.92 / 0.68 (low / high side) at κ = 1, and 0.76 / 0.35 at κ = 1.37;
    - C: 0.88 / 0.76 at κ = 1, and 0.65 / 0.45 at κ = 1.37.
  - C trades some low-side power for high-side power, so the asymmetry shrinks. It is also better calibrated (§3).

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
- **GUE stand-in at F2 geometry,** revised to draw from the Stage 2 baseline (v1 used Stage 1's sequences):
  - Against the ζ prediction: z = +4.2 to +5.0 per file, z_pool = +10.4, so R1 and R2 FAIL at k = 2 and 3.
  - Against the GUE prediction: z = −0.2 to +1.4, z_pool = +1.5, so both PASS.
- **The read code's own dry run** (`s2read.py dryrun`, on spot; results/dryrun/S2_DRYRUN.json):
  - F1 decoded again through the read path reproduces the stored window sums exactly (max |Δ| = 0) and reads PASS
    (z_pool = −0.24).
  - GUE stand-in vs ζ: FAIL (z_pool = +11.2). GUE stand-in vs GUE: PASS (z_pool = −0.19).
  - Guard witness: a would-be PASS with per-file SE 0.10 (2·SE_pool = 0.089) reads NOT RESOLVABLE.

## 6. Twenty-seventh round: adopted, and one open construction question
- **Adopted (Will):** option (a). PASS iff |z_pool| ≤ 2 (R2) and ≥ 4 of 5 files have |z_f| ≤ 3 (R1). The precision
  guard is RESOLVABLE iff 2·SE_pool ≤ 0.07. The read report gives pooled ĝ_B ± CI beside the prediction, regardless of
  verdict.
- **Open, for Will: the pooling construction.** The round-27 text records a false-fail rate of "~6–7%". That came from
  §4's χ² model. On GUE the adopted inverse-variance pooling (A) gives 9.0%, because of §3's weighting bias. Options:
  - **Keep A** and record 9% as the false-fail rate.
  - **Switch to C** (weights fixed pre-data ∝ n_f(10⁴) − 1; recommended): false-fail 5.5–5.7% on GUE, pooled z
    centred within 0.1 SE; power 0.88 / 0.76 against a 20% shrink error (κ = 1).
  - B (SE at the prediction) lies between them: 6.6–6.8%.
  - The guard is unaffected either way. For C it uses SE_pool = √(Σ W_f² SE_f²), which is ≥ the inverse-variance
    SE_pool, so the guard becomes slightly stricter.
- `s2read.py` implements A, as adopted. Switching to C changes `evaluate()` only.

## 6a. (v1, superseded) the options offered before the twenty-seventh round
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
