"""THE DISCRIMINATION REQUIREMENT for the module-scope sites — SEALED_CRITERIA §2.

COMMITTED GENERATOR of overnight_2026_08_23/mutations_module.json.

The def sites could be mutated in memory: their classifier is a function, so a
mutated source string rebuilds into a callable. Module sites are straight-line
script code, so the only way to observe a mutant is to RUN one — and the criteria
forbid editing any site file.

THE SCRATCH TREE
----------------
A directory is built where every entry of the repo is a SYMLINK to the original,
except:
  * the mutated script, which is a real file containing the perturbed source;
  * `plots/`, which is a real, empty directory — so the mutant's figure is
    written into scratch and CANNOT reach the repo's untracked 2026-05-07 PNGs.

Symlinks, not copies: signals_cache alone is 152 MB, and copying it per mutant
would make this harness cost more than the arc. The repo working tree is
verified unchanged by hash after every mutant, because a symlink farm is exactly
the kind of arrangement that is safe until one write follows a link.

WHAT A MODULE MUTANT IS COMPARED AGAINST
----------------------------------------
The banked stdout (masked identically) and the banked PNG hash. Two observables
of very different strength, and they are reported separately rather than merged:
stdout says WHAT changed; a figure hash says only THAT something did. Site
run_analytical_nns.py:297 has no stdout at all, so the figure hash is its only
witness — and a witness that cannot say what it saw is still a witness, provided
nobody writes down that it said more.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from redpath import redpath   # noqa: E402

SCRATCH_BASE = ("/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool/"
                "24c2aacc-2d7a-4059-bcf0-8164a33eb1b0/scratchpad/modmut")
PY = "/home/combust/fmexplorer/bin/python3"
BASE = json.load(open(f"{HERE}/baselines_module.json"))
MASKS = [(re.compile(r"(PLL bank: )\d+\.\d+s"), r"\1<WALLCLOCK>s")]
PNG_OF = {"run_controls.py": "08_controls.png",
          "run_per_pll_nns.py": "07_per_pll_nns.png",
          "run_analytical_nns.py": "14_analytical_vs_measured.png"}


def mask(t):
    for pat, rep in MASKS:
        t = pat.sub(rep, t)
    return t


def repo_hash():
    h = hashlib.sha256()
    for rel in ("plots", "signals_cache"):
        d = os.path.join(ROOT, rel)
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if os.path.isfile(p):
                h.update(rel.encode() + fn.encode())
                h.update(hashlib.sha256(open(p, "rb").read()).digest())
    for fn in sorted(os.listdir(ROOT)):
        if fn.endswith(".py") or fn.endswith(".npy"):
            h.update(fn.encode())
            h.update(hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).digest())
    return h.hexdigest()


# ── attacks, per measured divergence axis ───────────────────────────────────
def a_label_flip(src):
    for a, b in (("'Poiss'", "'Poisson'"), ("'Poisson'", "'Poiss'")):
        if a in src:
            return src.replace(a, b), None
    return None, "no Poisson-family label literal"


def a_argmin_swap(src):
    out = re.sub(r"\('GOE',\s*ks_o\),\s*\('GUE',\s*ks_u\)",
                 "('GOE', ks_u), ('GUE', ks_o)", src)
    if out != src:
        return out, None
    out = re.sub(r"np\.argmin\(\[ks_p,\s*ks_o,\s*ks_u\]\)",
                 "np.argmin([ks_u, ks_o, ks_p])", src)
    if out != src:
        return out, None
    return None, "decision arms are not a rewritable literal triple"


def a_guard_flip(src):
    out = re.sub(r"((?:\.size)\s*)>(\s*5\b)", r"\g<1>>\g<2>50 - 45 + ", src, count=1)
    out2 = re.sub(r"((?:\.size)\s*<\s*)5\b", r"\g<1>50", src, count=1)
    if out2 != src:
        return out2, None
    out3 = re.sub(r"((?:\.size)\s*>\s*)5\b", r"\g<1>500000", src, count=1)
    if out3 != src:
        return out3, None
    return None, "no size guard constant to flip"


def a_statistic_perturb(src):
    out = src.replace("np.arange(1, n + 1) / n", "np.arange(1, n + 1) / (n + 1e-12)")
    if out != src:
        return out, None
    return None, "site does not build the empirical CDF as arange(1, n+1)/n"


ATTACKS = {"label_flip": a_label_flip, "argmin_swap": a_argmin_swap,
           "guard_flip": a_guard_flip, "statistic_perturb": a_statistic_perturb}


def build_tree(script, mutated_src, tag):
    d = os.path.join(SCRATCH_BASE, f"{script}.{tag}")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    for name in os.listdir(ROOT):
        if name == script or name == "plots":
            continue
        os.symlink(os.path.join(ROOT, name), os.path.join(d, name))
    os.makedirs(os.path.join(d, "plots"))          # real dir: mutant figures stay here
    with open(os.path.join(d, script), "w") as fh:
        fh.write(mutated_src)
    return d


before_repo = repo_hash()
rows, tallies = {}, {}
for script, base in BASE["scripts"].items():
    src = open(os.path.join(ROOT, script), errors="replace").read()
    base_stdout, base_png = base["stdout"], base.get("png_sha", {})
    per_attack = {}
    for aname, attack in ATTACKS.items():
        mutated, why_not = attack(src)
        if mutated is None:
            per_attack[aname] = {"verdict": "INAPPLICABLE", "reason": why_not}
            continue
        d = build_tree(script, mutated, aname)
        try:
            p = subprocess.run([PY, script], cwd=d, capture_output=True,
                               text=True, timeout=1800)
        except subprocess.TimeoutExpired:
            per_attack[aname] = {"verdict": "MUTANT_TIMEOUT"}
            continue
        out = mask(p.stdout)
        png_path = os.path.join(d, "plots", PNG_OF[script])
        png = (hashlib.sha256(open(png_path, "rb").read()).hexdigest()
               if os.path.exists(png_path) else None)
        stdout_diff = out != base_stdout
        png_diff = bool(base_png) and png is not None and \
            png != list(base_png.values())[0]
        per_attack[aname] = {
            "verdict": ("DETECTED" if (stdout_diff or png_diff) else "SURVIVED"),
            "exit": p.returncode,
            "stdout_changed": stdout_diff, "figure_changed": png_diff,
            "witness": ("stdout" if stdout_diff else "figure only" if png_diff else "none")}
        shutil.rmtree(d, ignore_errors=True)

    applicable = {k: v for k, v in per_attack.items()
                  if v["verdict"] in ("DETECTED", "SURVIVED")}
    detected = {k: v for k, v in applicable.items() if v["verdict"] == "DETECTED"}
    rows[script] = dict(sites=base["sites"], attacks=per_attack,
                        n_applicable=len(applicable), n_detected=len(detected),
                        verdict=("CAPTURED" if detected else
                                 "CAPTURED_INERT" if applicable else "CAPTURED_UNATTACKED"))
    tallies[rows[script]["verdict"]] = tallies.get(rows[script]["verdict"], 0) + 1

after_repo = repo_hash()
repo_intact = before_repo == after_repo

print(f"{'script':28s} {'appl':>5s} {'det':>4s}  verdict")
for s, r in rows.items():
    print(f"  {s:26s} {r['n_applicable']:>5d} {r['n_detected']:>4d}  {r['verdict']}")
    for a, v in r["attacks"].items():
        mark = v["verdict"]
        extra = f"  witness={v['witness']}" if "witness" in v else ""
        print(f"        {a:20s} {mark}{extra}")

print(f"\nverdict tally: {tallies}")
print(f"repo working tree unchanged by every mutant: {repo_intact}")

# NON-VACUITY: an attack suite that lands nowhere proves nothing about these
# baselines. At least two attacks must have been applicable somewhere.
with redpath("module attacks applicable somewhere", expect_min=2) as rp:
    rp.observed(sum(1 for a in ATTACKS
                    if any(rows[s]["attacks"][a]["verdict"] in ("DETECTED", "SURVIVED")
                           for s in rows)))

json.dump(dict(rows=rows, verdicts=tallies, repo_intact=repo_intact),
          open(f"{HERE}/mutations_module.json", "w"), indent=1)
print("\nwritten -> overnight_2026_08_23/mutations_module.json")
if not repo_intact:
    print("A MUTANT WROTE THROUGH A SYMLINK INTO THE REPO — investigate before trusting anything")
    sys.exit(1)
