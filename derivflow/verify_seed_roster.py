"""Re-derive the beta-roster surface from its banked fits.

  1. THE PREMISE THAT MAKES IT A ROSTER AND NOT A NEW ARC: the beta=2 arm must
     still reproduce science_dense_grid's banked GUE numbers exactly. If it
     stops, the other two arms are measuring a different instrument.
  2. THE PREMISE THAT MAKES IT A MATCHED DESIGN: the seed laws must still agree.
     Every claim here attributes a k* difference to LOCAL repulsion, and that is
     licensed only because the global measure is held fixed.
  3. The surface re-derives: each arm's k* recomputes from its own stored fit
     parameters, and the ordering is strictly decreasing in beta with the ends
     separated well beyond their combined error.
  4. THE SCOPE LINE SURVIVES. iid carries a different global law and is a
     reference, not a fourth point. An artifact that quietly folded it into the
     matched surface would be claiming a repulsion effect for a difference that
     is partly global-shape.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from science_rate_question import KSTAR_LEVEL                       # noqa: E402

bad = []
d = json.load(open(os.path.join(HERE, "seed_roster_beta.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))

if d["p1_mismatches"] != 0:
    bad.append(f"P1 mismatches {d['p1_mismatches']}, not 0 — beta=2 no longer "
               "reproduces the banked GUE arm, so the roster is not built on it")
worst_ks = max(d["seed_law_ks"].values())
if worst_ks > 0.05:
    bad.append(f"max seed-law KS {worst_ks:.4f} exceeds 0.05 — the global measure "
               "is no longer held fixed, and no k* difference here can be "
               "attributed to local repulsion")

Y0, L10 = np.log10(KSTAR_LEVEL), np.log10(np.e)


def kstar(form, p):
    la = p[0]
    if form == "F1":
        return 10 ** ((la - Y0) / p[1])
    if form == "F2":
        return p[1] * (la - Y0) / L10
    return p[1] * ((la - Y0) / L10) ** (1.0 / p[2])


betas = [str(b) for b in d["betas"]]
ks = []
for b in betas:
    a = d["arms"][b]
    if a["selected"] != "F3":
        bad.append(f"beta={b} selects {a['selected']}, not F3 — the roster's "
                   "existence arm has changed")
    want = kstar(a["selected"], a["params"])
    if abs(a["kstar"] - want) > 1e-9 * max(abs(want), 1.0):
        bad.append(f"beta={b}: k* {a['kstar']} != re-derived {want}")
    ks.append(a["kstar"])

if not all(x > y for x, y in zip(ks, ks[1:])):
    bad.append(f"k* is no longer strictly decreasing in beta: {ks} — the "
               "ordering is the cell's mechanism claim")
lo, hi = d["arms"][betas[0]], d["arms"][betas[-1]]
sep = abs(lo["kstar"] - hi["kstar"]) / np.sqrt(lo["kstar_err"] ** 2
                                               + hi["kstar_err"] ** 2)
if sep < 3.0:
    bad.append(f"end-to-end separation {sep:.1f} sigma has fallen below 3 — the "
               "repulsion axis no longer moves the scale beyond its own error")
if abs(d["bars"]["|k*(beta=1) - k*(beta=4)| in combined sigma"]["value"] - sep) > 1e-6:
    bad.append("the banked separation does not re-derive")

# scope: iid stays a reference, not a roster point
if "iid" in d["arms"]:
    bad.append("iid has been folded into the roster arms — it carries a "
               "different (uniform) global law and cannot sit on a surface whose "
               "whole premise is a fixed global measure")
if "iid" not in d.get("banked_reference", {}):
    bad.append("the iid reference is gone from the artifact; it is what shows "
               "the trend continues beyond the matched range")
bi = d["banked_reference"]["iid"]
if abs(bi["kstar"] - bank["kstar_table"]["iid"]["4096"]["kstar"]) > 1e-12:
    bad.append("the banked iid reference no longer matches science_dense_grid")
if d["verdict"] != "RELAXATION_SCALE_ORDERS_WITH_SEED_REPULSION":
    bad.append(f"verdict is {d['verdict']!r}")

print(f"  P1 {d['p1_mismatches']}/40; seed-law KS max {worst_ks:.4f} "
      + ("(matched design holds)" if worst_ks <= 0.05
         else "(EXCEEDS the 0.05 bar — design NOT matched)"))
print(f"  k* by beta {d['betas']}: " + " > ".join(f"{x:.4f}" for x in ks)
      + f"   ends separated by {sep:.1f} sigma")
print(f"  iid reference (unmatched global law): k* {bi['kstar']:.4f}")

if bad:
    print("VERIFY_SEED_ROSTER: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_SEED_ROSTER: PASS — beta=2 still reproduces the banked arm, the "
      "global law is still held fixed, the surface re-derives and orders, and "
      "iid is still a reference rather than a roster point")
