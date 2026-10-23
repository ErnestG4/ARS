# specarith — open leads (descriptive; no verdicts)

Listed together at Will's instruction (2026-10-08), **not merged**: each was found on its own data with its own
statistic, and any connection between them is a hypothesis for a future sealed test, not a finding.

## L1 — low-height excess of the gap ratio ⟨r̃⟩ above GUE
- First 3·10⁴ zeros: ⟨r̃⟩ = 0.6129 (thirds 0.6147 / 0.6121 / 0.6120), **+8.5 SD** above the matched-size GUE band
  (W = 3·10⁴, mean 0.59991, SD 0.00153; `ph6/results/preread61/redpaths61.json`).
- Earlier, independently: ARS-RH Phase 1 resolved the same excess and its fall with height (+0.012 at γ ≈ 5·10³,
  +0.008 at 3.7·10⁴, +0.006 at 1.4·10⁵ against the surmise reference; +0.003 more against large N —
  `arsrh/PHASE1_FINDINGS.md` and its 2026-10-08 erratum).
- Context: Nishigaki (2025) finds the ⟨r̃⟩ CUE_N correction O(N⁻⁴) (the O(N⁻²) term cancels) and the ζ deviation
  ∝ N_e^{−3.08} (fitted) — `ph2/lit/NEXT_ORDER_LIT.md` §2.4.

## L2 — Phase 2: the zeros' spacing law sits closer to the sine kernel than CUE(N_eff) predicts
- κ̂ > 1 in all 8 resolvable bins, falling with height (SECONDARY 1.21 → 1.045 for N_eff 2.3 → 5.1); post hoc,
  (κ̂ − 1)·N_eff² ≈ const (SECONDARY 1.14–1.33); κ̂ depends on the fit window; against exact CUE(N_eff) the zeros move
  the other way from CUE's own higher-order terms (PRIMARY) — `ph2/PH2_FINDINGS.md` §3–§4,
  `ph2/results/run/CUE_EXACT_COMPARE.md`. Below N_eff = 2 (descriptive): κ̂ keeps rising as N_eff falls
  (`ph2/results/lowheight/LOWHEIGHT.md`).

## L3 — CS08's long-range four-point connected function does not decay (descriptive; twenty-fourth round)
- The assembled non-oscillating long-range C(r) of the Stage 2 statistic (pair bump (0.5, 0.3)) is almost periodic,
  with RMS 0.053 constant from r ≈ 20 to 4.8·10⁴ spacings at ℓ = 16.50. Its 2000-spacing block means are ±5·10⁻⁵. Only
  the sine-kernel part decays. Source: `cs4/diag_wincov_edge.py`, `cs4/GS_ZETA_RESULTS.md` §5.
- **Unchanged by CS08's J₁₃ sign erratum** (`cs4/CS08_ERRATUM.md` §4.1), which was in the code that computed C(r).
  - The correction has Bohr mean 0, so C(r)'s constant part c∞ is untouched.
  - **Recomputed with the fix** (2026-10-12, `cs4/results/gs_zeta_fix4/`): the RMS of the assembled C(r) on
    [4.7·10⁴, 4.8·10⁴] moves by +1.5e-6 to +5.4e-6 across the five F2 heights, about 1e-4 of its value. At
    ℓ = 16.50 it goes from 0.052643 to 0.052648.
  - Pointwise bound: ≤ 2.8e-4. The statement above (almost periodic, RMS constant out to 4.8·10⁴) stands.

## L4 — neighbouring windows of the zeros are anti-correlated; GUE's are not (seen data; descriptive)
- Lag-1 correlation of the tapered window sums (b = 100, centres 3b apart):
  - F1, all six bins: −0.03 to −0.04 (n ≈ 2·10⁴ each; about 5σ per bin);
  - Stage 1 GUE: ≈ 0;
  - CS08's prediction: −0.031 to −0.034.
- Source: `cs4/diag_f1_wincorr.py`, `cs4/results/diag_wincov/`. Not a test: F1 is seen data.

