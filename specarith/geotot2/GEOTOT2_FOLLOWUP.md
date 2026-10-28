# GEO-TOT2 follow-up (Will, 2026-10-28) — DESCRIPTIVE, POST HOC, no seal

Script `geotot2_followup.py` (committed before it ran), output `results/FOLLOWUP.json`; data: the sealed read's hashed
enumeration (fresh) and GEO-TOT1's per-q table (seen). Bootstrap SEs over squares, 10,000 resamples, seed 20261030.
The sealed verdicts stand as recorded in `GEOTOT2_READ.md`.

## 1. R against q (fresh prime squares, 4 bins in log₁₀ q)
| log₁₀ q | n | R₃ | R₄ | R₅ |
|---|---|---|---|---|
| (seen, 5.0–6.0) | 103 | 0.871 ± 0.292 | 0.273 ± 0.226 | 0.707 ± 0.184 |
| 6.0–6.5 | 107 | 0.897 ± 0.327 | 0.387 ± 0.223 | 0.838 ± 0.203 |
| 6.5–7.0 | 171 | 1.362 ± 0.265 | 0.636 ± 0.182 | 1.026 ± 0.151 |
| 7.0–7.5 | 293 | 1.323 ± 0.179 | 0.574 ± 0.150 | 1.025 ± 0.123 |
| 7.5–8.0 | 490 | 1.931 ± 0.145 | 0.687 ± 0.106 | 1.193 ± 0.097 |

Weighted least squares, R = a + b·log₁₀ q:
- **N = 3: R rises with q.** Slope +0.67 ± 0.20 per decade on the 4 fresh bins (χ² 1.9/2); +0.52 ± 0.13 with the seen
  point (χ² 3.0/3). A constant fails (χ² 13.0/3).
- **N = 4: no significant trend.** +0.15 ± 0.14 (with seen +0.18 ± 0.10); a constant fits (χ² 1.6/3). R stays below 1 in
  every bin (0.39 → 0.69).
- **N = 5: no significant trend.** +0.21 ± 0.13 (with seen +0.22 ± 0.09, 2.5σ); a constant fits (χ² 3.1/3).
The fit is post hoc with 4–5 points; the N = 3 rise is the only trend a constant cannot absorb.

## 2. Where the surplus and the deficit sit: fold against non-fold keys
Every Niederreiter fold key of each square was re-checked by its own canonical CF (denominator q, lowest terms, all
quotients ≤ N): all are counted E_N keys (F_N ≤ c_N everywhere). So c_N = F_N + (non-fold keys), and the non-fold excess
(c_N − F_N)·s(q) − matched-prime mean equals excess − fold, square by square.

| | N = 3 non-fold excess | N = 4 | N = 5 |
|---|---|---|---|
| seen (103) | −0.0076 ± 0.0172 | **−0.0192 ± 0.0060** | −0.0046 ± 0.0029 |
| fresh (1,061) | **+0.0118 ± 0.0025** | **−0.0035 ± 0.0007** | +0.0002 ± 0.0003 |

**Both effects sit in the non-fold keys.**
- **N = 4:** prime squares have fewer non-fold bounded keys than matched primes. The deficit is 3.2 SE (seen) and
  5.0 SE (fresh). The fold keys come on top of a reduced base.
- **N = 3 (fresh):** prime squares have more non-fold bounded keys than matched primes, 4.7 SE. This surplus is
  absent in the seen range (−0.008 ± 0.017).
- **N = 5:** no non-fold effect in either range.

**The N = 3 excess on its own (new result, not a confirmation of displacement):** on fresh prime squares in
(10⁶, 10⁸], R₃ = 1.49 ± 0.10. The extra bounded keys are 1.49 times the Niederreiter fold count, and the surplus beyond
the folds (+0.0118 ± 0.0025) lies in non-fold keys. It grows with q across the fresh bins. Its source is not identified;
Step 0's agent pointed to a wider near-palindrome census (untested here).

## 3. Squares of 2^k: fold representations against excess
Representations q = m·r², 1 ≤ m ≤ N + 1, r ≥ 2, for the 26 fresh squares of higher prime powers:
- 2²⁰, 2²², 2²⁴, 2²⁶: **two** (m = 1 and m = 4) at every N = 3, 4, 5.
- All the others (p⁴, p⁶, 3¹⁴, 3¹⁶, 5¹⁰, 7⁸): one (m = 1).

| q | excess / m = 1 fold, N = 3 | N = 4 | N = 5 |
|---|---|---|---|
| 2²⁰ | 11.1 | 7.4 | 5.4 |
| 2²² | 25.0 | 7.6 | 5.7 |
| 2²⁴ | 7.9 | 6.0 | 5.0 |
| 2²⁶ | 17.0 | 12.5 | 13.3 |
| others (median; range) | 1.2 (−13.6 … 5.6) | 1.3 (−3.8 … 4.7) | — |

The 2^k squares carry 5–25 times their m = 1 fold count. A second family (m = 4) would have to be several times larger
than the first for the representation count to explain this. That family's key count was not computed: Step 0's
general-fold construction is an unverified inference. So the 2^k excess is recorded, not attributed. Odd powers of 2
(2²¹, 2²³; m = 2) were excluded from the sealed sets and were not enumerated.
