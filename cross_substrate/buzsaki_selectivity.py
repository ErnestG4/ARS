"""
cross_substrate/buzsaki_selectivity.py — CA1 per-cell selectivity properties (the H1-analogue battery).

H1 in Allen: OSI (orientation selectivity) correlates with per-cell ks_gue. This computes the CA1 analogues
— "what makes a hippocampal cell selective" — to search for the one that tracks per-cell ks_gue:
  • spatial_info — Skaggs spatial information (bits/spike) on the linearized maze (Maze epoch) [PRIMARY]
  • theta_mrl   — theta (6–10 Hz) phase-locking strength (mean resultant length) from LFP [secondary]
  • burst_index — fraction of ISIs < 6 ms (complex-spike bursting) [secondary]
  • rate        — mean firing rate over Maze [control]
Computed during the Maze epoch (place coding + theta are prominent there). Correlated downstream against the
Maze-Awake per-cell ks_gue (buzsaki-port-cell.jsonl) by buzsaki_port_analysis.py.

Out: coordinates/buzsaki-selectivity.jsonl. Run: --run [--sessions N | --all].
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
from datetime import date

import numpy as np
import h5py
from scipy.signal import butter, filtfilt, hilbert

_HERE = os.path.dirname(os.path.abspath(__file__))
BUZ_GLOB = os.path.expandvars("$HOME/fmexplorer/buzsaki_cache/*.nwb")
COORD = os.path.join(_HERE, "coordinates")
N_POS_BINS = 50
THETA_BAND = (6.0, 10.0)


def _decode(a):
    return [x.decode() if isinstance(x, bytes) else x for x in a]


def _ts_rate(grp):
    """NWB TimeSeries sampling rate (attr on starting_time) + t0. NB this dataset stores some 'rate' attrs as
    the sampling PERIOD (e.g. position rate=0.0256 = 1/39.06 Hz) while LFP stores true Hz (1250) — invert any
    sub-1 value (no real neural sampling rate is < 1 Hz)."""
    st = grp["starting_time"]
    t0 = float(st[()])
    if "rate" not in st.attrs:
        return t0, None
    r = float(st.attrs["rate"])
    return t0, (1.0 / r if 0 < r < 1.0 else r)


def _find_linearized_position(h):
    """Find the *LinearizedPosition container (maze name varies per session: 1.6mLinearMaze, CircularMaze…).
    Returns (px, pt0, prate) or None."""
    beh = h["processing/behavior"]
    for k in beh:
        if k.endswith("LinearizedPosition"):
            grp = beh[k]
            for sk in grp:
                ts = grp[sk]
                if "data" in ts:
                    px = ts["data"][:, 0] if ts["data"].ndim == 2 else ts["data"][:]
                    pt0, prate = _ts_rate(ts)
                    return px, pt0, prate
    return None


def _maze_window(h):
    ep = h["intervals/epochs"]; lab = _decode(ep["label"][:])
    for l, s, e in zip(lab, ep["start_time"][:], ep["stop_time"][:]):
        if l.replace("Epoch", "") == "Maze":
            return float(s), float(e)
    return None


def _spatial_info(spk, pos_t, pos_x, t0, t1):
    """Skaggs bits/spike on linearized position over [t0,t1]."""
    m = (pos_t >= t0) & (pos_t < t1) & np.isfinite(pos_x)
    pt, px = pos_t[m], pos_x[m]
    if pt.size < 100:
        return None
    dt = np.median(np.diff(pt))
    edges = np.linspace(np.nanmin(px), np.nanmax(px), N_POS_BINS + 1)
    occ, _ = np.histogram(px, bins=edges)            # samples per bin
    occ_t = occ * dt                                  # seconds per bin
    sspk = spk[(spk >= t0) & (spk < t1)]
    if sspk.size < 50 or occ_t.sum() <= 0:
        return None
    spk_x = np.interp(sspk, pt, px)
    scount, _ = np.histogram(spk_x, bins=edges)
    valid = occ_t > 0
    p = occ_t[valid] / occ_t.sum()
    r_i = scount[valid] / occ_t[valid]
    r = sspk.size / occ_t.sum()
    if r <= 0:
        return None
    nz = r_i > 0
    return float(np.sum(p[nz] * (r_i[nz] / r) * np.log2(r_i[nz] / r)))


def _theta_mrl(spk, analytic, lfp_t0, lfp_rate, t0, t1):
    """Mean resultant length of theta phase at spike times (one representative channel)."""
    sspk = spk[(spk >= t0) & (spk < t1)]
    if sspk.size < 50:
        return None
    idx = np.round((sspk - lfp_t0) * lfp_rate).astype(int)
    idx = idx[(idx >= 0) & (idx < analytic.size)]
    if idx.size < 50:
        return None
    z = analytic[idx]
    u = z / np.abs(z)
    return float(np.abs(np.mean(u)))


def _burst_index(spk):
    if spk.size < 50:
        return None
    isi = np.diff(np.sort(spk))
    return float(np.mean(isi < 0.006))


def _theta_channel(h, lfp_rate, t0, t1):
    """Pick the max-theta-power LFP channel in the Maze window; return analytic signal of that window + its
    start time (theta MRL only needs Maze-epoch phase, so we analyse just the window — ~16× cheaper)."""
    lfp = h["processing/ecephys/LFP/LFP"]; data = lfp["data"]
    i0 = max(0, int(t0 * lfp_rate)); i1 = min(data.shape[0], int(t1 * lfp_rate))
    nch = data.shape[1]
    cand = list(range(0, nch, max(1, nch // 16)))     # sample up to 16 channels for the power probe
    b, a = butter(3, [THETA_BAND[0] / (lfp_rate / 2), THETA_BAND[1] / (lfp_rate / 2)], btype="band")
    seg = data[i0:i1, :][:, cand].astype(float)
    best, best_pow, best_ft = None, -1, None
    for j, ch in enumerate(cand):
        ft = filtfilt(b, a, seg[:, j])
        p = float(np.mean(ft ** 2))
        if p > best_pow:
            best_pow, best, best_ft = p, ch, ft
    analytic = hilbert(best_ft)
    return analytic, best, i0 / lfp_rate


def run(n_sessions=1, all_sessions=False):
    files = sorted(glob.glob(BUZ_GLOB))
    if not all_sessions:
        files = files[:n_sessions]
    out = open(os.path.join(COORD, "buzsaki-selectivity.jsonl"), "w")
    t0all = time.perf_counter(); n = 0
    print(f"BUZSAKI CA1 SELECTIVITY — {len(files)} session(s) (spatial-info / theta-MRL / burst / rate)")
    for f in files:
        sid = os.path.basename(f).replace(".nwb", "")
        with h5py.File(f, "r") as h:
            mz = _maze_window(h)
            if mz is None:
                print(f"  {sid}: no Maze epoch, skip"); continue
            mt0, mt1 = mz
            cell_type = _decode(h["units/cell_type"][:])
            location = _decode(h["units/location"][:]) if "location" in h["units"] else ["?"] * len(cell_type)
            sti = h["units/spike_times_index"][:]; st_all = h["units/spike_times"]
            nU = len(cell_type)
            # position (maze container name varies per session)
            pos = _find_linearized_position(h)
            if pos is None:
                print(f"  {sid}: no linearized position, skip"); continue
            px, pt0, prate = pos
            if prate is None:
                prate = px.size / (mt1 - mt0)
            pos_t = pt0 + np.arange(px.size) / prate
            # LFP rate + theta channel
            lfp = h["processing/ecephys/LFP/LFP"]
            _, lrate = _ts_rate(lfp)
            if lrate is None:
                lrate = lfp["data"].shape[0] / (h["intervals/epochs/stop_time"][-1])
            print(f"  {sid}: {nU} units, Maze [{mt0:.0f},{mt1:.0f}]s, pos_rate≈{prate:.1f}, lfp_rate≈{lrate:.0f}; "
                  "picking theta channel...", flush=True)
            analytic, thch, ltz = _theta_channel(h, lrate, mt0, mt1)
            print(f"    theta channel = {thch}", flush=True)
            for i in range(nU):
                spk = st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])]
                rec = {"substrate": "buzsaki-selectivity", "session": sid, "unit": i,
                       "cell_type": cell_type[i], "location": location[i],
                       "spatial_info": _spatial_info(spk, pos_t, px, mt0, mt1),
                       "theta_mrl": _theta_mrl(spk, analytic, ltz, lrate, mt0, mt1),
                       "burst_index": _burst_index(spk[(spk >= mt0) & (spk < mt1)]),
                       "rate": float(((spk >= mt0) & (spk < mt1)).sum() / (mt1 - mt0)),
                       "source_artifact": "generated (CA1 Maze-epoch selectivity)",
                       "computed_date": date.today().isoformat()}
                out.write(json.dumps(rec) + "\n"); n += 1
            out.flush()
    out.close()
    print(f"\n→ {n} per-cell selectivity records in {(time.perf_counter()-t0all)/60:.1f} min. Flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sessions", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.run:
        run(a.sessions, all_sessions=a.all)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
