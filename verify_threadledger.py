"""Board row for the thread ledger.

RENAMED 2026-08-25, from queue.py / verify_queue.py: `queue` shadows a stdlib
module, and because the repo root precedes stdlib on sys.path, ANY script run
from the root that imported `concurrent.futures` died with
`AttributeError: module 'queue' has no attribute 'SimpleQueue'`.
`run_phase20_acquire.py` does exactly that. A ledger built to make things
visible was silently breaking unrelated scripts.

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
from threadledger import DROPPED, LANDED, QUEUED, load                          # noqa: E402

# ---------------------------------------------------------------------------
# SELF-TEST, added 2026-09-02 with the amendment fix. A sealed cell records a
# correction in `verdict_amended`, NOT by overwriting `verdict` -- and for as
# long as the resolver read `verdict` alone, this board certified six citations
# whose artifacts had already been amended, four of them to the REVERSE of the
# seal. The check that exists to catch verdict drift was blind to the repo's
# only mechanism for verdict drift.
#
# So the checker red-paths itself on that exact finding before it grades
# anything: build an artifact carrying both keys and require the resolver to
# return the AMENDMENT. If anyone re-points it at the seal, this fails loudly
# here instead of going quietly green on a superseded claim.
def _self_test():
    import json as _json, tempfile as _tf
    from threadledger import _verdict_of
    d = _tf.mkdtemp()
    with open(os.path.join(d, "a.json"), "w") as fh:
        _json.dump({"verdict": "SEALED_HEAD",
                    "verdict_amended": "AMENDED_HEAD"}, fh)
    got = _verdict_of(d, "a.json")
    if got != "AMENDED_HEAD":
        print("  FAIL  SELF-TEST: _verdict_of returned %r, not the amendment. "
              "The 2026-09-02 blind spot is back: an amended artifact would "
              "read as its dead seal and every row citing it would pass."
              % (got,))
        sys.exit(1)
    with open(os.path.join(d, "b.json"), "w") as fh:
        _json.dump({"verdict": "SEALED_HEAD"}, fh)
    if _verdict_of(d, "b.json") != "SEALED_HEAD":
        print("  FAIL  SELF-TEST: an un-amended artifact no longer resolves -- "
              "the fix would then hide every row it was meant to check.")
        sys.exit(1)
    print("  self-test: amendment beats seal, seal still resolves\n")


_self_test()
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
stale = [e for e in rows if e.get("warrant_stale")]
for e in rows:
    if e["status"] == QUEUED:
        mark = "  WARRANT_STALE" if e.get("warrant_stale") else ""
        print(f"        QUEUED   {e['id']:<24s} {e['request'][:52]}{mark}")
for e in stale:
    for w in e["warrant_stale"]:
        print(f"  FAIL  WARRANT_STALE  {e['id']} [{w.get('layer', 'unlabelled')}]: "
              f"{os.path.basename(w['artifact'])} "
              f"was {w['minted']!r} when this row was minted, is now {w['now']!r}. "
              "Re-adjudicate and record the new verdict in warrant_reviewed — "
              "an action inherits its premise's changes.")
bad += stale
# DROPPED rows were rendered by nothing at all until 2026-08-25 — a disposition
# class invisible on the board, in the file whose purpose is visibility.
for e in rows:
    if e["status"] == DROPPED:
        print(f"        DROPPED  {e['id']:<24s} {e['request'][:64]}")
bad_status = [e for e in rows if e["status"] not in (LANDED, QUEUED, DROPPED)]
for e in bad_status:
    print(f"  FAIL  UNKNOWN STATUS {e['status']!r} on {e['id']} — a typo'd "
          "status made an entry vanish silently before this check existed")
bad += bad_status

n = sum(1 for e in rows if e["status"] == LANDED)
q = sum(1 for e in rows if e["status"] == QUEUED)
dr = sum(1 for e in rows if e["status"] == DROPPED)
nbad = sum(1 for e in bad if e["status"] == LANDED)
print(f"\n  {n - nbad}/{n} landed threads verify; {q} open, {dr} dropped "
      "(all visible by design; open and dropped do not fail the board)")
if bad:
    print("\nVERIFY_QUEUE: FAIL")
    sys.exit(1)
print("\nVERIFY_QUEUE: PASS — every landed thread names an artifact whose "
      "verdict still matches, and every open thread is on the board.")
