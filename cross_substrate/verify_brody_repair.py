#!/usr/bin/env python3
"""Reproduction gate for the Brody-axis repair propagation (Tier B / Tier C).

A producer re-run is only allowed to publish `I.8_brody_q_unbounded` if it first
reproduces its banked values bit-identically against a pre-run baseline. That
equality is the whole licence: it shows the re-run addressed the same object set
with the same estimators, so the new axis describes the banked objects rather
than some silently different ones.

  python3 cross_substrate/verify_brody_repair.py <file-stem> [--baseline DIR]

Takes the coordinate FILE STEM (e.g. `quasiperiodic-operators`), not the
`substrate` field -- they differ on several files.

WHY THE GATE COMPARES EVERY AXIS, not just I.8_brody_q
------------------------------------------------------
On some substrates the bounded Brody axis is almost constant: pvc-11 banks 1152
of 1159 values on a single rail value, leaving 7 uniquely valued rows. A gate
that checks only I.8_brody_q there is very nearly INERT -- it would pass on a
run that had silently changed almost everything else. So the gate compares the
full axis vector and reports drift per axis.

PASS requires: identical row count, identical identity fields, and zero drift on
I.8_brody_q. Drift on OTHER axes does not fail the gate but is always reported,
because some of it is legitimate and known:
  * I.9_berry_robnik_rho -- the fitter was CORRECTED (axes.py now imports
    phase34e.run_berry_robnik.fit_rho), so old values are expected to move; and
    separately, population channels unfold via np.polyfit and drift in the 3rd
    decimal across identical runs.
  * new keys (I.10_cv, I.11_mass03, I.12_cv2, I.13_lv) appear on re-run because
    FAMILY_I grew -- these are additions, not drift.
Anything else drifting is a finding: read it, do not wave it through.
"""
import argparse
import glob as _glob
import json
import os
import sys
from collections import Counter, defaultdict
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(HERE, "coordinates")

OLD, NEW = "I.8_brody_q", "I.8_brody_q_unbounded"

# Axes whose movement is explained and does not by itself fail the gate.
EXPECTED_TO_MOVE = {"I.9_berry_robnik_rho"}

# Never part of an object's identity: one moves every run by design, the other
# is an absolute path.
NON_IDENTITY = {"axes_computed", "computed_date", "source_artifact"}


