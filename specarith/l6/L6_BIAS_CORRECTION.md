# L6 correction: the long-baseline block variance without within-sequence mean subtraction (round 73; DESCRIPTIVE; committed before computing)

**Why.** The L6 long-baseline variance W_long(G) = SE_boot(G)²·n was a moving-block bootstrap within each 10⁵-level
sequence. Every bootstrap is centred on its own sequence. At G = 10⁴ that leaves about 10 blocks per sequence, so the
estimate loses roughly a block's worth of variance, a bias of order G/n. The concatenation variant (n = 5·10⁶) sits
4–24% above it at G = 10⁴ (§13). The zeros' files have n ≈ 5·10⁶, so their own G/n ≤ 0.002 and the zeros' side is
unaffected. Only the long-baseline denominator of zeros/long is in question.

## Revised estimator (primary): disjoint blocks about the global mean, with an explicit correction
- For each long CUE sequence r (50), each statistic and file geometry, and each G in {300, 1000, 3000, 10000}:
  - cut the sequence into k = ⌊10⁵/G⌋ disjoint blocks, of G spacings for route (a) and (A) and G unfolded units for
    corrected (B);
  - fit the identical estimator on each block, with no bootstrap (`route_a_read.fit_file`, `followup_read.fit_file_A`,
    `b2_est.zeros_stats` → μ = (k̄₃ − κ₃^sine)/Δκ₃).
- Pool all M = 50·k block estimates μ̂_b.
  - **W_glob(G) = G·Σ_b (μ̂_b − μ̄)²/(M − 1)**, with μ̄ the global mean over all M blocks.
  - The divisor M − 1 is the explicit bias correction for estimating the one global mean.
  - This is the MBB's target without its centring: G·Var(block mean) = Var(Σ_block φ)/G, the same W as §13.
- **SE** from the 50 sequences: SD over r of each sequence's mean of G·(μ̂_b − μ̄)², divided by √50.
- **Revised Var_long** at a file's geometry = W_glob/n_file, and **revised zeros/long = Var_zeros/that**.
  Var_zeros is the read record's SE(G)², unchanged.

## Checks reported with it
- **Known answer at small G:** at G = 300 and 1,000 the MBB's G/n bias is ≤ 1% (G/n ≤ 0.01). W_glob should agree with
  the stored per-sequence MBB W there, within combined SE.
  - Disagreement would point to the block fits themselves, for example nonlinearity of a fit on a short block. The
    revised values would then be reported with that caveat.
- **The bias, shown directly:** the same blocks with each sequence's own mean subtracted (divisor k, no correction),
  W_within. The ratio W_within/W_glob shows the mean-subtraction bias at each G.
- **Cross-check:** the concatenation variant (one MBB at n = 5·10⁶, already in `compare.json`) beside W_glob.

## Reading (declared)
- The revised zeros/long ratios at G = 3,000 and 10,000 are reported next to the old ones (§13).
- **"Changed"** means some file's revised ratio differs from its old one by more than the revised ratio's SE, at G =
  3,000 or 10,000.
- **If they change:**
  - findings §11, OPEN_LEADS L6 and the release-notes draft take the revised numbers;
  - the L6 table gains the zeros/long rows (revised). It currently holds only zeros/stitched-calibration, whose
    file-sized MBB has G/n ≤ 0.002 and is unaffected.
- **Otherwise** the record says unchanged.

Code: `round73.py blocks R OUT` (per sequence) and `round73.py summary OUT` → `results/r73/`.
