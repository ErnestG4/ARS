"""Closest approach of gs_zeta's short-grid four-point evaluations to a coincidence (diag_coinc.py measured the fast
evaluator's error against 50 digits as a function of the distance δ to one: single coincidence ≤ 3e-10 down to
δ = 1e-3; double coincidence 2e-8 at δ = 1e-2, 8e-5 at δ = 1e-3).

Points (−d₁/2, d₁/2, r − d₂/2, r + d₂/2), d₁, d₂ on the GJ16 in-pair nodes, r on the short grid (k + ½)·0.1. A
cross-pair coincidence is r = ±(d₁ ± d₂)/2; a double one (both cross pairs at once) needs d₁ = d₂ and r → 0. The long
grid starts at r = 5 > DMAX, so it has none."""
import numpy as np

import gs_zeta as Z

rs = Z.short_grid()
D1, D2 = np.meshgrid(Z.DN, Z.DN, indexing="ij")
targets = np.abs(np.stack([(D1 + D2) / 2, (D1 - D2) / 2]))     # r ≥ 0 coincides when r = |d₁ ± d₂|/2
dist = np.abs(rs[:, None, None, None] - targets[None])
k = np.unravel_index(np.argmin(dist), dist.shape)
print("closest single coincidence: δ = %.3e at r = %.3f, d = (%.4f, %.4f), %s"
      % (dist[k], rs[k[0]], Z.DN[k[2]], Z.DN[k[3]], "(d1+d2)/2" if k[1] == 0 else "|d1-d2|/2"))
for thr in (1e-2, 1e-3, 1e-4):
    print("evaluations with δ < %.0e: %d of %d" % (thr, int((dist < thr).sum()), dist.size))
print("double coincidences: d₁ = d₂ pairs at r = 0, nearest grid r = %.3f (δ = %.3f)" % (rs.min(), rs.min()))
