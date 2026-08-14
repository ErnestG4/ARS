"""BRIDGE-B B2 substrate: split Gaussian primes in a pre-registered annular
wedge — sealed in prereg BEFORE B1 runs (brief §1 B2).

Window (sealed): r ∈ [3000, 3600], θ ∈ [0.15, 0.35] rad (inside the first
octant).  Declared properties:
  * The wedge excludes the axes, hence contains NO inert primes (those sit on
    the rays θ ∈ {0, π/2, ...}); the configuration is split Gaussian primes
    a+bi, a²+b²=p ≡ 1 mod 4, one point per rational prime in the octant.
  * Support set is the checkerboard sublattice {a+b odd} of Z[i] — minimum
    pair distance √2.  Continuous DPP/cluster families cannot express a
    lattice-supported process; this is a DECLARED approximation and the
    support-set discipline (TOOLKIT §9) is expected to surface in the fits.
  * Intensity model (theory-supplied, TOOLKIT §11.2 option 1):
    λ(r) = 2/(π ln r) from the Landau prime-ideal count.  Variation across
    the annulus: ln(3000)/ln(3600) → 2.24%, inside the sealed 5% budget.
Sieve/Cornacchia machinery reused from phase34d/gaussian_primes.py.
"""

import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
from phase34d.gaussian_primes import sieve_primes, split_p_as_sum_of_two_squares

R1, R2 = 3000.0, 3600.0
T1, T2 = 0.15, 0.35


def build():
    lo, hi = int(R1**2), int(R2**2)
    primes = sieve_primes(hi)
    primes = primes[(primes >= lo) & (primes % 4 == 1)]
    pts = []
    for p in primes:
        a, b = split_p_as_sum_of_two_squares(int(p))   # a ≥ b > 0 → θ ∈ (0, π/4)
        th = np.arctan2(b, a)
        if T1 <= th <= T2:
            pts.append((a, b))
    pts = np.array(pts, float)
    r = np.hypot(pts[:, 0], pts[:, 1])
    pts = pts[(r >= R1) & (r <= R2)]
    return pts


if __name__ == "__main__":
    pts = build()
    area = 0.5 * (T2 - T1) * (R2**2 - R1**2)
    lam = len(pts) / area
    lam_theory = 2.0 / (np.pi * np.log(0.5 * (R1 + R2)))
    print(f"n={len(pts)}  area={area:.0f}  lam_hat={lam:.5f}  "
          f"lam_theory(mid)={lam_theory:.5f}  mean spacing={lam**-0.5:.2f}")
    np.save("/home/combust/fmexplorer/criticality_tool/bridge/gp_annulus_points.npy", pts)
