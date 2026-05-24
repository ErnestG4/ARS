"""
cross_substrate/allen_depth.py — Allen Brain Observatory depth-extension (Tier-1 neuro pivot).

Scales Phase-2a (719 cells, 1 session, V1, drifting-gratings only) to the full cached corpus:
12 sessions × 6 visual areas (V1/LM/RL/AL/PM/AM) + LGN × 8 stimulus blocks → ~8,583 good units,
~68k (cell, stimulus) fingerprints. NO download — all NWBs already cached locally (Phase 24).

Per (cell, stimulus): gap-removed spike train within that stimulus's presentations →
  I.5q (q-banded ks-GUE, ars_classify) + matched I.5 (unfold_unit_mean) + W1δ,
tagged with recording area + per-cell tuning (OSI/DSI/pref-SF/pref-TF/F1F0/run-mod). The proxy
verdict (I.5q≈I.5, n≥100, not strong-stimulus-locked) means q-banded placement is trustable at scale.

Cross-reference hooks (post-processing on the banked coordinates):
  • H1 OSI↔ks_gue ACROSS areas (cross-area generality, complements cross-species);
  • tuning-dim privilege (does DSI/SF/TF/F1F0 each couple, or is OSI special?);
  • Family VII |I.5q−I.5| OSI-grading at 12× scale (stays pvc-11-specific / absent in mouse?);
  • cross-area landscape position (visual-cortex cluster vs functional split);
  • within-cell stimulus-state trajectory (does a cell's universality class shift with stimulus?).

Incremental per-session banking → resumable (skips sessions already in the output). Reuses the
validated h5py-direct extraction + ars_classify (allensdk version-mismatches these legacy NWBs).

Run:  --probe [--session N]  |  --run [--workers 10]
Out:  coordinates/allen-depth.jsonl  (+ allen_depth_targets.csv reference)
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
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a"), os.path.join(_ROOT, "phase35a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify, unfold_unit_mean                  # noqa: E402
from cross_substrate.axes import canonical_spacings, I5_ks_gue, I1_w1_clock  # noqa: E402

CACHE = "/home/combust/fmexplorer/allen_cache"
NWB_GLOB = CACHE + "/session_*/session_*.nwb"
COORD = os.path.join(_HERE, "coordinates")
OUT = os.path.join(COORD, "allen-depth.jsonl")

TARGET_AREAS = {"VISp": "V1", "VISl": "LM", "VISrl": "RL", "VISal": "AL",
                "VISpm": "PM", "VISam": "AM", "LGd": "LGN"}
STIMULI = ["drifting_gratings", "static_gratings", "natural_movie_one",
           "natural_movie_three", "natural_scenes", "gabors", "flashes", "spontaneous"]
TUNING = ["g_osi_dg", "g_dsi_dg", "pref_sf_sg", "pref_tf_dg", "f1_f0_dg", "run_mod_dg"]
MIN_SPIKES = 50


# ── target table: good units in target areas, with area + per-session tuning ─────
def build_targets():
    cached = [int(os.path.basename(os.path.dirname(f)).split("_")[1])
              for f in glob.glob(NWB_GLOB)]
    pr = pd.read_csv(f"{CACHE}/probes.csv", low_memory=False)
    scol = [c for c in pr.columns if "session" in c.lower()][0]
    pr = pr.rename(columns={"id": "probe_id", scol: "session_id"})[["probe_id", "session_id"]]
    ch = pd.read_csv(f"{CACHE}/channels.csv", low_memory=False).rename(columns={"id": "chan_id"})
    ch = ch.merge(pr, left_on="ecephys_probe_id", right_on="probe_id")
    ch = ch[["chan_id", "ecephys_structure_acronym", "session_id"]]
    u = pd.read_csv(f"{CACHE}/units.csv", low_memory=False)
    m = u.merge(ch, left_on="ecephys_channel_id", right_on="chan_id")
    m = m[(m["quality"] == "good")
          & (m["ecephys_structure_acronym"].isin(TARGET_AREAS))
          & (m["session_id"].isin(cached))].copy()
    tun = []
    for sid in m["session_id"].unique():
        amf = f"{CACHE}/session_{sid}/session_{sid}_analysis_metrics.csv"
        if os.path.exists(amf):
            t = pd.read_csv(amf, low_memory=False)
            keep = ["ecephys_unit_id"] + [c for c in TUNING if c in t.columns]
            tun.append(t[keep])
    if tun:
        tun = pd.concat(tun, ignore_index=True)
        m = m.merge(tun, left_on="id", right_on="ecephys_unit_id", how="left")
    out = m[["id", "session_id", "ecephys_structure_acronym"]
            + [c for c in TUNING if c in m.columns]].rename(
        columns={"id": "unit_id", "ecephys_structure_acronym": "area"})
    return out


def extract_train(spk, starts, stops):
    """Gap-removed concatenation of spikes within [start,stop] windows (matched to pvc-11)."""
    order = np.argsort(starts)
    chunks, off = [], 0.0
    for k in order:
        s0, s1 = starts[k], stops[k]
        i0 = np.searchsorted(spk, s0, "left")
        i1 = np.searchsorted(spk, s1, "left")
        chunks.append(spk[i0:i1] - s0 + off)
        off += (s1 - s0)
    return np.sort(np.concatenate(chunks)) if chunks else np.zeros(0)


def _f(v):
    return None if v is None or not np.isfinite(v) else float(v)


# ── module-level classify task (picklable) ───────────────────────────────────────
def _task(arg):
    meta, train = arg
    cl = classify(train)
    i5q = cl.get("ks_gue_med") if isinstance(cl, dict) else None
    pos = unfold_unit_mean(train)
    s = canonical_spacings(pos)
    rec = dict(meta)
    rec["n"] = int(train.size)
    rec["axes_computed"] = {"I.5q_ks_gue_med": _f(i5q),
                            "I.5_ks_gue": _f(I5_ks_gue(s)),
                            "I.1_w1_clock": _f(I1_w1_clock(s))}
    return rec


def _session_tasks(h, sess_rows, sess_id):
    """Build (meta, train) tasks for all target units × stimuli in one open NWB."""
    ids = h["units/id"][:]
    row_of = {int(u): r for r, u in enumerate(ids)}
    sti = h["units/spike_times_index"]
    # stimulus windows (present blocks only)
    windows = {}
    for stim in STIMULI:
        key = f"intervals/{stim}_presentations"
        if key in h:
            windows[stim] = (h[key]["start_time"][:], h[key]["stop_time"][:])
    tasks = []
    for _, ur in sess_rows.iterrows():
        u = int(ur["unit_id"])
        r = row_of.get(u)
        if r is None:
            continue
        lo = 0 if r == 0 else int(sti[r - 1])
        hi = int(sti[r])
        spk = h["units/spike_times"][lo:hi]      # read once, reuse across stimuli
        tun = {t: (_f(ur[t]) if t in ur and pd.notna(ur[t]) else None) for t in TUNING}
        for stim, (st, sp) in windows.items():
            train = extract_train(spk, st, sp)
            if train.size < MIN_SPIKES:
                continue
            meta = {"substrate": "allen-depth",
                    "cell_id": f"{sess_id}/u{u}/{stim}",
                    "session": sess_id, "unit_id": u, "area": ur["area"],
                    "stimulus": stim, "tuning": tun}
            tasks.append((meta, train))
    return tasks


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


def _drain(futs, fh, block=False):
    """Write results of completed futures; return still-pending list. block=True drains all.
    (Non-blocking drain bounds memory + lets the next session's cold read overlap classify.)"""
    keep, n = [], 0
    for fu in futs:
        if block or fu.done():
            rec = fu.result()
            if fh:
                fh.write(json.dumps(rec) + "\n")
            n += 1
        else:
            keep.append(fu)
    if fh and n:
        fh.flush()
    return keep, n


def run(workers, probe=False, only_session=None):
    targets = build_targets()
    targets.to_csv(os.path.join(COORD, "allen_depth_targets.csv"), index=False)
    print(f"targets: {len(targets)} good units in {targets['area'].nunique()} areas, "
          f"{targets['session_id'].nunique()} sessions; {workers} workers (classify probed knee)")
    files = sorted(glob.glob(NWB_GLOB))
    if only_session is not None:
        files = [f for f in files if f"session_{only_session}" in f]
    done = set() if probe else _done_sessions()
    fh = None if probe else open(OUT, "a" if os.path.exists(OUT) else "w")
    grand = 0
    t_all = time.perf_counter()
    # ONE persistent pool: submit each session's tasks (non-blocking), then read the NEXT
    # session while the pool classifies → cold I/O (~4min) hides under classify CPU (~11min).
    # Reads stay single-stream sequential (rotational disk; no read fan-out).
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = []
        for f in files:
            sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
            if sid in done:
                print(f"  session {sid}: already banked, skip")
                continue
            sess_rows = targets[targets["session_id"] == sid]
            t0 = time.perf_counter()
            with h5py.File(f, "r") as h:
                tasks = _session_tasks(h, sess_rows, sid)
            if probe:
                tasks = tasks[:200]
            for t in tasks:
                futs.append(ex.submit(_task, t))
            futs, n = _drain(futs, fh)          # opportunistic, non-blocking (overlap)
            grand += n
            print(f"  session {sid}: {len(sess_rows)} units → {len(tasks)} (cell,stim) tasks "
                  f"submitted  [read+extract {time.perf_counter()-t0:.0f}s; {n} drained, "
                  f"{len(futs)} in flight]", flush=True)
            if probe:
                break
        futs, n = _drain(futs, fh, block=True)  # final blocking drain
        grand += n
    if fh:
        fh.close()
    dt = time.perf_counter() - t_all
    print(f"\n→ {grand} (cell,stimulus) records banked to {os.path.relpath(OUT, _HERE)} "
          f"in {dt/60:.1f} min")
    if probe:
        print(f"  PROBE: {grand} cells in {dt:.0f}s → {grand/dt:.1f} cells/s → "
              f"~53k cells ≈ {53000/max(0.1,grand/dt)/3600:.1f} h")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--session", type=int, default=None)
    ap.add_argument("--workers", type=int, default=14)   # classify knee (probed; compute-bound)
    a = ap.parse_args()
    if a.probe:
        run(a.workers, probe=True, only_session=a.session)
    elif a.run:
        run(a.workers, only_session=a.session)
    else:
        ap.error("need --probe or --run")


if __name__ == "__main__":
    main()
