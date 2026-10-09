# Phase 2, new part (R₂) — findings: the arithmetic lower-order terms of ζ's pair correlation at five fresh heights

**Headline (draft; framing is Will's call):** at five fresh heights, t ≈ 6.7·10⁶ to 2.25·10¹⁰ (log(t/2π) = 14–22), the
amplitude of Conrey–Snaith's (Bogomolny–Keating's) arithmetic lower-order term in the pair correlation is **μ̂ = 1 within
0.01 in every bin**. Each 95% CI contains 1 and excludes 0, so **G1 is PASS in all five bins**. Pooled (descriptive):
μ̂ = 1.003 ± 0.006. This is an independent quantitative replication (§1 framing) of the formula that Berry–Keating 1999
compared visually with Odlyzko's zeros. It tests the ratios conjecture's lower-order prediction, not a theorem.

Run under **PH2R2_SEAL_1.0** (commit fb83059f, tag `ph2r2-seal`; amendments A1–A3; 20/20 pre-read checks). The read ran
locally on 2026-10-09 (PDT), after the seal commit (10:00:29), finishing at 10:00:42. `r2run.py read` refused unless the code sha256s and each Platt md5 matched the
seal, and no fresh zero was decoded before the seal commit. Per-bin JSON: `results/read/<bin>.json`. Tables:
`results/read/READ_REPORT.md` (generator committed before the read). Post-hoc: `results/read/POSTHOC.md`.

## 1. Sealed verdicts (primary f: bump at u = 0.5, w = 0.3 mean spacings)
| bin | log(t/2π) | zeros (− N̄) | μ̂ | 95% CI | half-width achieved / target | G1 |
|---|---|---|---|---|---|---|
| R1 | 14.03 | 4,688,582 (+0.1) | 0.9995 | [0.948, 1.051] | 0.052 / 0.082 | **PASS** |
| R2 | 16.00 | 5,349,157 (+0.2) | 1.0064 | [0.984, 1.028] | 0.022 / 0.039 | **PASS** |
| R3 | 18.00 | 6,016,496 (+0.5) | 0.9979 | [0.972, 1.024] | 0.026 / 0.043 | **PASS** |
| R4 | 20.00 | 6,684,531 (+0.0) | 0.9976 | [0.963, 1.032] | 0.035 / 0.053 | **PASS** |
| R5 | 22.00 | 7,352,948 (−0.3) | 1.0098 | [0.978, 1.042] | 0.032 / 0.052 | **PASS** |

- **Power arm (μ = 0 excluded):** yes in all five bins. The leading-order-only prediction is rejected by 19–46
  CI half-widths (μ̂ / half-width = 19, 46, 38, 29, 32).
- **Resolution:** every achieved half-width is below its sealed target. The CI is μ̂ ± 1.96·max(surrogate SD, widest
  bootstrap SD). In R1 the widest bootstrap SD (10,000-level blocks) sets it, and that SD is inflated by the density
  drift (A3). In R2–R4 the surrogate SD sets it. In R5 it is the zeros' own 100-level bootstrap.
- **Red paths (pre-data, all reachable at power 1.0):** each would read FAIL against these CIs. The wrong density
  log(E/2πe) reads μ ≈ −8.5 to −10.8, the flipped LOT sign reads −1, and the shuffle shifts μ by −1.5 to −2.9.
- **Zero counts** equal the smooth count N̄(t₁) − N̄(t₀) to within 0.5 in every bin. The files decode completely.

## 2. Is the agreement finer than the resolution? (post-hoc, descriptive)
Against the sealed surrogate SDs, (μ̂ − 1)/SD = −0.04, +0.57, −0.16, −0.14, +0.67, with χ²₅ = 0.82 and P(χ²₅ ≤ 0.82) =
0.024. That is tighter than chance would give. Against the zeros' own drift-removed 10,000-level bootstrap SD, the values
are −0.09, +0.96, −0.26, −0.24, +0.85, with χ²₅ = 1.77 and P = 0.12, which is unremarkable. The tight agreement is
therefore explained by the zeros' μ̂ varying less than the surrogates' (§3). Both SDs come from the same data and code,
so this does not rule out a shared upstream determinant. It does mean no anomaly is needed: the sealed CIs are
conservative for the zeros.

