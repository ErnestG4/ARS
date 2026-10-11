# Stage 2 G-s, ζ step — the predicted v(b) and g at the five F2 heights (G_S_DESIGN.md §2, §3, §6; 2026-10-10)

The prediction is fixed by theory, with no parameters. It uses CS08's n ≤ 4 ratios-conjecture correlations, through
the same assembly that reproduces the sine kernel (`GS_UNITARY_RESULTS.md`). v(b) and g are computed directly at the
sealed ladder and taper, with no functional form (twenty-first round). No F2 data was read.

Code and outputs:
- **Code:** `gs_zeta.py`, `cs4lr.py`, run by `run_gs_zeta_spot.sh` (255 tasks, all exit 0).
- **Raw output:** `results/gs_zeta/gs_zeta_L*.json`.
- **Summary:** `gs_zeta_summary.py` → `results/gs_zeta/gs_zeta_summary.json`.
- **Heights:** each F2 file's zero-weighted mean ℓ. Prime cutoff 3·10⁵. In-pair quadrature is GJ16 (weight d²).

## 1. Prediction

| ℓ (F2 file) | v(100) | v(300) | v(1000) | v(3000) | v(10⁴) | g = √(v(10⁴)/v(100)) | g / g_GUE |
|---|---|---|---|---|---|---|---|
| 15.7502 | 0.072623 | 0.058159 | 0.044594 | 0.037270 | 0.033241 | **0.6765** | 0.704 |
| 16.4972 | 0.075927 | 0.061799 | 0.047737 | 0.039365 | 0.034481 | **0.6739** | 0.702 |
| 17.2491 | 0.078969 | 0.065311 | 0.051002 | 0.041709 | 0.035854 | **0.6738** | 0.701 |
| 19.5003 | 0.086519 | 0.074680 | 0.060747 | 0.049708 | 0.041143 | **0.6896** | 0.718 |
| 21.7500 | 0.092120 | 0.082223 | 0.069605 | 0.058187 | 0.047976 | **0.7217** | 0.751 |

g_GUE = 0.9606 is the sine-kernel prediction through the same assembly (`GS_UNITARY_RESULTS.md` (i)).

- **Positivity guard (§4, on computed values): PASS** at every rung and height.
- **Where the b-dependence comes from.** The long-range non-oscillating part I₄,long carries almost all of it:
  - I₄,long goes from +0.017 at b = 100 to −0.036 at b = 10⁴ (ℓ = 15.75), and from +0.004 to −0.057 (ℓ = 21.75).
  - I₂ and I₃ change by < 1e-4 over the ladder.
  - The short-range I₄ changes by < 2e-3.
  - For the sine kernel, the same long-range part only decays, as 1/b.
- **log b behaviour (descriptive only; amendment 3).** dv/d log b per rung:

  | ℓ | 100→300 | 300→1000 | 1000→3000 | 3000→10⁴ |
  |---|---|---|---|---|
  | 15.75 | −0.0132 | −0.0113 | −0.0067 | −0.0033 |
  | 16.50 | −0.0129 | −0.0117 | −0.0076 | −0.0041 |
  | 17.25 | −0.0124 | −0.0119 | −0.0085 | −0.0049 |
  | 19.50 | −0.0108 | −0.0116 | −0.0100 | −0.0071 |
  | 21.75 | −0.0090 | −0.0105 | −0.0104 | −0.0085 |

  - v(b) falls at every rung.
  - At the lower heights the fall per log b slows towards b = 10⁴.
  - At ℓ = 21.75 it is close to linear in log b over the whole ladder.

## 2. Precision and validity checks
| check | result |
|---|---|
| \|Im\| noise bound on v (the result must be real) | ≤ 2.1e-6 relative, all rungs and heights |
| Fourier-series tail (cs4lr) | ≤ 5.5e-6 |
| max imaginary residue, ρ₄c / ρ₃ | ≤ 3.9e-7 / ≤ 1.4e-29 |
| ρ₃ near the diagonal (2nd differences, \|a − e\| < 0.2 vs elsewhere) | 6.0 vs 6.5 (relative to max ρ₃): no spike |
| evaluator vs cs4fastc (`cs4lr_check.py`) | worst 1.1e-9 |
| isolated near-coincidences (`diag_coinc.py`) vs grid margin (`coinc_margin.py`) | ≤ 3e-10 down to δ = 1e-3; grid min δ = 1.3e-3 |
| clustered grid corner vs 50 digits (`diag_cluster.py`) | worst 1.4e-7 abs → 8e-10 of v |
| sine-kernel quadrature check (`gs_zeta_sinetest.py`) | 6.7e-6 |
| long grid Δr = 0.5 vs Δr = 0.1, kept non-oscillating part (`diag_osc_alias.py`) | ≤ 3e-5 of v per pair, all rungs |
| kept part: mean-ℓ value vs file average (pair (5,5), F2 15.75 file) | ≤ 5e-6 of v |
| dropped ℓ-oscillating long-range part, **file-averaged** (§3 below) | (1.3 ± 5.3)e-4 of v at b = 10⁴ for the heaviest pair at the lowest height |

