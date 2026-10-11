"""Sparse direct check, v2: the same 300 points and the same threshold as sparse_check.py (|fast − reference| ≤ 1e-9,
oscillating and non-oscillating parts, every point), but against the independent 50-digit mpmath reference (cs4ref.ZetaRef:
prime sums and Euler products in mpmath too). v1 compared against the slow evaluator, whose prime sums are complex
double and which was itself off by up to 1.6e-9 at r > 10⁴ (SPARSE_CHECK_RECORD.md §4.1).

  python sparse_check_ref.py CHUNK NCHUNKS OUT
  python sparse_check_ref.py merge OUT
"""
import glob
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

import sparse_check as V1


def run(chunk, nchunks, out):
    import cs4fast as F
    import cs4ref as RF
    import cs4split as S
    rows, models = [], {}
    for i, (L, d1, d2, r) in enumerate(V1.points()):
        if i % nchunks != chunk:
            continue
        if L not in models:
            models[L] = (RF.ZetaRef(2 * mp.pi * mp.exp(L)), F.FastZeta(2 * math.pi * math.exp(L), pmax=100_000))
        ref, fast = models[L]
        o, n_, _ = S.connected_split(ref, d1, d2, r)
        fo, fn = fast.connected(d1, d2, np.array([r]))
        rows.append(dict(L=L, d1=d1, d2=d2, r=r, ref_non=str(n_), ref_osc=str(o),
                         err_non=float(abs(complex(fn[0]) - n_)), err_osc=float(abs(complex(fo[0]) - o))))
        print(i, L, d1, d2, round(r, 2), "err_non %.2e err_osc %.2e" % (rows[-1]["err_non"], rows[-1]["err_osc"]), flush=True)
        os.makedirs(out, exist_ok=True)
        json.dump(rows, open(os.path.join(out, f"sparse_ref_{chunk:03d}.json"), "w"), indent=1)   # incremental


def merge(out):
    rows = [r for f in sorted(glob.glob(os.path.join(out, "sparse_ref_*.json"))) for r in json.load(open(f))]
    worst = max(max(r["err_non"], r["err_osc"]) for r in rows)
    res = dict(n=len(rows), worst_abs_err=worst, n_over=sum(max(r["err_non"], r["err_osc"]) > 1e-9 for r in rows),
               PASS=bool(len(rows) == 300 and worst <= 1e-9), rows=rows)
    json.dump(res, open(os.path.join(out, "sparse_check_ref.json"), "w"), indent=1)
    print("sparse check v2 (vs 50-digit reference):", res["n"], "points, worst %.2e," % worst, res["n_over"], "over 1e-9:",
          "PASS" if res["PASS"] else "FAIL")


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge(sys.argv[2])
    else:
        run(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
