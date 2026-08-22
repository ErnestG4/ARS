"""C3 DIVERGENCE INVENTORY — what actually differs across the 11 classifier variants.
COMMITTED GENERATOR of gate_census/c3_divergences.json. DESCRIPTIVE ONLY; no migration.

THE DIFFERENCE RULE, committed WITH this generator and before its output, because
"every behavioural difference" is mechanical only after someone says what registers
as one — and that is where judgment hides if left implicit (the normalisation-spec
situation again). A divergence count is reproducible only against a stated rule.

REGISTERS AS A DIFFERENCE:
  D1 GUARD THRESHOLD    — numeric literal in a size/precondition comparison
                          (`pooled.size < 50` vs `< 5` vs absent)
  D2 COMPUTED-UNUSED    — a quantity assigned and/or returned but never COMPARED
  D3 CONTROL-FLOW FORK  — presence/absence of an early-return or branch
  D4 RETURNED KEY SET   — the dict keys each variant emits
  D5 LABEL VOCABULARY   — the class strings ('Poiss' vs 'Poisson')
  D6 DEFAULT PARAMETERS — default values in the signature

DOES NOT REGISTER: comments, whitespace, variable names, statement order where it
does not change control flow. (Consistent with the dedup normalisation, which also
ignores comments and whitespace — but note the dedup DOES split on variable names
while this does not, because a rename is a code difference and not a BEHAVIOURAL
one. The two counts therefore need not agree, and that is by design.)
"""
import ast, json, os, re

ROOT = "/home/combust/fmexplorer/criticality_tool"
DEDUP = json.load(open(f"{ROOT}/gate_census/copy_dedup.json"))
REPS = {h: ps[0] for h, ps in DEDUP["groups"].items()}


def analyse(path):
    src = open(os.path.join(ROOT, path), errors="replace").read()
    tree = ast.parse(src)
    fn = None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in ("classify", "_classify"):
            fn = n; break
    if fn is None:
        return None
    seg = ast.get_source_segment(src, fn)
    # D1 guard thresholds
    guards = sorted(set(int(m) for m in re.findall(r"\.size\s*<\s*(\d+)", seg)))
    # D2 computed-unused: assigned names never appearing in a Compare
    assigned, compared = set(), set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
        if isinstance(n, ast.Compare):
            for sub in ast.walk(n):
                if isinstance(sub, ast.Name):
                    compared.add(sub.id)
    quality = {a for a in assigned if re.match(r"^(pv_|ks_|best_ks|p_)", a)}
    unused = sorted(quality - compared)
    # D3 early returns
    n_returns = sum(1 for n in ast.walk(fn) if isinstance(n, ast.Return))
    # D4 returned key set
    keys = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":
            keys |= {kw.arg for kw in n.keywords if kw.arg}
    # D5 label vocabulary
    labels = sorted(set(re.findall(r"'(Poiss|Poisson|GOE|GUE)'", seg)))
    # D6 defaults
    defaults = [ast.unparse(d) for d in fn.args.defaults]
    return dict(guards=guards, computed_unused=unused, n_returns=n_returns,
                returned_keys=sorted(keys), labels=labels, defaults=defaults)


rows = {}
for h, p in REPS.items():
    a = analyse(p)
    if a:
        rows[p] = dict(impl_hash=h, sites=DEDUP["groups"][h], **a)

# tabulate divergence per axis
axes = {}
for ax in ("guards", "computed_unused", "n_returns", "returned_keys", "labels", "defaults"):
    vals = {}
    for p, r in rows.items():
        vals.setdefault(json.dumps(r[ax], sort_keys=True), []).append(p)
    axes[ax] = dict(n_distinct=len(vals), groups=vals)

out = dict(n_variants=len(rows), axes=axes, per_variant=rows)
print(f"variants analysed: {len(rows)}\n")
print(f"{'axis':18s} {'distinct':>9s}  values")
for ax, d in axes.items():
    vs = list(d["groups"])
    print(f"{ax:18s} {d['n_distinct']:>9}  " + "; ".join(v[:34] for v in vs[:3])
          + (" …" if len(vs) > 3 else ""))
div = [ax for ax, d in axes.items() if d["n_distinct"] > 1]
out["diverging_axes"] = div
print(f"\naxes on which variants DIVERGE: {div}")
print(f"axes on which all {len(rows)} agree: {[a for a in axes if a not in div]}")
json.dump(out, open(f"{ROOT}/gate_census/c3_divergences.json", "w"), indent=1)