## L5 — does CS08 explain Coram–Diaconis's lag-1 anti-correlation (−0.2)?
- CD (2000 report; `ph2s/lit/PAIRSUM_VARIANCE_LIT.md` §1.8) found −0.2 between consecutive blocks' values of
  |Σ_j e^{iθ_j}|². Their blocks are n = 42 zeros, sharp and adjacent, each rescaled to its own length.
- To do: the theory's ρ₁ in their configuration, with the per-block-rescaling effect measured separately on GUE
  (Will's caution: rescaling alone anti-correlates neighbours in any rigid sequence). If the GUE part accounts for
  −0.2, CS08's arithmetic part is what is left to compare.
- **First step done (2026-10-10, descriptive; F1 is seen data): `ph2s2/cd_lag1.py`, `ph2s2/results/cd_lag1/`.**
  - **GUE does not do it.** On the Stage 1 GUE sequences (16 × 10⁶ unfolded levels, a long rigid sine-kernel
    sequence), CD's construction with own-length wrapping gives ρ₁ = +0.00 to +0.04 for every n = 4…64 (SE ≈ 0.002).
    Unit-length wrapping gives +0.01. So per-block rescaling plus rigidity does **not** produce −0.2.
  - **The zeros do.** On F1 with CD's rule n = ⌊ℓ⌋, ρ₁ = −0.23 to −0.27 in all six bins (SE 0.0017), against CD's
    −0.2 ± 0.03 at ℓ ≈ 42.
  - **ρ₁ is a function of u = ℓ/n alone.** u is the frequency, in t, that the block-scale mode e^{2πiΔ/n} probes; the
    block is one period, 2π/u in t. F1b (ℓ = 15.47) and F1x (ℓ = 22.10) fall on one curve:

    | u | ≈ 1.0 | ≈ 0.7 | ≈ 0.55 | ≈ 0.45 | ≈ 0.38 | ≈ 0.35 |
    |---|---|---|---|---|---|---|
    | ρ₁ | −0.24 to −0.26 | −0.32 to −0.37 (minimum) | ≈ 0 | +0.55 (peak) | ≈ 0 | +0.2 (second peak) |

    At n = 42 on F1 (u ≈ 0.35–0.53) it therefore swings from +0.10 to +0.54.
  - **Bearing on the twenty-second-round novelty wording:** it said CD's −0.2 "may be a generic rigidity effect".
    **Revised (Will, twenty-fifth round; recorded as a correction):** "not explained by GUE-level rigidity (GUE gives
    ≈ 0 under the same construction); an arithmetic origin is conjectured (possibly prime 2) and not yet tested."
  - **Still to do:** the theory curve ρ₁(u) from CS08 (or the explicit formula) in CD's configuration.
  - **Scoping the theory curve (not started; for Will to prioritise).** Three obstacles:
    - **CS08's theorem does not cover CD's statistic as it stands.** It needs test functions holomorphic in a strip.
      CD's blocks are sharp, indexed by zero count (each starts at a zero, a Palm-type conditioning), and own-length
      wrapping makes W nonlinear in the zeros.
    - **The tractable neighbour:** blocks at fixed positions, unit wrapping, and a smooth taper w,
      Z_k = Σ_γ w(x_γ − kn) e^{2πi x_γ/n}. Its lag-1 Cov(|Z_k|², |Z_{k+1}|²) is a four-point integral of the same
      kind as Stage 2's (`cs4lr`), with the pair bump F replaced by e^{2πi(x₁ − x₂)/n}.
    - **Comparing the two needs the bridge.** That variant would first be measured on F1 next to CD's own
      construction, to check that it keeps the u-curve.
  - **Reading of the mechanism (a conjecture, not a check).** The mode e^{2πiΔ/n} probes frequency u in t. By the
    explicit formula, the prime powers m with log m near u contribute terms that are deterministic in the block position
    and rotate by 2π·log m/u from one block to the next. Their beats then set the sign of ρ₁. The minimum near
    u ≈ 0.7 sits at log 2 = 0.693. GUE has no such terms, which fits its ρ₁ ≈ 0.

