# Fresh Platt sets F4–F5 — declared and md5-pinned BEFORE download (round 50, 2026-10-16)

Generator: `declare_fresh_sets_f4f5.py` (rule and touched set in its docstring; declare_fresh_sets.py's v2 rule at F3's targets). Index: `ph2/data/platt_md5.txt` sha256 6ca3534a1e967f593a93428e6479eac0992c446a105da3eeb0b7a64121808521. Every pick is separated by >= 1 file from the 13 files seen by 2026-10-09, Phase 2's Odlyzko bins A and B, every F1–F3 pick and every other pick (asserted). None is to be downloaded before its observable's seal is Bitcoin-attested and verified (round 49 protocol), nor decoded before its seal.

**Infeasible targets (no gap-feasible file within 0.3 in L; not substituted):** F4 L = 14.75 (nearest feasible: zeros_36146000.dat, L-midpoint 15.593); F4 L = 15.25 (nearest feasible: zeros_36146000.dat, L-midpoint 15.593); F5 L = 14.75 (nearest feasible: zeros_36146000.dat, L-midpoint 15.593); F5 L = 15.25 (nearest feasible: zeros_36146000.dat, L-midpoint 15.593).

**Round 51 (Will): asymmetric by decision.** F4 keeps its three files. F5 also gets zeros_36146000.dat (L-midpoint 15.593), the gap-feasible file nearest the infeasible low targets. The weaker observable, (B), gets the extra low-height file. This was decided before any F4/F5 prediction, calibration or download. Its row's target L is its own L-midpoint.

## F4 — route (a) follow-up (A): next-nearest-neighbour spacing law

| target L | file | height range [t0, t1) | L range | md5 (pinned) |
|---|---|---|---|---|
| 17.50 | zeros_252446000.dat | [252,446,000, 254,546,000) | 17.5088–17.5171 | 4d9c80df1f369a48e985cf5f2da870e6 |
| 19.75 | zeros_2369246000.dat | [2,369,246,000, 2,371,346,000) | 19.7480–19.7488 | d2d328ee9dc75e908f4194d6aa45e0db |
| 21.25 | zeros_10634846000.dat | [10,634,846,000, 10,636,946,000) | 21.2495–21.2497 | 873b302f888a8c58642ca9a6f4952a79 |

## F5 — route (a) follow-up (B): third cumulant of the count

| target L | file | height range [t0, t1) | L range | md5 (pinned) |
|---|---|---|---|---|
| 15.59 | zeros_36146000.dat | [36,146,000, 38,246,000) | 15.5652–15.6217 | 8fb15afc113768103c1b3891a83f9d54 |
| 17.50 | zeros_244046000.dat | [244,046,000, 246,146,000) | 17.4750–17.4836 | 4f19fac76037c7f361b1a0c12a706b9b |
| 19.75 | zeros_2377646000.dat | [2,377,646,000, 2,379,746,000) | 19.7515–19.7524 | abbec916f56f69bc96df594e735c5401 |
| 21.25 | zeros_10643246000.dat | [10,643,246,000, 10,645,346,000) | 21.2503–21.2505 | 916639a260da1c6b84b291260b5627e6 |

Touched (excluded) files: zeros_14.dat, zeros_2546000.dat, zeros_19346000.dat, zeros_151646000.dat, zeros_1119746000.dat, zeros_8284946000.dat, zeros_30404246000.dat, zeros_30607946000.dat, zeros_6746000.dat, zeros_55046000.dat, zeros_412046000.dat, zeros_3047546000.dat, zeros_22522946000.dat, zeros_10946000.dat, zeros_31946000.dat, zeros_319646000.dat, zeros_1438946000.dat, zeros_13660946000.dat, zeros_24891746000.dat, zeros_42446000.dat, zeros_90746000.dat, zeros_193646000.dat, zeros_1848446000.dat, zeros_17541746000.dat, zeros_15146000.dat, zeros_25646000.dat, zeros_248246000.dat, zeros_2373446000.dat, zeros_10639046000.dat.

Download: by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into `specarith/ph2r2/data/platt_fresh/`, verified against this table before any use.