## 3. The dropped ℓ-oscillating long-range part: the record
The split (G_S_DESIGN §3) keeps only the non-oscillating pieces beyond r ≈ 10–20 spacings. The design says the
ℓ-oscillating pieces integrate to ≈ 0 against the smooth window.

1. **The production check was aliased.** `gs_zeta.py` evaluated the dropped part for two node pairs on the Δr = 0.5
   long grid and found it large (pair (5,5): −0.16 at b = 10⁴; if real, 25% of v). But the two-pair pieces carry
   e^{∓4πir}, which sample to exactly 1 at Δr = 0.5. The Δr = 0.5 subsample of a Δr = 0.1 grid reproduces the
   production numbers exactly. On the Δr = 0.1 grid (aliasing only at ±10 cycles per spacing) the dropped part is
   100–1000× smaller.
2. **At a fixed ℓ it is still not negligible at low heights.** On the fine grid, pair (5,5) at b = 10⁴ is 3.6–3.8e-3
   of v at ℓ = 15.75 and 16.50, and up to 9e-3 at other ℓ inside the 15.75 file. At ℓ = 21.75 it is 4e-5.
   - Mechanism (my reading): the one-cycle-per-spacing carrier beats against products of Euler factors whose prime
     frequencies sum to ≈ 1 (pq ≈ e^ℓ). That leaves near-DC content, whose position moves with ℓ.
3. **Averaged over the file it vanishes within resolution.**
   - Pair (5,5) was evaluated at 64 stratified ℓ across the F2 15.75 file ([15.7259, 15.7742]), weighted ∝ ℓe^ℓ
     (`run_diag_osc_lavg64_spot.sh`, `diag_osc_lavg.py dense`).
   - The file-averaged dropped part, as a fraction of v:

     | b | 100 | 300 | 1000 | 3000 | 10⁴ |
     |---|---|---|---|---|---|
     | file-averaged | 4.2e-6 | 3.0e-5 | (0.9 ± 0.6)e-4 | (0.9 ± 2.3)e-4 | (1.3 ± 5.3)e-4 |

     This is consistent with zero, against up to 9e-3 at a single ℓ.
   - A first 5-node Gauss–Legendre average gave (3.2 ± 1.2)e-3 at b = 10⁴. That was a chance excursion: at
     r ~ 2·10⁴ the resonant phase turns ~70 rad between adjacent nodes, so five nodes are five random samples.
   - The kept part varies smoothly with ℓ, and its mean-ℓ value equals its file average to ≤ 5e-6 of v.
4. **Consequence.**
   - The values in §1 (kept part at the mean ℓ, oscillating part dropped) equal the **file-averaged** prediction to
     within this test's resolution.
   - The file average is what each F2 file measures, which is the "exact for the statistic measured" rule.
   - The residual bound (2σ ≈ 1e-3 of v for the heaviest pair at the lowest height, b = 10⁴) is a resolution limit.
     It is not a detected effect.
   - The other pairs carry smaller weights. Higher heights are smaller at fixed ℓ already.
5. **Open, for Will.** Whether the file-averaged reading of the prediction, and this evidence for dropping the
   oscillating part, should be written into the seal as the prediction's definition (G_S_DESIGN §6, amendment 7,
   proposed).

## 4. Against the GUE baseline and Stage 1 (descriptive; nothing here is a test)
- **Predicted shrink vs GUE.** g / g_GUE = 0.70 at ℓ = 15.75–17.25, rising to 0.72 (19.50) and 0.75 (21.75). The
  predicted shrink weakens with height. That is the direction the few-prime mechanism predicts; Stage 1's arm D could
  not establish it.
- **Stage 1 is not commensurable with this.** Stage 1 measured the drift-removed moving-block bootstrap SD with sharp
  blocks on F1 (g_zeros 0.66–0.70, d = g_GUE − g_zeros = 0.28–0.30). This statistic is the tapered window variance.
  The numbers look close (predicted d = 0.961 − g = 0.28–0.29 at ℓ ≤ 17.25), but the statistics differ, so the
  closeness is not evidence. The F2 measurement of this statistic is the test.

## 5. Prediction vs estimator: the seal condition (twenty-third round)
The estimator (`ph2s2/tapered.py`) is the sample variance of S(c; b) over n window centres spaced 3b apart, centred on
the file mean, divided by b. Its expectation is
  E[v̂(b)] = v(b)·[1 − (2/(n − 1)) Σ_{k=1}^{n−1} (1 − k/n) ρ_k] + b·s²_c(μ(ℓ_c)),
