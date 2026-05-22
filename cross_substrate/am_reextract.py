"""
cross_substrate/am_reextract.py — Phase 1: AM matched re-extraction (parallel, hardened).

Phase 35 banked only the W1δ reduction, not eigenvalues/spacings. This recovers
AM into the landscape on the matched object-(a) leg. Three stages:

  A (eigensolve, ~min parallel): am_eigs per (cell,φ) → checkpoint
     coordinates/am_work/eig_{cell}_phi{i}.npy. The reusable raw object.
  B (unfold @ converged L, ~hours): O(N·L) Sturm unfold per (cell,φ) →
     checkpoint coordinates/am_work/unf_{cell}_phi{i}.npy. The expensive stage;
     48 independent tasks, parallel across local workers.
  agg: pool φ-ensemble positions per cell → matched Family I/II → coordinates/am.jsonl.

HARDENING: every task persists its own .npy before any post-processing; tasks
skip if their checkpoint exists (resumable / analyze-only re-run). Threads pinned
to 1 so the ProcessPool isn't oversubscribed by LAPACK.

Run:  ... --probe | --stage A | --stage B [--Lcap L] | --agg   [--workers 18]
"""
from __future__ import annotations

import os
# pin threads BEFORE numpy import (hardened-run pattern)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase35a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from unfold_rotnum import am_eigs, unfold_rotnum, GOLDEN  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
WORK = os.path.join(COORD, "am_work")
os.makedirs(WORK, exist_ok=True)

N_PHI = 16
PHIS = np.arange(N_PHI) / (2 * N_PHI)            # 16 pts in [0,0.5), spacing 1/32
THETA = GOLDEN
CELLS = [
    {"name": "sup_N50k", "N": 50000, "lam": 1.5, "delta": 0.5, "L": 25_600_000},
    {"name": "sup_N70k", "N": 70000, "lam": 1.5, "delta": 0.5, "L": 25_600_000},
    {"name": "sup_N100k", "N": 100000, "lam": 1.5, "delta": 0.5, "L": 6_400_000},
]
CMAP = {c["name"]: c for c in CELLS}


def _eig_f(name, i):
    return os.path.join(WORK, f"eig_{name}_phi{i}.npy")


def _unf_f(name, i, L):
    return os.path.join(WORK, f"unf_{name}_phi{i}_L{L}.npy")


# ── module-level tasks (picklable for ProcessPool) ───────────────────────────
def _eig_task(arg):
    name, i = arg
    c = CMAP[name]
    f = _eig_f(name, i)
    if os.path.exists(f):
        return (name, i, "skip", 0.0)
    t0 = time.perf_counter()
    e = am_eigs(c["lam"], c["N"], float(PHIS[i]), THETA)
    np.save(f, e)
    return (name, i, "ok", time.perf_counter() - t0)


def _unfold_task(arg):
    name, i, Lcap = arg
    c = CMAP[name]
    L = min(c["L"], Lcap) if Lcap else c["L"]
    f = _unf_f(name, i, L)
    if os.path.exists(f):
        return (name, i, "skip", 0.0)
    e = np.load(_eig_f(name, i))
    t0 = time.perf_counter()
    unf = unfold_rotnum(e, c["lam"], THETA, L, phis=(float(PHIS[i]),))
    np.save(f, unf)
    return (name, i, "ok", time.perf_counter() - t0)


def _run_pool(tasks, fn, workers, label):
    print(f"[{label}] {len(tasks)} tasks, {workers} workers")
    t0 = time.perf_counter()
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(fn, t) for t in tasks]
        for fu in as_completed(futs):
            name, i, st, dt = fu.result()
            done += 1
            if st == "ok":
                print(f"  [{label}] {done}/{len(tasks)} {name} φ{i} {dt:.0f}s", flush=True)
    print(f"[{label}] complete in {(time.perf_counter()-t0)/60:.1f} min")


def stage_A(workers):
    _run_pool([(c["name"], i) for c in CELLS for i in range(N_PHI)],
              _eig_task, workers, "A")


def stage_B(workers, Lcap=None):
    tasks = [(c["name"], i, Lcap) for c in CELLS for i in range(N_PHI)]
    missing = [(n, i) for (n, i, _) in tasks if not os.path.exists(_eig_f(n, i))]
    if missing:
        raise SystemExit(f"Stage A incomplete: {len(missing)} eigfiles missing. Run --stage A.")
    _run_pool(tasks, _unfold_task, workers, "B")


def aggregate(Lcap=None):
    from cross_substrate.axes import compute_family_I, compute_family_II
    import datetime
    recs = []
    for c in CELLS:
        L = min(c["L"], Lcap) if Lcap else c["L"]
        files = [_unf_f(c["name"], i, L) for i in range(N_PHI)]
        if not all(os.path.exists(f) for f in files):
            print(f"  agg: {c['name']} L={L} incomplete, skipping")
            continue
        positions = np.concatenate([np.load(f) for f in files])
        fI, fII = compute_family_I(positions), compute_family_II(positions)
        recs.append({
            "substrate": "AM", "cell_id": f"{c['name']}/lam{c['lam']}/Lconv{L}",
            "axes_computed": {**fI, **fII},
            "applicable_axes_not_yet_computed": [],
            "non_applicable_axes": ["V.1_lyapunov", "V.2_correlation_dim"],
            "extraction_method": f"unfold_rotnum @ L={L}, {N_PHI}φ pooled, θ=golden (matched object-a)",
            "extraction_audit": {"N": c["N"], "lam": c["lam"], "delta": c["delta"],
                                 "L_converged": L, "n_phi": N_PHI,
                                 "n_positions": int(positions.size)},
            "source_artifact": f"coordinates/am_work/ (eig+unf checkpoints)",
            "computed_date": datetime.date.today().isoformat()})
        def _fm(v):
            return f"{v:.3f}" if isinstance(v, (int, float)) else str(v)
        print(f"  agg {c['name']} L={L}: {positions.size} pos  "
              f"W1δ={_fm(fI['I.1_w1_clock'])} ks_gue={_fm(fI['I.5_ks_gue'])} "
              f"brody={_fm(fI['I.8_brody_q'])} BRρ={_fm(fI['I.9_berry_robnik_rho'])}")
    if recs:
        with open(os.path.join(COORD, "am.jsonl"), "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        print(f"  → wrote coordinates/am.jsonl ({len(recs)} cells)")


def probe():
    print("AM PHASE-1 COST PROBE")
    for c in CELLS:
        t0 = time.perf_counter(); e = am_eigs(c["lam"], c["N"], 0.0, THETA)
        te = time.perf_counter() - t0
        t1 = time.perf_counter(); unfold_rotnum(e, c["lam"], THETA, 200_000, (0.0,))
        tu = (time.perf_counter() - t1) * (c["L"] / 200_000)
        print(f"  {c['name']}: eig {te:.0f}s/φ, unfold proj {tu/60:.0f}min/φ "
              f"(L={c['L']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--stage", choices=["A", "B"])
    ap.add_argument("--agg", action="store_true")
    ap.add_argument("--Lcap", type=int, default=None)
    ap.add_argument("--workers", type=int, default=18)
    a = ap.parse_args()
    if a.probe:
        probe()
    elif a.stage == "A":
        stage_A(a.workers)
    elif a.stage == "B":
        stage_B(a.workers, a.Lcap)
    elif a.agg:
        aggregate(a.Lcap)
    else:
        ap.error("need --probe / --stage A / --stage B / --agg")


if __name__ == "__main__":
    main()
