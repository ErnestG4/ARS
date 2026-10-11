"""Diagnostic (not a gate): the stored gs_zeta short-range values at the clustered corner of the grid against the 50-digit
reference. With the smallest in-pair nodes (d = 0.0513, 0.1363) and r = 0.05, 0.15, all four points lie within ~0.2
mean spacings; the closest cross-pair approach is δ = 1.3e-3 (coinc_margin.py). diag_coinc.py covered isolated
coincidences only (d = 0.5, 0.7), so this checks the configuration the Stage 2 integral actually uses.

  python diag_cluster.py ELL GS_ZETA_OUT TASK OUT     TASK indexes CASES; compares with OUT/L{ELL}/pairs/pIJ.npz c_short
"""
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

import cs4ref as RF
import cs4split as S
import gs_zeta as Z

CASES = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 1, 0), (0, 0, 5)]     # (i, j, short-grid index k): r = (k + ½)·0.1


def main(ell, gsout, task, out):
    i, j, k = CASES[task]
    d1, d2, r = Z.DN[i], Z.DN[j], Z.short_grid()[k]
    stored = float(np.load(os.path.join(gsout, f"L{ell}", "pairs", f"p{i:02d}_{j:02d}.npz"))["c_short"][k])
    ref = RF.ZetaRef(2 * mp.pi * mp.exp(mp.mpf(ell)), pmax=Z.PMAX)
    _, _, tot = S.connected_split(ref, d1, d2, r)
    row = dict(ell=ell, i=i, j=j, d1=d1, d2=d2, r=r, ref_re=float(mp.re(tot)), ref_im=float(mp.im(tot)),
               stored=stored, err=abs(stored - float(mp.re(tot))))
    print(json.dumps(row), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(row, open(os.path.join(out, f"cluster_{task}.json"), "w"), indent=1)


if __name__ == "__main__":
    main(float(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4])
