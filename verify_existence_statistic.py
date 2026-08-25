"""Board row for the existence-statistic guard.

WHAT TURNS THIS RED:
  (a) existence.py stops refusing a detection-shaped median, or stops requiring
      the question type — the guard itself going inert
  (b) either HISTORICAL SITE regresses to a central-tendency summary of its
      detection field. Those two are the reason the guard exists, and a fix that
      silently reverts is the failure this row is for.

WHY THE SURVEY DOES NOT FAIL THE ROW: the name heuristic is deliberately broad
(a false positive costs one argument, a false negative buries a finding), so
hard-failing on every match would make this row noisy and then ignored. The
survey REPORTS candidates for a human; the regression checks are what fail.
That split is the lesson from `verify_pending_debt`: a row that cries wolf gets
deleted, and a deleted row protects nothing.
"""
import ast
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
CHECKS = []

# The two sites whose defect motivated the guard, with the field each buried.
HISTORICAL = {
    "cross_substrate/brocot_useful_depth.py": "coin",
    "cross_substrate/brocot_theorem_scope.py": "refl_other",
}

CENTRAL = {"median", "mean", "fmean", "average", "nanmedian", "nanmean"}


def central_calls_over(path, field):
    """median/mean calls whose source text mentions `field`."""
    src = open(os.path.join(HERE, path), errors="replace").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        fn = (n.func.attr if isinstance(n.func, ast.Attribute)
              else n.func.id if isinstance(n.func, ast.Name) else None)
        if fn not in CENTRAL:
            continue
        seg = ast.get_source_segment(src, n) or ""
        if f'"{field}"' in seg or f"'{field}'" in seg:
            out.append((n.lineno, seg.replace("\n", " ")[:90]))
    return out


# (a) the guard still refuses
p = subprocess.run([PY, os.path.join(HERE, "existence.py")],
                   capture_output=True, text=True, cwd=HERE)
CHECKS.append(("existence.py still refuses a detection-shaped median",
               p.returncode == 0,
               "" if p.returncode == 0 else
               (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))

# (b) neither historical site has regressed
for path, field in HISTORICAL.items():
    hits = central_calls_over(path, field)
    CHECKS.append((f"{os.path.basename(path)} does not summarise '{field}' centrally",
                   not hits,
                   "" if not hits else f"line {hits[0][0]}: {hits[0][1]}"))

# survey, reported not enforced
sys.path.insert(0, HERE)
from existence import looks_like_a_detection            # noqa: E402

survey = []
for root, dirs, files in os.walk(HERE):
    dirs[:] = [d for d in dirs if d not in
               (".git", "__pycache__", "build", "external", "signals_cache")]
    for fn in files:
        if not fn.endswith(".py") or fn == "existence.py":
            continue
        rel = os.path.relpath(os.path.join(root, fn), HERE)
        src = open(os.path.join(root, fn), errors="replace").read()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = (n.func.attr if isinstance(n.func, ast.Attribute)
                 else n.func.id if isinstance(n.func, ast.Name) else None)
            if f not in CENTRAL:
                continue
            seg = ast.get_source_segment(src, n) or ""
            keys = {t.strip("\"'") for t in seg.split() if t.strip("\"'[](),")}
            for k in keys:
                k = k.strip("\"'[](),")
                if k and looks_like_a_detection(k) and len(k) > 2:
                    survey.append((rel, n.lineno, k, seg.replace("\n", " ")[:70]))
                    break

print("existence-statistic guard\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why and not ok else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")

print(f"\n  SURVEY (reported, not enforced): {len(survey)} central-tendency call(s) "
      f"over a detection-shaped name")
for rel, ln, k, seg in survey[:10]:
    print(f"      {rel}:{ln}  '{k}'  {seg}")
if len(survey) > 10:
    print(f"      ... and {len(survey) - 10} more")

if bad:
    print("\nVERIFY_EXISTENCE_STATISTIC: FAIL")
    sys.exit(1)
print("\nVERIFY_EXISTENCE_STATISTIC: PASS — the guard refuses, and neither "
      "historical site has regressed to a central summary of its detection field.")
