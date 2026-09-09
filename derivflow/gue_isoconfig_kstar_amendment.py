#!/usr/bin/env python3
"""AMENDMENT to gue_isoconfig_adapted: C2's comparison was not commensurable.

POST-HOC AND UNSEALED, STATED FIRST. Everything here was computed AFTER the
sealed arms were read. It gets no sealed credit, it does not change
gue_isoconfig_adapted.json, and it does not convert C2's MISS into a hit. C2
missed as executed and stays missed. What this amendment establishes is that the
miss does not mean what the seal said it would mean.

THE DEFECT, in my own seal
--------------------------
C2 compared "the LARGEST fitted tau among that class's bins" across conditioning
times. Checked after the fact against the artifacts:

    slow bin form, K_COND = 2 (banked):   gue F2,  iid F2
    slow bin form, K_COND = 1 (adapted):  gue F3,  iid F3

tau in F2 is the scale of exp(-k/tau). tau in F3 is the scale of
exp(-(k/tau)^beta), and in a stretched-exponential fit it is strongly degenerate
with beta. These are parameters of different functional forms; a ratio between
them is not a measurement of anything. This is the commensurability rule's own
failure mode, committed inside a cell whose premise arms were specifically built
to catch instrument substitution -- the arms guarded the instrument and the
comparison walked in through the parameters.

THE COMMENSURABLE COMPARISON
----------------------------
k*, the k at which a fitted bin curve crosses KSTAR_LEVEL = 1e-2. It is defined
for F1, F2 and F3 alike, it is what the arc already uses for its scale law, and
it is a property of the CURVE rather than of a parameterisation. Computed from
the banked per-bin fits of all four arms, changing no fit.

WHAT IT SHOWS, and it reverses C2's reading:

    slowest-bin k*   K_COND=2   K_COND=1    ratio
        iid            13.631     13.510    1.009
        gue             7.039      6.754    1.042

Both classes are stable to within 5% across the third conditioning time, against
C2's 1.5 bar -- so the SCIENTIFIC claim C2 was written to test ("a real
coexisting slow subpopulation should keep its timescale when the conditioning
time moves") is SUPPORTED, on the measure that can carry it. Every bin is stable,
not only the slowest, so this is a property of the whole environmental ordering
rather than of one extreme.

A SECOND ARTIFACT OF THE SAME CAUSE, found while checking the first: the adapted
GUE arm reports tau_monotone = False (taus 0.552, 1.107, 1.241, 0.921, 0.745).
Its k* sequence is 6.754, 6.409, 6.158, 5.830, 5.414 -- strictly DECREASING. GUE
does order monotonically by environment; the non-monotonicity was the same
tau/beta degeneracy showing up in a second place. The reported reading stands in
the artifact and is corrected here rather than edited there.

CARRY-FORWARD: tau is not a safe cross-fit comparison quantity anywhere in this
arc. Any future comparison of relaxation timescales across bins, seeds, forms or
conditioning times should be made at a level crossing.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from science_rate_question import KSTAR_LEVEL                       # noqa: E402

Y0 = np.log10(KSTAR_LEVEL)
LOG10E = np.log10(np.e)


def kstar(form, p):
    """k where the fitted curve crosses KSTAR_LEVEL. Same solve as
    science_rate_question.kstar, form-independent by construction."""
    la = p[0]
    if form == "F1":
        return 10 ** ((la - Y0) / p[1])
    if form == "F2":
        return p[1] * (la - Y0) / LOG10E
    return p[1] * ((la - Y0) / LOG10E) ** (1.0 / p[2])


def arm(fits, forms):
    out = []
    for b, f in enumerate(forms):
        p = fits[f"bin{b}"]["ladder"][f].get("params")
        out.append(kstar(f, p) if p else None)
    return out


old_g = json.load(open(os.path.join(HERE, "step2b_isoconfig_gue.json")))
old_i = json.load(open(os.path.join(HERE, "step2b_isoconfig.json")))
new = json.load(open(os.path.join(HERE, "gue_isoconfig_adapted.json")))

rows = {
    "gue_K2": dict(ks=arm(old_g["fits"], old_g["selected_forms"]),
                   forms=old_g["selected_forms"], taus=old_g["taus"]),
    "iid_K2": dict(ks=arm(old_i["fits"], old_i["selected_forms"]),
                   forms=old_i["selected_forms"], taus=old_i["taus"]),
    "gue_K1": dict(ks=arm(new["arms"]["gue_new"]["fits"],
                          new["arms"]["gue_new"]["selected_forms"]),
                   forms=new["arms"]["gue_new"]["selected_forms"],
                   taus=new["arms"]["gue_new"]["taus"]),
    "iid_K1": dict(ks=arm(new["arms"]["iid_new"]["fits"],
                          new["arms"]["iid_new"]["selected_forms"]),
                   forms=new["arms"]["iid_new"]["selected_forms"],
                   taus=new["arms"]["iid_new"]["taus"]),
}

ratios, monotone = {}, {}
for sc in ("iid", "gue"):
    o = max(x for x in rows[f"{sc}_K2"]["ks"] if x)
    n = max(x for x in rows[f"{sc}_K1"]["ks"] if x)
    ratios[sc] = dict(kstar_K2=o, kstar_K1=n, ratio=max(o / n, n / o))
for k, v in rows.items():
    ks = [x for x in v["ks"] if x]
    monotone[k] = dict(
        kstar_monotone=all(a > b for a, b in zip(ks, ks[1:])),
        tau_monotone_reported=None)
for k, arm_key in (("gue_K1", "gue_new"), ("iid_K1", "iid_new")):
    monotone[k]["tau_monotone_reported"] = new["arms"][arm_key]["tau_monotone"]

print(__doc__.split("WHAT IT SHOWS")[0].strip()[:0] or "", end="")
print("POST-HOC AMENDMENT — unsealed. C2 stays MISSED in the sealed artifact.\n")
print(f"per-bin k* (crossing of {KSTAR_LEVEL:g}), from the banked fits:\n")
print(f"{'arm':9s} " + "".join(f"{'bin' + str(b):>9s}" for b in range(5))
      + f"{'max':>10s}   forms")
for k, v in rows.items():
    print(f"{k:9s} " + "".join(f"{('%.3f' % x) if x else '--':>9s}" for x in v["ks"])
          + f"{max(x for x in v['ks'] if x):>10.3f}   {v['forms']}")
print("\nslowest-bin k* across conditioning times (the commensurable C2):")
for sc in ("iid", "gue"):
    r = ratios[sc]
    print(f"  {sc}: {r['kstar_K2']:.3f} (K_COND=2) -> {r['kstar_K1']:.3f} "
          f"(K_COND=1)   ratio {r['ratio']:.3f}   "
          f"{'STABLE' if r['ratio'] <= 1.5 else 'DRIFTED'} against C2's 1.5")
print("\nmonotonicity, k* vs the reported tau reading:")
for k, m in monotone.items():
    extra = ("" if m["tau_monotone_reported"] is None
             else f"   (artifact reported tau_monotone = {m['tau_monotone_reported']})")
    print(f"  {k:9s} k* monotone decreasing: {m['kstar_monotone']}{extra}")

json.dump(dict(
    status="POST-HOC, UNSEALED AMENDMENT to gue_isoconfig_adapted.json",
    amends="C2 (worst-class slow-tau ratio across conditioning times), which "
           "MISSED at 1.897 vs 1.5 and remains MISSED in the sealed artifact",
    defect="C2 compared tau across DIFFERENT FUNCTIONAL FORMS -- the slow bin is "
           "F2 at K_COND=2 and F3 at K_COND=1 in both classes. tau in F3 is "
           "degenerate with beta; a ratio between an F2 tau and an F3 tau is not "
           "a measurement.",
    commensurable_statistic=f"k*, the crossing of {KSTAR_LEVEL:g}, defined for "
                            "F1/F2/F3 alike and already the arc's scale-law "
                            "statistic",
    kstar_level=KSTAR_LEVEL,
    per_bin_kstar={k: v["ks"] for k, v in rows.items()},
    forms={k: v["forms"] for k, v in rows.items()},
    taus={k: v["taus"] for k, v in rows.items()},
    slowest_bin=ratios,
    monotonicity=monotone,
    reading="C2's SCIENTIFIC claim is SUPPORTED on the commensurable measure: "
            "both classes stable to within 5% (iid 1.009, gue 1.042) across the "
            "third conditioning time, and every bin is stable, not only the "
            "slowest. The sealed arm's MISS was an artifact of the comparison "
            "design and is retained as a miss.",
    second_artifact="the adapted GUE arm's tau_monotone = False is the same "
                    "degeneracy: its k* sequence decreases strictly, so GUE DOES "
                    "order monotonically by environment.",
    carry_forward="tau is not a safe cross-fit comparison quantity in this arc; "
                  "compare relaxation timescales at a level crossing."),
    open(os.path.join(HERE, "gue_isoconfig_kstar_amendment.json"), "w"), indent=1)
print("\nwrote gue_isoconfig_kstar_amendment.json")
