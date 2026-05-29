"""
cross_substrate/allen_v1_burst.py — close the H1-not-a-burst-confound loop on V1 (the substrate where
H1 = OSI↔ks_gue was established). allen-depth.jsonl never banked burst. Here: for VISp good units during
drifting_gratings (where g_osi_dg is defined), compute burst_frac + ks_gue + W1 + OSI, then test whether
OSI↔ks_gue (H1) survives controlling for burst, and whether OSI↔burst is ~0 (i.e. H1 is extrinsic-OSI,
not a burst re-encoding). Reuses allen_depth.build_targets (OSI) + extract_train. Out: coordinates/
v1-burst-osi.jsonl. Run: --run [--workers N] | --analyse.
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
import h5py

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                              # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I                  # noqa: E402
from cross_substrate.allen_depth import build_targets, NWB_GLOB, extract_train, _f  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
STIM = "drifting_gratings"
MIN_SPIKES = 100


def _burst(spk):
    isi = np.diff(np.sort(spk)); isi = isi[isi > 0]
    if isi.size < 10:
        return None, None
    return float(np.mean(isi < 0.010)), (float(np.std(isi) / np.mean(isi)) if np.mean(isi) > 0 else None)


def _process(f):
    sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
    tg = build_targets()
    # all Allen visual areas (was VISp-only)
    rows = tg[tg["session_id"] == sid]
    if rows.empty:
        return []
    recs = []
    with h5py.File(f, "r") as h:
        key = f"intervals/{STIM}_presentations"
        if key not in h:
            return []
        st, sp = h[key]["start_time"][:], h[key]["stop_time"][:]
        ids = h["units/id"][:]; row_of = {int(u): r for r, u in enumerate(ids)}
        sti = h["units/spike_times_index"]
        for _, ur in rows.iterrows():
            u = int(ur["unit_id"]); r = row_of.get(u)
            if r is None:
                continue
            lo = 0 if r == 0 else int(sti[r - 1]); hi = int(sti[r])
            spk = h["units/spike_times"][lo:hi]
            train = extract_train(spk, st, sp)
            if train.size < MIN_SPIKES:
                continue
            bf, cv = _burst(train)
            try:
                i5q = _f(classify(train).get("ks_gue_med"))
            except Exception:
                i5q = None
            s = canonical_spacings(train)
            recs.append({"substrate": "v1-burst-osi", "session": sid, "unit_id": u,
                         "area": ur["area"],
                         "osi": _f(ur["g_osi_dg"]) if "g_osi_dg" in ur else None,
                         "n": int(train.size), "burst_frac": bf, "cv_isi": cv,
                         "axes_computed": {"I.5q_ks_gue_med": i5q,
                                           "I.1_w1_clock": _f(FAMILY_I["I.1_w1_clock"](s))},
                         "computed_date": date.today().isoformat()})
    return recs


def run(workers=10):
    files = sorted(glob.glob(NWB_GLOB))
    out = open(os.path.join(COORD, "v1-burst-osi.jsonl"), "w")
    t0 = time.perf_counter(); n = 0
    print(f"V1 burst+OSI extraction — {len(files)} sessions, {workers}w (VISp x drifting_gratings)")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for recs in ex.map(_process, files):
            for r in recs:
                out.write(json.dumps(r) + "\n"); n += 1
            out.flush()
    out.close()
    print(f"→ {n} V1 cells in {(time.perf_counter()-t0)/60:.1f} min. --analyse next.")


def analyse():
    from scipy import stats
    recs = [json.loads(l) for l in open(os.path.join(COORD, "v1-burst-osi.jsonl")) if l.strip()]
    def arr(key, ax=False):
        out = []
        for r in recs:
            v = r["axes_computed"].get(key) if ax else r.get(key)
            out.append(v if (v is not None and np.isfinite(v)) else np.nan)
        return np.array(out, float)
    osi = arr("osi"); ks = arr("I.5q_ks_gue_med", ax=True); bf = arr("burst_frac")
    area = np.array([r.get("area") for r in recs])
    m = np.isfinite(osi) & np.isfinite(ks) & np.isfinite(bf)
    osi_a, ks_a, bf_a, area_a = osi[m], ks[m], bf[m], area[m]
    # per-area breakdown (if multiple areas present)
    areas = sorted(set(area_a) - {None, "nan"})
    if len(areas) > 1:
        print(f"Allen visual hierarchy H1 burst-control (drifting_gratings, n_total={osi_a.size}):\n")
        print(f"  {'area':6s} {'n':>5s} {'raw':>9s} {'OSI↔burst':>11s} {'burst↔ks':>10s} {'PARTIAL':>9s} {'ret%':>6s}")
        for ar in areas:
            mm = area_a == ar
            if mm.sum() < 30:
                continue
            o, k, b = osi_a[mm], ks_a[mm], bf_a[mm]
            r_raw, _ = stats.spearmanr(o, k); r_ob, _ = stats.spearmanr(o, b); r_bk, _ = stats.spearmanr(b, k)
            rx = stats.rankdata(o); ry = stats.rankdata(k); rz = stats.rankdata(b)
            bx = rx - np.polyval(np.polyfit(rz, rx, 1), rz); by = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
            r_part, p_part = stats.pearsonr(bx, by)
            ret = (r_part / r_raw * 100) if r_raw else float("nan")
            tag = " CLEAN" if abs(r_ob) < 0.1 else ""
            print(f"  {ar:6s} {mm.sum():>5d} {r_raw:+9.3f} {r_ob:+11.3f} {r_bk:+10.3f} {r_part:+9.3f} {ret:>6.0f}%{tag}")
        print()
        osi, ks, bf = osi_a, ks_a, bf_a
        print(f"POOLED across visual areas: n={osi.size}\n")
    else:
        osi, ks, bf = osi_a, ks_a, bf_a
        print(f"V1 (VISp, drifting_gratings): n={osi.size} cells with OSI+ks_gue+burst\n")
    def sp(a, b, lab):
        r, p = stats.spearmanr(a, b); print(f"  {lab:28s} ρ={r:+.3f} p={p:.1e}  n={a.size}"); return r
    print("Is ks_gue burst-driven in V1? (expect ~0 if H1 is clean):")
    sp(bf, ks, "burst_frac <-> ks_gue")
    print("\nH1 link + is it burst-mediated?")
    r_ok = sp(osi, ks, "OSI <-> ks_gue (H1)")
    sp(osi, bf, "OSI <-> burst_frac")
    # H1 controlling for burst: residualize ks on burst (rank), then OSI<->resid
    order = np.argsort(bf); br = np.empty_like(bf); br[order] = np.arange(bf.size)
    resid = ks - np.polyval(np.polyfit(br, ks, 1), br)
    rr, pp = stats.spearmanr(osi, resid)
    print(f"\n  OSI <-> ks_gue  BURST-RESID : ρ={rr:+.3f} p={pp:.1e}")
    print("  -> if H1 RESID ρ ≈ raw H1 ρ, the OSI↔class link is NOT burst-mediated (H1 is clean extrinsic-OSI)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--analyse", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    elif a.analyse:
        analyse()
    else:
        ap.error("need --run or --analyse")


if __name__ == "__main__":
    main()
