# Parametric spectral dynamics (AdamW vs Muon) — pre-registration. SEALED at commit, before any real spectrum is read.

Source of the predictions and controls: Will's addendum (2026-10-01, doc 7Pr3SrJVDs8MyGayyBc2tq), folded into
`PARAMETRIC_DYNAMICS_PLAN.md`; pipeline and calibrators sealed in 6a28aff (`pdyn_m2.py`, `pdyn_m3.py`, `pdyn_calib.py`,
`verify_pdyn.py`, `PDYN_PIPELINE_NOTES.md`). This file fixes what is read as evidence, what is provisional, and the words.

## 1. Data and scope
- **Phase 1 (this seal):** the banked B4 extraction of A0, A1, A2, M0s1, M0s2 (+ A0r as the between-run floor pair), fp64
  singular values (`sig_M`), per-head σ, Frobenius norm from the spectrum, top-32 vectors (`U32_M`, `V32_M`) for M3 only.
  **No bulk-vector statistic of any Arm B run is read** (split-sample rule; M3 uses the top-16 only).
- Windows: W1 = [0, 500) (warmup, 10-step cadence) and W2 = [500, 3000] (25-step), analysed separately, never pooled;
  the extension range (every 100 past 3000) is a third window W3, descriptive only.
- Phase 2 (pilots, per-step σ + M4) and phase 3 (production) are sealed by their own amendments when designed.

## 2. Measurements (as in the addendum; estimator settings fixed by phase 0)
- M1 fp64 σ trajectories + ‖W‖_F per matrix per checkpoint (from the bank).
- M2 bulk parametric statistics: top-16 stripped BEFORE unfolding; per-checkpoint kde(32) unfolding on the band
  [0.10, 0.90) of the remaining index range; local ⟨v²⟩ (cubic in band index); uneven-Δt finite differences; velocity
  distribution (skew, excess kurtosis, KS vs Gaussian), C(x) and C_lag, curvature |k| median and ZD fits.
- M3 edge dynamics: top-16, sign-aligned, Hungarian matching, Davis–Kahan rule (gap_mult = 2, overlap_min = 0.5), events
  with min gap, time, mixing angle, ambiguous fraction; exported as a point process.
- M5 context: effective rank, stable rank, outliers above the MP edge (reported with the MP fit's KS; WITHDRAWN where
  the fit fails, as in Stage 3), HTSR α only beside its ESD plot.
- M6 event rates per interval, overlaid on loss and lr.

## 3. Predictions and verdict words (P1–P6 as sealed by Will; the addendum text governs where this summary is terse)
| ID | Claim | Read on | Expected | Falsified by |
|---|---|---|---|---|
| P1 | Bulk local spacing stays β = 1 for both optimizers | existing ⟨r̃⟩/q (ARMB §6) | holds | sustained departure after unfolding, across seeds |
| P2 | Bulk parametric statistics match β = 1 after unfolding + time rescaling | M2 velocity stats + C(x) + curvature, vs C1 AT THE SAME CADENCE | H0 holds for AdamW; Muon uncertain | non-Gaussian velocity, or C(x) / P(k) off the C1 curves beyond calibrator spread |
| P3 | Muon: higher effective rank, fewer/weaker outliers | M5 | holds (replication at this scale) | Muon ≤ AdamW across seeds |
| P4 | Trajectory Gram k* = 1 (Muon) vs 2 (AdamW) | M4 — **phase 2 only** | holds | different modal k*, or no stable gap |
| P5 | Edge crossing rate decays with lr and clusters at loss transitions | M3/M6 — **PROVISIONAL at bank cadence** | holds | flat rate, or no clustering vs shuffled-time null |
| P6 | Inter-event statistics of edge crossings | M3 — **PROVISIONAL at bank cadence** | no prediction; ARS classification with calibrators and its n stated | n/a (exploratory) |

- **Reading rules.** A P2 reading is made ONLY against C1 generated at the SAME cadence and matched x_step (phase 0:
  finite-difference curvature at 10/25-step cadence does not follow the ZD law even for a true β = 1 process); a
  "β = 1 pass" counts only if C2's β = 2 and Poisson witnesses, through the identical unfolding, read as NOT β = 1 at the
  same n (phase 0: separation at ~1000 curvature samples for β = 2, ~500 for Poisson; fewer → NOT RESOLVABLE).
- **Provisional:** at the bank's 10/25-step cadence, curvature tails and edge-crossing events may be aliased (phase 0:
  25-step loses ~83% of the curvature tail at the assumed rate). Phase-1 readings of P5/P6 and of the curvature part of
  P2 carry the word PROVISIONAL and are superseded by the pilot, whatever they say.
- **Floors.** C4 = fp32 round-trip re-estimation (measurement noise; phase 0: 3e-6 of a step). Between-run comparisons
  (AdamW vs Muon) are read against the A0 vs A0r divergence at the same step (one draw, n = 1).
- **Vocabulary:** HOLDS / FAILS (vs the stated falsifier) / NOT RESOLVABLE (n below the discrimination size) /
  PROVISIONAL (cadence) / DESCRIPTIVE (W3, M5 context, anything not in the table).
- **Multiplicity:** the primary endpoints are P2 (velocity Gaussianity + C(x) on W2, AdamW A0 and Muon M0s1) and P3;
  everything else is exploratory and labelled so. Per-layer/per-type tables are reported, not counted as verdicts.

## 4. Controls that must run and be shown to fail where they should, before any real result is read
C1 (positive, same cadence and x_step), C2 (β = 2 and Poisson through the identical pipeline), C3 (shuffled order:
C(x) collapses, P5 clustering vanishes), C4 (fp32 round-trip floor), C5 (sign flips: M3 bit-identical), C8 (ambiguous
matches reported; results stable when excluded). C6 and C7 wait for the pilot (dense reference; frozen-gradient run).
All six phase-1 controls are exercised by `verify_pdyn.py` (PASS 10-02; red path fires); C8 is reported per arm.

## 5. Cadence rule for phase 2 (declared now, filled by phase 1's estimate and the pilot's measurement)
Production interval = the largest interval with < 0.1 expected edge crossings per interval, from the PILOT's measured
mean crossing time; phase 1's estimate is a prior only and may not set the production cadence.

## 6. Deliverables
`armb/pdyn_phase1.py` (runner over the bank; committed before it runs), `results/armb_pdyn_phase1/*`,
`armb/PDYN_FINDINGS.md` (numbers with their words; nulls as nulls; provisional tags carried through).
