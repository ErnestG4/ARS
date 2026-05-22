"""
cross_substrate/phase2b_recompute.py — Phase 2b: matched object-(a) recompute.

Computes the matched plain-unfolded-NNS axes (Family I.1–I.9 + II.1–II.3) per
substrate cell from the RAW event trains, and MERGES them into the existing
coordinate records (which already carry the q-banded I.5q + III from Phase 2a).
This puts these substrates into AM's frame on object (a).

Brody/BR (I.8/I.9) are banked ONLY if cross_substrate/fitter_validation.json
reports all_pass; else banked None + flag (§7.ter.57).

pvc-11 leg: loader.concatenated_spikes(unit) → unfold_unit_mean → positions →
axes (which route through unfold_rotnum.spacings — matched to AM).

Usage:
  python3 cross_substrate/phase2b_recompute.py pvc-11 [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from phase22a.loader import load                       # noqa: E402
from phase22a.ars_classify import unfold_unit_mean      # noqa: E402
from cross_substrate.axes import (                      # noqa: E402
    compute_family_I, compute_family_II,
)

COORD_DIR = os.path.join(_HERE, "coordinates")
TODAY = date.today().isoformat()
MATCHED_LEG = ("object (a): unfold_unit_mean → unfold_rotnum.spacings "
               "(2–98% trim, unit-mean) — matched to AM W1δ leg")


def _fitter_gate() -> bool:
    p = os.path.join(_HERE, "fitter_validation.json")
    if not os.path.exists(p):
        return False
    return bool(json.load(open(p)).get("all_pass"))


def _read_records(substrate):
    path = os.path.join(COORD_DIR, f"{substrate}.jsonl")
    recs = [json.loads(l) for l in open(path)]
    return path, recs


def _matched_axes(positions, gate_pass: bool) -> dict:
    fI = compute_family_I(positions)
    fII = compute_family_II(positions)
    if not gate_pass:
        fI["I.8_brody_q"] = None
        fI["I.9_berry_robnik_rho"] = None
    out = {**fI, **fII}
    return out


def recompute_pvc11(limit=None):
    gate = _fitter_gate()
    path, recs = _read_records("pvc-11")
    if limit:
        recs = recs[:limit]

    # group cells by recording (cell_id = "recording/unit_id/condition")
    by_rec: dict[str, list] = {}
    for r in recs:
        rec_name = r["cell_id"].split("/")[0]
        by_rec.setdefault(rec_name, []).append(r)

    n_done = 0
    t0 = time.perf_counter()
    for rec_name, cell_recs in by_rec.items():
        recording = load(rec_name)
        uid_to_u = {recording.unit_id(u): u for u in range(recording.n_units)}
        for r in cell_recs:
            uid = r["cell_id"].split("/")[1]
            u = uid_to_u.get(uid)
            if u is None:
                r.setdefault("flags", []).append("unit_id not found in loader")
                continue
            pos = unfold_unit_mean(recording.concatenated_spikes(u))
            matched = _matched_axes(pos, gate)
            r["axes_computed"].update(matched)
            r["applicable_axes_not_yet_computed"] = [
                a for a in r["applicable_axes_not_yet_computed"]
                if a not in matched
            ]
            r["extraction_audit"]["object_a_recompute"] = {
                "leg": MATCHED_LEG, "matched_to_AM": True,
                "fitter_gate_pass": gate, "date": TODAY,
            }
            n_done += 1
    dt = time.perf_counter() - t0
    return path, recs, n_done, dt, gate


def _write(path, recs):
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("substrate", choices=["pvc-11"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="compute + report, do not write back")
    args = ap.parse_args()

    print("=" * 72)
    print(f"PHASE 2b — matched object-(a) recompute: {args.substrate}"
          + (f"  [limit {args.limit}]" if args.limit else "")
          + ("  [DRY-RUN]" if args.dry_run else ""))
    print("=" * 72)

    if args.substrate == "pvc-11":
        path, recs, n_done, dt, gate = recompute_pvc11(args.limit)
    else:
        raise SystemExit("only pvc-11 implemented in this runner")

    print(f"  fitter gate pass: {gate}")
    print(f"  cells recomputed: {n_done}")
    print(f"  elapsed: {dt:.1f}s  ({dt / max(n_done, 1) * 1000:.1f} ms/cell)")
    # quick summary of one example
    ex = next((r for r in recs
               if r["axes_computed"].get("I.1_w1_clock") is not None), None)
    if ex:
        a = ex["axes_computed"]
        print(f"  example {ex['cell_id']}:")
        for k in ("I.1_w1_clock", "I.2_w1_gue", "I.5_ks_gue", "I.8_brody_q",
                  "I.9_berry_robnik_rho", "II.1_sigma2_L", "II.2_delta3_L"):
            v = a.get(k)
            print(f"     {k:22s} = {round(v,4) if isinstance(v,float) else v}")

    if args.dry_run:
        print("  [dry-run] not written")
    else:
        _write(path, recs)
        print(f"  → merged into {os.path.basename(path)}")


if __name__ == "__main__":
    main()
