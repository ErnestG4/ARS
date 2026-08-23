"""R3 BASELINE CAPTURE — the module-scope decision sites (straight-line script code).

COMMITTED GENERATOR of overnight_2026_08_23/baselines_module.json.

Five decision sites live in three scripts as straight-line code:
    run_controls.py:217
    run_analytical_nns.py:184, :249, :297
    run_per_pll_nns.py:138
Their observable is what the code EMITS, so capture means running them.

WHAT THIS HARNESS REFUSES TO DO QUIETLY
---------------------------------------
1. ARCHIVE BEFORE RUN. Each script overwrites one PNG in plots/, and those PNGs
   are NOT tracked by git — dated 2026-05-07, unrecoverable if lost. They are
   hashed and copied aside first, restored after, and the restore is VERIFIED by
   hash. `--limit 3` truncated 1159 records to 3 because nobody archived first.
2. WIDER SNAPSHOT THAN THE KNOWN WRITES. plots/, signals_cache/ and the root
   .npy files are all hashed before and after. The write inventory says only the
   PNG changes; the snapshot is what makes that a MEASUREMENT rather than a
   reading of the source.
3. EXIT STATUS IS PART OF THE OBSERVABLE. run_analytical_nns imports cupy at
   line 204, AFTER site :184 has printed. On a broken box it emits the :184
   table and dies — and banking that stdout captures a baseline in which :249
   and :297 DO NOT EXIST, which a post-migration run that also dies would
   "match". Capture requires exit 0 AND a sentinel line for every site.
4. DETERMINISM IS MEASURED, NOT ASSUMED. Each script runs TWICE. Differing runs
   are INFEASIBLE_NONDETERMINISM, and the differing lines are recorded so the
   verdict names its cause.
5. MASKING IS LITERAL AND MINIMAL. run_analytical_nns prints a wall-clock
   duration; exactly that line pattern is masked, nothing broader. Every
   normalisation is a place a real diff can hide, so each one is declared here.

WHAT THESE BASELINES CANNOT CERTIFY — stated with the artifact, not discovered later
------------------------------------------------------------------------------------
* run_analytical_nns's p_o/p_p/p_u are computed and NEVER emitted. A migration
  that drops or corrupts them yields a byte-identical baseline. These are exactly
  the quantities R5 promotes: the baseline is structurally blind to the thing this
  stratum was flagged for. Recorded per-site as OBSERVABLE_ABSENT.
* The guardless paths at run_controls:217 and run_per_pll_nns:138 are unreachable:
  pooled sizes come from banked signals of fixed size, so the no-guard branch never
  executes. Migrating them onto a guarded classifier is a policy change these
  baselines would certify as "no change".
* One trajectory. Each script's multi-branch verdicts take one branch per run.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from redpath import redpath   # noqa: E402

SCRATCH = os.environ.get("C3_SCRATCH", "/tmp/claude-1000/-home-combust-fmexplorer-"
                         "criticality-tool/24c2aacc-2d7a-4059-bcf0-8164a33eb1b0/"
                         "scratchpad/plots_archive")
PY = "/home/combust/fmexplorer/bin/python3"
TIMEOUT = 3600

SCRIPTS = {
    "run_controls.py": {"sites": [217], "sentinels": ["Task 1", "KS"]},
    "run_per_pll_nns.py": {"sites": [138], "sentinels": ["PLL"]},
    "run_analytical_nns.py": {"sites": [184, 249, 297],
                              "sentinels": ["Two-sample KS", "ζ measured"]},
}

# declared, literal, minimal
MASKS = [(re.compile(r"(PLL bank: )\d+\.\d+s"), r"\1<WALLCLOCK>s")]

PNG_OF = {"run_controls.py": ("08_controls.png",),
          "run_per_pll_nns.py": ("07_per_pll_nns.png",),
          "run_analytical_nns.py": ("14_analytical_vs_measured.png",)}

OBSERVABLE_ABSENT = {
    "run_analytical_nns.py:184": "p_o/p_p/p_u are computed at :180-182 and never "
                                 "printed, plotted, or written — no observable exists "
                                 "for the quantities R5 promotes at this site",
}

# Sites whose only observable is the figure. Captured as a PNG hash, which is
# weaker than stdout: it detects that something changed, never what.
OBSERVABLE_IS_FIGURE_ONLY = {
    "run_analytical_nns.py:297": "its `best` reaches ax.set_title and nothing else "
                                 "(run_analytical_nns.py:315) — the 21st decision "
                                 "site emits no stdout at all",
}


def snapshot():
    out = {}
    for rel in ("plots", "signals_cache"):
        d = os.path.join(ROOT, rel)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if os.path.isfile(p):
                out[f"{rel}/{fn}"] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    for fn in sorted(os.listdir(ROOT)):
        if fn.endswith(".npy"):
            out[fn] = hashlib.sha256(open(os.path.join(ROOT, fn), "rb").read()).hexdigest()
    return out


def mask(text):
    for pat, rep in MASKS:
        text = pat.sub(rep, text)
    return text


os.makedirs(SCRATCH, exist_ok=True)
before = snapshot()
archived = []
for rel, _h in before.items():
    if rel.startswith("plots/"):
        shutil.copy2(os.path.join(ROOT, rel), os.path.join(SCRATCH, os.path.basename(rel)))
        archived.append(rel)
print(f"archived {len(archived)} plot file(s) to scratch before any run")

# NON-VACUITY: the three PNGs these scripts overwrite are known to exist. An
# archive step that copies nothing has protected nothing.
with redpath("plot files archived before running", expect_min=3) as rp:
    rp.observed(len(archived))

results = {}
for script, meta in SCRIPTS.items():
    runs = []
    for attempt in (1, 2):
        t0 = time.time()
        p = subprocess.run([PY, script], cwd=ROOT, capture_output=True,
                           text=True, timeout=TIMEOUT)
        runs.append(dict(exit=p.returncode, stdout=mask(p.stdout),
                         stderr_tail=p.stderr.strip().splitlines()[-3:],
                         seconds=round(time.time() - t0, 1)))
        # THE PNG IS AN OBSERVABLE, and the archive-and-restore would discard
        # it. run_analytical_nns.py:297's `best` reaches only ax.set_title --
        # never stdout -- so without this the 21st decision site has NO captured
        # observable at all while its file reports CAPTURED.
        pngs = {}
        for fn in sorted(os.listdir(os.path.join(ROOT, "plots"))):
            fp = os.path.join(ROOT, "plots", fn)
            if os.path.isfile(fp) and fn in PNG_OF.get(script, ()):
                pngs[fn] = hashlib.sha256(open(fp, "rb").read()).hexdigest()
        runs[-1]["png_sha"] = pngs
        print(f"  {script} run {attempt}: exit={p.returncode} "
              f"{runs[-1]['seconds']}s  stdout {len(runs[-1]['stdout'])} bytes  "
              f"png {list(pngs.values())[0][:12] if pngs else '—'}")

    deterministic = runs[0]["stdout"] == runs[1]["stdout"]
    png_deterministic = runs[0].get("png_sha") == runs[1].get("png_sha")
    diff_lines = []
    if not deterministic:
        a, b = runs[0]["stdout"].splitlines(), runs[1]["stdout"].splitlines()
        diff_lines = [f"{i}: {x!r} vs {y!r}"
                      for i, (x, y) in enumerate(zip(a, b)) if x != y][:6]

    # CASE-INSENSITIVE. The first run scored run_controls
    # INFEASIBLE_TRUNCATED_RUN because the sentinel read "Task 1" and the script
    # prints "TASK 1" -- a verdict about the SUBJECT assigned for a defect in the
    # HARNESS, on a run that exited 0 and was byte-identical across two attempts.
    # This repo already has that exact failure on record: the B4 extraction's
    # uppercase-only matcher silently missed universality.py and emitted
    # NEEDS_JUDGMENT for a tooling reason. Same defect, mirrored.
    low = runs[0]["stdout"].lower()
    missing = [s for s in meta["sentinels"] if s.lower() not in low]

    if runs[0]["exit"] != 0:
        verdict = "INFEASIBLE_NONZERO_EXIT"
    elif missing:
        verdict = "INFEASIBLE_TRUNCATED_RUN"
    elif not deterministic:
        verdict = "INFEASIBLE_NONDETERMINISM"
    else:
        verdict = "CAPTURED"

    results[script] = dict(sites=[f"{script}:{ln}" for ln in meta["sites"]],
                           verdict=verdict, deterministic=deterministic,
                           # png_sha/png_deterministic were computed into runs[]
                           # and then NEVER COPIED HERE, so the banked baseline
                           # carried png_sha=None and the whole figure arm of the
                           # module mutation test was INERT -- meaning site :297,
                           # whose ONLY witness is the figure, had no witness at
                           # all while its file reported CAPTURED. Found by asking
                           # whether the arm can fire, not by it failing.
                           png_sha=runs[0].get("png_sha", {}),
                           png_deterministic=png_deterministic,
                           diff_lines=diff_lines, missing_sentinels=missing,
                           exit=runs[0]["exit"], seconds=runs[0]["seconds"],
                           stdout_sha=hashlib.sha256(runs[0]["stdout"].encode()).hexdigest(),
                           stdout=runs[0]["stdout"])

# ── restore and VERIFY ──────────────────────────────────────────────────────
for rel in archived:
    shutil.copy2(os.path.join(SCRATCH, os.path.basename(rel)), os.path.join(ROOT, rel))
after = snapshot()
changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))

print(f"\nrestore verification: {len(changed)} file(s) differ from the pre-run snapshot")
for k in changed:
    print(f"  CHANGED {k}")

print(f"\n{'script':28s} {'verdict':28s} {'det':>4s} {'exit':>5s} {'sec':>7s}")
for s, r in results.items():
    print(f"  {s:26s} {r['verdict']:28s} {str(r['deterministic']):>4s} "
          f"{r['exit']:>5d} {r['seconds']:>7.1f}")
    for d in r["diff_lines"]:
        print(f"        nondeterministic line {d[:96]}")

print("\nOBSERVABLE_ABSENT (declared, not discovered):")
for k, why in OBSERVABLE_ABSENT.items():
    print(f"  {k}\n      {why}")

print("\nOBSERVABLE_IS_FIGURE_ONLY:")
for k, why in OBSERVABLE_IS_FIGURE_ONLY.items():
    print(f"  {k}\n      {why}")

json.dump(dict(scripts=results, snapshot_changed=changed,
               observable_absent=OBSERVABLE_ABSENT,
               observable_figure_only=OBSERVABLE_IS_FIGURE_ONLY,
               masks=[p.pattern for p, _ in MASKS]),
          open(f"{HERE}/baselines_module.json", "w"), indent=1)
print("\nwritten -> overnight_2026_08_23/baselines_module.json")
if changed:
    print("\nCAPTURE MUTATED THE REPO — investigate before trusting these baselines")
    sys.exit(1)
