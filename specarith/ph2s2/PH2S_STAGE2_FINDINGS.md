# PH2S Stage 2 — findings (read on F2 under PH2S_SEAL_2.0)

**Headline (Will, twenty-ninth round):** *On five fresh heights, the suppression of the zeta zeros' pair-statistic
block variance matches a parameter-free prediction from Conrey–Snaith's four-point correlations (conditional on the
ratios conjecture): measured/predicted shrink = 1.01 [0.89, 1.14]; the zeros sit 16 SE below the sine-kernel value.
The prediction was publicly tagged before the test data was read.*

**Verdict: PASS.** The zeros' tapered window-variance growth on F2 agrees with CS08's parameter-free prediction (tag
`ph2s-stage2-prediction`) under the sealed rule (tag `ph2s-stage2-seal`, commit 91f74031). Stage 1 established that
the suppression exists; Stage 2 tests its size.

**Post-release note (2026-10-12): a second CS08 erratum; the prediction recomputed.**
- **The erratum.** After this read, a second erratum in Conrey–Snaith (2008) was found: the sign of the prime-sum
  term in J*({a},{b₁,b₂,b₃}) (`../cs4/CS08_ERRATUM.md` §4).
- **It was in the prediction code.** This differs from the A* erratum, which the code had right from the start.
- **Recompute.** The full prediction pipeline was rerun with the sign corrected (`../cs4/run_gs_zeta_fix4_spot.sh`).
  It was compared with the sealed values (`../cs4/compare_fix4.py`, `../cs4/results/compare_fix4.json`) against a
  10⁻³ budget that Will set before the run.
- **Result:** the largest change in any sealed quantity is 1.2e-9 (v_B, relative).
  - Per-file ĝ_B moves by ≤ 3.4e-10.
  - The pooled prediction goes from 0.6830255987 to 0.6830255986.
  - ρ₁ moves by ≤ 7.6e-10.
  - z_pool stays −0.22, and the per-file z are unchanged.
- **The verdict and every number below stand.**

**Limits (Will, twenty-ninth round):**
- **Conditional on the ratios conjecture,** like R₂. The prediction uses CS08's ratios-conjecture n ≤ 4 correlations.
  A PASS is evidence for that conjecture's higher-order structure, not a theorem about ζ.
- **The agreement is to about ±13%;** nothing finer is supported.
- **One statistic and one taper:** the R₂ bump (u, w) = (0.5, 0.3) and the Gaussian window taper, at b = 100 and 10⁴.
  No height trend is claimed. The two top files landing on opposite sides is what five files look like.

- **Read:** 2026-10-11 on spot (`s2read.py read`, the sealed code; hashes checked against the seal JSON before the run).
  - All five F2 md5s matched their pins, locally and on spot, before any decode.
  - Window counts equal the pinned counts at every rung in all five files.
  - Outputs: `results/read/S2_READ.json`, `S2_READ.md`, `s2read_run.log`.

## 1. Sealed result
| file (ℓ) | ĝ_B ± SE | g_pred | z | weight |
|---|---|---|---|---|
| zeros_42446000 (15.7502) | 0.6648 ± 0.0322 | 0.6703 | −0.17 | 0.1733 |
| zeros_90746000 (16.4972) | 0.6421 ± 0.0386 | 0.6656 | −0.61 | 0.1813 |
| zeros_193646000 (17.2491) | 0.6508 ± 0.0365 | 0.6646 | −0.38 | 0.1902 |
| zeros_1848446000 (19.5003) | 0.6394 ± 0.0386 | 0.6829 | −1.13 | 0.2151 |
| zeros_17541746000 (21.7500) | 0.7759 ± 0.0438 | 0.7201 | +1.27 | 0.2400 |

- **Pooled (C):** ĝ_B = 0.6792, 95% CI [0.6441, 0.7143], beside a pooled prediction of 0.6830 (same weights).
- **R2:** d_pool = −0.0038 ± 0.0175, so z_pool = −0.22 and |z_pool| ≤ 2 holds.
- **R1:** 5 of 5 files lie within 3 SE (≥ 4 required).
- **Guard:** 2·SE_pool = 0.0351 ≤ 0.07, so the test is RESOLVABLE. The achieved precision is slightly better than the
  pre-read's κ = 1 estimate of 0.037.

## 2. Descriptive (not sealed; arithmetic on the sealed numbers)
- **Distance from GUE:** the pooled ĝ_B lies 0.280 below the sine-kernel g_GUE,B = 0.9591, which is 16 SE_pool. This
  is consistent with Stage 1's direction.
- **Size of the shrink:** the measured pooled shrink is 1 − ĝ/g_GUE,B relative to the predicted one, which gives
  0.2799/0.2761 = 1.01. The 95% interval is [0.89, 1.14], so the size agrees with CS08 to about ±13%.
- **Per-file scatter:** the z values (SD ≈ 0.9) show no sign of SE inflation.
  - The two highest files sit on opposite sides of their predictions (−1.13 at ℓ = 19.5, +1.27 at ℓ = 21.75).
  - With five files at this SE, no height trend in the residual can be resolved, and none is claimed.
- **Ladder:** the v̂_B ladder at all five rungs is in `S2_READ.json`.

## 3. Standing and what is next
- **Standing:** this is a pre-registered test of the size, not only the direction, of the zeros' variance shrink. The
  prediction was public before any F2 zero was downloaded, the rule and weights were sealed before the read, and the
  GUE calibration gives a false-FAIL rate of 5.5%.
  - What PASS licenses: agreement to within the pooled CI, about ±13% of the shrink.
  - What it does not license: a test of the CS08 correlations' individual terms, or of anything finer than this CI.
- **Next (twenty-fifth round):** one Zenodo release bundling prediction, seal and result.
