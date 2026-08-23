"""How coarse can the serialiser be before statistic_perturb becomes invisible?

COMMITTED GENERATOR of overnight_2026_08_23/serialiser_sensitivity.json.

WHY THIS EXISTS. RESULTS.md claimed "a 9-significant-digit serialiser would catch
0 of 55, and %.12g only 2 of 55" on the strength of an independent reviewer's
measurement. Those were UNATTRIBUTED CONSTANTS: no committed generator in the
repo produced them, and they were load-bearing for the claim that `float.hex()`
is doing real work rather than decorative work. The house rule is that every
banked number needs a committed generator that reproduces it, so here is the
measurement, run against the shipped closure machinery and the shipped attack.

WHAT IS MEASURED. For each def site, the `statistic_perturb` mutant is built
through the shipped builder and evaluated on all 55 sealed inputs. The outputs
are then serialised at a range of precisions, and we count how many inputs differ
from the baseline under each. `float.hex()` is exact; the `%.Ng` forms are the
counterfactual coarser serialisers.

The perturbation's actual magnitude is reported too, because "it moves the KS
distances a little" is a claim with a number behind it and the number belongs in
the artifact rather than in prose.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from capture_def_baselines import closure_source, build_from_source, adapt   # noqa: E402
from mutate_def_baselines import m_statistic_perturb                          # noqa: E402
from redpath import redpath                                                   # noqa: E402

BASE = json.load(open(f"{HERE}/baselines_def.json"))
INPUTS = json.load(open(f"{HERE}/inputs.json"))["vectors"]

PRECISIONS = ["hex", "%.17g", "%.15g", "%.12g", "%.9g", "%.6g", "%.3g"]


def render(obj, prec):
    """Serialise a returned value at the given precision."""
    if isinstance(obj, float):
        return float.hex(obj) if prec == "hex" else (prec % obj)
    if isinstance(obj, (np.floating,)):
        return render(float(obj), prec)
    if isinstance(obj, (bool, int, str, type(None))):
        return repr(obj)
    if isinstance(obj, (np.integer,)):
        return repr(int(obj))
    if isinstance(obj, np.ndarray):
        return "|".join(render(float(x), prec) for x in np.ravel(obj))
    if isinstance(obj, dict):
        return "{" + ",".join(f"{k}:{render(v, prec)}" for k, v in sorted(obj.items())) + "}"
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(render(v, prec) for v in obj) + "]"
    if hasattr(obj, "__dataclass_fields__"):
        return "{" + ",".join(f"{f}:{render(getattr(obj, f), prec)}"
                              for f in sorted(obj.__dataclass_fields__)) + "}"
    return repr(obj)


rows, magnitudes = {}, []
for key, b in sorted(BASE["baselines"].items()):
    code, _pulled, needed = closure_source(b["path"], b["callable"])
    mutated, why_not = m_statistic_perturb(code)
    if mutated is None:
        rows[key] = {"status": "INAPPLICABLE", "reason": why_not}
        continue
    orig, _ = build_from_source(code, needed, b["callable"])
    mut, _ = build_from_source(mutated, needed, b["callable"])

    counts = {p: 0 for p in PRECISIONS}
    for vname, vec in INPUTS.items():
        try:
            a, c = orig(adapt(key, vec)), mut(adapt(key, vec))
        except Exception:                                     # noqa: BLE001
            continue
        for p in PRECISIONS:
            if render(a, p) != render(c, p):
                counts[p] += 1
        # magnitude of the induced change, on the KS distances themselves
        if isinstance(a, dict) and isinstance(c, dict):
            for k in ("ks_p", "ks_o", "ks_u"):
                if isinstance(a.get(k), float) and isinstance(c.get(k), float) \
                        and np.isfinite(a[k]) and np.isfinite(c[k]):
                    magnitudes.append(abs(a[k] - c[k]))
    rows[key] = {"status": "MEASURED", "differing_inputs_by_precision": counts}

measured = {k: v for k, v in rows.items() if v["status"] == "MEASURED"}
totals = {p: sum(v["differing_inputs_by_precision"][p] for v in measured.values())
          for p in PRECISIONS}
sites_detecting = {p: sum(1 for v in measured.values()
                          if v["differing_inputs_by_precision"][p] > 0)
                   for p in PRECISIONS}

mags = np.array([m for m in magnitudes if m > 0])
print(f"sites measured: {len(measured)} of {len(rows)}")
print(f"induced |dKS|: n={mags.size}  min={mags.min():.3e}  "
      f"median={np.median(mags):.3e}  max={mags.max():.3e}")
print(f"\n{'precision':10s} {'sites detecting':>16s} {'input-comparisons differing':>30s}")
for p in PRECISIONS:
    print(f"  {p:10s} {sites_detecting[p]:>14d}/{len(measured)} {totals[p]:>28d}")

# NON-VACUITY, both ends: the exact serialiser must detect, and some coarse one
# must fail. A sweep where every precision behaves identically is measuring
# nothing about precision.
with redpath("sites where the exact serialiser detects the perturbation",
             expect_min=len(measured)) as rp:
    rp.observed(sites_detecting["hex"])
with redpath("precisions at which detection collapses to zero sites", expect_min=1) as rp:
    rp.observed(sum(1 for p in PRECISIONS if sites_detecting[p] == 0))

json.dump(dict(precisions=PRECISIONS, sites_detecting=sites_detecting,
               differing_totals=totals,
               magnitude=dict(n=int(mags.size), min=float(mags.min()),
                              median=float(np.median(mags)), max=float(mags.max())),
               rows=rows),
          open(f"{HERE}/serialiser_sensitivity.json", "w"), indent=1)
print("\nwritten -> overnight_2026_08_23/serialiser_sensitivity.json")
