"""
cross_substrate/buzsaki_ratematch.py — rate-match de-confound of the CA1 state/epoch avalanche effect (G3).

The framework-port found avl-onset q varies strongly by natural cell (state/epoch), but the avalanche n
swings ~470–210k across states (rate-saturation confound, [[ars_rate_dependence_lesson]]). This applies the
SAME population-level rate-match recipe as Allen: within each session, the natural cells share the SAME CA1
units (unit-count auto-matched), so we thin each contrast pair to a COMMON total spike-count and recompute
avl-onset q (K repeats averaged). If the named contrast survives matching ⇒ state effect is rate-INDEPENDENT.

Named contrasts (the consolidation literature's questions):
  NonREM_consolidation  PRE-NonREM vs POST-NonREM
  REM_consolidation     PRE-REM    vs POST-REM
  wake_state            Maze-Awake vs Awake-in-sleep

Out: coordinates/buzsaki-ratematch.jsonl + prints the matched contrasts. Run: --run [--all] [--workers N].
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

from cross_substrate.population_fingerprint import _avalanche_onsets, _fp, _f   # noqa: E402
from cross_substrate.buzsaki_port import _natural_cells, BUZ_GLOB              # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
K_REPEATS = 5
MIN_MATCH = 1000           # need enough spikes post-thin for a meaningful avalanche NNS
SEED = 20260525
CONTRASTS = [("NonREM_consolidation", "PRE-NonREM", "POST-NonREM"),
             ("REM_consolidation", "PRE-REM", "POST-REM"),
             ("wake_state", "Maze-Awake", "Awake-in-sleep")]


def _pooled(per_unit_all, intervals):
    out = []
    for spk in per_unit_all:
        for (s, e) in intervals:
            out.append(spk[(spk >= s) & (spk < e)])
    return np.sort(np.concatenate(out)) if out else np.zeros(0)


def _avl_q(pooled, rng, r_match):
    if pooled.size > r_match:
        pooled = np.sort(rng.choice(pooled, r_match, replace=False))
    if pooled.size < 200:
        return None
    isi = np.diff(pooled); dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
    onsets = _avalanche_onsets(pooled, dt_av)
    if onsets is None or len(onsets) < 50:
        return None
    return _f(_fp(onsets, is_positions=True).get("I.8_brody_q"))


def _task(arg):
    f, sid = arg
    rng = np.random.default_rng(SEED + abs(hash(sid)) % 9999)
    with h5py.File(f, "r") as h:
        sti = h["units/spike_times_index"][:]; st_all = h["units/spike_times"]
        nU = len(sti)
        per_unit_all = [st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])] for i in range(nU)]
        cells = _natural_cells(h)
    out = []
    for name, a, b in CONTRASTS:
        if a not in cells or b not in cells:
            continue
        pa, pb = _pooled(per_unit_all, cells[a]), _pooled(per_unit_all, cells[b])
        r_match = int(min(pa.size, pb.size))
        if r_match < MIN_MATCH:
            out.append({"session": sid, "contrast": name, "a": a, "b": b, "r_match": r_match,
                        "q_a": None, "q_b": None, "note": "underpowered"})
            continue
        qa = [q for q in (_avl_q(pa, rng, r_match) for _ in range(K_REPEATS)) if isinstance(q, float)]
        qb = [q for q in (_avl_q(pb, rng, r_match) for _ in range(K_REPEATS)) if isinstance(q, float)]
        out.append({"session": sid, "contrast": name, "a": a, "b": b, "r_match": r_match,
                    "n_a": int(pa.size), "n_b": int(pb.size),
                    "q_a": float(np.mean(qa)) if qa else None,
                    "q_b": float(np.mean(qb)) if qb else None})
    return out


def run(all_sessions=False, workers=8):
    files = sorted(glob.glob(BUZ_GLOB))
    if not all_sessions:
        files = files[:3]
    tasks = [(f, os.path.basename(f).replace(".nwb", "")) for f in files]
    print(f"BUZSAKI G3 RATE-MATCH — {len(tasks)} sessions, contrasts thinned to common spike-count, K={K_REPEATS}")
    out = open(os.path.join(COORD, "buzsaki-ratematch.jsonl"), "w")
    t0 = time.perf_counter(); allrecs = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for recs in ex.map(_task, tasks):
            for r in recs:
                r["computed_date"] = date.today().isoformat()
                out.write(json.dumps(r) + "\n"); allrecs.append(r)
    out.close()
    print(f"→ {len(allrecs)} contrast×session in {(time.perf_counter()-t0)/60:.1f} min\n")
    print("Per-contrast matched avalanche q (a→b), does the raw state effect survive rate-matching?")
    for name, a, b in CONTRASTS:
        rows = [r for r in allrecs if r["contrast"] == name and isinstance(r.get("q_a"), float)
                and isinstance(r.get("q_b"), float)]
        if not rows:
            n_under = sum(1 for r in allrecs if r["contrast"] == name)
            print(f"  {name:22s} {a}→{b}: no powered sessions ({n_under} underpowered)")
            continue
        da = np.mean([r["q_a"] for r in rows]); db = np.mean([r["q_b"] for r in rows])
        deltas = [r["q_b"] - r["q_a"] for r in rows]
        consistent = all(d > 0 for d in deltas) or all(d < 0 for d in deltas)
        print(f"  {name:22s} {a}({da:.3f})→{b}({db:.3f})  Δ={db-da:+.3f}  "
              f"n={len(rows)} sess, R_match≈{int(np.mean([r['r_match'] for r in rows]))}  "
              f"{'SIGN-CONSISTENT' if consistent else 'sign-varies'}")
    print("\n(matched = unit-count auto-equal [same CA1 units] + spike-count thinned to common R_match) "
          "Flag, don't interpret — verdict is Will's.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.run:
        run(all_sessions=a.all, workers=a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
