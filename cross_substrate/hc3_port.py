"""
cross_substrate/hc3_port.py — framework-port to CRCNS hc-3 (Mizuseki/Buzsáki), the DE-CONFOUNDED EC-vs-CA3.

hc-3 records EC (EC2-5) + CA3 (+ DG) SIMULTANEOUSLY in one implant — so the EC-vs-CA3 attractor contrast is
WITHIN one dataset/recording (no cross-dataset validity-bridge confound that voided the 000638-vs-Allen
headline). Identical tooling as the MEC/Allen/Buzsáki ports: ars_classify ks_gue + Family I per-cell;
corr-eig/avl-onset/sync-event population; dt=25ms; burst stats; place-coherence on spatial sessions.

Neuroscope/Klusters format (extracted small files only; .dat/.eeg/.spk NOT downloaded):
  .xml         -> broadband samplingRate (20000) for .res; .whl rate (39.0625)
  .res.N       -> spike sample indices for shank N (÷ samplingRate = seconds)
  .clu.N       -> line1=#clusters, then cluster id per spike (aligned to .res.N); clu 0=noise,1=MUA -> drop
  .whl         -> position (x1,y1,x2,y2) at 39.0625 Hz, -1 = untracked
  hc3-cell.csv -> (topdir, ele=N, clu) -> region + cellType ('p'/'i'/'n'); cells common across a topdir.

Out: coordinates/hc3-port-{cell,pop}.jsonl + hc3-placefields.jsonl.  Run: --run [--workers N].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                             # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I                 # noqa: E402
from cross_substrate.population_fingerprint import (_corr_eig, _avalanche_onsets,  # noqa: E402
                                                    _sync_events, _fp, _f)

SESS_ROOT = "/home/combust/fmexplorer/crcns_cache/sessions"
META = "/home/combust/fmexplorer/crcns_cache/docs/hc3-metadata-tables/hc3-cell.csv"
COORD = os.path.join(_HERE, "coordinates")
DT = 0.025
MIN_UNITS = 20
WHL_FS = 39.0625


def coarse_region(r):
    r = str(r)
    if r.startswith("EC"):
        return "EC"
    if r in ("CA1", "CA3", "DG"):
        return r
    return "other"


CELLTYPE = {"p": "excitatory", "i": "inhibitory", "n": "unclassified"}


def load_cell_table():
    c = pd.read_csv(META, header=None)
    c.columns = ["id", "topdir", "animal", "ele", "clu", "region", "nexc", "ninh",
                 "exc", "inh", "excd", "inhd", "fr", "tfr", "type"]
    m = {}
    for _, r in c.iterrows():
        m[(r["topdir"], int(r["ele"]), int(r["clu"]))] = (coarse_region(r["region"]),
                                                          CELLTYPE.get(str(r["type"]), "unclassified"))
    return m


def _read_ints(path):
    with open(path) as fh:
        return np.array(fh.read().split(), dtype=np.int64)


def _xml_rates(xmlpath):
    root = ET.parse(xmlpath).getroot()
    sr = root.findtext(".//acquisitionSystem/samplingRate")
    sr = float(sr) if sr else 20000.0
    return sr


def _burst_stats(spk):
    isi = np.diff(np.sort(spk)); isi = isi[isi > 0]
    if isi.size < 10:
        return {"burst_frac": None, "cv_isi": None, "cv2": None}
    bf = float(np.mean(isi < 0.010))
    cv = float(np.std(isi) / np.mean(isi)) if np.mean(isi) > 0 else None
    d = np.abs(np.diff(isi)); s = isi[:-1] + isi[1:]
    cv2 = float(np.mean(2 * d / s)) if s.size and (s > 0).all() else None
    return {"burst_frac": bf, "cv_isi": cv, "cv2": cv2}


def parse_session(sdir, topdir, session, cellmap):
    """Return units = [{ele,clu,region,celltype,spk(sec)}], duration, whl(x at 39Hz or None)."""
    xmls = glob.glob(os.path.join(sdir, "*.xml"))
    sr = _xml_rates(xmls[0]) if xmls else 20000.0
    units = []
    tmax = 0.0
    for resf in sorted(glob.glob(os.path.join(sdir, "*.res.*"))):
        N = int(resf.rsplit(".", 1)[1])
        cluf = resf.replace(".res.", ".clu.")
        if not os.path.exists(cluf):
            continue
        res = _read_ints(resf)
        clu = _read_ints(cluf)
        if clu.size != res.size + 1:
            # first line is count; if mismatch, still drop first
            clu = clu[1:] if clu.size > res.size else clu
        else:
            clu = clu[1:]
        if res.size == 0:
            continue
        tmax = max(tmax, res.max() / sr)
        for c in np.unique(clu):
            if c < 2:
                continue
            spk = np.sort(res[clu == c]) / sr
            reg, ct = cellmap.get((topdir, N, int(c)), ("other", "unclassified"))
            units.append({"ele": N, "clu": int(c), "region": reg, "celltype": ct, "spk": spk})
    # whl position (first LED x), valid samples only kept with time index
    whlf = glob.glob(os.path.join(sdir, "*.whl"))
    pos = None
    if whlf:
        w = np.loadtxt(whlf[0])
        if w.ndim == 2 and w.shape[0] > 10:
            x = w[:, 0].astype(float)
            pos = x  # -1 = invalid; handled downstream
    return units, tmax, pos, sr


# ── place coherence on .whl (39Hz) ──
def _placefields(units, pos, tmax, nbins=50):
    if pos is None or (pos > -1).sum() < 100:
        return []
    t = np.arange(pos.size) / WHL_FS
    valid_t = pos > -1
    sp = np.zeros_like(pos)
    good = np.where(valid_t)[0]
    if good.size < 50:
        return []
    sp[good[1:]] = np.abs(np.diff(pos[good])) * WHL_FS / np.maximum(np.diff(t[good]) * WHL_FS, 1)
    speed = np.abs(np.gradient(np.where(valid_t, pos, np.nan)))
    speed = np.nan_to_num(speed) * WHL_FS
    run = valid_t & (speed > np.nanpercentile(speed[valid_t & (speed > 0)], 50) if (speed[valid_t] > 0).any() else valid_t)
    lo, hi = np.percentile(pos[valid_t], [1, 99])
    edges = np.linspace(lo, hi, nbins + 1)
    bidx = np.clip(np.digitize(pos, edges) - 1, 0, nbins - 1)
    occ = np.zeros(nbins)
    for b in bidx[run]:
        occ[b] += 1.0 / WHL_FS
    out = []
    for u in units:
        if u["region"] not in ("EC", "CA3", "CA1", "DG"):
            continue
        spk = u["spk"]
        if spk.size < 100:
            continue
        si = np.clip(np.searchsorted(t, spk), 0, pos.size - 1)
        si = si[run[si]]
        sc = np.zeros(nbins)
        for b in bidx[si]:
            sc[b] += 1
        vmask = occ > 0.1
        if vmask.sum() < 5 or sc[vmask].sum() < 20:
            continue
        rate = np.full(nbins, np.nan)
        rate[vmask] = sc[vmask] / occ[vmask]
        r = rate[vmask]; o = occ[vmask]; p = o / o.sum()
        mean_r = np.sum(p * r)
        info = float(np.sum(p[r > 0] * (r[r > 0] / mean_r) * np.log2(r[r > 0] / mean_r))) if mean_r > 0 else None
        # coherence: bin vs neighbor-mean
        idx = np.where(vmask)[0]; a, b2 = [], []
        for i in idx:
            nb = [j for j in (i - 1, i + 1) if 0 <= j < nbins and vmask[j]]
            if nb:
                a.append(rate[i]); b2.append(np.mean(rate[nb]))
        coh = float(np.corrcoef(a, b2)[0, 1]) if len(a) >= 8 and np.std(a) > 0 and np.std(b2) > 0 else None
        try:
            ksg = _f(classify(spk).get("ks_gue_med"))
        except Exception:
            ksg = None
        out.append({"region": u["region"], "celltype": u["celltype"], "n": int(spk.size),
                    "spatial_info_bits_per_spike": info, "place_coherence": coh, "ks_gue_med": ksg})
    return out


def _matrix(per_unit, t1, dt):
    nb = max(4, int(t1 / dt)); edges = np.linspace(0, t1, nb + 1)
    M = np.empty((nb, len(per_unit)), float)
    for i, spk in enumerate(per_unit):
        M[:, i] = np.histogram(spk, bins=edges)[0]
    return M


def _process(arg):
    sdir, topdir, session = arg
    cellmap = load_cell_table()
    units, tmax, pos, sr = parse_session(sdir, topdir, session, cellmap)
    if not units or tmax < 10:
        return [], [], [], f"{session}: no units"
    pop_recs, cell_recs = [], []
    regions = sorted(set(u["region"] for u in units if u["region"] in ("EC", "CA3", "CA1", "DG")))
    for reg in regions:
        ru = [u for u in units if u["region"] == reg]
        groups = {"all": ru,
                  "excitatory": [u for u in ru if u["celltype"] == "excitatory"],
                  "inhibitory": [u for u in ru if u["celltype"] == "inhibitory"]}
        for ct, us in groups.items():
            if len(us) < (MIN_UNITS if ct != "inhibitory" else 8):
                continue
            per = [u["spk"] for u in us]
            M = _matrix(per, tmax, DT)
            pooled = np.sort(np.concatenate(per))
            isi = np.diff(pooled); dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
            obs = {"corr-eig": _corr_eig(M),
                   "avl-onset": _avalanche_onsets(pooled, dt_av),
                   "sync-event": _sync_events(M, np.arange(M.shape[0] + 1) * DT)}
            for agg, o in obs.items():
                if o is None or len(o) < 50:
                    continue
                fp = _fp(o, is_positions=True)
                try:
                    i5q = _f(classify(np.sort(np.asarray(o, float))).get("ks_gue_med"))
                except Exception:
                    i5q = None
                pop_recs.append({"substrate": "hc3-port-pop", "topdir": topdir, "session": session,
                                 "region": reg, "cell_type": ct, "n_units": len(us), "aggregation": agg,
                                 "n": int(len(o)), "session_s": round(tmax, 1),
                                 "axes_computed": {"I.5q_ks_gue_med": i5q, **fp},
                                 "source_artifact": "generated (hc-3 population aggregation)",
                                 "computed_date": date.today().isoformat()})
    for u in units:
        if u["region"] not in ("EC", "CA3", "CA1", "DG"):
            continue
        spk = u["spk"]
        if spk.size < 50:
            continue
        try:
            i5q = _f(classify(spk).get("ks_gue_med"))
        except Exception:
            i5q = None
        fI = {k: _f(fn(canonical_spacings(spk))) for k, fn in FAMILY_I.items()}
        cell_recs.append({"substrate": "hc3-port-cell", "topdir": topdir, "session": session,
                          "ele": u["ele"], "clu": u["clu"], "region": u["region"],
                          "cell_type": u["celltype"], "rate_hz": round(spk.size / max(tmax, 1e-9), 4),
                          "n": int(spk.size), "burst": _burst_stats(spk),
                          "axes_computed": {"I.5q_ks_gue_med": i5q, **fI},
                          "source_artifact": "generated (hc-3 per-cell spike-time)",
                          "computed_date": date.today().isoformat()})
    pf = [{**r, "substrate": "hc3-placefields", "topdir": topdir, "session": session,
           "source_artifact": "generated (hc-3 1D place map)", "computed_date": date.today().isoformat()}
          for r in _placefields(units, pos, tmax)]
    return pop_recs, cell_recs, pf, None


def find_sessions():
    out = []
    for sdir in sorted(glob.glob(os.path.join(SESS_ROOT, "*", "*"))):
        if not os.path.isdir(sdir):
            continue
        if not glob.glob(os.path.join(sdir, "*.res.*")):
            continue
        parts = sdir.split("/")
        topdir, session = parts[-2], parts[-1]
        out.append((sdir, topdir, session))
    return out


def run(workers=6):
    tasks = find_sessions()
    pop_out = open(os.path.join(COORD, "hc3-port-pop.jsonl"), "w")
    cell_out = open(os.path.join(COORD, "hc3-port-cell.jsonl"), "w")
    pf_out = open(os.path.join(COORD, "hc3-placefields.jsonl"), "w")
    t0 = time.perf_counter(); npop = ncell = npf = 0
    print(f"hc-3 PORT — {len(tasks)} sessions, {workers}w (de-confounded EC-vs-CA3 within one dataset)")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for pop_recs, cell_recs, pf, err in ex.map(_process, tasks):
            if err:
                print("  ERR", err, flush=True); continue
            for r in pop_recs:
                pop_out.write(json.dumps(r) + "\n"); npop += 1
                if r["cell_type"] == "all":
                    ax = r["axes_computed"]
                    g = lambda k: (f"{ax.get(k):.3f}" if isinstance(ax.get(k), float) else "  -")
                    print(f"  {r['session']:12s} {r['region']:4s} {r['aggregation']:11s} "
                          f"nU={r['n_units']:>3d} n={r['n']:>7d} q={g('I.8_brody_q')} BRρ={g('I.9_berry_robnik_rho')}",
                          flush=True)
            for r in cell_recs:
                cell_out.write(json.dumps(r) + "\n"); ncell += 1
            for r in pf:
                pf_out.write(json.dumps(r) + "\n"); npf += 1
            pop_out.flush(); cell_out.flush(); pf_out.flush()
    pop_out.close(); cell_out.close(); pf_out.close()
    print(f"\n→ {npop} pop + {ncell} cell + {npf} placefield records in {(time.perf_counter()-t0)/60:.1f} min. "
          "Analyse: attractor_analysis.py (add hc3). Flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if a.run:
        run(workers=a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
