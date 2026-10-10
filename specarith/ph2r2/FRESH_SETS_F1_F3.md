# Fresh Platt sets F1–F3 — declared and md5-pinned BEFORE download (Will, 2026-10-09)

Generator: `declare_fresh_sets.py` (selection rule, grid and checks in its docstring). Index: `ph2/data/platt_md5.txt` sha256 6ca3534a1e967f593a93428e6479eac0992c446a105da3eeb0b7a64121808521. Every pick is separated by >= 1 file from all 13 seen Platt files, from Phase 2's Odlyzko bins A and B, and from every other pick (asserted; v2 rule). None is to be decoded before its stage's seal.

**Infeasible targets (no gap-feasible file within 0.3 in L; not substituted):** F1 L = 13.25 (nearest feasible: zeros_15146000.dat, L-midpoint 14.760).

## F1 — shrink direction (Stage 1)

| target L | file | height range [t0, t1) | L range | md5 (pinned) |
|---|---|---|---|---|
| 14.25 | zeros_10946000.dat | [10,946,000, 13,046,000) | 14.3706–14.5461 | 754495b7e5603d1544d20876909700c9 |
| 15.50 | zeros_31946000.dat | [31,946,000, 34,046,000) | 15.4417–15.5053 | 1f6f5d94fea2e372fd7ef7e09216fb6a |
| 17.75 | zeros_319646000.dat | [319,646,000, 321,746,000) | 17.7448–17.7514 | 378eb1cdca224fd2ca4c556ca5a9b62c |
| 19.25 | zeros_1438946000.dat | [1,438,946,000, 1,441,046,000) | 19.2493–19.2508 | d1d8d60c71f7efcad1d373c4dd8b061f |
| 21.50 | zeros_13660946000.dat | [13,660,946,000, 13,663,046,000) | 21.4999–21.5001 | fbb8c83b765dff81903e7a22ddaee69d |
| 22.10 | zeros_24891746000.dat | [24,891,746,000, 24,893,846,000) | 22.0999–22.1000 | 662d01b2d2b6923788a1d70602db687b |

## F2 — quantitative few-prime model (Stage 2)

| target L | file | height range [t0, t1) | L range | md5 (pinned) |
|---|---|---|---|---|
| 15.75 | zeros_42446000.dat | [42,446,000, 44,546,000) | 15.7259–15.7742 | b9e8b34c5bab7367b68848c9e61940b0 |
| 16.50 | zeros_90746000.dat | [90,746,000, 92,846,000) | 16.4857–16.5086 | 8b05f3b38121178a7e563517ea08d0fe |
| 17.25 | zeros_193646000.dat | [193,646,000, 195,746,000) | 17.2437–17.2545 | 69b955f15e063c3646f4c92092f12290 |
| 19.50 | zeros_1848446000.dat | [1,848,446,000, 1,850,546,000) | 19.4997–19.5009 | 2169ed28b1dba1b889ccb25778eba4fc |
| 21.75 | zeros_17541746000.dat | [17,541,746,000, 17,543,846,000) | 21.7500–21.7501 | c706184af0a09d8f0df825ee9a81718a |

## F3 — route (a)

| target L | file | height range [t0, t1) | L range | md5 (pinned) |
|---|---|---|---|---|
| 14.75 | zeros_15146000.dat | [15,146,000, 17,246,000) | 14.6954–14.8252 | 12759c6bf4892f90244d240a7893c96a |
| 15.25 | zeros_25646000.dat | [25,646,000, 27,746,000) | 15.2220–15.3007 | 17769568c69cbabc1c47138f7159812e |
| 17.50 | zeros_248246000.dat | [248,246,000, 250,346,000) | 17.4921–17.5005 | 763374d804b79351fa5890bc56cae1b4 |
| 19.75 | zeros_2373446000.dat | [2,373,446,000, 2,375,546,000) | 19.7497–19.7506 | 10af7827aba9e214d135847c686e6d69 |
| 21.25 | zeros_10639046000.dat | [10,639,046,000, 10,641,146,000) | 21.2499–21.2501 | 6203cd45f34fb389b3be1108bdf9c913 |

Seen (excluded) files and their L ranges: zeros_14.dat 0.801–6.679; zeros_2546000.dat 12.912–13.514; zeros_19346000.dat 14.940–15.043; zeros_151646000.dat 16.999–17.013; zeros_1119746000.dat 18.998–19.000; zeros_8284946000.dat 21.000–21.000; zeros_30404246000.dat 22.300–22.300; zeros_30607946000.dat 22.307–inf; zeros_6746000.dat 13.887–14.158; zeros_55046000.dat 15.986–16.023; zeros_412046000.dat 17.999–18.004; zeros_3047546000.dat 20.000–20.000; zeros_22522946000.dat 22.000–22.000.

Download: by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into `specarith/ph2r2/data/platt_fresh/` (F1–F3 together or per stage), verified against this table before any use.