where v(b) is §1, ρ_k = Cov(S(c), S(c + 3bk))/V(b) is the predicted correlation between windows k apart, and μ(ℓ) is the
two-point mean per unit length (E S(c; b) = b·μ(ℓ_c)). The three terms, as fractions of v(b):

**(ii) Oscillating height-dependence of the two-point mean: none.** `diag_mu2.py`, `results/diag_mu2/`.
- μ(ℓ) = ∫F ρ₂ (CS08, cutoff 3·10⁵) was evaluated at 64 stratified ℓ across each F2 file, plus two dense pockets at
  the file midpoint (16 ℓ spaced 1e-6 and, where the file is wide enough, 16 spaced 1e-4), so faster oscillations
  could not alias.
- The residual from a quadratic in ℓ is ≤ 6e-12, i.e. b·Var/v ≤ 2e-18. The pocket spreads equal slope × span
  (1.7e-8, 1.7e-6), and the bound from them is ≤ 9e-7 of v.
- Structural reason: in unfolded units the two-point carrier is exactly e^{∓2πid} (`cs4fast.R2`: Φ = i·c₀·x with
  x = 2πd/ℓ). ℓ enters only through the arithmetic factors at τ = 2πd/ℓ, with d ≤ 3, which is smooth.

**(i) Smooth height-dependence of the window mean: negligible, so the prediction carries it.**
- dμ/dℓ = 1.15e-3 (ℓ = 15.75) falling to 6.4e-4 (21.75); μ ≈ 0.825–0.830.
- The between-window term b·Var_c μ / v at b = 10⁴ is 7.7e-5, 1.4e-5, 2.7e-6, 2e-8 and 7e-11 (files 15.75 to 21.75),
  and 100× smaller at b = 100.
- **F1 descriptive:** a linear detrend changes the window variance by ≤ 0.1% at b ≤ 3000, consistent with this.

**(iii) Centring: the predicted windows are correlated, and the lag sum does not converge on the stored grid.**
`diag_wincov.py`, `diag_wincov_edge.py`, `results/diag_wincov/`.
- **C(r) does not decay.** The assembled non-oscillating long-range C(r) is almost periodic, with RMS 0.053
  constant out to r = 4.8·10⁴ (CS08's arithmetic terms at r ≪ t; only the sine-kernel part decays).
- **So the windows are correlated at every lag the grid reaches.** Lags were used only when their Gaussian lies inside
  the grid to 5σ; a cut at 1.75σ gave a spurious ρ = −0.22.
  - Lag 1: ρ₁ = −0.031 to −0.034 (b = 100) and −0.010 to −0.031 (b = 3000).
  - Partial sums Σ_{k≤K}(1 − k/n)ρ_k wander between +0.06 and −0.35 out to K = 159 (b = 100), 52 (300), 15 (1000)
    and 4 (3000), without converging. They are negative almost throughout, and their end values are −0.01 to −0.30.
  - **b = 10⁴ has no usable lag:** lag 1 needs C to 5.8·10⁴.
- **F1 descriptive (seen data):** the measured lag-1 correlation of window sums at b = 100 is −0.03 to −0.04 in all
  six bins (n ≈ 2·10⁴), against about 0 for GUE. This agrees with the predicted −0.033. (`diag_f1_wincorr.py`)
- **Size of the centring term.**
  - Var(Σ_i S_i) ≥ 0 gives the rigorous bound E[s²]/V ≤ 1 + 1/(n − 1).
  - n at b = 10⁴ is 175, 183, 192, 217 and 242 (F2 files), so the bound is ≤ 5.7e-3 of v.
  - If the full lag sums are like the partial ones (−0.1 to −0.3), the term is +0.8 to 3.4e-3 of v at b = 10⁴,
    +2.5e-4 to 1e-3 at b = 3000, and ≤ 3.4e-4 at b ≤ 1000. This is an illustration, not a computation.
  - The sign is one-sided while the lag sums stay negative. The ζ estimate is then biased up, towards GUE, so a shrink
    claim is not inflated. For GUE (C decays as r⁻²) the term is ≈ 0.
- **Not computable to the end.** The full lag sum at b = 10⁴ needs C out to the file length (~5·10⁶ spacings, 100× the
  stored grid). It also depends on the slow modes from nearly equal primes, whose cutoff convergence was checked
  only at b ≤ 300.
- **c∞** (amendment 1: "still computed and reported") has **not been computed**. Any constant part of C is common to
  every window of a file, so centring removes it exactly. It is inside this same term and covered by the same bound.
- **Open, for Will:** how to close (iii). Options in `MORNING_2026-10-10.md` (20:00).
