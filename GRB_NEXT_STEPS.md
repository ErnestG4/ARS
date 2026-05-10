# GRB Phase 21 — decision document

This document records the Phase 21 PoC verdict and the
outcome-conditioned next steps.  See §7.ter.29 in RESULTS.md for
methodology and full per-event data.

## Verdict

**Methodology-only result.  No positive ARS-replicates-published-QPO
finding at the joint-plane resolution.**

Per the Tier 4 verdict map:

  - **Quadrant classification doesn't shift** during published QPO
    windows on any of the four events (GRB 230307A, GRB 200415A,
    GRB 221009A, GRB 211211A).  All four classify uniformly as BL
    throughout prompt and surrounding windows; the cascade-shape /
    transition signature lives at sub-quadrant resolution if it
    exists in the framework's q-range at all.  This is the Phase
    20.5 lesson reproduced on a different domain.

  - **Lightcurve-modulated Poisson surrogate reproduces the
    empirical BL classification** on every event (3 seeds × 4
    events → 12/12 reproductions).  At the joint-plane resolution
    we operated at, the QPO/prompt-window reading is fully
    accounted for by the empirical rate envelope.  No detectable
    timing signature beyond the lightcurve survives this
    falsification.

  - **MGF positive control is partial**: the 836 Hz mode in
    GRB 200415A produces an elevated RF-amplitude at q = 74
    (predicted q = 70.5) on a full-prompt-window scan at
    q_max = 300; the higher-frequency modes (1444 / 2132 / 4250 Hz
    per Castro-Tirado 2021) do not register elevated RF amplitudes
    at their predicted q-bands.

  - **Published QPO frequencies for 230307A (909 Hz) and 200415A's
    2132 Hz mode** fall just above q_max = 30 at the sub-window
    sizes used in Tier 3 (q_target ≈ 31, 41).  The framework's
    q-resolution at our chosen compute budget does not span the
    published claims' frequencies cleanly.

The Phase 21 PoC is a methodology-and-resolution result, not a
positive finding about the published QPO claims.  No outreach is
justified.

## Outcome-conditioned next steps

### What this verdict triggers

**No outreach.**  Per the SESSION-PLAN ground rule: "If negative or
methodological-only: document transferable lessons, no outreach,
move on."  Adria Updike reconnection is deferred until work
supports it.  Bing Zhang / Bin-Bin Zhang outreach is downstream of
that and not in scope.

### Transferable lessons documented for any future use

1. **Lightcurve-modulated Poisson surrogate** as a generic
   falsification tool for cascade-driven photon-counting
   measurements — applies to GRBs, X-ray binaries, AGN flares,
   astrophysical transients.  Implementation in
   `lightcurve_modulated_surrogate.py` is ~50 lines of Python.

2. **Quadrant-resolution coarseness** continues to bite at the
   sub-quadrant signature level.  Phase 20.5 identified this for
   BGP; Phase 21 reproduces it on GRB data.  A finer-resolution
   classifier (rep_med-axis trajectory distance, energy-band
   stratification) would be needed for any positive cascade-shape
   finding.

3. **q-range vs published-QPO-frequency mismatch** is a
   methodology-tuning issue.  The framework's natural detection
   range is q ∈ [2, q_max], which corresponds to particular
   sub-window sizes for each QPO frequency.  For 909 Hz to fall
   at q ≤ 30, sub-windows must be ≤ ~110 ms.  Any future targeted
   QPO replication needs sub-window sizes matched to the QPO
   frequency.

4. **Mechanism-distinctness saturation in gamma photon
   detectors.**  All scintillator + PMT + deadtime detectors
   collapse into a single mechanism equivalence class under the
   §7.ter.26 empirical-distinctness criterion.  Cross-instrument
   GRB agreement is *not* Phase 19-principled — it is one
   mechanism's testimony at multiple vantage points.  Genuinely
   multi-mechanism corroboration requires a different detection
   class (gravitational-wave timing, neutrino timing,
   optical-counterpart photometric timing) — none currently at the
   ms temporal resolution required for QPO verification.  This is
   the calibrated upper bound on what photon-detector panels can
   establish.

5. **Per-instrument deadtime artifact baseline.**  At rate
   ≥ 200 K events/s, scintillator-detector deadtime alone shifts
   the joint-plane classification from BL (Poisson, rep_med ≈ 0.04)
   to TR (Wigner-class, rep_med ≈ 0.45).  Any future joint-plane
   reading on high-rate scintillator data must subtract this
   baseline before non-Poisson structure is reported.

### What's NOT triggered by this verdict

- No expansion to cross-event panel for an ApJ / MNRAS / A&A study.
- No collaboration outreach.
- No methods-only paper at this stage — the methodology lessons
  (1)–(5) above are documented in §7.ter.29 and accessible to any
  future user, but a standalone methods paper would require a
  positive ARS-detects-something result that this PoC does not
  produce.

### Optional follow-ups (not currently justified)

If the verdict is revisited (e.g., on the basis of additional
event panel coverage or a different sub-window resolution):

  - **Targeted 909 Hz replication on GRB 230307A** at q_max = 50
    with 100 ms sub-windows in the published QPO claim window
    (45–47 s post-trigger per Chen 2025).  Compute cost ~30 min
    wall-time.  This would tell us whether the framework's
    classification at the published claim's natural q-range
    distinguishes the claim window from surrounding sub-windows.

  - **SGR 1806-20 RHESSI archival integration** as the
    galactic-MGF ground-truth case.  Currently RHESSI access via
    HEASARC requires additional pipeline work (different file
    format, different trigger archive structure than Fermi GBM).
    Filed for longer-term consideration.

  - **Energy-band stratification** of Phase 21 trajectory analysis.
    The current analysis pools all energy channels; an
    energy-stratified per-(detector, channel-band) trajectory
    would test whether the QPO signal is energy-dependent
    (predicted by the magnetar-central-engine interpretation).

These are documented as candidate refinements; they are not
recommended actions on the basis of the current PoC.

## Methodological notes (independent of verdict)

The Phase 21 deliverables (data, scripts, plots, §7.ter.29
methodology section) are sufficient to reproduce any Phase 21
result starting from public Fermi GBM TTE downloads.  The
framework's reading on bright GRB events is calibrated and
documented; future users applying ARS to GRB-class timing data
have a baseline to start from.

The framework does not produce positive QPO replication on the
events tested; it does produce calibrated null results and a
documented methodology that future GRB applications can build on.
The instrument-as-instrument positioning is preserved: the toolkit
classifies what it can classify, falsifies at the orders it can
falsify, and reports the verdict the data supports.

## Provenance

- Tier 1 raw data: `data/phase21_grb_panel/raw/`
- Tier 1 parsed parquet: `data/phase21_grb_panel/{event}.parquet`
- Tier 1 detector geometry:
  `data/phase21_grb_panel/detector_geometry.parquet`
- Tier 2 calibrators: `data/phase21_calibrators.parquet`
- Tier 3 trajectory: `data/phase21_classification.parquet`
- Tier 3 QPO comparison: `data/phase21_qpo_comparison.parquet`
- Tier 4 falsification: `data/phase21_falsification.parquet`
- Plots: `plots/58_phase21_deadtime.png`,
  `plots/59_phase21_quiescent_baseline.png`,
  `plots/60_phase21_trajectory_per_event.png`,
  `plots/62_phase21_surrogate_survival.png`
- Source: `grb_pipeline.py`, `run_phase21_acquire.py`,
  `run_phase21_calibrators.py`,
  `run_phase21_classification.py`,
  `run_phase21_falsification.py`,
  `lightcurve_modulated_surrogate.py`.
