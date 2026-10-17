# Route (a) follow-up — two independent replications (round 50)

**Status.** The follow-up selection (`FOLLOWUP_SELECTION_RULE.md`, 6122a236 + amendment 1, 968a8066) is abandoned
after its one run, which was defective (d3c50fa8); no choice was made from it. Both candidates now run as independent
replications of route (a), with no selection (Will, round 50, `../ph2/PH2_DECISIONS_2026-10-07.md`).

**Timing (recorded, not hidden).**
- This file is committed after the route (a) PASS and after the defective run.
- That run printed both candidates' CUE replicate SEs: (A) SE_pool 0.0386 → 0.0039 over s ≤ 1.0 … 2.1 (skip-rule
  variants); (B) SE_pool 0.0235, 0.0162, 0.0187, 0.0154, 0.0145 at L = 0.5, 1, 1.5, 2, 3. They were seen before
  round 50 and before the window rules below were fixed.
- The rules below are committed **before** S_A, (B)'s L or any ∂μ*/∂μ is computed with the fixed code.

**Withdrawn.** The block-cut n ≥ 3 share criterion for (B) is withdrawn as ill-conditioned: Δκ₃ = 3ΔF₂ + ΔF₃ nearly
cancels, so the share is 3.9, 9.0 and 15.8 at L = 1.5, 2 and 3, and identically 1 at L = 1. This is the same
cancellation that makes the per-order constraints in `ROUTE_A_FINDINGS.md` §3 non-identifiable.

**Common to both.**
- μ is the sealed route (a) family's global amplitude: every arithmetic part (CS08's n ≤ 5 correction) is scaled
  jointly, with μ = 1 the CS prediction and μ = 0 the sine kernel.
- The data-free inputs are `results/followup_nnn.json` (a6bb79fa), `results/followup_k3.json` (a01bf8d0) and the
  CUE_1000 replicates (R = 100 per file at F3 geometry, `results/followup_reps`, md5-of-md5s 100edbc9…).
- The five files are pooled with w_f ∝ n_f, as route (a). SE_pool = (Σ w_f² SE_f²)^½, with SE_f the SD of the
  per-file amplitude over the R replicates.

## 1. Mechanical fixes to (A)'s fit (amendment-2 items kept by round 50; needed for calibration)
1. **Resolved bins only.** (A) is fitted only on bins whose centre is ≥ S_RES, where S_RES is the smallest 1e-4 bin
   centre from which p⁽²⁾_sine ≥ P2_RES = 1e-6 on every later bin up to 3.0.
   - P2_RES is about 480× the interpolant's largest negative excursion on [0, 0.2], −2.1e-9 (d3c50fa8).
   - The window is then [S_RES, s], conditionally normalised as before. The sine-kernel probability mass below S_RES
     is computed and reported with S_RES; if it exceeds 1e-7 per spacing, that goes to Will before calibration.
2. **A fit at its bound is a failure, not a value.**
   - A fit fails if μ̂ is within 1e-6 of either bound (±20), if the negative log-likelihood is not finite at μ̂, or if
     the model density is ≤ 0 on any bin of the window at μ̂.
   - A failed fit is recorded as a failure. It never enters an SE, a mean or a verdict as a number.
   - In calibration, each file's failure count is reported. Any failure among a file's replicates is a calibration
     defect for that file and goes to Will before a seal.
3. **Every-node variants dropped.** (A) uses route (a)'s skip rule only (|T_n^sine| < RZ.SKIP → no ζ change), as the
   sealed route (a) prediction did. The every-node variants failed in d3c50fa8 (SE_pool 1.648 at every window) and
   are not carried.
4. **Red path.** A test injects one negative interpolation bin (p⁽²⁾_sine := −1e-9) inside the window at a bin with a
   positive count. The fit must report failure; a returned bound value is a test failure. A second red path checks
   that the guard in item 1 rejects a window whose model density is ≤ 0 anywhere. Both run in `followup_fit.py
   selftest`, which must pass before any calibration.

## 2. ∂μ*/∂μ, measured (no assumption that it equals 1)
- **(A):** the estimator limit μ*(μ′) of the fixed fit on expected counts p⁽²⁾_{μ′}·(bin width), per file and per
  window, at μ′ ∈ {0.98, 0.99, 1.01, 1.02}. ∂μ*/∂μ is the ±0.01 symmetric difference, and the linearity check is the
  ±0.02 difference against it (as B₂). Counts are scaled to 1e9 per window; a failed fit (§1.2) here is a defect.
- **(B):** two parts.
  1. The estimator limit: μ̂_B is affine in k₃, and κ₃(L; μ′) = κ₃^sine + μ′Δκ₃ exactly (κ₃ involves ρ₁–ρ₃ only, each
     linear in μ′). It is evaluated numerically at μ′ = 0.99, 1.01 from the stored terms, and reported.
  2. A known-answer slope on CUE_N, where κ₃ is exactly computable: for N ∈ {8, 12, 16, 24, 32}, the mean k₃ over
     disjoint windows of length L (unit mean spacing on the circle, random rotation per matrix) against the exact
     κ₃^{CUE_N}(L) from the CUE_N kernel sin(πx)/(N sin(πx/N)) with followup_k3's quadrature. The slope of mean k₃
     on exact κ₃ across N (weighted least squares, SEs from the replicates) is the measured ∂k₃/∂κ₃. Then
     ∂μ*_B/∂μ = slope × (the limit in part 1). Enough matrices per N are drawn that the slope's SE is ≤ 0.05.
     These replicates use fresh seeds, disjoint from every earlier use.
