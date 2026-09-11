"""Re-derive the recertification series, and hold the ONE thing that ties it together.

RECERT_SCOPE Stages 1 and 2a bank instrument measurements against a known answer.
Three of those numbers are load-bearing for what the paper may eventually say, so
they get a row rather than sitting in a JSON nobody re-reads:

  1. THE GATE'S RESOLUTION IS RE-DERIVED, not trusted. Every bar in the series is
     set to `knownanswer.detectable_bias(...)` at that cell's ensemble size. If
     the module's constant drifts, or a cell's stored resolution stops matching
     what its own configuration implies, every bar in that cell is mis-set and
     its verdict is unreadable. verify_knownanswer guards the constant; this
     guards the cells' USE of it.
  2. THE BARS RE-DERIVE FROM THE STORED SURFACE. Each headline statistic --
     Stage 1's max/min over the eps grid, Stage 2a's section spread, its
     centre/outer difference and its clean-region edge -- is recomputed here from
     the per-cell bias dictionaries and compared to the banked bar value. A cell
     whose summary no longer follows from its own data is the defect this
     catches.
  3. CROSS-CELL CONTINUITY. Stage 2a's central window at the science's own size
     must agree with Stage 1's reading. The two cells share a construction and a
     truth; if one is re-run and the other is not, they drift apart silently and
     the section table stops being comparable to the surface it was built to
     dissect. Stage 2a checks this as a premise at run time; this checks it
     again across the two ARTIFACTS, which is the thing a later session actually
     reads.

What this does NOT check: that the instrument measurements are correct, or that
the configuration resembles a flowed polynomial. Those are judgements no checker
can make, and the cells' own scope lines say so.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from knownanswer import detectable_bias                               # noqa: E402

bad = []
S1 = json.load(open(os.path.join(HERE, "recert_bias_surface.json")))
S2 = json.load(open(os.path.join(HERE, "recert_section_sweep.json")))

# ---- 1. resolutions re-derive from each cell's own configuration ------------
BULK = 0.20
m1 = S1["n"] - min(S1["k_test"])
r1 = detectable_bias(int(BULK * m1), S1["reps"])
if abs(r1 - S1["gate_resolution"]) > 1e-12 * max(r1, 1e-300):
    bad.append(f"Stage 1 gate_resolution {S1['gate_resolution']:.6f} != "
               f"re-derived {r1:.6f}")
for sz in S2["sizes"]:
    want = detectable_bias(max(8, int(round(sz * S2["m"]))), S2["reps"])
    got = S2["resolution_by_size"][str(sz)]
    if abs(want - got) > 1e-12 * max(want, 1e-300):
        bad.append(f"Stage 2a resolution at size {sz}: stored {got:.6f} != "
                   f"re-derived {want:.6f}")
print(f"  resolutions re-derived: Stage 1 {r1:.4%}; Stage 2a "
      + ", ".join(f"{sz}:{S2['resolution_by_size'][str(sz)]:.2%}" for sz in S2["sizes"]))

# ---- 2. bars re-derive from the stored surfaces -----------------------------
eta_p, kmax = S1["eta_primary"], max(S1["k_test"])
row = S1["bias"][f"k{kmax}_eta{eta_p:.0e}"]
rich = {c: abs(row[f"rich@{c}"]) for c in S1["eps_grid"]}
rec1 = {
    "max |Richardson bias| over the eps grid (k=64)": max(rich.values()),
    f"|Richardson bias| at eps/Delta = {S1['eod_node']} (k=64 operating point)":
        rich[S1["eod_node"]],
    "largest eps/Delta still within the gate's resolution":
        max([c for c in S1["eps_grid"] if rich[c] <= r1], default=0.0),
}
sec = {(p, s_): S2["bias"][f"eta{S2['eta_primary']:.0e}_eps{S2['eps_nodes'][0]}"
                           f"_pos{p}_size{s_}"]
       for p in S2["positions"] for s_ in S2["sizes"]}
res_bulk = S2["resolution_by_size"][str(BULK)]
usable = [p for p in S2["positions"] if abs(sec[(p, BULK)]) <= res_bulk]
rec2 = {
    "max - min Richardson bias across all (position, size) cells":
        max(sec.values()) - min(sec.values()),
    "|bias| at the outermost position minus |bias| at the centre":
        abs(sec[(max(S2["positions"]), BULK)]) - abs(sec[(0.0, BULK)]),
    "outermost position still within the gate's resolution":
        max(usable) if usable else 0.0,
}
for cell, rec in ((S1, rec1), (S2, rec2)):
    for name, want in rec.items():
        if name not in cell["bars"]:
            bad.append(f"bar {name!r} missing from the artifact")
            continue
        got = cell["bars"][name]["value"]
        if abs(got - want) > 1e-9 * max(abs(want), 1e-300):
            bad.append(f"{name}: banked {got:.6g} != re-derived {want:.6g}")
print(f"  bars re-derived: {len(rec1)} in Stage 1, {len(rec2)} in Stage 2a")

# ---- 3. cross-cell continuity ----------------------------------------------
centre = sec[(0.0, BULK)]
s1_read = S1["bias"][f"k{kmax}_eta{eta_p:.0e}"][f"rich@{S1['eod_node']}"]
gap = abs(centre - s1_read)
# KNOWN DEFECT, recorded rather than smoothed over. Stage 2a TYPED its
# Stage-1 reference value as the literal 0.007265 instead of reading it from
# recert_bias_surface.json, so it carries only the 4 significant figures that
# were visible in a terminal. The values agree to 5.8e-07 relative, which is
# exactly the rounding and nothing more -- but the cell cannot NOTICE if Stage 1
# is ever re-run, because it is comparing against a number that no longer has a
# source. The tolerance below is therefore the stored precision, and the defect
# is printed on every board run so it is not forgotten: cross-cell values must
# be READ from the artifact, never typed. Fifth instance of this shape in the
# recert series (see knownanswer._REL_SD_PER_ROOT_GAP and the hardcoded grid
# indices in Stages 1 and 2b).
_typed_rel = abs(S2["stage1_reading"] - s1_read) / max(abs(s1_read), 1e-300)
if _typed_rel > 1e-5:
    bad.append(f"Stage 2a's TYPED Stage-1 reading {S2['stage1_reading']:.6g} is "
               f"{_typed_rel:.2e} from Stage 1's artifact {s1_read:.6g} — beyond "
               "rounding, so Stage 1 has been re-run and Stage 2a is stale")
if gap > res_bulk:
    bad.append(f"cross-cell continuity BROKEN: Stage 2a centre {centre:+.4%} vs "
               f"Stage 1 {s1_read:+.4%}, gap {gap:.4%} exceeds {res_bulk:.4%}")
print(f"  continuity: Stage 2a centre {centre:+.4%} vs Stage 1 {s1_read:+.4%} "
      f"(gap {gap:.4%}, bar {res_bulk:.4%})")
print(f"  KNOWN DEFECT: Stage 2a TYPED its Stage-1 reference ({_typed_rel:.1e} "
      f"from the artifact, i.e. rounding). Cross-cell values must be READ.")

# ---- 4. the verdicts still say what the arms imply --------------------------
for cell, name in ((S1, "Stage 1"), (S2, "Stage 2a")):
    ex = [a for a in cell["composed"]["arms"] if "EXISTENCE" in a]
    if not ex:
        bad.append(f"{name}: no EXISTENCE arm in the composed verdict")
if S1["verdict"] != "NO_RESOLVABLE_BANDWIDTH_BIAS_AT_THE_SCIENCES_OPERATING_POINT":
    bad.append(f"Stage 1 verdict changed: {S1['verdict']!r}")
if S2["verdict"] != "FLATNESS_IS_AN_ARTIFACT_OF_THE_CENTRAL_WINDOW":
    bad.append(f"Stage 2a verdict changed: {S2['verdict']!r}")
print(f"  verdicts: {S1['verdict']}")
print(f"            {S2['verdict']}")

if bad:
    print("VERIFY_RECERT: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_RECERT: PASS — resolutions re-derive from knownanswer, every "
      "headline bar re-derives from its own surface, and the two cells still "
      "agree at the window they share")
