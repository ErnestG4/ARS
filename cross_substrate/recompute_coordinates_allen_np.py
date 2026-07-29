"""
recompute_coordinates_allen_np.py — recompute the allen-np block of the coordinate store on the
REPAIRED signed repulsion integral.

Third substrate of the coordinate-store recompute (kuramoto R-175, pvc-11, then this).

allen-np is the hardest of the three and the only one whose events are a DERIVED point process:
each row is a spatial CLUSTER (an anchor unit plus every unit within a distance bin), and the
events are the times at which >= K_THRESH cluster members co-fire in a 5 ms bin. So the recompute
must rebuild the binning, the distance matrix, the anchor subsample and the co-activation
threshold, not just re-read a spike train.

It is reproducible because all of that is deterministic given two things that are both local:
  - the session NWB          $HOME/fmexplorer/allen_cache/session_<id>/session_<id>.nwb  (12/12 present)
  - the spatial positions    data/phase28_results/spatial_positions/session_<id>.parquet (12/12 present)
There is no RNG on the real arm (the surrogate arm has seeds; it is not recomputed here).

FUNCTIONS ARE IMPORTED FROM phase28, NOT REIMPLEMENTED. Reimplementing per_unit_binned_spikes /
cluster_events / the anchor subsample would silently drift from the deployed definitions, and the
whole value of the reproduction check is that it compares against the same code path.

THE BUILT-IN POWERED CHECK: recompute the DEPLOYED `rep_med` and require it to reproduce the banked
parquet before any repaired number is believed.

NON-DESTRUCTIVE: writes a NEW file; the original jsonl and parquet are untouched.

Run:  $HOME/fmexplorer/bin/python3 cross_substrate/recompute_coordinates_allen_np.py [--sessions N]
Writes: cross_substrate/coordinates/allen-np.repaired.jsonl
        cross_substrate/coordinates/allen-np_recompute_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, os.path.join(_ROOT, "phase22a"), os.path.join(_ROOT, "phase24"),
           os.path.join(_ROOT, "phase28")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ars_classify import classify                                        # noqa: E402
from loader import load_session                                          # noqa: E402
from analysis1_spatial_scale_neuropixels import (                        # noqa: E402
    per_unit_binned_spikes, cluster_events, POS_DIR, SPATIAL_BINS,
    ANCHORS_PER_SESSION, MIN_CLUSTER_SIZE, K_THRESH, Q_MAX,
)

BANKED = os.path.join(_ROOT, "data", "phase28_results",
                      "analysis1_per_cluster_real.parquet")
OUT_JSONL = os.path.join(_HERE, "coordinates", "allen-np.repaired.jsonl")
OUT_REPORT = os.path.join(_HERE, "coordinates", "allen-np_recompute_report.json")
p_ = lambda *a: print(*a, flush=True)


def session_rows(session_id):
    """Rebuild one session's clusters exactly as classify_session does, then classify."""
    pos_path = POS_DIR / f"session_{session_id}.parquet"
    if not pos_path.exists():
        return []
    pos_df = pd.read_parquet(pos_path)
    unit_ids = pos_df["unit_id"].astype(int).tolist()
    pos = pos_df[["probe_vertical_position_um",
                  "probe_horizontal_position_um"]].to_numpy()
    d = squareform(pdist(pos))
    rec = load_session(int(session_id))
    mat, total_dur = per_unit_binned_spikes(rec, unit_ids)
    if mat.shape[1] == 0:
        return []
    n_units = len(unit_ids)
    v_order = np.argsort(pos[:, 0])
    if n_units <= ANCHORS_PER_SESSION:
        anchor_idxs = v_order.tolist()
    else:
        sel = np.linspace(0, n_units - 1, ANCHORS_PER_SESSION).astype(int)
        anchor_idxs = [int(v_order[i]) for i in sel]

    out = []
    for bin_name, (lo, hi) in SPATIAL_BINS:
        for anchor in anchor_idxs:
            members = sorted(set([anchor]
                                 + np.where((d[anchor] >= lo) & (d[anchor] <= hi))[0].tolist()))
            if len(members) < MIN_CLUSTER_SIZE:
                continue
            events = cluster_events(mat, members, K_THRESH)
            if events.size < 30:
                out.append((bin_name, int(unit_ids[anchor]), len(members),
                            int(events.size), "underpowered", float("nan"),
                            float("nan"), 0))
                continue
            r = classify(events, return_full=False, q_max=Q_MAX)
            out.append((bin_name, int(unit_ids[anchor]), len(members),
                        int(events.size), r["primary"], r["rep_med"],
                        r.get("rep_med_signed", float("nan")), r["n_well"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=0)
    args = ap.parse_args()

    banked = pd.read_parquet(BANKED)
    sids = sorted(banked.session_id.unique().tolist())
    if args.sessions:
        sids = sids[:args.sessions]
    p_("=" * 84)
    p_("ALLEN-NP COORDINATE RECOMPUTE — deployed rep_med reproduced, signed rep_med added")
    p_(f"  banked rows {len(banked)}   sessions {len(sids)}")
    p_("=" * 84)

    key = {(int(r.session_id), r.bin, int(r.anchor_unit)): float(r.rep_med)
           for r in banked.itertuples()}
    recs, repro_ok, repro_bad, t0 = [], 0, 0, time.time()
    for k, sid in enumerate(sids, 1):
        try:
            rows = session_rows(sid)
        except Exception as e:                                   # noqa: BLE001
            p_(f"  session {sid}: FAILED {repr(e)[:120]}")
            continue
        for bin_name, anchor, n_mem, n_ev, primary, dep, sig, n_well in rows:
            b = key.get((int(sid), bin_name, int(anchor)))
            if b is not None and np.isfinite(b) and np.isfinite(dep):
                if abs(dep - b) < 1e-9:
                    repro_ok += 1
                else:
                    repro_bad += 1
            recs.append({"substrate": "allen-np",
                         "cell_id": f"s{sid}_{bin_name}_a{anchor}",
                         "session_id": int(sid), "bin": bin_name,
                         "anchor_unit": int(anchor), "n_members": n_mem,
                         "n_events": n_ev, "primary": primary, "n_well": n_well,
                         "axes_computed": {"ARS.rep_med": dep,
                                           "ARS.rep_med_signed": sig},
                         "banked_rep_med": b, "recompute_date": "2026-07-28",
                         "note": "rep_med reproduces the deployed clipped value; "
                                 "rep_med_signed is the repaired field"})
        p_(f"  session {k}/{len(sids)} ({sid})  rows={len(recs)}  "
           f"repro ok/bad={repro_ok}/{repro_bad}  {time.time()-t0:.0f}s")

    dep = np.array([r["axes_computed"]["ARS.rep_med"] for r in recs], dtype=float)
    sig = np.array([r["axes_computed"]["ARS.rep_med_signed"] for r in recs], dtype=float)
    m = np.isfinite(dep) & np.isfinite(sig)
    lo0 = int((dep[m] == 0.0).sum())
    changed = int((np.abs(dep[m] - sig[m]) > 1e-9).sum())
    clustered = int((sig[m] < 0).sum())
    inverted = int(((sig[m] < 0) & (dep[m] > 0)).sum())

    p_("\n" + "-" * 84)
    p_(f"  REPRODUCTION of the deployed value: {repro_ok} match, {repro_bad} mismatch")
    if repro_bad:
        p_("  *** pipeline does NOT reproduce its banked output — repaired values NOT trustworthy ***")
    p_(f"  finite pairs {int(m.sum())}  of {len(recs)} rows")
    p_(f"  deployed exactly 0.0 (LOWER rail) : {lo0}  ({100*lo0/max(m.sum(),1):.1f}%)")
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
    rep = {"substrate": "allen-np", "sessions": len(sids), "records": len(recs),
           "reproduction_match": repro_ok, "reproduction_mismatch": repro_bad,
           "trustworthy": repro_bad == 0,
           "n_finite_pair": int(m.sum()), "n_deployed_lower_rail_zero": lo0,
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
