# Grid-anchoring sibling sweep — specarith (round 56)

The "anchoring/origin" defect family: a windowed or gridded statistic whose window origin is tied to the data, read
against a prediction or calibrator that is phase-averaged. Found in (B) (`cs4/DIAG_D_RESULTS.md`). The legacy sweep and
the ledger rows are in ARSv2 (Task 0b, the new family there); this file covers specarith.

**Red path (round 56):** the same data at grid offsets u ∈ [0, 1) must give the same statistic within SE.

**Grep:** `floor(`, `//`, `np.floor`, `bincount`, `histogram`, window/centre loops over `specarith/**/*.py` (28 candidate
lines), each read and classified below.

| site | statistic | grid anchored to | origin-shift result | status |
|---|---|---|---|---|
| `cs4/followup_read.seq_B` (+ `followup_calsamp`, `followup_reps`, `followup_cuen` for CUE) | (B): k₃ of counts in integer windows L = 3 | x = N̄(t₀) on the zeros (a fixed lattice phase per file); random rotation per matrix in the CUE null | **RED**: k₃(u) moves by up to 5× within a file over u ∈ [0, 3) (`results/diag_d/phaseavg`); k₂, k₃ track cos 2πφ (r = −0.99, −0.88) | **FLAGGED** — (B)'s sealed FAIL attributed to it; corrected (B) queued |
| `ph2s2/tapered.window_sums` (Stage 2, and L4's `cs4/diag_f1_wincorr.py` on the same sums) | Gaussian-tapered pair sums, width b ≥ 100, centres 3b apart from the first zero | the file's first zero | **within SE**: 8 offsets u = k/8 move pooled ĝ_B by 1·10⁻⁵ against a CI half-width of 0.0351; ≤ 0.004 SE per file (`ph2s2/results/s2_offsets`, d942657d) | clear |
| `ph2s/s1lib.zero_windows`, `ph2r2/longbase.py` (Stage 1, long baseline) | pair-sum SD growth over blocks of consecutive levels | level index (each block starts at a zero), in the zeros and in the mapped-GUE null alike | invariant to a position offset by construction (blocks are defined by index, not position) | clear (by construction) |
| `ph2r2` R₂ (`r2prep`, `r2run`, `g0b.contributions`) | pair statistic of differences x_j − x_i | none (differences only) | invariant by construction | clear |
| route (a) and (A) (`route_a_read`, `followup_fit`, `followup_read.seq_A`) | nearest / next-nearest spacings | none (spacings only) | invariant by construction | clear |
| `ph2r2/checks/a3_drift_removal_check.py` | places levels on the N̄ lattice (`nbar_inv(arange(...) + 0.5)`) for a drift check | a construction, not a statistic of data on a grid | not applicable | clear |
| `ph1/rfwire.py`, `ph6/candidates.py`, `ph6/detection_floor.py`, `ph2/preread.py` | histograms of integer labels / root bracketing / tolerance search | not a positional grid on data | not applicable | clear |

**Lesson carried forward:** before sealing a statistic of counts or positions on a grid, ask what the grid is anchored to
in the real data and whether the null reproduces that anchoring; otherwise the estimator must average over it (round
56; engine v2 gate G1b in ARSv2).
