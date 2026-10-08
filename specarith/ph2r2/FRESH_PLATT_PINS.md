# Phase 2 R₂ (new confirmatory phase) — fresh Platt heights, md5 pinned BEFORE download

Will, eleventh round (2026-10-08): fresh Platt heights L = log(E/2π) = 14, 16, 18, 20, 22, md5-pinned pre-download.
Selection rule (as in PH2_SEAL_2.1 §3): the file whose start height is the largest ≤ E = 2π·e^L, from the LMFDB index
`md5.txt` (sha256 6ca3534a1e967f59…, the same index pinned for Phase 2, 14,580 entries; local copy
`specarith/ph2/data/platt_md5.txt`). None of these files, and no height range overlapping them, has been read: the
Phase 2 bins sit at L ≈ 12.9–13.5, 14.94–15.04, 17.0, 19.0, 21.0, 22.3 (P1–P6) and below 12.1 (A, B, zeros6).

| bin | target L | file | height range [t0, t1) | L range | md5 (pinned before download) |
|---|---|---|---|---|---|
| R1 | 14 | zeros_6746000.dat | [6,746,000, 8,846,000) | 13.887–14.158 | 7da68bfe58799d9ad96d6e47f3c3fb3a |
| R2 | 16 | zeros_55046000.dat | [55,046,000, 57,146,000) | 15.986–16.023 | a702b364cf5f262b9f36963c58e12599 |
| R3 | 18 | zeros_412046000.dat | [412,046,000, 414,146,000) | 17.999–18.004 | b38965a1e947a9d5ebb69b4fd70bcde5 |
| R4 | 20 | zeros_3047546000.dat | [3,047,546,000, 3,049,646,000) | 19.9997–20.0004 | 75781990d6be699da0e7a80d5e184be3 |
| R5 | 22 | zeros_22522946000.dat | [22,522,946,000, 22,525,046,000) | 21.99992–22.00002 | 7b9726648af12152eda3ec9cde888210 |

Download: by hand in a browser (beta.lmfdb.org human gate, PH2 A5) from
`https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into `specarith/ph2r2/data/platt/`; verified against this table
before any use. These files are not to be decoded before the R₂ phase is sealed.
