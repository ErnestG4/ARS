# Brief — Gratings-divergence substrate study

**Status:** brief + compute (Will authorized "check, brief, and compute"). Existing-data
analysis, no generation. **Date:** 2026-05-21.

## Frame

The agreement formalization found `|I.5q − I.5|` (q-banded vs matched plain-NNS KS-to-GUE)
is near-zero everywhere EXCEPT a ~3% tail of pvc-11 **drifting-gratings** units (max 0.09),
absent from spontaneous/movie conditions. Conjecture (Will): q-banding picks up
**stimulus-phase-correlated rhythmicity** (the grating drift at TF=6.25 Hz) that plain-NNS
washes out — so the divergence is a *rhythmicity/stimulus-coupling detector*, not proxy error.
If so, `|I.5q − I.5|` is a candidate new landscape coordinate orthogonal to universality class.

## Goals

- **G1 (primary).** Does the divergence `D = I.5q − I.5` track **F1/F0** (`f1_f0_pref`, the
  canonical simple/complex modulation ratio = degree of linear stimulus-locking) across all
  210 gratings cells? Predict: |D| rises with F1/F0.
- **G2 (control — load-bearing).** Does the F1/F0 relationship survive controlling for
  **firing rate** and event count? (ARS rate-regime lesson: divergence could track rate, not
  locking.) Partial correlation / rate-stratified.
- **G3 (secondary).** Does |D| also track OSI / DSI (tuning sharpness)?
- **G4 (exploratory).** Per-q localization: do high-D cells concentrate their GUE-distance
  excess in specific `ks_gue_per_q` bands, and do those map to the stimulus TF period?
  Flagged exploratory — the q↔frequency map is non-trivial.

## Acceptance / verdict vocabulary

- **STIMULUS_LOCKING_CONFIRMED** — |D|↔F1/F0 Spearman p<0.05 AND survives rate-control (G2).
- **RATE_CONFOUNDED** — F1/F0 correlation vanishes under rate-control.
- **NULL** — no F1/F0 relationship.
- G4: **LOCALIZED** vs **DIFFUSE** (exploratory, non-gating).

## Methodological commitments

- Spearman primary (robust to the small high-D tail); report signed D and |D|.
- Rate-control is mandatory before claiming a locking effect (rate-regime lesson).
- Cross-condition anchor: movie/spontaneous show 0% divergence — the contrast that grounds
  any gratings effect; report it.
- G4 is exploratory; it does not gate the G1/G2 verdict.

## Out of scope

- New event-train generation; Allen/other substrates; deriving the q↔frequency map rigorously
  (that's the math-path, separate). This is one substrate, existing data.
