"""
cross_substrate/buzsaki_port.py — framework-port of the Allen population+per-cell fingerprints to CA1.

Applies the IDENTICAL tooling (ars_classify, the 3 trustable population observables, _fp) to Grosmark &
Buzsáki CA1 (DANDI 000044), to test whether the Allen cross-substrate findings GENERALISE. Fair-comparison:
same observables / classify / dt=25ms / MIN_UNITS=30 / _fp as Allen — no mid-substrate method changes.

STRATIFICATION (ratified): NATURAL CELLS (state within epoch), cell-type orthogonal.
  natural cells: PRE-NonREM, PRE-REM, Maze-Awake, POST-NonREM, POST-REM, Awake-in-sleep (disentangle ctrl).
  cell-type groups: all / excitatory(pyramidal) / inhibitory(interneuron).
Per (session, natural_cell, cell_type): the 3 population observables (corr-eig/avl-onset/sync-event) + per
that cell's units, per-cell ks_gue + Family I. Reuses population_fingerprint observables verbatim.

Out: coordinates/buzsaki-port-pop.jsonl + buzsaki-port-cell.jsonl. Run: --run [--sessions N | --all].
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
from cross_substrate.axes import canonical_spacings, FAMILY_I, family_local                 # noqa: E402
from cross_substrate.population_fingerprint import (_corr_eig, _avalanche_onsets,  # noqa: E402
                                                    _sync_events, _fp, _f)

BUZ_GLOB = "$HOME/fmexplorer/buzsaki_cache/*.nwb"
COORD = os.path.join(_HERE, "coordinates")
DT = 0.025
MIN_UNITS = 30
SLEEP_EPOCHS = ("PRE", "POST")


def _decode(arr):
    return [x.decode() if isinstance(x, bytes) else x for x in arr]


def _natural_cells(h):
    """Build {natural_cell_name: [(start,stop),...]} = state intervals clipped to epoch windows."""
    ep = h["intervals/epochs"]
    elab = _decode(ep["label"][:]); est, esp = ep["start_time"][:], ep["stop_time"][:]
    epochs = {}
    for l, s, e in zip(elab, est, esp):
        epochs[l.replace("Epoch", "")] = (float(s), float(e))   # PRE / Maze / POST
    st = h["processing/behavior/states"]
    slab = _decode(st["label"][:]); sst, ssp = st["start_time"][:], st["stop_time"][:]
    def clip(state, epoch):
        e0, e1 = epochs[epoch]
        out = []
        for l, s, e in zip(slab, sst, ssp):
            if l == state:
                a, b = max(float(s), e0), min(float(e), e1)
                if b - a > 1.0:
                    out.append((a, b))
        return out
    cells = {}
    if "PRE" in epochs:
        cells["PRE-NonREM"] = clip("Non-REM", "PRE"); cells["PRE-REM"] = clip("REM", "PRE")
    if "Maze" in epochs:
        cells["Maze-Awake"] = clip("Awake", "Maze")
    if "POST" in epochs:
        cells["POST-NonREM"] = clip("Non-REM", "POST"); cells["POST-REM"] = clip("REM", "POST")
    # disentangle-control: brief wake within sleep epochs
    aws = []
    for ce in SLEEP_EPOCHS:
        if ce in epochs:
            aws += clip("Awake", ce)
    cells["Awake-in-sleep"] = aws
    return {k: v for k, v in cells.items() if v}


def _multi_matrix(per_unit_all, intervals, dt):
    """Stack per-interval count matrices + pool spikes (natural cell = concatenated disjoint intervals)."""
    cols = [[] for _ in per_unit_all]; pooled = [[] for _ in per_unit_all]
    for (s, e) in intervals:
        nb = max(2, int((e - s) / dt)); edges = np.linspace(s, e, nb + 1)
        for i, spk in enumerate(per_unit_all):
            sel = spk[(spk >= s) & (spk < e)]
            cols[i].append(np.histogram(sel, bins=edges)[0]); pooled[i].append(sel)
    M = np.array([np.concatenate(c) for c in cols], float).T if cols else np.zeros((0, 0))
    per_unit = [np.sort(np.concatenate(p)) if p else np.zeros(0) for p in pooled]
    return M, per_unit


def _pop_observables(M, per_unit):
    pooled = np.sort(np.concatenate(per_unit)) if per_unit else np.zeros(0)
    isi = np.diff(pooled); dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
    pseudo_edges = np.arange(M.shape[0] + 1) * DT
    return {"corr-eig": _corr_eig(M),
            "avl-onset": _avalanche_onsets(pooled, dt_av),
            "sync-event": _sync_events(M, pseudo_edges)}


def _process(arg):
    """One (session, natural_cell): population (3 cell-types) + per-cell records. Worker re-opens the NWB."""
    f, sid, ncell_name, intervals = arg
    pop_recs, cell_recs = [], []
    with h5py.File(f, "r") as h:
        cell_type = _decode(h["units/cell_type"][:])
        location = _decode(h["units/location"][:]) if "location" in h["units"] else ["?"] * len(cell_type)
        sti = h["units/spike_times_index"][:]; st_all = h["units/spike_times"]
        n_units = len(cell_type)
        per_unit_all = [st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])] for i in range(n_units)]
    ctype_groups = {"all": list(range(n_units)),
                    "excitatory": [i for i in range(n_units) if cell_type[i] == "excitatory"],
                    "inhibitory": [i for i in range(n_units) if cell_type[i] == "inhibitory"]}
    for ct, idxs in ctype_groups.items():
        if len(idxs) < (MIN_UNITS if ct != "inhibitory" else 8):
            continue
        M, per_unit = _multi_matrix([per_unit_all[i] for i in idxs], intervals, DT)
        if M.shape[0] < 50:
            continue
        for agg, obj in _pop_observables(M, per_unit).items():
            if obj is None or len(obj) < 50:
                continue
            fp = _fp(obj, is_positions=True)
            try:
                i5q = _f(classify(np.sort(np.asarray(obj, float))).get("ks_gue_med"))
            except Exception:
                i5q = None
            pop_recs.append({"substrate": "buzsaki-port-pop", "session": sid,
                             "natural_cell": ncell_name, "cell_type": ct, "n_units": len(idxs),
                             "aggregation": agg, "n": int(len(obj)),
                             "axes_computed": {"I.5q_ks_gue_med": i5q, **fp},
                             "source_artifact": "generated (CA1 population aggregation)",
                             "computed_date": date.today().isoformat()})
    for i in range(n_units):
        _, pu = _multi_matrix([per_unit_all[i]], intervals, DT)
        spk = pu[0]
        if spk.size < 50:
            continue
        try:
            i5q = _f(classify(spk).get("ks_gue_med"))
        except Exception:
            i5q = None
        fI = {k: _f(fn(canonical_spacings(spk))) for k, fn in FAMILY_I.items()}; fI.update({k: _f(v) for k, v in family_local(spk).items()})
        cell_recs.append({"substrate": "buzsaki-port-cell", "session": sid, "unit": i,
                          "natural_cell": ncell_name, "cell_type": cell_type[i],
                          "location": location[i], "n": int(spk.size),
                          "axes_computed": {"I.5q_ks_gue_med": i5q, **fI},
                          "source_artifact": "generated (CA1 per-cell spike-time)",
                          "computed_date": date.today().isoformat()})
    return pop_recs, cell_recs


def run(n_sessions=1, all_sessions=False, workers=10):
    files = sorted(glob.glob(BUZ_GLOB))
    if not all_sessions:
        files = files[:n_sessions]
    tasks = []
    for f in files:
        sid = os.path.basename(f).replace(".nwb", "")
        with h5py.File(f, "r") as h:
            for name, intervals in _natural_cells(h).items():
                tasks.append((f, sid, name, intervals))
    pop_out = open(os.path.join(COORD, "buzsaki-port-pop.jsonl"), "w")
    cell_out = open(os.path.join(COORD, "buzsaki-port-cell.jsonl"), "w")
    t0 = time.perf_counter(); npop = ncell = 0
    print(f"BUZSAKI CA1 PORT — {len(files)} session(s), {len(tasks)} (session,natural_cell) tasks, {workers}w")
    print(f"{'session':>18s} {'natural_cell':14s} {'agg':11s} {'nU':>4s} {'n':>7s} {'q':>6s} {'BRρ':>6s}")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for pop_recs, cell_recs in ex.map(_process, tasks):
            for r in pop_recs:
                pop_out.write(json.dumps(r) + "\n"); npop += 1
                if r["cell_type"] == "all":
                    ax = r["axes_computed"]
                    def _g(k):
                        v = ax.get(k)
                        return f"{v:.3f}" if isinstance(v, float) else "  -"
                    print(f"{r['session']:>18s} {r['natural_cell']:14s} {r['aggregation']:11s} "
                          f"{r['n_units']:>4d} {r['n']:>7d} {_g('I.8_brody_q'):>6s} "
                          f"{_g('I.9_berry_robnik_rho'):>6s}", flush=True)
            for r in cell_recs:
                cell_out.write(json.dumps(r) + "\n"); ncell += 1
            pop_out.flush(); cell_out.flush()
    pop_out.close(); cell_out.close()
    print(f"\n→ {npop} population + {ncell} per-cell records in {(time.perf_counter()-t0)/60:.1f} min. "
          "Analyse with buzsaki_port_analysis.py. Flag, don't interpret.")


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
