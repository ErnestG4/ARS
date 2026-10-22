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

## Result (`results/r73/R73_SUMMARY.json`; the per-block estimates stay on spot)
**Revised zeros/long.** Geometric mean over files, with the range in brackets:

| statistic | G = 3,000 old → revised | G = 10,000 old → revised | concatenated variant (3,000 / 10,000) |
|---|---|---|---|
| route (a) | 0.58 → **0.54** (0.38–0.74) | 0.43 → **0.40** (0.29–0.60) | 0.56 / 0.42 |
| (A) | 0.56 → **0.53** (0.44–0.63) | 0.51 → **0.44** (0.33–0.56) | 0.55 / 0.47 |
| corrected (B) | 0.19 → **0.18** (0.14–0.22) | 0.18 → **0.16** (0.13–0.23) | 0.18 / 0.16 |

- **"Changed," by the declared criterion:** the per-file differences exceed the revised SE in most G ≥ 3,000 cells.
  The revision lowers the ratios by 3–13%.
- **The revised values now match the file-sized stitched calibration's ratios almost exactly:** 0.55 / 0.40, 0.53 /
  0.44 and 0.18 / 0.16 (L6 table). That is what "stitching irrelevant" plus "short-segment bias removed" predicts.

**Checks.**
- **The mean-subtraction bias, shown directly:** W_within/W_glob = 0.997, 0.99, 0.97 and 0.89–0.90 at G = 300, 1,000,
  3,000 and 10,000. That is 1 − 1/k for k = 333, 100, 33 and 10 blocks per sequence.
- **Known answer at small G:**
  - **route (a):** W_glob/W_MBB = 0.99–1.01 at G = 300 and 0.99–1.04 at 1,000, with |z| ≤ 1.2. It passes.
  - **(A):** 7% of the 300-level block fits fail, 1,114–1,239 of 16,650; 13–14 fail at 1,000 and none at 3,000 and
    above. At G = 300 and 1,000 one file reads z = +3.3 and +3.0. **This check does not pass for (A) at small G.** The
    cause is the block fits on short blocks, which is irrelevant at G ≥ 3,000, where nothing fails.
  - **corrected (B):** W_glob/W_MBB = 1.08–1.11 at G = 300 (z +3.1 to +4.7) and 1.01–1.05 at 1,000. **It does not
    pass at G = 300.**
    - The reading: k₃ subtracts each block's own count mean, which adds O(1/W) variance on a 300-unit block. That is
      the block estimator's small-block term, and it scales as 1/G: about 10% at 300 and about 3% at 1,000, so about
      1% at 3,000 and 0.3% at 10⁴.
    - So the revised (B) values at G ≥ 3,000 may sit up to about 1% low from this term. That is inside their SE.
- **Cross-check:** the concatenated variant (single MBB at n = 5·10⁶) over W_glob is 0.77–1.06 per file at G = 10⁴.
  - The per-file spread is wider than the concatenated value's expected ~6% sampling error. It is not interpreted.
  - The geometric means agree: zeros/long 0.42 against 0.40, 0.47 against 0.44, and 0.16 against 0.16.

**Applied** (round 73: "update the L6 table and findings §11 if they change"):
- the L6 table gains zeros/long rows, marked ‡ at G ≥ 3,000;
- findings §11, OPEN_LEADS L6 and the release-notes draft take the revised G ≥ 3,000 values;
- G = 300 and 1,000 keep the per-sequence MBB values (G/n ≤ 0.01).
