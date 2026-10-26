"""RQ1 read-estimator check (round 87, committed as a generator in round 88 and rerun on spot in the pinned ph6c env).
Synthetic data only.
  1. var_stream (rq1_read) against var_exact (rq1_angles): 30 random sorted sets, n ∈ [50, 3000), every third with
     the edge points 0, 1 − 1e-9 and 0.5 added; K ∈ {2, 3, 7, 50, 400, 5000} (K = 1 excluded: degenerate window).
     Round 88 addition: the same on mirror-symmetrised sets (n/2 points plus np.mod(1 − θ, 1)), the archives' form.
  2. sorted_uniform: 200 replicates of N = 200,000, K = 64; mean ratio against 1 − 1/64.
The round-87 part reproduces the inline computation behind results/READ_ESTIMATOR_CHECK.json exactly (same seeds).

  python rq1_read_check.py OUT_JSON
"""
import json
import sys

import numpy as np
import numba

import rq1_angles as R
import rq1_read as Q


def main(out):
    rng = np.random.default_rng(1)
    worst = 0
    for trial in range(30):
        n = int(rng.integers(50, 3000))
        th = np.sort(rng.random(n))
        if trial % 3 == 0:
            th = np.sort(np.concatenate([th, [0.0, 1 - 1e-9, 0.5]]))
        for K in (2, 3, 7, 50, 400, 5000):
            a = Q.var_stream(th, K)
            b = R.var_exact(th, K)
            worst = max(worst, abs(a - b) / abs(b))
    u = [Q.var_stream(Q.sorted_uniform(200000, np.random.default_rng([3, i])), 64) / (200000 / 64) for i in range(200)]
    rng = np.random.default_rng(88)
    worst_m = 0
    for trial in range(30):
        h = rng.random(int(rng.integers(25, 1500))) * 0.5
        th = np.sort(np.concatenate([h, np.mod(1.0 - h, 1.0)]))
        for K in (2, 3, 7, 50, 400, 5000):
            worst_m = max(worst_m, abs(Q.var_stream(th, K) - R.var_exact(th, K)) / abs(R.var_exact(th, K)))
    res = dict(stream_vs_exact_max_rel=worst, K_range="2..5000 (K=1 excluded: degenerate whole-circle window)",
               uniform_mean_ratio_K64=float(np.mean(u)), uniform_expected=1 - 1 / 64,
               uniform_se=float(np.std(u, ddof=1) / np.sqrt(200)), mirror_stream_vs_exact_max_rel=worst_m,
               numpy=np.__version__, numba=numba.__version__, python=sys.version.split()[0])
    print(res)
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
