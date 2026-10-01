# OLMo plan (1), step 0: premise-and-endpoint check — pre-registration DRAFT for Will's seal (2026-10-01)

**Status: DRAFT, not sealed. No new OLMo tensor is read until Will seals this file (commit = seal).** The layout-vs-run
checks Will asked for first are DONE (olmo_main_provenance.py: `main` is a different run; the lineage endpoint is
`stage2-ingredient3-step23852-tokens51B`, ingredients 1–2 are seed replicates of the same anneal). This file covers the
next two things in his order: the gain-folded dip tests and the row-norm confusable, plus the dead-row depth.

## 0. Question
Is the stage-1-end OLMo Q multimodality (13.3% of heads, dead rows excluded; STAGE1_FINDINGS, row 3) a property of the
effective query map, and does it survive the lineage's own anneal — or is it an artefact of (a) analysing raw W_Q without
the full-width QK-norm gain, or (b) row-norm heterogeneity within heads?

## 1. Objects (all streamed; nothing banked beyond per-head singular values, row norms and the gain)
- Model `allenai/OLMo-2-0425-1B`. Revisions: `stage1-step1907359-tokens4001B` (stage-1 end; already banked raw),
  `stage2-ingredient{1,2,3}-step23852-tokens51B` (NEW), `stage1-step0-tokens0B` (G0 sanity, already banked).
- Per layer: `q_proj.weight` (2048×2048), `k_proj.weight`, `q_norm.weight` and `k_norm.weight` (2048 each; the QK-norm is
  RMSNorm over the full 2048-dim query with a per-channel gain, applied AFTER the projection: q = g ⊙ RMSNorm(W_Q x)).
- **Gain-folded object:** the effective linear map up to a per-token scalar is diag(g)·W_Q (rows scaled by g). Per head h:
  rows h·128 … h·128+127 of diag(g)·W_Q. Both RAW and FOLDED per-head blocks are analysed; the folded one is primary.
- Per head: 128 singular values (fp64), the 128 row norms (raw and folded), the head's 128 gain entries.

## 2. Tests (the Stage 1b machinery, unchanged: `stage1b_dip.py`, licence `seals/stage1b_dip_calibration.json`)
- T1 **Folded vs raw at stage-1 end.** Fraction of Q heads MULTIMODAL (dip p < 0.01) on (i) raw, (ii) folded, each over
  all 128 levels and over levels ≥ 0.1 × median (the dead-row trim, as sealed). Same for K.
- T2 **Row-norm confusable (new licence class, run BEFORE reading T1's folded numbers).** For each head: W = D_r·G with
  G Gaussian (128×2048) and D_r the head's OWN row norms (raw, and folded), 2000 draws over heads drawn at random; plus
  the same with a planted dead-row cluster (the head's own number of rows below 0.1 × median set to their actual norms).
  FPR of the dip rule on this class at both trims. Licence rule as sealed: the class must have FPR ≤ 0.02 for the dip
  reading to stand; otherwise the stage-1-end rate is NOT LICENSED against row-norm heterogeneity and is re-scoped.
- T3 **Per-head predictor.** Among heads MULTIMODAL on raw: does row-norm bimodality (dip p < 0.01 on the 128 row norms)
  predict σ-multimodality? Report the 2×2 table (σ-multimodal × rownorm-bimodal) with Fisher's exact p; and the same on
  folded. A strong association means the "peaks" are row-scale structure.
- T4 **Endpoint.** T1 on the three ingredient finals: fraction per ingredient (the 3 are seed replicates of one anneal,
  so their spread is the seed noise), raw and folded, both trims. Compared to stage-1 end with the sealed floor rule
  (SHOWS PEAKS iff fraction ≥ 0.10 AND binomial P < 1e-3 at f0 = max(0.01, worst confusable FPR incl. T2's class)).
- T5 **Dead-row depth.** For every row with norm < 0.1 × median at stage-1 end: its norm, its gain entry, and the bound
  weight decay alone allows over stage 1 (∏(1 − 0.1·lr_t) ≈ e^{−50} on the config's schedule); report the ratio
  observed/bound. Descriptive; the ~1e-28 vs ~1e-22 discrepancy (critique S5) is either resolved or named.

## 3. Reading rule (declared now; the verdict vocabulary of FINDINGS_MEMO)
- If T2 FPR > 0.02 at the trim used: the stage-1-end 13.3% is **NOT LICENSED (row-norm confusable)**; row 3 is re-worded;
  T1/T4 are reported as DESCRIPTIVE only.
- Else, if the folded rate at stage-1 end is < 0.10 (sub-floor) while raw is ≥ 0.10: **GAUGE ARTEFACT** — the peaks live in
  the un-normalised rows, not in the effective map; row 3 becomes "raw-W_Q only".
- Else (folded ≥ floor, licensed): the multimodality is a property of the effective query map: **STANDS (folded)**.
  Then T4: if all three ingredient finals read sub-floor (folded): **FADES THROUGH THE LINEAGE'S ANNEAL** (with the
  declared caveat: stage 2 changes LR AND data mix together; no cause is attributed); if ≥ 2 of 3 read ≥ floor:
  **SURVIVES**; otherwise **INCONCLUSIVE (seed-split)**.
- T3 is reported beside the verdict, never as one. T5 is descriptive.
- Nothing here licenses the trajectory (plan 1 proper); that is a separate pre-registration with per-checkpoint power.

## 4. Known-answer and red path (before the seal is used)
- The dip pipeline on a gain-folded GAUSSIAN block with the stage-1-end gains must read UNIMODAL (FPR ≤ 0.02): the gain
  alone must not manufacture peaks. On a planted two-component head (d = 0.3, sd = 0.03, w = 0.5, the sealed power
  cell) folded with the same gains it must read MULTIMODAL. Both run under checkrun and pasted into the seal commit.

## 5. Cost
Three new checkpoints × 16 layers × (Q, K) 2048² streamed (≈ 1.6 GB) + gains; SVD per head on CPU (or the lean box);
minutes. T2: 2000 draws × 128×2048 SVDs ≈ 20 min CPU (spot).

## 6. Not in scope
The stage-1 trajectory; any `main` reading (different run); any claim about the data mix vs the schedule.
