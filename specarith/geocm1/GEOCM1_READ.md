# GEO-CM1 read (2026-10-27/28): sealed clauses on a = 1 … 10

Seal: `GEOCM1_SEAL.md` §11, tag `geocm1-seal`, OpenTimestamps receipt attested in Bitcoin block 973466 (2026-10-27
22:48:51 UTC) and verified on two explorers (682b0116) before any a ≥ 3 path ran. Pins re-checked at the read:
`geocm1.py` c42634a2…cbc5, `geocm1_analyze.py` 424f8686…8246, `results/GATES.json` 9019471c…ea81 (all equal).

## Procedure (as sealed)
- `geocm1.py path aN` for a = 3 … 10, twice, in two separate process sets (8 processes, NUMBA_NUM_THREADS=2, nice), into
  `results/READ1/` and `results/READ2/`. **All 8 pairs `cmp` byte-identical.**
- `geocm1_analyze.py read` on READ1 with GATES.json and GATE_a1/a2 copied in; also on READ2: the two `ANALYSIS.json`
  are byte-identical.

## Sealed clauses
| Clause | Powered at | Result | Verdict |
|---|---|---|---|
| P1 f(a) increasing | pairs (1,2) … (4,5) | SUPPORT at all four (each step > 2 SE) | **PASS on the powered pairs**; (5,6) … (9,10) UNPOWERED |
| P2 f(a) < 1.5 | a = 1 … 5 | SUPPORT at all five | **PASS on the powered a**; a = 6 … 10 UNPOWERED |
| P3 → h_a clause | none | h_a reported below | **UNPOWERED as sealed** (cusp form not validated on fresh N, §10) |

## Per-path values
| a | λ_a | \|δ_a\| | SE | f(a) | SE |
|---|---|---|---|---|---|
| 1 | 1.6180 | 2.8336106599 | 6.5·10⁻⁹ | 1.0822175351 | 1.2·10⁻⁹ |
| 2 | 2.4142 | 6.7992251981 | 2.0·10⁻⁷ | 1.0873985203 | 2.3·10⁻⁹ |
| **3 (bronze)** | 3.3028 | **13.7602826** | 7.1·10⁻⁷ | **1.09719914** | 4.4·10⁻⁸ |
| 4 | 4.2361 | 24.620348 | 2.3·10⁻⁵ | 1.1095507 | 1.0·10⁻⁶ |
| 5 | 5.1926 | 40.3869134 | 1.3·10⁻⁷ | 1.1226432 | 7.3·10⁻⁷ |
| 6 | 6.1623 | 62.140 | — | 1.13542 | — |
| 7 | 7.1401 | 90.996 | — | 1.14737 | — |
| 8 | 8.1231 | 128.080 | — | 1.15831 | — |
| 9 | 9.1098 | — | — | — | — |
| 10 | 10.0990 | 231.439 | — | 1.17718 | — |

Paths without an SE are estimates only (as sealed; a = 9 has 4 levels below its cap q = 20,000, too few for an estimate, as the seal stated). The
a = 4 |δ| SE (2.3·10⁻⁵) is larger than both neighbours'; reported as computed.

**h_a (descriptive; UNPOWERED):** 1.094, 1.125, 1.169, 1.215, 1.258, 1.295, 1.325 for the pairs (1,2) … (7,8), at
pair-geometric-mean λ 1.98 … 7.62; increasing in a, still well below the predicted limit 1.5 at the last pair. (9,10)
is absent because a = 9 has no estimate.

## Cost (mispriced; recorded)
Per read, the summed per-level wall times are 7.5 h (READ1) and 7.3 h (READ2) at two threads per process: at most ≈ 15
core-h per read, ≈ 30 core-h for the double read, against the sealed ≈ 6–12 core-h. Almost all of the excess is
a = 8: ≈ 3.2 h wall per read (≈ 6 core-h) against its 0.78 core-h price. The price scaled the cost of the raised cap
(q = 34,840) roughly linearly in q; the top level costs grow faster than that (5,283 s of the a = 8 read's 30-digit
pass is the q = 4,289 … 34,840 level). Will was told of the overrun mid-read and let it finish overnight.