- Both are reported per file and pooled with w_f. They enter every band, power and verdict in place of 1.

## 3. (A)'s window S_A (data-free)
- **Grid:** s ∈ {1.0, 1.1, …, 3.0}.
- **Band:** (A)'s band at s is 2·SE_pool(s), from the fixed fits on the CUE replicates (§1), with SE in μ units after
  dividing by the measured ∂μ*/∂μ (§2).
- **T₅ bracket disagreement in μ units, δμ_T5(s):** per file, the estimator limit of the fixed fit with the primary
  model (ΔT₅ = −T₅^sine, "rho5_zero") on expected counts generated from the other end of the bracket (ΔT₅ = 0,
  "rho5_sine") at μ = 1, minus 1, in absolute value and divided by the measured ∂μ*/∂μ. Pooled as Σ w_f |·|.
- **S_A** is the largest s on the grid with δμ_T5(s) ≤ 0.01 × 2·SE_pool(s).
- **Checks reported with S_A; any failing check goes to Will before the prediction is tagged:**
  1. The condition also holds at every grid point below S_A. If it doesn't, S_A is not contiguous.
  2. Amendment 1's n = 6 truncation bound in μ units (route (a)'s check-(c) construction applied to 4·T₆_CAP·|T₆^sine|)
     is also ≤ 0.01 × 2·SE_pool at S_A.
  3. S_A ≤ 2.0. Past 2.0 the window needs the exact T₅ (round 50).
- **Prediction.** (A)'s tagged prediction uses the primary end (ΔT₅ = −T₅^sine). This matches the ratios model's exact
  ζ T₅ where it was computed (s ≤ 1.8: |T₅^ζ| ≤ 4.5e-6, `results/connected/`). δμ_T5(S_A) enters (A)'s δμ_sys.

## 4. (B)'s window L (data-free)
- **Grid:** L ∈ {0.5, 1.0, 1.5, 2.0, 3.0}.
- **Metric:** |∂μ*_B/∂μ| / SE_pool(L) in the global μ family, with ∂μ*_B/∂μ measured as §2 and SE_pool(L) from the
  k-statistic on the CUE replicates (as `followup_select.candidate_B`, without the share).
- **L** is the grid value with the largest metric. If two metrics are exactly equal, the smaller L is used.
- **Recorded:** the metric at every L. The SEs at every L were already seen (Timing, above).

## 5. Pipeline, per observable (round 50)
1. Tagged prediction: the data-free prediction file, with its own sha256, tagged before anything else.
2. Calibration: false-FAIL rate at μ = 1 and power at μ = 0, by route (a)'s method (bias subtracted, SE floor = CUE SD,
   band 2SE_pool + δμ_sys).
3. Seal.
4. OpenTimestamps stamp of the seal manifest, Bitcoin-attested and verified on two explorers before any decode (round
   49 protocol).
5. Fresh zeros, not yet downloaded: a new fresh set per observable (F4 for (A), F5 for (B)), declared and md5-pinned
   with `declare_fresh_sets.py`'s v2 gap rule at F3's target heights, before any download.
6. Double read: two reads in separate processes, bit-identical or VOID.

## 6. Joint reading (to be declared in both seals)
- Each test keeps its own calibrated false-FAIL rate α₁, α₂. The family-wise false-FAIL rate is reported as
  1 − (1 − α₁)(1 − α₂).
- **Both PASS:** replication of route (a) by two further observables.
- **Exactly one FAIL:** reported as a FAIL for that observable, with attribution limited to "observable-specific model
  terms or estimator". It is not a refutation of route (a).
- **Both FAIL:** route (a)'s PASS is called into question, and that is reported plainly.

## Round 51 addendum (Will, 2026-10-16)
**Geometry.** The gap rule stays. F4, for (A): the three declared files (L = 17.5, 19.75, 21.25). F5, for (B): those
three plus the L ≈ 15.59 file. The asymmetry is deliberate: the weaker observable, (B), gets the extra low-height file.
This was decided before any F4/F5 prediction, calibration or download (`../ph2r2/FRESH_SETS_F4_F5.md`).

**(A).** S_A = 1.6 from the window_A rerun (b3fa4824), with the refusal fix: an invalid window is recorded as invalid,
never a hang. `followup_fit.py selftest` gains a red path for it (an injected negative-density window, run through the
pool with a timeout).

**(B)'s L = 3 known-answer flag (committed before the rerun).** L stays at 3.
- **Rerun:** `followup_cuen.py` with fresh seeds [20261016, 51, N, batch] and 2× the replicates (4000 batches of
  20,000 matrices per N, N = 8, 12, 16, 24, 32), merged to `results/followup_cuen_r51.json`. The first run's batches are
  not pooled with it.
- **Reading:** the χ² of the L = 3 known-answer fit on its 3 degrees of freedom, p = P(χ²₃ ≥ χ²).
  - p ≥ 0.01: the first run's χ² of 11.0 is recorded as chance.
  - p < 0.01: the known-answer check is recorded as marginal at L = 3, and that is carried as a caveat on (B)'s result.
- The rerun's L = 3 slope is reported with the first run's. Neither changes L.
