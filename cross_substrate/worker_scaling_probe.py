"""
worker_scaling_probe.py — find the throughput-optimal worker count for the
ids_rotnum unfold (memory-bandwidth-bound). Answers: 10 threads vs 18?

Method: run W identical unfold tasks concurrently on W workers (one wave),
time it → per-task wall under W-way contention. Throughput = W / per_task.
If bandwidth-bound, throughput plateaus/peaks below the core count.

Uses a banked eigenvalue array at a moderate L (cheap, representative).
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "phase35a"))
from unfold_rotnum import unfold_rotnum, GOLDEN  # noqa

EIG = os.path.join(_HERE, "coordinates/am_work/eig_sup_N70k_phi0.npy")
L_PROBE = 400_000          # moderate: representative of the streaming pattern
LAM = 1.5


def _task(_):
    e = np.load(EIG)
    t0 = time.perf_counter()
    unfold_rotnum(e, LAM, GOLDEN, L_PROBE, phis=(0.0,))
    return time.perf_counter() - t0


def main():
    print(f"WORKER-SCALING PROBE — N=70k eig, L={L_PROBE}, ids_rotnum unfold")
    print(f"{'workers':>7} {'wave_wall_s':>11} {'per_task_s':>10} {'throughput':>11} {'speedup_vs_serial':>17}")
    base = None
    for W in (1, 4, 8, 10, 12, 18):
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=W) as ex:
            list(ex.map(_task, range(W)))      # W tasks, one wave
        wall = time.perf_counter() - t0
        per_task = wall                         # one wave => wall == slowest task time
        thr = W / wall                          # tasks/sec at this concurrency
        if base is None:
            base = thr
        print(f"{W:>7} {wall:>11.1f} {per_task:>10.1f} {thr:>11.4f} {thr/base:>16.2f}x")


if __name__ == "__main__":
    main()