def load(path):
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def identity(r):
    return tuple(sorted((k, json.dumps(v, sort_keys=True))
                        for k, v in r.items() if k not in NON_IDENTITY))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem", help="coordinate file stem, e.g. 'hc3-port-cell'")
    ap.add_argument("--baseline", default=None,
                    help="baseline dir (default: newest $HOME/fmexplorer/coordinate_baselines_* by mtime)")
    a = ap.parse_args()

    base_dir = a.baseline
    if base_dir is None:
        # by mtime, not by name: the naming conventions in use
        # (…2026-07-31 and …2026_07_29) do not sort chronologically.
        cands = sorted(_glob.glob(os.path.expandvars("$HOME/fmexplorer/coordinate_baselines_*")),
                       key=os.path.getmtime)
        if not cands:
            raise SystemExit("no baseline directory found")
        base_dir = cands[-1]

    new_p = os.path.join(COORD, f"{a.stem}.jsonl")
    old_p = os.path.join(base_dir, f"{a.stem}.jsonl")
    for p in (new_p, old_p):
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}")

    print(f"file      : {a.stem}.jsonl")
    print(f"baseline  : {old_p}")
    print(f"candidate : {new_p}\n")

    old_rows, new_rows = load(old_p), load(new_p)
    print(f"rows      : baseline {len(old_rows)}  candidate {len(new_rows)}")
    if len(old_rows) != len(new_rows):
        print("\nGATE: FAIL — row count changed; a different object set, not a recompute.")
        return 1
    if not new_rows:
        print("\nGATE: FAIL — candidate is EMPTY (truncated mid-write?).")
        return 1

    # Producers emit in a deterministic order, so compare positionally and
    # verify the identity fields agree at each position.
    mismatched = [i for i, (o, n) in enumerate(zip(old_rows, new_rows))
                  if identity(o) != identity(n)]
    if mismatched:
        print(f"\nGATE: FAIL — identity fields differ at {len(mismatched)} row(s); "
              f"first at index {mismatched[0]}.")
        o, n = old_rows[mismatched[0]], new_rows[mismatched[0]]
        for k in sorted(set(o) | set(n)):
            if k not in NON_IDENTITY and o.get(k) != n.get(k):
                print(f"    {k}: {o.get(k)!r} -> {n.get(k)!r}")
        return 1

    # ---- full axis-vector comparison ----------------------------------------
    axes = sorted({k for r in old_rows for k in (r.get("axes_computed") or {})})
    drift = defaultdict(list)
    comparable = Counter()
    for i, (o, n) in enumerate(zip(old_rows, new_rows)):
        ao, an = (o.get("axes_computed") or {}), (n.get("axes_computed") or {})
        for ax in axes:
            ov, nv = ao.get(ax), an.get(ax)
            if ov is None and nv is None:
                continue
            comparable[ax] += 1
            if json.dumps(ov) != json.dumps(nv):
                drift[ax].append((i, ov, nv))

    old_vals = [r["axes_computed"].get(OLD) for r in old_rows]
    oldf = [v for v in old_vals if isinstance(v, float)]
    distinct = len(set(oldf))

    print(f"axes compared: {len(axes)}")
    for ax in axes:
        d = len(drift[ax])
        tag = ""
        if d:
            tag = "  [expected: corrected fitter / polyfit unfold]" if ax in EXPECTED_TO_MOVE \
                  else "  <-- UNEXPECTED"
        print(f"  {ax:28s} {comparable[ax]:6d} comparable  {d:5d} drifted{tag}")

    # power of the gate on THIS substrate
    print(f"\ngate power on {OLD}: {len(oldf)} values, {distinct} distinct")
    if distinct <= 3 and len(oldf) > 50:
        print(f"  ⚠ NEARLY INERT on {OLD} alone ({distinct} distinct values) — "
              f"the full axis vector above is what carries this gate.")

    if drift[OLD]:
        print(f"\nGATE: FAIL — {OLD} moved on {len(drift[OLD])} row(s). Sample:")
        for i, ov, nv in drift[OLD][:5]:
            print(f"  row {i}: {ov!r} -> {nv!r}")
        return 1

    unexpected = {ax: len(v) for ax, v in drift.items()
                  if v and ax != OLD and ax not in EXPECTED_TO_MOVE}
    print(f"\nGATE: PASS — {OLD} reproduction is EXACT.")
    if unexpected:
        print(f"  ⚠ but {len(unexpected)} other axis/axes moved unexpectedly: {unexpected}")
        print("    Investigate before trusting the repaired values.")

    # ---- report the repaired axis -------------------------------------------
    newv = [r["axes_computed"].get(NEW) for r in new_rows]
    got = [v for v in newv if isinstance(v, float)]
    if not got:
        print(f"\nWARNING: {NEW} absent from every candidate row — the producer did not emit it.")
        return 1

    print(f"\n{NEW}: {len(got)}/{len(new_rows)} non-null")

    # Rail criterion: the largest EXACT-VALUE PILEUP, matching rail_audit.py.
    # Do NOT test proximity to the declared bounds 0.0/1.0 -- the optimiser
    # converges just inside them (6.610696135189609e-05, 0.9999338930386481), so
    # a within-1e-9-of-a-bound test reports 0% railed on 86%-railed data.
    if oldf:
        counts = Counter(oldf)
        piles = [(v, c) for v, c in counts.most_common(5) if c > 1]
        railed = sum(c for _, c in piles)
        print(f"  bounded railed : {railed}/{len(oldf)} ({100.0 * railed / len(oldf):.1f}%)")
        for v, c in piles[:3]:
            print(f"      pileup at {v!r}: {c} ({100.0 * c / len(oldf):.1f}%)")
        print(f"  median bounded : {median(oldf):+.4f}")

    print(f"  median repaired: {median(got):+.4f}")
    print(f"  repaired range : [{min(got):+.4f}, {max(got):+.4f}]")
    neg = sum(1 for v in got if v < 0.0)
    gt1 = sum(1 for v in got if v > 1.0)
    print(f"  outside [0,1]  : {neg + gt1}/{len(got)} ({100.0 * (neg + gt1) / len(got):.1f}%) "
          f"— {neg} negative (clustered), {gt1} above 1 (super-rigid)")

    rc = Counter(got)
    rpiles = [(v, c) for v, c in rc.most_common(3) if c > 1]
    rrail = sum(c for _, c in rpiles)
    print(f"  repaired railed: {rrail}/{len(got)} ({100.0 * rrail / len(got):.1f}%)"
          + (f"  top pileup {rpiles[0][0]!r}" if rpiles else "  — no pileup"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
