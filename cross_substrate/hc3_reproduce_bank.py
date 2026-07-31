#!/usr/bin/env python3
"""Re-run hc3_port over EXACTLY the sessions present in the banked coordinate file.

WHY THIS EXISTS
---------------
`hc3_port.run()` calls `find_sessions()`, a bare glob of `sessions/*/*`, and has
no flag that can restrict it.  Since the bank was written (computed_date
2026-06-01) the cache gained `ec016.11/ec016.106`, downloaded 2026-06-04.  A
bare `hc3_port.py --run` therefore addresses 23 sessions and writes 971 per-cell
rows over a 923-row bank -- a different object set, so the reproduction gate
that licenses the repaired Brody axis could never pass.

Tier B is a REPAIR of banked values, not an EXTENSION of the bank.  Those are
separate operations and must not be conflated: extending the object set in the
same run would make it impossible to tell a genuine estimator change from the
arrival of new sessions.  So this driver reproduces the bank, and the new
session is left for a deliberate, separately-gated extension.

The session list is derived FROM THE BANK ITSELF rather than hardcoded, so it
cannot drift out of sync with the file it is meant to reproduce.

  python3 cross_substrate/hc3_reproduce_bank.py [--workers 6] [--dry-run]
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import json  # noqa: E402

from cross_substrate import hc3_port  # noqa: E402

BANK = os.path.join(_HERE, "coordinates", "hc3-port-cell.jsonl")


def banked_pairs(path):
    """The (topdir, session) pairs the banked file actually covers."""
    pairs = set()
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                pairs.add((r["topdir"], r["session"]))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--bank", default=BANK,
                    help="file whose session set defines the run (default: the banked cell file)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the session selection and exit WITHOUT writing anything")
    a = ap.parse_args()

    want = banked_pairs(a.bank)
    discovered = hc3_port.find_sessions()
    keep = [t for t in discovered if (t[1], t[2]) in want]

    found_pairs = {(t[1], t[2]) for t in discovered}
    excluded = sorted(found_pairs - want)
    missing = sorted(want - found_pairs)

    print(f"bank        : {a.bank}")
    print(f"bank covers : {len(want)} sessions")
    print(f"on disk     : {len(discovered)} sessions")
    print(f"selected    : {len(keep)} sessions")
    for t, s in excluded:
        print(f"  EXCLUDED (on disk, not in bank): {t}/{s}")
    for t, s in missing:
        print(f"  !! MISSING (in bank, not on disk): {t}/{s}")

    if missing:
        print("\nABORT: the cache can no longer supply every banked session; "
              "reproduction is impossible and a partial run would truncate the bank.")
        return 1
    if len(keep) != len(want):
        print("\nABORT: selection does not match the bank.")
        return 1

    if a.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    # Restrict the port to the banked object set.  run() takes its tasks from
    # find_sessions(), so this is the only interception point.
    hc3_port.find_sessions = lambda: keep
    print(f"\nrunning hc3_port over {len(keep)} banked sessions, {a.workers} workers\n", flush=True)
    hc3_port.run(workers=a.workers)
    return 0


if __name__ == "__main__":
    sys.exit(main())
