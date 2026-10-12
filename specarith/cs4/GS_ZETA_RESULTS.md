# Stage 2 G-s, ζ step — the predicted v(b) and g at the five F2 heights (G_S_DESIGN.md §2, §3, §6; 2026-10-10)

The prediction is fixed by theory, with no parameters. It uses CS08's n ≤ 4 ratios-conjecture correlations, through
the same assembly that reproduces the sine kernel (`GS_UNITARY_RESULTS.md`). v(b) and g are computed directly at the
sealed ladder and taper, with no functional form (twenty-first round). No F2 data was read.

**Note (2026-10-11, after the read and the release): a second CS08 erratum.** This prediction was computed with
CS08's printed sign of J₁₃'s prime-sum term, which is wrong (`CS08_ERRATUM.md` §4). The correction to ρ₄ has no
constant part and oscillates in r at ≥ 0.39 per spacing, so every windowed quantity here (v, v_B, g, g_B, ρ₁) is
unchanged to ~1e-18 (§4.1; `check_s13_stage2.py`). The numbers below stand as computed.

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
- ~~**Open, for Will:** how to close (iii). Options in `MORNING_2026-10-10.md` (20:00).~~ **Closed (twenty-fourth
  round):** Will chose option B, the successive-difference estimator; its prediction is §6.

## 6. Estimator B: the prediction (twenty-fourth round; G_S_DESIGN §6 amendment 8)
Will chose B. The measured statistic is the successive-difference variance v̂_B(b) = Σ(S_{i+1} − S_i)²/(2(n − 1)b)
over window centres 3b apart. Its expectation is exactly
  E[v̂_B(b)] = v_B(b) := v(b)(1 − ρ₁(b)) = v(b) − Cov(3b)/b,   Cov(R)/b = (1/√2)∫_ℝ exp(−π(r − R)²/2b²) C(r) dr,
