# Stage 1b dip-test licence — amendment (DRAFT for Will's seal, 2026-10-03; NOT in force until he seals it)

**Trigger.** OLMO_PREMISE (OLMO_PREMISE_FINDINGS §1) found a confusable class the Stage 1b licence battery
(`seals/stage1b_dip_calibration.json`) did not contain: Gaussian 128 × 2048 blocks whose rows are scaled by a real head's
OWN row norms read MULTIMODAL in 20.7 % (all levels) / 7.8 % (trimmed) of draws, against the licence's ≤ 2 %. The battery's
nearest stand-in (i.i.d. lognormal σ, and lognormal row norms) reads 0 %: it is the substrate's two-scale row structure
that fires, not heterogeneity per se. The Stage 1b licence was therefore issued against an incomplete battery.

## A. Battery additions (computed before any re-read)
1. `own_rownorm` — for each model × revision × type, Gaussian blocks scaled by the row norms of randomly drawn real heads
   of that same model/revision/type (2000 draws), both trims.
2. `own_rownorm_deadrows_removed` — the same with rows below 0.1 × median set to the median.
3. `gain_folded` (OLMo only, folded readings) — Gaussian blocks scaled by real heads' q_norm/k_norm gains.
f0 per model/type = max(0.01, worst FPR over the sealed battery and these classes), per trim; the licence (every class
≤ 0.02) is re-evaluated per model/type and the result is recorded in a NEW calibration file
(`seals/stage1b_dip_calibration_v2.json`); the sealed v1 file is not edited.

## B. Consequences, declared before re-reading
- **OLMo stage-1 end (memo row 3):** already re-read by OLMO_PREMISE → NOT LICENSED (row-norm confusable). No further
  read needed; v2 records it.
- **Pythia (null):** adding confusables can only raise f0, so the Pythia "none" stays "none" under v2 — but it remains a
  WEAK null (lit v2 item 4: the uniform-calibrated dip is conservative). v2 reports Pythia's own-row-norm FPR for the
  record; no re-wording unless the class reads > 0.02 there, in which case the Pythia row says "NULL under a rule that
  is NOT LICENSED for Pythia's row structure" (i.e. not informative).
- **Arm A and any future dip reading:** must use v2.

## C. Candidate replacement (a method change; for Will to choose, not in this amendment)
A per-head matched null: is a head's singular spectrum MORE multimodal than Gaussian blocks with its own row norms
(and own gains, for folded)? Statistic: the head's dip p against its own matched-null distribution of dip statistics
(e.g. 200 draws per head); fraction of heads beyond the 1 % matched quantile vs a binomial floor at 0.01. This asks the
right question ("more peaked than its own row structure explains") instead of licensing one global rule.

## D. Cost
A: one CPU pass on spot, minutes per model (2000 SVDs of 128 × 2048 per class). C (if chosen): ~200 SVDs per head ×
256 heads per model ≈ 50 k SVDs, ~30 min CPU per model.
