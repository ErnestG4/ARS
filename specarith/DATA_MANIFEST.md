# specarith — input data manifest

Inputs are gitignored (`odlyzko_zeros*.txt`, `/data/*`); they live in the main checkout's `data/`
(`/home/combust/fmexplorer/criticality_tool/data/`). Every runner pins these hashes and fails closed on a mismatch.

## ζ zeros (A. M. Odlyzko, https://www-users.cse.umn.edu/~odlyzko/zeta_tables/)

| file | upstream | lines | range of γ | stated accuracy | sha256 |
|---|---|---|---|---|---|
| `data/odlyzko_zeros1.txt` | `zeros1` | 100,000 | 14.134725142 … 74920.827498994 | within 3·10⁻⁹ | `3436c916a7878261ac183fd7b9448c9a4736b8bbccf1356874a6ce1788541632` |
| `data/odlyzko_zeros6.txt` | `zeros6` (Last-Modified 2006-12-09) | 2,001,052 | 14.134725142 … 1132490.658714411 | within 4·10⁻⁹ | `2ef7b752c2f17405222e670a61098250c8e4e09047f823f41e2b41a7b378e7c6` |

Verified 2026-10-07: both local files (dated 2026-05-07) were re-downloaded from upstream and are byte-identical
(same sha256, same length 1,800,000 / 36,018,936 bytes). The first 100,000 lines of `zeros6` are byte-identical to
`zeros1`. The `zeros1` hash also matches `data/README.md`. Accuracy figures are quoted from the upstream index page.

Note for programme Phase 2: the upstream page lists high-height tables at 10¹², 10²¹ and 10²² (10⁴ zeros each).
There is no 10²³ table on it, although the programme brief lists one.

## Maass eigenvalues, PSL(2,ℤ) (Session K)

`sessionK/maass_level1_partial.csv` (tracked; sha256 `c6134f0b16f2d96031204790075fe91f46b6d83fec39fee0c5f5c10d3c3a93a2`):
600 forms, idx 0–599, r ∈ [9.53369526, 98.76496727]; sym0 = even (266, last r 98.75949735), sym1 = odd (334, last
r 98.76496727) per `sessionK/SESSION_K_CONTINUATION_FINDINGS.md` Run 1. Source: LMFDB `maass_rigor` level 1
(Booker–Strömbergsson certified).

**Completeness (corrected 2026-10-07): complete up to r_max = 98.765, NOT to r = 100.** Parity Weyl laws (Booker–
Strömbergsson 2007 via `ph6/lit/selberg.md` item 5) against the list: T = 60: even 79 vs 78.8, odd 111 vs 110.7;
T = 90: 214 vs 213.9, 272 vs 272.6; T = 98.765: 266 vs 266.5, 334 vs 333.8; T = 100: 266 vs 274.4, 334 vs 342.9
(≈ 17 forms in (98.765, 100] are not in the list — Session K kept the clean block idx 0–599). Session K's
"Weyl 599.8 vs 599" was evaluated at r_max, which shows nothing is missing BELOW r_max. So Phase 6 G1's window
must be supported in r ≤ 98.76 (truncation bound declared at r_max), unless idx 600–616 are fetched.
The even sector is additionally incomplete above r ≈ 100 (`sessionK/SESSION_K_FINDINGS.md` §3).
