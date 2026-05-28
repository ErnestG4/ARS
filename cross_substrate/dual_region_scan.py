"""
cross_substrate/dual_region_scan.py — remote-stream the units table of every 000638 session and tabulate
units per coarse region x cell-type, to pick sessions richest in MEC+CA3 (the EC-vs-CA3 headline contrast).

Reads only units + electrodes tables over HTTP range (no raw-trace download). Writes a composition table.
000638 = "Hippocampus and Entorhinal Cortex Dual Region Silicon Probe recording" (turnkey NWB, MEC+HPC).
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

from nwb_remote import open_dandi_asset

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
DANDISET = "000638"


def coarse_region(fine: str) -> str:
    f = (fine or "").strip()
    if f.startswith("MEC"):
        return "MEC"
    if f.startswith("LEC"):
        return "LEC"
    if f.startswith("CA3"):
        return "CA3"
    if f in ("Pyr", "Or", "Rad", "LM", "SP", "SO", "SR", "SLM", "Py"):
        return "CA1"
    if f in ("GC", "Hil", "Mol", "LB", "UB", "ML", "DG", "po"):
        return "DG"
    return "other"


def _dec(a):
    return [x.decode() if isinstance(x, bytes) else x for x in a]


def unit_regions(h):
    """Per-unit coarse region (via units/electrodes -> electrodes/location) + fine label + unit_type."""
    eg = "general/extracellular_ephys/electrodes"
    eloc = _dec(h[eg]["location"][:]) if "location" in h[eg] else None
    u = h["units"]
    el = u["electrodes"][:]
    eli = u["electrodes_index"][:]
    utype = _dec(u["unit_type"][:]) if "unit_type" in u else ["?"] * len(eli)
    fine, coarse = [], []
    prev = 0
    for idx in eli:
        sl = el[prev:int(idx)]
        prev = int(idx)
        if len(sl) == 0 or eloc is None:
            fine.append("?")
            coarse.append("other")
            continue
        f = eloc[int(sl[0])]
        fine.append(f)
        coarse.append(coarse_region(f))
    return fine, coarse, utype


def _scan(arg):
    aid, size, path = arg
    sid = path.split("/")[0]
    try:
        h = open_dandi_asset(DANDISET, aid, size=size)
        fine, coarse, utype = unit_regions(h)
        n = len(coarse)
        # composition: region -> {exc, inh, unc, total}
        comp = {}
        for r, t in zip(coarse, utype):
            d = comp.setdefault(r, {"excitatory": 0, "inhibitory": 0, "other": 0, "total": 0})
            key = t if t in ("excitatory", "inhibitory") else "other"
            d[key] += 1
            d["total"] += 1
        h.close()
        return {"session": sid, "asset_id": aid, "n_units": n, "comp": comp, "ok": True}
    except Exception as e:
        return {"session": sid, "asset_id": aid, "ok": False, "err": f"{type(e).__name__}: {e}"}


def main(workers=8):
    assets = json.load(open(os.path.join(COORD, "dr000638_assets.json")))
    tasks = [(a["asset_id"], a["size"], a["path"]) for a in assets]
    t0 = time.perf_counter()
    rows = []
    print(f"DUAL-REGION SCAN — {len(tasks)} sessions of 000638, {workers}w (units table only)")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(_scan, tasks):
            rows.append(r)
            if r["ok"]:
                c = r["comp"]
                def g(reg):
                    return c.get(reg, {}).get("total", 0)
                print(f"  {r['session']:14s} n={r['n_units']:4d}  MEC={g('MEC'):3d} LEC={g('LEC'):3d} "
                      f"CA3={g('CA3'):3d} CA1={g('CA1'):3d} DG={g('DG'):3d} other={g('other'):3d}",
                      flush=True)
            else:
                print(f"  {r['session']:14s} FAILED {r['err']}", flush=True)
    json.dump(rows, open(os.path.join(COORD, "dr000638_composition.json"), "w"), indent=1)
    ok = [r for r in rows if r["ok"]]
    # rank for EC-vs-CA3 (need MEC and CA3 both present)
    print(f"\n{len(ok)}/{len(rows)} scanned ok in {(time.perf_counter()-t0)/60:.1f} min.")
    print("\nSessions with BOTH MEC>=8 and CA3>=8 (headline EC-vs-CA3):")
    for r in sorted(ok, key=lambda x: -(min(x['comp'].get('MEC',{}).get('total',0),
                                            x['comp'].get('CA3',{}).get('total',0)))):
        m = r['comp'].get('MEC',{}).get('total',0); c3 = r['comp'].get('CA3',{}).get('total',0)
        if m >= 8 and c3 >= 8:
            print(f"  {r['session']:14s} MEC={m} CA3={c3} CA1={r['comp'].get('CA1',{}).get('total',0)} "
                  f"DG={r['comp'].get('DG',{}).get('total',0)}")


if __name__ == "__main__":
    w = int(sys.argv[sys.argv.index("--workers")+1]) if "--workers" in sys.argv else 8
    main(workers=w)
