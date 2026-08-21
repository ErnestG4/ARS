"""Measured dedup of the classify() copies. COMMITTED GENERATOR.
Run AFTER Amendment 1 sealed the denominator-scaling rule; commit order is the evidence.

Extracts each site's classifier body and hashes it on NORMALISED content (comments
and blank lines stripped, whitespace collapsed) so cosmetic differences do not
inflate the distinct count, while any change to LOGIC OR CONSTANTS does.
"""
import ast, hashlib, io, json, os, re, sys, tokenize
from collections import defaultdict

ROOT = "/home/combust/fmexplorer/criticality_tool"
SITES = ["run_lmfdb_family.py", "run_controls.py", "run_fungal_nns.py",
         "run_mertens_liouville.py", "run_eeg_full.py", "run_lmfdb_postprocess.py",
         "run_dirichlet_family.py", "run_zeta_height_convergence.py", "run_phase5.py",
         "run_eeg_depth.py", "run_phase4.py", "run_analytical_nns.py",
         "run_earthquake_nns.py", "run_lmfdb_extend.py", "run_per_pll_nns.py",
         "universality.py", "run_lmfdb_edge.py", "verify/tier1_lfunction_guard.py",
         "arithmetic_toolkit.py"]


def strip_comments(src):
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.COMMENT, tokenize.NL):
                continue
            out.append(tok.string)
    except Exception:
        return src
    return " ".join(out)


def body(path):
    src = open(os.path.join(ROOT, path), errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("classify", "_classify"):
            seg = ast.get_source_segment(src, node)
            if seg:
                return seg
    return None


rows, by_hash = {}, defaultdict(list)
for p in SITES:
    b = body(p)
    if b is None:
        rows[p] = dict(found=False)
        continue
    norm = re.sub(r"\s+", " ", strip_comments(b)).strip()
    h = hashlib.sha256(norm.encode()).hexdigest()[:16]
    rows[p] = dict(found=True, hash=h, n_chars=len(norm))
    by_hash[h].append(p)

n_found = sum(1 for v in rows.values() if v.get("found"))
N = len(by_hash)
lo, hi = round(N / 3), round(N / 2)          # THE SEALED RULE, applied
out = dict(sites_checked=len(SITES), bodies_found=n_found, N_distinct=N,
           groups={h: v for h, v in by_hash.items()},
           sealed_rule="predicted_low = round(N/3), predicted_high = round(N/2)",
           predicted_range=[lo, hi])
print(f"sites inspected {len(SITES)}   classifier bodies found {n_found}")
print(f"DISTINCT implementations by normalised content hash: {N}\n")
for h, ps in sorted(by_hash.items(), key=lambda kv: -len(kv[1])):
    print(f"  {h}  x{len(ps):<3} {ps[0]}")
    for extra in ps[1:]:
        print(f"  {'':16s}      {extra}")
missing = [p for p, v in rows.items() if not v.get("found")]
if missing:
    print(f"\n  no classify()/_classify body found in: {missing}")
print(f"\nSEALED RULE APPLIED: predicted {lo}-{hi} of {N} distinct implementations")
json.dump(out, open(f"{ROOT}/gate_census/copy_dedup.json", "w"), indent=1)
