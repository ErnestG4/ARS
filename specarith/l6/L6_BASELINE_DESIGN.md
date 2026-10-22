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
  - **Same matrix (Will, round 68 note).** The Verblunsky coefficients are those of the float64 draw. They are saved
    as complex128 (`v7check_alpha.npy`) and carried into mpmath unchanged, as `mp.mpc(complex(x))`, which is an exact
    conversion of each binary double. They are never regenerated or re-rounded at higher precision. (c) therefore
    compares roots of the identical matrix. On a 500-level draw the refinement reproduced the float roots to
    10⁻¹³–10⁻¹⁶ spacings.
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

## 11. Round 69 ruling: the CMV route accepted (ruling record; amended (a) committed before it runs)
**Ruling (Will, round 69), on the §10 record committed in 1ae0db16** (`results/step0/v7check.json`, sha256
`8cb466f5e48235ebdef4eabd2080ab7bdc07e017aea5c560b7800cdfc4363a03`):
- All 9 flagged roots pass (b) and (c); (c) agrees with the float roots to at most 7.4·10⁻¹² mean spacings.
- Root m = 37,025's failure of (a) is a flaw in the check's definition: (a) uses the derivative at θ, not the slope
  across the bracket. There ψ′ is 1.3·10¹⁵ at θ and 8.1·10¹⁵ one ulp up, and f jumps from −3.10 to +1.44 across that
  ulp, so the point derivative understates the local slope.
- K = 4 is applied as pre-declared in §10 (the smallest power of two covering every (c)-verified N = 10⁵ root). The
  amended V7, |f| ≤ F_ACCEPT + 4·ψ′(θ)·ulp(θ), passes all 10⁵ roots.

**What changes and what does not.**
- The v7check code and its record are not modified. `v7check.exit` stays `exit=1`.
- The pipeline (`run_l6_base_spot.sh`) accepts step 0's v7check either on its own exit 0 or under this ruling. The ruling
  is bound to the exact output it rules on by `results/step0/v7check_ruling.sha256` (`sha256sum -c` against
  `v7check.json`); any other v7check output is refused. Both paths and both refusals were exercised on a scratch copy.
- Generation writes each sequence's `.npy` last and atomically (`os.replace`), so the per-sequence restart (an existing
  `.npy` is kept) never keeps a partial sequence. The pipeline is otherwise unchanged.

**Post-hoc amendment to (a), for future runs (round 69): the slope across the bracket.**
- f(θ) = N·θ − c_m + φ(θ) is strictly increasing, since f′ = ψ′ > 0. For a flagged root θ, the bracket edge θ_e is
  BRACKET_ULPS = 4 representable doubles from θ on the root's side: up if f(θ) < 0, down if f(θ) > 0.
- s_br = |f(θ_e) − f(θ)| / |θ_e − θ|, the secant slope across that bracket, replaces ψ′(θ).
- **(a′) holds iff |f(θ)| ≤ BRACKET_ULPS·s_br·ulp(θ) + 10⁻⁶.** Within one binade |θ_e − θ| = 4 ulp, so the bound is
  |f(θ_e) − f(θ)| + 10⁻⁶: the residual is no larger than f's change across the bracket that holds the root.
- **Stated plainly:** for a strictly increasing f, (a′) follows from the sign change on the root's side, which is (b).
  So (a′) is no longer independent of (b). It measures the floor from the same bracket. The independent check on
  correctness stays (c).
- **Not chosen, reported descriptively:** the symmetric secant over [θ − 4 ulp, θ + 4 ulp] at the half-width,
  4·ulp·(f(θ + 4 ulp) − f(θ − 4 ulp))/(8 ulp). It assumes f is linear across the bracket, which is false where ψ′ spikes.
  From the §10 diagnostic, already seen, it gives 3.04 against |f| = 3.10 at m = 37,025 and would fail there.
