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
