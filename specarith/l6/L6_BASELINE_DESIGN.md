# L6 long baseline: design and pre-registration (approved by Will in round 66)

**Status:** approved in round 66, and committed before any step-0 run or baseline sequence exists. The outcome is **descriptive**: no verdict, no seal. Any confirmatory
version gets its own pre-registration on fresh heights (round 64).

**Purpose.** The L6 descriptive pass (`results/L6_TABLE.md`, 3fa5a4d0) compares the zeros' block variances with the CUE_1000
calibrations only up to 300-level blocks. Longer blocks are marked "baseline invalid: stitched CUE_1000": the calibration
sequences are independent rotated 1,000-level matrices, so they carry no rigidity beyond one matrix. A long CUE sequence
run through the identical block statistics unblocks the long-block comparison for route (a) (F3), (A) (F4) and the
corrected (B) (F6). The pair statistic already has a long baseline (R₂ §6, a 10⁶-level Dumitriu–Edelman GUE) and is not
the target here. It is used as a cross-check (§5).

## 1. Generator (preferred): CUE_N through Killip–Nenciu CMV, no unfolding
- **Sampler:** `cs4/cbe.py`, reused unchanged.
  - Killip–Nenciu Verblunsky coefficients α_k ~ Θ_{β(N−k−1)+1}, β = 2, with α_{N−1} uniform on the circle. The CMV
    matrix built from them has exactly the CUE_N eigenvalue law.
  - Eigenphases are the roots of the lifted Prüfer phase ψ_{N−1}(θ) = c_m, found by safeguarded Newton (O(N²) per
    sequence) and certified by `certify()` (strictly increasing within one period, so no root is missed or doubled).
- **No unfolding:** CUE's density is uniform, so x = Nθ/2π exactly. There is no fitted density and no drift removal on
  the baseline side, which avoids the high-pass caveat below.
- **Size:** N = 10⁵ levels per sequence, with R = 50 independent sequences (5·10⁶ levels in all, about one zero file).
  - Blocks are formed **within** a sequence and never across two, so there are no seams.
  - G ≤ 10⁴ means G/N ≤ 0.1. Finite-N effects at that scale are checked by gate 1 against the exact CUE_N formula, not
    assumed.
- **Seeds:** [20261020, 65, r] for r = 0..49, disjoint from every earlier use.
- **Machine:** spot, CPU (`roots_np`), 50 processes under `nice`. Rough cost per Newton
  iteration: N recursion steps of N-element vector operations, 10¹⁰ elementwise operations at N = 10⁵; about 10
  iterations, so on the order of 10–20 minutes per sequence and about 1 hour wall time. To be
  confirmed by the step-0 timing at N = 10⁵. The char GPU path (`roots_gpu`) is fp64 on a 3080 and is not planned.

## 2. Step 0: cbe.py red paths first (round 65: "if cbe.py is reused, re-run its red paths first")
All of these must hold before any baseline sequence is drawn. Any failure stops the work and goes to Will.
- **Existing suite** (on spot CPU, gpu = False), each as recorded in `results/calib/cbe_selftest.log`:
  - V1: Prüfer roots equal the dense CMV eigenvalues.
  - V2: β = 2 against Haar (Mezzadri).
  - V3: β = 1, 2, 4 nearest-neighbour spacing variance against the sine-process limits.
  - V4: no doubled roots on 10⁴ N = 1000 matrices. Its red path must also reproduce: the pre-fix Newton step doubles
    some roots.
- **New, at the target size:**
  - **V5:** N = 10⁴, Prüfer roots against dense CMV eigenvalues (numpy `eigvals`, feasible at 10⁴), max |Δθ|·N/2π ≤ 1e-8.
  - **V6:** N = 10⁵ certification. `certify()` passes on a real draw. Red path: the same draw with one root deleted, and
    with one root duplicated, must each be refused.
  - **V7:** N = 10⁵ Prüfer residual. Every accepted root has |ψ_{N−1}(θ) − c_m| < F_ACCEPT. Report the maximum, and the
    float64 headroom of ψ ~ 2πN.

