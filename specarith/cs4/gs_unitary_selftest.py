"""Self-test for gs_unitary.py: the closed-form 4×4 determinant against numpy, then the sine-limit pieces check."""
import numpy as np

import gs_unitary as G

rng = np.random.default_rng(1)
worst = 0.0
for _ in range(20):
    d1, d2, r = rng.uniform(0, 2), rng.uniform(0, 2), rng.uniform(0, 6)
    x = np.array([-d1 / 2, d1 / 2, r - d2 / 2, r + d2 / 2])
    worst = max(worst, abs(np.linalg.det(np.sinc(x[:, None] - x[None, :])) - G.det4(d1, d2, r)))
print("det4 closed form vs numpy: worst %.1e" % worst)
print("I2 %.10f  I3(100) %.10f  I3(1e4) %.10f" % (G.I2(), G.I3(100), G.I3(10_000)))
G.check()
