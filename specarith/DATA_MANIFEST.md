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

`sessionK/maass_level1_partial.csv` (tracked): 600 forms, idx 0–599, r ∈ [9.53369526, 98.76496727]; sym0 = even
(266), sym1 = odd (334) per `sessionK/SESSION_K_CONTINUATION_FINDINGS.md` Run 1. Source: LMFDB `maass_rigor`
level 1 (Booker–Strömbergsson certified). Completeness gate passed for r < 100 (Weyl 599.8 vs 599); the even sector
is incomplete above r ≈ 100 (`sessionK/SESSION_K_FINDINGS.md` §3), so Phase 6 G1 is capped at r < 100.
