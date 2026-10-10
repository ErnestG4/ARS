"""Will's sparse direct check (twentieth round (1); overnight queue item 1): the ζ connected two-pair ρ₄c evaluated by
the slow 30-digit CS08 code (cs4split, mpmath) at a few hundred large-r points on a log grid, beside the fast vectorised
evaluator (cs4fast) at the same points. 300 points: heights L = log(t/2π) ∈ {16.5, 21.75} (the F2 range's ends),
in-pair offsets (d₁, d₂) ∈ {(0.5, 0.5), (0.3, 0.8), (1.0, 0.4)}, r on 50 log-spaced values in [10, 2·10⁴] spacings.
Pass: |fast − slow| ≤ 1e-9 for both the oscillating and non-oscillating parts at every point.

  python sparse_check.py CHUNK NCHUNKS OUT    (one process per chunk; points interleaved)
  python sparse_check.py merge OUT
"""
import glob
import json
import math
import os
import sys

import mpmath as mp
import numpy as np


def points():
    pts = []
    for L in (16.5, 21.75):
        for d1, d2 in ((0.5, 0.5), (0.3, 0.8), (1.0, 0.4)):
            for r in np.geomspace(10, 2e4, 50):
                pts.append((L, d1, d2, float(r)))
    return pts


def run(chunk, nchunks, out):
    import cs4fast as F
    import cs4split as S
    rows = []
    models = {}
    for i, (L, d1, d2, r) in enumerate(points()):
        if i % nchunks != chunk:
            continue
        t = 2 * math.pi * math.exp(L)
        if L not in models:
            models[L] = (S.Zetap(t, pmax=100_000), F.FastZeta(t, pmax=100_000))
        slow, fast = models[L]
        o, n_, _ = S.connected_split(slow, d1, d2, r)
        fo, fn = fast.connected(d1, d2, np.array([r]))
        rows.append(dict(L=L, d1=d1, d2=d2, r=r, slow_non=complex(n_).real, slow_osc=complex(o).real,
                         fast_non=fn[0].real, fast_osc=fo[0].real, slow_non_im=complex(n_).imag,
                         err_non=abs(fn[0] - complex(n_)), err_osc=abs(fo[0] - complex(o))))
        print(i, L, d1, d2, round(r, 2), "non %.6e err %.1e" % (rows[-1]["slow_non"], rows[-1]["err_non"]), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(rows, open(os.path.join(out, f"sparse_{chunk:03d}.json"), "w"), indent=1)


def merge(out):
    rows = [r for f in sorted(glob.glob(os.path.join(out, "sparse_*.json"))) for r in json.load(open(f))]
    worst = max(max(r["err_non"], r["err_osc"]) for r in rows)
    res = dict(n=len(rows), worst_abs_err=worst, PASS=bool(len(rows) == 300 and worst <= 1e-9),
               max_abs_non_by_L={str(L): max(abs(r["slow_non"]) for r in rows if r["L"] == L) for L in (16.5, 21.75)},
               rows=rows)
    json.dump(res, open(os.path.join(out, "sparse_check.json"), "w"), indent=1)
    print("sparse check:", res["n"], "points, worst |fast - slow| %.2e" % worst, "PASS" if res["PASS"] else "FAIL")


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge(sys.argv[2])
    else:
        run(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
