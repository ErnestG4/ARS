#!/usr/bin/env python3
"""Reproduction gate for the Tier B Brody-axis repair.

A port re-run is only allowed to publish `I.8_brody_q_unbounded` if it first
reproduces `I.8_brody_q` bit-identically against the pre-run baseline.  That
equality is the whole licence: it shows the re-run addressed the same object
set with the same estimator, so the new axis describes the banked objects
rather than some silently different ones.

  python3 cross_substrate/verify_brody_repair.py <substrate> [--baseline DIR]

Exit status is 0 only when the gate passes.
"""
import argparse
import json
import os
import sys
from collections import Counter
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(HERE, "coordinates")

OLD, NEW = "I.8_brody_q", "I.8_brody_q_unbounded"

# Identity columns per substrate.  Deliberately excludes `computed_date` (moves
# every run by design) and `source_artifact` (an absolute path).
KEYS = {
    "ibl-port-cell": ("session", "unit"),
    "buzsaki-port-cell": ("session", "unit", "natural_cell"),
    "dr-port-cell": ("session", "unit"),
    "hc3-port-cell": ("topdir", "session", "ele", "clu", "behavior"),
}


def load(path):
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def keyed(rows, cols):
    out = {}
    for r in rows:
        k = tuple(r.get(c) for c in cols)
        if k in out:
            raise SystemExit(f"FAIL: duplicate identity key {k} — cannot gate on it")
        out[k] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("substrate")
    ap.add_argument("--baseline", default=None,
                    help="baseline dir (default: newest $HOME/fmexplorer/coordinate_baselines_*)")
    a = ap.parse_args()

    sub = a.substrate
    if sub not in KEYS:
        raise SystemExit(f"unknown substrate {sub!r}; known: {', '.join(sorted(KEYS))}")

    base_dir = a.baseline
    if base_dir is None:
        import glob as _g
        # by mtime, not by name: the two naming conventions in use
        # (…2026-07-31 and …2026_07_29) do not sort chronologically
        cands = sorted(_g.glob(os.path.expandvars("$HOME/fmexplorer/coordinate_baselines_*")),
                       key=os.path.getmtime)
        if not cands:
            raise SystemExit("no baseline directory found")
        base_dir = cands[-1]

    new_p = os.path.join(COORD, f"{sub}.jsonl")
    old_p = os.path.join(base_dir, f"{sub}.jsonl")
    for p in (new_p, old_p):
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}")

    print(f"substrate : {sub}")
    print(f"baseline  : {old_p}")
    print(f"candidate : {new_p}\n")

    cols = KEYS[sub]
    old_rows, new_rows = load(old_p), load(new_p)
    print(f"rows      : baseline {len(old_rows)}  candidate {len(new_rows)}")
    if len(old_rows) != len(new_rows):
        print("\nGATE: FAIL — row count changed; this is a different object set, not a recompute.")
        return 1

    O, N = keyed(old_rows, cols), keyed(new_rows, cols)
    if set(O) != set(N):
        only_o, only_n = len(set(O) - set(N)), len(set(N) - set(O))
        print(f"\nGATE: FAIL — identity sets differ (baseline-only {only_o}, candidate-only {only_n}).")
        return 1

    # --- the gate: OLD axis must be bit-identical -----------------------------
    drift, missing = [], 0
    for k in O:
        ov, nv = O[k]["axes_computed"].get(OLD), N[k]["axes_computed"].get(OLD)
        if ov is None and nv is None:
            missing += 1
            continue
        # bit-identical: compare the JSON repr, not a tolerance
        if json.dumps(ov) != json.dumps(nv):
            drift.append((k, ov, nv))

    print(f"{OLD}: {len(O) - missing} comparable, {missing} null-in-both, {len(drift)} drifted")
    if drift:
        print("\nGATE: FAIL — old axis moved. Sample:")
        for k, ov, nv in drift[:5]:
            print(f"  {k}: {ov!r} -> {nv!r}")
        return 1
    print("GATE: PASS — reproduction is EXACT.\n")

    # --- report the repaired axis --------------------------------------------
    newv = [r["axes_computed"].get(NEW) for r in new_rows]
    got = [v for v in newv if isinstance(v, float)]
    oldv = [r["axes_computed"].get(OLD) for r in new_rows]
    oldf = [v for v in oldv if isinstance(v, float)]

    if not got:
        print(f"WARNING: {NEW} absent from every candidate row — the port did not emit it.")
        return 1

    print(f"{NEW}: {len(got)}/{len(new_rows)} non-null")

    # Rail criterion: the largest EXACT-VALUE PILEUP, matching cross_substrate/
    # rail_audit.py::audit_axis.  Do NOT test proximity to the declared bounds
    # 0.0/1.0 -- the optimiser converges to its own floor/ceiling just inside
    # them (on this axis, 6.610696135189609e-05 and 0.9999338930386481), so a
    # within-1e-9-of-a-bound test reports 0% railed on data that is 86% railed.
    rail_report = "n/a"
    if oldf:
        counts = Counter(oldf)
        piles = [(v, c) for v, c in counts.most_common(5) if c > 1]
        railed = sum(c for _, c in piles)
        rail_report = f"{railed}/{len(oldf)} ({100.0 * railed / len(oldf):.1f}%)"
        print(f"  bounded railed : {rail_report}")
        for v, c in piles[:3]:
            print(f"      pileup at {v!r}: {c} ({100.0 * c / len(oldf):.1f}%)")
        print(f"  median bounded : {median(oldf):+.4f}")

    print(f"  median repaired: {median(got):+.4f}")
    print(f"  repaired range : [{min(got):+.4f}, {max(got):+.4f}]")

    # The substantive quantity: how many objects had a true value the bounded
    # axis could not represent at all.
    neg = sum(1 for v in got if v < 0.0)
    gt1 = sum(1 for v in got if v > 1.0)
    print(f"  outside [0,1]  : {neg + gt1}/{len(got)} ({100.0 * (neg + gt1) / len(got):.1f}%) "
          f"— {neg} negative (clustered), {gt1} above 1 (super-rigid)")

    # does the repaired axis itself rail?  its fit bounds are (-1.0, 4.0)
    rc = Counter(got)
    rpiles = [(v, c) for v, c in rc.most_common(3) if c > 1]
    rrail = sum(c for _, c in rpiles)
    print(f"  repaired railed: {rrail}/{len(got)} ({100.0 * rrail / len(got):.1f}%)"
          + (f"  top pileup {rpiles[0][0]!r}" if rpiles else "  — no pileup"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
