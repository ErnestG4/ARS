#!/usr/bin/env python3
"""CENSUS: every per-bin tau ordering in this arc, re-read at a level crossing.

POST-HOC AND UNSEALED, STATED FIRST. This is a re-reading of already-banked fits,
not a new measurement: no flow is run, no fit is refitted, no banked artifact is
edited. It carries no sealed predictions because it makes no prediction -- it
applies one correction uniformly and reports what changes.

WHY IT EXISTS
-------------
2026-09-08, twice in one day, a conclusion turned out to rest on a fitted SHAPE
PARAMETER compared across fits that had selected DIFFERENT functional forms:

  * gue_isoconfig_adapted's C2 ratioed the largest per-bin tau across two
    conditioning times, where the slow bin is F2 at one and F3 at the other;
  * F_window_exponent chased a "genus-dependent exponent" that RH already fixes,
    where the fitted slope could only ever measure the oscillating prefactor.

Both were caught individually. A defect seen twice in one arc is a census
question, not two anecdotes, so this cell asks it of every per-bin cell here.

SCOPE OF THE RISK, bounded first. `fit_ladder` -- the AICc form selector whose
output makes a tau comparison form-dependent -- is used in exactly ten files, all
in derivflow. THE SEALED SCIENCE IS SAFE BY CONSTRUCTION: science_dense.py
compares shape parameters ONLY inside the `fi["selected"] == fg["selected"]`
branch and routes form disagreement to a separate verdict, so the sealed shape-z
never crosses forms. The exposure is the per-bin cells, which compare tau across
five bins that select forms independently.

THE COMMENSURABLE STATISTIC is k*, the crossing of KSTAR_LEVEL: defined
identically for F1, F2 and F3, already this arc's scale-law quantity, and a
property of the curve rather than of a parameterisation.

WHAT THE CENSUS FINDS -- the correction runs in the direction that HELPS.
THREE of the five per-bin cells select mixed forms across their bins (an earlier
draft of this docstring said all five; the census contradicted it and the claim
is corrected here rather than softened). Re-read at k*:

    cell               forms                     tau mono   k* mono
    step2_K0           F2,F3,F3,F3,F3            False      False
    step2b_iid_K2      F2,F3,F3,F3,F1            False      True
    step2b_gue_K2      F2,F2,F1,F1,F1            False      True
    adapted_gue_K1     F3,F3,F3,F3,F3            False      True
    adapted_iid_K1     F3,F3,F3,F3,F3            True       True

k* orders monotonically in FOUR of five conditionings; tau reports it in ONE of
those four. The environmental ordering is therefore considerably more robust than
the banked tau readings suggest -- tau fails to see it for two distinct reasons,
neither of them physical: an F1 bin yields no tau at all (so the ordering is
scored False on a missing value), and F3's tau is degenerate with its stretch
exponent (so a real ordering can come out shuffled).

AND THE SECOND REASON DOES NOT NEED MIXED FORMS. `adapted_gue_K1` selects F3 in
all five bins -- no cross-form comparison anywhere -- and tau STILL reports
non-monotone where k* is strictly decreasing. So tau is unsafe across forms AND
within a single stretched form, and "check the forms match" is necessary but not
sufficient. Only two of the five cells have tau and k* agreeing at all.

The one genuine non-monotonicity is step2_K0, and it is in the LAST quintile
only: k* = 13.413, 10.977, 9.857, 9.280, 9.337 -- the final bin ticks back up by
0.06. Conditioning on the SEED breaks the ordering in one extreme bin where the
two mid-flow conditionings do not. That is a texture the tau reading could not
have shown, since it scored the same cell False for an unrelated reason.

NOTHING HERE OVERTURNS A VERDICT. The per-bin ladder's SUPPORTED branch requires
`n_f2 >= 4 AND tau_ok`, and no cell fired it, so no banked outcome ever rested on
a cross-form tau. What rested on it is PROSE: the sentence "tau orders
monotonically by environment" states a WEAKER and partly wrong version of a
stronger true fact, and is corrected there to cite k*.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from science_rate_question import KSTAR_LEVEL                       # noqa: E402

Y0, L10 = np.log10(KSTAR_LEVEL), np.log10(np.e)


def kstar(form, p):
    la = p[0]
    if form == "F1":
        return 10 ** ((la - Y0) / p[1])
    if form == "F2":
        return p[1] * (la - Y0) / L10
    return p[1] * ((la - Y0) / L10) ** (1.0 / p[2])


def arm_kstar(fits, forms):
    out = []
    for b, f in enumerate(forms):
        p = fits[f"bin{b}"]["ladder"][f].get("params")
        out.append(float(kstar(f, p)) if p else None)
    return out


def strictly_decreasing(seq):
    s = [x for x in seq if x is not None]
    return len(s) > 1 and all(a > b for a, b in zip(s, s[1:]))


srcs = {}
for fn, lab in (("step2_env_decomposition.json", "step2_K0"),
                ("step2b_isoconfig.json", "step2b_iid_K2"),
                ("step2b_isoconfig_gue.json", "step2b_gue_K2")):
    d = json.load(open(os.path.join(HERE, fn)))
    srcs[lab] = (d["fits"], d["selected_forms"], d["taus"], fn)
d = json.load(open(os.path.join(HERE, "gue_isoconfig_adapted.json")))
for a, lab in (("gue_new", "adapted_gue_K1"), ("iid_new", "adapted_iid_K1")):
    srcs[lab] = (d["arms"][a]["fits"], d["arms"][a]["selected_forms"],
                 d["arms"][a]["taus"], f"gue_isoconfig_adapted.json:{a}")

cells = {}
for lab, (fits, forms, taus, origin) in srcs.items():
    ks = arm_kstar(fits, forms)
    tau_mono = (strictly_decreasing(taus)
                if all(t is not None for t in taus) else False)
    cells[lab] = dict(origin=origin, forms=forms, mixed_forms=len(set(forms)) > 1,
                      taus=taus, kstar=ks,
                      tau_monotone=tau_mono, kstar_monotone=strictly_decreasing(ks),
                      tau_missing=sum(1 for t in taus if t is None))

n_mixed = sum(1 for c in cells.values() if c["mixed_forms"])
n_k = sum(1 for c in cells.values() if c["kstar_monotone"])
n_t = sum(1 for c in cells.values() if c["tau_monotone"])
disagree = [k for k, c in cells.items() if c["tau_monotone"] != c["kstar_monotone"]]

print(__doc__.split("WHY IT EXISTS")[0].strip())
print(f"\n{'cell':18s} {'forms':30s} {'mixed':6s} {'tau mono':9s} {'k* mono':8s}")
for lab, c in cells.items():
    print(f"{lab:18s} {','.join(c['forms']):30s} {str(c['mixed_forms']):6s} "
          f"{str(c['tau_monotone']):9s} {str(c['kstar_monotone']):8s}")
    print(f"{'':18s}   k* = {[None if x is None else round(x, 3) for x in c['kstar']]}")
print(f"\n  mixed forms in {n_mixed} of {len(cells)} cells — so every cross-bin tau "
      f"comparison in this arc is cross-form")
print(f"  k* monotone in {n_k} of {len(cells)};  tau reports it in {n_t}")
print(f"  they disagree in {len(disagree)}: {', '.join(disagree)}")
print(f"\n  no banked verdict moves: the SUPPORTED branch needs n_f2>=4 AND "
      f"tau_ok, and no cell fired it.")

json.dump(dict(
    status="POST-HOC, UNSEALED CENSUS — a re-reading of banked fits; no flow "
           "re-run, no fit refitted, no artifact edited",
    kstar_level=KSTAR_LEVEL,
    scope="fit_ladder is used in 10 files, all in derivflow. science_dense.py "
          "compares shape parameters only within the same-form branch, so the "
          "SEALED shape-z is safe by construction; the exposure is the per-bin "
          "cells.",
    cells=cells,
    summary=dict(n_cells=len(cells), n_mixed_forms=n_mixed,
                 n_kstar_monotone=n_k, n_tau_monotone=n_t,
                 disagreements=disagree),
    reading="k* orders monotonically in 4 of 5 conditionings; tau reports it in "
            "1 of those 4. tau fails for two non-physical reasons: an F1 bin "
            "yields no tau (ordering scored False on a missing value), and F3's "
            "tau is degenerate with its stretch exponent. The environmental "
            "ordering is more robust than the banked tau readings suggest.",
    genuine_nonmonotonicity="step2_K0 only, and only in the last quintile "
                            "(k* 9.280 -> 9.337). Seed-conditioning breaks the "
                            "ordering in one extreme bin where both mid-flow "
                            "conditionings do not.",
    verdicts_unaffected="the per-bin SUPPORTED branch requires n_f2>=4 AND "
                        "tau_ok and never fired in any cell, so no banked "
                        "outcome rested on a cross-form tau.",
    carry_forward="compare relaxation timescales at a level crossing, never by "
                  "a shape parameter, whenever form selection is data-driven"),
    open(os.path.join(HERE, "tau_vs_kstar_census.json"), "w"), indent=1)
print("\nwrote tau_vs_kstar_census.json")
