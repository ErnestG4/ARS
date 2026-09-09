"""Re-derive the tau-vs-k* census from the banked fits it re-reads.

  1. Every k* recomputes from the source artifact's own per-bin fit parameters.
     The census edits nothing, so a disagreement means a source artifact moved.
  2. The CORRECTION STILL RUNS THE HELPFUL WAY: k* must order monotonically in
     strictly more cells than tau does. That is the census's whole content -- if
     it inverted, the recommendation to compare at a level crossing would be
     backwards.
  3. The scope claim holds: `fit_ladder` remains confined to derivflow, and
     science_dense.py still compares shape parameters only inside the same-form
     branch. The sealed shape-z's safety is a property of that code, not of a
     sentence, so it is re-checked rather than trusted.
  4. The census keeps its POST-HOC label.
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from science_rate_question import KSTAR_LEVEL                       # noqa: E402

bad = []
c = json.load(open(os.path.join(HERE, "tau_vs_kstar_census.json")))
Y0, L10 = np.log10(KSTAR_LEVEL), np.log10(np.e)
if abs(c["kstar_level"] - KSTAR_LEVEL) > 0:
    bad.append("census kstar_level differs from the arc's KSTAR_LEVEL")


def kstar(form, p):
    la = p[0]
    if form == "F1":
        return 10 ** ((la - Y0) / p[1])
    if form == "F2":
        return p[1] * (la - Y0) / L10
    return p[1] * ((la - Y0) / L10) ** (1.0 / p[2])


def load(origin):
    fn = origin.split(":")[0]
    d = json.load(open(os.path.join(HERE, fn)))
    if ":" in origin:
        a = origin.split(":")[1]
        return d["arms"][a]["fits"], d["arms"][a]["selected_forms"]
    return d["fits"], d["selected_forms"]


for lab, cell in c["cells"].items():
    fits, forms = load(cell["origin"])
    if forms != cell["forms"]:
        bad.append(f"{lab}: selected_forms changed in the source artifact")
        continue
    for b, f in enumerate(forms):
        p = fits[f"bin{b}"]["ladder"][f].get("params")
        want = float(kstar(f, p)) if p else None
        got = cell["kstar"][b]
        if (want is None) != (got is None):
            bad.append(f"{lab} bin{b}: k* presence mismatch")
        elif want is not None and abs(got - want) > 1e-9 * max(abs(want), 1.0):
            bad.append(f"{lab} bin{b}: k* {got} != re-derived {want}")

s = c["summary"]
if s["n_kstar_monotone"] <= s["n_tau_monotone"]:
    bad.append(f"k* orders in {s['n_kstar_monotone']} cells and tau in "
               f"{s['n_tau_monotone']} — the correction no longer runs the "
               "helpful way, and the level-crossing recommendation would be "
               "backwards")

# scope: fit_ladder confined to derivflow, and the sealed comparison still guarded
r = subprocess.run(["grep", "-rln", "fit_ladder", "--include=*.py", ROOT],
                   capture_output=True, text=True)
users = [p for p in r.stdout.split()
         if "__pycache__" not in p and "archive_v1grid" not in p]
outside = [p for p in users if "/derivflow/" not in p]
if outside:
    bad.append(f"fit_ladder is now used outside derivflow: {outside} — the "
               "census's bounded-scope claim no longer holds")
sd = open(os.path.join(HERE, "science_dense.py")).read()
if not re.search(r'fi\["selected"\]\s*!=\s*fg\["selected"\]', sd):
    bad.append("science_dense.py no longer routes form disagreement to its own "
               "branch — the sealed shape-z may now compare across forms")

if "POST-HOC" not in c["status"].upper():
    bad.append("the census has lost its POST-HOC label")

print(f"  {len(c['cells'])} per-bin cells re-derived; k* monotone in "
      f"{s['n_kstar_monotone']}, tau in {s['n_tau_monotone']}, "
      f"disagreeing in {len(s['disagreements'])}")
print(f"  fit_ladder confined to derivflow ({len(users)} files); "
      f"science_dense form-disagreement branch present")

if bad:
    print("VERIFY_TAU_VS_KSTAR_CENSUS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_TAU_VS_KSTAR_CENSUS: PASS — every k* re-derives from its source "
      "fits, the correction still runs the helpful way, and the sealed shape-z "
      "remains form-guarded")
