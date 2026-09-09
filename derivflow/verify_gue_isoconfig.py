"""Re-derive the GUE-adapted isoconfigurational probe and its amendment.

  1. The PREMISE holds: the old-design re-run still reproduces the banked GUE arm
     (0 mismatches), and the adaptation still delivers assessable windows. These
     are what make the rest of the cell about the banked instrument.
  2. The bars re-derive from the arms' own stored fits.
  3. C2's MISS IS PRESERVED. It missed as executed; the amendment explains why the
     miss does not carry its intended meaning, and does not convert it.
  4. The AMENDMENT re-derives: every k* recomputes from the banked per-bin fit
     parameters, and the stability ratios follow. If a fit moves, this fails.
  5. The amendment keeps its post-hoc label. A future edit that quietly promoted
     it to sealed standing would be the one thing that makes it dishonest.
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
d = json.load(open(os.path.join(HERE, "gue_isoconfig_adapted.json")))
am = json.load(open(os.path.join(HERE, "gue_isoconfig_kstar_amendment.json")))
bank = json.load(open(os.path.join(HERE, "step2b_isoconfig_gue.json")))
bank_i = json.load(open(os.path.join(HERE, "step2b_isoconfig.json")))

# 1. premise
if d["p1_mismatches"] != 0:
    bad.append(f"p1_mismatches = {d['p1_mismatches']}, not 0")
if d["arms"]["gue_old"]["selected_forms"] != bank["selected_forms"]:
    bad.append("old-design re-run forms no longer match the banked GUE arm")
for a, b in zip(d["arms"]["gue_old"]["taus"], bank["taus"]):
    if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-9 * max(abs(b), 1e-300)):
        bad.append("old-design re-run taus no longer match the banked GUE arm")
        break
if min(d["arms"]["gue_new"]["windows"]) < 6:
    bad.append("the adapted GUE windows are no longer assessable (min < 6)")

# 2. bars re-derive
rec = {
    "old-design re-run vs banked GUE arm, mismatches": float(d["p1_mismatches"]),
    "smallest GUE per-bin fit window under the adapted design":
        float(min(d["arms"]["gue_new"]["windows"])),
    "GUE bins selecting F3 with beta < 0.9 (adapted)":
        float(d["arms"]["gue_new"]["n_f3_stretch"]),
    "iid bins selecting F3 with beta < 0.9 (adapted, control)":
        float(d["arms"]["iid_new"]["n_f3_stretch"]),
}
for name, want in rec.items():
    got = d["bars"][name]["value"]
    if abs(got - want) > 1e-9 * max(abs(want), 1.0):
        bad.append(f"bar '{name}': banked {got!r}, re-derived {want!r}")
for arm in ("gue_new", "iid_new"):
    a = d["arms"][arm]
    n = sum(1 for f, be in zip(a["selected_forms"], a["betas"])
            if f == "F3" and be is not None and be < 0.9)
    if n != a["n_f3_stretch"]:
        bad.append(f"{arm}: n_f3_stretch {a['n_f3_stretch']} != recount {n}")
    if a["ladder_outcome"] != "NOT_SUPPORTED":
        bad.append(f"{arm} outcome is {a['ladder_outcome']}, not NOT_SUPPORTED "
                   "— the mechanism reading has changed")
if d["verdict"] != "STRETCH_MECHANISM_IS_NOT_SEED_DEPENDENT":
    bad.append(f"verdict is {d['verdict']!r}")

# 3. the miss is preserved
c2 = d["bars"]["worst-class slow-tau ratio across conditioning times"]
if c2["met"]:
    bad.append("C2 now reads MET. It MISSED at 1.897; the amendment explains the "
               "miss, it does not convert it")

# 4. the amendment re-derives
Y0, LOG10E = np.log10(KSTAR_LEVEL), np.log10(np.e)


def kstar(form, p):
    la = p[0]
    if form == "F1":
        return 10 ** ((la - Y0) / p[1])
    if form == "F2":
        return p[1] * (la - Y0) / LOG10E
    return p[1] * ((la - Y0) / LOG10E) ** (1.0 / p[2])


srcs = {"gue_K2": (bank["fits"], bank["selected_forms"]),
        "iid_K2": (bank_i["fits"], bank_i["selected_forms"]),
        "gue_K1": (d["arms"]["gue_new"]["fits"], d["arms"]["gue_new"]["selected_forms"]),
        "iid_K1": (d["arms"]["iid_new"]["fits"], d["arms"]["iid_new"]["selected_forms"])}
for key, (fits, forms) in srcs.items():
    got = am["per_bin_kstar"][key]
    for b, f in enumerate(forms):
        p = fits[f"bin{b}"]["ladder"][f].get("params")
        want = kstar(f, p) if p else None
        g = got[b]
        if (g is None) != (want is None):
            bad.append(f"amendment k* {key} bin{b}: presence mismatch")
        elif want is not None and abs(g - want) > 1e-9 * max(abs(want), 1.0):
            bad.append(f"amendment k* {key} bin{b}: {g} vs re-derived {want}")
for sc in ("iid", "gue"):
    r = am["slowest_bin"][sc]
    o = max(x for x in am["per_bin_kstar"][f"{sc}_K2"] if x)
    n = max(x for x in am["per_bin_kstar"][f"{sc}_K1"] if x)
    if abs(r["ratio"] - max(o / n, n / o)) > 1e-9:
        bad.append(f"amendment ratio {sc} does not re-derive")
    if r["ratio"] > 1.5:
        bad.append(f"amendment: {sc} slowest-bin k* ratio {r['ratio']:.3f} now "
                   "exceeds C2's 1.5 bar — the correction no longer holds")

# 5. the post-hoc label survives
if "POST-HOC" not in am["status"].upper():
    bad.append("the amendment has lost its POST-HOC label — it was computed after "
               "the sealed arms were read and may never be quoted as sealed")

print(f"  premise: {d['p1_mismatches']} of 10 mismatched vs the banked GUE arm; "
      f"smallest adapted GUE window {min(d['arms']['gue_new']['windows'])} (was 3)")
print(f"  mechanism: gue {d['arms']['gue_new']['n_f3_stretch']}/5 and iid "
      f"{d['arms']['iid_new']['n_f3_stretch']}/5 bins stretched -> "
      f"{d['verdict']}")
print(f"  C2 stands MISSED at {c2['value']:.3f} vs {c2['thresh']}; on k* the "
      f"same comparison gives iid {am['slowest_bin']['iid']['ratio']:.3f}, "
      f"gue {am['slowest_bin']['gue']['ratio']:.3f} (POST-HOC)")

if bad:
    print("VERIFY_GUE_ISOCONFIG: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_GUE_ISOCONFIG: PASS — premise holds, bars re-derive, C2's miss is "
      "preserved, and the post-hoc amendment re-derives with its label intact")
