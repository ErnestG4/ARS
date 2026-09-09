"""Guard the graph-staleness census, and fail when the input moves again.

This is the standing half of a one-time census. The census answered "which
artifacts stopped re-deriving when the graph moved on 2026-08-31". The guard
answers the question that will matter next time: **has the input moved again,
and is the recorded re-check list therefore out of date?**

  1. THE INPUT IS PINNED HERE. If the live graph's sha256 stops matching the one
     the census ran against, this fails — because every row below describes a
     comparison against a graph that no longer exists, and the whole list needs
     re-running. That is the check whose absence cost six artifacts.
  2. The recorded arm reversal is preserved. `brocot_truncated_butterfly`'s
     "matched minus plain-q |rho|" reversed sign; its head survived on other
     arms, so a head-level check would have missed it. A census that quietly
     dropped it would restore exactly the blindness it documents.
  3. The clean negative is preserved: horizon_extensions re-derives exactly.
     Naming a moving input makes an artifact UNCHECKED, not stale, and losing
     that row would turn a measured negative into an assumption.
  4. Every subject still exists and still loads the graph, so the census's scope
     claim stays true of the tree rather than of the day it was written.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
bad = []
c = json.load(open(os.path.join(HERE, "graph_staleness_census.json")))

gpath = os.path.join(BROCOT, "resources", c["graph"])
if not os.path.exists(gpath):
    print(f"  SKIP — {c['graph']} not present (sibling repo absent)")
    print("VERIFY_GRAPH_STALENESS: PASS (input unavailable; nothing to compare)")
    sys.exit(0)
live = hashlib.sha256(open(gpath, "rb").read()).hexdigest()
if live != c["graph_sha256"]:
    bad.append(f"the graph has MOVED AGAIN: live {live[:16]}... vs census "
               f"{c['graph_sha256'][:16]}.... Every row in this census compares "
               "against a graph that no longer exists, so the re-check list is "
               "stale. Re-run graph_staleness_census.py.")

for name in c["subjects"]:
    py = os.path.join(HERE, name + ".py")
    js = os.path.join(HERE, name + ".json")
    if not os.path.exists(py) or not os.path.exists(js):
        bad.append(f"{name}: generator or artifact missing; the census scope no "
                   "longer matches the tree")
        continue
    if c["graph"] not in open(py).read():
        bad.append(f"{name} no longer loads {c['graph']} — it should leave the "
                   "census, not sit in it as a false positive")

if "brocot_truncated_butterfly" not in c["arm_reversals"]:
    bad.append("the recorded arm reversal is gone. It is the census's sharpest "
               "finding precisely because the composed head did NOT change, and "
               "dropping it restores the head-level blindness the census exists "
               "to document")
if "brocot_horizon_extensions" not in c["clean"]:
    bad.append("the clean negative (horizon_extensions re-derives exactly) is "
               "gone; naming a moving input makes an artifact unchecked, not "
               "stale, and that distinction needs a measured example")
if c["n_verdicts_changed"] != 0:
    bad.append(f"{c['n_verdicts_changed']} composed verdict(s) now recorded as "
               "changed — that is a much larger finding than drift and must not "
               "sit inside a census summary line")
if "POST-HOC" not in c["status"].upper():
    bad.append("the census has lost its POST-HOC label")

print(f"  graph {c['graph']} sha {live[:16]}... "
      + ("matches the census" if live == c["graph_sha256"] else "HAS MOVED"))
print(f"  {len(c['stale'])} stale, {len(c['clean'])} clean of "
      f"{len(c['subjects'])} subjects; verdicts changed: {c['n_verdicts_changed']}")
for n, fl in c["arm_reversals"].items():
    for f in fl:
        print(f"  preserved arm reversal: {n} — {f['bar'].split('/')[-2]}")

if bad:
    print("VERIFY_GRAPH_STALENESS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_GRAPH_STALENESS: PASS — the graph still matches the census's pin, "
      "every subject still loads it, and both the arm reversal and the clean "
      "negative are preserved")