## L6 — number-variance saturation from the existing bootstrap outputs (round 64; descriptive first)
- **Observation (`cs4/ROUTE_A_FINDINGS.md` §11).** In four places the zeros fluctuate less than the CUE null predicts:
  - route (a)'s GoF χ² is at the 18.5th percentile of its CUE calibration;
  - (A)'s between-file χ² is 0.6 on 2;
  - in the R₂ bins check the drift-removed bootstrap SD shrinks with block length;
  - the corrected (B)'s between-file χ² is at the 4th percentile of its CUE replicates.

  The CUE-floor SEs are therefore conservative for the zeros.
- **Lead:** compute Var_zeros/Var_CUE of block statistics as a function of block length, from bootstrap outputs that
  already exist. Examples are the per-segment SE_boot at 300/1000/3000/10000 in `cs4/results/b2_read/` against the
  calibration's mean SE_boot and SD, route (a)'s and (A)'s block-length SEs, and the R₂ bins series. This would be a
  direct measure of number-variance saturation at fresh heights.
- **Candidate cause (untested):** Berry-type saturation of Σ² beyond L_max ≈ ln(E/2π)/(2π ln 2), driven by the shortest
  primes.
- **What it needs to mean anything:** a single long CUE_N (or sine-kernel) baseline of ≥ 10⁵ levels, run through the
  same block statistics. The CUE_1000 calibration blocks have no correlation beyond one block, so they cannot separate
  generic long-sequence rigidity from arithmetic.
  - **Correction (round 65):** for the pair statistic this already exists. A 10⁶-level DE GUE baseline was run
    (`ph2r2/PH2R2_FINDINGS.md` §6; levels saved on spot), then confirmed on fresh heights (Stage 1) and matched to
    CS08's n ≤ 4 prediction in size (Stage 2).
  - The first version of this lead wrongly called it "the same missing baseline". What is missing is the long baseline
    for the spacing and κ₃ statistics.
- **Descriptive pass (round 65; `l6/l6_table.py`, `l6/results/L6_TABLE.md`, 3fa5a4d0).** Var_zeros/Var_baseline of the
  block statistics against block length G, from outputs that already exist.

  | test (set) | baseline | G ≈ 100 | G = 300 | G ≥ 1,000 |
  |---|---|---|---|---|
  | route (a) (F3) | CUE_1000 calibration | — | 0.78 (0.63–0.91) | baseline invalid: stitched CUE_1000 |
  | (A) (F4) | CUE_1000 calibration | — | 0.69 (0.57–0.85) | baseline invalid: stitched CUE_1000 |
  | corrected (B) (F6) | CUE_1000 calibration | — | 0.31 (0.24–0.43) | baseline invalid: stitched CUE_1000 |
  | R₂ bins (seen) | 10⁶-level GUE, unstitched | 0.56–0.82 | — | 0.37–0.67 at 10³; 0.30–0.47 at 10⁴ |

  - **Descriptive reading of the short blocks only.** At 300 levels, all three statistics fluctuate less than CUE_1000
    on every file.
  - Within each test the ratio rises with height:
    - route (a): 0.63 → 0.91;
    - (A): 0.57 → 0.85;
    - corrected (B): 0.25 → 0.43.

    That matches Stage 1's finding that the shrink weakens with height.
  - The κ₃ statistic shows the largest deficit.
  - **Caveat at 300 levels:** a block can straddle a seam between two independent CUE_1000 matrices, where the baseline
    has no rigidity. That could inflate the baseline's variance and push the ratio down, so the long baseline is needed
    even here to be sure.
    (Round 70: it does not. Against the long baseline the ratio at 300 levels is 0.98–1.00.)
  - **The R₂ row is valid at every G**, because its baseline is one long sequence. Those bins are seen data
    (exploratory), and its ratios are absolute SDs at matched heights, not the growth ratio of §6.
  - **The long CUE_N baseline is what unblocks the long-block comparison** for the three cs4 statistics. Its design
    and pre-registration were drafted for Will in round 65. It has since been run (next item).
