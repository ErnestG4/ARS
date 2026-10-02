# Attribution controls for the phase-1 P2 C(x) failure: C9 (β = 1 + real slow drift) and the C1-driver (β = 1 + optimiser-like velocity time scale) — 2026-10-02

Scope: PDYN_FINDINGS §4 candidates 1 and 2. Code: `pdyn_c9.py` (constructions + comparison), `verify_pdyn_c9.py`
(synthetic known answers, `--redpath`). Results: `results/armb_pdyn_c9/` (`<arm>/L<LL>_<M>.json` + `.npz` curves,
`table.csv`, `table.md`, `summary.json`). Units: A0 and M0s1, W2 = [500, 3000] (102 checkpoints, every 25 steps plus
step 512), layers 0, 2, 5, types Q, K, O, MLP_OUT (24 units). Pipeline: `pdyn_m2.analyse` with the sealed PARAMS
(top-16 stripped, kde(32), band [0.10, 0.90), local ⟨v²⟩ cubic) — untouched. Bank keys read: `sig_*`, `rms_*` only.
Phase-1 inputs: the real W2 C(x)/C_lag/velocity/curvature numbers and the C1 seed-mean curve from
`results/armb_pdyn_phase1/<arm>/parts/`, and the C1 draws regenerated bit-identically (same seed, matched τ, grid;
`c1_regen_s*` rows: vrms equal to the phase-1 value to 1e-9). Runtime 1 592 s on 5 workers (nice 10); 0 errors.

## 1. Constructions (declared before the run; verbatim in the module docstring)

**C9.** Real slow component: strip the top-16, sort, L(k, t) = log σ_(k)(t); Gaussian smoothing in time (sd σ_t = 200
steps; the measured velocity decorrelation time is ~85 steps) then in rank (sd h ranks): variants `smooth` h = 32 (the
unfolding's own bandwidth), `fine` h = 8, `raw` h = 0. Warp: a C1 draw (phase-1 seed and τ, real shape) is stripped of
its own top-16, each level mapped to its pooled quantile u = F_syn(σ) (time-mean empirical CDF of the stationary
synthetic bulk) and placed at exp(Lslow(u·n_eff − ½, t)); 16 dummy outliers above the bulk are prepended so the
pipeline's strip removes exactly them. C9 therefore carries the real slow density at every checkpoint (‖W‖_F, band
edges, log-moments, the whole quantile function) and the synthetic's β = 1 relative motion in quantile coordinates.
τ is re-solved from vrms² = (v_C1 τ_C1/τ)² + v_drift² (≤ 3 passes; vrms/target 0.951–1.046 on all 216 C9 draws,
all within 5 %). Companions: `zero` (time-mean map, no drift), `scale_only` (time-mean shape × real ‖W‖_F(t), a
pure dilation), `null` (slow component extracted from an independent C1 draw under the time-mean real map: the
extraction's leakage without real drift), `planted_A50` (zero map + δ log σ = 50 spacings × local log-spacing ×
sin(2πk/24) × (t − t_mid)/span: rank period 24 < the kde bandwidth, so the unfolding cannot remove it).

