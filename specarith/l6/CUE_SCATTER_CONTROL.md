# CUE scatter control for the own-bootstrap SE check (round 72; DESCRIPTIVE; committed before computing)

**Question.** The zeros' per-file estimates scatter less than their own bootstrap SEs at G = 300 predict: pooled
χ² 1.65 on 9 dof (`OWNBOOT_SE_CHECK.md`). Does the identical pipeline give χ²/dof ≈ 1 on CUE?
- **If yes,** the zeros' low scatter is a property of the zeros (long-range rigidity).
- **If CUE is also low,** the estimator pipeline is suspect. Work stops and the pipeline is diagnosed.

## Deviation from round 72's wording (stated before computing)
Round 72 asks for file-sized segments matched to the F3/F4/F6 zero counts, about 5·10⁶ levels each. The L6 baseline
holds 50 × 10⁵ = 5·10⁶ levels in all: enough for one file-sized segment, so a scatter χ² at file size cannot be formed
from it. A matched set (12 file-sized segments, or more for power) would take about 600 more N = 10⁵ sequences, roughly
120 h on spot. That is Will's call. What runs now, at three scales:
1. **Segments of 10⁵ levels:** each of the 50 long CUE sequences is one segment, run through each file's estimator
   geometry. That gives 50 estimates per (statistic, file), so χ² on **49 dof**.
2. **Segments of 10⁶ levels:** 10 consecutive sequences concatenated (seams every 10⁵, as in the L6 concatenation
   variant), giving 5 segments per (statistic, file) and χ² on **4 dof**. This is a fifth of a file, the closest the
   data allow.
3. **File size, existing records:** each file's declared calibration holds 200 file-sized CUE_1000 replicates through
   the identical estimator. It records the replicate SD and the mean bootstrap SE at each G. The proxy χ²/dof is
   (SD/SE_boot,mean(300))².
   - These replicates are stitched. Stitching does not change these statistics' block variance within ±14% at
     G = 1,000 (§13).

## Method
- **Estimators:** the identical per-file estimators, exactly as `l6_base.stats` runs them:
  - route (a): `route_a_read.fit_file`;
  - (A): `followup_read.fit_file_A`;
  - corrected (B): `b2_est.zeros_stats` then `b2_read.fit`.

  Same seeds as the L6 statistics run, so the 10⁵-segment SEs must equal the stored `results/base/stats` SEs bitwise.
  That equality is checked and recorded. The estimate μ̂ is now kept as well.
- **Scatter χ²,** per (statistic, file, G): Σ_r (μ̂_r − m)²/SE_r(G)², where m is the inverse-variance weighted mean, on
  R − 1 dof, with the percentile under χ²_{R−1}.
  - The files share segments, because the same CUE sequences run through different file geometries. So the files are
    not independent, and no cross-file pooled percentile is formed. Per statistic, the median χ²/dof over its files is
    reported.

## Reading (declared)
Based on the 10⁵-segment median χ²/dof at G = 300 for each statistic:
- **≈ 1** if it lies inside the central 95% of χ²_49/49, which is [0.64, 1.43].
- **Low** below 0.64, **high** above 1.43.
- **If any statistic is low, work stops** for that statistic's pipeline and it goes to diagnosis.
- The 10⁶-segment and file-size results are reported beside it. With 4 dof the 10⁶-segment χ² is coarse: its central
  95% band is [0.12, 2.79].
- **For comparison, the zeros:** 0.11 (route (a)), 0.37 (A) and 0.16 (corrected (B)), each on 2–4 dof.

Code: `round72.py ctrl` / `ctrl_cat` / `ctrl_summary` → `results/r72/ctrl_*.json`, `results/r72/CTRL_SUMMARY.json`.

## Result (`results/r72/CTRL_SUMMARY.json`)
| statistic | 10⁵ segments, G = 300: median χ²/dof (per-file range; 49 dof) | 10⁶ segments, G = 300 (4 dof) | file-size calibration proxy | zeros (for comparison) |
|---|---|---|---|---|
| route (a) | **1.14** (1.09–1.21) | 0.47–0.64 | 0.88–1.15 | 0.11 |
| (A) | **0.97** (0.93–0.99) | 0.71–0.82 | 0.93–1.04 | 0.37 |
| corrected (B) | **1.06** (1.05–1.07) | 0.84–0.96 | 0.95–1.11 | 0.16 |

- **The pipeline reproduces itself:** all 50 × 12 re-run SEs equal the stored L6 statistics bitwise.
- **The 10⁶-segment values** all sit inside their 4-dof band of [0.12, 2.79], at percentiles 25–57.
- **On CUE, χ²/dof rises with the block length of the SE.** For route (a) at 10⁵ it goes 1.14 → 1.32–1.49 from
  G = 300 to 10⁴. That is the moving-block bootstrap's G/n bias: at n = 10⁵ and G = 10⁴ the block SE runs a few to
  20% low, as the concatenation variant shows (§13: concat/primary 0.87–1.24 at 10⁴). The zeros' files have
  n ≈ 5·10⁶, so their G/n ≤ 0.002.

**Reading as declared: ≈ 1 for all three statistics.** The identical pipeline, run on CUE, gives a scatter consistent
with its own bootstrap SEs at G = 300, at every scale available.

**Recorded (round 72): the zeros' low file-to-file scatter is a property of the zeros (long-range rigidity),** not of
the estimator pipeline.

**Not run:** the file-sized matched control. It needs about 600 more sequences, roughly 120 h on spot; that is Will's
call.
