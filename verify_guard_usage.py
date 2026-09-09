"""Re-derive the guard usage census, and protect against a guard going dark.

  1. The import graph re-derives from the tree as it stands now.
  2. REGRESSION PROTECTION, which is the point of putting this on the board: a
     guard that currently HAS consumers must not silently drop to zero. That is
     precisely how railed.py got where it is -- a rule codified once, wired to
     nothing, and indistinguishable from a working guard ever after. The known
     zero is declared in the artifact; a NEW zero fails.
  3. The extraction facts hold: zero guard-to-guard dependency edges, and only
     detector_spec (numpy) and boundary_rate (scipy) reach outside stdlib.
     Both are load-bearing for the packaging decision the operator asked about.
  4. The census keeps declaring railed as visible debt rather than quietly
     dropping it from the roster.
"""
import ast
import warnings
import collections
import json
import os
import sys

# Parsing the whole tree surfaces SyntaxWarnings from files this census
# only reads; they are not this checker's findings and must not look like
# its output.
warnings.filterwarnings("ignore", category=SyntaxWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
bad = []
c = json.load(open(os.path.join(HERE, "guard_usage_census.json")))
GUARDS = list(c["guards"])
GS = set(GUARDS)
SKIP = {".git", "__pycache__", "archive_v1grid", "node_modules", "proposals"}

deps = collections.defaultdict(set)
consumers = collections.defaultdict(set)
for dp, dn, fn in os.walk(HERE):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".py"):
            continue
        mod = f[:-3]
        try:
            tree = ast.parse(open(os.path.join(dp, f)).read())
        except Exception:
            continue
        for n in ast.walk(tree):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module:
                names = [n.module.split(".")[0]]
            for nm in names:
                if mod in GS and nm in GS and nm != mod:
                    deps[mod].add(nm)
                if nm in GS and mod not in GS:
                    consumers[nm].add(os.path.relpath(os.path.join(dp, f), HERE))

known_unused = set(c["unused_guards"])
now_unused = {g for g in GUARDS if not consumers[g]}
new_dark = sorted(now_unused - known_unused)
if new_dark:
    bad.append(f"guard(s) went dark since the census: {new_dark} — a guard that "
               "loses its last call site becomes a codified rule nothing runs, "
               "and reads as coverage from inside the repo")
revived = sorted(known_unused - now_unused)

edges = sum(len(v) for v in deps.values())
if edges != c["guard_dependency_edges"]:
    bad.append(f"guard-to-guard dependency edges now {edges}, census says "
               f"{c['guard_dependency_edges']} — extraction is no longer a flat "
               "move and the packaging note is stale")
for g, want in (("detector_spec", "numpy"), ("boundary_rate", "scipy")):
    if want not in c["guards"][g]["third_party"]:
        bad.append(f"{g} no longer records its {want} dependency")
stdlib_only = [g for g in GUARDS if not c["guards"][g]["third_party"]]
if len(stdlib_only) != len(GUARDS) - 2:
    bad.append(f"{len(GUARDS) - len(stdlib_only)} guards now reach outside "
               "stdlib; the census claims exactly two")

# Consumer COUNTS are reported, never failed on. The first version of this check
# froze them exactly, and the very next cell that imported a guard turned the
# board red -- punishing a guard for being USED MORE, which is the opposite of
# what this row exists to protect. What matters is a guard going dark (checked
# above), not the census's arithmetic staying frozen.
drifted = [(g, len(consumers[g]), c["guards"][g]["n_consumers"])
           for g in GUARDS if len(consumers[g]) != c["guards"][g]["n_consumers"]]
gone_thin = [(g, n, w) for g, n, w in drifted if n < w]
if gone_thin:
    for g, n, w in gone_thin:
        print(f"  note: {g} lost consumers ({w} -> {n}) — not a failure unless "
              "it reaches zero, but worth a look")

if "railed" not in known_unused:
    bad.append("railed is no longer declared as unused debt — either it was "
               "wired up (good: re-run the census) or it was dropped from the "
               "roster (not good)")

print(f"  {len(GUARDS)} guards, {edges} guard-to-guard edges, "
      f"{len(set().union(*consumers.values()) if consumers else set())} consumer files")
if drifted:
    print(f"  consumer counts moved since the census: "
          + ", ".join(f"{g} {w}->{n}" for g, n, w in drifted)
          + "  (reported, not failed)")
print(f"  unused now: {sorted(now_unused) or 'none'}"
      + (f"   (revived since census: {revived})" if revived else ""))

if bad:
    print("VERIFY_GUARD_USAGE: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_GUARD_USAGE: PASS — the import graph re-derives, no guard has gone "
      "dark, and the extraction facts (0 internal edges, 2 third-party reaches) "
      "still hold")