**C1-driver.** W(t) = W(0) + ∫M, W(0) iid N(0,1) at the real shape, M an iid OU momentum process with time constant
τ_v and stationary variance s_M² (exact joint Gaussian step per uneven interval; coefficients in the docstring,
series for dt/τ_v < 1e-2). After every step W is rescaled to its initial Frobenius norm (a pure dilation, exactly
invisible to the sealed unfolding; without it the entry variance grows by 2 s_M² τ_v t, a 40 % dilation at τ_v = 80).
τ_v ∈ {0 (literal DBM), 2, 5, 10, 20, 40, 80, τ_C1 (the matrix's matched C1 Gaussian-kernel τ, 420–960 steps)};
τ_v = ∞ (W(0) + t M(0)) is not a Simons–Altshuler limit at n = 512 (44 spacings of travel over W2; dev 26 on the
pilot unit) and is kept out of the sweep. s_M matched to the real vrms (∝; ≤ 3 passes on seed 0, seed 1 reuses seed 0's s_M): the match is LOW-SIDED —
vrms/target 0.874–0.987 at τ_v = 0 (21/48 draws below 0.95), 0.898–0.989 at τ_v = 10 (13/48 below), 0.911–0.989 at
τ_v = 80 (10/48), 0.871–0.985 at τ_v = τ_C1 (31/48); group means 0.935–0.969 (τ_v ≤ 80), 0.924–0.947 (τ_C1). The
norm projection makes vrms sublinear in s_M, so three proportional passes do not close the last 3–10 %; the driver's
x_step is correspondingly 3–13 % below the real one (C(x) is read in rescaled x, C_lag in checkpoint lag).

**Comparison.** The runner's dev_Cx (max over bins x ≤ 2 with ≥ 10 pairs, / 0.15) and dev_Clag (max over lags 1–6,
/ 0.10), against the real curve and the phase-1 C1 seed-mean, are reported as computed. On the first unit the runner's
dev_Cx was set by the bins x < 0.3 (63–400 pairs; band-edge levels with small local ⟨v²⟩): the same C1 draw under a
fixed map differs from itself by 0.14 there and by 0.008 on C_lag[1..6]. Words are therefore taken on dev_Clag and on
dev_Cx_dense (bins with ≥ 1 000 pairs on both curves; declared before the full run): REPRODUCES = both ≤ 1 vs real;
STAYS AT C1 = else both ≤ 1 vs C1; OVERSHOOTS = else dip (min C over dense bins, 0.3 ≤ x ≤ 2) shallower than real by
> 0.15 or C_lag[1] above real by > 0.10; PARTIAL = else every dense bin between C1 and real within 0.15; OFF-CURVE
otherwise. The dip was first read on ≥ 10-pair bins; a 10-pair bin set the verifier's planted-A50 minimum, so the dip
moved to dense bins and all stored words were recomputed from the stored curves (`--reword`; only the OVERSHOOTS /
PARTIAL / OFF-CURVE branch depends on the dip).

## 2. Verifier (`verify_pdyn_c9.py`, synthetic only, 512 × 512, W2 grid, vrms 0.0177; 92 s per mode)
```
(i) zero-drift warp vs same-seed C1: max|dC_lag[1..6]| 0.0086 (<= 0.05), dense max|dC(x<=2)| 0.0179 (<= 0.075); C_lag[1] +0.062 vs +0.071; med|k| 0.644 vs 0.642 | scale-only vs zero: max|dC_lag| 1.48e-15 (<= 1e-9; fro x1.88)
(ii) planted A=5 (lambda 24 ranks): C_lag[1] +0.088 (zero +0.062), C_lag[2] -0.226, dip -0.257 (zero -0.243), med|k| 0.579, vrms/target 1.012 (matched True, tau 610)
(ii) planted A=20 (lambda 24 ranks): C_lag[1] +0.359 (zero +0.062), C_lag[2] -0.093, dip -0.137 (zero -0.243), med|k| 0.355, vrms/target 0.983 (matched True, tau 988)
(ii) planted A=50 (lambda 24 ranks): C_lag[1] +0.416 (zero +0.062), C_lag[2] +0.114, dip +0.045 (zero -0.243), med|k| 0.252, vrms/target 1.200 (matched False, tau 3427)
(ii) A=50: dC_lag[1] +0.354 (> 0.1), d dip +0.287 (> 0.15) -> fires
(iii) driver tau_v=0: C_lag[1..3] [-0.207 -0.096 -0.043] med|k| 0.792 vrms/target 0.959 | pdyn_calib.dbm_sym(rect): C_lag[1..3] [-0.219 -0.095 -0.06 ] med|k| 0.775 vrms/target 0.980 | dev lag 0.020 (<= 0.1) dense 0.042 (<= 0.15); C_lag[1] below C1 by +0.278 / +0.290 (> 0.1)
(iii-b) driver tau_v = tau_C1 = 580: C_lag[1..3] [ 0.092 -0.231 -0.137] med|k| 0.658 vrms/target 0.950 | vs independent C1: dev lag 0.032 (<= 0.1) dense 0.047 (<= 0.15); vs C1 seed 0: 0.021 / 0.060
(iv) extraction (h 32, sigma_t 200) vs planted: drift rms error over the band, inner window 0.311 spacings (<= 1.5 x leakage; leakage on a zero-drift series 0.236; the time-constant map offset is 3.59 spacings rms, not gated); edge-90 move over the inner window planted +112.7 recovered +112.4 spacings (within 10 %); planted total: fro x1.88, logsd x1.20
(iv) matched C9 of the planted smooth drift: C_lag[1..3] [ 0.063 -0.219 -0.135] med|k| 0.644 vrms/target 1.009 (tau 580 vs C1 580) | vs same-seed C1: dev lag 0.009 dense 0.018 (<= 0.1 / 0.15); vs independent C1: 0.029 / 0.056 | synthetic real itself vs C1: lag 0.018 dense 0.038
FAILURES: none            (exit 0)
--redpath: (ii) A=50: dC_lag[1] +0.354 (> 0.1), d dip +0.287 (> 0.15) -> DOES NOT FIRE (threshold FLIPPED)
REDPATH failures: ['(ii) planted A=50 does not fill the dip: dC_lag1 +0.354, d dip +0.287 (FLIPPED)']   (exit 0)
```
Item (iii) as briefed ("τ → 0 reproduces the C1 curve") is not the right limit for an OU-velocity process: τ_v → 0 is
the literal DBM (phase-0 known answer, checked against `pdyn_calib.dbm_sym`), and the C1-like reference is τ_v = τ_C1
(iii-b). Gate calibrations changed after a first green run and before the full-run words were read: the dip on dense
bins (ii), and (iv) gated relative to the measured leakage (0.236) instead of an absolute 0.3 (first read 0.311).

## 3. Real drift over W2 (per matrix; edge moves in units of the time-mean band spacing; "surv." = the slow
deformation alone through the sealed unfolding: rms index-tracked displacement in spacings, and its velocity rms as a
percentage of the real vrms; null = the same extraction on a drift-free C1 series)
| arm | L | type | x_step | vrms 1st/2nd half | fro x | edge10 move | edge90 move | spacing x | logsd x | surv. drift rms smooth/fine/raw (null) | surv. v/vrms smooth/fine/raw (null) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 0 | Q | 0.44 | 0.0157/0.0194 | 1.26 | -2 | +81 | 1.22 | 1.09 | 0.16/0.33/0.48 (0.02/0.11/0.22) | 1.4/3.4/6.0 % (0.5/2.0/4.4) |
| A0 | 0 | K | 0.39 | 0.0133/0.0178 | 1.17 | -0 | +59 | 1.16 | 1.06 | 0.15/0.27/0.44 (0.03/0.10/0.22) | 1.4/3.3/6.7 % (0.8/2.3/5.2) |
| A0 | 0 | O | 0.64 | 0.0253/0.0262 | 1.42 | -3 | +135 | 1.38 | 1.15 | 0.33/0.59/0.71 (0.02/0.07/0.15) | 1.8/3.4/4.8 % (0.3/1.1/2.3) |
| A0 | 0 | MLP_OUT | 0.54 | 0.0177/0.0251 | 1.44 | +158 | +265 | 1.31 | 0.88 | 0.15/0.24/0.42 (0.02/0.08/0.20) | 1.0/2.0/4.3 % (0.3/1.5/3.4) |
| A0 | 2 | Q | 0.48 | 0.0174/0.0211 | 1.17 | -6 | +49 | 1.15 | 1.11 | 0.20/0.40/0.53 (0.02/0.09/0.20) | 1.4/3.3/5.7 % (0.4/1.6/3.8) |
| A0 | 2 | K | 0.44 | 0.0149/0.0203 | 1.13 | -7 | +18 | 1.06 | 1.07 | 0.11/0.23/0.42 (0.02/0.10/0.21) | 0.8/2.5/5.5 % (0.4/2.1/4.4) |
| A0 | 2 | O | 0.54 | 0.0219/0.0217 | 1.64 | +0 | +229 | 1.78 | 1.23 | 0.30/0.42/0.48 (0.03/0.07/0.17) | 2.8/4.8/6.0 % (0.4/1.5/3.1) |
| A0 | 2 | MLP_OUT | 0.53 | 0.0205/0.0219 | 1.45 | +78 | +290 | 1.70 | 1.21 | 0.08/0.19/0.34 (0.03/0.09/0.19) | 0.6/2.0/4.1 % (0.5/1.5/3.3) |
| A0 | 5 | Q | 0.42 | 0.0153/0.0186 | 1.29 | -3 | +85 | 1.24 | 1.12 | 0.24/0.45/0.57 (0.03/0.09/0.20) | 2.3/4.7/7.2 % (0.5/1.8/4.4) |
| A0 | 5 | K | 0.37 | 0.0132/0.0167 | 1.19 | -6 | +45 | 1.14 | 1.09 | 0.14/0.26/0.38 (0.03/0.11/0.25) | 1.4/3.4/6.8 % (0.5/2.4/5.6) |
| A0 | 5 | O | 0.49 | 0.0201/0.0196 | 1.74 | +13 | +253 | 1.82 | 1.11 | 0.15/0.26/0.38 (0.02/0.10/0.20) | 1.8/3.3/5.6 % (0.3/1.8/3.8) |
| A0 | 5 | MLP_OUT | 0.44 | 0.0182/0.0174 | 1.86 | +149 | +442 | 2.14 | 1.21 | 0.07/0.18/0.35 (0.02/0.09/0.20) | 1.1/2.8/5.9 % (0.4/1.7/4.4) |
| M0s1 | 0 | Q | 0.55 | 0.0220/0.0223 | 1.45 | +5 | +155 | 1.48 | 1.11 | 0.03/0.12/0.24 (0.03/0.09/0.19) | 0.4/1.5/3.3 % (0.4/1.4/3.1) |
| M0s1 | 0 | K | 0.54 | 0.0215/0.0218 | 1.51 | +10 | +161 | 1.49 | 1.07 | 0.04/0.15/0.32 (0.03/0.11/0.20) | 0.4/1.7/3.7 % (0.5/1.6/3.4) |
| M0s1 | 0 | O | 0.68 | 0.0280/0.0266 | 2.04 | +11 | +301 | 2.11 | 1.17 | 0.12/0.21/0.31 (0.02/0.07/0.15) | 0.9/1.8/2.8 % (0.3/1.1/2.2) |
| M0s1 | 0 | MLP_OUT | 0.67 | 0.0271/0.0270 | 2.20 | +314 | +568 | 1.95 | 0.85 | 0.21/0.40/0.40 (0.01/0.07/0.15) | 1.2/2.8/3.9 % (0.2/1.0/2.2) |
| M0s1 | 2 | Q | 0.53 | 0.0205/0.0225 | 1.52 | +3 | +187 | 1.59 | 1.16 | 0.11/0.19/0.30 (0.03/0.08/0.18) | 1.3/2.5/4.3 % (0.4/1.4/3.1) |
| M0s1 | 2 | K | 0.51 | 0.0195/0.0217 | 1.53 | +7 | +187 | 1.57 | 1.09 | 0.07/0.13/0.24 (0.03/0.08/0.19) | 1.0/2.1/4.0 % (0.4/1.3/3.4) |
| M0s1 | 2 | O | 0.60 | 0.0251/0.0233 | 2.57 | +16 | +372 | 2.69 | 1.18 | 0.20/0.34/0.39 (0.03/0.08/0.17) | 1.9/2.8/3.8 % (0.4/1.3/2.7) |
| M0s1 | 2 | MLP_OUT | 0.62 | 0.0274/0.0221 | 2.60 | +205 | +615 | 3.22 | 1.29 | 0.09/0.20/0.42 (0.02/0.07/0.17) | 0.5/1.6/3.5 % (0.3/1.2/2.6) |
| M0s1 | 5 | Q | 0.55 | 0.0221/0.0226 | 1.57 | -3 | +169 | 1.59 | 1.24 | 0.06/0.20/0.35 (0.02/0.08/0.17) | 0.6/1.9/3.6 % (0.3/1.3/3.0) |
| M0s1 | 5 | K | 0.54 | 0.0215/0.0217 | 1.50 | -3 | +165 | 1.59 | 1.22 | 0.05/0.11/0.20 (0.02/0.08/0.18) | 0.4/1.4/3.3 % (0.4/1.3/3.1) |
| M0s1 | 5 | O | 0.56 | 0.0257/0.0194 | 4.02 | +42 | +521 | 4.11 | 1.07 | 0.14/0.19/0.28 (0.03/0.08/0.18) | 1.0/1.7/3.3 % (0.4/1.4/3.0) |
| M0s1 | 5 | MLP_OUT | 0.58 | 0.0263/0.0202 | 3.88 | +349 | +832 | 4.29 | 1.14 | 0.11/0.36/0.30 (0.02/0.08/0.17) | 0.7/2.5/3.9 % (0.3/1.3/2.7) |

Read-out: ‖W‖_F grows ×1.13–1.86 (A0) and ×1.45–4.02 (M0s1); the 90 % edge moves +18 to +442 (A0) and +155 to +832
(M0s1) spacings; the band log-sd changes ×0.85–1.29. Of this, the sealed per-checkpoint unfolding leaves an
index-tracked drift of 0.03–0.33 spacings rms (smooth), 0.11–0.59 (fine), 0.20–0.71 (raw) over the whole window,
whose velocity is 0.4–2.8 % (smooth), 1.4–4.8 % (fine), 2.8–7.2 % (raw) of the real vrms; the drift-free null
extraction gives 0.01–0.03 / 0.07–0.11 / 0.15–0.25 spacings and 0.2–0.8 / 1.0–2.4 / 2.2–5.6 %. The real vrms in the
first vs second half of W2 differs by −4 % to +42 % (A0) and −25 % to +10 % (M0s1).

## 4. Per-matrix words
## words per matrix (R = REPRODUCES, C1 = STAYS AT C1, OV = OVERSHOOTS, P = PARTIAL, OFF = OFF-CURVE); C9 matched seed 0 / seed 1; driver seed 0 / seed 1
| arm | L | type | x_step | real lag1/lag2 | C1 lag1/lag2 | C9 smooth m0/m1/null | C9 fine m0/m1/null | C9 raw m0/m1/null | drv τ=0 | drv τ=2 | drv τ=5 | drv τ=10 | drv τ=20 | drv τ=40 | drv τ=80 | drv τ=c1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 0 | Q | 0.44 | -0.163/-0.115 | +0.063/-0.235 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| A0 | 0 | K | 0.39 | -0.132/-0.107 | +0.133/-0.233 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| A0 | 0 | O | 0.64 | -0.352/-0.071 | -0.228/-0.165 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | R/R | C1/R | C1/C1 | C1/C1 |
| A0 | 0 | MLP_OUT | 0.54 | -0.395/-0.023 | -0.079/-0.211 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | OV/R | OV/OV | OV/OV | OV/OV | C1/C1 | C1/C1 | C1/C1 | C1/C1 |
| A0 | 2 | Q | 0.48 | -0.208/-0.123 | +0.002/-0.234 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| A0 | 2 | K | 0.44 | -0.179/-0.113 | +0.050/-0.229 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| A0 | 2 | O | 0.54 | -0.280/-0.072 | -0.094/-0.207 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 | C1/C1 | C1/C1 |
| A0 | 2 | MLP_OUT | 0.53 | -0.303/-0.074 | -0.063/-0.216 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 | C1/C1 | C1/C1 |
| A0 | 5 | Q | 0.42 | -0.128/-0.119 | +0.077/-0.230 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | OFF/OFF | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 | C1/C1 |
| A0 | 5 | K | 0.37 | -0.079/-0.120 | +0.182/-0.224 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | P/P | P/P | R/P | R/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| A0 | 5 | O | 0.49 | -0.268/-0.093 | -0.012/-0.233 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | OV/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| A0 | 5 | MLP_OUT | 0.44 | -0.212/-0.101 | +0.082/-0.239 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | OV/OV | C1/C1 | C1/C1 | C1/C1 |
| M0s1 | 0 | Q | 0.55 | -0.244/-0.126 | -0.107/-0.205 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | R/R | C1/R | C1/C1 | C1/C1 |
| M0s1 | 0 | K | 0.54 | -0.215/-0.144 | -0.099/-0.205 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 |
| M0s1 | 0 | O | 0.68 | -0.349/-0.091 | -0.262/-0.151 | R/R/R | R/R/R | R/R/R | R/R | R/R | R/R | R/R | R/R | R/R | R/R | C1/C1 |
| M0s1 | 0 | MLP_OUT | 0.67 | -0.387/-0.052 | -0.229/-0.159 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | C1/R | C1/C1 | C1/C1 | C1/C1 |
| M0s1 | 2 | Q | 0.53 | -0.214/-0.133 | -0.098/-0.208 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/OFF | P/R | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 |
| M0s1 | 2 | K | 0.51 | -0.185/-0.157 | -0.059/-0.218 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | P/R | P/R | P/R | R/R | R/R | R/R | C1/C1 | C1/C1 |
| M0s1 | 2 | O | 0.60 | -0.282/-0.110 | -0.194/-0.176 | R/R/R | R/R/R | R/R/R | R/R | R/R | R/R | R/R | R/R | R/R | C1/R | C1/C1 |
| M0s1 | 2 | MLP_OUT | 0.62 | -0.320/-0.099 | -0.161/-0.182 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | R/R | C1/R | C1/C1 | C1/C1 |
| M0s1 | 5 | Q | 0.55 | -0.229/-0.132 | -0.120/-0.208 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/OFF | R/R | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 |
| M0s1 | 5 | K | 0.54 | -0.205/-0.149 | -0.097/-0.206 | C1/R/C1 | C1/R/C1 | C1/R/C1 | R/R | R/R | R/R | R/R | R/R | R/R | R/R | C1/C1 |
| M0s1 | 5 | O | 0.56 | -0.252/-0.135 | -0.124/-0.202 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 |
| M0s1 | 5 | MLP_OUT | 0.58 | -0.292/-0.107 | -0.134/-0.197 | C1/C1/C1 | C1/C1/C1 | C1/C1/C1 | R/R | R/R | R/R | R/R | R/R | C1/C1 | C1/C1 | C1/C1 |


## 5. Driver C_lag[1] / C_lag[2] / median |k| per matrix (seed mean; curvature PROVISIONAL at bank cadence)
| arm | L | type | real | C1 | τ=0 | τ=2 | τ=5 | τ=10 | τ=20 | τ=40 | τ=80 | τ=c1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A0 | 0 | Q | -0.16/-0.11/0.72 | +0.06/-0.23/0.64 | -0.22/-0.09/0.80 | -0.20/-0.10/0.79 | -0.17/-0.12/0.78 | -0.12/-0.16/0.75 | -0.05/-0.19/0.72 | +0.01/-0.21/0.70 | +0.04/-0.23/0.68 | +0.09/-0.23/0.65 |
| A0 | 0 | K | -0.13/-0.11/0.77 | +0.13/-0.23/0.66 | -0.19/-0.09/0.88 | -0.16/-0.11/0.86 | -0.13/-0.13/0.85 | -0.06/-0.16/0.82 | +0.02/-0.20/0.78 | +0.10/-0.21/0.76 | +0.15/-0.22/0.72 | +0.19/-0.23/0.68 |
| A0 | 0 | O | -0.35/-0.07/0.55 | -0.23/-0.16/0.55 | -0.32/-0.08/0.59 | -0.33/-0.07/0.59 | -0.32/-0.09/0.58 | -0.30/-0.11/0.57 | -0.27/-0.13/0.57 | -0.25/-0.15/0.56 | -0.24/-0.16/0.55 | -0.18/-0.17/0.56 |
| A0 | 0 | MLP_OUT | -0.39/-0.02/0.57 | -0.08/-0.21/0.61 | -0.29/-0.08/0.67 | -0.27/-0.10/0.66 | -0.25/-0.12/0.65 | -0.21/-0.14/0.64 | -0.17/-0.17/0.64 | -0.14/-0.18/0.62 | -0.11/-0.20/0.61 | -0.08/-0.21/0.61 |
| A0 | 2 | Q | -0.21/-0.12/0.66 | +0.00/-0.23/0.64 | -0.25/-0.09/0.73 | -0.22/-0.11/0.73 | -0.20/-0.12/0.72 | -0.15/-0.15/0.70 | -0.10/-0.18/0.68 | -0.06/-0.21/0.67 | -0.03/-0.21/0.65 | +0.04/-0.23/0.63 |
| A0 | 2 | K | -0.18/-0.11/0.68 | +0.05/-0.23/0.65 | -0.22/-0.09/0.79 | -0.20/-0.10/0.78 | -0.17/-0.12/0.77 | -0.12/-0.15/0.74 | -0.05/-0.20/0.72 | -0.02/-0.22/0.70 | +0.03/-0.23/0.68 | +0.08/-0.23/0.65 |
| A0 | 2 | O | -0.28/-0.07/0.64 | -0.09/-0.21/0.60 | -0.28/-0.09/0.67 | -0.27/-0.10/0.66 | -0.25/-0.11/0.65 | -0.21/-0.14/0.64 | -0.17/-0.17/0.63 | -0.14/-0.19/0.62 | -0.12/-0.19/0.61 | -0.08/-0.20/0.61 |
| A0 | 2 | MLP_OUT | -0.30/-0.07/0.64 | -0.06/-0.22/0.62 | -0.27/-0.09/0.68 | -0.27/-0.09/0.67 | -0.25/-0.11/0.67 | -0.21/-0.15/0.66 | -0.15/-0.18/0.64 | -0.12/-0.19/0.63 | -0.10/-0.21/0.62 | -0.06/-0.22/0.61 |
| A0 | 5 | Q | -0.13/-0.12/0.72 | +0.08/-0.23/0.66 | -0.22/-0.09/0.82 | -0.20/-0.11/0.81 | -0.16/-0.13/0.79 | -0.10/-0.17/0.78 | -0.04/-0.20/0.75 | +0.04/-0.22/0.73 | +0.08/-0.23/0.70 | +0.12/-0.23/0.67 |
| A0 | 5 | K | -0.08/-0.12/0.79 | +0.18/-0.22/0.68 | -0.17/-0.09/0.90 | -0.16/-0.10/0.90 | -0.12/-0.13/0.88 | -0.05/-0.16/0.85 | +0.03/-0.20/0.81 | +0.13/-0.21/0.77 | +0.18/-0.21/0.73 | +0.22/-0.22/0.69 |
| A0 | 5 | O | -0.27/-0.09/0.69 | -0.01/-0.23/0.63 | -0.25/-0.09/0.71 | -0.24/-0.10/0.71 | -0.21/-0.13/0.71 | -0.17/-0.16/0.70 | -0.12/-0.19/0.68 | -0.07/-0.19/0.65 | -0.06/-0.21/0.65 | +0.01/-0.23/0.62 |
| A0 | 5 | MLP_OUT | -0.21/-0.10/0.75 | +0.08/-0.24/0.64 | -0.22/-0.10/0.79 | -0.20/-0.10/0.78 | -0.17/-0.13/0.77 | -0.13/-0.16/0.75 | -0.06/-0.19/0.72 | -0.00/-0.22/0.69 | +0.03/-0.22/0.68 | +0.09/-0.23/0.65 |
| M0s1 | 0 | Q | -0.24/-0.13/0.61 | -0.11/-0.20/0.59 | -0.29/-0.08/0.66 | -0.28/-0.08/0.65 | -0.26/-0.11/0.65 | -0.22/-0.14/0.64 | -0.18/-0.16/0.63 | -0.15/-0.18/0.62 | -0.13/-0.19/0.61 | -0.09/-0.20/0.60 |
| M0s1 | 0 | K | -0.22/-0.14/0.62 | -0.10/-0.20/0.60 | -0.28/-0.09/0.67 | -0.26/-0.10/0.67 | -0.24/-0.12/0.66 | -0.21/-0.14/0.64 | -0.17/-0.17/0.64 | -0.13/-0.19/0.63 | -0.11/-0.19/0.62 | -0.07/-0.21/0.61 |
| M0s1 | 0 | O | -0.35/-0.09/0.52 | -0.26/-0.15/0.52 | -0.34/-0.08/0.57 | -0.35/-0.07/0.57 | -0.34/-0.08/0.56 | -0.32/-0.10/0.56 | -0.30/-0.12/0.54 | -0.28/-0.13/0.54 | -0.26/-0.15/0.54 | -0.22/-0.16/0.55 |
| M0s1 | 0 | MLP_OUT | -0.39/-0.05/0.53 | -0.23/-0.16/0.55 | -0.35/-0.06/0.58 | -0.34/-0.07/0.57 | -0.33/-0.09/0.56 | -0.31/-0.10/0.56 | -0.28/-0.12/0.55 | -0.27/-0.14/0.55 | -0.26/-0.15/0.54 | -0.22/-0.17/0.55 |
| M0s1 | 2 | Q | -0.21/-0.13/0.60 | -0.10/-0.21/0.61 | -0.28/-0.08/0.67 | -0.26/-0.10/0.67 | -0.24/-0.11/0.65 | -0.20/-0.14/0.65 | -0.17/-0.16/0.64 | -0.13/-0.18/0.62 | -0.11/-0.19/0.62 | -0.06/-0.21/0.60 |
| M0s1 | 2 | K | -0.18/-0.16/0.62 | -0.06/-0.22/0.61 | -0.26/-0.09/0.70 | -0.25/-0.10/0.69 | -0.22/-0.12/0.68 | -0.18/-0.15/0.67 | -0.15/-0.18/0.66 | -0.11/-0.19/0.64 | -0.08/-0.20/0.63 | -0.04/-0.22/0.62 |
| M0s1 | 2 | O | -0.28/-0.11/0.58 | -0.19/-0.18/0.57 | -0.31/-0.08/0.62 | -0.30/-0.09/0.61 | -0.29/-0.10/0.61 | -0.27/-0.12/0.60 | -0.23/-0.14/0.59 | -0.21/-0.16/0.58 | -0.20/-0.17/0.57 | -0.15/-0.19/0.58 |
| M0s1 | 2 | MLP_OUT | -0.32/-0.10/0.55 | -0.16/-0.18/0.57 | -0.32/-0.08/0.60 | -0.31/-0.08/0.60 | -0.30/-0.09/0.59 | -0.27/-0.11/0.59 | -0.25/-0.14/0.58 | -0.23/-0.16/0.57 | -0.20/-0.16/0.57 | -0.17/-0.19/0.57 |
| M0s1 | 5 | Q | -0.23/-0.13/0.61 | -0.12/-0.21/0.60 | -0.29/-0.08/0.66 | -0.28/-0.09/0.65 | -0.26/-0.11/0.65 | -0.24/-0.14/0.63 | -0.19/-0.16/0.62 | -0.16/-0.18/0.61 | -0.13/-0.20/0.60 | -0.08/-0.20/0.60 |
| M0s1 | 5 | K | -0.21/-0.15/0.62 | -0.10/-0.21/0.60 | -0.28/-0.09/0.67 | -0.27/-0.09/0.67 | -0.25/-0.11/0.66 | -0.20/-0.14/0.65 | -0.16/-0.17/0.64 | -0.13/-0.18/0.62 | -0.12/-0.19/0.62 | -0.07/-0.21/0.61 |
| M0s1 | 5 | O | -0.25/-0.13/0.58 | -0.12/-0.20/0.59 | -0.29/-0.08/0.64 | -0.28/-0.10/0.64 | -0.27/-0.11/0.64 | -0.24/-0.13/0.63 | -0.19/-0.16/0.62 | -0.16/-0.18/0.61 | -0.14/-0.19/0.60 | -0.08/-0.21/0.59 |
| M0s1 | 5 | MLP_OUT | -0.29/-0.11/0.57 | -0.13/-0.20/0.59 | -0.30/-0.08/0.63 | -0.30/-0.09/0.63 | -0.28/-0.10/0.62 | -0.25/-0.13/0.61 | -0.22/-0.14/0.60 | -0.19/-0.17/0.60 | -0.16/-0.18/0.59 | -0.11/-0.20/0.59 |

## group counts
### A0

## 6. Group tables (n = draws; dev medians; velocity moments and vrms/target means)
|---|---|---|---|---|---|---|---|---|---|
| real | 12 | | -0.225 | -0.094 | 0.680 | | | -0.001 / +0.360 / 0.012 | |
| C1 (phase 1, seed mean) | 12 | | +0.009 | -0.221 | 0.631 | | | +0.005 / +0.094 / 0.004 | |
| c1_regen | 24 | STAYS AT C1 24 | +0.008 | -0.221 | 0.630 | 2.33 / 0.07 | 1.83 / 0.16 | +0.002 / +0.094 / 0.004 | nan |
| c9_smooth_zero | 12 | STAYS AT C1 12 | +0.004 | -0.218 | 0.632 | 2.28 / 0.10 | 1.79 / 0.19 | +0.000 / +0.074 / 0.004 | nan |
| c9_scale_only | 12 | STAYS AT C1 12 | +0.004 | -0.218 | 0.632 | 2.28 / 0.10 | 1.79 / 0.19 | +0.000 / +0.074 / 0.004 | nan |
| c9_smooth_matched | 24 | STAYS AT C1 24 | +0.004 | -0.220 | 0.631 | 2.24 / 0.10 | 1.76 / 0.21 | -0.001 / +0.080 / 0.004 | 0.987 |
| c9_smooth_null | 12 | STAYS AT C1 12 | +0.005 | -0.218 | 0.632 | 2.28 / 0.10 | 1.79 / 0.19 | +0.000 / +0.078 / 0.004 | 0.987 |
| c9_fine_zero | 12 | STAYS AT C1 12 | +0.004 | -0.218 | 0.631 | 2.27 / 0.09 | 1.75 / 0.21 | +0.001 / +0.076 / 0.004 | nan |
| c9_fine_matched | 24 | STAYS AT C1 24 | +0.004 | -0.219 | 0.630 | 2.24 / 0.10 | 1.76 / 0.22 | -0.002 / +0.079 / 0.004 | 0.988 |
| c9_fine_null | 12 | STAYS AT C1 12 | +0.004 | -0.218 | 0.631 | 2.27 / 0.10 | 1.76 / 0.20 | +0.001 / +0.082 / 0.004 | 0.987 |
| c9_raw_zero | 12 | STAYS AT C1 12 | +0.004 | -0.218 | 0.626 | 2.28 / 0.09 | 1.80 / 0.21 | +0.001 / +0.117 / 0.005 | nan |
| c9_raw_matched | 24 | STAYS AT C1 24 | +0.008 | -0.215 | 0.610 | 2.23 / 0.12 | 1.87 / 0.25 | -0.005 / +0.285 / 0.008 | 0.996 |
| c9_raw_null | 12 | STAYS AT C1 12 | +0.004 | -0.216 | 0.615 | 2.28 / 0.09 | 1.80 / 0.25 | -0.001 / +0.227 / 0.007 | 0.995 |
| c9_planted_A50 | 12 | OVERSHOOTS 12 | +0.368 | +0.085 | 0.246 | 6.00 / 3.61 | 4.50 / 3.09 | -0.012 / +1.702 / 0.028 | 1.198 |
| driver_tau0 | 24 | REPRODUCES 19, OFF-CURVE 2, PARTIAL 2, OVERSHOOTS 1 | -0.241 | -0.088 | 0.751 | 0.41 / 2.60 | 0.54 / 2.39 | +0.003 / +0.221 / 0.006 | 0.955 |
| driver_tau2 | 24 | REPRODUCES 20, OVERSHOOTS 2, PARTIAL 2 | -0.226 | -0.100 | 0.745 | 0.32 / 2.38 | 0.43 / 2.29 | +0.001 / +0.192 / 0.005 | 0.957 |
| driver_tau5 | 24 | REPRODUCES 21, OVERSHOOTS 2, PARTIAL 1 | -0.200 | -0.120 | 0.734 | 0.38 / 2.11 | 0.44 / 2.03 | -0.002 / +0.157 / 0.005 | 0.963 |
| driver_tau10 | 24 | REPRODUCES 21, OVERSHOOTS 3 | -0.153 | -0.151 | 0.716 | 0.67 / 1.64 | 0.60 / 1.53 | +0.000 / +0.129 / 0.005 | 0.966 |
| driver_tau20 | 24 | OVERSHOOTS 14, STAYS AT C1 6, REPRODUCES 4 | -0.095 | -0.182 | 0.694 | 1.23 / 1.04 | 0.93 / 0.98 | +0.000 / +0.105 / 0.005 | 0.969 |
| driver_tau40 | 24 | STAYS AT C1 23, REPRODUCES 1 | -0.045 | -0.201 | 0.675 | 1.74 / 0.58 | 1.24 / 0.64 | -0.005 / +0.091 / 0.004 | 0.965 |
| driver_tau80 | 24 | STAYS AT C1 24 | -0.013 | -0.211 | 0.657 | 2.08 / 0.29 | 1.55 / 0.40 | +0.000 / +0.103 / 0.005 | 0.967 |
| driver_tauc1 | 24 | STAYS AT C1 24 | +0.037 | -0.220 | 0.635 | 2.64 / 0.27 | 1.78 / 0.28 | +0.002 / +0.229 / 0.006 | 0.947 |

### M0s1
| control | n | words | C_lag1 mean | C_lag2 mean | med\|k\| mean | dev_Clag real / C1 (median) | dev_Cx_dense real / C1 (median) | v skew / exkurt / KS (mean) | vrms/target (mean) |
|---|---|---|---|---|---|---|---|---|---|
| real | 12 | | -0.265 | -0.120 | 0.585 | | | -0.001 / +0.255 / 0.009 | |
| C1 (phase 1, seed mean) | 12 | | -0.140 | -0.193 | 0.583 | | | +0.002 / +0.092 / 0.004 | |
| c1_regen | 24 | STAYS AT C1 19, REPRODUCES 5 | -0.147 | -0.192 | 0.579 | 1.19 / 0.10 | 0.85 / 0.19 | -0.002 / +0.090 / 0.004 | nan |
| c9_smooth_zero | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.151 | -0.188 | 0.581 | 1.14 / 0.11 | 0.83 / 0.22 | +0.002 / +0.086 / 0.003 | nan |
| c9_scale_only | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.151 | -0.188 | 0.581 | 1.14 / 0.11 | 0.83 / 0.22 | +0.002 / +0.086 / 0.003 | nan |
| c9_smooth_matched | 24 | STAYS AT C1 19, REPRODUCES 5 | -0.153 | -0.190 | 0.580 | 1.14 / 0.11 | 0.84 / 0.22 | -0.002 / +0.077 / 0.004 | 0.968 |
| c9_smooth_null | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.153 | -0.187 | 0.580 | 1.14 / 0.11 | 0.82 / 0.25 | +0.002 / +0.100 / 0.004 | 0.968 |
| c9_fine_zero | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.152 | -0.188 | 0.580 | 1.13 / 0.11 | 0.82 / 0.22 | +0.001 / +0.086 / 0.003 | nan |
| c9_fine_matched | 24 | STAYS AT C1 19, REPRODUCES 5 | -0.153 | -0.189 | 0.579 | 1.14 / 0.11 | 0.81 / 0.22 | -0.003 / +0.082 / 0.004 | 0.968 |
| c9_fine_null | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.154 | -0.187 | 0.580 | 1.12 / 0.11 | 0.80 / 0.24 | -0.001 / +0.089 / 0.004 | 0.968 |
| c9_raw_zero | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.151 | -0.187 | 0.576 | 1.17 / 0.12 | 0.85 / 0.21 | +0.001 / +0.104 / 0.004 | nan |
| c9_raw_matched | 24 | STAYS AT C1 19, REPRODUCES 5 | -0.151 | -0.188 | 0.567 | 1.16 / 0.11 | 0.83 / 0.25 | -0.007 / +0.180 / 0.006 | 0.974 |
| c9_raw_null | 12 | STAYS AT C1 10, REPRODUCES 2 | -0.152 | -0.185 | 0.568 | 1.16 / 0.11 | 0.85 / 0.22 | +0.002 / +0.183 / 0.006 | 0.974 |
| c9_planted_A50 | 12 | OVERSHOOTS 12 | +0.196 | -0.038 | 0.244 | 4.73 / 3.48 | 3.85 / 3.15 | -0.002 / +2.480 / 0.037 | 1.201 |
| driver_tau0 | 24 | REPRODUCES 21, OFF-CURVE 2, PARTIAL 1 | -0.300 | -0.081 | 0.640 | 0.55 / 1.71 | 0.76 / 1.52 | +0.001 / +0.227 / 0.005 | 0.935 |
| driver_tau2 | 24 | REPRODUCES 22, PARTIAL 2 | -0.291 | -0.089 | 0.635 | 0.40 / 1.62 | 0.69 / 1.45 | +0.005 / +0.204 / 0.005 | 0.940 |
| driver_tau5 | 24 | REPRODUCES 23, PARTIAL 1 | -0.274 | -0.103 | 0.628 | 0.29 / 1.42 | 0.55 / 1.29 | -0.001 / +0.157 / 0.005 | 0.947 |
| driver_tau10 | 24 | REPRODUCES 24 | -0.243 | -0.127 | 0.619 | 0.20 / 1.07 | 0.39 / 0.98 | +0.000 / +0.126 / 0.005 | 0.948 |
| driver_tau20 | 24 | REPRODUCES 23, STAYS AT C1 1 | -0.208 | -0.152 | 0.609 | 0.52 / 0.69 | 0.43 / 0.61 | -0.003 / +0.107 / 0.004 | 0.951 |
| driver_tau40 | 24 | REPRODUCES 18, STAYS AT C1 6 | -0.179 | -0.171 | 0.599 | 0.82 / 0.37 | 0.60 / 0.41 | +0.004 / +0.096 / 0.004 | 0.951 |
| driver_tau80 | 24 | STAYS AT C1 19, REPRODUCES 5 | -0.158 | -0.181 | 0.591 | 1.04 / 0.17 | 0.75 / 0.25 | -0.000 / +0.101 / 0.004 | 0.953 |
| driver_tauc1 | 24 | STAYS AT C1 24 | -0.112 | -0.199 | 0.589 | 1.53 / 0.26 | 0.97 / 0.24 | +0.002 / +0.203 / 0.005 | 0.924 |


Full per-draw numbers (the runner's dev_Cx, the dense dev, dip depth/position, velocity moments, median |k|, τ or s_M,
match history): `results/armb_pdyn_c9/table.csv` / `table.md`; curves in the unit `.npz` files.

## 7. Summary (numbers only)
C9 does not reproduce: every variant (smooth / fine / raw; 144 matched draws, 72 null, 24 zero-drift, 24 scale-only)
reads STAYS AT C1 on 21/24 matrices (C_lag[1] mean −0.07 vs C1 −0.07 vs real −0.25; dev_Clag vs C1 median
0.10–0.12, vs real 1.14–1.36; matched draws differ from their zero-drift companions by ≤ 0.02 on C_lag[1]); on M0s1
L0 O and L2 O every C9 draw AND the zero-drift / scale-only companions read REPRODUCES (the real curve is within the
dense tolerance of C1 on those two matrices), and on M0s1 L5 K one matched seed of three variants reads REPRODUCES
(dev vs real 0.9–1.0). The planted A = 50 drift fires OVERSHOOTS on 24/24 (C_lag[1] +0.28, dip filled). The C1-driver with τ_v ≤ 10 steps reproduces:
τ_v = 10 on 45/48 draws (A0 21/24, 3 OVERSHOOTS; M0s1 24/24), τ_v = 5 on 44/48, τ_v = 2 on 42/48, τ_v = 0 (DBM) on
40/48; τ_v = 20 splits (27 REPRODUCES / 14 OVERSHOOTS / 7 STAYS AT C1), τ_v = 40 reads STAYS AT C1 on 29/48 and
τ_v = 80 on 43/48, τ_v = τ_C1 on 48/48. Driver C_lag[1]/C_lag[2] at τ_v = 10: A0 −0.153/−0.151 (real −0.225/−0.094,
C1 +0.009/−0.221), M0s1 −0.243/−0.127 (real −0.265/−0.120, C1 −0.140/−0.193); at τ_v = 2: A0 −0.226/−0.100, M0s1
−0.291/−0.089. Median |k| at τ_v = 5–10: A0 0.73–0.72 (real 0.68, C1 0.63), M0s1 0.63–0.62 (real 0.585, C1 0.58);
velocity excess kurtosis at τ_v = 5–10: 0.13–0.16 (real 0.36 / 0.26, C1 0.09). Driver vrms/target 0.87–0.99 per draw
(low-sided; §1), 0.94–0.97 group means (τ_v ≤ 80).
