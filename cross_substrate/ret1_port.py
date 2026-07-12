"""
cross_substrate/ret1_port.py — per-cell fingerprint port of CRCNS ret-1 (Meister mouse retina, MEA).

Retina is an INDEPENDENT FEEDFORWARD circuit (retinal ganglion cells = the output layer; no recurrence like
cortex/hippocampus). ret-1 is binary-white-noise only (no moving-bar/grating stimulus), so it does NOT supply
the motion/direction (DSI) axis-kind — it supplies a feedforward-circuit test of whether the per-cell
fingerprint (ks_gue + Family I + burst) is even meaningful here, and a 4th datapoint for the ks_gue↔burst
substrate-relativity map (retinal RGCs fire ~10 Hz — a high-rate regime vs hc-3 ~0.3 Hz tetrode).

Per cell: longest white-noise block spike train → ks_gue (ars_classify) + Family I + burst stats.
RGCs have no exc/inh split (all projection neurons). Out: coordinates/ret1-cell.jsonl. Run: --run [--workers N].
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
import scipy.io

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                             # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, family_local                # noqa: E402
from cross_substrate.population_fingerprint import _f                         # noqa: E402

DATA = os.path.expandvars("$HOME/fmexplorer/crcns_cache/ret1/crcns_ret-1/Data")
COORD = os.path.join(_HERE, "coordinates")
MIN_SPIKES = 100


def _burst_stats(spk):
    isi = np.diff(np.sort(spk)); isi = isi[isi > 0]
    if isi.size < 10:
        return {"burst_frac": None, "cv_isi": None, "cv2": None}
    bf = float(np.mean(isi < 0.010))
    cv = float(np.std(isi) / np.mean(isi)) if np.mean(isi) > 0 else None
    d = np.abs(np.diff(isi)); s = isi[:-1] + isi[1:]
    cv2 = float(np.mean(2 * d / s)) if s.size and (s > 0).all() else None
    return {"burst_frac": bf, "cv_isi": cv, "cv2": cv2}


def _process(f):
    rid = os.path.basename(f).replace(".mat", "")
    m = scipy.io.loadmat(f, squeeze_me=True, struct_as_record=False)
    stim = np.atleast_1d(m["stimulus"])
    ncell = int(getattr(m["datainfo"], "Ncell"))
    nstim = len(stim)
    # spikes is M cells x N stimuli; squeeze_me collapses a singleton stimulus axis, so re-orient
    # by datainfo.Ncell rather than trusting atleast_2d's axis placement.
    sp = np.asarray(m["spikes"], dtype=object)
    if sp.ndim == 1:
        sp = sp.reshape(ncell, nstim) if nstim == 1 else sp.reshape(nstim, ncell).T
    elif sp.shape[0] != ncell and sp.shape[1] == ncell:
        sp = sp.T
    spikes = sp
    # pick the white-noise block with the longest duration
    durs = [float(s.frame) * int(s.Nframes) for s in stim]
    blk = int(np.argmax(durs)); dur = durs[blk]
    recs = []
    n_cells = spikes.shape[0]
    for i in range(n_cells):
        spk = np.atleast_1d(spikes[i, blk]).astype(float)
        spk = np.sort(spk[np.isfinite(spk)])
        if spk.size < MIN_SPIKES:
            continue
        try:
            i5q = _f(classify(spk).get("ks_gue_med"))
        except Exception:
            i5q = None
        fI = {k: _f(fn(canonical_spacings(spk))) for k, fn in FAMILY_I.items()}; fI.update({k: _f(v) for k, v in family_local(spk).items()})
        recs.append({"substrate": "ret1-cell", "recording": rid, "cell": i,
                     "stim_type": "binarywhitenoise", "block_s": round(dur, 1),
                     "rate_hz": round(spk.size / dur, 4), "n": int(spk.size),
                     "burst": _burst_stats(spk),
                     "axes_computed": {"I.5q_ks_gue_med": i5q, **fI},
                     "source_artifact": "generated (ret-1 RGC white-noise spike-time)",
                     "computed_date": date.today().isoformat()})
    return recs


def run(workers=8):
    files = sorted(glob.glob(os.path.join(DATA, "*.mat")))
    out = open(os.path.join(COORD, "ret1-cell.jsonl"), "w")
    t0 = time.perf_counter(); n = 0
    print(f"ret-1 PORT — {len(files)} recordings, {workers}w (mouse RGC, white-noise; feedforward circuit)")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for recs in ex.map(_process, files):
            for r in recs:
                out.write(json.dumps(r) + "\n"); n += 1
            out.flush()
            if recs:
                print(f"  {recs[0]['recording']:14s} {len(recs):>3d} cells "
                      f"(median rate {np.median([r['rate_hz'] for r in recs]):.1f} Hz)", flush=True)
    out.close()
    print(f"→ {n} RGC fingerprints in {(time.perf_counter()-t0)/60:.1f} min. Analyse with ret1_analysis. Flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
