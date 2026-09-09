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

# The re-banked artifact must exist, be pinned to the graph it was measured on,
# and still record the flip. Re-banking preserves a number by SCOPING it to its
# input; an unpinned re-bank would just restage the original defect.
RG = os.path.join(HERE, "brocot_truncated_butterfly_regraph.json")
if not os.path.exists(RG):
    bad.append("brocot_truncated_butterfly_regraph.json is missing — the arm "
               "reversal was re-banked on 2026-09-09 and that artifact is where "
               "the current-graph numbers live")
else:
    rg = json.load(open(RG))
    prov = rg.get("provenance", {})
    if prov.get("graph_sha256") != c["graph_sha256"]:
        bad.append("the re-banked truncated_butterfly names a different graph "
                   "sha than the census — one of them is measuring another tree")
    h3 = rg["bars"].get("matched minus plain-q |rho|")
    if h3 is None or h3["met"] or h3["value"] >= 0:
        bad.append(f"the re-bank no longer records H3 as MISSED with a negative "
                   f"value ({h3}) — that reversal is the whole reason it exists")
    if rg.get("verdict") != c["rows"]["brocot_truncated_butterfly"].get("verdict_changed", []) and \
       rg.get("verdict") != "MAP_TRACKS_THE_TRUNCATION":
        bad.append(f"the re-bank's head is {rg.get('verdict')!r}; it should still "
                   "read MAP_TRACKS_THE_TRUNCATION, since the head reads EXISTENCE "
                   "arms only and both still hold")

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
