# Fresh set F6 — declared and md5-pinned BEFORE any prediction or download (round 58, 2026-10-18)

Generator: `declare_fresh_set_f6.py` (rule in its docstring; `check_fresh_set_f6.py`'s gap rule plus the round-58 extra file). Index `ph2/data/platt_md5.txt` sha256 6ca3534a1e967f593a93428e6479eac0992c446a105da3eeb0b7a64121808521.

**Round 58 (Will): F6 is four files** — the three gap-feasible files at L ≈ 17.5, 19.75 and 21.25 plus zeros_46646000.dat (L-midpoint 15.842). Reason: the low heights carry the largest corrections, the test stands alone, and the set is comparable to F5. Decided before any prediction.

**Checked (asserted):** all four are distinct from every F1–F5 file (so from F3, F4 and F5); each one's extended range (previous file's start to next file's end) overlaps no touched range (the 13 files seen by 2026-10-09, Phase 2's Odlyzko bins A and B, F1–F5) and no other F6 file. Infeasible targets (not substituted): L = 14.75 (nearest feasible zeros_46646000.dat, 15.842); L = 15.25 (nearest feasible zeros_46646000.dat, 15.842).

## F6 — corrected (B): offset-averaged third cumulant of the count

| target L | file | height range [t0, t1) | L range | md5 (pinned) |
|---|---|---|---|---|
| 15.84 | zeros_46646000.dat | [46,646,000, 48,746,000) | 15.8202–15.8643 | aa9f1f18b0e724dc54f3d184cc596bd2 |
| 17.50 | zeros_256646000.dat | [256,646,000, 258,746,000) | 17.5253–17.5335 | 020344a4229d8fc85f73fa1180aef729 |
| 19.75 | zeros_2365046000.dat | [2,365,046,000, 2,367,146,000) | 19.7462–19.7471 | 93c286212f9405741d6454370e0e108d |
| 21.25 | zeros_10630646000.dat | [10,630,646,000, 10,632,746,000) | 21.2491–21.2493 | ec13d8753e5e6e0a1161539df1d14a0a |

None is to be downloaded before the corrected (B)'s seal receipt is Bitcoin-attested and verified, nor decoded before its seal. Download by hand from `https://beta.lmfdb.org/data/riemann-zeta-zeros/<file>` into `specarith/ph2r2/data/platt_fresh/`, verified against this table before any use.
