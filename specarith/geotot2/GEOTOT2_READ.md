# GEO-TOT2 read (2026-10-28): prime powers in (10⁶, 10⁸] against size-matched primes

Seal: `GEOTOT2_SEAL.md`, tag `geotot2-seal` (a2332f46), stamped 08:13 UTC, Bitcoin block 973525 (08:20:13 UTC), verified
on two explorers (3b0d291a) before the read. Enumeration of the 5,805 q on spot (10.86 core-h, 0.871× the model; the
first launch at 01:14 PDT was stopped unread when ARSv2 jobs started alongside, and relaunched at 11:35 on free cores);
file and per-array sha256 committed before any statistic (67ba81dc). Read twice in separate processes from the hashed
file: `results/enum/READ1.json` = `READ2.json` byte-identical (logs too). φ(q) of every target = q − q/p.

## (A) Zero excess at the 74 non-foldable odd prime powers — PASS at N = 3, 4, 5
| N | mean excess | SE | fold-size/2 | verdict |
|---|---|---|---|---|
| 3 | −0.0039 | 0.0099 | 0.0122 | PASS (zero excess) |
| 4 | +0.0017 | 0.0026 | 0.0043 | PASS (zero excess) |
| 5 | +0.0006 | 0.0014 | 0.0022 | PASS (zero excess) |

All three powered (SE below half the fold size). The Bourgain–Kontorovich local factor's prediction — no excess at a
prime power that cannot fold — holds at the resolution of half a fold.

## (B) R_N = mean excess / mean fold over the 1,061 prime squares
| | R | SE | H_fold (R = 1) | H_seen (R_seen ± SE_seen) | sealed reading |
|---|---|---|---|---|---|
| N = 3 | **1.485** | 0.105 | inconsistent (4.6 SE above) | consistent (0.871 ± 0.291; band ± 0.62) | displacement |
| N = 4 | **0.589** | 0.079 | inconsistent (5.2 SE below) | consistent (0.273 ± 0.227; band ± 0.48) | displacement |
| N = 5 | 1.036 | 0.070 | consistent | consistent (0.707 ± 0.183) | unpowered/unexplained |
| pooled | 0.970 | 0.062 | consistent | inconsistent (0.601 ± 0.166; band ± 0.35) | pure folding |

Mean excess 0.0362 / 0.0050 / 0.0045 against mean fold 0.0243 / 0.0086 / 0.0043 (N = 3 / 4 / 5); pooled weights
0.20 / 0.35 / 0.45.

**What the sealed labels mean here (interpretation, not a change of verdict):**
- **N = 4: the seen deficit replicates on fresh squares.** The excess is 0.59 of the fold count, 5.2 SE below pure
  folding, in the direction seen at q ≤ 10⁶ (0.27), though smaller. Something offsets part of the fold keys at N = 4.
- **N = 3 is labelled "displacement" only because H_seen's band is wide** (its SE 0.29 makes the band ±0.62, the
  limit the seal stated: N = 3 cannot separate the hypotheses). The value itself lies *above* both hypotheses: the excess
  is 1.49 times the fold count, 4.6 SE above 1. That is the opposite of a deficit: prime squares carry more extra keys at
  N = 3 than Niederreiter's single fold accounts for (Step 0 §3 noted a wider near-palindrome census; not tested here).
- **The pooled "pure folding" averages opposite deviations** (N = 3 above 1, N = 4 below 1, N = 5 at 1). The per-N
  results are not homogeneous, so the pooled value near 1 does not show that folding alone explains the excess at every
  N. The pooled label stands as sealed; it should not be quoted without the per-N rows.
- N = 5 sits between the hypotheses, as the power analysis expected (P(pure folding | H_fold) was 0.07).

## Descriptive: the 26 squares of higher prime powers (excess / fold, never in a verdict)
Squares of 2^j carry by far the largest excess (2²⁰: 0.74 against a fold of 0.067 at N = 3; 2²², 2²⁴, 2²⁶: 0.57, 0.51,
0.33 at N = 3), consistent with Step 0's note that q = m·r² with 2 ≤ m ≤ N + 1 admits several fold families (a power
of 2 is m·r² for several m). The others (p⁴, p⁶, 3¹⁴, 3¹⁶, 5¹⁰, 7⁸) scatter around their fold counts. Full rows in
`results/enum/READ1.json` (`even_pp_descriptive`).

## Cost
Enumeration 10.86 spot core-h (sealed model 12.46; 0.871×). Read: seconds.
