"""
cross_substrate/allen_depth_fam2.py — Family II (Σ²/Δ₃/K long-range) for the Allen depth cells.

Completes the depth-extension fingerprint: allen_depth.py banked Family I (I.5q/I.5/W1δ); this adds
Family II (II.1 Σ²(L), II.2 Δ₃(L), II.3 K(τ=1)) on the SAME matched unfold (unfold_unit_mean), per
(cell, stimulus). Serves the long-range / phase-coupling cross-reference (does Family II carry the
theta-gamma signal frequency-domain methods capture?). Banked by cell_id → merge into allen-depth.

Reuses allen_depth's target table + h5py extraction; only the per-train computation differs
(compute_family_II instead of classify). Same persistent-pool + read-next-while-compute pipeline,
resumable. Run: --probe | --run [--workers 14]
Out: coordinates/allen-depth-fam2.jsonl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a"), os.path.join(_ROOT, "phase35a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import unfold_unit_mean                              # noqa: E402
from cross_substrate.axes import compute_family_II                     # noqa: E402
from cross_substrate.allen_depth import (                              # noqa: E402
    build_targets, _session_tasks, _drain, _f, NWB_GLOB, COORD)

OUT = os.path.join(COORD, "allen-depth-fam2.jsonl")


def _task_f2(arg):
    meta, train = arg
    pos = unfold_unit_mean(train)
    f2 = compute_family_II(pos)
    rec = {"cell_id": meta["cell_id"], "session": meta["session"],
           "unit_id": meta["unit_id"], "area": meta["area"], "stimulus": meta["stimulus"],
           "n": int(train.size),
           "axes_computed": {k: _f(v) if isinstance(v, (int, float)) else None
                             for k, v in f2.items()}}
    return rec


def _done_sessions():
    if not os.path.exists(OUT):
        return set()
    s = set()
    for line in open(OUT):
        try:
            s.add(json.loads(line)["session"])
        except Exception:
            pass
    return s


def run(workers, probe=False):
    targets = build_targets()
    print(f"Family II extension: {len(targets)} units, {workers} workers")
    files = sorted(glob.glob(NWB_GLOB))
    done = set() if probe else _done_sessions()
    fh = None if probe else open(OUT, "a" if os.path.exists(OUT) else "w")
    grand = 0
    t_all = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = []
        for f in files:
            sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
            if sid in done:
                print(f"  session {sid}: banked, skip"); continue
            t0 = time.perf_counter()
            with h5py.File(f, "r") as h:
                tasks = _session_tasks(h, targets[targets["session_id"] == sid], sid)
            if probe:
                tasks = tasks[:200]
            for t in tasks:
                futs.append(ex.submit(_task_f2, t))
            futs, n = _drain(futs, fh)
            grand += n
            print(f"  session {sid}: {len(tasks)} tasks submitted [read {time.perf_counter()-t0:.0f}s, "
                  f"{n} drained, {len(futs)} in flight]", flush=True)
            if probe:
                break
        futs, n = _drain(futs, fh, block=True)
        grand += n
    if fh:
        fh.close()
    dt = time.perf_counter() - t_all
    print(f"\n→ {grand} Family-II records in {dt/60:.1f} min")
    if probe:
        print(f"  PROBE: {grand} cells / {dt:.0f}s overlapped; classify-side rate dominates timing")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=14)
    a = ap.parse_args()
    if a.probe:
        run(a.workers, probe=True)
    elif a.run:
        run(a.workers)
    else:
        ap.error("need --probe or --run")


if __name__ == "__main__":
    main()
