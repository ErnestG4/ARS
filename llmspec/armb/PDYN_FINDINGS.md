# Parametric spectral dynamics — phase 1 findings (banked Arm B, 2026-10-02)

Pre-registration: `PDYN_PREREG.md` (4405874). Pipeline: 6a28aff; runner `pdyn_phase1.py` (ea47dad, committed before the
run). Data: the sealed B4 bank (fp64 σ, top-32 vectors) of A0, A1, A2, M0s1, M0s2, A0r; 216 (arm, layer, type) units,
windows W1 = [0, 500) at 10-step cadence (warmup), W2 = [500, 3000] at 25-step; run 05:45–07:05 PDT, 0 errors.
Results: `results/armb_pdyn_phase1/` (summary.json; per-arm m1/m2/m3/m5/m6/controls.json; figs/). Words are the sealed
vocabulary, read mechanically by `verdict()`; nothing here was re-thresholded after the run.

## 1. Controls (ran before the real reading; all as required)
- C1 (smooth β = 1 at the real cadence, vrms-matched: x_step_c1 = x_step_real to 3 digits), C2 (β = 2, Poisson) through the
  identical unfolding: witnesses separated on every matrix (median |k|: C1 0.64, β2 0.77–0.78, Poisson 0.23; z_c1_b2 ≈ 15,
  z_c1_po ≈ 130 at n_k ≈ 40 000 per matrix on W2). C3 shuffled order: C(x) collapsed on 97–100 % of matrices. C4 fp32
  round-trip floor: 3e-5 of a step (spectrum). C5 sign flips: M3 bit-identical on every matrix. C8 ambiguous fractions
  reported per matrix (events below).
- Real x_step on W2 ≈ 0.44–0.53 mean level spacings per 25-step checkpoint (A0 0.49, M0s1 0.53): the bank cadence is
  coarse relative to the motion, as phase 0 warned; W1 (10-step) x_step ≈ 0.06–0.16.

## 2. Primary endpoints (as sealed)
| Endpoint | Word | Numbers |
|---|---|---|
| **P2 on W2, A0 (AdamW)** | **FAILS** (36/36 matrices) | velocity HOLDS 34/36 (skew 0.04, excess kurtosis 0.4–0.5, KS 0.014); **C(x) FAILS 36/36** (dev_Cx ≈ 5 calibrator SDs); curvature FAILS 21/36 (median |k| 0.72 vs C1 0.64–0.65, β2 0.77–0.78; PROVISIONAL) |
| **P2 on W2, M0s1 (Muon)** | **FAILS** (36/36) | velocity HOLDS 36/36 (ex. kurtosis 0.37); **C(x) FAILS 36/36**; curvature HOLDS 33/36 (median |k| 0.63; PROVISIONAL) |
| **P3 (A0 vs M0s1)** | **HOLDS** | effective rank: Muon above AdamW beyond the A0/A0r floor on 28/36 matrices (8 ≤); top-16 mass lower under Muon on 29/36; "fewer MP outliers" FAILS but on 5 MP-valid matrices only (the MP fit is WITHDRAWN elsewhere, as in Stage 3). Replication at 70M of the known Muon direction. |
- Secondary (same reading): A1, A2, M0s2 and A0r all FAIL P2 on W2 for the same reason (C(x) 0/36 HOLDS everywhere);
  A2 also fails velocity Gaussianity on W2 (13/36 hold; excess kurtosis ≈ 1.0, the arm with the shortest warmup and the
  dense grid) and A1 holds velocity on only 3/36. W1 (warmup, x_step ≈ 0.1) FAILS everywhere on every component.
  A0 and A0r agree to the third digit on every aggregate (C_lag1 −0.207 ± 0.085 both; |k| 0.719 / 0.716): the reading
  is reproducible across the paired runs.
- **What the C(x) failure looks like** (figs `*_W2_*_Cx.png`): the trained velocity autocorrelation has the β = 1 SHAPE —
  a dip at x ≈ 0.5–0.7 and decay to 0 by x ≈ 1.5 — but its dip is SHALLOWER than C1's (A0 Q: ≈ −0.10 vs C1 ≈ −0.20,
  β2 ≈ −0.35); Poisson (+0.5 → 0, no dip) and the shuffle (−2, meaningless) are far away. The curvature tail, by
  contrast, is slightly HEAVIER than β = 1 on AdamW (0.72 vs 0.64, toward β = 2) and at β = 1 on Muon. So the
  departure is not a β shift: the two statistics move in opposite directions.

## 3. Provisional and descriptive (as sealed)
- **P5 FAILS (PROVISIONAL at bank cadence)** for every arm and window: ~2 000–4 000 top-16 "events" per arm per window
  (A0 W2 2 230), rate vs lr Spearman ρ −0.24 (p 0.07) on W1, no clustering at loss changes vs a shuffled-time null
  (z 0.3). With x_step ≈ 0.5 per checkpoint, consecutive-checkpoint matching cannot resolve individual crossings; the
  event list is what phase 0 predicted a coarse grid would produce. Superseded by the pilot, whatever it says.
- **P6 DESCRIPTIVE** (no prediction; no class word is given at this cadence).
- **W3** (every 100 steps, A1 only): DESCRIPTIVE (FAILS) on the same component; the other arms' W3 are NOT RESOLVABLE
  (no bank past 3000 yet).
- P1 NOT COMPUTED HERE (read on ARMB_FINDINGS §6); P4 NOT READ (phase 2).

