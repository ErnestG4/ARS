"""GATE ENUMERATION SWEEP — mechanical pass against the sealed criteria.
COMMITTED GENERATOR of gate_census/sweep_table.json.

Sealed inputs (gate_census/TRIAGE_CRITERIA_SEALED.md, committed before any output):
  Q1 named negative set?  Q2 was it measured?  Q3 what lies beyond each endpoint?
  Q4 can it say "none of these"?
  Verdicts: MEASURED_NEGATIVE_SET / UNMEASURED / NO_NAMED_SET / NEEDS_JUDGMENT / NOT_A_GATE

DISCLOSED INTERPRETATION LAYER. The seal fixed the QUESTIONS and the VOCABULARY; it
did not fix the mapping from code features to verdicts. That mapping is written
here, before the run, and stated rather than left implicit:

  * a SIZE GUARD (`n < k -> 'insufficient'`) is a PRECONDITION refusal, not a
    negative-set refusal. It says "I cannot measure", not "this is none of my
    classes". It does NOT earn MEASURED_NEGATIVE_SET.
  * a FIT-QUALITY quantity (best_ks, a p-value) that is COMPUTED AND COMPARED in a
    return/branch is a rejection region -> the site can say "none of these".
  * COMPUTED BUT NEVER COMPARED -> NEEDS_JUDGMENT (pre-committed for run_phase4;
    applied uniformly to any site with the same shape).
  * neither present -> NO_NAMED_SET (the argmin cannot be wrong in the
    "none of these" direction).
  * MEASURED_NEGATIVE_SET additionally requires evidence the complementary error
    rate was measured; a rejection region alone is necessary, not sufficient.
  * no classify/_classify body found -> NEEDS_JUDGMENT (extraction by another
    route), NOT exempt.
"""
import ast, json, os, re, sys

ROOT = "/home/combust/fmexplorer/criticality_tool"
DEDUP = json.load(open(f"{ROOT}/gate_census/copy_dedup.json"))
SITES = ["run_lmfdb_family.py", "run_controls.py", "run_fungal_nns.py",
         "run_mertens_liouville.py", "run_eeg_full.py", "run_lmfdb_postprocess.py",
         "run_dirichlet_family.py", "run_zeta_height_convergence.py", "run_phase5.py",
         "run_eeg_depth.py", "run_phase4.py", "run_analytical_nns.py",
         "run_earthquake_nns.py", "run_lmfdb_extend.py", "run_per_pll_nns.py",
         "universality.py", "run_lmfdb_edge.py", "verify/tier1_lfunction_guard.py",
         "arithmetic_toolkit.py"]
FITQ = re.compile(r"best_ks|fit_poor|fit_rejected|pvalue|p_value|\bpv_[pou]\b|ks_crit")


def body(path):
    src = open(os.path.join(ROOT, path), errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None, None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in ("classify", "_classify"):
            return ast.get_source_segment(src, n), n
    return None, None


def judge(path):
    seg, node = body(path)
    if seg is None:
        return dict(verdict="NEEDS_JUDGMENT",
                    why="no classify/_classify function found; the argmin is inline "
                        "or under another name — extraction by another route required")
    size_guard = bool(re.search(r"\.size\s*<\s*\d+", seg))
    fitq_names = sorted(set(FITQ.findall(seg)))
    # is any fit-quality quantity COMPARED (used in a Compare node), not just computed?
    compared = False
    for n in ast.walk(node):
        if isinstance(n, ast.Compare):
            src_cmp = ast.dump(n)
            if any(k in src_cmp for k in ("best_ks", "ks_crit", "pv_", "pvalue", "p_value")):
                compared = True
    has_none_branch = bool(re.search(r"'none'|\"none\"|REFUSE|UNCLASSIFIED", seg))
    if fitq_names and compared:
        v = "MEASURED_NEGATIVE_SET" if "fit_poor" in seg and "KS_NONMEMBER" in \
            open(os.path.join(ROOT, path), errors="replace").read() else "UNMEASURED"
        why = (f"rejection region present ({', '.join(fitq_names)}) and COMPARED; "
               + ("threshold calibrated against measured non-members"
                  if v == "MEASURED_NEGATIVE_SET" else
                  "but no complementary error rate is recorded at this site"))
        return dict(verdict=v, why=why, size_guard=size_guard)
    if fitq_names and not compared:
        return dict(verdict="NEEDS_JUDGMENT", size_guard=size_guard,
                    why=f"fit-quality quantities COMPUTED but never COMPARED "
                        f"({', '.join(fitq_names)}) — measures-but-ignores fits neither "
                        "MEASURED nor UNMEASURED; taxonomy extension deferred to adjudication")
    return dict(verdict="NO_NAMED_SET", size_guard=size_guard, has_none_branch=has_none_branch,
                why="argmin over a fixed class set with no fit-quality rejection; "
                    + ("a size guard exists but that is a PRECONDITION refusal "
                       "('cannot measure'), not a negative-set refusal ('none of these')"
                       if size_guard else "not even a size guard"))


hash_of = {}
for h, ps in DEDUP["groups"].items():
    for p in ps:
        hash_of[p] = h

rows = {}
for p in SITES:
    r = judge(p)
    r["impl_hash"] = hash_of.get(p)
    rows[p] = r

# collapse to DISTINCT implementations (the sealed denominator)
by_impl = {}
for p, r in rows.items():
    key = r["impl_hash"] or f"<none:{p}>"
    by_impl.setdefault(key, dict(sites=[], verdict=r["verdict"], why=r["why"]))
    by_impl[key]["sites"].append(p)

counts = {}
for k, v in by_impl.items():
    counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1

N = DEDUP["N_distinct"]
hits = counts.get("NO_NAMED_SET", 0) + counts.get("UNMEASURED", 0)
out = dict(N_distinct_sealed=N, n_impl_rows=len(by_impl), verdict_counts=counts,
           hits_NO_NAMED_SET_or_UNMEASURED=hits,
           predicted_dual=["4-5 (half-down)", "4-6 (half-up / half-to-even)"],
           by_impl=by_impl, by_site=rows)
print(f"{'verdict':24s} {'impls':>6s}")
for k, n in sorted(counts.items(), key=lambda kv: -kv[1]):
    print(f"{k:24s} {n:>6}")
print(f"\nimplementation rows: {len(by_impl)}  (sealed N_distinct = {N}, "
      f"+{len(by_impl)-N} no-body sites entering as their own rows)")
print(f"\nSCORED: NO_NAMED_SET + UNMEASURED = {hits}")
print(f"  predicted 4-5 (half-down)              -> {'MET' if 4 <= hits <= 5 else 'MISSED'}")
print(f"  predicted 4-6 (half-up / half-to-even) -> {'MET' if 4 <= hits <= 6 else 'MISSED'}")
json.dump(out, open(f"{ROOT}/gate_census/sweep_table.json", "w"), indent=1)
