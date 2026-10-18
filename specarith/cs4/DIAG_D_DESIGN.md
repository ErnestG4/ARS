# Diagnostic D — scale dependence of (B)'s count cumulants (round 55; EXPLORATORY, NO VERDICT)

**Status:** committed before anything below is run (round 55). Nothing here changes route (a)'s or (A)'s verdict, or
(B)'s sealed FAIL. D asks one question: is (B)'s between-file heterogeneity (χ² 282.7 on 3, ROUTE_A_FINDINGS §9) the
signature of slow arithmetic fluctuation in the zeros' count statistics, or does it point to the model terms or a
pipeline defect?

## Data (all at L = 3, the sealed (B) window)
- **Zeros, F5** (the four sealed files): window-count sequences built by the sealed read's own path
  (`followup_sealread.sequence`: md5 against the pins before decoding, Platt decode, exact-θ unfolding, `followup_read.seq_B`).
  Saved as `.npy` on spot (not committed; their sha256 recorded).
- **CUE null, F5 geometry:** the 200 calibration count sequences per F5 file (`results/followup_calsamp/seq/B_*`, md5s
  in `results/followup_calsamp_md5.txt`), and the four F5 dry-run stand-ins decoded by the read's path
  (`results/followup_dryrun_synth`). Both are concatenated CUE_1000 matrices (333 windows each), as the calibration.
- **Zeros, descriptive controls:** F4 (three files, read under (A)) and F3 (five files, read under route (a)), window
  counts at L = 3 by the same path. No prediction is used for them; descriptive only.

## D1 — k₃ by sub-block scale
- **Scales:** for a file with W windows, b_j = ⌊W/2^j⌋ windows for j = 1, 2, … while b_j ≥ 100 (100 windows = 300
  unfolded units, the sealed bootstrap block). K_j = 2^j contiguous, non-overlapping sub-blocks from the file's start;
  the remainder (< 2^j windows) is dropped.
- **Per sub-block i:** k₃,i (the k-statistic, as the read) and its within-block SE_i, by the moving-block bootstrap of
  `followup_read.boot_k3` with block length min(100, ⌊b_j/10⌋) windows and B = 200 (seeds [20261018, 55, file index, j, i]).
- **Per scale:** V_j = the sample variance of the k₃,i (K_j − 1 degrees of freedom; χ² 95% interval reported);
  S_j = mean of SE_i²; the **excess ratio R_j = V_j/S_j**; the absolute excess E_j = V_j − S_j; for F5 also
  √max(E_j, 0)/|Δκ₃,f| in μ units.
- **Trend:** τ = least-squares slope of log R_j on log₂ b_j over all scales of the file.
- **CUE null:** the same R_j and τ for each of the 200 calibration replicates of the file (and the stand-in), giving
  per-scale percentiles (50, 95, 99) of R_j and the distribution of τ.

## D2 — the second-order analogue
The same scales, sub-blocks, bootstrap and statistics for k₂,i, the unbiased variance of the counts (κ₂(3), the
number variance at L = 3), with its own CUE null. Purpose: whether the pair-level count statistic carries the same slow
component, at a smaller relative size (excess relative to κ₂ compared with excess relative to |Δκ₃|).

## Reading, declared in advance (round 55; exploratory, no verdict)
For each F5 file, against that file's CUE null (200 replicates):
- **Scale-growing excess** — the zeros' τ above the null's 99th percentile **and** R_j above the null's 95th
  percentile at the largest scale with K_j ≥ 8 (j = 3, so the variance has ≥ 7 degrees of freedom).
- **Flat excess** — R_j above the null's 99th percentile at the smallest scales (j_max, j_max − 1) with τ inside the
  null's 1–99% range.
- **None** — R_j inside the null's 99% range at every scale, and τ inside its 1–99% range.
- **Reading:** scale-growing excess in the zeros but not in CUE (stand-in inside its null) supports the
  slow-arithmetic-fluctuation hypothesis; a flat excess, or none, points toward the model terms or a pipeline defect.
  Any other combination is reported as is. F4/F3 are reported beside F5 with the same statistics, descriptively.

## Pipeline checks (alongside D1)
- **Halves:** for each F5 file, k₃ (and μ̂ with the sealed b_f, Δκ₃,f) for each half of the windows, with its
  bootstrap SE (block 100 windows, B = 200). This is D1's j = 1 row, reported explicitly.
- **Zero-count completeness**, as for route (a): for every decoded file (F5, F4, F3), the number of zeros against the
  θ count N̄(t₁) − N̄(t₀) (exact θ, the pre-data n_f); require |count − θ count| ≤ 2, and report the difference.

## D3 — theory (primary sources)
From primary sources (Selberg; Tsang; later work on moments of S(t) and of S(t + h) − S(t)), the size and period of
the off-diagonal (nearly resonant prime) contributions to the third moment of S(t + h) − S(t) over a finite t-window,
and an estimate of whether they reach about 0.007 in k₃ at L = 3 over a window of 2·10⁶ in height. Every cited result
is checked against its source; a claim that cannot be sourced is labelled as our own derivation or dropped.

## Outputs
`diag_d.py` (this design as code), `results/diag_d/` (per-file, per-scale tables for D1/D2 with their nulls, the halves,
the completeness check), `DIAG_D_RESULTS.md` (descriptive write-up), D3 notes in `DIAG_D_THEORY.md`.
