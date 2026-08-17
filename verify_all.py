#!/usr/bin/env python3
"""Run every live checker in the repository and report one pass/fail board.

Each arc keeps a `verify_*.py` that re-derives its banked claims from the
committed artifacts and exits nonzero on any regression.  Several also carry
blob-SHA tamper-evidence against their seal's freeze list, so an edited
artifact fails even if its numbers still look plausible.

    python3 verify_all.py              # run the board
    python3 verify_all.py --list       # show what would run, run nothing
    python3 verify_all.py -k comb      # run only checkers matching a substring
    python3 verify_all.py --timeout 900

Exit code is 0 only if every checker that ran passed.

WHAT A GREEN BOARD DOES AND DOES NOT MEAN.  Green says: the numbers in the
findings documents are the numbers in the artifacts, the artifacts have not
been edited since they were sealed, and the derived quantities re-derive.  It
does NOT say the measurements are correct, that the instrument measures what
we claim, or that a conclusion follows from its data.  Those are judgements no
checker can make; they are what an outside reader is for.
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

# Checkers needing arguments are not board items; they are tools. Listed so the
# board is honest about what it is NOT covering.
PARAMETERIZED = {
    "verify_brody_repair.py": "takes a coordinate stem, e.g. "
                              "`python3 verify_brody_repair.py hc3-port-cell`",
}

# External datasets a checker needs but the repository does not redistribute.
# Missing input is reported as SKIP, never as FAIL: a row that is permanently
# red for a benign reason trains the reader to ignore red rows, which is how a
# guard goes inert. See data/README.md for how to obtain these.
REQUIRES = {
    "arsrh/verify_brief_v2.py": ["data/odlyzko_zeros1.txt"],
    "phase22a/verify_calibrators.py": ["data/odlyzko_zeros1.txt"],
}


def discover():
    found = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in
                   (".git", "__pycache__", "node_modules", "archive_v1grid")]
        for fn in files:
            if not (fn.startswith("verify_") and fn.endswith(".py")):
                continue
            full = os.path.join(root, fn)
            if os.path.abspath(full) == os.path.abspath(__file__):
                continue          # never discover self — that recurses
            found.append(full)
    return sorted(found)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-k", "--filter", default=None,
                    help="only run checkers whose path contains this substring")
    ap.add_argument("--list", action="store_true", help="list checkers, run nothing")
    ap.add_argument("--timeout", type=int, default=900, help="per-checker seconds")
    a = ap.parse_args()

    checkers = discover()
    if a.filter:
        checkers = [c for c in checkers if a.filter in c]
    if not checkers:
        print("no checkers found", file=sys.stderr)
        return 1

    board, skipped, no_data = [], [], []
    for c in checkers:
        rel = os.path.relpath(c, HERE)
        if os.path.basename(c) in PARAMETERIZED:
            skipped.append((rel, PARAMETERIZED[os.path.basename(c)]))
            continue
        missing = [d for d in REQUIRES.get(rel.replace(os.sep, "/"), [])
                   if not os.path.exists(os.path.join(HERE, d))]
        if missing:
            no_data.append((rel, missing))
            continue
        board.append((rel, c))

    if a.list:
        for rel, missing in no_data:
            print(f"  (would skip {rel}: needs {', '.join(missing)})")
        print(f"{len(board)} board checkers:")
        for rel, _ in board:
            print(f"  {rel}")
        if skipped:
            print(f"\n{len(skipped)} parameterized tools (not board items):")
            for rel, why in skipped:
                print(f"  {rel}\n      {why}")
        return 0

    for rel, missing in no_data:
        print(f"  SKIP  {rel} — needs {', '.join(missing)} (see data/README.md)")
    if no_data:
        print()
    print(f"running {len(board)} checkers from {HERE}\n", flush=True)
    width = max(len(r) for r, _ in board)
    results = []
    for rel, path in board:
        t0 = time.time()
        try:
            p = subprocess.run([PY, os.path.basename(path)], cwd=os.path.dirname(path),
                               capture_output=True, text=True, timeout=a.timeout)
            rc, out = p.returncode, (p.stdout + p.stderr)
        except subprocess.TimeoutExpired:
            rc, out = 124, f"TIMEOUT after {a.timeout}s"
        dt = time.time() - t0
        results.append((rel, rc, dt, out))
        mark = "PASS" if rc == 0 else "FAIL"
        print(f"  {mark}  {rel:<{width}}  {dt:6.1f}s"
              + ("" if rc == 0 else f"  exit={rc}"), flush=True)

    bad = [r for r in results if r[1] != 0]
    print("\n" + "-" * (width + 22))
    print(f"  {len(results) - len(bad)}/{len(results)} passed")
    if no_data:
        print(f"  {len(no_data)} skipped for missing external data "
              f"(not a failure — see data/README.md):")
        for rel, missing in no_data:
            print(f"      {rel} — {', '.join(missing)}")
    if skipped:
        print(f"  {len(skipped)} parameterized tool(s) not run:")
        for rel, why in skipped:
            print(f"      {rel} — {why}")
    if bad:
        print("\nfailures in full:\n")
        for rel, rc, _, out in bad:
            print(f"===== {rel} (exit {rc}) " + "=" * 20)
            print(out.rstrip()[:4000])
            print()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
