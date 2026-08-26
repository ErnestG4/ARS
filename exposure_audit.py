"""EXPOSURE-WINDOW AUDIT: what did the broken guards certify while broken?

Fixing a guard discharges nothing about what it certified beforehand. On
2026-08-25 adversarial review demonstrated four defects in this repo's guards
and the board was green through all of them:

  A  verdictlattice.compose()'s NEGATION PATH was unfalsifiable — replacing the
     head computation with `head = holds` left the board green.
  B  reachable.Bar.score()'s `met` was asserted by nothing — hardcoding
     `met = True` left the board green.
  C  reachable's inertness check was ONE-SIDED: bars that could not MISS were
     accepted, so any threshold sitting at the edge of its own declared range
     was certified while inert.
  D  queue.py shadowed the stdlib. Not a verdict path; out of scope here.

The precedent is exact: when a gc could have orphaned frozen blobs, the response
was to cat-file every one, not to trust the seal survived.

THE TEST THAT ISOLATES THE GUARD, which a naive one does not
--------------------------------------------------------------
Comparing each cell's CURRENT verdict against its baseline verdict answers
nothing: the cells were edited during the repairs, so a match only says the
headline is stable across two simultaneous changes. The question is whether the
cell AS IT STOOD AT BASELINE survives the HARDENED guards.

So this audit reconstructs each cell at the baseline commit, runs it against the
current guard modules, and reports:

  SURVIVES   the baseline cell still constructs and runs — its arms were live,
             and the repairs were not load-bearing for it
  REFUSED    the baseline cell no longer constructs — it held an inert bar or an
             unreachable lattice, so whatever it certified during the window was
             certified by machinery that could not have failed

A REFUSED row is a DISCLOSURE, not a regression. The cell may have been repaired
since and may report the same headline; that is a different fact from the seal
having been valid at the time. Every refusal must therefore appear in
DISCLOSED below, with where its output travelled — and this board row FAILS if
one does not, so an exposure cannot be quietly absorbed by fixing the cell.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
BASELINE = "0dd7bb6"
SCRATCH = os.path.expandvars(
    "/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool/"
    "24c2aacc-2d7a-4059-bcf0-8164a33eb1b0/scratchpad/exposure_audit")

CELLS = [
    "brocot_above_horizon_parent", "brocot_audible_horizon",
    "brocot_index_routing", "brocot_jump_display_v3", "brocot_map_dimension",
    "brocot_path_truncation", "brocot_suggest_census",
    "brocot_suggest_score_census", "brocot_truncated_butterfly",
]

# Every REFUSED cell must appear here, with where its output travelled.
DISCLOSED = {
    "brocot_audible_horizon":
        "SHIPPED. Its -40/-60 dB region tables are in brocot MAP-FIELD.md. "
        "Both arms it designated EXISTENCE were inert -- E1 ('share <= 1.0' "
        "against ceiling 1.0) and E3 ('<= 13 regions' against ceiling 13, off "
        "by one from the real claim, 12) -- so the cell as sealed could not "
        "have failed to find a shrinkage. The COUNTS are computations and do "
        "not depend on any bar; what was uncertified was the CLAIM that they "
        "constitute a shrinkage. E2 (23.1% audible at -40 dB against a bar of "
        "50%) is a live arm on a [0,1] range and does certify it. MAP-FIELD.md "
        "carries the disclosure.",
}


def build_scaffold():
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH)
    os.makedirs(os.path.join(SCRATCH, "cross_substrate"))
    for name in os.listdir(HERE):
        src = os.path.join(HERE, name)
        if name in (".git", "__pycache__"):
            continue
        if name == "cross_substrate":
            for f in os.listdir(src):
                if f.endswith(".py"):
                    os.symlink(os.path.join(src, f),
                               os.path.join(SCRATCH, "cross_substrate", f))
            continue
        os.symlink(src, os.path.join(SCRATCH, name))


def install_baseline(stem):
    rel = f"cross_substrate/{stem}.py"
    p = subprocess.run(["git", "show", f"{BASELINE}:{rel}"],
                       capture_output=True, text=True, cwd=HERE)
    if p.returncode != 0:
        return False
    dst = os.path.join(SCRATCH, rel)
    if os.path.islink(dst):
        os.unlink(dst)
    open(dst, "w").write(p.stdout)
    return True


build_scaffold()
rows = []
for stem in CELLS:
    if not install_baseline(stem):
        rows.append(dict(cell=stem, state="NO-BASELINE", why=""))
        continue
    p = subprocess.run([PY, f"cross_substrate/{stem}.py"], capture_output=True,
                       text=True, cwd=SCRATCH, timeout=5400)
    if p.returncode == 0:
        rows.append(dict(cell=stem, state="SURVIVES", why=""))
    else:
        guard = [ln for ln in p.stderr.splitlines()
                 if "UnreachableBar" in ln or "BadLattice" in ln
                 or "VacuousRedPath" in ln]
        rows.append(dict(cell=stem, state="REFUSED",
                         why=(guard[-1] if guard else
                              (p.stderr.strip().splitlines() or [""])[-1])))

print(f"EXPOSURE-WINDOW AUDIT — baseline cells vs hardened guards ({BASELINE})\n")
print(f"{'cell':>34s}   state")
for r in rows:
    print(f"{r['cell']:>34s}   {r['state']}")
    if r["state"] == "REFUSED":
        print(f"{'':>36s} {r['why'][:96]}")

refused = [r for r in rows if r["state"] == "REFUSED"]
surv = [r for r in rows if r["state"] == "SURVIVES"]
print(f"\n  {len(surv)}/{len(rows)} baseline cells survive the hardened guards")

missing = [r["cell"] for r in refused if r["cell"] not in DISCLOSED]
if refused:
    print("\n  EXPOSED — certified during the window by machinery that could "
          "not have failed:")
    for r in refused:
        d = DISCLOSED.get(r["cell"], "*** UNDISCLOSED ***")
        print(f"      {r['cell']}\n        {d}")

json.dump(dict(baseline=BASELINE, rows=rows,
               n_surviving=len(surv), n_refused=len(refused),
               disclosed=DISCLOSED, undisclosed=missing),
          open(f"{HERE}/exposure_audit.json", "w"), indent=1)
print("\nwritten -> exposure_audit.json")

if missing:
    print(f"\nEXPOSURE_AUDIT: FAIL — {len(missing)} exposure(s) undisclosed: "
          f"{missing}. Repairing the cell does not discharge what it certified "
          "while the guard was broken.")
    sys.exit(1)
print("\nEXPOSURE_AUDIT: PASS — every baseline cell either survives the "
      "hardened guards or has its exposure disclosed with where the output "
      "travelled.")
