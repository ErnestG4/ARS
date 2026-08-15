"""The exact-equality witness that observer_b.sigma2_direct_1d's docstring
and pilot_tolerances.py claimed but which existed only as a session heredoc
(2026-08-15 bridge review F9 — the committed-generator discipline applied to
TESTS: a claimed verification that isn't committed doesn't exist).

Asserts sigma2_direct_1d reproduces universality.number_variance EXACTLY
(same positions grid, same ddof) on small n, where the home implementation
is tractable.  Exit nonzero on any drift in either implementation."""

import sys

import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/bridge")
sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
from observer_b import sigma2_direct_1d
from universality import number_variance

worst = 0.0
for seed, n in ((5, 5000), (6, 3000), (7, 800)):
    rng = np.random.default_rng(seed)
    e = np.sort(rng.uniform(0, n, n))
    nv = number_variance(e, L_max=20.0, n_L=40)
    fast = sigma2_direct_1d(e, nv["L"])
    m = ~np.isnan(nv["sigma2"])
    d = float(np.abs(nv["sigma2"][m] - fast[m]).max())
    worst = max(worst, d)
    print(f"seed {seed} n={n}: max |home - fast| = {d:.3e}")
assert worst == 0.0, f"EQUALITY BROKEN: {worst}"
print("sigma2_direct_1d == universality.number_variance: EXACT")