- **Disclosure:** this definition is written after the m = 37,025 values were seen (1ae0db16's descriptive diagnostic). It
  is post-hoc, as round 69 says.
- **Run:** `python l6_base.py step0 v7a_bracket results/step0/v7a_bracket.json`, on spot, from the saved N = 10⁵ arrays
  (no re-solve).
  - Per flagged root it records f at θ + k ulp for k = −4…4, recomputed in float64 as in (b), with a monotonicity flag.
  - It also records s_br/ψ′(θ) and the three bounds: (a′), the original (a), and the symmetric secant.
  - Its domain is the 9 flagged roots. Unflagged roots were accepted by |f| < F_ACCEPT, not by bracket collapse, and may
    sit more than 4 ulps from their root, so (a′) does not apply to them.
- **Then:** the generation and the rest of the pipeline run as committed. That covers 50 CUE sequences; the witnesses
  (10 CSE, 10 Poisson, 25 stitched); gate 1; the block statistics, concatenation and pair windows; gate 2; and compare
  (stitched/long, zeros/long, and the pair cross-check against the 10⁶ DE GUE). All of it is descriptive.

**Result of the amended (a) (`results/step0/v7a_bracket.json`; spot, from the saved arrays).**
- **(a′) holds for 9 of 9 flagged roots.** For comparison, the original (a) holds for 8 of 9 (m = 37,025 fails) and the
  symmetric secant for 7 of 9 (m = 37,025 at 3.04 against 3.10, and m = 86,531 at 3.11 against 4.34).
- f, recomputed in float64, is strictly increasing across θ ± 4 ulp at all 9 roots, and |f(θ)| equals the saved residual
  exactly.
- s_br/ψ′(θ) ranges from 0.11 to 2.49. ψ′ at θ overstates the bracket slope at 8 roots and understates it only at
  m = 37,025 (2.49).

| m | f(θ) | s_br/ψ′(θ) | (a′) bound | (a) bound | symmetric bound |
|---|---|---|---|---|---|
| 11,483 | −1.908 | 0.13 | 2.672 | 21.235 | 2.950 |
| 35,385 | −1.727 | 0.38 | 3.986 | 10.391 | 2.860 |
| 37,025 | −3.098 | 2.49 | 5.688 | 2.286 ✗ | 3.042 ✗ |
| 59,797 | +1.228 | 0.47 | 4.182 | 8.916 | 2.866 |
| 62,243 | −1.146 | 0.81 | 4.681 | 5.805 | 2.882 |
| 62,248 | +1.399 | 0.38 | 3.427 | 9.038 | 2.747 |
| 74,854 | +1.860 | 0.43 | 4.159 | 9.569 | 2.876 |
| 85,689 | +1.229 | 0.11 | 2.375 | 21.642 | 2.973 |
| 86,531 | +4.337 | 0.29 | 5.468 | 18.606 | 3.110 ✗ |

Generation started on spot after this run, at 2026-10-21T00:44 (60 parallel jobs).

## 12. Generation restart: the active-set, checkpointed solver (round 69 follow-up; committed before it runs)
**Why.** The first generation run started at 2026-10-21T00:44 with 60 jobs on spot. After 19.5 h no CUE sequence had
finished, and Will called for a fix. Spot's 56 vCPUs share cache and memory bandwidth, so 60 simultaneous N = 10⁵ solves
each ran about 9.6× slower than one alone. That figure comes from the finished CSE witnesses: 59,000 s for 9 iterations
plus the grid, against 23,816 s for the standalone CUE solve's 46. `roots_np` evaluates all 10⁵ roots on every
iteration, even after almost all have converged. A CUE draw needs about 46 iterations because of a few hard roots, so
most of each run is spent recomputing roots that are already done. I skipped a worker-count probe before launching;
that was my error.

**What was stopped and what was kept.**
- At 2026-10-21T20:15 the launcher, its xargs and the 50 CUE jobs were stopped by PID. No CUE output existed.
- The finished witnesses are kept: Poisson 10/10, stitched 25/25 and CSE 5/10. These came from the validated solver, and
  the new solver is checked to be bit-identical to it.
- The 5 running CSE jobs were left to finish. If any is stopped instead, the restart regenerates it.

**The change (`cbe.roots_np`, new keyword arguments, defaults unchanged).** With the defaults the function computes
exactly what it computed before, so every cs4 caller and the sealed calibrations are unaffected.
- **`active=True`:** each iteration evaluates φ only on the root columns that are not yet done in every matrix.
  - A done root's θ is frozen (`np.where(done, θ, new)`), and its lo/hi are never read again.
  - So the returned θ and the iteration count are those of the validated solver, element for element, provided numpy's
    elementwise arithmetic does not depend on the array's length. That proviso is what the checks below test.
- **`ckpt=PATH`:** the state is saved atomically after the initial grid and after every iteration: θ, lo, hi, done,
  polish, the next iteration index, and the sha256 of the Verblunsky coefficients' bytes.
  - An existing checkpoint is resumed. A checkpoint belonging to a different matrix is refused.
  - The state is exact float64, so a resumed solve continues bit for bit.
  - `gen` uses `active=True` and a checkpoint for the CUE and CSE sequences, `results/base/gen/KIND_RRR.ckpt.npz`. The
    checkpoint is removed once the sequence's `.npy` is in place. A stopped job, or a restarted launcher, resumes from
    its last finished iteration instead of from zero.

**Checks, committed before they run (the launcher's step 0 now also requires both exits to be 0).**
- **`step0 activeset`** compares the new solver with the validated `roots_np`, bitwise on θ (compared as uint64) and on
  the iteration count, for three draws:
  - β = 2, N = 10⁴, seed 905;
  - β = 4, N = 10⁴, seed 906;
  - 100 × CUE_1000, seed 907 (the stitched shape).

  On the β = 2 draw it also stops a checkpointed solve after iteration 3, resumes it, and requires the bitwise-equal
  result; and it requires a foreign matrix's checkpoint to be refused.
- **`step0 activeset_full`** re-solves the saved v7check N = 10⁵ draw with `active=True` and a checkpoint, stops after
  iteration 5, and resumes. It requires θ bitwise equal to the saved validated θ (1ae0db16) and 46 iterations.
- A local smoke run passed both properties on three tiny draws (N = 800 at β = 2 and β = 4; 20 × 200), including a
  resume after iteration 2.
- **Worker-count probe (`probe_workers.py`; engineering only).** K concurrent phi_np passes with the N = 10⁵ working set,
  for K = 1, 8, 14, 28, 42 and 56. NPROC is chosen from the throughput. Unlike the previous run, the active set leaves
  fewer than 60 jobs fully active for most of the run.

**Results of the small checks and the probe (spot; `results/step0/activeset.json`, `probe_workers.log`).**
- **`step0 activeset`** passed. All three draws are bitwise equal, with the same iteration counts:
  - β = 2, N = 10⁴: 9 iterations;
  - β = 4, N = 10⁴: 9;
  - 100 × CUE_1000: 13.

  On the β = 2 draw the solve stopped after iteration 3 and resumed bitwise equal, and the foreign checkpoint was
  refused.
- **Worker probe.** Throughput, in tenth-passes per second:

  | K (concurrent) | 1 | 8 | 14 | 28 | 42 | 56 |
  |---|---|---|---|---|---|---|
  | throughput | 0.0116 | 0.080 | 0.117 | **0.143** | 0.135 | 0.131 |

  - Throughput peaks near 28 concurrent jobs.
  - The 5 CSE jobs from the first run were still running during the probe, so its absolute numbers are slightly
    pessimistic.
- **Restart (`run_l6_gen_cue_spot.sh`).** The 50 CUE sequences start now with 25 processes, alongside the 5 old CSE jobs
  and `activeset_full`, about 31 in all.
  - They start before `activeset_full` finishes, to save its 1–3 h.
  - When the CUE pass ends, the script waits for `activeset_full` and then runs `run_l6_base_spot.sh 28`. That keeps
    every existing `.npy`, regenerates any missing CSE witness with the new solver, and stops at step 0 unless
    `activeset_full` exited 0.
  - **If `activeset_full` fails, the restarted CUE sequences are discarded.**

**Result of `step0 activeset_full` (`results/step0/activeset_full.json`).** The check passed.
- The saved N = 10⁵ draw, re-solved with the active-set, checkpointed solver and stopped after iteration 5 then resumed,
  gives θ **bitwise equal** to the validated θ from 1ae0db16 (max |Δ| = 0), in 46 iterations, as before.
- Timing under about 31 concurrent jobs: the grid and the first 5 iterations took 17,816 s, and the other 41 iterations
  took 529 s. The late iterations are nearly free.
- The first 15 restarted CUE sequences took 16,077–18,109 s each (28–51 iterations), against about 19.5 h and still
  unfinished in the first run.

## 13. Gates 1 and 2 (records; descriptive; the pipeline stopped at gate 2 as coded)
**Generation.** All 50 CUE sequences come from the active-set solver. The witnesses are 10 CSE, 10 Poisson and
25 stitched. The CUE pass ended at 2026-10-22T06:05; the per-sequence metadata are in `results/base/gen/*.json`.

**Gate 1 passed** (`results/base/gate1.json`). The CUE baseline's Σ²(L) against the exact CUE_N number variance gives
|z| ≤ 1.87 at every L from 1 to 1000. Every witness fails, as required:

| | z at L = 1 | 10 | 100 | 500 | 1000 |
|---|---|---|---|---|---|
| stitched | +2.1 | +7.9 | +17.4 | +19.1 | +20.3 |
| CSE | −661 | −320 | −192 | −105 | −54 |
| Poisson | +616 | +245 | +85 | +48 | +58 |

The exact formula agrees with the sine kernel to a relative 1.6·10⁻⁵ over the grid.

**Gate 2 did not pass as coded, because its witness did not fire** (`results/base/gate2.json`).
- **Halves agree:** for half A (even R) against half B (odd R), |z| ≤ 1.32 at every test and G.
- **Witness:** CUE half A against the 25 stitched sequences gives |z| ≤ 0.92 at every test and G, so there is no
  |z| > 3 at G ≥ 1000. The ratios Var_long/Var_stitched are:

  | G | route (a) | (A) | corrected (B) |
  |---|---|---|---|
  | 300 | 1.015 ± 0.032 | 1.008 ± 0.034 | 0.973 ± 0.042 |
  | 1000 | 1.005 ± 0.043 | 0.985 ± 0.046 | 0.957 ± 0.047 |
  | 3000 | 1.017 ± 0.062 | 0.978 ± 0.061 | 0.963 ± 0.084 |
  | 10000 | 1.006 ± 0.085 | 0.926 ± 0.098 | 1.002 ± 0.122 |

  The ± values are the SEs of the log ratio.
- **The pre-declared reading (§3):** "If it cannot fail anywhere, the long baseline adds nothing over the calibration,
  and that is reported."
  - For these three block statistics, the stitched CUE_1000 construction and a true 10⁵-level CUE sequence give the same
    block variance.
  - The resolution is about ±14% at 3 SE for G = 1000, and ±25–37% at G = 10⁴.
  - Stitching does change the number variance: the stitched witness fails gate 1 with z = +19 at L = 500. The block
    statistics do not register that change.
- **Not run:** compare (stitched/long, zeros/long, and the pair cross-check). §3 says both gates must hold before any
  comparison, and the launcher stopped at gate 2. The 5 pair windows (`results/base/pair/`) and the block statistics
  (`results/base/stats/`) are computed and saved. Whether compare runs is Will's decision.
