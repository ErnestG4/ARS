"""C3 INVENTORY COMPLETION — the decision sites the def-based extractor cannot see.
COMMITTED GENERATOR of gate_census/c3_inline_divergences.json. DESCRIPTIVE ONLY; no migration.

WHY THIS EXISTS
---------------
c3_divergence_inventory.py finds classifiers by `ast.FunctionDef` named classify/_classify.
copy_dedup.json recorded the shortfall plainly -- "sites_checked": 19, "bodies_found": 15 --
and the inventory then analysed 11 variants without either number ever being reconciled to 19.

The four unextracted sites are not a rounding error. THREE OF THE FOUR ARE THE COMPUTED_UNUSED
SITES OF RULING 2 (run_analytical_nns, run_per_pll_nns, universality; the fourth is
run_controls). The blind spot is CORRELATED WITH THE DIVERGENCE THE INVENTORY EXISTS TO
MEASURE: sites whose classifier is not a tidy named function are the same sites that carry
extra computed quantities. So the sealed axis counts are biased LOW, not merely incomplete.

Measured consequence, before this generator runs: axis D5 reports 2 label vocabularies
('Poiss', 'Poisson'). The population has 3 -- universality.py decides over lowercase
('poisson','goe','gue'), and it is an uninventoried site.

A ruling on clause 7 taken against the def-only inventory would be a ruling on a sample
biased away from the hard cases. Hence: complete the inventory, then rule.

COUNTING RULE (R4, adjudicated 2026-08-22 — stated here so no future census re-derives it)
------------------------------------------------------------------------------------------
THE CENSUS UNIT IS THE DECISION SITE, NOT THE FILE. A file is a storage convention. One
file holding two decisions by two mechanisms is two rows, two verdicts, two migrations.
This rule accounts for part of the 11-vs-20 gap on its own. Canonical form and its
enforcement live in gate_census/c3_rulings.py (COUNTING_RULE).

SCOPE RULE, committed with the generator
----------------------------------------
A DECISION SITE is a min()/argmin() selecting among a Poisson/GOE/GUE KS triple, wherever it
occurs -- inside a def or as straight-line module code. Sites are counted PER DECISION, not
per file: run_analytical_nns.py has two, by different mechanisms (min at 184, np.argmin at
249), and they are two rows. Counting per file would hide a mechanism divergence inside a
file that already has a row.

AXIS APPLICABILITY, committed with the generator
------------------------------------------------
At module-level sites there is no enclosing function, so D4 RETURNED KEY SET and D6 DEFAULT
PARAMETERS DO NOT EXIST there. They are recorded INAPPLICABLE -- never an empty value that a
distinct-count would silently score as one more variant. (House rule, earned earlier this
arc: a dead arm is INAPPLICABLE, never 0/n.)

D2 COMPUTED-UNUSED is measured MODULE-WIDE at such sites: is the quantity ever compared
ANYWHERE in the file? That is the strictly harder test and the right one -- a script that
compares ks_p two hundred lines below its decision has still compared it. A site reported
COMPUTED_UNUSED under a module-wide search is therefore a stronger finding than one reported
under a function-scoped search, and the two are labelled so they are never pooled.
"""
import ast
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redpath import redpath  # noqa: E402

ROOT = "/home/combust/fmexplorer/criticality_tool"
DEDUP = json.load(open(f"{ROOT}/gate_census/copy_dedup.json"))
INVENTORIED = {p for ps in DEDUP["groups"].values() for p in ps}

# The 19 call sites named in CLASSIFIER_CONSOLIDATION_BRIEF.md.
SITES = """run_lmfdb_family run_controls run_fungal_nns run_mertens_liouville run_eeg_full
run_lmfdb_postprocess run_dirichlet_family run_zeta_height_convergence run_phase5
run_eeg_depth run_phase4 run_analytical_nns run_earthquake_nns run_lmfdb_extend
run_per_pll_nns universality run_lmfdb_edge verify/tier1_lfunction_guard
arithmetic_toolkit""".split()
# arithmetic_toolkit is the CANONICAL 19th site. It was omitted from the first
# sealed run of this generator: the brief lists the 18 COPIES, and I transcribed
# that list without adding the original back. copy_dedup.json checks 19. An
# inventory built to fix a coverage gap must not open a smaller one, and the
# canonical implementation is the one every migration target is measured against.

