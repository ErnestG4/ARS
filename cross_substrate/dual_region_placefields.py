"""
cross_substrate/dual_region_placefields.py — pillar-2 probe on the CONTINUOUS-attractor substrate (000638).

P1.3/P2.3: 1D place coherence per cell on the track task, then place-coherence <-> universality-class
(ks_gue) correlation PER REGION (rho_MEC vs rho_CA1 vs rho_DG). This is the EC-side analogue of the
Allen V1 OSI<->class (H1) and Buzsaki CA1 place-coherence<->class findings. Cross-substrate it is NOT
comparable (Allen visual task has no spatial behavior) — this is a within-000638 pillar-2 instantiation.

Position is 25kHz/938MB per session, contiguous-uncompressed. We block-read it sequentially (low memory),
decimate to ~50Hz, derive speed from |dx/dt|, restrict to running, build per-cell 1D rate maps ->
Skaggs spatial information (bits/spike) + spatial coherence (bin-rate vs neighbor-mean correlation).
Sequential over a few sessions (bandwidth). Caches decimated position to coordinates/dr_pos_<sid>.npz.

Out: coordinates/dr-placefields.jsonl.  Run: --run [--sessions S1 S2 ...] [--nbins 50] [--fs 50].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                             # noqa: E402
from cross_substrate.nwb_remote import open_dandi_asset                       # noqa: E402
from cross_substrate.dual_region_scan import coarse_region, _dec              # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
DANDISET = "000638"
NATIVE_FS = 25000.0


def _decimate_position(h, target_fs=50.0, block_samp=8_000_000):
    """Block-read the 25kHz contiguous position, decimate to ~target_fs. Low-memory streaming."""
    node = h["processing/behavior/position/position"]
    data = node["data"]
    n = data.shape[0]
    stride = max(1, int(round(NATIVE_FS / target_fs)))
    chunks = []
    start = 0
    while start < n:
        end = min(start + block_samp, n)
        blk = data[start:end]
        # align stride across blocks
        off = (-start) % stride
        chunks.append(blk[off::stride])
        start = end
    pos = np.concatenate(chunks)
    fs = NATIVE_FS / stride
    return pos.astype(float), fs


def _rate_map(spk, pos, fs, nbins, run_mask, occ_min=0.1):
    t = np.arange(pos.size) / fs
    edges = np.linspace(np.nanmin(pos), np.nanmax(pos), nbins + 1)
    bidx = np.clip(np.digitize(pos, edges) - 1, 0, nbins - 1)
    # occupancy (s) over running samples
    occ = np.zeros(nbins)
    rb = bidx[run_mask]
    for b in rb:
        occ[b] += 1.0 / fs
    # spikes assigned to position bin via nearest time sample
    si = np.clip(np.searchsorted(t, spk), 0, pos.size - 1)
    si = si[run_mask[si]]
    sc = np.zeros(nbins)
    for b in bidx[si]:
        sc[b] += 1
    valid = occ > occ_min
    if valid.sum() < 5:
        return None
    rate = np.full(nbins, np.nan)
    rate[valid] = sc[valid] / occ[valid]
    return rate, occ, valid


def _skaggs(rate, occ, valid):
    r = rate[valid]; o = occ[valid]
    p = o / o.sum()
    mean_r = np.sum(p * r)
    if mean_r <= 0:
        return None
    nz = r > 0
    info = np.sum(p[nz] * (r[nz] / mean_r) * np.log2(r[nz] / mean_r))
    return float(info)


def _coherence(rate, valid):
    idx = np.where(valid)[0]
    if idx.size < 8:
        return None
    a, b = [], []
    for i in idx:
        nb = [j for j in (i - 1, i + 1) if 0 <= j < rate.size and valid[j]]
        if nb:
            a.append(rate[i]); b.append(np.mean(rate[nb]))
    if len(a) < 8:
        return None
    a = np.array(a); b = np.array(b)
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def process_session(aid, size, sid, nbins=50, fs=50.0):
    cachef = os.path.join(COORD, f"dr_pos_{sid}.npz")
    # large range-blocks: position is a multi-GB contiguous read; 1MB blocks are latency-bound (~2MB/s).
    # 16MB blocks cut round-trips ~16x.
    h = open_dandi_asset(DANDISET, aid, size=size, block=16 << 20, max_blocks=12)
    try:
        if os.path.exists(cachef):
            z = np.load(cachef); pos = z["pos"]; real_fs = float(z["fs"])
        else:
            pos, real_fs = _decimate_position(h, target_fs=fs)
            np.savez_compressed(cachef, pos=pos, fs=real_fs)
        # speed from |dx/dt|, smoothed; running threshold = 60th pct of nonzero speed
        sp = np.abs(np.gradient(pos)) * real_fs
        k = max(3, int(real_fs * 0.25))
        sp = np.convolve(sp, np.ones(k) / k, mode="same")
        thr = np.percentile(sp[sp > 0], 60) if (sp > 0).any() else 0.0
        run_mask = sp > thr
        # units
        eg = "general/extracellular_ephys/electrodes"
        eloc = _dec(h[eg]["location"][:]) if "location" in h[eg] else None
        u = h["units"]
        el = u["electrodes"][:]; eli = u["electrodes_index"][:]
        utype = _dec(u["unit_type"][:]) if "unit_type" in u else ["?"] * len(eli)
        sti = u["spike_times_index"][:]; st_all = u["spike_times"][:]
    finally:
        h.close()
    recs = []
    prev_e = 0
    for i in range(len(eli)):
        sl = el[prev_e:int(eli[i])]; prev_e = int(eli[i])
        reg = coarse_region(eloc[int(sl[0])]) if (len(sl) and eloc) else "other"
        if reg not in ("MEC", "CA1", "DG"):
            continue
        s_lo = 0 if i == 0 else int(sti[i - 1]); s_hi = int(sti[i])
        spk = np.sort(st_all[s_lo:s_hi])
        if spk.size < 100:
            continue
        rm = _rate_map(spk, pos, fs, nbins, run_mask)
        if rm is None:
            continue
        rate, occ, valid = rm
        info = _skaggs(rate, occ, valid)
        coh = _coherence(rate, valid)
        try:
            ksg = classify(spk).get("ks_gue_med")
            ksg = None if ksg is None or not np.isfinite(ksg) else float(ksg)
        except Exception:
            ksg = None
        recs.append({"substrate": "dr-placefields", "session": sid, "unit": i, "region": reg,
                     "cell_type": utype[i], "n": int(spk.size),
                     "spatial_info_bits_per_spike": info, "place_coherence": coh,
                     "peak_rate": float(np.nanmax(rate)), "ks_gue_med": ksg,
                     "source_artifact": "generated (000638 1D place map, running)",
                     "computed_date": date.today().isoformat()})
    return recs


def run(sessions=None, nbins=50, fs=50.0):
    assets = {a["path"].split("/")[0]: a for a in
              json.load(open(os.path.join(COORD, "dr000638_assets.json")))}
    if not sessions:
        # default: strongest MEC+CA1+DG sessions
        sessions = ["sub-TS90-0", "sub-TS118-4", "sub-TS118-3"]
    out = open(os.path.join(COORD, "dr-placefields.jsonl"), "w")
    t0 = time.perf_counter(); n = 0
    print(f"000638 PLACE-COHERENCE (pillar-2) — {len(sessions)} sessions, nbins={nbins} fs~{fs}Hz")
    for sid in sessions:
        a = assets.get(sid)
        if not a:
            print(f"  {sid}: no asset, skip"); continue
        ts = time.perf_counter()
        try:
            recs = process_session(a["asset_id"], a["size"], sid, nbins, fs)
        except Exception as e:
            print(f"  {sid}: FAILED {type(e).__name__}: {e}", flush=True); continue
        for r in recs:
            out.write(json.dumps(r) + "\n"); n += 1
        out.flush()
        import collections
        byreg = collections.Counter(r["region"] for r in recs)
        print(f"  {sid}: {len(recs)} cells {dict(byreg)}  ({(time.perf_counter()-ts)/60:.1f} min)", flush=True)
    out.close()
    print(f"\n→ {n} place-field cells in {(time.perf_counter()-t0)/60:.1f} min. "
          "Correlate place_coherence/spatial_info <-> ks_gue per region (pillar-2). Flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sessions", nargs="*", default=None)
    ap.add_argument("--nbins", type=int, default=50)
    ap.add_argument("--fs", type=float, default=50.0)
    a = ap.parse_args()
    if a.run:
        run(sessions=a.sessions, nbins=a.nbins, fs=a.fs)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
