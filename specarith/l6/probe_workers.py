"""Worker-count probe for the L6 generation on spot (design §12; engineering only, no result depends on it).
One task = one phi_np(amp=True) pass with 10⁵ θ points (the N = 10⁵ working set) over the first 10⁴ Verblunsky
coefficients (a tenth of a full pass). K tasks run at once in K processes; throughput = K / median wall.
  python probe_workers.py K1 K2 ...   → prints one JSON line per K
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cs4"))
import cbe  # noqa: E402


def task(i):
    a = cbe.verblunsky(np.random.default_rng([1, i]), 1, 10_000, 2.0)
    th = np.sort(np.random.default_rng([2, i]).uniform(0, cbe.TWO_PI, (1, 100_000)))
    t = time.time()
    cbe.phi_np(a, th, amp=True)
    return time.time() - t


if __name__ == "__main__":
    for K in map(int, sys.argv[1:]):
        with Pool(K) as p:
            w = p.map(task, range(K), chunksize=1)
        print(json.dumps(dict(K=K, median_wall_s=round(float(np.median(w)), 2), max_wall_s=round(float(max(w)), 2),
                              throughput_tasks_per_s=round(K / float(np.median(w)), 4))), flush=True)
