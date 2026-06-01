"""
cross_substrate/dual_region_port.py — framework-port to DANDI 000638 (Hippocampus+EC dual-region probe).

Supplies the CONTINUOUS-attractor pole the Allen HPF port lacks: MEC (medial entorhinal, grid cells =
continuous/toroidal attractor) recorded SIMULTANEOUSLY with CA1 (relay/comparator) and DG (sparse
separator). [No CA3/LEC units were sorted in any of the 33 sessions — only MEC/CA1/DG.] The discrete-
attractor pole (CA3) comes from the Allen HPF port; CA1+DG are measured in BOTH substrates as a cross-
substrate VALIDITY BRIDGE for any MEC(000638)-vs-CA3(Allen) comparison.

Identical tooling as Allen/Buzsaki ports: ars_classify ks_gue + Family I per-cell; corr-eig/avl-onset/
sync-event population observables; dt=25ms. Cell-type = the NWB's own unit_type (excitatory/inhibitory/
unclassified). Per-cell + population over the full track-task session. Streams ONLY units+electrodes over
HTTP range (nwb_remote) — never the 30-70GB raw traces. Place coherence (pillar-2) is a separate pass
(dual_region_placefields.py) since position is 25kHz/938MB per session.

Out: coordinates/dr-port-cell.jsonl + dr-port-pop.jsonl.  Run: --run [--workers N] [--min-mec 20].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                             # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I, family_local                # noqa: E402
from cross_substrate.population_fingerprint import (_corr_eig, _avalanche_onsets,  # noqa: E402
                                                    _sync_events, _fp, _f)
from cross_substrate.nwb_remote import open_dandi_asset                       # noqa: E402
from cross_substrate.dual_region_scan import coarse_region, _dec              # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
DANDISET = "000638"
DT = 0.025
MIN_UNITS = 20


def _burst_stats(spk):
    isi = np.diff(np.sort(spk)); isi = isi[isi > 0]
    if isi.size < 10:
        return {"burst_frac": None, "cv_isi": None, "cv2": None}
    bf = float(np.mean(isi < 0.010))
    cv = float(np.std(isi) / np.mean(isi)) if np.mean(isi) > 0 else None
    d = np.abs(np.diff(isi)); s = isi[:-1] + isi[1:]
    cv2 = float(np.mean(2 * d / s)) if s.size and (s > 0).all() else None
    return {"burst_frac": bf, "cv_isi": cv, "cv2": cv2}


def _matrix(per_unit, t0, t1, dt):
    nb = max(4, int((t1 - t0) / dt)); edges = np.linspace(t0, t1, nb + 1)
    M = np.empty((nb, len(per_unit)), float)
    for i, spk in enumerate(per_unit):
        M[:, i] = np.histogram(spk, bins=edges)[0]
    return M, edges


def _pop_observables(M, pooled):
    isi = np.diff(pooled); dt_av = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
    pseudo_edges = np.arange(M.shape[0] + 1) * DT
    return {"corr-eig": _corr_eig(M),
            "avl-onset": _avalanche_onsets(pooled, dt_av),
            "sync-event": _sync_events(M, pseudo_edges)}


def _process(arg):
    aid, size, sid = arg
    try:
        h = open_dandi_asset(DANDISET, aid, size=size)
    except Exception as e:
        return [], [], f"{sid}: open failed {type(e).__name__}: {e}"
    try:
        eg = "general/extracellular_ephys/electrodes"
        eloc = _dec(h[eg]["location"][:]) if "location" in h[eg] else None
        u = h["units"]
        el = u["electrodes"][:]; eli = u["electrodes_index"][:]
        utype = _dec(u["unit_type"][:]) if "unit_type" in u else ["?"] * len(eli)
        sti = u["spike_times_index"][:]
        st_all = u["spike_times"][:]                       # ~10MB, full read once
    finally:
        h.close()
    n_units = len(eli)
    per_unit, region, ctype = [], [], []
    prev_e = 0; prev_s = 0
    for i in range(n_units):
        sl = el[prev_e:int(eli[i])]; prev_e = int(eli[i])
        r = coarse_region(eloc[int(sl[0])]) if (len(sl) and eloc) else "other"
        region.append(r); ctype.append(utype[i])
        s_lo = 0 if i == 0 else int(sti[i - 1]); s_hi = int(sti[i])
        per_unit.append(np.sort(st_all[s_lo:s_hi]))
    t0 = 0.0
    t1 = float(max((pu[-1] for pu in per_unit if pu.size), default=1.0))
    pop_recs, cell_recs = [], []
    regions = sorted(set(r for r in region if r in ("MEC", "CA1", "DG", "CA3", "LEC")))
    for reg in regions:
        idx_reg = [i for i in range(n_units) if region[i] == reg]
        groups = {"all": idx_reg,
                  "excitatory": [i for i in idx_reg if ctype[i] == "excitatory"],
                  "inhibitory": [i for i in idx_reg if ctype[i] == "inhibitory"]}
        for ct, idxs in groups.items():
            if len(idxs) < (MIN_UNITS if ct != "inhibitory" else 8):
                continue
            M, _ = _matrix([per_unit[i] for i in idxs], t0, t1, DT)
            pooled = np.sort(np.concatenate([per_unit[i] for i in idxs]))
            for agg, obj in _pop_observables(M, pooled).items():
                if obj is None or len(obj) < 50:
                    continue
                fp = _fp(obj, is_positions=True)
                try:
                    i5q = _f(classify(np.sort(np.asarray(obj, float))).get("ks_gue_med"))
                except Exception:
                    i5q = None
                pop_recs.append({"substrate": "dr-port-pop", "session": sid, "region": reg,
                                 "cell_type": ct, "n_units": len(idxs), "aggregation": agg,
                                 "n": int(len(obj)), "session_s": round(t1, 1),
                                 "axes_computed": {"I.5q_ks_gue_med": i5q, **fp},
                                 "source_artifact": "generated (000638 population aggregation)",
                                 "computed_date": date.today().isoformat()})
    for i in range(n_units):
        if region[i] not in ("MEC", "CA1", "DG", "CA3", "LEC"):
            continue
        spk = per_unit[i]
        if spk.size < 50:
            continue
        try:
            i5q = _f(classify(spk).get("ks_gue_med"))
        except Exception:
            i5q = None
        fI = {k: _f(fn(canonical_spacings(spk))) for k, fn in FAMILY_I.items()}; fI.update({k: _f(v) for k, v in family_local(spk).items()})
        cell_recs.append({"substrate": "dr-port-cell", "session": sid, "unit": i,
                          "region": region[i], "cell_type": ctype[i],
                          "rate_hz": round(spk.size / max(t1, 1e-9), 4), "n": int(spk.size),
                          "burst": _burst_stats(spk),
                          "axes_computed": {"I.5q_ks_gue_med": i5q, **fI},
                          "source_artifact": "generated (000638 per-cell spike-time)",
                          "computed_date": date.today().isoformat()})
    return pop_recs, cell_recs, None


def select_sessions(min_mec=20, min_ca1=20, min_dg=15):
    comp = json.load(open(os.path.join(COORD, "dr000638_composition.json")))
    assets = {a["path"].split("/")[0]: a for a in
              json.load(open(os.path.join(COORD, "dr000638_assets.json")))}
    out = []
    for r in comp:
        if not r.get("ok"):
            continue
        c = r["comp"]
        def g(k):
            return c.get(k, {}).get("total", 0)
        if g("MEC") >= min_mec and g("CA1") >= min_ca1 and g("DG") >= min_dg:
            a = assets[r["session"]]
            out.append((a["asset_id"], a["size"], r["session"]))
    return out


def run(workers=5, min_mec=20):
    tasks = select_sessions(min_mec=min_mec)
    pop_out = open(os.path.join(COORD, "dr-port-pop.jsonl"), "w")
    cell_out = open(os.path.join(COORD, "dr-port-cell.jsonl"), "w")
    t0 = time.perf_counter(); npop = ncell = 0
    print(f"000638 DUAL-REGION PORT — {len(tasks)} sessions (MEC>={min_mec},CA1>=20,DG>=15), {workers}w "
          "(remote stream, units only)")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for pop_recs, cell_recs, err in ex.map(_process, tasks):
            if err:
                print("  ERR", err, flush=True); continue
            for r in pop_recs:
                pop_out.write(json.dumps(r) + "\n"); npop += 1
                if r["cell_type"] == "all":
                    ax = r["axes_computed"]
                    def g(k):
                        v = ax.get(k); return f"{v:.3f}" if isinstance(v, float) else "  -"
                    print(f"  {r['session']:12s} {r['region']:4s} {r['aggregation']:11s} "
                          f"nU={r['n_units']:>3d} n={r['n']:>6d} q={g('I.8_brody_q')} "
                          f"BRρ={g('I.9_berry_robnik_rho')}", flush=True)
            for r in cell_recs:
                cell_out.write(json.dumps(r) + "\n"); ncell += 1
            pop_out.flush(); cell_out.flush()
    pop_out.close(); cell_out.close()
    print(f"\n→ {npop} pop + {ncell} per-cell records in {(time.perf_counter()-t0)/60:.1f} min. "
          "Analyse with dual_region_analysis.py. Flag, don't interpret.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--min-mec", type=int, default=20)
    a = ap.parse_args()
    if a.run:
        run(workers=a.workers, min_mec=a.min_mec)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