## 3. Block-length growth of the bootstrap SD (A1/A3; descriptive, changes no verdict)
| bin | raw | G0b surrogate mean (raw) | surrogate-relative | drift-removed | dry-run surrogate, drift-removed |
|---|---|---|---|---|---|
| R1 | 1.00 → 1.07 → 2.66 | 1.00 → 1.13 → 2.25 | 1.00 → 0.95 → 1.18 | 1.00 → 0.77 → 0.59 | 1.00 → 0.85 → 0.89 |
| R2 | 1.00 → 0.75 → 0.73 | 1.00 → 0.96 → 0.97 | 1.00 → 0.78 → 0.75 | 1.00 → 0.76 → 0.60 | 1.00 → 0.96 → 0.87 |
| R3 | 1.00 → 0.82 → 0.69 | 1.00 → 0.97 → 0.96 | 1.00 → 0.85 → 0.71 | 1.00 → 0.79 → 0.65 | 1.00 → 0.92 → 1.02 |
| R4 | 1.00 → 0.90 → 0.81 | 1.00 → 0.96 → 0.94 | 1.00 → 0.94 → 0.86 | 1.00 → 0.88 → 0.70 | 1.00 → 1.00 → 0.95 |
| R5 | 1.00 → 0.80 → 0.73 | 1.00 → 0.96 → 0.97 | 1.00 → 0.83 → 0.75 | 1.00 → 0.89 → 0.75 | 1.00 → 1.02 → 1.02 |

- **The error bars shrink with block length; they do not grow.** This is the opposite sign to what A1 was set up to
  detect. Drift-removed, the zeros' bootstrap SD at 10,000 levels is 0.59–0.75 of its 100-level value in all five bins.
  On the dry-run surrogates the same series stays at 0.87–1.02. Per-level pair contributions in the zeros are
  **anti-correlated** over 10²–10⁴ levels: a locally high pair count is compensated further along. The surrogates
  cannot show this.
- **R1 shows why the three views are needed.** Raw R1 "grows" 2.66×, entirely from the density drift; drift-removed it
  shrinks to 0.59, in line with R2–R5. The surrogate-relative column (1.18) is not a clean correction when the zeros'
  intrinsic growth differs from the surrogates'. The drift adds variance in quadrature, so dividing the ratios leaves a
  residue. Drift-removed is the reliable view.
- **What it might be, and what it is not yet (hypotheses):** a sine-kernel (GUE) process's pair-count fluctuations are
  short-range, so its growth curve should be near-flat beyond about 100 levels. That expectation is not verified here.
  The surrogates are independent CUE_250 blocks and carry no correlation beyond 250 levels, so they cannot separate
  "generic long-sequence rigidity" from "arithmetic". The arithmetic candidate is long-range suppression of the zeros'
  fluctuations: Berry's saturation of the number variance beyond L_max ~ log(t/2π)/log 2 spacings, driven by the
  shortest primes, which is the long-range structure Phase 6 measured. Separating the two needs a single long CUE_N (or
  sine-kernel) sequence of ≥ 10⁵ levels as the baseline. That baseline has not been run. **Open lead, not a finding.**

## 4. What the verdicts say, and what they do not
- They say that, at these five heights, the pair-correlation sum for a small-separation test function matches CS07
  Thm 4.1 with its arithmetic lower-order term at full amplitude, to 2–5% per bin and 0.6% pooled. Leading order alone
  (μ = 0) is excluded everywhere.
- They test one test function (the R3 primary, small separations: bump at 0.5 spacings). The 2–3 other family members
  are descriptive and not yet computed on the zeros.
- They are conditional on the ratios conjecture in the sense that CS07's formula rests on it. A PASS is consistent
  with the conjecture's lower-order prediction. It is not a proof of anything about ζ.
- Prior work: Berry–Keating 1999 compared the same formula visually through Σ², near t ≈ 3.7·10⁸ and 2.7·10¹¹. R3
  (t ≈ 4.1·10⁸) sits next to their Fig. 6 height.

## 5. Next (proposed; Will's call)
1. Route (a) (Will: GO after the R₂ seal): milestone 1, the U(N) construction reproducing the exact CUE_N tables, as a
   gate.
2. Optional, descriptive: the long-sequence CUE baseline for §3's shrinking error bars, to tell generic rigidity from
   the arithmetic.
3. Phase 1 decisions D1–D6, then its seal.
