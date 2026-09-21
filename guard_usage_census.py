#!/usr/bin/env python3
"""CENSUS: what imports each guard module, and what would have to move to extract them.

Two questions in one pass, because they read the same import graph.

QUESTION 1 — EXTRACTION FEASIBILITY (the operator asked 2026-09-07 for "whatever
is best practice", flagged not urgent). To package the guards, one needs to know
what they depend on and who depends on them.

QUESTION 2 — DEAD GUARDS, which the same graph answers for free. A guard module
with no importers is a codified rule with no call sites. From inside the repo it
is indistinguishable from a working guard: it has a docstring, a literature
anchor, and a place in `verify_literature_anchors`'s roster. It simply never
runs. That is this repo's oldest recurring meta-finding -- the discipline gets
applied where it LOOKS like it belongs rather than where it decides things -- and
the census is the cheapest instrument that can see it.

WHAT IT FINDS

  * ZERO guard-to-guard dependencies. All eleven are standalone, so extraction is
    a flat move with no internal import graph to preserve.
  * Only two reach outside the standard library: detector_spec (numpy) and
    boundary_rate (scipy). The other nine are stdlib-only.
  * 83 distinct files import at least one guard; redpath leads at 70.
  * `railed.py` HAD NO IMPORTERS AT ALL when this census was first run. It was
    mentioned once in a docstring (`cross_substrate/brocot_map_dimension.py`) and
    otherwise reached only by `verify_literature_anchors`, which imports it to
    read its LITERATURE dict -- that is, the only thing that loaded it was the
    checker asking where its rule came from, never anything that used the rule.
    **WIRED UP 2026-09-09**: `bridge/dpp_boundary.py` and its audit are its first
    call sites, on the bridge's railed Thomas fits -- the case it was written for,
    two directories away, unread since August. All eleven guards now have call
    sites, and the check that used to assert railed's absence is retired in
    favour of the general form (the census's unused list must match the tree).

WHY THAT LAST ONE IS NOT A TIDINESS ISSUE. railed.py exports `Bounded` (refuses
to hand back a railed value silently) and `brody_q`. The Brody work in this repo
runs through a DIFFERENT implementation, `cross_substrate/axes.py:I8_brody_q`,
whose two-ended rail defect is documented in `class_collapse_sweep.py` (R-140 /
R-144) and repaired in the c2_acceptance arc by adding an unbounded variant. So
the rail problem was found, understood and fixed ad hoc, a module was written to
encode the general rule -- and the module was never wired to anything.

AND THERE IS A LIVE INSTANCE, found the same night in a different arc. The bridge
arc's `fit_thomas` rails at its upper bound on 2 of 2 fits (kappa = 99.99999 of
100.0) with no boundary check at all; the only record that a rail occurred is a
sentence in RESULTS_BRIDGE.md. A guard for exactly that sits unused two
directories away. Filed at `bridge/proposals/PROPOSED_boundary_reporting.md`.

STATUS: census, unsealed. It measures the repo rather than the world, and makes
no prediction.
"""
import ast
import warnings
import collections
import json
import os

# Parsing the whole tree surfaces SyntaxWarnings from files this census
# only reads; they are not this checker's findings and must not look like
# its output.
warnings.filterwarnings("ignore", category=SyntaxWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
GUARDS = ["aggregate", "reachable", "verdictlattice", "modelparams",
          "detector_spec", "redpath", "threadledger", "existence",
          "railed", "countrecon", "boundary_rate"]
GS = set(GUARDS)
STDLIB = {"os", "sys", "json", "math", "re", "subprocess", "collections",
          "itertools", "fractions", "hashlib", "time", "datetime", "functools",
          "statistics", "gzip", "csv", "random", "argparse", "textwrap",
          "pathlib", "typing", "multiprocessing", "importlib", "ast", "glob",
          "shutil", "tempfile", "warnings", "copy", "bisect", "heapq"}
SKIP_DIRS = {".git", "__pycache__", "archive_v1grid", "node_modules", "proposals", ".claude"}   # .claude = nested worktrees


def scan():
    deps = collections.defaultdict(set)
    third = collections.defaultdict(set)
    consumers = collections.defaultdict(set)
    for dp, dn, fn in os.walk(HERE):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(".py"):
                continue
            path = os.path.join(dp, f)
            mod = f[:-3]
            try:
                tree = ast.parse(open(path).read())
            except Exception:
                continue
            for n in ast.walk(tree):
                names = []
                if isinstance(n, ast.Import):
                    names = [a.name.split(".")[0] for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    names = [n.module.split(".")[0]]
                for nm in names:
                    if mod in GS:
                        if nm in GS and nm != mod:
                            deps[mod].add(nm)
                        elif nm not in STDLIB and nm not in GS:
                            third[mod].add(nm)
                    if nm in GS and mod not in GS:
                        consumers[nm].add(os.path.relpath(path, HERE))
    return deps, third, consumers


deps, third, consumers = scan()
rows = {}
for g in GUARDS:
    cs = sorted(consumers[g])
    rows[g] = dict(guard_deps=sorted(deps[g]), third_party=sorted(third[g]),
                   n_consumers=len(cs), consumers=cs[:12])
unused = [g for g in GUARDS if rows[g]["n_consumers"] == 0]
all_consumers = set().union(*[consumers[g] for g in GUARDS]) if GUARDS else set()
n_dep_edges = sum(len(v) for v in deps.values())

print("guard module census\n")
print(f"{'guard':16s} {'deps':6s} {'third-party':14s} {'consumers':>9s}")
for g in GUARDS:
    r = rows[g]
    print(f"{g:16s} {str(len(r['guard_deps'])):6s} "
          f"{(','.join(r['third_party']) or 'stdlib'):14s} {r['n_consumers']:>9d}")
print(f"\n  guard-to-guard dependency edges: {n_dep_edges}  "
      f"(0 means extraction is a flat move)")
print(f"  distinct consumer files: {len(all_consumers)}")
if unused:
    print(f"\n  UNUSED GUARDS (visible debt, does not fail this census): "
          f"{', '.join(unused)}")
    print("  A guard with no importers is a codified rule with no call sites. It")
    print("  is indistinguishable from a working guard from inside the repo.")

json.dump(dict(
    status="CENSUS, unsealed — measures the repo, makes no prediction",
    guards=rows, unused_guards=unused,
    guard_dependency_edges=n_dep_edges,
    n_distinct_consumers=len(all_consumers),
    extraction_note="zero guard-to-guard dependencies and only two third-party "
                    "reaches (detector_spec:numpy, boundary_rate:scipy), so the "
                    "eleven modules can be packaged flat; the cost is in the "
                    f"{len(all_consumers)} consumer files' import lines, not in "
                    "the guards themselves",
    live_instance="bridge/dpp_python.py:fit_thomas rails at its upper bound on "
                  "2 of 2 fits with no boundary check; the only record is prose "
                  "in RESULTS_BRIDGE.md, while railed.py sits unused. Filed at "
                  "bridge/proposals/PROPOSED_boundary_reporting.md",
    railed_detail="railed.py exports Bounded and brody_q; the repo's Brody work "
                  "runs through cross_substrate/axes.py:I8_brody_q instead, "
                  "whose two-ended rail defect is documented in "
                  "class_collapse_sweep.py (R-140/R-144) and repaired ad hoc in "
                  "the c2_acceptance arc. The rule was codified and never wired."),
    open(os.path.join(HERE, "guard_usage_census.json"), "w"), indent=1)
print("\nwrote guard_usage_census.json")
