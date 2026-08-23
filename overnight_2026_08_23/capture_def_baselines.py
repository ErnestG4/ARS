"""R3 BASELINE CAPTURE — the def-scope decision sites.

COMMITTED GENERATOR of overnight_2026_08_23/baselines_def.json.
Captures only; migrates nothing. Reads the repo, writes one file in this directory.

EACH SITE GETS ITS OWN DEPENDENCY CLOSURE
-----------------------------------------
The obvious harness injects one canonical `ks_to` into every site. That is SILENT
at run_phase4, whose helper returns `(ks, n)` while the others return `(ks, p)`:
the second element is discarded at the call site, today's values agree, and the
baseline would certify a function wired to a helper the site does not use. The
consolidation is going to touch exactly these helpers, so a baseline that never
ran the site's own helper protects nothing about it.

So: from each site's classifier we take the transitive closure of names it
references within its own module — helpers, constants, nested functions — and
exec only that. The single genuinely shared dependency, `nns_cdf_*`, is imported
from `universality`, which is where all 21 sites import it from. `numpy` is
injected. Nothing else crosses the boundary.

Executing the whole module instead is not an option: most of these files are
scripts, and importing them runs them.

SERIALISATION IS FULL-PRECISION, NOT repr()
-------------------------------------------
`repr()` is shortest-exact for a Python float and would be sound for the 15
dict-returning sites. It is NOT sound for universality.py:129, which returns a
dataclass holding an ndarray: numpy summarises above ~1000 elements and truncates
to 8 significant digits below, so a low-order-bit change passes unseen. One
serialiser is used everywhere — `float.hex()` for scalars, a sha256 of
`tobytes()` for arrays — because a per-site serialiser is one more place for a
divergence to hide, and because NaN must survive the round trip verbatim.

INPUT ADAPTERS ARE DECLARED, NEVER IMPLICIT
-------------------------------------------
`universality.compute_nns` takes EVENTS and differences them internally; every
other site takes SPACINGS. Feeding it the shared spacings vector raises nothing —
it computes spacings-of-spacings and the baseline certifies a computation no
caller performs, forever green. The adapter is declared in ADAPTERS below with
its reason, so the harness cannot silently apply one.
"""
import ast
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from universality import nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue   # noqa: E402
from redpath import redpath                                          # noqa: E402

INV = json.load(open(f"{ROOT}/gate_census/c3_inline_divergences.json"))
INPUTS = json.load(open(f"{HERE}/inputs.json"))

# ── declared input adapters ─────────────────────────────────────────────────
ADAPTERS = {
    "universality.py:129": (
        "events",
        "compute_nns takes EVENT POSITIONS and differences them internally, "
        "while every other site takes SPACINGS. Passing spacings would have it "
        "compute spacings-of-spacings — no error, no signal, a baseline "
        "certifying a computation no caller performs. cumsum recovers events "
        "whose diff is the sealed spacings vector."),
}


def adapt(site_key, vec):
    kind = ADAPTERS.get(site_key, ("spacings", ""))[0]
    a = np.asarray(vec, dtype=np.float64)
    return np.cumsum(a) if kind == "events" else a


