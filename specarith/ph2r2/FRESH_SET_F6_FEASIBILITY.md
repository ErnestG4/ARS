# Fresh set F6 — feasibility under the gap rule (round 57; nothing downloaded, nothing pinned)

Generator: `check_fresh_set_f6.py` (rule and touched set in its docstring). Index `ph2/data/platt_md5.txt` sha256 6ca3534a1e967f593a93428e6479eac0992c446a105da3eeb0b7a64121808521. Touched: 36 files (13 seen by 2026-10-09, F1–F3, F4–F5) and Phase 2's Odlyzko bins.

## Gap-rule picks at F3's targets (in order; each pick blocks its neighbours for the next)

| target L | file | height range [t0, t1) | L-midpoint | md5 (index) |
|---|---|---|---|---|
| 17.50 | zeros_256646000.dat | [256,646,000, 258,746,000) | 17.529 | 020344a4229d8fc85f73fa1180aef729 |
| 19.75 | zeros_2365046000.dat | [2,365,046,000, 2,367,146,000) | 19.747 | 93c286212f9405741d6454370e0e108d |
| 21.25 | zeros_10630646000.dat | [10,630,646,000, 10,632,746,000) | 21.249 | ec13d8753e5e6e0a1161539df1d14a0a |

**Infeasible targets (no gap-feasible file within 0.3 in L):** L = 14.75 (nearest feasible: zeros_46646000.dat, L-midpoint 15.842); L = 15.25 (nearest feasible: zeros_46646000.dat, L-midpoint 15.842).

## Gap-feasible files within 1.0 in L of each target (before picks block neighbours; for review)

- **L = 14.75:** none
- **L = 15.25:** zeros_46646000.dat (15.842), zeros_48746000.dat (15.885), zeros_50846000.dat (15.927), zeros_59246000.dat (16.077), zeros_61346000.dat (16.111), zeros_63446000.dat (16.144), zeros_65546000.dat (16.176), zeros_67646000.dat (16.207)
- **L = 17.5:** zeros_256646000.dat (17.529), zeros_258746000.dat (17.538), zeros_239846000.dat (17.462), zeros_260846000.dat (17.546), zeros_237746000.dat (17.453), zeros_262946000.dat (17.554), zeros_235646000.dat (17.444), zeros_265046000.dat (17.561)
- **L = 19.75:** zeros_2365046000.dat (19.747), zeros_2381846000.dat (19.754), zeros_2362946000.dat (19.746), zeros_2383946000.dat (19.755), zeros_2360846000.dat (19.745), zeros_2386046000.dat (19.755), zeros_2358746000.dat (19.744), zeros_2388146000.dat (19.756)
- **L = 21.25:** zeros_10630646000.dat (21.249), zeros_10647446000.dat (21.251), zeros_10628546000.dat (21.249), zeros_10649546000.dat (21.251), zeros_10626446000.dat (21.249), zeros_10651646000.dat (21.251), zeros_10624346000.dat (21.249), zeros_10653746000.dat (21.251)

Pinning (FRESH_SET_F6.md) follows Will's review of this geometry, before any prediction is built.
