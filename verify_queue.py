"""Board row for the queued-thread ledger.

WHAT TURNS THIS RED: a LANDED entry whose artifact is missing, or whose recorded
verdict no longer matches the artifact on disk. Either means the ledger is
claiming a thread was resolved when it was not, which is worse than no ledger.

WHAT DOES NOT TURN IT RED: an open QUEUED entry. Forcing the work would be wrong;
making it invisible is what this file exists to prevent. QUEUED items print on
every green board, exactly as `verify_pending_debt` prints proposals.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from queue import LANDED, QUEUED, load                          # noqa: E402

rows = load(HERE)
bad = []
print("queued-thread ledger\n")
for e in rows:
    if e["status"] == LANDED:
        ok = e["artifact_exists"] and e["verdict_matches"]
        if not ok:
            bad.append(e)
        why = ("" if ok else
               "  [artifact missing]" if not e["artifact_exists"] else
               "  [verdict no longer matches the artifact]")
        print(f"  {'PASS' if ok else 'FAIL'}  LANDED   {e['id']:<24s} "
              f"{e['verdict']}{why}")
for e in rows:
    if e["status"] == QUEUED:
        print(f"        QUEUED   {e['id']:<24s} {e['request'][:64]}")

n = sum(1 for e in rows if e["status"] == LANDED)
q = sum(1 for e in rows if e["status"] == QUEUED)
print(f"\n  {n - len(bad)}/{n} landed threads verify; {q} still open "
      "(visible by design; does not fail the board)")
if bad:
    print("\nVERIFY_QUEUE: FAIL")
    sys.exit(1)
print("\nVERIFY_QUEUE: PASS — every landed thread names an artifact whose "
      "verdict still matches, and every open thread is on the board.")