## 3. Gates on the baseline (both must hold before any comparison with the zeros)
**Gate 1: Σ²(L) against the exact CUE_N number variance, L up to about 10³ spacings.**
- **Exact formula:** for an arc of expected count L in CUE_N, Σ²_N(L) = 2 Σ_{m≥1} min(m, N) sin²(πmL/N)/(π² m²). This is
  the CUE linear-statistic variance Σ_m min(|m|, N)|f̂_m|² for the arc's indicator. It is summed to m = 50N with the
  remainder bounded analytically. As a check, it must agree with the sine-kernel Σ²(L) to O(L/N) at L ≪ N.
- **Estimate:** on the pooled baseline, the variance of counts in arcs of length L at 32 offsets per L, averaged over
  offsets. The SE comes from the spread over the R = 50 sequences.
- **Grid:** L = 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000.
- **Criterion:** |z| ≤ 3 at every L, and Σ z² within its χ²₁₀ 99% quantile.
- **Witnesses (the gate must be able to fail):**
  - (i) a stitched sequence of 100 independent CUE_1000 matrices (10⁵ levels, the calibration's construction) must fail
    the gate at L ≥ 500, where it has no rigidity across seams;
  - (ii) a β = 4 (CSE) CMV sequence must fail at small L;
  - (iii) a Poisson sequence must fail everywhere.
**Gate 2: independent-replicate consistency.**
- Split the 50 sequences into two halves of 25, A and B, by seed parity.
- For each block statistic (§4) and each G, take the ratio Var_A(G)/Var_B(G) of the bootstrap block variances.
- **Criterion:** |log ratio| ≤ 3·SE at every G, with the SE from the spread over sequences within each half.
- **Witness:** half A against a stitched-CUE_1000 half must fail at G ≥ 1000 for at least one statistic. If it cannot
  fail anywhere, the long baseline adds nothing over the calibration, and that is reported.

## 4. The block statistics: identical to the zeros'
Each statistic is the zeros' read code, run on the baseline as on a file. These are the statistics in `results/L6_TABLE.md`.

| test | statistic (read code) | block lengths G | normalisation |
|---|---|---|---|
| route (a) | μ̂ of the n ≤ 5 spacing law and its moving-block bootstrap SE (`route_a_read.fit_file`) | 300, 1000, 3000, 10000 spacings | each F3 file's prediction (μ units) |
| (A) | μ̂ of the NNN law, s ≤ 1.6, and its bootstrap SE (`followup_read.fit_file_A`) | the same | each F4 file's prediction |
| corrected (B) | offset-averaged k̄₃ at L = 4 and its segment bootstrap SE (`b2_est.zeros_stats`) | 300, 1000, 3000, 10000 units | each F6 file's Δκ₃ |

- **Per sequence and per file geometry**, the baseline's bootstrap SE at G is computed in the same units as the zeros'.
  Var_baseline(G) is the mean over sequences of SE² scaled to the file's level count (SE² ∝ 1/n at fixed G).
- **Output, per test, file and G:** Var_zeros(G)/Var_baseline(G), with an SE from the spread over sequences. The zeros'
  side is the existing read records (no re-read).
- The table replaces the "baseline invalid" cells of `L6_TABLE.md` with values against the long baseline, and keeps the
  CUE_1000 column beside it for comparison.

## 5. Cross-check against the existing pair-statistic baseline (descriptive)
- The R₂ drift-removed pair-sum statistic (`ph2r2/longbase.py`) is also run on the CMV baseline, mapped onto the five R₂
  bins as in v2.
- Its growth SD(10⁴)/SD(100) should agree with the 10⁶-level DE GUE's 0.92–0.99 (R₂ §6) within the combined SE.
- Disagreement is reported. It would point at one of the two generators (or the DE unfolding, §6), not at the zeros.

## 6. Fallback: Dumitriu–Edelman β = 2 (only if step 0 or gate 1 fails for the CMV route)
- **Generator:** Hermite β = 2 tridiagonal of size n_mat, all eigenvalues by LAPACK `sterf` (as `ph2r2/longbase.py`).
  **Bulk only:** the central 50% of the spectrum.
- **Unfolding:** the fixed semicircle count n_mat·F(x), R² = 8·n_mat, never fitted.
- **High-pass caveat (stated as required):**
  - The baseline needs an unfolding, and any unfolding is a reference density for long-wavelength density fluctuations.
  - A fitted or smoothed density, or a drift removal applied to the baseline, would act as a high-pass filter. It would
    remove the long-range variance this baseline exists to measure, and bias Var_baseline(G) low at large G.
  - Even the fixed semicircle leaves the global "breathing" mode: tr H² fluctuates about its mean, so the realised
    spectrum is dilated relative to the fixed unfolding. That adds a long-range component growing with L.
  - Gate 1 (Σ² against the sine kernel up to 10³) bounds both effects at the comparison's scales. Above 10³ spacings
    they are not bounded, and are reported as a limitation.
- The R₂ 10⁶-level DE levels already on spot (8 sequences, 94% of the spectrum, unfolded) could serve if cut to the
  central 50%. They would go through the same gates and are not reused without passing them.

## 7. Reporting
- **Descriptive only.** For each test: Var_zeros/Var_baseline against G = 300 … 10⁴, per file, with SEs, beside the
  CUE_1000 column.
- **Reading:** no threshold, no verdict. The question is whether the 300-level deficit (route (a) 0.78, (A) 0.69,
  corrected (B) 0.31; each rising with height) persists or deepens at long blocks against a baseline with real long-range
  rigidity, as it does for the pair statistic.
- **What would count as a seam artefact:** the CUE_1000 cells moving towards the long-baseline values. Bear in mind that
  even 300-level blocks can straddle CUE_1000 seams.
- **Stops:** a step-0 failure, a gate-1 or gate-2 failure, or a witness that does not fire. In any of these, nothing is
  compared with the zeros, and the failure goes to Will.
- **Artifacts:** `l6/results/baseline/` (per-sequence JSON, no levels committed; the levels stay on spot), the gate
  reports, and an extended `L6_TABLE.md`.

## 8. Round 66 additions (committed with the approval, before any run)
**Order:** step 0 → generation on spot → gates 1 and 2 with their witnesses → comparisons. Any stop goes to Will.

**Three ratios per block length G (descriptive only):**
1. **stitched/long, the artifact:** Var(G) of the CUE_1000 calibration (its declared mean bootstrap SE at each file's
   geometry) over Var(G) of the long baseline, per test and file.
2. **zeros/long, the arithmetic part:** Var(G) of the zeros (the existing read records) over Var(G) of the long baseline.
3. **The pair-statistic cross-check:** the R₂ drift-removed pair-sum growth SD(10⁴)/SD(100) on the CMV baseline against
   the 10⁶-level DE GUE's (R₂ §6).

The zeros/stitched ratio of the existing L6 table is then the product of (1) and (2) by construction.

**Geometry (declared here, before any number).**
- The zeros' bootstrap SEs come from files of 5–7·10⁶ levels; the baseline sequences have 10⁵. A moving-block bootstrap
  on n points with block G is biased low by roughly G/n, which is about 10% at G = 10⁴ on one 10⁵-level sequence.
- **Primary, as approved:** per sequence (blocks within one sequence), scaled to each file's level count.
- **Sensitivity variant:** the 50 sequences concatenated into one 5·10⁶-level series with seams every 10⁵ levels, run
  through each read's code exactly as the calibration ran its stitched CUE_1000 series. At G ≤ 10⁴ at most G/10⁵ of the
  blocks straddle a seam.
- Both are reported. Where they differ by more than their combined SE, that is reported and neither is preferred
  after the fact.
- For the corrected (B), the variant is `b2_est.cue_stats` with 10⁵-level pieces (the calibration used 1,000-level
  pieces).

**Calibration-method note (round 66):** if gates 1 and 2 pass, propose single-sequence CUE baselines as the calibration
standard for future tests, in place of stitched CUE_1000. This is a proposal only; no sealed result is re-read.

## 9. V7 diagnostic (round 67; committed before it runs)
**Run.** The N = 10⁴ draw of V5 (seed [20261020, 65, 905]; deterministic, so the same Verblunsky coefficients and the
same roots) is re-solved by `roots_np` and by the dense CMV eigensolver. For every root the record holds:
- its residual |f| = |N·θ − c_m + φ(θ)| (V7's quantity);
- ψ′(θ) = dψ_{N−1}/dθ;
- ulp(θ);
- the float64 floor ψ′·ulp(θ);
- its distance to the dense root in unfolded units.

A root is **verified** if it matches the dense root to ≤ 10⁻⁸ unfolded (V5's tolerance).

**Reading (Will's, round 67).**
- **If any verified root has |f| > F_ACCEPT (1.0):** V7 is miscalibrated. Its threshold is recalibrated as a post-hoc gate
  amendment, in a form declared now, before any N = 10⁴ residual is seen:
  - a root passes the amended V7 iff |f| ≤ F_ACCEPT + K·ψ′(θ)·ulp(θ), the float64 floor of f at the root's own
    location;
  - K is the smallest power of two ≥ 1 such that every verified N = 10⁴ root passes;
  - ψ′ grows with N, so the threshold scales with N without any N-specific constant.

  Then V7 is re-run at N = 10⁵ on the step-0 draw (seed [20261020, 65, 967], identical roots), saving θ and ψ′. If it
  passes, the 50 CMV sequences are generated on spot in parallel (the committed pipeline, unchanged).
- **If every verified root passes the original V7:** the N = 10⁵ failure is real. The work falls back to
  Dumitriu–Edelman (§6), with one amendment from Will: unfold with the **finite-N** GUE density (the exact one-point
  density of GUE_n), not the asymptotic semicircle, with the high-pass caveat stated.
- **The GPU port is skipped** (round 67).
- **A root that is not verified** (more than 10⁻⁸ from its dense root) is reported on its own: a sampler-accuracy
  finding. Neither branch is taken, and the case goes back to Will.

## 10. V7 targeted check at N = 10⁵ (round 68; committed before it runs)
**Why §9 did not decide.** At N = 10⁴ the largest ψ′ is 1.7·10¹³, so the float64 floor ψ′·ulp(θ) is at most about
0.015, and no N = 10⁴ root can reach V7's threshold of 1. §9's "every verified root passes" is therefore consistent
with both readings.

**Run.** The step-0 N = 10⁵ draw (seed [20261020, 65, 967]; identical Verblunsky coefficients and roots) is re-solved by
`roots_np`. Saved per root: θ, ψ′(θ), and the V7 residual |f| = |N·θ − c_m + φ(θ)|. A root is **flagged** if
|f| > F_ACCEPT = 1. Every flagged root gets three independent checks:
- **(a) float floor:** |f| ≤ BRACKET_ULPS·ψ′(θ)·ulp(θ) + 10⁻⁶, with BRACKET_ULPS = 4 (cbe.py's own acceptance width).
  The 10⁻⁶ allows for rounding in f's evaluation (|N·θ| ≈ 6·10⁵ gives ulp ≈ 10⁻¹⁰).
- **(b) sign change:** in float64, f(θ − 4 ulp) < 0 < f(θ + 4 ulp), stepping exactly 4 representable doubles by
  `np.nextafter`.
- **(c) extended precision:**
  - ψ_{N−1} and c_m are recomputed in mpmath at 40 digits (the float64 α_k are taken as exact inputs; c₀ from the mp
    ψ_{N−1}(0) and arg α_{N−1}).
  - The root of f_mp is bracketed starting from [θ − 64 ulp, θ + 64 ulp], doubling the half-width up to 2²⁰ ulp until f
    changes sign, then bisected to a width of 10⁻³⁰.
  - The check holds iff |θ_mp − θ|·N/2π ≤ 10⁻⁶ mean spacings. No sign change within 2²⁰ ulp counts as a failure of (c).

**Reading (round 68).**
- **(a), (b) and (c) hold for every flagged root:** V7 was miscalibrated, and the §9 amendment applies.
  - **K as committed:** calibrated on the verified N = 10⁴ roots, where none exceeded F_ACCEPT, so the minimum rule
    gives K = 1.
  - **If a (c)-verified N = 10⁵ root still exceeds F_ACCEPT + 1·ψ′·ulp:** K becomes the smallest power of two covering
    all (c)-verified N = 10⁵ roots. This is declared here, before the run, because the N = 10⁴ calibration cannot reach
    this regime. It is recorded as part of the post-hoc amendment.
  - The amended V7 is then reported at N = 10⁵, and the CMV generation starts (the committed pipeline; its step-0 check
    now requires this run's pass in place of V6/V7's original verdict).
- **Any flagged root fails (b) or (c):** the work falls back to Dumitriu–Edelman via a committed design addendum (finite-N
  density unfolding, with the high-pass caveat).
- **(a) fails while (b) and (c) hold, for some root:** the case is not covered by round 68 and goes back to Will.
- **Outputs:** `results/step0/v7check.json` (the counts, the per-flagged-root table, the reading and K), and θ and ψ′ as
  `.npy`, kept on spot (they are not committed).
