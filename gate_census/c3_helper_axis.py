"""D7 — THE CALLED-HELPER AXIS. The one the inventory structurally could not see.

COMMITTED GENERATOR of gate_census/c3_helper_axis.json. DESCRIPTIVE ONLY.

WHY IT WAS INVISIBLE
--------------------
Every axis in c3_divergence_inventory.py and c3_inline_inventory.py is INTRA-BODY:
guards, computed-unused names, returns, key sets, labels, defaults — all read off
the classifier's own source segment. A divergence in a function the classifier
CALLS leaves no trace inside that segment.

So the inventory that was built to fix a coverage gap had a second one of the
same shape, one level down. This is the blind-spot lesson recurring at the next
scale: the completion generator widened the SEARCH (which files) without widening
the DEPTH (which code counts as part of the classifier). Both times the missing
region was defined by the extractor's structural assumption, not by the domain.

WHAT IS MEASURED
----------------
For each decision site, the KS helper it actually calls:
  H1 STATISTIC       — the normalised body of the max-deviation computation
  H2 RETURN ARITY    — bare float, or (ks, p_value)
  H3 SENTINEL ARITY  — what the small-n path returns, and with how many values
  H4 SENTINEL BOUND  — the n below which the helper refuses

H4 IS THE FINDING THAT MATTERS FOR R1. The guard fork was recorded as
{50, 5, none} at the BODY. Every helper carries its own n<5 NaN sentinel
underneath it, so the real structure is two-layered: a site with a body guard of
50 still has a helper floor at 5, and a site with NO body guard inherits the
helper's floor rather than having none at all. `arithmetic_toolkit._classify`
computes KS inline with no helper, so it has no NaN path — at n=3 it returns
best='insufficient' while a helper-using site returns NaN distances and then
takes an argmin over NaNs. That is a real behavioural divergence at small n, and
it is exactly why the sealed overnight input set includes n=3.
"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from redpath import redpath   # noqa: E402

INV = json.load(open(f"{HERE}/c3_inline_divergences.json"))
HELPER_NAMES = ("ks_to", "ks_distance", "quick_ks")


def normalise(src):
    """Whitespace/comment-insensitive body signature, matching the dedup
    normalisation so the two counts are comparable."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    for n in ast.walk(tree):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) \
                and isinstance(n.value.value, str):
            n.value.value = ""
    return re.sub(r"\s+", " ", ast.unparse(tree)).strip()


def find_helper(path):
    src = open(os.path.join(ROOT, path), errors="replace").read()
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in HELPER_NAMES:
            seg = ast.get_source_segment(src, n)
            returns = [r for r in ast.walk(n) if isinstance(r, ast.Return)]
            arities, sentinel_bound, sentinel_arity = [], None, None
            for r in returns:
                if r.value is None:
                    arities.append(0)
                elif isinstance(r.value, ast.Tuple):
                    arities.append(len(r.value.elts))
                else:
                    arities.append(1)
            m = re.search(r"n\s*<\s*(\d+)", seg)
            if m:
                sentinel_bound = int(m.group(1))
                # the return inside the small-n branch
                for node in ast.walk(n):
                    if isinstance(node, ast.If):
                        cmp_src = ast.get_source_segment(src, node.test) or ""
                        if re.search(r"n\s*<\s*\d+", cmp_src):
                            rr = [x for x in ast.walk(node) if isinstance(x, ast.Return)]
                            if rr:
                                sentinel_arity = (len(rr[0].value.elts)
                                                  if isinstance(rr[0].value, ast.Tuple) else 1)
            return dict(name=n.name, lineno=n.lineno, body_hash=hash(normalise(seg)) & 0xFFFFFFFF,
                        normalised=normalise(seg),
                        return_arities=sorted(set(arities)),
                        sentinel_bound=sentinel_bound, sentinel_arity=sentinel_arity)
    return None


rows = {}
for r in INV["rows"]:
    p = r["path"]
    if p in rows:
        continue
    h = find_helper(p)
    rows[p] = dict(site=p, body_guard=r["guards"], helper=h,
                   helper_present=h is not None)

# ── axis tabulation ──────────────────────────────────────────────────────────
stat_groups, arity_groups, sentinel_groups = {}, {}, {}
for p, r in rows.items():
    h = r["helper"]
    key_stat = h["normalised"] if h else "INLINE — no helper function"
    stat_groups.setdefault(key_stat, []).append(p)
    arity_groups.setdefault(json.dumps(h["return_arities"]) if h else "INLINE", []).append(p)
    sentinel_groups.setdefault(
        json.dumps([h["sentinel_bound"], h["sentinel_arity"]]) if h else "INLINE", []).append(p)

print(f"decision-site files examined: {len(rows)}")
print(f"  with a local KS helper : {sum(1 for r in rows.values() if r['helper_present'])}")
print(f"  computing KS inline    : {sum(1 for r in rows.values() if not r['helper_present'])}")

print(f"\nH1 STATISTIC — distinct normalised bodies: {len(stat_groups)}")
for i, (k, ps) in enumerate(sorted(stat_groups.items(), key=lambda kv: -len(kv[1]))):
    print(f"  [{i}] {len(ps):2d} site(s): {', '.join(sorted(ps))[:88]}")

print(f"\nH2 RETURN ARITY — distinct contracts: {len(arity_groups)}")
for k, ps in sorted(arity_groups.items()):
    print(f"  {k:10s} {len(ps):2d} site(s): {', '.join(sorted(ps))[:80]}")

print(f"\nH3/H4 SENTINEL [bound, arity] — distinct: {len(sentinel_groups)}")
for k, ps in sorted(sentinel_groups.items()):
    print(f"  {k:12s} {len(ps):2d} site(s): {', '.join(sorted(ps))[:78]}")

print("\nTWO-LAYER GUARD STRUCTURE (body guard x helper floor):")
layer = {}
for p, r in rows.items():
    bg = r["body_guard"][0] if r["body_guard"] else None
    hf = r["helper"]["sentinel_bound"] if r["helper"] else None
    layer.setdefault((bg, hf), []).append(p)
for (bg, hf), ps in sorted(layer.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
    print(f"  body={str(bg):5s} helper={str(hf):5s}  {len(ps):2d} site(s): "
          f"{', '.join(sorted(ps))[:70]}")

# NON-VACUITY: at least two distinct return contracts are known by hand
# (run_lmfdb_family returns a bare float; run_controls returns a pair). An axis
# that collapses to one group has stopped discriminating.
with redpath("distinct KS-helper return contracts", expect_min=2) as rp:
    rp.observed(len(arity_groups))

out = dict(files=len(rows),
           n_statistic_variants=len(stat_groups),
           n_return_contracts=len(arity_groups),
           n_sentinel_variants=len(sentinel_groups),
           two_layer_guard={f"body={k[0]},helper={k[1]}": v for k, v in layer.items()},
           per_site={p: {kk: vv for kk, vv in r.items() if kk != "helper"}
                     | {"helper": ({kk: vv for kk, vv in r["helper"].items()
                                    if kk != "normalised"} if r["helper"] else None)}
                     for p, r in rows.items()})
json.dump(out, open(f"{HERE}/c3_helper_axis.json", "w"), indent=1)
print("\nwritten -> gate_census/c3_helper_axis.json")
