# PH2S Stage 1 — findings: the zeros' pair-sum error bars shrink beyond the sine kernel, confirmed on fresh heights

**Headline (Will):** *On five fresh heights, the zeta zeros' pair-statistic fluctuations are suppressed relative to the
sine kernel at 10²–10⁴-level scales: confirmed in all four resolvable bins. The width dependence predicted by a few-prime
form-factor mechanism holds; its predicted height dependence is not established (narrow FAIL).*

The statistic is the drift-removed moving-block bootstrap SD of the pair sum, as a ratio from 100- to 10,000-level blocks.
- **Zeros:** it falls to 0.66–0.70 of its short-block value (F1, L = log(t/2π) ≈ 14.5–21.5).
- **Long GUE baseline, through identical code:** it stays at 0.97–0.99.
- **Arm A PASS:** every resolvable core bin shrinks, by 7.9–11.9 combined SE (22.6 SE pooled, descriptive).
- **The conservative reference did not bind.** The observed shrinks (0.28–0.30) sit at the seen size (0.235–0.333),
  not at half of it, so arm A's PASS did not depend on its ≈ 0.51 joint power at the half-size reference.
- **Arms C and D:** the mechanism's width prediction holds (arm C PASS, 13.5 SE). Its height prediction is not
  established (arm D FAIL, narrowly; the point estimate is in the predicted direction), recorded as sealed with no
  re-analysis.

This confirms, as a direction, the exploratory candidate finding (`ph2r2/PH2R2_FINDINGS.md` §6), on heights pinned
before download and not seen.

**Novelty** (blinded literature check `lit/PAIRSUM_VARIANCE_LIT.md`, §0 and §1.8; wording adopted by Will,
2026-10-10): To our knowledge, no published work measures how the across-block variance of a local pair statistic of
the zeta zeros (test function a few mean spacings wide) depends on block length, or compares it with the sine kernel
and a theory-fixed arithmetic prediction. The closest precedent is Coram & Diaconis (2003; read in its 2000
technical-report version). They tested the across-block distribution of |Σ_j e^{iθ_j}|², a pair sum in a single
block-scale Fourier mode, for blocks of n ≈ log(T/2π) = 42 zeros wrapped onto the circle, found agreement with CUE₄₂,
and noted a lag-1 anti-correlation (−0.2) between consecutive blocks' values, without a sine-kernel or arithmetic
comparison.

Run under **PH2S_SEAL_1.0** (commit 663062ee, tag `ph2s-stage1-seal`; 11/11 pre-read checks). The F1 files were
downloaded by hand by Will. `s1read.py` verified each md5 against the pins before decoding; all six matched. Per-bin
data: `results/read/S1_READ.json`.

## 1. Arm A (primary): f = (0.5, 0.3), windows of 10⁶ levels
d = g_GUE − g_zeros of the drift-removed growth SD(10⁴)/SD(100); SE_c combines both arms' SEs; a bin shrinks iff it is
resolvable and d > 3·SE_c.

| bin | L | windows | g_GUE (16 seqs) | g_zeros | d ± SE_c | d/SE_c | verdict |
|---|---|---|---|---|---|---|---|
| F1a | 14.46 | 4 | 0.989 ± 0.019 | 0.663 ± 0.019 | 0.325 ± 0.027 | 12.0 | **NOT RESOLVABLE (pre-data)**; d descriptive |
| F1b | 15.47 | 5 | 0.982 ± 0.014 | 0.680 ± 0.033 | 0.302 ± 0.036 | 8.4 | shrinks |
| F1c | 17.75 | 5 | 0.973 ± 0.018 | 0.682 ± 0.032 | 0.292 ± 0.037 | 7.9 | shrinks |
| F1d | 19.25 | 6 | 0.978 ± 0.020 | 0.688 ± 0.023 | 0.290 ± 0.031 | 9.5 | shrinks |
| F1e | 21.50 | 7 | 0.974 ± 0.019 | 0.698 ± 0.013 | 0.276 ± 0.023 | 11.9 | shrinks |
| F1x | 22.10 | 7 | 0.986 ± 0.017 | 0.732 ± 0.018 | 0.253 ± 0.025 | 10.2 | arm D only |

- **A: PASS.** F1a was sealed NOT RESOLVABLE (power 0.708 at the half-size reference), so PASS required all four of
  F1b–F1e. All four shrink, and no bin's achieved precision guard fired.
- **Sealed joint-power note:** arm A's power was ≈ 0.51 at the half-size reference (d_ref = 0.118) and ≈ 1 at the
  smallest seen shrink (0.235). The observed shrinks (0.28–0.30) are at or above the seen size, consistent with the
  exploration rather than with half of it.
- **Pooled one-sided (descriptive):** d = 0.296 ± 0.013 (z = 22.6).

## 2. Arm B (L = 2·10⁵): descriptive (unresolvable pre-data in every bin)
d = 0.298, 0.245, 0.227, 0.221, 0.243 (F1a–F1e), and 0.135 for F1x. That is 4.7–9.1 SE, all positive. Every bin reads
NOT RESOLVABLE (achieved), because the precision guard compares 3·SE_c (0.09–0.12) with the 2·10⁵ reference (0.075).
The effect is visible at 2·10⁵ too; the arm was never able to rule on it.

## 3. Arm C (mechanism i, wider bump → larger shrink): PASS
Δ_u = mean over core bins of d(u, 0.3) − d(u, 0.15) = 0.161, 0.125, 0.114, 0.124 for u = 0.5, 1, 1.5, 2: all four are
positive. The mean is 0.131 ± 0.0097 (unit-resampled SE), 13.5 SE against the sealed threshold of 3. The empirical
false-positive rate under the sealed rule was 0.014 (500 GUE-vs-GUE splits). The seen value was 0.136 ± 0.010.

## 4. Arm D (mechanism ii, shrink weakens with height): FAIL
The WLS slope of d on L over the six F1 bins is −0.0076 ± 0.0039 per unit L, so slope + 2·SE = +0.0002 and the arm
FAILs, narrowly. The power at the seen slope (−0.013 on R1–R5) was 0.863. The empirical false-positive rate was 0.018.
**Reading:** the point estimate is in the predicted direction at 1.95 SE, but its size is about 60% of the seen slope.
The sealed test does not establish a height dependence on fresh data. The decline from F1a to F1x (0.325 → 0.253) is
descriptive. It sits at the two ends of the range, one of which (F1a) is unresolvable for arm A. Stage 2's quantitative
model makes a specific height prediction, which F2 will test.

## 5. What this says, and what it does not
- **It says:** a property of the zeros' pair-correlation *fluctuations*, not their mean, departs from the sine kernel
  at 10²–10⁴-level scales:
  - the variance of the pair sum over long blocks is suppressed;
  - this replicates on fresh heights across L ≈ 14.5–22.1;
  - its size is stable (d ≈ 0.25–0.33);
  - it is larger for wider test functions, those with more weight below τ = 1.
- **It does not say why.** The few-prime form-factor mechanism is a candidate. Stage 2 (F2) seals a quantitative
  prediction from it, with its own known-answer gate.
- **The reference is a long GUE sequence through identical code.** Its finite-n bootstrap behaviour is shared by both
  arms; only the difference d is interpreted.
- **One test-function family, one block-length pair** (100 vs 10⁴), as sealed.
