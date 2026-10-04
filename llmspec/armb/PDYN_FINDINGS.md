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

## 7. Amendment A1 re-read (sealed by Will 10-04; `pdyn_a1.py`, verifier `verify_pdyn_a1.py` CHECKRUN PASS; run 04:57–06:13;
## results/armb_pdyn_a1/{summary,words}.json, cx_dense_diagnostic.json)
Reference: C1′ = β = 1 OU driver with τ_v FIXED (AdamW 10, Muon 20); β = 2′ and Poisson′ witnesses on the same driver;
the sealed runner and verdict_p2 unchanged. Scope declared before the read (A1.6): a HOLDS could not have separated
β = 1 from β = 2 at bank cadence.

| arm | role | A1 word (≥ 30/36) | matrices HOLD | runner-majority word | velocity / C(x) / curvature hold (of 36) | comp. 4 ex-kurt fails (real vs C1′ medians) |
|---|---|---|---|---|---|---|
| A1 | PRIMARY (AdamW) | **FAILS** | 0 | FAILS | 3 / 7 / 1 | 36/36 (1.01 vs 0.12) |
| A2 | PRIMARY (AdamW) | **FAILS** | 0 | FAILS | 21 / 0 / 12 | 36/36 (0.99 vs 0.45) |
| M0s2 | PRIMARY (Muon) | **FAILS** | 6 | FAILS | 36 / 6 / 35 | 24/36 (0.25 vs 0.11) |
| M0s3 | PRIMARY (Muon) | **FAILS** | 5 | FAILS | 36 / 5 / 36 | 23/36 (0.26 vs 0.11) |
| A0 | secondary, post-sweep | FAILS | 0 | FAILS | 34 / 1 / 24 | 32/36 (0.37 vs 0.13) |
| M0s1 | secondary, post-sweep | FAILS | 6 | FAILS | 36 / 6 / 36 | 28/36 (0.29 vs 0.11) |

- **Sealed word: P2 FAILS vs C1′ in all four primary arms, both optimizers** (and in both secondary arms). The two word
  rules agree everywhere (the ≥ 30/36 count and the runner's majority), so the rule mismatch flagged in A1 does not bite.
- **What carries it (DESCRIPTIVE, post-read; results/armb_pdyn_a1/cx_dense_diagnostic.json):** the C(x) component. Its
  sealed statistic (max over every bin with ≥ 10 pairs, x ≤ 2) reads a median 1.6–2.0 tolerance units in every arm, with
  the maximum at small separations (x ≈ 0.15–0.65). Restricted to dense bins (≥ 1000 pairs on both curves, the
  restriction PDYN_C9_NOTES declared before its own run because the runner's dev_Cx is set by sparse small-x bins): the
  Muon arms match C1′ on 100 % of matrices (median 0.48–0.52), A0 on 92 %, A1 on 75 %, **A2 on 0 % (median 1.84)**.
  C_lag (dev 0.75–0.94) is within tolerance in the median everywhere.
- **Muon:** velocity Gaussianity HOLDS 36/36 and curvature HOLDS 35–36/36 in all three Muon runs; the FAILS rests on the
  sparse-bin C(x) statistic. **AdamW:** A1 and A2 also fail velocity (excess kurtosis ≈ 1.0 against C1′ 0.1–0.5) and
  curvature (A1: median |k| 0.77 vs C1′ 0.95, below even the Poisson witness 0.85), so AdamW's failure is not only the
  C(x) statistic.
- **Component 4 (velocity excess kurtosis vs 3 × the C1′ draw spread), beside the word:** fails 36/36 in both AdamW
  primaries (real ≈ 1.0) and 23–24/36 in the Muon primaries (real ≈ 0.25 vs 0.11): the expected open residual, larger
  under AdamW.
- **Reading.** The optimiser-memory OU reference does what the sweep suggested on its own terms (dense C(x), C_lag,
  Muon's velocity and curvature), but the SEALED P2 statistic does not license it: P2 FAILS vs C1′ as sealed. Two things
  stand between this and an interpretation, both for Will: (i) the full-bin dev_Cx has no known-answer licence on
  REALISTIC shapes — the OU fake bank (n = 256, smooth densities) read dev_Cx 0.14–0.58 for a β = 1 truth, so whether a
  β = 1 OU truth with the real arms' densities would also fail the sparse bins is untested (lesson: calibrator bias =
  the finding); (ii) the AdamW velocity-kurtosis and curvature departures are not explained by the C(x) statistic and
  are the open residual A1 anticipated (component 4).
- **Will's reading (10-04):** P2 cannot speak to the universality class here (A1.6); the result is a descriptive
  difference in how the optimisers move the spectrum — Muon's motion matches the optimiser-memory reference except for
  C(x)'s sparse bins, AdamW's does not, consistent with Adam's per-coordinate normalisation making updates burstier.
  One post-hoc known-answer check of the full-bin C(x) statistic follows (A1.8, §8); after it P2 is not amended again.

## 8. A1.8 — POST-HOC known answer for the full-bin C(x) statistic on realistic shapes (designed after the A1 read;
## `pdyn_a1_ka.py`, committed before it ran; results/armb_pdyn_a1_ka/{ka_verdict.json, build_meta.json, read/summary.json})
Truth per real matrix: a β = 1 OU draw at the arm's τ_v, warped onto that matrix's OWN time-mean W2 density (fixed map, no
drift), vrms matched to the real window; read by the unchanged A1 runner and OU controls. Rule declared in A1.8.

| arm | known β = 1 truth: C(x) holds | real arm: C(x) holds | word | KA P2 (≥ 30/36) | KA comp. 4 fails | real comp. 4 fails |
|---|---|---|---|---|---|---|
| M0s1 | 6/36 (0.17) | 6/36 | **STATISTIC** | FAILS (6) | 9/36 | 28/36 |
| M0s2 | 7/36 (0.19) | 6/36 | **STATISTIC** | FAILS (7) | 12/36 | 24/36 |
| M0s3 | 11/36 (0.31) | 5/36 | **STATISTIC** | FAILS (11) | 9/36 | 23/36 |
| A2 (AdamW contrast) | 35/36 (0.97) | 0/36 | **DYNAMICS** | HOLDS (34) | 18/36 | 36/36 |

- **Muon:** a known β = 1 OU process carrying the real Muon densities fails the sealed full-bin C(x) statistic as often as
  the real Muon runs do. The full-bin statistic is NOT LICENSED on Muon's realistic shapes, so **Muon's one P2 failure is
  the statistic, not the dynamics**: Muon's spectral motion is consistent with the optimiser-memory reference on every
  component the instrument can read.
- **AdamW (A2):** the same construction on A2's densities passes 35/36 while the real A2 passes 0/36, so the statistic is
  licensed there and **A2's C(x) failure is the dynamics**, alongside its velocity-kurtosis and curvature departures
  (§7). Consistent with Will's reading: Adam's per-coordinate normalisation moves the spectrum more burstily than a
  shared-memory OU process.
- Component 4 (kurtosis) is partly the statistic too: the known-answer truths fail it 9–18/36, the real arms 23–36/36.
- **P2 is closed here (Will, 10-04).** It cannot discriminate β at bank cadence (A1.6); after this step it is not amended
  further. What stands, descriptively: Muon's spectral motion ≈ optimiser-memory OU (instrument-limited on C(x)); AdamW's
  departs from it in velocity statistics, curvature and C(x).
