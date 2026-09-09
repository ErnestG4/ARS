#!/usr/bin/env python3
"""CENSUS: which banked artifacts no longer re-derive from the graph they name?

POST-HOC AND UNSEALED. It measures the repo against its own inputs and makes no
prediction. It is reproducible: it re-runs each committed generator in a
temporary directory (they all write beside their own file, so a copy isolates
them) and diffs the result against what is banked here.

WHY, AND WHY THE SCOPE IS BIGGER THAN THE ONE CASE WE ALREADY KNEW
-------------------------------------------------------------------
On 2026-09-06 `brocot_filter_worth_it.json` was found stale: it named its input
-- brocot's `landscape_graph_16mix.json.gz` -- by PATH, and brocot regenerated
that graph on 2026-08-31, five days after the artifact was banked. It was caught
only because a new cell happened to carry a premise arm that re-derived the
banked numbers first. That fix pinned ONE artifact by hash.

Nobody asked the obvious next question: **how many others name the same input?**
Seven artifacts in this directory load that graph, and six of them were banked
BEFORE 2026-08-31. This census re-runs all of them.

WHAT IT FINDS. Numbers move in five of six; **no composed verdict changes**; and
**one ARM reverses sign** -- `brocot_truncated_butterfly`'s "matched minus
plain-q |rho|" goes from +0.0258 (MET against a 0.02 bar) to -0.0093 (MISSED).
Its head survives because the head rests on other arms, so the cell still reads
MAP_TRACKS_THE_TRUNCATION; but the supporting claim that the matched predictor
beats plain-q does not hold on the current graph. A head-level check would have
missed that entirely, which is why this census compares every `met` flag and not
just the verdict.

`brocot_horizon_extensions` re-derives EXACTLY (0 of 57 numeric fields move),
which is worth recording as a negative: naming a moving input does not make an
artifact stale, it makes it UNCHECKED, and the two are different.

THE GENERAL RULE this makes concrete, already banked as a lesson on 09-06: a
path is not a pin. The remedy applied then was to pin one artifact's input by
sha256; the remedy this census supports is to know, for every artifact, which
input version it was banked against -- so that when an input moves, the list of
things to re-check is derivable rather than remembered.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
GRAPH = f"{BROCOT}/resources/landscape_graph_16mix.json.gz"

# Every artifact in this directory whose generator loads the 16mix graph and
# which was banked BEFORE the 2026-08-31 regeneration. filter_worth_it is
# excluded: it was already caught and re-banked with its input pinned by hash
# (brocot_filter_worth_it_regraph.json).
SUBJECTS = ["brocot_horizon_extensions", "brocot_index_routing",
            "brocot_map_dimension", "brocot_suggest_score_census",
            "brocot_truncated_butterfly", "brocot_coherence_model"]


def flat(o, p=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flat(v, p + "/" + str(k)))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flat(v, p + f"[{i}]"))
    else:
        out[p] = o
    return out


def same(x, y):
    if isinstance(x, float) and isinstance(y, float):
        if x != x and y != y:          # NaN == NaN, for this purpose
            return True
    return x == y


gsha = hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()
tmp = tempfile.mkdtemp(prefix="staleness_")
work = os.path.join(tmp, "cross_substrate")
os.makedirs(work)
for f in os.listdir(HERE):
    if f.endswith((".py", ".json")):
        shutil.copy2(os.path.join(HERE, f), work)
if os.path.isdir(os.path.join(HERE, "coordinates")):
    shutil.copytree(os.path.join(HERE, "coordinates"),
                    os.path.join(work, "coordinates"))

env = dict(os.environ, PYTHONPATH=f"{ROOT}:{BROCOT}")
rows = {}
for name in SUBJECTS:
    r = subprocess.run([sys.executable, f"{name}.py"], cwd=work, env=env,
                       capture_output=True, text=True, timeout=1800)
    banked = json.load(open(os.path.join(HERE, f"{name}.json")))
    try:
        fresh = json.load(open(os.path.join(work, f"{name}.json")))
    except Exception:
        rows[name] = dict(rerun_ok=False, exit=r.returncode,
                          note="generator did not produce an artifact")
        print(f"  {name:32s} RE-RUN FAILED (exit {r.returncode})", flush=True)
        continue
    a, b = flat(fresh), flat(banked)
    shared = set(a) & set(b)
    num = [k for k in shared
           if isinstance(b[k], (int, float)) and not isinstance(b[k], bool)]
    drift = [k for k in num if not same(a[k], b[k])]
    mets = [k for k in shared if k.endswith("/met")]
    flips = [dict(bar=k, banked=b[k], now=a[k]) for k in mets if a[k] != b[k]]
    vkeys = [k for k in banked if "verdict" in k.lower()]
    vchg = [k for k in vkeys if banked.get(k) != fresh.get(k)]
    rows[name] = dict(rerun_ok=True, n_numeric=len(num), n_drift=len(drift),
                      arm_flips=flips, verdict_changed=vchg,
                      examples=[dict(field=k, banked=b[k], now=a[k])
                                for k in drift[:3]])
    print(f"  {name:32s} drift {len(drift):>3d}/{len(num):<3d}  "
          f"arm flips {len(flips)}  verdict {'CHANGED' if vchg else 'unchanged'}",
          flush=True)
shutil.rmtree(tmp, ignore_errors=True)

stale = [n for n, r in rows.items() if r.get("n_drift")]
clean = [n for n, r in rows.items() if r.get("rerun_ok") and not r.get("n_drift")]
flipped = {n: r["arm_flips"] for n, r in rows.items() if r.get("arm_flips")}
vchanged = [n for n, r in rows.items() if r.get("verdict_changed")]

print(f"\n  graph sha256 {gsha[:16]}...")
print(f"  {len(stale)} of {len(SUBJECTS)} artifacts no longer re-derive; "
      f"{len(clean)} re-derive exactly")
print(f"  composed verdicts changed: {vchanged or 'none'}")
for n, fl in flipped.items():
    for f in fl:
        print(f"  ARM REVERSAL  {n}: {f['bar'].split('/')[-2]} "
              f"{f['banked']} -> {f['now']}")

json.dump(dict(
    status="POST-HOC, UNSEALED CENSUS — reproducible; re-runs each committed "
           "generator in a temp dir and diffs against the banked artifact",
    graph=os.path.basename(GRAPH), graph_sha256=gsha,
    graph_regenerated="2026-08-31 (brocot 3197126)",
    subjects=SUBJECTS,
    excluded=dict(brocot_filter_worth_it="already caught 2026-09-06 and re-banked "
                                         "with its input pinned by sha256 "
                                         "(brocot_filter_worth_it_regraph.json)"),
    re_banked_since=dict(brocot_truncated_butterfly="re-banked 2026-09-09 as "
                         "brocot_truncated_butterfly_regraph.json, input pinned. It "
                         "REMAINS a subject here: the census records what the move "
                         "cost, and a re-bank does not undo that record."),
    rows=rows, stale=stale, clean=clean,
    n_verdicts_changed=len(vchanged),
    arm_reversals=flipped,
    reading="Numbers move in most; NO composed verdict changes; ONE arm reverses "
            "sign (brocot_truncated_butterfly, 'matched minus plain-q |rho|', "
            "+0.0258 MET -> -0.0093 MISSED). Its head survives on other arms, so "
            "a head-level check would have missed it entirely.",
    negative_worth_keeping="brocot_horizon_extensions re-derives exactly. Naming "
                           "a moving input does not make an artifact stale, it "
                           "makes it UNCHECKED, and those are different.",
    carry_forward="a path is not a pin. Record which input VERSION each artifact "
                  "was banked against, so that when an input moves the re-check "
                  "list is derivable rather than remembered."),
    open(os.path.join(HERE, "graph_staleness_census.json"), "w"), indent=1)
print("\nwrote graph_staleness_census.json")
