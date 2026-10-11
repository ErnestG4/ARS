"""Debug: the A* local factor on the θ-circle for the first key with c_r ≠ 0 (smoke-test geometry)."""
import math

import numpy as np

import cs4fastc as FC
import cs4lr as LR

t = 2 * math.pi * math.exp(16.5)
lr = LR.LongRangeZeta(t, pmax=10_000)
r = 4.0 + 0.5 * np.arange(64)
lr.set_grid(r)
lr.cache = {}
orig = lr._memo
seen = []


def spy(name, fn, *ks):
    if name == "As" and not seen and any(k.cr for k in ks):
        seen.append([(k.s, k.cr) for k in ks])
        g = lr.groups[0]
        J = 128
        th = 2 * np.pi * np.arange(J) / J
        args = [1j * (k.s + k.cr * th[:, None] / g["lp"]) for k in ks]
        lr._grp = g
        m, prod = fn(*args)
        lr._grp = None
        m = np.broadcast_to(m, (J, g["p"].shape[1]))
        print("keys", seen[0])
        for j in (0, 1, 5, 50, 150):
            col = m[:, j]
            ph = np.unwrap(np.angle(col))
            print("p=%d  |f-1| max %.3e  min|f| %.3e  phase span %.3f  closing %.3f  first/last %s %s"
                  % (g["p"][0, j], np.abs(col - 1).max(), np.abs(col).min(), ph[-1] - ph[0], np.angle(col[0] / col[-1]),
                     col[0], col[-1]))
        raise SystemExit
    return orig(name, fn, *ks)


lr._memo = spy
try:
    lr.connected(0.5, 0.5, r)
except SystemExit:
    pass
