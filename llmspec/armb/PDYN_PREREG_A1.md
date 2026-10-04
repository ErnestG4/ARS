# PDYN_PREREG — Amendment A1 — SEALED by Will 2026-10-04 ("SEAL with change"; the change is A1.2's arm split below)

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

## A1.2 P2 re-read on W2, components
- **Arms (Will's change at the seal):** PRIMARY = the arms NOT used in the exploratory τ_v sweep: **A1, A2 (AdamW,
  τ_v = 10) and M0s2, M0s3 (Muon, τ_v = 20)**. The sweep (`pdyn_c9.py`, PDYN_C9_NOTES.md; results/armb_pdyn_c9/) used
  **A0 and M0s1 only** (layers 0/2/5, types Q/K/O/MLP_OUT) — confirmed from its defaults and outputs. **A0 and M0s1 are
  SECONDARY, labelled post-sweep and non-blind.** M0s3 (banked by the Q4EXT extraction, ≤ 3000) is read through the same
  runner; it had no phase-1 read.
- Primary word per arm; the arm-level words are reported per optimizer (AdamW: A1, A2; Muon: M0s2, M0s3), never pooled
  into one cross-optimizer verdict.
1. velocity Gaussianity — unchanged test;
2. C(x): dev vs C1′ (same tolerance rule as the runner: calibrator spread);
3. curvature median |k| between C1′ and the β = 2′ witness: unchanged rule, PROVISIONAL at bank cadence;
4. **NEW — velocity excess kurtosis** vs C1′: tolerance = 3 × the C1′ draw spread (declared; phase-1 real values 0.36 /
   0.26 vs controls ≤ 0.16, so this component is EXPECTED to fail and is the open residual).
- P2 word per arm = HOLDS iff 1–3 hold on ≥ 30/36 matrices (the runner's majority rule) AND the witnesses separate at the real n;
  component 4 is reported beside the word, never folds into it in this amendment.

## A1.3 What is not changed
Unfolding, band, windows, M3/M5/M6, P3–P6 words, the PROVISIONAL tags, the cadence rule (§5), and the sealed phase-1
result (which stands as "FAILS vs C1 as sealed" in PDYN_FINDINGS §2; the re-read is reported as a separate row).

## A1.4 Cost
CPU only (this box or spot): 2 arms × 36 matrices × (C1′ + 2 witnesses) × 2 draws ≈ the phase-1 control time (~1 h).

## A1.5 Implementation (committed before it runs)
`armb/pdyn_a1.py`: the sealed phase-1 runner (`pdyn_phase1.analyse_unit`, `verdict_p2`, every statistic and tolerance)
UNCHANGED, with only its control generator swapped: c1 → β = 1 OU driver (`pdyn_c9.gen_driver`), b2 → the same driver on
complex Gaussian matrices, po → independent levels with the same OU velocity; τ_v fixed per optimizer; the driver scale
s_M matched to the real vrms in ≤ 3 passes (vrms ∝ s_M). W2 only; 2 draws per family. `armb/verify_pdyn_a1.py`
(synthetic, `--redpath`) re-measures the witness separation for the OU family before the re-read.

## A1.6 Known-answer finding, declared BEFORE the real re-read (verify_pdyn_a1.py, 10-04 04:50; CC)
On an OU fake bank (n = 256, the W2 grid, τ_v = 10): a β = 1 OU truth reads HOLDS on 12/12 matrices; a Poisson OU truth
on 0/12 (C(x) fails); the β = 1 truth read against the ORIGINAL smooth-GP controls reads 0/12 (the reference matters —
the phase-1 failure mode reproduced on a known β = 1 truth). **But a β = 2 OU truth reads HOLDS on 9/12 matrices
(runner-majority word HOLDS):** at the bank's 25-step cadence the curvature medians of the C1′ and β = 2′ witnesses
differ by only ~5 % (≈ 1.38 vs 1.42, against draw-to-draw scatter ≈ 0.02), the β = 2 truth falls between them, and the
C(x) and velocity components are β-blind. The per-matrix "witnesses separated" check (2 draws per family) passes on
12/12 regardless — it certifies that the witness DRAWS differ, not that a β = 2 truth is classified as such.
**Declared scope of every A1 P2 word (no threshold changed):** a HOLDS means "consistent with a β-ensemble driven by
optimiser-like velocity memory; Poisson-like independent levels and the smooth-GP (long-memory) reference excluded"; it
does NOT distinguish β = 1 from β = 2 at bank cadence. That discrimination is NOT RESOLVABLE here and waits for the
per-step pilot (phase 2), as the sealed PROVISIONAL tag on curvature already anticipated.

## A1.7 Amendment history note (10-04, Will)
- **Rule mismatch, recorded:** A1.2 states "HOLDS iff 1–3 hold on ≥ 30/36 matrices (the runner's majority rule)". The
  runner's arm-level rule (`aggregate_p2`) is different: each component must hold on more than half of the resolvable
  matrices. Both were computed on the re-read and **gave the same word in every arm** (FAILS ×6), so the mismatch did not
  affect any result. Any future use states which rule it applies.
- **Will's reading of the re-read (10-04):** P2 cannot speak to the universality class at bank cadence (A1.6), so neither
  its failures nor a pass say anything about β. What it shows, descriptively, is a difference in how the optimisers move
  the spectrum: Muon's motion matches the simple optimiser-memory reference everywhere except C(x)'s sparse bins; AdamW's
  does not (velocity kurtosis and curvature too), consistent with Adam's per-coordinate normalisation making updates
  burstier.
- **Last PDYN step, then P2 amendments stop (Will):** one post-hoc known-answer check of the full-bin C(x) statistic on
  realistic shapes (A1.8). After it, P2 is not amended further: it cannot discriminate β at this cadence, so more rounds
  would chase a statistic rather than a question.

## A1.8 Post-hoc known answer for the full-bin C(x) statistic (designed 10-04 AFTER the A1 read; labelled POST HOC)
- **Truth:** per real matrix (arms M0s1, M0s2, M0s3; A2 as the AdamW contrast whose dense C(x) also failed), a β = 1 OU
  draw at the arm's τ_v and real shape, warped onto that matrix's OWN time-mean density (log-quantile function of the
  real W2 spectra, rank-smoothed at the unfolding's bandwidth h = 32: pdyn_c9's fixed-map 'zero' construction, no
  drift), scale matched to the real window's vrms (≤ 3 passes). Written as a fake bank in the runner's format and read by
  `pdyn_a1.py` unchanged (OU controls at the same τ_v). `armb/pdyn_a1_ka.py`, committed before it runs.
- **Reading (declared now):** h_KA = fraction of the known-answer matrices whose C(x) component HOLDS (full-bin, as sealed).
  h_KA ≤ 0.5 → the full-bin statistic is **NOT LICENSED on realistic shapes** (it fails a known β = 1 OU truth): Muon's
  C(x) failure is attributable to the STATISTIC. h_KA ≥ 0.8 → the statistic is licensed on realistic shapes: Muon's
  failure is the DYNAMICS. Otherwise INCONCLUSIVE. Per arm, with the real arm's C(x) hold fraction beside it.

