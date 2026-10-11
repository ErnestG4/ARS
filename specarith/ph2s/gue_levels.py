"""Shrink phase (PH2S) Stage 1 pre-read: fresh long-GUE sequences for the matched sine-kernel baseline (Will, fifteenth
round: ≥ 16 seeds per window length, distinct from the exploration seeds in ph2r2/longbase.py).

Construction identical to ph2r2/longbase.py's gue(): Dumitriu–Edelman GUE tridiagonal (β = 2) of size ⌈1.06·L⌉, all
eigenvalues by LAPACK sterf, central L kept, unfolded by the exact semicircle count with R² = 8·n. Saved: the unfolded
levels (unit density, starting at 0) and the sanity record. Mapping onto bin heights and the growth statistic are done
later, per bin and per test function (s1lib.py), from these files.

  python gue_levels.py SEED L OUT        -> OUT/gue_L<L>_s<SEED>.npy + .json
"""
import json
import math
import os
import sys

import numpy as np
from scipy.linalg import eigh_tridiagonal

SEED0 = 20261011                     # Stage 1 baseline seeds (exploration used 20261010)


def semicircle_count(x, n, R):
    x = np.clip(x, -R, R)
    return n * (0.5 + (x * np.sqrt(R * R - x * x) + R * R * np.arcsin(x / R)) / (math.pi * R * R))


def main(seed, L, out):
    n = int(math.ceil(1.06 * L))
    rng = np.random.default_rng([SEED0, seed, L])
    d = math.sqrt(2.0) * rng.standard_normal(n)
    b = np.sqrt(rng.chisquare(2 * np.arange(n - 1, 0, -1)))
    ev = np.sort(eigh_tridiagonal(d, b, eigvals_only=True, lapack_driver="sterf"))
    i0 = (n - L) // 2
    u = semicircle_count(ev[i0:i0 + L], n, math.sqrt(8.0 * n))
    resid = u - (i0 + 0.5 + np.arange(L))
    s = np.diff(u)
    sanity = dict(seed=seed, L=L, n_mat=n, count_resid_mean=float(resid.mean()), count_resid_sd=float(resid.std()),
                  count_resid_drift=float(resid[-1000:].mean() - resid[:1000].mean()), mean_spacing=float(s.mean()),
                  rtilde=float((np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])).mean()))
    os.makedirs(out, exist_ok=True)
    np.save(os.path.join(out, f"gue_L{L}_s{seed:03d}.npy"), u - u[0])
    json.dump(sanity, open(os.path.join(out, f"gue_L{L}_s{seed:03d}.json"), "w"), indent=1)
    print(json.dumps(sanity), flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