- **Long CUE baseline (rounds 66–70; `l6/L6_BASELINE_DESIGN.md` §11–§13).** 50 CMV CUE sequences of 10⁵ levels each.
  - **Gate 1 passed:** the exact CUE number variance matches, and three witnesses fail as required. The two halves
    agree.
  - **Gate 2's stitched witness did not fire.** Will ruled it mis-specified (round 70).
  - **Stitching does not affect these statistics' block variance** within ±14% at G = 1,000 and ±30% at G = 10,000. So
    the "baseline invalid" marks above are revised to "valid within stated sensitivity" (L6 table, †).
  - **Zeros/long** (descriptive; gate-2 stitched witness did not fire):

    | test | G = 300 | 1,000 | 3,000 | 10,000 |
    |---|---|---|---|---|
    | route (a) | 0.77 | 0.68 | 0.54 | 0.40 |
    | (A) | 0.69 | 0.56 | 0.53 | 0.44 |
    | corrected (B) | 0.31 | 0.21 | 0.18 | 0.16 |

    The G ≥ 3,000 values are revised in round 73: a long-baseline estimator free of the short-segment bootstrap's
    mean-subtraction bias (`l6/L6_BIAS_CORRECTION.md`). They were 0.58 / 0.43, 0.56 / 0.51 and 0.19 / 0.18.

  - **The zeros' lower variance is therefore not a calibration artifact.** Its cause for these local statistics is
    untested. The arithmetic suppression established for the pair statistic is a candidate.
  - **Pair cross-check:** the CMV and 10⁶-level DE GUE baselines agree to 0.97–1.08 across the five R₂ bins.
- **Rounds 71–72 (descriptive / exploratory; `l6/OWNBOOT_SE_CHECK.md`, `l6/CUE_SCATTER_CONTROL.md`,
  `l6/PAIR_APPROX.md`):**
  - **The zeros scatter less than their own bootstrap SEs predict:** pooled χ² 1.65 on 9 dof at G = 300.
  - **The identical pipeline on CUE gives χ²/dof ≈ 1** (1.14, 0.97, 1.06). So the zeros' low scatter is a property of
    the zeros (long-range rigidity).
  - **No bootstrap calibration rule (round 72):** the zeros' SE falls with block length and never levels off below
    file scale.
  - **The pair-connected approximation is not validated:** its known answer was contaminated by short-segment block
    bias (round 73). Within the approximation only, and with an unvalidated implementation, the pair channel carries
    ≤ 0.2% of CUE's block variance. It was not applied to ζ.
  - **Hypothesis (not a finding):** the deficit travels through connected terms of order > 2. That would match
    Stage 2, where the shrink came through the long-range four-point term. The cause stays open.
- **Round 75 (n = 6 stage (a); `l6/N6_STAGE_A.md`):**
  - For corrected (B), the exact U(N) block variance is flat in G, to 0.05%. The CUE covariance is gone by r ≈ 10.
  - The zeros' halving of block variance between G = 300 and 10,000 is therefore entirely arithmetic long-range in
    origin.
  - The rounds 72–73 CUE "fall" was estimator bias: +10% at G = 300 and +5% at G = 1,000.
  - Next: stage (b), the 3+3 long-range extraction under three gates; stage (c), the n = 6 short-range bound.
- **Status:** descriptive first. Any confirmatory version gets its own pre-registration. It is a candidate for the
  engine v2 gallery.

## Status
L1 and L2 have no theory-fixed prediction yet. The routes in progress: the R₂ phase (`ph2r2/`, pair correlation with
the arithmetic lower-order terms, fresh heights) and the Conrey–Snaith next-order spacing project
(`ph2/SCOPE_CS_SPACING.md`, GO after the R₂ seal).
