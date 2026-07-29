"""
recompute_coordinates_pvc11.py — recompute the pvc-11 block of the coordinate store on the
REPAIRED signed repulsion integral.

Second substrate of the coordinate-store recompute (after kuramoto, R-175). pvc-11 is the one the
STALE_AXES_NOTICE singled out: **median rep_med 0.0000, 79.2% exact zeros** — i.e. the block where
the clip's LOWER rail dominates, the mirror image of kuramoto where the newly-found UPPER rail
(0.85) held 56%.

RECOMPUTABLE because the raw recordings are local (`data/pvc-11/data_and_scripts`, 416 MB) and the
banked parquet keys every row by (recording, unit_idx, condition), so each unit's spike stream is
reconstructible exactly through the same loader the original used.

THE BUILT-IN POWERED CHECK, same as kuramoto: recompute the DEPLOYED `rep_med` as well and require
it to reproduce the banked parquet. A repaired number from a pipeline that cannot reproduce its own
banked output is worthless.

NON-DESTRUCTIVE: writes a NEW file; the original jsonl and parquet are untouched.

Run:  $HOME/fmexplorer/bin/python3 cross_substrate/recompute_coordinates_pvc11.py [--limit N]
Writes: cross_substrate/coordinates/pvc-11.repaired.jsonl
        cross_substrate/coordinates/pvc-11_recompute_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from loader import load                       # noqa: E402  phase22a/loader.py
from ars_classify import classify             # noqa: E402

BANKED = os.path.join(_ROOT, "data", "phase22a_results", "h1_classifications.parquet")
OUT_JSONL = os.path.join(_HERE, "coordinates", "pvc-11.repaired.jsonl")
OUT_REPORT = os.path.join(_HERE, "coordinates", "pvc-11_recompute_report.json")
N_PROC = 12
p_ = lambda *a: print(*a, flush=True)

_CACHE = {}


def _rec(name):
    if name not in _CACHE:
        _CACHE[name] = load(name)
    return _CACHE[name]


def _one(args):
    """Worker. Mirrors phase22a/h1_per_unit_ars._classify_one exactly, including the
    pooled-vs-direction split, so the deployed value is reproduced rather than approximated."""
    recording, unit_idx, condition = args
    try:
        rec = _rec(recording)
        if condition in (None, "pooled"):
            ev = rec.concatenated_spikes(unit_idx)
        else:
            ev = rec.concatenated_spikes(unit_idx, condition=int(str(condition).split("_")[-1]))
        r = classify(ev, return_full=False)
        return (recording, unit_idx, condition, r["rep_med"],
                r.get("rep_med_signed", float("nan")), r["primary"], r["n_well"],
                int(ev.size), None)
    except Exception as e:                                   # noqa: BLE001
        return (recording, unit_idx, condition, None, None, None, None, None, repr(e)[:200])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    banked = pd.read_parquet(BANKED)
    if args.limit:
        banked = banked.head(args.limit)
    jobs = [(r.recording, int(r.unit_idx), r.condition) for r in banked.itertuples()]
    p_("=" * 84)
    p_("PVC-11 COORDINATE RECOMPUTE — deployed rep_med reproduced, signed rep_med added")
    p_(f"  banked rows {len(banked)}   jobs {len(jobs)}   procs {N_PROC}")
    p_(f"  conditions: {banked.condition.value_counts().to_dict()}")
    p_("=" * 84)

    t0 = time.time()
    with Pool(N_PROC) as pool:
        out = []
        for k, res in enumerate(pool.imap_unordered(_one, jobs, chunksize=4), 1):
            out.append(res)
            if k % 100 == 0 or k == len(jobs):
                p_(f"  {k}/{len(jobs)}  {time.time()-t0:.0f}s")

    key = {(r.recording, int(r.unit_idx), r.condition): float(r.rep_med)
           for r in banked.itertuples()}
    recs, repro_ok, repro_bad, errs = [], 0, 0, 0
    for recording, unit_idx, cond, dep, sig, primary, n_well, n_ev, err in out:
        if err:
            errs += 1
            continue
        b = key.get((recording, unit_idx, cond))
        if b is not None and np.isfinite(b) and dep is not None and np.isfinite(dep):
            if abs(dep - b) < 1e-9:
                repro_ok += 1
            else:
                repro_bad += 1
        recs.append({"substrate": "pvc-11",
                     "cell_id": f"{recording}_u{unit_idx}_{cond}",
                     "recording": recording, "unit_idx": unit_idx, "condition": cond,
                     "n_events": n_ev, "primary": primary, "n_well": n_well,
                     "axes_computed": {"ARS.rep_med": dep, "ARS.rep_med_signed": sig},
                     "banked_rep_med": b, "recompute_date": "2026-07-28",
                     "note": "rep_med reproduces the deployed clipped value; "
                             "rep_med_signed is the repaired field"})

    dep = np.array([r["axes_computed"]["ARS.rep_med"] for r in recs], dtype=float)
    sig = np.array([r["axes_computed"]["ARS.rep_med_signed"] for r in recs], dtype=float)
    m = np.isfinite(dep) & np.isfinite(sig)
    lo = int((dep[m] == 0.0).sum())
    changed = int((np.abs(dep[m] - sig[m]) > 1e-9).sum())
    clustered = int((sig[m] < 0).sum())
    inverted = int(((sig[m] < 0) & (dep[m] > 0)).sum())

    p_("\n" + "-" * 84)
    p_(f"  REPRODUCTION of the deployed value: {repro_ok} match, {repro_bad} mismatch"
       f"   (worker errors {errs})")
    if repro_bad:
        p_("  *** pipeline does NOT reproduce its banked output — repaired values NOT trustworthy ***")
    p_(f"  finite pairs {int(m.sum())}")
    p_(f"  deployed exactly 0.0 (LOWER rail) : {lo}  ({100*lo/max(m.sum(),1):.1f}%)")
    p_(f"  deployed != signed                : {changed}  ({100*changed/max(m.sum(),1):.1f}%)")
    p_(f"  genuinely CLUSTERED (signed < 0)  : {clustered}")
    p_(f"    of those, deployed read > 0 (SIGN INVERSION): {inverted}")
    if m.sum():
        p_(f"  deployed  mean {dep[m].mean():+.4f}  median {np.median(dep[m]):+.4f}  min {dep[m].min():+.4f}")
        p_(f"  SIGNED    mean {sig[m].mean():+.4f}  median {np.median(sig[m]):+.4f}  min {sig[m].min():+.4f}")
        p_(f"  clipped >= signed on every cell: {bool(np.all(dep[m] >= sig[m] - 1e-12))}")

    with open(OUT_JSONL, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    rep = {"substrate": "pvc-11", "records": len(recs),
           "reproduction_match": repro_ok, "reproduction_mismatch": repro_bad,
           "worker_errors": errs, "trustworthy": repro_bad == 0 and errs == 0,
           "n_finite_pair": int(m.sum()), "n_deployed_lower_rail_zero": lo,
           "n_changed": changed, "n_clustered_signed": clustered,
           "n_sign_inverted": inverted,
           "deployed": {"mean": float(dep[m].mean()), "median": float(np.median(dep[m])),
                        "min": float(dep[m].min())} if m.sum() else None,
           "signed": {"mean": float(sig[m].mean()), "median": float(np.median(sig[m])),
                      "min": float(sig[m].min())} if m.sum() else None}
    with open(OUT_REPORT, "w") as f:
        json.dump(rep, f, indent=2)
    p_(f"\n-> wrote {OUT_JSONL}\n-> wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
