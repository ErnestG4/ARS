"""
recompute_coordinates_kuramoto.py — recompute the kuramoto block of the coordinate store
on the REPAIRED signed repulsion integral.

WHY THIS SUBSTRATE FIRST. The store's `ARS.rep_med` was computed with the `np.maximum(0, ·)` clip
(R-093/R-094), which saturates to exactly 0 for any clustered band and erases the magnitude. A
recompute needs the RAW EVENT TIMES -- and the banked `source_artifact` files are RESULTS tables
(`rep_int_per_q` and friends, ~500 bytes/cell), not spike trains. So recomputability is decided
per substrate by whether its raw input can be regenerated:

  kuramoto  6361 records  SIMULATED, and the parquet banks (K, seed, N) for all 63 cells with
                          seeds {0,1,2} -- so it is EXACTLY regenerable with no external data.
  pvc-11    1159          needs crcns_cache (present, 630M)
  allen-np   544          needs allen_cache (present, 29G)
  Tier B   19619 brody    "generated (...)" procedures over the big caches; separate job.

THE BUILT-IN POWERED CHECK. This does not merely compute the repaired value -- it recomputes the
DEPLOYED `rep_med` too and asserts it reproduces the banked parquet. A repaired number from a
pipeline that cannot reproduce its own banked output is worthless, and the reproduction is the only
evidence the simulation, seeds, unfolding and q-banding were all re-entered correctly.

NON-DESTRUCTIVE. Writes a NEW file; the original jsonl and parquet are untouched.

Run:  $HOME/fmexplorer/bin/python3 cross_substrate/recompute_coordinates_kuramoto.py [--cells N]
Writes: cross_substrate/coordinates/kuramoto.repaired.jsonl
        cross_substrate/coordinates/kuramoto_recompute_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, os.path.join(_ROOT, "phase30"), os.path.join(_ROOT, "phase22a")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from kuramoto import simulate, per_oscillator_rates            # noqa: E402
from ars_classify import classify, Q_MAX, MIN_EVENTS_PER_Q     # noqa: E402

# locked sim parameters, copied verbatim from phase30/analysis1_K_sweep.py
OMEGA_0 = 2.0 * np.pi * 2.0
GAMMA = 2.0 * np.pi * 1.0
DT, T_SIM, T_TRANSIENT, N_DEFAULT = 0.005, 1200.0, 200.0, 100
SEEDS = [0, 1, 2]
BANKED = os.path.join(_ROOT, "data", "phase30_results",
                      "analysis1_per_oscillator_real.parquet")
OUT_JSONL = os.path.join(_HERE, "coordinates", "kuramoto.repaired.jsonl")
OUT_REPORT = os.path.join(_HERE, "coordinates", "kuramoto_recompute_report.json")
p_ = lambda *a: print(*a, flush=True)


def _one(ev):
    """Module-level so the worker pool can pickle it (same shape as the original
    sweep's parallel_classify -- a serial rewrite was ~40x slower and would have
    made the recompute look infeasible when it is not)."""
    return classify(ev, return_full=False, q_max=Q_MAX)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", type=int, default=0, help="limit cells (0 = all)")
    args = ap.parse_args()

    banked = pd.read_parquet(BANKED)
    cells = banked[["K", "seed", "N"]].drop_duplicates().sort_values(["K", "seed"])
    if args.cells:
        cells = cells.head(args.cells)
    p_("=" * 84)
    p_("KURAMOTO COORDINATE RECOMPUTE — deployed rep_med reproduced, signed rep_med added")
    p_(f"  banked rows {len(banked)}   cells {len(cells)}   seeds {SEEDS}")
    p_("=" * 84)

    recs, repro_ok, repro_bad, t0 = [], 0, 0, time.time()
    for ci, (_, row) in enumerate(cells.iterrows(), 1):
        K, seed, N = float(row.K), int(row.seed), int(row.N)
        sim = simulate(K=K, sigma=0.0, N=N, omega_0=OMEGA_0, gamma=GAMMA,
                       dt=DT, T_sim=T_SIM, T_transient=T_TRANSIENT,
                       seed=seed, record_r=True, r_downsample=200)
        rates = per_oscillator_rates(sim)
        sub = banked[(banked.K == K) & (banked.seed == seed)].set_index("i")
        # SERIAL by choice: a per-cell `with Pool(...)` deadlocked on teardown across 63
        # create/destroy cycles.
        # ⚠ COST, corrected -- my first estimate was a THIN SLICE, the same sampling error
        # gate0f was written about. I timed sim.spikes[0] (n=157) at 0.23 s and projected 6
        # minutes. The MEDIAN oscillator has n=2304 and the max 11247, costing 2-3 s each, so
        # the true cost is ~4 min/cell and ~4.5 h for the sweep. Time the median, never the
        # first element.
        todo = [(i, ev) for i, ev in enumerate(sim.spikes) if ev.size >= MIN_EVENTS_PER_Q]
        out = [_one(ev) for _, ev in todo]
        for (i, ev), r in zip(todo, out):
            b = sub.loc[i] if i in sub.index else None
            dep, sig = r["rep_med"], r.get("rep_med_signed", float("nan"))
            if b is not None and np.isfinite(b.rep_med) and np.isfinite(dep):
                if abs(dep - float(b.rep_med)) < 1e-9:
                    repro_ok += 1
                else:
                    repro_bad += 1
            recs.append({"substrate": "kuramoto",
                         "cell_id": f"K{K:.6f}_s{seed}_i{i}",
                         "K": K, "K_factor": K / sim.K_c, "seed": seed, "N": N, "i": i,
                         "n_events": int(ev.size), "rate": float(rates[i]),
                         "primary": r["primary"], "n_well": r["n_well"],
                         "axes_computed": {"ARS.rep_med": dep,
                                           "ARS.rep_med_signed": sig},
                         "banked_rep_med": (float(b.rep_med) if b is not None else None),
                         "recompute_date": "2026-07-28",
                         "note": "rep_med reproduces the deployed clipped value; "
                                 "rep_med_signed is the repaired field"})
        if ci % 5 == 0 or ci == len(cells):
            p_(f"  cell {ci}/{len(cells)}  K={K:.3f} seed={seed}  "
               f"rows={len(recs)}  repro ok/bad={repro_ok}/{repro_bad}  "
               f"{time.time()-t0:.0f}s")

    dep = np.array([r["axes_computed"]["ARS.rep_med"] for r in recs], float)
    sig = np.array([r["axes_computed"]["ARS.rep_med_signed"] for r in recs], float)
    m = np.isfinite(dep) & np.isfinite(sig)
    sat = int((dep[m] == 0.0).sum())
    moved = int((np.abs(dep[m] - sig[m]) > 1e-9).sum())

    p_("\n" + "-" * 84)
    p_(f"  REPRODUCTION of the deployed value: {repro_ok} match, {repro_bad} mismatch")
    if repro_bad:
        p_("  *** the pipeline does NOT reproduce its own banked output — the repaired numbers")
        p_("      below are NOT trustworthy and must not be banked. ***")
    p_(f"  cells with finite pair      : {int(m.sum())}")
    p_(f"  deployed exactly 0 (saturated): {sat}  ({100*sat/max(m.sum(),1):.1f}%)")
    p_(f"  deployed != signed            : {moved}  ({100*moved/max(m.sum(),1):.1f}%)")
    if m.sum():
        p_(f"  deployed  mean {dep[m].mean():+.4f}  median {np.median(dep[m]):+.4f}  "
           f"min {dep[m].min():+.4f}")
        p_(f"  SIGNED    mean {sig[m].mean():+.4f}  median {np.median(sig[m]):+.4f}  "
           f"min {sig[m].min():+.4f}")
        p_(f"  clipped >= signed on every cell (max(0,x) >= x): "
           f"{bool(np.all(dep[m] >= sig[m] - 1e-12))}")

    with open(OUT_JSONL, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    rep = {"substrate": "kuramoto", "cells": int(len(cells)), "records": len(recs),
           "reproduction_match": repro_ok, "reproduction_mismatch": repro_bad,
           "trustworthy": repro_bad == 0,
           "n_finite_pair": int(m.sum()), "n_deployed_saturated_zero": sat,
           "n_changed": moved,
           "deployed": {"mean": float(dep[m].mean()), "median": float(np.median(dep[m])),
                        "min": float(dep[m].min())} if m.sum() else None,
           "signed": {"mean": float(sig[m].mean()), "median": float(np.median(sig[m])),
                      "min": float(sig[m].min())} if m.sum() else None}
    with open(OUT_REPORT, "w") as f:
        json.dump(rep, f, indent=2)
    p_(f"\n-> wrote {OUT_JSONL}\n-> wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
