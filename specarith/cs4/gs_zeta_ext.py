"""Stage 2, estimator B (twenty-fourth round): extend the stored long-range non-oscillating C(r) of gs_zeta.py from
r = 4.8·10⁴ to 6·10⁴, so the predicted lag-1 window correlation ρ₁ = Cov(S(c), S(c + 3b))/V(b) is computable at
b = 10⁴ (its Gaussian, s = b/√π, must lie inside the grid to 5σ: 3·10⁴ + 5s = 5.82·10⁴).

Same evaluator (cs4lr.LongRangeZeta, prime cutoff 3·10⁵), same node pairs, same Δr = 0.5 on the production lattice
r = 5 + 0.5k. The extension grid starts at r = 47000, so [47000, 48000.5] overlaps the stored grid. The overlap is a
consistency check: the re-initialised evaluator, with a different grid and Euler–Maclaurin length, must reproduce
the stored values there.

  python gs_zeta_ext.py pairs ELL CHUNK NCHUNKS OUT    -> OUT/L{ELL}/ext/p{i}_{j}.npz (c_non_ext on ext_grid())
"""
import math
import os
import sys
import time

import numpy as np

import gs_zeta as Z

R_EXT_LO, R_EXT_HI = 47_000.0, 60_000.0


def ext_grid():
    k0 = int(round((R_EXT_LO - Z.R_LO) / Z.DR_L))
    n = int(math.ceil((R_EXT_HI - R_EXT_LO) / Z.DR_L)) + 1
    n += n % 2
    return Z.R_LO + Z.DR_L * (k0 + np.arange(n))


def pairs(ell, chunk, nchunks, out):
    import cs4lr as LR
    lr = LR.LongRangeZeta(Z.tval(ell), pmax=Z.PMAX)
    r = ext_grid()
    d = os.path.join(out, f"L{ell}", "ext")
    os.makedirs(d, exist_ok=True)
    for k, (i, j) in enumerate(Z.PAIRS):
        if k % nchunks != chunk:
            continue
        fn = os.path.join(d, f"p{i:02d}_{j:02d}.npz")
        if os.path.exists(fn):
            continue
        t0 = time.time()
        _, nl = lr.connected(Z.DN[i], Z.DN[j], r, nonosc_only=True)
        tail = max(lr.diag.values())
        np.savez(fn, c_non_ext=nl.real, imag_max=np.abs(nl.imag).max(), tail=tail, secs=time.time() - t0)
        print(ell, i, j, "%.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    assert sys.argv[1] == "pairs"
    pairs(float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