CLASS_TOKEN = re.compile(r"['\"](Poiss|Poisson|poisson|GOE|goe|GUE|gue)['\"]")
KS_TRIPLE = re.compile(r"ks_[poun]\b")
KS_HELPERS = ("ks_to", "ks_distance", "quick_ks")
CDF_TOKEN = re.compile(r"nns_cdf_(poisson|goe|gue)")
INAPPLICABLE = "INAPPLICABLE"


def decision_sites(src, tree):
    """min()/argmin() calls that select among the class triple."""
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        fname = None
        if isinstance(n.func, ast.Name):
            fname = n.func.id
        elif isinstance(n.func, ast.Attribute):
            fname = n.func.attr
        if fname not in ("min", "argmin"):
            continue
        seg = ast.get_source_segment(src, n) or ""
        labels = set(CLASS_TOKEN.findall(seg))
        # a decision needs to name the classes, or index a ks triple by argmin
        hit = (len({l.lower() for l in labels}) >= 2
               or (fname == "argmin" and len(set(KS_TRIPLE.findall(seg))) >= 2))
        # THIRD PRONG, added 2026-08-23. The first two assume the KS values
        # arrive as NAMED VARIABLES (ks_p) or that the class labels sit inside
        # the min/argmin call. run_analytical_nns.py:297 does neither: it is
        # `['Poiss','GOE','GUE'][int(np.argmin([ks_to(x, cdf_p)[0], ...]))]`,
        # where the arguments are inline CALLS and the labels live in the
        # enclosing subscript. Both prongs were blind to it, and the site was
        # found by an independent reader of a file this census had certified
        # complete -- the same structural-assumption blind spot for the third
        # time in this arc, one level further in each time.
        if not hit and fname in ("min", "argmin"):
            calls_to_ks = [c for c in ast.walk(n)
                           if isinstance(c, ast.Call)
                           and ((isinstance(c.func, ast.Name) and c.func.id in KS_HELPERS)
                                or (isinstance(c.func, ast.Attribute)
                                    and c.func.attr in KS_HELPERS))]
            cdfs = set(CDF_TOKEN.findall(seg))
            hit = len(calls_to_ks) >= 2 and len(cdfs) >= 2
        if hit:
            out.append((n, seg, sorted(labels), fname))
    return out


def enclosing_def(tree, lineno):
    encl = [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.lineno <= lineno <= (n.end_lineno or n.lineno)]
    encl.sort(key=lambda n: (n.end_lineno or n.lineno) - n.lineno)
    return encl[0] if encl else None


def labels_at(seg, src, node, tree):
    """Class vocabulary used by the decision. argmin over ks names carries its
    labels in the indexed list beside it, so widen to the statement when empty."""
    labels = sorted(set(CLASS_TOKEN.findall(seg)))
    if labels:
        return labels
    stmt = [n for n in ast.walk(tree) if isinstance(n, ast.stmt)
            and n.lineno <= node.lineno <= (n.end_lineno or n.lineno)]
    stmt.sort(key=lambda n: (n.end_lineno or n.lineno) - n.lineno)
    if stmt:
        return sorted(set(CLASS_TOKEN.findall(ast.get_source_segment(src, stmt[0]) or "")))
    return []


def computed_unused_names(scope_node):
    """D2: quality quantities ASSIGNED in this scope and never appearing in a
    Compare within it. Extracted so the certifier can exercise THIS function
    rather than a copy of it -- a verifier holding a mirrored body is the exact
    defect (verify/tier1_lfunction_guard.py) that C3 exists to reconcile.

    Consumption by min()/argmin() is deliberately NOT use: Ruling 2."""
    assigned, compared = set(), set()
    for n in ast.walk(scope_node):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
                elif isinstance(t, ast.Tuple):
                    assigned |= {e.id for e in t.elts if isinstance(e, ast.Name)}
        if isinstance(n, ast.Compare):
            for sub in ast.walk(n):
                if isinstance(sub, ast.Name):
                    compared.add(sub.id)
    quality = {a for a in assigned if re.match(r"^(pv_|ks_|best_ks|p_)", a) and a != "_"}
    return sorted(quality - compared)


def enclosing_guards(tree, lineno, src):
    """Size/length conditions on the `if` statements that enclose this decision.

    Reported as (op, constant) so `< 5` and `> 5` cannot collapse to `5`: they
    are opposite guards and an inventory that prints both as "5" has erased the
    divergence it exists to record.
    """
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.If):
            continue
        body_lines = [c for c in n.body if hasattr(c, "lineno")]
        if not body_lines:
            continue
        lo = min(c.lineno for c in body_lines)
        hi = max((c.end_lineno or c.lineno) for c in body_lines)
        if not (lo <= lineno <= hi):
            continue
        test = ast.get_source_segment(src, n.test) or ""
        m = re.search(r"(?:\.size|len\([^)]*\))\s*(<=|>=|<|>|==)\s*(\d+)", test)
        if m:
            out.append(f"{m.group(1)}{m.group(2)}")
    return sorted(set(out))


