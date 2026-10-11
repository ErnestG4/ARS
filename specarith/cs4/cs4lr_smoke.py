"""Smoke test for cs4lr: pmax 1e4, one node, a short grid; compare a few points with cs4fastc."""
import math
import time

import numpy as np

import cs4fastc as FC
import cs4lr as LR

t = 2 * math.pi * math.exp(16.5)
lr = LR.LongRangeZeta(t, pmax=10_000)
ref = FC.FastZetaCached(t, pmax=10_000)
r = 4.0 + 0.5 * np.arange(64)
t0 = time.time()
o, n = lr.connected(0.5, 0.5, r)
print("lr %.1fs" % (time.time() - t0), "blocks", len(lr.diag), "max tail %.1e" % max(lr.diag.values()))
idx = np.array([0, 7, 31, 63])
ro, rn = ref.connected(0.5, 0.5, r[idx])
print("non err", np.abs(n[idx] - rn).max(), "osc err", np.abs(o[idx] - ro).max(), "|non|", np.abs(rn).max())
