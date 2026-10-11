"""Inspect the assembled long-range non-oscillating C(r) (as in diag_wincov.py) along the stored grid: block means and
block RMS over r-blocks of 2000, to see whether the large covariances at lags reaching r ≈ 4.5·10⁴ come from the
function or from the end of the grid. Also the running Σ_k (1 − k/n) ρ_k over all lags fully inside the grid.

  python diag_wincov_edge.py ELL
"""
import math
import os
import sys

import numpy as np

import gs_unitary as G
import gs_zeta as Z


def main(ell):
    d = os.path.join("results", "gs_zeta", f"L{ell}", "pairs")
    rl = Z.long_grid()
    cl_ = 1 - G.chi(rl)
    Cl = np.zeros(len(rl))
    for (i, j) in Z.PAIRS:
        z = np.load(os.path.join(d, f"p{i:02d}_{j:02d}.npz"))
        wgt = 4 * Z.DW[i] * Z.FD[i] * Z.DW[j] * Z.FD[j] * (1 if i == j else 2)
        Cl += wgt * cl_ * z["c_non"]
    print("ℓ =", ell, " grid", rl[0], "…", rl[-1], len(rl))
    for lo in range(0, 48000, 2000):
        m = (rl >= lo) & (rl < lo + 2000)
        print("r ∈ [%5d, %5d): mean %+.3e  rms %.3e  max|C| %.3e" % (lo, lo + 2000, Cl[m].mean(), np.sqrt((Cl[m] ** 2).mean()),
                                                                   np.abs(Cl[m]).max()))
    k = np.argmax(np.abs(Cl))
    print("largest |C| at r = %.1f: %+.3e;  last 10 values:" % (rl[k], Cl[k]), " ".join("%+.2e" % x for x in Cl[-10:]))
    print("mean over r>40000 / r in [20000, 40000): %+.3e / %+.3e" % (Cl[rl > 40000].mean(), Cl[(rl >= 2e4) & (rl < 4e4)].mean()))


if __name__ == "__main__":
    main(sys.argv[1])
