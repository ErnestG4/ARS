"""
cross_substrate/population_strat.py — STRATIFIED population fingerprints (Step 2 of the neural arc).

The population study found population-level fingerprints FRAGMENT by aggregation (corr-eig→GUE,
avl-onset→intermediate, sync-event→Poisson), consistent across 12 sessions. This stratifies the 3
TRUSTABLE observables (drops the rate-peak artifact) along three axes to ask what STRUCTURES the
population position:
  • STIMULUS  — 8 blocks (spontaneous / drifting_gratings / static_gratings / natural_scenes /
                natural_movie_one|three / gabors / flashes): do the observables trace a COHERENT
                trajectory across stimuli, or scatter?
  • AREA      — VISp/VISl/VISrl/VISal/VISpm/VISam/LGd: does cortical area set the population position
                (the population analogue of the per-cell H1-across-areas finding)?
  • SESSION   — within-session (across blocks) vs cross-session: population fingerprint stability.

Per (session, area, block, observable): subset units to the area, build the population aggregate,
fingerprint (I.5q + Family I + Σ²/Δ₃). Reuses population_fingerprint's validated observables/_fp.
Incremental + resumable per session (I/O-bound). Out: coordinates/population-strat.jsonl.
Run: --run [--sessions N] (default: smoke-test on 1 session; --all for 12).
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

from ars_classify import classify                                              # noqa: E402
from cross_substrate.allen_depth import build_targets, NWB_GLOB                # noqa: E402
from cross_substrate.population_fingerprint import (                            # noqa: E402
    _corr_eig, _avalanche_onsets, _sync_events, _fp, _f)

COORD = os.path.join(_HERE, "coordinates")
BLOCKS = ["spontaneous", "drifting_gratings", "static_gratings", "natural_scenes",
          "natural_movie_one", "natural_movie_three", "gabors", "flashes"]
MIN_UNITS = 30            # corr-eig needs a populated bulk after MP filtering
DT = 0.025                # 25 ms bins (matches population_fingerprint)


def _block_matrix(h, urows, t0, t1, dt):
    """Count matrix (T×N) + per-unit spike arrays over [t0,t1]; built ONCE per block, sliced by area."""
    sti = h["units/spike_times_index"]
    st_all = h["units/spike_times"]
    nb = max(4, int((t1 - t0) / dt))
    edges = np.linspace(t0, t1, nb + 1)
    cols, per_unit = [], []
    for r in urows:
        lo = 0 if r == 0 else int(sti[r - 1])
        hi = int(sti[r])
        spk = st_all[lo:hi]
        spk = spk[(spk >= t0) & (spk < t1)]
        cols.append(np.histogram(spk, bins=edges)[0])
        per_unit.append(spk)
    M = np.array(cols, float).T if cols else np.zeros((nb, 0))
    return M, per_unit, edges


def _observables(M, per_unit, edges):
    """The 3 trustable aggregates from a (sub)population. Returns {name: (positions, note)}."""
    pooled = np.sort(np.concatenate(per_unit)) if per_unit else np.zeros(0)
    isi = np.diff(pooled)
    dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
    return {
        "corr-eig":   (_corr_eig(M),                     "spectral — no extractor"),
        "avl-onset":  (_avalanche_onsets(pooled, dt_av), "point process"),
        "sync-event": (_sync_events(M, edges),           "threshold-extractor (FLAGGED)"),
    }


def _task(arg):
    """One (session, area, block) cell → up to 3 observable records. Worker re-opens the NWB."""
    f, sid, area, blk, tb0, tb1, aurows = arg
    out = []
    with h5py.File(f, "r") as h:
        M, per_unit, edges = _block_matrix(h, aurows, tb0, tb1, DT)
    for name, (obj, note) in _observables(M, per_unit, edges).items():
        if obj is None or len(obj) < 50:
            continue
        fp = _fp(obj, is_positions=True)
        try:
            i5q = _f(classify(np.sort(np.asarray(obj, float))).get("ks_gue_med"))
        except Exception:
            i5q = None
        out.append({"substrate": "population-strat",
                    "cell_id": f"{sid}/{area}/{blk}/{name}", "session": sid,
                    "area": area, "block": blk, "aggregation": name,
                    "n_units": len(aurows), "n": int(len(obj)),
                    "axes_computed": {"I.5q_ks_gue_med": i5q, **fp},
                    "extraction_audit": {"note": note},
                    "source_artifact": "generated (area-stratified population aggregation)",
                    "computed_date": date.today().isoformat()})
    return out


def _build_tasks(files, targets, done):
    """Serial pre-pass: open each NWB once to read block windows + unit rows; emit (session,area,block) tasks."""
    tasks = []
    for f in files:
        sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
        if sid in done:
            continue
        srows = targets[targets["session_id"] == sid]
        areas = [a for a, c in srows.groupby("area").size().items() if c >= MIN_UNITS]
        with h5py.File(f, "r") as h:
            row_of = {int(u): r for r, u in enumerate(h["units/id"][:])}
            for blk in BLOCKS:
                key = f"intervals/{blk}_presentations"
                if key not in h:
                    continue
                st, sp = h[key]["start_time"][:], h[key]["stop_time"][:]
                tb0, tb1 = float(st.min()), float(sp.max())
                for area in areas:
                    aurows = [row_of[int(u)] for u in srows[srows["area"] == area]["unit_id"].astype(int)
                              if int(u) in row_of]
                    if len(aurows) >= MIN_UNITS:
                        tasks.append((f, sid, area, blk, tb0, tb1, aurows))
    return tasks


def run(n_sessions=1, all_sessions=False, workers=10):
    targets = build_targets()
    files = sorted(glob.glob(NWB_GLOB))
    if not all_sessions:
        files = files[:n_sessions]
    out = os.path.join(COORD, "population-strat.jsonl")
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                done.add((json.loads(line)["session"], json.loads(line)["area"], json.loads(line)["block"]))
            except Exception:
                pass
    tasks = [t for t in _build_tasks(files, targets, set())
             if (t[1], t[2], t[3]) not in done]
    print(f"STRATIFIED POPULATION FINGERPRINTS — {len(tasks)} (session,area,block) cells, {workers} workers")
    print(f"{'sess':>9s} {'area':>6s} {'block':17s} {'agg':11s} {'nU':>4s} {'n':>7s} "
          f"{'I.5q':>6s} {'q':>6s} {'BRρ':>6s}")
    fh = open(out, "a" if done else "w")
    t0all = time.perf_counter()
    n_total = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for recs in ex.map(_task, tasks):
            for rec in recs:
                fh.write(json.dumps(rec) + "\n"); fh.flush()
                n_total += 1
                ax = rec["axes_computed"]
                def g(k):
                    v = ax.get(k)
                    return f"{v:.3f}" if isinstance(v, float) else "  -"
                print(f"{rec['session']:>9d} {rec['area']:>6s} {rec['block']:17s} {rec['aggregation']:11s} "
                      f"{rec['n_units']:>4d} {rec['n']:>7d} {g('I.5q_ks_gue_med'):>6s} "
                      f"{g('I.8_brody_q'):>6s} {g('I.9_berry_robnik_rho'):>6s}", flush=True)
    fh.close()
    print(f"\n→ {n_total} stratified fingerprints in {(time.perf_counter()-t0all)/60:.1f} min "
          f"→ {os.path.basename(out)}. Analyse with population_strat_analysis.py. Flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sessions", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.sessions, all_sessions=a.all, workers=a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
