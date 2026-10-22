# Own-bootstrap SE validation (round 71; DESCRIPTIVE; data already seen; method committed before computing)

**Question.** Do the zeros' own moving-block bootstrap SEs describe the actual file-to-file scatter of the per-file
estimates? If they do, a future pre-registration could use them in place of the CUE floor. The L6 comparison
(`L6_BASELINE_DESIGN.md` §13) shows the CUE floor overstates the zeros' variance by a factor of 1.3–5.

## Inputs (committed read records; nothing recomputed)
| statistic | read record | fresh files | declared block length |
|---|---|---|---|
| route (a) | `cs4/results/read/run1/ROUTE_A_READ.json` | F3 (5) | BLOCK = 300 (`ROUTE_A_SEAL.md`) |
| (A) | `cs4/results/followup_read/A/run1/FOLLOWUP_READ.json` | F4 (3) | BLOCK = 300 (`FOLLOWUP_A_SEAL.md`) |
| corrected (B) | `cs4/results/b2_read/run1/B2_READ.json` | F6 (4) | BLOCK = 300 (`CORRECTED_B_SEAL.md`) |

- **These are every fresh file each statistic was read on.** The sealed (B) on F5 is a different statistic (L = 3, one
  window grid) and is not included.
- **Per-file estimate:** μ̃_f = (μ_f − bias_f)/g_f, the sealed read's own value (`result.mu_file`). Here μ_f is the raw
  estimate, bias_f the declared calibration bias, and g_f the gain: 1 for route (a), g_f for (A) and (B) as sealed.
- **Own-bootstrap SE:** SE_own,f = SE_boot,f(BLOCK)/g_f, the zeros' own moving-block bootstrap SE at the declared block
  length (`records[f].se["300"]`). g_f is recovered as (μ_f − bias_f)/μ̃_f; for route (a) that gives exactly 1.
  - The sealed rule used max(SD_f, SE_boot,f(L ≥ 300)), where SD_f is the CUE floor, widened by SD_f/√R. The own SE
    leaves out both.
  - Because SE_boot falls with L, the max over L ≥ 300 is the value at 300.

## Statistic
- Per statistic: the inverse-variance weighted mean m = Σ w_f μ̃_f / Σ w_f with w_f = 1/SE_own,f², and
  **χ² = Σ (μ̃_f − m)²/SE_own,f² on n − 1 dof.** Reported: χ²/dof and the percentile P(χ²_{n−1} ≤ χ²).
- **Pooled:** the sum over the three statistics, on 4 + 2 + 3 = 9 dof. The files are disjoint, so the three are
  independent.
- **Also reported, descriptively:**
  - the same χ² at G = 1,000, 3,000 and 10,000;
  - the χ² against μ = 1 (n dof);
  - the χ² with the sealed SEs (`result.se_file`), for comparison.

## Reading (declared before computing)
- **Validates:** the pooled 9-dof percentile lies in [2.5, 97.5], and no single statistic lies outside [0.5, 99.5].
- **Too small:** a pooled percentile below 2.5 means the own SEs still overstate the scatter.
- **Too large:** above 97.5, they understate it.
- **Power, stated before computing:** with 9 dof, the central 95% of χ²/dof runs from 0.30 to 2.11. So the check can
  only catch an SE that is wrong by a factor of about 1.45 or more (√2.11), in either direction. A pass does not
  establish the SEs to better than that.
- **If it validates:** a draft calibration rule goes to Will (`CALIB_RULE_DRAFT.md`, not committed).

Code: `ownboot_chi2.py` → `results/ownboot_chi2.json`.

## Result (`results/ownboot_chi2.json`)
| statistic | files | χ² / dof at BLOCK = 300 | χ²/dof | percentile | own SE / sealed SE | χ² with sealed SEs (percentile) |
|---|---|---|---|---|---|---|
| route (a) | 5 | 0.43 / 4 | 0.11 | 2.0 | 0.74–1.00 | 0.27 / 4 (0.8) |
| (A) | 3 | 0.74 / 2 | 0.37 | 30.8 | 0.78–0.96 | 0.62 / 2 (26.5) |
| corrected (B) | 4 | 0.48 / 3 | 0.16 | 7.8 | 0.50–0.67 | 0.16 / 3 (1.6) |
| **pooled** | 12 | **1.65 / 9** | **0.18** | **0.4** | | 1.05 / 9 (0.1) |

The sealed gains are all 1, so SE_own = SE_boot(300).

**Reading as declared: does not validate, too small.**
- The pooled percentile is 0.4, below 2.5: even the own bootstrap SEs at the declared block length overstate the
  file-to-file scatter. Each statistic alone is inside [0.5, 99.5].
- Own SEs bring the pooled χ² up from 1.05 (sealed SEs, 0.1st percentile) to 1.65. That is the right direction, but not
  enough.

**Descriptive, beyond the declared reading.** The own SE keeps falling with block length (the zeros' rigidity), and the
χ² rises with it:

| G | 300 | 1,000 | 3,000 | 10,000 |
|---|---|---|---|---|
| pooled χ² / 9 | 1.65 | 2.23 | 2.51 | 3.04 |
| percentile | 0.4 | 1.3 | 1.9 | 3.7 |

- The SE that matches the observed scatter is the long-block one. At G = 10⁴ the pooled χ² would sit inside the
  declared range, but that block length is chosen after seeing this table. It is not a validation.
- **Caveats:**
  - only 12 files (9 dof), at heights from 1.5·10⁷ to 1.1·10¹⁰;
  - a low χ² is partly chance at this size; the 0.4th percentile is about a 1-in-250 event;
  - per-file bias corrections can only add scatter, not remove it.
- Against μ = 1 (n dof, at BLOCK = 300): route (a) 0.50/5, (A) 0.74/3, corrected (B) 0.60/4.
- **No calibration-rule draft:** round 71 asked for one only if the check validates. What a future rule would have to
  settle (which block length, and how to declare it before data) goes to Will.