with C assembled as for v(b) (amendment 7's file-averaged definition, ℓ-oscillating long-range part dropped). Seal
condition (i) is met by the estimator, (ii) by §5, and c∞ cancels.
- **Code:** `gs_zeta_ext.py` extends the long grid from 4.8·10⁴ to 6.0005·10⁴ on the production lattice, run by
  `run_gs_zeta_ext_spot.sh` (5 heights × 8 chunks, all exit 0). `gs_zeta_B.py` → `results/gs_zeta/gs_zeta_B_summary.json`.
  The per-pair npz files (pairs, ext) stay on spot, as for §1.
- Every lag lies inside the grid to 5σ of its Gaussian: b = 10⁴ needs 5.82·10⁴.

### 6.1 Prediction
| ℓ (F2 file) | v_B(100) | v_B(300) | v_B(1000) | v_B(3000) | v_B(10⁴) | g_B = √(v_B(10⁴)/v_B(100)) | g_B / g_GUE,B | g (§1) |
|---|---|---|---|---|---|---|---|---|
| 15.7502 | 0.075036 | 0.060089 | 0.045339 | 0.037655 | 0.033711 | **0.6703** | 0.699 | 0.6765 |
| 16.4972 | 0.078394 | 0.064145 | 0.048769 | 0.039868 | 0.034727 | **0.6656** | 0.694 | 0.6739 |
| 17.2491 | 0.081532 | 0.068046 | 0.052375 | 0.042417 | 0.036016 | **0.6646** | 0.693 | 0.6738 |
| 19.5003 | 0.089413 | 0.078041 | 0.062954 | 0.051091 | 0.041697 | **0.6829** | 0.712 | 0.6896 |
| 21.7500 | 0.094936 | 0.085466 | 0.072090 | 0.060003 | 0.049230 | **0.7201** | 0.751 | 0.7217 |

g_GUE,B = 0.9591 is the sine kernel through the same assembly (`gs_unitary_lag1.py`; g_GUE = 0.9606 under §1).

- **Positivity guard (on v_B): PASS** at every rung and height.
- **ρ₁(b), the predicted lag-1 correlation of windows 3b apart:**

  | ℓ | b = 100 | 300 | 1000 | 3000 | 10⁴ |
  |---|---|---|---|---|---|
  | 15.75 | −0.0332 | −0.0332 | −0.0167 | −0.0103 | −0.0142 |
  | 16.50 | −0.0325 | −0.0380 | −0.0216 | −0.0128 | −0.0071 |
  | 17.25 | −0.0325 | −0.0419 | −0.0269 | −0.0170 | −0.0045 |
  | 19.50 | −0.0335 | −0.0450 | −0.0363 | −0.0278 | −0.0135 |
  | 21.75 | −0.0306 | −0.0394 | −0.0357 | −0.0312 | −0.0261 |
  | sine kernel | −3.1e-3 | −1.1e-3 | −3.5e-4 | −1.2e-4 | −4.5e-5 |

  - Negative at every rung and height, so v_B > v. ρ₁ is largest at b = 100–300, which lowers g_B by 0.002–0.009
    against g. At ℓ = 21.75 ρ₁ stays near −0.03 up to b = 10⁴, and g_B ≈ g.
  - The b = 100 and 3000 values reproduce `diag_wincov.py` on the stored grid (−0.031 to −0.034; −0.010 to −0.031).
- **The shrink is unchanged.** g_B / g_GUE,B = 0.69–0.75, against 0.70–0.75 under §1.

### 6.2 Checks
| check | result |
|---|---|
| overlap [47000, 48000.5]: extension vs stored c_non, per pair (relative) | ≤ 3.1e-8 |
| overlap, assembled C (absolute; C's RMS there 0.034–0.057) | ≤ 1.4e-11 |
| extension \|Im\| / Fourier-series tail | ≤ 1.4e-8 / ≤ 5.5e-6 |
| lag 0 on the combined grid vs stored I₄ (short + long) | ≤ 3e-15 |
| dropped ℓ-oscillating part in the B term (lag 0 − lag 1), file-averaged (`diag_osc_lag1.py`) | (2.0 ± 8.9)e-4 of v at b = 10⁴; consistent with 0 at every rung (below) |

- **The amendment-7 check for the lag term** (`diag_osc_lag1.py`, `results/diag_osc_lag1/`). Pair (5,5), 64 stratified ℓ
  across the F2 15.75 file (weights ∝ ℓe^ℓ), Δr = 0.1 to 6·10⁴. The dropped ℓ-oscillating part, file-averaged, as a
  fraction of v:

  | b | 100 | 300 | 1000 | 3000 | 10⁴ |
  |---|---|---|---|---|---|
  | lag 0 (enters v) | (−4.2 ± 0.3)e-6 | (−3.0 ± 0.6)e-5 | (−0.9 ± 0.6)e-4 | (−0.9 ± 2.3)e-4 | (−1.3 ± 5.3)e-4 |
  | lag 1 (enters Cov) | (0.6 ± 0.5)e-5 | (−1.8 ± 4.0)e-5 | (−0.06 ± 0.8)e-4 | (−0.4 ± 2.5)e-4 | (−3.3 ± 7.0)e-4 |
  | **B term (lag 0 − lag 1)** | (−1.0 ± 0.5)e-5 | (−1.3 ± 4.1)e-5 | (−0.8 ± 1.0)e-4 | (−0.5 ± 3.4)e-4 | **(2.0 ± 8.9)e-4** |
  | largest at a single ℓ, lag 1 | 6.6e-5 | 5.1e-4 | 1.2e-3 | 5.1e-3 | 1.3e-2 |

  - Lag 0 reproduces §3's 64-ℓ run (same magnitudes and SEs; §3 quotes |avg|), on a grid now extended to 6·10⁴.
  - As at lag 0, the single-ℓ values are large (up to 1.3e-2 at b = 10⁴) and the file average is consistent with zero.
  - **Resolution, not detection:** 2σ ≈ 1.8e-3 of v at b = 10⁴ for the heaviest pair at the lowest height. That is
    ≤ 9e-4 relative in g_B (≈ 6e-4 absolute), against a per-file SE on g of about 0.04. Other pairs carry smaller
    weights.
  - **It misses the 10⁻³ standard; accepted as recorded (Will, twenty-fifth round).** The 10⁻³-of-v standard (seal
    condition (ii), and §3's lag-0 resolution) is not met by this check's resolution at b = 10⁴. It does not matter
    for the test: the shift it allows in g_B, about 6×10⁻⁴, is about 1.5% of the per-file SE on g (≈ 0.04), so it cannot
    move a verdict. The standard is not relaxed elsewhere.
- **Validity range.** Lag 1 at b = 10⁴ reaches r = 5.8·10⁴ spacings ≈ 2.3·10⁴ in t, still ≪ t ≥ 10⁷ (§4 of the design).
- **Prime-cutoff convergence of the lag term: required before the seal (Will, twenty-fifth round); DONE —
  converged.** The amendment-4 diagnostic covered lag 0 at b ≤ 300 only.
  - **Setup.** `gs_zeta_cutB.py`, run by `run_gs_zeta_cutB_spot.sh` (48 procs, ~2.3 h). It evaluates every node pair
    at pmax 10⁶ for ℓ = 15.7502, on the short grid and the full estimator-B long grid. It compares against the stored
    3·10⁵ values, assembled as in `gs_zeta_B.py`. I₃ is held at 3·10⁵.
  - **Output.** `results/gs_zeta_cutB/cutB_summary.json`. The per-pair npz files stay on spot.
  - **Results, 3·10⁵ → 10⁶:**

  | b | Δ[Cov(3b)/b] / v_B | Δv / v | **Δv_B / v_B** |
  |---|---|---|---|
  | 100 | −2.2e-5 | −2.3e-5 | +3.9e-7 |
  | 300 | −8.4e-5 | −8.6e-5 | +6.6e-7 |
  | 1000 | −3.7e-4 | −3.8e-4 | +1.3e-6 |
  | 3000 | −1.3e-3 | −1.4e-3 | +2.0e-6 |
  | 10⁴ | −5.0e-3 | −5.1e-3 | **+3.1e-6** |

  - **g_B: 0.670275 → 0.670276** (Δ = +9.2e-7).
  - I₂ changes by 1e-8. The 3·10⁵ recheck against the stored v is ≤ 2e-15. At 10⁶, |Im| ≤ 6.8e-7 and the Fourier tail
    is ≤ 4.7e-6.
  - **What moves is a constant in C.** The lag term and v(b) shift by the same amount, growing ∝ b: Δv/b = −1.7e-8 at
    every rung. That is the signature of a constant shift δC of C(r) over the whole grid. Primes beyond 3·10⁵ beat
    against each other with periods far longer than 6·10⁴ spacings, so on this grid they look constant (a c∞-type
    term). Estimator B cancels a constant exactly (amendment 8), so v_B moves by ≤ 3e-6 while v and Cov move by up to
    5e-3.
  - **Side finding (§1, superseded estimator).** The plain v(10⁴) of §1 is cutoff-sensitive at 5e-3, i.e. about 2.5e-3
    relative in g. Amendment 4's check at b ≤ 300 did not reach this. It does not affect the estimator-B prediction,
    which is the one to be sealed.

### 6.3 GUE baseline and F1 under B (descriptive; `ph2s2/results/tapered/TAPERED_SUMMARY.md`)
- **GUE (Stage 1, 16 × 10⁶):** g_B = 0.997, with v_B(10⁴) = 0.1199 ± 0.0092 (SE ≈ 0.04 in g). The prediction 0.959 is
  within 1 SE.
- **F1 (seen data; not the F2 heights):** g_B = 0.663, 0.669, 0.714, 0.682, 0.685, 0.752 at ℓ = 14.46, 15.47,
  17.75, 19.25, 21.50, 22.10 (F1a–e, F1x; SE ≈ 0.03–0.06 in g, from v(10⁴)), against the predicted 0.665–0.720 at the F2 heights
  15.75–21.75. F2 is the test.