## 4. Attribution: OPEN (declared; the sealed word is FAILS, the cause is not established)
The P2 failure is on the velocity autocorrelation, reproducible across arms and across the paired runs, with Gaussian
velocities and a β-ambiguous curvature tail. Candidate causes, none tested:
1. **Non-stationary drift inside the window** (addendum warning 7/11): a slow deterministic deformation of the band's
   density adds positively correlated velocity to the index-tracked unfolded levels, filling in the repulsion dip. C1 has
   no drift. Nearest confusable → **C9: C1 plus a slow smooth density drift matched to the real ‖W‖_F and band-edge
   motion**, through the identical pipeline. If C9 reproduces the shallow dip, the FAIL is drift, not dynamics.
2. **The C1 family's time structure.** C1 is a smooth Gaussian-process β = 1 family whose correlation time was set in
   phase 0 to reproduce the Simons–Altshuler curve; Adam/Muon updates carry their own momentum time scales (β₁ 0.9,
   β₂ 0.95 EMAs ≈ 10–20 steps, below the 25-step cadence). A driver-matched C1 variant (velocity OU time ≈ the
   optimiser's) is the second confusable.
3. **Genuinely non-generic motion** (the addendum's "most interesting outcome"): levels repel in position (static β = 1)
   but their motion is less anticorrelated than DBM — e.g. a fraction of the bulk moving coherently (function?). Only
   admissible after 1 and 2 are excluded.
The pilot (per-step σ) removes the cadence caveat but not 1 or 2; C9 and the driver-matched C1 are CPU work and come
first.

## 5. What this does and does not change
- FINDINGS_MEMO: no row changes. A new row for P2 waits on §4's controls; P3 is a replication of known Muon behaviour at
  70M and is recorded here only.
- The production cadence (PDYN_PREREG §5) is NOT set by this phase: x_step ≈ 0.5 per 25 steps says the pilot needs
  per-step sampling at least through the warmup, as the addendum asked.

## 6. Attribution controls (2026-10-02, `pdyn_c9.py`, `PDYN_C9_NOTES.md`, `results/armb_pdyn_c9/`; 24 units: A0 and
M0s1 × layers 0/2/5 × Q/K/O/MLP_OUT on W2; identical sealed pipeline; C1 draws regenerated bit-identically)
- **C9 — β = 1 motion + the real arms' slow density drift: DOES NOT reproduce the C(x) departure.** The fitted drift is
  large in absolute terms (‖W‖_F ×1.1–1.9 on A0, ×1.5–4.0 on M0s1; the 90 % band edge moves +18…+832 spacings over W2),
  but after the sealed per-checkpoint unfolding only 0.03–0.7 spacings rms survive (velocity 0.4–7 % of the real vrms),
  and the warped C1 stays at C1 on 43/48 draws (C_lag1 −0.07 vs C1 −0.07 vs real −0.25). A planted drift 50× larger
  fills the dip on 24/24 (the control can fire; verifier (ii), red path flips it). Candidate 1 of §4 is EXCLUDED.
- **Driver-matched β = 1 (OU-momentum velocity, τ_v swept): REPRODUCES.** With τ_v = 5–10 steps the control matches the
  real C(x) on 44–45/48 draws (τ_v = 10: M0s1 24/24, A0 21/24 + 3 overshoot) and the curvature median too (A0 0.72 vs
  real 0.68, C1 0.63; M0s1 0.62 vs 0.585, C1 0.58); the white-velocity DBM limit (τ_v → 0) reproduces 40/48; τ_v = 80
  and the phase-0 smooth family (τ_C1 ≈ 580 steps) stay at C1 (48/48). Lag values at τ_v = 10: A0 −0.153/−0.151 vs
  real −0.225/−0.094 (C1 +0.009/−0.221); M0s1 −0.243/−0.127 vs real −0.265/−0.120 (C1 −0.140/−0.193). Residuals: the
  real velocity excess kurtosis (0.36 / 0.26) is above every control's (≤ 0.16); the driver's vrms match is low-sided
  (0.87–0.99). Candidate 2 of §4 is SUPPORTED: the phase-0 C1 family's long velocity memory (chosen to reproduce the
  Simons–Altshuler curve in the smooth limit) is the wrong reference for optimiser-driven motion, whose velocity memory
  is of order the momentum time scale and below the 25-step cadence.
- **Reading.** The sealed word for P2 stays **FAILS vs C1 as sealed**. What the controls establish is the attribution:
  the departure is reproduced by a β = 1 process with short velocity memory and NOT by density drift; a pass against the
  driver-matched family would be a post-hoc re-threshold and is NOT claimed. Candidate 3 (non-generic motion) is not
  needed to explain C(x) and curvature at this cadence; the unexplained residual is the velocity kurtosis.
- **Proposed amendment (for Will to seal, PDYN_PREREG A1):** redefine C1 as the OU-driven β = 1 family with τ_v fixed
  BEFORE the re-read from the optimiser's momentum (Adam β₁ = 0.9 → τ_v = 10 steps; Muon momentum 0.95 → 20 steps —
  note τ_v = 20 reproduced only 27/48 here, so the Muon value is a prediction that can fail), then re-read P2 on W2 with
  the velocity-kurtosis residual as an added component with its own tolerance from the calibrator spread. The per-step
  pilot then tests the same family at a cadence below τ_v.
