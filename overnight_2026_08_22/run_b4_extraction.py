"""B4 — extraction route for the four rows with an argmin but no classify() function.
COMMITTED GENERATOR of overnight_2026_08_22/b4_extraction.json.

Per SEALED_CRITERIA.md (82e408e): building the route is pure tooling, but the
verdicts land under the code-feature->verdict mapping whose size-guard clause is
docket item one, and that mapping is DECLARED, not SEALED (8ba9d52). EVERY row
here carries that label and inherits the existing 8's contingency if it has a
generic size guard.

ROUTE: locate the argmin over a Poisson/GOE/GUE KS triple, take its ENCLOSING
SCOPE (function if any, else the whole module), and apply the same tests the
sweep applied to a classify() body: is a fit-quality quantity computed, and is it
ever COMPARED in that scope?
"""
import ast, json, os, re, sys
R = "/home/combust/fmexplorer/criticality_tool"
SITES = ["run_controls.py", "run_analytical_nns.py", "run_per_pll_nns.py", "universality.py"]
QUAL = re.compile(r"^(pv_|pp$|po$|pu$|p_[pou]$|ks_crit|best_ks|fit_poor)")


def is_fn(scope):
    return isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef))


def enclosing(path):
    src = open(os.path.join(R, path), errors="replace").read()
    tree = ast.parse(src)
    target = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "min":
            d = ast.dump(n).lower()
            # CASE-INSENSITIVE (fixed after the first run). universality.py uses
            # lowercase labels ('poisson','goe','gue') and was silently missed,
            # landing at NEEDS_JUDGMENT for a TOOLING reason -- which is the exact
            # state B4 exists to resolve. A detector that misses a known target
            # reports a verdict it has not earned.
            if "'goe'" in d and "'gue'" in d:
                target = n; break
    if target is None:
        return None, None, None
    best_fn, best_span = None, None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if n.lineno <= target.lineno <= (n.end_lineno or n.lineno):
                span = (n.end_lineno or n.lineno) - n.lineno
                if best_span is None or span < best_span:
                    best_fn, best_span = n, span
    scope = best_fn if best_fn is not None else tree
    return scope, (best_fn.name if best_fn else "<module>"), src


rows = {}
for p in SITES:
    scope, where, src = enclosing(p)
    if scope is None:
        rows[p] = dict(verdict="NEEDS_JUDGMENT", why="argmin not located by this route")
        continue
    assigned, compared = set(), set()
    for n in ast.walk(scope):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
                if isinstance(t, ast.Tuple):
                    for e in t.elts:
                        if isinstance(e, ast.Name):
                            assigned.add(e.id)
        if isinstance(n, ast.Compare):
            for sub in ast.walk(n):
                if isinstance(sub, ast.Name):
                    compared.add(sub.id)
    qual = sorted(a for a in assigned if QUAL.match(a))
    qual_compared = sorted(set(qual) & compared)
    seg = ast.get_source_segment(src, scope) if is_fn(scope) else src
    guards = sorted(set(int(m) for m in re.findall(r"\.size\s*<\s*(\d+)", seg or "")))
    if qual and qual_compared:
        v, why = "UNMEASURED", f"fit-quality compared ({', '.join(qual_compared)}) but no error rate recorded"
    elif qual:
        v = "NEEDS_JUDGMENT"
        why = (f"fit-quality quantities COMPUTED but never COMPARED ({', '.join(qual)}) — "
               "measures-but-ignores; same shape as run_phase4, taxonomy extension deferred")
    else:
        v = "NO_NAMED_SET"
        why = ("argmin over a fixed class set with no fit-quality quantity at all"
               + (f"; generic size guard(s) {guards}" if guards else "; no size guard"))
    rows[p] = dict(verdict=v, scope=where, quality_computed=qual,
                   quality_compared=qual_compared, size_guards=guards, why=why,
                   mapping_label="DECLARED — size-guard clause pending adjudication")



# NON-VACUITY FLOOR (redpath.py discipline): the route must LOCATE every site it
# was built for. A row that reads NEEDS_JUDGMENT because the extractor missed it is
# indistinguishable, in the table, from one that genuinely resists classification.
sys.path.insert(0, R)
from redpath import redpath                                          # noqa: E402
with redpath("B4 extraction route: argmin located", expect_min=len(SITES)) as rp:
    rp.observed(sum(1 for r in rows.values() if r.get("scope") is not None))

print(f"{'site':26s} {'verdict':16s} {'scope':22s} label")
for p, r in rows.items():
    print(f"{p:26s} {r['verdict']:16s} {str(r.get('scope','-')):22s} DECLARED (clause pending)")
    print(f"{'':26s}   {r['why'][:96]}")
json.dump(dict(mapping_status="DECLARED, not SEALED (8ba9d52); size-guard clause is docket item one",
               rows=rows), open(f"{R}/overnight_2026_08_22/b4_extraction.json", "w"), indent=1)
