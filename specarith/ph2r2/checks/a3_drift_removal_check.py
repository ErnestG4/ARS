"""A3 pre-data check of r2run.drift_removed: a synthetic R1-sized series c_i = e(t_i)·(1 + 0.05·ε_i) with i.i.d. ε (no
correlation at any range) at R1's exact smooth-density heights. The raw moving-block bootstrap SD must grow with block
length (the drift); the drift-removed one must stay flat (ratio to block 100 within bootstrap noise of 1). Also checks e(t)
against g0b_trend_check (E[c] at t0 for (0.5, 0.3) = 0.82271)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import g0b as G
import r2prep as P
import r2run as RR

name, u, w = "R1", 0.5, 0.3
g = P.geometry(name)
print("e(t0) =", float(RR.expected_contribution(g["t0"], u, w, g["delta"])[0]), "(g0b_trend_check: 0.82271)")
x0, x1 = float(P.nbar(g["t0"])), float(P.nbar(g["t1"]))
lev = G.nbar_inv(np.arange(np.ceil(x0), np.floor(x1)) + 0.5, g["tc"])
rng = np.random.default_rng(3)
grid = np.linspace(g["t0"], g["t1"], 257)
c = np.interp(lev, grid, RR.expected_contribution(grid, u, w, g["delta"])) * (1 + 0.05 * rng.standard_normal(len(lev)))
cd = RR.drift_removed(c, lev, name, u, w)
for tag, s in (("raw", c), ("drift-removed", cd)):
    sds = [G.boot_sd_sum(s, bl, np.random.default_rng(4)) for bl in G.BOOT_LEVELS]
    print(f"{tag:14s} n={len(s)} growth 100 -> 1,000 -> 10,000:", [round(v / sds[0], 3) for v in sds])