def analyse_site(path, src, tree, node, seg, labels, mech):
    fn = enclosing_def(tree, node.lineno)
    scope_node, scope = (fn, "def") if fn is not None else (tree, "module")
    scope_src = ast.get_source_segment(src, fn) if fn is not None else src

    # D1 is the guard GOVERNING THIS DECISION, read from the conditionals that
    # enclose it -- not a regex over the whole scope. At module scope the old
    # form scraped every `.size < N` in the FILE, so run_analytical_nns:184's
    # `pooled.size < 5` was attributed to :249 as well, whose actual guard is
    # `zeta_meas_pooled.size > 5` and EXCLUDES n=5. Two opposite guards were
    # recorded as the same value.
    guards = enclosing_guards(tree, node.lineno, src)

    unused = computed_unused_names(scope_node)

    if fn is not None:
        keys = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "dict":
                keys |= {kw.arg for kw in n.keywords if kw.arg}
        returned_keys = sorted(keys)
        n_returns = sum(1 for n in ast.walk(fn) if isinstance(n, ast.Return))
        defaults = [ast.unparse(d) for d in fn.args.defaults]
    else:
        # no function: these axes do not exist here. Never an empty value.
        returned_keys = n_returns = defaults = INAPPLICABLE

    return dict(path=path, line=node.lineno, mechanism=mech, scope=scope,
                enclosing=(fn.name if fn is not None else None),
                guards=guards, computed_unused=unused,
                computed_unused_search=("function-scoped" if fn is not None else "module-wide"),
                n_returns=n_returns, returned_keys=returned_keys,
                labels=labels, defaults=defaults,
                previously_inventoried=(path in INVENTORIED))


def main():
    rows = []
    for s in SITES:
        path = s + ".py"
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            continue
        src = open(full, errors="replace").read()
        tree = ast.parse(src)
        for node, seg, labels, mech in decision_sites(src, tree):
            labs = labels or labels_at(seg, src, node, tree)
            rows.append(analyse_site(path, src, tree, node, seg, labs, mech))

    newly = [r for r in rows if not r["previously_inventoried"]]

    # NON-VACUITY FLOOR: the four uninventoried files are known to hold decision sites
    # (measured by hand at adjudication: run_controls:217, run_analytical_nns:184 and
    # :249, run_per_pll_nns:138, universality:129). An extractor that reaches fewer
    # than five of them is still blind and must not be allowed to report a clean count.
    with redpath("C3 inline decision sites at previously-uninventoried files", expect_min=5) as rp:
        rp.observed(len(newly))

    by_file = {}
    for r in newly:
        by_file.setdefault(r["path"], []).append(r["line"])

    all_labels = {}
    for r in rows:
        all_labels.setdefault(json.dumps(r["labels"], sort_keys=True), []).append(
            f"{r['path']}:{r['line']}")

    print(f"decision sites found across {len(SITES)} call sites: {len(rows)}")
    print(f"  of which PREVIOUSLY UNINVENTORIED: {len(newly)} at {len(by_file)} files")
    for p, ls in sorted(by_file.items()):
        print(f"    {p}:{ls}")
    print()
    print("D5 LABEL VOCABULARY over the completed population:")
    for v, where in sorted(all_labels.items()):
        print(f"  {v:44s} {len(where):2d} site(s)  e.g. {where[0]}")
    print(f"  distinct vocabularies: {len(all_labels)}   (def-only inventory reported 2)")
    print()
    print("NEWLY VISIBLE SITES:")
    for r in newly:
        print(f"  {r['path']}:{r['line']:<4d} mech={r['mechanism']:<6s} scope={r['scope']:<6s} "
              f"guards={r['guards']} labels={r['labels']}")
        print(f"      computed_unused={r['computed_unused']} ({r['computed_unused_search']})  "
              f"returned_keys={r['returned_keys']}")

    out = dict(n_decision_sites=len(rows), n_newly_visible=len(newly),
               def_only_inventory_variants=11,
               label_vocabularies=len(all_labels), label_groups=all_labels, rows=rows)
    json.dump(out, open(f"{ROOT}/gate_census/c3_inline_divergences.json", "w"), indent=1)
    print(f"\nwritten -> gate_census/c3_inline_divergences.json")


if __name__ == "__main__":
    main()
