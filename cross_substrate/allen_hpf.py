"""
cross_substrate/allen_hpf.py — Allen hippocampal-subfield cross-region fingerprint (CA3/CA1/DG/...).

Complement to the 000638 EC-vs-CA3 headline: a well-powered (8 sessions), zero-acquisition comparison on
the DISCRETE-attractor axis within hippocampus. CA3 = autoassociative/discrete attractor; DG = sparse
pattern-separator (non-attractor); CA1 = relay/comparator. NO MEC here (Allen probes don't reach EC), so
this cannot test the continuous-vs-discrete contrast — it characterizes the discrete side + its neighbors.

Identical tooling as Allen V1 / Buzsaki ports (ars_classify ks_gue + Family I per-cell; corr-eig / avl-onset
/ sync-event population observables; dt=25ms). Per (session, region, cell_type): population observables
(all/exc/inh) + per-cell fingerprints. Spontaneous block (intrinsic dynamics; HPF not visually driven).
Cell-type via waveform duration (<0.4ms = putative inhibitory/FS, else excitatory/RS). Rate stats banked
per record so cross-region comparison can rate-match downstream.

Out: coordinates/allen-hpf-cell.jsonl + allen-hpf-pop.jsonl.  Run: --run [--all] [--workers N].
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
from datetime import date

import numpy as np
import pandas as pd
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                             # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, family_local                # noqa: E402
from cross_substrate.population_fingerprint import (_corr_eig, _avalanche_onsets,  # noqa: E402
                                                    _sync_events, _fp, _f)

CACHE = "$HOME/fmexplorer/allen_cache"
NWB_GLOB = CACHE + "/session_*/session_*.nwb"
COORD = os.path.join(_HERE, "coordinates")
HPF_REGIONS = ("CA1", "CA2", "CA3", "DG", "SUB", "ProS", "POST", "PRE")
DT = 0.025
MIN_UNITS = 20
FS_DUR = 0.4   # ms; waveform duration < this = putative inhibitory (fast-spiking)


def build_hpf_targets():
    """Good HPF units per cached session, with region (structure acronym) + waveform cell-type."""
    cached = [int(os.path.basename(os.path.dirname(f)).split("_")[1]) for f in glob.glob(NWB_GLOB)]
    pr = pd.read_csv(f"{CACHE}/probes.csv", low_memory=False)
    scol = [c for c in pr.columns if "session" in c.lower()][0]
    pr = pr.rename(columns={"id": "probe_id", scol: "session_id"})[["probe_id", "session_id"]]
    ch = pd.read_csv(f"{CACHE}/channels.csv", low_memory=False).rename(columns={"id": "chan_id"})
    ch = ch.merge(pr, left_on="ecephys_probe_id", right_on="probe_id")
    ch = ch[["chan_id", "ecephys_structure_acronym", "session_id"]]
    u = pd.read_csv(f"{CACHE}/units.csv", low_memory=False)
    m = u.merge(ch, left_on="ecephys_channel_id", right_on="chan_id")
    m = m[(m["quality"] == "good")
          & (m["ecephys_structure_acronym"].isin(HPF_REGIONS))
          & (m["session_id"].isin(cached))].copy()
    m["region"] = m["ecephys_structure_acronym"]
    m["cell_type"] = np.where(m["duration"] < FS_DUR, "inhibitory", "excitatory")
    return m[["id", "session_id", "region", "cell_type", "firing_rate", "duration"]]


def _burst_stats(spk):
    """Intrinsic ISI/burst structure (P2.4): burst fraction (ISI<10ms), CV(ISI), local CV2."""
    isi = np.diff(np.sort(spk))
    isi = isi[isi > 0]
    if isi.size < 10:
        return {"burst_frac": None, "cv_isi": None, "cv2": None}
    burst_frac = float(np.mean(isi < 0.010))
    cv = float(np.std(isi) / np.mean(isi)) if np.mean(isi) > 0 else None
    d = np.abs(np.diff(isi))
    s = isi[:-1] + isi[1:]
    cv2 = float(np.mean(2 * d / s)) if s.size and (s > 0).all() else None
    return {"burst_frac": burst_frac, "cv_isi": cv, "cv2": cv2}


def _spont_intervals(h):
    key = "intervals/spontaneous_presentations"
    if key not in h:
        return None
    st, sp = h[key]["start_time"][:], h[key]["stop_time"][:]
    iv = [(float(a), float(b)) for a, b in zip(st, sp) if b - a > 1.0]
    return iv or None


def _multi_matrix(per_unit_all, intervals, dt):
    cols = [[] for _ in per_unit_all]; pooled = [[] for _ in per_unit_all]
    for (s, e) in intervals:
        nb = max(2, int((e - s) / dt)); edges = np.linspace(s, e, nb + 1)
        for i, spk in enumerate(per_unit_all):
            sel = spk[(spk >= s) & (spk < e)]
            cols[i].append(np.histogram(sel, bins=edges)[0]); pooled[i].append(sel)
    M = np.array([np.concatenate(c) for c in cols], float).T if cols and cols[0] else np.zeros((0, 0))
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
    f, sid, region, unit_rows, celltypes, total_dur = arg
    pop_recs, cell_recs = [], []
    with h5py.File(f, "r") as h:
        iv = _spont_intervals(h)
        if iv is None:
            return [], []
        sti = h["units/spike_times_index"]; st_all = h["units/spike_times"]
        per_unit_all = []
        for r in unit_rows:
            lo = 0 if r == 0 else int(sti[r - 1]); hi = int(sti[r])
            per_unit_all.append(st_all[lo:hi])
    span = sum(e - s for s, e in iv)
    ctype_groups = {"all": list(range(len(unit_rows))),
                    "excitatory": [i for i, c in enumerate(celltypes) if c == "excitatory"],
                    "inhibitory": [i for i, c in enumerate(celltypes) if c == "inhibitory"]}
    for ct, idxs in ctype_groups.items():
        if len(idxs) < (MIN_UNITS if ct != "inhibitory" else 8):
            continue
        M, per_unit = _multi_matrix([per_unit_all[i] for i in idxs], iv, DT)
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
            pop_recs.append({"substrate": "allen-hpf-pop", "session": sid, "region": region,
                             "cell_type": ct, "n_units": len(idxs), "aggregation": agg,
                             "n": int(len(obj)), "spont_span_s": round(span, 1),
                             "axes_computed": {"I.5q_ks_gue_med": i5q, **fp},
                             "source_artifact": "generated (Allen HPF population aggregation)",
                             "computed_date": date.today().isoformat()})
    for i, r in enumerate(unit_rows):
        _, pu = _multi_matrix([per_unit_all[i]], iv, DT)
        spk = pu[0]
        if spk.size < 50:
            continue
        try:
            i5q = _f(classify(spk).get("ks_gue_med"))
        except Exception:
            i5q = None
        fI = {k: _f(fn(canonical_spacings(spk))) for k, fn in FAMILY_I.items()}; fI.update({k: _f(v) for k, v in family_local(spk).items()})
        cell_recs.append({"substrate": "allen-hpf-cell", "session": sid, "region": region,
                          "cell_type": celltypes[i], "rate_hz": round(spk.size / max(span, 1e-9), 4),
                          "n": int(spk.size), "burst": _burst_stats(spk),
                          "axes_computed": {"I.5q_ks_gue_med": i5q, **fI},
                          "source_artifact": "generated (Allen HPF per-cell spike-time)",
                          "computed_date": date.today().isoformat()})
    return pop_recs, cell_recs


def run(all_sessions=False, workers=8):
    tg = build_hpf_targets()
    files = sorted(glob.glob(NWB_GLOB))
    if not all_sessions:
        files = files[:1]
    tasks = []
    for f in files:
        sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
        sub = tg[tg["session_id"] == sid]
        if sub.empty:
            continue
        with h5py.File(f, "r") as h:
            ids = h["units/id"][:]
            row_of = {int(u): r for r, u in enumerate(ids)}
        for region in sub["region"].unique():
            rs = sub[sub["region"] == region]
            rows, cts = [], []
            for _, rec in rs.iterrows():
                uid = int(rec["id"])
                if uid in row_of:
                    rows.append(row_of[uid]); cts.append(rec["cell_type"])
            if len(rows) >= 8:
                tasks.append((f, sid, region, rows, cts, None))
    pop_out = open(os.path.join(COORD, "allen-hpf-pop.jsonl"), "w")
    cell_out = open(os.path.join(COORD, "allen-hpf-cell.jsonl"), "w")
    t0 = time.perf_counter(); npop = ncell = 0
    print(f"ALLEN HPF — {len(files)} session(s), {len(tasks)} (session,region) tasks, {workers}w")
    print(f"{'session':>10s} {region_hdr()}")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for pop_recs, cell_recs in ex.map(_process, tasks):
            for r in pop_recs:
                pop_out.write(json.dumps(r) + "\n"); npop += 1
                if r["cell_type"] == "all":
                    ax = r["axes_computed"]
                    def g(k):
                        v = ax.get(k); return f"{v:.3f}" if isinstance(v, float) else "  -"
                    print(f"{r['session']:>10d} {r['region']:5s} {r['aggregation']:11s} "
                          f"nU={r['n_units']:>3d} n={r['n']:>6d} q={g('I.8_brody_q')} "
                          f"BRρ={g('I.9_berry_robnik_rho')}", flush=True)
            for r in cell_recs:
                cell_out.write(json.dumps(r) + "\n"); ncell += 1
            pop_out.flush(); cell_out.flush()
    pop_out.close(); cell_out.close()
    print(f"\n→ {npop} pop + {ncell} per-cell records in {(time.perf_counter()-t0)/60:.1f} min. "
          "Analyse with allen_hpf_analysis.py. Flag, don't interpret.")


def region_hdr():
    return "region agg          counts/axes"


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
