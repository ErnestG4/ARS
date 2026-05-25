"""
cross_substrate/population_temporal.py — within-recording TEMPORAL stability of population fingerprints.

Completes the Step-2 stratification triad (area / stimulus / session done; temporal-within-recording is the
missing piece). Splits each (session, area, block) window into EARLY / LATE halves, recomputes the 3
trustable observables (corr-eig / avl-onset / sync-event) per half, and asks whether each observable is
TEMPORALLY STATIONARY within a recording (test-retest q_h1≈q_h2) or DRIFTS — i.e. is the population
landscape position a fixed property of the (area,stimulus) condition, or does it move during the recording?

Per observable: test-retest correlation of half-1 vs half-2 Brody q across all cells, and the within-cell
|Δq| vs the observable's between-cell sd. High test-retest + small within-Δ ⇒ stationary. Out:
coordinates/population-temporal.jsonl + figure P_population_temporal.png. Run: --run [--workers 10].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from cross_substrate.allen_depth import build_targets, NWB_GLOB                       # noqa: E402
from cross_substrate.population_strat import (_block_matrix, _observables, _build_tasks,  # noqa: E402
                                              MIN_UNITS, DT)
from cross_substrate.population_fingerprint import _fp, _f                            # noqa: E402

COORD = os.path.join(_HERE, "coordinates")


def _half_q(h, aurows, t0, t1):
    """Brody q per observable over a single time window."""
    M, per_unit, edges = _block_matrix(h, aurows, t0, t1, DT)
    out = {}
    for name, (obj, _note) in _observables(M, per_unit, edges).items():
        out[name] = _f(_fp(obj, is_positions=True).get("I.8_brody_q")) if (obj is not None and len(obj) >= 50) else None
    return out


def _task(arg):
    f, sid, area, blk, t0, t1, aurows = arg
    tmid = 0.5 * (t0 + t1)
    with h5py.File(f, "r") as h:
        h1 = _half_q(h, aurows, t0, tmid)
        h2 = _half_q(h, aurows, tmid, t1)
    recs = []
    for obs in ("corr-eig", "avl-onset", "sync-event"):
        if isinstance(h1.get(obs), float) and isinstance(h2.get(obs), float):
            recs.append({"substrate": "population-temporal", "cell_id": f"{sid}/{area}/{blk}/{obs}",
                         "session": sid, "area": area, "block": blk, "aggregation": obs,
                         "q_half1": h1[obs], "q_half2": h2[obs], "dq": abs(h1[obs] - h2[obs]),
                         "source_artifact": "generated (early/late half split)",
                         "computed_date": date.today().isoformat()})
    return recs


def run(workers=10):
    targets = build_targets()
    files = sorted(glob.glob(NWB_GLOB))
    tasks = _build_tasks(files, targets, set())
    print(f"TEMPORAL STABILITY — {len(tasks)} (session,area,block) cells split early/late, {workers}w")
    out = os.path.join(COORD, "population-temporal.jsonl")
    t0 = time.perf_counter()
    allrecs = []
    with open(out, "w") as fh, ProcessPoolExecutor(max_workers=workers) as ex:
        for recs in ex.map(_task, tasks):
            for r in recs:
                fh.write(json.dumps(r) + "\n"); fh.flush(); allrecs.append(r)
    print(f"→ {len(allrecs)} half-pairs in {(time.perf_counter()-t0)/60:.1f} min\n")
    _analyse(allrecs)


def _analyse(allrecs):
    from scipy import stats
    print("Per-observable TEMPORAL STATIONARITY (early vs late half, across all cells):")
    print(f"  {'observable':11s} {'n':>4s} {'test-retest ρ':>14s} {'within|Δq|':>11s} {'between-sd':>11s} {'verdict':>20s}")
    summ = {}
    for obs in ("corr-eig", "avl-onset", "sync-event"):
        sub = [r for r in allrecs if r["aggregation"] == obs]
        if len(sub) < 5:
            print(f"  {obs:11s} (too few)"); continue
        q1 = np.array([r["q_half1"] for r in sub]); q2 = np.array([r["q_half2"] for r in sub])
        rho = stats.spearmanr(q1, q2)[0]
        within = float(np.mean(np.abs(q1 - q2)))
        between = float(np.std(np.concatenate([q1, q2])))
        ratio = within / between if between > 1e-9 else np.nan
        verdict = ("STATIONARY" if (within < 0.5 * between and (np.isnan(rho) or rho > 0.4))
                   else "DRIFTS" if within > between else "intermediate")
        summ[obs] = (rho, within, between)
        print(f"  {obs:11s} {len(sub):>4d} {rho:>14.3f} {within:>11.3f} {between:>11.3f} {verdict:>20s}")
    print("  (within|Δq| ≪ between-sd AND high test-retest ⇒ position is a fixed property of the condition,"
          " not drifting during the recording)")
    _figure(allrecs)


def _figure(allrecs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, obs in zip(axes, ("corr-eig", "avl-onset", "sync-event")):
        sub = [r for r in allrecs if r["aggregation"] == obs]
        if not sub:
            continue
        q1 = [r["q_half1"] for r in sub]; q2 = [r["q_half2"] for r in sub]
        ax.scatter(q1, q2, s=24, alpha=0.5, edgecolor="k", linewidth=0.3)
        lim = [min(q1 + q2 + [0]), max(q1 + q2 + [1])]
        ax.plot(lim, lim, "r--", lw=1, label="identity (stationary)")
        ax.set_xlabel("Brody q — early half"); ax.set_ylabel("Brody q — late half")
        ax.set_title(f"{obs} (n={len(sub)})"); ax.legend(fontsize=7); ax.grid(alpha=0.2)
    fig.suptitle("Within-recording temporal stability: early vs late half Brody q (on identity ⇒ stationary)")
    p = os.path.join(_HERE, "figures", "P_population_temporal.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