# ── full-precision serialisation ────────────────────────────────────────────
def ser(obj):
    if isinstance(obj, float):
        return {"__f": float.hex(obj)}          # exact, and NaN survives
    if isinstance(obj, (np.floating,)):
        return {"__f": float.hex(float(obj))}
    if isinstance(obj, (bool, int, str, type(None))):
        return obj
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return {"__a": hashlib.sha256(np.ascontiguousarray(obj).tobytes()).hexdigest(),
                "shape": list(obj.shape), "dtype": str(obj.dtype)}
    if isinstance(obj, dict):
        return {k: ser(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [ser(v) for v in obj]
    if hasattr(obj, "__dataclass_fields__"):
        return {"__dataclass": type(obj).__name__,
                **{f: ser(getattr(obj, f)) for f in sorted(obj.__dataclass_fields__)}}
    return {"__repr": repr(obj)}


# ── per-site dependency closure ─────────────────────────────────────────────
def closure_source(path, fn_name):
    src = open(os.path.join(ROOT, path), errors="replace").read()
    tree = ast.parse(src)
    funcs = {n.name: n for n in tree.body
             if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    consts = {}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = n
    # NAMES THE SITE IMPORTS. The first version of this closure followed only
    # same-module definitions, so `_ks_pvalue` -- imported from universality by
    # run_phase4 and run_lmfdb_edge -- was missing, and those two sites "raised"
    # on 40 of 55 inputs. That looked exactly like a finding: it failed only at
    # large n, because the helper returns its NaN sentinel before reaching
    # _ks_pvalue at small n. A harness coverage gap that fails in a
    # behaviourally plausible pattern is worse than one that fails everywhere.
    imported = {}
    for n in tree.body:
        if isinstance(n, ast.ImportFrom) and n.module:
            for a in n.names:
                imported[a.asname or a.name] = (n.module, a.name)

    want, seen, pieces, needed_imports = [fn_name], set(), [], {}
    while want:
        name = want.pop()
        if name in seen:
            continue
        seen.add(name)
        node = funcs.get(name)
        if node is None:
            if name in imported:
                needed_imports[name] = imported[name]
            continue
        seg = ast.get_source_segment(src, node)
        if getattr(node, "decorator_list", None):
            # ast.get_source_segment starts at `class`/`def`, dropping decorators,
            # so NNSResult arrived UNDECORATED and raised "takes no arguments" on
            # every one of 55 inputs -- which is why its baseline was inert: 55
            # identical exceptions cannot be perturbed.
            lines = src.splitlines()
            first = min(d.lineno for d in node.decorator_list)
            seg = "\n".join(lines[first - 1:node.end_lineno])
        pieces.append(seg)
        # names BOUND INSIDE this function shadow anything at module level. The
        # first version ignored that and pulled a module-level `ks_p = [...]`
        # into the closure merely because classify has a local named ks_p --
        # dragging in a comprehension over `valid`, a module variable that does
        # not exist at closure time. A name is not an identity.
        local = set()
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                local.add(sub.id)
            elif isinstance(sub, ast.arg):
                local.add(sub.arg)
            elif isinstance(sub, (ast.comprehension,)):
                for t in ast.walk(sub.target):
                    if isinstance(t, ast.Name):
                        local.add(t.id)
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                if sub.id in local:
                    continue
                if sub.id in funcs and sub.id not in seen:
                    want.append(sub.id)
                elif sub.id in imported:
                    # BUG FOUND BY THE MUTATION TEST: names reached the
                    # needed_imports map only by being POPPED from `want`, and
                    # nothing ever pushed an imported name onto it. So the
                    # import-following added earlier never ran, and
                    # run_lmfdb_edge / run_phase4 still failed on _ks_pvalue --
                    # the fix was present, unreachable, and reported as applied.
                    needed_imports[sub.id] = imported[sub.id]
                elif sub.id in consts:
                    pieces.append(ast.get_source_segment(src, consts[sub.id]))
    return "\n\n".join(reversed(pieces)), sorted(seen), needed_imports


def build_from_source(code, needed, fn_name, path="<mutated>"):
    ns = {"np": np, "numpy": np,
          "nns_cdf_poisson": nns_cdf_poisson, "nns_cdf_goe": nns_cdf_goe,
          "nns_cdf_gue": nns_cdf_gue, "math": __import__("math"),
          "dataclass": __import__("dataclasses").dataclass,
          "field": __import__("dataclasses").field}
    injected = {}
    for local, (mod, orig) in needed.items():
        try:
            m = __import__(mod, fromlist=[orig])
            ns[local] = getattr(m, orig)
            injected[local] = f"{mod}.{orig}"
        except Exception as exc:                              # noqa: BLE001
            injected[local] = f"UNRESOLVED ({type(exc).__name__})"
    exec(compile(code, f"<closure:{path}>", "exec"), ns)     # noqa: S102
    return ns[fn_name], injected


def build(path, fn_name):
    code, pulled, needed = closure_source(path, fn_name)
    fn, injected = build_from_source(code, needed, fn_name, path)
    return fn, pulled, injected


def main():
    # ── capture ─────────────────────────────────────────────────────────────────
    def_rows = [r for r in INV["rows"] if r["scope"] == "def"]
    vectors = INPUTS["vectors"]

    baselines, failures = {}, {}
    for r in def_rows:
        key = f"{r['path']}:{r['line']}"
        fn_name = r["enclosing"]
        try:
            fn, pulled, injected = build(r["path"], fn_name)
        except Exception as exc:                                  # noqa: BLE001
            failures[key] = f"closure build failed: {type(exc).__name__}: {exc}"
            continue

        per_input = {}
        for vname in sorted(vectors):
            try:
                out = fn(adapt(key, vectors[vname]))
                per_input[vname] = {"ok": True, "value": ser(out)}
            except Exception as exc:                              # noqa: BLE001
                per_input[vname] = {"ok": False,
                                    "raised": f"{type(exc).__name__}: {exc}"}
        baselines[key] = dict(path=r["path"], line=r["line"], callable=fn_name,
                              closure_pulled=pulled, closure_injected=injected,
                              guards=r["guards"], labels=r["labels"],
                              adapter=ADAPTERS.get(key, ("spacings", ""))[0],
                              results=per_input)

    # ── did the ruler discriminate? (SEALED_CRITERIA §3) ────────────────────────
    best_by_input = {}
    for key, b in baselines.items():
        for vname, res in b["results"].items():
            if not res["ok"]:
                continue
            v = res["value"]
            # LABEL KEY IS PER-SITE, DECLARED. universality.py:129 returns a
            # dataclass whose field is `best_fit`, not `best`, so a lookup for
            # "best" alone silently dropped it -- making the headline
            # disagreement rate a statistic over 15 of 16 sites under an unnamed
            # stratum, which SEALED_CRITERIA §1 forbids by name.
            label = None
            if isinstance(v, dict):
                for cand in ("best", "best_fit"):
                    if isinstance(v.get(cand), str):
                        label = v[cand]
                        break
            if isinstance(label, str):
                best_by_input.setdefault(vname, {}).setdefault(label, []).append(key)

    disagreeing = {v: g for v, g in best_by_input.items() if len(g) > 1}

    # TWO RATES, because one of them is saturated for a trivial reason. Including
    # universality.py:129 lifts raw disagreement to 55/55 -- but only because its
    # vocabulary is lowercase, so 'gue' differs from 'GUE' on every input where both
    # answer. That is the D5 label divergence, not a classification difference, and
    # quoting the saturated number alone would overstate what the ruler resolves.
    # The canonical rate routes every label through R2's committed translation table
    # (its second consumer) and measures disagreement about the CLASS.
    sys.path.insert(0, os.path.join(ROOT, "gate_census"))
    from c3_rulings import to_canonical, RulingViolation           # noqa: E402

    canon_by_input = {}
    for vname, groups in best_by_input.items():
        for lab, keys in groups.items():
            try:
                c = to_canonical(lab)
            except RulingViolation:
                c = lab                     # sentinels like 'insufficient' are not classes
            canon_by_input.setdefault(vname, {}).setdefault(c, []).extend(keys)
    disagreeing_canonical = {v: g for v, g in canon_by_input.items() if len(g) > 1}

    # A build that succeeds while every CALL raises is not a captured baseline.
    # The first version of this report counted builds and printed "16 of 16,
    # zero failures" while three sites were capturing nothing but exceptions --
    # liveness read off the wrong line.
    fully = sum(1 for b in baselines.values()
                if all(r["ok"] for r in b["results"].values()))
    partly = sum(1 for b in baselines.values()
                 if any(r["ok"] for r in b["results"].values())
                 and not all(r["ok"] for r in b["results"].values()))
    never = sum(1 for b in baselines.values()
                if not any(r["ok"] for r in b["results"].values()))
    print(f"def-scope decision sites: {len(def_rows)}")
    print(f"  closure built        : {len(baselines)}   (build failures: {len(failures)})")
    print(f"  returns on ALL inputs: {fully}")
    print(f"  returns on SOME      : {partly}")
    print(f"  raises on EVERY input: {never}   <- not a captured baseline")
    for k, why in failures.items():
        print(f"      {k}  {why}")

    sites_with_label = {k for g in best_by_input.values() for ks in g.values() for k in ks}
    print(f"\nsites contributing a class label: {len(sites_with_label)} of {len(baselines)}")
    print(f"input vectors: {len(vectors)}")
    print(f"inputs on which sites DISAGREE, raw label     : "
          f"{len(disagreeing)} of {len(best_by_input)}")
    print(f"inputs on which sites DISAGREE, canonical class: "
          f"{len(disagreeing_canonical)} of {len(canon_by_input)}   <- the informative one")
    for vname in sorted(disagreeing)[:8]:
        groups = disagreeing[vname]
        print(f"  {vname:24s} " + "  ".join(f"{lab}×{len(ks)}" for lab, ks in sorted(groups.items())))

    # raised-vs-returned divergence is itself a behaviour to bank
    raise_counts = {}
    for key, b in baselines.items():
        n_raise = sum(1 for res in b["results"].values() if not res["ok"])
        raise_counts[key] = n_raise
    print("\nsites by number of inputs that RAISED (small-n paths are where they differ):")
    for k in sorted(raise_counts, key=lambda k: -raise_counts[k]):
        if raise_counts[k]:
            print(f"  {k:36s} {raise_counts[k]:>3d}/{len(vectors)}")

    # NON-VACUITY: the sealed criteria pre-registered that the input set must make
    # at least one site disagree with another. Zero disagreement is a FAILURE OF THE
    # RULER, and it must not be reportable as "the variants agree".
    with redpath("inputs on which def sites disagree on `best`", expect_min=1) as rp:
        rp.observed(len(disagreeing))

    payload = json.dumps(dict(
        inputs_sha=hashlib.sha256(open(f"{HERE}/inputs.json", "rb").read()).hexdigest(),
        numpy_version=np.__version__,
        python_version=sys.version.split()[0],
        n_sites=len(baselines), failures=failures,
        disagreeing_inputs=sorted(disagreeing),
    disagreeing_inputs_canonical=sorted(disagreeing_canonical),
    sites_contributing_a_label=len(sites_with_label),
        baselines=baselines), indent=1, sort_keys=True)
    open(f"{HERE}/baselines_def.json", "w").write(payload)
    print(f"\nwritten -> overnight_2026_08_23/baselines_def.json "
          f"(sha {hashlib.sha256(payload.encode()).hexdigest()[:16]}…)")


if __name__ == "__main__":
    main()
