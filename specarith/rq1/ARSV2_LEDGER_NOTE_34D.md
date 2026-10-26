# Ledger note for ARSv2 (from the specarith session, round 86; for Will to hand over; ARSv2 itself is not touched)

**Defect: Phase 34d's RW-variance verdicts (ℤ[i], ℤ[ω]) rest on half-sample means.**

**What.**
- `phase34d/run_amendments.py` and `run_x_rate_scan.py` report σ²(K, X)/(N/K) as the mean over 50 random
  half-samples: `rng.choice(N_full, N_full/2, replace=False)`.
- Sampling exactly half without replacement maps the full-sample ratio r to ½·r + ½·(1 − 1/K)·N/(N − 1), i.e.
  ≈ (r + 1)/2 at 34d's K (≥ 30).
- Every reading is therefore pulled halfway toward 1, the comparison value (RW's saturation level and the Poisson
  value).
- The quoted ± is the half-sample spread, not the full-sample statistic's sampling error.

**Reproduced.**
- At X = 10⁷, β = 0.65 (ℤ[i]), the full-sample ratio is 0.79 (exact estimator) to 0.84 (34d's grid estimator). The
  mapping gives 0.90–0.92, against 34d's reported 0.923.
- Positive control on CUE_200 (K = 10): full 0.033, half-sample mean 0.471, exact mapping 0.469
  (`specarith/rq1/results/SIBLING_CHECK.json`).

**Affected verdicts (bannered in place in `PHASE34D_FINDINGS.md`, 2026-10-25):**
- RW_REPLICATED_AT_DEEP_LAYER_AT_X=10⁸_IN_β=0.65_CELL;
- "within 1σ of the RW asymptote" (Gaussian 0.984 ± 0.025; Eisenstein 1.000 ± 0.022);
- "rigidity regime matches RW within 1σ".

These are **not established.** The qualitative X-trend survives. For scale, the full-sample ℤ[i] value at x = 10⁸,
β = 0.66 is 0.88 (`specarith/rq1/results/GATES.json`, G3), not 0.98.

**Sibling search (specarith):** no site averages a variance or count ratio over random subsamples of the data. There
are six sites, each with a reproducing test (`specarith/rq1/sibling_subsample_check.py`).

**Requests for ARSv2 (Will's list):**
- (1) Mark any ARSv2 ledger entry or gallery item that imports Phase 34d's σ² verdicts or the memory summary
  "RW_SHAPE_CONFIRMED … within 1σ" as not established.
- (2) Run the same sibling search in ARSv2's code: any ratio or variance averaged over random subsamples,
  bootstrap half-splits, or subsample-replicates of points rather than of whole units.
- (3) Note the general rule. Thinning a point process maps any count-variance ratio toward the Poisson value. A
  subsample replicate is a different statistic, not an error bar for the full-sample one.
