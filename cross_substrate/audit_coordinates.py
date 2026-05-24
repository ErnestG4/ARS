"""
cross_substrate/audit_coordinates.py — coordinate-file integrity audit.

Pre-visual data-shoring pass. For every coordinates/*.jsonl: valid JSON per line,
required top-level keys present, the axes_computed key-set, NaN/inf scan, and
computed_date range (stale-value detection vs the Family-II / Benettin re-runs).
Read-only — reports, does not modify.
"""
from __future__ import annotations

import glob
import json
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")

REQUIRED_TOP = {"substrate", "cell_id", "axes_computed"}


def _bad_floats(obj, path=""):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += _bad_floats(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += _bad_floats(v, f"{path}[{i}]")
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            out.append(path)
    return out


def main():
    files = sorted(glob.glob(os.path.join(COORD, "*.jsonl")))
    print(f"INTEGRITY AUDIT — {len(files)} coordinate files\n")
    print(f"{'file':28s} {'cells':>5s} {'substrates':>22s} {'dates':>23s} {'flags'}")
    grand_axes = {}
    for f in files:
        rows, subs, dates, nan_hits, miss_top, bad_json = [], set(), set(), [], 0, 0
        axis_keys = {}
        for ln, line in enumerate(open(f), 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                bad_json += 1
                continue
            rows.append(r)
            if not REQUIRED_TOP.issubset(r):
                miss_top += 1
            subs.add(r.get("substrate", "?"))
            dates.add(r.get("computed_date", "?"))
            for k in (r.get("axes_computed") or {}):
                axis_keys[k] = axis_keys.get(k, 0) + 1
            for p in _bad_floats(r.get("axes_computed", {})):
                nan_hits.append(f"L{ln}{p}")
        flags = []
        if bad_json:
            flags.append(f"BAD_JSON×{bad_json}")
        if miss_top:
            flags.append(f"MISSING_TOPKEY×{miss_top}")
        if nan_hits:
            flags.append(f"NAN/INF×{len(nan_hits)}")
        # axis presence: which axes are NOT on every cell (expected for non-applicable)
        partial = {k: c for k, c in axis_keys.items() if c != len(rows)}
        name = os.path.basename(f)
        dr = (min(dates) if dates else "-") + ("…" + max(dates) if len(dates) > 1 else "")
        print(f"{name:28s} {len(rows):>5d} {','.join(sorted(subs))[:22]:>22s} "
              f"{dr:>23s} {' '.join(flags) if flags else 'ok'}")
        if nan_hits:
            print(f"    NAN/INF at: {nan_hits[:6]}{'…' if len(nan_hits) > 6 else ''}")
        if partial:
            ps = ', '.join(f"{k}:{c}/{len(rows)}" for k, c in sorted(partial.items()))
            print(f"    partial-coverage axes: {ps}")
        for k in axis_keys:
            grand_axes.setdefault(k, set()).add(name)
    print(f"\nUnion of axes across all files ({len(grand_axes)}):")
    for k in sorted(grand_axes):
        print(f"  {k:28s} in {len(grand_axes[k])} files")


if __name__ == "__main__":
    main()
