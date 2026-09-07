"""Re-derive the criterion-scope claims from the committed artifacts.

Checks, in order of what they protect:
  1. v2's bars re-derive from v2's own grid/rates -- the composed head is a
     function of the artifact, not a transcription.
  2. v1's INVALID head is PRESERVED. v1 is the record of the premise arm
     catching filter_worth_it's banked rates gone stale against a regenerated
     input; a v1 that reads green would erase the catch.
  3. The regraph artifact and v2 agree at their 6 shared grid points, and the
     pinned graph hash is declared consistently in both.
  4. v2's Part-1 numbers still agree with masked_horizon's banked artifact.
ADVISORY ONLY (printed, never failed): whether the live graph in the sibling
repo still matches the pin. External state must not hold a board row red --
the pin FAILS CLOSED where it matters, at every RUN of the v2 generator.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
bad = []

v1 = json.load(open(os.path.join(HERE, "brocot_criterion_scope.json")))
v2 = json.load(open(os.path.join(HERE, "brocot_criterion_scope_v2.json")))
rg = json.load(open(os.path.join(HERE, "brocot_filter_worth_it_regraph.json")))
mh = json.load(open(os.path.join(HERE, "brocot_masked_horizon.json")))

# 1. v2 bars re-derive from v2's own data.
c1_fail = sum(1 for m in v2["margins"] for s in v2["sigmas"] if s >= 0.4
              and v2["grid"][f"I=0.9,m={m},s={s}"]["nondeg"] > 0)
edge_nz = sum(1 for m in v2["margins"]
              if v2["grid"][f"I=0.9,m={m},s=0.25"]["nondeg"] > 0)
inv = 0
for m in v2["margins"]:
    g = [v2["filter_rates"][f"m={m},s={s}"]["gain"] for s in v2["sigmas"]]
    inv += sum(1 for a, b in zip(g, g[1:]) if b < a)
g0 = [v2["filter_rates"][f"m=0.0,s={s}"]["gain"] for s in v2["sigmas"]]
cross = sum(1 for a, b in zip(g0, g0[1:])
            if (a >= v2["ship_bar"]) != (b >= v2["ship_bar"]))
derived = {
    "cells with sigma >= 0.4 where a non-degenerate ratio is audible (I=0.9)": c1_fail,
    "margin cells at sigma = 0.25 with a non-degenerate audible ratio": edge_nz,
    "adjacent gain inversions along the sigma axis, all margins": inv,
    "0.10-bar crossings along sigma at margin 0": cross,
    "0.10-bar crossings along sigma at margin 0 (uniqueness)": cross,
}
for name, want in derived.items():
    got = v2["bars"][name]["value"]
    if got != want:
        bad.append(f"v2 bar '{name}': banked {got}, re-derived {want}")
    if not v2["bars"][name]["met"]:
        bad.append(f"v2 bar '{name}' banked as MISSED; the head cannot be the "
                   "holds-head over a missed arm without saying so")
if v2["verdict"] != "CLAIMS_NOW_TRAVEL_WITH_THEIR_CRITERION_REGION":
    bad.append(f"v2 head is {v2['verdict']!r}")
if not (len(v2["crossing_intervals"]) == 1
        and tuple(v2["crossing_intervals"][0]) == (0.7, 0.5)):
    bad.append(f"crossing interval banked as {v2['crossing_intervals']}, "
               "expected the single interval (0.7, 0.5)")

# 2. v1's catch is preserved.
if v1["verdict"] != "INVALID":
    bad.append(f"v1 head is {v1['verdict']!r} -- the record of the stale-input "
               "catch has been erased or overwritten")
r2v1 = v1["bars"]["Part-2 mismatches vs 13 banked filter_worth_it numbers"]
if r2v1["met"] or r2v1["value"] != 12:
    bad.append("v1's R2 no longer records 12 mismatches MISSED")

# 3. regraph <-> v2 agreement at shared points; pin declared consistently.
for k, v in rg["sweep"].items():
    m = float(k.split(",")[0].split("=")[1])
    w = float(k.split("sigma=")[1])
    r = v2["filter_rates"][f"m={m},s={w}"]
    for fld in ("shipped", "filtered"):
        if abs(r[fld] - v[fld]) > 1e-15:
            bad.append(f"regraph vs v2 disagree at {k} {fld}")
pin = rg["provenance"]["graph_sha256"]
decl = next(p for p in v2["instrument"]["params"]
            if p["name"] == "graph_and_seed")["value"]
if pin[:16] not in decl:
    bad.append("v2's declared graph hash prefix does not match the regraph pin")

# 4. Part-1 agreement with masked_horizon.
for lab, s in (("ERB", 1.0), ("ERB/2", 0.5), ("ERB/2.5", 0.4), ("ERB/4", 0.25)):
    for I in mh["I_list"]:
        if (v2["grid"][f"I={I},m=0.0,s={s}"]["total"]
                != mh["width_sensitivity"][lab][str(I)]):
            bad.append(f"Part-1 vs masked_horizon width table at {lab}, I={I}")
for I in mh["I_list"]:
    for m in mh["margins"]:
        if (v2["grid"][f"I={I},m={m},s=1.0"]["total"]
                != mh["per_I"][str(I)]["counts"][str(m)]):
            bad.append(f"Part-1 vs masked_horizon margin table at I={I}, m={m}")

# advisory: live graph state.
gpath = os.path.expandvars(
    "$HOME/fmexplorer/brocot/resources/landscape_graph_16mix.json.gz")
if os.path.exists(gpath):
    live = hashlib.sha256(open(gpath, "rb").read()).hexdigest()
    tag = "matches pin" if live == pin else (
        "HAS MOVED AGAIN (advisory only; the v2 generator fails closed on this "
        "at run time, and a deliberate re-pin needs a new regraph artifact)")
    print(f"  live graph: {tag}")
else:
    print("  live graph: sibling repo not present (advisory only)")

if bad:
    print("VERIFY_CRITERION_SCOPE: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_CRITERION_SCOPE: PASS — v2 re-derives, v1's catch is preserved, "
      "the regraph pin is consistent, and Part 1 still matches masked_horizon")
