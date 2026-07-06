"""
cross_substrate/hc3_ec_pillar1.py — pillar-1 (structural poles) for the continuous-attractor EC, via POOLING.

EC population was underpowered per-session for corr-eig (<20 active EC units). Cells are COMMON across all
sessions of a topdir, so we POOL sessions: align units by (ele,clu), stack each session's binned count matrix
vertically (time-concatenate; within-session covariance preserved), giving each unit more counts so more
EC units pass the variance/bulk threshold. Then compute corr-eig Brody q per region. Question: does EC
corr-eig -> GUE (q~1) like CA3 (q=0.97)? Reuses parse_session + _corr_eig + _fp + classify.

Run: python3 hc3_ec_pillar1.py [--topdirs ec013.55 ec013.53 ...] [--behaviors linear bigSquare ...]
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from hc3_port import (parse_session, load_cell_table, load_behavior_map, SESS_ROOT, DT)  # noqa: E402
from population_fingerprint import _corr_eig, _fp, _f  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "phase22a"))
from ars_classify import classify  # noqa: E402


def pooled_corr_eig(topdir, behaviors):
    cellmap = load_cell_table(); bmap = load_behavior_map()
    sdirs = [d for d in sorted(glob.glob(os.path.join(SESS_ROOT, topdir, "*")))
             if os.path.isdir(d) and glob.glob(os.path.join(d, "*.res.*"))]
    # master unit list (ele,clu)->region from any session
    region_of = {}
    per_session = []
    for sdir in sdirs:
        se = os.path.basename(sdir)
        if behaviors and bmap.get(se) not in behaviors:
            continue
        units, tmax, _, _ = parse_session(sdir, topdir, se, cellmap)
        if tmax < 10:
            continue
        d = {}
        for u in units:
            if u["region"] in ("EC", "CA3", "CA1", "DG"):
                key = (u["ele"], u["clu"])
                d[key] = u["spk"]; region_of[key] = u["region"]
        per_session.append((tmax, d))
    if not per_session:
        return {}
    keys = sorted(region_of.keys())
    # build concatenated count matrix: rows=time bins across sessions, cols=units
    blocks = []
    for tmax, d in per_session:
        nb = max(4, int(tmax / DT)); edges = np.linspace(0, tmax, nb + 1)
        M = np.zeros((nb, len(keys)))
        for j, k in enumerate(keys):
            if k in d:
                M[:, j] = np.histogram(d[k], bins=edges)[0]
        blocks.append(M)
    big = np.vstack(blocks)
    out = {}
    for reg in ("EC", "CA3", "CA1", "DG"):
        cols = [j for j, k in enumerate(keys) if region_of[k] == reg]
        if len(cols) < 20:
            out[reg] = {"n_units": len(cols), "note": "underpowered (<20 units)"}
            continue
        Mr = big[:, cols]
        ev = _corr_eig(Mr)
        if ev is None:
            out[reg] = {"n_units": len(cols), "note": "corr-eig None (bulk<30)"}
            continue
        fp = _fp(ev, is_positions=True)
        out[reg] = {"n_units": len(cols), "n_bulk": int(len(ev)),
                    "brody_q": _f(fp.get("I.8_brody_q")), "brho": _f(fp.get("I.9_berry_robnik_rho")),
                    "ks_gue": _f(classify(np.sort(ev)).get("ks_gue_med")),
                    "n_sessions_pooled": len(per_session)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topdirs", nargs="*", default=["ec013.55", "ec013.53", "ec013.54", "ec016.44"])
    ap.add_argument("--behaviors", nargs="*", default=["linear", "bigSquare", "Mwheel", "wheel", "midSquare"])
    a = ap.parse_args()
    print("EC PILLAR-1 via POOLED corr-eig (does EC->GUE like CA3?)")
    print(f"behaviors pooled: {a.behaviors}\n")
    for td in a.topdirs:
        res = pooled_corr_eig(td, a.behaviors)
        if not res:
            print(f"{td}: no sessions on disk"); continue
        print(f"{td}:")
        for reg in ("EC", "CA3", "CA1", "DG"):
            r = res.get(reg)
            if not r:
                continue
            if "brody_q" in r:
                g = lambda v: f"{v:.3f}" if isinstance(v, float) else "  -  "
                print(f"   {reg:4s} corr-eig: q={g(r['brody_q'])} BRρ={g(r['brho'])} ks_gue={g(r['ks_gue'])} "
                      f"(nU={r['n_units']}, bulk={r['n_bulk']}, {r['n_sessions_pooled']} sessions)")
            else:
                print(f"   {reg:4s} corr-eig: {r['note']} (nU={r['n_units']})")


if __name__ == "__main__":
    main()
