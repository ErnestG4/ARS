"""Phase 6.1 pre-read (PH6_SEAL 6.1 §7.2): matched-size ⟨r̃⟩ bands at W = 30,000 levels, run in parallel.
Same generators as preread61.py: Poisson (exponential spacings); GOE/GUE/GSE from the Dumitriu–Edelman Hermite tridiagonal
(β = 1, 2, 4), central W eigenvalues of a size-5W matrix; band = [2.5, 97.5] percentiles. Each draw has its own seed
(base·10⁴ + ensemble·10³ + i), so the run is reproducible draw by draw. Labels: large-N constants (rtilde_refs, D4).

  python bands61.py OUT DRAWS PROCS
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.linalg import eigh_tridiagonal

W = 30_000
BASE = 20261008
ENS = {"Poisson": (0, None), "GOE": (1, 1), "GUE": (2, 2), "GSE": (3, 4)}
LARGE_N = {"Poisson": 2 * math.log(2) - 1, "GOE": 0.5307, "GUE": 0.5996, "GSE": 0.6744}   # = rtilde_refs.LARGE_N


def rtilde(levels):
    s = np.diff(np.sort(levels))
    return float((np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])).mean())


def draw(args):
    name, i = args
    k, beta = ENS[name]
    rng = np.random.default_rng(BASE * 10_000 + k * 1_000 + i)
    if beta is None:
        return name, i, rtilde(np.cumsum(rng.exponential(1.0, W)))
    n = 5 * W
    d = math.sqrt(2.0) * rng.standard_normal(n)
    b = np.sqrt(rng.chisquare(beta * np.arange(n - 1, 0, -1)))
    return name, i, rtilde(central_window(d, b, W))


def central_window(d, b, Wn):
    """The central Wn eigenvalues (indices 2Wn … 3Wn − 1) of the size-5Wn tridiagonal. All eigenvalues by LAPACK sterf
    (O(n²), eigenvalues only) and then the slice — identical to select='i' on that index range (checked in
    check_driver), which uses bisection and is ~100× slower at Wn = 3·10⁴."""
    ev = eigh_tridiagonal(d, b, eigvals_only=True, lapack_driver="sterf")
    return np.sort(ev)[2 * Wn:3 * Wn]


def check_driver(Wn=2000, seed=1):
    rng = np.random.default_rng(seed)
    n = 5 * Wn
    d = math.sqrt(2.0) * rng.standard_normal(n)
    b = np.sqrt(rng.chisquare(2 * np.arange(n - 1, 0, -1)))
    a = central_window(d, b, Wn)
    c = np.sort(eigh_tridiagonal(d, b, eigvals_only=True, select="i", select_range=(2 * Wn, 3 * Wn - 1)))
    return float(np.max(np.abs(a - c))), abs(rtilde(a) - rtilde(c))


if __name__ == "__main__":
    out, draws, procs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    jobs = [(name, i) for name in ENS for i in range(draws)]
    with Pool(procs) as pool:
        res = pool.map(draw, jobs, chunksize=1)
    bands = {}
    for name in ENS:
        v = np.array([r for nm, i, r in sorted(res) if nm == name])
        bands[name] = dict(label_large_N=LARGE_N[name], mean=float(v.mean()), sd=float(v.std(ddof=1)),
                           band=[float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], draws=int(len(v)),
                           values=v.tolist())
        print(name, {k: (round(x, 5) if isinstance(x, float) else x) for k, x in bands[name].items() if k != "values"},
              flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(dict(W=W, base_seed=BASE, bands=bands), open(os.path.join(out, "bands61.json"), "w"), indent=1)
