# PDYN_PREREG — Amendment A1 (DRAFT for Will's seal; not in force until he says so)

**Trigger.** Phase 1 read P2 as FAILS vs the sealed C1 (PDYN_FINDINGS §2). The attribution controls (§6, 3a7cc46) showed
the departure is reproduced by a β = 1 process with short velocity memory and not by density drift: the phase-0 C1
family's velocity correlation time (τ ≈ 580 steps, chosen to reproduce the Simons–Altshuler curve in the smooth limit)
is the wrong reference for optimiser-driven motion. This amendment replaces the reference family BEFORE any re-read.

## A1.1 New positive control C1′ (replaces C1 for P2 from this amendment on)
- The β = 1 process of `pdyn_c9.py` ("driver"): W(t) = W(0) + ∫ M, with M an Ornstein–Uhlenbeck-filtered β = 1 increment
  of velocity time constant τ_v, norm-projected, vrms-matched to the real arm after the fact (3 passes; the match is
  low-sided by up to 13 %, reported per draw), run at the real cadence and the real shape.
- **τ_v is FIXED here, not fitted:** τ_v = 1/(1 − β₁) of the optimiser's first-moment EMA — **AdamW: β₁ = 0.9 → τ_v = 10
  steps; Muon: momentum 0.95 → τ_v = 20 steps.** The Muon value reproduced only 27/48 draws in the exploratory sweep
  (τ_v = 10 reproduced 24/24 for M0s1), so the Muon prediction CAN fail; if it fails, that is reported, and no τ_v is
  re-fitted. The sweep values are banked (results/armb_pdyn_c9) and may be shown as context, never as the reference.
- C2 witnesses (β = 2, Poisson) are rebuilt with the SAME OU driver (same τ_v) so that the discrimination is of β, not of
  memory; the phase-0 separation sizes are re-measured for the new family before the re-read (verify_pdyn amendment).

## A1.2 P2 re-read on W2 (A0 and M0s1 primary; the other arms secondary), components
1. velocity Gaussianity — unchanged test;
2. C(x): dev vs C1′ (same tolerance rule as the runner: calibrator spread);
3. curvature median |k| between C1′ and the β = 2′ witness: unchanged rule, PROVISIONAL at bank cadence;
4. **NEW — velocity excess kurtosis** vs C1′: tolerance = 3 × the C1′ draw spread (declared; phase-1 real values 0.36 /
   0.26 vs controls ≤ 0.16, so this component is EXPECTED to fail and is the open residual).
- P2 word = HOLDS iff 1–3 hold on ≥ 30/36 matrices (the runner's majority rule) AND the witnesses separate at the real n;
  component 4 is reported beside the word, never folds into it in this amendment.

## A1.3 What is not changed
Unfolding, band, windows, M3/M5/M6, P3–P6 words, the PROVISIONAL tags, the cadence rule (§5), and the sealed phase-1
result (which stands as "FAILS vs C1 as sealed" in PDYN_FINDINGS §2; the re-read is reported as a separate row).

## A1.4 Cost
CPU only (this box or spot): 2 arms × 36 matrices × (C1′ + 2 witnesses) × 2 draws ≈ the phase-1 control time (~1 h).
