# Parametric spectral dynamics — pipeline notes (phase 0, 2026-10-01)

Synthetic-only phase (PARAMETRIC_DYNAMICS_PLAN.md §2 phase 0; Will's corrections of 2026-10-01 folded in). No
`cache/armb` read. Modules: `pdyn_m2.py` (bulk, eigenvalue-only), `pdyn_m3.py` (edge/outlier dynamics),
`pdyn_calib.py` (calibrators C1–C5 + planted crossing), `verify_pdyn.py` (known answers, `--redpath`). Everything
below was produced by those files on the real Arm B grid (161 checkpoints to 3000; `grids.arm_grid`) unless stated.

## 1. What each module computes

**M2 (`pdyn_m2.analyse(spectra (T,n), times)`)** — per declared time window, never pooled across the cadence change
(default windows `[0,500)` and `[500,3001)`):
1. strip the top `top_k = 16` levels BEFORE unfolding;
2. unfold each checkpoint against its own smoothed integrated density: Gaussian-CDF kernel smoothing of the
   staircase, per-level bandwidth `kde_c` × local spacing (the stage2_g7 `unfold("kde", c)` formula, s3stats
   machinery); **default `kde_c = 32`** (see §3); non-monotone unfolding refused (> 0.1 % non-positive spacings);
3. band = rank quantiles `[0.10, 0.90)` of the remaining levels; per checkpoint the band is centred (one
   translation removed) and ONE time-averaged factor sets unit mean spacing (Δ = 1). Levels tracked by sorted index;
4. velocities v = Δε/Δt at interval midpoints (uneven spacing exact); **local** mean-square velocity ⟨v²⟩ᵢ = cubic
   least-squares fit of the per-level time-mean v² against band index (`v2_deg = 3`); rescaled time
   x = t·√⟨v²⟩ᵢ/Δ; `x_step = dt·v_rms`; velocity skew, excess kurtosis, KS vs Gaussian;
5. C(x) = ⟨v(x')v(x'+x)⟩ᵢ/⟨v²⟩ᵢ over same-level pairs, binned in x (`xbin = 0.1`, bins with < 10 pairs → NaN), and
   C_lag by index lag;
6. curvature K by the three-point uneven second difference; **k = Δ·K/(πβ⟨v²⟩ᵢ)** with β = 1 always (so a β = 2
   process reads with k doubled); fitted: ν̂ (fixed scale, MLE in C_ν(1+k²)^{−ν}), (ν̂, γ̂) free scale, truncated fit
   |k| < k_cut = 1/(π x_step_max), KS to the ZD form, tails P(|k| > 1, 2, 5), Hill tail index on |k| > 1, 2,
   median |k|, mean |k|, k skew / excess kurtosis.
   Outputs: dict → `save()` writes `.json` (scalars) + `.npz` (curves, k samples, local ⟨v²⟩). CLI:
   `python pdyn_m2.py in.npz out [--kde-c 32] [--windows a0 b0 a1 b1] [--pool]`.

**M3 (`pdyn_m3.analyse(sig, U, V, times, K=16)`)** — per consecutive checkpoint pair: overlap
O_ij = (|⟨uᵢ,uⱼ'⟩| + |⟨vᵢ,vⱼ'⟩|)/2; Hungarian matching (`linear_sum_assignment`); sign fix for display only;
Davis–Kahan gap rule: match accepted iff the local gap g_i = min(σ_{i−1}−σ_i, σ_i−σ_{i+1}) > `gap_mult` (2) ×
δ_ab at both checkpoints, δ_ab = max_j |σ_j(b) − σ_j(a)| over the top-K (a Weyl lower bound on ‖ΔW‖₂, declared
proxy — the bank has no ΔW), and matched overlap ≥ `overlap_min` (0.5); else FLAGGED ambiguous. Avoided-crossing
events: interior local minima of the gap series g_i(t) with g_min < `event_frac` (0.5) × median_t g; refined by
fitting g² (exactly quadratic in t for a two-level system) through three points → t_min, g_min; mixing angle
θ = arccos|⟨uᵢ(t_{k−1}), uᵢ(t_{k+1})⟩| (and the V side); event ambiguous if any adjacent step/level was flagged.
Exported: event times (all; unambiguous) as point processes, ambiguous fractions, swaps, qualities.

**Calibrators (`pdyn_calib.py`)** — stationary Gaussian matrix processes on the real grid (or `uniform:dt:stop`):
- C1 smooth β = 1: H(t) = Σₐ L_ta Gₐ (Gₐ GOE; L = Karhunen–Loève factor of exp(−(t−t')²/2τ²)); rectangular analogue
  (iid real Gaussian W → singular values). Positive control for ZD/SA.
- C1 literal DBM: H + s√dt·G with s set so the per-interval displacement is `xstep` spacings (optional OU).
  Independent increments ⇒ white velocities, Gaussian FD curvature; no ZD/SA statistics at any cadence.
- C2: β = 2 (GUE increments; complex W → real singular values); Poisson walk (independent smooth GPs, no repulsion).
- C3 `shuffle`, C5 `sign_flips` (joint/independent), C4 `roundtrip_floor` (fp32 master precision; bf16 reported as a
  comparison only), `planted_crossing` (two-level system in the top-16, analytic t₀, 2c, rotation angle).
- Rate knob: τ from `xstep` at `dt_ref` (default 10) via x_step = dt·√(2n)/(πτ) for a GOE bulk (β = 2 τ scaled by
  1/√2 so x_step matches). The rate is an ASSUMPTION about the real runs ("DBM-rate assumption"), not a measurement.

## 2. Zakrzewski–Delande normalisation: verification result

Source used (the 1993 PRE is paywalled): **Fyodorov, arXiv:1108.0950** (Acta Phys. Pol. A 120, 100 (2012)), read
from ar5iv. His eq. (4), (6): λ_m(t) = λ_m + t v_m + t² C_m, C_m = Σ_{n≠m}|W_mn|²/(λ_m−λ_n) ⇒ C = K/2; eq. (7):
C_typ = πρ(μ) y_typ, y_typ = Tr W²/N (ρ unit-normalised); eq. (40): the ZD GUE law
P(c) = (2/π) κ³/[(c−c₀)² + κ²]², κ = πρy = 1, c = C/C_typ (c₀ = the smooth global-curvature offset, removed by
per-checkpoint unfolding). With ⟨v²⟩ = ⟨|W_mm|²⟩ = y_typ/N and Δ = 1/(Nρ): πβ⟨v²⟩/Δ = 2πρ y_typ = 2C_typ, hence
k = K/(2C_typ) = c and **P(k) = (2/π)(1+k²)^{−2} with k = Δ·K/(πβ⟨v²⟩), β = 2** — i.e. the family
P_β(k) = C_β(1+k²)^{−(β+2)/2}, C_1 = 1/2, C_2 = 2/π, C_4 = 8/(3π). For β = 1 the same scale follows from the
small-spacing tail (GOE p(s) ≈ (π²/6)s/Δ², K ≈ 2W²_mn/s, ⟨v²⟩ = 2⟨W²_mn⟩ for real Haar vectors ⇒ P(K) → γ²/(2K³),
γ = π⟨v²⟩/Δ). von Oppen PRL 73, 798 (1994) abstract states the same k = K/(πβρ⟨(dE/dλ)²⟩) (APS page returned 403;
read through the search engine's rendering). **The addendum's memory version (k = Δ·K/(πβ⟨v²⟩),
P ∝ (1+k²)^{−(β+2)/2}) matches the sources.** Note Canali et al. (cond-mat/9602018) use the OTHER convention
k = K/⟨|K|⟩; under the velocity scale ⟨|k|⟩ = 1 exactly for β = 1 and 2/π for β = 2, so the two agree for GOE only.

Numerical confirmation (`compare_oracle`, 3001 per-step checkpoints, 512×512, τ = 300, ORACLE = fixed semicircle
CDF): β = 1 median |k| = 0.582 / 0.576 (exact 1/√3 = 0.5774), ν̂_fixed = 1.48 / 1.49 (1.5); β = 2 median
0.879 / 0.881 (exact 0.879 under the β = 1 scale), γ̂_free = 2.04, ν̂_free = 2.00. With the pipeline's own kde(32)
unfolding at the plan's rate (τ = 1019, per-step): median 0.582, ν̂_fixed 1.482, γ̂ 0.997, KS 0.004, ⟨|k|⟩ 1.018.
Rectangular β = 1 (2048×512, kde(32), per-step): median 0.601, ν̂ 1.457, γ̂ 1.035, ⟨|k|⟩ 1.02 — singular values
obey the same scale (coupling s²/2 vs velocity s², the GOE ratio). **Open:** complex rectangular (β = 2, 2048×512)
reads median 1.015 and γ̂ 2.28 (expected 0.879 / 2.0; exponent ν̂_free 1.97 is right) — a +13–14 % scale excess
on one seed, unexplained; flagged for phase 1 if complex matrices ever matter (they do not for the real runs).

## 3. Instrument findings that changed the design (all measured, all in the docstrings)

1. **Unfolding bandwidth.** Against the oracle, per-checkpoint kde unfolding injects velocity noise
   var(v_kde − v_oracle)/var(v_oracle) = 13 % (c = 4), 8 % (8), 4–5 % (16), 2 % (32), and inflates median |k| from
   0.577 to 0.651 / 0.624 / 0.604 / 0.594. The Stage 3 kde(4) is therefore NOT the dynamics setting; default c = 32
   (the s3stats long-range setting). The witness separation holds at every c ∈ {4, 8, 16, 32} (verify (b)).
2. **Local velocity scale.** After unfolding, ⟨v²⟩ varies across the band as the local density squared (×2.5 over the
   band for the MP-shaped singular-value density); a band-mean scale biases k by ρᵢ²/⟨ρ²⟩. A 33-level moving average
   (25 % noise with ~1 realisation per correlation time) and a log-space fit (E[log χ²₁] = −1.27 bias) were rejected;
   the cubic linear-space fit is in place.
3. **Renormalisation.** Pinning the band's end levels froze two levels; a per-checkpoint span/slope rescale injected a
   random dilation of ~1.4 × 10⁻³ relative (reported as `unfold.span_rel_sd`), ~0.3 spacing at the band edge —
   larger than x_step. Centre-only + one time-averaged scale is in place.
4. **Finite-difference curvature is not the ZD curvature at the real cadence.** It is the velocity change over
   ~2 x_step; the tail beyond |k| ≈ 1/(π x_step) is lost and the body broadens. Every curvature statistic is compared
   with the β = 1 calibrator at the SAME cadence and x_step, never with the formula (the formula is recovered only as
   x_step → 0, §2).
5. **A literal DBM carries no SA/ZD statistics.** C_lag[1] = −0.04, median |k| = 2.19 vs the Gaussian prediction
   0.6745·√2/(π x_step) = 2.16. Whether the real trajectories look DBM-like or smooth at 10-step cadence is a phase-1
   measurement (C_lag[1] ≈ 0 ⇒ DBM-like); the plan's "DBM-rate" wording refers to the rate, not to the process class.
6. **Shuffled order has an exact answer:** iid positions give a pooled lag-1 FD-velocity correlation
   −Σ1/(d_k d_{k+1})/Σ(2/d_k²)·(T−1)/(T−2) = −1/2 for uniform spacing (measured −0.501 in [500,3001)), −0.36 for the
   log-step window (measured −0.32); lags ≥ 2 vanish. "C(x) collapses" means this, not C → 0 at lag 1.

## 4. Sample sizes at which each discrimination works (feeds the pre-registration's power statement)

Shapes 512×512 / 2048×512 / 512×2048, real grid, x_step 0.1 at 10 steps (τ ≈ 1019; **rate assumption**), kde(32),
statistic S = median |k| in [500,3001) (x_step ≈ 0.21), 4 seeds per family:

| family | S per seed | ν̂_fixed |
|---|---|---|
| β = 1 smooth (sym) | 0.696 0.698 0.682 0.677 | 1.44 |
| β = 2 smooth (sym) | 0.926 0.933 0.928 0.935 | 1.26 |
| Poisson walk | 0.123 0.125 0.127 0.123 | 1.97 |

- β = 1 vs β = 2: seed-dispersion z = 21.6 (c = 32; 32–38 at c ≤ 16); within one series, random level blocks of
  **10 levels × 100 interior checkpoints = 1000 curvature samples** separate at z > 3 (5 levels: z = 2.8). One 70M
  matrix (band ≈ 400 levels) over 100 checkpoints is ~40× that.
- β = 1 vs Poisson: z = 54 across seeds; **5 levels × 100 checkpoints = 500 samples** suffice (z = 10.9).
- Declared thresholds (c = 32, x_step ≈ 0.2): Poisson < 0.45 < β1 < 0.80 < β2. Red path (threshold flipped so the
  β = 1 seeds must read β = 2) fails as required.
- The **tail exponent** itself (−3/2 vs −2 in (1+k²), i.e. Hill α = 2 vs 3 on |k|) is NOT readable at the real
  cadence: at x_step ≈ 0.2 Hill α(k₀ = 1) is 1.8 for β = 1 and 1.4–1.6 for β = 2 (ordering inverted by the ×2 scale
  and the FD truncation). At per-step cadence (x_step 0.01–0.03) Hill α(k₀ = 2) = 1.8 (β = 1) / 2.2 (β = 2) and
  ν̂_free = 1.47 / 2.00 — the exponent separates there; the fixed-scale ν̂ and the median separate at any cadence.
- Velocity Gaussianity at the real cadence: |skew| ≤ 0.11, |excess kurtosis| ≤ 0.15, KS ≤ 0.012 on every β = 1 shape
  (effective n ≈ n_band × span/τ ≈ 400 × 2.5, not n_band × T).
- Two independent β = 1 draws agree on C_lag[1..6] within 0.09 and on C(x ≤ 2) within 0.094 (bins with ≥ 10 pairs).
  The SA reference curve is the calibrator's own C(x) (e.g. sym 512 at x_step 0.077: 0.92, 0.70, 0.44, 0.19, −0.01,
  −0.15, −0.22, −0.27, −0.28 for x = 0.05 … 0.85), not a formula.

## 5. Curvature tail lost to cadence (C6; same realisation subsampled; DBM-rate ASSUMPTION, kde(32), 512×512)

Rate A — the plan's assumption, x_step 0.1 per 10 steps (τ ≈ 1019), 0–3000:

| cadence | x_step | median k | ν̂_fixed | γ̂_free | P(k>2) | P(k>5) | Hill α(k₀=2) | C_lag[1] |
|---|---|---|---|---|---|---|---|---|
| 1 step | 0.009 | 0.582 | 1.482 | 1.00 | 0.110 | 0.0206 | 1.82 | 0.997 |
| 5 | 0.046 | 0.590 | 1.463 | 1.00 | 0.115 | 0.0227 | 1.82 | 0.964 |
| **10** | 0.092 | 0.611 | 1.443 | 1.10 | 0.125 | 0.0200 | 2.00 | 0.891 |
| **25** | 0.219 | 0.674 | 1.452 | 1.86 | 0.119 | 0.0036 | 3.03 | 0.594 |

At this rate the 10-step cadence keeps the tail (P(|k| > 5) within 3 % of per-step; median +5 %); the 25-step
cadence loses **83 % of the P(|k| > 5) tail** and distorts the free-scale fit (γ̂ 1.9, ν̂_free 2.4).

Rate B — 3× faster (τ = 300, x_step 0.03 per step): median 0.593 / 0.650 / 0.693 / 0.582, P(|k| > 5)
0.0226 / 0.0112 / 0.0007 / 0.0000 at 1 / 5 / 10 / 25 steps (x_step 0.03 / 0.15 / 0.29 / 0.55): the 10-step
cadence already loses 97 % of the k > 5 tail and the 25-step cadence all of it; C_lag[1] turns negative at 25
(aliasing). **The production cadence rule must be set from the measured x_step of the real runs (phase 1), not from
either assumption.**

## 6. Other measured quantities

- **C4 floor (fp32 round-trip, 2048×512, entries rms 0.02, 40 checkpoints):** unfolded-level displacement rms
  3.4 × 10⁻⁷ spacings vs 0.107 per step at rate A — ratio 3 × 10⁻⁶ (raw relative σ change 6 × 10⁻¹⁰). bf16, as a
  comparison only: 0.022 spacings, 21 % of a step. The fp32 master precision is not a velocity floor at any rate
  considered; the A0 vs A0r paired divergence (plan §3) remains the real floor.
- **M3 planted crossing:** t_min 1500.0 (true 1500), g_min 0.1000 (true 0.1), θ_U = θ_V = 26.6° (analytic 26.6°),
  not ambiguous; with 2c = 0.01 against a per-step change of 0.025 the event is detected and FLAGGED ambiguous
  (0.2 % of step/level matches flagged). Sign flips (joint and independent) leave all M3 arrays bit-identical.
- Runtime: `verify_pdyn.py` 267 s on 5 CPU threads (3 shapes × 4 seeds + sweeps); the 3001-checkpoint per-step
  series: 54 s generation + 49 s analysis (512×512), 540 s generation for complex 2048×512.

## 7. Guesses and open items (declared)

- The smooth Gaussian-process family (not the literal DBM) is the positive control for ZD/SA — the addendum names a
  DBM, which has no such statistics; both are implemented and the DBM's own known answers are verified.
- The Davis–Kahan proxy δ_ab = max|Δσ| over the top-K is a lower bound on ‖ΔW‖₂; the gap rule is therefore
  permissive; `gap_mult = 2` and `overlap_min = 0.5` are declared, untuned.
- The event criterion g_min < 0.5 × median gap, the band [0.10, 0.90), `v2_deg = 3`, `xbin = 0.1`, `min_pairs = 10`
  are declared defaults, untuned against real data.
- Complex rectangular β = 2 scale excess (+13 %) is unexplained (§2).
- All sample-size statements are at the assumed rate and for one matrix; the real x_step per window is the first
  number phase 1 must report.
